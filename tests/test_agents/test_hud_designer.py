"""Tests for backend/agents/hud_designer.py — Opus 4.7 HUD Designer.

Reuses the same SimpleNamespace fake pattern as test_opus_coach.py.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

from backend.agents.hud_designer import (
    DEFAULT_VALID_UNTIL_MS_OFFSET,
    generate_hud_layout,
)
from backend.db.schema import HUDLayoutSpec

# ──────────────────────────── Fake client ────────────────────────────


def _text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def _response_with_text(text: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    return SimpleNamespace(
        content=[_text_block(text)],
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=100, output_tokens=80,
                              cache_read_input_tokens=0, cache_creation_input_tokens=0),
    )


class _ScriptedClient:
    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.call_log: list[dict[str, Any]] = []
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, **kwargs: Any) -> Any:
        self.call_log.append({**kwargs, "messages": list(kwargs.get("messages", []))})
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


def test_designer_parses_clean_json_output() -> None:
    opus_output = """{
      "reason": "Serve ritual starting — foreground the toss and the nameplate.",
      "widgets": [
        {"widget": "PlayerNameplate", "slot": "top-left", "props": {"player": "A", "highlight": true}},
        {"widget": "PlayerNameplate", "slot": "top-right", "props": {"player": "B"}},
        {"widget": "TossTracer", "slot": "center-overlay", "props": {"player": "A"}}
      ]
    }"""
    client = _ScriptedClient([_response_with_text(opus_output)])
    layout = _run(generate_hud_layout(
        client,
        t_ms=12_000,
        layout_id="hud_test_1",
        trigger_description="A entered PRE_SERVE_RITUAL",
        state_summary="Player A serving, Player B waiting.",
    ))
    assert isinstance(layout, HUDLayoutSpec)
    assert layout.layout_id == "hud_test_1"
    assert layout.timestamp_ms == 12_000
    assert layout.reason.startswith("Serve ritual")
    assert len(layout.widgets) == 3
    # Correct widget kinds
    kinds = {w.widget for w in layout.widgets}
    assert kinds == {"PlayerNameplate", "TossTracer"}


def test_designer_handles_json_wrapped_in_markdown_fences() -> None:
    opus_output = """```json
{
  "reason": "Fatigue signal dominant — show nameplates + signal bars.",
  "widgets": [
    {"widget": "PlayerNameplate", "slot": "top-left", "props": {"player": "A"}},
    {"widget": "SignalBar", "slot": "right-1", "props": {"player": "B", "signal": "recovery_latency_ms", "z_score": 2.3}}
  ]
}
```"""
    client = _ScriptedClient([_response_with_text(opus_output)])
    layout = _run(generate_hud_layout(
        client,
        t_ms=5000,
        trigger_description="anomaly",
        state_summary="state",
    ))
    assert len(layout.widgets) == 2
    assert layout.reason.startswith("Fatigue")


def test_designer_handles_json_with_leading_prose() -> None:
    """Opus sometimes violates 'no preamble' instruction — we must still extract the JSON."""
    opus_output = """Sure, here's the layout I recommend:

