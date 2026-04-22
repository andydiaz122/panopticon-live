"""Tests for backend/agents/opus_coach.py — the Opus 4.7 Coach Reasoner.

Fakes the Anthropic SDK with `types.SimpleNamespace` objects duck-matching
`response.content[]`, `response.stop_reason`, `response.usage` — no real API calls.

Covers:
- End-turn on first round-trip (text-only response)
- Tool-use loop → tool_result → end_turn
- Extended-thinking block extraction
- Token accumulation across multiple round-trips
- Cache tokens propagate into CoachInsight
- Iteration cap fallback
- API-exception graceful degradation
- tool_calls audit log captures every dispatch
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

from backend.agents.opus_coach import generate_coach_insight
from backend.agents.tools import ToolContext
from backend.db.schema import SignalSample

# ──────────────────────────── Fake client plumbing ────────────────────────────


def _text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def _thinking_block(text: str, signature: str = "sig123") -> SimpleNamespace:
    return SimpleNamespace(type="thinking", thinking=text, signature=signature)


def _tool_use_block(name: str, tool_input: dict, tool_id: str = "toolu_1") -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", id=tool_id, name=name, input=tool_input)


def _usage(
    input_tokens: int = 100,
    output_tokens: int = 50,
    cache_read_input_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
) -> SimpleNamespace:
    return SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_input_tokens=cache_read_input_tokens,
        cache_creation_input_tokens=cache_creation_input_tokens,
    )


def _response(
    *blocks: SimpleNamespace,
    stop_reason: str = "end_turn",
    usage: SimpleNamespace | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        content=list(blocks),
        stop_reason=stop_reason,
        usage=usage if usage is not None else _usage(),
    )


class _ScriptedClient:
    """Minimal AsyncAnthropic-shaped client that returns responses from a pre-scripted list.

    Usage:
        client = _ScriptedClient(responses=[_response(...), _response(...)])
        result = await client.messages.create(...)  # returns responses[0]
        result = await client.messages.create(...)  # returns responses[1]
    """

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.call_log: list[dict[str, Any]] = []
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, **kwargs: Any) -> Any:
        # Snapshot `messages` — the coach mutates the same list across iterations,
        # so without a copy the log would show the FINAL state on every call, not
        # the state at the time of the call.
        snap = {**kwargs}
        if "messages" in snap:
            snap["messages"] = list(snap["messages"])
        self.call_log.append(snap)
        if not self._responses:
            raise AssertionError("scripted client ran out of responses")
        return self._responses.pop(0)


class _ExplodingClient:
    """Fake client that always raises on .messages.create — exercises error path."""

    def __init__(self, exc: Exception) -> None:
        self._exc = exc
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, **kwargs: Any) -> Any:
        raise self._exc


# ──────────────────────────── Test fixtures ────────────────────────────


def _ctx_with_signal(value: float = 1.5) -> ToolContext:
    return ToolContext(
        match_id="utr_01",
        signals=[
            SignalSample(
                timestamp_ms=1000,
                match_id="utr_01",
                player="A",
                signal_name="recovery_latency_ms",
                value=value,
                baseline_z_score=None,
                state="ACTIVE_RALLY",
            ),
        ],
    )


def _run(coro: Any) -> Any:
    """Convenience wrapper around asyncio.run for terse tests."""
    return asyncio.run(coro)


# ──────────────────────────── Tests ────────────────────────────


def test_coach_end_turn_on_first_response_returns_insight() -> None:
    client = _ScriptedClient([
        _response(_text_block("Player B is fading."), stop_reason="end_turn"),
    ])
    ctx = _ctx_with_signal()
    insight = _run(generate_coach_insight(
        client, ctx,
        t_ms=42_500, match_id="utr_01",
        insight_id="coach_42500",
        trigger_description="Anomaly: B recovery_latency_ms z=2.7",
    ))
    assert insight.insight_id == "coach_42500"
    assert insight.timestamp_ms == 42_500
    assert insight.match_id == "utr_01"
    assert insight.commentary == "Player B is fading."
    assert insight.thinking is None  # no thinking block in this fake response
    assert insight.tool_calls == []
    assert insight.input_tokens == 100
    assert insight.output_tokens == 50


def test_coach_runs_tool_loop_and_resolves() -> None:
    tool_use = _tool_use_block(
        name="get_signal_window",
        tool_input={"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 1000, "window_sec": 10.0},
        tool_id="toolu_xyz",
    )
    client = _ScriptedClient([
        _response(tool_use, stop_reason="tool_use"),
        _response(_text_block("Confirmed: A's recovery is elevated."), stop_reason="end_turn"),
    ])
    ctx = _ctx_with_signal(value=1.5)

    insight = _run(generate_coach_insight(
        client, ctx,
        t_ms=2000, match_id="utr_01", insight_id="coach_2000",
        trigger_description="testing",
    ))

    assert insight.commentary == "Confirmed: A's recovery is elevated."
    # One tool_call record
    assert len(insight.tool_calls) == 1
    tc = insight.tool_calls[0]
    assert tc["name"] == "get_signal_window"
    assert tc["id"] == "toolu_xyz"
    assert tc["input"]["player"] == "A"
    assert tc["output"]["count"] == 1  # from ctx_with_signal


def test_coach_extracts_thinking_block() -> None:
    client = _ScriptedClient([
        _response(
            _thinking_block("Let me check the baseline first..."),
            _text_block("B is fading fast."),
            stop_reason="end_turn",
        ),
    ])
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=100, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    assert insight.thinking == "Let me check the baseline first..."
    assert insight.commentary == "B is fading fast."


def test_coach_accumulates_tokens_across_iterations() -> None:
    tool_use = _tool_use_block("get_match_phase", {"t_ms": 500})
    client = _ScriptedClient([
        _response(tool_use, stop_reason="tool_use", usage=_usage(input_tokens=200, output_tokens=30)),
        _response(_text_block("Analysis."), stop_reason="end_turn",
                  usage=_usage(input_tokens=150, output_tokens=40)),
    ])
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=500, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    assert insight.input_tokens == 350  # 200 + 150
    assert insight.output_tokens == 70  # 30 + 40


def test_coach_accumulates_cache_tokens() -> None:
    client = _ScriptedClient([
        _response(
            _text_block("ok"),
            stop_reason="end_turn",
            usage=_usage(cache_read_input_tokens=1500, cache_creation_input_tokens=500),
        ),
    ])
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    assert insight.cache_read_tokens == 1500
    assert insight.cache_creation_tokens == 500


def test_coach_iteration_cap_returns_fallback_insight() -> None:
    # Always return tool_use — never reaches end_turn
    tool_use = _tool_use_block("get_match_phase", {"t_ms": 0})
    client = _ScriptedClient([
        _response(tool_use, stop_reason="tool_use") for _ in range(10)
    ])
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
        max_iterations=3,
    ))
    assert "iteration cap 3 exceeded" in insight.commentary
    # Still has all 3 rounds of tool_calls logged
    assert len(insight.tool_calls) == 3


def test_coach_api_exception_returns_error_insight_no_raise() -> None:
    client = _ExplodingClient(RuntimeError("simulated API failure"))
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    assert insight.commentary.startswith("[coach_error:")
    assert "simulated API failure" in insight.commentary
    # Must still satisfy Pydantic (non-None commentary, valid ids)
    assert insight.match_id == "utr_01"


def test_coach_sends_system_prompt_with_cache_control() -> None:
    client = _ScriptedClient([_response(_text_block("ok"), stop_reason="end_turn")])
    _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    call = client.call_log[0]
    system = call["system"]
    assert isinstance(system, list) and len(system) == 1
    assert system[0]["type"] == "text"
    assert system[0]["cache_control"] == {"type": "ephemeral"}
    # Primer content hint (don't lock on exact text; primer can evolve)
    assert "7 signals" in system[0]["text"]


def test_coach_sends_tools_and_adaptive_thinking() -> None:
    """Opus 4.7 REQUIRES `thinking={"type": "adaptive"}` — the old "enabled"+budget_tokens
    API is rejected with a 400 (USER-CORRECTION-027). Lock this in a test so the
    shape never drifts back silently."""
    client = _ScriptedClient([_response(_text_block("ok"), stop_reason="end_turn")])
    _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    call = client.call_log[0]
    assert call["thinking"] == {"type": "adaptive"}
    # Must NOT pass the rejected legacy shape
    assert "budget_tokens" not in str(call["thinking"])
    # All 4 tool schemas present
    tool_names = {t["name"] for t in call["tools"]}
    assert tool_names == {
        "get_signal_window", "compare_to_baseline", "get_rally_context", "get_match_phase",
    }


def test_coach_handles_response_with_no_text_block() -> None:
    """Defensive: if Opus returns only a thinking block (unlikely but legal), don't crash."""
    client = _ScriptedClient([
        _response(_thinking_block("silent pondering"), stop_reason="end_turn"),
    ])
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    assert insight.commentary == "[no commentary produced]"
    assert insight.thinking == "silent pondering"


