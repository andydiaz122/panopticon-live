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

---

## 2026-04-21 End-of-Day Block (post Phase-1 Action-2)

### What happened this session (chronological)
1. **Day 0 morning**: 10 USER-CORRECTIONs absorbed over two team-lead review waves (see [MEMORY.md](MEMORY.md) entries USER-CORRECTION-001 through 010).
2. **Late-morning infrastructure investment**: created 4 new specialized project skills (`physical-kalman-tracking`, `topological-identity-stability`, `match-state-coupling`, `vercel-ts-server-actions`), bringing the skill team to 12 orthogonal skills; updated 6 existing skills; updated 4 agents to reference the canonical rules directly in their charters. Committed as `db2a1e9`.
3. **Afternoon TDD-first CV spine** (Action 2): wrote tests before each module.
   - `backend/cv/homography.py` — 11/11 tests green
   - `backend/cv/pose.py` — 14/14 tests green
   - `backend/cv/kalman.py` — 8/8 tests green
   - `backend/cv/state_machine.py` — 12/12 tests green
   - **Total 45/45 tests green**, coverage 82.75%, ruff clean
   - Committed as `cd52758`

### Key architectural decisions this session
- **Absolute Court Half Assignment** supersedes Hungarian/Y-sort for player identity (USER-CORRECTION-007). Implemented in `backend/cv/pose.py::assign_players`.
- **Physical Kalman domain**: the Kalman filter operates on court meters and emits m/s so state-machine thresholds are physically meaningful (USER-CORRECTION-008). Enforced by `test_input_units_are_assumed_meters_not_normalized` regression.
- **MatchStateMachine** couples both players via bounce event so `split_step_latency` fires for the returner (USER-CORRECTION-010). Implemented in `backend/cv/state_machine.py`.
- **Vercel surface is pure Next.js**; `backend/` is strictly a local Mac Mini pre-compute tool (USER-CORRECTION-006). The scouting-report Managed Agent uses the TypeScript `@anthropic-ai/sdk` via Next.js Server Action.

### Non-obvious learnings captured in MEMORY.md
1. **Perspective warp compresses far half in image space** — the image-space net line is ~`y_norm=0.34` for a typical broadcast trapezoid, NOT `0.54`. Caught via TDD. (PATTERN-010)
2. **Ultralytics `.xyn` is pre-normalized [0,1]** — no manual W/H division needed. (PATTERN-004)
3. **Security hook trips on literal `exec` / `innerHTML`** — use `subprocess.Popen` + `textContent`/`createElement`. (PATTERN-006, PATTERN-007)
4. **Memory slope sign**: only positive > 200 KB/frame is a leak; negative = freed. (GOTCHA-007)
5. **YOLO sees 2-25 detections per frame on broadcast** (crowd, ballboys, linesmen); USER-CORRECTION-007 solves this canonically. (PATTERN-009)
6. **Managed Agents 2026-04-01 API shape** captured via Perplexity — `client.beta.agents.create(...)` + `client.beta.sessions.create(...)` + `agent_toolset_20260401`. (PATTERN-008)
7. **Plan-mode inheritance is silent** — dispatched sub-agents inherit the parent's plan-mode unless explicitly passed `mode: "acceptEdits"`. Cost a round-trip on the documentation save. (anti-pattern #33 re-learned)

### Bug journal
- **2026-04-21 late — perspective-warp test fixture** (`tests/test_cv/test_pose.py::test_assign_players_splits_by_court_half`): initial fixture used `image_y=0.40` for the far-side detection, expecting it to land in the far half. Actual projection via the trapezoid homography: `y_m ≈ 13.2` (above net line 11.885 → Player A's half, not B's). Fixed by moving far detection to `image_y=0.30`. Fix is captured in PATTERN-010.
- **2026-04-21 late — ruff N806 on `W`, `H`**: standard CV `width, height` uppercase idiom. Added per-file-ignore in `pyproject.toml` rather than renaming.

### What's NEXT (resume directives)

When this session resumes (or after compact):

1. **HOLD for team-lead review of CV Spine** — do NOT start Action 3 until explicit approval.
2. Once approved, begin Action 3 parallel signal sprint via `/devfleet`:
   - Fleet 1: `recovery_latency_ms`, `split_step_latency_ms`
   - Fleet 2: `serve_toss_variance_cm`, `ritual_entropy_delta`
   - Fleet 3: `crouch_depth_degradation_deg`, `baseline_retreat_distance_m` (enforce far-court fallbacks)
   - Fleet 4: `lateral_work_rate`
3. Each signal must have `test-forensic-validator` write tests FIRST with synthetic keypoint fixtures proving physical-realism assertions before any math is implemented.
4. After all 7 signals green, smoke integration on `data/clips/utr_match_01_segment_a.mp4` producing a full DuckDB row set + `match_data.json` pre-compute.
5. Then Phase 2 (offline Opus: Coach + HUD Designer + Haiku Narrator + scouting-report TypeScript Server Action).

### Documentation is safe to compact from this point
All 5 living docs reflect current state. MEMORY.md has 10 USER-CORRECTIONs + 13 PATTERNs + 5 DECISIONs + 8 GOTCHAs. TOOLS_IMPACT.md has Day-0 and Phase-1-late-session ROI blocks. PHASE_1_PLAN.md status line reflects where we are. CLAUDE.md prime directive unchanged. All agents + skills on main branch.
