"""Tests for backend/cv/signals/recovery_latency.py — recovery_latency_ms during ACTIVE_RALLY.

Enforces USER-CORRECTION-017 (physics guardrail): the ONLY input is
`math.hypot(target_kalman[2], target_kalman[3])`. No CourtMapper. No keypoint derivation.

Enforces USER-CORRECTION-018 (Compiler Flush Contract):
- `required_state == ("ACTIVE_RALLY",)`
- ingest() accumulates (t_ms, speed_mps) ONLY during ACTIVE_RALLY
- flush(t_ms) is called by the compiler on state EXIT (extractor is state-blind beyond the gate)

Enforces USER-CORRECTION-022 (fail-fast): `self.deps["match_id"]` strict; flush with a
non-empty buffer and no match_id in deps must raise KeyError.

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import pytest

from backend.cv.signals.recovery_latency import RecoveryLatency
from backend.db.schema import FrameKeypoints, PlayerDetection, SignalSample

# ──────────────────────────── Stub frame + simulate helper ────────────────────────────


def _stub_frame(t_ms: int = 0) -> FrameKeypoints:
    """Minimal FrameKeypoints; extractor consumes only target_kalman."""
    stub_keypoints = [(0.5, 0.5)] * 17
    stub_conf = [0.9] * 17
    detection_a = PlayerDetection(
        player="A",
        keypoints_xyn=stub_keypoints,
        confidence=stub_conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.9),
        feet_mid_m=(4.0, 15.0),
        fallback_mode="ankle",
    )
    detection_b = PlayerDetection(
        player="B",
        keypoints_xyn=stub_keypoints,
        confidence=stub_conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.3),
        feet_mid_m=(4.0, 8.0),
        fallback_mode="ankle",
    )
    return FrameKeypoints(t_ms=t_ms, frame_idx=t_ms // 33, player_a=detection_a, player_b=detection_b)


def simulate_ticks(
    ext: RecoveryLatency,
    ticks_data: list[tuple[str, float | None, float, int]],
) -> None:
    """Feed (target_state, vx, vy, t_ms) tuples into ingest().

    opponent_state fixed to 'DEAD_TIME'; opponent_kalman None.
    target_kalman is (0.0, 0.0, vx, vy), or None if vx is None.
    """
    for target_state, vx, vy, t_ms in ticks_data:
        target_kalman = None if vx is None else (0.0, 0.0, vx, vy)
        ext.ingest(
            frame=_stub_frame(t_ms),
            target_state=target_state,  # type: ignore[arg-type]
            opponent_state="DEAD_TIME",
            target_kalman=target_kalman,
            opponent_kalman=None,
            t_ms=t_ms,
        )


# ──────────────────────────── Construction / class metadata ────────────────────────────


def test_class_attributes_signal_name_and_required_state() -> None:
    """Class-level signal_name and required_state are wired for compiler routing."""
    assert RecoveryLatency.signal_name == "recovery_latency_ms"
    assert RecoveryLatency.required_state == ("ACTIVE_RALLY",)
    assert isinstance(RecoveryLatency.required_state, tuple)


# ──────────────────────────── Gate correctness ────────────────────────────


def test_ingest_during_pre_serve_ritual_is_ignored() -> None:
    """PRE_SERVE_RITUAL ticks do not accumulate; flush returns None."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("PRE_SERVE_RITUAL", 3.0, 0.0, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


def test_ingest_during_dead_time_is_ignored() -> None:
    """DEAD_TIME ticks do not accumulate; flush returns None."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("DEAD_TIME", 3.0, 0.0, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


def test_ingest_with_none_kalman_is_skipped() -> None:
    """Occluded ticks (target_kalman=None) contribute nothing."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", None, 0.0, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── Math correctness ────────────────────────────


