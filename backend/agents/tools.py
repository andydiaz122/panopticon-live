"""Deterministic query tools exposed to Opus 4.7 during OFFLINE precompute.

The tools are NOT more LLMs. Each tool is a pure Python function that queries
the in-memory ToolContext (signals + transitions) and returns a JSON-safe dict.

Design invariants:
  - Inputs validated by Pydantic (model_config frozen + extra="forbid")
  - Outputs are plain dicts (Anthropic SDK serializes them into tool_result blocks)
  - Output size capped to prevent context blow-up (50 samples / 20 transitions)
  - Variance-zero guarded — z_score is None when baseline_std < VARIANCE_FLOOR
    (same discipline as the signal extractors per USER-CORRECTION-015)
  - Pure over the ctx — never mutate the context

Why in-memory (not DuckDB):
  Phase 2 runs inside precompute.py BEFORE writer.flush(). The signals and
  transitions already live in Python memory; a DuckDB round-trip would add
  latency and an SQL-injection surface for zero reasoning benefit. Phase 3's
  live scouting-report agent can swap in a DuckDB-backed implementation
  behind the same TOOL_EXECUTORS registry.

Anthropic SDK compatibility:
  TOOL_SCHEMAS is a list[dict] in Anthropic tool-API format. It can be passed
  directly as `tools=TOOL_SCHEMAS` to `client.messages.create`. Each entry's
  `input_schema` is generated from the corresponding Pydantic model via
  `model_json_schema()`, so there's a SINGLE source of truth for validation.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.db.schema import (
    MatchPhase,
    PlayerProfile,
    PlayerSide,
    QualitativeNarration,
    SignalName,
    SignalSample,
    StateTransition,
)

# ──────────────────────────── Tunables ────────────────────────────

MAX_SAMPLES_RETURNED: int = 50
"""Hard cap on samples in `get_signal_window` output. Keeps tool_result tokens bounded."""

MAX_TRANSITIONS_RETURNED: int = 20
"""Hard cap on transitions in `get_rally_context` output."""

DEFAULT_WINDOW_SEC: float = 10.0
"""Default recency window for get_signal_window."""

DEFAULT_BASELINE_WINDOW_SEC: float = 30.0
"""Default baseline window — the first N seconds of the match define 'normal'."""

VARIANCE_FLOOR: float = 1e-5
"""Below this, baseline_std is effectively zero — return None for z_score."""

# ──────────────────────────── Input schemas ────────────────────────────


class _FrozenModel(BaseModel):
    """Base for tool input schemas — frozen + extra-forbid for dict-hallucination prevention."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class GetSignalWindowInput(_FrozenModel):
    """Inputs to get_signal_window: recent signal values for ONE player + ONE signal."""

    player: PlayerSide
    signal_name: SignalName
    t_ms: int = Field(ge=0, description="Current match time in milliseconds")
    window_sec: float = Field(
        default=DEFAULT_WINDOW_SEC, gt=0.0, le=120.0,
        description="How far back to look (seconds)",
    )


class CompareToBaselineInput(_FrozenModel):
    """Inputs to compare_to_baseline: current value vs opening baseline."""

    player: PlayerSide
    signal_name: SignalName
    t_ms: int = Field(ge=0)
    baseline_window_sec: float = Field(default=DEFAULT_BASELINE_WINDOW_SEC, gt=0.0, le=600.0)
    current_window_sec: float = Field(default=DEFAULT_WINDOW_SEC, gt=0.0, le=120.0)


class GetRallyContextInput(_FrozenModel):
    """Inputs to get_rally_context: recent state-transition history."""

    t_ms: int = Field(ge=0)
    last_n: int = Field(default=MAX_TRANSITIONS_RETURNED, ge=1, le=MAX_TRANSITIONS_RETURNED)


class GetMatchPhaseInput(_FrozenModel):
    """Inputs to get_match_phase: current high-level phase (WARMUP / SET_N / CHANGEOVER)."""

    t_ms: int = Field(ge=0)


class QueryVideoContextInput(_FrozenModel):
    """Inputs to query_video_context_mcp: hand-authored broadcaster narration over a time window.

    Stubbed-MCP tool (G9 — provenance="stubbed_mcp" in trace). Reads from
    authored narrations loaded during precompute's A6 ingestion. Returns
    narration lines whose `timestamp_ms` falls within `time_range_ms`.
    """

    time_range_ms: tuple[int, int] = Field(
        description=(
            "Inclusive (start_ms, end_ms) window in match-time milliseconds. "
            "Narrations whose timestamp_ms falls in this window are returned."
        ),
    )
    video_uri: str = Field(
        default="local:utr_match_01_segment_a.mp4",
        description=(
            "Video identifier. Stubbed for this hackathon — any value accepted; "
            "production would route this to a real Video MCP server."
        ),
    )


