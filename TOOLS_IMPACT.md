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

## Day 3 (Apr 23 — Phase 3 Next.js HUD PENDING)

(To be populated when frontend work begins.)
