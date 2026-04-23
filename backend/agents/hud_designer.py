"""Opus 4.7 HUD Designer — generative UI layout spec generator (OFFLINE).

Exercises Opus's "design upgrade" capability directly. Given the current match state,
the active anomaly, and a summary of the dominant narrative signal, Opus emits a
JSON `HUDLayoutSpec` — which widgets appear, where, with what props.

Contrast with `opus_coach.py`:
  - Coach uses the tool-use loop (grounds claims in data)
  - Designer is pure JSON generation (context pushed into the user prompt)
  - Lower thinking budget — the task is more constrained
  - No caching contention with Coach's primer: Designer has its OWN system prompt

Failure modes are handled defensively:
  - JSON parse error → return a minimal default layout with the error in `reason`
  - Pydantic validation error (e.g., hallucinated widget name) → same fallback
  - API exception → same fallback

The caller decides WHEN to invoke the Designer (typically on a match-state transition,
not per-frame). See `docs/ORCHESTRATION_PLAYBOOK.md` Phase 2.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

from backend.agents.opus_coach import AnthropicClientLike
from backend.db.schema import HUDLayoutSpec, HUDWidgetSpec

DEFAULT_MODEL: str = "claude-opus-4-7"
DEFAULT_MAX_TOKENS: int = 1200
# Opus 4.7 uses adaptive thinking — the model decides reasoning depth.
# The old `thinking={"type": "enabled", "budget_tokens": N}` API is rejected with
# a 400 error. See USER-CORRECTION-027 (2026-04-22 smoke-test discovery).

DEFAULT_VALID_UNTIL_MS_OFFSET: int = 30_000
"""If the caller doesn't specify a valid_until_ms, default to +30s from the emit timestamp."""


HUD_DESIGNER_PROMPT: str = """\
You are the HUD Designer for a pro tennis biomechanical-intelligence overlay.

Your job: given the current match state, the active anomaly, and the dominant narrative
signal, output a compact JSON layout spec for the HUD. The frontend has a FIXED set of
widget primitives — you arrange them dynamically. You do NOT write React code or CSS.

## SINGLE-PLAYER FOCUS (IMPORTANT)

Panopticon Live is a single-player deep-dive system. The target is Player A (near court).
Player B data is usually unavailable on the current clip because the far-court player falls
below the CV detector's effective resolution. Design layouts that make Player A look
WORLD-CLASS; do NOT emit widgets that require Player B data (MomentumMeter, PredictiveOverlay).

## Rules of taste

1. **Minimalism wins** — prefer 3-5 widgets, not 9. The frontend looks broken with too many.
2. **Foreground Player A's narrative** — widgets should serve the moment (serve ritual,
   fatigue, retreat pattern), not a generic dashboard.
3. **State-appropriate** — `TossTracer` only during PRE_SERVE_RITUAL; `FootworkHeatmap`
   only during ACTIVE_RALLY.
4. **Always include `PlayerNameplate` for Player A** at `top-left`. Do NOT emit
   `PlayerNameplate` at `top-right` (no Player B).
5. **DO NOT EMIT** `MomentumMeter` or `PredictiveOverlay` — both require opponent data
   we don't have.

## Available widgets (use EXACT names)

  PlayerNameplate       — player info card (only for Player A; slot must be top-left)
  SignalBar             — one biomechanical signal visualization; up to 4 on screen at once
  TossTracer            — serve toss trajectory trace (PRE_SERVE_RITUAL only, Player A)
  FootworkHeatmap       — court footwork density (ACTIVE_RALLY only, Player A)

## Available slots (use EXACT names)

  top-left, top-center, right-1, right-2, right-3, right-4, center-overlay, bottom

`SignalBar` widgets go in `right-1` ... `right-4` (use the slot index to order by importance).
`PlayerNameplate` goes in `top-left` (Player A only).
`TossTracer` / `FootworkHeatmap` go in `center-overlay`.

## Required output

Respond with ONLY a JSON object (no prose, no markdown fences). The schema is:

{
  "reason": "<one-sentence natural-language explanation of WHY this layout fits the moment>",
  "widgets": [
    {"widget": "<WidgetKind>", "slot": "<WidgetSlot>", "props": { ... widget-specific props ... }}
  ]
}

Do NOT include `layout_id`, `timestamp_ms`, or `valid_until_ms` — the caller will attach them.

## Props conventions (free-form but predictable)

  PlayerNameplate:  {"player": "A", "highlight": bool}
  SignalBar:        {"player": "A", "signal": "<SignalName>", "z_score": <float>, "label": "<string>"}
  TossTracer:       {"player": "A"}
  FootworkHeatmap:  {"player": "A", "intensity": <float 0..1>}
"""