# ──────────────────────────── Tool context (read-only data store) ────────────────────────────


@dataclass(frozen=True)
class ToolContext:
    """Read-only view of match state at the moment Opus is invoked.

    Constructed once per coach/designer invocation; passed through to each tool executor.
    Frozen to prevent accidental mutation by tool code.

    A9 additions (`narrations`, `player_profile`): hand-authored broadcaster
    content. The `query_video_context_mcp` tool reads `narrations` to return
    time-windowed narration lines. `player_profile` is referenced by the
    Scouting Committee's user prompts so the swarm cites ATP stats verbatim.
    Both default to empty/None — when no `_authoring/` directory exists, the
    tool still functions and returns an empty list.
    """

    match_id: str
    signals: list[SignalSample] = field(default_factory=list)
    transitions: list[StateTransition] = field(default_factory=list)
    match_phase: MatchPhase = "UNKNOWN"
    """Phase 2 simplification: no phase tracker yet; defaults to UNKNOWN. Phase 3 may wire a score-reader."""
    narrations: tuple[QualitativeNarration, ...] = ()
    """A9: hand-authored broadcaster narrations. Tuple (not list) per G35 —
    frozen=True doesn't stop list.append()."""
    player_profile: PlayerProfile | None = None
    """A9: authored Hurkacz ATP profile card. Referenced by all 3 agents."""


# ──────────────────────────── Helpers ────────────────────────────


def _finite_values(samples: list[SignalSample]) -> list[float]:
    """Extract finite (non-None, non-NaN) float values from a sample list."""
    out: list[float] = []
    for s in samples:
        if s.value is not None and math.isfinite(s.value):
            out.append(s.value)
    return out


def _fit_slope_per_sec(samples: list[SignalSample]) -> float | None:
    """Linear-regression slope of value vs time (seconds). None if <3 finite points or degenerate."""
    pairs = [
        (s.timestamp_ms / 1000.0, s.value)
        for s in samples
        if s.value is not None and math.isfinite(s.value)
    ]
    if len(pairs) < 3:
        return None
    xs_list, ys_list = zip(*pairs, strict=True)
    xs = np.asarray(xs_list, dtype=float)
    ys = np.asarray(ys_list, dtype=float)
    # Guard degenerate x-variance (all samples at same timestamp — shouldn't happen but belt-and-braces)
    if float(np.var(xs)) < VARIANCE_FLOOR:
        return None
    slope = float(np.polyfit(xs, ys, 1)[0])
    return slope if math.isfinite(slope) else None


def _round(v: float | None, ndigits: int = 4) -> float | None:
    return None if v is None else round(v, ndigits)


# ──────────────────────────── Tool executors ────────────────────────────


def execute_get_signal_window(ctx: ToolContext, raw_input: dict[str, Any]) -> dict[str, Any]:
    """Return recent samples + summary statistics for one (player, signal) pair.

    Window is (t_ms - window_sec*1000, t_ms] — inclusive upper bound.
    """
    inp = GetSignalWindowInput.model_validate(raw_input)
    t_lo = inp.t_ms - int(inp.window_sec * 1000)
    window = [
        s for s in ctx.signals
        if s.player == inp.player
        and s.signal_name == inp.signal_name
        and t_lo < s.timestamp_ms <= inp.t_ms
    ]
    values = _finite_values(window)
    mean = float(np.mean(values)) if values else None
    std = float(np.std(values, ddof=0)) if len(values) >= 2 else None
    # Truncate samples list for token safety. Keep MOST RECENT N (tail, not head).
    recent = window[-MAX_SAMPLES_RETURNED:]
    return {
        "player": inp.player,
        "signal_name": inp.signal_name,
        "window_sec": inp.window_sec,
        "t_ms": inp.t_ms,
        "count": len(window),
        "samples": [
            {
                "timestamp_ms": s.timestamp_ms,
                "value": _round(s.value),
                "state": s.state,
            }
            for s in recent
        ],
        "mean": _round(mean),
        "std": _round(std),
        "trend_slope_per_sec": _round(_fit_slope_per_sec(window)),
    }