def test_decelerate_from_moving_to_still_yields_latency() -> None:
    """30 frames at speed 3.0 then 30 at speed 0.0 → latency = first-still-t - last-moving-t."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    # Moving phase: speed = hypot(3.0, 0.0) = 3.0 (>= 0.5)
    moving = [("ACTIVE_RALLY", 3.0, 0.0, 100 + i * 33) for i in range(30)]
    # Still phase: speed = hypot(0.0, 0.0) = 0.0 (< 0.5)
    still = [("ACTIVE_RALLY", 0.0, 0.0, 100 + (30 + i) * 33) for i in range(30)]
    simulate_ticks(ext, moving + still)

    last_moving_t = 100 + 29 * 33  # 1057
    first_still_t = 100 + 30 * 33  # 1090
    expected_latency = float(first_still_t - last_moving_t)  # 33.0

    sample = ext.flush(t_ms=100 + 60 * 33)
    assert sample is not None
    assert sample.value == pytest.approx(expected_latency, abs=1e-12)


def test_threshold_boundary_half_mps_counts_as_moving() -> None:
    """speed >= 0.5 counts as moving; a tick at exactly 0.5 then at 0.4 should emit latency."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    # Exactly 0.5 m/s (threshold inclusive)
    simulate_ticks(ext, [("ACTIVE_RALLY", 0.5, 0.0, 100)])
    # Then below threshold
    simulate_ticks(ext, [("ACTIVE_RALLY", 0.4, 0.0, 200)])
    sample = ext.flush(t_ms=300)
    assert sample is not None
    assert sample.value == pytest.approx(100.0, abs=1e-12)


def test_all_fast_buffer_never_decelerates_returns_none() -> None:
    """If buffer never drops below 0.5 m/s (player still moving at rally end), flush None."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 3.0, 0.0, t) for t in range(100, 3100, 100)])
    assert ext.flush(t_ms=3100) is None


def test_all_slow_buffer_never_moved_returns_none() -> None:
    """If buffer never crossed 0.5 m/s (never moved during rally), flush None."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 0.1, 0.0, t) for t in range(100, 3100, 100)])
    assert ext.flush(t_ms=3100) is None


def test_empty_buffer_flush_returns_none() -> None:
    """No ingest calls → flush returns None."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    assert ext.flush(t_ms=1000) is None


def test_speed_uses_2d_hypot_not_just_vx() -> None:
    """Moving purely vertically (vy=3.0, vx=0.0) counts as moving — 2D speed magnitude."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    # Pure vertical motion: hypot(0, 3) = 3.0
    simulate_ticks(ext, [("ACTIVE_RALLY", 0.0, 3.0, 100)])
    # Then still
    simulate_ticks(ext, [("ACTIVE_RALLY", 0.0, 0.0, 250)])
    sample = ext.flush(t_ms=300)
    assert sample is not None
    assert sample.value == pytest.approx(150.0, abs=1e-12)


def test_last_moving_tick_selects_latest_index_above_threshold() -> None:
    """Buffer with moving → slow → moving → slow: last moving index wins."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(
        ext,
        [
            ("ACTIVE_RALLY", 3.0, 0.0, 100),  # moving
            ("ACTIVE_RALLY", 0.1, 0.0, 200),  # slow (first time)
            ("ACTIVE_RALLY", 3.0, 0.0, 300),  # moving again (LAST moving tick)
            ("ACTIVE_RALLY", 0.1, 0.0, 400),  # slow (first slow AFTER last moving)
            ("ACTIVE_RALLY", 0.0, 0.0, 500),
        ],
    )
    sample = ext.flush(t_ms=600)
    assert sample is not None
    # last moving = t=300; first slow after that = t=400 → latency = 100
    assert sample.value == pytest.approx(100.0, abs=1e-12)


# ──────────────────────────── Flush / reset semantics ────────────────────────────


def test_flush_clears_buffer_so_second_flush_is_none() -> None:
    """After flush emits (or clears), second flush returns None."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(
        ext,
        [
            ("ACTIVE_RALLY", 3.0, 0.0, 100),
            ("ACTIVE_RALLY", 0.0, 0.0, 200),
        ],
    )
    first = ext.flush(t_ms=300)
    assert first is not None
    second = ext.flush(t_ms=400)
    assert second is None


