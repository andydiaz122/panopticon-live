# RESUME.md — New-Session Handoff

**Purpose**: point a fresh Claude Code session at everything it needs to pick up work on PANOPTICON LIVE without re-reading the full prior transcript. Read this file, then read the living docs it points to, then start.

**Project context**: Hackathon project. Anthropic × Cerebral Valley "Built with Opus 4.7" — **deadline Sunday April 26 2026 @ 8 PM EST**. Today is 2026-04-22.

---

## Strategic Frame (DECISION-009, 2026-04-22 pivot-evening) — READ FIRST

**The core value proposition is the 7 novel biometric fatigue-telemetry signals** (recovery latency, serve-toss variance, ritual entropy, crouch-depth degradation, baseline retreat, lateral work rate, split-step latency) — extracted from standard 2D broadcast pixels with ZERO hardware sensors. That's the proprietary data moat.

**The deliverable is an improved fan experience** built around those signals. Every widget ships a plain-English fan-facing label + one-line physiology explanation.

**Opus coaching is ICING, not cake.** Visual hierarchy:
1. **SignalBar stack = hero** (right rail, prominent, spring-physics motion, fan-facing copy).
2. **PlayerNameplate = identity chrome** (top-left, minimal).
3. **Video + skeleton = center** (existing).
4. **CoachPanel = subordinate footer chip** (≤88px, only when insight active).
5. **Banned**: MomentumMeter, PredictiveOverlay, PlayerNameplate@top-right (DECISION-008).

See MEMORY.md → DECISION-009 for full rationale + how-to-apply.

---

## Where we are (as of commit `e854ab5` on `main`, already on `origin/main`)

- **Phase 1 (CV pipeline)**: DONE. 7 biomechanical signals + DuckDB writer + precompute.py.
- **Phase 2 (Opus/Haiku agents)**: DONE. Coach + HUD Designer + Haiku Narrator all running OFFLINE inside `precompute.py`.
- **Phase 2.5 (Skeleton Sanitation Sprint)**: DONE. `bbox_conf >= 0.5` gate in `assign_players`; ghost-detection rate went from 55.7% to **0%**.
- **Phase 2.6 (Single-Player Pivot, DECISION-008)**: DONE. All four agent prompts + HUD layouts refactored for world-class single-player focus on Player A.
- **Phase 3 (Next.js HUD)**: **SCAFFOLD DONE, polish IN PROGRESS**. `PanopticonEngine.tsx` with rAF zero-render loop is rendering the cyan skeleton correctly.

## Known-good state at this commit

- **Tests**: `pytest tests/ -q` → 383/383 passing
- **Lint**: `ruff check backend/ tests/` → clean; `cd dashboard && bun run lint` → clean; `bunx tsc --noEmit` → clean
- **Golden data**: `dashboard/public/match_data/utr_01_segment_a.json` (V6 Crucible output) + `data/panopticon.duckdb`
- **Dev server** (may still be running from prior session): `http://localhost:3000`. To restart: `cd dashboard && bun run dev`. To kill the old one: `pkill -f "next dev"`.

## The canonical living docs — READ THESE FIRST in a new session

1. [CLAUDE.md](../CLAUDE.md) — auto-loaded; prime directive + SCOPE + hard constraints
2. [MEMORY.md](../MEMORY.md) — 30 USER-CORRECTIONs, 41 PATTERNs, 16 GOTCHAs, 8 DECISIONs. Grep this file for any term you're unsure about.
3. [FORANDREW.md](../FORANDREW.md) — plain-language decision log. Tail (last ~100 lines) has the 2026-04-22 Skeleton Sanitation Sprint + Single-Player Pivot narrative.
4. [TOOLS_IMPACT.md](../TOOLS_IMPACT.md) — what worked / what didn't, with V4↔V6 data tables.
5. [docs/ORCHESTRATION_PLAYBOOK.md](ORCHESTRATION_PLAYBOOK.md) — tool-by-phase runbook, updated for single-player scope.
6. [docs/PHASE_1_PLAN.md](PHASE_1_PLAN.md) — (historical) Phase 1 action log, useful for context on why things look the way they do.

## Hard constraints you MUST know before making changes

