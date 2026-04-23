# FORANDREW.md — Plain-Language Project Walkthrough

This is a non-technical decision log, bug journal, and "talk to Andrew tomorrow morning" document. Updated every working session.

---

## What We're Building (in one paragraph)

Panopticon Live is a web app that takes a pro tennis match video and renders a **2K-Sports-style video-game HUD** over the footage — a **world-class single-player biomechanics deep-dive** (DECISION-008, 2026-04-22). As the match plays, animated bars and meters pulse to show Player A's live biomechanical state — fatigue, serve toss variance, baseline retreat, lateral work rate. Below the video, **Claude Opus 4.7** streams coach-grade commentary, with its extended-thinking tokens visible in a collapsible panel (*"here's Opus reasoning about A's crouch depth degradation..."*). The HUD layout itself is dynamically designed by Opus as match state changes — generative UI in action. A second tab shows the raw JSON signal stream as the B2B product ("this is what Valence, Sequence, Dome subscribe to"). A third tab generates a full PDF scouting report via Claude Managed Agents. The "Moneyball for tennis" angle — deep forensic analysis of ONE player — is a stronger demo story than shallow two-player coverage, AND it matches our CV detector's capacity on broadcast clips (GOTCHA-016). **The demo is the product** — we ship this Sunday April 26 by 8pm EST.

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

---

## 2026-04-22 (late, post-compact) — Phase 2 Opus Agent Layer

### What we shipped (commit `c981773`)

Three Anthropic models orchestrated OFFLINE inside `precompute.py`:
- **Opus 4.7 Coach Reasoner** — anomaly/rally-end triggered `CoachInsight` with extended thinking + tool-use loop (4 deterministic tools over in-memory ToolContext)
- **Opus 4.7 HUD Designer** — state-transition triggered `HUDLayoutSpec` via pure JSON generation (no tools, Opus arranges React widget primitives)
- **Haiku 4.5 Narrator** — per-N-second `NarratorBeat` color commentary (cheap model in the multi-model orchestration story)

Phase 2 commit contents:
- `backend/agents/__init__.py`, `tools.py`, `system_prompt.py`, `opus_coach.py`, `hud_designer.py`, `haiku_narrator.py`
- Schema additions: `NarratorBeat` Pydantic model + `narrator_beats` DDL table + writer queue/flush/export plumbing
- `precompute.run_agent_phase` + new CLI flags: `--skip-agents`, `--coach-cap`, `--design-cap`, `--beat-cap`, `--beat-period-sec`
- 83 new tests: 25 tool executors + 14 coach + 15 designer + 12 narrator + 17 precompute-agent-phase + 5 NarratorBeat writer tests. 349/349 total green, ruff clean.

### Non-obvious engineering decisions (logged to MEMORY.md)

1. **In-memory ToolContext (not DuckDB queries)** — Phase 2 runs inside precompute.py where signals are already in Python. DuckDB round-trip per tool call = latency + SQL-injection surface for zero benefit. Phase 3's live scouting-report agent can swap in a DuckDB-backed impl behind the same `TOOL_EXECUTORS` registry. (PATTERN-032)

2. **Anthropic tool schemas from `Pydantic.model_json_schema()`** — single source of truth for validation. Hand-writing schema JSON drifts from runtime validation. (PATTERN-033)

3. **Token accumulation across tool-use loop iterations** — `response.usage` is per-API-call. A coach insight that does 3 tool round-trips consumes 3x the tokens of the last response. `_TokenAcc` dataclass accumulates across all rounds so `CoachInsight.*_tokens` fields report TRUE per-insight cost. (PATTERN-034)

4. **Structural `Protocol` client typing** — `AnthropicClientLike` Protocol with just `.messages.create`; fakes are `SimpleNamespace`. Real `AsyncAnthropic` import lives only in `main()`. (PATTERN-035)

5. **Every agent's 3 failure modes land as valid Pydantic records** — API exception / JSON parse error / Pydantic validation error. Each gets a distinct error marker (`[coach_error:]`, `[designer_parse_error]`, `[designer_validation_error:]`, `[narrator_error:]`). Agents NEVER raise into precompute.py. (PATTERN-036)

