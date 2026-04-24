"""Tests for the AgentTrace schema (PATTERN-056: Multi-Agent Trace Playback).

Contract under test:
  - TraceEvent is a discriminated union over `kind` field — the frontend TypeScript
    consumer MUST be able to narrow by `kind` to render the right pill type.
  - AgentStep.events is a monotonically non-decreasing list by `t_ms`.
  - AgentTrace.steps are chronologically ordered by `started_at_ms`.
  - Round-trip: AgentTrace → JSON → AgentTrace is lossless.
  - Every field uses FLOAT_SERIALIZE_DECIMALS rounding (consistency with rest of schema).

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.db.schema import (
    AgentStep,
    AgentTrace,
    TraceHandoff,
    TraceText,
    TraceThinking,
    TraceToolCall,
    TraceToolResult,
)


# ──────────────────────────── Discriminated-union narrowing ────────────────────────────


def test_trace_thinking_has_kind_literal() -> None:
    ev = TraceThinking(t_ms=100, content="reasoning about anomaly")
    assert ev.kind == "thinking"


def test_trace_tool_call_has_kind_literal() -> None:
    ev = TraceToolCall(
        t_ms=200, tool_name="query_duckdb", input_json='{"sql": "SELECT 1"}'
    )
    assert ev.kind == "tool_call"


def test_trace_tool_result_has_kind_literal() -> None:
    ev = TraceToolResult(
        t_ms=300, tool_name="query_duckdb", output_json='{"rows": []}', is_error=False
    )
    assert ev.kind == "tool_result"


def test_trace_text_has_kind_literal() -> None:
    ev = TraceText(t_ms=400, content="Analytics complete.")
    assert ev.kind == "text"


def test_trace_handoff_has_kind_literal() -> None:
    ev = TraceHandoff(
        t_ms=500,
        from_agent="Analytics Specialist",
        to_agent="Technical Biomechanics Coach",
        payload_summary="3 anomalies; lateral work rate -18%",
    )
    assert ev.kind == "handoff"


def test_agent_step_accepts_heterogeneous_event_list() -> None:
    """The discriminated union must let us mix event types inside AgentStep.events."""
    step = AgentStep(
        agent_name="Analytics Specialist",
        agent_role="Quant",
        started_at_ms=0,
        completed_at_ms=1000,
        events=[
            TraceThinking(t_ms=10, content="starting analysis"),
            TraceToolCall(t_ms=100, tool_name="query", input_json="{}"),
            TraceToolResult(t_ms=400, tool_name="query", output_json="{}"),
            TraceText(t_ms=800, content="done"),
        ],
    )
    assert len(step.events) == 4
    assert [e.kind for e in step.events] == ["thinking", "tool_call", "tool_result", "text"]


# ──────────────────────────── JSON round-trip lossless ────────────────────────────


def test_agent_trace_json_round_trip_preserves_discriminators() -> None:
    trace = AgentTrace(
        match_id="utr_01",
        generated_at=datetime(2026, 4, 23, 12, 0, 0, tzinfo=timezone.utc),
        committee_goal="Analyze Player A fatigue drift.",
        steps=[
            AgentStep(
                agent_name="Analytics Specialist",
                agent_role="Quant",
                started_at_ms=0,
                completed_at_ms=5000,
                events=[
                    TraceThinking(t_ms=50, content="inspecting 7 signal arrays"),
                    TraceHandoff(
                        t_ms=4800,
                        from_agent="Analytics Specialist",
                        to_agent="Technical Biomechanics Coach",
                        payload_summary="z=2.8 in crouch_depth; z=2.1 in recovery_latency",
                    ),
                ],
            ),
        ],
        final_report_markdown="## Report\nFatigue drift detected.",
        total_compute_ms=48_321,
    )

    # Dump to JSON, reload, compare
    serialized = trace.model_dump_json()
    restored = AgentTrace.model_validate_json(serialized)

    assert restored.match_id == trace.match_id
    assert restored.total_compute_ms == trace.total_compute_ms
    # Discriminator narrowing must survive the round-trip
    assert restored.steps[0].events[0].kind == "thinking"
    assert restored.steps[0].events[1].kind == "handoff"
    # Type-level assertion: the second event must be a TraceHandoff after round-trip
    handoff = restored.steps[0].events[1]
    assert isinstance(handoff, TraceHandoff)
    assert handoff.from_agent == "Analytics Specialist"


def test_agent_trace_round_trip_via_dict() -> None:
    """Round-trip via model_dump -> model_validate (not JSON string) — catches
    any Pydantic v2 discriminator bugs that stringification would mask."""
    step = AgentStep(
        agent_name="Tactical Strategist",
        agent_role="Strategist",
        started_at_ms=10_000,
        completed_at_ms=15_000,
        events=[TraceText(t_ms=10_100, content="Exploit compromised split-step.")],
    )
    trace = AgentTrace(
        match_id="utr_01",
        generated_at=datetime(2026, 4, 23, tzinfo=timezone.utc),
        committee_goal="Test",
        steps=[step],
        final_report_markdown="done",
        total_compute_ms=5000,
    )

    dumped = trace.model_dump()
    restored = AgentTrace.model_validate(dumped)

    assert restored == trace


# ──────────────────────────── Timeline monotonicity ────────────────────────────


def test_agent_step_rejects_events_with_decreasing_t_ms() -> None:
    """Replay correctness requires monotonic event timestamps within a step."""
    with pytest.raises(ValidationError, match=r"events.*monotonic|t_ms.*order|non-decreasing"):
        AgentStep(
            agent_name="Analytics Specialist",
            agent_role="Quant",
            started_at_ms=0,
            completed_at_ms=1000,
            events=[
                TraceText(t_ms=500, content="later"),
                TraceText(t_ms=100, content="earlier"),  # violates monotonicity
            ],
        )


def test_agent_step_rejects_completed_before_started() -> None:
    with pytest.raises(ValidationError, match=r"completed_at_ms.*started|started.*before.*completed|completed"):
        AgentStep(
            agent_name="X",
            agent_role="Y",
            started_at_ms=1000,
            completed_at_ms=500,  # earlier than started
            events=[],
        )


def test_agent_trace_steps_must_be_chronological() -> None:
    """Cross-step ordering: later step must not start before earlier step finishes."""
    step_1 = AgentStep(
        agent_name="Analytics Specialist",
        agent_role="Quant",
        started_at_ms=0,
        completed_at_ms=5000,
        events=[],
    )
    step_2_bad = AgentStep(
        agent_name="Technical Biomechanics Coach",
        agent_role="Coach",
        started_at_ms=3000,  # starts BEFORE step_1 finished
        completed_at_ms=8000,
        events=[],
    )
    with pytest.raises(ValidationError, match=r"chronologi|overlap|started_at_ms"):
        AgentTrace(
            match_id="utr_01",
            generated_at=datetime(2026, 4, 23, tzinfo=timezone.utc),
            committee_goal="t",
            steps=[step_1, step_2_bad],
            final_report_markdown="x",
            total_compute_ms=8000,
        )


# ──────────────────────────── Minimal construction ────────────────────────────


def test_agent_trace_accepts_empty_steps_list() -> None:
    """A failed run should still produce a well-formed AgentTrace (zero steps)."""
    trace = AgentTrace(
        match_id="utr_01",
        generated_at=datetime(2026, 4, 23, tzinfo=timezone.utc),
        committee_goal="test",
        steps=[],
        final_report_markdown="no data",
        total_compute_ms=0,
    )
    assert trace.steps == []
    json_str = trace.model_dump_json()
    assert '"steps":[]' in json_str.replace(" ", "")


def test_trace_event_field_forbids_extras() -> None:
    """PanopticonBase pattern: no surprise keys. Regression guard."""
    with pytest.raises(ValidationError, match=r"[Ee]xtra|forbidden"):
        TraceThinking.model_validate(
            {"kind": "thinking", "t_ms": 0, "content": "x", "bogus_field": 1}
        )


# ──────────────────────────── Discriminator selects correct subclass ────────────────────────────


def test_deserializing_heterogeneous_events_picks_correct_subclass() -> None:
    """The frontend will send us trace JSON with mixed `kind` fields — Pydantic
    must route each dict to the right subclass based on `kind`.
    """
    raw = {
        "agent_name": "X",
        "agent_role": "Y",
        "started_at_ms": 0,
        "completed_at_ms": 1000,
        "events": [
            {"kind": "thinking", "t_ms": 10, "content": "ok"},
            {"kind": "tool_call", "t_ms": 20, "tool_name": "q", "input_json": "{}"},
            {"kind": "tool_result", "t_ms": 30, "tool_name": "q", "output_json": "{}", "is_error": False},
            {"kind": "text", "t_ms": 40, "content": "done"},
            {"kind": "handoff", "t_ms": 50, "from_agent": "A", "to_agent": "B", "payload_summary": "p"},
        ],
    }
    step = AgentStep.model_validate(raw)
    assert isinstance(step.events[0], TraceThinking)
    assert isinstance(step.events[1], TraceToolCall)
    assert isinstance(step.events[2], TraceToolResult)
    assert isinstance(step.events[3], TraceText)
    assert isinstance(step.events[4], TraceHandoff)


def test_unknown_kind_rejected() -> None:
    """Future-proofing: adding a new TraceEvent type MUST update the union,
    not silently accept arbitrary `kind` values."""
    with pytest.raises(ValidationError):
        AgentStep.model_validate(
            {
                "agent_name": "X",
                "agent_role": "Y",
                "started_at_ms": 0,
                "completed_at_ms": 100,
                "events": [{"kind": "totally_made_up", "t_ms": 0, "data": "x"}],
            }
        )


# ──────────────────────────── TypeScript-codegen-friendly JSON shape ────────────────────────────


def test_agent_trace_json_has_stable_top_level_shape() -> None:
    """Frontend TypeScript relies on a STABLE JSON shape for zod/TS codegen.
    Any breaking rename here must be caught by this test.
    """
    trace = AgentTrace(
        match_id="utr_01",
        generated_at=datetime(2026, 4, 23, tzinfo=timezone.utc),
        committee_goal="t",
        steps=[],
        final_report_markdown="r",
        total_compute_ms=0,
    )
    data = json.loads(trace.model_dump_json())
    assert set(data.keys()) == {
        "match_id", "generated_at", "committee_goal",
        "steps", "final_report_markdown", "total_compute_ms",
        "match_time_range_ms",
    }


# ──────────────────────────── Phase 4 UX Sync: match timecode anchor ────────────────────────────


def test_agent_trace_defaults_match_time_range_to_none() -> None:
    """Backwards-compat: existing traces without the new field must still load.
    Optional field default is None, indicating 'no signals were analyzed'."""
    trace = AgentTrace(
        match_id="utr_01",
        generated_at=datetime(2026, 4, 23, tzinfo=timezone.utc),
        committee_goal="t",
        steps=[],
        final_report_markdown="r",
        total_compute_ms=0,
    )
    assert trace.match_time_range_ms is None


def test_agent_trace_round_trips_match_time_range() -> None:
    """The [min_ms, max_ms] tuple must survive JSON round-trip so the frontend
    can display it (Orchestration Console MatchTimecodeAnchor chip)."""
    trace = AgentTrace(
        match_id="utr_01",
        generated_at=datetime(2026, 4, 23, tzinfo=timezone.utc),
        committee_goal="t",
        steps=[],
        final_report_markdown="r",
        total_compute_ms=0,
        match_time_range_ms=(1_500, 58_200),
    )
    restored = AgentTrace.model_validate_json(trace.model_dump_json())
    assert restored.match_time_range_ms == (1_500, 58_200)


def test_agent_trace_match_time_range_serializes_to_array() -> None:
    """The TypeScript mirror types it as `[number, number]` — Pydantic serializes
    a tuple to a JSON array. Regression guard against any schema change that
    accidentally emits an object form."""
    trace = AgentTrace(
        match_id="utr_01",
        generated_at=datetime(2026, 4, 23, tzinfo=timezone.utc),
        committee_goal="t",
        steps=[],
        final_report_markdown="r",
        total_compute_ms=0,
        match_time_range_ms=(0, 60_000),
    )
    data = json.loads(trace.model_dump_json())
    assert data["match_time_range_ms"] == [0, 60_000]
