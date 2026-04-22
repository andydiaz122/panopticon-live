# PHASE 1 PLAN — CV Spine + 7 Signals (Revised after 2026-04-21 Team Lead Review)

**Status** (updated 2026-04-22 late session):
- **Action 1**: ✅ **COMPLETE** (commit `db2a1e9`) — MEMORY.md: 10 USER-CORRECTIONs + 13 PATTERNs; 6 existing skills updated; 4 new specialized skills created; 4 agents updated; FORANDREW.md + ORCHESTRATION_PLAYBOOK.md revised.
- **Action 2**: ✅ **COMPLETE** (commit `cd52758`) — 45/45 tests, 82.75% coverage, ruff clean.
- **Action 2.5** (Citadel override patch sprint): ✅ **COMPLETE** (commit `5e22166`) — USER-CORRECTIONs 011-016 integrated; BaseSignalExtractor ABC, @field_serializer float rounding, conditional DEAD_TIME uncoupling, RollingBounceDetector; 96/96 tests, 87.68% coverage, ruff clean, python-reviewer 1H+2M fixed.
- **Action 3 pre-flight USER-CORRECTION-017** (Homography Z=0 Invariant): ✅ **COMPLETE** (commit `6a12399`).
- **Fleet 4 PILOT** (`lateral_work_rate`): ✅ **COMPLETE** (commit `058cf32`) — 12 tests, 100% coverage.
- **Action 3 pre-flight round 2** (USER-CORRECTIONs 018-022): ✅ **COMPLETE** (commit `5d2395f`) — compiler-flush contract, structural split-step, phantom-serve guard + biological ruler, asymmetric baseline geometry, fail-fast dict access. 109/109 tests.
- **Action 3 sequential fleet sprint**: ✅ **COMPLETE** — 4 fleets dispatched sequentially (worktree isolation unavailable → DECISION-006).
  - Fleet 1 (`recovery_latency_ms` + `split_step_latency_ms`, commit `8ecb27e`): 135/135 tests, 97% coverage.
  - Fleet 2 (`serve_toss_variance_cm` + `ritual_entropy_delta`, commit `144343a`): 160/160 tests, 91% coverage.
  - Fleet 3 (`crouch_depth_degradation_deg` + `baseline_retreat_distance_m`, commit `67fb7ae`): 194/194 tests, 100% coverage.
- **Action 3.5** (FeatureCompiler integration): ✅ **COMPLETE** (commit `23de0f2`) — 13 end-to-end tests, 207/207 total, 91.36% project coverage, ruff clean.
- **Action 4** (Pre-Compute Crucible): 🟡 **IN PROGRESS** — DB writer + precompute CLI with mocked tests.

**Owner agents**: `documentation-librarian`, `cv-pipeline-engineer`, `test-forensic-validator`, `vercel-deployment-specialist`.

## Wave 2 — 5 Additional USER-CORRECTIONs Integrated (006-010)

Per 2026-04-21 team-lead second-wave review:

| # | Correction | Implementation location |
|---|---|---|
| 006 | **Vercel Python Elimination** — delete `backend/api/` FastAPI; Next.js Server Action for scouting report | `.claude/skills/vercel-ts-server-actions/SKILL.md`, `vercel-deployment-specialist` agent, `opus-coach-architect` agent |
| 007 | **Absolute Court Half Assignment** — split by `y_m` vs net (11.885m); top-1 per half | `.claude/skills/topological-identity-stability/SKILL.md`, `backend/cv/pose.py` |
| 008 | **Physical Kalman Domain** — meters-in, m/s-out; conversion happens BEFORE Kalman update | `.claude/skills/physical-kalman-tracking/SKILL.md`, `backend/cv/kalman.py` |
| 009 | **Lateral Rally Blindspot** — `math.hypot(vx, vy)` for state thresholds | `backend/cv/state_machine.py` |
| 010 | **Asymmetric Pre-Serve Desync** — match-level coupling via bounce | `.claude/skills/match-state-coupling/SKILL.md`, `backend/cv/state_machine.py` |

**Architecture consequence**: The Vercel deploy surface collapsed from (Next.js + Python Fluid Compute + DuckDB) to (Next.js only). The `backend/api/` directory is cancelled. `requirements-prod.txt` is deleted. Python becomes strictly a local tool producing static JSON + PDF artifacts.

