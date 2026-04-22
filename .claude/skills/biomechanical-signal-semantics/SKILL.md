---
name: biomechanical-signal-semantics
description: Mathematical definitions, academic thresholds, and test-case patterns for the 7 tennis biomechanical signals PANOPTICON LIVE extracts. Use when implementing any signal module, writing signal tests, or constructing the Opus system prompt. Prevents threshold hallucination.
---

# Biomechanical Signal Semantics

The 7 signals are the ALPHA of the entire product. Each must be mathematically sound and grounded in literature. This skill is the reference.

## ⚠️ Common Mathematical Traps (CHECK BEFORE WRITING ANY SIGNAL)

1. **`scipy.signal.lombscargle` requires ANGULAR frequencies (rad/s), NOT Hz** (USER-CORRECTION-012).
   Tennis bounce cadence is 1-3 Hz = 6.28-18.8 rad/s. Passing raw Hz silently analyzes the wrong band and returns wrong entropy. Always multiply by `2*np.pi`.

2. **`lombscargle(normalize=True)` divides by buffer variance** (USER-CORRECTION-015).
   A constant / all-NaN buffer produces inf / NaN. Guard with `np.nanvar(buf) < 1e-5 → return None`.

3. **Relative kinematics defeat camera pan/tilt** (USER-CORRECTION-012).
   Broadcast cameras pan during serves. Raw `wrist_y` = biomech + camera. Use `wrist_y − hip_y` to isolate biomech.

4. **YOLO outputs `None` / low-confidence keypoints** (USER-CORRECTION-014).
   Use `np.nan` + `np.nan{var, max, min, mean}` in buffers. Ambidextrous wrist selection: pick the confident wrist with max y (lower screen position = closer to ball at bounce).

5. **Cross-player signals** (USER-CORRECTION-011, 013).
   `split_step_latency_ms` needs the OPPONENT's PRE_SERVE → ACTIVE_RALLY transition timestamp. Use the symmetric `BaseSignalExtractor` API: `ingest(target_state, opponent_state, target_kalman, opponent_kalman, ...)`.

6. **Homography Z=0 Invariant** (USER-CORRECTION-017 — CRITICAL PHYSICS GUARDRAIL).
   `CourtMapper.to_court_meters` uses `cv2.getPerspectiveTransform`, which is valid ONLY for points on the ground plane (Z=0). **NEVER project shoulders, hips, wrists, or any upper-body keypoint through `CourtMapper`** — a 1.8m player's shoulders will project several meters behind their actual ground position due to parallax, and any velocity derived from that is fiction. If you need physical velocity in court meters, use the `PhysicalKalman2D` output (`target_kalman[2]=vx_mps`, `target_kalman[3]=vy_mps`), which is anchored to `robust_foot_point` (a ground-plane point).

See `temporal-kinematic-primitives` and `signal-extractor-contract` skills for details.

## Far-Court Occlusion Fallback Chain (USER-CORRECTION-003)

The broadcast camera's perspective places the tennis net in front of Player B's ankles ~80% of frames. All leg-dependent signals MUST use the helper below, NOT raw ankle keypoints.

```python
from typing import Sequence

def robust_foot_point(
    keypoints_xyn: Sequence[tuple[float, float]],
    confidence: Sequence[float],
    threshold: float = 0.3,
) -> tuple[float, float] | None:
    """Return the most reliable lower-body reference point.

    Tries ankle → knee → hip midpoint in that order, falling through when confidence
    falls below `threshold` on either side of the body.

    COCO indices:
      11 left_hip    12 right_hip
      13 left_knee   14 right_knee
      15 left_ankle  16 right_ankle
    """
    def _try(idx_l: int, idx_r: int) -> tuple[float, float] | None:
        if confidence[idx_l] < threshold or confidence[idx_r] < threshold:
            return None
        return (
            (keypoints_xyn[idx_l][0] + keypoints_xyn[idx_r][0]) / 2.0,
            (keypoints_xyn[idx_l][1] + keypoints_xyn[idx_r][1]) / 2.0,
        )

    return _try(15, 16) or _try(13, 14) or _try(11, 12)
```

**Torso scalar re-normalization**: when we fall back from ankle to knee (or hip), signals that depend on vertical body segments must normalize against the SAME segment:
- Full ankle-to-shoulder torso scalar when ankles present
- Knee-to-shoulder scalar when knee fallback
- Hip-to-shoulder scalar when hip fallback

Each signal module exposes its own `torso_scalar_for_mode(mode)` helper. Do NOT mix scalars across fallback modes within a single signal.

**Per-signal implications:**
- `crouch_depth_degradation_deg`: falls back gracefully; the metric measures *angle change from that player's own baseline*, so long as we compute baseline in the same fallback mode as the current sample, the delta is still meaningful.
- `baseline_retreat_distance_m`: falls back via `robust_foot_point` → knee midpoint → hip midpoint. Homography still projects the midpoint into court meters (with some accuracy loss for hip fallback).
- `split_step_latency_ms`: velocity-based, derived from Kalman of `feet_mid` which already uses this fallback chain.