{
  "reason": "Neutral moment, clean layout.",
  "widgets": [
    {"widget": "PlayerNameplate", "slot": "top-left", "props": {"player": "A"}}
  ]
}"""
    client = _ScriptedClient([_response_with_text(opus_output)])
    layout = _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    assert layout.reason == "Neutral moment, clean layout."
    assert len(layout.widgets) == 1


def test_designer_no_json_returns_fallback() -> None:
    client = _ScriptedClient([_response_with_text("I can't help with that.")])
    layout = _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    assert layout.reason.startswith("[designer_parse_error]")
    # Single-player fallback: Player A nameplate + one signal bar = 2 widgets.
    assert len(layout.widgets) == 2
    # Must NOT include any top-right nameplate (would mean Player B).
    assert all(w.slot != "top-right" for w in layout.widgets)


def test_designer_malformed_json_returns_fallback() -> None:
    # Unclosed brace
    client = _ScriptedClient([_response_with_text('{"reason": "oops", "widgets": [')])
    layout = _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    assert layout.reason.startswith("[designer_parse_error]")


def test_designer_invalid_widget_name_returns_fallback() -> None:
    """Opus hallucinates a widget not in WidgetKind — Pydantic validates, we fallback cleanly."""
    opus_output = """{
      "reason": "Hallucinated widget.",
      "widgets": [
        {"widget": "MagicSparklePanel", "slot": "top-left", "props": {}}
      ]
    }"""
    client = _ScriptedClient([_response_with_text(opus_output)])
    layout = _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    assert layout.reason.startswith("[designer_validation_error")


def test_designer_invalid_slot_returns_fallback() -> None:
    opus_output = """{
      "reason": "Bad slot.",
      "widgets": [
        {"widget": "PlayerNameplate", "slot": "nonsense-slot", "props": {}}
      ]
    }"""
    client = _ScriptedClient([_response_with_text(opus_output)])
    layout = _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    assert layout.reason.startswith("[designer_validation_error")


def test_designer_api_exception_returns_fallback_no_raise() -> None:
    client = _ExplodingClient(RuntimeError("connection reset"))
    layout = _run(generate_hud_layout(
        client, t_ms=500, trigger_description="t", state_summary="s",
    ))
    assert layout.reason.startswith("[designer_error:")
    assert "connection reset" in layout.reason
    # Fallback is still a valid HUDLayoutSpec — single-player (2 widgets).
    assert layout.timestamp_ms == 500
    assert len(layout.widgets) == 2


def test_designer_default_layout_id_generated_when_missing() -> None:
    client = _ScriptedClient([_response_with_text(
        '{"reason": "ok", "widgets": [{"widget": "PlayerNameplate", "slot": "top-left", "props": {}}]}',
    )])
    layout = _run(generate_hud_layout(
        client, t_ms=7000, trigger_description="t", state_summary="s",
    ))
    # Default pattern: f"hud_{t_ms}_{6-hex}"
    assert layout.layout_id.startswith("hud_7000_")
    assert len(layout.layout_id) == len("hud_7000_") + 6


def test_designer_valid_until_default_offset() -> None:
    client = _ScriptedClient([_response_with_text(
        '{"reason": "ok", "widgets": [{"widget": "PlayerNameplate", "slot": "top-left", "props": {}}]}',
    )])
    layout = _run(generate_hud_layout(
        client, t_ms=1000, trigger_description="t", state_summary="s",
    ))
    assert layout.valid_until_ms == 1000 + DEFAULT_VALID_UNTIL_MS_OFFSET


def test_designer_valid_until_override_honored() -> None:
    client = _ScriptedClient([_response_with_text(
        '{"reason": "ok", "widgets": [{"widget": "PlayerNameplate", "slot": "top-left", "props": {}}]}',
    )])
    layout = _run(generate_hud_layout(
        client, t_ms=1000, valid_until_ms=1500,
        trigger_description="t", state_summary="s",
    ))
    assert layout.valid_until_ms == 1500


def test_designer_sends_system_prompt_with_cache_control_and_no_tools() -> None:
    client = _ScriptedClient([_response_with_text(
        '{"reason": "ok", "widgets": [{"widget": "PlayerNameplate", "slot": "top-left", "props": {}}]}',
    )])
    _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    call = client.call_log[0]
    # System prompt cached
    assert call["system"][0]["cache_control"] == {"type": "ephemeral"}
    # Designer does NOT pass tools (pure generation, no tool loop)
    assert "tools" not in call


def test_designer_state_summary_reaches_user_prompt() -> None:
    client = _ScriptedClient([_response_with_text(
        '{"reason": "ok", "widgets": [{"widget": "PlayerNameplate", "slot": "top-left", "props": {}}]}',
    )])
    _run(generate_hud_layout(
        client, t_ms=0,
        trigger_description="A entered PRE_SERVE_RITUAL",
        state_summary="UNIQUE_STATE_MARKER_12345",
    ))
    call = client.call_log[0]
    user_msg = call["messages"][0]["content"]
    assert "UNIQUE_STATE_MARKER_12345" in user_msg
    assert "A entered PRE_SERVE_RITUAL" in user_msg


def test_designer_strips_fence_with_trailing_prose_containing_brace() -> None:
    """Reviewer HIGH-1: fence + trailing prose with stray `}` must not extend greedy regex match.

    Without the fence-stripping fix, the greedy `\\{.*\\}` would extend to the LAST `}`
    in the text — including a stray one in Opus's trailing commentary — and json.loads
    would fail, silently falling through to the default layout.
    """
    opus_output = (
        "Here's my pick:\n"
        "```json\n"
        '{"reason": "ok", "widgets": [{"widget": "PlayerNameplate", "slot": "top-left", "props": {}}]}\n'
        "```\n"
        "(Emoji fallback with {curly} braces in the tail prose.)"
    )
    client = _ScriptedClient([_response_with_text(opus_output)])
    layout = _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    # Must be the Opus-emitted layout, NOT the fallback
    assert layout.reason == "ok"
    assert len(layout.widgets) == 1
    assert layout.widgets[0].widget == "PlayerNameplate"


def test_designer_binds_target_player_name_into_user_prompt() -> None:
    """Player A's name must reach Designer's user message. Per single-player focus
    (2026-04-22 GOTCHA-016), Player B's name is NOT injected — we don't design
    widgets for a player we can't detect."""
    client = _ScriptedClient([_response_with_text(
        '{"reason": "ok", "widgets": [{"widget": "PlayerNameplate", "slot": "top-left", "props": {"player": "A"}}]}',
    )])
    _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
        player_a_name="Rafael Nadal", player_b_name="Carlos Alcaraz",
    ))
    user_msg = client.call_log[0]["messages"][0]["content"]
    assert "Rafael Nadal" in user_msg
    # Player B's name must NOT appear — Designer only operates on Player A
    assert "Carlos Alcaraz" not in user_msg


def test_designer_rejects_player_b_widgets_in_prompt_instruction() -> None:
    """The user prompt must explicitly instruct Opus to avoid MomentumMeter,
    PredictiveOverlay, and top-right nameplate (all require Player B data)."""
    client = _ScriptedClient([_response_with_text(
        '{"reason": "ok", "widgets": [{"widget": "PlayerNameplate", "slot": "top-left", "props": {}}]}',
    )])
    _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    user_msg = client.call_log[0]["messages"][0]["content"]
    assert "top-right" in user_msg.lower() or "PlayerNameplate@top-right" in user_msg
    assert "MomentumMeter" in user_msg
    assert "PredictiveOverlay" in user_msg


def test_designer_empty_widgets_array_is_valid() -> None:
    """Opus might decide 'no overlay' is the right answer. Empty widgets is a legitimate layout."""
    client = _ScriptedClient([_response_with_text(
        '{"reason": "Full-screen moment — no overlay.", "widgets": []}',
    )])
    layout = _run(generate_hud_layout(
        client, t_ms=0, trigger_description="t", state_summary="s",
    ))
    assert layout.widgets == []
    assert layout.reason == "Full-screen moment — no overlay."
