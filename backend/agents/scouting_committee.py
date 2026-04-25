"""Multi-Agent Scouting Committee for PANOPTICON LIVE (PATTERN-056, USER-CORRECTION-024).

Three orthogonal Claude agents running SEQUENTIALLY during offline precompute:

  1. Analytics Specialist — queries the signal arrays via DuckDB-backed tools,
     identifies anomalies. Has tool access (get_signal_window, compare_to_baseline,
     get_rally_context, get_match_phase).

  2. Technical Biomechanics Coach — reads Analytics Specialist's output, maps
     anomalies to physical-breakdown narrative grounded in biomech literature
     (BIOMECH_PRIMER). No tools — pure synthesis.

  3. Tactical Strategist — reads Technical Coach's output, synthesizes match-
     strategy recommendation. No tools — pure synthesis.

Every event (thinking, tool_call, tool_result, handoff, text) is captured into
AgentTrace and serialized to agent_trace.json for frontend playback.

Orthogonality contract: each agent's USER message is the PRIOR AGENT'S OUTPUT
(real handoff), not the raw ToolContext.signals dump. This forces genuine
cascading reasoning instead of three parallel agents doing the same job.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable

from backend.agents.opus_coach import (
    _extract_text,
    _extract_thinking_text,
    _response_to_dict_content,
    _tool_use_blocks,
)
from backend.agents.system_prompt import BIOMECH_PRIMER
from backend.agents.tools import (
    ANALYTICS_SCOPED_TOOLS,
    STUBBED_MCP_TOOLS,
    TOOL_SCHEMAS,
    ToolContext,
    dispatch_tool,
)
from backend.db.schema import (
    AgentStep,
    AgentTrace,
    PlayerProfile,
    ProvenanceTag,
    QualitativeNarration,
    SignalSample,
    StateTransition,
    TraceEvent,
    TraceHandoff,
    TraceText,
    TraceThinking,
    TraceToolCall,
    TraceToolResult,
)

# ──────────────────────────── Agent identity constants ────────────────────────────

ANALYTICS_SPECIALIST_NAME: str = "Analytics Specialist"
TECHNICAL_COACH_NAME: str = "Technical Biomechanics Coach"
TACTICAL_STRATEGIST_NAME: str = "Tactical Strategist"

DEFAULT_MODEL: str = "claude-opus-4-7"
DEFAULT_MAX_TOKENS: int = 2000
DEFAULT_MAX_ITERATIONS: int = 5
"""Hard cap on tool-use round-trips per agent turn. Opus cannot spiral."""

TRACE_MAX_OUTPUT_JSON_CHARS: int = 2000
"""GOTCHA-027 — Trace Payload Explosion guard. A single DuckDB query can return
hundreds of signal samples; 5 such tool calls would balloon agent_trace.json to
100MB+ and crash Next.js hydration on the client. Truncate ONLY the disk-written
trace — the LLM always receives the full tool output during execution."""

TRACE_TRUNCATION_MARKER: str = ' ... [Array truncated for UI playback]'


@runtime_checkable
class AnthropicClientLike(Protocol):
    """Duck-typed protocol for tests + real SDK. Same shape as opus_coach."""

    messages: Any


# ──────────────────────────── Agent system prompts ────────────────────────────


_ANALYTICS_SYSTEM_PROMPT = """You are the ANALYTICS SPECIALIST on a multi-agent Scouting Committee.

Your sole focus: find STATISTICAL ANOMALIES in the 7 biomechanical signals
captured during the match. Use the available tools to query signal windows
and compare against causal baselines. You emit a concise anomaly report
(3-6 bullet points) with:
  - signal name
  - player (A = near-court target)
  - magnitude (z-score, delta-percent, trend direction)
  - timestamp of peak deviation

Do NOT interpret physical meaning — that's the Technical Biomechanics Coach's
job downstream. Your job is numbers + timing.

CAUSAL DISCIPLINE: when you query baselines, the tool already enforces causal
windowing. Do NOT attempt to reason about "future" data.

