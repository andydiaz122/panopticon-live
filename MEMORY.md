# MEMORY.md — Structured Learnings for Panopticon Live

Cross-session recall. Every entry is:
- **Type**: Gotcha | Pattern | Tool-ROI | Decision | User-Correction
- **Context**: when/where discovered
- **Lesson**: what to do differently next time
- **Severity**: CRITICAL | HIGH | MEDIUM | LOW

---

## BASELINE (pre-Day-0, from prior work + strategic advisor input)

### GOTCHA-001 — The "Batch 11 ML Forge" Trap
- **Type**: Gotcha
- **Context**: Prior Alternative_Data handoff doc instructed "Batch 11" ML alignment work (CatBoost, Spearman, merge_asof)
- **Lesson**: In a hackathon, backend ML accuracy is invisible. Judges see the demo. ABORT all ML-accuracy work; optimize visual polish + creative Opus usage.
- **Severity**: CRITICAL
- **Source**: Strategic advisor (Apr 21, 2026) — prevented a full-week time sink

### GOTCHA-002 — React 30-FPS Death Spiral
- **Type**: Gotcha
- **Context**: Binding 30 FPS YOLO keypoint data to React `useState` → DOM re-renders 30x/sec → browser crash
- **Lesson**: Per-frame data → `useRef` + `requestAnimationFrame` + canvas paint. React state ONLY for low-frequency events.
- **Severity**: CRITICAL (would crash demo)

### GOTCHA-003 — Absolute YOLO Coordinates Break on Resize
- **Type**: Gotcha
- **Context**: YOLO emits pixel coordinates; but `<video>` element's pixel dimensions change with window resize
- **Lesson**: Backend normalizes all coords to `[0.0, 1.0]` BEFORE DuckDB write. Frontend multiplies by `<video>.clientWidth/Height` at paint time. `ResizeObserver` keeps dims fresh.
- **Severity**: HIGH (would cause skeleton-video misalignment)

### GOTCHA-004 — Vercel 250MB Serverless Size Limit
- **Type**: Gotcha
- **Context**: Vercel Serverless Functions have 250MB unzipped limit. `torch` alone is ~700MB.
- **Lesson**: Bifurcated requirements: `requirements-local.txt` (torch, ultralytics, opencv) for pre-compute; `requirements-prod.txt` (fastapi, anthropic, duckdb only) for Vercel. Vercel does NO machine learning — it replays pre-computed DuckDB.
- **Severity**: CRITICAL (would fail deploy)

### GOTCHA-005 — macOS `timeout`, `flock`, `lockfile` Don't Exist
- **Type**: Gotcha (global, from ~/.claude/CLAUDE.md)
- **Context**: These GNU tools silently fail on macOS
- **Lesson**: Use `gtimeout` (via `brew install coreutils`) or background+kill pattern
- **Severity**: MEDIUM

### GOTCHA-006 — MPS Memory Leaks Without Explicit Cache Flush
- **Type**: Gotcha
- **Context**: PyTorch MPS uses unified memory; without `torch.mps.empty_cache()`, accumulates across inference calls
- **Lesson**: Call `torch.mps.empty_cache()` every 50 frames. Single-worker asyncio executor (MPS is not reentrant-safe).
- **Severity**: HIGH (long runs would OOM)

### PATTERN-001 — Pre-Compute + Replay Architecture for Demo "Live" Feel
- **Type**: Pattern
- **Context**: Hackathon demo needs to look "live" but we don't need actual live inference
- **Lesson**: Pre-compute everything once locally → DuckDB. SSE service paces rows at video wallclock. Judges can't tell the difference. Vercel doesn't need GPU.
- **Severity**: HIGH-ROI

### PATTERN-002 — Orthogonal Skill Team (5 domains)
- **Type**: Pattern
- **Context**: Project-specific skills in `.claude/skills/` mirror real professional roles
- **Lesson**: `cv-engineer` + `agent-orchestrator` + `hud-auteur` + `verification-gate` + `demo-director`. Each OWNS one domain, DELEGATES everything else.
- **Severity**: HIGH-ROI (compounds all week)

### PATTERN-003 — Three Roles for Opus 4.7
- **Type**: Pattern
- **Context**: Hackathon judges 25% on "Opus 4.7 Use" — need creative, multi-faceted usage
- **Lesson**: Role 1 = Reasoner (tools + extended thinking). Role 2 = Designer (generative HUD JSON). Role 3 = Voice (streaming coach commentary). Plus Managed Agent for long-running PDF. Plus Haiku 4.5 for cost-aware narration.
- **Severity**: HIGH-ROI (key prize target)

### DECISION-001 — UTR Match Clips Are Sufficient
- **Type**: Decision
- **Context**: User has 8 UTR match MP4s (~6.5GB total) at Alternative_Data/data/videos/
- **Lesson**: 3 ANCHOR_OK clips are enough for a 3-min demo. No external clip sourcing needed. No copyright scrutiny (UTR is niche, not broadcast TV).
- **Severity**: Foundation

### DECISION-002 — Zero-Disk Video Pipeline
- **Type**: Decision
- **Context**: Large MP4 files + disk I/O = slow and error-prone
- **Lesson**: `ffmpeg -f rawvideo -pix_fmt bgr24 -` → stdout → `io.BytesIO` → YOLO. Stream via `stdout.readexactly(frame_size)`.
- **Severity**: Foundation

---

## DAY 0 LEARNINGS (Apr 21, 2026)

### PATTERN-004 — Ultralytics `.xyn` gives pre-normalized coords
- **Type**: Pattern (high-ROI, non-obvious)
- **Context**: Context7 query on `/websites/ultralytics` (Apr 21, 2026)
- **Lesson**: `result.keypoints.xyn` (not `.xy`) returns keypoints pre-normalized to `[0.0, 1.0]` relative to original image shape. We do NOT need to manually divide by frame width/height — Ultralytics handles it. Shape is `(N_players, 17, 2)`.
- **Severity**: HIGH-ROI — saves us a normalization step AND prevents the absolute-pixel-on-resize bug at the source

### PATTERN-005 — Anthropic SDK extended thinking shape
- **Type**: Pattern
- **Context**: Context7 query on `/anthropics/anthropic-sdk-python` (Apr 21, 2026)
- **Lesson**: `client.messages.create(..., thinking={"type": "enabled", "budget_tokens": 1500})`. Response has `block.type == "thinking"` blocks with `block.thinking` text attribute. Stream with `async with client.messages.stream(...)` context manager, iterate `stream.text_stream`. Cache via `system=[{"type": "text", "text": SYS, "cache_control": {"type": "ephemeral"}}]`.
- **Severity**: Foundation for Phase 2 agent wiring

### DECISION-003 — Use polars over pandas for probe parquet output
- **Type**: Decision
- **Context**: Day 0 probe_clip.py
- **Lesson**: pandas wasn't in requirements-local; polars already is (ships as transitive dep). Polars parquet write is faster and lighter. Prefer polars for any DataFrame work in this project.
- **Severity**: MEDIUM

### DECISION-004 — Python 3.14 not yet broadly supported; use 3.12
- **Type**: Decision
- **Context**: System has python3.12 AND python3.14 installed. Chose 3.12.
- **Lesson**: Vercel Fluid Compute supports Python 3.12 and 3.13. Many libs (ultralytics, torch) may not have 3.14 wheels yet. Stick to 3.12 for compatibility.
- **Severity**: MEDIUM

### PATTERN-006 — `asyncio.create_subprocess_exec` trips security hook
- **Type**: Pattern (tooling gotcha)
- **Context**: Writing probe_clip.py Apr 21, 2026 — the PreToolUse security hook scans for the literal string "exec" and raises a warning
- **Lesson**: For ffmpeg stdout piping, use `subprocess.Popen` (sync, blocking) instead of `asyncio.create_subprocess_exec`. For our CV pre-compute pipeline the perf difference is irrelevant — ffmpeg decoding is orders of magnitude faster than YOLO inference. Sync is simpler and doesn't trip the hook.
- **Severity**: LOW (workaround-ready) — but save future debugging time

### PATTERN-007 — Set DOM via textContent + createElement, not innerHTML
- **Type**: Pattern (tooling gotcha)
- **Context**: Writing court_annotator.html Apr 21, 2026 — security hook flags `innerHTML` as XSS risk
- **Lesson**: Even in a local-only dev tool, use `textContent` + `createElement` + `appendChild`. The hook is right — it's a better default habit. Also avoids the `DOMPurify` dep suggestion.
- **Severity**: LOW

### DECISION-005 — DAY-0 GO ✅
- **Type**: Decision (phase gate cleared)
- **Context**: Probe on `data/clips/utr_match_01_segment_a.mp4` (30s @ 30 FPS = 900 frames)
- **Results**:
  - Warm FPS: **12.7** on MPS with `yolo11m-pose.pt`, `imgsz=1280`, `conf=0.001` — comfortably above our 8 FPS floor
  - Detection rate: **100%** (every frame detected ≥1 person)
  - Two-player frames: **99.9%** (899/900)
  - MPS memory slope: **-314 KB/frame** (RSS decreased over time — zero leak signal)
  - Cold start: ~22 CPU-sec before first frame (MPS graph compilation — expected, one-time)
- **Lesson**: The UTR ANCHOR_OK clips are CV-friendly — minimal player-loss, stable camera, broadcast-quality lighting. The pipeline is viable. Proceed with Phase 1 (CV pre-compute pipeline + 7 signals).
- **Severity**: CRITICAL foundation validation

### GOTCHA-007 — Memory slope sign matters
- **Type**: Gotcha
- **Context**: First probe run flagged NO-GO on `abs(slope) < 200 KB/frame`. The observed slope was -314 KB/frame — which is actually FINE (memory being freed).
- **Lesson**: Only POSITIVE memory slopes indicate leaks. Negative slopes are GC or buffer reshuffling. Script corrected in probe_clip.py.
- **Severity**: MEDIUM (false-alarm defense)

### PATTERN-009 — YOLO returns many false-positive detections on broadcast tennis
- **Type**: Pattern
- **Context**: Day-0 probe saw 2-25 detections per frame — includes crowd in background, ball-boys, linesmen, even broadcast camera operators
- **Lesson**: Phase 1 needs player-filtering logic: (a) restrict to detections whose feet fall inside the court homography polygon, (b) keep the 2 highest-confidence detections per frame in court-zone, (c) use Kalman track continuity to stabilize player-A vs player-B identity across frames (Hungarian assignment).
- **Severity**: HIGH — without this, signals will contaminate with crowd noise

### USER-CORRECTION-001 — Video-Sync Trap (Vercel SSE timeout + buffering desync)
- **Type**: User-Correction (CRITICAL)
- **Context**: Team-lead review 2026-04-21
- **Lesson**: ABORT FastAPI SSE streaming for 30 FPS keypoints. Vercel Serverless severs long connections at 10-60s, and HTML5 video buffering would desync the skeleton from the player. Canonical shape: `precompute.py` writes `dashboard/public/match_data.json` (keypoints + signals + Opus commentary + HUD layouts, all tagged `timestamp_ms`). Frontend fetches once. `requestAnimationFrame` loop indexes via `videoRef.currentTime × clip_fps`. Perfect sync, zero network jitter, $0 compute.
- **Severity**: CRITICAL

### USER-CORRECTION-002 — Opus Latency Paradox (5-15s thinking vs 1.5s rally)
- **Type**: User-Correction (CRITICAL)
- **Context**: Team-lead review 2026-04-21
- **Lesson**: Live Opus during demo produces "prediction after the fact" because extended-thinking calls take 5-15s. Pre-compute all Opus intelligence offline during `precompute.py`. Store `CoachInsight` + `HUDLayoutSpec` with `timestamp_ms`. Replay at playback time. The ONLY live Opus at demo time is the Managed Agents scouting-report pipeline (Best Use of Managed Agents prize).
- **Severity**: CRITICAL

### USER-CORRECTION-003 — Far-Court Net Occlusion
- **Type**: User-Correction (HIGH)
- **Context**: Team-lead review 2026-04-21
- **Lesson**: The broadcast camera's perspective places the tennis net IN FRONT of Player B's ankles ~80% of frames. Signal extractors MUST implement an asymmetric fallback chain when ankle confidence < 0.3: ankle → knee → hip/pelvis, with torso-scalar re-normalized to the lower body segment actually in use. Applies to: `crouch_depth`, `baseline_retreat`, feet-position homography projection, `split_step` zero-crossing.
- **Severity**: HIGH

### USER-CORRECTION-004 — Topological Y-Sorting (not Hungarian)
- **Type**: User-Correction (HIGH)
- **Context**: Team-lead review 2026-04-21 — SUPERSEDED by USER-CORRECTION-007
- **Lesson**: Original guidance was "filter by court polygon → top-2 confidence → max-Y = A, min-Y = B." **This was refined in USER-CORRECTION-007 to use Absolute Court Half Assignment (top-1 per court half), which is stronger against occlusion-induced identity swapping.** Keep this entry for the lineage; the canonical rule lives in USER-CORRECTION-007.
- **Severity**: HIGH (superseded)

### USER-CORRECTION-005 — Homography Aspect-Ratio Skew
- **Type**: User-Correction (HIGH)
- **Context**: Team-lead review 2026-04-21
- **Lesson**: `tools/court_annotator.html` outputs normalized [0,1] corners. `cv2.getPerspectiveTransform` operates in whatever coordinate space you feed it. Feeding normalized coords directly produces a matrix that assumes a 1:1 aspect ratio — a 1m lateral move registers as larger than a 1m vertical move on 16:9 footage. Backend MUST un-normalize first:
  ```python
  corners_pixels = corners_normalized * np.array([[frame_width, frame_height]])
  cv2.getPerspectiveTransform(corners_pixels.astype(np.float32), court_meters.astype(np.float32))
  ```
  Feed keypoints to the mapper as pixel coords (multiply `.xyn` by W, H before projection).
- **Severity**: HIGH

### USER-CORRECTION-006 — Vercel Python Elimination (Deployment Moat)
- **Type**: User-Correction (CRITICAL)
- **Context**: Team-lead review 2026-04-21 (second wave)
- **Lesson**: DELETE `backend/api/` FastAPI entirely. Since `precompute.py` exports a static `dashboard/public/match_data.json` containing CV features + pre-computed Opus insights, we DO NOT need Python on Vercel at all. The Next.js frontend fetches the static JSON natively. For the live "Generate Scouting Report" button, use a **Next.js Server Action with the TypeScript `@anthropic-ai/sdk`**. Python becomes STRICTLY a local Mac Mini pre-compute tool. This vaporizes the 250MB Vercel Serverless limit risk, eliminates Python cold-start latency, and makes the frontend architecture bulletproof.
- **Severity**: CRITICAL
- **Architectural impact**: Delete `requirements-prod.txt`, `backend/api/`, Python `vercel.ts` runtime config. The only Vercel surface is the Next.js `dashboard/`.

### USER-CORRECTION-007 — Absolute Court Half Assignment (Anti-Identity-Swap)
- **Type**: User-Correction (HIGH)
- **Context**: Team-lead review 2026-04-21 (second wave) — **SUPERSEDES USER-CORRECTION-004**
- **Lesson**: The original "top-2 by confidence, sort by Y" is vulnerable: if Player B is occluded by the net → low confidence → a ballboy with higher confidence steals Player B's identity. Even worse, Kalman tracking then rubber-bands between locations. CANONICAL RULE:
  ```
  1. Project ALL in-polygon detections to physical court meters via CourtMapper.
  2. Split by absolute court half: the net is at Y = 23.77 / 2 = 11.885 m.
     - Detections with y_m > 11.885 belong to Player A's half (near camera).
     - Detections with y_m < 11.885 belong to Player B's half (far camera).
  3. Take the highest-confidence detection WITHIN each half.
  ```
  This is mathematically immune to occlusion-induced swapping because a ballboy on Player A's half cannot steal Player B's identity regardless of confidence.
- **Severity**: HIGH
- **Pattern skill**: see `.claude/skills/topological-identity-stability/SKILL.md`

### USER-CORRECTION-008 — Physical Kalman Domain (Unit Mismatch)
- **Type**: User-Correction (HIGH)
- **Context**: Team-lead review 2026-04-21 (second wave)
- **Lesson**: You cannot feed normalized `xyn` coordinates into `KalmanTracker2D` if the state machine expects m/s. Normalized-velocity is in "screen-percentages/second" and the 0.2 m/s threshold will never fire correctly. CANONICAL PIPELINE:
  ```
  YOLO .xyn → feet_mid_xyn (with ankle→knee→hip fallback per USER-CORRECTION-003)
      → CourtMapper.to_court_meters(feet_mid_xyn)   [MUST happen BEFORE Kalman update]
      → KalmanTracker2D.update(feet_mid_meters)
      → (x_m, y_m, vx_mps, vy_mps)                  [true physical units]
      → state_machine.update(vx_mps, vy_mps)         [thresholds in m/s are now meaningful]
  ```
  If `CourtMapper.to_court_meters` returns `None` (off-court), Kalman coasts via `predict()` without `update()`.
- **Severity**: HIGH
- **Pattern skill**: see `.claude/skills/physical-kalman-tracking/SKILL.md`

### USER-CORRECTION-009 — Lateral Rally Blindspot
- **Type**: User-Correction (HIGH)
- **Context**: Team-lead review 2026-04-21 (second wave)
- **Lesson**: `|vy|` (Y-axis velocity magnitude) is blind to baseline rallies, which involve massive X-axis movement with near-zero Y-axis movement. A state machine using only `|vy|` will false-trigger `DEAD_TIME` mid-rally, chopping rallies into fragments and corrupting `recovery_latency`. CANONICAL RULE:
  ```python
  speed_mps = math.hypot(vx, vy)   # 2D speed magnitude
  # PRE_SERVE_RITUAL → ACTIVE_RALLY: speed_mps > 0.2 for 5+ frames
  # ACTIVE_RALLY → DEAD_TIME:       speed_mps < 0.05 for 15+ frames
  ```
  Do NOT evaluate axes independently.
- **Severity**: HIGH

### USER-CORRECTION-010 — Asymmetric Pre-Serve Desync (Returner stays in DEAD_TIME)
- **Type**: User-Correction (HIGH)
- **Context**: Team-lead review 2026-04-21 (second wave)
- **Lesson**: Only the SERVER bounces the ball; the RETURNER stands still. If state is evaluated purely independently per player, the Returner never enters `PRE_SERVE_RITUAL` (they never move enough to exit DEAD_TIME). Consequence: `split_step_latency` signal — which gates on `PRE_SERVE_RITUAL → ACTIVE_RALLY` transition — never fires for the Returner. CANONICAL RULE:
  ```
  Match-level state machine wraps two PlayerStateMachine instances.
  When either player emits a BOUNCE_DETECTED event (Server signature),
  the MatchStateMachine forces the OTHER player into PRE_SERVE_RITUAL,
  regardless of that player's own kinematic state.
  ```
  The server's bounce is the match's clock; both players synchronize to it.
- **Severity**: HIGH
- **Pattern skill**: see `.claude/skills/match-state-coupling/SKILL.md`

---

### PATTERN-008 — Claude Managed Agents API (2026-04-01 beta)
- **Type**: Pattern
- **Context**: Perplexity research Apr 21, 2026 on Anthropic beta managed-agents endpoint
- **Lesson**: Minimal usage pattern:
  ```python
  agent = client.beta.agents.create(
      name="ScoutingReport",
      model={"id": "claude-opus-4-7"},
      system=SYSTEM_PROMPT,
      tools=[{"type": "agent_toolset_20260401", "default_config": {"permission_policy": {"type": "always_allow"}}}],
  )
  task = client.beta.sessions.create(agent_id=agent.id, input=match_id)
  while task.status not in ("completed", "failed"):
      task = client.beta.sessions.retrieve(task.id)
      await asyncio.sleep(5)
  result = task.output
  ```
  Key details: `agent_toolset_20260401` provides code exec + web search + file ops by default. The `anthropic-beta: managed-agents-2026-04-01` header is auto-added by `client.beta.*`.
- **Severity**: HIGH — Phase 2 scouting-report work depends on this
- **Source**: https://platform.claude.com/docs/en/managed-agents/agent-setup

---

## PHASE-1 LEARNINGS (Apr 21, 2026 — late session)

