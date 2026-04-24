# PHASE 6 — Team-Lead Handoff (Demo Production Sprint)

**Project**: PANOPTICON LIVE — Anthropic x Cerebral Valley "Built with Opus 4.7" Hackathon
**Branch**: `hackathon-demo-v1`
**Working directory**: `/Users/andrew/Documents/Coding/hackathon-demo-v1`
**Leg dates**: 2026-04-24 (Phase 6 kickoff + dialectical steelman, ~7 h wall-clock)
**Author (agent)**: Claude Opus 4.7 (1M context)
**Human architect**: Andrew Diaz (solo)
**Document purpose**: Context + narrative + focus ahead for a cold-reading team lead. The operational timeline (storyboard beats, Sat/Sun hour-by-hour build, submission checklist) is handed off separately — this file does not duplicate it.

---

## 1. Project Identity

PANOPTICON LIVE is a 2K-Sports-style video-game HUD for pro tennis powered by Claude Opus 4.7. It was built for the Anthropic x Cerebral Valley "Built with Opus 4.7" virtual hackathon (April 21–26, 2026). Submission is due **Sunday 2026-04-26 @ 8:00 PM EST**. Andrew Diaz is the solo architect; the codebase was co-built with Claude Code. Core differentiator: seven novel biomechanical fatigue-telemetry signals extracted from standard 1080p broadcast pixels — a proprietary data moat, with Opus commentary riding as icing on top of that moat (DECISION-009).

---

## 2. Where the Project Stands Right Now

The project is **approximately 90% demo-ready.** PR #4 (anomaly injection, TelemetryLog refactor, Vercel production deploy fix) is merged into `main`. PR #5 (Phase 5 postmortem + Phase 6 planning docs) is open on `hackathon-demo-v1` with non-code documentation only. A stable production deployment is live on Vercel, serving three dashboard tabs: **Tab 1 — Live HUD**, **Tab 2 — Raw Telemetry**, **Tab 3 — Opus Scouting Report**. All seven biomechanical signals (`recovery_latency`, `serve_toss_variance`, `ritual_entropy`, `crouch_depth_degradation`, `baseline_retreat`, `lateral_work_rate`, `split_step_latency`) flow end-to-end from CV precompute through DuckDB and into the HUD. Three choreographed anomaly moments at **t = 35.9 s, 45.3 s, 59.1 s** are visible on the 60-second hero clip; these are the dramatic pulses the video will open on.

Opus 4.7 is correctly wired with `thinking: { type: 'adaptive' }` and ephemeral prompt caching on the system block (Tab 3 Server Action, `dashboard/src/app/actions.ts`). Backend: 386/386 pytest green, ruff clean. Frontend: 71/71 vitest green, `tsc` + ESLint clean. The state-machine edge-trigger fix (PATTERN-053) and the Client-Driven Payload for Vercel Server Actions (PATTERN-054) shipped in Phase 4 are holding.

All remaining work is **demo video production**, not code. Saturday 2026-04-25 is a focused build sprint (Remotion chrome, tickertape bar, dual OBS takes, narration script). Sunday 2026-04-26 is the final cut, render, YouTube upload, and submission — target **17:00 EST soft-submit** with a three-hour buffer before the 20:00 EST hard deadline.

---

## 3. What Happened Today (2026-04-24, Phase 6 Kickoff + Dialectical Sprint)

Phase 6 opened with the **WORKFLOW-006 three-parallel-agent research pattern**: one Explore agent audited the codebase against parent `CLAUDE.md` claims (surfacing GOTCHA-022 — narrative drift between marketing copy and actual implementation), one general-purpose agent inventoried video production tooling (Remotion, OBS, ElevenLabs, Sportradar reference aesthetic), and one general-purpose agent studied prior Anthropic hackathon winners and game-theory positioning. The nested `demo-presentation/` scope was created (assets / scripts / remotion / audio / renders / CLAUDE.md / PLAN.md). Storyboard v1 was drafted as tennis-broadcast-analyst narration; user correction re-scoped it to engineering-judge register ("clear, simple, useful, novel, interesting, cool, beautifully aesthetic — not childish, overly dramatic"), landing as v3 with ≤ 15 narration lines.

The afternoon ran a **4-iteration dialectical-mapping steelman** (WORKFLOW-007) with orthogonal Alpha/Beta agent pairs per iteration (risk lens vs. creative lens), all Perplexity-grounded against 2025–2026 sources. Eight agent passes surfaced ~30 non-obvious findings. Convergence hit at Iter 4 (net-new findings dropped below the 3-per-iteration threshold).

