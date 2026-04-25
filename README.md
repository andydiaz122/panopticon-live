# PANOPTICON LIVE

**Clinical-grade biomechanical fatigue telemetry for pro tennis. Extracted from standard 2D broadcast pixels. No wearables. No sensors. Just pose estimation, physics, and Claude Opus 4.7.**

> Live demo: https://panopticon-live.vercel.app · 3-minute video: [YouTube](https://youtube.com) · Source: [github.com/andydiaz122/panopticon-live](https://github.com/andydiaz122/panopticon-live)

---

## TL;DR — three things that make this novel

1. **Seven biomechanical fatigue signals extracted from 2D broadcast pixels.** Recovery lag, toss precision, ritual discipline, crouch depth, court position, court coverage, reaction timing. No wearables. No mocap. Every signal physics-grounded in court meters, state-gated by a kinematic FSM, and anchored to published biomechanics literature. **Benchmarked against 2025–2026 tennis CV landscape — no prior art for broadcast-only extraction of this signal set.**

2. **Strict 3-Pass Offline DAG.** Forward YOLO11m-Pose + Kalman → RTS backward smoother → semantic state machine + signal extractors on smoothed kinematics. Empirically measured **47 % peak-velocity compression** vs. forward-only noise. Reproducible from `run_golden_data.sh` in under 3 minutes on a Mac Mini M4 Pro.

3. **Multi-Agent Trace Playback.** The Opus 4.7 Scouting Committee — Analytics Specialist → Technical Biomechanics Coach → Tactical Strategist — runs the real reasoning offline (~60 s, uses extended thinking, prompt caching, stubbed-MCP `query_video_context_mcp` tool), captures every `thinking`/`tool_call`/`handoff` event into a Pydantic-typed `AgentTrace`, and replays it client-side at baud-rate pacing. The 2030 architecture: cache the agent loop, replay at interaction time. Ship.

---

## Architecture at a glance

```
 ┌──────────────────────────────────────────────────────────────────────┐
 │                      Offline pre-compute (M4 Pro MPS)                │
 │                                                                      │
 │   ffmpeg → YOLO11m-Pose → Kalman(forward)    ▲ Pass 1 (forward)      │
 │                                              │                       │
 │                    RTS smoother ─────────────┤ Pass 2 (backward)     │
 │                                              │                       │
 │   BounceDetector → FSM → 7 signal extractors ▼ Pass 3 (semantic)     │
 │                                                                      │
 │   DuckDB  +  dashboard/public/match_data/<id>.json                   │
 │                                                                      │
 │   Scouting Committee (Opus 4.7 · extended thinking · prompt cache)   │
 │        Analytics ──► Technical Coach ──► Tactical Strategist         │
 │        query_video_context_mcp (stubbed) ───┐                        │
 │                                             ▼                        │
 │             agent_trace.json  (captured trace)                       │
 └──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼   (Vercel CDN · static JSON)
 ┌──────────────────────────────────────────────────────────────────────┐
 │                     Next.js 16 dashboard (Turbopack)                 │
 │                                                                      │
 │   Tab 1 — Live HUD  · 30 FPS canvas skeleton · SignalBars · CoachPanel│
 │   Tab 2 — Raw Telemetry · 4-kind firehose feed                       │
 │   Tab 3 — Orchestration Console · trace playback · STUB chip         │
 │                                                                      │
 │   Defense-in-depth: LoadingScreen · visibilityChange auto-pause ·    │
 │   DPR-aware ResizeObserver · Record<RallyMicroPhase> gating          │
 └──────────────────────────────────────────────────────────────────────┘
```

Every arrow is a Pydantic v2 contract. Zero dict crosses a module boundary. See [`backend/db/schema.py`](backend/db/schema.py) for the source of truth.

---

## Why now

Every sports-AI company on earth has access to the same thing we do: 30-year-old HD broadcast feeds. Two-dimensional pixels. Nothing on the athlete's body. The conventional wisdom says you need wearables or a dedicated motion-capture rig to get clinical biomechanics. We built the opposite.

