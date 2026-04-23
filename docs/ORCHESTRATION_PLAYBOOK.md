# ORCHESTRATION PLAYBOOK — Master Runbook

The tool-by-phase orchestration map for winning this hackathon. Every skill, agent, MCP, and slash command has a specific phase where it fires. This is the "when do we use what" reference.

**Principle:** Use tools intelligently and orthogonally. Chain them. Avoid redundancy and diminishing returns. Measure ROI in `TOOLS_IMPACT.md`.

---

## The 5 Orthogonal Skills (project-scoped in `.claude/skills/`)

They form a "virtual team" where each member owns one domain:

```
         ┌─────────────────────────────────────────────────┐
         │         HACKATHON DEMO (Sun 8pm EST)            │
         └─────────────────────┬───────────────────────────┘
                               │
     ┌─────────────────────────┼─────────────────────────┐
     │                         │                         │
     ▼                         ▼                         ▼
┌──────────┐             ┌──────────┐             ┌──────────────┐
│cv-engineer│ produces → │ DuckDB   │ ← consumes │agent-         │
│           │   signals  │(sidecar) │  signals    │orchestrator  │
└──────────┘             └────┬─────┘             └──────┬───────┘
                              │                           │
                              │  (replay via SSE)         │  (commentary +
                              │                           │   HUD layout JSON)
                              ▼                           ▼
                     ┌────────────────────────────────────────┐
                     │          hud-auteur                    │
                     │  (2K-Sports frontend + rAF canvas)     │
                     └────────────────┬───────────────────────┘
                                      │
                     ┌────────────────┴───────────────────────┐
                     │                                        │
                     ▼                                        ▼
              ┌─────────────┐                         ┌──────────────┐
              │verification-│                         │demo-director │
              │gate         │                         │              │
              └─────────────┘                         └──────────────┘
              (tests + deploy)                        (video + submit)
```

---

## Phase 0 — Today (Tue Apr 21) — Scaffolding & Meta-Setup

**Owner**: `verification-gate` + `cv-engineer`

**Activities:**
- Create repo, LICENSE, CLAUDE.md, FORANDREW.md, MEMORY.md, TOOLS_IMPACT.md, this playbook
- Bifurcated `requirements-local.txt` + `requirements-prod.txt`
- `pyproject.toml`, `config.py`, Pydantic schemas
- Project-scoped skills in `.claude/skills/` — the 5-orthogonal-team
- Build `scripts/probe_clip.py` (YOLO on real UTR clip)
- Build `tools/court_annotator.html`
- Go/No-Go gate: run probe on utr_match_01_ANCHOR_OK.mp4 segment

**Tools that fire:**
- `Explore` agent (already used 3x in parallel Apr 21 planning)
- `Plan` agent (already used 1x for architecture validation)
- `perplexity_ask` — biomechanical thresholds seeding system prompt
- `context7` — Ultralytics + Anthropic SDK current API
- `python-reviewer` agent — on probe_clip.py, config.py
- `TodoWrite` — task tracking

**Skills that fire:**
- `python-patterns` — idiomatic Python 3.12
- `search-first` — library/tool reuse before writing

**Exit criterion:** One UTR clip segment produces valid YOLO keypoints + court-corner JSON exists. Commit to GitHub.

---

## Phase 1 — Wed Apr 22 — CV Pre-Compute Pipeline

**Owner**: `cv-engineer`

**Activities:**
- `backend/cv/pose.py` — YOLO11m-Pose async wrapper with MPS safeguards
- `backend/cv/kalman.py` — 2D Kalman tracker via `filterpy`
- `backend/cv/state_machine.py` — 3-state per-player FSM
- `backend/cv/biomechanics.py` — posture, COM, torso scalar
- `backend/cv/homography.py` — court-corner → court-meters
- `backend/cv/signals/*.py` — 7 signal modules (each ≤100 LOC, TDD)
- `backend/db/schema.py` — DuckDB tables via Pydantic schemas
- `backend/precompute.py` CLI — clip → DuckDB

