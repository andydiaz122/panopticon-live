# FORANDREW.md — Plain-Language Project Walkthrough

This is a non-technical decision log, bug journal, and "talk to Andrew tomorrow morning" document. Updated every working session.

---

## What We're Building (in one paragraph)

Panopticon Live is a web app that takes a pro tennis match video and renders a **2K-Sports-style video-game HUD** over the footage. As the match plays, animated bars and meters pulse to show each player's live biomechanical state — fatigue, power, momentum, footwork. Below the video, **Claude Opus 4.7** streams coach-grade commentary, with its extended-thinking tokens visible in a collapsible panel (*"here's Opus reasoning about Alcaraz's crouch depth degradation..."*). The HUD layout itself is dynamically designed by Opus as match state changes — generative UI in action. A second tab shows the raw JSON signal stream as the B2B product ("this is what Valence, Sequence, Dome subscribe to"). A third tab generates a full PDF scouting report via Claude Managed Agents. **The demo is the product** — we ship this Sunday April 26 by 8pm EST.

---

## The 5-Day Sprint (Apr 21 Tue kickoff → Apr 26 Sun 8pm EST submission)

| Day | Focus | Outcome |
|---|---|---|
| Tue Apr 21 | Scaffold + Day-0 validation | Project skeleton + one UTR clip produces valid YOLO keypoints |
| Wed Apr 22 | CV pre-compute pipeline | 7 biomechanical signals written to DuckDB for one clip |
| Thu Apr 23 | Opus agents + SSE replay | Coach commentary + generative HUD + Haiku beats streaming |
| Fri Apr 24 | Frontend HUD (2K Sports) | Full dashboard with skeleton overlay + HUD + 3 tabs working on localhost |
| Sat Apr 25 | Polish + Vercel deploy + second clip | Production URL live, multi-agent review panel passes |
| Sun Apr 26 | Record demo + submit | YouTube video + GitHub + written summary submitted by 8pm EST |

## What Makes This Different

1. **The sensor doesn't exist today.** Nobody — Starlizard, Smartodds, Pinnacle, zero commercial competitors — extracts biomechanical fatigue signals from free broadcast video. Feb 2026 + April 17 2026 research confirmed this.
2. **Opus 4.7 plays three distinct roles** — Reasoner, Designer, Voice. That's "creative medium, not just a tool" territory (aligns with the $5K Creative Opus Exploration prize).
3. **The 2K Sports HUD is the demo moment.** Video-game aesthetics + live biomechanical telemetry + Opus reasoning = a visual nobody's seen in sports analytics.

## Current Decisions (locked)

- **Sport**: Pro tennis. User has 8 curated UTR match videos (single-camera, no broadcast cuts) — already at `~/Documents/Coding/Predictive_Modeling/Alternative_Data/data/videos/`.
- **Hardware**: Mac Mini M4 Pro MPS only. No CUDA.
- **Repo**: Public GitHub `panopticon-live`, MIT license.
- **Agent architecture**: Single Opus 4.7 + deterministic signal-query tools + Haiku 4.5 narrator + Claude Managed Agent for long-running scouting report.
- **Frontend**: Next.js 16, Bun for dev, Tailwind + shadcn/ui + Recharts + Motion. 2D canvas skeleton overlay — NO Three.js.
- **Runtime**: Zero-Disk (ffmpeg → BytesIO → YOLO). Pre-compute CV once per clip. Vercel serves SSE replay only, no ML.

## What We ARE NOT Doing (explicit non-goals)

