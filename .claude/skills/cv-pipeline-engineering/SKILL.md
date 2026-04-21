---
name: cv-pipeline-engineering
description: CV pipeline architectural patterns for PANOPTICON LIVE. Use when building or modifying anything under backend/cv/. Covers Ultralytics YOLO11m-Pose async wrapper, Kalman occlusion smoothing, the 3-state kinematic state machine, ffmpeg-stdout Zero-Disk ingestion, and the pre-compute-to-DuckDB flow.
---

# CV Pipeline Engineering Patterns

This skill documents the architectural patterns for the Panopticon CV pipeline. Use when touching `backend/cv/` or `backend/precompute.py`.

## Pipeline Stages (left to right)

```
Video → ffmpeg stdout → BytesIO → YOLO11m-Pose (MPS) → keypoints.xyn
       → Kalman smoother (per player) → State Machine (per player)
       → Signal Extractors (7) → Pydantic FatigueVector → DuckDB
```

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

## Stage 4 — Kinematic State Machine

```
PER-PLAYER STATE (independent):

  ┌────────────────┐   velocity ↑   ┌──────────────┐
  │ PRE_SERVE_     │────────────────►│ ACTIVE_RALLY │
  │ RITUAL         │                 │              │
  └──────▲─────────┘                 └─────┬────────┘
         │ stillness                        │ stillness
         │ after rally                      │
         │                                  ▼
         │                         ┌──────────────┐
         └─────────────────────────┤ DEAD_TIME    │
                     extended      │              │
                     stillness     └──────────────┘
```

**Transition rules (Kalman-smoothed vy as primary signal):**
- PRE_SERVE_RITUAL → ACTIVE_RALLY: `|vy| > 0.2 m/s` for 5+ consecutive frames
- ACTIVE_RALLY → DEAD_TIME: `|vy| < 0.05 m/s` for 15+ consecutive frames
- DEAD_TIME → PRE_SERVE_RITUAL: small bounce cadence detected in Y-position

**Asymmetric evaluation**: Each player evaluated independently. One player walking off-camera does NOT gate the other player's state.

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

## Stage 6 — DuckDB Write (per segment)

Segments are ~1-second windows where state is stable. At segment end:
```python
compiler = FeatureCompiler(match_id, player)
for frame in segment_frames:
    compiler.ingest(frame, kalman.state, state_machine.state)
vec = compiler.flush()  # FatigueVector Pydantic model
db.write(vec)
```

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