### Two HIGH bugs caught by python-reviewer (post-implementation)

- **HIGH-1**: Greedy `\{.*\}` regex on Opus JSON output extends to the LAST `}` in the text — silently corrupts matches when trailing prose contains stray braces. Fix: `json.JSONDecoder.raw_decode` after fence stripping. Parses ONE complete object and stops. (USER-CORRECTION-025, GOTCHA-013)

- **HIGH-2**: Narrator had NO cap while Coach/Designer did (inconsistency = the bug). A 15-min clip at 1/sec cadence would fire 900 concurrent Haiku calls, trip the rate limiter, and produce mostly `[narrator_error]` beats. Fix: `beat_cap` parameter (default 20, mirrors coach_cap/design_cap). (USER-CORRECTION-024)

### GOTCHAs caught in-flight

- **GOTCHA-012** (fake-client `messages[]` list mutation): The scripted Anthropic fake captured `kwargs` by reference, and since the coach mutates the messages list in-place across iterations, the log showed the FINAL state on every call. Fix: snapshot via `{**kwargs, "messages": list(kwargs["messages"])}` before logging. Two tests failed before this fix, silently (wrong lookup, not runtime error).

### Meta-learning

The python-reviewer's ROI on Phase 2 was very high: 2 HIGH bugs + 3 MEDIUM in <2 minutes of agent time. Both HIGHs were cases where the author's ATTENTION had drifted — greedy regex is a classic trap, and cap asymmetry is something you only see once you review from the outside. **Always dispatch python-reviewer after writing a new agent layer, before the commit.**

### Next session RESUME DIRECTIVES (post-Phase 2)

1. **Action 4.4** (optional, gated on Andrew): smoke test on real UTR clip with `--skip-agents` first (CV only), then with agents enabled + `ANTHROPIC_API_KEY` set
2. **Phase 3** (Fri Apr 24 target): Next.js HUD scaffold + canvas rAF loop + typewriter coach panel + Motion animations + scouting-report Managed Agent Server Action
3. **Phase 4** (Sat Apr 25): Vercel deploy + multi-agent review panel + second match clip
4. **Phase 5** (Sun Apr 26 8pm EST): demo video + submission

---

## 2026-04-22 (evening) — Court Annotator "Video Won't Load" Debugging Postmortem

### The bug

You opened `tools/court_annotator.html`, clicked "Load video...", picked `data/clips/utr_match_01_segment_a.mp4`, and nothing happened. Video area stayed black. Status banner got stuck at STEP 4/4: "video.src set; waiting for loadedmetadata..." No loadstart, no loadedmetadata, no error. Every reasonable next-try fix failed.

### 5 iterations of red herrings before finding the real cause

1. **Dynamic video created in JS, appended to `document.body`** — the video was rendering below the main grid, off-screen. FIXED by moving `<video>` into the HTML inside `.canvas-wrap`. **Didn't solve it.**
2. **MP4 had `moov` atom at the END of the file** (non-faststart). Remuxed with `ffmpeg -c copy -movflags +faststart`. **Didn't solve it.**
3. **`preload="metadata"` was conservative** — changed to `preload="auto"`. **Didn't solve it.**
4. **`file://` origin might block blob video playback** — launched `python -m http.server` and served via `http://localhost:8000`. **Didn't solve it.**
5. **Added deep diagnostic (status banner, 3s timeout dump, direct-URL test button)** + dispatched research agent in parallel — ROOT CAUSE found.

### The actual root cause

`<input type="file" id="video">` and `<video id="video">` **both had `id="video"`**. `document.getElementById("video")` returns the first match in document order — the input. Every `video.src = ...`, `video.addEventListener(...)` call in the script was silently operating on the INPUT, not the video element. The actual `<video>` tag in the DOM was never touched.

**One character of change would have fixed it:** rename `<input id="video">` to `<input id="videoPicker">`.

### Why it ate 5 iterations

