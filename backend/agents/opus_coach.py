"""Opus 4.7 Coach Reasoner — pre-computed CoachInsight generator (OFFLINE).

Runs inside backend/precompute.py, typically when an anomaly fires on one of
the 7 signals. Produces a `CoachInsight` with:
  - thinking:      extended-thinking text (visible to judges in frontend panel)
  - commentary:    final 3-paragraph coach output (see system_prompt.py)
  - tool_calls:    structured log of every tool invocation (inputs + outputs)
  - token counts:  accurate ACROSS all API round-trips in the tool-use loop

Design invariants:
  - Client is `Protocol`-typed so tests can pass a fake without importing `anthropic`
  - Tool-use loop has a hard iteration cap (`max_iterations=5`) — Opus cannot hang
  - Token counts accumulate across ALL round-trips (not just the last)
  - On API error: return a MINIMAL CoachInsight with commentary=<error marker>.
    NEVER raise into precompute.py — one failed insight must not kill the run.
  - Prompt caching: system prompt wrapped with `cache_control: ephemeral`
    so repeated invocations inside the same 5-minute window hit the cache.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from backend.agents.system_prompt import BIOMECH_PRIMER
from backend.agents.tools import TOOL_SCHEMAS, ToolContext, dispatch_tool
from backend.db.schema import CoachInsight

DEFAULT_MODEL: str = "claude-opus-4-7"
DEFAULT_MAX_TOKENS: int = 2000
DEFAULT_MAX_ITERATIONS: int = 5
"""Hard cap on tool-use round-trips per insight. Opus can't spiral."""

# NOTE: Opus 4.7 uses ADAPTIVE thinking — the model decides how much reasoning to
# allocate per turn. The old `thinking={"type": "enabled", "budget_tokens": N}` API
# is REJECTED with a 400. See USER-CORRECTION-027 (2026-04-22 smoke-test discovery).
# To force a minimum reasoning depth on hard problems, pass output_config={"effort": "max"|"xhigh"|"high"|"low"}
# (but for Coach we let the model auto-tune — biomech reasoning qualifies as "hard").


@runtime_checkable
class AnthropicClientLike(Protocol):
    """Protocol for the Anthropic SDK AsyncAnthropic client shape we consume.

    Matches `client.messages.create(...)` coroutine returning an object with
    `.content: list`, `.stop_reason: str`, `.usage: object` attributes. Exists
    so tests can pass a fake without needing the real SDK.
    """

    messages: Any  # duck-typed: has an async `create` method