---

## 1. Acknowledgment of the 5 "Reality Gap" Corrections

| # | Correction | Old architecture | New architecture |
|---|---|---|---|
| 1 | **Video-Sync Trap** | FastAPI SSE streamed 30 FPS keypoints from DuckDB; Vercel would sever at 10-60s, video buffering would desync | `precompute.py` exports `dashboard/public/match_data.json`; Next.js fetches once; `<canvas>` rAF reads `videoRef.currentTime × fps` to index frames |
| 2 | **Opus Latency Paradox** | Live Opus during demo via SSE; 5-15s thinking = commentary arrives 10s after the point | Opus runs OFFLINE inside `precompute.py`, emits timestamped `CoachInsight` + `HUDLayoutSpec`. Live Opus ONLY for scouting-report Managed Agent |
| 3 | **Far-Court Occlusion** | Ankle-dependent signals assume confident ankle keypoints | Asymmetric fallback chain: ankle → knee → hip/pelvis with torso-scalar re-normalization when confidence < 0.3 |
| 4 | **Hungarian Identity Swap** | Euclidean-distance Hungarian assignment for A/B identity | **Topological Y-sorting**: in-court polygon filter → top-2 confidence → Player A = max Y (near), Player B = min Y (far) |
| 5 | **Homography Aspect-Ratio Skew** | `cv2.getPerspectiveTransform` fed normalized [0,1] corners | Backend un-normalizes first: `corners_pixels = corners_normalized × [[W, H]]` before feeding to OpenCV |

