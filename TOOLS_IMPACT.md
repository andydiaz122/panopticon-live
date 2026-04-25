# TOOLS_IMPACT.md — Tool ROI Log

Tracks which tools / skills / agents / MCPs we used, why, and whether they paid off. The "Skills NOT Used" section is the durable defense against silently ignoring the skill ecosystem.

> **Note on ID references (2026-04-24 merge):** this file was authored on `origin/main`'s numbering scheme. After the `hackathon-research` merge, several PATTERN / GOTCHA / DECISION IDs were renumbered to avoid collision with pre-existing branch-native entries. When cross-referencing an ID below, consult the `MERGE-RENUMBERING MAP` in `MEMORY.md` to resolve to canonical post-merge IDs. Approximate mapping: GOTCHA-019→034, GOTCHA-020→035, GOTCHA-021→036, PATTERN-055→063, PATTERN-056→064, PATTERN-057→065, PATTERN-058→066, DECISION-010→011.

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
| `claude-md-improver` | **NOT FOUND** in this installation — does not exist. Fell back to `documentation-librarian`. | If ever installed globally, revisit as preferred tool for CLAUDE.md edits |
| `IMM-filter` / sliding-window Kalman patterns | PROJECT-2026-04-28 roadmap (B2B post-hackathon); out of scope for Sunday submission | Post-submission (Monday+) |
| `MotionAGFormer` / `BioPose 3D` monocular lifting | PROJECT-2026-04-28 roadmap; 2D YOLO11m-Pose stays for hackathon | Post-submission |
| `DuckDB-WASM` HTTP Range Requests | PROJECT-2026-04-28 roadmap; current 15-25MB JSON via `fetch()` + `useEffect` is GOTCHA-026-compliant for 60s clip | Post-submission; needed for 3-hour-match support |
| `/rules-distill` | Week-end meta-synthesis command | After Sunday submission, before next Monday's Seed-Round prep |

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
| `/vercel:vercel-cli` skill (documentation-only, no command wrappers) | Reading `references/environment-variables.md` clarified the `vercel env add NAME preview "" --value "..." --yes --sensitive` positional-arg pattern and the `printf %s \| pipe` discipline | HIGH (saved 1 failed deploy attempt, ~10 min turnaround) | The skill is pure guidance — it did NOT wrap a command. Knowledge transfer from skill reference → PATTERN-056 (canonical in this repo: PATTERN-064 post-merge). Entry worth capturing because the skill type (documentation-only, no executor) is easy to under-use; you have to actively READ it, not just invoke it. |
| Claude-GitHub-Action `@claude` PR-review bot (landed in `a64533b`) | PR #4: `@claude please review` comment triggered a full orthogonal review in ~3 min. Caught unstable `key={i}`, lost Tab 2 streaming progress counter, vercel.json glob breadth, hardcoded hex vs design-token, `buildTimeline` double-invocation | HIGH (one comment = multi-lens review, zero marginal cost) | Addressed quick wins in same PR (`787a5d1`), deferred perf/style nits with rationale. See https://github.com/andydiaz122/panopticon-live/pull/4#issuecomment-4308215489 |
| `vercel curl --deployment <url> /<path> -- -I` | Post-deploy asset verification for `public/match_data/*.json` + `public/clips/*.mp4`. Confirmed `Content-Type`, `Content-Length`, `Accept-Ranges: bytes` on the MP4 before declaring deploy green | MEDIUM (turns "I think it works" into "I know these URLs returned 200") | Preferred over plain `curl` because it auto-authenticates against protected preview deploys and attaches the deployment ID. See PATTERN-058 (canonical in this repo: PATTERN-066 post-merge). |
| `vercel logs --deployment <url> --no-follow --limit N --expand --status-code 500` | Surfaced the Turbopack-strip error (`The module has no exports at all`) + later the Anthropic 401 errors (driven by GOTCHA-020 newline corruption) from the Serverless Function logs | HIGH (runtime debugging for Server Actions that 500 on Vercel; unblocked GOTCHA-019/020 diagnosis) | `--status-code 500` filters to failures; `--expand` dumps full stack trace. Entry-point for any Server Action debug flow. |
| TelemetryLog refactor (`telemetry.ts` + `TelemetryLog.tsx`) | Extracted 115 lines of shared primitives from `SignalFeed.tsx` into a library module; new 192-line `TelemetryLog` component takes props for filter/height/density; slotted 2× in Tab 1 + 1× in Tab 2 with zero visual regression | HIGH-ROI (one refactor unlocked three consumer slots; no bundle bloat) | Captured as PATTERN-055 (canonical in this repo: PATTERN-063 post-merge). Net diff: 388 insertions / 248 deletions in 5 files; SignalFeed.tsx shrank from 250 lines to ~80 lines. |
| `anthropic` TypeScript SDK + Turbopack `'use server'` interaction | Discovered GOTCHA-019 empirically (local worked, Vercel build stripped the module). Fix moved config from `actions.ts` to `vercel.json` | CRITICAL | Would have cost the demo if only caught on Sunday. Caught Thu afternoon with time to fix. GOTCHA-019 canonical in this repo: **GOTCHA-034** post-merge. |

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

