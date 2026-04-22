---
name: cv-pipeline-engineering
description: CV pipeline architectural patterns for PANOPTICON LIVE. Use when building or modifying anything under backend/cv/. Covers Ultralytics YOLO11m-Pose async wrapper, Kalman occlusion smoothing, the 3-state kinematic state machine, ffmpeg-stdout Zero-Disk ingestion, and the pre-compute-to-DuckDB flow.
---

# CV Pipeline Engineering Patterns

This skill documents the architectural patterns for the Panopticon CV pipeline. Use when touching `backend/cv/` or `backend/precompute.py`.

## Pipeline Stages (left to right) — REVISED 2026-04-21

```
Video → ffmpeg stdout → BytesIO → YOLO11m-Pose (MPS) → keypoints.xyn
       → robust_foot_point (ankle→knee→hip fallback per USER-CORRECTION-003)
       → CourtMapper.to_court_meters (un-normalized per USER-CORRECTION-005)
       → Absolute Court Half Assignment (USER-CORRECTION-007: y_m > 11.885 = A)
       → PhysicalKalman2D (meters-in, m/s-out per USER-CORRECTION-008)
       → MatchStateMachine (2D hypot speed + bounce coupling per USER-CORRECTIONS-009, 010)
       → Signal Extractors (7) → Pydantic FatigueVector + CoachInsight + HUDLayoutSpec
       → match_data.json (static, per USER-CORRECTION-001/002/006)
```

**Note on the output shape**: The pipeline's end artifact is `dashboard/public/match_data/<match_id>.json`, NOT a DuckDB file served over SSE. DuckDB is retained for Opus Managed Agent tool queries (scouting-report only), operated locally during pre-compute and bundled into the Vercel Next.js deploy if needed.

## Stage 1 — Video Ingestion (Zero-Disk)

Use Python's `asyncio.subprocess` module to launch ffmpeg with stdout captured. Read frames via `stdout.readexactly(frame_size)` where `frame_size = width * height * 3` for BGR24.

Key command arguments (conceptually):
- `-loglevel error` (silence ffmpeg chatter)
- `-i <clip_path>` (input file)
- `-f rawvideo -pix_fmt bgr24` (output format)
- `-` (stdout)

Reshape each raw buffer into `numpy.ndarray` of shape `(height, width, 3)` dtype `uint8`. Yield frames via `async for` generator.

## Stage 2 — YOLO Inference with MPS Safeguards

```python
# backend/cv/pose.py
import torch
from ultralytics import YOLO

class PoseExtractor:
    def __init__(self, weights: str = "yolo11m-pose.pt", device: str = "mps"):
        self.model = YOLO(weights)
        self.device = device
        self._frame_count = 0

    @torch.inference_mode()
    def infer(self, frame_bgr):
        results = self.model(
            frame_bgr,
            device=self.device,
            conf=0.001,      # captures occluded players
            imgsz=1280,      # accuracy/speed balance
            verbose=False,
        )
        self._frame_count += 1
        if self._frame_count % 50 == 0 and self.device == "mps":
            torch.mps.empty_cache()
        # Use Ultralytics' .xyn (normalized [0, 1]) — NOT .xy (pixels)
        return [
            {
                "player_idx": i,
                "keypoints_xyn": r.keypoints.xyn[0].cpu().numpy().tolist(),
                "confidence": r.keypoints.conf[0].cpu().numpy().tolist() if r.keypoints.conf is not None else None,
            }
            for i, r in enumerate(results)
            if r.keypoints is not None and r.keypoints.xyn is not None
        ]
```

## Stage 3 — Kalman Smoothing (per player)

```python
# backend/cv/kalman.py — via filterpy
from filterpy.kalman import KalmanFilter
import numpy as np

def make_kalman_2d() -> KalmanFilter:
    """2D constant-velocity Kalman filter for player centroid tracking."""
    kf = KalmanFilter(dim_x=4, dim_z=2)  # state: [x, y, vx, vy]
    kf.F = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=float)
    kf.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=float)
    kf.P *= 10.0
    kf.R *= 0.01   # measurement noise (normalized coords are low-variance)
    kf.Q *= 0.001  # process noise
    return kf
```

**Spike Suppression (SP5)**: The first 10 frames after init have noisy velocity estimates. Signal extractors that depend on velocity/acceleration MUST return `None` for those frames. Track `frames_since_init` per player.

## Stage 4 — Kinematic State Machine (REVISED per USER-CORRECTIONS-009, 010)