def execute_compare_to_baseline(ctx: ToolContext, raw_input: dict[str, Any]) -> dict[str, Any]:
    """Compare current window stats against the opening-baseline window stats.

    z_score = (current_mean - baseline_mean) / baseline_std

    Returns z_score=None when baseline_std < VARIANCE_FLOOR (USER-CORRECTION-015).
    """
    inp = CompareToBaselineInput.model_validate(raw_input)
    # Baseline = first baseline_window_sec of match.
    baseline_hi_ms = int(inp.baseline_window_sec * 1000)
    baseline = [
        s for s in ctx.signals
        if s.player == inp.player
        and s.signal_name == inp.signal_name
        and s.timestamp_ms <= baseline_hi_ms
    ]
    # Current = last current_window_sec of match up to t_ms.
    current_lo_ms = inp.t_ms - int(inp.current_window_sec * 1000)
    current = [
        s for s in ctx.signals
        if s.player == inp.player
        and s.signal_name == inp.signal_name
        and current_lo_ms < s.timestamp_ms <= inp.t_ms
    ]
    baseline_vals = _finite_values(baseline)
    current_vals = _finite_values(current)
    baseline_mean = float(np.mean(baseline_vals)) if baseline_vals else None
    baseline_std = float(np.std(baseline_vals, ddof=0)) if len(baseline_vals) >= 2 else None
    current_mean = float(np.mean(current_vals)) if current_vals else None

    z_score: float | None = None
    if (
        baseline_mean is not None
        and baseline_std is not None
        and baseline_std >= VARIANCE_FLOOR
        and current_mean is not None
    ):
        z_score = (current_mean - baseline_mean) / baseline_std

    delta_pct: float | None = None
    if baseline_mean is not None and current_mean is not None and abs(baseline_mean) >= VARIANCE_FLOOR:
        delta_pct = 100.0 * (current_mean - baseline_mean) / baseline_mean

    return {
        "player": inp.player,
        "signal_name": inp.signal_name,
        "t_ms": inp.t_ms,
        "baseline_window_sec": inp.baseline_window_sec,
        "current_window_sec": inp.current_window_sec,
        "baseline_n": len(baseline_vals),
        "current_n": len(current_vals),
        "baseline_mean": _round(baseline_mean),
        "baseline_std": _round(baseline_std),
        "current_mean": _round(current_mean),
        "z_score": _round(z_score),
        "delta_pct": _round(delta_pct, 2),
    }


def execute_get_rally_context(ctx: ToolContext, raw_input: dict[str, Any]) -> dict[str, Any]:
    """Return the last N state transitions up to t_ms.

    Opus infers rally boundaries from patterns like:
      DEAD_TIME -> PRE_SERVE_RITUAL -> ACTIVE_RALLY -> DEAD_TIME
    """
    inp = GetRallyContextInput.model_validate(raw_input)
    past = [t for t in ctx.transitions if t.timestamp_ms <= inp.t_ms]
    recent = past[-inp.last_n:]
    return {
        "t_ms": inp.t_ms,
        "count_total": len(past),
        "count_returned": len(recent),
        "transitions": [
            {
                "timestamp_ms": t.timestamp_ms,
                "player": t.player,
                "from_state": t.from_state,
                "to_state": t.to_state,
                "reason": t.reason,
            }
            for t in recent
        ],
    }


def execute_get_match_phase(ctx: ToolContext, raw_input: dict[str, Any]) -> dict[str, Any]:
    """Return the current high-level match phase (WARMUP / SET_N / TIEBREAK / CHANGEOVER)."""
    inp = GetMatchPhaseInput.model_validate(raw_input)
    return {
        "t_ms": inp.t_ms,
        "match_phase": ctx.match_phase,
    }


def execute_query_video_context_mcp(ctx: ToolContext, raw_input: dict[str, Any]) -> dict[str, Any]:
    """Stubbed-MCP tool — return hand-authored broadcaster narrations for a time window.

    Implementation reads from `ctx.narrations` (loaded during precompute A6
    ingestion from `_authoring/narrations_*.json`). Provenance tag on the
    corresponding TraceToolCall is set to `"stubbed_mcp"` so the UI renders
    a `STUB · Video Context API` chip (G9).

    Contract (documented on the TOOL_SCHEMAS entry): the LLM receives a
    real tool response. In production V2, this executor swaps to a real
    MCP dispatch; the LLM-visible schema + return shape stays identical.
    """
    inp = QueryVideoContextInput.model_validate(raw_input)
    lo_ms, hi_ms = inp.time_range_ms
    if lo_ms > hi_ms:
        return {
            "error": "invalid_range",
            "detail": f"time_range_ms start ({lo_ms}) must be <= end ({hi_ms})",
        }

    hits: list[dict[str, Any]] = []
    for n in ctx.narrations:
        if lo_ms <= n.timestamp_ms <= hi_ms:
            hits.append(
                {
                    "narration_id": n.narration_id,
                    "timestamp_ms": n.timestamp_ms,
                    "match_time_range_ms": list(n.match_time_range_ms),
                    "narration_text": n.narration_text,
                    "biometric_hook": n.biometric_hook,
                    "player_profile_ref": n.player_profile_ref,
                    "narration_kind": n.narration_kind,
                },
            )

    return {
        "video_uri": inp.video_uri,
        "time_range_ms": [lo_ms, hi_ms],
        "narration_count": len(hits),
        "narrations": hits,
        "_provenance_note": (
            "Stubbed — read from local _authoring/ JSON. In V2 this would "
            "route to a real Video MCP server."
        ),
    }