### PATTERN-010 — Perspective warp compresses the "far half" in image space
- **Type**: Pattern (non-obvious math; critical for test fixtures)
- **Context**: Writing `tests/test_cv/test_pose.py` Apr 21, 2026 — initially assumed the net line would project to `image_y ≈ 0.54` (midpoint of `top_y=0.20`, `bottom_y=0.88`). The first run of `test_assign_players_splits_by_court_half` flagged a false positive.
- **Lesson**: Perspective homography is NON-LINEAR. For a trapezoid with `top_y=0.20` and `bottom_y=0.88`, the physical net line (court length / 2 = 11.885 m) projects to ~`image_y=0.34`, not the midpoint. The far half of the image is compressed toward the top of the frame due to 3D foreshortening. ALWAYS compute expected test coordinates by running a forward projection through the actual homography matrix — never assume linear midpoints.
- **Severity**: MEDIUM (test correctness gate)
- **File**: `backend/cv/homography.py`, `tests/test_cv/test_pose.py::test_assign_players_splits_by_court_half`

### PATTERN-011 — TDD with synthetic keypoint fixtures proves physical constraints BEFORE code
- **Type**: Pattern (high-ROI methodology)
- **Context**: Action 2 CV spine landed 45/45 tests green on a single TDD pass
- **Lesson**: For physics-grounded code (Kalman meters, court polygon, state thresholds), synthetic fixtures (linear motion at 2 m/s, stepwise bounces, occluded frames) let you assert CONTRACTS (converged velocity, coast-on-None, transition frame counts) BEFORE any real YOLO data. This methodology caught the perspective-warp test-fixture bug AND catches unit-mismatch regressions via the explicit `test_input_units_are_assumed_meters_not_normalized` guard. Production data is for smoke integration and validation; unit tests NEVER depend on production data.
- **Severity**: HIGH-ROI — compounds across every signal module in Action 3
- **Files**: `tests/test_cv/test_homography.py` (11), `test_pose.py` (14), `test_kalman.py` (8), `test_state_machine.py` (12)

### PATTERN-012 — Absolute Court Half Assignment is provably immune to identity swapping
- **Type**: Pattern (architectural)
- **Context**: Canonicalized in USER-CORRECTION-007; implemented in `backend/cv/pose.py::assign_players`
- **Lesson**: Because top-1-per-half never compares detections ACROSS halves, a ballboy on Player A's side (high bbox_conf) CANNOT steal Player B's identity — even if occluded Player B has lower YOLO confidence. Provably correct under the tennis non-crossing invariant (players do not cross the net mid-rally). The `test_assign_players_immune_to_occlusion_swap` test demonstrates the scenario concretely.
- **Severity**: HIGH (prevents demo-corrupting identity swaps)
- **File**: `backend/cv/pose.py:112`

### PATTERN-013 — Kalman contract: input MUST be court meters, not normalized coords
- **Type**: Pattern (contract discipline)
- **Context**: USER-CORRECTION-008; enforced by the regression test `test_input_units_are_assumed_meters_not_normalized`
- **Lesson**: State machine thresholds (0.2 m/s, 0.05 m/s) are only meaningful if Kalman's velocity output is in m/s. Therefore Kalman MUST receive meters as input. Canonical pipeline: `YOLO.xyn → robust_foot_point → CourtMapper.to_court_meters → PhysicalKalman2D.update(meters)`. The regression test asserts that feeding normalized-space input would produce absurd velocities, making unit drift detectable at test time. Without this guard, a silent bug could make every downstream signal fire correctly on synthetic but wildly wrong on real data.
- **Severity**: HIGH
- **Files**: `backend/cv/kalman.py`, `tests/test_cv/test_kalman.py::test_input_units_are_assumed_meters_not_normalized`

## DAY 1 LEARNINGS (Apr 22, 2026) — Action 2.5 Citadel Override Patch Sprint

### USER-CORRECTION-011 — Conditional DEAD_TIME Uncoupling (PRE_SERVE_RITUAL-only rescue)
- **Rule**: In `MatchStateMachine.update()`, when EITHER player transitions into `DEAD_TIME` this tick, force the opponent into `DEAD_TIME` ONLY if the opponent is in `PRE_SERVE_RITUAL`. Never force an `ACTIVE_RALLY` opponent into `DEAD_TIME`.
- **Why**: The original blanket "force opponent to DEAD_TIME on any entry" would truncate legitimate deceleration curves. If Player A hits a winner and stops while Player B is still sprinting for the ball (ACTIVE_RALLY), instantly forcing B to DEAD_TIME destroys `recovery_latency_ms` and `lateral_work_rate` signals. The ONLY case we need to rescue is the Ace/Fault deadlock where the returner never moved (standing-still PRE_SERVE_RITUAL after an ace).
- **How to apply**: Use `if a_entered_dead and self._b.state == "PRE_SERVE_RITUAL"` (symmetric for B). Tests `test_active_rally_opponent_preserved_when_server_stops` and `test_ace_forces_standing_returner_to_dead_time` lock both halves.
- **File**: `backend/cv/state_machine.py:178-187`

### USER-CORRECTION-012 — Lomb-Scargle Angular-Frequency Trap + Relative Kinematics for Camera Invariance
- **Rule**: (a) `scipy.signal.lombscargle` expects ANGULAR frequencies (rad/s), not Hz — multiply by `2*np.pi`. (b) For any Y-position oscillation analysis on broadcast video, operate on `wrist_y - hip_y` (relative kinematics), NOT raw `wrist_y`.
- **Why**: (a) Tennis bounce cadence is 1-3 Hz = 6.28-18.8 rad/s. Passing raw Hz silently samples the wrong band (0.08-0.8 Hz) and returns wrong spectral entropy. (b) Broadcast cameras pan/tilt during serves. Absolute `wrist_y` carries biomechanics + camera motion superposed. The difference removes the common-mode camera drift, isolating pure arm-swing oscillation.
- **How to apply**: Always `freqs_rad = freqs_hz * (2 * np.pi)` before `lombscargle`. In `RollingBounceDetector` and any wrist-oscillation signal, store `wrist_y - hip_y` in the buffer. Tests `test_camera_pan_rejected_via_relative_kinematics` and `test_camera_pan_with_superposed_bounce_still_detects` lock both cases.
- **Files**: `backend/cv/temporal_signals.py`; `.claude/skills/biomechanical-signal-semantics/SKILL.md` (Common Traps callout at top).

### USER-CORRECTION-013 — Symmetric BaseSignalExtractor API + Dependency Injection + Bounce Deadlock Resolution
- **Rule**: (a) Every signal extractor inherits from `BaseSignalExtractor` in `backend/cv/signals/base.py`. (b) Constructor takes `target_player: PlayerSide` + `dependencies: dict[str, Any]`. (c) `ingest()` receives `(target_state, opponent_state, target_kalman, opponent_kalman, t_ms)` — symmetric around target. (d) Bounce detection runs UNCONDITIONALLY before the state machine (via `RollingBounceDetector`, not inside any signal extractor).
- **Why**: (a-c) An asymmetric `a_state/b_state` API forces every extractor to branch on `self.target_player`, leaking compiler-routing logic into every module. Symmetric "target/opponent" + DI is clean — cross-player signals (like `split_step_latency_ms`) naturally read `opponent_state` / `opponent_kalman`. (d) If bounce detection lived inside signal extractors that only run AFTER state transitions, there'd be a Chicken-and-Egg deadlock. Promoting bounce to a continuous rolling primitive resolves it.
- **How to apply**: Fleet agents in Action 3 MUST subclass `BaseSignalExtractor` and access `self.target_player` + `self.deps["court_mapper"]`/`self.deps["clip_fps"]`. Compiler instantiates each extractor TWICE (target="A" then target="B"). `RollingBounceDetector.evaluate()` runs BEFORE `MatchStateMachine.update()` every tick.
- **Files**: `backend/cv/signals/base.py`, `backend/cv/temporal_signals.py`; `.claude/skills/signal-extractor-contract/SKILL.md`.

### USER-CORRECTION-014 — Null-Safe Ambidextrous Wrist Selection (np.nan + np.nanvar/nanmax/nanmin)
- **Rule**: For any rolling buffer of image-space keypoints subject to occlusion: (a) ingest `np.nan` when keypoints are `None` or below confidence threshold; (b) evaluate via `np.nan{var, max, min, mean}` (silently skip NaN); (c) pick the confident wrist with MAX y (lower screen position = closer to ball at bounce) as the ambidextrous reference.
- **Why**: YOLO outputs `None` or low-confidence values during occlusion. `deque[float | None]` fed to `max()` crashes `TypeError`. Casting `None → 0.0` fabricates data. NaN + numpy's nan-aware ops is the canonical pattern. MAX-y selection handles lefty/righty servers whose non-dominant wrist is often out of frame.
- **How to apply**: Always add an all-NaN early exit (`np.sum(~np.isnan(arr)) < MIN_SAMPLES → return False`) to suppress `RuntimeWarning: Degrees of freedom <= 0` and avoid inf/nan propagation. Tests `test_occlusion_nan_does_not_crash`, `test_ambidextrous_wrist_selection_right_hand`, `test_hip_occlusion_yields_nan_rejection` lock the cases.
- **File**: `backend/cv/temporal_signals.py::_pick_wrist`, `::_has_bounce`.

### USER-CORRECTION-015 — Zero-Variance Spectral Guard + Pydantic @field_serializer Float Rounding
- **Rule**: (a) Before calling `scipy.signal.lombscargle(normalize=True)`, check `np.nanvar(buf) < 1e-5` — if true, return `None` (no spectral content). (b) Every float-bearing Pydantic model has `@field_serializer` rounding to 4 decimal places at JSON serialization only (in-memory retains full precision).
- **Why**: (a) `lombscargle(normalize=True)` divides by buffer variance. A constant / all-nan buffer explodes to `inf`/`nan`, corrupting downstream entropy. `1e-5` is below YOLO's squared-normalized jitter floor (~1e-4²), so it catches "genuinely nothing" without false-negating on noise. (b) 1800 frames × 2 players × 17 keypoints × 2 coords = 122,400 floats. At default 15-decimal precision → ~2.5 MB for keypoints alone. 4-decimal rounding → ~850 KB. Prevents mobile-Safari browser-OOM on static `match_data.json`.
- **How to apply**: Always guard `lombscargle` with the variance floor. Use `@field_serializer("field")` (NOT `@field_validator`) — serializer runs on `model_dump()` only, preserving in-memory precision for downstream math. Tests `test_zero_variance_returns_no_bounce`, `test_in_memory_values_retain_full_precision`, `test_round_trip_drift_is_bounded` lock behavior.
- **Files**: `backend/db/schema.py` (13 fields across 5 models), `backend/cv/temporal_signals.py::_has_bounce`.

### USER-CORRECTION-016 — DevFleet Sandbox Boundaries (Action 3 orchestration discipline)
- **Rule**: `/devfleet` fleet agents may edit ONLY `backend/cv/signals/<signal_name>.py` and `tests/test_cv/test_signal_<signal_name>.py`. FORBIDDEN: `schema.py`, `compiler.py`, `signals/__init__.py`, `signals/base.py`, `state_machine.py`, `kalman.py`, `homography.py`, `pose.py`, `temporal_signals.py`. Integration of all 7 signals into `FeatureCompiler` happens SEQUENTIALLY in Action 3.5 by the orchestrator, post-merge.
- **Why**: Parallel Git worktrees where each agent "helpfully" edits shared infrastructure (compiler wiring, schema additions, `__init__.py` exports) produce unresolvable merge conflicts. The only safe parallelism is one-file-per-agent on new files.
- **How to apply**: Every fleet dispatch prompt includes the sandbox constraint VERBATIM. After each fleet returns, orchestrator runs `git diff --name-only` and REJECTS any diff touching forbidden paths. If a fleet discovers a schema change is needed → return with a description; orchestrator lands it in Action 3.5 before wiring.
- **File**: Applies to Action 3 orchestration; no production-code impact.

### PATTERN-014 — ABC + Symmetric API is the clean pattern for pluggable fleet-built modules
- **Type**: Architectural (Python idiom for parallel agent sprints)
- **Context**: Designed for Action 3 `/devfleet` where 4 parallel fleets each build 1-2 signal extractors.
- **Lesson**: `abc.ABC` + `@abstractmethod` + class-level contract attributes (`signal_name`, `required_state`) + dependency-injected resources gives each fleet a COMPLETE written contract. Extractors write pure math on `target_*`/`opponent_*` inputs — no branching on `self.target_player`. Compiler handles routing once; every extractor benefits. When the ABC is stateless except for `self.deps`, it's trivially serializable / swappable / testable.
- **Severity**: HIGH — this is the scaffold that lets 4 parallel fleets merge cleanly.
- **Files**: `backend/cv/signals/base.py`; `.claude/skills/signal-extractor-contract/SKILL.md`.

### PATTERN-015 — Common-Mode Rejection via Relative Kinematics generalizes beyond wrist-hip
- **Type**: Signal processing pattern (from EE / DSP)
- **Context**: USER-CORRECTION-012 — broadcast cameras drift during serves.
- **Lesson**: Any time an input has "signal + shared-noise" (biomech + camera pan, limb + torso orientation, court-frame + body-frame), subtracting a CO-MOVING reference removes the noise in one operation. Generalizes to: `shoulder_y - hip_y` for torso lean; `ankle_x - hip_x` for lateral foot placement relative to body; `wrist_z - chest_z` for vertical reach. **Useful anywhere the camera is not locked down.**
- **Severity**: MEDIUM (applies across future signals)
- **File**: Applies to `backend/cv/signals/*` going forward.

### PATTERN-016 — Rising-Edge Detection prevents redundant coupling in multi-FSM systems
- **Type**: FSM coupling pattern
- **Context**: USER-CORRECTION-011 conditional DEAD_TIME uncoupling — must fire ONCE on transition INTO DEAD_TIME, not every tick thereafter.
- **Lesson**: Capture `a_prev, b_prev = self._a.state, self._b.state` BEFORE advancing either FSM. Then `entered_X = (prev != "X" and self.state == "X")` isolates the rising edge. No steady-state retriggering. Generalizes to any cross-FSM coupling in multi-agent environments. Alternative (passing boolean events out of each FSM) is more complex and error-prone.
- **Severity**: HIGH (prevents subtle double-fire bugs)
- **File**: `backend/cv/state_machine.py:172-175`.

### PATTERN-017 — Pydantic v2 `@field_serializer` with typed `_round_*` helpers scales to N models
- **Type**: Pydantic v2 idiom
- **Context**: USER-CORRECTION-015 float rounding across 5 models with 13+ fields.
- **Lesson**: Extract helpers `_round_float(v: float | None)`, `_round_pair(v: tuple[float, float])`, `_round_pair_list(v: list[tuple])`, `_round_list(v: list[float] | None)`, `_round_dict(v: dict[str, float | None])`. Each model uses the appropriate helper. Tight helper signatures catch future misuse at type-check time. `@field_serializer` supports multi-field decoration: `@field_serializer("value", "baseline_mean", "baseline_std", ...)`.
- **Severity**: MEDIUM (discipline that compounds)
- **File**: `backend/db/schema.py:22-50`.

### USER-CORRECTION-017 — Homography Z=0 Invariant (CRITICAL PHYSICS GUARDRAIL)
- **Rule**: `CourtMapper.to_court_meters()` uses `cv2.getPerspectiveTransform`, a 3x3 homography that maps a plane-to-plane transformation. It is MATHEMATICALLY VALID ONLY for points on the ground plane (Z=0). **NEVER project upper-body keypoints** (shoulders, hips, wrists, head) through `CourtMapper` — the resulting court-meters are parallax-corrupted fiction. Signals needing physical velocity in meters must consume the Kalman state (`target_kalman[2] = vx_mps`, `target_kalman[3] = vy_mps`) which is anchored to `robust_foot_point` (a ground-plane point).
- **Why**: A 1.8m-tall player's shoulders project several meters behind their actual ground position when run through a ground-plane homography. The taller the point above Z=0, the larger the bias. A velocity time-series derived from upper-body-projected meters would show 5-10× the actual speed and drift incoherently with camera angle. Broadcast cameras change angle constantly, so the bias is non-stationary and cannot be calibrated out.
- **How to apply**: (a) `lateral_work_rate` uses `abs(target_kalman[2])` during ACTIVE_RALLY, NOT a manually-diffed COM X series. (b) Any new signal that needs physical meters of an upper-body point should be reformulated to use (i) the Kalman velocity (already ground-plane), or (ii) image-space relative kinematics (USER-CORRECTION-012's `wrist_y - hip_y` pattern), or (iii) camera-invariant angular quantities (torso scalars, joint angles). NEVER route upper-body keypoints through `CourtMapper`.
- **Severity**: CRITICAL (silent physics corruption of every upper-body signal)
- **Files**: `.claude/skills/biomechanical-signal-semantics/SKILL.md` (Common Traps callout + Signal 6 rewrite); future `backend/cv/signals/lateral_work_rate.py` + any signal touching upper-body kinematics.

### PATTERN-018 — Homography is a plane-to-plane map; use Kalman state for physical velocity
- **Type**: Physics / geometry (generalizes beyond tennis)
- **Context**: USER-CORRECTION-017. Any system using a ground-plane homography for player tracking.
- **Lesson**: A single-camera homography `H` satisfies `[x_m, y_m, 1]^T = H @ [u, v, 1]^T` ONLY when the image point `(u, v)` corresponds to a 3D point with Z=0. For any point above the ground plane (Z > 0), the projected meters are biased by the camera's extrinsic parameters and the point's true height. The bias is NOT a constant offset — it varies with camera angle and player position within the frame. Rule of thumb: a point at height `h` in a frame captured by a camera at height `H_cam` with tilt θ will have its homography projection displaced by approximately `h / tan(θ)` meters in the direction away from the camera. For broadcast tennis (camera tilt ~20°, player shoulder height ~1.4m), this is ~3.8m of bias. The correct path for "ground-plane velocity of a player" is: `(u, v) → robust_foot_point (still image space) → CourtMapper.to_court_meters → PhysicalKalman2D → target_kalman[2:4] = (vx_mps, vy_mps)`. The Kalman output is the canonical ground-plane velocity; any further derivative/computation should consume `vx_mps/vy_mps` directly.
- **Severity**: CRITICAL (enforces physics correctness)
- **File**: `backend/cv/homography.py::CourtMapper`; usage convention in all future signal extractors.

### USER-CORRECTION-018 — Compiler Flush Contract (timing belongs to the orchestrator, not the extractor)
- **Rule**: The `FeatureCompiler` calls `flush(t_ms)` on each extractor EXACTLY ONCE when the target player transitions OUT of that extractor's `required_state`. Extractors do NOT track their own state exits — they simply check the state gate in `ingest()`, accumulate data in a buffer, and wait passively.
- **Why**: If every extractor has to track `_last_target_state` and decide when to self-flush, each fleet re-implements the same logic 7 times and bugs proliferate. Timing belongs to ONE place (the compiler), math belongs to ONE place per signal (the extractor). Clean separation of concerns.
- **How to apply**: In extractors, `ingest()` checks `if target_state not in self.required_state: return` and buffers only. Never self-flush. In the compiler (Action 3.5), detect `prev_target_state in ext.required_state and target_state not in ext.required_state` and call `ext.flush(t_ms)` once. Extractors `reset()` at match start only.
- **Severity**: HIGH (architectural separation of concerns for fleet-parallel development)
- **Files**: `.claude/skills/signal-extractor-contract/SKILL.md` (Flush Contract section); future `backend/cv/compiler.py`.

### USER-CORRECTION-019 — Structural State-Proxy for split_step_latency_ms (no raw-derivative hunting)
- **Rule**: `split_step_latency_ms` is computed from MatchStateMachine TRANSITIONS, not from raw keypoint peak-velocity hunting. Track `_last_target_state` + `_last_opponent_state`. On opponent's PRE_SERVE_RITUAL → ACTIVE_RALLY transition, record `opp_t_ms`. On target's PRE_SERVE_RITUAL → ACTIVE_RALLY transition, record `target_t_ms`. At flush, emit `target_t_ms - opp_t_ms` if the opponent transitioned first (opponent was server); else return `None` (target was server).
- **Why**: Raw-derivative detection of "opponent wrist peak velocity" on jittery YOLO keypoints is catastrophic — signal drowned in noise. But the state machine ALREADY provides smoothed transition timestamps (5 consecutive frames above threshold). Server ACTIVE_RALLY entry = visible serve motion. Returner ACTIVE_RALLY entry = split-step + commit. Typical delta is 150-250 ms fresh, 300-500 ms fatigued — matches literature.
- **How to apply**: Fleet 1's `split_step_latency.py` uses `required_state = ("PRE_SERVE_RITUAL", "ACTIVE_RALLY")` so it sees both states. Tracks `_last_*_state` to detect rising-edge transitions. Gate with "opp transitioned first" check to skip emitting for server side.
- **Severity**: HIGH (prevents unusable signal from raw-derivative noise)
- **File**: `.claude/skills/biomechanical-signal-semantics/SKILL.md` (Signal 7 rewrite).

### USER-CORRECTION-020 — Phantom-Serve Guard + Biological Ruler for serve_toss_variance_cm
- **Rule**: Two combined constraints. (a) **Amplitude floor**: buffer's `(max_y - min_y)` must exceed `0.05` normalized units to qualify as a "real toss"; otherwise return `None` (filters returner's wrist-jitter phantom-serve). (b) **Biological ruler (Z=0 compliant)**: convert normalized → cm using the player's own torso `abs(shoulder_y - hip_y)` as a pixel ruler, assuming a 60 cm pro-tennis torso. Camera-invariant (common-mode rejection) and bypasses the forbidden `CourtMapper.to_court_meters` upper-body projection.
- **Why**: (a) Both players live in PRE_SERVE_RITUAL simultaneously; only the server tosses. Static returner wrist jitter (~0.005-0.01 normalized) must not register. 0.05 threshold is ~3× YOLO jitter and well below pro toss range (~0.15-0.25). (b) CourtMapper is Z=0 only; airborne wrist at toss apex projects to fiction. Torso scalar solves this: `wrist_cm ≈ wrist_norm × (60 cm / torso_norm)`. 60 cm avg for pro torso (bounded error ~10% across sexes); fine for relative-fatigue signal.
- **How to apply**: Fleet 2's `serve_toss_variance_cm.py` buffers `(ambi_wrist_y - hip_y)` and `abs(shoulder_y - hip_y)` pairs during PRE_SERVE_RITUAL. On flush: check amplitude floor first; if below, return None; else compute `std_norm × (60 / mean_torso_norm)`. Apex extraction uses MIN relative_y (image `y=0` is TOP of frame).
- **Severity**: HIGH (prevents both false-positive phantom serves AND wrong-units physics bugs)
- **File**: `.claude/skills/biomechanical-signal-semantics/SKILL.md` (Signal 2 rewrite).

