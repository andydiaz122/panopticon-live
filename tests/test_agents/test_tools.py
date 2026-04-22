"""Tests for backend/agents/tools.py — deterministic Opus tool executors.

Covers:
- get_signal_window: filter correctness, output caps, mean/std/slope, empty result
- compare_to_baseline: z-score math, zero-variance guard, empty windows, delta_pct
- get_rally_context: last-N slicing, future-event exclusion
- get_match_phase: returns context phase verbatim
- dispatch_tool: unknown-tool error, validation error, never-raise contract
- TOOL_SCHEMAS format: Anthropic SDK compatibility
"""

from __future__ import annotations

import math

import pytest

from backend.agents.tools import (
    DEFAULT_BASELINE_WINDOW_SEC,
    DEFAULT_WINDOW_SEC,
    MAX_SAMPLES_RETURNED,
    TOOL_EXECUTORS,
    TOOL_SCHEMAS,
    ToolContext,
    dispatch_tool,
    execute_compare_to_baseline,
    execute_get_match_phase,
    execute_get_rally_context,
    execute_get_signal_window,
)
from backend.db.schema import SignalSample, StateTransition

# ──────────────────────────── Fixtures ────────────────────────────


def _sample(
    t_ms: int,
    value: float | None = 1.0,
    player: str = "A",
    signal_name: str = "recovery_latency_ms",
    state: str = "ACTIVE_RALLY",
) -> SignalSample:
    return SignalSample(
        timestamp_ms=t_ms,
        match_id="utr_01",
        player=player,
        signal_name=signal_name,
        value=value,
        baseline_z_score=None,
        state=state,
    )


def _transition(
    t_ms: int,
    player: str = "A",
    from_state: str = "PRE_SERVE_RITUAL",
    to_state: str = "ACTIVE_RALLY",
    reason: str = "kinematic",
) -> StateTransition:
    return StateTransition(
        timestamp_ms=t_ms,
        player=player,
        from_state=from_state,
        to_state=to_state,
        reason=reason,
    )


# ──────────────────────────── get_signal_window ────────────────────────────


def test_get_signal_window_returns_samples_in_range() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=ms, value=float(ms)) for ms in (500, 1500, 2500, 3500)],
    )
    out = execute_get_signal_window(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 3000, "window_sec": 2.0},
    )
    # Window is (3000 - 2000, 3000] = (1000, 3000] → includes 1500, 2500 but NOT 500 or 3500
    returned_ts = [s["timestamp_ms"] for s in out["samples"]]
    assert returned_ts == [1500, 2500]
    assert out["count"] == 2


def test_get_signal_window_filters_by_player_and_signal() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        signals=[
            _sample(t_ms=100, value=1.0, player="A", signal_name="recovery_latency_ms"),
            _sample(t_ms=200, value=2.0, player="B", signal_name="recovery_latency_ms"),
            _sample(t_ms=300, value=3.0, player="A", signal_name="lateral_work_rate"),
            _sample(t_ms=400, value=4.0, player="A", signal_name="recovery_latency_ms"),
        ],
    )
    out = execute_get_signal_window(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 1000, "window_sec": 10.0},
    )
    assert out["count"] == 2
    vals = [s["value"] for s in out["samples"]]
    assert vals == [1.0, 4.0]


def test_get_signal_window_caps_output_at_max_samples() -> None:
    n = MAX_SAMPLES_RETURNED + 30
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=i * 10, value=float(i)) for i in range(n)],
    )
    out = execute_get_signal_window(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": n * 10, "window_sec": 120.0},
    )
    # Full count reported, but samples list truncated to tail (most recent)
    assert out["count"] == n
    assert len(out["samples"]) == MAX_SAMPLES_RETURNED
    # Last returned sample is the most recent
    assert out["samples"][-1]["value"] == pytest.approx(float(n - 1))


def test_get_signal_window_mean_and_std() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=ms, value=val) for ms, val in [(100, 2.0), (200, 4.0), (300, 6.0)]],
    )
    out = execute_get_signal_window(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 400, "window_sec": 1.0},
    )
    assert out["mean"] == pytest.approx(4.0, abs=1e-9)
    # std with ddof=0 of [2,4,6] = sqrt(((-2)^2 + 0 + 2^2)/3) = sqrt(8/3)
    assert out["std"] == pytest.approx(math.sqrt(8.0 / 3), abs=1e-3)


def test_get_signal_window_trend_slope_linear() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        # Perfect linear trend: value = 2 * t_sec + 1
        signals=[_sample(t_ms=ms, value=2.0 * (ms / 1000) + 1.0) for ms in (1000, 2000, 3000, 4000)],
    )
    out = execute_get_signal_window(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 5000, "window_sec": 10.0},
    )
    assert out["trend_slope_per_sec"] == pytest.approx(2.0, abs=1e-3)