def test_reset_clears_buffer() -> None:
    """reset() wipes the buffer; subsequent flush returns None."""
    ext = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(
        ext,
        [
            ("ACTIVE_RALLY", 3.0, 0.0, 100),
            ("ACTIVE_RALLY", 0.0, 0.0, 200),
        ],
    )
    ext.reset()
    assert ext.flush(t_ms=300) is None


def test_flush_returns_signal_sample_with_correct_player_and_name() -> None:
    """Returned SignalSample carries target_player, signal_name, state, timestamp."""
    ext = RecoveryLatency(target_player="B", dependencies={"match_id": "match-xyz"})
    simulate_ticks(
        ext,
        [
            ("ACTIVE_RALLY", 3.0, 0.0, 100),
            ("ACTIVE_RALLY", 0.0, 0.0, 200),
        ],
    )
    sample = ext.flush(t_ms=300)
    assert isinstance(sample, SignalSample)
    assert sample.player == "B"
    assert sample.signal_name == "recovery_latency_ms"
    assert sample.state == "ACTIVE_RALLY"
    assert sample.timestamp_ms == 300
    assert sample.match_id == "match-xyz"
    assert sample.baseline_z_score is None


# ──────────────────────────── Symmetric API (USER-CORRECTION-013) ────────────────────────────


def test_two_instances_accumulate_independently_ignoring_opponent_kalman() -> None:
    """Twin extractors for A and B use only their own target_kalman; opponent is distractor."""
    ext_a = RecoveryLatency(target_player="A", dependencies={"match_id": "m1"})
    ext_b = RecoveryLatency(target_player="B", dependencies={"match_id": "m1"})

    frame = _stub_frame(t_ms=100)
    kalman_a_moving = (0.0, 0.0, 3.0, 0.0)  # A is moving
    kalman_b_still = (0.0, 0.0, 0.0, 0.0)  # B is still

    # Tick 1: A moving, B still
    ext_a.ingest(
        frame=frame,
        target_state="ACTIVE_RALLY",
        opponent_state="ACTIVE_RALLY",
        target_kalman=kalman_a_moving,
        opponent_kalman=kalman_b_still,
        t_ms=100,
    )
    ext_b.ingest(
        frame=frame,
        target_state="ACTIVE_RALLY",
        opponent_state="ACTIVE_RALLY",
        target_kalman=kalman_b_still,  # B's own kalman says still
        opponent_kalman=kalman_a_moving,  # opponent is moving — distractor
        t_ms=100,
    )

    # Tick 2: A decelerates to still
    frame2 = _stub_frame(t_ms=200)
    ext_a.ingest(
        frame=frame2,
        target_state="ACTIVE_RALLY",
        opponent_state="ACTIVE_RALLY",
        target_kalman=(0.0, 0.0, 0.0, 0.0),  # A now still
        opponent_kalman=kalman_b_still,
        t_ms=200,
    )
    ext_b.ingest(
        frame=frame2,
        target_state="ACTIVE_RALLY",
        opponent_state="ACTIVE_RALLY",
        target_kalman=kalman_b_still,  # B still still
        opponent_kalman=(0.0, 0.0, 0.0, 0.0),
        t_ms=200,
    )

    sample_a = ext_a.flush(t_ms=300)
    sample_b = ext_b.flush(t_ms=300)

    # A moved then stilled → recovery latency
    assert sample_a is not None and sample_a.player == "A"
    assert sample_a.value == pytest.approx(100.0, abs=1e-12)
    # B never moved (its own kalman was always still) → None, regardless of opponent
    assert sample_b is None


# ──────────────────────────── USER-CORRECTION-022: Fail-fast dependency lookup ────────────────────────────


def test_missing_match_id_raises_keyerror_on_flush() -> None:
    """If deps lacks 'match_id', flush() with a non-empty buffer must raise KeyError."""
    ext = RecoveryLatency(target_player="A", dependencies={})  # no match_id
    simulate_ticks(
        ext,
        [
            ("ACTIVE_RALLY", 3.0, 0.0, 100),
            ("ACTIVE_RALLY", 0.0, 0.0, 200),
        ],
    )
    with pytest.raises(KeyError, match="match_id"):
        ext.flush(t_ms=300)