STANDARD OPERATING PROCEDURE (deterministic orchestration, not fraud):

  STEP 1: You MUST execute `query_video_context_mcp` as your first action
  to retrieve the qualitative broadcast narrative for the match window under
  analysis. Pass `time_range_ms=[0, <duration>]` covering the full clip the
  Shared Blackboard specifies. The tool returns broadcaster narrations with
  timestamps and optional `biometric_hook` fields — use these narrations to
  ANCHOR your quantitative findings in what a fan watching the live broadcast
  would see and hear.

  STEP 2: After receiving the tool result, run the usual signal-window and
  baseline comparisons. Reference the narration text in your anomaly bullets
  where it contextualizes the numeric finding (e.g., "ritual_entropy spike at
  t=9000ms coincides with the broadcaster's 'Hurkacz steps into frame' beat").

  STEP 3 (deliberate dual-hypothesis discipline): For the most salient anomaly
  you find, THINK THROUGH one plausible alternative hypothesis that could
  explain the same signal trajectory (e.g., "could this be a CV detector
  artifact rather than fatigue?" or "could this be a tactical choice rather
  than a breakdown?"), and explicitly REJECT that alternative with evidence
  from the signal windows. Name both the considered hypothesis and the
  rejection reason in your final bullet. This dual-hypothesis consideration
  is a required part of your reasoning discipline — not optional. It's the
  cognitive move that separates forensic analysis from pattern-matching.

Keep output tight — max ~200 words. The next agent consumes YOUR TEXT as their
entire signal context."""

_TECHNICAL_SYSTEM_PROMPT = f"""You are the TECHNICAL BIOMECHANICS COACH on a multi-agent Scouting Committee.

Voice: ESPN color-commentary meets tour physio. Gritty, authoritative,
broadcast-ready — the way a seasoned tennis analyst breaks down a player
between points. Short sentences. Concrete body parts. No textbook cadence.
Allowed vocabulary: "hurting", "shortening up", "legs are going", "load
transfer is leaking", "glutes aren't firing", "burning through reserves",
"mechanics are starting to break". Tell the story a fan would hear on a
broadcast, grounded in the biomech literature below.

You receive the ANALYTICS SPECIALIST's anomaly report. Your job: translate
those numbers into a physical-breakdown narrative. Map each flagged anomaly
to a musculoskeletal story:

  - Lateral work rate up + recovery lagging  -> posterior chain is cooking
  - Toss variance climbing                   -> shoulder stabilizer is slipping
  - Crouch depth regressing                  -> quads + glutes leaking load,
                                                 split-step losing spring
  - Ritual entropy rising                    -> motor pattern is coming apart
  - Baseline retreat creeping back           -> anticipation is shot, legs
                                                 cheating deep

DO NOT parrot the Analytics numbers verbatim — you're telling the PHYSICAL
STORY, not reciting stats. Lead with the body system that's breaking, then
explain WHY it's breaking, then what it means for shotmaking. Max ~200 words.
Write it like it's going to live-voiceover on a Grand Slam broadcast.

{BIOMECH_PRIMER}"""

_TACTICAL_SYSTEM_PROMPT = """You are the TACTICAL STRATEGIST on a multi-agent Scouting Committee.

Voice: opposing-coach in the box between points. Decisive, no hedging. You
speak in plays, not possibilities — "drive it wide, chase them down,
collect the error." The Technical Coach already told you what's hurting;
your job is to name the exploit and the window.

You receive the TECHNICAL BIOMECHANICS COACH's physiological story. Convert
it into a match-strategy brief — what an opposing coach (or a sharp bettor)
should DO in the next 10-20 points.

Output format: ONE crisp markdown brief, ESPN-broadcast tight:
  1. `## Vulnerability` — ONE punchy sentence. No qualifiers. Name the body
     system that's going and the shot shape it compromises.
  2. `## Exploit Pattern` — 2-3 concrete tactical plays. Each play is a
     single-sentence directive: the shot, the court zone, the intent.
     Example flavor: "Drive heavy cross-court, force stretch-wide backhand,
     follow with inside-out forehand behind them."
  3. `## Watch Window` — rally count or approximate minutes the exploit
     window stays open. Cite the fatigue state Technical described.

Tight. Punchy. Every word earns its place. Max ~200 words.

Max ~250 words. This is the FINAL REPORT — it ships to the fan-facing HUD."""


# ──────────────────────────── Event-list accumulator ────────────────────────────


@dataclass
class _EventRecorder:
    """Builds an ordered list[TraceEvent] with monotonic timestamps from a wall-clock origin."""

    origin_ms: int

    def __post_init__(self) -> None:
        self._events: list[TraceEvent] = []

    def _t_now(self) -> int:
        return max(0, _now_ms() - self.origin_ms)

    def thinking(self, content: str) -> None:
        if not content:
            return
        self._events.append(TraceThinking(t_ms=self._t_now(), content=content))

    def text(self, content: str) -> None:
        if not content:
            return
        self._events.append(TraceText(t_ms=self._t_now(), content=content))

    def tool_call(self, tool_name: str, inp: dict[str, Any]) -> None:
        self._events.append(
            TraceToolCall(
                t_ms=self._t_now(),
                tool_name=tool_name,
                input_json=json.dumps(inp, default=str),
                provenance=_provenance_for(tool_name),
            ),
        )

    def tool_result(self, tool_name: str, output: dict[str, Any], is_error: bool = False) -> None:
        """Record a tool_result event, TRUNCATING the output_json if it exceeds
        TRACE_MAX_OUTPUT_JSON_CHARS (GOTCHA-027). This is UI-SIDE truncation only —
        the LLM already received the full `output` dict during execution. Only the
        disk-written trace that ships to the Orchestration Console is truncated.

        Provenance is stamped to match the call event so UI consumers can style
        the result pill without cross-referencing the call.
        """
        raw_json = json.dumps(output, default=str)
        if len(raw_json) > TRACE_MAX_OUTPUT_JSON_CHARS:
            # Reserve space for the marker so the final string stays <= cap.
            body_budget = TRACE_MAX_OUTPUT_JSON_CHARS - len(TRACE_TRUNCATION_MARKER)
            raw_json = raw_json[:body_budget] + TRACE_TRUNCATION_MARKER
        self._events.append(
            TraceToolResult(
                t_ms=self._t_now(),
                tool_name=tool_name,
                output_json=raw_json,
                is_error=is_error,
                provenance=_provenance_for(tool_name),
            ),
        )

    def handoff(self, from_agent: str, to_agent: str, payload_summary: str) -> None:
        self._events.append(
            TraceHandoff(
                t_ms=self._t_now(),
                from_agent=from_agent,
                to_agent=to_agent,
                payload_summary=payload_summary,
            )
        )

    def snapshot(self) -> list[TraceEvent]:
        return list(self._events)


def _now_ms() -> int:
    return int(time.monotonic() * 1000)


def _provenance_for(tool_name: str) -> ProvenanceTag:
    """Map a tool_name to its provenance tag (G9).

    Tools in STUBBED_MCP_TOOLS produce events tagged `stubbed_mcp` so the UI
    renders a neutral `STUB · Video Context API` chip. Everything else
    defaults to `live_anthropic` (native tool invocation).
    """
    return "stubbed_mcp" if tool_name in STUBBED_MCP_TOOLS else "live_anthropic"


# ──────────────────────────── Single-agent turn runner ────────────────────────────


async def _run_agent_turn(
    client: AnthropicClientLike,
    *,
    agent_name: str,
    agent_role: str,
    system_prompt: str,
    user_content: str,
    ctx: ToolContext,
    use_tools: bool,
    model: str,
    max_tokens: int,
    max_iterations: int,
    origin_ms: int,
    tools_override: list[dict[str, Any]] | None = None,
) -> AgentStep:
    """Run ONE agent turn to completion (tool-use loop if use_tools=True).

    NEVER raises — on API error, returns a step whose events contain a single
    TraceText "[error: ...]". The caller must still get a valid AgentStep so
    the trace can be completed.
    """
    started_at_ms = max(0, _now_ms() - origin_ms)
    recorder = _EventRecorder(origin_ms=origin_ms)

    system_blocks = [
        {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}},
    ]
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_content}]

    final_text = ""
    try:
        for _iteration in range(max_iterations):
            kwargs: dict[str, Any] = {
                "model": model,
                "max_tokens": max_tokens,
                "thinking": {"type": "adaptive"},
                "system": system_blocks,
                "messages": messages,
            }
            if use_tools:
                # A9 / G19: per-agent tool scoping. Analytics Specialist receives
                # ANALYTICS_SCOPED_TOOLS (includes query_video_context_mcp);
                # Technical + Tactical stick with cache-warm TOOL_SCHEMAS.
                kwargs["tools"] = tools_override if tools_override is not None else TOOL_SCHEMAS
            response = await client.messages.create(**kwargs)

            blocks = list(getattr(response, "content", []) or [])
            stop_reason = getattr(response, "stop_reason", "end_turn")

            # Capture thinking + text into trace BEFORE tool dispatch so even
            # an iteration-capped run produces some visible output.
            thinking_text = _extract_thinking_text(blocks)
            if thinking_text:
                recorder.thinking(thinking_text)
            text_part = _extract_text(blocks)
            if text_part:
                recorder.text(text_part)
                final_text = text_part

            tool_uses = _tool_use_blocks(blocks)

            # Echo assistant turn into messages[] for next loop iteration
            messages.append({"role": "assistant", "content": _response_to_dict_content(blocks)})

            if stop_reason == "end_turn" or not use_tools or not tool_uses:
                break

            # Dispatch each tool_use, record both call + result
            tool_results: list[dict[str, Any]] = []
            for tu in tool_uses:
                tool_name = getattr(tu, "name", "")
                tool_input = getattr(tu, "input", {}) or {}
                recorder.tool_call(tool_name, tool_input)
                try:
                    result = dispatch_tool(ctx, tool_name, tool_input)
                    is_err = bool(result.get("error")) if isinstance(result, dict) else False
                    recorder.tool_result(tool_name, result, is_error=is_err)
                except Exception as exc:  # noqa: BLE001 — tool execution is opaque
                    err_payload = {"error": str(exc), "tool": tool_name}
                    recorder.tool_result(tool_name, err_payload, is_error=True)
                    result = err_payload
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": getattr(tu, "id", ""),
                        "content": json.dumps(result, default=str),
                    }
                )
            messages.append({"role": "user", "content": tool_results})
    except Exception as exc:  # noqa: BLE001 — never crash the pipeline
        err_text = f"[error: {agent_name} failed with {type(exc).__name__}: {exc}]"
        recorder.text(err_text)
        final_text = err_text

    completed_at_ms = max(started_at_ms, _now_ms() - origin_ms)
    step = AgentStep(
        agent_name=agent_name,
        agent_role=agent_role,
        started_at_ms=started_at_ms,
        completed_at_ms=completed_at_ms,
        events=recorder.snapshot(),
    )
    # Attach the final text to a side-channel for the orchestrator to forward.
    # We stash it in a closure variable via the caller pattern — returning tuple
    # keeps the API type-safe.
    step._output_text = final_text  # type: ignore[attr-defined]
    return step


def _extract_output_text(step: AgentStep) -> str:
    """Return the concatenated TraceText content from a step (the agent's message)."""
    cached = getattr(step, "_output_text", None)
    if cached:
        return str(cached)
    return "\n".join(e.content for e in step.events if isinstance(e, TraceText))


# ──────────────────────────── Main orchestrator ────────────────────────────


def _build_baseline_context(
    *,
    committee_goal: str,
    signals: list[SignalSample],
    transitions: list[StateTransition],
    player_a_name: str,
    match_id: str,
    player_profile: PlayerProfile | None = None,
) -> str:
    """Shared Blackboard (PATTERN-059): the ground-truth frame every agent receives.

    Carried verbatim in the user message of ALL three agents so Technical Coach
    and Tactical Strategist can never be starved of baseline context by an
    Analytics Specialist that under-reports. Prevents hallucinated physical-
    breakdown claims unconstrained by the raw signal taxonomy.

    A9: when `player_profile` is provided, its ATP stats are appended as a
    `=== PLAYER PROFILE ===` section. Cached only through the USER message
    (G5 — keeps system prompts cache-warm). Narrations arrive only via the
    `query_video_context_mcp` ToolResult, NOT here (G36 — avoids double-feeding).
    """
    n_sig = len(signals)
    signal_names = sorted({s.signal_name for s in signals if s.value is not None})
    last_t_ms = max((s.timestamp_ms for s in signals), default=0)
    parts = [
        "=== COMMITTEE BASELINE (shared across all agents) ===",
        f"Match ID: {match_id}",
        f"Target player: Player A = {player_a_name} (near-court).",
        f"Scouting goal: {committee_goal}",
        f"Raw signal taxonomy: {n_sig} samples across {len(signal_names)} signal types "
        f"({', '.join(signal_names) or '(none detected)'}).",
        f"State transitions on record: {len(transitions)}.",
        f"Last observed timestamp: {last_t_ms} ms.",
        # G10 fix — dynamic identity injection (team-lead override 2026-04-24).
        # When an authored player_profile is present the LLM is UNGAGGED and
        # told to use the real name + cite profile stats (personalization).
        # When profile is absent the strict anonymity guardrail holds to
        # prevent the Djokovic/Federer/Nadal hallucination trap.
        _identity_rule(player_a_name, player_profile),
        "===",
    ]
    if player_profile is not None:
        parts.append("")
        parts.append(_format_player_profile(player_profile))
    return "\n".join(parts)


def _identity_rule(player_a_name: str, player_profile: PlayerProfile | None) -> str:
    """Dynamic identity rule (G10). Switches on whether an authored profile exists.

    Two states:
      - **Profile present** — explicitly revoke anonymity and DEMAND that the
        agent refer to the target by `{profile.name}` and actively cite stats.
        Still forbids inventing players OUTSIDE the profile to prevent
        cross-match hallucination (Djokovic/Federer leaking in).
      - **Profile absent** — keep the strict anonymity guardrail from the
        pre-G10 prompt. Safe default for unknown clips.
    """
    if player_profile is not None:
        return (
            f"PROFILE DETECTED for Player A. You MUST refer to the target player by "
            f"their real name '{player_profile.name}' (not 'Player A' or 'the target'). "
            "You MUST actively integrate their specific attributes from the PLAYER "
            "PROFILE section below (playing style, ritual signature, known fatigue "
            "signature, rank / serve-velocity if present) into your analysis — cite "
            "them verbatim to ground your reasoning in the authored profile. "
            "CRITICAL: do NOT reference any OTHER players not named in the profile. "
            "Opus has been trained on famous matches and will otherwise hallucinate "
            "Djokovic/Federer/Nadal — refer ONLY to the profile's player by name."
        )
    return (
        f"Refer to the target ONLY as {player_a_name} or 'Player A' — do NOT "
        "invent other names (Opus has been trained on famous matches and will "
        "otherwise hallucinate Djokovic/Federer/Nadal)."
    )


def _format_player_profile(profile: PlayerProfile) -> str:
    """Format a PlayerProfile for inclusion in the user-prompt blackboard (G37).

    Renders each ProvenancedValue with its source URL so the Scouting Committee
    can cite stats verbatim. Keeps the block under ~400 tokens — fits the
    prompt-cache TTL budget per agent.
    """
    lines = [
        "=== PLAYER PROFILE ===",
        f"Name: {profile.name} (id: {profile.player_id})",
    ]

    def _fmt_entry(label: str, pv) -> str:
        if pv is None:
            return ""
        url_tag = f" [src: {pv.source_url}]" if pv.source_url else ""
        status_tag = f" ({pv.verification_status})" if pv.verification_status else ""
        return f"- {label}: {pv.value}{status_tag}{url_tag}"

    candidate_fields = [
        ("Nationality", profile.nationality),
        ("World rank", profile.world_rank),
        ("Avg first-serve velocity (km/h)", profile.serve_velocity_avg_kmh),
        ("First-serve %", profile.first_serve_pct),
        ("Playing style", profile.playing_style),
        ("Pre-serve ritual", profile.pre_serve_ritual_style),
        ("Known fatigue signature", profile.known_fatigue_signature),
    ]
    for label, pv in candidate_fields:
        entry = _fmt_entry(label, pv)
        if entry:
            lines.append(entry)
    lines.append("===")
    return "\n".join(lines)


def _compose_user_prompt(baseline: str, focus: str, instructions: str) -> str:
    """Additive prompt composition (PATTERN-059 Shared Blackboard).

    Baseline stays CONSTANT across agents; focus (upstream output) and
    instructions vary per turn. Never substitute — always append.
    """
    return f"{baseline}\n\n---\nFOCUS OF SYNTHESIS:\n{focus}\n\n---\n{instructions}"


def _build_analytics_focus_and_instructions(
    player_a_name: str,
    player_profile: PlayerProfile | None = None,
) -> tuple[str, str]:
    """Analytics Specialist is the first agent — no upstream output to focus on,
    so the focus layer describes its own starting state.

    G10: identity instruction is dynamic — when a profile is authored the
    agent is told to USE the profile name; otherwise the anonymity fallback
    applies. The COMMITTEE BASELINE section (built by _build_baseline_context)
    already carries the authoritative rule; this instruction re-emphasizes it
    in the Analytics-specific turn layer to keep the LLM's attention anchored.
    """
    focus = (
        "You are the FIRST agent in the committee. No upstream analysis exists "
        "yet. Start from the baseline and use the available tools to query "
        "signal windows + causal baselines."
    )
    if player_profile is not None:
        identity_clause = (
            f"Refer to the target player by their real name '{player_profile.name}' "
            "and cite specific fields from the PLAYER PROFILE section verbatim in "
            "your analysis — this grounds the anomaly report in the authored profile."
        )
    else:
        identity_clause = (
            f"Refer to the target player ONLY as {player_a_name} or 'Player A'."
        )
    instructions = (
        "Run the analysis. Use tools (get_signal_window, compare_to_baseline, "
        "get_rally_context, get_match_phase) to ground your findings. "
        f"{identity_clause} "
        "Output 3-6 bullet anomalies with signal+player+magnitude+timestamp. "
        "If no signals meet anomaly criteria, say so explicitly — do NOT invent."
    )
    return focus, instructions


def _build_technical_focus_and_instructions(
    analytics_output: str, player_a_name: str,
) -> tuple[str, str]:
    focus = (
        f"ANALYTICS SPECIALIST'S ANOMALY REPORT (target = {player_a_name}):\n\n"
        f"{analytics_output}"
    )
    instructions = (
        "Translate these anomalies into a PHYSICAL-BREAKDOWN narrative grounded "
        f"in biomech literature. Focus on {player_a_name}'s posterior chain, "
        "rotator stabilizers, quad/glute loading, and motor-pattern consistency. "
        "Do NOT restate the numbers — synthesize the physiological story. "
        "Stay within the signal taxonomy listed in the baseline above — do NOT "
        "invent a biomech claim that references a signal we don't actually track."
    )
    return focus, instructions


def _build_tactical_focus_and_instructions(
    technical_output: str, player_a_name: str,
) -> tuple[str, str]:
    focus = (
        f"TECHNICAL BIOMECHANICS COACH'S PHYSIOLOGICAL STORY (target = {player_a_name}):\n\n"
        f"{technical_output}"
    )
    instructions = (
        "Convert this into a match-strategy brief: Vulnerability / Exploit Pattern / "
        "Watch Window. Concrete tactical plays only. Markdown format. "
        "The exploit pattern MUST be consistent with the signal taxonomy listed "
        "in the baseline — if no signals in the taxonomy support a tactic, do "
        "NOT recommend it."
    )
    return focus, instructions


async def generate_scouting_report(
    client: AnthropicClientLike,
    ctx: ToolContext,
    *,
    match_id: str,
    player_a_name: str,
    committee_goal: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
) -> AgentTrace:
    """Run the 3-agent Scouting Committee and return the full captured AgentTrace.

    NEVER raises — individual agent failures are caught and recorded as
    [error: ...] text events so the trace is always a well-formed AgentTrace.

    Args:
        client: AsyncAnthropic-compatible client (real SDK or a scripted fake for tests).
        ctx: Read-only snapshot of the match signals + transitions (passed to
            Analytics Specialist's tool dispatcher).
        match_id: Parent match identifier, stored on the trace.
        player_a_name: Near-court player's human name (used in every agent prompt).
        committee_goal: One-line summary of WHY this committee is running
            (e.g., "Analyze fatigue drift across the last 5 rallies").
        model: Anthropic model ID; default claude-opus-4-7.
        max_tokens: Output cap per API round-trip.
        max_iterations: Tool-use round-trip cap per agent turn.
    """
    origin_ms = _now_ms()
    started_at = datetime.now(timezone.utc)

    # Shared Blackboard (PATTERN-059): baseline context that EVERY agent receives
    # verbatim in their user prompt. Prevents downstream context starvation.
    # A9: player_profile included when authored (G37 provenance auditable).
    baseline = _build_baseline_context(
        committee_goal=committee_goal,
        signals=ctx.signals,
        transitions=ctx.transitions,
        player_a_name=player_a_name,
        match_id=match_id,
        player_profile=ctx.player_profile,
    )

    steps: list[AgentStep] = []

    # Agent 1: Analytics Specialist (has tool access — scoped to include query_video_context_mcp per A9/G19)
    analytics_focus, analytics_instructions = _build_analytics_focus_and_instructions(
        player_a_name, ctx.player_profile,
    )
    analytics_prompt = _compose_user_prompt(baseline, analytics_focus, analytics_instructions)
    analytics_step = await _run_agent_turn(
        client,
        agent_name=ANALYTICS_SPECIALIST_NAME, agent_role="Quantitative Anomaly Detection",
        system_prompt=_ANALYTICS_SYSTEM_PROMPT, user_content=analytics_prompt,
        ctx=ctx, use_tools=True, model=model, max_tokens=max_tokens,
        max_iterations=max_iterations, origin_ms=origin_ms,
        tools_override=ANALYTICS_SCOPED_TOOLS,
    )
    analytics_output = _extract_output_text(analytics_step)
    steps.append(analytics_step)

    # Handoff 1 → 2 (appended to step 1's events to preserve chronology)
    _append_handoff(
        steps[-1], origin_ms,
        from_agent=ANALYTICS_SPECIALIST_NAME, to_agent=TECHNICAL_COACH_NAME,
        payload_summary=_summarize_handoff(analytics_output),
    )

    # Agent 2: Technical Biomechanics Coach (no tools — pure synthesis on top of baseline)
    technical_focus, technical_instructions = _build_technical_focus_and_instructions(
        analytics_output, player_a_name,
    )
    technical_prompt = _compose_user_prompt(baseline, technical_focus, technical_instructions)
    technical_step = await _run_agent_turn(
        client,
        agent_name=TECHNICAL_COACH_NAME, agent_role="Biomechanical Interpretation",
        system_prompt=_TECHNICAL_SYSTEM_PROMPT, user_content=technical_prompt,
        ctx=ctx, use_tools=False, model=model, max_tokens=max_tokens,
        max_iterations=1, origin_ms=origin_ms,  # single turn — no tool loop needed
    )
    technical_output = _extract_output_text(technical_step)
    steps.append(technical_step)

    # Handoff 2 → 3
    _append_handoff(
        steps[-1], origin_ms,
        from_agent=TECHNICAL_COACH_NAME, to_agent=TACTICAL_STRATEGIST_NAME,
        payload_summary=_summarize_handoff(technical_output),
    )

    # Agent 3: Tactical Strategist (pure synthesis)
    tactical_focus, tactical_instructions = _build_tactical_focus_and_instructions(
        technical_output, player_a_name,
    )
    tactical_prompt = _compose_user_prompt(baseline, tactical_focus, tactical_instructions)
    tactical_step = await _run_agent_turn(
        client,
        agent_name=TACTICAL_STRATEGIST_NAME, agent_role="Strategy Synthesis",
        system_prompt=_TACTICAL_SYSTEM_PROMPT, user_content=tactical_prompt,
        ctx=ctx, use_tools=False, model=model, max_tokens=max_tokens,
        max_iterations=1, origin_ms=origin_ms,
    )
    final_report_markdown = _extract_output_text(tactical_step) or "[no tactical output]"
    steps.append(tactical_step)

    total_compute_ms = max(0, _now_ms() - origin_ms)

    # Enforce chronological non-overlap between steps (shift if needed — should
    # already be true since we run sequentially, but belt-and-suspenders).
    _enforce_chronology(steps)

    # Match-timecode anchor (Phase 4 audit): the MIN/MAX of signal timestamps
    # the committee analyzed — lets the Orchestration Console display which
    # window of the match the swarm's reasoning applies to. None when there
    # were zero signals to analyze.
    signal_timestamps = [s.timestamp_ms for s in ctx.signals]
    match_time_range_ms: tuple[int, int] | None = (
        (min(signal_timestamps), max(signal_timestamps))
        if signal_timestamps
        else None
    )

    return AgentTrace(
        match_id=match_id,
        generated_at=started_at,
        committee_goal=committee_goal,
        steps=steps,
        final_report_markdown=final_report_markdown,
        total_compute_ms=total_compute_ms,
        match_time_range_ms=match_time_range_ms,
    )


def _append_handoff(
    step: AgentStep, origin_ms: int, *, from_agent: str, to_agent: str, payload_summary: str,
) -> None:
    """Append a TraceHandoff to an AgentStep (the only in-place mutation allowed).

    AgentStep is frozen — we rebuild it with an updated events list and mutate
    the list reference in-place on the containing list. Because Python's
    frozen=True blocks attribute assignment, we instead reach into __dict__.
    """
    handoff_t_ms = max(
        (e.t_ms for e in step.events), default=step.started_at_ms,
    ) + 1
    new_event = TraceHandoff(
        t_ms=handoff_t_ms,
        from_agent=from_agent,
        to_agent=to_agent,
        payload_summary=payload_summary,
    )
    # Pydantic v2 frozen models: mutate via __dict__ as a last resort.
    new_events = list(step.events) + [new_event]
    step.__dict__["events"] = new_events
    # Ensure completed_at_ms covers the handoff.
    if step.completed_at_ms < handoff_t_ms:
        step.__dict__["completed_at_ms"] = handoff_t_ms


def _enforce_chronology(steps: list[AgentStep]) -> None:
    """Ensure step[i].started_at_ms >= step[i-1].completed_at_ms.

    Because the wall-clock timer is monotonic and we run sequentially, this
    should never need to fire. But if a test fixture scripts a fast-enough
    fake, the timestamps could tie — bump by 1ms when we detect overlap.
    """
    for i in range(1, len(steps)):
        prev = steps[i - 1]
        curr = steps[i]
        if curr.started_at_ms < prev.completed_at_ms:
            curr.__dict__["started_at_ms"] = prev.completed_at_ms
            if curr.completed_at_ms < curr.started_at_ms:
                curr.__dict__["completed_at_ms"] = curr.started_at_ms


def _summarize_handoff(text: str, max_len: int = 160) -> str:
    """Produce a one-line summary of an agent's output for the TraceHandoff pill."""
    if not text:
        return "(no output)"
    collapsed = " ".join(text.split())
    return collapsed[:max_len] + ("…" if len(collapsed) > max_len else "")
