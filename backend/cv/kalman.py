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
    """2D constant-velocity Kalman filter operating on court meters (USER-CORRECTION-008)."""

    CONVERGENCE_FRAMES: int = 10

    def __init__(self, dt: float = 1.0 / 30.0) -> None:
        if dt <= 0:
            raise ValueError(f"dt must be positive; got {dt}")
        self._kf = _make_filter(dt)
        self._frames_since_init = 0

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
        x_m, y_m, vx, vy = self._kf.x.flatten().tolist()
        return x_m, y_m, vx, vy

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
