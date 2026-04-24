# TOOLS_IMPACT.md — Tool ROI Log

Tracks which tools / skills / agents / MCPs we used, why, and whether they paid off. The "Skills NOT Used" section is the durable defense against silently ignoring the skill ecosystem.

---

## HIGH-IMPACT TOOLS FOR THIS PROJECT (planned)

### MCPs — actively used
| MCP | Role in project | Expected ROI |
|---|---|---|
| `perplexity_ask` / `perplexity_research` | Biomechanical threshold literature; verify library versions | HIGH — cites, recency |
| `context7` | Ultralytics YOLO11m-Pose, Anthropic SDK, Next.js 16, shadcn/ui docs | HIGH — current APIs beat training data |
| `figma` | HUD design spec before coding Tailwind | HIGH — Opus 4.7 design muscle showcase |
| `Claude_in_Chrome` | Live browser testing during frontend dev | MEDIUM — faster than manual QA |
| `Claude_Preview` | Quick UI preview snapshots for design iteration | MEDIUM |
| `vercel` (50+ tools) | Deployment, env vars, domain, logs, env checking | HIGH |
| `computer-use` | OBS recording for demo video (Sun) | HIGH (demo day only) |

### Skills — actively used (in planned firing order)
| Skill | When it fires | Why |
|---|---|---|
| `claude-api` | Day 2 agent wiring | Prompt caching + extended thinking patterns |
| `vercel-react-best-practices` | Day 3-4 frontend review | Code-level quality pass |
| `awwwards-animations` | Day 3 HUD motion design | Framer Motion patterns |
| `vercel:shadcn` | Day 3 scaffolding | Component CLI |
| `vercel:nextjs` | Day 3-4 | App Router patterns |
| `vercel:vercel-functions` | Day 4-5 | Python Fluid Compute setup |
| `vercel:ai-gateway` | Day 2 | Opus call routing |
| `python-testing` | Day 1 | pytest fixtures + mocking |
| `e2e-testing` | Day 4 | Playwright regression |
| `frontend-design` | Day 3 | 2K Sports aesthetic patterns |
| `top-design` | Day 3 | Awwwards-level polish |
| `content-hash-cache-pattern` | Day 1 | DuckDB row caching by clip hash |
| `long-running-tasks` | Day 1 | If precompute crosses 2 min |
| `continuous-learning-v2` | All week | Session observation → instincts |

### Agents — actively used
| Agent | When it fires | Why |
|---|---|---|
| `Explore` | Pre-planning | Fast codebase scans (used already Apr 21) |
| `Plan` | Plan validation | Design review (used already Apr 21) |
| `python-reviewer` | After every .py change | Code review |
| `typescript-reviewer` | After every .ts/.tsx change | Code review |
| `code-reviewer` | Pre-PR gates | General quality |
| `security-reviewer` | Pre-deploy | Attack surface |
| `tdd-guide` | New features | Test-first enforcement |
| `e2e-runner` | Post-UI changes | Automated regression |
| `build-error-resolver` | When CI fails | Minimal-diff fixes |
| `refactor-cleaner` | Pre-submit | Dead code removal |

### Slash commands — actively used
| Command | Phase | Why |
|---|---|---|
| `/tdd` | Day 1+ | Enforce test-first |
| `/devfleet` | Day 1 | Parallelize 7 signal implementations |
| `/verify` | Daily | Build + tests + coverage gate |
| `/e2e` | Day 4 | Dashboard regression |
| `/vercel:deploy` | Day 4-5 | Preview → prod |
| `/vercel:verification` | Day 5 | Full-story check |
| `/code-review` | After features | PR review simulation |
| `/go` | Day 5 | Ship-it workflow |
| `/save-session` | EOD each day | Context preservation |
| `/checkpoint` | Mid-day stable points | Recovery points |
| `/skill-create` | If new pattern emerges | Capture reusable pattern |
| `/continuous-learning-v2` | All week | Instinct extraction |

---

## SKILLS NOT USED (and why) — Citadel-level discipline section

Tracks skills we evaluated and consciously skipped. Prevents anti-pattern #18 (ignoring available skills).

| Skill | Why skipped | Revisit trigger |
|---|---|---|
| `kotlin-*` | Project is Python/TypeScript | N/A |
| `rust-*`, `go-*`, `java-*`, `laravel-*`, `django-*`, `flutter-*`, `perl-*`, `cpp-*` | Language mismatch | N/A |
| `springboot-*` | No Java/Spring stack | N/A |
| `swift-*`, `foundation-models-on-device` | Not iOS/macOS native | N/A |
| `database-migrations` | DuckDB is file-based; no migrations needed | Revisit if schema evolves |
| `api-design` | Internal API only; no public REST design | N/A |
| `renaissance-statistical-arbitrage` | No trading in hackathon project | N/A |
| `backtesting-frameworks` | Explicitly aborted ML work (Batch 11 trap) | N/A |
| `monte-carlo` | No simulation work this week | N/A |
| `energy-procurement`, `returns-reverse-logistics`, `customs-trade-compliance`, `logistics-exception-management`, `inventory-demand-planning`, `production-scheduling`, `carrier-relationship-management`, `quality-nonconformance` | Wrong domain | N/A |
| `cost-aware-llm-pipeline` | Haiku/Opus routing decisions are simple; already baked in | Revisit if API cost becomes concern |
| `data-validation` | Pydantic v2 already mandated; skill is a superset | Consult if multi-model validation needed |
| `data-quality-frameworks` | No complex data pipelines | N/A |
| `regex-vs-llm-structured-text` | Decisions are obvious here | Revisit if text parsing needed |
| `mcp-server-patterns` | Unless we ship an MCP for biomech queries (stretch) | Revisit Day 4 if time |
| `compose-multiplatform-patterns` | No KMP needed | N/A |
| `android-clean-architecture` | No Android | N/A |
| `swiftui-patterns` | No SwiftUI | N/A |
| `laravel-*` | PHP not used | N/A |
| `videodb` | Considered for auto-highlight clips; might invoke on Day 5 stretch | Revisit Day 5 if time |
| `agent-eval` | No head-to-head agent comparison needed | Revisit if Opus behavior needs calibration |
| `deep-research` | perplexity_research is sufficient for scope | N/A |
| `x-api`, `social-content` | Only on Day 6 (submission post), after submit | Day 6 |
| `investor-outreach`, `investor-materials` | YC app is separate track, May 4 deadline | Next week |
| `deployment-patterns` | `vercel:*` skills are more specific | N/A |
| `docker-patterns` | Vercel handles this | N/A |
| `nutrient-document-processing` | Scouting PDF uses ReportLab (standard lib) | Revisit if PDF complex |
| `chat-sdk` | Not building a chatbot | N/A |
| `crosspost` | Post-submit only | Day 6 |

---

## ROI LOG — actual outcomes (populate as we go)

### Day 0 (Apr 21) — Setup phase — COMPLETE

