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

---

## META-LEARNING FRAMEWORK

At end of each day, answer:
1. **Which tool paid off unexpectedly?** → Update HIGH-IMPACT section
2. **Which tool did nothing?** → Move to SKILLS NOT USED with reason
3. **Did I skip a tool I should have used?** → Anti-pattern #18; note and use tomorrow
4. **What non-obvious pattern emerged?** → Extract to `.claude/skills/` via `/skill-create`