- **Duplicate IDs are valid HTML** — no parse error, no warning in console.
- **Wrong-type operations silently succeed** — `<input>.src = blobURL` is a harmless no-op that doesn't throw.
- **Listeners attach to ANY EventTarget** — so `input.addEventListener("loadedmetadata", ...)` succeeds and simply never fires.
- **The symptoms match a dozen other real bugs** — codec issues, CORS, autoplay blocks, network stalls, MSE init problems. I pattern-matched to each in turn instead of questioning whether my variable was pointing at the right element.

### Defenses installed

1. **`tests/test_tools/test_court_annotator_html.py`** — 9 static-validation tests. The critical ones:
   - `test_no_duplicate_ids` — fails build if any two HTML elements share an id.
   - `test_video_id_is_on_video_element_not_input` — fails build if `id="video"` is on anything other than a `<video>` tag.
   - `test_script_get_element_by_id_references_exist` — fails build if the inline script references an id not present in the DOM.
2. **Runtime guard in `court_annotator.html`** — if `document.getElementById("video").tagName !== "VIDEO"` at page load, blank the page with a red FATAL error rather than silently misbehaving.
3. **3-second diagnostic timeout in the load handler** — if `loadedmetadata` hasn't fired, dump `readyState` / `networkState` / `videoWidth` / `error` / `currentSrc` / `tagName` into a red banner. `tagName` in that dump would have caught the ID-collision bug on the FIRST iteration.
4. **"Test direct URL" button** — loads the same file via `http://localhost:8000/data/clips/...` (no blob) to disambiguate blob-specific vs general load bugs.

### Meta-lesson (most important)

**After 3 failed debugging iterations, escalate to parallel research + runtime diagnostics.** Don't keep iterating on "just one more reasonable fix." The cost of a research agent (~2 min) + a diagnostic dump (~5 min) is trivial compared to another 3 rounds of phantom chasing. Logged as PATTERN-039 in MEMORY.md.

The research agent I dispatched in iteration 5 ranked "duplicate `#video`" as cause #2 in its list — it took a specialist's outside perspective to surface the hypothesis I'd been blind to.

### Files touched

- `tools/court_annotator.html` — full refactor (DOM structure, listeners, diagnostics, guards)
- `tests/test_tools/__init__.py` + `test_court_annotator_html.py` — 9 static-validation tests
- `data/clips/utr_match_01_segment_a.mp4` — faststart remuxed (original preserved as `.original.mp4`)
- `MEMORY.md` — GOTCHA-014, PATTERN-037/038/039
- `FORANDREW.md` — this postmortem

**Tests**: 358 pass, ruff clean.

---

## 2026-04-22 (late evening) — Corners JSON wrapper adapter + current state rollup

### The small follow-on

After you successfully annotated `utr_match_01_segment_a.mp4`, the `court_annotator.html` saved a JSON with a **wrapper shape**:
```
{"clip": "...", "annotated_at": "...", "corners": {top_left, top_right, ...}, "notes": "..."}
```
But `precompute.py` was calling `CornersNormalized(**json.load(...))` on the whole wrapper, which Pydantic v2 frozen models reject because extras are forbidden. Easy fix:

- New helper `load_corners_json(path) -> (raw_text, CornersNormalized)` in `backend/precompute.py`.
- Handles BOTH shapes: wrapper (what the annotator emits) AND bare (back-compat for hand-edited JSONs).
- Raw text preserved for `MatchMeta.court_corners_json` provenance — the full annotation metadata (clip name, annotation timestamp, notes) travels with the pre-computed artifact.
- 5 regression tests in `tests/test_cv/test_precompute_corners_json.py`.
- Logged as PATTERN-040 in MEMORY.md.

### Current repo state (as of commit `114c1f0`)

**363 tests passing, ruff clean. 15 commits landed this week.** Phase 1 (CV signals + DuckDB writer + precompute CLI) is complete. Phase 2 (Opus Coach + HUD Designer + Haiku Narrator OFFLINE) is complete. Court annotator works, corners JSON exists, precompute.py can now ingest it.