def _default_fallback_layout(
    *,
    layout_id: str,
    t_ms: int,
    valid_until_ms: int,
    reason: str,
) -> HUDLayoutSpec:
    """Minimal single-player layout used when Opus output can't be parsed/validated
    or the API fails.

    Nameplate + an empty SignalBar slot is the neutral Player A baseline.
    """
    return HUDLayoutSpec(
        layout_id=layout_id,
        timestamp_ms=t_ms,
        reason=reason,
        widgets=[
            HUDWidgetSpec(widget="PlayerNameplate", slot="top-left", props={"player": "A"}),
            HUDWidgetSpec(widget="SignalBar", slot="right-1",
                          props={"player": "A", "signal": "recovery_latency_ms"}),
        ],
        valid_until_ms=valid_until_ms,
    )


_MARKDOWN_FENCE_RE = re.compile(r"```(?:json)?\s*|```", re.IGNORECASE)


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Find the first JSON object in text and parse it. None on no-match or parse error.

    Robust to:
      - Markdown fences (```json ... ```)
      - Preamble prose before the JSON
      - Trailing commentary AFTER the JSON (even prose that contains stray `{` or `}`)

    Reviewer HIGH-1 (v2): greedy regex `\\{.*\\}` extends to the LAST `}` in the text,
    which corrupts the match when tail prose contains any brace. Use
    `json.JSONDecoder.raw_decode` instead — it parses ONE complete object starting at
    a position and stops there, so trailing prose is ignored entirely.
    """
    cleaned = _MARKDOWN_FENCE_RE.sub("", text)
    first_brace = cleaned.find("{")
    if first_brace < 0:
        return None
    decoder = json.JSONDecoder()
    try:
        parsed, _ = decoder.raw_decode(cleaned[first_brace:])
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


async def generate_hud_layout(
    client: AnthropicClientLike,
    *,
    t_ms: int,
    player_a_name: str = "Player A",
    player_b_name: str = "Player B",
    layout_id: str | None = None,
    trigger_description: str,
    state_summary: str,
    valid_until_ms: int | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> HUDLayoutSpec:
    """Run Opus 4.7 Designer; return a validated HUDLayoutSpec.

    On ANY failure (API, JSON parse, Pydantic validation), returns the default
    fallback layout with a descriptive `reason`. Never raises into the caller.

    Args:
        client: AsyncAnthropic-compatible client (real or fake).
        t_ms: Emit timestamp stored on the spec.
        layout_id: Unique id; generated if None.
        trigger_description: What just changed (state transition / anomaly). Goes into user prompt.
        state_summary: Snapshot of current match state, active anomalies, and dominant signal.
            Caller formats this as a string; Designer reads it verbatim.
        valid_until_ms: Layout TTL. Defaults to `t_ms + DEFAULT_VALID_UNTIL_MS_OFFSET`.
    """
    layout_id = layout_id or f"hud_{t_ms}_{uuid.uuid4().hex[:6]}"
    if valid_until_ms is None:
        valid_until_ms = t_ms + DEFAULT_VALID_UNTIL_MS_OFFSET

    system_blocks = [
        {"type": "text", "text": HUD_DESIGNER_PROMPT, "cache_control": {"type": "ephemeral"}},
    ]
    user_prompt = (
        f"Current match time: {t_ms} ms.\n"
        f"Target: Player A = {player_a_name} (the near-court player).\n"
        f"Trigger: {trigger_description}\n\n"
        f"State snapshot:\n{state_summary}\n\n"
        f"Emit a single JSON object matching the schema. No preamble, no markdown fences. "
        f"All widgets target Player A only. Do NOT emit PlayerNameplate@top-right, "
        f"MomentumMeter, or PredictiveOverlay — we have no Player B data. "
        f"Widget props use 'A' as the player identifier; the frontend resolves the display "
        f"name from MatchMeta."
    )

    try:
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            # Opus 4.7: adaptive thinking (see module header)
            thinking={"type": "adaptive"},
            system=system_blocks,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:
        return _default_fallback_layout(
            layout_id=layout_id, t_ms=t_ms, valid_until_ms=valid_until_ms,
            reason=f"[designer_error: {type(exc).__name__}: {exc}]",
        )

    # Extract text blocks
    text_parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        if getattr(block, "type", None) == "text":
            text = getattr(block, "text", None)
            if isinstance(text, str):
                text_parts.append(text)
    raw_text = "\n".join(text_parts).strip()

    parsed = _extract_json_object(raw_text)
    if parsed is None:
        return _default_fallback_layout(
            layout_id=layout_id, t_ms=t_ms, valid_until_ms=valid_until_ms,
            reason=f"[designer_parse_error] raw: {raw_text[:200]!r}",
        )

    # Attach caller-controlled fields; Opus only supplies `reason` + `widgets`
    parsed_spec = {
        "layout_id": layout_id,
        "timestamp_ms": t_ms,
        "valid_until_ms": valid_until_ms,
        "reason": parsed.get("reason", "(no reason given)"),
        "widgets": parsed.get("widgets", []),
    }

    try:
        return HUDLayoutSpec.model_validate(parsed_spec)
    except Exception as exc:
        return _default_fallback_layout(
            layout_id=layout_id, t_ms=t_ms, valid_until_ms=valid_until_ms,
            reason=f"[designer_validation_error: {type(exc).__name__}: {exc}]",
        )
