---
name: opus-47-creative-medium
description: Using Claude Opus 4.7 as a creative medium (not just a tool) for PANOPTICON LIVE. Use when wiring any agent in backend/agents/, designing system prompts, configuring extended thinking budgets, setting up prompt caching, or integrating Claude Managed Agents. Targets the 25% Opus 4.7 Use judging criterion and the $5K Creative Opus Exploration prize.
---

# Opus 4.7 as Creative Medium

The hackathon's 25% "Opus 4.7 Use" criterion rewards creative, multi-faceted integration. A basic "send prompt, get response" loop scores below average. PANOPTICON LIVE shows Opus playing THREE roles + one Managed Agent — that's the differentiator.

## The Three Roles

### Role 1 — Reasoner (opus_coach.py)

**What it does**: Reads the live signal stream, queries it through deterministic tools, and produces structured coach-register commentary with VISIBLE extended-thinking tokens.

**Why it's creative**: Most demos hide Opus's reasoning. We show it. Judges watch Claude think about biomechanics in real time.

**Implementation**:
```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

response = await client.messages.create(
    model="claude-opus-4-7",
    max_tokens=2000,
    thinking={"type": "enabled", "budget_tokens": 1500},
    system=[
        {
            "type": "text",
            "text": BIOMECH_PRIMER_10K_TOKENS,
            "cache_control": {"type": "ephemeral"},  # prompt cache
        }
    ],
    tools=[
        {"name": "get_signal_window", "description": "...", "input_schema": {...}},
        {"name": "compare_to_baseline", "description": "...", "input_schema": {...}},
        {"name": "get_rally_context", "description": "...", "input_schema": {...}},
        {"name": "get_match_phase", "description": "...", "input_schema": {...}},
    ],
    messages=[{"role": "user", "content": f"Analyze player A's last 10 seconds at t={t_ms}."}],
)

# Extract thinking blocks for UI display
for block in response.content:
    if block.type == "thinking":
        yield {"type": "thinking", "text": block.thinking}
    elif block.type == "tool_use":
        # execute deterministic tool, feed result back
        ...
    elif block.type == "text":
        yield {"type": "commentary", "text": block.text}
```

**Extended thinking budget strategy**:
- Per-event beats (triggered by anomaly): `budget_tokens=500`
- Coach commentary stream (every ~10s): `budget_tokens=1500`
- Scouting report (long-running): `budget_tokens=4000`

### Role 2 — Designer (hud_designer.py)

**What it does**: Given the current match state + active anomaly + dominant signal, Opus outputs a JSON layout spec for the HUD. The frontend has fixed widget primitives; Opus arranges them.

**Why it's creative**: Generative UI. Opus IS the designer. It exercises Opus 4.7's design upgrade directly.

**Prompt template**:
```
You are the HUD designer for a pro tennis biomechanical intelligence overlay. Current state:
- Match phase: {phase}
- Active anomalies: {anomalies}
- Dominant signal: {dominant_signal_name} (magnitude {z_score})
- Previous layout: {last_layout_spec}

Choose a HUD layout that foregrounds what matters now. Available widgets:
- PlayerNameplate (position: top-left, top-right)
- SignalBar (4 slots: each holds one signal)
- MomentumMeter (position: center-top)
- PredictiveOverlay (player A or B)
- TossTracer (only during PRE_SERVE_RITUAL)
- FootworkHeatmap (only during ACTIVE_RALLY)

Output a LayoutSpec JSON matching this schema: {schema}
Prefer minimalism — don't show every widget. Foreground the narrative.
```

**Recomputation rule**: Only call Opus on match-state CHANGE (serve → rally → break), NOT per frame. Cache last layout. This keeps Opus cost + latency manageable.

### Role 3 — Voice (streaming commentary)

**What it does**: The Reasoner's `text` output is streamed to the frontend as a typewriter effect. Haiku 4.5 generates cheap per-second beats in parallel.

**Why it's creative**: Multi-model orchestration visible in UI. Judges see cost-aware routing in action.

**Haiku narrator**:
```python
response = await client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=80,
    system="You are a tennis broadcast color commentator. One sentence per beat.",
    messages=[{"role": "user", "content": f"Beat at {t}s: {signal_snapshot}"}],
)
```

### Role 4 (Bonus) — Managed Agent (Scouting Report)

**What it does**: Long-running task — generates a full PDF scouting report over 30-90 seconds.

**Why it's creative**: Exercises Claude Managed Agents ($5K "Best Use" prize target).

**Pattern**:
```python
from anthropic.beta.managed_agents import ManagedAgent  # placeholder — use current SDK API

agent = ManagedAgent(
    name="scouting-report-generator",
    tools=[...],
    system_prompt=SCOUTING_SYSTEM_PROMPT,
)
run = await agent.start(input={"match_id": match_id})
# Poll or webhook for completion
pdf_bytes = await run.get_result()
```

Consult `context7` for the latest Managed Agents Python SDK surface before implementation.

## Prompt Caching (Mandatory)

The 5-10K-token biomechanics primer is static. Cache it:
```python
system=[
    {
        "type": "text",
        "text": BIOMECH_PRIMER,  # 5-10K tokens
        "cache_control": {"type": "ephemeral"},
    }
]
```

**Cache-hit observability**: The response includes `usage.cache_read_input_tokens` and `usage.cache_creation_input_tokens`. Render these in a dev panel — judges see cost-awareness.

## Streaming API

```python
async with client.messages.stream(
    model="claude-opus-4-7",
    max_tokens=2000,
    thinking={"type": "enabled", "budget_tokens": 1500},
    system=[...],
    tools=[...],
    messages=[...],
) as stream:
    async for event in stream:
        if event.type == "content_block_delta":
            # forward to frontend via SSE
            ...
```

## Tool Design Principles

- Tools are **deterministic, not more LLMs**. Each tool is a DuckDB query or a simple calculation.
- Tool responses are Pydantic-serialized. No unstructured strings.
- Tool timeouts: 5 seconds hard cap. If a tool takes longer, return `{"error": "timeout"}`.
- Tool call count cap: 10 per Opus invocation. Prevents runaway loops.

## Citadel Discipline

- `ANTHROPIC_API_KEY` via env var only, never committed
- `httpx.AsyncClient` with `timeout=30.0`
- Never log user-submitted match IDs to external services
- Pydantic v2 for tool inputs/outputs
- Streaming responses gracefully handle disconnect (frontend reconnect logic)

## Model ID Cheat Sheet

| Use case | Model ID |
|---|---|
| Reasoner (extended thinking, tools) | `claude-opus-4-7` |
| Designer (generative UI JSON) | `claude-opus-4-7` |
| Narrator (cheap per-sec beats) | `claude-haiku-4-5-20251001` |
| Scouting Report Managed Agent | `claude-opus-4-7` (via managed agents API) |

## What This ISN'T

- Not a chat interface (no conversation history — each invocation is stateless, re-read from DuckDB)
- Not a predictive model (no training — Opus reasons from facts + tools)
- Not a RAG system (no vector DB — signals are structured, queryable)
- Not a fine-tuned model (off-the-shelf Opus 4.7 with great prompts)