@dataclass
class _TokenAcc:
    """Accumulator for token usage across multiple API round-trips in a tool-use loop."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    tool_calls: list[dict[str, Any]] = field(default_factory=list)

    def add_usage(self, usage: Any) -> None:
        """Accumulate from an Anthropic response.usage object. Tolerates missing fields."""
        self.input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
        self.output_tokens += int(getattr(usage, "output_tokens", 0) or 0)
        self.cache_read_tokens += int(getattr(usage, "cache_read_input_tokens", 0) or 0)
        self.cache_creation_tokens += int(getattr(usage, "cache_creation_input_tokens", 0) or 0)


def _extract_thinking_text(blocks: list[Any]) -> str | None:
    """Concatenate any `thinking` block content from an Anthropic response.

    Extended thinking blocks expose their text via `block.thinking` (SDK >= 0.40).
    Returns None if no thinking blocks present (model chose not to think).
    """
    parts: list[str] = []
    for block in blocks:
        if getattr(block, "type", None) == "thinking":
            text = getattr(block, "thinking", None)
            if isinstance(text, str) and text:
                parts.append(text)
    return "\n\n".join(parts) if parts else None


def _extract_text(blocks: list[Any]) -> str:
    """Concatenate all `text` blocks from an Anthropic response. Empty string if none."""
    parts: list[str] = []
    for block in blocks:
        if getattr(block, "type", None) == "text":
            text = getattr(block, "text", None)
            if isinstance(text, str):
                parts.append(text)
    return "\n\n".join(parts)


def _tool_use_blocks(blocks: list[Any]) -> list[Any]:
    """Return just the tool_use blocks (Opus asked us to call these tools)."""
    return [b for b in blocks if getattr(b, "type", None) == "tool_use"]


def _response_to_dict_content(blocks: list[Any]) -> list[dict[str, Any]]:
    """Convert Opus's response.content blocks into a JSON-safe list for the next messages[] turn.

    We need to echo the full assistant turn back in messages[] for the tool-use loop.
    Anthropic's SDK accepts either block objects or dicts; dicts are easier to build defensively.
    """
    out: list[dict[str, Any]] = []
    for b in blocks:
        btype = getattr(b, "type", None)
        if btype == "text":
            out.append({"type": "text", "text": getattr(b, "text", "")})
        elif btype == "thinking":
            out.append({
                "type": "thinking",
                "thinking": getattr(b, "thinking", ""),
                "signature": getattr(b, "signature", ""),
            })
        elif btype == "tool_use":
            out.append({
                "type": "tool_use",
                "id": getattr(b, "id", ""),
                "name": getattr(b, "name", ""),
                "input": getattr(b, "input", {}) or {},
            })
    return out


async def generate_coach_insight(
    client: AnthropicClientLike,
    ctx: ToolContext,
    *,
    t_ms: int,
    match_id: str,
    insight_id: str,
    trigger_description: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> CoachInsight:
    """Run the Opus 4.7 Coach Reasoner against the current ToolContext.

    Returns a fully-populated CoachInsight. On API error, returns a minimal
    CoachInsight with an [error] commentary — never raises into the caller.

    Args:
        client: AsyncAnthropic-compatible client (real or fake).
        ctx: Read-only snapshot of signals + transitions at time t_ms.
        t_ms: Current match time (used in trigger prompt + stored on insight).
        match_id: Parent match id (stored on insight).
        insight_id: Unique id for this CoachInsight (caller-assigned, often `f"coach_{t_ms}"`).
        trigger_description: Human-readable string describing what triggered this insight
            (e.g., "Anomaly: player B recovery_latency_ms z-score=2.7 at t=42500ms").
        model: Anthropic model ID. Default claude-opus-4-7.
        max_tokens: Output cap per round-trip.
        (thinking depth: Opus 4.7 adaptive — model auto-tunes per problem)
        max_iterations: Hard cap on tool-use round-trips. Prevents runaway loops.
    """
    system_blocks = [
        {"type": "text", "text": BIOMECH_PRIMER, "cache_control": {"type": "ephemeral"}},
    ]
    user_prompt = (
        f"Match time: {t_ms} ms.\n"
        f"Trigger: {trigger_description}\n\n"
        f"Produce your 3-paragraph coach insight now. Use tools to ground your claims."
    )
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": user_prompt},
    ]
    acc = _TokenAcc()

    try:
        for iteration in range(max_iterations):
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                # Opus 4.7: adaptive thinking — model decides reasoning depth (see module header)
                thinking={"type": "adaptive"},
                system=system_blocks,
                tools=TOOL_SCHEMAS,
                messages=messages,
            )
            acc.add_usage(getattr(response, "usage", None))

            stop_reason = getattr(response, "stop_reason", "")
            content_blocks = list(getattr(response, "content", []) or [])

            # Echo assistant turn into messages[] — required for tool-result follow-ups
            messages.append({"role": "assistant", "content": _response_to_dict_content(content_blocks)})

            tool_uses = _tool_use_blocks(content_blocks)
            if stop_reason == "end_turn" or not tool_uses:
                # Extract final commentary + thinking and return
                return CoachInsight(
                    insight_id=insight_id,
                    timestamp_ms=t_ms,
                    match_id=match_id,
                    thinking=_extract_thinking_text(content_blocks),
                    commentary=_extract_text(content_blocks) or "[no commentary produced]",
                    tool_calls=acc.tool_calls,
                    input_tokens=acc.input_tokens,
                    output_tokens=acc.output_tokens,
                    cache_read_tokens=acc.cache_read_tokens,
                    cache_creation_tokens=acc.cache_creation_tokens,
                )

            # Dispatch tool calls, build tool_result content block for the next turn
            tool_results: list[dict[str, Any]] = []
            for tu in tool_uses:
                tool_id = getattr(tu, "id", "")
                tool_name = getattr(tu, "name", "")
                tool_input = getattr(tu, "input", {}) or {}
                result = dispatch_tool(ctx, tool_name, tool_input)
                # Record for CoachInsight.tool_calls (auditable trail)
                acc.tool_calls.append({
                    "iteration": iteration,
                    "id": tool_id,
                    "name": tool_name,
                    "input": tool_input,
                    "output": result,
                })
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": json.dumps(result),
                })
            messages.append({"role": "user", "content": tool_results})

        # Hit iteration cap — return best-effort insight from last response
        return CoachInsight(
            insight_id=insight_id,
            timestamp_ms=t_ms,
            match_id=match_id,
            thinking=None,
            commentary=f"[iteration cap {max_iterations} exceeded — no final commentary]",
            tool_calls=acc.tool_calls,
            input_tokens=acc.input_tokens,
            output_tokens=acc.output_tokens,
            cache_read_tokens=acc.cache_read_tokens,
            cache_creation_tokens=acc.cache_creation_tokens,
        )

    except Exception as exc:
        # NEVER crash the precompute run on a single failed insight.
        return CoachInsight(
            insight_id=insight_id,
            timestamp_ms=t_ms,
            match_id=match_id,
            thinking=None,
            commentary=f"[coach_error: {type(exc).__name__}: {exc}]",
            tool_calls=acc.tool_calls,
            input_tokens=acc.input_tokens,
            output_tokens=acc.output_tokens,
            cache_read_tokens=acc.cache_read_tokens,
            cache_creation_tokens=acc.cache_creation_tokens,
        )
