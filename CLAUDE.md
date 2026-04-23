# CLAUDE.md — PANOPTICON LIVE (Hackathon Project)

**Project**: Panopticon Live — 2K-Sports-style video-game HUD for pro tennis, powered by Opus 4.7.
**Event**: Anthropic × Cerebral Valley "Built with Opus 4.7" virtual hackathon.
**Deadline**: Sunday April 26, 2026 @ 8:00 PM EST.
**Owner**: Andrew Diaz (solo). Co-built with Claude Code.

---

## THE PRIME DIRECTIVE

**Win the Demo criterion (25%) + Opus 4.7 Use criterion (25%) with visible craft.** Judges evaluate a 3-minute video. The demo IS the product. We optimize for visual "cool factor," creative Opus usage (generative UI + visible extended thinking + Managed Agents), and engineering craft. We DO NOT optimize for predictive accuracy or backtest R² — that is the wrong attack vector in a time-boxed event.

## CORE VALUE PROPOSITION (DECISION-009, 2026-04-22)

**Panopticon Live's differentiating value is the NOVEL BIOMETRIC DATA nobody else is extracting from standard 2D broadcast pixels.** The 7 biomechanical fatigue-telemetry signals — recovery latency, serve-toss variance, ritual entropy, crouch-depth degradation, baseline retreat, lateral work rate, split-step latency — are a proprietary data moat, not a cool-factor feature. The deliverable is **an improved fan experience** built around those signals. Opus coaching is ICING, not cake. Visual hierarchy rule: SignalBar is the hero widget, PlayerNameplate is identity chrome, CoachPanel is a subordinate footer chip, and every signal ships a plain-English fan-facing label + one-line physiology caption. See DECISION-009 in MEMORY.md.

## SCOPE: SINGLE-PLAYER DEEP-DIVE (DECISION-008, 2026-04-22)

Panopticon Live is a WORLD-CLASS SINGLE-PLAYER biomechanics intelligence system targeting Player A (the near-court player). The "Moneyball for tennis" angle — deep forensic analysis of ONE pro player — is a stronger demo story than shallow two-player coverage, and matches our CV detector's effective resolution on broadcast tennis clips (GOTCHA-016: YOLO11m-Pose cannot reliably detect the small, partially-occluded far-court player). Any widget, prompt, or signal that depends on Player B data (MomentumMeter, PredictiveOverlay, split_step_latency_ms) is explicitly out of scope. Commit fully to the narrow scope — no half-hearted "kinda still supports both" implementations.

## HARD CONSTRAINTS (rule-based)

1. **New Work Only** — Every line of code in this repo is written during the hackathon (Apr 21–26). **No copy-paste from `Alternative_Data`.** We implement patterns fresh using public libraries (`ultralytics`, `filterpy`, `scipy`, `opencv-python`, `duckdb`, `anthropic`, `fastapi`).
2. **Open Source, MIT license** — Everything shown in the demo must be open source.
3. **Mac Mini M4 Pro MPS ONLY** — No CUDA. Strict MPS safeguards mandatory (see below).
4. **Zero-Disk Video Policy** — ffmpeg stdout → `io.BytesIO` → YOLO input. NO `cv2.VideoCapture` reading from disk.
5. **Bifurcated Requirements** — `requirements-local.txt` (torch, ultralytics, etc.) for pre-compute; `requirements-prod.txt` (fastapi, anthropic, duckdb) for Vercel. Vercel 250MB limit is a hard wall.
6. **Pydantic v2 for ALL inter-module data contracts** — No dict hallucinations. Every interface is a Pydantic model.
7. **ABORTED: Batch 11 ML Forge** — Do NOT build merge_asof matrices, CatBoost targets, Spearman heatmaps, or predictive models. The Omni-Brain handoff doc from `Alternative_Data` included those instructions; they are explicitly cancelled for this project.

## MANDATORY MPS SAFEGUARDS