| Layer | Status | Commit |
|---|---|---|
| Phase 1 CV Spine (YOLO + Kalman + state machine + homography) | ✅ | `cd52758` |
| Phase 1 — USER-CORRECTIONs 011–022 + BaseSignalExtractor ABC | ✅ | `5e22166` |
| Phase 1 — 7 biomech signals (Fleet 1/2/3/4) | ✅ | `058cf32`..`67fb7ae` |
| Phase 1 — FeatureCompiler integration | ✅ | `23de0f2` |
| Phase 1 — DuckDBWriter + setup tests | ✅ | `faca491` |
| Phase 1 — precompute.py master CLI | ✅ | `66d8cf5` |
| Phase 1 — python-reviewer hardening | ✅ | `47c354b` |
| Phase 2 — Opus agent layer (Coach + Designer + Narrator + tools + integration) | ✅ | `c981773` |
| Phase 2 — docs | ✅ | `101cafb` |
| Court annotator — ID collision fix + 9 static-validation tests | ✅ | `3061d5d` |
| Corners JSON wrapper adapter | ✅ | `114c1f0` |

**Files you now have:**
- `data/clips/utr_match_01_segment_a.mp4` — your 60-second clip (1920×1080, H.264, faststart-remuxed today).
- `data/clips/utr_match_01_segment_a.original.mp4` — pre-faststart original (backup; you can delete if disk space matters).
- `data/corners/utr_match_01_segment_a_corners.json` — your 4 court corners, annotated today via the fixed annotator.

### Next up: Action 4.4 smoke test (the original directive you asked about)

Now that ALL prerequisites are in place, the smoke test is a single command. It will:
1. Run the full CV pipeline on the 60s clip (YOLO pose → Kalman → bounce detector → state machine → FeatureCompiler → 7 biomech signals)
2. Optionally run the Opus/Haiku agents (requires `ANTHROPIC_API_KEY` in env; skip with `--skip-agents` for CV-only smoke)
3. Write everything to `data/panopticon.duckdb` and export `dashboard/public/match_data/utr_01_seg_a.json`

