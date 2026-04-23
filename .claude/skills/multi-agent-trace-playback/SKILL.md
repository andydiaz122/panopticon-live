---
name: multi-agent-trace-playback
description: The canonical PANOPTICON LIVE pattern for showcasing real multi-agent Claude reasoning in a demo when the live reasoning loop exceeds the deploy-target's serverless timeout. Capture every agent event (thinking, tool_call, tool_result, handoff) into a typed AgentTrace during offline precompute; replay it client-side with timed pacing. Use when building any Managed-Agents feature that the judges must SEE reason in real-time.
---

# Multi-Agent Trace Playback

## One-line purpose

Decouple agent compute-time from display-time by CAPTURING every agent event offline and REPLAYING them client-side with deterministic pacing.

## Why this pattern exists

Deep Managed-Agents loops run 20-60+ seconds (extended thinking + tool calls + handoffs). Vercel Hobby serverless functions are capped at 10-15 seconds. A naive live invocation hangs and crashes the demo. But the Opus 4.7 Use judging criterion (25%) + the judges' stated preference for "projects at the edge of what's probably not fully possible" means we MUST show real multi-agent reasoning. Playback solves both constraints.

## The three orthogonal Scouting Committee agents (Panopticon's canonical swarm)

| Agent | Sole Focus | Tools | Input | Output |
|---|---|---|---|---|
| **Analytics Specialist** (Quant) | Statistical anomalies in the 7 signal arrays | DuckDB read-only query | `match_id`, signal schema | Anomaly list: `{signal, player, delta, z_score, timestamp}` |
| **Technical Biomechanics Coach** | Physical-breakdown narrative grounded in literature | BIOMECH_PRIMER (prompt), no tools | Analytics Specialist's output | Cause narrative: "player failing to load right leg on split-step due to quad fatigue" |
| **Tactical Strategist** | Match-strategy recommendation | no tools (pure synthesis) | Technical Coach's output | Tactical play: "exploit compromised split-step by hitting behind the player" |

**Hard rule: each handoff is REAL.** Agent N+1's user message contains agent N's OUTPUT, not the raw `match_data.json`. This forces genuine orthogonal reasoning (not three parallel agents doing the same job) and mirrors the development process the founder drew from (quant desk → biomech consult → tactics).

## The AgentTrace schema (Pydantic v2, discriminated-union events)

```python
class TraceThinking(BaseModel):
    kind: Literal["thinking"] = "thinking"
    t_ms: int  # ms offset from trace start (not wall clock)
    content: str

class TraceToolCall(BaseModel):
    kind: Literal["tool_call"] = "tool_call"
    t_ms: int
    tool_name: str
    input_json: str  # pre-serialized — avoids arbitrary-dict drift at rehydrate

class TraceToolResult(BaseModel):
    kind: Literal["tool_result"] = "tool_result"
    t_ms: int
    tool_name: str
    output_json: str
    is_error: bool = False

class TraceText(BaseModel):
    kind: Literal["text"] = "text"
    t_ms: int
    content: str

class TraceHandoff(BaseModel):
    kind: Literal["handoff"] = "handoff"
    t_ms: int
    from_agent: str
    to_agent: str
    payload_summary: str  # one-liner; full payload is the next agent's input_json

TraceEvent = Annotated[
    TraceThinking | TraceToolCall | TraceToolResult | TraceText | TraceHandoff,
    Field(discriminator="kind"),
]

class AgentStep(BaseModel):
    agent_name: str
    agent_role: str
    started_at_ms: int
    completed_at_ms: int
    events: list[TraceEvent]

class AgentTrace(BaseModel):
    match_id: str
    generated_at: datetime
    committee_goal: str
    steps: list[AgentStep]
    final_report_markdown: str
    total_compute_ms: int  # real wall-clock time the offline run took
```

**Why discriminated union, not dict[str, Any]**: the TypeScript frontend needs `kind`-based narrowing to render the right pill (thinking → dim italic; tool_call → code block; tool_result → JSON tree; handoff → arrow animation). `dict[str, Any]` forces runtime shape-sniffing, which WILL break silently when a new event type lands.

## The UI replay contract (frontend)

- **Loading**: fetch `/match_data/agent_trace.json` in `useEffect` (NOT via Server Component props — GOTCHA-026 hydration death).
- **Pacing**: reveal events at a constant "dramatic" rate, not their real timestamps (the real loop's 45s is too long for demo).
  - 200-800ms per `TraceText` event
  - 1200-2500ms per `TraceHandoff` (let the judge feel the state transition)
  - 400-1200ms per `TraceToolCall` (stagger call + result with ~800ms between them)
- **User control**: Pause / Resume / Skip-to-End buttons. Judges want to scrub.
- **Disclosure**: banner "ARCHITECTURAL PREVIEW: SWARM ACCELERATED FOR DEMO" near the console title. Honest > sneaky.

## Orthogonality with other skills

- **Reads from**: `duckdb-pydantic-contracts` (the schema file the Analytics tool queries).
- **Reads from**: `biomechanical-signal-semantics` (the knowledge base the Technical Coach synthesizes).
- **Writes to**: `dashboard/public/match_data/agent_trace.json`.
- **Consumed by**: the Orchestration Console component (Tab 3 in the dashboard).
- **Does NOT own**: the biomech knowledge itself (lives in `biomechanical-signal-semantics`), the DuckDB schema (lives in `duckdb-pydantic-contracts`), or the HUD aesthetic (`2k-sports-hud-aesthetic`).

## What this skill forbids

- Mocking agent events. Every event in `agent_trace.json` MUST come from a real Anthropic API call during precompute.
- Passing `match_data.json` directly to the Tactical agent. Each handoff must cascade.
- Embedding `agent_trace.json` in a Next.js Server Component prop. Always `fetch()` in `useEffect`.
- Dropping the "ARCHITECTURAL PREVIEW" banner. The disclosure is the difference between honest engineering and a demo-mock.

## References
- `PATTERN-056` in MEMORY.md (origin pattern entry)
- `USER-CORRECTION-024` in MEMORY.md (founder's strategic framing)
- `opus-47-creative-medium` skill (prompt caching + extended thinking patterns that each agent uses)
- `react-30fps-canvas-architecture` (frontend rendering substrate)