def test_get_signal_window_slope_none_when_fewer_than_3_points() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=100, value=1.0), _sample(t_ms=200, value=2.0)],
    )
    out = execute_get_signal_window(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 500, "window_sec": 10.0},
    )
    assert out["trend_slope_per_sec"] is None


def test_get_signal_window_handles_empty_result() -> None:
    ctx = ToolContext(match_id="utr_01", signals=[])
    out = execute_get_signal_window(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 5000, "window_sec": 10.0},
    )
    assert out["count"] == 0
    assert out["samples"] == []
    assert out["mean"] is None
    assert out["std"] is None
    assert out["trend_slope_per_sec"] is None


def test_get_signal_window_ignores_none_and_nan_values_in_stats() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        signals=[
            _sample(t_ms=100, value=2.0),
            _sample(t_ms=200, value=None),
            _sample(t_ms=300, value=float("nan")),
            _sample(t_ms=400, value=4.0),
        ],
    )
    out = execute_get_signal_window(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 500, "window_sec": 10.0},
    )
    # count counts ALL rows in window; stats ignore None/NaN
    assert out["count"] == 4
    assert out["mean"] == pytest.approx(3.0, abs=1e-9)


# ──────────────────────────── compare_to_baseline ────────────────────────────


def test_compare_to_baseline_z_score_positive() -> None:
    # Baseline (first 30s): values 1,2,3 → mean=2, std=sqrt(2/3)
    # Current (last 10s ending at 40s): values 10 → z = (10 - 2) / sqrt(2/3)
    ctx = ToolContext(
        match_id="utr_01",
        signals=[
            _sample(t_ms=5000, value=1.0),
            _sample(t_ms=10000, value=2.0),
            _sample(t_ms=15000, value=3.0),
            _sample(t_ms=35000, value=10.0),
        ],
    )
    out = execute_compare_to_baseline(
        ctx,
        {
            "player": "A", "signal_name": "recovery_latency_ms", "t_ms": 40000,
            "baseline_window_sec": 30.0, "current_window_sec": 10.0,
        },
    )
    expected_std = math.sqrt(2.0 / 3)
    assert out["baseline_mean"] == pytest.approx(2.0)
    assert out["baseline_std"] == pytest.approx(expected_std, abs=1e-3)
    assert out["current_mean"] == pytest.approx(10.0)
    assert out["z_score"] == pytest.approx((10.0 - 2.0) / expected_std, abs=1e-2)


def test_compare_to_baseline_zero_variance_returns_none_z_score() -> None:
    # All baseline samples equal -> std == 0 -> guard fires
    ctx = ToolContext(
        match_id="utr_01",
        signals=[
            _sample(t_ms=1000, value=5.0),
            _sample(t_ms=2000, value=5.0),
            _sample(t_ms=3000, value=5.0),
            _sample(t_ms=35000, value=7.0),
        ],
    )
    out = execute_compare_to_baseline(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 40000},
    )
    # Baseline std is 0 -> z_score must be None (USER-CORRECTION-015 pattern)
    assert out["baseline_std"] == pytest.approx(0.0)
    assert out["z_score"] is None


def test_compare_to_baseline_empty_baseline_returns_nones() -> None:
    # Only current samples, no baseline window hits
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=50_000, value=3.0)],
    )
    out = execute_compare_to_baseline(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 55_000},
    )
    assert out["baseline_mean"] is None
    assert out["baseline_std"] is None
    assert out["z_score"] is None
    assert out["delta_pct"] is None


def test_compare_to_baseline_delta_pct() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        signals=[
            _sample(t_ms=1000, value=100.0),
            _sample(t_ms=2000, value=100.0),
            _sample(t_ms=35_000, value=120.0),
        ],
    )
    out = execute_compare_to_baseline(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 40_000},
    )
    # 100 baseline, 120 current -> +20%
    assert out["delta_pct"] == pytest.approx(20.0, abs=1e-2)


def test_compare_to_baseline_uses_defaults() -> None:
    """Defaults come from the Pydantic model, not from magic constants in the executor."""
    ctx = ToolContext(match_id="utr_01", signals=[])
    out = execute_compare_to_baseline(
        ctx,
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 10_000},
    )
    assert out["baseline_window_sec"] == DEFAULT_BASELINE_WINDOW_SEC
    assert out["current_window_sec"] == DEFAULT_WINDOW_SEC


# ──────────────────────────── get_rally_context ────────────────────────────