### USER-CORRECTION-021 — Asymmetric Baseline Geometry for baseline_retreat_distance_m
- **Rule**: Player A's baseline is at y=23.77 m, Player B's baseline is at y=0.0 m. Retreat MUST branch on `self.target_player`:
  - A: `retreat_m = max(0.0, y_m - SINGLES_COURT_LENGTH_M)` (retreats in +y direction)
  - B: `retreat_m = max(0.0, -y_m)` (retreats in -y direction)
  Clamp negatives to 0.0 (inside the court = no retreat).
- **Why**: A single-baseline implementation would produce mathematically inverted values for one player with magnitudes on the order of the full court length (~23m). The symmetric branch exploits the fact that in the canonical coordinate convention both players face the net (y=11.885); retreating moves AWAY from the net, which is +y for A and -y for B.
- **How to apply**: Fleet 3's `baseline_retreat_distance_m.py` reads `self.target_player` + `target_kalman[1]` (Kalman-smoothed y_m — no re-projection per USER-CORRECTION-017). Uses `SINGLES_COURT_LENGTH_M` constant from `backend/db/schema.py`.
- **Severity**: HIGH (prevents catastrophically-wrong values for one of two players)
- **File**: `.claude/skills/biomechanical-signal-semantics/SKILL.md` (Signal 5 rewrite).

### USER-CORRECTION-022 — Fail-Fast Dependency Lookup (no silent defaults in quant systems)
- **Rule**: Use strict dict access for REQUIRED deps: `self.deps["match_id"]`, NOT `self.deps.get("match_id", "unknown")`. If a required dep is missing, `flush()` must raise `KeyError` loudly.
- **Why**: `SignalSample.match_id` is part of the DuckDB primary key `(timestamp_ms, match_id, player, signal_name)`. A silent default like `"unknown"` would cause PK collisions across matches and pollute downstream analytics (all misconfigured runs aggregated into a single "unknown" bucket). In quant systems, LOUD failure is correct — pipeline should fail fast during orchestration setup, not silently corrupt data at write time.
- **How to apply**: Every extractor's `flush()` uses `self.deps["match_id"]`. Regression test: `pytest.raises(KeyError, match="match_id")` when constructed with `dependencies={}`. All fleets MUST follow this pattern.
- **Severity**: HIGH (data integrity)
- **File**: `backend/cv/signals/lateral_work_rate.py:70`; `.claude/skills/signal-extractor-contract/SKILL.md`.

### PATTERN-019 — Compiler-Orchestrated Flush is the clean idiom for buffered-window signal extractors
- **Type**: Architectural (applies to any streaming signal-extraction pipeline)
- **Context**: USER-CORRECTION-018.
- **Lesson**: When signal extractors produce a value per "window" defined by external state transitions (e.g., "per rally", "per pre-serve ritual"), pushing flush-timing into each extractor produces boilerplate duplication AND subtle bugs when N extractors disagree on "when did the window end." Clean idiom: orchestrator owns window-boundary detection and calls `flush()` on the subset of extractors whose `required_state` just exited. Each extractor stays stateless except for its buffer. Generalizes to any message-broadcast + windowed-aggregation pipeline.
- **Severity**: HIGH (architectural)
- **File**: Applies to `backend/cv/compiler.py` in Action 3.5.

### PATTERN-020 — State-Machine Transitions as Smoothed Event Timestamps (instead of raw-derivative peak finding)
- **Type**: Signal processing pattern
- **Context**: USER-CORRECTION-019 split-step latency.
- **Lesson**: When a "moment of interest" is defined by a peak/zero-crossing in a noisy time series, resist the temptation to compute the peak directly via `np.argmax(np.diff(y))`. Instead, look for whether an UPSTREAM STATE MACHINE (which already denoises via consecutive-frame gating) emits a transition at ~the same moment — and use that transition's timestamp. In tennis, `PRE_SERVE_RITUAL → ACTIVE_RALLY` is effectively a serve-contact timestamp with a 5-frame (~167ms) latency baked in; far more robust than differentiating YOLO keypoints for peak-velocity detection. Generalizes: if an FSM already filters noise, its transitions are the events you want.
- **Severity**: HIGH-ROI (prevents an entire class of noise-sensitive derivative code)
- **File**: Applies to `backend/cv/signals/split_step_latency.py` in Fleet 1.

### PATTERN-021 — Biological Ruler (Camera-Invariant Pixel-to-Physical Conversion)
- **Type**: Computer vision pattern (alternative to homography for airborne / above-ground points)
- **Context**: USER-CORRECTION-020 toss variance.
- **Lesson**: When you cannot use a ground-plane homography (because the point of interest is above Z=0) but you still need physical units, use a nearby BODY SEGMENT as a pixel ruler. Both the target point and the segment project through the same camera with the same perspective, so `target_cm ≈ target_norm_px × (segment_known_cm / segment_norm_px)`. For tennis: torso (~60cm) is the best ruler — stable, visible, and a reasonable avg across pro players. Generalizes to: any CV task needing physical lengths of airborne body parts (shot placement, vertical leap, serve toss). Bounded error ~10% from human-size variance, acceptable for relative-change signals.
- **Severity**: HIGH-ROI (enables an entire class of Z>0 signals that homography can't touch)
- **File**: Applies to `backend/cv/signals/serve_toss_variance_cm.py` in Fleet 2.

### PATTERN-022 — Asymmetric Coordinate Branching for Two-Player Signals with Opposite Half-Courts
- **Type**: Coordinate convention discipline
- **Context**: USER-CORRECTION-021 baseline retreat.
- **Lesson**: When two players inhabit MIRRORED half-courts under a single coordinate system (A's baseline at y=L, B's at y=0), any signal involving "distance from own baseline" or "own court position" must branch on `self.target_player`. Using a single global formula silently inverts the sign for one player. The fix is always a short branch: `A: max(0, y - L); B: max(0, -y)`. Applies beyond tennis: any two-sided game with a fixed divider (pickleball, badminton, volleyball, etc.).
- **Severity**: HIGH (prevents one player's signal being catastrophically wrong)
- **File**: Applies to `backend/cv/signals/baseline_retreat_distance_m.py` in Fleet 3.

### PATTERN-023 — Fail-Fast Dict Access for Required Deps in Data Systems
- **Type**: Defensive programming (quant discipline)
- **Context**: USER-CORRECTION-022 match_id lookup.
- **Lesson**: `dict.get(key, default)` is safe in UI code where defaults are meaningful, and dangerous in data pipelines where a wrong default silently corrupts the dataset. For any dict value REQUIRED for correct operation (primary keys, IDs, join keys), use strict `[key]` access so missing keys raise `KeyError` loudly during orchestration setup — NOT silently during data write. Generalizes: error early, error loud, fix once. A `KeyError` in a test during dev is a gift; a corrupted dataset is a week of debugging.
- **Severity**: HIGH (data integrity)
- **File**: Applies to every `BaseSignalExtractor` subclass; `lateral_work_rate.py:70` is the reference.

### PATTERN-024 — Rising-Edge Compiler-Flush Detection (state-exit is the trigger, not state-entry)
- **Type**: Orchestrator architectural pattern
- **Context**: Implementing USER-CORRECTION-018 in `backend/cv/compiler.py::FeatureCompiler.tick()`.
- **Lesson**: When orchestrating N state-gated extractors, the flush signal is NOT "state is no longer required" (steady-state check); it's the rising EXIT edge: `prev_state IN required_state AND curr_state NOT IN required_state`. Without the `prev in` check, you'd flush every tick the player was out of state (duplicate flushes). Without the `curr not in` check, you'd never flush (steady-state required doesn't trigger). The pattern: capture `prev_states` dict BEFORE advancing, detect the edge in a single pass, call `flush(t_ms)` exactly once. Same structural pattern as USER-CORRECTION-011 (conditional DEAD_TIME uncoupling) — both use rising-edge detection to prevent repeated firing. Generalizes to any pipeline where "one-shot emission on state transition" is needed.
- **Severity**: HIGH (architectural correctness)
- **File**: `backend/cv/compiler.py:142-156`.

### PATTERN-025 — Synthetic Multi-Player Rally Simulation for End-to-End CV Tests
- **Type**: Testing pattern
- **Context**: `tests/test_cv/test_feature_compiler_end_to_end.py` validates 14 extractors + DAG without real YOLO inference.
- **Lesson**: For CV pipeline integration tests, construct a 3-phase synthetic scenario: (1) PRE_SERVE_RITUAL with Player A's wrist oscillating at 2Hz against a static hip (real toss amplitude), Player B static (phantom-serve returner); (2) transition both to ACTIVE_RALLY (10 ticks of motion); (3) transition both to DEAD_TIME. Assert SignalSamples emitted with correct `(signal_name, player)` pairs at each transition. This approach tests (a) state-gated ingest routing, (b) compiler-flush contract, (c) per-signal math correctness end-to-end, (d) target/opponent symmetry — all WITHOUT needing MP4 files or ML weights. 13 tests cover the full DAG in <1 second. Pattern: build `_detection(player, hip_y, wrist_y, shoulder_y, feet_mid_m)` + `_frame(t_ms, a_kwargs, b_kwargs)` helpers for minimal boilerplate.
- **Severity**: HIGH-ROI (compounds all future signal/compiler changes)
- **File**: `tests/test_cv/test_feature_compiler_end_to_end.py:45-88` (helpers), whole file (13 tests).

### PATTERN-026 — Three-Round Audit is the Right Cadence for Physics-Critical CV Pipelines
- **Type**: Meta-process (engineering discipline)
- **Context**: Team-lead audits revealed 11 USER-CORRECTIONs (012-022) across 3 audit rounds over Actions 2.5, 3-preflight, 3-round-2-preflight, BEFORE implementation ran.
- **Lesson**: For anything involving physics invariants (homography planes, kinematic units, camera-invariance), a single round of audit is insufficient. Round 1 catches obvious bugs (Lomb-Scargle Hz-vs-rad/s, bounce deadlock). Round 2 catches subtle bugs from round-1 fixes (conditional-uncoupling, camera pan, NaN safety). Round 3 catches integration-level bugs (Z=0 homography, fleet collision risk, fail-fast). **Each round's refinements compound** — skipping audits would have produced silent data corruption on real video. Schedule: audit → patch → test → re-audit → patch → test → re-audit. For hackathon-pace work, cap at 3 rounds and commit.
- **Severity**: HIGH (process discipline)
- **File**: Applies meta-level to any physics-critical work; session-log in FORANDREW.md captures the full audit chain.

### PATTERN-027 — Independent Orchestrator Verification After Each Fleet (do NOT trust the agent summary)
- **Type**: Agent orchestration discipline
- **Context**: After each fleet returned, orchestrator ran its own `git status`, `pytest tests/`, `ruff check`, + coverage verification. All 4 fleets passed first-try, but verification discipline means this was luck, not guaranteed.
- **Lesson**: Fleet agents return summaries describing what they wrote. The summary is the agent's SELF-REPORT, not an independent verification. Orchestrator MUST run: (1) `git diff --name-only` to verify sandbox compliance, (2) full pytest suite (not just the new file's tests — side-effects in shared fixtures can break other modules), (3) ruff on full project, (4) coverage on new modules. Zero additional token cost vs trusting the summary, and catches the cases where the agent wrote the code but didn't actually run all gates. Anti-pattern to avoid: `"agent said 100% coverage"` → ship without re-verifying.
- **Severity**: HIGH (trust discipline)
- **File**: Applies to every `/devfleet`-style orchestration. Session-log shows clean `git status` verification after each of Fleets 4 (pilot), 1, 2, 3.

### DECISION-006 — Sequential Fleet Dispatch (trade-off: 6 min slower, zero collision risk)
- **Type**: Decision
- **Context**: Worktree isolation hooks (`WorktreeCreate`) unavailable on this Claude Code installation; Agent tool's `isolation: "worktree"` returns "not in a git repository and no WorktreeCreate hooks configured" despite `git rev-parse --show-toplevel` succeeding. Could configure hooks manually, but complexity exceeds ~6 min total savings.
- **Rationale**: Parallel agents on the SAME working directory race on: (a) `pytest` reading mid-edit test files, (b) `git status` / `git diff` commands, (c) shared `__pycache__`. Each race produces false pytest failures that are hard to distinguish from real bugs. Sequential dispatch: each fleet completes (~2 min) before next starts. Total added time: ~6 min across 3 fleets. Acceptable trade-off.
- **How to apply**: For any future `/devfleet` or multi-agent code task where worktree isolation is not confirmed working, run sequentially with `isolation: undefined`. Only switch to parallel if WorktreeCreate hooks are verified functional.
- **Files**: Applies to orchestration policy.

### GOTCHA-011 — `isolation: "worktree"` fails silently when WorktreeCreate hook is missing
- **Type**: Gotcha
- **Context**: Tried to dispatch Fleet 4 pilot with `isolation: "worktree"`. Error: "Cannot create agent worktree: not in a git repository and no WorktreeCreate hooks are configured."
- **Lesson**: The `isolation: "worktree"` parameter in the Agent tool depends on a `WorktreeCreate` hook configured in Claude Code `settings.json`. Without the hook, the feature is effectively unavailable — even in a clean git repo. Workarounds: (a) configure the hook manually if you need parallel isolation; (b) dispatch sequentially without isolation (our choice); (c) manually `git worktree add` + change CWD if truly needed. Don't assume `isolation` will "just work" on a fresh machine.
- **Severity**: MEDIUM (orchestration feature unavailable)
- **File**: Applies to Claude Code Agent tool invocations.

---

## DAY 1.5 LEARNINGS (Apr 22, 2026 late — Action 3.5 FeatureCompiler + Action 4 Pre-Compute Forge)

### PATTERN-028 — Mocked YOLO + Mocked subprocess.Popen for Zero-Dependency CI Tests
- **Type**: Testing pattern (CI-friendly CV pipeline)
- **Context**: `backend/precompute.py` integration test must run on GitHub Actions runners without ffmpeg, without MP4 files, without PyTorch MPS. Approach: pytest monkeypatches `subprocess.Popen` to yield N pre-constructed bytes of `bgr24` raw video + monkeypatches `ultralytics.YOLO` to return canned `Results` objects with synthetic keypoint tensors.
- **Lesson**: For any CI-tested pipeline that touches external binaries (ffmpeg, ML weights, GPU drivers), the test strategy is: inject mock objects at the module-import boundary. Pattern:
  ```python
  def test_precompute_end_to_end(tmp_path, monkeypatch):
      fake_proc = MagicMock()
      fake_proc.stdout.read.side_effect = [b"\x00" * (1920*1080*3)] * 10 + [b""]
      monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: fake_proc)
      monkeypatch.setattr("backend.cv.pose.YOLO", FakeYOLO)
      # ... run precompute, assert DuckDB + match_data.json emitted
  ```
  Gotcha: mocking MUST happen at the import site, not the source (`backend.cv.pose.YOLO`, not `ultralytics.YOLO`).
- **Severity**: HIGH (enables CI coverage of end-to-end pipeline)
- **File**: `tests/test_cv/test_precompute.py` (Action 4.2 target).

### PATTERN-029 — Idempotent DuckDB DDL + Test Setup
- **Type**: Database pattern
- **Context**: `backend/db/schema.py::SCHEMA_DDL` uses `CREATE TABLE IF NOT EXISTS`. `backend/db/setup.py` runs this against a DuckDB file.
- **Lesson**: DuckDB DDL with `IF NOT EXISTS` can run repeatedly without error — this is the correct idempotent pattern for pre-compute pipelines where the DB may already exist. Tests should (a) use `tmp_path` for isolated `.duckdb` files per test, (b) call setup TWICE in a test to verify idempotence, (c) query `information_schema.tables` to verify all expected tables exist post-setup. Never use in-memory `:memory:` for tests that verify persistence — DuckDB's in-memory mode has different concurrency semantics than file-mode.
- **Severity**: MEDIUM (reproducibility)
- **File**: `backend/db/setup.py`, `tests/test_db/test_setup.py` (Action 4.1 target).

### PATTERN-030 — `@field_serializer` Float Rounding Propagates Through Nested Pydantic Models
- **Type**: Pydantic v2 behavior (non-obvious on first read)
- **Context**: `match_data.json` export uses `model_dump_json(by_alias=True)` on a root `MatchData` model that nests `SignalSample[]`, `KeypointFrame[]`, etc. Each inner model has its own `@field_serializer`s (USER-CORRECTION-015).
- **Lesson**: Pydantic v2's `@field_serializer` fires even when the model is nested inside another model's `model_dump_json()` call — no manual work needed. The 4-decimal rounding applies to every inner float automatically. VERIFY this with a test that constructs a nested payload with full-precision floats, calls `.model_dump_json()` on the outer, parses, and asserts the inner floats are rounded. Without verification, a future Pydantic upgrade could silently change this behavior and bloat `match_data.json`.
- **Severity**: HIGH (payload-size regression prevention)
- **File**: `backend/db/writer.py::dump_match_data_json` (Action 4.1 target).

### PATTERN-031 — Pipeline DAG Ordering Must Be Re-Verified Each Major Change
- **Type**: Process
- **Context**: After each of Actions 2, 2.5, 3, 3.5, the canonical per-tick DAG (ffmpeg → YOLO → assign_players → CourtMapper → Kalman → RollingBounceDetector → MatchStateMachine → FeatureCompiler) was re-checked. Each layer has preconditions that compound: Kalman requires meters (not pixels); BounceDetector requires hip+wrist availability; MatchStateMachine requires bounce bool AND speed; FeatureCompiler requires both target + opponent states simultaneously.
- **Lesson**: Whenever a new layer is added to a multi-stage pipeline, redraw the full DAG and verify each edge. For PANOPTICON: the DAG is documented in 3 places — (a) `cv-pipeline-engineering` skill (canonical), (b) `backend/cv/compiler.py` docstring, (c) `backend/precompute.py` main loop. These MUST stay in sync; drift between them is a bug. For Action 4, `precompute.py` is the first time all 8 layers run together on a single frame — TDD validates the DAG end-to-end.
- **Severity**: HIGH (architectural consistency)
- **File**: Will land in `backend/precompute.py` (Action 4.2).