**Tools that fire:**
- `/devfleet` — parallelize 7 signal implementations in orthogonal worktrees
- `/tdd` — test-first for every signal file
- `tdd-guide` agent — TDD enforcement
- `python-reviewer` + `python-testing` skill — after every module
- `context7` — `scipy.signal.lombscargle`, `filterpy.kalman.KalmanFilter`, `opencv-python`
- `perplexity_ask` (1-2 calls) — validate ritual_entropy Lomb-Scargle parameters
- `/code-review` — at end of day on the full CV package
- `code-simplifier` agent — before commit (simplify newly written code)

**Skills that fire:**
- `python-testing-patterns` — TDD workflow
- `python-patterns` — idiomatic Python
- `content-hash-cache-pattern` — DuckDB cache key per clip SHA-256
- `long-running-tasks` — if precompute exceeds 2 min

**Exit criterion:** `python -m backend.precompute --clip data/clips/utr_01_seg_a.mp4 --corners data/corners/utr_01_seg_a.json` produces full DuckDB row set with 7 non-None signals during ACTIVE_RALLY. Unit tests pass with ≥80% coverage.

---

## Phase 2 — Thu Apr 23 — Opus Agents (REVISED per USER-CORRECTIONs 002, 006)

**Owner**: `opus-coach-architect`

**Activities (OFFLINE Python, runs inside `precompute.py`):**
- `backend/agents/tools.py` — deterministic signal-query tool schemas (Python, for offline use)
- `backend/agents/system_prompt.py` — 5-10K biomech primer (seeded from Perplexity citations)
- `backend/agents/opus_coach.py` — Opus 4.7 Reasoner pre-computes `CoachInsight` records tagged `timestamp_ms`
- `backend/agents/hud_designer.py` — Opus 4.7 Designer pre-computes `HUDLayoutSpec` records tagged `timestamp_ms`
- `backend/agents/haiku_narrator.py` — Haiku 4.5 pre-computes per-second `NarratorBeat` records

**Activities (LIVE on Vercel TypeScript, Phase 3+4):**
- `dashboard/app/actions/scouting-report.ts` — Next.js Server Action using `@anthropic-ai/sdk`
- `dashboard/app/api/scouting-report-status/route.ts` — polling endpoint for long-running Managed Agent
- See `vercel-ts-server-actions` skill for canonical implementation

**Activities REMOVED (cancelled per USER-CORRECTION-006):**
- ~~`backend/api/stream.py`~~ — no FastAPI SSE at runtime
- ~~`backend/api/agents.py`~~ — no Python agent endpoints on Vercel
- ~~`requirements-prod.txt`~~ — Python vanished from Vercel deploy

**Tools that fire:**
- `claude-api` skill — prompt caching + extended thinking patterns
- `vercel:ai-gateway` skill — model routing via AI Gateway
- `context7` — `/anthropics/anthropic-sdk-python` (thinking, streaming, tool use)
- `perplexity_research` (1 call) — Claude Managed Agents latest patterns for long-running tasks
- `mcp-server-patterns` skill — IF we decide to expose the biomech tools as an MCP (stretch)
- `security-reviewer` agent — on the API endpoints (secret handling, rate limits)
- `python-reviewer` agent — on every agent file

**Skills that fire:**
- `cost-aware-llm-pipeline` — Opus vs Haiku routing decisions
- `agent-harness-construction` — structuring the tool set for max Opus reasoning quality

**Exit criterion:** Given a 10-sec window on utr_01_seg_a, Opus returns structured JSON response in <10s (with cache hit), Haiku streams 1 beat/sec, SSE endpoint streams DuckDB rows at wallclock pace. Extended thinking tokens visible in response.

---

## Phase 3 — Fri Apr 24 — 2K-Sports Frontend HUD

**Owner**: `hud-auteur`

**Scope note (DECISION-008, 2026-04-22)**: Single-player deep-dive on Player A.
Player B widgets (MomentumMeter, PredictiveOverlay, top-right nameplate) are
EXPLICITLY OUT OF SCOPE — GOTCHA-016 documents the detector-capacity limit.