**Net effect on Vercel architecture:**
- Runtime compute (previously SSE proxy + Opus calls) → **near zero** (only scouting-report Managed Agent)
- Payload shape: 1 static JSON file per match (~3–5 MB gzipped) served from Next.js `public/`
- Demo robustness: frame-perfect, network-independent
- Prize targeting: cleaner "Best Use of Managed Agents" story (it's now the ONLY live agent call)

---

## 2. Revised Runtime Architecture

```
═══════════════════════ OFFLINE PRECOMPUTE (local, one-time per clip) ═══════════════════════

  Video MP4 → ffmpeg stdout pipe → numpy BGR24
     ↓
  YOLO11m-Pose (MPS, imgsz=1280, conf=0.001) → .xyn normalized keypoints
     ↓
  In-court polygon filter (via CourtMapper with aspect-ratio-corrected homography)
     ↓
  Topological Y-sort → Player A (near) + Player B (far)
     ↓
  2D Kalman smoother per player (filterpy, 10-frame spike suppression)
     ↓
  Kinematic state machine per player (PRE_SERVE_RITUAL / ACTIVE_RALLY / DEAD_TIME)
     ↓
  7 signal extractors (with asymmetric far-court fallbacks)
     ↓
  Per-player baseline calibration (first 2 min) + anomaly z-scores
     ↓
  Opus 4.7 COACH reasoning on sliding windows → CoachInsight(timestamp_ms, thinking, commentary)
     ↓
  Opus 4.7 DESIGNER on match-state transitions → HUDLayoutSpec(timestamp_ms, widgets)
     ↓
  Haiku 4.5 NARRATOR per-second beats → NarratorBeat(timestamp_ms, text)
     ↓
  Export → dashboard/public/match_data.json
         → data/panopticon.duckdb  (for tool-use queries from live Managed Agent only)

═══════════════════════ RUNTIME (Vercel) ═══════════════════════

  Dashboard loads → fetch('/match_data.json') ONCE
     ↓
  <video src="…"> plays (HTML5 native controls)
     ↓
  requestAnimationFrame loop:
    frameIdx = floor(videoRef.current.currentTime × clip_fps)
    draw skeleton at match_data.keypoints[frameIdx]
    render HUD at nearest HUDLayoutSpec before currentTime
    typewrite commentary matching currentTime band
  ↓
  "Generate Scouting Report" button → POST /api/scouting-report → Managed Agent → PDF
```

**Vercel function footprint**: a single `/api/scouting-report` Python function reading `panopticon.duckdb`. No SSE. No per-frame endpoints. Stays well under 250 MB.

---

## 3. Action 1 — Documentation Updates (do first)

Executed by `documentation-librarian`.

### 3.1. `MEMORY.md` additions (5 USER-CORRECTION entries)

```markdown
### USER-CORRECTION-001 — Video-Sync Trap (Vercel SSE timeout + buffering desync)
- Type: User-Correction (critical)
- Context: Team-lead review 2026-04-21
- Lesson: ABORT FastAPI SSE streaming for 30 FPS keypoints. Vercel Serverless severs long
  connections at 10-60s, and HTML5 video buffering would desync the skeleton from the player.
  Canonical shape: precompute.py writes dashboard/public/match_data.json (keypoints + signals +
  Opus commentary + HUD layouts, all tagged timestamp_ms). Frontend fetches once. rAF loop
  indexes via videoRef.currentTime × clip_fps. Perfect sync, zero network jitter, $0 compute.
- Severity: CRITICAL

### USER-CORRECTION-002 — Opus Latency Paradox (5-15s thinking vs 1.5s rally)
- Type: User-Correction (critical)
- Context: Team-lead review 2026-04-21
- Lesson: Live Opus during demo produces "prediction after the fact" because extended-thinking
  calls take 5-15s. Pre-compute all Opus intelligence offline during precompute.py. Store
  CoachInsight + HUDLayoutSpec with timestamp_ms. Replay at playback time. The ONLY live Opus
  at demo time is the Managed Agents scouting-report pipeline (Best Use of Managed Agents prize).
- Severity: CRITICAL

### USER-CORRECTION-003 — Far-Court Net Occlusion
- Type: User-Correction
- Context: Team-lead review 2026-04-21
- Lesson: The broadcast camera's perspective places the tennis net IN FRONT of Player B's
  ankles ~80% of frames. Signal extractors MUST implement an asymmetric fallback chain when
  ankle confidence < 0.3: ankle → knee → hip/pelvis, with torso-scalar re-normalized to the
  lower body segment actually in use. Applies to: crouch_depth, baseline_retreat, feet-position
  homography projection, split_step zero-crossing.
- Severity: HIGH

### USER-CORRECTION-004 — Topological Y-Sorting (not Hungarian)
- Type: User-Correction
- Context: Team-lead review 2026-04-21
- Lesson: DO NOT use Hungarian assignment or Euclidean-distance tracking for A/B identity.
  A ball-boy running behind a player will swap IDs. Instead:
    1. Filter YOLO detections to those inside the court homography polygon (+2m margin)
    2. Take top-2 by confidence
    3. Player A (near) = detection with max Y (closer to camera = bottom of frame)
    4. Player B (far) = detection with min Y (farther from camera = top of frame)
  Tennis players do NOT cross the net mid-rally; this is provably correct.
- Severity: HIGH

### USER-CORRECTION-005 — Homography Aspect-Ratio Skew
- Type: User-Correction
- Context: Team-lead review 2026-04-21
- Lesson: court_annotator.html outputs normalized [0,1] corners. cv2.getPerspectiveTransform
  operates in whatever coordinate space you feed it. Feeding normalized coords directly produces
  a matrix that assumes a 1:1 aspect ratio — a 1m lateral move registers as larger than a 1m
  vertical move on 16:9 footage. Backend MUST un-normalize first:
    corners_pixels = corners_normalized * np.array([[frame_width, frame_height]])
  THEN call cv2.getPerspectiveTransform(corners_pixels, court_meters_numpy).
  Feed keypoints to the mapper as pixel coords (multiply .xyn by W, H before projection).
- Severity: HIGH
```

### 3.2. `.claude/skills/*/SKILL.md` edits

Update these skills to bake the corrections into the pattern reference (so future Claude sessions can't regress):

- **`cv-pipeline-engineering`**: replace "Stage 6 — DuckDB Write" section with "Stage 6 — match_data.json Export" describing the static-JSON pattern. Add topological Y-sort to Stage 4 state machine.
- **`biomechanical-signal-semantics`**: add "Far-Court Occlusion Fallback Chain" subsection. Update crouch_depth, baseline_retreat, split_step_latency formulas to reference the fallback.
- **`opus-47-creative-medium`**: add "Pre-compute over Live for high-frequency UX" subsection. Clarify that live Opus = scouting-report only.
- **`react-30fps-canvas-architecture`**: add "Video-Clock-Slaved rAF" pattern. `useEffect` subscribes to the video's `timeupdate`/rAF; canvas paints at `Math.floor(currentTime × clip_fps)`.
- **`duckdb-pydantic-contracts`**: note that DuckDB is now read-only for Managed Agent tool queries; the frontend doesn't touch DuckDB.
- **`panopticon-hackathon-rules`**: add "No live SSE streaming; no live Opus at playback" as an enforced rule.

### 3.3. Update `FORANDREW.md`

Add a 2026-04-21 entry under "Lessons Learned" summarizing the 5 corrections, plus a decision note that the architecture now has a SINGLE live API path (scouting report), making Vercel risk nearly zero.

### 3.4. Update `docs/ORCHESTRATION_PLAYBOOK.md`

Replace Phase 2 "FastAPI SSE Replay Service" references with "Static `match_data.json` + video-clock-slaved rAF."

**Deliverable of Action 1**: one commit `docs: team-lead 5-correction review — USER-CORRECTION-001 through 005`.

---

## 4. Action 2 — CV Spine (sequential, TDD-enforced)

Executed by `cv-pipeline-engineer` with `test-forensic-validator` writing tests FIRST.

### 4.1 `backend/cv/homography.py` — aspect-ratio-safe court mapper

**API surface:**
```python
class CourtMapper:
    SINGLES_LENGTH_M: float = 23.77
    SINGLES_WIDTH_M: float = 8.23

    def __init__(
        self,
        corners_normalized: CornersNormalized,  # Pydantic: top_left, top_right, bottom_right, bottom_left
        frame_width: int,
        frame_height: int,
    ) -> None: ...

    def to_court_meters(self, pt_normalized_xy: tuple[float, float]) -> tuple[float, float] | None:
        """Project a normalized [0,1] point to court meters. Returns None if off-court (>2m margin)."""

    def is_in_court_polygon(self, pt_normalized_xy: tuple[float, float], margin_m: float = 2.0) -> bool: ...
```

**Implementation rules:**
- **USER-CORRECTION-005**: Un-normalize corners: `corners_px = corners_norm * np.array([[W, H]])`
- Target court corners in meters: top-left = `(0, 0)`, top-right = `(W_singles, 0)`, bottom-right = `(W_singles, L_singles)`, bottom-left = `(0, L_singles)` where W = 8.23, L = 23.77
- `cv2.getPerspectiveTransform(corners_px.astype(np.float32), court_m.astype(np.float32))`
- On project: un-normalize input pt, apply transform, check bounds with margin, return None if out

**Tests first (written by test-forensic-validator):**
- Synthetic: rectangular corners → identity-like mapping → on-court point projects to expected meters
- Synthetic: trapezoidal corners from broadcast angle → validate top-of-frame point maps to far baseline (~23m)
- Bounds: bleacher pixel → returns None
- Aspect-ratio regression: without un-normalization, a 1m lateral vs vertical move produce distorted magnitudes (must FAIL if we ever regress)

### 4.2 `backend/cv/pose.py` — YOLO wrapper with Topological Y-Sort

**API surface:**
```python
class PlayerDetection(PanopticonBase):
    player: Literal["A", "B"]
    keypoints_xyn: list[tuple[float, float]]  # length 17
    confidence: list[float]                    # length 17
    feet_mid_xyn: tuple[float, float]          # average of ankle keypoints, or knee/hip fallback if ankle conf low
    in_court: bool

class PoseExtractor:
    def __init__(self, weights: str, device: str, court_mapper: CourtMapper): ...

    @torch.inference_mode()
    def infer(self, frame_bgr: np.ndarray) -> list[PlayerDetection]:
        """Runs YOLO, filters to in-court, topological-Y-sorts, returns at most 2 detections."""
```

**Implementation rules:**
- **USER-CORRECTION-004**: after YOLO, compute `feet_mid_xyn` for every raw detection (with ankle→knee→hip fallback). Filter via `court_mapper.is_in_court_polygon(feet_mid_xyn)`. Take top-2 by mean confidence. Sort by `feet_mid_xyn.y`: max-Y → Player A (near), min-Y → Player B (far).
- **USER-CORRECTION-003**: helper `robust_foot_point(kp, conf)` returns ankle-mid if both ankles confidence ≥ 0.3, else knee-mid if both ≥ 0.3, else hip-mid.
- MPS safeguards: `@torch.inference_mode()`, `torch.mps.empty_cache()` every 50 frames, conf=0.001, imgsz=1280, single-worker executor.

**Tests first:**
- Synthetic: crafted YOLO output with 4 detections (2 in-court + 2 crowd) → returns exactly 2 in-court, sorted A/B correctly
- Far-court fallback: ankle confidence < 0.3 → foot-point falls back to knees → still in-court polygon
- Empty frame: returns []
- Only 1 detection: returns [PlayerA] (near player), B is None-equivalent absent

### 4.3 `backend/cv/kalman.py` — 2D constant-velocity tracker

**API surface:**
```python
class KalmanTracker2D:
    def __init__(self, dt: float = 1/30) -> None: ...
    def update(self, measurement_xy: tuple[float, float] | None) -> tuple[float, float, float, float]:
        """Returns (x, y, vx, vy) smoothed state."""
    @property
    def frames_since_init(self) -> int: ...
    @property
    def is_converged(self) -> bool:  # True after 10+ frames
```

**Implementation rules:**
- `filterpy.kalman.KalmanFilter(dim_x=4, dim_z=2)`, F = constant-velocity, H = position-only, P, R, Q per `cv-pipeline-engineering` skill
- **SP5 spike suppression**: expose `is_converged` = `frames_since_init >= 10`. Downstream signals that depend on velocity/acceleration MUST gate on this.
- Occlusion handling: on `measurement_xy=None`, call `predict()` without `update()` — the filter "coasts" at last velocity.

**Tests first:**
- Synthetic linear motion 2 m/s → smoothed velocity converges to 2.0 within 10 frames
- Stepwise measurement → Kalman smooths the step (low-pass behavior)
- Occlusion: 5 None frames → position extrapolates linearly
- `is_converged` is False for first 10 updates, True from 11 onward

### 4.4 `backend/cv/state_machine.py` — per-player 3-state FSM

**API surface:**
```python
class PlayerStateMachine:
    def __init__(self) -> None: ...
    def update(self, vy_smoothed: float, timestamp_ms: int) -> PlayerState:
        """Returns current state. Handles transitions per velocity thresholds."""
    def transition_events(self) -> list[StateTransition]:
        """Returns transitions since last call (for signal extractors to react to)."""
```

**Implementation rules:**
- PRE_SERVE_RITUAL → ACTIVE_RALLY: `|vy| > 0.2 m/s` for 5+ consecutive frames
- ACTIVE_RALLY → DEAD_TIME: `|vy| < 0.05 m/s` for 15+ consecutive frames
- DEAD_TIME → PRE_SERVE_RITUAL: small-amplitude bounce detected in Y position (`|vy|` oscillates through 0 with period < 2s)
- Initial state: UNKNOWN → PRE_SERVE_RITUAL on first valid measurement

**Tests first:**
- Feed simulated `vy` series from stillness → motion → stillness → asserts correct state sequence
- Transition events emitted exactly once per transition
- Returner walking off-screen (null vy sequence) does not gate the other player's state (asymmetric independence)

### 4.5 Action-2 exit gate (before Action 3)

- All 4 spine modules pass unit tests
- `pytest --cov=backend.cv --cov-report=term-missing` shows ≥80% line coverage on the spine
- `ruff check backend/cv/` is clean
- A "smoke" integration: run pose.py on `data/clips/utr_match_01_segment_a.mp4` with a fake court-corners JSON, confirm output is 2 PlayerDetections per frame (or ≤2) with Kalman-smoothed state, no MPS OOMs.
- Commit: `feat(cv): phase-1 CV spine — homography, pose, kalman, state machine`
- **Pause** for team-lead review. Action 3 (signal sprint) does not start automatically.

---

## 5. Action 3 — Parallel Signal Sprint (APPROVAL REQUIRED FIRST)

Executed via `/devfleet`. Each fleet is a separate worktree + agent pair running TDD.

| Fleet | Signals | Complexity |
|---|---|---|
| 1 | recovery_latency_ms, split_step_latency_ms | velocity-threshold timings |
| 2 | serve_toss_variance_cm, ritual_entropy_delta | Lomb-Scargle + wrist tracking |
| 3 | crouch_depth_degradation_deg, baseline_retreat_distance_m | **Far-court fallbacks required** |
| 4 | lateral_work_rate | X-axis COM velocity p95 |

For each signal: `test-forensic-validator` writes `tests/test_signals/test_<name>.py` with 3 synthetic-keypoint fixtures FIRST, `biomech-signal-architect` defines math contract, `cv-pipeline-engineer` implements.

Exit gate: 7/7 signals pass tests, end-to-end precompute on utr_01 produces a `match_data.json` with all 7 non-None during ACTIVE_RALLY.

**This phase will NOT be started until the team lead reviews Action 2's output.**

---

## 6. Files to be created / modified in Actions 1 + 2

```
MEMORY.md                                                          (edit: +5 USER-CORRECTION entries)
FORANDREW.md                                                       (edit: +2026-04-21 lessons entry)
docs/ORCHESTRATION_PLAYBOOK.md                                     (edit: Phase 2 SSE → static JSON)
.claude/skills/cv-pipeline-engineering/SKILL.md                    (edit: stage 4 Y-sort; stage 6 JSON export)
.claude/skills/biomechanical-signal-semantics/SKILL.md             (edit: +far-court fallback section)
.claude/skills/opus-47-creative-medium/SKILL.md                    (edit: precompute > live for UX)
.claude/skills/react-30fps-canvas-architecture/SKILL.md            (edit: +video-clock-slaved rAF)
.claude/skills/duckdb-pydantic-contracts/SKILL.md                  (edit: DuckDB is RO for Managed Agent only)
.claude/skills/panopticon-hackathon-rules/SKILL.md                 (edit: +"no live SSE, no live Opus at playback")

backend/cv/homography.py                                           (new)
backend/cv/pose.py                                                 (new)
backend/cv/kalman.py                                               (new)
backend/cv/state_machine.py                                        (new)

tests/test_cv/__init__.py                                          (new)
tests/test_cv/test_homography.py                                   (new, TDD-first)
tests/test_cv/test_pose.py                                         (new, TDD-first)
tests/test_cv/test_kalman.py                                       (new, TDD-first)
tests/test_cv/test_state_machine.py                                (new, TDD-first)

backend/db/schema.py                                               (edit: +CornersNormalized, PlayerDetection, StateTransition)
```

Not touched in Actions 1+2: `backend/agents/`, `backend/api/`, `dashboard/`, `scripts/precompute.py` (those are later phases).

---

## 7. Verification Plan (before pausing for review)

1. `pytest tests/test_cv/ -v` — all new tests green
2. `pytest --cov=backend.cv --cov-report=term-missing` — ≥80% coverage on spine
3. `ruff check backend/ tests/` — clean
4. Smoke integration (manual): feed one frame of utr_01 to `PoseExtractor` with a mocked CourtMapper, print the 2 returned `PlayerDetection` records
5. `git log --oneline` shows 2 commits: Action 1 docs + Action 2 spine
6. Claude's FORANDREW.md has the "Day 1 end-of-phase" block populated

---

## 8. Open assumptions (flag if wrong)

- **A1**: The court corners JSON format from `tools/court_annotator.html` is normalized [0,1] (verified Apr 21). `CourtMapper` constructor accepts that format + frame W,H.
- **A2**: UTR singles matches use the standard singles court (23.77m × 8.23m). If these are mixed singles/doubles, we may need doubles dims (10.97m width). Assumption: singles.
- **A3**: `clip_fps` from ffprobe is trustworthy (30 FPS on utr_01 confirmed). The rAF loop will assume this as constant.
- **A4**: The dashboard will consume a single `match_data.json` up to ~10 MB gzipped. At 15 FPS keypoint decimation for 60s, we project ~3–5 MB uncompressed, well inside budget.
- **A5**: Opus pre-computation on a 60s clip yields ~5–8 CoachInsight entries + ~3–5 HUDLayoutSpec entries + ~60 Haiku beats. Batch size manageable in <2 minutes offline.

---

## 9. What I am NOT changing

- No changes to `.claude/agents/*.md` — the 12 agents still have narrow mandates; these corrections are constraint-layer, not role-layer.
- No changes to Day-0 probe results or the `scripts/probe_clip.py` slope-sign fix — already committed.
- No changes to `LICENSE`, `pyproject.toml`, or the requirements bifurcation.

---

## Awaiting approval

Please approve executing **Action 1** (doc updates) and **Action 2** (CV spine with TDD). Action 3 (parallel signal sprint) will be held until you review Action 2's output.