```
MATCH-LEVEL COUPLING (wraps two PlayerStateMachines):

  Per-player independent kinematics:
     ┌────────────────┐  speed↑  ┌──────────────┐
     │ PRE_SERVE_     │─────────►│ ACTIVE_RALLY │
     │ RITUAL         │          │              │
     └──────▲─────────┘          └─────┬────────┘
            │ stillness                 │ stillness
            │ after rally               │
            │                           ▼
            │                   ┌──────────────┐
            └───────────────────┤ DEAD_TIME    │
                   extended     │              │
                   stillness    └──────────────┘

  Match-level coupling:
     if Player A emits BOUNCE_DETECTED:
         force both A and B into PRE_SERVE_RITUAL
     if Player B emits BOUNCE_DETECTED:
         force both A and B into PRE_SERVE_RITUAL
```

**Transition rules — use 2D speed magnitude (USER-CORRECTION-009):**
- `speed_mps = math.hypot(vx, vy)` (NOT `|vy|` alone)
- PRE_SERVE_RITUAL → ACTIVE_RALLY: `speed_mps > 0.2 m/s` for 5+ consecutive frames
- ACTIVE_RALLY → DEAD_TIME: `speed_mps < 0.05 m/s` for 15+ consecutive frames
- DEAD_TIME → PRE_SERVE_RITUAL: bounce signature (Lomb-Scargle peak 1-4 Hz) detected on either player — coupling applies

**Match-level sync (USER-CORRECTION-010):** When either player emits a bounce signature, the `MatchStateMachine` forces BOTH into PRE_SERVE_RITUAL. This ensures the returner's `split_step_latency` signal (which gates on PRE_SERVE_RITUAL → ACTIVE_RALLY) fires correctly. See `match-state-coupling` skill for the algorithm.

**Velocity input must be in m/s.** The state machine receives `speed_mps` from the `PhysicalKalman2D` — which operates on court meters. See `physical-kalman-tracking` skill.

## Stage 5 — Signal Extractor Dispatch

See `biomechanical-signal-semantics` skill for per-signal math. State-gating matrix:

| Signal | Active during |
|---|---|
| recovery_latency_ms | ACTIVE_RALLY → DEAD_TIME transition |
| serve_toss_variance_cm | PRE_SERVE_RITUAL |
| ritual_entropy_delta | PRE_SERVE_RITUAL (buffer ≥10 samples) |
| crouch_depth_degradation_deg | ACTIVE_RALLY |
| baseline_retreat_distance_m | ACTIVE_RALLY |
| lateral_work_rate | ACTIVE_RALLY |
| split_step_latency_ms | PRE_SERVE_RITUAL → ACTIVE_RALLY (opponent serve contact → own first velocity) |

## Stage 6 — match_data.json Export (REVISED per USER-CORRECTIONs 001/002/006)

The pre-compute pipeline's end artifact is a single static JSON file per match, consumed directly by the Next.js frontend. NO SSE, NO FastAPI, NO Python on Vercel.

Output path: `dashboard/public/match_data/<match_id>.json`

Shape (top-level Pydantic model `MatchData`):
```python
class MatchData(PanopticonBase):
    meta: MatchMeta
    keypoints: list[FrameKeypoints]             # per-frame A + B xyn (for canvas)
    signals: list[SignalSample]                  # 7 × 2 players × timestamps
    anomalies: list[AnomalyEvent]
    coach_insights: list[CoachInsight]           # Opus reasoning, pre-computed offline
    hud_layouts: list[HUDLayoutSpec]             # Opus designer, pre-computed offline
    narrator_beats: list[NarratorBeat]           # Haiku per-second, pre-computed offline

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)
```

Frontend fetches once; rAF loop indexes via `videoRef.currentTime × clip_fps`. See `react-30fps-canvas-architecture` skill.

DuckDB is retained as a LOCAL pre-compute intermediate (for Opus Managed-Agent tool queries during the scouting-report pipeline). It does NOT ship to Vercel.

## Async Concurrency Rules

- **One worker thread for YOLO** (`ThreadPoolExecutor(max_workers=1)`) — MPS is not reentrant-safe
- **Kalman + state machine run on asyncio event loop** — no threading required
- **DuckDB writes batched** — flush every 10 segments to amortize transaction overhead
- **No multiprocessing** — adds complexity for no speed gain when MPS is the bottleneck

## Integration with Agents

- `cv-pipeline-engineer` agent owns this code
- `mps-performance-engineer` agent reviews every pose.py change
- `biomech-signal-architect` agent designs signal contracts
- `test-forensic-validator` agent writes tests before any implementation
