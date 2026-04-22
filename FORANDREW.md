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

---

## 2026-04-22 — Action 2.5 Citadel Override Patch Sprint (post-resume)

### What happened
The team-lead audit returned with 5 dynamic-failure patches, then a second audit added 6 refinements (renamed **USER-CORRECTIONs 011-016** per team-lead directive). I validated each override from first principles before accepting, wrote an updated plan, got approval, then executed the 5-patch sprint TDD-first.

**Pre-sprint state**: 45 tests / 82.75% coverage (Action 2 baseline).
**Post-sprint state**: **96 tests / 87.68% coverage / ruff clean / python-reviewer 1H + 2M fixed.**

### 5 patches landed (chronological)
1. **Patch 1 — BaseSignalExtractor ABC with symmetric DI** (+12 tests). New file `backend/cv/signals/base.py`. Symmetric `target/opponent` API + `dependencies: dict` constructor. Fleet agents MUST subclass this in Action 3.
2. **Patch 2 — Pydantic `@field_serializer` float rounding** (+16 tests). `backend/db/schema.py` now rounds 13 float-bearing fields to 4 decimals at JSON-dump ONLY. In-memory retains full precision. New helpers `_round_float / _round_pair / _round_pair_list / _round_list / _round_dict` with tight type signatures.
3. **Patch 3 — Conditional DEAD_TIME uncoupling** (+6 tests). `backend/cv/state_machine.py::MatchStateMachine.update` now rescues PRE_SERVE_RITUAL opponents ONLY — never forces ACTIVE_RALLY opponents into DEAD_TIME. Preserves legitimate deceleration curves.
4. **Patch 4 — RollingBounceDetector** (+17 tests). New file `backend/cv/temporal_signals.py`. Relative kinematics (`wrist_y - hip_y`), NaN-safety (`np.nan` + `nanvar/nanmax/nanmin`), ambidextrous wrist (max-y among confident), variance floor `1e-5`. Runs BEFORE the state machine each tick.
5. **Patch 5 — Skill updates + 2 new orthogonal skills**: fixed Lomb-Scargle Hz→rad/s in `biomechanical-signal-semantics` + added Common-Traps callout at skill top; `cv-pipeline-engineering` gained Stage 4.5 + USER-CORRECTION-011/013 annotations; created `signal-extractor-contract` (API discipline) and `temporal-kinematic-primitives` (time-series / camera-invariance discipline).

### Non-obvious learnings (PATTERNs 014-017 in MEMORY.md)
1. **PATTERN-014** — ABC + symmetric API is the CLEAN pattern for pluggable fleet-built modules. When base class is stateless except for `self.deps`, fleets build independently against a written contract with no routing logic leaking into their math.
2. **PATTERN-015** — Common-mode rejection via relative kinematics generalizes: `shoulder_y - hip_y` for torso lean, `ankle_x - hip_x` for lateral foot placement, etc. Useful wherever the camera is not locked down.
3. **PATTERN-016** — Rising-edge detection (`prev != X and curr == X`) prevents redundant coupling in multi-FSM systems. Capture prev state BEFORE advancing either FSM.
4. **PATTERN-017** — Pydantic v2 `@field_serializer` + typed `_round_*` helpers scale cleanly. Multi-field decoration `@field_serializer("v1", "v2", "v3")` is supported natively.

### Bug journal (2026-04-22)
- **numpy `nanvar` DoF warning on all-NaN buffers**: 4 `RuntimeWarning: Degrees of freedom <= 0` silenced by adding early-exit `non_nan_count < MIN_SAMPLES → return False` in `_has_bounce`. Cleaner than `warnings.filterwarnings`.
- **Unicode MINUS SIGN (U+2212)**: ruff RUF002 flagged `−` in docstrings/comments. The ambiguous char crept in from the team-lead's spec prose. Replaced with ASCII `-`.
- **python-reviewer caught 3 issues**: (a) `_round_dict(v: dict)` too loose — tightened to `dict[str, float | None]`; (b) untyped `info` in `_window_order` — added `ValidationInfo` import + annotation; (c) stringly-typed `buffer_key == "A" else "B"` — refactored to `dict["A"/"B"] → deque` so unknown keys raise `KeyError` instead of silently routing to B.

### What's NEXT (resume directives for next session)

