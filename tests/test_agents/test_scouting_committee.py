"""Tests for backend/agents/scouting_committee.py — the 3-agent Swarm.

PATTERN-056: Multi-Agent Trace Playback. Each test uses a scripted fake client
that returns deterministic responses for each agent turn — tests verify:
  - The committee runs all 3 agents sequentially with real handoffs
  - Each agent's output is captured as trace events with monotonic t_ms
  - The final AgentTrace is chronologically valid + JSON-serializable
  - Errors in any single agent are caught; partial traces still returned
  - Token-accounting accumulates across all 3 agents
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import pytest

from backend.agents.scouting_committee import (
    TACTICAL_STRATEGIST_NAME,
    ANALYTICS_SPECIALIST_NAME,
    TECHNICAL_COACH_NAME,
    generate_scouting_report,
)
from backend.agents.tools import ToolContext
from backend.db.schema import (
    AgentTrace,
    SignalSample,
    StateTransition,
    TraceHandoff,
    TraceText,
    TraceThinking,
    TraceToolCall,
    TraceToolResult,
)


# ──────────────────────────── Fake Anthropic client ────────────────────────────


@dataclass
class _FakeBlock:
    """Minimal shape that mimics Anthropic content blocks."""

    type: str
    text: str = ""
    thinking: str = ""
    signature: str = ""
    id: str = ""
    name: str = ""
    input: dict[str, Any] = field(default_factory=dict)


@dataclass
class _FakeUsage:
    input_tokens: int = 100
    output_tokens: int = 50
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


@dataclass
class _FakeResponse:
    content: list[_FakeBlock]
    stop_reason: str = "end_turn"
    usage: _FakeUsage = field(default_factory=_FakeUsage)


class _ScriptedMessages:
    """Scripted client.messages.create — returns responses in order."""

    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> _FakeResponse:
        self.calls.append(kwargs)
        if not self._responses:
            raise RuntimeError("scripted client ran out of responses")
        return self._responses.pop(0)


class _FakeClient:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self.messages = _ScriptedMessages(responses)


def _sample(t_ms: int, name: str = "lateral_work_rate", value: float = 2.4) -> SignalSample:
    return SignalSample(
        timestamp_ms=t_ms, match_id="utr_01", player="A",
        signal_name=name, value=value, baseline_z_score=None, state="ACTIVE_RALLY",
    )


def _transition(t_ms: int = 10_000) -> StateTransition:
    return StateTransition(
        timestamp_ms=t_ms, player="A",
        from_state="PRE_SERVE_RITUAL", to_state="ACTIVE_RALLY",
        reason="kinematic",
    )


def _happy_path_responses() -> list[_FakeResponse]:
    """Three agent turns, each end_turn with thinking + text."""
    return [
        # Analytics Specialist — one turn, no tools
        _FakeResponse(
            content=[
                _FakeBlock(type="thinking", thinking="scanning 7 signal arrays for anomalies"),
                _FakeBlock(
                    type="text",
                    text="Found: lateral_work_rate z=+2.3 at t=42s. "
                         "recovery_latency trending upward (+18% over baseline).",
                ),
            ],
            stop_reason="end_turn",
        ),
        # Technical Biomechanics Coach
        _FakeResponse(
            content=[
                _FakeBlock(type="thinking", thinking="mapping anomalies to biomech literature"),
                _FakeBlock(
                    type="text",
                    text="Elevated lateral work rate + recovery lag = quad/glute fatigue. "
                         "Player compensating with upper-body torque — load-transfer degrading.",
                ),
            ],
            stop_reason="end_turn",
        ),
        # Tactical Strategist
        _FakeResponse(
            content=[
                _FakeBlock(type="thinking", thinking="synthesizing tactical consequences"),
                _FakeBlock(
                    type="text",
                    text="Exploit compromised lateral-recovery: drive cross-court-deep, "
                         "force stretch-wide responses. Peak window: next 12-18 points.",
                ),
            ],
            stop_reason="end_turn",
        ),
    ]


# ──────────────────────────── Happy path ────────────────────────────


@pytest.mark.asyncio
async def test_happy_path_produces_valid_agent_trace() -> None:
    client = _FakeClient(_happy_path_responses())
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=42_000), _sample(t_ms=50_000, value=2.7)],
        transitions=[_transition()],
    )
    trace = await generate_scouting_report(
        client,
        ctx,
        match_id="utr_01",
        player_a_name="Alice",
        committee_goal="Analyze Alice's fatigue drift in the last rally.",
    )

    assert isinstance(trace, AgentTrace)
    assert trace.match_id == "utr_01"
    assert len(trace.steps) == 3
    assert [s.agent_name for s in trace.steps] == [
        ANALYTICS_SPECIALIST_NAME, TECHNICAL_COACH_NAME, TACTICAL_STRATEGIST_NAME,
    ]
    # Each step must contain at least one text event + at least one thinking event
    for step in trace.steps:
        kinds = [e.kind for e in step.events]
        assert "thinking" in kinds, f"{step.agent_name} missing thinking event"
        assert "text" in kinds, f"{step.agent_name} missing text event"

    # Handoffs between steps are captured (between 3 agents → 2 handoffs)
    all_handoffs = [
        e for s in trace.steps for e in s.events if isinstance(e, TraceHandoff)
    ]
    assert len(all_handoffs) == 2
    assert all_handoffs[0].from_agent == ANALYTICS_SPECIALIST_NAME
    assert all_handoffs[0].to_agent == TECHNICAL_COACH_NAME
    assert all_handoffs[1].from_agent == TECHNICAL_COACH_NAME
    assert all_handoffs[1].to_agent == TACTICAL_STRATEGIST_NAME

    # Final report = Tactical Strategist's last text event
    assert "cross-court-deep" in trace.final_report_markdown.lower() or \
           "tactic" in trace.final_report_markdown.lower() or \
           "exploit" in trace.final_report_markdown.lower()


@pytest.mark.asyncio
async def test_real_handoff_cascading_inputs() -> None:
    """Each agent's user message must contain the PRIOR agent's output
    (real handoff), not the raw ToolContext.signals dump.
    """
    client = _FakeClient(_happy_path_responses())
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=42_000)],
        transitions=[_transition()],
    )
    await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice",
        committee_goal="Test handoff cascading.",
    )
    calls = client.messages.calls
    assert len(calls) == 3

    # Call 1 (Analytics): user message should reference signal summary / goal
    call_1_user = calls[0]["messages"][0]["content"]
    assert "committee" in call_1_user.lower() or "fatigue" in call_1_user.lower() or \
           "goal" in call_1_user.lower() or "handoff" in call_1_user.lower() or \
           "analyze" in call_1_user.lower() or "alice" in call_1_user.lower()

    # Call 2 (Technical): user message MUST contain analytics output (z=+2.3, lateral...)
    call_2_user = calls[1]["messages"][0]["content"]
    assert "lateral_work_rate" in call_2_user or "z=+2.3" in call_2_user or \
           "recovery_latency" in call_2_user, (
        f"Technical Coach did not receive Analytics Specialist's output; got: {call_2_user[:200]}"
    )

    # Call 3 (Tactical): user message MUST contain Technical Coach's biomech narrative
    call_3_user = calls[2]["messages"][0]["content"]
    assert "quad" in call_3_user or "glute" in call_3_user or "fatigue" in call_3_user or \
           "upper-body torque" in call_3_user or "load-transfer" in call_3_user, (
        f"Tactical Strategist did not receive Technical Coach's output; got: {call_3_user[:200]}"
    )


@pytest.mark.asyncio
async def test_trace_events_have_monotonic_timestamps() -> None:
    client = _FakeClient(_happy_path_responses())
    ctx = ToolContext(match_id="utr_01", signals=[_sample(t_ms=1000)], transitions=[])
    trace = await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice", committee_goal="t"
    )
    for step in trace.steps:
        last_t = -1
        for ev in step.events:
            assert ev.t_ms >= last_t
            last_t = ev.t_ms
    # Cross-step: step[i].started_at_ms >= step[i-1].completed_at_ms
    for i in range(1, len(trace.steps)):
        assert trace.steps[i].started_at_ms >= trace.steps[i - 1].completed_at_ms


@pytest.mark.asyncio
async def test_trace_is_json_serializable_and_round_trips() -> None:
    client = _FakeClient(_happy_path_responses())
    ctx = ToolContext(match_id="utr_01", signals=[_sample(t_ms=1000)], transitions=[])
    trace = await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice", committee_goal="t"
    )
    as_json = trace.model_dump_json()
    restored = AgentTrace.model_validate_json(as_json)
    assert restored == trace


# ──────────────────────────── Analytics Specialist tool-use loop ────────────────────────────


@pytest.mark.asyncio
async def test_analytics_specialist_tool_use_loop_captures_tool_calls() -> None:
    """Analytics Specialist needs DuckDB tool access. Verify tool_call +
    tool_result events appear in the trace."""
    responses = [
        # Analytics Specialist round 1 — tool_use
        _FakeResponse(
            content=[
                _FakeBlock(type="thinking", thinking="need to query the signal window"),
                _FakeBlock(
                    type="tool_use", id="tu_1", name="get_signal_window",
                    input={"player": "A", "signal_name": "lateral_work_rate",
                           "t_ms": 42_000, "window_sec": 15.0},
                ),
            ],
            stop_reason="tool_use",
        ),
        # Analytics Specialist round 2 — end_turn after seeing tool result
        _FakeResponse(
            content=[
                _FakeBlock(type="text", text="Lateral work rate mean=2.4, elevated."),
            ],
            stop_reason="end_turn",
        ),
        # Technical Coach — end_turn
        _FakeResponse(
            content=[_FakeBlock(type="text", text="Quad fatigue likely.")],
            stop_reason="end_turn",
        ),
        # Tactical Strategist — end_turn
        _FakeResponse(
            content=[_FakeBlock(type="text", text="Drive cross-court deep.")],
            stop_reason="end_turn",
        ),
    ]
    client = _FakeClient(responses)
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=42_000), _sample(t_ms=50_000)],
        transitions=[],
    )
    trace = await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice", committee_goal="t"
    )

    analytics_step = trace.steps[0]
    kinds = [e.kind for e in analytics_step.events]
    assert "tool_call" in kinds, "Analytics Specialist didn't record tool_call event"
    assert "tool_result" in kinds, "Analytics Specialist didn't record tool_result event"

    tool_calls = [e for e in analytics_step.events if isinstance(e, TraceToolCall)]
    tool_results = [e for e in analytics_step.events if isinstance(e, TraceToolResult)]
    assert len(tool_calls) == 1
    assert len(tool_results) == 1
    assert tool_calls[0].tool_name == "get_signal_window"
    assert tool_results[0].tool_name == "get_signal_window"
    # Tool result must be JSON-parsable (frontend renders it)
    parsed = json.loads(tool_results[0].output_json)
    assert "mean" in parsed or "count" in parsed or "samples" in parsed


# ──────────────────────────── Error resilience ────────────────────────────


@pytest.mark.asyncio
async def test_api_error_in_middle_agent_produces_graceful_partial_trace() -> None:
    """If Technical Coach fails, we still get a valid AgentTrace with:
      - Analytics Specialist step: complete
      - Technical Coach step: error-marker text event
      - Tactical Strategist step: still runs, even if it has minimal technical input
    Invariant: generate_scouting_report NEVER raises into precompute.py.
    """
    class _BoomOnSecondCall:
        def __init__(self) -> None:
            self._n = 0
            self.messages = self  # type: ignore[assignment]

        async def create(self, **kwargs: Any) -> _FakeResponse:
            self._n += 1
            if self._n == 1:
                return _FakeResponse(
                    content=[_FakeBlock(type="text", text="z=+2.3 lateral")],
                )
            if self._n == 2:
                raise RuntimeError("simulated Anthropic 529")
            return _FakeResponse(
                content=[_FakeBlock(type="text", text="fallback tactical play")],
            )

    client = _BoomOnSecondCall()
    ctx = ToolContext(match_id="utr_01", signals=[_sample(t_ms=1000)], transitions=[])
    trace = await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice", committee_goal="t"  # type: ignore[arg-type]
    )
    assert isinstance(trace, AgentTrace)
    assert len(trace.steps) == 3
    # Technical Coach step should have an error marker, not crash
    tech_text = " ".join(
        e.content for e in trace.steps[1].events if isinstance(e, TraceText)
    )
    assert "[error" in tech_text.lower() or "fail" in tech_text.lower() or \
           "529" in tech_text, (
        f"Expected error marker in Technical Coach step; got: {tech_text[:200]}"
    )


# ──────────────────────────── Empty input ────────────────────────────


# ──────────────────────────── PATTERN-059: Shared Blackboard (additive handoffs) ────────────────────────────


@pytest.mark.asyncio
async def test_baseline_context_appears_in_every_agent_user_message() -> None:
    """Shared Blackboard invariant: every agent's user message MUST carry the
    baseline context (signal taxonomy + player identity + match_id) so downstream
    agents are never context-starved by an Analytics Specialist that under-reports.
    """
    client = _FakeClient(_happy_path_responses())
    ctx = ToolContext(
        match_id="utr_baseline_01",
        signals=[
            _sample(t_ms=1000, name="lateral_work_rate"),
            _sample(t_ms=2000, name="crouch_depth_degradation_deg"),
        ],
        transitions=[_transition(t_ms=1500)],
    )
    await generate_scouting_report(
        client, ctx, match_id="utr_baseline_01", player_a_name="Alice",
        committee_goal="Probe fatigue drift across last 5 rallies.",
    )

    assert len(client.messages.calls) == 3
    for i, call in enumerate(client.messages.calls):
        user_msg = call["messages"][0]["content"]
        # Baseline MUST include the committee goal so Technical/Tactical can
        # situate their synthesis in the original scouting mandate.
        assert "fatigue drift" in user_msg.lower() or \
               "probe fatigue" in user_msg.lower() or \
               "committee" in user_msg.lower(), (
            f"Agent {i} user message missing baseline goal marker"
        )
        # Baseline MUST include the match_id so a future MultiBatch can key replay
        assert "utr_baseline_01" in user_msg, (
            f"Agent {i} user message missing match_id from baseline"
        )
        # Baseline MUST include the player identity so every agent knows WHO
        assert "Alice" in user_msg or "Player A" in user_msg, (
            f"Agent {i} user message missing player identity"
        )
        # Baseline MUST enumerate the signal taxonomy so tool-less agents
        # cannot hallucinate signals that don't exist
        assert "signal taxonomy" in user_msg.lower() or \
               "samples across" in user_msg.lower() or \
               "lateral_work_rate" in user_msg, (
            f"Agent {i} user message missing signal taxonomy baseline"
        )


@pytest.mark.asyncio
async def test_downstream_agents_get_both_baseline_AND_upstream_focus() -> None:
    """The blackboard is ADDITIVE: Technical/Tactical agents see the baseline
    PLUS the upstream agent's output as the focus of their synthesis. Regression
    guard against a future refactor that replaces `_compose_user_prompt` with
    substitutive semantics.
    """
    client = _FakeClient(_happy_path_responses())
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=1000, name="lateral_work_rate")],
        transitions=[],
    )
    await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice", committee_goal="t",
    )

    tech_user_msg = client.messages.calls[1]["messages"][0]["content"]
    tact_user_msg = client.messages.calls[2]["messages"][0]["content"]

    # Technical sees baseline (match_id) AND Analytics focus (anomaly text)
    assert "utr_01" in tech_user_msg, "Technical missing baseline"
    assert "z=+2.3" in tech_user_msg or "lateral" in tech_user_msg.lower() or \
           "recovery_latency" in tech_user_msg.lower(), (
        "Technical missing Analytics focus layer"
    )

    # Tactical sees baseline (match_id) AND Technical focus (biomech narrative)
    assert "utr_01" in tact_user_msg, "Tactical missing baseline"
    assert "quad" in tact_user_msg or "glute" in tact_user_msg or \
           "fatigue" in tact_user_msg or "upper-body torque" in tact_user_msg or \
           "load-transfer" in tact_user_msg, "Tactical missing Technical focus layer"


# ──────────────────────────── GOTCHA-027: Trace Payload Explosion ────────────────────────────


@pytest.mark.asyncio
async def test_tool_result_truncated_when_output_json_exceeds_limit() -> None:
    """A fat tool result (e.g., DuckDB returning hundreds of samples) must NOT
    bloat agent_trace.json. Truncate with a clear marker so the UI knows.
    """
    from backend.agents.scouting_committee import (
        TRACE_MAX_OUTPUT_JSON_CHARS,
        TRACE_TRUNCATION_MARKER,
    )
    # 500 samples in a signal window — each sample is a small dict, but the total
    # JSON easily exceeds 2000 chars
    huge_signals = [_sample(t_ms=i * 100, value=float(i)) for i in range(500)]

    responses = [
        # Analytics round 1 — tool_use (the tool will return the huge payload)
        _FakeResponse(
            content=[
                _FakeBlock(
                    type="tool_use", id="tu_1", name="get_signal_window",
                    input={"player": "A", "signal_name": "lateral_work_rate",
                           "t_ms": 50_000, "window_sec": 60.0},
                ),
            ],
            stop_reason="tool_use",
        ),
        # Analytics round 2 — end_turn
        _FakeResponse(
            content=[_FakeBlock(type="text", text="Saw the big window.")],
            stop_reason="end_turn",
        ),
        # Technical — end_turn
        _FakeResponse(
            content=[_FakeBlock(type="text", text="Quad fatigue.")],
            stop_reason="end_turn",
        ),
        # Tactical — end_turn
        _FakeResponse(
            content=[_FakeBlock(type="text", text="Exploit it.")],
            stop_reason="end_turn",
        ),
    ]
    client = _FakeClient(responses)
    ctx = ToolContext(match_id="utr_01", signals=huge_signals, transitions=[])

    trace = await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice", committee_goal="t"
    )

    # Find the tool_result event in the Analytics step
    analytics_step = trace.steps[0]
    tool_results = [e for e in analytics_step.events if isinstance(e, TraceToolResult)]
    assert len(tool_results) == 1
    tr = tool_results[0]
    # Must be truncated — length <= limit AND marker appended
    assert len(tr.output_json) <= TRACE_MAX_OUTPUT_JSON_CHARS
    assert tr.output_json.endswith(TRACE_TRUNCATION_MARKER), (
        f"Expected truncation marker at end; got ...{tr.output_json[-60:]}"
    )


@pytest.mark.asyncio
async def test_small_tool_result_is_NOT_truncated() -> None:
    """A normal tool result (well under the limit) MUST pass through unchanged
    — no spurious truncation marker on small payloads."""
    from backend.agents.scouting_committee import TRACE_TRUNCATION_MARKER
    responses = [
        _FakeResponse(
            content=[
                _FakeBlock(
                    type="tool_use", id="tu_1", name="get_signal_window",
                    input={"player": "A", "signal_name": "lateral_work_rate",
                           "t_ms": 5000, "window_sec": 10.0},
                ),
            ],
            stop_reason="tool_use",
        ),
        _FakeResponse(
            content=[_FakeBlock(type="text", text="Window normal.")],
            stop_reason="end_turn",
        ),
        _FakeResponse(
            content=[_FakeBlock(type="text", text="Nothing concerning.")],
            stop_reason="end_turn",
        ),
        _FakeResponse(
            content=[_FakeBlock(type="text", text="No tactical change.")],
            stop_reason="end_turn",
        ),
    ]
    client = _FakeClient(responses)
    # 2 tiny signal samples — tool output is clearly under the 2000-char limit
    ctx = ToolContext(match_id="utr_01", signals=[_sample(t_ms=5000)], transitions=[])
    trace = await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice", committee_goal="t"
    )
    analytics_step = trace.steps[0]
    tool_results = [e for e in analytics_step.events if isinstance(e, TraceToolResult)]
    assert len(tool_results) == 1
    assert TRACE_TRUNCATION_MARKER not in tool_results[0].output_json, (
        "Small tool result should NOT carry truncation marker"
    )


# ──────────────────────────── Edge case (existing) ────────────────────────────


@pytest.mark.asyncio
async def test_empty_signals_produces_minimal_trace() -> None:
    """No signals to analyze? Still produce a valid AgentTrace noting the vacuum."""
    client = _FakeClient(_happy_path_responses())
    ctx = ToolContext(match_id="utr_01", signals=[], transitions=[])
    trace = await generate_scouting_report(
        client, ctx, match_id="utr_01", player_a_name="Alice",
        committee_goal="No anomalies expected.",
    )
    assert isinstance(trace, AgentTrace)
    assert len(trace.steps) == 3
