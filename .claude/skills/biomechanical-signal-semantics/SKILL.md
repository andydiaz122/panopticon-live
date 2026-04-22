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

**State gate** (USER-CORRECTION-018 compiler-flush contract): Extractor buffers `(t_ms, |v|)` tuples during ACTIVE_RALLY. The compiler calls `flush()` exactly once when the player transitions OUT of ACTIVE_RALLY (either → DEAD_TIME via natural stillness, or coupled by other match events). The extractor then scans its buffer for the last tick where `|v| >= 0.5` (t_rally_end) and the first subsequent tick where `|v| < 0.5` (t_at_stillness).

**Kalman velocity magnitude** (USER-CORRECTION-017 physics guardrail): compute `math.hypot(vx, vy)` from `target_kalman[2], target_kalman[3]`. Do NOT re-derive velocity from keypoints. Do NOT project upper-body points through CourtMapper.

**Calculation**:
```python
# On each ACTIVE_RALLY ingest tick:
speed_mps = math.hypot(target_kalman[2], target_kalman[3])
self._buffer.append((t_ms, speed_mps))

# On flush (compiler calls this when state exits ACTIVE_RALLY):
t_rally_end = last t in buffer where speed_mps >= 0.5
t_at_stillness = first t after t_rally_end where speed_mps < 0.5
recovery_latency_ms = t_at_stillness - t_rally_end  # may be None if never stilled
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

**Definition**: Standard deviation of wrist-keypoint apex height across serve attempts within a sliding window during PRE_SERVE_RITUAL, converted from normalized pixels to centimeters via a camera-invariant biological ruler.

**State gate** (USER-CORRECTION-018 compiler-flush): accumulated only during PRE_SERVE_RITUAL; compiler flushes on transition OUT.

**USER-CORRECTION-020 — Phantom-Serve Guard + Biological Ruler**:

1. **Relative kinematics** (USER-CORRECTION-012): operate on `wrist_y - hip_y` (ambidextrous wrist selection per USER-CORRECTION-014), not raw `wrist_y`. Removes camera pan/tilt.

2. **Apex extraction**: in normalized image coords, `y=0` is the TOP of the frame, so the TOSS APEX corresponds to the MINIMUM `relative_y` over the toss phase (NOT the max).

3. **Phantom-serve amplitude filter**: the returner also lives in PRE_SERVE_RITUAL. If the wrist y-range `(max_y - min_y)` over the buffer is BELOW `0.05` normalized units, the buffer is jitter — return `None`, do not emit a value. Only a real toss clears this threshold (typical pro toss spans ~0.15-0.25 normalized units).

4. **Biological ruler (Z=0 invariant compliant)**: cannot use `CourtMapper` to convert airborne wrist pixels to meters (per USER-CORRECTION-017). Instead, use the player's OWN torso (`abs(shoulder_y - hip_y)`) as a pixel ruler. A pro tennis torso averages ~60 cm; use it to convert normalized → cm:
   ```python
   torso_px_norm = abs(shoulder_y - hip_y)  # same coordinate system as wrist_y
   CM_PER_NORMALIZED_UNIT = 60.0 / torso_px_norm
   variance_cm = std(apex_heights_norm) * CM_PER_NORMALIZED_UNIT
   ```
   Both wrist and torso project through the same camera, so the torso-scalar naturally absorbs perspective. The 60 cm assumption bounds error to ~10% (pro men avg ~62 cm, pro women ~55 cm), which is fine for a relative-fatigue signal.

**Calculation (canonical)**:
```python
# Per-frame during PRE_SERVE_RITUAL:
ambi_wrist_y = max(left_wrist_y, right_wrist_y)  # confident + max-y per USER-CORRECTION-014
rel_y = ambi_wrist_y - hip_y
self._wrist_buffer.append(rel_y)
self._torso_buffer.append(abs(shoulder_y - hip_y))

# On flush:
if (max(wrist_buffer) - min(wrist_buffer)) < 0.05:
    return None  # phantom serve — too little range to be a real toss
apex_norm = min(self._wrist_buffer)  # smallest y = highest point
std_norm = float(np.std(apex_series))  # std of apex across serves in sliding window
torso_norm = float(np.mean(self._torso_buffer))  # stable across the buffer
cm_per_norm = 60.0 / torso_norm
variance_cm = std_norm * cm_per_norm
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

**Definition**: Player's distance BEHIND their own baseline in court meters, clamped to 0.0 (standing inside the court is "no retreat").

**USER-CORRECTION-021 — Asymmetric Baseline Geometry**: Player A and Player B have OPPOSITE baselines and retreat directions. A naive single-baseline implementation would invert B's retreat or produce negative distances. Retreat MUST branch on `self.target_player`:

- **Player A** (near baseline in our convention, y=23.77m): retreat = `max(0.0, y_m - SINGLES_COURT_LENGTH_M)`
- **Player B** (far baseline, y=0.0m): retreat = `max(0.0, 0.0 - y_m)` = `max(0.0, -y_m)`

**Input source** (USER-CORRECTION-017 physics guardrail): use `target_kalman[1]` (y_m) directly — the Kalman filter runs on `robust_foot_point` which IS a ground-plane point, so its y-output is already the valid court-meter y-coordinate. Do NOT re-derive by running keypoints through `CourtMapper` a second time.

**Calculation (canonical)**:
```python
from backend.db.schema import SINGLES_COURT_LENGTH_M  # = 23.77

if target_state != "ACTIVE_RALLY" or target_kalman is None:
    return
y_m = target_kalman[1]
if self.target_player == "A":
    retreat_m = max(0.0, y_m - SINGLES_COURT_LENGTH_M)
else:  # "B"
    retreat_m = max(0.0, -y_m)
self._buffer.append(retreat_m)

# On flush (compiler flushes on ACTIVE_RALLY exit):
mean_retreat_m = float(np.mean(self._buffer))  # or median, or max — TDD-decide
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

**Definition**: Time from the OPPONENT'S transition into ACTIVE_RALLY (serve/stroke contact) to the TARGET'S transition into ACTIVE_RALLY (commit-to-return).

**USER-CORRECTION-019 — Structural State-Proxies (no raw-derivative hunting)**:

The original specification said: "time from opponent wrist-velocity PEAK to target's first velocity ZERO-CROSSING." Differentiating raw YOLO keypoints to find a peak is chaotic — jitter + occlusion noise destroys the signal. **However**, the MatchStateMachine already gives us canonical transition timestamps that are:
- Smoothed over 5 consecutive frames (`CONSECUTIVE_FRAMES_TO_RALLY`)
- Unambiguously aligned with serve-contact moments (server transitions PRE_SERVE_RITUAL → ACTIVE_RALLY at the moment of contact)
- Returner-specific transition timestamps are the commit-to-return moment

So: `split_step_latency_ms = target_ACTIVE_RALLY_entry_t_ms - opponent_ACTIVE_RALLY_entry_t_ms`. The state machine's 5-frame gating naturally absorbs jitter.

**State-tracking pattern** (USER-CORRECTION-013 symmetric API, USER-CORRECTION-018 compiler-flush):

```python
class SplitStepLatency(BaseSignalExtractor):
    signal_name = "split_step_latency_ms"
    required_state = ("PRE_SERVE_RITUAL", "ACTIVE_RALLY")  # both — we need to see the transition

    def __init__(self, target_player, dependencies):
        super().__init__(target_player, dependencies)
        self._opp_entered_active_t_ms: int | None = None
        self._target_entered_active_t_ms: int | None = None
        self._last_target_state: PlayerState | None = None
        self._last_opponent_state: PlayerState | None = None

    def ingest(self, frame, target_state, opponent_state,
               target_kalman, opponent_kalman, t_ms):
        # Opponent just entered ACTIVE_RALLY = serve/stroke contact
        if self._last_opponent_state == "PRE_SERVE_RITUAL" and opponent_state == "ACTIVE_RALLY":
            self._opp_entered_active_t_ms = t_ms
            self._target_entered_active_t_ms = None  # reset target-entry for this rally

        # Target just entered ACTIVE_RALLY = split-step commit
        if self._last_target_state == "PRE_SERVE_RITUAL" and target_state == "ACTIVE_RALLY":
            self._target_entered_active_t_ms = t_ms

        self._last_target_state = target_state
        self._last_opponent_state = opponent_state

    def flush(self, t_ms):
        # If target is the server (transitioned FIRST), return None — no meaningful latency.
        # If opponent transitioned first AND target transitioned after, emit the delta.
        if (self._opp_entered_active_t_ms is None
                or self._target_entered_active_t_ms is None):
            return None
        if self._target_entered_active_t_ms < self._opp_entered_active_t_ms:
            return None  # target is the server this rally — no latency to measure
        latency_ms = self._target_entered_active_t_ms - self._opp_entered_active_t_ms
        sample = SignalSample(..., value=float(latency_ms), ...)
        self._opp_entered_active_t_ms = None
        self._target_entered_active_t_ms = None
        return sample
```

**Why this is physically correct**:
- The state machine transitions ACTIVE_RALLY only after 5 consecutive frames (167 ms @ 30 fps) above 0.2 m/s. This inherently filters noise.
- Server → ACTIVE_RALLY aligns with the visible serve motion starting.
- Returner → ACTIVE_RALLY aligns with the visible split-step and forward/lateral commit.
- A healthy returner's commit-to-return timing is 150-250 ms AFTER the server's commit; a fatigued returner is delayed 300-500 ms. These match the literature-informed ranges below.

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