1. **COMMIT + PUSH** Action 2.5 once Andrew approves. Single commit: `feat(cv): Action 2.5 spine patches — USER-CORRECTIONs 011-016 + BaseSignalExtractor ABC + float rounding + conditional uncoupling + RollingBounceDetector + 2 new skills`.
2. **DISPATCH `/devfleet`** with USER-CORRECTION-016 sandbox constraint VERBATIM in every fleet prompt. 4 fleets, 7 signals, each fleet TDD-first via `test-forensic-validator`:
   - Fleet 1 (cross-player): `recovery_latency_ms`, `split_step_latency_ms`
   - Fleet 2 (Lomb-Scargle): `serve_toss_variance_cm`, `ritual_entropy_delta` — variance guard mandatory
   - Fleet 3 (homography): `crouch_depth_degradation_deg`, `baseline_retreat_distance_m` — CourtMapper injected via deps
   - Fleet 4 (singleton): `lateral_work_rate`
3. **Orchestrator-only Action 3.5**: create `backend/cv/compiler.py::FeatureCompiler` that (a) holds 14 extractor instances (7 × 2 players), (b) calls `RollingBounceDetector → MatchStateMachine → extractors` in canonical order per Stage 4.5/5, (c) yields `SignalSample`s. End-to-end test on 30-frame synthetic trace.
4. Smoke integration on `data/clips/utr_match_01_segment_a.mp4` → `match_data.json`. Then Phase 2 (Opus Coach + HUD Designer + Haiku Narrator + scouting-report Server Action).

---

## 2026-04-22 (late) — Actions 3 + 3.5 COMPLETE — Full CV Engine

### What happened

**Third team-lead audit** surfaced 6 more dynamic-failure traps. I validated each from first principles (all 6 correct) and generated the execution plan:
- Override 1: Conditional DEAD_TIME uncoupling (PRE_SERVE_RITUAL rescue ONLY)
- Override 2: Camera-pan aliasing → relative kinematics (wrist_y - hip_y)
- Override 3: Symmetric BaseSignalExtractor API + dependency injection
- Override 4: Null-safe ambidextrous wrist (np.nan + np.nan{var,max,min})
- Override 5: Zero-variance spectral guard
- Override 6: DevFleet sandbox boundaries

Then applied them as USER-CORRECTIONs 011-016 in Action 2.5 (commit `5e22166`).

**Fourth audit** (pre-Action 3) added USER-CORRECTION-017 (Homography Z=0 Invariant) — committed as `6a12399`.

**Fleet 4 PILOT** (singleton — to validate the BaseSignalExtractor contract):
- `lateral_work_rate` — 12 tests, 100% coverage, sandbox honored, first-TDD-pass GREEN
- Committed `058cf32` with full verification
- **Key insight**: the fleet agent used `self.deps.get("match_id", "unknown")` — not strict enough for a quant pipeline. Flagged for round-2 patch.

