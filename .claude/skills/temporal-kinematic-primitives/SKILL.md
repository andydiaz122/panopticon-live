---
name: temporal-kinematic-primitives
description: Time-series + camera-invariance discipline for PANOPTICON. Covers RollingBounceDetector, Lomb-Scargle angular-frequency trap (USER-CORRECTION-012), relative kinematics (wrist_y − hip_y) for camera-pan rejection (USER-CORRECTION-012), NaN-safe ambidextrous wrist selection (USER-CORRECTION-014), and the zero-variance spectral guard (USER-CORRECTION-015). Use when touching backend/cv/temporal_signals.py, writing bounce/serve-cue detectors, or any signal that uses Lomb-Scargle.
---

# Temporal Kinematic Primitives

Time-series primitives that run BEFORE the MatchStateMachine, plus the mathematical disciplines for any extractor that consumes a rolling buffer of image-space keypoints.

This skill owns:
- The `RollingBounceDetector` algorithm in `backend/cv/temporal_signals.py`
- The **relative kinematics principle** (camera-invariance via `wrist_y − hip_y`)
- The **NaN-safety + ambidextrous pattern** for occlusion-robust buffers
- The **angular-frequency contract** for `scipy.signal.lombscargle`
- The **zero-variance spectral guard** for any normalized-periodogram code

It does NOT own:
- Signal math / physical semantics → `biomechanical-signal-semantics`
- Pipeline orchestration → `cv-pipeline-engineering`
- Extractor API shape (ABC) → `signal-extractor-contract`

## 1 — The Chicken-and-Egg Deadlock (Why This Skill Exists)

The MatchStateMachine transitions both players into `PRE_SERVE_RITUAL` on a bounce signature. The natural place to compute a bounce would be in the `ritual_entropy_delta` signal extractor — but signal extractors only run AFTER state transitions. Without a bounce, no state transition; without the transition, no signal; deadlock.

**Resolution (USER-CORRECTION-013)**: promote bounce detection to a **continuous rolling primitive** that runs UNCONDITIONALLY every frame, independent of the state machine. The MatchStateMachine consumes its output; the extractor layer never computes bounces directly.

Per-tick ordering:
```
1. RollingBounceDetector.ingest_player_frame(A)
2. RollingBounceDetector.ingest_player_frame(B)
3. (a_bounce, b_bounce) = RollingBounceDetector.evaluate()
4. MatchStateMachine.update(a_speed, b_speed, a_bounce, b_bounce, t_ms)
5. <extractor dispatch — state-gated>
```

This pattern generalizes to **any kinematic primitive** the state machine needs (serve-contact cue, stroke-start cue, etc.).

## 2 — Relative Kinematics (USER-CORRECTION-012)

Broadcast cameras pan/tilt during serves. Raw `wrist_y` = biomechanical motion + camera motion superposed. A Lomb-Scargle periodogram on raw `wrist_y` sees the serve toss AND the 0.1 Hz camera sweep — noise overwhelms signal.

**Fix**: operate on the difference `relative_y = wrist_y − hip_y`. Since the camera moves the hip and wrist equally, the difference isolates pure biomechanical oscillation (common-mode rejection).

Applies to:
- `RollingBounceDetector` ✓ (buffer stores `wrist_y − hip_y`, not `wrist_y`)
- `ritual_entropy_delta` (same principle — compute entropy on relative-y)
- `serve_toss_variance_cm` (variance of toss height relative to the hip anchor)

**When you must NOT apply this**:
- Signals that are SUPPOSED to capture absolute court position (e.g., `baseline_retreat_distance_m`). These use `CourtMapper` to transform to physical meters, which removes camera perspective differently.

## 3 — NaN-Safety + Ambidextrous Wrist (USER-CORRECTION-014)

YOLO outputs `None` or low-confidence keypoints during occlusion. A `deque[float | None]` fed to `max()` crashes `TypeError`. A `deque[float]` with `None` cast to `0.0` fabricates data.

**The correct pattern**:

