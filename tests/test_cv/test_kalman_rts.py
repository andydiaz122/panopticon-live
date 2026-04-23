"""Tests for the RTS (Rauch-Tung-Striebel) smoother on PhysicalKalman2D.

PATTERN-053 + GOTCHA-019: precompute.py is an OFFLINE batch pipeline, so we have
access to all future states. The forward Kalman pass trusts only past measurements;
the RTS backward pass refines every state using future info, producing mathematically
optimal, zero-lag smoothed trajectories.

Contract under test:
  - PhysicalKalman2D records (x, P) after every update() call (forward pass).
  - PhysicalKalman2D.rts_smooth() returns an (N, 4) ndarray of smoothed states
    in the same (x_m, y_m, vx_mps, vy_mps) units as forward output.
  - Smoothed velocities have strictly lower error AND lower variance than the
    forward-only velocities against a known ground-truth constant-velocity path.
  - rts_smooth() does NOT mutate the live filter state (immutability rule).

Written FIRST per TDD discipline — this file is expected to fail until rts_smooth
is implemented on PhysicalKalman2D.
"""

from __future__ import annotations

import numpy as np
import pytest

from backend.cv.kalman import PhysicalKalman2D


# ──────────────────────────── Shape + basic contract ────────────────────────────


def test_rts_smooth_returns_shape_n_by_4_after_updates() -> None:
    kf = PhysicalKalman2D(dt=1 / 30.0)
    for i in range(20):
        kf.update((i * 0.05, 0.0))

    smoothed = kf.rts_smooth()

    assert isinstance(smoothed, np.ndarray)
    assert smoothed.shape == (20, 4), f"Expected (20, 4); got {smoothed.shape}"


def test_rts_smooth_before_any_updates_raises() -> None:
    kf = PhysicalKalman2D(dt=1 / 30.0)
    with pytest.raises(ValueError, match="no forward-pass states"):
        kf.rts_smooth()


def test_rts_smooth_does_not_mutate_live_filter_state() -> None:
    """Calling rts_smooth must not advance the forward filter or corrupt its posterior."""
    kf = PhysicalKalman2D(dt=1 / 30.0)
    for i in range(15):
        kf.update((i * 0.05, 0.0))
    live_state_before = kf.state
    frames_before = kf.frames_since_init

    _ = kf.rts_smooth()

    assert kf.state == live_state_before, "rts_smooth mutated the live posterior state"
    assert kf.frames_since_init == frames_before


# ──────────────────────────── Optimality vs. forward-only ────────────────────────────


