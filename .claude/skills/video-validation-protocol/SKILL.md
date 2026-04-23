---
name: video-validation-protocol
description: Visual ground-truth validation protocol for the PANOPTICON LIVE CV pipeline. Defines how to extract frames, use Claude vision, query DuckDB, and cross-reference biomechanical signal values against what is visually observable. Use when debugging signal extractors, validating precompute output, or confirming that skeleton overlays look correct.
---

# Video Validation Protocol

## Purpose

Automated tests verify that the CV pipeline produces correct outputs given correct inputs. But they cannot verify that the YOLO keypoints themselves are correct, that state machine transitions happen at the right moments, or that signal spikes correspond to observable biomechanics. This protocol closes that gap using Claude's vision capability.

## Core Capability: Claude Can Read Images

The `Read` tool reads any image file path and renders it visually (PNG, JPEG, MP4 thumbnails). Use this for:
- Validating YOLO skeleton overlay quality at specific timestamps
- Confirming player identity assignment (A vs B) matches actual court position
- Verifying that signal anomalies correspond to observable player behavior

## Tool Stack for Video/Image Work

| Tool | Purpose | When to Use |
|---|---|---|
| `ffmpeg` (Bash) | Extract single frame at timestamp T | Any frame-level inspection |
| `Read` (Claude vision) | Visual inspection of extracted frame | After ffmpeg extraction |
| `python3 -c "json.load(...)"` | Query match_data.json signal values | Cross-reference with frame |
| `context7 MCP` | Fetch current ffmpeg/OpenCV/YOLO docs | Before implementing new video features |
| `perplexity_ask` | Research specific CV technique | Before implementing |
| `video-frame-validator` agent | Full validation workflow | Systematic pre-demo audit |

## Frame Extraction Commands