**Twelve decisions were locked (Q1–Q12)**. Highest-leverage outcomes: the full **Detective Cut** narrative arc (cold open on anomaly, defer title to closing); **kill** the animated Managed Agents Scene 5B fan-out (reads as "heard about the feature, didn't use it") in favor of a ≤ 15 s still + fade; **unfilter** `dashboard/src/app/actions.ts:145` (currently discards every `thinking` content block from the SDK response) and build a **Thinking Vault** UI surfacing model-internal reasoning as a first-class object paired 1:1 with outputs; add a **vision-pass** capability showcase (one pre-computed Opus 4.7 vision call on a broadcast frame, exploiting 4.7's 98.5 % XBOW score); **tier-split** Sportradar slow-mo add-on A2 into low-risk core (A2a, 30 min playback-rate slowdown) and high-risk stretch (A2b, 4 h canvas annotation geometry); **add submission dry-runs** (Sat 14:00 Prod smoke-test + Sat 16:00 YouTube throwaway upload); and the **post-submit amplification playbook** (PATTERN-066). Living docs extended with GOTCHA-024 through GOTCHA-028, PATTERN-061 through PATTERN-066, DECISION-012 and DECISION-013, and WORKFLOW-007.

---

## 4. Five Critical-Path Facts the Team Lead Needs to Know

- **`actions.ts:145` currently filters out thinking blocks.** The consumer does `.filter(b => b.type === 'text')`, silently discarding every adaptive-thinking block the server emits. Unlocking this is the single highest-leverage Saturday priority — it's the prerequisite for the Thinking Vault (hero visual of the 25% Opus 4.7 Use judging criterion).
- **macOS Sequoia OBS freeze at 20–30 min of 60 fps capture** (GOTCHA-024, three independent sources). Mitigation: dual 90-second OBS takes + parallel QuickTime recording in a second macOS Space as backup (PATTERN-061). Do not attempt a single long take.
- **YouTube Content ID + Vercel April 2026 key-rotation risk.** Pro tennis broadcast footage triggers Content ID auto-mute and ~13 % global geo-block independent of fair-use claim (GOTCHA-027). Vercel's April 2026 incident remediation may silently auto-rotate Production secrets while Preview stays valid (GOTCHA-028). Both reasons the Sat 14:00 / 16:00 dry runs are **non-negotiable**.
- **Detective Cut narrative arc** (PATTERN-065). Judges discover alongside Opus — cold open on the anomaly, the title card moves to the closing. Derived from convergent 2025 demo-video research (ChaplinAI, Advids, Guidejar). The whole edit restructures around this.
- **User rule (DECISION-013):** *"Low-risk / high-value items only in the core sprint; high-risk items get dedicated, undivided resources at the end."* This is the master scheduling constraint for Saturday. A2b, ElevenLabs, and any stretch-geometry work are end-of-day only.

---

## 5. Open Items and Focus Ahead

- **Fri 2026-04-24 22:00** — Remotion pre-warm + arm64 audit (verify `node -p process.arch === "arm64"`, avoid the Rosetta 2 silent 2× render slowdown — GOTCHA-025). Chrome Headless Shell fetch.
- **Sat 2026-04-25 08:00 – 22:00** — build sprint per the separate operational plan (core ~7.5 h + stretch 4 h for A2b).
- **Sun 2026-04-26 08:00 – 17:00** — final cut in DaVinci Resolve Free, YouTube upload (moved from 15:00 to 12:00 for Content ID / HD-lock buffer), soft-submit 17:00, hard lockout 19:55 EST.
- **Sun 20:15+** — post-submit amplification playbook: X thread, participant directory, Discord, DevRel DM, platform profile (PATTERN-066).
- **Tue 2026-04-28 12:00 EST** — finalist announcement.

---

## 6. Risks Currently in Flight

1. **Saturday build budget is tight.** ~7.5 h for the core sprint, 4 h for A2b stretch, leaves essentially no overrun slack. Any build failure cascades directly into Sunday.
2. **Branch reconciliation.** Andrew is concurrently working on match-state alignment and video-to-narration sync on the `hackathon-research` branch. As of this writing `hackathon-research` has advanced ~10 commits beyond `hackathon-demo-v1` with its own Phase A / Phase 3 merge history. The two branches must be reconciled **before Saturday morning's build**, or Saturday starts with an unresolved merge.
3. **Last-mile submission buffer.** The nominal 3-hour pad (17:00 → 20:00) is closer to 30–45 minutes net once YouTube processing (HD lock can take 20–60 min), Content ID re-check, and CV-submission-form authentication are factored in. One retry budget, not more.

---

## 7. Assets and Artifacts Inventory

| Asset | Location / Spec |
|---|---|
| Live preview URL | `panopticon-live-1fqx9c4iz-dmg-decisions.vercel.app` |
| Demo video specs | 1920×1080 H.264 MP4, ≤180 s, ≤500 MB |
| Demo scope folder | `/Users/andrew/Documents/Coding/hackathon-demo-v1/demo-presentation/` (`assets/`, `scripts/`, `remotion/`, `audio/`, `renders/`, `CLAUDE.md`, `PLAN.md`) |
| Tennis footage library | 8 matches available in `Alternative_Data/data/videos/`; 3 ANCHOR_OK |
| Hero clip | Existing 60-s segment already deployed: `dashboard/public/clips/utr_match_01_segment_a.mp4` |
| Project-scoped skill packs | 15 in `.claude/skills/` — `cv-pipeline-engineering`, `2k-sports-hud-aesthetic`, `biomechanical-signal-semantics`, `biometric-fan-experience`, `hackathon-demo-director`, `topological-identity-stability`, `opus-47-creative-medium`, `vercel-ts-server-actions`, `match-state-coupling`, `physical-kalman-tracking`, `duckdb-pydantic-contracts`, `react-30fps-canvas-architecture`, `temporal-kinematic-primitives`, `signal-extractor-contract`, `panopticon-hackathon-rules` |

---

## 8. Handoff Contract

- The **operational plan** (storyboard beats, hour-by-hour Saturday build, submission checklist, fallback plans) will be passed separately. Canonical sources: `/Users/andrew/Documents/Coding/hackathon-demo-v1/demo-presentation/PLAN.md` + `/Users/andrew/.claude/plans/pull-from-remote-main-humble-forest.md`.
- **This document** covers NARRATIVE + CONTEXT + FOCUS AHEAD only — not the timeline.
- Clarifying questions: direct to Andrew.

---

## Key File Paths

### Living project docs
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/CLAUDE.md` — project constitution (hard constraints, MPS safeguards, React architecture rules, skill team)
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/FORANDREW.md` — plain-language decision log (Phase 6 kickoff at line 806, dialectical steelman at line 880)
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/MEMORY.md` — structured learnings (§ `DAY 3 LEARNINGS` at line 1154, § `DAY 3 CONTINUED` at line 1239)
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/TOOLS_IMPACT.md` — tool ROI + "Skills NOT Used"
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/docs/ORCHESTRATION_PLAYBOOK.md` — phase-by-phase tool runbook
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/docs/PHASE_4_TEAM_LEAD_HANDOFF.md` — prior-phase forensic dossier (style reference for this document)

### Phase 6 scope
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/demo-presentation/CLAUDE.md` — demo tone + narrative discipline rules
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/demo-presentation/PLAN.md` — storyboard v4 (Detective Cut), Sat/Sun timeline, asset registry
- `/Users/andrew/.claude/plans/pull-from-remote-main-humble-forest.md` — master strategic trail for Phase 6 (Iter 1–4 findings, §10–11 operational plan)
- `/Users/andrew/.claude/plans/phase-6-demo-production.md` — original Phase 6 strategic plan (kickoff session)

### Code paths load-bearing for Phase 6 work
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/dashboard/src/app/actions.ts` — line 145 is the thinking-block filter to remove (GOTCHA-026 fix)
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/dashboard/src/components/Scouting/ScoutingReportTab.tsx` — Thinking Vault rendering surface (PATTERN-063)
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/dashboard/public/clips/utr_match_01_segment_a.mp4` — hero clip for the Detective Cut
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/backend/cv/state_machine.py` — edge-trigger bounce coupling (Phase 4 PATTERN-053, unchanged this phase)

### Concurrent branch to reconcile
- Local branch `hackathon-research` — Andrew's match-state alignment + video-to-narration sync work; must reconcile with `hackathon-demo-v1` before the Saturday build begins.

— Agent handoff prepared 2026-04-24 evening. Ready for Saturday sprint handoff.

---

## Update since handoff — 2026-04-24 PM / evening (post-polish sprint)

This document is the point-in-time handoff from the Phase 6 kickoff session. **The following work has landed in the `hackathon-research` branch SINCE this handoff was written** — it is additive to (not a replacement for) the Phase 6 plan above.

### Polish sprint (Final 20 %, team-lead override 2026-04-24 PM)

Five perimeter-hardening directives shipped in ~90 min. All validated (`tsc --noEmit` exit 0, `vitest run` 96/96 green). See MEMORY.md → "2026-04-24 PM — Final 20 % Polish Sprint" section for GOTCHA-038/039, PATTERN-070/071/072, DECISION-013, WORKFLOW-008.

1. **GOTCHA-038 — Tab-visibility rAF drift defense**. `document.visibilitychange` listener in PanopticonProvider pauses the video on hidden; manual play required on return so rAF re-syncs with videoClock.
2. **GOTCHA-039 — Vercel cold-boot blocker**. New `LoadingScreen.tsx` 2K-Sports CRT terminal overlay gates the UI until `matchData` resolves. `z-index: 9999` + `pointer-events: auto` on the inner panel. Fades out over 500 ms (PATTERN-071).
3. **PATTERN-070 — DPR-aware Canvas Resize**. `PanopticonEngine` now observes `<video>` directly (canonical per `react-30fps-canvas-architecture` skill), sets canvas buffer dims to `clientW * DPR × clientH * DPR`, `ctx.setTransform(DPR, ...)`, per-frame paint math uses `canvas.clientWidth/Height` (CSS pixels, not buffer pixels).
4. **PATTERN-071 — Framer Motion UX masking**. 500 ms opacity fade on CoachPanel (via per-property transition override spreading spring + overriding just `opacity`); 400 ms opacity fade on each TelemetryLog row. Masks any residual Opus-cache narration desync.
5. **DECISION-013 — demo-presentation/ consolidation**. Sibling worktree's `demo-presentation/` (CLAUDE.md + PLAN.md + folder skeleton) copied into `hackathon-research/demo-presentation/`. `docs/DEMO_STORYBOARD.md` now has a canonical pointer at the top referencing `demo-presentation/PLAN.md §5` as the v4 Detective Cut source of truth.

### G10 Dynamic Identity Injection (also post-handoff)

The v4 plan's "display-only authoring" architecture (G43) + `query_video_context_mcp` (A9 stubbed-MCP tool) both shipped green. Then the team lead's **G10 follow-up** landed: the Analytics Specialist's system prompt used to say "Refer to the target ONLY as Player A" which actively GAGGED the agents from citing the authored `player_profile`. Fix was a DYNAMIC identity rule in `_build_baseline_context`:

- **Profile absent** → strict anonymity guardrail (unchanged, anti-hallucination).
- **Profile present** → "PROFILE DETECTED: You MUST refer to the target player by `{player_profile.name}` and actively integrate their specific attributes..." (unlocks personalization).

Verified in a re-run: all 3 agents cite "UTR Pro A" by name; 2/3 cite profile fields (`right-handed`, `compact pre-serve motion`, `orange racket strings`); zero Hurkacz / Djokovic / Federer / Nadal hallucinations. See MEMORY.md → DECISION-014 for full audit, and `dashboard/public/match_data/_authoring/player_profile.json` for the anonymized-but-rich profile (no fabricated ATP numerics — `world_rank`/`serve_velocity_avg_kmh` dropped because actual player identity was never verified at authoring time).

### Test counts now

- **Python**: ~434 pytest (baseline from prior handoff was 386 — the additions are the G10 + display_*/provenance + AuthoredStateTransition + QualitativeNarration + PlayerProfile validation tests).
- **TypeScript**: 96 vitest (baseline was 71 — additions are stateSignalGating Record exhaustiveness + LoadingScreen rendering + DisclosureBanner).

### What's still queued for Saturday (per PLAN.md §6)

- **A1** Tickertape bar (phase-weighted signal order) — 1 h
- **A5** Architecture diagram (Canva) — 1 h
- **A6** Remotion chrome (title + closing card + scene breaks) — 1.5 h
- **A7** Precomputed Opus 4.7 vision pass on t=45.3 s frame — 1 h
- **A2a** Video `playbackRate` slow-mo at anomaly timestamps — 30 min
- **A4** Managed Agents fan-out (≤ 15 s still/fade) — 30 min
- **A9** Submission dry runs (YouTube + CV form) — 1 h total
- **A8** Thinking Vault 3-column UI — deferred to Saturday after user's "minimal A8" scope decision tonight

### Critical-path facts that CHANGED since the handoff

- **`dashboard/src/app/actions.ts:145` no-longer-applicable**: on the `hackathon-research` branch, `actions.ts` is a stub returning hand-authored markdown (not a live Opus call). The sibling handoff's "unfilter actions.ts:145" directive was for the sibling's live-Opus version. On THIS branch, the real Opus work runs in `backend/agents/scouting_committee.py` during precompute; the captured thinking blocks flow through to `agent_trace.json`.
- **Thinking blocks currently at 0 across all 3 Scouting Committee agents** — not a filter bug (extraction is correct per `_extract_thinking_text` in `opus_coach.py`), but Opus 4.7's adaptive thinking chose not to emit for the current prompt. **Prompt nudge ADDED 2026-04-24 PM**: Analytics Specialist system prompt now has STEP 3 explicitly requiring dual-hypothesis consideration with a rejection clause. Re-run golden data to verify thinking blocks appear.
- **Concurrent branch reconciliation is RESOLVED** — `demo-presentation/` is now canonical inside this branch; the sibling worktree at `~/Documents/Coding/hackathon-demo-v1/` is READ-ONLY going forward.

— Update prepared 2026-04-24 PM by Claude Opus 4.7 (current session, post-polish sprint).
