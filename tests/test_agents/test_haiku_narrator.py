"""Tests for backend/agents/haiku_narrator.py — Haiku 4.5 per-second beats."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

from backend.agents.haiku_narrator import DEFAULT_MODEL, generate_narrator_beat
from backend.db.schema import NarratorBeat

# ──────────────────────────── Fake client ────────────────────────────


def _text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def _response(text: str, in_tokens: int = 150, out_tokens: int = 22) -> SimpleNamespace:
    return SimpleNamespace(
        content=[_text_block(text)],
        stop_reason="end_turn",
        usage=SimpleNamespace(input_tokens=in_tokens, output_tokens=out_tokens),
    )


class _ScriptedClient:
    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.call_log: list[dict[str, Any]] = []
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, **kwargs: Any) -> Any:
        self.call_log.append({**kwargs})
        if not self._responses:
            raise AssertionError("scripted client ran out of responses")
        return self._responses.pop(0)


class _ExplodingClient:
    def __init__(self, exc: Exception) -> None:
        self._exc = exc
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, **kwargs: Any) -> Any:
        raise self._exc


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


# ──────────────────────────── Tests ────────────────────────────


def test_narrator_returns_beat_with_text_and_tokens() -> None:
    client = _ScriptedClient([_response("Ace up the tee!", in_tokens=180, out_tokens=7)])
    beat = _run(generate_narrator_beat(
        client,
        t_ms=5000, match_id="utr_01", beat_id="b1",
        signal_snapshot="A serving; first serve in.",
    ))
    assert isinstance(beat, NarratorBeat)
    assert beat.beat_id == "b1"
    assert beat.timestamp_ms == 5000
    assert beat.match_id == "utr_01"
    assert beat.text == "Ace up the tee!"
    assert beat.input_tokens == 180
    assert beat.output_tokens == 7


def test_narrator_uses_haiku_model_by_default() -> None:
    client = _ScriptedClient([_response("ok")])
    _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01", signal_snapshot="x",
    ))
    assert client.call_log[0]["model"] == DEFAULT_MODEL
    assert "haiku" in client.call_log[0]["model"]


def test_narrator_does_not_pass_thinking_or_tools() -> None:
    client = _ScriptedClient([_response("ok")])
    _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01", signal_snapshot="x",
    ))
    call = client.call_log[0]
    # Haiku doesn't support extended thinking — caller must NOT pass the arg
    assert "thinking" not in call
    # Narrator has no tools
    assert "tools" not in call


def test_narrator_signal_snapshot_reaches_prompt() -> None:
    client = _ScriptedClient([_response("ok")])
    _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01",
        signal_snapshot="UNIQUE_NARRATOR_MARKER_99",
    ))
    user_msg = client.call_log[0]["messages"][0]["content"]
    assert "UNIQUE_NARRATOR_MARKER_99" in user_msg


def test_narrator_generates_default_beat_id_when_missing() -> None:
    client = _ScriptedClient([_response("ok")])
    beat = _run(generate_narrator_beat(
        client, t_ms=12_345, match_id="utr_01", signal_snapshot="x",
    ))
    assert beat.beat_id.startswith("beat_12345_")
    assert len(beat.beat_id) == len("beat_12345_") + 6


def test_narrator_api_exception_returns_error_beat_no_raise() -> None:
    client = _ExplodingClient(ConnectionError("DNS fail"))
    beat = _run(generate_narrator_beat(
        client, t_ms=3000, match_id="utr_01",
        beat_id="b_err", signal_snapshot="x",
    ))
    assert beat.text.startswith("[narrator_error:")
    assert "DNS fail" in beat.text
    assert beat.beat_id == "b_err"
    assert beat.input_tokens == 0
    assert beat.output_tokens == 0


def test_narrator_empty_response_returns_placeholder() -> None:
    """If Haiku returns no text blocks at all, we still return a valid NarratorBeat."""
    empty_response = SimpleNamespace(
        content=[],
        stop_reason="end_turn",
        usage=SimpleNamespace(input_tokens=10, output_tokens=0),
    )
    client = _ScriptedClient([empty_response])
    beat = _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01", signal_snapshot="x",
    ))
    assert beat.text == "[narrator silent]"
    # min_length=1 on NarratorBeat.text still satisfied by the placeholder


def test_narrator_multiple_text_blocks_are_joined() -> None:
    """Rare but possible — Haiku returns multiple text blocks; we concat them."""
    response = SimpleNamespace(
        content=[_text_block("Fast winner!"), _text_block("Down the line.")],
        stop_reason="end_turn",
        usage=SimpleNamespace(input_tokens=50, output_tokens=15),
    )
    client = _ScriptedClient([response])
    beat = _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01", signal_snapshot="x",
    ))
    assert beat.text == "Fast winner! Down the line."


def test_narrator_system_prompt_is_string_not_cached() -> None:
    """Haiku narrator system is a simple string (no cache_control — prompts are too small for cache TTL to pay off)."""
    client = _ScriptedClient([_response("ok")])
    _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01", signal_snapshot="x",
    ))
    system = client.call_log[0]["system"]
    assert isinstance(system, str)
    assert "broadcast" in system.lower()


def test_narrator_truncates_long_signal_snapshot() -> None:
    """Reviewer MEDIUM-2: caller-supplied snapshot must be capped at MAX_SNAPSHOT_CHARS."""
    from backend.agents.haiku_narrator import MAX_SNAPSHOT_CHARS
    long_snapshot = "A" * (MAX_SNAPSHOT_CHARS + 1000)
    client = _ScriptedClient([_response("ok")])
    _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01", signal_snapshot=long_snapshot,
    ))
    user_msg = client.call_log[0]["messages"][0]["content"]
    # Snapshot + "..." + prompt boilerplate, but snapshot portion itself is capped
    assert "A" * (MAX_SNAPSHOT_CHARS + 1) not in user_msg  # not the full original
    assert "..." in user_msg  # truncation marker present


def test_narrator_short_snapshot_not_truncated() -> None:
    from backend.agents.haiku_narrator import MAX_SNAPSHOT_CHARS
    short = "B" * (MAX_SNAPSHOT_CHARS - 10)
    client = _ScriptedClient([_response("ok")])
    _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01", signal_snapshot=short,
    ))
    user_msg = client.call_log[0]["messages"][0]["content"]
    # Whole short string is present, no ellipsis from our truncation
    assert short in user_msg


def test_narrator_binds_player_names_into_user_prompt() -> None:
    """Player names from run_agent_phase must reach Haiku's user message.
    Prevents the observed hallucination of famous-player names in narrator beats."""
    client = _ScriptedClient([_response("ok")])
    _run(generate_narrator_beat(
        client, t_ms=10_000, match_id="utr_01",
        signal_snapshot="A serving",
        player_a_name="Coco Gauff",
        player_b_name="Iga Swiatek",
    ))
    user_msg = client.call_log[0]["messages"][0]["content"]
    assert "Coco Gauff" in user_msg
    assert "Iga Swiatek" in user_msg
    assert "Do NOT invent other names" in user_msg


def test_narrator_usage_missing_tokens_defaults_zero() -> None:
    """If the API response has a usage object missing some fields, treat them as 0."""
    response = SimpleNamespace(
        content=[_text_block("Beat!")],
        stop_reason="end_turn",
        usage=SimpleNamespace(),  # no fields at all
    )
    client = _ScriptedClient([response])
    beat = _run(generate_narrator_beat(
        client, t_ms=0, match_id="utr_01", signal_snapshot="x",
    ))
    assert beat.input_tokens == 0
    assert beat.output_tokens == 0
    assert beat.text == "Beat!"