- **Single-player focus (DECISION-008)**: Panopticon is a world-class DEEP-DIVE on Player A. Player B is out of scope. Do NOT add `MomentumMeter`, `PredictiveOverlay`, or `PlayerNameplate@top-right`. Reason: GOTCHA-016 (YOLO11m-Pose cannot detect far-court player on broadcast clips).
- **Zero-Disk video policy**: ffmpeg stdout → numpy only. Never `cv2.VideoCapture`.
- **MPS only** (Mac Mini M4 Pro): `@torch.inference_mode()`, `torch.mps.empty_cache()` every 50 frames.
- **Pydantic v2 everywhere**: No dict crosses a module boundary.
- **React zero-render rule**: Per-frame keypoints live in `useRef` + `requestAnimationFrame` + `<canvas>` direct paint. NEVER `useState` for high-frequency data.
- **Opus 4.7 adaptive thinking**: `thinking={"type": "adaptive"}` — the old `{"type": "enabled", "budget_tokens": N}` shape is rejected with HTTP 400 (USER-CORRECTION-027).
- **bbox_conf >= 0.5 gate in assign_players**: Bimodal distribution; 0.5 is the unambiguous cutoff. Do NOT lower it (USER-CORRECTION-030).
- **Mocked SDK tests validate shape of OUR CALL, not shape API ACCEPTS** (PATTERN-038). Any API surface needs at least one integration smoke test against the real API.

## Quick sanity checks you can run

```bash
# 1. Verify clean state
cd /Users/andrew/Documents/Coding/Built_with_Opus_4-7_Hackathon
git status                    # expect: clean, on main, up to date with origin/main
git log --oneline -5          # expect: e854ab5 at top

# 2. Run tests
source .venv/bin/activate && pytest tests/ -q
# expect: 383 passed

# 3. Verify golden data present
ls -lh dashboard/public/match_data/utr_01_segment_a.json data/panopticon.duckdb

# 4. Start dashboard dev server
cd dashboard && bun run dev
# open http://localhost:3000 — should see cyan Player A skeleton tracking video
```

## What's next (biometric-signals-first, per DECISION-009)

### Phase 3 Core Trio (THIS is the current active plan — see `/Users/andrew/.claude/plans/picking-up-where-we-wobbly-crescent.md`)

Hero widget first, icing last:

1. **SignalBar + SignalRail** — THE hero. Right rail. Reads `activeHUDLayout.widgets[right-1..4]` and `activeSignalsByName`. Spring-physics fill widths (PATTERN-044). Plain-English fan-facing labels + physiology captions via `signalCopy.ts` / `.claude/skills/biometric-fan-experience/`. No Recharts (PATTERN-043). Omits sparkline in Core Trio.
2. **SensorCalibratingPlaceholder** — The 11.5s dead-air guardian (GOTCHA-017 / PATTERN-048). Rendered until `currentTimeMs ≥ matchDataRef.current.hud_layouts[0].timestamp_ms`.
3. **PlayerNameplate** — Top-left. Player A only. Minimal pill with state chip.
4. **PanopticonProvider** (foundation) — Dual-context (PATTERN-046). Single rAF loop with 10Hz-gate (PATTERN-042). Bounds-clamped frameIdx (PATTERN-045).
5. **CoachPanel** — SUBORDINATE footer chip. ≤88px tall. Typewriter via DOM mutation (PATTERN-047), `key={insight_id}` on wrapper. Only visible when insight active.

### Phase 3 follow-up (approved backlog — next plan after Core Trio lands)

- NarratorTicker (bottom bar, sync'd to `videoRef.currentTime`)
- TossTracer SVG overlay (PRE_SERVE_RITUAL only)
- FootworkHeatmap (ACTIVE_RALLY only)
- Optional: SignalBar hand-rolled `<svg><polyline>` sparkline (NOT Recharts)

### After Phase 3

- **Tab 2 (Signal Feed)**: raw JSON view, syntax highlighted, auto-scroll to current time
- **Tab 3 (Scouting Report)**: scouting-report Server Action via `@anthropic-ai/sdk` TypeScript Managed Agent (see `.claude/skills/vercel-ts-server-actions/SKILL.md`) — THE live-Opus demo moment
- **Phase 4 Vercel deploy** (Saturday): see `docs/ORCHESTRATION_PLAYBOOK.md` Phase 4
- **Phase 5 demo video** (Sunday): see `.claude/skills/hackathon-demo-director/SKILL.md`

## The exact prompt to paste into a new Claude Code session

```
Read docs/RESUME.md, then MEMORY.md (tail the last 400 lines), then
FORANDREW.md (tail the last 150 lines). Acknowledge the single-player
focus scope (DECISION-008). Then [tell me what to do next].
```

Replace `[tell me what to do next]` with the specific task. A good default is:

```
Read docs/RESUME.md, then MEMORY.md (tail the last 400 lines), then
FORANDREW.md (tail the last 150 lines). Confirm 383 tests pass and
the dev server is live. Then help me continue Phase 3 visual polish
(HUD widget library, Motion animations, typewriter CoachPanel).
```

## If the session needs deeper history

The full transcript of the prior session lives at:

```
/Users/andrew/.claude/projects/-Users-andrew-Documents-Coding-Built-with-Opus-4-7-Hackathon/5359be1a-0b17-4499-a60e-60f49c330702.jsonl
```

This is LARGE — ~100K+ lines of tool calls and reasoning. Only read specific ranges if you need to understand WHY a particular decision was made. Almost everything important is already distilled into the living docs.