def test_coach_handles_unknown_tool_gracefully_via_dispatch() -> None:
    """When Opus hallucinates a non-existent tool, dispatch returns error and the loop continues."""
    tool_use = _tool_use_block("fake_tool_does_not_exist", {"anything": 1}, tool_id="t1")
    client = _ScriptedClient([
        _response(tool_use, stop_reason="tool_use"),
        _response(_text_block("Recovered and finished."), stop_reason="end_turn"),
    ])
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    assert insight.commentary == "Recovered and finished."
    # The bad tool call was logged with an error output
    assert insight.tool_calls[0]["output"]["error"] == "unknown_tool"


def test_coach_tool_result_content_is_valid_json_string() -> None:
    """The tool_result content must be a JSON string (Anthropic SDK requirement for structured output)."""
    tool_use = _tool_use_block(
        "get_signal_window",
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 1000, "window_sec": 10.0},
    )
    client = _ScriptedClient([
        _response(tool_use, stop_reason="tool_use"),
        _response(_text_block("done"), stop_reason="end_turn"),
    ])
    _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=2000, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    # Inspect the SECOND .create call — it should have messages[] with the tool_result
    call_2 = client.call_log[1]
    tool_result_turn = call_2["messages"][-1]
    assert tool_result_turn["role"] == "user"
    content = tool_result_turn["content"]
    assert len(content) == 1
    assert content[0]["type"] == "tool_result"
    # The content must be a JSON string (not a dict)
    import json as _json  # local — avoid top-level shadow
    parsed = _json.loads(content[0]["content"])
    assert parsed["count"] == 1


