"""Tests for Phase 2 agent integration in backend/precompute.py.

Covers:
- run_agent_phase in isolation with a scripted fake Anthropic client
  (coach/designer/narrator cadence + caps)
- run_precompute wired end-to-end with a mocked agent client — verifies
  DuckDB rows AND match_data.json include agent outputs
- CLI `--skip-agents` flag short-circuits the agent phase
- Missing ANTHROPIC_API_KEY produces a warning but does NOT crash
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import duckdb
import numpy as np
import pytest

from backend import precompute
from backend.db.schema import PlayerDetection, PlayerSide, SignalSample, StateTransition

# ──────────────────────────── Fake Anthropic client ────────────────────────────


def _text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def _make_end_turn_response(text: str) -> SimpleNamespace:
    return SimpleNamespace(
        content=[_text_block(text)],
        stop_reason="end_turn",
        usage=SimpleNamespace(
            input_tokens=100, output_tokens=30,
            cache_read_input_tokens=50, cache_creation_input_tokens=0,
        ),
    )


class _PatternedClient:
    """Fake AsyncAnthropic that returns canned responses based on which agent called it.

    Coach calls have `tools=<list>`; Designer has no tools but uses Opus model; Narrator
    uses Haiku. That's enough to route responses to the right stub.
    """

    def __init__(self) -> None:
        self.coach_calls = 0
        self.design_calls = 0
        self.narrator_calls = 0
        self.call_log: list[dict[str, Any]] = []
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, **kwargs: Any) -> Any:
        self.call_log.append({"model": kwargs.get("model"), "has_tools": "tools" in kwargs})
        model = kwargs.get("model", "")
        has_tools = "tools" in kwargs
        if "haiku" in model.lower():
            self.narrator_calls += 1
            return _make_end_turn_response(f"beat #{self.narrator_calls}")
        if has_tools:
            # Opus with tools -> Coach
            self.coach_calls += 1
            return _make_end_turn_response(f"coach insight #{self.coach_calls}")
        # Opus no tools -> Designer. Return valid JSON spec.
        self.design_calls += 1
        layout_json = (
            '{"reason": "auto layout",'
            ' "widgets": ['
            '{"widget": "PlayerNameplate", "slot": "top-left", "props": {"player": "A"}}'
            ']}'
        )
        return _make_end_turn_response(layout_json)


# ──────────────────────────── Fixtures ────────────────────────────


def _sig(t_ms: int, player: str = "A", value: float = 1.0, state: str = "ACTIVE_RALLY") -> SignalSample:
    return SignalSample(
        timestamp_ms=t_ms,
        match_id="utr_01",
        player=player,
        signal_name="recovery_latency_ms",
        value=value,
        baseline_z_score=None,
        state=state,
    )


def _tr(t_ms: int, player: str = "A", from_state: str = "ACTIVE_RALLY", to_state: str = "DEAD_TIME") -> StateTransition:
    return StateTransition(
        timestamp_ms=t_ms,
        player=player,
        from_state=from_state,
        to_state=to_state,
        reason="kinematic",
    )


# ──────────────────────────── run_agent_phase tests ────────────────────────────


def _run_phase(**kwargs: Any) -> tuple[list, list, list]:
    return asyncio.run(precompute.run_agent_phase(**kwargs))


def test_run_agent_phase_fires_coach_on_active_rally_exit() -> None:
    client = _PatternedClient()
    transitions = [
        _tr(1000, "A", from_state="ACTIVE_RALLY", to_state="DEAD_TIME"),
        _tr(2000, "B", from_state="ACTIVE_RALLY", to_state="DEAD_TIME"),
        _tr(3000, "A", from_state="DEAD_TIME", to_state="PRE_SERVE_RITUAL"),  # not rally exit
    ]
    coach, _design, _beats = _run_phase(
        client=client, match_id="utr_01",
        signals=[_sig(500)], transitions=transitions,
        duration_ms=0, beat_period_sec=0,  # disable narrator for focused test
    )
    assert client.coach_calls == 2
    assert len(coach) == 2
    assert coach[0].commentary == "coach insight #1"
    assert coach[1].commentary == "coach insight #2"
    # Insight IDs include the player so they're unique per rally-end
    ids = {c.insight_id for c in coach}
    assert ids == {"coach_1000_A", "coach_2000_B"}


def test_run_agent_phase_fires_designer_on_pre_serve_entry() -> None:
    client = _PatternedClient()
    transitions = [
        _tr(1000, "A", from_state="DEAD_TIME", to_state="PRE_SERVE_RITUAL"),
        _tr(2000, "B", from_state="DEAD_TIME", to_state="PRE_SERVE_RITUAL"),
    ]
    _coach, design, _beats = _run_phase(
        client=client, match_id="utr_01",
        signals=[], transitions=transitions,
        duration_ms=0, beat_period_sec=0,
    )
    assert client.design_calls == 2
    assert len(design) == 2
    # Designer produced fallback-free layouts (our stub returned valid JSON)
    assert all(layout.reason == "auto layout" for layout in design)


def test_run_agent_phase_narrator_cadence() -> None:
    client = _PatternedClient()
    # 30s duration, 10s period → beats at 0, 10000, 20000 ms = 3 beats
    _coach, _design, beats = _run_phase(
        client=client, match_id="utr_01",
        signals=[], transitions=[],
        duration_ms=30_000, beat_period_sec=10.0,
    )
    assert client.narrator_calls == 3
    assert len(beats) == 3
    assert [b.timestamp_ms for b in beats] == [0, 10_000, 20_000]


def test_run_agent_phase_respects_coach_cap() -> None:
    client = _PatternedClient()
    transitions = [
        _tr(t, from_state="ACTIVE_RALLY", to_state="DEAD_TIME")
        for t in (1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000)
    ]
    coach, _, _ = _run_phase(
        client=client, match_id="utr_01",
        signals=[], transitions=transitions,
        duration_ms=0, beat_period_sec=0,
        coach_cap=3,
    )
    assert client.coach_calls == 3
    assert len(coach) == 3


def test_run_agent_phase_respects_design_cap() -> None:
    client = _PatternedClient()
    transitions = [
        _tr(t, from_state="DEAD_TIME", to_state="PRE_SERVE_RITUAL")
        for t in (1000, 2000, 3000, 4000)
    ]
    _, design, _ = _run_phase(
        client=client, match_id="utr_01",
        signals=[], transitions=transitions,
        duration_ms=0, beat_period_sec=0,
        design_cap=2,
    )
    assert client.design_calls == 2
    assert len(design) == 2


def test_run_agent_phase_respects_beat_cap() -> None:
    """Reviewer HIGH-2: narrator must cap concurrent API calls even on long clips."""
    client = _PatternedClient()
    # 200s duration, 1s period would fire 200 beats without the cap
    _coach, _design, beats = _run_phase(
        client=client, match_id="utr_01",
        signals=[], transitions=[],
        duration_ms=200_000, beat_period_sec=1.0,
        beat_cap=5,
    )
    assert client.narrator_calls == 5
    assert len(beats) == 5


def test_run_agent_phase_beat_period_zero_skips_narrator() -> None:
    client = _PatternedClient()
    _, _, beats = _run_phase(
        client=client, match_id="utr_01",
        signals=[], transitions=[],
        duration_ms=60_000, beat_period_sec=0.0,
    )
    assert client.narrator_calls == 0
    assert beats == []


def test_run_agent_phase_zero_duration_skips_narrator() -> None:
    client = _PatternedClient()
    _coach, _design, _beats = _run_phase(
        client=client, match_id="utr_01",
        signals=[], transitions=[],
        duration_ms=0, beat_period_sec=10.0,
    )
    assert client.narrator_calls == 0


def test_run_agent_phase_empty_everything_returns_empty_lists() -> None:
    client = _PatternedClient()
    coach, design, beats = _run_phase(
        client=client, match_id="utr_01",
        signals=[], transitions=[],
        duration_ms=0, beat_period_sec=0,
    )
    assert (coach, design, beats) == ([], [], [])
    assert client.call_log == []


def test_build_state_summary_with_signals_and_transitions() -> None:
    summary = precompute._build_state_summary(
        signals=[
            _sig(1000, "A", value=1.5, state="ACTIVE_RALLY"),
            _sig(1500, "B", value=2.3, state="ACTIVE_RALLY"),
        ],
        transitions=[_tr(1800, "A", from_state="ACTIVE_RALLY", to_state="DEAD_TIME")],
        t_ms=2000,
        window_sec=5.0,
    )
    assert "Latest transition" in summary
    assert "A ACTIVE_RALLY -> DEAD_TIME" in summary
    assert "recovery_latency_ms" in summary
    # Recent sample present
    assert "1.5" in summary or "2.3" in summary


def test_build_state_summary_empty_window() -> None:
    summary = precompute._build_state_summary(
        signals=[], transitions=[], t_ms=1000, window_sec=5.0,
    )
    assert "No recent signals" in summary


def test_build_signal_snapshot_returns_most_recent() -> None:
    snapshot = precompute._build_signal_snapshot(
        signals=[
            _sig(500, "A", value=1.0, state="ACTIVE_RALLY"),
            _sig(900, "B", value=2.0, state="ACTIVE_RALLY"),
        ],
        t_ms=1000,
        window_sec=1.0,
    )
    assert "Player B" in snapshot
    assert "ACTIVE_RALLY" in snapshot


def test_build_signal_snapshot_empty_window_returns_quiet_message() -> None:
    snapshot = precompute._build_signal_snapshot(
        signals=[_sig(0, value=1.0)],
        t_ms=60_000, window_sec=1.0,  # window doesn't include t=0
    )
    assert "Quiet moment" in snapshot


# ──────────────────────────── run_precompute end-to-end with client ────────────────────────────


def _valid_corners_dict() -> dict:
    return {
        "top_left": [0.25, 0.20],
        "top_right": [0.75, 0.20],
        "bottom_right": [0.95, 0.88],
        "bottom_left": [0.05, 0.88],
    }


def _write_corners_json(tmp_path: Path) -> Path:
    p = tmp_path / "corners.json"
    p.write_text(json.dumps(_valid_corners_dict()))
    return p


class _MinimalFakePose:
    """Same shape as FakePoseExtractor in test_precompute.py but inlined to avoid cross-file dep."""

    def infer(self, frame_bgr: np.ndarray) -> dict[PlayerSide, PlayerDetection | None]:
        kp_a = [(0.5, 0.75)] * 17
        kp_b = [(0.5, 0.25)] * 17
        conf = [0.9] * 17
        return {
            "A": PlayerDetection(
                player="A", keypoints_xyn=kp_a, confidence=conf, bbox_conf=0.92,
                feet_mid_xyn=(0.5, 0.75), feet_mid_m=(4.0, 20.0), fallback_mode="ankle",
            ),
            "B": PlayerDetection(
                player="B", keypoints_xyn=kp_b, confidence=conf, bbox_conf=0.88,
                feet_mid_xyn=(0.5, 0.25), feet_mid_m=(4.0, 4.0), fallback_mode="ankle",
            ),
        }


def _monkeypatch_probe_and_iter(
    monkeypatch: pytest.MonkeyPatch,
    width: int, height: int, fps: float, n_frames: int,
) -> None:
    duration = int(n_frames * 1000 / fps)
    monkeypatch.setattr(precompute, "probe_video_meta", lambda _p: (width, height, fps, duration))

    def _iter(_clip: Path, _w: int, _h: int):
        for i in range(n_frames):
            yield i, np.zeros((height, width, 3), dtype=np.uint8)

    monkeypatch.setattr(precompute, "iter_frames_from_ffmpeg", _iter)


def test_run_precompute_with_anthropic_client_writes_agent_outputs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _monkeypatch_probe_and_iter(monkeypatch, 1920, 1080, 30.0, 60)  # 2s @ 30fps

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"fake")
    db_path = tmp_path / "p.duckdb"
    out_json = tmp_path / "out.json"

    client = _PatternedClient()
    precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_agent_01",
        player_a_name="A", player_b_name="B",
        db_path=db_path,
        match_data_json_path=out_json,
        pose_extractor=_MinimalFakePose(),
        device="cpu",
        anthropic_client=client,
        beat_period_sec=1.0,  # 2 beats in 2s (t=0, t=1000)
    )

    # Narrator should have been called (at least once), so DuckDB has rows
    assert client.narrator_calls >= 1
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        beat_count = conn.execute(
            "SELECT COUNT(*) FROM narrator_beats WHERE match_id = 'utr_agent_01'"
        ).fetchone()[0]
        assert beat_count == client.narrator_calls
    finally:
        conn.close()

    # JSON has all three agent arrays populated (or at least narrator_beats given short clip)
    data = json.loads(out_json.read_text())
    assert "narrator_beats" in data
    assert len(data["narrator_beats"]) == client.narrator_calls
    # coach_insights + hud_layouts depend on state transitions; we accept 0+
    assert isinstance(data["coach_insights"], list)
    assert isinstance(data["hud_layouts"], list)


def test_run_precompute_without_anthropic_client_skips_agents(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    _monkeypatch_probe_and_iter(monkeypatch, 1920, 1080, 30.0, 15)

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"fake")
    db_path = tmp_path / "p.duckdb"
    out_json = tmp_path / "out.json"

    precompute.run_precompute(
        clip_path=clip_path, corners_json_path=corners_path,
        match_id="utr_none", player_a_name="A", player_b_name="B",
        db_path=db_path, match_data_json_path=out_json,
        pose_extractor=_MinimalFakePose(), device="cpu",
        anthropic_client=None,  # EXPLICIT skip
    )
    data = json.loads(out_json.read_text())
    assert data["coach_insights"] == []
    assert data["hud_layouts"] == []
    assert data["narrator_beats"] == []
    # DuckDB agent tables exist but empty
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        for table in ("coach_insights", "narrator_beats"):
            n = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            assert n == 0
    finally:
        conn.close()


# ──────────────────────────── CLI --skip-agents flag ────────────────────────────


def test_main_cli_skip_agents_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    _monkeypatch_probe_and_iter(monkeypatch, 1920, 1080, 30.0, 3)

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"fake")
    db_path = tmp_path / "p.duckdb"
    out_json = tmp_path / "out.json"

    # Inject a fake pose extractor through a monkeypatched run_precompute that we still
    # want to exercise end-to-end. Instead we assert that the code path doesn't touch
    # the Anthropic SDK at all when --skip-agents is set.
    import backend.precompute as pm

    captured_kwargs: dict[str, Any] = {}

    def _spy_run(*args: Any, **kwargs: Any) -> tuple[int, int]:
        captured_kwargs.update(kwargs)
        # Don't run the real pipeline — return a stub
        return (0, 0)

    monkeypatch.setattr(pm, "run_precompute", _spy_run)
    rc = pm.main([
        "--clip", str(clip_path),
        "--corners", str(corners_path),
        "--match-id", "utr_cli",
        "--player-a", "A", "--player-b", "B",
        "--db", str(db_path), "--out-json", str(out_json),
        "--device", "cpu",
        "--skip-agents",
    ])
    assert rc == 0
    # When --skip-agents, anthropic_client is None
    assert captured_kwargs.get("anthropic_client") is None
    out = capsys.readouterr().out
    assert "SKIPPED" in out


def test_main_cli_warns_and_skips_when_api_key_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    _monkeypatch_probe_and_iter(monkeypatch, 1920, 1080, 30.0, 3)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"fake")
    db_path = tmp_path / "p.duckdb"
    out_json = tmp_path / "out.json"

    import backend.precompute as pm
    captured: dict[str, Any] = {}
    monkeypatch.setattr(pm, "run_precompute", lambda *a, **kw: (captured.update(kw) or (0, 0)))

    rc = pm.main([
        "--clip", str(clip_path),
        "--corners", str(corners_path),
        "--match-id", "utr_cli",
        "--player-a", "A", "--player-b", "B",
        "--db", str(db_path), "--out-json", str(out_json),
        "--device", "cpu",
    ])
    assert rc == 0
    # No client built -> agents skipped silently (with stderr warn)
    assert captured.get("anthropic_client") is None
    err = capsys.readouterr().err
    assert "ANTHROPIC_API_KEY not set" in err