## Signal 1 — recovery_latency_ms

**Definition**: Time elapsed between `ACTIVE_RALLY` exit and player's Kalman-smoothed velocity magnitude dropping below 0.5 m/s.

**State gate**: Only computed at `ACTIVE_RALLY → DEAD_TIME` transition. Standing still during an extended changeover (pure DEAD_TIME) is NOT recovery.

**Calculation**:
```python
t_rally_end: int  # ms, moment state transitions out of ACTIVE_RALLY
t_at_stillness: int  # ms, first frame after t_rally_end where |v| < 0.5 m/s
recovery_latency_ms = t_at_stillness - t_rally_end
```

**Physical ranges** (literature-informed):
- Elite fresh: 400-800 ms
- Elite fatigued: 800-2000 ms
- Recreational: 1500-3500 ms
- Anomaly threshold: z-score ≥ 2.0 vs player's match-opening baseline

**Test cases**:
- Synthetic player decelerating linearly 3 m/s → 0 m/s over 800ms → assert 800 ± 50 ms
- State-gate violation: returns `None` if called during PRE_SERVE_RITUAL
- Kalman warm-up: returns `None` for first 10 frames of new player track

## Signal 2 — serve_toss_variance_cm

**Definition**: Standard deviation of wrist-keypoint apex height (peak Y over the toss phase) across serves within a sliding window during PRE_SERVE_RITUAL.

**State gate**: Only accumulated during PRE_SERVE_RITUAL; flushed at transition.

**Calculation**:
```python
# For each serve attempt (wrist Y trajectory)
apex_y = max(wrist_y_series)
apex_heights.append(apex_y)
# Sliding window of last N serves
variance_cm = np.std(apex_heights[-N:]) * court_scale_cm_per_unit
```

**Physical ranges** (elite research on serve-toss consistency):
- Elite consistent server: 2-6 cm stdev
- Fatigued elite: 8-15 cm stdev
- Tracking failure threshold: >50 cm (YOLO losing wrist)

**Test cases**:
- Identical tosses (zero variance) → assert value < 1 cm
- Jittery tosses (wide spread) → assert value > 10 cm
- State-gate: returns `None` during ACTIVE_RALLY

## Signal 3 — ritual_entropy_delta

**Definition**: Spectral entropy of pre-serve bounce cadence (Y-position oscillation of the COM) computed via Lomb-Scargle periodogram, delta vs player's match-opening baseline.

**State gate**: PRE_SERVE_RITUAL only. Buffer must have ≥10 samples (SP3 — Spectral Noise Gate).

**Calculation**:
```python
from scipy.signal import lombscargle
import numpy as np

# Buffer: COM Y-position samples during PRE_SERVE_RITUAL
if len(buffer_y) < 10:
    return None  # SP3 guard

# USER-CORRECTION-015: Zero-variance guard — lombscargle(normalize=True) divides by
# variance; constant / all-nan buffers explode to inf/nan. Below the YOLO jitter
# noise floor, declare "no spectral content."
if np.nanvar(buffer_y) < 1e-5:
    return None

# USER-CORRECTION-012: scipy.signal.lombscargle requires ANGULAR frequencies (rad/s),
# NOT Hz. Tennis bounce cadence is 1-3 Hz = 6.28-18.8 rad/s. Passing raw Hz looks at
# the wrong band (0.08-0.8 Hz) and silently returns wrong spectral entropy.
freqs_hz = np.linspace(0.5, 5.0, 100)          # physical cadence range
freqs_rad = freqs_hz * (2 * np.pi)             # ANGULAR frequencies for lombscargle
power = lombscargle(buffer_t, buffer_y, freqs_rad, normalize=True)
spectral_entropy = -np.sum(power * np.log(power + 1e-10))
delta = spectral_entropy - baseline_entropy
```

**Physical interpretation**:
- Low entropy = rhythmic, calm ritual
- High entropy = disrupted, anxious ritual
- Delta > 0 under pressure = ritual breakdown

**Test cases**:
- Pure sine wave bounce → low entropy
- Random walk bounce → high entropy
- Buffer < 10 samples → returns `None`

## Signal 4 — crouch_depth_degradation_deg

**Definition**: Drift in pelvis-Y relative to ankle-Y (normalized by torso scalar) over the course of the match, in angular degrees.

**Key principle**: Do NOT invent a floor plane. Broadcast camera tilt invalidates absolute floor estimates. Use relative skeletal geometry only.

**Calculation**:
```python
# COCO keypoints: hip_y = avg(left_hip_y, right_hip_y); ankle_y = avg(left_ankle_y, right_ankle_y)
hip_ankle_dist = ankle_y - hip_y
torso_scalar = shoulder_y - hip_y  # camera-invariant scale
normalized_crouch = hip_ankle_dist / torso_scalar
# Convert to degree equivalent: drift from baseline
degradation_deg = np.degrees(np.arctan2(normalized_crouch - baseline_normalized, 1.0))
```

**Physical ranges**:
- Typical crouch change through a match: -2° to +4° drift
- Fatigue indicator: degradation > 3° from baseline
- Tracking failure: |degradation| > 10°