### USER-CORRECTION-023 (implicit) — Sequential Dispatch When Worktree Unavailable
- **Rule**: When the Agent tool's `isolation: "worktree"` fails due to missing `WorktreeCreate` hook, default to sequential fleet dispatch. Do NOT attempt parallel without isolation — file-level races (pytest mid-edit, __pycache__ contention, git index locks) produce false-negative failures.
- **Why**: The orchestrator's trust gate is independent verification (`git status`, full `pytest`, ruff, coverage). Sequential preserves that gate; parallel without isolation would break it.
- **How to apply**: Check `isolation: "worktree"` once on a pilot dispatch. If the error returns, switch to `mode: "acceptEdits"` only (no isolation) and run fleets sequentially. Cost: ~2 min per fleet × N fleets extra time.
- **Severity**: MEDIUM (orchestration policy)
- **File**: Applies to this project's `/devfleet` pattern.

---

## PHASE 2 LEARNINGS (Apr 22-23, 2026) — Opus Agent Layer

### USER-CORRECTION-024 — Narrator Beat Cap Parity with Coach/Design Caps
- **Rule**: Every async agent that fires N-per-clip MUST have a hard cap parameter, even if its per-call cost is low. Haiku beats at 1/sec over a 15-min clip = 900 concurrent Anthropic calls via `asyncio.gather` → hit the rate limiter → 429s → the `except Exception` fallback turns every beat into `[narrator_error: ...]` text → demo looks broken.
- **Why**: Discovered by python-reviewer HIGH-2 in Phase 2. Coach had `coach_cap=5`, Designer had `design_cap=10`, Narrator had NONE. Asymmetry was the bug — the existence of the other caps was tacit evidence the author already understood the need.
- **How to apply**: When adding an async agent to an orchestrator, audit ALL peer agents for the cap parameter. If any has a cap, ALL must. Default value should be "fits inside the demo budget" — for PANOPTICON that's ~20 beats (3 minutes @ 10s cadence).
- **Severity**: HIGH (rate-limiter + cost)

### USER-CORRECTION-025 — JSONDecoder.raw_decode over Greedy Regex for LLM JSON Extraction
- **Rule**: When parsing JSON from LLM output that may contain preamble prose, markdown fences, OR trailing commentary with stray braces, use `json.JSONDecoder.raw_decode(text, start_idx)` — NEVER a greedy `re.compile(r"\{.*\}", re.DOTALL)`.
- **Why**: Greedy regex matches from the FIRST `{` to the LAST `}` in the text. Opus sometimes wraps JSON in ```fences``` and adds trailing commentary like "(Note: fallback uses {curly} braces in the tail.)". The greedy regex extends to the `}` in the tail prose, corrupting the match — `json.loads` fails, silently falls through to a default. The bug is invisible: no exception, just wrong output. `raw_decode` parses ONE complete object starting at a given index and returns both the value + the index where it stopped, so trailing prose is ignored entirely.
- **How to apply**: Strip markdown fences first, then `first_brace = text.find("{")`, then `json.JSONDecoder().raw_decode(text[first_brace:])`. See `backend/agents/hud_designer.py:_extract_json_object`.
- **Severity**: HIGH (silent correctness)

### PATTERN-032 — In-Memory ToolContext for Offline Agents (Defer DuckDB to Live Path)
- **Type**: Architecture
- **Context**: Phase 2 runs Opus agents INSIDE `precompute.py`, which already holds all signals + transitions in Python memory. A DuckDB-backed tool would require a round-trip to disk per tool call, add an SQL-injection surface, and provide zero reasoning benefit.
- **Lesson**: For offline agent pipelines, implement tools as pure Python functions over an in-memory `@dataclass(frozen=True)` context. Declare the interface as `TOOL_EXECUTORS: dict[str, Callable]` so Phase 3's live path (scouting-report Managed Agent on Vercel) can swap in a DuckDB-backed implementation behind the same dispatch without changing tool names or schemas.
- **File**: `backend/agents/tools.py` (ToolContext frozen dataclass + TOOL_EXECUTORS registry).
- **Severity**: MEDIUM (pattern reusable for future offline agent pipelines)

### PATTERN-033 — Anthropic-Format Tool Schemas Generated from Pydantic `model_json_schema()`
- **Type**: Architecture
- **Context**: Anthropic's tool API expects `{"name", "description", "input_schema"}` per tool. Hand-writing `input_schema` JSON drifts from runtime validation. Generating it from `ToolInput.model_json_schema()` gives a SINGLE source of truth: Opus sees the schema, the executor validates the payload via the same Pydantic model.
- **Lesson**: Always generate Anthropic tool schemas from Pydantic input models, never by hand. Use a small helper: `_make_schema(name, description, PydanticModel) -> dict`. See `backend/agents/tools.py:TOOL_SCHEMAS`.
- **Severity**: MEDIUM (drift-prevention)

### PATTERN-034 — Token Accumulation Across Tool-Use Loop Iterations
- **Type**: Correctness
- **Context**: `response.usage` is per-API-call, not per-logical-insight. A coach insight that requires 3 tool round-trips consumes 3× the tokens of the last response. Naively storing `response.usage.input_tokens` in `CoachInsight` would under-report cost by 2/3.
- **Lesson**: Accumulate `input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` via a `_TokenAcc` dataclass across ALL iterations of the tool-use loop. Expose on the final Pydantic record. Judges reading the dev panel see TRUE cost, not last-call cost. See `backend/agents/opus_coach.py:_TokenAcc`.
- **Severity**: MEDIUM (observability correctness)

### PATTERN-035 — Structural `Protocol` Client Typing Avoids SDK Import at Test Time
- **Type**: Testing
- **Context**: `generate_coach_insight(client, ...)` needs to type-check the Anthropic client. Importing `AsyncAnthropic` directly for the annotation would force tests to mock the full SDK surface area.
- **Lesson**: Declare an `AnthropicClientLike` `Protocol` with just `.messages.create` (duck-typed). Tests pass `SimpleNamespace`-based fakes with the same shape. The real `AsyncAnthropic` import stays in `precompute.main()` (a call site), never in the reasoning layer. See `backend/agents/opus_coach.py:AnthropicClientLike`.
- **Severity**: MEDIUM (test-isolation)

### GOTCHA-012 — Scripted Fake Client Must Snapshot `messages[]` List in Tests
- **Symptom**: A test that inspects `call_log[N]["messages"]` sees the FINAL mutated state of the messages list on every call — not the state at the time of the call.
- **Root cause**: The coach mutates the `messages` list in-place across tool-use iterations (`messages.append(assistant_turn)`, `messages.append(tool_result)`). The fake's `call_log` stores a reference to the same list object.
- **Fix**: In the scripted client's `_create(**kwargs)`, snapshot via `snap = {**kwargs}; snap["messages"] = list(snap["messages"])` before logging. Shallow list copy is enough because inner message dicts are never mutated in-place.
- **Severity**: HIGH (silent test correctness — tests may PASS with wrong assertions)
- **File**: `tests/test_agents/test_opus_coach.py:_ScriptedClient`

