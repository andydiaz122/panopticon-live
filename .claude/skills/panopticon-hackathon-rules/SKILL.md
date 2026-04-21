---
name: panopticon-hackathon-rules
description: Hard constraints for the PANOPTICON LIVE hackathon project. Use when starting any task, proposing any architecture, or making any engineering decision in this repo. Enforces the 3 critical gotchas (Batch 11 ML trap, React 30-FPS death spiral, Vercel 250MB limit) + the New Work Only + MPS-only + Zero-Disk + Pydantic v2 rules.
---

# PANOPTICON LIVE — Hackathon Hard Constraints

This skill encodes the inviolable rules for every task in this repo. If your proposed work violates any of these, stop and redesign. **Do not negotiate with the rules.**

## Prime Directive

Win the Demo criterion (25%) + Opus 4.7 Use criterion (25%) with visible craft. Judges evaluate a 3-minute video. The demo IS the product. Optimize for visual Cool Factor + creative Opus usage + engineering craft — NOT predictive accuracy or backtest R².

## The Three Critical Gotchas

### Gotcha 1 — ABORTED: Batch 11 ML Forge (STRATEGIC)
**Rule**: Do NOT build predictive ML models this week. No CatBoost targets, no Spearman correlation heatmaps, no `pandas.merge_asof` alignment matrices, no cross-validation infrastructure.
**Why**: A prior Alternative_Data handoff doc ended with instructions to begin Batch 11 ("The Alpha Forge"). Letting Claude Code start this work would consume the entire 5-day budget on invisible backend accuracy.
**Detection**: If code under `backend/` imports `catboost`, `xgboost`, `lightgbm`, `sklearn.model_selection`, or uses `pandas.merge_asof` on signal data — STOP. This is the trap.

### Gotcha 2 — React 30-FPS Death Spiral (ARCHITECTURAL)
**Rule**: Per-frame keypoint data NEVER goes into React `useState`. Use `useRef` + `requestAnimationFrame` + `<canvas>` direct paint.
**Why**: 30 FPS of keypoint updates × ~20 keypoints per player × 2 players = 1200 state updates/sec. React re-renders the entire component tree → browser tab crash.
**Detection**: Any `.tsx` file in `dashboard/` that calls `setState(keypoints)` or binds per-frame data to component state. Replace with `keypointsRef.current = nextFrame`.

### Gotcha 3 — Vercel 250MB Serverless Size Limit (DEPLOYMENT)
**Rule**: `requirements-prod.txt` contains ONLY `fastapi`, `uvicorn`, `anthropic`, `duckdb`, `pydantic`. NO `torch`, NO `ultralytics`, NO `opencv-python`, NO `scipy`.
**Why**: Vercel Serverless Functions have a 250MB unzipped limit. `torch` alone is ~700MB. Build will fail instantly.
**Detection**: Before any deploy, run `du -sh .vercel/output/functions/*` and verify < 250MB per function.

## Core Constraints (Foundational)

### New Work Only
Every line of code in this repo is written during the hackathon window (Apr 21-26, 2026). **No copy-paste from `Alternative_Data`**. Patterns may be reimplemented; files may not be vendored. Public libraries (`ultralytics`, `filterpy`, `scipy`, `opencv-python-headless`, `duckdb`, `anthropic`, `fastapi`) are fine — those are library imports, not our prior work.

### Hardware: Mac Mini M4 Pro MPS Only
- No CUDA this week
- Every YOLO inference path enforces:
  - `@torch.inference_mode()` decorator
  - `torch.mps.empty_cache()` every 50 frames
  - `conf=0.001` (captures occluded players)
  - `imgsz=1280` (accuracy/speed balance)
  - Single-worker asyncio executor (MPS is not reentrant-safe)
  - Graceful `torch.mps.MemoryError` handling — drop frame, continue

### Zero-Disk Video Policy
- ffmpeg stdout → `io.BytesIO` → YOLO input
- NO `cv2.VideoCapture` reading from disk
- Raw video format: `ffmpeg -f rawvideo -pix_fmt bgr24 -`
- Stream via `stdout.readexactly(frame_size)`

### Coordinate Normalization
- Use Ultralytics' built-in `.xyn` property (pre-normalized to [0.0, 1.0])
- DuckDB writes normalized coordinates only
- Frontend multiplies by `<video>.clientWidth/Height` at paint time

### Pydantic v2 at Every Module Boundary
- No dict crosses a module boundary
- `model_config = ConfigDict(frozen=True, extra="forbid")`
- `@field_validator` on every physical-realism constraint

### Open Source + MIT License
Hackathon rule. Repo is public, MIT-licensed. No private code, no proprietary libs, no paid APIs except Anthropic (which is the point).

## Decision Protocol

Before writing any code, ask:
1. Does this violate New Work Only?
2. Does this cross the React state-vs-ref line?
3. Does this add weight to the Vercel deploy bundle?
4. Is there a Pydantic schema for this data?
5. Does this violate Zero-Disk?
6. Does this exercise an Opus 4.7 feature (extended thinking, tools, caching, Managed Agents)?

Answer #1-5: if yes on any, STOP and redesign.
Answer #6: if no on most code, WHY ARE WE WRITING IT? Can it exercise Opus more?

## Automatic Behaviors

- Any code change → `python-reviewer` or `typescript-reviewer` agent
- Any new module → `/tdd` workflow (tests first)
- Pre-deploy → multi-agent review panel (4 orthogonal lenses)
- Every non-obvious learning → `MEMORY.md` entry within 5 minutes
- End of day → update `FORANDREW.md` with day's lessons, `/save-session`

## Submission Deadline

**Sunday April 26, 2026 @ 8:00 PM EST.** Non-negotiable. Working backwards:
- Sun 6pm EST: submission form filled out, ready to submit
- Sun 4pm EST: YouTube upload complete
- Sun 2pm EST: final demo take recorded
- Sun 12pm EST: rehearsal take 2
- Sun 10am EST: rehearsal take 1
- Sat 10pm EST: production URL live and stable