def test_get_rally_context_returns_last_n() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        transitions=[_transition(t_ms=i * 1000) for i in range(1, 11)],
    )
    out = execute_get_rally_context(ctx, {"t_ms": 12_000, "last_n": 3})
    assert out["count_total"] == 10
    assert out["count_returned"] == 3
    ts = [t["timestamp_ms"] for t in out["transitions"]]
    assert ts == [8000, 9000, 10_000]


def test_get_rally_context_excludes_future_transitions() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        transitions=[
            _transition(t_ms=1000),
            _transition(t_ms=5000),
            _transition(t_ms=9000),  # in the future relative to t_ms=7000
        ],
    )
    out = execute_get_rally_context(ctx, {"t_ms": 7000, "last_n": 10})
    # Future one excluded
    ts = [t["timestamp_ms"] for t in out["transitions"]]
    assert ts == [1000, 5000]


def test_get_rally_context_handles_empty_history() -> None:
    ctx = ToolContext(match_id="utr_01", transitions=[])
    out = execute_get_rally_context(ctx, {"t_ms": 1000, "last_n": 5})
    assert out["transitions"] == []
    assert out["count_total"] == 0


# ──────────────────────────── get_match_phase ────────────────────────────


def test_get_match_phase_returns_context_phase() -> None:
    ctx = ToolContext(match_id="utr_01", match_phase="SET_1")
    out = execute_get_match_phase(ctx, {"t_ms": 12_345})
    assert out["match_phase"] == "SET_1"
    assert out["t_ms"] == 12_345


def test_get_match_phase_defaults_to_unknown() -> None:
    ctx = ToolContext(match_id="utr_01")
    out = execute_get_match_phase(ctx, {"t_ms": 0})
    assert out["match_phase"] == "UNKNOWN"


# ──────────────────────────── dispatch_tool ────────────────────────────


def test_dispatch_tool_unknown_returns_error() -> None:
    ctx = ToolContext(match_id="utr_01")
    out = dispatch_tool(ctx, "not_a_tool", {})
    assert out["error"] == "unknown_tool"
    assert out["tool_name"] == "not_a_tool"


def test_dispatch_tool_invalid_input_returns_error_not_exception() -> None:
    """Pydantic validation errors must NOT propagate — they become structured {"error": ...}."""
    ctx = ToolContext(match_id="utr_01")
    out = dispatch_tool(ctx, "get_signal_window", {"player": "INVALID_PLAYER"})
    assert out["error"] == "invalid_input"
    assert out["tool_name"] == "get_signal_window"
    assert "details" in out


def test_dispatch_tool_catches_arbitrary_exceptions() -> None:
    """Even non-ValidationError crashes inside an executor must be caught."""
    ctx = ToolContext(match_id="utr_01")
    # Register a temporary broken executor to exercise the general-exception path
    broken_name = "_test_broken_tool"

    def _boom(ctx_: ToolContext, raw: dict) -> dict:
        raise RuntimeError("synthetic failure")

    TOOL_EXECUTORS[broken_name] = _boom
    try:
        out = dispatch_tool(ctx, broken_name, {})
    finally:
        del TOOL_EXECUTORS[broken_name]
    assert out["error"] == "tool_exception"
    assert "synthetic failure" in out["details"]


def test_dispatch_tool_happy_path_forwards_output() -> None:
    ctx = ToolContext(
        match_id="utr_01",
        signals=[_sample(t_ms=500, value=1.0)],
    )
    out = dispatch_tool(
        ctx,
        "get_signal_window",
        {"player": "A", "signal_name": "recovery_latency_ms", "t_ms": 1000, "window_sec": 5.0},
    )
    # On success, no 'error' key
    assert "error" not in out
    assert out["count"] == 1


# ──────────────────────────── TOOL_SCHEMAS format ────────────────────────────


def test_tool_schemas_are_anthropic_format() -> None:
    """Each schema must have name + description + input_schema — Anthropic tool API requirement."""
    for schema in TOOL_SCHEMAS:
        assert set(schema.keys()) == {"name", "description", "input_schema"}
        assert isinstance(schema["name"], str) and schema["name"]
        assert isinstance(schema["description"], str) and len(schema["description"]) > 10
        assert schema["input_schema"]["type"] == "object"
        assert "properties" in schema["input_schema"]


def test_tool_schemas_match_registry_keys() -> None:
    """Every schema's name must map to a real executor in TOOL_EXECUTORS (no silent drift)."""
    schema_names = {s["name"] for s in TOOL_SCHEMAS}
    assert schema_names == set(TOOL_EXECUTORS.keys())


def test_tool_schemas_expected_tools_present() -> None:
    """Lock in the four canonical tool names (per opus-47-creative-medium skill)."""
    names = {s["name"] for s in TOOL_SCHEMAS}
    assert names == {
        "get_signal_window",
        "compare_to_baseline",
        "get_rally_context",
        "get_match_phase",
    }