Every YOLO inference path must include:
- `@torch.inference_mode()` decorator on inference functions
- `torch.mps.empty_cache()` every 50 frames (prevents unified-memory accumulation)
- YOLO `conf=0.001` (captures occluded players)
- YOLO `imgsz=1280` (accuracy/speed balance)
- Single-worker asyncio executor (MPS is not reentrant-safe)
- Graceful `torch.mps.MemoryError` handling — drop frame, continue, never crash

## REACT ARCHITECTURE RULES

1. **Keypoints NEVER go into `useState`.** Per-frame keypoints → `useRef<KeypointFrame>()` + `requestAnimationFrame` loop that paints `<canvas>` directly. The SSE handler writes into the ref. Zero React renders per video frame.
2. **Normalized coords from backend.** Every pixel coord divided by frame width/height to `[0.0, 1.0]` BEFORE writing to DuckDB. Frontend multiplies by `<video>.clientWidth/Height` at paint time.
3. **`ResizeObserver` on video element** — keeps canvas dimensions aligned when window resizes.
4. **React state ONLY for low-frequency updates** — match phase, Opus commentary chunks, HUD layout changes, anomalies. Max ~1 update/sec into state.
5. **Canvas overlay** — `position: absolute; inset: 0` over the `<video>`. `width`/`height` attributes from ResizeObserver, not CSS.

## SKILL TEAM (project-scoped, in `.claude/skills/`)

Orthogonal ownership mirrors a professional team:

| Skill | Owns | Delegates |
|---|---|---|
| `cv-engineer` | YOLO inference, Kalman, state machine, 7 signal extractors, DuckDB schema | Agent orchestration, frontend, deployment |
| `agent-orchestrator` | Opus Coach/Designer/Narrator, Managed Agents, prompt caching, tool schemas | CV internals, React, deploy |
| `hud-auteur` | 2K-Sports visual language, HUD widgets, rAF canvas loop, Motion animations | Backend code, CV, Opus prompts |
| `verification-gate` | TDD tests, eval harness, multi-agent review panels, Vercel deploy verification | Feature code, design |
| `demo-director` | 3-min video storyboard, narrative pacing, OBS recording, submission QA | Everything technical |

## ORCHESTRATION PLAYBOOK

See [docs/ORCHESTRATION_PLAYBOOK.md](docs/ORCHESTRATION_PLAYBOOK.md) — master runbook mapping every skill/agent/MCP to the phase where it fires.

## LIVING DOCS (update every session)

- **[FORANDREW.md](FORANDREW.md)** — plain-language decision log, bug journal, lessons learned
- **[TOOLS_IMPACT.md](TOOLS_IMPACT.md)** — tool usage ROI + "Skills NOT Used" section
- **[MEMORY.md](MEMORY.md)** — structured learnings for cross-session recall
- **[docs/ORCHESTRATION_PLAYBOOK.md](docs/ORCHESTRATION_PLAYBOOK.md)** — tool-by-phase runbook

## COMMANDS THAT FIRE AUTOMATICALLY

- Any code change → `python-reviewer` or `typescript-reviewer` agent
- Any new module → `/tdd` workflow (write tests first)
- Pre-deploy → `/verify pre-pr` + multi-agent review panel (orthogonal: `code-reviewer` + `security-reviewer` + `vercel:react-best-practices` + `python-reviewer`)
- End of day → `/save-session` + update `MEMORY.md`
- Pre-submission → `/go` finishing workflow

## LOGGING DISCIPLINE (Citadel-level)

Every non-obvious learning → logged immediately to the right file:
- Hit a macOS tooling trap? → `MEMORY.md` under "Gotchas"
- Discover a tool's ROI? → `TOOLS_IMPACT.md`
- Pattern worth a skill? → `/skill-creator` → `.claude/skills/`
- User correction → append to this file + `MEMORY.md`

**Mistakes only compound value if recorded.**

## DELIVERABLES (due Sun 8pm EST)

1. YouTube 3-min demo video (unlisted or public)
2. Public GitHub repo `panopticon-live` (MIT license)
3. Written summary (100-200 words) via CV submission platform