| Tool | Outcome | ROI | Notes |
|---|---|---|---|
| `Explore` agent (3x parallel) | Deep understanding of Alternative_Data foundation in ~5 min | HIGH (+60 min saved) | Revealed that 3 of 7 signals are MISSING not just stubbed |
| `Plan` agent (1x) | Found 4-agent swarm was redundant; single Opus + tools recommended | HIGH (3-4x Opus cost avoided) | Restructured entire agent architecture |
| `perplexity_ask` | Biomech thresholds cited (400ms serve return, 150ms split-step baseline, 2.5x body-weight vGRF on split-step landing) | MEDIUM | Partial — elite thresholds for some signals not in literature |
| `perplexity_ask` (#2) | Claude Managed Agents 2026-04-01 API (`client.beta.agents.create`, `client.beta.sessions.create`, `agent_toolset_20260401`) | HIGH | Directly unblocks Phase 2 scouting-report work |
| `context7` / `/websites/ultralytics` | Keypoints `.xyn` (pre-normalized [0,1]) | HIGH — non-obvious | Saves coordinate-normalization step AND pre-empts resize bug at source |
| `context7` / `/anthropics/anthropic-sdk-python` | Extended thinking API shape, streaming pattern, prompt caching `cache_control` | HIGH | Phase 2 code shape confirmed |
| `ToolSearch` (deferred-tool loading) | AskUserQuestion, ExitPlanMode, TodoWrite loaded on demand | MEDIUM | Avoids cluttering context with tools we don't need |
| PreToolUse security hook | Caught `exec`/`innerHTML` strings twice (false positives but forced better code) | LOW — but habit-forming | Rewrote probe_clip with sync subprocess + court_annotator with textContent + DOM methods |
| Day-0 probe (YOLO11m-Pose MPS) | 12.7 FPS warm, 100% detection, 99.9% two-player, no leak | HIGH (Go/No-Go GATE) | Unblocked Phase 1 — entire week's work was contingent on this |
| pyproject.toml bifurcation | `-local` vs `-prod` req files baked in from day 1 | CRITICAL (250MB wall defense) | Prevents Vercel deploy failure later |

### End-of-Day-0 Meta-Summary

**What the tool stack produced in ~6 hours:**
- 5 living docs (~3000 lines)
- 12 specialized agents (~2500 lines of system prompts)
- 8 project-scoped skills (~4000 lines of pattern/constraint documentation)
- Full Python scaffolding (config, Pydantic schemas, DuckDB DDL, venv + deps)
- Working YOLO probe pipeline on real pro tennis broadcast video
- Initial public GitHub repo committed + pushed

**Skills I could have used and didn't:** `search-first` was skipped when I confidently searched library docs directly via Context7 — justified. `continuous-learning-v2` hooks not yet activated; will activate on Wed Apr 22. `/find-skills` not used because user explicitly listed the skill inventory.

**Gotchas discovered (now in MEMORY.md):**
- Ultralytics `.xyn` gives pre-normalized coords (saves code)
- YOLO sees crowd + ball-boys + linesmen → Phase 1 needs player-filtering
- Memory-slope sign matters (only positive = leak)
- `create_subprocess_exec` + `innerHTML` trip the security hook (workarounds documented)

**Day 1 pre-loaded learnings ready to deploy** — Wed Apr 22 starts Phase 1 with zero re-discovery overhead.

### Phase-1 Late-Session Block (Apr 21, 2026) — Action 1 + Action 2 executed same day

| Tool | Outcome | ROI | Notes |
|---|---|---|---|
| TDD-first methodology (enforced via `test-forensic-validator` agent) | Caught perspective-warp test fixture bug BEFORE `homography.py` was finalized; caught Kalman unit-mismatch regression via explicit guard test | **HIGH** | Test expected `image_y=0.54` for net; actual projection is ~0.34. Fix applied before any production code depended on wrong expectation. Pattern captured as PATTERN-010, PATTERN-011. |
| 12-agent + 12-skill infrastructure (Day-0 build) | Zero re-discovery of 10 USER-CORRECTIONs during implementation of CV spine | **HIGH** — compounded across all 4 modules | The 4 new skills added today (`physical-kalman-tracking`, `topological-identity-stability`, `match-state-coupling`, `vercel-ts-server-actions`) all fired during spine implementation. Each saved ~20-30 min of ad-hoc reasoning. |
| `perplexity_ask` (Managed Agents 2026-04-01 API) | PATTERN-008 captures exact beta shape for scouting-report | **HIGH** | Directly unblocks Phase-2 scouting report Server Action wiring via `@anthropic-ai/sdk` TypeScript. |
| `context7` (Ultralytics, Anthropic SDK) | `.xyn` pre-normalization (PATTERN-004); extended-thinking + streaming + `cache_control` patterns (PATTERN-005) | **HIGH** | Zero training-data reliance. |
| Pydantic v2 extensions (`CornersNormalized`, `RawDetection`, `PlayerDetection`, `StateTransition`, `FrameKeypoints` + COCO index constants + court dimensions) | Inter-module contracts mechanically enforced; module constants prevent "magic number" drift | **HIGH-ROI** — type safety compounds all week | Exports `NET_Y_M=11.885`, `SINGLES_COURT_LENGTH_M=23.77`, `SINGLES_COURT_WIDTH_M=8.23` as canonical source. |
| Security hook (PreToolUse) | Caught `asyncio.create_subprocess_exec` and `innerHTML` strings | LOW direct, MEDIUM habit-forming | Sync `subprocess.Popen` + DOM-API-based annotator remain canonical (see PATTERN-006/007). |
| `ruff --fix` then per-file-ignores | 39 initial issues → 2 after auto-fix → 0 after targeted per-file-ignores + 2 manual fixes (SIM102 collapse + unicode `×` → `by`) | MEDIUM | Code is now fully lint-clean without compromising CV idioms (`W`, `H`). |
| `pytest-cov` | Verified 82.75% total coverage on `backend/cv` + `backend/db`, gate 80% passed | HIGH | `backend/cv/pose.py` at 69% because `PoseExtractor` wraps real YOLO inference — smoke-tested separately, not unit-tested. |

**Skills that FIRED during Action 2**: `panopticon-hackathon-rules`, `cv-pipeline-engineering`, `duckdb-pydantic-contracts`, `physical-kalman-tracking`, `topological-identity-stability`, `match-state-coupling`, `biomechanical-signal-semantics` (referenced for signal math), `python-testing-patterns` (TDD).

**Skills QUEUED but not yet used** (target phases in parens):
- `opus-47-creative-medium`, `claude-api`, `agent-harness-construction` (Phase 2: Opus wiring)
- `vercel-ts-server-actions`, `vercel:nextjs`, `vercel:shadcn`, `vercel:react-best-practices` (Phase 3+4: frontend + deploy)
- `react-30fps-canvas-architecture`, `2k-sports-hud-aesthetic`, `awwwards-animations`, `top-design`, `frontend-design` (Phase 3: dashboard)
- `e2e-testing`, `e2e-runner` (Phase 4: dashboard regression)
- `hackathon-demo-director` (Phase 5: video record + submit)
- `vercel:deployments-cicd`, `vercel:env-vars`, `vercel:vercel-functions` (Phase 4: production deploy)
- `continuous-learning-v2` (meta: session-level instinct extraction)

**Agents that FIRED during Action 2**: `cv-pipeline-engineer` (spine), `test-forensic-validator` (tests), `data-integrity-guard` (schema extensions), `homography-geometry-specialist` (CourtMapper aspect-ratio), `mps-performance-engineer` (safeguards in pose.py), `documentation-librarian` (pre-compact save — blocked by plan-mode inheritance, recovered by inline execution).

---

## Day 1 (Phase-1 Action 2.5 — Citadel Override Patch Sprint, Apr 22 2026)

### HIGH-IMPACT tools / patterns this session

| Tool / Pattern | Outcome | ROI | Notes |
|---|---|---|---|
| **Two-round team-lead audit** (CTO review) | 11 runtime-failure modes prevented at design time (5 in audit 1 + 6 in audit 2) | **MASSIVE** — each failure would cost hours of on-video debugging on real broadcast footage | Pattern: don't ship an architectural change until an external reviewer has stressed dynamic failure modes that static unit tests cannot catch. Even with 45/45 green, 2 audit rounds found 11 gaps. |
| **TDD-first (5 patches, RED→GREEN)** | Each patch RED→GREEN in minutes. No post-hoc bug hunt. | **HIGH** | Patch 1 wrote 12 ABC tests BEFORE `base.py`. Patch 2 wrote 16 serializer tests BEFORE `@field_serializer`. Patch 3 wrote 6 uncoupling tests BEFORE modifying state_machine. Patch 4 wrote 17 bounce tests BEFORE temporal_signals. All caught API shape issues during test authoring. |
| **`python-reviewer` agent (orthogonal-to-tests lens)** | Caught 1 HIGH (`_round_dict` type too loose) + 2 MEDIUM (stringly-typed dispatch, untyped `info`) — NONE caught by 96 tests | **HIGH** | Code-reviewer lens is orthogonal to test lens: tests prove correctness on TESTED inputs; reviewer catches type-drift risks on FUTURE inputs. Using both is the Citadel-rigor pattern. |
| **First-principles override validation** | Validated all 6 audit-round-2 overrides from first principles BEFORE accepting | **HIGH (trust-building)** | User explicitly instructed "don't take team lead as gospel, validate first principles." All 6 were correct — but going through the exercise catches the 1-in-10 case where the reviewer misreads. |
| **Orthogonal skill architecture** (2 new skills) | `signal-extractor-contract` (INTERFACE) + `temporal-kinematic-primitives` (TIME-SERIES + camera invariance) — orthogonal to `biomechanical-signal-semantics` (SEMANTICS) + `cv-pipeline-engineering` (ORCHESTRATION). 4-node DAG, zero overlap. | **COMPOUNDS across Phase 1-5** | Each skill owns one concern slice; future sessions load only what's relevant. Adding skills MUST preserve the DAG. |
| **`abc.ABC` + symmetric target/opponent API** | `BaseSignalExtractor` becomes a pluggable interface 4 parallel fleets in Action 3 implement INDEPENDENTLY | **HIGH-ROI** | Pattern generalizes: any future parallel-agent task where N agents produce one module each should start with an ABC. Prevents fleet-invented API divergence. |
| **Pydantic v2 `@field_serializer` + typed helpers** | 13 float fields across 5 models round to 4 decimals at JSON-only; in-memory precision preserved | **HIGH-ROI** — prevents 10MB+ JSON browser-OOM on `match_data.json` | `_round_float`, `_round_pair`, `_round_pair_list`, `_round_list`, `_round_dict` + multi-field decoration `@field_serializer("v1", "v2", ...)` scale cleanly. |
| **`ruff --fix` then targeted RUF002 manual fix** | 9 errors → 6 auto-fixed → 3 remaining (Unicode minus in docstrings) manually fixed in <1 min | MEDIUM | The 3 manual fixes caught real issues: team-lead spec prose contained `−` (U+2212) looking identical to `-` but blocking grep / causing ambiguity. |
| **`mode: "acceptEdits"` on every sub-agent dispatch** | python-reviewer returned actionable review in 51 seconds, zero plan-mode stalls | CRITICAL | Anti-pattern #33 (subagent plan-mode inheritance) consistently applied. ZERO round-trips wasted. |

### Skills that FIRED during Action 2.5

- `signal-extractor-contract` (NEW — authored + applied)
- `temporal-kinematic-primitives` (NEW — authored + applied)
- `cv-pipeline-engineering` (updated Stage 4.5 + USER-CORRECTIONs 011/013)
- `biomechanical-signal-semantics` (updated Common-Traps callout + Lomb-Scargle fix)
- `match-state-coupling` (referenced for USER-CORRECTION-011 logic check)
- `panopticon-hackathon-rules` (prime directive)
- `duckdb-pydantic-contracts` (serializer scope)

### Skills QUEUED but NOT USED in Action 2.5

- `opus-47-creative-medium`, `claude-api`, `agent-harness-construction` (Phase 2: Opus wiring)
- `vercel-ts-server-actions`, `vercel:nextjs`, `vercel:shadcn`, `vercel:react-best-practices` (Phase 3+4)
- `react-30fps-canvas-architecture`, `2k-sports-hud-aesthetic`, `awwwards-animations`, `top-design`, `frontend-design` (Phase 3: dashboard)
- `e2e-testing`, `e2e-runner` (Phase 4: regression)
- `hackathon-demo-director` (Phase 5: submission)
- `vercel:deployments-cicd`, `vercel:env-vars`, `vercel:vercel-functions` (Phase 4)
- `continuous-learning-v2` (meta)
- `topological-identity-stability`, `physical-kalman-tracking` (Action 2 stable — no re-use needed)

### Agents that FIRED during Action 2.5

- `python-reviewer` (one pass over all 5 patches, `mode: "acceptEdits"`) — **1 HIGH + 2 MEDIUM findings, all fixed pre-commit**

### Anti-patterns dodged this session

- **#18 (ignoring skills)** — 7 skills explicitly referenced in code comments
- **#33 (plan-mode inheritance)** — every sub-agent dispatched with `mode: "acceptEdits"`
- **#29 (redundant tool inventory)** — used system-reminder tool list directly
- **#32 (bypassing quality commands)** — used `python-reviewer` agent directly (no `/review` wrapper exists for it)

### Meta-learning

**Two-round audit is the right unit of review for architectural changes.** Round 1 catches obvious bugs (Lomb-Scargle Hz-vs-rad/s, bounce deadlock). Round 2 catches subtle bugs that only show up on real data (camera pan, ACTIVE_RALLY truncation, NaN-safety). For anything shipping to production video, plan on TWO rounds of external review between "code complete" and "code committed." Single-round review is acceptable only for isolated bug fixes.

### Meta-lesson
Agent plan-mode inheritance (anti-pattern #33) re-surfaced when dispatching the `documentation-librarian` without `mode: "acceptEdits"`. The agent produced a comprehensive plan file but executed zero edits. Recovery: read the agent's plan file and apply the edits inline (Write/Edit tools). Net cost: ~2 min of round-trip but saved because the plan was high-quality. Future: every sub-agent that should write files MUST pass `mode: "acceptEdits"` or `"bypassPermissions"`.

---

## META-LEARNING FRAMEWORK

At end of each day, answer:
1. **Which tool paid off unexpectedly?** → Update HIGH-IMPACT section
2. **Which tool did nothing?** → Move to SKILLS NOT USED with reason
3. **Did I skip a tool I should have used?** → Anti-pattern #18; note and use tomorrow
4. **What non-obvious pattern emerged?** → Extract to `.claude/skills/` via `/skill-create`

---

## Day 1.5 (Apr 22, late — Actions 3 + 3.5 COMPLETE — full CV Engine)

### HIGH-IMPACT tools/patterns this session

| Tool / Pattern | Outcome | ROI | Notes |
|---|---|---|---|
| **Three-round team-lead audit** (CTO review pattern) | Surfaced USER-CORRECTIONs 017 (Homography Z=0), 018-022 (compiler-flush, structural state-proxy, phantom-serve, asymmetric baseline, fail-fast) | **MASSIVE** — prevented ~11 silent physics/data-integrity bugs before implementation | Two-round was right for Action 2.5; three-round was right for Action 3 (pilot → pre-flight round 2 → fleet dispatch). PATTERN-026 captures this cadence. |
| **Sequential fleet dispatch** (after worktree isolation failed) | Fleets 1, 2, 3, 4-pilot each ran in ~2 min with full gate verification between; zero collisions | **HIGH** (risk mitigation) | Trade: ~6 min extra total vs. parallel. DECISION-006 + GOTCHA-011 capture this. Pilot-test `isolation: "worktree"` on the first dispatch to detect hook availability. |
| **Fleet 4 PILOT before scaling** (team-lead Option C) | Validated BaseSignalExtractor ABC works cleanly, sandbox discipline held, found the `.get("match_id", "unknown")` leak → fixed pre-Fleet-1 | **HIGH** | Pattern: always pilot a new contract on the SMALLEST independent unit (singleton) before scaling to the N-fleet sprint. Pilot caught a fail-fast violation that would have propagated to 6 more extractors. |
| **Independent orchestrator verification** (PATTERN-027) | After EACH fleet, ran `git status`, `pytest tests/`, `ruff check`, + coverage. Zero fleet summaries were blindly trusted. | **CRITICAL** (trust discipline) | Cost: ~15 sec per verification. Benefit: catches silent agent self-reports. All 4 fleets passed first-try, but the verification gate would have caught regressions. |
| **Rising-edge compiler-flush pattern** (PATTERN-024) | FeatureCompiler fires `flush()` EXACTLY ONCE on state-exit — no duplicates, no misses | **HIGH** | Generalizes to any pub/sub pipeline where one-shot emission on state transition is needed. Same structural idea as USER-CORRECTION-011 conditional uncoupling. |
| **Synthetic rally simulation** (PATTERN-025) | 13 end-to-end tests for FeatureCompiler validate 14 extractors + DAG in <1 second, no MP4, no ML weights | **HIGH-ROI** | Build `_detection(player, hip_y, wrist_y, shoulder_y, feet_mid_m)` + `_frame(t_ms, a_kwargs, b_kwargs)` helpers. Three-phase scenario (PSR → RALLY → DEAD) exercises every extractor's state gate + flush timing. |
| **Pydantic `@field_serializer` inheritance through nested models** (PATTERN-030) | Confirmed 4-decimal rounding propagates through `MatchData` → `SignalSample[]` automatically | HIGH (payload-bloat prevention) | Next Pydantic upgrade could silently change this — add a regression test in `test_writer.py` (Action 4.1). |
| **ALL_EXTRACTOR_CLASSES stable-order tuple** | Deterministic per-tick sample emission order for testing; compiler instantiates `len(classes) × 2 = 14` instances | MEDIUM | Allows integration tests to assert `(signal_name, player)` tuples in a predictable order. |
| **Fail-fast `self.deps["match_id"]`** (USER-CORRECTION-022) | Missing match_id raises `KeyError` during orchestration setup instead of silently corrupting DuckDB PKs | **HIGH** (data integrity) | Regression test uses `pytest.raises(KeyError, match="match_id")`. |

### Skills that FIRED during Actions 3 + 3.5

- `signal-extractor-contract` (authored in Action 2.5, USED 7× — once per signal extractor)
- `temporal-kinematic-primitives` (referenced in Fleet 2 ritual_entropy for Lomb-Scargle angular frequencies)
- `biomechanical-signal-semantics` (referenced + UPDATED with USER-CORRECTIONs 019-021 math contracts for Fleets 1-3)
- `cv-pipeline-engineering` (referenced — FeatureCompiler follows Stage 4.5/5 ordering)
- `duckdb-pydantic-contracts` (referenced for schema modifications)
- `match-state-coupling` (referenced for USER-CORRECTION-011 conditional uncoupling)
- `physical-kalman-tracking` (referenced for USER-CORRECTION-017 Z=0 + Kalman-meter semantics)
- `panopticon-hackathon-rules` (prime directive)

### Skills QUEUED but NOT used in Actions 3 + 3.5

- `opus-47-creative-medium`, `claude-api` (Phase 2: Opus Coach + HUD Designer + Haiku Narrator)
- `vercel-ts-server-actions`, `vercel:nextjs`, `vercel:shadcn`, `vercel:react-best-practices` (Phases 3-4)
- `react-30fps-canvas-architecture`, `2k-sports-hud-aesthetic`, `awwwards-animations` (Phase 3)
- `e2e-testing`, `e2e-runner` (Phase 4)
- `hackathon-demo-director` (Phase 5 — record + submit)
- `topological-identity-stability` (Action 2 code stable — no re-use)

### Agents that FIRED during Actions 3 + 3.5

- `general-purpose` agent × 4 (Fleet 4 pilot + Fleets 1/2/3, all with `mode: "acceptEdits"`)
- Orchestrator (self) did Action 3.5 FeatureCompiler inline — no fleet needed (single file, needed full context of all 7 signal classes)

### Anti-patterns dodged this session

- **#33 (plan-mode inheritance)** — every fleet dispatched with `mode: "acceptEdits"`; zero plan-mode stalls
- **#29 (redundant tool inventory)** — used system-reminder tool list directly for orchestration
- **#18 (ignoring skills)** — 8 skills referenced across the session, including 2 authored in Action 2.5
- **#30 (project agents without Write)** — all agents dispatched with `mode: "acceptEdits"`, not "plan"
- **Trust-but-verify** — every fleet's self-report was independently re-verified with pytest + ruff + git status + coverage

### Meta-learning this session

**Three complementary engineering disciplines compounded today**:

1. **Audit-first, code-second** (PATTERN-026): three audit rounds surfaced 11 subtle bugs that zero amount of unit-testing would have caught. Audit is orthogonal to tests — tests verify behavior on KNOWN inputs; audits verify the input-behavior contract itself.

2. **Contracts enable parallelism even without parallel execution** (PATTERN-014, 024): the `BaseSignalExtractor` ABC + compiler-flush contract meant 4 fleets could build 7 signals INDEPENDENTLY (even though we ran them sequentially). Once the contract lands, the fleets don't need to coordinate — they inherit + obey.

3. **Independent verification is free** (PATTERN-027): 15 seconds of orchestrator-level verification per fleet is negligible overhead that catches silent self-report issues. Never ship agent-written code without re-running the gates locally.

---

## Day 2 (Apr 22-23 — Phase 2 Opus Agent Layer) — HIGH ROI

### Python-reviewer agent (post-Phase-2 dispatch) — HIGHEST ROI of the week

Dispatched once, ~2 minutes of agent wall time. Returned 2 HIGH + 3 MEDIUM findings, each actionable:

| Finding | Severity | Root cause | Cost if shipped |
|---|---|---|---|
| HIGH-1: Greedy `\{.*\}` regex extends to LAST `}` in tail prose | HIGH | Classic greedy-regex trap on LLM output | Silent fallback layouts on any Opus response with trailing prose |
| HIGH-2: Narrator had no `beat_cap` while coach/design did | HIGH | Attention drift; asymmetry = the bug | 900 concurrent Haiku calls on a 15-min clip → rate limiter → `[narrator_error]` beats dominating demo |
| MEDIUM-1: bare `list` parameter types in `_safe_gather` | MEDIUM | Missed type annotation | mypy noise + future-refactor hazard |
| MEDIUM-2: no length guard on caller-supplied `signal_snapshot` | MEDIUM | Future-proofing gap | Unbounded Haiku input cost if a future caller passes unvalidated data |
| MEDIUM-3: `asyncio.run` inside sync function — not documented | MEDIUM | Future-refactor hazard | `RuntimeError: event loop already running` if moved into FastAPI |

All 5 actioned with 3 regression tests added (markdown-fence test, beat_cap test, signal-snapshot-truncation test + its complement). 349/349 tests pass after hardening, ruff clean. Total hardening effort: ~15 minutes.

**ROI calculus**: reviewer's 2 minutes of attention caught 2 silent-correctness bugs that unit tests alone missed (because the tests I wrote didn't exercise the failure-mode inputs — fence + tail-prose JSON, and clips with >50 beats). This is orthogonal coverage — tests verify behavior on KNOWN inputs; reviewers verify the input space ITSELF.

### Pattern worth entrenching

**Always dispatch `python-reviewer` after writing a new agent layer, before the commit.** The commit message should credit the findings. This is now part of my mental "definition of done" for agent-facing code.

### Other tools that fired during Phase 2

- `TodoWrite` — 8-item Phase 2 plan from P2.0 to P2.6, updated in real-time as each action completed. Prevented scope drift across 6 sub-actions and 83 tests.
- `Write` + `Edit` — 6 new files in `backend/agents/` and 5 new test files, plus surgical edits to `schema.py`/`writer.py`/`precompute.py`
- `Bash` for `pytest` + `ruff check` as a tight feedback loop — ran 8+ times across Phase 2, each <4 seconds
- `Read` for checking existing test patterns (`test_writer.py`, `test_precompute.py`) before writing new ones — prevented duplication of helper code

### Tools NOT used in Phase 2 (by design)

- `context7` — didn't need it; Pydantic v2 and Anthropic SDK 0.96.0 behavior was well-known
- `perplexity_*` — Phase 2 was pure implementation, no external research needed
- Any Vercel tool — Phase 2 is offline Python; Vercel surface is Phase 3+
- `e2e-runner` / Playwright — no UI yet (Phase 3)
- `devfleet` / parallel agents — Phase 2 was a single coherent author-one-file-at-a-time task, not parallelizable in the way Phase 1's 7 signals were

### Meta-learning on the hackathon ROI curve

The hackathon's tool-ROI peak is when **orthogonal specialists fire at the right moment**. Phase 2's single most valuable decision was NOT dispatching a swarm, but running ONE python-reviewer at the hand-off between "author wrote it" and "committed to main." The HIGH-1 fence bug would have survived every unit test I wrote — it needed a fresh set of eyes that understood the JSON-extraction-from-LLM problem space. That's a different skill from "author the code" or "write tests for the code." Right tool, right moment.

---

## Day 2.5 (Apr 22, evening) — Court Annotator Debugging Session

### The story in one paragraph

User opened `tools/court_annotator.html`, picked an MP4, nothing loaded. I iterated through 4 "reasonable next-try" fixes (dynamic DOM placement, faststart remux, preload attribute, file:// vs http:// protocol) — all red herrings. On iteration 5 I dispatched a research agent IN PARALLEL with instrumenting runtime diagnostics (`tagName` dump, 3-second timeout, direct-URL test button). Both paths converged on the same answer: **`<input type="file" id="video">` and `<video id="video">` shared `id="video"`**, so `document.getElementById("video")` returned the input. Every `video.*` operation was silently no-oping on the wrong element. One-character fix (rename input to `videoPicker`), 9 static validation tests, 3 commits, 1 faststart-remuxed clip, 4 new MEMORY entries.

### Tool ROI — the asymmetric insight

**Iterations 1-4 (serial next-try fixes):**
- 4 hypotheses tested, all wrong. Each took ~10 minutes. **Cumulative cost: ~40 minutes + user's patience.**
- The hypotheses were NOT unreasonable — each matched the symptom pattern. This is the trap.

**Iteration 5 (research-agent + runtime-diagnostic PARALLEL attack):**
- Dispatched `general-purpose` research agent in background with a detailed problem statement + ranked-causes request. **~75 seconds agent time.**
- Simultaneously built the runtime diagnostic (`tagName` in the 3-second dump). **~5 minutes authoring time.**
- Research agent returned 8 ranked causes — #2 (duplicate ID) matched instantly.
- Total iteration cost: ~5 minutes wall, 2 minutes of the agent's time. **Bug fixed same iteration.**

**ROI lesson — the 3-failure circuit breaker.** After iteration 3, the marginal value of another serial fix attempt approaches zero. Parallel escalation (research + diagnostics) costs ~5 minutes and cracks sticky bugs. This is codified in PATTERN-039.

### Tests-as-future-guards ROI

Wrote 9 static-validation tests (`tests/test_tools/test_court_annotator_html.py`). The most important ones:
- `test_no_duplicate_ids` — fails the build if ANY two HTML elements share an ID anywhere in `tools/*.html`.
- `test_video_id_is_on_video_element_not_input` — the SPECIFIC regression guard for this exact bug.
- `test_script_get_element_by_id_references_exist` — fails if inline script references a non-existent ID (typo/stale rename).
- `test_script_attaches_critical_media_listeners` — requires `loadedmetadata`, `error`, AND `loadstart` listeners. Absence of `loadstart` in the user's console was the smoking gun; future sessions will have that signal available by construction.

These tests took ~8 minutes to write. They prevent the same 45+ minutes of debugging from EVER recurring, AND they encode the lesson at a level where a future session's author doesn't need to read MEMORY.md to avoid the trap — the build just fails.

### Tools that FIRED during this debugging session

- `Bash` for `ffprobe` / atom-walker Python snippet — diagnosed the faststart issue (iteration 2, red herring but taught us what to check).
- `Bash` for `ffmpeg -movflags +faststart` — remuxed the clip (iteration 2 action).
- `Bash` for `python -m http.server 8000` — served via localhost (iteration 4).
- **`Agent` (general-purpose, background, run_in_background=true)** — THE high-ROI tool of the session. Detailed problem statement with ranked-causes format request returned an 8-item causes list in 75 seconds, one of which (duplicate ID) matched exactly.
- `Write` + `Edit` — annotator HTML refactor + test file creation.
- `Grep` — found all `id="video"` instances (confirmed the collision).

### Tools NOT used (noteworthy for future sessions)

- `Claude_Preview` MCP (preview panel) — preview DID render the file but it's not equivalent to a real browser session for `<input type="file">` interactions. Chrome in a dedicated window was needed.
- `e2e-runner` / Playwright — could have automated the reproduction but probably overkill for a single-tool HTML file.
- `perplexity_*` research — the general-purpose agent with Web access was the right tool here (research agent has reasoning + source-citing abilities that raw Perplexity queries don't).

### Meta-pattern: "silent correctness" bugs are deceptive

Duplicate HTML IDs are syntactically VALID. `<input>.src = blobURL` is a harmless no-op that doesn't throw. `addEventListener` attaches to any EventTarget. Every browser layer happily cooperated with the wrong pointer. When symptoms match a dozen real bugs (codec, CORS, autoplay, network, MSE), pattern-matching leads you toward familiar fixes — not toward questioning whether your variable even points to the right element.

**The single-biggest preventive move:** when something silently no-ops, IMMEDIATELY log `element.tagName` before any other debugging. If it's not what you expect, you've found the bug. Our 3-second diagnostic timeout in the annotator now includes `tagName` in the dump — future sessions will catch this class of bug at iteration 1.

---

## Day 2 evening / Skeleton Sanitation Sprint — HIGHEST-ROI DEBUG SESSION SO FAR

The bimodal-histogram diagnostic pattern that broke open the Skeleton Sanitation investigation is the single highest-ROI tool-use pattern in the project. Worth studying.

### The debug sequence (20-minute forensic sweep)

| Tool | Action | What it revealed |
|---|---|---|
| Image MCP | Read 11 screenshots from `screenshot_errors/` | Characterized failure modes visually: ghosts in mid-court, edge-clinging, mis-scale, zero Player B |
| `grep -n + Read` | Opened `backend/cv/pose.py:assign_players` | Found the selector used `mean_keypoint_confidence` as tiebreaker, ignored `bbox_conf` |
| Python `json` + `statistics` | Ran bucketed histogram of `bbox_conf` across 1731 detections | **THE BREAKTHROUGH** — revealed bimodal distribution: 55.7% <0.05 (ghosts), 44.3% ≥0.5 (real), empty 0.2–0.5 gap → 0.5 cutoff is obvious |
| `subprocess.run(ffmpeg)` + inline YOLO | Extracted frame 1200 + ran inference directly, bypassing assign_players | Proved Player B truly invisible at ANY imgsz — detector-capacity limit, not pipeline bug |
| `assign_players` replay | Manually ran the function on the extracted frame's raw detections | Confirmed the remaining edge case: high-conf "far player" detections are actually crowd members whose feet project off-court |

**Total wall time**: ~20 minutes from screenshot inspection to definitive root-cause diagnosis.

### Tool ROI observations

- **Real-data histogram over synthetic-test-fixture checking**: ~100x the diagnostic power per minute. The mocked tests for `assign_players` used HAND-CRAFTED detections with plausible bbox_conf; they could never surface the REAL YOLO-at-conf=0.001 pathology. PATTERN-038 applied to CV: mocked tests validate shape of our code, not shape of data reality.
- **Image MCP for screenshot inspection**: reading the 11 error screenshots took ~2 minutes and gave failure-mode categorization that would have taken 10+ minutes to extract from verbal description. Worth always including when user reports visual bugs.
- **Inline `ffmpeg` subprocess for frame extraction**: avoided standing up a full debugging harness. One-shot `ffmpeg -vf "select=eq(n\,1200)"` grabs a specific frame for manual YOLO interrogation.
- **`np.nanvar/nanmax/nanmin` + bucketed histograms**: the numerical-diagnostic toolkit that surfaces bimodality / trimodality / heavy-tail patterns. Always try these BEFORE assuming "it's probably a bug in code X."

### New patterns entrenched

1. **When UI misbehaves on real data, INSTRUMENT the real data first, not the code.** Run a histogram/quantile over every numerical field before assuming the problem is in the logic.
2. **PATTERN-038 (mocked tests validate our-call shape, not API shape) has a CV analog**: mocked test fixtures validate the code path, not the pathology the real detector produces. Add ONE integration-smoke-test assertion for every new model-in-the-loop layer.

### V6 Crucible ROI table (post-Skeleton Sanitation Sprint)

| Metric | V4 (pre-fix) | V6 (post-fix + single-player pivot) |
|---|---|---|
| Player A detections | 1731 (96.2%, 55.7% ghosts) | 806 (44.8%, 0% ghosts) |
| `bbox_conf < 0.5` ghost count | 964 | **0** |
| `x_m` range | [-0.92, 12.95] (edge-clinging) | [1.38, 11.46] (clean) |
| Coach insights with real anchors | ~0 (all "warm-up artifacts") | 4 of 4 (e.g., "baseline_retreat collapsed 1.67m → 0.10m") |
| HUD layouts with B widgets | 4 (MomentumMeter etc.) | **0** (verified via set check) |
| Narrator "Djokovic/Federer" hallucinations | present | zero |
| Tests | 381/381 | 383/383 |
| Wall time | 2:24 | 2:30 |
| API spend | ~$0.30 | ~$0.30 |

---

## Day 3 (Apr 23 — Phase 3 Next.js HUD continuation)

(To be populated as Phase 3 visual polish, motion animations, and HUD widget library development progresses.)

---

## Phase 5 (Apr 23 afternoon → evening — Demo Polish + Vercel Production Deploy; PR #4 merged)

### HIGH-IMPACT tools/patterns this session

| Tool / Pattern | Outcome | ROI | Notes |
|---|---|---|---|
| `/vercel:vercel-cli` skill (documentation-only, no command wrappers) | Reading `references/environment-variables.md` clarified the `vercel env add NAME preview "" --value "..." --yes --sensitive` positional-arg pattern and the `printf %s \| pipe` discipline | HIGH (saved 1 failed deploy attempt, ~10 min turnaround) | The skill is pure guidance — it did NOT wrap a command. Knowledge transfer from skill reference → PATTERN-056. Entry worth capturing because the skill type (documentation-only, no executor) is easy to under-use; you have to actively READ it, not just invoke it. |
| Claude-GitHub-Action `@claude` PR-review bot (landed in `a64533b`) | PR #4: `@claude please review` comment triggered a full orthogonal review in ~3 min. Caught unstable `key={i}`, lost Tab 2 streaming progress counter, vercel.json glob breadth, hardcoded hex vs design-token, `buildTimeline` double-invocation | HIGH (one comment = multi-lens review, zero marginal cost) | Addressed quick wins in same PR (`787a5d1`), deferred perf/style nits with rationale. See https://github.com/andydiaz122/panopticon-live/pull/4#issuecomment-4308215489 |
| `vercel curl --deployment <url> /<path> -- -I` | Post-deploy asset verification for `public/match_data/*.json` + `public/clips/*.mp4`. Confirmed `Content-Type`, `Content-Length`, `Accept-Ranges: bytes` on the MP4 before declaring deploy green | MEDIUM (turns "I think it works" into "I know these URLs returned 200") | Preferred over plain `curl` because it auto-authenticates against protected preview deploys and attaches the deployment ID. See PATTERN-058. |
| `vercel logs --deployment <url> --no-follow --limit N --expand --status-code 500` | Surfaced the Turbopack-strip error (`The module has no exports at all`) + later the Anthropic 401 errors (driven by GOTCHA-020 newline corruption) from the Serverless Function logs | HIGH (runtime debugging for Server Actions that 500 on Vercel; unblocked GOTCHA-019/020 diagnosis) | `--status-code 500` filters to failures; `--expand` dumps full stack trace. Entry-point for any Server Action debug flow. |
| TelemetryLog refactor (`telemetry.ts` + `TelemetryLog.tsx`) | Extracted 115 lines of shared primitives from `SignalFeed.tsx` into a library module; new 192-line `TelemetryLog` component takes props for filter/height/density; slotted 2× in Tab 1 + 1× in Tab 2 with zero visual regression | HIGH-ROI (one refactor unlocked three consumer slots; no bundle bloat) | Captured as PATTERN-055. Net diff: 388 insertions / 248 deletions in 5 files; SignalFeed.tsx shrank from 250 lines to ~80 lines. |
| `anthropic` TypeScript SDK + Turbopack `'use server'` interaction | Discovered GOTCHA-019 empirically (local worked, Vercel build stripped the module). Fix moved config from `actions.ts` to `vercel.json` | CRITICAL | Would have cost the demo if only caught on Sunday. Caught Thu afternoon with time to fix. |

### Skills that FIRED during Phase 5

- `/vercel:vercel-cli` (documentation reference for env-var CLI)
- `vercel-ts-server-actions` (route-segment config placement; led to GOTCHA-019 fix)
- `panopticon-hackathon-rules` (prime directive: demo criterion + CLAUDE.md React architecture rules)
- `coding-standards` (TS/React idioms — implicit; enforced by `typescript-reviewer` + PR-review bot)

### Skills QUEUED but NOT USED in Phase 5

- `hackathon-demo-director` (recording script — Phase 5 NEXT action, but Sun Apr 26 is the actual recording day)
- `e2e-runner` / Playwright (would have validated TelemetryLog integration; deferred because pure-function vitest coverage is adequate and demo clip will be visually verified Sat-Sun)
- `claude-api` / `agent-harness-construction` (Phase 2 wiring already stable; no new agent work in Phase 5)
- `2k-sports-hud-aesthetic` / `awwwards-animations` / `top-design` (visual polish already landed in Phase 3.5; Phase 5 was deploy + DRY refactor, not new visuals)

### Agents that FIRED during Phase 5

- `claude` GitHub-Action reviewer (invoked via `@claude please review` comment on PR #4) — returned 5 findings; 2 addressed in same PR, 3 deferred with rationale.
- No local sub-agents invoked (Phase 5 was orchestration-light: refactor + deploy + PR review loop, no fleet dispatches or parallel tasks).

### Anti-patterns dodged this session

- **#29 (redundant tool inventory)** — used existing skill references + system-reminder tool list; no tool-cataloging agent dispatched.
- **#32 (bypassing quality-preserving commands)** — `@claude please review` IS the canonical review wrapper; used directly on the PR comment rather than dispatching a raw `code-reviewer` agent via Task.
- **#18 (ignoring skills)** — `/vercel:vercel-cli` reference was actively consulted for PATTERN-056; skill was NOT skipped despite being documentation-only (easy to under-use).

### Anti-patterns we hit (and recovered from)

- **Re-learning GOTCHA-018's class** — GOTCHA-020 is a closely related hidden-byte corruption that I should have anticipated given the recency of GOTCHA-018. Recovery: captured both as cross-linked entries so the next session sees BOTH mechanisms. The meta-lesson is that "same symptom, different upstream cause" deserves its own numbered entry rather than folding into the existing GOTCHA.
- **Anomaly injection v1 without layout-lookup** — GOTCHA-021. Fixed same session by re-injecting into layout-visible signals. Root cause was "mutating the raw data without consulting the curation filter." Captured.

### Meta-learning this session

**Phase 5 had three distinct sub-phases, each demanding a different tool discipline**:

1. **Demo-data authoring** (morning → afternoon) — anomaly injections. Tool: `jq` + Python `json` edits directly against the golden JSON. Lesson: ALWAYS pre-check the curation filter (HUD layout widget list at target timestamp) before mutating. → GOTCHA-021.

2. **DRY refactor** (mid-afternoon) — TelemetryLog. Tool: Read/Edit/Write on the dashboard source tree; vitest for regression. Lesson: pure-function extraction into a `lib/` module BEFORE component authoring enables three consumers with no duplication. → PATTERN-055.

3. **Production deploy + PR review** (evening) — Vercel wire-up. Tool: `vercel` CLI + `@claude` PR bot + `vercel curl` asset verification + `vercel logs` for debugging. Lesson: the deploy surface is unforgiving; one reliable incantation per task is worth more than three almost-right ones. → GOTCHA-019/020, PATTERN-056/058, WORKFLOW-005, DECISION-010.

The combined session shipped PR #4 with 4 commits and no hot-fix revert. That's the bar for Phase 5 velocity. Phase 6 (Sat polish + Sun record) should preserve this cadence.

### Artifacts

- Preview URL: `panopticon-live-1fqx9c4iz-dmg-decisions.vercel.app` (as of PR #4 merge)
- 4 commits merged to main: `4f9df37` (force-add assets) → `b20c370` (vercel.json maxDuration fix) → `888acb5` (anomaly injection + TelemetryLog slots) → `787a5d1` (PR-review feedback — stable keys + Tab 2 progress counter)
- PR #4 URL: https://github.com/andydiaz122/panopticon-live/pull/4

---

## Phase 6 (Apr 24 — Demo Production Planning Kickoff)

### HIGH-IMPACT tools/patterns this session

| Tool / Pattern | Outcome | ROI | Notes |
|---|---|---|---|
| 3 parallel research agents (Explore + 2× `general-purpose`) | Parallelized codebase audit + video-production tooling research + creative/strategic research into ~8 min wall-clock. Produced the narrative-vs-code drift finding (GOTCHA-022), the Remotion hybrid pattern (PATTERN-059), the Sportradar visual-language reference (PATTERN-060) | HIGH (saved ~90 min of sequential time; the narrative-drift finding alone prevented a demo-killing claim getting into voice-over) | Codified as WORKFLOW-006 — default for any phase-kickoff going forward. |
| `@remotion/mcp` (install planned Saturday) | Programmatic React-based video composition for opening title / scene breaks / closing URL card / Managed Agents fan-out graph | Expected HIGH for chrome rendering (~30 s of the 3-min video). Chrome-only scope = ~6 h to ship | Paired with the Remotion Agent Skills pack (`bunx skills add remotion-dev/skills`) so Claude Code generates opinionated Remotion code without hallucinated imports. PATTERN-059. |
| Remotion Agent Skills pack | Expected: eliminates hallucinated imports / outdated-API patterns when Claude Code authors Remotion compositions | Expected MEDIUM (saves ~30 min of compile-fix loop) | Install Saturday alongside `@remotion/mcp`. |
| ElevenLabs MCP | Stretch goal: higher-production voice-over if time permits after MacBook-mic primary take is done | Expected MEDIUM-LOW (reasonable default is MacBook mic; ElevenLabs is polish) | Skip if Saturday build sprint eats the time budget. |
| OBS Studio | Primary live-capture of dashboard (~2:30 of the 3-minute video) | Expected CRITICAL — the hero of the demo is the live dashboard | Backup option: Playwright recording if OBS jitters. |
| DaVinci Resolve Free | Sunday final-cut tool: assemble OBS live-capture + 4 Remotion compositions + voice-over track + music bed | Expected HIGH — Free tier is sufficient for a 3-min 1080p export | No timeline experience needed; 4 cuts + audio alignment only. |
| Canva MCP | Fallback for architecture diagram + YouTube thumbnail if Remotion chrome hits a blocker | Expected LOW-MEDIUM (only fires if Remotion fails) | Keep in reserve. |
| Figma MCP | Reference-only: pull Sportradar aesthetic screenshots for the `AnnotationOverlay` design study (A2) | Expected LOW (A2 is deprioritized) | Skip if A2 doesn't land. |
| Playwright (backup live capture) | Alternative to OBS if OBS jitters or screen-capture permission fails | Expected LOW-MEDIUM — only fires as fallback | Covered under `e2e-runner` agent infra. |

### Skills that FIRED this session

- `explore` agent (codebase audit — caught the narrative-vs-code drift).
- 2× `general-purpose` agents (video-production tooling + creative/strategic research).
- `documentation-librarian` (this documentation-consolidation pass).

### Skills QUEUED for Saturday (Apr 25)

- `hackathon-demo-director` — recording script + storyboard-to-shot-list translation.
- `2k-sports-hud-aesthetic` — final-polish pass on any HUD widgets that need refinement before OBS takes.
- `biometric-fan-experience` — copy-pass on signal labels / physiology captions for fan-facing readability.

### Skills NOT USED (intentional) — Citadel-level discipline

- `frontend-slides` — not a slide-format demo. Panopticon is a live dashboard; chrome is Remotion, not slide deck.
- `awwwards-animations` — over-kill for 30 s of chrome animations. Remotion primitives are sufficient; awwwards patterns add complexity without proportional demo-criterion impact.
- `agent-harness-construction` — Phase 2 Opus wiring is stable and shipped. No new agent scaffolding in Phase 6.
- `claude-api` — no new Anthropic SDK calls; existing Tab 3 Server Action is the surface.
- `vercel-ts-server-actions` / `/vercel:vercel-cli` — deploy is green; no new Vercel surface in Phase 6 (all chrome lives in Remotion output, not Vercel).

### Anti-patterns DODGED this session

- **#22 (push content DOWN, leave pointers UP)** — new rules / tone guidance went into nested `demo-presentation/CLAUDE.md` (under 200 lines), NOT into parent `CLAUDE.md`. Parent stays at 95 lines.
- **#29 (redundant tool inventories)** — no tool-inventory agent dispatched. System-reminder MCP list provided every tool surface at zero token cost; the three research agents were each pointed at an orthogonal research question, not at tool discovery.
- **#32 (bypassing quality-preserving commands)** — used `documentation-librarian` skill invocation (this agent) rather than raw Write-orchestration from the parent session.
- **#17 (parallel on dependent tasks)** — the three research agents were truly orthogonal (code audit vs. tooling research vs. creative research); none of them depended on another's output. Synthesis happened in the parent session after all three returned.
- **#34 (skipping local-archive sweep)** — the tennis-footage inventory and codebase-state audit are instances of the same pattern: look locally before dispatching external research.

### Meta-learning this session

The 3-parallel-research-agent pattern (WORKFLOW-006) is now the default for any phase kickoff — the wall-clock win (30 min vs. 2 h) is the headline, but the structural win is *orthogonality by construction*. Each agent owns one research lens (code / tooling / creative), and synthesis in the parent session surfaces cross-lens findings (e.g., the narrative-vs-code audit fed directly into storyboard tone calibration, which fed into the Remotion hybrid decision). Sequential research would have missed those cross-lens connections because each research pass would have been scoped tightly to its own question.

Secondary meta-learning: **the user's AskUserQuestion batch is a design choice, not a convenience**. Batching 4 questions into one turn forces us to identify the *highest-leverage* decision points and model their interdependencies upfront. One-at-a-time questions produce sequential anchoring bias and cost more turns.

### Artifacts

- `demo-presentation/CLAUDE.md` (rules + tone guide, under 200 lines).
- `demo-presentation/PLAN.md` (storyboard + timeline + assets + open questions).
- `~/.claude/plans/phase-6-demo-production.md` (strategic trail, ~80 lines).
- `demo-presentation/{assets/references, scripts, remotion, audio, renders}/` (directory skeleton for Saturday's build sprint).
- No commits this session (docs consolidation is a read-only audit + synthesis pass; Andrew will audit + commit himself per task instructions).

### Phase 6 continued (Apr 24 Fri PM) — Dialectical Steelman Sprint

After the morning kickoff (3-parallel-research pass captured above), ran a 4-iteration dialectical-mapping steelman Friday evening (~90 min wall-clock) to stress-test the plan before Saturday's build sprint. Single-session tool ROI addendum below.

| Tool / Pattern | Outcome | ROI | Notes |
|---|---|---|---|
| `.claude/skills/dialectical-mapping-steelmanning` (invoked via `/dialectical-mapping-steelmanning`) | 4 iterations × 2 orthogonal Agent calls = 8 agent passes; ~30 distinct non-obvious findings (GOTCHA-024 through 028, PATTERN-061 through 066, DECISION-012/013, WORKFLOW-007) | **HIGHEST-ROI skill invocation of Phase 6 planning** | Orthogonal Alpha/Beta pair structure is the operative mechanism, not the number of agents or the agent type. Captured as WORKFLOW-007. |
| `mcp__perplexity__perplexity_search` + `mcp__perplexity__perplexity_ask` | Grounded all 8 iteration agents against 2025–2026 sources: GitHub OBS issues #10636 + #2760 + forum 192890 (GOTCHA-024); Remotion docs + Rosetta 2 runtime (GOTCHA-025); Anthropic Opus 4.7 release notes + SDK thinking-block semantics (GOTCHA-026); YouTube Creator Content ID + HD-lock + new-channel upload cap behavior (GOTCHA-027); Vercel April 2026 security incident reports + env-var rotation playbook (GOTCHA-028); ChaplinAI / Advids / Guidejar demo-video research (PATTERN-065); Greg Ceccarelli Aug 2025 + #BuiltWithClaude Screen Demo Skill + Anthropic 16-min live-build video (PATTERN-062); post-winner X/Discord amplification audit (PATTERN-066) | **HIGH** — citations distinguish "model priors" from real 2025–2026 reality; without Perplexity grounding, Iter-1 GOTCHA-024 would have been a guess instead of three independent corroborating sources | Required ≥ 3 external citations per agent pass. Non-Perplexity-grounded iterations collapse to noise. |
| Orthogonal Alpha/Beta agent pair per iteration | Surfaced convergent-failure findings: Iter-2 Skeptic AND Iter-3 narrative-arc lens independently flagged the Managed Agents animated Scene 5B as net-negative → DECISION-012 cut. Two orthogonal lenses converging on the same finding is higher-confidence than either single lens. | **HIGH** | This is the "convergence signal" that Iter-1 single-agent runs cannot produce. |
| Iteration convergence-based stopping rule | Declared diminishing returns at Iter 4 (net-new findings/iteration dropped below the 3 threshold; Iter 5–10 projected to fall further). Saved ~2 h of diminishing-return iterations AND preserved Saturday build time. | **HIGH** | Hard threshold, not "one more for safety." Iter 4 itself was the highest-signal iteration — stopping at 2 iterations would have missed PATTERN-066 + GOTCHA-028 entirely; stopping later than 4 would have been wasted. |

#### Meta-learning — orthogonal prompt framing > agent-type difference

All 8 iteration agents were `general-purpose` subagents; the orthogonality that generated net-new insight came from PROMPT framing (risk/skeptic vs creative/builder), not from agent-type selection. This re-confirms a pattern visible earlier in the project (Phase 5 PR-review bot vs. local `python-reviewer`): the judgmental lens is what matters; the agent-type is mostly plumbing. For future multi-agent review panels, design the lens set BEFORE choosing agent types — picking agent types first anchors on "what tools do I have" instead of "what failure modes do I need to cover."

#### Artifacts updated (this session)

- `/Users/andrew/Documents/Coding/hackathon-demo-v1/MEMORY.md` — DAY 3 CONTINUED section (5 GOTCHAs + 6 PATTERNs + 2 DECISIONs + 1 WORKFLOW).
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/FORANDREW.md` — Friday PM subsection under 2026-04-24 Phase 6 Demo Production Kickoff.
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/demo-presentation/PLAN.md` — storyboard v4 Detective Cut + risk-stratified add-ons + Sat/Sun timeline (updated in parallel to this docs pass).
- `/Users/andrew/Documents/Coding/hackathon-demo-v1/demo-presentation/CLAUDE.md` — narrative discipline refinement (updated in parallel to this docs pass).
- `/Users/andrew/.claude/plans/pull-from-remote-main-humble-forest.md` — iteration trail §10 + master plan §11.
