---
name: biomechanical-signal-semantics
description: Mathematical definitions, academic thresholds, and test-case patterns for the 7 tennis biomechanical signals PANOPTICON LIVE extracts. Use when implementing any signal module, writing signal tests, or constructing the Opus system prompt. Prevents threshold hallucination.
---

# Biomechanical Signal Semantics

The 7 signals are the ALPHA of the entire product. Each must be mathematically sound and grounded in literature. This skill is the reference.

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

# Buffer: COM Y-position samples during PRE_SERVE_RITUAL
if len(buffer) < 10:
    return None  # SP3 guard
freqs = np.linspace(0.5, 5.0, 100)  # bounce cadence range (Hz)
power = lombscargle(buffer_t, buffer_y, freqs, normalize=True)
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

**Definition**: Statistical summary of X-axis COM velocity during ACTIVE_RALLY segments. Reported as p95 velocity in m/s.

**Upper-body only**: Legs are often occluded by camera angle. Use COM = weighted average of shoulder + hip keypoints.

**Calculation**:
```python
# Per-frame X-velocity during rally
vx_series = np.diff(com_x_m_series) / np.diff(com_t_s_series)
p95_vx = np.percentile(np.abs(vx_series), 95)
```

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