YOLO11m-Pose on Apple Silicon gives us 17 COCO keypoints per detection at `conf=0.001`. A Kalman filter running on **physical court meters** (not screen pixels) smooths the jitter. A three-pass DAG with an RTS backward smoother strips 47% of peak-velocity noise on real footage. A state machine gates signal extraction to the windows where each signal is physiologically meaningful. The output is seven fatigue telemetry streams with academic literature anchoring four of them — crouch depth (PMC12298469), recovery lag (PMC12298469), toss variance (PMC12294548), lateral work rate (PMC10302430).

The sensor didn't exist. So we built it. That is the moat.

---

## What's inside

A monorepo with a Python CV + agents backend and a Next.js 16 dashboard.

- **Backend** — YOLO11m-Pose inference on Mac Mini M4 Pro MPS, a `filterpy`-backed Kalman filter with an RTS smoother pass, a 4-state kinematic state machine, 7 signal extractors each built against a Pydantic v2 contract, DuckDB as the signal store, and an Anthropic SDK wrapper driving three Opus 4.7 agents.
- **Dashboard** — Next.js 16 App Router (Turbopack), React 19, TypeScript strict mode, a 30 FPS canvas overlay on top of `<video>` with zero React re-renders per frame, three HUD tabs (Live HUD, Raw Telemetry, Orchestration Console), and a baud-rate typewriter playback for the multi-agent trace.

Architecture deep-dive: [docs/ORCHESTRATION_PLAYBOOK.md](docs/ORCHESTRATION_PLAYBOOK.md), [docs/VERCEL_DEPLOYMENT.md](docs/VERCEL_DEPLOYMENT.md).

---

## Quick start

```bash
# 1. Clone
git clone https://github.com/andydiaz122/panopticon-live
cd panopticon-live

# 2. Backend env (pre-compute machine — Mac with MPS recommended)
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-local.txt
cp .env.example .env          # set ANTHROPIC_API_KEY

# 3. Drop a pro tennis clip in data/clips/ and annotate the 4 court corners
#    via tools/court_annotator.html — saves JSON to data/corners/

# 4. Pre-compute (about 2:30 on M4 Pro, ~$0.30 in API spend)
python -m backend.precompute \
  --clip data/clips/utr_match_01_segment_a.mp4 \
  --corners data/corners/utr_match_01_segment_a_corners.json \
  --match-id utr_01_segment_a \
  --db data/panopticon.duckdb \
  --out-json dashboard/public/match_data/utr_01_segment_a.json \
  --agent-trace-json dashboard/public/match_data/agent_trace.json \
  --device mps --doubles-corners

# 5. Start the dashboard
cd dashboard
bun install
bun run dev                   # http://localhost:3000
```

For a CV-only smoke run without API spend, add `--skip-agents`. Full CLI reference: `python -m backend.precompute --help`.

---

## Repo map

```
panopticon-live/
├── backend/
│   ├── cv/                   YOLO, Kalman, state machine, RTS smoother
│   │   └── signals/          7 signal extractors, BaseSignalExtractor ABC
│   ├── db/                   DuckDB schema + Pydantic v2 contracts
│   ├── agents/               Opus 4.7 Coach, HUD Designer, Haiku Narrator,
│   │                         3-agent Scouting Committee
│   └── precompute.py         Orchestration entrypoint
├── dashboard/
│   └── src/
│       ├── app/              Next.js App Router
│       ├── components/
│       │   ├── PanopticonEngine.tsx   30 FPS canvas + rAF loop
│       │   ├── Hud/                   SignalBar, PlayerNameplate
│       │   ├── Broadcast/             Telestrator, commentary
│       │   ├── Telemetry/             Raw signal feed (Tab 2)
│       │   └── Scouting/              Orchestration Console (Tab 3)
│       └── lib/
│           ├── signalCopy.ts          Fan-facing label table (source of truth)
│           └── types.ts               TS mirror of Pydantic contracts
├── tests/                    434 pytest + 82 vitest = 516 total
├── docs/                     Architecture, deploy, storyboard
└── .claude/
    ├── skills/               Project-scoped skill team
    └── agents/               Specialized review + build agents
```

---

## The 7 signals

Every signal is state-gated, physics-grounded, and maps to a fan-facing label. Copy is canonical in [`dashboard/src/lib/signalCopy.ts`](dashboard/src/lib/signalCopy.ts).