> **GOTCHA-025 (HARD RULE):** Broadcast tennis MP4s are often variable-frame-rate (VFR).
> `ffmpeg -ss <timestamp>` does NOT reliably land on the same frame that DuckDB stored as
> `frame_idx`. Vision will hallucinate mismatches against signal values because it is looking
> at the wrong frame. **ALWAYS extract by absolute frame index, never by timestamp.**
>
> DuckDB stores `frame_idx` as the authoritative integer identifier. Convert
> `timestamp_ms → frame_idx` using the known frame rate (`fps = 30` for our clips, or
> query the schema's canonical fps constant), then extract that exact integer index.

### Single frame by ABSOLUTE FRAME INDEX (MANDATORY):
```bash
# Extract frame N (absolute index, 0-based). This lands on the SAME frame
# every time regardless of VFR. Use this form for EVERY vision validation.
N=1500
ffmpeg -i /path/to/clip.mp4 -vf "select=eq(n\,${N})" -vframes 1 -q:v 2 /tmp/frame_${N}.png

# Timestamp -> frame_idx helper (for our 30 fps precompute):
# N = round(timestamp_ms / 1000 * 30)
```

### FORBIDDEN: timestamp-based extraction
```bash
# DO NOT USE — drifts on VFR MP4s, produces wrong-frame hallucinations in Vision
ffmpeg -ss $T_SEC -i clip.mp4 -frames:v 1 frame.jpg   # ← BANNED
```

### Multi-frame kinematic sprite strip (MANDATORY for velocity/motion signals):
> **GOTCHA-025 (HARD RULE — Kinematic Blindspot):** A single static frame cannot validate
> a velocity signal. `lateral_work_rate` = 2.4 m/s, `split_step_latency_ms` = 180 ms,
> `recovery_latency_ms` — none of these are inspectable from one still image. Vision can
> only validate POSE / POSITION from a still. To validate MOTION, you MUST either:
>
>  (a) extract a 3-5 frame strip across the event window (sprite sheet), OR
>  (b) render an OpenCV overlay with velocity-vector arrows on a single frame.

```bash
# (a) Sprite strip: 5 frames straddling frame N (N-6, N-3, N, N+3, N+6 at 30 fps = 200ms span)
N=1500
ffmpeg -i clip.mp4 -vf "select='eq(n\,$((N-6)))+eq(n\,$((N-3)))+eq(n\,${N}))+eq(n\,$((N+3)))+eq(n\,$((N+6)))',tile=5x1" \
  -frames:v 1 -q:v 2 /tmp/strip_${N}.png
```

```python
# (b) OpenCV velocity-vector overlay (use when a sprite strip is cluttered).
# Pull (x_m, y_m, vx_mps, vy_mps) from DuckDB at frame_idx == N, convert to pixel space
# via CourtMapper.to_pixels(), draw an arrow from the player's foot to
# (foot + vx*scale, foot + vy*scale), save PNG, then Read() it.
import cv2, numpy as np
frame = cv2.imread("/tmp/frame_1500.png")
cv2.arrowedLine(frame, (px, py), (px + int(vx * 60), py + int(vy * 60)),
                (0, 255, 0), 3, tipLength=0.25)
cv2.imwrite("/tmp/frame_1500_velarrow.png", frame)
```

### Dashboard frame (canvas skeleton overlay):
If you want to see the skeleton overlay on the frame (as it appears in the browser), you must screenshot the running dashboard. Use the dev server: `cd dashboard && bun dev`, open in browser, then use OBS or macOS screenshot.

## Two Banned Anti-Patterns (GOTCHA-025)

Before every validation call, confirm:
- [ ] Frame was extracted by ABSOLUTE FRAME INDEX (`select=eq(n\,N)`), NOT by timestamp.
- [ ] Any claim about a VELOCITY or MOTION signal is backed by a sprite strip or a velocity-arrow overlay, NOT a single still frame.

If either box is unchecked, the validation report is void.

## Visual Validation Checklist

For each inspected frame, verify:

### Player A detection quality
- [ ] Is Player A visible? (near-court player, right side of net)
- [ ] Is the skeleton correctly placed? (ankles at feet, shoulders at shoulders)
- [ ] Are keypoints on the correct body (not on Player B, ball, or crowd)
- [ ] Are any keypoints obviously wrong (e.g., wrist at hip level)?

### Match state consistency
- [ ] Does the observable player action match the logged state at that timestamp?
  - PRE_SERVE_RITUAL: Player should be near baseline, bouncing ball or in trophy position
  - ACTIVE_RALLY: Player should be moving actively
  - DEAD_TIME: Player should be walking, toweling off, stationary between points

### Signal-to-visual coherence
For each signal with anomaly at this timestamp:
- [ ] Can you SEE the anomalous behavior that produced the signal spike?
- [ ] If z > 2, is there an observable difference from "normal"?

## Signal-to-Visual Mapping

| Signal | What to Look For in Frame |
|---|---|
| `recovery_latency_ms` HIGH | Player walking slowly back to position after shot |
| `serve_toss_variance_cm` HIGH | Serve toss visibly off-center or inconsistent height |
| `ritual_entropy_delta` HIGH | Pre-serve routine looks rushed or abbreviated |
| `crouch_depth_degradation_deg` HIGH | Player's knees less bent than typical in ready position |
| `baseline_retreat_m` HIGH | Player standing noticeably behind baseline |
| `lateral_work_rate` HIGH | Player mid-sprint, clearly moving laterally |
| `split_step_latency_ms` HIGH | Player slow to react after serve (still in stance while ball is already past) |

## Physics Sanity Bounds (per frame observation)

These bounds catch systematic signal errors:

| Observable | Expected Signal Range | If Outside Range |
|---|---|---|
| Player clearly sprinting | lateral_work_rate > 2.0 m/s | State machine may have wrong state |
| Player stationary | lateral_work_rate < 0.3 m/s | Kalman may be producing phantom velocity |
| Player at baseline | baseline_retreat_m = 0-0.5m | Homography may be miscalibrated |
| Player at mid-court | baseline_retreat_m = 1.5-3.0m | Court mapper reference point check |
| Deep crouch visible | crouch_depth_degradation_deg positive | Check angle computation direction |
| Serve toss visible | serve_toss_variance_cm firing | Must be in PRE_SERVE_RITUAL |

## Using Context7 MCP for Video Library Docs

When implementing new video processing features, fetch current docs before coding:

```
# For ffmpeg-python API (not ffmpeg CLI):
mcp__plugin_context7_context7__query-docs: "ffmpeg-python pipe output to BytesIO"

# For OpenCV:
mcp__plugin_context7_context7__query-docs: "opencv python VideoCapture alternatives"

# For Ultralytics YOLO:
mcp__plugin_context7_context7__query-docs: "ultralytics yolo11 pose keypoints confidence"

# For filterpy RTS smoother:
mcp__plugin_context7_context7__query-docs: "filterpy KalmanFilter rts_smoother"

# For scipy SG filter:
mcp__plugin_context7_context7__query-docs: "scipy signal savgol_filter centered offline"
```

## Pre-Demo Validation Run (MANDATORY before recording demo video)

Run `video-frame-validator` agent on these 5 critical timestamps (use `match_data.json` anomaly list to find exact timestamps):
1. Highest z-score anomaly (most dramatic signal spike) — verify it's real
2. PRE_SERVE_RITUAL → ACTIVE_RALLY transition — verify state matches motion
3. Mid-clip sample (~halfway point) — general quality check
4. Last 10 seconds — verify signals don't degrade at clip end
5. First 15 seconds post-warmup — verify Kalman has converged correctly

## MPS Memory Validation (every precompute run)

After running `precompute.py`, verify:
```bash
# Check MPS memory hasn't leaked:
python3 -c "import torch; print('MPS allocated:', torch.mps.current_allocated_memory() / 1e6, 'MB')"
# Should be < 100MB after precompute completes with empty_cache() every 50 frames
```

## When to Use This Protocol

- **Always**: Before recording the demo video (pre-demo validation run above)
- **When**: Opus coaching commentary seems disconnected from what's visually happening
- **When**: Signal values seem physically implausible (velocity too high/low for observed motion)
- **When**: State machine transitions seem wrong (PRE_SERVE_RITUAL during a rally)
- **When**: Modified kalman.py, pose.py, or any signal extractor

## Integration with video-frame-validator Agent

The `video-frame-validator` agent in `.claude/agents/video-frame-validator.md` is the execution engine for this protocol. Dispatch it when you need a systematic validation run (not just a quick spot check).

```
Agent({
  subagent_type: "video-frame-validator",  // uses Bash + Read for frame extraction + vision
  prompt: "Validate signal quality at timestamp T=15000ms for the demo clip..."
})
```
