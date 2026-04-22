"""Tests for backend/cv/signals/baseline_retreat.py — mean metres behind own baseline.

Enforces USER-CORRECTION-017 (no CourtMapper — Kalman y IS the ground-plane
court-meters coordinate), USER-CORRECTION-021 (asymmetric baseline geometry:
Player A's baseline at y=SINGLES_COURT_LENGTH_M, Player B's at y=0.0), and
USER-CORRECTION-022 (fail-fast — `self.deps["match_id"]` must raise KeyError
when missing).

Retreat contract (clamped to zero inside the court):
- Player A: retreat_m = max(0.0, y - SINGLES_COURT_LENGTH_M)
- Player B: retreat_m = max(0.0, -y)

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import pytest

from backend.cv.signals.baseline_retreat import BaselineRetreat
from backend.db.schema import SINGLES_COURT_LENGTH_M, FrameKeypoints, PlayerDetection, SignalSample

# ──────────────────────────── Frame stub + simulate helper ────────────────────────────


def _stub_frame(t_ms: int = 0) -> FrameKeypoints:
    """Minimal FrameKeypoints — BaselineRetreat reads ONLY target_kalman, never keypoints."""
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


def simulate_ticks(ext: BaselineRetreat, ticks_data: list[tuple[str, float | None, int]]) -> None:
    """Feed (target_state, y_m, t_ms) tuples into ingest().

    target_kalman = (0.0, y_m, 0.0, 0.0) — only y matters for this signal. If y_m is None,
    target_kalman is None (simulates occlusion).
    """
    for target_state, y_m, t_ms in ticks_data:
        target_kalman = None if y_m is None else (0.0, y_m, 0.0, 0.0)
        ext.ingest(
            frame=_stub_frame(t_ms),
            target_state=target_state,  # type: ignore[arg-type]
            opponent_state="DEAD_TIME",
            target_kalman=target_kalman,
            opponent_kalman=None,
            t_ms=t_ms,
        )


# ──────────────────────────── 1. Class metadata ────────────────────────────


def test_class_attributes_signal_name_and_required_state() -> None:
    """Class-level wiring must match the SignalName literal + ACTIVE_RALLY gate."""
    assert BaselineRetreat.signal_name == "baseline_retreat_distance_m"
    assert BaselineRetreat.required_state == ("ACTIVE_RALLY",)
    assert isinstance(BaselineRetreat.required_state, tuple)


# ──────────────────────────── 2. Non-rally state ignored ────────────────────────────


def test_pre_serve_ritual_state_is_ignored() -> None:
    """Only ACTIVE_RALLY ticks contribute; PRE_SERVE_RITUAL is dropped."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("PRE_SERVE_RITUAL", 25.0, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


def test_dead_time_state_is_ignored() -> None:
    """Only ACTIVE_RALLY ticks contribute; DEAD_TIME is dropped."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("DEAD_TIME", 25.0, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── 3. None kalman skipped ────────────────────────────


def test_none_kalman_is_skipped() -> None:
    """When target_kalman is None (occluded), nothing is appended; flush returns None."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", None, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── 4. Player A inside the court → 0 retreat ────────────────────────────


def test_player_a_inside_court_retreat_is_zero() -> None:
    """Player A at y=20.0 is inside the court (baseline at 23.77) — retreat clamped to 0."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 20.0, t) for t in range(100, 600, 100)])
    sample = ext.flush(t_ms=700)
    assert sample is not None
    assert sample.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── 5. Player A behind baseline → positive retreat ────────────────────────────


def test_player_a_behind_baseline_retreat_is_positive() -> None:
    """Player A at y=25.0 is behind baseline — retreat = 25.0 - 23.77 = 1.23."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 25.0, t) for t in range(100, 600, 100)])
    sample = ext.flush(t_ms=700)
    assert sample is not None
    expected = 25.0 - SINGLES_COURT_LENGTH_M
    assert sample.value == pytest.approx(expected, abs=1e-9)


# ──────────────────────────── 6. Player A on baseline → 0 ────────────────────────────


def test_player_a_exactly_on_baseline_retreat_is_zero() -> None:
    """Player A standing exactly on y=23.77 — retreat = 0 (boundary condition)."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", SINGLES_COURT_LENGTH_M, t) for t in range(100, 600, 100)])
    sample = ext.flush(t_ms=700)
    assert sample is not None
    assert sample.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── 7. Player B inside the court → 0 ────────────────────────────


def test_player_b_inside_court_retreat_is_zero() -> None:
    """Player B at y=3.0 is inside the court (baseline at 0.0) — retreat clamped to 0."""
    ext = BaselineRetreat(target_player="B", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 3.0, t) for t in range(100, 600, 100)])
    sample = ext.flush(t_ms=700)
    assert sample is not None
    assert sample.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── 8. Player B behind baseline → positive retreat ────────────────────────────


def test_player_b_behind_baseline_retreat_is_positive() -> None:
    """Player B at y=-1.5 — retreat = max(0, -(-1.5)) = 1.5."""
    ext = BaselineRetreat(target_player="B", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", -1.5, t) for t in range(100, 600, 100)])
    sample = ext.flush(t_ms=700)
    assert sample is not None
    assert sample.value == pytest.approx(1.5, abs=1e-9)


# ──────────────────────────── 9. Player B on baseline → 0 ────────────────────────────


def test_player_b_exactly_on_baseline_retreat_is_zero() -> None:
    """Player B standing exactly on y=0.0 — retreat = 0 (boundary condition)."""
    ext = BaselineRetreat(target_player="B", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 0.0, t) for t in range(100, 600, 100)])
    sample = ext.flush(t_ms=700)
    assert sample is not None
    assert sample.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── 10. Mean of multiple values ────────────────────────────


def test_player_a_mean_of_sequence() -> None:
    """A with y sequence [24.0, 24.5, 25.0] → retreats [0.23, 0.73, 1.23] → mean ≈ 0.73."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(
        ext,
        [
            ("ACTIVE_RALLY", 24.0, 100),
            ("ACTIVE_RALLY", 24.5, 200),
            ("ACTIVE_RALLY", 25.0, 300),
        ],
    )
    sample = ext.flush(t_ms=400)
    assert sample is not None
    expected = (
        (24.0 - SINGLES_COURT_LENGTH_M)
        + (24.5 - SINGLES_COURT_LENGTH_M)
        + (25.0 - SINGLES_COURT_LENGTH_M)
    ) / 3.0
    assert sample.value == pytest.approx(expected, abs=1e-9)


