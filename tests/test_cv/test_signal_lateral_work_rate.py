"""Tests for backend/cv/signals/lateral_work_rate.py — p95 |vx| during ACTIVE_RALLY.

Enforces USER-CORRECTION-013 (symmetric API) and USER-CORRECTION-017 (physics guardrail):
- Consumes target_kalman[2] directly (Kalman vx in m/s). No CoM. No CourtMapper projection.
- Buffers |vx| only during ACTIVE_RALLY with non-None target_kalman.
- flush() emits SignalSample with 95th percentile, then CLEARS buffer.

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import numpy as np
import pytest

from backend.cv.signals.lateral_work_rate import LateralWorkRate
from backend.db.schema import FrameKeypoints, PlayerDetection, SignalSample

# ──────────────────────────── Stub frame + simulate helper ────────────────────────────


def _stub_frame(t_ms: int = 0) -> FrameKeypoints:
    """Minimal FrameKeypoints with both players present. Content does not matter;
    LateralWorkRate consumes only target_kalman, never the frame keypoints.
    """
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


def simulate_ticks(ext: LateralWorkRate, ticks_data: list[tuple[str, float | None, float, int]]) -> None:
    """Feed (target_state, vx, vy, t_ms) tuples into ingest().

    opponent_state is fixed to 'DEAD_TIME'; opponent_kalman to None.
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
    assert LateralWorkRate.signal_name == "lateral_work_rate"
    assert LateralWorkRate.required_state == ("ACTIVE_RALLY",)
    assert isinstance(LateralWorkRate.required_state, tuple)


# ──────────────────────────── Gate correctness ────────────────────────────


def test_ingest_during_pre_serve_ritual_is_ignored() -> None:
    """Only ACTIVE_RALLY ticks contribute; PRE_SERVE_RITUAL is dropped."""
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("PRE_SERVE_RITUAL", 2.0, 0.0, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


def test_ingest_during_dead_time_is_ignored() -> None:
    """Only ACTIVE_RALLY ticks contribute; DEAD_TIME is dropped."""
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("DEAD_TIME", 2.0, 0.0, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


def test_ingest_with_none_kalman_is_skipped() -> None:
    """When target_kalman is None (occlusion), the frame contributes nothing."""
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", None, 0.0, t) for t in range(100, 1100, 100)])
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── Math correctness ────────────────────────────


def test_pure_vertical_motion_yields_zero_lateral() -> None:
    """vx=0 everywhere — p95 must be exactly 0.0 regardless of vy magnitude."""
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 0.0, 3.0, t) for t in range(100, 3100, 100)])
    sample = ext.flush(t_ms=3100)
    assert sample is not None
    assert sample.value == pytest.approx(0.0, abs=1e-12)


def test_pure_lateral_motion_yields_p95_of_vx() -> None:
    """p95 of |vx| matches numpy percentile to 1e-9 tolerance."""
    vx_values = [0.2, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5]
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", vx, 0.0, 100 * (i + 1)) for i, vx in enumerate(vx_values)])
    sample = ext.flush(t_ms=100 * (len(vx_values) + 1))
    assert sample is not None
    expected = float(np.percentile([abs(v) for v in vx_values], 95))
    assert sample.value == pytest.approx(expected, abs=1e-9)


def test_absolute_value_of_negative_vx() -> None:
    """A single negative vx yields |vx| as p95 (trivial case: one sample)."""
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", -2.0, 0.0, 100)])
    sample = ext.flush(t_ms=200)
    assert sample is not None
    assert sample.value == pytest.approx(2.0, abs=1e-12)


# ──────────────────────────── Flush / reset semantics ────────────────────────────


def test_flush_empty_buffer_returns_none() -> None:
    """No ingest calls means flush returns None (not a zero-valued sample)."""
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    assert ext.flush(t_ms=1000) is None


def test_flush_returns_signal_sample_with_correct_player_and_name() -> None:
    """Returned SignalSample carries target_player, signal_name, state, timestamp."""
    ext = LateralWorkRate(target_player="B", dependencies={"match_id": "match-xyz"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 1.0, 0.0, 100), ("ACTIVE_RALLY", 2.0, 0.0, 200)])
    sample = ext.flush(t_ms=300)
    assert isinstance(sample, SignalSample)
    assert sample.player == "B"
    assert sample.signal_name == "lateral_work_rate"
    assert sample.state == "ACTIVE_RALLY"
    assert sample.timestamp_ms == 300
    assert sample.match_id == "match-xyz"
    assert sample.baseline_z_score is None


def test_flush_clears_buffer_so_second_flush_is_none() -> None:
    """After flush emits a sample, the buffer is cleared; a second flush returns None."""
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 1.0, 0.0, 100), ("ACTIVE_RALLY", 2.0, 0.0, 200)])
    first = ext.flush(t_ms=300)
    assert first is not None
    second = ext.flush(t_ms=400)
    assert second is None


def test_reset_clears_buffer() -> None:
    """reset() wipes the buffer; subsequent flush returns None."""
    ext = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    simulate_ticks(ext, [("ACTIVE_RALLY", 1.0, 0.0, 100), ("ACTIVE_RALLY", 2.0, 0.0, 200)])
    ext.reset()
    assert ext.flush(t_ms=300) is None


# ──────────────────────────── Symmetric API (USER-CORRECTION-013) ────────────────────────────


def test_two_instances_for_a_and_b_accumulate_independently() -> None:
    """Twin extractors for A and B ingest independent kalman streams; opponent_kalman is ignored."""
    ext_a = LateralWorkRate(target_player="A", dependencies={"match_id": "m1"})
    ext_b = LateralWorkRate(target_player="B", dependencies={"match_id": "m1"})

    # For the same frame, A's target is kalman_a, B's target is kalman_b.
    # Each extractor must use ONLY its own target_kalman; opponent_kalman is a distractor.
    frame = _stub_frame(t_ms=100)
    kalman_a = (0.0, 0.0, 5.0, 0.0)   # player A: vx = 5.0
    kalman_b = (0.0, 0.0, 1.0, 0.0)   # player B: vx = 1.0

    # First tick
    ext_a.ingest(
        frame=frame,
        target_state="ACTIVE_RALLY",
        opponent_state="ACTIVE_RALLY",
        target_kalman=kalman_a,
        opponent_kalman=kalman_b,
        t_ms=100,
    )
    ext_b.ingest(
        frame=frame,
        target_state="ACTIVE_RALLY",
        opponent_state="ACTIVE_RALLY",
        target_kalman=kalman_b,
        opponent_kalman=kalman_a,
        t_ms=100,
    )

    sample_a = ext_a.flush(t_ms=200)
    sample_b = ext_b.flush(t_ms=200)

    assert sample_a is not None and sample_a.player == "A"
    assert sample_b is not None and sample_b.player == "B"
    # A only saw vx=5.0; B only saw vx=1.0. If opponent_kalman leaked into either buffer,
    # the p95 would not be the pure |vx| of the target.
    assert sample_a.value == pytest.approx(5.0, abs=1e-12)
    assert sample_b.value == pytest.approx(1.0, abs=1e-12)