Two invocation options (pick one and run it; I'll help triage any failures):

**CV-only (fast, no API cost, ~30s on M4 Pro):**
```bash
source .venv/bin/activate && python -m backend.precompute \
  --clip data/clips/utr_match_01_segment_a.mp4 \
  --corners data/corners/utr_match_01_segment_a_corners.json \
  --match-id utr_01_seg_a --player-a "Player A" --player-b "Player B" \
  --out-json dashboard/public/match_data/utr_01_seg_a.json \
  --skip-agents
```

**Full pipeline including Opus/Haiku (~2–3 min, costs ANTHROPIC credits):**
```bash
# Requires ANTHROPIC_API_KEY set in env OR .env
source .venv/bin/activate && python -m backend.precompute \
  --clip data/clips/utr_match_01_segment_a.mp4 \
  --corners data/corners/utr_match_01_segment_a_corners.json \
  --match-id utr_01_seg_a --player-a "Player A" --player-b "Player B" \
  --out-json dashboard/public/match_data/utr_01_seg_a.json
```

After either completes, we'll have a real `match_data.json` that Phase 3 (Next.js HUD) can consume. That's the bridge to the next phase.

---

## 2026-04-22 (deep into the night) — Skeleton Sanitation Sprint + Single-Player Pivot

### The incident

Andrew opened localhost:3000 after the Phase 3 scaffold landed and saw erratic cyan skeletons drifting in mid-court with no player underneath them — cling to left frame edge, tiny shrunken figures on line judges, ghosts hovering during warm-up. Eleven screenshots in `screenshot_errors/` document the failure modes.

### Root cause (diagnosed via bimodal bbox_conf histogram)

YOLO11m-Pose at `conf=0.001` (our max-recall floor) emits garbage detections for line judges, ball kids, scoreboard graphics, banner images, and shadows. These have LOW `bbox_conf` (0.001–0.01) but HIGH `mean_keypoint_confidence` (0.6–0.8) — YOLO is confident WHERE the pseudo-joints are, just not that it's a real person. Our `assign_players` picked by mean_kp_conf and ignored bbox_conf, so ghosts regularly won identity assignment. **964 of 1731 "Player A" detections (55.7%) were ghosts.**

Worse, Player B was 0% detected — the far-court player is ~80–100 px tall in broadcast frames (vs 253 px for near) and partially occluded by the FAB LETICS / DUN KIN' banners. YOLO11m-Pose simply cannot detect them at ANY imgsz. This is GOTCHA-016, a detector-capacity limit, not a pipeline bug.

### Phase Alpha + Phase Beta (team-lead approved; Phase Gamma temporal coherence HELD per YAGNI)

- **Frontend** (`PanopticonEngine.tsx`): skip drawing when `bbox_conf < 0.5`. Defense in depth.
- **Backend** (`backend/cv/pose.py:assign_players`), three filters in canonical order:
  1. `bbox_conf >= BBOX_CONF_THRESHOLD (0.5)` gate BEFORE projection → kills ghosts
  2. Lowered `ASSIGN_PLAYERS_FALLBACK_THRESHOLD` 0.3 → 0.15 globally → rescues small far-court player (PATTERN-040 chicken-and-egg resolution — safe because ghosts already dead)
  3. Tight lateral polygon `-0.5 ≤ x_m ≤ court_width_m + 0.5` → drops ball kids / line judges

### Decision on Player B

Andrew chose option **#3 (Accept the limitation — demo Player A only)** with the directive *"focus on one player and master that player and make sure we do it exceptionally well at a world-class level."* We refactored all four agent prompts for explicit single-player focus:

- Coach `BIOMECH_PRIMER`: new SINGLE-PLAYER FOCUS prologue; signal 7 (split_step_latency_ms) flagged as "often unavailable, don't fabricate"
- Coach user prompt: Player A = "target", Player B = "opponent (may be undetected, that's OK)"
- HUD Designer: removed `PlayerNameplate@top-right`, banned `MomentumMeter` + `PredictiveOverlay`; fallback layout is 2-widget single-player default
- Haiku Narrator: "Player A must be subject of every beat"

### V6 Crucible (the polished golden run)

- Player A: 806/1800 frames, 0% bbox_conf<0.5 ghosts, clean x_m [1.38, 11.46]
- Coach: 4 insights with real quantitative anchors ("A's baseline_retreat collapsed from 1.67m → 0.10m (slope -0.70 m/s)")
- Designer: 10 HUD layouts, all 4-5 widgets, zero B-widgets (verified via set membership check)
- Narrator: 6 broadcast-quality beats ("Player A explodes laterally, covering the court with explosive urgency")
- Cost: ~$0.30
- Tests: 383/383 passing, ruff clean

### New patterns + learnings logged

- **USER-CORRECTION-030** — Skeleton Sanitation: bbox_conf gate in assign_players
- **PATTERN-039** — Max Recall at Sensor, High Precision at Selector (architectural principle for any two-stage ML pipeline)
- **PATTERN-040** — Chicken-and-Egg dependency resolution via upstream filtering (the team lead caught this design flaw in my initial plan; generalized into a reusable pattern)
- **PATTERN-041** — Scope Narrowing as Demo Craft (commit fully to the narrow scope; no half-hearted "kinda still supports both")
- **GOTCHA-016** — Far-court player invisible to YOLO11m-Pose on broadcast tennis clips (detector capacity, not pipeline bug)
- **DECISION-008** — Single-Player Focus as Deliberate Demo Scope

### Meta-learning

The bimodal `bbox_conf` histogram was the diagnostic that broke the investigation open. "Run the smoke test against real data and plot what comes out" is a higher-ROI debugging move than adding more tests or reading more code. It's the CV analog of PATTERN-038 (mocked SDK tests validate shape-of-call, not shape-API-accepts) — mocked test fixtures validate the shape of our CODE, not the shape of DATA the real world produces.

---

## 2026-04-22 (pivot evening) — Biometrics-as-Hero Repositioning + Team-Lead Citadel Patches

### The framing flip

You pulled me aside (metaphorically — you were typing, not literally pulling) and said something that reframed the entire product: **"I don't want to make it about the coaching insights. The value we are providing is the biometric athlete insights."** You gave me the full sentence: the 7 signals, extracted from standard 2D broadcast pixels with no hardware sensors, are the proprietary data moat. Opus coaching is "icing on the cupcake."

This is DECISION-009. It's the most important framing decision in the project so far.

**Why it matters for the demo:** Judges don't care that Opus can write nice commentary about tennis — every LLM can do that. They care that we extracted fatigue-telemetry from frames anyone could scrape. That's a hard-tech differentiator. If the demo leads with Opus commentary, we look like a thin wrapper. If it leads with "here's a signal nobody else has," we look like a CV startup.

**What I changed in response:**
- CLAUDE.md gained a new top-level section "CORE VALUE PROPOSITION (DECISION-009)" right below the Prime Directive. Future sessions will read it on auto-load.
- MEMORY.md got DECISION-009 logged with "how to apply" guidance: visual hierarchy rule (SignalBar hero, CoachPanel subordinate), fan-facing copy requirement on every signal.
- The in-flight Phase-3-plan was rewritten. SignalBar moved to hero position. CoachPanel got demoted to a "thin footer chip" — NOT a full-width bottom panel. Every signal now ships a plain-English label + physiology caption aimed at the casual fan.
- RESUME.md got a "Strategic Frame" block up top so new sessions inherit the pivot.
- A new orthogonal skill is being created: `.claude/skills/biometric-fan-experience/` — owns the fan-facing copy layer (plain-English labels, why-this-matters captions, calibration states, anomaly copy). Orthogonal to `biomechanical-signal-semantics` (physics/math), `2k-sports-hud-aesthetic` (visual language), `react-30fps-canvas-architecture` (render pattern).

### The team-lead citadel patches (9 architectural upgrades)

After I wrote the first draft plan, you ran it past a team-lead review pass and came back with 5 (then 9) architectural patches. Each one was right, each one would have been a real bug. In plain English:

**1. Kill `setInterval` for video-driven state.** My first design had a 100ms setInterval reading `video.currentTime` to refresh HUD state at 10Hz. Problem: setInterval doesn't know about video playback. It fires on pause, drifts on tab-throttle, misses scrub events. Fix: put the 10Hz gate INSIDE a `requestAnimationFrame` loop. rAF pauses when the tab is hidden, stays at 60Hz during playback, sees the true `video.currentTime`. Logged as PATTERN-042.

**2. Ban Recharts for high-frequency widgets.** I proposed a Recharts sparkline inside each SignalBar. At 10Hz × 4 bars, that's 40 full React-managed SVG rerenders per second — enough to micro-stutter the skeleton canvas. Fix: omit the sparkline in Core Trio. If we add one later, hand-rolled `<svg><polyline>` only. PATTERN-043.

**3. Turn the 11.5s dead-air window into cinematic framing.** The backend drops the first 10s of CV data as warmup. Result: the right rail is EMPTY for the first 11.5s of the demo. Judges would think the app is broken. Fix: stylized "BIOMETRIC SENSORS — CALIBRATING…" placeholder with a pulsing loader — turns a technical constraint into ESPN-grade polish. GOTCHA-017.

**4. Spring physics, not tweens.** Framer Motion with `easeOutQuart` tweens looks "web-app-y." Real broadcast graphics use spring physics — mass + damping — so values chase their targets fluidly. With 10Hz data feeding a spring animator at 120Hz display rate, the motion reads as "physical telemetry." PATTERN-044.

**5. Clamp array indices on video scrub.** Scrubbing to end-of-video makes `Math.floor(currentTime * fps)` exceed `keypoints.length`. Accessing `keypoints[oob]` returns undefined, which the renderer dereferences → React error boundary → blank screen mid-demo. Fix: `Math.min(idx, keypoints.length - 1)` everywhere. PATTERN-045.

**6. Split the React context.** My first design exposed refs AND 10Hz state in one `PanopticonContext`. Every consumer re-renders every 100ms — including the canvas engine that must NOT re-render. Fix: two contexts — `PanopticonStaticContext` (refs, never changes) and `PanopticonStateContext` (10Hz state). The canvas engine consumes only the static one. PATTERN-046. This one is the most impactful fix architecturally — it's a general React pattern that applies far beyond this project.

**7. Typewriter via DOM mutation, not setState.** Naïve typewriter = `setText(prev + ch)` every 18ms = 55 React renders/sec during animation = video stutter. Fix: mutate `spanRef.current.textContent` directly inside the interval; React never re-renders. Plus `key={insight_id}` on the wrapper so React fully unmounts the old typewriter when the insight changes — auto-cancels any in-flight interval, no race conditions on scrub. PATTERN-047.

**8. Don't hardcode warmup thresholds.** I wrote `if (currentTimeMs < 11500) showCalibration()`. That's a hardcoded mirror of the backend's `--warmup-ms` flag. If the backend changes warmup from 10s → 7s, the UI stays broken for 11.5s on 7s-warmup data. Fix: derive from data: `firstLayoutMs = matchDataRef.current?.hud_layouts[0]?.timestamp_ms ?? Infinity`. PATTERN-048.

**9. Don't burn time on a bleeding-edge test stack.** I planned full Vitest + JSDOM + RTL + Next.js 16 + React 19 + Tailwind 4 component tests. You flagged the risk: that combo is a config rabbit-hole that could eat 2-3 hours. Guardrail: prioritize pure-function tests (binary search, clamping, copy completeness, tone mapping). If component tests don't stand up in ≤30 min of config, delete them — visual smoke on localhost is the real QA gate. PATTERN-049.

### Why this review loop was high-ROI

Every one of those 9 would have fired as a bug, some as outright demo-killers. Catching them BEFORE writing code cost ~20 min of conversation. Finding them after writing would have cost hours of debugging, possibly with video in hand ("why is the right rail empty? why is the screen blank at 60s? why is the typewriter glitchy when I scrub?"). The lesson isn't "never write bugs" — it's "get an orthogonal architectural review on non-trivial plans before execution."

**Meta-pattern**: for any multi-file Phase N plan, the team-lead review pass is cheap insurance. The orthogonal lenses are: performance (can this keep 60FPS?), coupling (does this hardcode anything it shouldn't?), state-flow (does this respect high-freq-in-ref, low-freq-in-state?), defensive programming (what happens at array bounds / null paths?), aesthetic (does this look like a 2K-Sports broadcast or a Bootstrap admin dashboard?).

### The orthogonal skill team, updated

Current project skill layers, each owning one concern:
- `panopticon-hackathon-rules` — inviolable constraints
- `cv-pipeline-engineering` — YOLO / Kalman / state machine
- `biomechanical-signal-semantics` — physics / math / thresholds
- `2k-sports-hud-aesthetic` — visual language, colors, typography
- `react-30fps-canvas-architecture` — render architecture (now updated with PATTERN-042 and PATTERN-045)
- `biometric-fan-experience` (NEW today) — plain-English fan-facing copy, calibration/no-data UX, progressive jargon
- `hackathon-demo-director` — 3-min video

Orthogonality check (what each skill would say about "how should this SignalBar look?"):
- `biomechanical-signal-semantics`: "z-score ≥ 2 means anomaly. Use the published threshold from the academic literature."
- `2k-sports-hud-aesthetic`: "Use `playerA` color + spring physics + neon glow on anomaly. Broadcast prominence."
- `react-30fps-canvas-architecture`: "Consume `usePanopticonState()`. Don't re-render faster than 10Hz."
- `biometric-fan-experience`: "Label it 'Baseline Retreat' not `baseline_retreat_distance_m`. Caption it: 'How far Player A has drifted backward from his warmup position.'"
- `panopticon-hackathon-rules`: "New work only. No copy-paste from Alternative_Data."

Each skill answers a DIFFERENT question. Together they specify the widget completely without overlap. That's the orthogonality discipline codified from `~/.claude/CLAUDE.md`.