| Signal (dev name) | Fan label | What it measures | Literature anchor |
|---|---|---|---|
| `recovery_latency_ms` | Recovery Lag | Time Player A takes to return to ready stance after shots. Elite fresh: <800 ms; fatigued: 800 ms+. | PMC12298469 (wrist velocity decline) |
| `serve_toss_variance_cm` | Toss Precision | Vertical scatter of Player A's ball toss at apex. Variance above 8 cm correlates with serve accuracy breakdown. | PMC12294548 (toss variance → serve error) |
| `ritual_entropy_delta` | Ritual Discipline | Spectral consistency of Player A's pre-serve movements — rising signals routine breaking down under load. | PMC8312934 (motor-variability indirect) |
| `crouch_depth_degradation_deg` | Crouch Depth | Loss of knee flexion in Player A's ready position — the primary marker of lower-limb fatigue. | PMC12298469 (#1 fatigue marker) |
| `baseline_retreat_distance_m` | Court Position | Player A's court position behind the baseline — tracks positioning adaptations as match demands accumulate. | PMC12069318 (tactical adaptation) |
| `lateral_work_rate` | Court Coverage | Player A's peak lateral velocity per rally — tracks court coverage capacity and agility under load. | PMC10302430 (agility decline post-fatigue) |
| `split_step_latency_ms` | Reaction Timing | Player A's movement burst timing relative to serve-bounce detection — delays signal neuromuscular slowing. | Novel (structurally first-of-kind) |

Scope note (DECISION-008): we deliberately target Player A — the near-court athlete YOLO can reliably detect on broadcast footage. Moneyball for tennis. One player, forensic depth. See [MEMORY.md](MEMORY.md) GOTCHA-016 for the CV detector-capacity rationale.

### Match-state gating (the CAPS terms you'll see in Tab 2)

Signals don't fire constantly — they fire when the player is in the **right phase** of a point. We track three states per player:

| State | What it means | Why signals gate on it |
|---|---|---|
| `PRE_SERVE_RITUAL` | Player is at the baseline, bouncing the ball, setting up to serve (or returner setting their stance). | Toss precision + ritual discipline only fire here — measuring pre-serve mechanics mid-rally is meaningless. |
| `ACTIVE_RALLY` | A point is in play — player is moving, hitting, covering court. | Lateral work rate, recovery lag, split-step reaction, crouch depth all fire here. |
| `DEAD_TIME` | Between points — toweling off, walking to position, reset. | No signal fires here; it's the quiet window that separates rallies. |

Transitions between states drive the signal pipeline. The raw telemetry feed in Tab 2 shows every transition inline with signal emissions, e.g., `PRE_SERVE_RITUAL → ACTIVE_RALLY  lateral_work_rate: 2.14`.

---

## The Multi-Agent Swarm

Panopticon's Opus 4.7 showcase is a three-agent Scouting Committee with real tool use, real extended thinking, and real handoffs. Each agent owns an orthogonal lens — the same division of labor a human quant desk uses.

| Agent | Lens | Tools | Input |
|---|---|---|---|
| **Analytics Specialist** | Statistical anomalies in the 7 signal arrays | DuckDB read-only (`get_signal_window`, `compare_to_baseline`, `get_rally_context`, `get_match_phase`) | Raw signal schema + match ID |
| **Technical Biomechanics Coach** | Physical-breakdown narrative grounded in biomech literature | None (grounded in `BIOMECH_PRIMER` system prompt) | Analytics Specialist's anomaly list |
| **Tactical Strategist** | Match-strategy exploit (Vulnerability / Exploit Pattern / Watch Window) | None (pure synthesis) | Technical Coach's causal narrative |

Handoffs cascade. Agent N+1's user message contains agent N's OUTPUT plus a shared-blackboard baseline context — PATTERN-059. This prevents the Coach from hallucinating biomech claims unconstrained by raw data.