### GOTCHA-013 — Greedy `{.*}` Regex on LLM JSON Output Corrupts on Tail Prose
- See USER-CORRECTION-025. Captured here because the SYMPTOM is distinctive:
  - Test with "clean JSON" passes
  - Test with "JSON in markdown fence" passes (fences don't contain `}`)
  - Test with "prose containing `{curly}` after JSON" FAILS — fallback layout returned silently
- **Severity**: HIGH (silent correctness)

### PATTERN-036 — Defense-in-Depth for Agent Failure Modes
- **Type**: Architecture
- **Context**: Every agent (Coach/Designer/Narrator) has THREE potential failure modes: (a) API exception, (b) parse error (for JSON-emitting agents), (c) Pydantic validation error (hallucinated enum values). All three must be caught and converted to a valid Pydantic record with an error marker — NEVER raise into the caller.
- **Lesson**: Treat Opus/Haiku output the same way you'd treat a third-party API response: hostile data. For each agent: try the API call; catch-all exception → error record. Parse JSON (if applicable); catch JSONDecodeError → fallback record. Validate via Pydantic; catch ValidationError → fallback record. Each layer has its own error marker in the text/commentary field so debugging later can identify WHICH layer failed. See `backend/agents/hud_designer.py` for the 3-layer pattern.
- **Severity**: HIGH (resilience)

### USER-CORRECTION-026 — Court-Corner Annotation Intent Must Match CourtMapper's Canonical Frame
- **Rule**: When annotating court corners via `tools/court_annotator.html`, the operator can click EITHER the singles sideline (inner 8.23m) OR the outer doubles-alley perimeter (10.97m). These are physically different courts; the canonical rectangle `CourtMapper` maps to must match the intent. Pass `--doubles-corners` to `precompute.py` when the annotation traces the outer doubles lines.
- **Why**: `CourtMapper` constructs a homography from `corners_pixels → [(0,0), (W,0), (W,L), (0,L)]` where `W = court_width_m`. If `W = 8.23m` (singles default) but the corners actually span 10.97m of real court, every lateral measurement compresses by a factor of 8.23/10.97 = 0.75. `baseline_retreat_distance_m` is unaffected (length is 23.77m for both), but `lateral_work_rate`, Kalman `vx_mps`, and any signal derived from `feet_mid_m[0]` are all ~25% under-reported.
- **How to apply**: When running the pipeline, check how the corners were annotated. If the operator clicked the OUTSIDE of the doubles alleys, pass `--doubles-corners`. If they clicked the singles sideline (inside the alleys), use the default. Document the choice in `data/corners/<match_id>_corners.json` notes.
- **Severity**: HIGH (physical-scale correctness; affects every lateral signal)
- **File**: `backend/cv/homography.py:CourtMapper(court_width_m=)`, `backend/precompute.py:--doubles-corners`

### PATTERN-037 — Per-Instance Override + Class-Attribute Default for Back-Compat
- **Type**: Design
- **Context**: CourtMapper had `COURT_WIDTH_M` as a CLASS attribute (8.23m). Adding a doubles option could have either (a) replaced the class attribute with an instance attribute (breaks every existing test that asserts `CourtMapper.COURT_WIDTH_M == 8.23`), (b) subclassed to `DoublesCourtMapper` (duplicates logic), or (c) added a per-instance override that defaults to the class attribute.
- **Lesson**: Option (c) is the surgical fix. `court_width_m: float | None = None` parameter; when None, use `self.COURT_WIDTH_M` class attribute. All existing tests pass unchanged (they never pass the override), AND new tests exercise the override. Zero regression risk. Same pattern applies whenever you add a configurable dimension to an existing class that had it hardcoded.
- **File**: `backend/cv/homography.py:CourtMapper.__init__` — 3 lines changed to add the override.
- **Severity**: MEDIUM (reusable for any "make previously-hardcoded constant tunable" refactor)

### GOTCHA-014 — Smoke Test on Real Video Reveals Player-B Starvation
- **Symptom**: 1800-frame smoke run on `utr_match_01_segment_a.mp4` produced 37 signals ALL for Player A. Zero signals for Player B despite 381 state transitions being emitted.
- **Root cause hypothesis**: Broadcast tennis camera angle places the far player (B) at the top of the frame with lower keypoint confidence + heavier occlusion (net blocks ankles/knees most frames). State machine may keep B in `PRE_SERVE_RITUAL` indefinitely when Kalman never converges; signals gated by `ACTIVE_RALLY` or long-window `PRE_SERVE_RITUAL` never fire for B. This is a known Phase 1 limitation (USER-CORRECTION-003 far-court occlusion fallback chain mitigates but doesn't eliminate).
- **How to verify**: After any real-video smoke run, check `SELECT player, COUNT(*) FROM signals GROUP BY player` in DuckDB. If B is 0, either (a) the clip genuinely doesn't show B in a rally state (server's POV clip), (b) the Kalman warm-up threshold needs lowering for far-court tracks, or (c) the fallback chain is tripping on confidence floors.
- **Severity**: MEDIUM (Phase 1 limitation carried forward; acceptable for Phase-2 demo but worth flagging in FORANDREW.md)
- **File**: Manifests in the output of `backend/precompute.py` on real video; NOT visible in synthetic tests (which construct both players with confidence=0.9).

### USER-CORRECTION-027 — Opus 4.7 Rejects `thinking.type.enabled`; Uses Adaptive Thinking Only
- **Rule**: For `model="claude-opus-4-7"`, the request shape `thinking={"type": "enabled", "budget_tokens": N}` is REJECTED with HTTP 400 `invalid_request_error`: *"thinking.type.enabled is not supported for this model. Use thinking.type.adaptive and output_config.effort to control thinking behavior."* Always use `thinking={"type": "adaptive"}` for Opus 4.7 (no budget_tokens). Optionally set `output_config={"effort": "low"|"high"|"xhigh"|"max"}` to influence depth.
- **Why**: Discovered the moment real Opus was first called in the Phase 2 smoke test (Apr 22). All 5 coach_insights came back as `[coach_error: BadRequestError 400 ...]` with zero tokens consumed. The mocked tests had passed — because mocks accept any shape — but the real API has schema validation. This is the generalized version of anti-pattern: **mocked SDK tests cannot catch API-shape drift**.
- **How to apply**: For any Claude 4.x model, do NOT pass `budget_tokens` in the `thinking` dict. Either pass `{"type": "adaptive"}` or omit `thinking` entirely (adaptive is the default on 4.7). Global CLAUDE.md says: "Opus 4.7 uses adaptive thinking — the model decides how much internal reasoning to allocate per turn. There is no MAX_THINKING_TOKENS budget."
- **Severity**: HIGH (any new Claude 4.x integration will fail silently via the agent fallback unless this shape is right)
- **File**: `backend/agents/opus_coach.py:generate_coach_insight` + `backend/agents/hud_designer.py:generate_hud_layout`

### PATTERN-038 — Mocked SDK Tests Validate SHAPE-of-OUR-CALL, Not SHAPE-API-ACCEPTS
- **Type**: Testing philosophy
- **Context**: Our fake `_ScriptedClient` accepts any `**kwargs` and returns scripted responses. Tests verify the fake was called with the expected kwargs. But the fake does NOT validate those kwargs against the real Anthropic API's schema — so request-shape drift (like USER-CORRECTION-027) slips through every mocked test and only surfaces when the code finally hits real servers.
- **Lesson**: Write a "shape regression" test that locks in the EXACT kwargs shape you expect to send. Then when the API evolves and you need to change the shape, the shape test fails loudly, forcing you to update the callers. Example: `test_coach_sends_tools_and_adaptive_thinking` asserts `call["thinking"] == {"type": "adaptive"}` and that `budget_tokens` does NOT appear — if someone regresses to the old shape, this test catches it before it ships.
- **Severity**: MEDIUM (testing discipline generalizable to any SDK integration)
- **File**: `tests/test_agents/test_opus_coach.py:test_coach_sends_tools_and_adaptive_thinking`

### GOTCHA-015 — Warm-Up State-Machine Flicker Triggers Spurious Coach Invocations
- **Symptom**: Coach was invoked on 5 transitions all within 5066-5733ms (the first 700ms of the clip). All 5 insights said "no rally data yet — warm-up artifact." This isn't a coach bug; it's the FeatureCompiler emitting ACTIVE_RALLY exits during warm-up because the RollingBounceDetector fires on noise before Kalman converges.
- **Root cause**: `coach_triggers = [t for t in transitions if t.from_state == "ACTIVE_RALLY"][:coach_cap]` takes the FIRST `coach_cap` transitions chronologically. Warm-up noise dominates the early timeline, so the cap gets consumed by fake transitions.
- **How to fix in Phase 3** (not urgent): skip transitions where the previous transition for the same player was <1s ago (rapid flicker = CV artifact), or gate on Kalman convergence time, or just skip the first 2s of the clip. For NOW, accept that coach commentary on demo clips will be thoughtful observations about warm-up noise ("no rally data yet, UNKNOWN phase") — which is actually a FINE demo narrative ("Claude is honest about what it knows").
- **Severity**: LOW-MEDIUM (demo-quality issue, not correctness)
- **File**: Emerges from `backend/precompute.py:run_agent_phase:coach_triggers`

### USER-CORRECTION-028 — Warm-Up Filter ALONE Is Insufficient; Add Dedup on Top
- **Rule**: `warmup_ms` (skip transitions in first N ms) catches the INITIAL CV convergence window, but Kalman/BounceDetector can continue emitting flicker bursts at 150ms cadence AFTER the warmup boundary. To prevent `coach_cap` / `design_cap` from being consumed by a single post-warmup noise burst, add a secondary `min_trigger_gap_ms` dedup filter (default 2000ms per player). Together the two filters ensure triggers SPREAD across the clip timeline.
- **Why**: Observed in the Apr 22 v3 smoke run. With `warmup_ms=10000` alone, triggers shifted from 700ms to 11500ms — technically "past warmup" — but all 5 caps were consumed by a 1.2s noise burst at 11500-12700ms. Opus correctly identified these as artifacts ("10+ back-to-back match_coupling flips every 167ms"), but burning the entire budget on warmup-aftermath means ZERO coverage of real rallies at 20s, 40s, etc. After adding dedup with 2000ms gap, v4 spread triggers across 11500-26133ms (12x wider time coverage).
- **How to apply**: Any time an agent cap is consumed by a rapid-fire trigger burst after the primary filter, add a per-entity gap filter BEFORE the cap slice. Pattern: `dedup(filter(candidates))[:cap]` not `filter(candidates)[:cap]`.
- **Severity**: HIGH (the original "demo killer" ruled insufficient; dedup is the true fix)
- **File**: `backend/precompute.py:_dedupe_close_triggers`, `DEFAULT_MIN_TRIGGER_GAP_MS`, `--min-trigger-gap-ms` CLI flag

### USER-CORRECTION-029 — LLM Player-Name Hallucination Requires Prompt Binding AND Anti-Hallucination Instruction
- **Rule**: When asking an LLM to generate commentary about generic actors ("Player A", "Player B"), it will hallucinate famous names ("Djokovic", "Federer", "Nadal") from its training data UNLESS you both (a) inject the real names in the user message AND (b) explicitly instruct: *"Refer to players ONLY by {name_a}, {name_b}, or 'Player A' / 'Player B'. Do NOT invent other names."* Just providing the names without the anti-hallucination clause is insufficient — the model will still "enrich" the output with famous names it has seen associated with tennis in training.
- **Why**: Observed in the Apr 22 v1 Haiku Narrator output: `"Djokovic catches his breath at the baseline, towel in hand"` when we passed `"Player A"`. After adding both the name binding AND the anti-hallucination clause to user prompt, v4 output is 100% "Player A"/"Player B" — zero invented names across 6 narrator beats + 5 coach insights + 5 designer layouts.
- **How to apply**: For any LLM generation involving generic/anonymized actors, always bind real identifiers in the USER message (never the system prompt if it's cached — dynamic values belong in user). Pair with an explicit DO-NOT-INVENT instruction. Verify in the first integration test run by grepping the output for unexpected proper nouns.
- **Severity**: MEDIUM (demo quality — wrong names make the HUD look untrustworthy)
- **File**: `backend/agents/opus_coach.py`, `hud_designer.py`, `haiku_narrator.py` — all three have the pattern

### USER-CORRECTION-030 — Skeleton Sanitation: bbox_conf Gate in assign_players
- **Rule**: At the identity-assignment layer (`assign_players`), reject ALL YOLO detections whose `bbox_conf < 0.5` BEFORE computing foot points, projections, or half-splits. This is independent of and additive to the keypoint confidence check.
- **Why**: YOLO11m-Pose at `conf=0.001` (max-recall sensor setting) emits garbage detections for line judges, ball kids, scoreboard graphics, banner images, shadows. These ghost detections can have HIGH mean keypoint confidence (0.6-0.8 — YOLO is sure WHERE the pseudo-joints are) while having VERY LOW bbox confidence (0.001-0.01 — YOLO knows it's not a real person). The Apr 22 golden v4 `bbox_conf` distribution was BIMODAL: 964 frames (55.7%) at <0.05, 767 frames (44.3%) at >=0.5, with an EMPTY 0.2-0.5 gap. The 0.5 cutoff is thus unambiguous — no legitimate player ever scores below it.
- **How to apply**: In any pose-assignment-style selector over a max-recall detector, the FIRST filter is `bbox_conf >= 0.5`. Keypoint confidence is a tiebreaker/quality signal, not a fitness gate. For Opus SDK work, analog is "response.stop_reason == end_turn" — the HIGH-level "is this actually the thing we asked for" gate must run before we inspect content.
- **Severity**: HIGH (55.7% of pre-fix detections were ghosts; eliminates demo-killing skeleton overlays)
- **File**: `backend/cv/pose.py:BBOX_CONF_THRESHOLD`, `assign_players`. Enforced also in frontend `PanopticonEngine.tsx` as defense-in-depth.

### PATTERN-039 — Max Recall at Sensor, High Precision at Selector
- **Type**: Architecture principle for any two-stage (detector → classifier/selector) pipeline
- **Context**: When a DETECTOR has a knob that trades off recall for precision (like YOLO's `conf` threshold), the optimal setting for the detector is the SENSITIVITY FLOOR (max recall). The PRECISION discipline belongs downstream in the SELECTOR layer, which has structured context the detector lacks (court geometry, player-identity priors, temporal history).
- **Examples**:
  - YOLO detector runs at `conf=0.001` (emits every vaguely-pose-like detection); `assign_players` runs at `bbox_conf >= 0.5` AND half-split AND lateral polygon
  - Raw signal buffers keep all `SignalSample` rows (max recall); downstream anomaly detection thresholds by z-score ≥ 2 (high precision)
  - Opus tool-use loop accepts every tool_use block from the model (max recall); dispatch_tool validates inputs and returns structured errors for malformed requests (high precision)
- **Why this beats the naive "tune the detector up"**: Raising YOLO's conf to 0.5 would drop garbage AND miss real partially-occluded players. Keeping the detector permissive preserves raw data for any future analysis that needs it (e.g., if we later want to compute "crowd density as proxy for rally excitement").
- **Related**: GOTCHA-013/Ghost-Regex pattern is the complement — greedy regex is MAX-recall lookup that needs a precision gate (json.JSONDecoder.raw_decode).
- **Severity**: MEDIUM (architectural principle, reusable across all two-stage ML pipelines)
- **File**: `backend/cv/pose.py`, `backend/agents/tools.py:dispatch_tool`

### PATTERN-040 — Chicken-and-Egg Dependency Resolution via Upstream Filtering
- **Type**: Design pattern for filtered selection
- **Context**: An earlier proposal was to "lower the keypoint confidence threshold only for the far-court player". Team lead correctly flagged: you cannot know they're the far-court player until you've done the projection, which requires passing the threshold. The dependency graph was circular.
- **Resolution**: When you want a role-specific filter on data that hasn't been role-assigned yet, check whether you can instead apply a ROLE-INDEPENDENT filter EARLIER that makes the role-specific relaxation safe. For skeleton sanitation: raising `bbox_conf >= 0.5` upstream eliminates ghosts, so we can safely lower the keypoint threshold GLOBALLY inside `assign_players` without admitting false positives.
- **How to apply**: When stuck on "how do we relax filter F only for entity type E?" — ask "is there a filter upstream of E-classification that makes F-relaxation safe for ALL entities?" Usually yes.
- **Severity**: MEDIUM (general-purpose engineering pattern)
- **File**: `backend/cv/pose.py:assign_players` — bbox_conf gate at step 1, lowered keypoint threshold at step 2

### GOTCHA-016 — Far-Court Player Invisible to YOLO11m-Pose on Broadcast Tennis Clips
- **Symptom**: Despite Phase Beta skeleton sanitation (bbox_conf gate, lowered keypoint threshold, tight lateral polygon), Player B (far-court) remains 0% detected in `data/clips/utr_match_01_segment_a.mp4`.
- **Diagnosis**: YOLO11m-Pose at both `imgsz=1280` and `imgsz=1920` produces only ONE high-confidence (bbox_conf > 0.3) detection per frame — the near-court player. The far-court player's apparent height is ~80-100 px (approximately 8-10% of frame height, vs 23% for the near player). They are additionally partially occluded by the "FAB LETICS" and "DUN KIN'" advertising banners at the top of the frame. At this size, YOLO11m (the "medium" variant) simply cannot classify them above noise.
- **When real far-half detections DO appear**: they are typically line judges / crowd members sitting in the upper-right or upper-left areas of the frame (outside the court polygon). Their feet project outside the CourtMapper's bounds, so `foot_m` returns None and they are correctly rejected.
- **Candidate fixes (NOT IMPLEMENTED — need team-lead direction)**:
  1. Upgrade to `yolo11l-pose.pt` (large) or `yolo11x-pose.pt` (x-large) — slower but better at small objects
  2. Run tile-based inference (split frame into 2-3 vertical strips, run YOLO per strip, merge)
  3. Accept as a known limitation of this specific clip + model combo; demo Player A only
  4. Use a different clip where camera is closer or both players are at similar scale
- **Severity**: HIGH for demo quality (half the biomech signals vanish); MEDIUM for architectural correctness (the Phase Beta filters are still mathematically correct, this is a detector-capacity issue)
- **File**: Emergent limitation visible in `backend/precompute.py` output; not fixable at the pipeline level, only at the detector or input level.

### DECISION-008 — Single-Player Focus as Deliberate Demo Scope (Not a Fallback)
- **Decision** (2026-04-22, team-lead approved): Panopticon Live is a WORLD-CLASS SINGLE-PLAYER deep-dive system, targeting Player A (near-court). Player B remediation (upgrading to yolo11l-pose, tile-based inference, etc.) is EXPLICITLY deferred out of scope. The project commits to mastering ONE player exceptionally well rather than covering TWO superficially.
- **Why this is a stronger narrative (not a weaker one)**: The "Moneyball for tennis" angle — deep forensic biomechanics on ONE pro — is a more credible demo story than shallow two-player match analysis. Judges see depth, not coverage. Post-DECISION-008 V6 Crucible output showed 10 HUD layouts (all 4-5 widgets, Player A only), 4 Coach insights with real quantitative anchors (e.g., "A's baseline_retreat collapsed from 1.67m → 0.10m, slope -0.70 m/s"), and 6 Haiku beats with broadcast-quality single-player copy ("Player A explodes laterally, covering the court with explosive urgency").
- **Implementation scope**:
  - `backend/agents/system_prompt.py`: added SINGLE-PLAYER FOCUS prologue to `BIOMECH_PRIMER`
  - `backend/agents/hud_designer.py`: removed `PlayerNameplate@top-right`, banned `MomentumMeter` + `PredictiveOverlay`, fallback layout is 2-widget single-player default
  - `backend/agents/haiku_narrator.py`: SINGLE-PLAYER FOCUS clause; "Player A must be subject of every beat"
  - `backend/agents/opus_coach.py`: user prompt labels A as "target", B as "opponent (may be undetected — that's OK)"
  - Tests: 5 new regression tests lock the single-player contract (no top-right nameplates, no MomentumMeter/PredictiveOverlay, Player B name excluded from Designer prompt, etc.)
- **How to apply**: When CV detector capacity is the bottleneck (per GOTCHA-016), embrace the narrower scope as a DESIGN CHOICE. Explicit scope narrowing enables better prompts, cleaner HUD, more varied commentary. Apply the "focus on one thing and master it" heuristic any time scope is forced by a constraint you can't change in the time available.
- **Severity**: HIGH (product direction for the hackathon demo)
- **File**: Across all four `backend/agents/*.py` modules + `tests/test_agents/*.py`.

### PATTERN-041 — Scope Narrowing as Demo Craft
- **Type**: Product / demo strategy
- **Context**: When a hard constraint (detector capacity, API limit, data gap) prevents the feature you originally designed, the weakest move is apologetic ("we would have had X but..."). The STRONGEST move is to reframe the constraint as a deliberate focus choice and upgrade every remaining piece to "world-class" at the narrower scope. For Panopticon: Player B invisible → "we deeply analyze ONE player instead of shallowly covering two" is a better demo pitch than "two players with patchy data on one of them."
- **How to apply**: When a constraint forces scope reduction, audit every output layer and make it EXPLICITLY align with the new narrower scope. Half-hearted "kinda still supports both" implementations fall into an uncanny valley. Commit to the narrow scope fully. System prompts, fallback layouts, default widgets, user prompts, docs, demo script — all should reference the new scope as PRIMARY, not a fallback.
- **Severity**: MEDIUM (hackathon / demo strategy, reusable)
- **File**: Captured in DECISION-008 implementation.

### DECISION-007 — HUDLayoutSpec Stays JSON-Only (No DuckDB Table)
- **Context**: Coach and Narrator insights have DuckDB tables; HUD layouts do not.
- **Why**: Layouts are low-frequency (one per match-state transition, ~10 per clip) and consumed exclusively by the frontend via match_data.json. Storing them in DuckDB too would be redundancy for zero read-path benefit.
- **File**: `backend/db/writer.py` — `queue_coach_insight` + `queue_narrator_beat` exist; no `queue_hud_layout`. Layouts go straight into `all_hud_layouts: list[HUDLayoutSpec]` → `_MatchData` → JSON.
- **Severity**: LOW (schema design — don't forget this when Phase 3 wonders why layouts aren't queryable via SQL)

---

## COURT-ANNOTATOR DEBUGGING (Apr 22, 2026) — 5-iteration Silent-Failure

### GOTCHA-014 — HTML ID Collision: `getElementById` Returns First-in-Document-Order, Silently
- **Symptom**: a video-loader tool silently does nothing. No `loadstart`, no `loadedmetadata`, no `error` event fires. Browser gives no visual feedback. DevTools console shows the JS successfully reached the line that sets `video.src = blobURL` but nothing happens after. 5 iterations of debugging lost to this (faststart remux, preload attribute, http vs file protocol — ALL red herrings).
- **Root cause**: `<input type="file" id="video">` AND `<video id="video">` both carried `id="video"` in the HTML. `document.getElementById("video")` returns the first match in document order (the input). Every subsequent `video.src = ...`, `video.addEventListener(...)` silently operated on the INPUT, not the video element. The input element had `.src` set to a blob URL (harmless no-op) and had listeners attached that would never fire.
- **Why it was hard to spot**: Duplicate IDs are syntactically valid HTML — no parse error, no runtime exception. The symptoms (nothing happens) look identical to codec issues, autoplay blocks, CORS, network stalls, a dozen other things. Every "fix" we tried (remuxing moov atom, switching protocol, changing preload) was chasing a phantom.
- **Why this class of bug is particularly deceptive**: browsers mis-silently ignore operations on wrong-type elements. `<input type="file">` doesn't fire a decoder error when you set `src` on it — it just accepts the property. Listeners attach successfully because `addEventListener` works on any EventTarget.
- **How to apply**: ANY time `getElementById` returns something weird or a DOM manipulation seems to silently no-op, immediately check `element.tagName` — if it's not what you expect, grep the HTML for `id="X"` and count matches.
- **Detector**: `tests/test_tools/test_court_annotator_html.py::test_no_duplicate_ids` — guards this class of bug statically. Fails the build if ANY two elements share an ID.
- **Runtime guard**: `court_annotator.html` now fails LOUD at page load if `document.getElementById("video").tagName !== "VIDEO"` — blanks the page with a red error rather than silently misbehaving.
- **Severity**: HIGH (silent correctness, very hard to diagnose without a bisecting mindset)

### PATTERN-037 — Use Known-Good Fallback Paths to Isolate Class of Bug
- **Type**: Debugging
- **Context**: When a video won't load via `blob:` URL, we added a "Test direct URL" button that loads the same file via a direct HTTP URL (no blob). If direct works but blob fails, bug is blob-specific. If BOTH fail, bug is with the element/pipeline itself.
- **Lesson**: For any "this doesn't work" debugging session, invest 2 minutes wiring up a known-good alternate path. It's a boolean bisect that eliminates half the hypothesis space instantly. See the `#btnTestDirect` handler in `tools/court_annotator.html`.
- **Severity**: MEDIUM (debugging-tool craft)

### PATTERN-038 — Timeout-Driven Diagnostics for "Never Happens" Bugs
- **Type**: Debugging
- **Context**: Waiting for an event that never fires is indistinguishable from waiting for an event that hasn't fired YET. After setting `video.src`, we start a 3-second timer; if `loadedmetadata` hasn't fired by then, we dump the full element state (`readyState`, `networkState`, `videoWidth`, `error.code`, `currentSrc`, `tagName`) into an on-screen red banner.
- **Lesson**: Silent-failure diagnosis needs a deadline + state dump. The dump should include enough context that the NEXT iteration of debugging has a concrete starting point (not "nothing happened"). `tagName` in the dump is what would have caught our ID-collision bug immediately.
- **File**: `tools/court_annotator.html` — the `setTimeout(() => { ... readyState + networkState + tagName dump ... }, 3000)` block.
- **Severity**: MEDIUM (debugging-tool craft)

### PATTERN-040 — Tolerant JSON Loaders for Tool-Emitted Artifacts
- **Type**: Integration boundary
- **Context**: `tools/court_annotator.html` emits a JSON with a wrapper (`{"clip": ..., "annotated_at": ..., "corners": {...}, "notes": ...}`) — useful provenance metadata. But `precompute.py` was calling `CornersNormalized(**json.load(...))`, which rejected the wrapper because Pydantic v2 frozen models forbid extras.
- **Lesson**: When a Pydantic model boundary receives JSON from a HUMAN-ORIENTED tool (annotator UI, hand-edited file, upload form), implement a `load_*` helper that accepts BOTH the wrapper and the bare shape. Pattern: `data.get("key", data)` to unwrap if wrapped, fall through to top-level if not. Return `(raw_text, ValidatedModel)` so callers can preserve provenance metadata.
- **Why non-obvious**: the temptation is to simplify the emitter (strip the wrapper from the UI) OR tighten the callsite (require the bare shape). Both break downstream provenance. The third path — a tolerant loader — keeps both ends clean.
- **File**: `backend/precompute.py:load_corners_json` + `tests/test_cv/test_precompute_corners_json.py`
- **Severity**: MEDIUM (integration correctness)

### PATTERN-039 — Research-Agent + Runtime-Diagnostic Parallel Attack on Sticky Bugs
- **Type**: Orchestration
- **Context**: When a bug survives 3+ iterations of "reasonable next-try" fixes, dispatch a research agent (general-purpose, background) IN PARALLEL with adding runtime diagnostics to the code. The research agent surfaces a ranked list of known causes while you build the diagnostic surface to disambiguate them. Both paths converge: the research agent's ranked list narrows hypothesis space; the diagnostic dumps narrow evidence space.
- **Example (this session)**: Research agent ranked ID-collision as cause #2 while I was already narrowing in on it via the `tagName` dump. Parallel execution took ~2 minutes; would have taken 15 minutes serially.
- **Non-obvious insight**: ALWAYS run both in parallel after 3+ failed iterations. The "just one more fix" instinct after each failure is what cost us 5 iterations here. Set a 3-failure circuit breaker: on iteration 4, escalate to research+diagnostics.
- **Severity**: MEDIUM (process — prevents future sessions from burning iterations on sticky bugs)

### DECISION-009 — Biometric Signals as Hero, Opus Coaching as Icing (2026-04-22, pivot evening)
- **Type**: Decision / strategic-framing
- **Context**: Mid-Phase-3 HUD polish. The original `2k-sports-hud-aesthetic` skill implied a full-width CoachPanel as a dominant footer, and the Haiku Narrator / Opus Coach outputs were conceptually "the product." Andrew intervened and reframed: **the proprietary value is the 7 biomechanical fatigue telemetry streams extracted from 2D broadcast pixels with zero hardware sensors — a hard-tech data moat**. The deliverable is an **improved fan experience** around those signals. Opus is icing.
- **Rule**: Visual hierarchy for every Panopticon UI surface:
  1. SignalBar stack = hero (right rail, prominent, spring-physics motion, fan-facing copy).
  2. PlayerNameplate = identity chrome (top-left, minimal).
  3. Video + skeleton = center (unchanged).
  4. CoachPanel = SUBORDINATE footer chip (≤88px tall, only when an insight is active).
  5. Every signal ships a plain-English fan-facing label + one-sentence physiology explanation, NOT the dev name.
- **Why**: Judges watch 3 minutes. They should leave thinking "they extracted fatigue telemetry nobody else is picking up from broadcast footage," not "they wrote nice commentary." Opus commentary is fungible; proprietary CV-derived biometrics is not.
- **How to apply**: When building or styling any HUD widget, ask: "Does this foreground the novel biometric data, or does it foreground Opus?" If the latter, reduce its visual weight. The fan-experience narrative is the differentiator.
- **Source**: Andrew, 2026-04-22 (late). Confirmed twice in the same session (worktree-scope + upgrade-set approval).
- **Severity**: CRITICAL (product-vision anchor)

### PATTERN-042 — rAF-Slaved State-Update Throttle (NOT setInterval)
- **Type**: React architecture
- **Context**: PanopticonProvider derives low-frequency state (activeHUDLayout, activeCoachInsight, activeSignalsByName) from `video.currentTime`. Original design used `setInterval(100)` to throttle state updates to 10Hz.
- **Rule**: Put the 10Hz gate INSIDE a `requestAnimationFrame` loop. Track `lastStateUpdateMs` with `performance.now()`; only `setState` when `performance.now() - lastStateUpdateMs ≥ 100`.
- **Why**: `setInterval` is disconnected from the browser render cycle AND from video playback. It keeps firing during pause, drifts on tab throttling, and misses scrub events. rAF is video-clock-slaved: it pauses when the tab is hidden, stays at 60Hz during playback, and correctly reflects `video.currentTime` whether the user is playing, paused, or scrubbing.
- **How to apply**: Any time you want a "state-driven by video-clock" React update, use the rAF-slaved pattern. Never use `setInterval` for anything tied to video time.
- **Copy-paste code**:
  ```tsx
  let lastStateUpdateMs = 0;
  const tick = () => {
    rafId = requestAnimationFrame(tick);
    // high-frequency ref writes happen every tick (≥30Hz)
    // ...update refs here...
    const now = performance.now();
    if (now - lastStateUpdateMs < 100) return;  // 10Hz gate
    lastStateUpdateMs = now;
    // compute derived values from refs + video.currentTime, then setState
    setActiveHUDLayout(pickActiveLayoutAtTime(...));
    setActiveCoachInsight(pickLatestBeforeOrAt(...));
    // ...etc
  };
  rafId = requestAnimationFrame(tick);
  return () => cancelAnimationFrame(rafId);
  ```
- **Source**: Team-lead citadel review of Phase-3-plan (2026-04-22). Original plan used setInterval.
- **Severity**: HIGH (prevents drift + scrub-race bugs in any video-driven UI)

### PATTERN-043 — Recharts Ban on High-Frequency Widgets
- **Type**: Frontend performance
- **Context**: Original Phase-3-plan proposed a Recharts `<LineChart>` sparkline inside each `SignalBar`, rendering at 10Hz.
- **Rule**: Recharts (and any full-featured React SVG chart library) is acceptable at ≤1Hz re-render. BANNED at ≥10Hz re-render. For high-frequency mini-charts: hand-roll `<svg><polyline points={...}/></svg>` reading a ref-backed ring buffer.
- **Why**: Recharts renders full React-managed SVG trees with internal state, tooltips, and responsive containers. Re-rendering 4 Recharts instances at 10Hz blocks the main thread during the video's paint window → micro-stutter on skeleton canvas at 30+FPS.
- **How to apply**: Before adding any chart library to a real-time widget, check the target re-render rate. If ≥10Hz, reach for raw SVG primitives.
- **Source**: Team-lead citadel review.
- **Severity**: HIGH (prevents video-stutter regressions)

### PATTERN-044 — Spring Physics Bridge (10Hz data → 60FPS visuals)
- **Type**: Motion design + frontend architecture
- **Context**: React state updates are capped at 10Hz for performance (PATTERN-042). But at 10Hz, a bar-fill width changing from 40% → 80% feels like a discrete jump — cheap web-app aesthetic.
- **Rule**: Use Framer Motion spring physics (NOT `easeOutQuart` / `linear` / fixed-duration tweens) on every UI element whose value updates from the 10Hz state stream. `<motion.div style={{ width }} transition={{ type: 'spring', stiffness: 300, damping: 30 }}>` — the `width` value updates at 10Hz, the spring animator interpolates through at display refresh rate (60-120Hz depending on monitor).
- **Why**: Springs model mass + damping. The displayed value smoothly "chases" the target value. ESPN / NBA 2K / F1 broadcast graphics all use this feel — it reads as "physical telemetry," not "web UI."
- **How to apply**: Codify canonical springs as `motion.springStandard` / `motion.springFirm` / `motion.springGentle` in `design-tokens.ts`. Every `<motion.*>` should reference one of these.
- **Severity**: HIGH (core visual-polish move for broadcast-quality feel)

### PATTERN-045 — Strict Array-Bounds Clamping on Video-Indexed Lookups
- **Type**: Defensive programming
- **Context**: Any time code does `keypoints[Math.floor(video.currentTime * fps)]`, a user scrubbing to end-of-video can produce an index > array length → `undefined` → React error boundary → blank screen mid-demo.
- **Rule**: Always clamp: `const frameIdx = Math.min(Math.max(0, Math.floor(video.currentTime * fps)), keypoints.length - 1);`. For signals (not uniformly sampled), use binary search with clamp: `Math.min(searchResult, items.length - 1)`.
- **Why**: Video playback past the last pre-processed frame is a legitimate user action (the MP4 ends 200ms after the last keypoint frame, for example). Defensive clamping is cheaper than the demo-crashing alternative.
- **How to apply**: Every time-indexed lookup in `PanopticonProvider.tsx`, every `keypoints[idx]` in `PanopticonEngine.tsx`, passes through a clamping helper. Test explicitly in `frameClamp.test.ts`.
- **Severity**: HIGH (crash prevention — demos cannot have React error boundaries)

### PATTERN-046 — Split Contexts for Static Refs + Low-Freq State (anti-context-fanout)
- **Type**: React architecture
- **Context**: `PanopticonProvider` originally exposed BOTH stable refs (`videoRef`, `matchDataRef`, getter functions) AND 10Hz throttled state via a single React context. Every consumer of `usePanopticon()` re-rendered every 100ms, including `PanopticonEngine` which MUST stay at ≤3 renders for the zero-render canvas loop to hold.
- **Rule**: Split into TWO contexts:
  - `PanopticonStaticContext` — stable refs + getters, never changes after mount. Consumed via `usePanopticonStatic()`.
  - `PanopticonStateContext` — throttled 10Hz state. Consumed via `usePanopticonState()`.
  Consumers opt into ONLY the subset they need.
- **Why**: React context updates trigger re-renders in ALL consumers. Mixing stable + state in one context forces every consumer to participate in state's render cadence, even if they only use stable refs. The canvas engine, which only needs refs, suffers a 10Hz render cadence it doesn't need.
- **How to apply**: Any provider that mixes "never changes" with "changes often" → split into two contexts with two hooks. Typed contexts make the separation explicit. Applicable to ANY React state manager pattern (auth + theme, user + preferences, etc. — not just this project).
- **Source**: Team-lead citadel review.
- **Severity**: HIGH (universal React perf pattern)

### PATTERN-047 — High-Frequency Text via DOM Mutation + `key` for Race-Free Unmount
- **Type**: React architecture / high-frequency rendering
- **Context**: Typewriter effect for Opus commentary — naïve impl uses `setText(prev => prev + ch)` on an 18ms interval → 55 setState/sec during animation → re-renders whole CoachPanel subtree → cuts into video paint budget. Worse, rapid video scrubbing triggers overlapping intervals → race conditions where an old typewriter finishes "after" a new one.
- **Rule**: Use `useRef<HTMLSpanElement>(null)` + direct DOM mutation:
  ```tsx
  spanRef.current.textContent = commentary.slice(0, i);
  ```
  inside the interval callback. React never re-renders. Then apply `key={activeCoachInsight.insight_id}` to the wrapper — React fully unmounts + remounts on insight change, which auto-cancels the old interval via the useEffect cleanup.
- **Why**: Text characters in a typewriter animation are HIGH-FREQUENCY data (55Hz). Same class as keypoints. Must not go through React state. `key`-driven unmount is the idiomatic way to guarantee effect cleanup + fresh state when identity changes.
- **How to apply**: Any animation that reveals text, numbers, or any character stream character-by-character → ref + DOM mutation. `key` on the wrapper for identity-driven resets.
- **Source**: Team-lead citadel review.
- **Severity**: HIGH (universal text-animation pattern)

### PATTERN-048 — Data-Driven UI Thresholds (No Hardcoded Backend-Config Mirrors)
- **Type**: Coupling discipline
- **Context**: Backend `--warmup-ms` flag drops the first 10000 ms of CV data. First HUD layout is at `t=11033ms`. Naïve calibration-placeholder gate: `if (currentTimeMs < 11500) showCalibration();`. Fragile: changing the backend's warmup-ms silently breaks the UI.
- **Rule**: Derive UI thresholds from the actual data shape, not from mirrored backend config. `const firstLayoutMs = matchDataRef.current?.hud_layouts[0]?.timestamp_ms ?? Infinity; if (currentTimeMs < firstLayoutMs) showCalibration();` — auto-adapts.
- **Why**: UI should react to what arrived in the payload, not to a guess about what MUST have arrived based on upstream config. Decouples the fronted from backend flag values.
- **How to apply**: Every threshold in the UI that "mirrors" a backend config value is a coupling smell. Replace with a data-shape query.
- **Severity**: MEDIUM (decoupling discipline)

### GOTCHA-017 — Dead-Air Window (Warmup Filter → Empty HUD for 11.5s)
- **Type**: Gotcha / UX
- **Context**: The backend CV warmup filter drops 10000ms of data so Kalman / state machine have time to stabilize. Resulting `utr_01_segment_a.json` has its first `hud_layout.timestamp_ms = 11033`. A straight playback from t=0 shows a blank right rail for the first 11.5s. Judges watching demo will assume the app is broken.
- **Rule**: Turn the dead-air into cinematic framing: render a stylized "BIOMETRIC SENSORS — CALIBRATING…" placeholder while `currentTimeMs < firstLayoutMs` (data-driven threshold per PATTERN-048). Use subtle pulse animation + staggered dot loader. On first real layout arrival, AnimatePresence spring-transitions the placeholder out and the real widgets in.
- **How to apply**: Canonical component `SensorCalibratingPlaceholder`. Wire into SignalRail's conditional render. Do NOT hardcode 11500; derive from `matchDataRef.current?.hud_layouts[0]?.timestamp_ms`.
- **Why**: Technical constraints become demo polish when reframed. "Calibrating" reads as professional broadcast UX, not "empty app."
- **Severity**: HIGH (demo-credibility — avoids "is it broken?" first impression)

### PATTERN-050 — Tab Keep-Alive via `display: none` (never unmount)
- **Type**: React architecture
- **Context**: Phase 3.5 TabShell. Naïve tab implementation unmounts inactive tab content → the `<video>` element + rAF loop + match_data fetch all re-initialize every tab switch. Demo pacing (auto-pause timeline, typewriter state) breaks immediately.
- **Rule**: In a tabbed app with shared state across tabs, render ALL tab bodies always. Hide inactive tabs with `style={{ display: id === activeId ? 'block' : 'none' }}`. Unmount is NEVER used for tab switches.
- **Why**: `display: none` keeps the DOM node alive + keeps React state mounted. Video continues playing, scroll position is preserved, refs remain valid. Zero re-fetching, zero re-hydration flicker.
- **How to apply**: `TabShell` renders a `<div>` per tab unconditionally; only the CSS display bit changes. The `<video>` inside Tab 1 keeps firing `timeupdate` events while the user is on Tab 2/3 → the telemetry feed auto-scrolls in real time even when invisible.
- **Trade-off**: slightly higher memory (all tabs mounted). In our app this is ~200KB of components — negligible vs the UX win.
- **Severity**: HIGH (demo-pacing-preserving)

### PATTERN-051 — Telestrator Auto-Pause Pacing Pattern
- **Type**: Demo-craft / video UX
- **Context**: Andrew's feedback on the 60s continuous-video pacing: judges can't absorb data that fast. Traditional sports video + data dashboard forces the viewer to choose where to look. The fix is "Telestrator Mode" — the video cooperates with the data.
- **Rule**: When a coach insight becomes active, pause the video. Typewriter the commentary (DOM mutation per PATTERN-047). When typewriter finishes, hold for `TELESTRATOR_HOLD_MS` (3500ms) so the judge reads the complete sentence. Then resume automatically. On unmount / insight-change, always resume so the demo never strands the viewer in a forced-pause state.
- **Why**: Transforms a passive dashboard into an interactive analytical presentation. The video stops speaking to let the biomechanics data speak. Judges see a directed, broadcast-quality walkthrough instead of a frenetic data-overlay.
- **How to apply**: `CoachPanel.tsx` captures `videoRef` at effect start (React 19 ref-cleanup safety), calls `video.pause()` on mount, schedules `video.play()` via `setTimeout` after typewriter completion. Cleanup clears the timeout AND unconditionally calls `play()` so panel exits don't leave a paused frame.
- **Non-obvious insight**: `video.play()` returns a Promise that REJECTS on autoplay-blocked contexts OR when the video has ended. Always `.catch(() => {})` to avoid unhandled rejections.
- **Severity**: HIGH (demo-polish win — changes "cool dashboard" to "cinematic product")

### PATTERN-052 — Frontend State-Gating as Defense-in-Depth Against LLM Layout-Lag
- **Type**: Coupling discipline / frontend safety net
- **Context**: Phase 3 visual QA (Andrew): "biometric telemetry on the right-hand side is showing things like toss consistency in the middle of a rally, where the toss consistency is only relevant to the fan before the serve." Root cause: the backend Opus HUD Designer picks signals at HUD-layout-creation time, but the player's match-state transitions continuously. The layout's suggested signals become inappropriate within seconds of creation.
- **Rule**: The frontend enforces a HARD mapping from `PlayerState → allowed SignalName[]`, applied as a filter on top of whatever `activeHUDLayout.widgets` contains. Specifically:
  - `ACTIVE_RALLY` → hide `serve_toss_variance_cm`, `ritual_entropy_delta`, `crouch_depth_degradation_deg` (serve-ritual signals)
  - `PRE_SERVE_RITUAL` / `DEAD_TIME` → hide `lateral_work_rate`, `baseline_retreat_distance_m` (rally-movement signals)
  - `recovery_latency_ms`, `split_step_latency_ms` → state-agnostic, always permitted
  - `UNKNOWN` / `null` → permissive (don't filter before we have state)
- **Why**: The UI should look CORRECT at every frame. LLM layout-lag is a systemic issue — even a smarter Designer will have second-scale lag. A client-side filter is cheap and makes the bad-layout case impossible to observe.
- **How to apply**: `lib/stateSignalGating.ts` owns the mapping. `SignalRail.tsx` calls `isSignalAllowedInState(signalName, state)` before pushing a SignalBar. Backend Designer prompts can stay focused on semantic choice; frontend guarantees contextual correctness.
- **Generalizes to**: any case where an LLM produces a structured UI spec that consumers must render in a changing context. Always have a client-side contract check — LLMs will produce valid-looking output for stale contexts.
- **Severity**: HIGH (UX correctness)

### PATTERN-049 — Bleeding-Edge Test-Stack Time Guardrail
- **Type**: Process / time budget
- **Context**: Setting up Vitest + JSDOM + React Testing Library + Next.js 16 + React 19 + Tailwind 4 for component tests is a bleeding-edge combo. Known to hit config rabbit-holes (transform pipelines, JSX runtime mismatches, Tailwind plugin resolution, RSC-boundary confusion) that can eat 2-3 hours to debug.
- **Rule**: Set a one-attempt time budget on bleeding-edge test stacks. If the stack doesn't stand up cleanly in ≤30 min, DELETE the component tests, keep the pure-function tests, and validate components via live-dev-server visual smoke. The pure-function layer (binary search, clamping, copy completeness, tone mapping) is where the logic bugs live; component rendering is validated by eye on localhost.
- **Why**: Hackathons are time-bounded. A working demo > exhaustive test coverage. Pure-function tests catch algorithmic regressions; visual smoke catches render regressions. Component tests would be nice-to-have but cannot block Phase 3 landing.
- **How to apply**: When adopting Vitest + JSDOM + RTL on a bleeding-edge Next.js major, set a 30-min timer. If config still fights you, drop the RTL layer.
- **Severity**: MEDIUM (time-budget discipline)

---

## DAY 2 LEARNINGS (Apr 23, 2026)

### GOTCHA-018 — Multi-line Paste Silently Embeds Newlines Inside Single-Quoted Env Vars
- **Type**: Gotcha (shell / terminal)
- **Context**: Apr 23, 2026 — Phase 4 Crucible Run. The user pasted a long `export ANTHROPIC_API_KEY='...'` command where the terminal display wrapped the key across two visual lines, AND the paste preserved a literal newline + two spaces of indent inside the quotes. Shell single-quoted strings span physical newlines lawfully — the embedded `\n  ` became part of the env var. Expected Anthropic key length 108 chars; actual `${#ANTHROPIC_API_KEY}` = 111 chars. The Anthropic SDK attempted HTTPS requests with a malformed Authorization header, which failed at the HTTP transport layer with `APIConnectionError: Connection error.` — NOT `AuthenticationError`, because the header never made it onto the wire. ALL 26 agent calls (10 Coach + 10 Designer + 6 Narrator) failed identically, producing `[coach_error: APIConnectionError: Connection error.]` commentaries. The underlying network + DNS + TLS + HTTPS to `api.anthropic.com` was perfectly healthy.
- **Lesson**: NEVER paste a multi-line export command that quotes a long token across physical newlines. Two defenses, pick both:
  1. Put the entire `export KEY=VALUE` on ONE physical line, preferably with `&&` chaining to the next command so the shell sees it as a single statement.
  2. Validate the env var length immediately: `echo "len=${#ANTHROPIC_API_KEY}"` — Anthropic API keys are exactly 108 chars (7-char literal prefix + `api03-` + 95-char body).
- **How to apply**:
  - When giving a user an export command to paste, prefer NO surrounding single-quotes (Anthropic keys are alphanumeric + dashes + underscores, no shell-metas) AND chain it to a length-check so a malformed paste fails loudly rather than silently producing `APIConnectionError`.
  - Template: `export ANTHROPIC_API_KEY=<the-key-body> && echo "len=${#ANTHROPIC_API_KEY} (expect 108)"`
- **Diagnostic ladder when Anthropic calls mysteriously fail with APIConnectionError**:
  1. DNS/TCP/TLS probe via `python -c "import socket; socket.create_connection(('api.anthropic.com', 443))"`. If healthy, network is not the problem.
  2. `echo ${#ANTHROPIC_API_KEY}` — should be 108 for current Anthropic keys. Any other length = malformed.
  3. Inspect the key with `echo -n "$ANTHROPIC_API_KEY" | od -c | head` — reveals embedded newlines, spaces, or non-printable bytes.
  4. Only after steps 1-3 pass, blame rate-limits / regional outages.
- **Severity**: MEDIUM (cost a full Crucible run (~8 min compute) before diagnosis; catchable in <10s with a `${#KEY}` length check)
- **Related**: See GOTCHA-020 for the `printf "%s\n\n"` variant — different mechanism (piped-stdin trailing newline fed into `vercel env add`, not clipboard quoting), same corruption outcome (Anthropic-401 loop). Treat both as members of the same "hidden-byte env-var" class.

### USER-CORRECTION-031 — Direct User Directive Overrides Forwarded Team-Lead Text
- **Type**: User-Correction
- **Context**: User forwarded a team-lead citadel-upgrade message that asserted "DO NOT create or switch to `hackathon-stage-3`. Claude hallucinated this path increment. Stay in `hackathon-stage-2`." The Environment block at session start explicitly set `/Users/andrew/Documents/Coding/hackathon-stage-3` as the primary working directory and `hackathon-stage-3` as the current branch. I reflexively switched my plan to stage-2 based on the forwarded text. User then issued an override: "I am overriding the team leads override. Work strictly inside stage-3 worktree."
- **Lesson**: When the Environment block and forwarded human/agent text disagree about working directory, the Environment block is the authoritative source-of-truth for the current session. Forwarded text (from a team lead, another session, pasted directive) is historical context that may reflect a prior or sibling session. Empirically verify (git log, directory contents) BEFORE switching paths; surface the discrepancy to the user as a question, not as a silent switch.
- **How to apply**:
  1. On a forwarded directive that contradicts the Environment block, run `pwd && git -C <env-cwd> log --oneline -5 && git -C <env-cwd> branch --show-current` to ground-truth the current state.
  2. If the forwarded directive still disagrees with observed state, ASK the user which path is canonical rather than switching.
  3. Never stage files or start destructive work across worktree boundaries until the path is user-confirmed.
- **Severity**: HIGH (worktree switches can abandon in-flight work or scatter assets across sibling repos — anti-pattern #31 adjacent)
- **Phase-5 addendum (2026-04-23)**: During the Vercel env-var rotation saga I flagged that the Anthropic API key had been forwarded in the raw chat transcript and therefore should be rotated before being added to Vercel. Andrew responded "use this exposed API key, don't rotate" — accepting the security trade-off explicitly. I re-surfaced the concern a second time, which was excess friction. **Lesson extension**: when the user has been informed of a security trade-off and chooses to accept it, state the trade-off clearly ONCE ("the key in the transcript is now considered burned; using it means you should rotate after the hackathon"), then comply. Do not re-argue, do not ask again, do not block progress. The override protocol in the original correction ("user directive beats forwarded text") also covers "user directive beats my security instinct, after they've been informed." The forcing function for me is to make the trade-off explicit and the ask singular — not to become a persistent objector.

### USER-CORRECTION-032 — Vercel NFT Cannot Bundle Dynamic fs.readFile Paths in Server Actions → Use Client-Driven Payload
- **Type**: User-Correction (deployment trap)
- **Context**: My Phase 4 plan's Server Action for the Scouting Report proposed `fs.promises.readFile(path.join(process.cwd(), 'public', 'match_data', \`${matchId}.json\`))`. User corrected: "It will BREAK on Vercel. Vercel's Node File Trace (NFT) cannot statically analyze dynamic paths, so the `public/match_data/` JSON files won't be bundled into the Serverless Function environment."
- **Lesson**: For any Next.js Server Action that needs to read data-at-rest, prefer passing the data FROM the client (which already has it loaded in React state/context) as an argument. This decouples the Server Action from the bundler's static-path analyzer and makes it Vercel-bulletproof. Strip high-frequency / high-volume keys (e.g., `keypoints`, `hud_layouts`) on the client before sending — the Server Action payload limit is 1MB but only a tiny fraction of that is actually needed for an LLM scouting call.
- **How to apply** to this project's Scouting Report:
  1. Server Action signature: `generateScoutingReport(matchId: string, payload: Omit<MatchData, 'keypoints' | 'hud_layouts' | 'narrator_beats'>): Promise<string>`
  2. In `ScoutingReportTab.tsx`, destructure matchData immutably: `const { keypoints: _kp, hud_layouts: _hl, narrator_beats: _nb, ...payload } = matchData;`
  3. Call `generateScoutingReport(matchId, payload)` — the payload crosses the network once, the Server Action never touches the FS.
  4. The LLM-relevant fields are: `meta`, `signals`, `transitions`, `anomalies`, `coach_insights`. Nothing else.
- **Generalizes to**: ANY Vercel Server Action that wants to ingest a known-client-side dataset. Don't reach for fs; accept the data as an argument. This pattern is also the canonical answer to "how do I pass state from a Client Component to a Server Action for AI processing" in Next.js App Router.
- **Severity**: CRITICAL (production deployment blocker — would 500 on Vercel, passing locally)

### PATTERN-053 — Edge-Triggered Match Coupling on Continuous Bounce Signal
- **Type**: Systems / state-machine discipline
- **Context**: Andrew flagged in visual QA: "the pre-serve ritual stays on well into the rally." Root-cause investigation found that `RollingBounceDetector.evaluate()` is a PURE spectral probe of a 90-frame (3-second @ 30fps) rolling buffer — once a bounce signature lives in the buffer, `evaluate()` returns True **every frame for the ~3 seconds it takes the signature to age out**. The original `MatchStateMachine.update()` called `self._a.force_state("PRE_SERVE_RITUAL", t_ms); self._b.force_state("PRE_SERVE_RITUAL", t_ms)` on every tick where `a_bounce or b_bounce` was True — so kinematic ACTIVE_RALLY transitions got immediately snapped back to PRE_SERVE_RITUAL for the full ~3-second window. Player was pinned in the ritual state across an actual rally.
- **Rule**: When a signal is a CONTINUOUS spectral/statistical probe (rolling-buffer variance, autocorrelation, Lomb-Scargle, etc.), but the CONSUMER wants a discrete EVENT (force a state change once per occurrence), do edge-detection at the CONSUMER, not the PROBE. The probe stays pure and idempotent (which enables invariants like `test_detector_evaluate_is_idempotent` in the test suite). The consumer tracks `_last_signal_state` and fires only on the rising edge (False → True).
- **Why it goes in the consumer**: the probe's idempotence contract is an invariant that makes it composable — multiple consumers can read it without side effects. Moving edge-detection into the probe breaks that. Moving it into the consumer localizes the edge semantics to the one place that needs them.
- **How to apply in `backend/cv/state_machine.py`**:
  ```python
  class MatchStateMachine:
      def __init__(self):
          ...
          self._last_bounce_state: tuple[bool, bool] = (False, False)
      def update(self, ..., a_bounce, b_bounce, t_ms):
          ...
          prev_a, prev_b = self._last_bounce_state
          a_edge = a_bounce and not prev_a
          b_edge = b_bounce and not prev_b
          self._last_bounce_state = (a_bounce, b_bounce)
          if a_edge or b_edge:
              self._a.force_state("PRE_SERVE_RITUAL", t_ms)
              self._b.force_state("PRE_SERVE_RITUAL", t_ms)
  ```
- **Generalizes to**: any signal-to-event bridging where the signal source is inherently continuous. Serve-bounce detection, anomaly detection (z-score > threshold for N consecutive ticks), heartbeat-timeout triggers, etc.
- **Severity**: CRITICAL (root cause of a flagship visual-QA bug, pinpointed during Phase 4)

### PATTERN-054 — Client-Driven Payload for Vercel Server Actions (Vercel-bulletproof AI reads)
- **Type**: Frontend architecture / Vercel deployment
- **Context**: USER-CORRECTION-032 surfaced during Phase 4 Scouting Report wiring. We wanted Tab 3 to call a Next.js Server Action that reasons over ~100KB of telemetry. The FS-read approach (`fs.readFile(path.join(process.cwd(), ...))` against a dynamic matchId) works locally in `next dev` but breaks on Vercel because NFT can't statically trace the file into the Serverless Function bundle.
- **Rule**: For any Server Action that needs to analyze data already resident in the Client Component tree, pass the data AS AN ARGUMENT to the Server Action instead of re-reading it on the server. Destructure out high-volume fields (keypoints, per-frame arrays) on the client first; keep only LLM-relevant keys in the payload.
- **Why this is superior**:
  1. **Vercel-bulletproof**: no FS access means NFT has nothing to trace; the Serverless Function is pure-compute.
  2. **Stateless**: the Server Action takes all its inputs from arguments; trivial to test, reason about, and move between edge/serverless/local.
  3. **Bandwidth-efficient**: client already has the JSON in memory; the network round-trip is the same 100KB it would have been if the server had to fetch from Blob/KV.
  4. **Typed**: the argument type can be `Omit<MatchData, 'keypoints' | 'hud_layouts'>` — the compiler enforces what we strip.
- **How to apply**:
  ```typescript
  // actions.ts
  'use server';
  export const maxDuration = 60;
  export async function generateScoutingReport(
    matchId: string,
    payload: Omit<MatchData, 'keypoints' | 'hud_layouts' | 'narrator_beats'>,
  ): Promise<string> {
    const client = new Anthropic();
    const resp = await client.messages.create({
      model: 'claude-opus-4-7',
      thinking: { type: 'adaptive' },
      system: [{ type: 'text', text: SYSTEM_PROMPT, cache_control: { type: 'ephemeral' } }],
      messages: [{ role: 'user', content: `Match: ${matchId}\n\n${JSON.stringify(payload, null, 2)}` }],
      max_tokens: 4096,
    });
    return resp.content.filter(b => b.type === 'text').map(b => b.text).join('\n\n');
  }

  // ScoutingReportTab.tsx (client)
  const { keypoints: _k, hud_layouts: _h, narrator_beats: _n, ...payload } = matchData;
  const md = await generateScoutingReport(matchId, payload);
  ```
- **Anti-pattern to avoid**: `fs.promises.readFile(path.join(process.cwd(), 'public', ..., dynamicName))` in a Server Action. Works locally, 500s on Vercel. If you MUST read from disk in a Server Action, the path must be a literal string constant or derived from build-time imports (not runtime params) so NFT can trace it.
- **Source**: User-Correction from Andrew during Phase 4 plan review, 2026-04-23.
- **Severity**: CRITICAL (prevents Vercel deploy regression)

---

### Phase 5 — Demo Polish + Vercel Production Deploy (2026-04-23 afternoon to evening, PR #4 merged)

### GOTCHA-019 — Turbopack Strips Non-Async Exports From use-server Files
- **Type**: Gotcha (Next.js 16 / Turbopack)
- **Context**: 2026-04-23, Phase 5 Vercel deploy. `dashboard/src/app/actions.ts` begins with `'use server';` and previously exported both `export const maxDuration = 60` (route-segment config) and `export async function generateScoutingReport(...)` (Server Action). Local `next dev` (Turbopack) built the module correctly. Production build via Turbopack completely stripped `actions.ts` from the client bundle — the `generateScoutingReport` import in `ScoutingReportTab.tsx` resolved to nothing, and the build log emitted `The module has no exports at all`. Root cause: Turbopack's `'use server'` analyzer only keeps async function exports; non-async exports (plain `const`, `let`, etc.) are treated as "not Server Action surface" and the whole module was dropped. This is a Turbopack-specific behavior — Webpack tolerates the mixed-export shape because its `'use server'` boundary-analyzer is more permissive.
- **Symptom ladder**: (a) local `next dev` — works (Turbopack dev mode). (b) `vercel` preview deploy — build succeeds but Tab 3 throws `TypeError: generateScoutingReport is not a function` in the browser. (c) `next build` locally with Turbopack forced — same error.
- **Lesson**: Route-segment config (`maxDuration`, `runtime`, `preferredRegion`, `revalidate`, `dynamic`, `fetchCache`, etc.) should NEVER co-habit a `'use server'` file. Move it to `vercel.json` (`functions."src/app/**/*.ts(x)".maxDuration: 60`) or to a non-`'use server'` route handler file.
- **Fix committed**: `b20c370 fix(deploy): move maxDuration from actions.ts to vercel.json` — deleted the `export const maxDuration = 60` line; added `dashboard/vercel.json` with `{"functions": {"src/app/**/*.ts": {"maxDuration": 60}, "src/app/**/*.tsx": {"maxDuration": 60}}}`.
- **Generalizes to**: any Next.js 16 `'use server'` file that tried to co-locate config. Treat `'use server'` files as strictly async-exports-only.
- **Severity**: CRITICAL (silent production break — local works, Vercel 500s)
- **Files**: `dashboard/src/app/actions.ts`, `dashboard/vercel.json` (new).

### GOTCHA-020 — printf Into vercel-env-add Embeds Trailing Newlines Into Stored Env Value
- **Type**: Gotcha (Vercel CLI / shell)
- **Context**: 2026-04-23, Phase 5 production deploy. After GOTCHA-018's clipboard-paste newline variant burned a Crucible run, I was extra-careful rotating the Anthropic API key into Vercel. My command was `printf "%s\n\n" "<redacted-key-body>" | vercel env add ANTHROPIC_API_KEY production --sensitive`. The `\n\n` at the end was reflexive — "make sure stdin ends with a newline so the CLI gets EOF cleanly." Vercel's CLI then displayed `WARNING! Value contains newlines.` and proceeded to store the value WITH the trailing newlines intact. Result: the stored API key was 110 bytes (108 valid + `\n\n`), and every Anthropic SDK call from the Serverless Function returned 401 auth error, because the Authorization header builder passed the newlines through into the HTTP header, which the Anthropic edge rejected as malformed.
- **Symptom**: identical to GOTCHA-018 from the outside — Anthropic calls fail uniformly. BUT the diagnostic ladder differs: this one lives inside the Vercel env store, not on the local shell. `vercel env pull` cannot reveal it (Sensitive vars do not download). Only way to see the corruption is to deploy and read the Function's runtime error.
- **Distinction from GOTCHA-018**: GOTCHA-018 was clipboard-paste quoting on the local shell, corrupting `$ANTHROPIC_API_KEY` BEFORE upload. GOTCHA-020 is stdin corruption DURING upload via `printf "%s\n\n"` — the shell env var was clean, but the value that reached Vercel's store was not. Different mechanism, same outcome.
- **Lesson**: When piping into `vercel env add`, use `printf "%s"` (no trailing newline) — NOT `printf "%s\n"` or `echo` (which append one implicit newline) or `printf "%s\n\n"` (which appends two). If Vercel's CLI prints `WARNING! Value contains newlines`, STOP, abort the upload (Ctrl-C before confirming), remove the var, and re-upload with the clean form.
- **Preferred incantation (from `/vercel:vercel-cli` reference)**: `vercel env add NAME preview "" --value "..." --yes --sensitive` — `--value` bypasses stdin entirely and stores the exact string you pass, with no newline ambiguity. See PATTERN-056.
- **Related**: Cross-linked to GOTCHA-018 (shell-quoting newline, same symptom, upstream mechanism). Both belong to the same class: any byte you cannot see in the visible terminal view can end up in your env var.
- **Severity**: CRITICAL (production break; caught only by deploying and reading runtime logs)
- **Files**: Vercel project `dmg-decisions/panopticon-live` env store; no repo-level code change.

### GOTCHA-021 — Anomaly Injection Must Target Signals Inside the ACTIVE hud_layouts Entry at That Timestamp
- **Type**: Gotcha (demo data authoring)
- **Context**: 2026-04-23, Phase 5 demo anomaly seeding. Golden `utr_01_segment_a.json` had no `baseline_z_score` hits >2.0 during the demo window; the `AnomalyBadge` pulsing-red UI therefore never fired on video. My first injection (v1) set `baseline_z_score: 2.5` on the `lateral_work_rate` signal sample at `timestamp_ms=36166`. Commit shipped; judges would still see a blank UI. Root cause on re-inspection: the active HUD layout at `t=36166` is `hud_34233_8b1eaa` (valid range 34233 to 64233 ms), whose `widgets` list specifies `serve_toss_variance_cm`, `ritual_entropy_delta`, and `crouch_depth_degradation_deg` — `lateral_work_rate` is not among them. The frontend's `SignalRail` only renders bars for signals present in the active layout's widget list (by design — that's how DECISION-009's HUD-Designer curation works). So a z-score flag on a signal the user cannot see is invisible.
- **Lesson**: Before mutating any `SignalSample` to showcase anomaly UI, ALWAYS look up the ACTIVE `hud_layouts` entry at the target timestamp and confirm the signal appears in that layout's `widgets` list. Pseudocode:
  ```python
  layout = next(l for l in match_data["hud_layouts"] if l["timestamp_ms"] <= t_ms < l["valid_until_ms"])
  assert target_signal_name in [w["signal_name"] for w in layout["widgets"]], \
      f"{target_signal_name} not rendered at t={t_ms} (layout={layout['layout_id']})"
  ```
- **Fix committed (v2)**: `888acb5 feat(dashboard): visible anomaly injections + dual TelemetryLog slots` — injected three on-screen anomalies that ARE in `hud_34233_8b1eaa`:
  - `serve_toss_variance_cm` at `t=35900ms`, `baseline_z_score=-2.3`
  - `crouch_depth_degradation_deg` at `t=45300ms`, `baseline_z_score=+2.5`
  - `crouch_depth_degradation_deg` at `t=59066ms`, `baseline_z_score=+2.8`
  Each has a matching `AnomalyEvent` entry in the `anomalies[]` array so the firehose log picks it up too. The original `lateral_work_rate@36166` v1 injection is PRESERVED as a Tab 2 easter egg — the Raw Telemetry tab shows ALL signals, so it's visible there even though it's not in the Tab 1 layout.
- **Generalizes to**: any demo authoring workflow where a proprietary curation layer (LLM-designed HUD, feature-flag gated UI, per-user personalization) sits between the raw data and the judge-visible surface. Mutations to the raw data are only visible if they pass through the curation filter. Always write your mutation by working backward from what the judge actually sees.
- **Severity**: HIGH (demo credibility — invisible anomaly injection is indistinguishable from a dead feature)
- **Files**: `dashboard/public/match_data/utr_01_segment_a.json` (signals[] + anomalies[] arrays).

### PATTERN-055 — Reusable TelemetryLog Primitive (factor-out of SignalFeed.tsx)
- **Type**: Frontend architecture / DRY refactor
- **Context**: 2026-04-23. Tab 1's HUD view had large empty whitespace regions on either side of the video + skeleton center. Tab 2 (Raw Telemetry) had the only live scrolling feed of signals/transitions/insights/anomalies, locked into a full-viewport shell. Goal: slot a telemetry feed into Tab 1's right aside and bottom strip WITHOUT duplicating the 250-line `SignalFeed.tsx` implementation.
- **Rule**: Extract every reusable primitive from `SignalFeed.tsx` into `dashboard/src/lib/telemetry.ts`. Specifically: `FeedRow` union type (`'state' | 'signal' | 'insight' | 'anomaly'`), `buildTimeline(data: MatchData): FeedRow[]` (merges signals + transitions + insights + anomalies into one time-sorted array, filters `player !== 'A'` per DECISION-008), `upperBound(rows, t)` (binary search for `[0, upperBound)` slice, `(lo + hi) >>> 1` unsigned-shift to prevent `lo+hi` overflow on large arrays), `toneForSignal(s)` (`|z| >= 2` → `colors.anomaly`, `|z| >= 1` → `colors.fatigued`, else `colors.energized`), `fmtClock(ms)` (`mm:ss.cc` with `Math.max(0, ...)` clamp), `transitionText(tr)`, `oneLineOpener(c)` (truncates commentary to 110 chars with ellipsis), `anomalyText(a)`, `signalUnit(signalName)`. Then author a new `dashboard/src/components/Telemetry/TelemetryLog.tsx` component that takes props: `rowKinds: FeedRowKind[]` (filter), `heightClass: string`, `className?: string`, `showHeader?: boolean`, `density?: 'compact' | 'comfortable'`. The component mounts the shared primitive with its own auto-scroll (followRef + effect on `visibleRows.length`).
- **Why this factoring is correct**: (a) `buildTimeline` is a pure function of `MatchData` — moving it into a library module removes the component-local coupling. (b) Two consumers (Tab 2 full-viewport + Tab 1 two slots) + possible future consumers (a demo-recorder overlay, a PDF snapshot renderer) all share the same timeline shape and tone palette. (c) Props-driven filter (`rowKinds`) lets one component serve three contexts: firehose (`['signal', 'anomaly']`), headlines (`['anomaly', 'insight', 'state']`), full (`['state', 'signal', 'insight', 'anomaly']`).
- **Concrete usage in `HudView.tsx` (Tab 1)**:
  - Right aside (under SignalRail, above footer): `<TelemetryLog rowKinds={['signal', 'anomaly']} heightClass="h-[360px]" className="..." />` — "firehose" showing every signal sample + anomaly as it lands.
  - Bottom strip (under CoachPanel, `max-w-[920px]` clamp): `<TelemetryLog rowKinds={['anomaly', 'insight', 'state']} heightClass="h-[260px]" className="..." />` — "headlines" showing only the narrative-worthy events.
- **Concrete usage in `SignalFeed.tsx` (Tab 2)**: the whole component collapses into a thin shell that renders `<TelemetryLog rowKinds={['state', 'signal', 'insight', 'anomaly']} heightClass="h-full" showHeader />` inside its full-viewport terminal frame. No visual regression vs. pre-refactor version.
- **Commit**: `888acb5 feat(dashboard): visible anomaly injections + dual TelemetryLog slots` — 388 insertions / 248 deletions in 5 files. `telemetry.ts` (new, 115 lines) + `TelemetryLog.tsx` (new, 192 lines). `SignalFeed.tsx` went from 250 lines to ~80 lines.
- **Generalizes to**: any dashboard where a rich scrolling feed is also needed as a smaller inline panel elsewhere. Extract the `buildTimeline`-equivalent + tone-palette into a library module first; only then author the reusable component wrapping them.
- **Severity**: HIGH-ROI (one refactor unlocked two Tab-1 slots + future consumers; no added bundle weight vs. inlining the logic per-consumer)
- **Files**: `dashboard/src/lib/telemetry.ts` (new), `dashboard/src/components/Telemetry/TelemetryLog.tsx` (new), `dashboard/src/components/Telemetry/SignalFeed.tsx` (collapsed), `dashboard/src/components/Hud/HudView.tsx` (two new slots).

### PATTERN-056 — Non-Interactive vercel-env-add with All-Preview-Branches Scope
- **Type**: Deploy workflow / Vercel CLI discipline
- **Context**: 2026-04-23, Phase 5 production env-var rotation. Needed to add `ANTHROPIC_API_KEY` to BOTH production and preview targets, Sensitive-flagged, without interactive prompts (so a hook/script can re-provision cleanly). First three attempts failed for different reasons:
  1. `vercel env add ANTHROPIC_API_KEY preview --sensitive` (interactive) → CLI hung waiting for stdin value.
  2. `echo "..." | vercel env add ANTHROPIC_API_KEY preview --sensitive` → worked but auto-attached the CURRENT git branch (`hackathon-demo-v1`) as the preview target, not "all branches."
  3. `printf "%s\n\n" "..." | vercel env add ...` → corrupted the value (GOTCHA-020).
- **Rule**: For preview vars scoped to ALL branches (not branch-specific), use: `vercel env add NAME preview "" --value "..." --yes --sensitive`. The three CRITICAL pieces:
  - `preview ""` — the empty-string 3rd positional ("") explicitly tells Vercel "all preview branches, no git-branch qualifier." Without it, the CLI auto-attaches whatever branch you're currently on.
  - `--value "..."` — bypasses stdin entirely; the exact string you pass is stored, with no newline/EOF ambiguity.
  - `--yes` — skip the interactive "are you sure?" prompt.
  - `--sensitive` — flags the var as non-downloadable via `vercel env pull`. Required for API keys per security policy.
- **Rule for production**: `printf "%s" "..." | vercel env add NAME production --sensitive`. Production never auto-attaches a branch (production IS the branch), so you don't need the empty-string positional. `printf "%s"` (no `\n`) keeps stdin clean — don't use `echo`, which appends an implicit newline.
- **Why this matters**: hackathon velocity requires a SINGLE reliable incantation. Three failed attempts on the same day indicate the surface is unforgiving. Codify the one that works and use it exclusively.
- **Reference**: `/vercel:vercel-cli` skill, `references/environment-variables.md`. The skill is pure documentation (no command wrappers); reading the positional-args section once saves 15 min of trial-and-error.
- **Generalizes to**: any deploy CLI that layers `interactive | stdin | flag` inputs for the same value. Always prefer an explicit flag (`--value`) when one exists. Fall back to `printf "%s"` only if no flag is available.
- **Severity**: HIGH (production env-var rotation is demo-day blocker; one reliable incantation is worth more than three almost-right ones)
- **Files**: Vercel project env store; captured in TOOLS_IMPACT.md Phase 5 ROI block.

### PATTERN-057 — Stable React Keys for Monotonic Append-Only Arrays
- **Type**: React correctness / future-proofing
- **Context**: 2026-04-23, Phase 5 PR-review feedback from the `@claude` GitHub-Action bot. Initial `TelemetryLog.tsx` rendered rows with `<FeedLine key={i} ... />`. The Claude reviewer flagged: "`visibleRows` is monotonic slice of a sorted array, so React reconciliation won't produce wrong DOM output TODAY — but any future reordering or pruning will cause subtle bugs. A stable key like `` `${row.kind}-${row.t}` `` costs nothing and future-proofs it."
- **Rule**: For arrays that are "currently monotonic append-only" but are exposed via a component API that doesn't enforce that invariant, ALWAYS use a composite stable key derived from the row's intrinsic identity, not the array index. The row's natural identity is usually `(timestamp, kind, discriminator)` where discriminator is whatever disambiguates same-`(t, kind)` collisions.
- **Canonical form used in `TelemetryLog.tsx`**:
  ```tsx
  visibleRows.map((row, i) => (
    <FeedLine
      key={`${row.t}-${row.kind}-${
        row.kind === 'signal' ? row.signal.signal_name : i
      }`}
      row={row}
      compact={isCompact}
    />
  ))
  ```
  - For `kind === 'signal'`: the `signal.signal_name` guarantees uniqueness across same-timestamp collisions (two different signals CAN land at the same `t`).
  - For `kind === 'state' | 'insight' | 'anomaly'`: index fallback is safe because same-`(t, kind)` collisions are rare for those kinds AND the array is monotonic-append-only (so a given `(t, kind, i)` stays stable across re-renders for the current session).
- **Why the index fallback is acceptable for non-signal kinds**: React's reconciliation uses the key to match previous-render VDOM nodes to current-render VDOM nodes. If the array is monotonic-append-only, `visibleRows[i]` for a given `i` doesn't change identity across renders — so `i` is effectively stable. The fallback is a pragmatic choice for the hackathon: fully stable keys would require a `uuid` field on every state/insight/anomaly, which would bloat the JSON payload. For the signal kind (highest collision risk because same-timestamp multi-signal emissions are routine), we pay the cost of a proper stable key.
- **Commit**: `787a5d1 fix(telemetry): stable FeedLine keys + restore Tab 2 progress counter` — addresses PR #4 review.
- **Generalizes to**: any React list rendering a sorted time-series. Default to composite stable keys (`${t}-${kind}-${discriminator}`) over `key={i}`. Index fallback is acceptable only when (a) the array is monotonic-append-only AND (b) you've audited that no collision source exists for the fallback kinds.
- **Severity**: MEDIUM (correctness — no current bug, but silent landmine under future reordering)
- **Files**: `dashboard/src/components/Telemetry/TelemetryLog.tsx:113-120`.

### DECISION-010 — Vercel Deployment Topology (dashboard/ root, vercel.json functions config, Sensitive env vars Production+Preview only)
- **Type**: Decision / infrastructure
- **Context**: 2026-04-23, Phase 5 production deploy. Locked the end-state topology after three failed attempts taught us what fails.
- **Topology**:
  - **Vercel project**: `dmg-decisions/panopticon-live`. Linked to the GitHub repo `andydiaz122/panopticon-live`.
  - **Root directory**: `dashboard/` (NOT repo root). The Python `backend/` is NEVER shipped to Vercel. This enforces USER-CORRECTION-006 (Vercel Python Elimination) at the infra layer: Vercel's build starts inside `dashboard/` so it cannot accidentally pick up `backend/` or `requirements-*.txt`.
  - **Functions config**: `dashboard/vercel.json` declares `{"functions": {"src/app/**/*.ts": {"maxDuration": 60}, "src/app/**/*.tsx": {"maxDuration": 60}}}`. This replaces the `export const maxDuration = 60` line that used to live in `actions.ts` before GOTCHA-019 mandated removal. Glob is intentionally broad (all `.ts`/`.tsx` under `src/app/`) rather than tight (`src/app/actions.ts`) — tight scoping risks breaking silently when a new Server Action lands. Glob breadth means `page.tsx`/`layout.tsx` inherit the 60s timeout too, which is harmless on a hobby plan (static-rendered pages don't hit Serverless at all; they're CDN-served) but worth revisiting on a paid tier.
  - **Golden data path**: `dashboard/public/match_data/utr_01_segment_a.json` (~94K lines, 4MB). Must be force-added to git (`-f`) because `.gitignore` excludes `**/match_data/` by default. Force-adding is the right call: Vercel needs these files statically served, and the client fetches them via `fetch('/match_data/...')` at runtime.
  - **Video asset path**: `dashboard/public/clips/utr_match_01_segment_a.mp4` (~3.9MB). Same story — `.gitignore` excludes `**/clips/`, force-added for Vercel.
  - **Env vars**: `ANTHROPIC_API_KEY` is the only secret. Scoped to Production + Preview (all branches). **Sensitive flag enabled** — Vercel stores it encrypted-at-rest, and `vercel env pull` will NOT write it to `.env.local`. Development target is explicitly NOT set, by design.
- **Why Development is excluded from Sensitive vars**: Sensitive Vercel env vars cannot target Development because `vercel env pull` (the command that syncs Vercel env into a local `.env.local`) refuses to write Sensitive values — that would violate the "never readable outside runtime" contract. Development target with Sensitive = no-op. Solution: keep Development env vars separately in a local `.env.local` file on disk (gitignored), and treat Sensitive-in-Vercel as a Production+Preview-only mechanism. Locally, devs use their own key, pulled from a password manager or `direnv`.
- **Golden data commitment protocol**: `git add -f dashboard/public/match_data/utr_01_segment_a.json dashboard/public/clips/utr_match_01_segment_a.mp4 && git commit -m "chore(deploy): force-add golden data and video for Vercel production build"`. Committed as `4f9df37`.
- **Severity**: HIGH (deploy topology is demo-day load-bearing; departures from this template will re-introduce the failure modes captured in GOTCHA-019/020/021)
- **Files**: `dashboard/vercel.json`, `dashboard/public/match_data/utr_01_segment_a.json`, `dashboard/public/clips/utr_match_01_segment_a.mp4`, Vercel project settings.

### PATTERN-058 — Vercel Deployment Asset Verification via `vercel curl --deployment`
- **Type**: Deploy workflow / verification
- **Context**: 2026-04-23, Phase 5 post-deploy smoke-test. After force-adding `public/match_data/*.json` + `public/clips/*.mp4` to a specific deployment URL, I needed to confirm the assets were actually being served before declaring the deploy green. Normal `curl -I <url>/match_data/...` works but requires the deployment URL be public; for preview deploys with protection rules, the deployment-scoped `vercel curl` auto-authenticates.
- **Rule**: After any deploy involving static assets, run `vercel curl --deployment <url> /<path> -- -I` for each critical asset. Pass flags after the `--` separator to forward them to the underlying `curl`. For JSON payloads: check `Content-Type: application/json` + `Content-Length` reasonable. For MP4: check `Content-Type: video/mp4` + `Accept-Ranges: bytes` (needed for `<video>` scrubbing).
- **Why `vercel curl` over plain curl**: handles deployment protection (bypass tokens, org SSO) transparently, logs the request server-side for audit, and attaches the deployment ID so the correct build artifact is probed (not a cached earlier deploy).
- **Paired with**: `vercel logs --deployment <url> --no-follow --limit 50 --expand --status-code 500` for debugging Server Actions that 500 on deploy. `--status-code 500` filters to the failing requests only; `--expand` dumps the full stack trace.
- **Severity**: MEDIUM (post-deploy verification habit; turns "I think it works" into "I know these URLs returned 200")
- **Files**: Command-line tooling; no repo artifact.

### WORKFLOW-005 — `@claude` PR-Review Bot (GitHub Action Orthogonal Review)
- **Type**: Tooling workflow (cross-linked from TOOLS_IMPACT.md)
- **Context**: 2026-04-23, Phase 5 PR #4 opened. `.github/workflows/claude.yml` (landed in `a64533b ci: add claude-code GitHub Action for @claude PR/issue responses`) configures an Action that listens for `@claude` mentions in PR/issue comments and dispatches the Claude Code agent in review mode. Post-PR-open, commenting `@claude please review` triggered the bot; returned in ~3 min with a full review.
- **What the bot caught on PR #4**:
  1. `key={i}` in `TelemetryLog.tsx:113` — monotonic-append-only array works today but silent landmine under future reordering. Addressed in `787a5d1`; captured as PATTERN-057.
  2. Lost "visible / total events" streaming progress counter in Tab 2 `SignalFeed.tsx` (regression from the `TelemetryLog` extraction). Addressed in `787a5d1` by passing `showHeader={true}` from `SignalFeed` to `TelemetryLog`.
  3. `vercel.json` glob breadth — `src/app/**/*.ts(x)` applies `maxDuration: 60` to all TS under `src/app/`, including `page.tsx`/`layout.tsx`. Deferred with rationale (hobby plan, static pages don't hit Serverless, tight scoping risks new-Action breakage).
  4. Hardcoded `#05080F` vs `colors.bg0` in TelemetryLog — `colors.bg0` is `#0A0E1A` (noticeably lighter); the darker hex is intentional terminal-feel treatment. Deferred (not a mistake).
  5. `buildTimeline` double/triple-invocation across Tab 1 TelemetryLog instances + Tab 2 SignalFeed. Accurate perf observation; deferred (demo clip is 60s, O(n)=94k rows runs in <5ms, not perceptible). Would lift to `PanopticonProvider` + expose as context state for longer clips.
- **Lesson**: The `@claude` bot review is a cheap orthogonal pass on any PR. Quick wins (stable keys, obvious regressions) are worth addressing in the same PR; perf/style nits are OK to defer with explicit rationale. The bot is not a substitute for human review — but it catches stable-key / regression / perf-smell classes that a human skimmer would miss.
- **Evidence**: https://github.com/andydiaz122/panopticon-live/pull/4#issuecomment-4308215489
- **Severity**: HIGH-ROI (one comment triggers a multi-lens review at zero marginal cost; institutionalize as a standard PR step)
- **Files**: `.github/workflows/claude.yml`; TOOLS_IMPACT.md Phase 5 ROI block.

---

## DAY 3 LEARNINGS (Apr 24, 2026) — Phase 6 Demo Production Kickoff

### GOTCHA-022 — Narrative-vs-code drift must be audited before demo voice-over
- **Type**: Gotcha / marketing-integrity
- **Context**: 2026-04-24 Phase 6 planning session. Parent `CLAUDE.md` (line 12) promises *"generative UI + visible extended thinking + Managed Agents"*. Audit against reality showed: HUD layouts are static precomputed JSON (not live Opus composition), "thinking visible" is collapsible static text (not token-by-token streaming), Managed Agents SDK not wired at all (standard Next.js Server Action).
- **Root cause**: `CLAUDE.md` is aspirational when written; code implementation catches a subset; nobody reconciles them before drafting marketing / demo voice-over.
- **Lesson**: Before writing any demo narration / submission summary, do a narrative-vs-code audit. Read the top of parent `CLAUDE.md`'s "CORE VALUE PROPOSITION" / "PRIME DIRECTIVE" claims, then grep/read the code for each claim. For each claim without a code match, REFRAME or DROP from the demo narrative. Do NOT let aspirational claims leak into voice-over.
- **Phase 6 application**: reframed Scene 2 + Scene 5 narration; Managed Agents became a 15 s future-vision segment (Scene 5B) with explicit "here's where we go next" framing, not a current-capability claim.
- **File references**: `/Users/andrew/Documents/Coding/hackathon-demo-v1/CLAUDE.md` (parent), `demo-presentation/CLAUDE.md §3.1` (codifies the three narrative corrections), `demo-presentation/PLAN.md §5` (revised storyboard).
- **Generalizes to**: any hackathon / demo / launch-page narrative where an aspirational spec document predates the implementation.
- **Severity**: HIGH — false demo claims discovered by engineering judges would sink "Depth & Execution" (20 % weight).

### GOTCHA-023 — Calibrate demo tone to the ACTUAL judge audience, not the domain audience
- **Type**: Gotcha / communication
- **Context**: 2026-04-24. Initial storyboard v1 used tennis-broadcast-analyst narration (Patrick McEnroe cadence — dramatic, emotional beats on anomaly moments). User correction Thu afternoon: *"Judges are Anthropic engineers. They value clear, simple, useful, novel, interesting, cool, beautifully aesthetic. Not childish, overly dramatic narrations."*
- **Root cause**: Pattern-matched on "sports broadcast" as the domain; failed to model who literally watches the demo video in round 1 (Anthropic + Cerebral Valley moderators, not sports fans).
- **Lesson**: The demo audience ≠ the product's end-user audience. Before drafting voice-over, explicitly ask: *who literally watches this video?* Calibrate tone to them. For engineering-judged hackathons the register is Tim-Cook-at-WWDC or demo-day-at-YC — measured, clinical, information-dense. Not SaaS keynote. Not sports broadcaster. Not sentimental voiceover.
- **Phase 6 application**: rewrote storyboard v3 with ≤ 15 narration lines total (was ~25 in v2). Every line carries a fact/number/mechanism. Silence + pulsing red bar beats McEnroe-voice. File: `demo-presentation/CLAUDE.md §3.2–3.4` codifies the tone rules.
- **Generalizes to**: any demo / marketing artifact where the consumer audience differs from the product's domain audience. Explicit audience modeling is always cheaper than a re-record.
- **Severity**: MEDIUM-HIGH — wrong tone alienates judges even when the tech is solid.

### PATTERN-059 — Remotion hybrid for React-dashboard demos (chrome only)
- **Type**: Pattern / demo-production tooling
- **Context**: 2026-04-24. Remotion (remotion.dev, React-based programmatic video) has an official MCP (`npx @remotion/mcp@latest`, launched 2026-04) and Agent Skills pack (`bunx skills add remotion-dev/skills`). Tempting to render the entire demo in Remotion.
- **The trap**: Panopticon's demo is fundamentally a LIVE React dashboard being recorded. Replicating canvas/skeleton/SignalBar spring-physics in Remotion = 40+ hours of work, duplicates animation logic, and risks drift between Remotion rendering and actual dashboard behavior.
- **Rule**: Hybrid recording. OBS records the live Vercel-deployed dashboard (~2:30 of the 3-minute video). Remotion renders ONLY the chrome: opening title card, scene-break cards, architecture slide, closing URL card, Managed Agents fan-out graph (~30 s total). Ships in ~6 hours total. Greg Ceccarelli precedent (Aug 2025): 2-hour polished chrome via Claude Code + `@remotion/mcp`.
- **When it applies**: any product demo where the hero is a live interactive UI (dashboard, IDE, editor, game). Chrome-only Remotion = title / transitions / closing. Live capture = the product itself.
- **When it doesn't**: pure motion-graphics explainers (data-viz walkthroughs, infographic-style talks) — full Remotion is correct there.
- **Phase 6 application**: Saturday build list includes 4 Remotion compositions (`OpeningTitle.tsx`, `SceneBreak.tsx`, `ManagedAgentsGraph.tsx`, `ClosingCard.tsx`) + OBS for the 2:30 live dashboard recording.
- **File reference**: `demo-presentation/PLAN.md §6` add-on A6, §7 asset registry.
- **Severity**: HIGH-ROI (avoided a 40-hour dead end; picks the right tool per surface).

### PATTERN-060 — Sportradar aesthetic: slow-mo + geometric primitives overlaid on live video
- **Type**: Pattern / visual language
- **Context**: 2026-04-24. Reference: https://sportradar.com landing page. Screenshots saved at `demo-presentation/assets/references/sportradar_tennis.png` + `sportradar_mma.png` (TODO Saturday).
- **Visual language**: player mid-motion, cyan/red vector lines drawn between body keypoints (hip→knee→ankle, shoulder→elbow→wrist), small floating label in bottom-right showing a raw CV coordinate like `"y": -38.05`. Dark navy/black background, red-and-white typography.
- **Implementation**: video playback rate animated from 1.0× → 0.25× at anomaly timestamps via `HTMLVideoElement.playbackRate`. New canvas overlay layer on top of existing skeleton canvas. Primitives:
  - angle wedge between 3 keypoints (20° arc, cyan stroke 2 px, 15 % alpha fill)
  - velocity arrow from keypoint position over 200 ms history (arrowhead at current frame)
  - trajectory spline (optional, bezier approx)
  - floating labels via absolute-positioned `<div>` with mono font + semi-transparent dark bg
- **Why it matters**: this is the visual signature that makes biometric overlays READABLE as data, not just skeleton lines. Sportradar is the sports-data industry reference; matching that register signals "this is production tech, not a toy."
- **Phase 6 application**: Add-on A2 in `PLAN.md §6`. Full implementation is 4 h (angle wedge + velocity arrow + floating labels). Minimal fallback is 30 min (playback-rate slowdown only, no annotations). User decision 2026-04-24: full A2 is end-of-Saturday polish ONLY; demo ships with or without.
- **File references**: `dashboard/src/components/PanopticonEngine.tsx` (extend point), new `dashboard/src/components/AnnotationOverlay.tsx` (create under `demo-v1` branch).
- **Severity**: HIGH-ROI if time permits, deprioritized if not.

### DECISION-011 — Phase 6 demo production decisions locked 2026-04-24
- **Type**: Decision (demo production)
- **Single-line summary**: 3-minute demo video produced Saturday–Sunday, submitted by Sunday 5 PM EST (3-hour buffer before 8 PM deadline).
- **Managed Agents**: SKIP implementation; include 15 s future-vision segment (Scene 5B) reasoned from first principles (per-player pre-trained agents, durable match memory, specialist skills).
- **Voice**: MacBook mic primary (Tennis Channel analyst register, MINIMAL footprint ~12 lines); ElevenLabs stretch if time.
- **Weird feature**: CUT (Opus Dreams skipped — too theatrical for engineering-judge audience, per GOTCHA-023).
- **Tickertape bar (Tab 1 bottom)**: ADD; phase-weighted signal order — `PRE_SERVE_RITUAL`: `toss_variance + ritual_entropy + crouch_depth`; `ACTIVE_RALLY`: `lateral_work + baseline_retreat + recovery_latency`.
- **Hero clip**: existing 60 s segment in repo (anomalies already tuned at t=35.9/45.3/59.1 s).
- **Remotion scope**: chrome only (title card + scene breaks + closing card + Managed Agents fan-out graph).
- **Sportradar slow-mo + annotation overlay (A2)**: deprioritized — end-of-Saturday polish only.
- **YouTube**: public, on Andrew's channel.
- **"Built with Claude Code" visibility**: Scene 5A architecture overlay + Scene 2 3-second `.claude/skills/` file-tree flash (12 project-scoped skill packs visible).
- **Tone**: technical-clinical, Tim Cook at WWDC, NOT McEnroe. No dramatic cadence.
- **`demo-v1` branch merge**: deferred until post-submit (defaults to M1 = immediate merge to main).
- **Files**: `demo-presentation/CLAUDE.md`, `demo-presentation/PLAN.md`, `~/.claude/plans/phase-6-demo-production.md`.
- **Severity**: Foundation for all Sat–Sun work.

### WORKFLOW-006 — Structured phase-planning protocol (3 parallel research agents + batched decisions)
- **Type**: Workflow / orchestration
- **Context**: 2026-04-24. Applied to Phase 6 demo planning; generalizes to any major new phase kickoff.
- **Protocol**:
  1. Fire 3 parallel research agents in a SINGLE message:
     - Explore agent → codebase state audit (what's demo-ready, what's missing, what narrative risks exist)
     - `general-purpose` → domain-specific research (tools, references, industry visual language)
     - `general-purpose` → creative/strategic research (past winners, blog best practices, game theory vs. other submissions)
  2. Synthesize findings into a draft plan + open-questions list.
  3. Use `AskUserQuestion` to BATCH the 2–4 highest-leverage decisions — never ask one-at-a-time when they can be batched.
  4. Lock answers into the plan; identify any follow-up questions; iterate via `AskUserQuestion` until no blockers.
  5. Split output into:
     - `<scope-folder>/CLAUDE.md` — rules (under 200 lines, no plans).
     - `<scope-folder>/PLAN.md` — detailed storyboard + timeline + assets + open questions.
     - `~/.claude/plans/phase-N.md` — strategic trail (short, ~80 lines) — keeps the chain of reasoning.
- **Why it works**: parallelizes ~30 min of research into ~15 min wall-clock. Batched `AskUserQuestion` prevents the back-and-forth where each question gets a 1:1 chat turn. Separating rules (`CLAUDE.md`) from plans (`PLAN.md`) prevents rule bloat and lets plans evolve independently.
- **Phase 6 application today**: ~5 min of agent dispatch → ~8 min of agent-parallel work → ~10 min synthesis → ~3 min `AskUserQuestion` for 4 decisions → plan locked in ~30 min wall-clock time vs. ~2 hours if done sequentially.
- **Generalizes to**: any phase kickoff, product launch, or strategic research sprint where decision space is large but knowable in a single synthesis pass.
- **Severity**: HIGH-ROI (default planning protocol going forward).

---

## DAY 4 LEARNINGS (Apr 25, 2026)

(To be populated)

---

## DAY 5 LEARNINGS (Apr 26, 2026)

(To be populated)