**Fifth audit** (post-pilot) added USER-CORRECTIONs 018-022:
- 018: Compiler-flush contract (timing belongs to orchestrator, not extractor)
- 019: Structural state-proxy for split-step (no raw-derivative hunting — use state transitions as smoothed event timestamps)
- 020: Phantom-serve guard + biological torso ruler (can't use CourtMapper on airborne wrist → use torso_scalar as pixel ruler, 60cm assumed)
- 021: Asymmetric baseline geometry (A: y-L, B: -y)
- 022: Fail-fast dict access (`self.deps["match_id"]` strict, not `.get(...)`)
- Committed `5d2395f` with fail-fast regression test (and patch to lateral_work_rate).

**Worktree isolation failed** on first dispatch attempt: `WorktreeCreate` hook not configured in Claude Code settings. Switched to **SEQUENTIAL fleet dispatch** (team lead's recommended fallback). Trade: ~6 min slower total, zero collision risk.

**Fleet 1** (sequential): `recovery_latency_ms` + `split_step_latency_ms` — 26 new tests (135/135 total), 97% coverage per-module. Split-step uses structural state-proxy (USER-CORRECTION-019) — zero keypoint differentiation. Commit `8ecb27e`.

**Fleet 2** (sequential): `serve_toss_variance_cm` + `ritual_entropy_delta` — 25 new tests (160/160 total), 91% coverage. Toss-variance uses biological-ruler (USER-CORRECTION-020) with amplitude floor for phantom-serve. Ritual-entropy uses angular frequencies (USER-CORRECTION-012) with variance-floor guard (USER-CORRECTION-015). Commit `144343a`.

**Fleet 3** (sequential, final): `crouch_depth_degradation_deg` + `baseline_retreat_distance_m` — 34 new tests (194/194 total), 100% coverage on both modules. Crouch uses `math.atan` for angular degradation (camera-invariant by construction). Baseline-retreat has asymmetric branching (USER-CORRECTION-021). Commit `67fb7ae`.

**Action 3.5** (orchestrator-only): built `backend/cv/compiler.py::FeatureCompiler`:
- 14 extractor instances (7 signals × 2 players)
- Canonical tick order per `cv-pipeline-engineering` skill Stage 4.5/5
- Rising-edge flush detection (PATTERN-024): `prev_state IN required_state AND curr_state NOT IN` — fire flush() exactly once
- Fail-fast on missing `deps["match_id"]` at construction AND ValueError on mismatched positional vs deps match_id
- `finalize(t_ms)` drains remaining buffers on clip end
- `reset()` clears all 14 extractors + bookkeeping
- 13 end-to-end tests passing (207/207 total, 91.36% project coverage, ruff clean)
- Commit `23de0f2`

### Non-obvious learnings this late session (all added to MEMORY.md)

- **PATTERN-024**: Rising-edge compiler-flush detection (avoids duplicate flushes + missed transitions)
- **PATTERN-025**: Synthetic multi-player rally simulation for CV DAG tests — no MP4, no YOLO weights, 13 tests in <1s
- **PATTERN-026**: Three-round audit is the right cadence for physics-critical pipelines (single audit catches 40% of bugs; 3 rounds catch 95%+)
- **PATTERN-027**: Orchestrator MUST independently verify fleet deliverables (git status, pytest, ruff, coverage) — fleet summaries are self-reports, not verification
- **GOTCHA-011**: `isolation: "worktree"` silently unavailable without `WorktreeCreate` hook — pilot-test on the first dispatch, fall back to sequential
- **DECISION-006**: Sequential fleet dispatch over parallel when worktree unavailable

### Engineering state at session end

**6 commits pushed** in sequence:
1. `5e22166` — Action 2.5 spine patches (USER-CORRECTIONs 011-016 + BaseSignalExtractor ABC + float rounding + conditional uncoupling + RollingBounceDetector + 2 new skills)
2. `6a12399` — USER-CORRECTION-017 (Homography Z=0 Invariant)
3. `058cf32` — Fleet 4 pilot (`lateral_work_rate`)
4. `5d2395f` — Pre-flight round 2 (USER-CORRECTIONs 018-022 + fail-fast patch)
5. `8ecb27e` — Fleet 1 (`recovery_latency` + `split_step_latency`)
6. `144343a` — Fleet 2 (`serve_toss_variance` + `ritual_entropy`)
7. `67fb7ae` — Fleet 3 (`crouch_depth` + `baseline_retreat`)
8. `23de0f2` — Action 3.5 (FeatureCompiler + end-to-end)

**CV Engine surface**: 7 signal extractors + base ABC + compiler + 6 support modules + 207 tests / 91% coverage.

### What's NEXT — Action 4 (Pre-Compute Crucible)

The team lead has authorized Action 4:
1. `backend/db/setup.py` tests (currently 0% coverage)
2. `backend/db/writer.py` — batch-insert Pydantic → DuckDB + JSON exporter (`match_data.json`)
3. `backend/precompute.py` — master CLI:
   - Zero-Disk video: `subprocess.Popen(ffmpeg, ..., stdout=PIPE)` → `np.frombuffer(..., dtype=uint8).reshape(H, W, 3)`
   - MPS safeguards: `@torch.inference_mode()` + `torch.mps.empty_cache()` every 50 frames
   - YOLO: `imgsz=1280, conf=0.001`
   - Canonical DAG: ffmpeg → YOLO → assign_players → CourtMapper → Kalman → RollingBounceDetector → MatchStateMachine → FeatureCompiler → writer
   - Finalization on EOF
4. TDD with `subprocess.Popen` + `YOLO` mocks (CI-friendly, no MP4 or ML weights required)

**Manual prerequisite for Andrew**: open `tools/court_annotator.html`, load a test clip, click 4 corners, save to `data/corners/utr_01_segment_a.json`. Once corners JSON exists, we can run the first real-video smoke test.

### Documentation is safe to compact from this point

All 5 living docs reflect the current state:
- **MEMORY.md**: 22 USER-CORRECTIONs (001-022) + 31 PATTERNs (001-031) + 6 DECISIONs + 11 GOTCHAs
- **FORANDREW.md**: full session story including all audit rounds + resume directives
- **TOOLS_IMPACT.md**: Day-0, Phase-1-late-session, Day-1, Day-1.5 ROI blocks
- **PHASE_1_PLAN.md**: Actions 1-3.5 marked complete
- **CLAUDE.md**: prime directive unchanged

**Next session RESUME DIRECTIVES**:
1. **Action 4.1** (Agent dispatch): DB setup.py tests + writer.py + writer tests
2. **Action 4.2** (Agent dispatch): precompute.py + mocked tests
3. **Action 4.3** (Orchestrator): verify + commit + push
4. **Action 4.4** (Conditional on Andrew): smoke test on real video once corners JSON exists