## Signal 5 — baseline_retreat_distance_m

**Definition**: Player's Y-position relative to own baseline, transformed from pixel space to court meters via homography.

**Requires**: Valid `CourtMapper` with 4 annotated court corners.

**Calculation**:
```python
# Feet midpoint in pixel space (normalized)
feet_pixel = ((kp[LEFT_ANKLE][0] + kp[RIGHT_ANKLE][0]) / 2,
              (kp[LEFT_ANKLE][1] + kp[RIGHT_ANKLE][1]) / 2)
# Transform to court meters
court_xy = court_mapper.to_court_meters(feet_pixel)  # returns None if off-court (SP1)
if court_xy is None:
    return None
# Distance from own baseline
retreat_m = court_xy[1] - player_baseline_y_m
```

**Physical ranges**:
- Baseline standoff (typical): 0-0.5 m
- Aggressive approach: < 0 m (inside baseline)
- Fatigue/defensive: 1-3 m behind baseline
- Out-of-bounds: mapper returns None; signal returns None

## Signal 6 — lateral_work_rate

**Definition**: Statistical summary of ground-plane X-axis velocity magnitude during ACTIVE_RALLY segments. Reported as p95 velocity in m/s.

**⚠️ USER-CORRECTION-017 (CRITICAL — Homography Z=0 Invariant)**: Do NOT compute a "Center of Mass" from upper-body keypoints and project it through `CourtMapper`. The `cv2.getPerspectiveTransform` homography is valid ONLY for points on the ground plane (Z=0). A 1.8m-tall player's shoulders project several meters behind their actual ground position — any velocity derived from that is parallax-corrupted fiction.

**Correct input**: `target_kalman[2]` — the already-smoothed `vx_mps` from `PhysicalKalman2D`, which is anchored to `robust_foot_point` (a ground-plane point) in true court meters.

**Calculation (canonical)**:
```python
# Per-frame during ACTIVE_RALLY — no homography on upper-body, no manual np.diff.
# target_kalman = (x_m, y_m, vx_mps, vy_mps) — vx is already the ground-plane X-velocity.
if target_state == "ACTIVE_RALLY" and target_kalman is not None:
    vx_mps = target_kalman[2]
    self._buffer.append(abs(vx_mps))

# On flush:
if not self._buffer:
    return None
p95 = float(np.percentile(self._buffer, 95))
# emit SignalSample(value=p95, ...), then reset the buffer
```

**Why this is immune to parallax**: the Kalman filter runs on `feet_mid_m` (from `robust_foot_point → CourtMapper.to_court_meters`), which is a ground-plane projection. The velocity output `vx_mps` therefore represents physical ground-plane motion, regardless of camera angle or player height.

**Why the state gate ("ACTIVE_RALLY" only)**: during PRE_SERVE_RITUAL / DEAD_TIME, the player shuffles/walks — velocity is not a fatigue signal there. Rally-only collection is the semantically meaningful window.

**Physical ranges**:
- Elite rally: 1-4 m/s p95
- Defensive grinding: 3-6 m/s p95
- Fatigue indicator: p95 trending DOWN across sets (player is less explosive)

## Signal 7 — split_step_latency_ms

**Definition**: Time from opponent's racquet-wrist peak velocity (serve/groundstroke contact) to player's first velocity zero-crossing (commit-to-return).

**State gate**: PRE_SERVE_RITUAL exit → ACTIVE_RALLY entry.

**Calculation**:
```python
t_contact: int  # ms, opponent wrist-velocity peak
t_commit: int  # ms, first zero-crossing of own velocity after t_contact
split_step_latency_ms = t_commit - t_contact
```

**Physical ranges** (literature-verified via Perplexity Apr 21 2026):
- Elite fresh: 150-250 ms
- 150ms delay from baseline correlates with 20% first-step speed loss (research)
- Fatigued: 300-500 ms
- Elite serve-return total window: ~400 ms (racquet-ball to response initiation)

## Baseline Protocol

For EVERY signal:
1. First ~2 minutes of play = calibration window
2. Compute per-player baseline: mean + std from calibration samples only during correct state
3. Subsequent samples reported with z-score vs baseline
4. Anomaly = |z| ≥ 2.0 AND |delta| > biological_noise_floor
5. Biological noise floors (from prior calibration work): posture ≈ 2.22° std, mechanics ≈ 2.48° std

## Anomaly Event Pydantic

```python
class AnomalyEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    timestamp_ms: int
    player: Literal["A", "B"]
    signal_name: Literal["recovery_latency_ms", "serve_toss_variance_cm", ...]
    value: float
    baseline_mean: float
    baseline_std: float
    z_score: float = Field(ge=-10.0, le=10.0)
    severity: float = Field(ge=0.0, le=1.0)  # derived from z_score, clipped
```

## Do Not Hallucinate

- No threshold in this file is a magic number — each has been anchored to biomech literature or prior empirical calibration
- When proposing a NEW threshold in code, cite the source in a comment
- When unsure, consult `biomech-signal-architect` agent
- When literature conflicts, document the choice in `MEMORY.md`
