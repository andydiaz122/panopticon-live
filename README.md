# PANOPTICON LIVE

**A 2K-Sports-style video-game HUD for professional tennis, powered by Claude Opus 4.7.**

Built for the Anthropic × Cerebral Valley **Built with Opus 4.7** virtual hackathon — April 21-26, 2026.

[Live demo](https://panopticon-live.vercel.app) (TBD) · [3-min demo video](https://youtube.com) (TBD) · MIT licensed

---

## What it does

Panopticon Live ingests a professional tennis match video, extracts seven biomechanical fatigue signals from broadcast-quality pose estimation, and renders the match as a **live video-game-style HUD** — a **world-class single-player biomechanics deep-dive**:

- **Cyan skeleton overlay** tracking the target player (Player A, near court) frame-by-frame — drawn via a zero-React-render rAF canvas loop at 30 FPS
- **Pulsing signal bars** — fatigue, serve toss variance, baseline retreat, lateral work rate — animate when the player deviates from their match-opening baseline
- **Opus 4.7 Coach panel** — coach-register commentary with visible `extended_thinking` tokens and real quantitative anchors ("A's baseline_retreat collapsed 1.67m → 0.10m")
- **Generative HUD layout** — Opus 4.7 Designer re-arranges widgets in real time as match state changes (serve ritual → toss tracer; rally → footwork heatmap)
- **Haiku 4.5 narrator ticker** — per-N-second broadcast-style color commentary ("Player A explodes laterally, covering the court with explosive urgency")
- **Signal Feed** (2nd tab) — raw JSON stream, the B2B product surface for prediction-market infrastructure (Valence, Sequence, Dome)
- **Scouting Report** (3rd tab) — Claude Managed Agent generates a full PDF report on demand

**Scope note (DECISION-008, 2026-04-22)**: Panopticon is deliberately a single-player system. We master ONE player's biomechanics at a world-class level rather than two players superficially. The "Moneyball for tennis" angle. See [MEMORY.md](MEMORY.md) GOTCHA-016 for the CV detector-capacity rationale.

## Why it matters

Nobody extracts biomechanical fatigue signals from free broadcast video today. The sensor doesn't exist — until you build it. Panopticon Live is both a judge-facing visual showcase AND the foundation of a B2B signal-feed product aimed at the prediction-market infrastructure layer.

## Architecture

```
Video (MP4)
  → ffmpeg stdout (BGR24 pipe, Zero-Disk per CLAUDE.md)
  → YOLO11m-Pose on Apple MPS (17 COCO keypoints per detection)
  → assign_players (bbox_conf ≥ 0.5 gate, court-half topology, tight lateral polygon)
  → Kalman 2D smoothing (filterpy) on court meters via homography
  → 3-state kinematic state machine (PRE_SERVE_RITUAL / ACTIVE_RALLY / DEAD_TIME)
  → 7 biomechanical signal extractors (state-gated, BaseSignalExtractor ABC)
  → DuckDB (pre-computed panopticon.duckdb) + match_data.json export
  → [OFFLINE] Claude Opus 4.7 Coach (tool-use loop over signal queries)
  → [OFFLINE] Claude Opus 4.7 HUD Designer (generative widget layouts)
  → [OFFLINE] Claude Haiku 4.5 Narrator (per-10s color-commentary beats)
  → match_data.json shipped to Next.js /public/match_data/
  → Next.js 16 dashboard (PanopticonEngine rAF canvas loop; target 30 FPS, zero React renders)
  → [LIVE @ demo time] Claude Managed Agent scouting report via Vercel Server Action
```

All Opus/Haiku work is **pre-computed** at build time, so there's no network wobble during the demo. The only live Anthropic call is the scouting-report Managed Agent, which the user initiates by clicking.

## The Three Roles of Opus 4.7

1. **Reasoner** — extended-thinking calls with deterministic signal-query tools. Thinking tokens streamed visibly in the UI.
2. **Designer** — generative UI. Given current match state + active anomaly, Opus outputs a JSON layout spec. The frontend has fixed widget primitives; Opus arranges them dynamically.
3. **Voice** — streamed coach-register commentary, typewritten into the HUD panel. Haiku 4.5 generates cost-aware per-second beats in parallel.

Plus a **Claude Managed Agent** for the long-running scouting-report PDF pipeline.

## Seven biomechanical signals

| Signal | What it measures |
|---|---|
| `recovery_latency_ms` | Time from rally end to Kalman-smoothed velocity < 0.5 m/s |
| `serve_toss_variance_cm` | Std dev of wrist-apex height across serves |
| `ritual_entropy_delta` | Lomb-Scargle spectral entropy of pre-serve bounce cadence |
| `crouch_depth_degradation_deg` | Pelvis-to-ankle distance drift (torso-normalized) |
| `baseline_retreat_distance_m` | Homography-transformed position relative to own baseline |
| `lateral_work_rate` | X-axis COM p95 velocity during rally |
| `split_step_latency_ms` | Time from opponent contact to own velocity zero-crossing |

See [`.claude/skills/biomechanical-signal-semantics/SKILL.md`](.claude/skills/biomechanical-signal-semantics/SKILL.md) for mathematical definitions + literature thresholds.

## Hackathon constraints (all enforced in code)

- **New Work Only** — every line written Apr 21-26, 2026; no prior code vendored
- **MPS only, no CUDA** — strict `@torch.inference_mode()`, `torch.mps.empty_cache()` every 50 frames, `conf=0.001`, `imgsz=1280`
- **Zero-Disk video pipeline** — ffmpeg stdout → numpy via `readexactly`; no `cv2.VideoCapture` from disk
- **Bifurcated requirements** — `requirements-local.txt` (torch, ultralytics, opencv) for pre-compute; `requirements-prod.txt` (fastapi, anthropic, duckdb only) for Vercel's 250MB serverless limit
- **Pydantic v2 at every module boundary** — no dict crosses between modules
- **React 30-FPS death-spiral defense** — per-frame keypoints go into `useRef` + `requestAnimationFrame` + `<canvas>` direct paint; never `useState`

## Repo layout

```
panopticon-live/
├── backend/            Python 3.12 CV + agents + API
│   ├── config.py       Env-derived Pydantic settings
│   ├── cv/             YOLO, Kalman, state machine, signals
│   ├── db/             DuckDB schema + Pydantic v2 contracts
│   ├── agents/         Opus 4.7 Reasoner/Designer/Voice + Haiku + Managed Agent
│   └── api/            FastAPI SSE replay + Opus orchestration
├── dashboard/          Next.js 16 App Router (Bun for dev)
├── scripts/            CLI tools (probe_clip.py, etc.)
├── tools/              court_annotator.html (local-only dev tool)
├── data/               Pre-computed DuckDB + clips (gitignored)
├── tests/              pytest suite (≥80% coverage)
├── docs/               ORCHESTRATION_PLAYBOOK.md + architecture
└── .claude/
    ├── agents/         12 specialized hackathon agents
    └── skills/         8 project-scoped skills (orthogonal)
```

## Living documents

- [CLAUDE.md](CLAUDE.md) — prime directive + hard constraints
- [FORANDREW.md](FORANDREW.md) — plain-language walkthrough, decisions, bug journal
- [MEMORY.md](MEMORY.md) — structured learnings (gotchas, patterns, decisions)
- [TOOLS_IMPACT.md](TOOLS_IMPACT.md) — tool/skill/agent ROI log
- [docs/ORCHESTRATION_PLAYBOOK.md](docs/ORCHESTRATION_PLAYBOOK.md) — tool-by-phase runbook

## Quick start (local dev)

```bash
# 1. Clone + venv
git clone https://github.com/andydiaz122/panopticon-live
cd panopticon-live
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-local.txt

# 2. Env
cp .env.example .env
# Set ANTHROPIC_API_KEY (required for the Phase 2 agent layer)

# 3. Place a tennis MP4 at data/clips/utr_match_01_segment_a.mp4 and
#    annotate the 4 court corners via tools/court_annotator.html →
#    saves to data/corners/utr_match_01_segment_a_corners.json

# 4. Run the pre-compute pipeline (~2:30 on Mac Mini M4 Pro, ~$0.30 in API spend)
python -m backend.precompute \
  --clip data/clips/utr_match_01_segment_a.mp4 \
  --corners data/corners/utr_match_01_segment_a_corners.json \
  --match-id utr_01_segment_a \
  --player-a "Player A" --player-b "Player B" \
  --db data/panopticon.duckdb \
  --out-json dashboard/public/match_data/utr_01_segment_a.json \
  --device mps --doubles-corners \
  --coach-cap 10 --design-cap 10 --beat-cap 20 --beat-period-sec 10.0

# For a fast CV-only smoke (no API cost), add --skip-agents

# 5. Start the dashboard
cd dashboard
bun install
bun run dev
# Open http://localhost:3000 — PanopticonEngine renders the cyan Player A
# skeleton overlay synchronized to video playback
```

**CLI flags worth knowing** (`python -m backend.precompute --help`):
- `--doubles-corners` — use when the court annotation traces the doubles alleys (USER-CORRECTION-026)
- `--coach-cap`, `--design-cap`, `--beat-cap` — hard budgets on agent invocations (rate-limiter safety, cost control)
- `--warmup-ms` — skip state transitions in first N ms (default 10000; GOTCHA-015)
- `--min-trigger-gap-ms` — dedupe rapid-fire transitions (default 2000; USER-CORRECTION-028)
- `--skip-agents` — CV-only mode, no API calls

## Acknowledgments

- Anthropic + Cerebral Valley for the hackathon
- Ultralytics for YOLO11m-Pose
- The UTR Tour for freely viewable professional tennis footage

## License

MIT — see [LICENSE](LICENSE).