- ❌ Training any ML models (we use pre-trained YOLO off-the-shelf)
- ❌ Building a profitable tennis predictor (that's the YC roadmap, not the hackathon)
- ❌ Batch 11 ML Forge work (CatBoost, Spearman correlation heatmaps, merge_asof matrices)
- ❌ Homography auto-detection (we manually annotate court corners)
- ❌ Three.js 3D visualizations (2D canvas is better for broadcast video)
- ❌ Twitter fan-engagement bubbles (noted as v2 roadmap; out of scope)
- ❌ Live broadcast RTSP ingestion (pre-computed, replay-driven)
- ❌ CUDA porting (Phase 2 after hackathon)

## Bug Journal (timestamped)

### 2026-04-21 19:55 — Day-0 probe verdict logic was backwards on memory slope
The probe reported `abs(slope) < 200 KB/frame` as the leak check, but we observed -314 KB/frame (memory DECREASING over time — no leak). Flipped the check to `slope > 200 KB/frame only`. False-alarm defense.

## Lessons Learned (timestamped)

### 2026-04-21 19:55 — Day-0 results are strongly positive
- **Warm FPS**: 12.7 on M4 Pro MPS with YOLO11m-Pose @ imgsz=1280, conf=0.001
- **Detection rate**: 100% frames detected ≥1 person
- **Two-player rate**: 99.9% (899/900)
- **Memory**: NO leak (-314 KB/frame = memory actually freed up)
- **Cold start**: ~22 CPU-sec for MPS graph compilation — one-time cost, acceptable

The UTR ANCHOR_OK clips are CV-friendly by Andrew's curation — minimal cuts, stable camera, broadcast-quality lighting. This de-risks the Phase 1 CV pipeline substantially.

### 2026-04-21 19:55 — YOLO sees crowd + ball-boys + linesmen (2-25 detections per frame)
Need Phase 1 player-filtering logic: (a) in-court homography polygon filter, (b) top-2 confidence selection, (c) Kalman-track continuity via Hungarian assignment for A/B identity. Without it, the 7 signals would be contaminated by crowd noise.

### 2026-04-21 19:30 — Ultralytics provides `.xyn` pre-normalized [0,1] keypoints
Discovered via Context7 doc lookup. We do NOT need to manually normalize pixel coords by frame width/height — it's built in. Saves code and prevents the absolute-pixel-on-resize bug at the source.

### 2026-04-21 21:15 — Team lead's second-wave review landed 5 more CRITICAL corrections
Two full waves of architectural scrutiny, totaling **10 USER-CORRECTIONs** baked into docs + skills + agents:

**Wave 1 (USER-CORRECTIONs 001-005):**
1. Video-Sync Trap → static `match_data.json` + video-clock-slaved rAF (no SSE)
2. Opus Latency Paradox → pre-compute Opus offline; scouting-report only live
3. Far-Court Occlusion → ankle→knee→hip fallback chain
4. Topological Y-Sort (superseded by #7)
5. Homography Aspect-Ratio Skew → un-normalize before `cv2.getPerspectiveTransform`

**Wave 2 (USER-CORRECTIONs 006-010):**
6. **Vercel Python Elimination** → delete `backend/api/`, delete `requirements-prod.txt`. Vercel runtime is Next.js + TypeScript only. Scouting report uses Server Action + `@anthropic-ai/sdk`. The 250MB Serverless risk is vaporized, not mitigated.
7. **Absolute Court Half Assignment** → split detections by `y_m > 11.885` (A) vs `y_m < 11.885` (B); top-1 confidence per half. Immune to occlusion-induced identity swap.
8. **Physical Kalman Domain** → Kalman operates on court meters. Feet_mid converted via `CourtMapper.to_court_meters()` BEFORE update. Output velocity is in m/s, making the state machine's 0.2 / 0.05 thresholds physically meaningful.
9. **Lateral Rally Blindspot** → use `speed = math.hypot(vx, vy)`, not `|vy|`. Baseline rallies would otherwise false-trigger DEAD_TIME.
10. **Asymmetric Pre-Serve Desync** → MatchStateMachine couples both players. Server's bounce forces returner's PRE_SERVE_RITUAL so `split_step_latency` gate fires.

**Net effect**: The Vercel deploy surface is now pure Next.js. The physics is provably correct in unit tests before code is written. We added 4 new specialized project skills (`physical-kalman-tracking`, `topological-identity-stability`, `match-state-coupling`, `vercel-ts-server-actions`) — skill count 8→12, all orthogonal.

## Follow-Up Items for Next Session (REVISED after Wave 2)

- [x] All 10 USER-CORRECTIONs logged in MEMORY.md
- [x] 6 existing skills updated + 4 new skills created
- [x] 4 agents updated (vercel-deployment, cv-pipeline-engineer, opus-coach-architect, homography)
- [ ] Extend Pydantic schemas: `CornersNormalized`, `RawDetection`, `PlayerDetection`, `StateTransition`, `MatchData`
- [ ] TDD-first implementation of the CV spine (homography → pose → kalman → state_machine)
- [ ] Smoke integration on `data/clips/utr_match_01_segment_a.mp4`
- [ ] Single-pass `python-reviewer` over the complete spine
- [ ] Commit + push + PAUSE for team-lead review (Action 3 signal sprint is gated on this approval)

## Follow-Up Items for Next Session

- [ ] Phase 1 Day 1 (Wed Apr 22): implement `backend/cv/pose.py` with the probe's safeguards + player-filtering (anti-crowd logic)
- [ ] Annotate court corners for `utr_match_01_segment_a.mp4` via `tools/court_annotator.html`
- [ ] Implement `backend/cv/kalman.py` + Hungarian assignment for A/B identity stabilization
- [ ] Implement `backend/cv/state_machine.py` with 3-state per-player FSM
- [ ] Start TDD cycle on the 7 signals (test fixtures before impl)

## Day 0 Status: GO ✅

Proceeding to Phase 1 (CV pre-compute pipeline) on Wednesday.