def _noisy_constant_velocity_path(
    n_frames: int = 90,
    vx_true: float = 2.0,
    vy_true: float = 0.0,
    noise_std_m: float = 0.10,
    dt: float = 1 / 30.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate ground-truth + noisy measurements for a CV trajectory in meters."""
    t = np.arange(n_frames) * dt
    true_xy = np.stack([vx_true * t, vy_true * t], axis=1)  # (N, 2)
    noise = np.random.normal(0.0, noise_std_m, size=true_xy.shape)
    return true_xy, true_xy + noise


def test_rts_smoothed_velocity_beats_forward_only_rmse() -> None:
    """The backward pass MUST reduce velocity RMSE against ground truth.

    Core claim of PATTERN-053: RTS is strictly superior for offline smoothing.
    """
    n = 90
    vx_true, vy_true = 2.0, 0.0
    _true_xy, measurements = _noisy_constant_velocity_path(
        n_frames=n, vx_true=vx_true, vy_true=vy_true, noise_std_m=0.10
    )

    kf = PhysicalKalman2D(dt=1 / 30.0)
    forward_velocities = np.empty((n, 2))
    for i, m in enumerate(measurements):
        _x, _y, vx, vy = kf.update((float(m[0]), float(m[1])))
        forward_velocities[i] = (vx, vy)

    smoothed = kf.rts_smooth()
    smoothed_velocities = smoothed[:, 2:4]

    true_velocity = np.array([vx_true, vy_true])
    fwd_rmse = float(np.sqrt(np.mean((forward_velocities - true_velocity) ** 2)))
    rts_rmse = float(np.sqrt(np.mean((smoothed_velocities - true_velocity) ** 2)))

    assert rts_rmse < fwd_rmse, (
        f"RTS should reduce velocity RMSE vs. forward-only. "
        f"forward={fwd_rmse:.4f} rts={rts_rmse:.4f}"
    )


def test_rts_smoothed_velocity_has_lower_jitter_than_forward_only() -> None:
    """Step-to-step velocity variance should drop — the visible demo benefit."""
    n = 90
    _true_xy, measurements = _noisy_constant_velocity_path(
        n_frames=n, vx_true=2.0, vy_true=0.0, noise_std_m=0.10
    )

    kf = PhysicalKalman2D(dt=1 / 30.0)
    forward_velocities = np.empty((n, 2))
    for i, m in enumerate(measurements):
        _x, _y, vx, vy = kf.update((float(m[0]), float(m[1])))
        forward_velocities[i] = (vx, vy)

    smoothed = kf.rts_smooth()
    smoothed_velocities = smoothed[:, 2:4]

    # Ignore the first 10 frames (Kalman convergence zone, SP5)
    fwd_var = float(np.var(forward_velocities[10:], axis=0).sum())
    rts_var = float(np.var(smoothed_velocities[10:], axis=0).sum())

    assert rts_var < fwd_var, (
        f"RTS velocities should have lower variance than forward-only. "
        f"forward_var={fwd_var:.5f} rts_var={rts_var:.5f}"
    )


def test_rts_smoothed_positions_track_ground_truth() -> None:
    """Smoothed positions should be within a few cm of ground truth on a clean CV path."""
    n = 90
    true_xy, measurements = _noisy_constant_velocity_path(
        n_frames=n, vx_true=2.0, vy_true=0.5, noise_std_m=0.10
    )

    kf = PhysicalKalman2D(dt=1 / 30.0)
    for m in measurements:
        kf.update((float(m[0]), float(m[1])))

    smoothed = kf.rts_smooth()
    smoothed_positions = smoothed[:, 0:2]

    pos_rmse = float(np.sqrt(np.mean((smoothed_positions - true_xy) ** 2)))
    assert pos_rmse < 0.10, (
        f"Smoothed-position RMSE should be under 10cm on clean CV path; got {pos_rmse:.3f} m"
    )


# ──────────────────────────── Occlusion interaction ────────────────────────────


def test_rts_smooth_handles_mid_trajectory_occlusion() -> None:
    """Occluded frames (update(None)) should still produce sensible smoothed states."""
    kf = PhysicalKalman2D(dt=1 / 30.0)
    # 30 frames moving at 2 m/s
    for i in range(30):
        kf.update((i * (2.0 / 30.0), 0.0))
    # 5 occluded frames
    for _ in range(5):
        kf.update(None)
    # 30 more measured frames continuing the trajectory
    for i in range(30):
        x_true = (35 + i) * (2.0 / 30.0)
        kf.update((x_true, 0.0))

    smoothed = kf.rts_smooth()
    assert smoothed.shape == (65, 4)

    # The smoothed velocity across the occlusion window should remain close to 2 m/s
    # (RTS has future info — it KNOWS the player kept moving)
    occlusion_vx = smoothed[30:35, 2]
    assert np.all(np.abs(occlusion_vx - 2.0) < 0.5), (
        f"Occluded-frame smoothed vx should be ~2.0 m/s; got {occlusion_vx}"
    )


# ──────────────────────────── Determinism ────────────────────────────


# ──────────────────────────── NaN / singular-matrix robustness (GOTCHA-023) ────────────────────────────


def test_rts_smooth_handles_prolonged_occlusion_without_nan() -> None:
    """A 10s dead-zone (300 occluded frames) must NOT produce NaN in the smoothed output.

    Covariance grows unboundedly during pure prediction. At realistic clip durations
    (≤ few minutes) this stays numerically stable, but the rts_smooth contract is:
    if we DO cross into instability, we fall back safely. This test pins the normal case.
    """
    kf = PhysicalKalman2D(dt=1 / 30.0)
    for i in range(5):
        kf.update((float(i * 0.05), 0.0))
    for _ in range(300):
        kf.update(None)
    # Brief recovery so the FSM analogue would have a valid closing measurement
    for i in range(5):
        kf.update((5 * 0.05 + i * 0.05, 0.0))

    smoothed = kf.rts_smooth()
    assert smoothed.shape == (310, 4)
    assert np.isfinite(smoothed).all(), "Smoothed trajectory contains NaN/inf after long occlusion"


def test_rts_smooth_falls_back_to_forward_means_on_linalgerror(
    recwarn: pytest.WarningsRecorder, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GOTCHA-023: if rts_smoother raises LinAlgError (singular P from occlusion blow-up),
    rts_smooth must NOT propagate the error. Contract:
      - catch LinAlgError
      - emit a UserWarning mentioning 'rts_smoother'
      - return the flattened FORWARD-PASS means (always finite).
    """
    kf = PhysicalKalman2D(dt=1 / 30.0)
    for i in range(30):
        kf.update((float(i * 0.05), 0.0))

    expected_forward_means = np.stack([x.flatten() for x in kf._x_history])

    def _raise_linalg_error(*_args: object, **_kwargs: object) -> None:
        raise np.linalg.LinAlgError("singular matrix (simulated occlusion blow-up)")

    monkeypatch.setattr(kf._kf, "rts_smoother", _raise_linalg_error)

    smoothed = kf.rts_smooth()

    assert smoothed.shape == (30, 4)
    assert np.isfinite(smoothed).all(), "Fallback output must be fully finite"
    np.testing.assert_array_equal(smoothed, expected_forward_means)
    assert any(
        issubclass(w.category, UserWarning)
        and "rts_smoother" in str(w.message).lower()
        for w in recwarn.list
    ), "Expected a UserWarning mentioning rts_smoother fallback"


def test_rts_smooth_falls_back_when_output_contains_nan(
    recwarn: pytest.WarningsRecorder, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GOTCHA-023 silent-NaN path: if rts_smoother returns WITHOUT raising but any
    element is non-finite (NaN/inf), rts_smooth must treat it as failure and fall back.

    This is the more insidious failure mode — numpy's behavior with near-singular matrices
    is to propagate NaN rather than raise.
    """
    kf = PhysicalKalman2D(dt=1 / 30.0)
    for i in range(20):
        kf.update((float(i * 0.05), 0.0))

    expected_forward_means = np.stack([x.flatten() for x in kf._x_history])

    def _return_nan_output(xs: np.ndarray, ps: np.ndarray) -> tuple[np.ndarray, ...]:
        nan_xs = np.full_like(xs, np.nan)
        return nan_xs, ps, np.zeros_like(ps), ps

    monkeypatch.setattr(kf._kf, "rts_smoother", _return_nan_output)

    smoothed = kf.rts_smooth()

    assert smoothed.shape == expected_forward_means.shape
    assert np.isfinite(smoothed).all(), "Fallback must produce all-finite output"
    np.testing.assert_array_equal(smoothed, expected_forward_means)
    assert any(
        issubclass(w.category, UserWarning)
        and "rts_smoother" in str(w.message).lower()
        for w in recwarn.list
    ), "Expected a UserWarning when rts_smoother output had non-finite values"


# ──────────────────────────── Determinism ────────────────────────────


def test_rts_smooth_is_deterministic_for_identical_inputs() -> None:
    """Two identical runs with the same seed must produce identical smoothed outputs."""

    def run_once() -> np.ndarray:
        np.random.seed(1234)
        _true_xy, measurements = _noisy_constant_velocity_path(n_frames=40, noise_std_m=0.1)
        kf = PhysicalKalman2D(dt=1 / 30.0)
        for m in measurements:
            kf.update((float(m[0]), float(m[1])))
        return kf.rts_smooth()

    a = run_once()
    b = run_once()
    np.testing.assert_array_equal(a, b)