**Activities:**
- `dashboard/` — Next.js 16 App Router scaffolded with Bun (DONE, commit `e702afd`)
- Tab 1 (Broadcast): `<video>` + cyan canvas skeleton (Player A only) + HUD widgets + CoachPanel
- Tab 2 (Signal Feed): raw JSON with syntax highlighting (Player A signals)
- Tab 3 (Scouting Report): button → Managed Agent → PDF (deep single-player analysis)
- Normalized-coord rAF rendering via `useRef` + `ResizeObserver` (DONE, `PanopticonEngine.tsx`)
- Single-player HUD widgets: `PlayerNameplate@top-left`, `SignalBar@right-1..4`, `TossTracer@center-overlay` (PRE_SERVE), `FootworkHeatmap@center-overlay` (RALLY)
- Motion animations: pulsing signal bars, HUD slide-in, typewriter commentary
- Opus thinking tokens in collapsible panel
- Visible quantitative anchors in coach commentary (from V6: "A's baseline_retreat collapsed 1.67m → 0.10m")

**Tools that fire:**
- `figma` MCP — iterate on HUD visual spec with Opus 4.7 design muscle
- `vercel:shadcn` — install component primitives
- `vercel:nextjs` — App Router / SSE patterns
- `vercel:react-best-practices` skill — code review
- `awwwards-animations` skill — Motion + GSAP patterns
- `top-design` skill — aesthetic polish
- `frontend-design` skill — Tailwind + design tokens
- `liquid-glass-design` — if we want a glass overlay feel
- `Claude_in_Chrome` MCP — live browser QA during dev
- `Claude_Preview` MCP — quick snapshot previews
- `typescript-reviewer` agent — after every .tsx component
- `/e2e` — Playwright regression after each major component
- `e2e-runner` agent — automation

**Skills that fire:**
- `frontend-patterns` — React architecture
- `nextjs-turbopack` — bundler config
- `coding-standards` — TypeScript/JS/React best practices

**Exit criterion:** Localhost dashboard plays utr_01_seg_a with skeleton overlay + 3 signal bars + Opus commentary typewriter + JSON feed tab. Zero React-state re-renders per keypoint frame (verified via React DevTools Profiler).

---

## Phase 4 — Sat Apr 25 — Deploy, Polish, Second Clip

**Owner**: `verification-gate` + `hud-auteur`

**Activities:**
- Process utr_match_05_ANCHOR_OK segment — DuckDB sidecar
- Match selector UI
- `vercel.ts` config — Python Fluid Compute + Next.js
- `/vercel:deploy` preview → QA → `/vercel:deploy prod`
- Vercel Blob for clip assets
- Final design polish on HUD
- README.md with architecture diagram + live URL

**Tools that fire:**
- `/vercel:bootstrap` — verify Vercel resources
- `/vercel:env` — production env var sync
- `/vercel:deploy` — preview then prod
- `/vercel:verification` — full-story check (browser → API → Opus → DuckDB)
- `/vercel:status` — deployment monitoring
- `vercel:deployments-cicd` skill — CI/CD troubleshooting if needed
- **Multi-agent review panel (orthogonal lenses)**:
  - `code-reviewer` (general quality)
  - `security-reviewer` (attack surface, API keys, CORS)
  - `vercel:react-best-practices` (frontend-specific)
  - `python-reviewer` (backend-specific)
- `/verify` — build + tests + coverage pre-deploy
- `e2e-runner` — automated regression on production URL
- `doc-updater` agent — generates README / architecture diagram

**Skills that fire:**
- `vercel:deployments-cicd`
- `vercel:vercel-functions` — Python Fluid Compute
- `vercel:env-vars` — ANTHROPIC_API_KEY, DUCKDB_PATH
- `deployment-patterns`

**Exit criterion:** Production URL live. Multi-agent panel reports no CRITICAL or HIGH findings. `/vercel:verification` passes. README public.

---

## Phase 5 — Sun Apr 26 — Demo Record & Submit (8pm EST deadline)

**Owner**: `demo-director`

**Activities:**
- Storyboard: 5 scenes × ~30-45s each
- OBS setup + multi-scene switching
- Record 2 rehearsal takes + 1 final take
- Edit in ffmpeg or DaVinci Resolve Lite
- YouTube upload (unlisted recommended; public if comfortable)
- Write 100-200 word summary
- Submit via CV platform
- Post to X + LinkedIn

