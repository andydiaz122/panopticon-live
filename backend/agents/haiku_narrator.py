"""Haiku 4.5 Narrator — per-second color-commentary beats (OFFLINE).

The cheap model in our multi-model orchestration. Opus reasons (Coach +
Designer); Haiku narrates. Judges see explicit cost-aware routing:
expensive deep thinking where it matters, cheap fast generation for
broadcast-style color commentary.

Input per beat:
  - t_ms: match timestamp
  - signal_snapshot: a short (1-2 line) textual description of what's happening
    right now (e.g., "Player A in ACTIVE_RALLY; lateral_work_rate high").
    Caller builds this from recent signals; Narrator does NOT query tools.

Output: NarratorBeat

Failure modes: on any error, return a beat with text="[narrator_error: ...]".
Never raises into precompute.py — a single failed beat does not kill the run.
"""

from __future__ import annotations

import uuid

from backend.agents.opus_coach import AnthropicClientLike
from backend.db.schema import NarratorBeat

DEFAULT_MODEL: str = "claude-haiku-4-5-20251001"
DEFAULT_MAX_TOKENS: int = 80
"""One sentence. If Haiku wraps over, truncate at max_tokens — the UI has a line cap."""

MAX_SNAPSHOT_CHARS: int = 500
"""Hard cap on caller-supplied signal_snapshot length (reviewer MEDIUM-2).

Future callers may build snapshots from arbitrary data sources; capping here
prevents a runaway prompt that blows the cost budget on what should be a
cheap one-sentence beat. 500 chars is ~120 tokens — 10x what a good snapshot needs."""


NARRATOR_SYSTEM_PROMPT: str = """\
You are a tennis broadcast color commentator — the voice between points.

SINGLE-PLAYER FOCUS: Panopticon Live is a deep-dive on Player A (the near-court player).
Make Player A the protagonist of every beat. The opponent (Player B) is often undetected
on broadcast clips, so avoid fabricating their actions. You MAY mention Player B as
context ("the serve comes back hard"), but Player A is always the subject of your sentence.

BIOMETRICS → TACTICS MANDATE (CRITICAL — DECISION-009):
Panopticon's value is the biomechanical telemetry extracted from broadcast footage.
Every beat should hint at a physical tell the fan wouldn't otherwise see — weight shift,
rhythm break, fatigue signature, stance change. Connect what's HAPPENING tactically back
to what's SHOWING up in the biomechanics. The fan should feel: "I'm seeing inside the
athlete's body."

Rules:
  - One sentence per beat. No headers, no lists, no markdown.
  - Under 20 words. Broadcast register: active verbs, concrete nouns.
  - Describe what is HAPPENING plus the PHYSICAL TELL driving it. Good: "Player A's
    retreat stretches deeper — legs starting to go." Bad: "Player A retreats." (no physio).
  - Numbers only when punchy ("down two inches on his crouch depth"). Never fabricate.
  - Do not say "we're seeing..." or other TV filler. Start with the action.
  - Never repeat a previous beat verbatim; vary your openings.
"""


async def generate_narrator_beat(
    client: AnthropicClientLike,
    *,
    t_ms: int,
    match_id: str,
    signal_snapshot: str,
    player_a_name: str = "Player A",
    player_b_name: str = "Player B",
    beat_id: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> NarratorBeat:
    """Run Haiku 4.5 for a single one-sentence color-commentary beat.

    Args:
        client: AsyncAnthropic-compatible client.
        t_ms: Timestamp stored on the beat.
        match_id: Parent match id.
        signal_snapshot: Short textual description of what's happening now.
            Caller is responsible for keeping this under ~100 words.
        beat_id: Unique id; generated if None.
    """
    beat_id = beat_id or f"beat_{t_ms}_{uuid.uuid4().hex[:6]}"
    # Reviewer MEDIUM-2: guard snapshot length — future callers may build snapshots from
    # arbitrary sources, and an unbounded string would balloon Haiku input cost.
    if len(signal_snapshot) > MAX_SNAPSHOT_CHARS:
        signal_snapshot = signal_snapshot[:MAX_SNAPSHOT_CHARS] + "..."
    # Bind real player names into the user message to stop Haiku hallucinating
    # famous-player names ("Djokovic", "Federer") from its training data.
    user_prompt = (
        f"Match time: {t_ms} ms.\n"
        f"Target: Player A = {player_a_name}. Opponent (often unseen): Player B = {player_b_name}.\n"
        f"Moment: {signal_snapshot}\n\n"
        f"One short beat with {player_a_name} as the subject of the sentence. "
        f"Refer to the target ONLY by {player_a_name} or 'Player A'. "
        f"Do NOT invent other names, and do NOT fabricate actions for the opponent."
    )

    try:
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=NARRATOR_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:
        return NarratorBeat(
            beat_id=beat_id,
            timestamp_ms=t_ms,
            match_id=match_id,
            text=f"[narrator_error: {type(exc).__name__}: {exc}]",
            input_tokens=0,
            output_tokens=0,
        )

    # Extract text from content blocks
    text_parts: list[str] = []
    for block in getattr(response, "content", []) or []:
        if getattr(block, "type", None) == "text":
            text = getattr(block, "text", None)
            if isinstance(text, str):
                text_parts.append(text)
    final_text = " ".join(text_parts).strip() or "[narrator silent]"

    usage = getattr(response, "usage", None)
    input_tokens = int(getattr(usage, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage, "output_tokens", 0) or 0)

    return NarratorBeat(
        beat_id=beat_id,
        timestamp_ms=t_ms,
        match_id=match_id,
        text=final_text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
