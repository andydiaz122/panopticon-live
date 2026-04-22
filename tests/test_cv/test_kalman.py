"""Tests for backend/cv/kalman.py.

Enforces USER-CORRECTION-008 (Kalman operates on physical meters, output velocity in m/s)
+ SP5 10-frame convergence gate + occlusion coasting.

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import math

import pytest

from backend.cv.kalman import PhysicalKalman2D

# ──────────────────────────── Convergence gate (SP5) ────────────────────────────


def test_not_converged_initially() -> None:
    kf = PhysicalKalman2D(dt=1 / 30.0)
    assert kf.is_converged is False
    assert kf.frames_since_init == 0


def test_converged_after_10_updates() -> None:
    kf = PhysicalKalman2D(dt=1 / 30.0)
    for _ in range(9):
        kf.update((0.0, 0.0))
        assert kf.is_converged is False
    kf.update((0.0, 0.0))
    assert kf.is_converged is True
    assert kf.frames_since_init == 10


def test_convergence_persists_through_occlusion() -> None:
    """Occlusion (None measurements) should NOT reset convergence."""
    kf = PhysicalKalman2D(dt=1 / 30.0)
    for _ in range(11):
        kf.update((0.0, 0.0))
    assert kf.is_converged is True

    # 5 occlusion frames
    for _ in range(5):
        kf.update(None)
    assert kf.is_converged is True


# ──────────────────────────── Physical unit sanity ────────────────────────────


def test_linear_motion_converges_to_true_velocity_in_mps() -> None:
    """Feed 30 frames of (t, t) meters at 30 FPS => velocity is (1, 1) m/s per unit step.

    At 30 FPS, a 1-meter step between consecutive frames implies 30 m/s which is far too fast.
    So instead: step 0.067 m (= 2 m/s at 30 FPS) each frame.
    """
    kf = PhysicalKalman2D(dt=1 / 30.0)
    dx = dy = 2.0 / 30.0  # 2 m/s horizontal+vertical

    vx: float = 0.0
    vy: float = 0.0
    for i in range(60):
        measurement = (i * dx, i * dy)
        _x_m, _y_m, vx, vy = kf.update(measurement)

    # After 60 frames (2 seconds at 30 FPS) the Kalman should have converged
    assert vx == pytest.approx(2.0, abs=0.2), f"Expected vx ~ 2.0 m/s, got {vx}"
    assert vy == pytest.approx(2.0, abs=0.2), f"Expected vy ~ 2.0 m/s, got {vy}"


def test_stationary_player_has_near_zero_velocity() -> None:
    kf = PhysicalKalman2D(dt=1 / 30.0)
    for _ in range(60):
        _, _, vx, vy = kf.update((5.0, 15.0))
    speed = math.hypot(vx, vy)
    assert speed < 0.1, f"Stationary player should have speed < 0.1 m/s, got {speed}"


def test_step_measurement_is_smoothed() -> None:
    """A discontinuous jump should be smoothed by the filter (low-pass behavior)."""
    kf = PhysicalKalman2D(dt=1 / 30.0)
    # 30 frames at (0, 0)
    for _ in range(30):
        kf.update((0.0, 0.0))
    # Then a sudden jump to (5, 5); filter should NOT teleport there
    x, y, _, _ = kf.update((5.0, 5.0))
    assert x < 5.0, f"Filter should not fully commit to step in one frame; got x={x}"
    assert y < 5.0
    # After many more frames of steady (5, 5), it should catch up
    for _ in range(60):
        x, y, _, _ = kf.update((5.0, 5.0))
    assert x == pytest.approx(5.0, abs=0.1)
    assert y == pytest.approx(5.0, abs=0.1)


# ──────────────────────────── Occlusion coasting ────────────────────────────


def test_occlusion_coasts_at_last_velocity() -> None:
    """None measurements should extrapolate at last known velocity (predict-only)."""
    kf = PhysicalKalman2D(dt=1 / 30.0)
    # Build up steady +1 m/s velocity in X
    for i in range(60):
        kf.update((i * (1.0 / 30.0), 0.0))
    x_before, _, vx_before, _ = kf.update((60 * (1.0 / 30.0), 0.0))
    assert vx_before == pytest.approx(1.0, abs=0.2)

    # 5 occlusion frames — filter extrapolates
    for _ in range(5):
        x_after, _, _vx_after, _ = kf.update(None)

    # Position should have advanced approximately 5 * dt * vx_before = 5 * (1/30) * 1.0 ~ 0.167m
    # But Kalman predict doesn't change velocity in constant-velocity model; position advances
    assert x_after > x_before, "Position should advance during occlusion coasting"


# ──────────────────────────── Input must be meters, not xyn ────────────────────────────


def test_input_units_are_assumed_meters_not_normalized() -> None:
    """USER-CORRECTION-008 regression guard.

    The contract is: input is in court meters (typically 0-24 range). If a caller naively
    feeds normalized xyn (0-1), the velocity will be in units/second, NOT m/s, and state
    machine thresholds (0.2 m/s) will never fire.

    This test makes the contract explicit — it's documentation, not runtime enforcement.
    It passes but the assertion message is the point.
    """
    kf = PhysicalKalman2D(dt=1 / 30.0)
    # Simulate running a player from baseline to net (0 -> 11 meters in 3 seconds = ~3.67 m/s)
    for i in range(90):
        kf.update((0.0, i * (11.0 / 90.0)))
    _, _, vx, vy = kf.update((0.0, 11.0))
    speed = math.hypot(vx, vy)
    # If input was meters (correct), speed ~ 3.67 m/s
    # If input had been normalized xyn (fed y_norm=0..0.457 over 3s at 30fps), speed would be ~0.15 (unitless)
    # We're asserting the input-IS-meters contract: speed should be in human-sprint range
    assert 2.0 < speed < 6.0, (
        f"Kalman speed {speed:.2f} m/s suggests input is not meters. "
        "USER-CORRECTION-008: must convert via CourtMapper.to_court_meters BEFORE update."
    )