**Tools that fire:**
- `computer-use` MCP — OBS scene control (if needed)
- `Claude_in_Chrome` MCP — record browser sequences via extension
- `frontend-slides` skill — title cards / intro frame
- `social-content` skill — X and LinkedIn posts
- `article-writing` skill — written summary (100-200 words)
- `gh` CLI — repo finalization (release tag, stars if any, etc.)
- `/go` — final ship workflow on any remaining commits

**Skills that fire:**
- `video-editing` — ffmpeg / DaVinci patterns
- `content-engine` — platform-native content adaptation

**Exit criterion:** YouTube link + GitHub public + 100-200 word summary submitted via CV platform by 8:00 PM EST. Submission confirmation screenshot in FORANDREW.md.

---

## Meta-Phase — Throughout All Week

**Continuous observation & learning:**

| Tool | Cadence | Output |
|---|---|---|
| `continuous-learning-v2` | Every Claude Code session | Instincts extracted to `.claude/instincts/` |
| `MEMORY.md` updates | After every gotcha | Cross-session recall |
| `TOOLS_IMPACT.md` updates | End of each day | Tool ROI tracking |
| `/save-session` | EOD daily | Session snapshot to ~/.claude/sessions/ |
| `/checkpoint` | Mid-day stable points | Recovery points |
| `/context-budget` | If context approaches 150K tokens | Audit bloat |
| `/skill-create` | If reusable pattern emerges | New project skill |
| `/harness-optimizer` | Pre-phase-transition | Tune agent harness for next phase |
| `/rules-distill` | Mid-week | Distill cross-cutting principles from skills |

---

## Parallel Execution Rules

- **ALWAYS parallelize independent tool calls.** When launching multiple file writes, research queries, or agent invocations that don't depend on each other, use ONE message with multiple tool-use blocks.
- **NEVER parallelize dependent tasks.** If task B needs task A's output, run A first.
- **ALWAYS verify agent outputs.** Trust but verify — read the file the agent wrote.
- **DEFAULT to `Explore` agent subtype** for open-ended research. DEFAULT to `Plan` agent subtype for design validation.
- **Multi-agent review panel** requires ORTHOGONAL lenses. Don't run 3 `code-reviewer` agents — run 1 `code-reviewer` + 1 `security-reviewer` + 1 domain-specific reviewer.

## Quality Gates (non-negotiable)

| Gate | Criterion | Blocker if fails? |
|---|---|---|
| Phase 0 exit (Day-0 Go/No-Go) | YOLO produces stable keypoints on 1 real UTR clip | YES — triggers Alt Framing A |
| Phase 1 exit | 7 signals non-None during ACTIVE_RALLY, tests pass, coverage ≥80% | YES — blocks Phase 2 |
| Phase 2 exit | Opus returns in <10s with cache hit, SSE streams correctly | YES — blocks Phase 3 |
| Phase 3 exit | Localhost dashboard works end-to-end, zero per-frame React renders | YES — blocks Phase 4 |
| Phase 4 exit | Production URL passes `/vercel:verification`, multi-agent panel clean | YES — blocks submission |
| Phase 5 exit | Submission confirmed by 8pm EST | YES — hackathon deadline |

## If Behind Schedule (graceful degradation)

1. **First cut:** Haiku narrator (Opus alone narrates)
2. **Second cut:** Managed Agent scouting report (inline coach commentary only)
3. **Third cut:** Second match clip (ship one hero clip)
4. **Fourth cut:** HUD generative UI (static layout, keep reasoner + signal bars)
5. **Fifth cut:** Fatigue divergence chart
6. **Minimum Viable Demo:** 1 clip + skeleton + 3 pulsing signal bars + Opus typewriter + Signal Feed JSON tab

## Citadel-Level Security Discipline

- Never use arbitrary-code-evaluation functions on untrusted data (we use no user-submitted code)
- Parameterized DuckDB queries (`?` placeholders) — never string interpolation for SQL
- All HTTP requests have `timeout=` explicitly
- `ANTHROPIC_API_KEY` via env var only, never committed
- No dict hallucinations — Pydantic v2 at every module boundary
- Multi-agent review panel before production deploy
- Log every non-obvious learning to `MEMORY.md` immediately
