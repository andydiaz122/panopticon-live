---
name: physical-kalman-tracking
description: The "Kalman filter operates on physical court meters, not screen-normalized coords" invariant for PANOPTICON LIVE. Use when building or reviewing backend/cv/kalman.py or any code that feeds keypoints into the Kalman tracker. Enforces unit consistency with the state machine's m/s thresholds and the 10-frame convergence gate.
---

# Physical Kalman Tracking

The Kalman filter is the spine between the raw CV pipeline and every downstream physical-measurement signal. Its unit system is load-bearing.

## The Unit Invariant (non-negotiable)

**Kalman filter operates on (x_m, y_m) in court meters. Its velocity state (vx, vy) is in meters per second. Period.**

If normalized screen coords leak in, every downstream m/s threshold silently collapses:
- State machine `speed > 0.2 m/s`: never fires
- `recovery_latency` `|v| < 0.5 m/s`: never fires
- `lateral_work_rate` p95: produces meaningless "screen-percentages per second" values

## The Canonical Pipeline

```
YOLO .xyn (normalized [0,1])
    |
    v
feet_mid_xyn = robust_foot_point(kp_xyn, conf_xyn)
    # USER-CORRECTION-003 ankle -> knee -> hip fallback when conf < 0.3
    |
    v
feet_mid_m = court_mapper.to_court_meters(feet_mid_xyn)
    # USER-CORRECTION-005 backend un-normalizes before cv2.getPerspectiveTransform
    # Returns None if off-court
    |
    v
if feet_mid_m is None:
    kalman.predict()                 # coast, no update
else:
    kalman.update(feet_mid_m)        # USER-CORRECTION-008 input must be meters
    |
    v
x_m, y_m, vx_mps, vy_mps = kalman.state
    |
    v
speed_mps = math.hypot(vx_mps, vy_mps)   # USER-CORRECTION-009: 2D speed, not |vy|
    |
    v
state_machine.update(speed_mps, bounce_detected, t_ms)
```

## filterpy Wiring

```python
from filterpy.kalman import KalmanFilter
import numpy as np

def make_kalman_2d_physical(dt: float = 1 / 30.0) -> KalmanFilter:
    """2D constant-velocity filter. Input and state are in court meters; dt is seconds-per-frame.

    State vector: [x_m, y_m, vx_mps, vy_mps]
    Measurement: [x_m, y_m]

    Q tuned for human-scale tennis motion; R for noisy foot-tracking observations.
    """
    kf = KalmanFilter(dim_x=4, dim_z=2)
    kf.F = np.array(
        [
            [1.0, 0.0, dt,  0.0],
            [0.0, 1.0, 0.0, dt ],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    kf.H = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ]
    )
    kf.P *= 5.0            # initial covariance
    kf.R *= 0.10           # measurement noise in m^2 (~30 cm std on foot projection)
    kf.Q *= 0.05           # process noise in m^2 (tennis sprints: large accel possible)
    return kf
```

## 10-Frame Convergence Gate (SP5)

The first ~10 frames after initialization have noisy velocity estimates. Downstream signals that depend on velocity or acceleration MUST gate on convergence.

```python
class PhysicalKalman2D:
    def __init__(self, dt: float = 1 / 30.0) -> None:
        self._kf = make_kalman_2d_physical(dt)
        self._frames_since_init = 0

    def update(self, measurement_m: tuple[float, float] | None) -> tuple[float, float, float, float]:
        self._kf.predict()
        if measurement_m is not None:
            self._kf.update(np.array(measurement_m, dtype=float))
        self._frames_since_init += 1
        x_m, y_m, vx, vy = self._kf.x.flatten().tolist()
        return x_m, y_m, vx, vy

    @property
    def is_converged(self) -> bool:
        return self._frames_since_init >= 10
```

Consumers:
```python
# In recovery_latency extractor
if not kalman.is_converged:
    return None  # refuse to emit until filter has settled
```

## Occlusion Coasting

When the measurement is `None` (player off-camera, obscured, YOLO drop):
- Call `kf.predict()` only — no `update()`
- Filter extrapolates at last known velocity
- Do NOT reset `_frames_since_init` — convergence persists through brief occlusions
- Reset occurs only when a new player instance is created (e.g., reassignment after extended absence)

## Instance Lifecycle (per player)

- One `PhysicalKalman2D` per `PlayerSide` (A, B) for the duration of a clip
- DO NOT create a new instance on every frame (that resets convergence every time)
- DO NOT share a single instance across both players (state would mix)
- If Player B is absent for >150 frames (5 seconds at 30 FPS), consider re-initializing their Kalman — but for the hackathon's curated UTR clips, this rarely happens

## Test-Forensic-Validator Requirements

- Synthetic linear motion: feed 30 frames of `(t, t)` meter updates at 2 m/s → smoothed velocity converges to `(2.0, 2.0)` within 10 frames
- Step measurement: a discontinuous jump → filter smooths the step (low-pass)
- Occlusion coasting: 5 consecutive `None` measurements → position extrapolates linearly, `is_converged` remains True
- Convergence gate: `is_converged` is False for updates 1-9, True from update 10 onward
- Unit regression: feeding normalized xyn values and asserting state is in meters — MUST FAIL. This test documents that we never regress.

## Integration with cv-pipeline-engineer Agent

This skill is canonical for any `kalman.py`-touching work. Reference explicitly in comments:
```python
# Per .claude/skills/physical-kalman-tracking/SKILL.md and USER-CORRECTION-008,
# input MUST be court meters from CourtMapper, not normalized xyn.
```

## What NOT to do

- Do NOT use a 1D tracker per axis — 2D correlation matters for state machine's `hypot`
- Do NOT normalize the Kalman state itself (keep raw meters)
- Do NOT tune `Q` and `R` to hide unit errors (tempting when velocities look "close" to expected but off by a factor of the aspect ratio — that's a USER-CORRECTION-008 violation, not a tuning issue)
- Do NOT reset the filter between frames. Let it run the full clip per player.