def test_coach_no_tool_uses_despite_non_end_turn_exits_loop() -> None:
    """If stop_reason != end_turn but there are no tool_uses, the loop must still exit.

    Guards against model weirdness where stop_reason='max_tokens' comes with only text.
    """
    client = _ScriptedClient([
        _response(_text_block("partial commentary"), stop_reason="max_tokens"),
    ])
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    assert insight.commentary == "partial commentary"


def test_coach_binds_player_names_into_user_prompt() -> None:
    """Explicit player names from run_agent_phase must reach Opus's user message,
    with an anti-hallucination instruction. Prevents Opus from inventing famous
    tennis names (Djokovic, Federer, etc.) from its training data."""
    client = _ScriptedClient([_response(_text_block("ok"), stop_reason="end_turn")])
    _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=42_000, match_id="utr_01", insight_id="ins1",
        trigger_description="test",
        player_a_name="Serena Williams",
        player_b_name="Naomi Osaka",
    ))
    user_msg = client.call_log[0]["messages"][0]["content"]
    assert "Serena Williams" in user_msg
    assert "Naomi Osaka" in user_msg
    assert "Do NOT invent any other names" in user_msg


def test_coach_falls_back_to_generic_names_when_not_supplied() -> None:
    """Defaults keep unit tests terse; production via run_agent_phase always supplies real names."""
    client = _ScriptedClient([_response(_text_block("ok"), stop_reason="end_turn")])
    _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=0, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    user_msg = client.call_log[0]["messages"][0]["content"]
    assert "Player A" in user_msg
    assert "Player B" in user_msg


def test_coach_multi_tool_use_in_one_response() -> None:
    """Opus can request >1 tool per turn. All must be dispatched + tool_results returned."""
    tu1 = _tool_use_block("get_match_phase", {"t_ms": 500}, tool_id="t1")
    tu2 = _tool_use_block(
        "get_signal_window",
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 1000, "window_sec": 5.0},
        tool_id="t2",
    )
    client = _ScriptedClient([
        _response(tu1, tu2, stop_reason="tool_use"),
        _response(_text_block("both checked"), stop_reason="end_turn"),
    ])
    insight = _run(generate_coach_insight(
        client, _ctx_with_signal(),
        t_ms=1000, match_id="utr_01", insight_id="ins1", trigger_description="t",
    ))
    # Two tool calls recorded from single iteration
    assert len(insight.tool_calls) == 2
    # And the SECOND create call must have TWO tool_result blocks
    call_2 = client.call_log[1]
    tool_results = [c for c in call_2["messages"][-1]["content"] if c["type"] == "tool_result"]
    assert len(tool_results) == 2
    assert {tr["tool_use_id"] for tr in tool_results} == {"t1", "t2"}