The real reasoning loop runs 45–60 seconds. Vercel serverless functions die at 15. So we built **Offline Trace Playback**: capture every `thinking` block, `tool_call`, `tool_result`, and `handoff` during `precompute.py` into a Pydantic-typed `AgentTrace` (discriminated union), write it to `dashboard/public/match_data/agent_trace.json`, and replay it client-side at baud-rate pacing (~25 chars/sec) with `[>> 4× SPEED]` scrub controls. Banner: *"ARCHITECTURAL PREVIEW: SWARM ACCELERATED FOR DEMO."* Honest disclosure, not a mock.

This is the 2030 architecture. Cache the agent-loop. Replay at interaction time. Ship.

Code: [`backend/agents/scouting_committee.py`](backend/agents/scouting_committee.py), [`backend/agents/system_prompt.py`](backend/agents/system_prompt.py), [`dashboard/src/components/Scouting/OrchestrationConsoleTab.tsx`](dashboard/src/components/Scouting/OrchestrationConsoleTab.tsx).

---

## Engineering craft

- **Tests: TypeScript 96 / Python 434+.** Zero regressions across Phase 2-6 refactors (display-only authoring, G10 dynamic identity injection, Phase A4.5 exhaustive gating).
- **TypeScript strict mode clean.** `next build` compiles in 1327 ms (Next.js 16.2.4 + Turbopack).
- **Strict 3-Pass DAG** (PATTERN-055). Pass 1: ffmpeg stdout → YOLO → forward Kalman. Pass 2: RTS backward smoother. Pass 3: state-machine + signal extraction on smoothed kinematics. Empirically measured **47% peak-velocity compression** vs forward-only noise on `utr_match_01_segment_a.mp4` (60s, 1800 frames).
- **Kalman filter on physical court meters**, not normalized pixels (USER-CORRECTION-008). Homography transforms pixel space → court plane before any kinematic claim is made.
- **Zero-Disk video policy.** `ffmpeg` stdout → `io.BytesIO` → YOLO. No `cv2.VideoCapture` from disk.
- **React 30-FPS defense.** Per-frame keypoints → `useRef` + `requestAnimationFrame` + `<canvas>` direct paint. Zero React re-renders per frame. See [`.claude/skills/react-30fps-canvas-architecture/SKILL.md`](.claude/skills/react-30fps-canvas-architecture/SKILL.md).
- **MPS safeguards.** `@torch.inference_mode()`, `torch.mps.empty_cache()` every 50 frames, graceful `torch.mps.MemoryError` handling, single-worker asyncio executor.
- **Pydantic v2 at every module boundary.** No dict ever crosses between modules. Schema: [`backend/db/schema.py`](backend/db/schema.py).
- **Bifurcated requirements.** `requirements-local.txt` (torch, ultralytics, opencv) for pre-compute; `requirements-prod.txt` (fastapi, anthropic, duckdb) for Vercel's 250 MB serverless limit.

Living docs: [CLAUDE.md](CLAUDE.md) (constraints), [FORANDREW.md](FORANDREW.md) (decision log), [MEMORY.md](MEMORY.md) (gotchas + patterns), [TOOLS_IMPACT.md](TOOLS_IMPACT.md) (ROI).

---

## Who buys this

- **Broadcasters.** Every match feels like Game 7. Live fatigue chyrons, anomaly callouts, clutch-moment detection. The HUD is broadcast-grade visual intelligence the network can run itself.
- **Sports betting syndicates.** The raw signal feed is a live edge. Biomechanical fatigue is a leading indicator that closing odds have not priced in — 46 signal emissions per minute on a real UTR clip, each one a tick a model can consume.
- **Elite coaching and player operations.** Post-match opponent scouting. Pre-match preparation briefs. Forensic breakdowns of one opponent's biomechanics over a full season — Moneyball for tennis.

Same physics engine. Three surfaces. Three revenue streams.

---

## Credits

Solo-built by [Andrew Diaz](https://andrewdiaz.io) with Claude Code for the Anthropic × Cerebral Valley *Built with Opus 4.7* hackathon (April 21–26, 2026).

MIT licensed — see [LICENSE](LICENSE).

Acknowledgments: Ultralytics for YOLO11m-Pose, the `filterpy` maintainers for the Kalman + RTS implementation, Anthropic for Opus 4.7 + extended thinking + tool use, the UTR Tour for freely viewable professional tennis footage.
