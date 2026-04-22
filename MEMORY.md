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

---

## DAY 2 LEARNINGS (Apr 23, 2026)

(To be populated)

---

## DAY 3 LEARNINGS (Apr 24, 2026)

(To be populated)

---

## DAY 4 LEARNINGS (Apr 25, 2026)

(To be populated)

---

## DAY 5 LEARNINGS (Apr 26, 2026)

(To be populated)