# ──────────────────────────── Anthropic-format tool schemas ────────────────────────────


def _make_schema(name: str, description: str, model: type[BaseModel]) -> dict[str, Any]:
    """Build an Anthropic-API tool spec from a Pydantic input model."""
    return {
        "name": name,
        "description": description,
        "input_schema": model.model_json_schema(),
    }


TOOL_SCHEMAS: list[dict[str, Any]] = [
    _make_schema(
        "get_signal_window",
        (
            "Fetch recent samples + summary statistics (mean, std, trend slope) for one "
            "biomechanical signal from one player. Use when you need to ground a claim in the "
            "actual signal trajectory over the last N seconds."
        ),
        GetSignalWindowInput,
    ),
    _make_schema(
        "compare_to_baseline",
        (
            "Compare a player's current signal value to their opening-baseline value for the same "
            "signal; returns z-score and percent delta. Use when you suspect fatigue, form change, "
            "or ritual drift and want quantitative confirmation."
        ),
        CompareToBaselineInput,
    ),
    _make_schema(
        "get_rally_context",
        (
            "Return the last N player-state transitions (PRE_SERVE_RITUAL, ACTIVE_RALLY, DEAD_TIME). "
            "Use to reconstruct rally cadence, ace/fault patterns, and who served when."
        ),
        GetRallyContextInput,
    ),
    _make_schema(
        "get_match_phase",
        (
            "Return the current coarse match phase (WARMUP / SET_1 / SET_2 / SET_3 / TIEBREAK / "
            "CHANGEOVER / UNKNOWN). Use to contextualize commentary appropriately."
        ),
        GetMatchPhaseInput,
    ),
]

# A9: Analytics-Specialist-scoped extra tool schema (G19 — per-agent scoping
# preserves Technical/Tactical cache-warm state; only Analytics pays the
# one-time cache miss on tools-block mutation per G34).
VIDEO_CONTEXT_MCP_SCHEMA: dict[str, Any] = _make_schema(
    "query_video_context_mcp",
    (
        "Fetch hand-authored BROADCASTER NARRATIONS for a specific match-time window. "
        "Returns narration lines describing the visible broadcast action (player "
        "walking to baseline, toss initiation, etc.) with optional `biometric_hook` "
        "naming the signal each narration primes. Use this as the FIRST call in "
        "your analysis to ground quantitative signal findings in the qualitative "
        "broadcast narrative. The tool is backed by a local stub in this run; its "
        "response is a real tool result that enters the conversation as the next "
        "user turn."
    ),
    QueryVideoContextInput,
)

ANALYTICS_SCOPED_TOOLS: list[dict[str, Any]] = TOOL_SCHEMAS + [VIDEO_CONTEXT_MCP_SCHEMA]
"""Analytics Specialist sees all base tools PLUS the video context MCP (A9).
Technical + Tactical agents keep the cache-warm shared TOOL_SCHEMAS list."""

# Registry for dispatching tool_use blocks coming back from the Opus stream.
ToolExecutor = Callable[[ToolContext, dict[str, Any]], dict[str, Any]]

TOOL_EXECUTORS: dict[str, ToolExecutor] = {
    "get_signal_window": execute_get_signal_window,
    "compare_to_baseline": execute_compare_to_baseline,
    "get_rally_context": execute_get_rally_context,
    "get_match_phase": execute_get_match_phase,
    "query_video_context_mcp": execute_query_video_context_mcp,
}

STUBBED_MCP_TOOLS: frozenset[str] = frozenset({"query_video_context_mcp"})
"""Tools whose TraceToolCall/TraceToolResult should carry provenance='stubbed_mcp'
(G9). Consulted by scouting_committee._EventRecorder when stamping trace events."""


def dispatch_tool(ctx: ToolContext, tool_name: str, tool_input: dict[str, Any]) -> dict[str, Any]:
    """Run one tool invocation by name; never raise on bad input — return an {"error": ...} dict instead.

    This shape is what the Opus tool-use loop feeds back to the model in a tool_result block.
    Errors get back to Opus as structured content so it can recover, not as exceptions that crash the run.
    """
    executor = TOOL_EXECUTORS.get(tool_name)
    if executor is None:
        return {"error": "unknown_tool", "tool_name": tool_name}
    try:
        return executor(ctx, tool_input)
    except ValidationError as exc:
        return {"error": "invalid_input", "tool_name": tool_name, "details": exc.errors()}
    except Exception as exc:
        return {"error": "tool_exception", "tool_name": tool_name, "details": str(exc)}
