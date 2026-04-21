# PANOPTICON LIVE

**A 2K-Sports-style video-game HUD for professional tennis, powered by Claude Opus 4.7.**

Built for the Anthropic × Cerebral Valley **Built with Opus 4.7** virtual hackathon — April 21-26, 2026.

[Live demo](https://panopticon-live.vercel.app) (TBD) · [3-min demo video](https://youtube.com) (TBD) · MIT licensed

---

## What it does

Panopticon Live ingests a professional tennis match video, extracts seven biomechanical fatigue signals from broadcast-quality pose estimation, and renders the match as a **live video-game-style HUD**:

- **Skeleton overlay** tracing both players frame-by-frame
- **Pulsing signal bars** — fatigue, power, footwork, ritual stability — that animate when a player deviates from their match-opening baseline
- **Opus 4.7 Coach panel** — streaming coach-register commentary with visible `extended_thinking` tokens
- **Generative HUD layout** — Opus 4.7 re-designs the overlay in real time as the match state changes
- **Signal Feed** (2nd tab) — raw JSON stream, the B2B product surface for prediction-market infrastructure (Valence, Sequence, Dome)
- **Scouting Report** (3rd tab) — Claude Managed Agent generates a full PDF report on demand

## Why it matters

Nobody extracts biomechanical fatigue signals from free broadcast video today. The sensor doesn't exist — until you build it. Panopticon Live is both a judge-facing visual showcase AND the foundation of a B2B signal-feed product aimed at the prediction-market infrastructure layer.

## Architecture

```
Video (MP4)
  → ffmpeg stdout (BGR24 pipe, Zero-Disk)
  → YOLO11m-Pose on Apple MPS (17 COCO keypoints per player)
  → Kalman 2D smoothing (filterpy) + spike suppression
  → 3-state kinematic state machine (PRE_SERVE_RITUAL / ACTIVE_RALLY / DEAD_TIME)
  → 7 biomechanical signal extractors (state-gated)
  → DuckDB (pre-computed panopticon.duckdb)
  → FastAPI SSE replay at video wallclock
  → Claude Opus 4.7 (Reasoner + Designer + Voice) + Haiku 4.5 (Narrator) + Managed Agent (Scouting)
  → Next.js 16 dashboard on Vercel (Tab 1 HUD, Tab 2 Signal Feed, Tab 3 Scouting Report)
```

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
# Set ANTHROPIC_API_KEY for Phase 2+ agent work

# 3. Pre-compute one clip to DuckDB (requires ~60s of MP4 in data/clips/)
python -m scripts.probe_clip \
  --clip data/clips/utr_match_01_segment_a.mp4 \
  --out data/probe_out.parquet

# 4. (once Phase 2 lands) Start the backend
uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000

# 5. (once Phase 3 lands) Start the dashboard
cd dashboard
bun install
bun run dev
```

## Acknowledgments

- Anthropic + Cerebral Valley for the hackathon
- Ultralytics for YOLO11m-Pose
- The UTR Tour for freely viewable professional tennis footage

## License

MIT — see [LICENSE](LICENSE).