# ──────────────────────────── 11. Symmetric A/B: asymmetric geometry ────────────────────────────


def test_a_and_b_produce_different_values_for_same_kalman_sequence() -> None:
    """Same y-values fed to A and B should produce DIFFERENT retreats because their
    baselines are at opposite ends of the court. Asymmetric geometry (USER-CORRECTION-021).
    """
    ext_a = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    ext_b = BaselineRetreat(target_player="B", dependencies={"match_id": "m1"})

    # y=25.0 → A's retreat = 25 - 23.77 = 1.23; B's retreat = max(0, -25) = 0.
    y_values = [25.0, 25.0, 25.0]
    for i, y in enumerate(y_values):
        kalman = (0.0, y, 0.0, 0.0)
        ext_a.ingest(
            frame=_stub_frame(100 * (i + 1)),
            target_state="ACTIVE_RALLY",
            opponent_state="ACTIVE_RALLY",
            target_kalman=kalman,
            opponent_kalman=None,
            t_ms=100 * (i + 1),
        )
        ext_b.ingest(
            frame=_stub_frame(100 * (i + 1)),
            target_state="ACTIVE_RALLY",
            opponent_state="ACTIVE_RALLY",
            target_kalman=kalman,
            opponent_kalman=None,
            t_ms=100 * (i + 1),
        )

    sample_a = ext_a.flush(t_ms=500)
    sample_b = ext_b.flush(t_ms=500)
    assert sample_a is not None and sample_a.player == "A"
    assert sample_b is not None and sample_b.player == "B"
    assert sample_a.value == pytest.approx(25.0 - SINGLES_COURT_LENGTH_M, abs=1e-9)
    assert sample_b.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── 12. Empty buffer flush → None ────────────────────────────


def test_flush_with_empty_buffer_returns_none() -> None:
    """No ingests ever → flush returns None (not a zero-valued sample)."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    assert ext.flush(t_ms=1000) is None


# ──────────────────────────── 13. Flush clears the buffer ────────────────────────────


def test_flush_clears_buffer_so_second_flush_returns_none() -> None:
    """After flush emits, the buffer is cleared; a second flush returns None."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 25.0, 100), ("ACTIVE_RALLY", 25.0, 200)])
    first = ext.flush(t_ms=300)
    assert first is not None
    second = ext.flush(t_ms=400)
    assert second is None


# ──────────────────────────── 14. reset() clears the buffer ────────────────────────────


def test_reset_clears_buffer() -> None:
    """reset() wipes the buffer; subsequent flush returns None."""
    ext = BaselineRetreat(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 25.0, 100), ("ACTIVE_RALLY", 25.0, 200)])
    ext.reset()
    assert ext.flush(t_ms=300) is None


# ──────────────────────────── 15. Fail-fast missing match_id → KeyError ────────────────────────────


def test_missing_match_id_raises_keyerror_on_flush() -> None:
    """USER-CORRECTION-022: missing match_id must raise KeyError on flush (never silent default)."""
    ext = BaselineRetreat(target_player="A", dependencies={})  # no match_id
    simulate_ticks(ext, [("ACTIVE_RALLY", 25.0, 100)])
    with pytest.raises(KeyError, match="match_id"):
        ext.flush(t_ms=200)


# ──────────────────────────── 16. Returned SignalSample field correctness ────────────────────────────


def test_returned_signal_sample_has_correct_fields() -> None:
    """Emitted SignalSample carries target_player, signal_name, state, timestamp, match_id."""
    ext = BaselineRetreat(target_player="B", dependencies={"match_id": "match-xyz"})
    simulate_ticks(ext, [("ACTIVE_RALLY", -2.0, 100), ("ACTIVE_RALLY", -2.0, 200)])
    sample = ext.flush(t_ms=300)
    assert isinstance(sample, SignalSample)
    assert sample.player == "B"
    assert sample.signal_name == "baseline_retreat_distance_m"
    assert sample.state == "ACTIVE_RALLY"
    assert sample.timestamp_ms == 300
    assert sample.match_id == "match-xyz"
    assert sample.baseline_z_score is None
    assert sample.value == pytest.approx(2.0, abs=1e-9)
