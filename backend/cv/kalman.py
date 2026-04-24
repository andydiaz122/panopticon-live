"""Physical 2D Kalman tracker for player position in court meters.

Enforces USER-CORRECTION-008: input MUST be court meters (not normalized xyn or pixels).
Output state (x, y, vx, vy) is in (m, m, m/s, m/s), making downstream state-machine
thresholds in m/s physically meaningful.

SP5 10-frame convergence gate: `is_converged` returns False for the first 10 updates.
Signal extractors that depend on velocity/acceleration MUST gate on this.

Occlusion handling: `update(None)` calls predict() without update() — filter coasts at
last known velocity. `is_converged` persists through occlusion.
"""

from __future__ import annotations

import warnings

import numpy as np
from filterpy.kalman import KalmanFilter


def _make_filter(dt: float) -> KalmanFilter:
    """2D constant-velocity Kalman filter. State = [x_m, y_m, vx_mps, vy_mps]."""
    kf = KalmanFilter(dim_x=4, dim_z=2)
    kf.F = np.array(
        [
            [1.0, 0.0, dt, 0.0],
            [0.0, 1.0, 0.0, dt],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    kf.H = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    kf.P *= 5.0
    # Measurement noise: foot-projection is noisy, ~30cm std
    kf.R *= 0.10
    # Process noise: tennis players sprint + decelerate hard; allow reasonable accel
    kf.Q *= 0.05
    return kf


class PhysicalKalman2D:
    """2D constant-velocity Kalman filter operating on court meters (USER-CORRECTION-008).

    Forward pass stores (x, P) snapshots for offline RTS (Rauch-Tung-Striebel) smoothing.
    See PATTERN-053 + GOTCHA-019: precompute.py is offline, so we pay the O(N) memory cost
    for mathematically optimal zero-lag velocities.
    """

    CONVERGENCE_FRAMES: int = 10

    def __init__(self, dt: float = 1.0 / 30.0) -> None:
        if dt <= 0:
            raise ValueError(f"dt must be positive; got {dt}")
        self._kf = _make_filter(dt)
        self._frames_since_init = 0
        self._x_history: list[np.ndarray] = []
        self._p_history: list[np.ndarray] = []

    def update(
        self, measurement_m: tuple[float, float] | None
    ) -> tuple[float, float, float, float]:
        """Advance the filter by one timestep.

        Args:
            measurement_m: (x_m, y_m) in court meters, or None for occlusion (predict-only).

        Returns:
            (x_m, y_m, vx_mps, vy_mps) smoothed state in physical units.
        """
        self._kf.predict()
        if measurement_m is not None:
            # On the first measurement, seed the position state to avoid a huge predict->update jump
            if self._frames_since_init == 0:
                self._kf.x[0, 0] = float(measurement_m[0])
                self._kf.x[1, 0] = float(measurement_m[1])
            self._kf.update(np.array(measurement_m, dtype=float))
        self._frames_since_init += 1
        self._x_history.append(self._kf.x.copy())
        self._p_history.append(self._kf.P.copy())
        x_m, y_m, vx, vy = self._kf.x.flatten().tolist()
        return x_m, y_m, vx, vy

    def rts_smooth(self) -> np.ndarray:
        """Run the Rauch-Tung-Striebel backward pass over stored forward states.

        Offline-only. Returns an (N, 4) array of smoothed (x_m, y_m, vx_mps, vy_mps)
        trajectories. Does not mutate the live posterior — callers may continue using
        update() after smoothing.

        GOTCHA-023: prolonged occlusion can balloon covariance to near-singular values;
        filterpy's matrix inversion may raise LinAlgError OR silently propagate NaN.
        On either failure, this method emits a UserWarning and falls back to the
        flattened forward-pass means (always finite by construction).

        Raises:
            ValueError: if no forward-pass states have been recorded yet.
        """
        if not self._x_history:
            raise ValueError("no forward-pass states recorded; call update() first")
        xs = np.stack(self._x_history)  # (N, 4, 1)
        ps = np.stack(self._p_history)  # (N, 4, 4)
        forward_fallback = xs.reshape(xs.shape[0], -1)

        try:
            smoothed_xs, _p, _k, _pp = self._kf.rts_smoother(xs, ps)
        except np.linalg.LinAlgError as exc:
            warnings.warn(
                f"rts_smoother raised LinAlgError ({exc}); "
                f"falling back to forward-pass means over {xs.shape[0]} frames. "
                "Likely cause: prolonged occlusion blew up covariance.",
                UserWarning,
                stacklevel=2,
            )
            return forward_fallback

        smoothed_flat = smoothed_xs.reshape(smoothed_xs.shape[0], -1)
        if not np.isfinite(smoothed_flat).all():
            warnings.warn(
                f"rts_smoother returned non-finite values over {xs.shape[0]} frames; "
                "falling back to forward-pass means. Likely cause: near-singular covariance.",
                UserWarning,
                stacklevel=2,
            )
            return forward_fallback
        return smoothed_flat

    @property
    def frames_since_init(self) -> int:
        return self._frames_since_init

    @property
    def is_converged(self) -> bool:
        """True after the Kalman filter has settled. Gate velocity-dependent signals on this (SP5)."""
        return self._frames_since_init >= self.CONVERGENCE_FRAMES

    @property
    def state(self) -> tuple[float, float, float, float]:
        """Current (x_m, y_m, vx_mps, vy_mps) without advancing the filter."""
        x_m, y_m, vx, vy = self._kf.x.flatten().tolist()
        return x_m, y_m, vx, vy