```python
from collections import deque
import numpy as np

_buf: deque[float] = deque(maxlen=WINDOW_FRAMES)   # stores float or np.nan

# Ingestion
def ingest(left_y, left_conf, right_y, right_conf, hip_y, hip_conf):
    chosen = _pick_wrist(left_y, left_conf, right_y, right_conf)
    if chosen is None or hip_y is None or (hip_conf or 0.0) < CONF_THRESHOLD:
        rel_y = float("nan")
    else:
        rel_y = chosen - hip_y
    _buf.append(rel_y)

# Evaluation (NaN-safe)
arr = np.asarray(_buf, dtype=float)
if int(np.sum(~np.isnan(arr))) < MIN_SAMPLES:
    return False     # insufficient real data

var = float(np.nanvar(arr))
if not math.isfinite(var) or var < VARIANCE_FLOOR:
    return False     # zero-variance or all-NaN

amp = float(np.nanmax(arr) - np.nanmin(arr))
```

**Ambidextrous wrist selection**: players serve with either hand, and the non-dominant wrist is often out of frame. Pick the confident wrist with the **maximum y** (lower screen position = closer to the ball at bounce). This is a stable ambidextrous heuristic.

```python
def _pick_wrist(left_y, left_conf, right_y, right_conf):
    candidates = []
    if left_y is not None and (left_conf or 0.0) >= CONF_THRESHOLD:
        candidates.append(left_y)
    if right_y is not None and (right_conf or 0.0) >= CONF_THRESHOLD:
        candidates.append(right_y)
    return max(candidates) if candidates else None
```

## 4 — Lomb-Scargle Angular-Frequency Contract (USER-CORRECTION-012)

`scipy.signal.lombscargle(t, y, freqs, normalize=...)` takes **angular frequencies in rad/s**, not Hz. Tennis bounce cadence at 1-3 Hz is 6.28-18.8 rad/s. Passing raw Hz silently samples the wrong band (0.08-0.8 Hz) and returns wrong spectral entropy.

**Always multiply by `2 * np.pi`**:

```python
import numpy as np
from scipy.signal import lombscargle

freqs_hz = np.linspace(0.5, 5.0, 100)      # physical cadence range
freqs_rad = freqs_hz * (2 * np.pi)         # ANGULAR frequencies for lombscargle
power = lombscargle(buffer_t, buffer_y, freqs_rad, normalize=True)
```

This has been the canonical trap since scipy's API surface was designed. Document it everywhere.

## 5 — Zero-Variance Spectral Guard (USER-CORRECTION-015)

`lombscargle(normalize=True)` divides by `np.var(y)` internally. If the buffer is:
- All identical values (player standing perfectly still)
- All NaN (total occlusion)
- All one finite value + NaN tail

then variance approaches or equals zero. Division explodes to `inf` or `NaN`, corrupting downstream entropy calculations.

**Always guard**:

```python
if np.nanvar(buffer_y) < 1e-5:
    return None    # no spectral content; report "no reading"

power = lombscargle(buffer_t, buffer_y, freqs_rad, normalize=True)
```

The floor `1e-5` is below YOLO's typical jitter squared-normalized (~1e-4²). It says: "If the buffer is quieter than YOLO's noise floor, there is genuinely nothing to analyze."

## 6 — Class Constants Reference (RollingBounceDetector)

```python
WINDOW_FRAMES: int = 90             # ~3s @ 30fps
AMP_THRESHOLD_REL: float = 0.02     # ~2% of frame height (relative units)
BOUNCE_PERIOD_RANGE_S: tuple = (0.25, 1.5)   # 0.67-4 Hz
MIN_SAMPLES: int = 10
VARIANCE_FLOOR: float = 1e-5
WRIST_CONF_THRESHOLD: float = 0.3
```

Changes to these constants should be driven by empirical TDD evidence, not intuition.

## When this skill fires

- Writing bounce/serve-cue detectors
- Any signal using `scipy.signal.lombscargle` (`ritual_entropy_delta`)
- Any code that consumes a rolling buffer of image-space keypoints with occlusion
- Reviewing Fleet 2 deliverables (ritual_entropy + serve_toss_variance)

## Delegation graph

- Delegates math semantics → `biomechanical-signal-semantics`
- Delegates pipeline orchestration → `cv-pipeline-engineering`
- Delegates extractor API → `signal-extractor-contract`
- Referenced by `test-forensic-validator` for Lomb-Scargle correctness tests