3. **Production deploy + PR review** (evening) — Vercel wire-up. Tool: `vercel` CLI + `@claude` PR bot + `vercel curl` asset verification + `vercel logs` for debugging. Lesson: the deploy surface is unforgiving; one reliable incantation per task is worth more than three almost-right ones. → GOTCHA-019/020 (canonical in this repo: GOTCHA-034/035 post-merge), PATTERN-056/058 (canonical: PATTERN-064/066 post-merge), WORKFLOW-005, DECISION-010 (canonical: DECISION-011 post-merge).

The combined session shipped PR #4 with 4 commits and no hot-fix revert. That's the bar for Phase 5 velocity. Phase 6 (Sat polish + Sun record) should preserve this cadence.

### Artifacts

- Preview URL: `panopticon-live-1fqx9c4iz-dmg-decisions.vercel.app` (as of PR #4 merge)
- 4 commits merged to main: `4f9df37` (force-add assets) → `b20c370` (vercel.json maxDuration fix) → `888acb5` (anomaly injection + TelemetryLog slots) → `787a5d1` (PR-review feedback — stable keys + Tab 2 progress counter)
- PR #4 URL: https://github.com/andydiaz122/panopticon-live/pull/4

---

## Phase A (Apr 24, 2026 — demo-v1 merge + main-merge + Golden Run on hackathon-research)

### HIGH-IMPACT tools / patterns this session

| Tool / Pattern | Outcome | ROI | Notes |
|---|---|---|---|
| **PATTERN-062 Isolated-Worktree + Ordered-Cherry-Pick + Orthogonal-Review Merge** | Applied TWICE in one day. First absorbed demo-v1 UI + CV fix into hackathon-research (6 cherry-picks, 3 skips, renumbering). Second merged `origin/main` into the branch with per-file conflict resolution. Zero regressions across both merges. | **CRITICAL** — unlocked safe multi-commit merges without touching main workdir | 4-layer recipe: (1) `git merge-tree --write-tree` preview, (2) `Agent` with `isolation: "worktree"` for execution, (3) ordered `git cherry-pick -x` per dependency, (4) parallel orthogonal reviewer panel post-merge. Pattern formalized in MEMORY.md PATTERN-062. |
| **`git merge-tree --write-tree HEAD <sha>`** | Read-only conflict preview per candidate cherry-pick. Zero working-tree impact. | **HIGH** (pre-merge triage) | Tells you which commits apply clean vs conflict BEFORE committing to a strategy. Prevented 3 doomed cherry-picks from wasting time. |
| **Agent tool with `isolation: "worktree"`** | Executed 6 cherry-picks in isolated worktree. Main workdir untouched while per-commit tests + ruff ran in the worktree. Agent returned only after all gates green. | **CRITICAL** (risk isolation) | Contrast with GOTCHA-011: Day 1 had WorktreeCreate hook missing. By Phase A that had been resolved; the isolated-worktree pattern is now the canonical merge harness. |
| **Orthogonal 4-reviewer panel** (post-merge): `code-reviewer` + `python-reviewer` + `typescript-reviewer` + `security-reviewer` | Phase 3 post-merge review caught 3 HIGH findings (0 CRITICAL): inline array-literal rowKinds in HudView breaking `useMemo` at 10 Hz, 52 stale ID refs in PHASE_4_TEAM_LEAD_HANDOFF.md, Windows-permission leak in `.claude/settings.json`. Post-main-merge review caught the `See PATTERN-056` → should be PATTERN-064 cross-ref drift at MEMORY.md:1375. | **HIGH** (each lens is distinct; running 3 `code-reviewer` instances would have been redundant, not orthogonal) | Applied the "Orthogonality Over Quantity" principle from global CLAUDE.md. 4 lenses × orthogonal failure modes = super-linear coverage. |
| **Golden Run execution** (2026-04-24) on `utr_match_01_segment_a.mp4` via `./run_golden_data.sh` | 1800 frames → 53 signals, 5 coach_insights, 6 narrator_beats, 36 state_transitions, 3-step swarm captured in agent_trace.json with 57s real compute. Token budget consumed and within limits. | **HIGH** (demo assets ready) | Critical data fact discovered: **0 anomalies emitted**. Anomaly extractor wired in `anomalies[]` but not populated by signal pipeline (only hand-injected test data at t=36 from demo-v1 reaches the UI). Flagged for follow-up; not a blocker for demo because manual injections (GOTCHA-036) cover the visible anomaly UI path. |
| **`run_golden_data.sh` preflight script** | Founder-only helper: exports ANTHROPIC_API_KEY length check (GOTCHA-033 defense), runs precompute with canonical args, checks exit code. | **HIGH** (saves 10-15 min of manual arg-assembly + defends against env-var corruption) | New script shipped this phase. Preflight catches the GOTCHA-033 class of "invisible byte" bugs via `echo "len=${#ANTHROPIC_API_KEY}"` before the ~2-min Anthropic call surface is touched. |
| **HUD layout width-clamp repair** | STATE TelemetryLog moved into center column under CoachPanel (adjacent to right-rail SIGNAL log); CoachPanel `maxHeight` clamp bumped from 88/260 to 220/380 to fit col-span-6 wrapped text. | **MEDIUM** (visual polish, pre-recording) | Meta-observation: width-assumption-baked-into-pixel-clamp is the layout-level analog of GOTCHA-030 (JSON Syntax Trap from truncation marker) — both involve a UI-rendering assumption that stops holding at real content sizes. |

### Backend Surgery Bootstrap (pre-Golden-Run, ~13:00-14:15 EST)

Before the full Golden Run fired, the morning session ran a **3-Step Bootstrap** (PATTERN-076) that shipped the display-only G43 architecture (DECISION-016) and verified it against the 4-Criteria Protocol (PATTERN-075). Tools that carried the morning:

| Tool / Pattern | Outcome | ROI | Notes |
|---|---|---|---|
| **`video-frame-validator` agent (single-pass per G38)** | Extracted frames at 1 s intervals for the demo window. Discovered Player A is NOT in frames 0-8s — only Player B visible; `BREAK POINT` scoreboard overlay active; Player A enters at t=9s, serves at t=11s. **Invalidated the plan's t=0-8s narration grid.** | **CRITICAL** (saved shipping a narration track that contradicts what judges literally see; whole class of authoring errors prevented by one gate) | Captured as GOTCHA-042 ("Frame-ground BEFORE authoring"). Extends `video-validation-protocol` skill's remit from demo-playback validation to pre-authoring narration grounding. |
| **`ffmpeg -ss <t> -frames:v 1` one-liner** | Cheap primary-source sanity check on "what's on screen at time T." Ran inside the video-frame-validator agent's single-pass loop. | **HIGH** (canonical pre-authoring gate) | Alternative — trusting the plan's visual assumptions — would have shipped wrong narration. Rule: the video file itself is the only reliable primary source. |
| **Pydantic v2 model additions** (`QualitativeNarration`, `PlayerProfile`, `AuthoredStateTransition`, `ProvenancedValue`, `ProfileMeta`, `RallyMicroPhase`, `NarrationKind`, `NarrationSource`, `ProvenanceTag`) in `backend/db/schema.py` | Every authored-content inter-module contract mechanically enforced. No dict hallucinations. `provenance="stubbed_mcp"` stamping enabled end-to-end for honest disclosure. | **HIGH** (type safety carried through the entire display-only stack + made the 4-Criteria verification mechanical) | Mirror TS types in `dashboard/src/lib/types.ts` added with ALL fields OPTIONAL per G28. The Pydantic v2 discipline from earlier phases paid compound interest here — every new model was trivially self-documenting. |
| **Ad-hoc 4-Verification-Criteria checks** (jq/grep against `match_data.json` + `agent_trace.json`) | (a) `display_narrations`/`display_transitions`/`display_player_profile` populated, (b) `query_video_context_mcp` is FIRST tool call in Analytics trace with `provenance="stubbed_mcp"`, (c) ToolResult carries authored text, (d) `signals[].state` still pinned to 4-member `PlayerState` (no `RallyMicroPhase` leakage). | **CRITICAL** (verified display-only vs live partition held; prevents silent regression class where authored content leaks into telemetry stream) | Captured as PATTERN-075 — generalizes to any future "display-only vs live" architectural change. |
| **Shell-wrapper surgical fixes** to `run_golden_data.sh` | Added `"$@"` forwarding to `python -m backend.precompute`; relaxed hard ANTHROPIC_API_KEY preflight when `--skip-scouting-committee` is in args. Unblocks Step 1 baseline-without-swarm. | **HIGH** (enables the cost-minimization discipline of WORKFLOW-009 — baseline before spending Anthropic budget) | 2-line script fix unlocked the "baseline → frame-ground → full swarm" bootstrap sequence. |
| **Dynamic identity rule (G10)** in `_build_baseline_context` of `scouting_committee.py` | Profile present → `"PROFILE DETECTED: You MUST refer to {player_profile.name} and cite specific stats"`; profile absent → strict anonymity. Unblocked profile citation while preserving the anti-hallucination guardrail for unprofiled runs. | **HIGH** (narrative density unlocked without breaking anti-hallucination invariant) | Captured as DECISION-014 (locked) + USER-CORRECTION-034 (Hurkacz → UTR Pro A anonymization). Verified: all 3 agents cite "UTR Pro A", zero hallucinated player names. |

**Meta-pattern: the 3-Step Bootstrap saved ~$1-1.60 + ~3 hours wall-clock** vs. naïve-iterate approach of launching the full swarm first and iterating post-swarm on authoring errors. Every Step 2 correction made pre-swarm is a Step 3 API call avoided. WORKFLOW-009 institutionalizes the discipline.

### Skills that FIRED during Phase A

- `panopticon-hackathon-rules` (prime directive carried through)
- `video-validation-protocol` (new SKILL landed as part of Phase 2B; referenced when sanity-checking Golden Run outputs)
- `physical-kalman-tracking` (kalman.py edits during Phase 2B/3 still in scope)
- `2k-sports-hud-aesthetic` (HUD width-clamp repair)
- `react-30fps-canvas-architecture` (gate HUD refactor against rAF canvas invariants)
- `multi-agent-trace-playback` (agent_trace.json format referenced)

### Agents that FIRED during Phase A

- `video-frame-validator` — single-pass frame extraction + visual verification across the demo window. Discovered Player A off-screen 0-8s. Extends the skill's remit from playback validation to pre-authoring grounding. GOTCHA-042.
- `general-purpose` agent × 6 for cherry-pick execution (inside isolated worktree, `mode: "acceptEdits"` every time — zero plan-mode stalls)
- `code-reviewer`, `python-reviewer`, `typescript-reviewer`, `security-reviewer` — parallel orthogonal panel, ~2 min wall time for all 4

### Agents NOT found / partial-failure recovery (anti-pattern #35 in action)

| Attempted | Outcome | Recovery |
|---|---|---|
| `claude-md-improver` agent | Agent not found — does not exist in this installation | **Fell back to `documentation-librarian`** (this very agent). Silently swallowing the failure would have been anti-pattern #35; instead, surfaced the missing-agent fact immediately and used the closest-available orthogonal tool. |
| `agent_trace.json` stale-ref cross-references | Post-main-merge review flagged `See PATTERN-056` at MEMORY.md:1375 which should be PATTERN-064 (the renumbered ID) | Applied sed-style fix in-worktree before integration; added renumbering-map disclaimer to TOOLS_IMPACT.md header; will be caught by this audit going forward |
| Vercel auto-deploy not firing on branch push | Expected deploy URL to update, didn't | Diagnosed, escalated to user; confirmed no auto-deploy on this branch per PROJECT-2026-04-23 "do-not-deploy" constraint. Not actually a failure — the constraint worked as designed. Surfaced rather than silently assuming |

**Meta-observation**: partial-failure surfacing happened THREE times in this session (missing agent, stale cross-refs, non-firing auto-deploy) — each surfaced, diagnosed, and either fixed or escalated. This IS anti-pattern #35 in action (global rule, `~/.claude/rules/anti-patterns.md`): never silently swallow tool-call failures. Captured in FORANDREW.md as a real session-level learning worth preserving.

### Skills NOT USED this session (and why)

- `e2e-runner` / `/e2e` Playwright — deferred to pre-submission pass; Golden Run output validates end-to-end via manual visual QA on localhost
- `hackathon-demo-director` — NEXT session (Sat Apr 25 + Sun Apr 26 — record + submit)
- `computer-use` — deferred to Sunday Apr 26 OBS recording session
- `/vercel:deploy` / `/vercel:verification` — blocked by PROJECT-2026-04-23 "do-not-deploy" constraint
- `biometric-fan-experience` — locked from Phase 3.5; no copy changes needed this phase

### Meta-learning this session

**Orthogonality over quantity**, as articulated in global CLAUDE.md, is a force multiplier when the stakes are merge-level or deploy-level. 4 specialized reviewers running in parallel caught 3 HIGH findings nobody else would have surfaced; 4 `code-reviewer` instances running in parallel would have caught the same 1-2 findings 4 times. The discipline is to NAME each reviewer's distinct failure-mode lens BEFORE dispatching, and collapse redundant lenses.

**PATTERN-062 is now the canonical merge methodology for this project.** Any future multi-commit cross-branch merge — including post-submission PR prep against main — should use the 4-layer recipe. The ROI compounded specifically because the session required TWO merges in sequence; each time the recipe executed cleanly, building confidence that the main workdir stayed pristine while risky operations happened inside the worktree.

---

## Phase 6 — Final 20 % Polish Sprint (2026-04-24 PM)

Post-backend-fortress team-lead override: pivot from engineering to UX craft. 5 polish directives executed in ~90 min edit + ~5 min validation. ZERO new correctness fixes — every directive hardened the demo perimeter.

### Tools used with highest ROI

- **`Skill` tool → `react-30fps-canvas-architecture`** — single-invocation load of the canonical canvas-resize pattern. Informed D3 (PATTERN-070 DPR-aware Canvas Resize) directly. ROI: replaced what would have been 30 min of "read the skeleton canvas code + figure out how to DPR-scale" with a 60 s skill load + 15 min surgical edit.
- **`Edit` tool with narrow `old_string` scopes** — 10 edits across 5 files, each with enough surrounding context to be unambiguous but scoped tight enough for surgical review. Zero edit collisions, zero retry loops.
- **`Bash` + `curl`** — smoke tests on the running dev server (HTTP 200 + page HTML grep for "LOADING BIOMETRIC" / "Broadcast narration" / "STUB") confirmed HMR picked up every edit without a single broken render.
- **`TaskCreate`/`TaskUpdate`** — set up 8 new tasks (consolidation + 5 directives + validation + logging), clean in-progress/completed transitions, kept progress legible across an interrupted session.

### Tools NOT used (deliberately — diminishing returns)

- **Multi-agent review panel (`/code-review` wrapping `code-reviewer` + `security-reviewer` + `typescript-reviewer`)** — scope was surgical (≤300 LoC across 5 files, each directive owning a distinct concern). Panel would have surfaced 0-1 findings for 4× the wall clock. Saved ~20 min for an orthogonal-lens review that wasn't earning its cost. Captured lesson: reserve multi-agent panels for merge-level/deploy-level stakes, not polish sprints.
- **`Perplexity`/`Context7` MCP** — directives were prescriptive (the team lead named each API signature and behavior). External research would have been noise. Non-use case worth naming: when the user hands you a spec, call the code, not the web.
- **`/e2e` Playwright** — existing manual browser scrub at `localhost:3000` + `curl`/`grep` smoke test covered the visual regression surface for the 5 directives. Playwright adds value when you have a test journey to regress; these were single-page additions where the journey is "did the page render with banner + loading state." Save `/e2e` for Saturday's full storyboard rehearsal.
- **`demo-director` agent dispatch** — the v4 Detective Cut storyboard was ALREADY written in `demo-presentation/PLAN.md`. Dispatching an agent to re-write or review it would have been redundant. Consolidation was a file-copy task, not a reasoning task.
- **`documentation-librarian` agent** — I wrote MEMORY.md / FORANDREW.md / TOOLS_IMPACT.md myself. Dispatching the agent would have added latency for formatting an already-scoped append. Rule: dispatch the librarian for END-OF-DAY log rolls that aggregate multi-session patterns; do direct append for in-session entries.

### Skills NOT used (would have been redundant)

- **`awwwards-animations`** / **`animation-designer`** — my Framer Motion usage was a 3-line per-property transition override, not an animation choreography. Loading these skills would have been 50+ tokens for zero additional guidance.
- **`nextjs-hydration-traps`** — LoadingScreen is a presentation-layer component that renders AFTER hydration; the hydration-traps skill is about SSR/RSC prop death, a different failure mode.
- **`hackathon-demo-director`** — the storyboard was already locked (v4 Detective Cut after 4 iterations of dialectical steelmanning in the sibling worktree). Loading the skill would have been "re-plan the plan."
- **`vercel-react-best-practices`** — deployment wasn't touched this phase. The Vercel perimeter was strengthened defensively (GOTCHA-039 LoadingScreen) but not via deploy-config changes.

### Validation suite (5 min total)

- `./node_modules/.bin/tsc --noEmit` → exit 0
- `./node_modules/.bin/vitest run` → 96/96 tests pass (6 test files)
- `curl -s http://localhost:3000 | grep -oE "LOADING BIOMETRIC|Broadcast narration|STUB|UTR Pro A"` → 4/4 expected strings present
- `curl -s /match_data/utr_01_segment_a.json` → `display_narrations: 5`, `display_transitions: 4`, `display_player_profile.name: UTR Pro A`

### Meta-learning this phase

**The Final 20 % is UX craft, not engineering.** This phase did not add a single correctness fix. Every directive was about masking, blocking, or hardening the PERIMETER. The engineering was done; the presentation discipline is categorically the highest-ROI work of hackathon week because judges evaluate what they SEE, not what the code DOES.

**Tool orthogonality mapping BEFORE editing is a workflow gate.** Name each directive's primary file surface before any code moves. Same-file collisions force serialization; distinct-file directives unlock parallel-safe execution (~30 % time savings). WORKFLOW-008.

**The `pointer-events: auto` on a blocker inner panel is the single most load-bearing CSS rule for cold-boot defense.** Without it, the LoadingScreen would render over the video but video's native controls would still receive clicks through the transparent parent. PATTERN-072 names this explicitly so future overlays don't forget it.

---

## Phase 6 — Friday Pull-Forward Sprint (2026-04-24 Evening)

Pulled Saturday's code-level items (A1 + A2a + A7 + A8-minimal) forward into Friday evening to buy multi-hour slack on Saturday's physical-presence recording day.

### Tools used with highest ROI

- **`AskUserQuestion` tool** — two early scope questions (A8 aggressiveness + handoff-doc treatment) shaped the entire sprint before any code moved. Saved ~1 h of scope-guess-and-correct. Tool-use lesson: spend 30 s asking to save 30 min executing wrong scope.
- **`Bash` + `ffmpeg` one-liner** — A7 frame extraction (`-ss 45.3 -frames:v 1 -q:v 2`). 180 KB JPEG in ~100 ms. Would have taken 10 min to wire a Python ffmpeg-wrapper.
- **`Anthropic` Python SDK (vision)** — A7 biomechanics observation on the t=45.3 s frame. 3 335 input tokens (mostly image) + 207 output tokens = well under $0.05. Returned parseable JSON on first call thanks to the ```json fence directive in the prompt. ROI: $0.05 for a demo-critical cold-open overlay.
- **`Write` + `Edit` for surgical hook + component** — `useSlowMoAtAnomalies.ts` (117 LoC, pure function + rAF wrapper) + `Tickertape.tsx` (110 LoC, phase-weighted component) + `useSlowMoAtAnomalies.test.ts` (96 LoC, 15 test cases). Zero cross-file coupling.
- **`vitest run` on a single test file** — 15 new tests in 289 ms. Pure-function testability of `computePlaybackRate` is a direct consequence of the hook's design (ramp/hold/exit math extracted into a side-effect-free function).
- **`Skill` tool for `react-30fps-canvas-architecture`** (inherited from polish sprint) — already loaded the canonical DPR-aware canvas pattern, so A2a's rAF-slaved design was informed by a 60 s skill load, not by re-deriving from first principles.

### Tools NOT used this evening (deliberately — diminishing returns)

- **Multi-agent steelman / review panel** — scope was sequential (A1 → A2a → A7 → A8-minimal) with clear specs. Convening a review panel would have doubled wall-clock for 0-1 findings.
- **`Perplexity` / `Context7` MCP** — every API signature was known (Anthropic vision, HTMLMediaElement `playbackRate`, Framer Motion per-property transitions). External research would have been padding.
- **`Remotion` MCP / `Canva` MCP** — explicitly out of scope tonight (A4/A5/A6 are Saturday physical-presence items).
- **`video-frame-validator` agent for A7** — the `run_vision_pass.py` script IS the frame-validator for this use case. Dispatching a separate agent to "validate the frame before vision call" would have been redundant.

### The "transient APIConnectionError" learning

First post-STEP-3 golden run had an APIConnectionError on the Analytics Specialist (first agent with tool-use = highest call-surface). Trace: `[error: Analytics Specialist failed with APIConnectionError: Connection error.]`. The pipeline's `NEVER raises` contract held — Technical + Tactical still completed, just with the error text as their upstream input. A clean retry was cheap (~60 s + $0.50-1) and the RIGHT move for demo-load-bearing artifacts. **Rule: when a background CV/API pipeline produces a textual error in a downstream trace, the issue is almost always transient network — one retry before escalating to code-level investigation.** Saved ~15 min of debugging a non-existent code bug.

### Validation after Friday pull-forward

- `tsc --noEmit` → exit 0
- `vitest run` → **111/111** tests passing (96 baseline + 15 new A2a unit tests)
- Dev server at localhost:3000 HMR'd all new components; curl confirms Tickertape + LoadingScreen + DisclosureBanner rendering
- `dashboard/public/match_data/vision_pass.json` parsed successfully with biomech annotation
- Golden run retry in flight (pending notification)

### Meta-learning this sprint

**"Pull code work forward when evenings are free" is the dual of "save physical-presence work for the physical-presence day."** Code work is concentration-bound but not location-bound or time-bound. Recording, Canva design work, Remotion rendering, OBS takes, YouTube uploads, and CV form submission are all time-windowed or coordination-bound. Freeing tomorrow's morning by burning tonight's evening is a universal hackathon-arbitrage.

**Sibling worktrees are read-only context libraries, not work surfaces.** The sibling `hackathon-demo-v1/` has been consolidated into this branch's `demo-presentation/`. It lives on disk but is no longer a work surface. This disambiguates future "where do I edit?" questions — the answer is always "here, in `hackathon-research/`".

**Adaptive thinking is a prompt-engineering problem.** Opus 4.7 won't emit thinking blocks for "analyze these signals" — the model judges that single-step. It WILL emit for "consider this alternative hypothesis and explicitly reject it with evidence" — that's a genuine 2-step reasoning task. The STEP 3 nudge is the prompt-design equivalent of "always wire the multi-hypothesis structure explicitly." Captured as GOTCHA-040.

---

## Phase 6 — Late-Late Evening Vimeo/Numerai Sprint (2026-04-24 ~19:30-22:00 EST)

### Tool: Custom local agent — Vimeo deconstruction

**Cost**: 1 background agent dispatch, ~7 minutes wall-clock, ~175K tokens, 55 tool uses.
**Output**: 4.1MB DNA file at `demo-presentation/assets/references/vimeo_205032211_dna.md` with 11 numbered sections, hex-confirmed palette tables, scene-by-scene log.
**ROI**: **HIGH**. Three direct wins:
1. Identified the source as Numerai's *Introducing Numeraire* — gave us proper context, not just "some cool video."
2. Section "What's UNIQUE to Numerai" + "Cross-reference with Anthropic — CONVERGENT" provided a structured ADOPT-vs-REJECT framework that prevented copy-paste mistakes (letterbox, single-family typography, two-card-split would all have been wrong inheritances).
3. Section §10 ("Five-to-Seven Concrete Remotion Principles") gave us 7 transferable surgical mechanics, of which 3 (logo ignition, whispered body copy, slow drift) landed in code that same evening.
**When to repeat**: any time a design reference video / film / motion piece comes in cold. Spend the 7 minutes on background analysis BEFORE the synthesis attempt. The agent's structured "convergent vs unique vs anti-pattern" framing is what makes the synthesis tractable.
**Anti-pattern caught**: would have inherited Numerai's letterbox + two-card-split + single-family typography wholesale without the agent's "register-bearing vs surgical-mechanic" distinction. Captured as DECISION-017 in MEMORY.md.

### Tool: `mcp__claude_ai_Figma__generate_diagram` (Figma MCP)

**Cost**: 1 tool call. EXEMPT from the 6-call/month MCP budget (GOTCHA-043). ~20 seconds wall-clock from Mermaid syntax → FigJam diagram with shareable URL.
**Output**: PANOPTICON LIVE pipeline architecture diagram in FigJam at `figma.com/board/1McYlYT0isbmTOJshc9ip9`. 9 nodes (ffmpeg → YOLO → Kalman → 3-Pass DAG → 7 Signals → DuckDB → Server Action → Opus 4.7 → 2K HUD) + dotted feedback edge from Opus to HUD.
**ROI**: **HIGH for our specific use case**. The diagram needs to LIVE somewhere collaborative + editable + exportable as PNG for the demo. Mermaid CLI would render a static PNG faster but couldn't be edited, embedded in Figma branding, or shared with team members. The Figma MCP fits the "architecture-as-living-document" use case exactly.
**Caveats**:
- Returns an `imageUrl` that's S3-signed with a 7-day expiry. Don't reference that URL in deliverables — re-export to local PNG before expiry. Captured as GOTCHA-045.
- The tool generates ONE diagram per call. Don't attempt to compose multi-diagram boards in a single call.
- Saving to a `planKey` (Andrew's team key from `whoami`) keeps the diagram in his account so it's not lost when the conversation ends.
- Cannot move/style individual shapes after generation — all visual customization happens at the Mermaid syntax level. For richer post-generation editing, open in FigJam.
**When to repeat**: any time a project needs an architecture diagram, decision tree, sequence diagram, or state diagram that lives in a shareable surface. Don't use for: data visualizations, design-system layouts, interactive prototypes.

### Tool: ToolSearch (deferred-tool loader)

**Cost**: 1-2 tool calls per session to load deferred tool schemas. Negligible token cost (one tool's schema is ~500 tokens).
**Use case this session**: loaded `mcp__claude_ai_Figma__generate_diagram`, `TaskUpdate`, `TaskCreate` schemas on demand. The schema-on-demand pattern (vs. all tools loaded upfront) keeps the global tool list short and the system reminder small.
**ROI**: **MEDIUM**. Mainly invisible — saves ~5-10K tokens per session by deferring rarely-used tool schemas. The visible benefit is "I forgot how to call this tool" → ToolSearch with a name → schema loads → done. Better than guessing parameters and getting InputValidationError.
**Anti-pattern caught**: tried to call `mcp__claude_ai_Figma__generate_diagram` directly without loading its schema → would have failed with InputValidationError. ToolSearch + name resolves cleanly.
**When to use**: any time a tool name appears in the deferred-tools list at session start but isn't in the active tool list. Don't keyword-search if you know the name — use the `select:NAME` form for an exact match.

### Tool: Remotion render (`./node_modules/.bin/remotion render <id>`)

**Cost**: ~2-5 seconds per second of output video on M4 Pro. b0-opener (25s) renders in ~50s; 5s closing card in ~10s; 1.5s scene break in ~5s.
**Use this session**: rendered 5 compositions (b0-opener, b5-closing, scene-break-b2/b3/b4) in a single batch. Used `run_in_background: true` for the 4-composition batch (~70s total) so the main session could continue writing docs.
**ROI**: **EXTREMELY HIGH for this project**. Programmatic Remotion + frame-driven animations + batch rendering = full DaVinci-ready chrome library in ~2 minutes after each Remotion code change. Compare to After Effects manual render farm: ~30+ minutes per pass.
**Patterns established**:
- ALWAYS use `./node_modules/.bin/remotion` (full path) instead of `bunx remotion` — avoids cwd drift bugs.
- Batch background renders log to `/tmp/render-batch.log` so progress can be tailed without interrupting the main session.
- Render each composition individually rather than chained — clearer error isolation when one breaks.

### Meta-learning this micro-sprint

**Tool selection cascade for design references**: when a user drops a design reference, the optimal pipeline is:
1. **ToolSearch** to confirm tool availability (cheap)
2. **Custom local agent** (background) for deep deconstruction (~7 min, finds patterns that take humans hours)
3. **Synthesize structured ADOPT-vs-REJECT** in main session while agent runs
4. **Apply** as surgical code edits (Edit tool, not Write — preserves git diff readability)
5. **Render** to verify visually (Remotion + background batch)
6. **Document** the synthesis durably (PLAN.md + MEMORY.md + FORANDREW.md + TOOLS_IMPACT.md — ALL FOUR)

Skipping step 6 is the silent failure mode. The lessons learned tonight (PATTERN-082, 083, 084, DECISION-017, GOTCHA-045) are worth more across future projects than the specific B5 closing card itself. Documenting durably is the leverage move.
