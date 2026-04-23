"""Tests for backend/cv/thresholds.py — the single source of truth for
kinematic + pose-confidence + numerical-guard constants (PATTERN-057).
"""

from __future__ import annotations

import pytest

from backend.cv.thresholds import KINEMATIC, NUMERIC, POSE_CONF


def test_kinematic_thresholds_are_frozen() -> None:
    """Frozen dataclass — prevents accidental mutation across modules."""
    with pytest.raises(Exception):  # FrozenInstanceError
        KINEMATIC.active_rally_speed_mps = 99.9  # type: ignore[misc]


def test_kinematic_thresholds_physical_ordering() -> None:
    """Dead-time speed must be < rally-entry speed must be < recovery-onset speed.
    Violating this ordering creates logical contradictions in the FSM.
    """
    assert KINEMATIC.dead_time_speed_mps < KINEMATIC.active_rally_speed_mps
    assert KINEMATIC.active_rally_speed_mps < KINEMATIC.recovery_speed_mps


def test_kinematic_thresholds_are_positive_mps() -> None:
    assert KINEMATIC.active_rally_speed_mps > 0
    assert KINEMATIC.dead_time_speed_mps > 0
    assert KINEMATIC.recovery_speed_mps > 0
    assert KINEMATIC.consecutive_frames_to_rally > 0
    assert KINEMATIC.consecutive_frames_to_dead_time > 0


def test_pose_confidence_is_in_unit_interval() -> None:
    assert 0.0 <= POSE_CONF.keypoint_confidence_min <= 1.0


def test_numerical_guards_are_positive_but_tiny() -> None:
    """Variance floors / amplitude floors must be strictly positive; if they're
    too large they'd swallow real signal."""
    assert 0 < NUMERIC.variance_floor < 1e-3
    assert 0 < NUMERIC.torso_collapse_floor < 1e-3
    assert 0 < NUMERIC.serve_toss_amplitude_floor < 1.0
    assert 0 < NUMERIC.bounce_amplitude_rel < 1.0


def test_post_rts_calibration_flag_defaults_false() -> None:
    """Regression guard: don't silently flip `post_rts_calibrated` without the
    empirical evidence noted in MEMORY.md / FORANDREW.md."""
    assert KINEMATIC.post_rts_calibrated is False, (
        "post_rts_calibrated must only flip to True after empirical re-tuning "
        "on real post-RTS telemetry. See PATTERN-057."
    )


def test_current_values_match_legacy_fsm_values() -> None:
    """Until post-RTS re-tuning produces evidence for a change, the new module
    MUST emit the exact same values the FSM was running on pre-refactor. This
    prevents stealth behavioral drift masquerading as a refactor."""
    assert KINEMATIC.active_rally_speed_mps == 0.2
    assert KINEMATIC.dead_time_speed_mps == 0.05
    assert KINEMATIC.recovery_speed_mps == 0.5
    assert KINEMATIC.consecutive_frames_to_rally == 5
    assert KINEMATIC.consecutive_frames_to_dead_time == 15
    assert POSE_CONF.keypoint_confidence_min == 0.3
