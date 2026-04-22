"""Tests for backend/db/writer.py — batch-insert Pydantic models into DuckDB
and export `match_data.json` for the Next.js frontend.

TDD-first: these tests were written BEFORE writer.py existed.

Covers:
- write_match_meta insert + upsert semantics
- queue_* batching with auto-flush at BATCH_SIZE
- FrameKeypoints → 2 rows with BLOB packed float32 arrays
- None player handling (one-row-only case)
- AnomalyEvent / CoachInsight queue + flush + JSON round-trip for tool_calls
- close() flushes pending + context-manager __exit__ closes
- dump_match_data_json — file creation, parent dir, float rounding (USER-CORRECTION-015),
  exclude_none behavior
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import numpy as np
import pytest

from backend.db.schema import (
    AnomalyEvent,
    CoachInsight,
    FrameKeypoints,
    HUDLayoutSpec,
    HUDWidgetSpec,
    MatchMeta,
    NarratorBeat,
    PlayerDetection,
    SignalSample,
    StateTransition,
)
from backend.db.writer import DuckDBWriter, dump_match_data_json

# ──────────────────────────── Helpers ────────────────────────────

VALID_SHA = "a" * 64  # 64-char hex-ish


def _match_meta(match_id: str = "utr_01", **overrides) -> MatchMeta:
    defaults = dict(
        match_id=match_id,
        clip_sha256=VALID_SHA,
        clip_fps=30.0,
        duration_ms=10_000,
        width=1920,
        height=1080,
        player_a="Alice",
        player_b="Bob",
        court_corners_json='{"top_left": [0.1, 0.2]}',
    )
    defaults.update(overrides)
    return MatchMeta(**defaults)


def _signal_sample(t_ms: int = 100, value: float | None = 12.34, **overrides) -> SignalSample:
    defaults = dict(
        timestamp_ms=t_ms,
        match_id="utr_01",
        player="A",
        signal_name="recovery_latency_ms",
        value=value,
        baseline_z_score=0.5,
        state="ACTIVE_RALLY",
    )
    defaults.update(overrides)
    return SignalSample(**defaults)


def _player_detection(player: str = "A") -> PlayerDetection:
    kp = [(0.1 * i, 0.2 * i) for i in range(17)]
    # Normalize to [0,1]
    kp = [(min(x, 1.0), min(y, 1.0)) for x, y in kp]
    conf = [0.8] * 17
    return PlayerDetection(
        player=player,
        keypoints_xyn=kp,
        confidence=conf,
        bbox_conf=0.85,
        feet_mid_xyn=(0.5, 0.95),
        feet_mid_m=(4.0, 12.0),
        fallback_mode="ankle",
    )


def _frame_keypoints(
    t_ms: int = 100,
    frame_idx: int = 3,
    with_a: bool = True,
    with_b: bool = True,
) -> FrameKeypoints:
    return FrameKeypoints(
        t_ms=t_ms,
        frame_idx=frame_idx,
        player_a=_player_detection("A") if with_a else None,
        player_b=_player_detection("B") if with_b else None,
    )


def _anomaly(event_id: str = "evt_1", t_ms: int = 100) -> AnomalyEvent:
    return AnomalyEvent(
        event_id=event_id,
        timestamp_ms=t_ms,
        match_id="utr_01",
        player="A",
        signal_name="recovery_latency_ms",
        value=150.0,
        baseline_mean=100.0,
        baseline_std=10.0,
        z_score=5.0,
        severity=0.9,
    )


def _coach_insight(
    insight_id: str = "ins_1",
    tool_calls: list[dict] | None = None,
) -> CoachInsight:
    return CoachInsight(
        insight_id=insight_id,
        timestamp_ms=100,
        match_id="utr_01",
        thinking="Considering the matchup...",
        commentary="Alice is dominating the baseline.",
        tool_calls=tool_calls if tool_calls is not None else [{"name": "get_stats", "args": {}}],
        input_tokens=500,
        output_tokens=200,
        cache_read_tokens=50,
        cache_creation_tokens=10,
    )


def _narrator_beat(
    beat_id: str = "beat_1",
    t_ms: int = 500,
    text: str = "Forehand winner down the line.",
    **overrides,
) -> NarratorBeat:
    defaults = dict(
        beat_id=beat_id,
        timestamp_ms=t_ms,
        match_id="utr_01",
        text=text,
        input_tokens=80,
        output_tokens=25,
    )
    defaults.update(overrides)
    return NarratorBeat(**defaults)


def _hud_layout() -> HUDLayoutSpec:
    return HUDLayoutSpec(
        layout_id="l1",
        timestamp_ms=100,
        reason="First serve incoming",
        widgets=[HUDWidgetSpec(widget="PlayerNameplate", slot="top-left", props={"player": "A"})],
        valid_until_ms=5000,
    )


def _state_transition() -> StateTransition:
    return StateTransition(
        timestamp_ms=100,
        player="A",
        from_state="PRE_SERVE_RITUAL",
        to_state="ACTIVE_RALLY",
        reason="kinematic",
    )


# ──────────────────────────── write_match_meta ────────────────────────────


def test_write_match_meta_persists_single_row(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    meta = _match_meta()
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.write_match_meta(meta)

    with duckdb.connect(str(db), read_only=True) as conn:
        row = conn.execute(
            "SELECT match_id, clip_sha256, clip_fps, duration_ms, width, height, "
            "player_a, player_b, court_corners_json FROM match_meta"
        ).fetchone()
    assert row == (
        "utr_01",
        VALID_SHA,
        30.0,
        10_000,
        1920,
        1080,
        "Alice",
        "Bob",
        '{"top_left": [0.1, 0.2]}',
    )


def test_write_match_meta_upserts_on_same_id(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.write_match_meta(_match_meta(player_a="Alice", player_b="Bob"))
        w.write_match_meta(_match_meta(player_a="Carl", player_b="Dana", duration_ms=20_000))

    with duckdb.connect(str(db), read_only=True) as conn:
        rows = conn.execute("SELECT player_a, player_b, duration_ms FROM match_meta").fetchall()
    assert rows == [("Carl", "Dana", 20_000)]


# ──────────────────────────── queue_signal ────────────────────────────


def test_queue_and_flush_signal_samples(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_signal(_signal_sample(t_ms=100, value=10.0))
        w.queue_signal(_signal_sample(t_ms=200, value=20.0, signal_name="lateral_work_rate"))
        w.queue_signal(_signal_sample(t_ms=300, value=30.0, signal_name="split_step_latency_ms"))
        w.flush()

    with duckdb.connect(str(db), read_only=True) as conn:
        rows = conn.execute(
            "SELECT timestamp_ms, match_id, player, signal_name, value, "
            "baseline_z_score, state FROM signals ORDER BY timestamp_ms"
        ).fetchall()
    assert len(rows) == 3
    assert rows[0] == (100, "utr_01", "A", "recovery_latency_ms", 10.0, 0.5, "ACTIVE_RALLY")
    assert rows[1][3] == "lateral_work_rate"
    assert rows[2][3] == "split_step_latency_ms"


def test_queue_signal_auto_flushes_at_batch_size(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(DuckDBWriter, "BATCH_SIZE", 2)
    db = tmp_path / "p.duckdb"
    w = DuckDBWriter(db, match_id="utr_01")
    try:
        w.queue_signal(_signal_sample(t_ms=100))
        w.queue_signal(_signal_sample(t_ms=200))
        # At this point BATCH_SIZE reached — auto-flush should have fired.
        w.queue_signal(_signal_sample(t_ms=300))
        # 3rd queued; not yet flushed. Verify 2 persisted so far.
        count = w._conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
    finally:
        w.close()
    assert count == 2


# ──────────────────────────── queue_keypoint_frame ────────────────────────────


def test_queue_and_flush_keypoint_frames(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    frame = _frame_keypoints(t_ms=500, with_a=True, with_b=True)
    orig_a_kp = frame.player_a.keypoints_xyn  # type: ignore[union-attr]
    orig_a_conf = frame.player_a.confidence  # type: ignore[union-attr]

    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_keypoint_frame(frame)
        w.flush()

    with duckdb.connect(str(db), read_only=True) as conn:
        rows = conn.execute(
            "SELECT timestamp_ms, match_id, player, keypoints_xyn, confidence "
            "FROM keypoints ORDER BY player"
        ).fetchall()
    assert len(rows) == 2
    assert {r[2] for r in rows} == {"A", "B"}

    # Verify the A row's BLOB round-trips to the original keypoints
    a_row = next(r for r in rows if r[2] == "A")
    kp_blob = a_row[3]
    conf_blob = a_row[4]
    kp_arr = np.frombuffer(kp_blob, dtype=np.float32).reshape(17, 2)
    conf_arr = np.frombuffer(conf_blob, dtype=np.float32)
    # Compare with float32 tolerance — schema kept the original floats
    for (orig_x, orig_y), (got_x, got_y) in zip(orig_a_kp, kp_arr, strict=True):
        assert got_x == pytest.approx(orig_x, abs=1e-5)
        assert got_y == pytest.approx(orig_y, abs=1e-5)
    for orig_c, got_c in zip(orig_a_conf, conf_arr, strict=True):
        assert got_c == pytest.approx(orig_c, abs=1e-5)


def test_queue_keypoint_frame_with_none_player_b_writes_only_one_row(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    frame = _frame_keypoints(t_ms=500, with_a=True, with_b=False)
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_keypoint_frame(frame)
        w.flush()

    with duckdb.connect(str(db), read_only=True) as conn:
        rows = conn.execute("SELECT player FROM keypoints").fetchall()
    assert rows == [("A",)]


def test_queue_keypoint_frame_with_both_none_writes_zero_rows(tmp_path: Path) -> None:
    """Defensive — if both detections are None, no rows at all."""
    db = tmp_path / "p.duckdb"
    frame = _frame_keypoints(t_ms=500, with_a=False, with_b=False)
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_keypoint_frame(frame)
        w.flush()
    with duckdb.connect(str(db), read_only=True) as conn:
        count = conn.execute("SELECT COUNT(*) FROM keypoints").fetchone()[0]
    assert count == 0


# ──────────────────────────── queue_anomaly ────────────────────────────


def test_queue_and_flush_anomalies(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_anomaly(_anomaly(event_id="evt_1", t_ms=100))
        w.queue_anomaly(_anomaly(event_id="evt_2", t_ms=200))
        w.flush()

    with duckdb.connect(str(db), read_only=True) as conn:
        rows = conn.execute(
            "SELECT event_id, timestamp_ms, match_id, player, signal_name, "
            "value, baseline_mean, baseline_std, z_score, severity "
            "FROM anomalies ORDER BY timestamp_ms"
        ).fetchall()
    assert len(rows) == 2
    assert rows[0][0] == "evt_1"
    assert rows[0][4] == "recovery_latency_ms"
    assert rows[0][5] == 150.0
    assert rows[0][9] == 0.9
    assert rows[1][0] == "evt_2"


# ──────────────────────────── queue_coach_insight ────────────────────────────


def test_queue_and_flush_coach_insights(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    tool_calls_payload = [
        {"name": "get_stats", "args": {"player": "A"}},
        {"name": "lookup_history", "args": {"k": 5}},
    ]
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_coach_insight(_coach_insight(tool_calls=tool_calls_payload))
        w.flush()

    with duckdb.connect(str(db), read_only=True) as conn:
        rows = conn.execute(
            "SELECT insight_id, timestamp_ms, thinking, commentary, tool_calls, "
            "input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens "
            "FROM coach_insights"
        ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "ins_1"
    assert rows[0][2] == "Considering the matchup..."
    assert rows[0][3] == "Alice is dominating the baseline."
    # tool_calls round-trips through json.dumps/loads
    assert json.loads(rows[0][4]) == tool_calls_payload
    assert rows[0][5] == 500
    assert rows[0][6] == 200
    assert rows[0][7] == 50
    assert rows[0][8] == 10


def test_queue_and_flush_narrator_beats(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_narrator_beat(_narrator_beat(beat_id="b1", t_ms=1000, text="Ace up the tee."))
        w.queue_narrator_beat(_narrator_beat(beat_id="b2", t_ms=2000, text="Service break in sight."))
        w.flush()

    with duckdb.connect(str(db), read_only=True) as conn:
        rows = conn.execute(
            "SELECT beat_id, timestamp_ms, match_id, text, input_tokens, output_tokens "
            "FROM narrator_beats ORDER BY timestamp_ms"
        ).fetchall()
    assert len(rows) == 2
    assert rows[0] == ("b1", 1000, "utr_01", "Ace up the tee.", 80, 25)
    assert rows[1][0] == "b2"
    assert rows[1][3] == "Service break in sight."


def test_queue_narrator_beat_auto_flushes_at_batch_size(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = tmp_path / "p.duckdb"
    monkeypatch.setattr(DuckDBWriter, "BATCH_SIZE", 3)
    with DuckDBWriter(db, match_id="utr_01") as w:
        for i in range(3):
            w.queue_narrator_beat(_narrator_beat(beat_id=f"b{i}", t_ms=1000 * i, text=f"beat {i}"))
        # After 3 queued, auto-flush fires; pending must be empty
        assert w._pending_narrator == []

    with duckdb.connect(str(db), read_only=True) as conn:
        count = conn.execute("SELECT COUNT(*) FROM narrator_beats").fetchone()[0]
    assert count == 3


def test_queue_narrator_beat_primary_key_upsert(tmp_path: Path) -> None:
    """beat_id is PRIMARY KEY — re-queueing the same id must upsert, not duplicate."""
    db = tmp_path / "p.duckdb"
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_narrator_beat(_narrator_beat(beat_id="same", text="v1"))
        w.queue_narrator_beat(_narrator_beat(beat_id="same", text="v2"))
        w.flush()

    with duckdb.connect(str(db), read_only=True) as conn:
        rows = conn.execute(
            "SELECT beat_id, text FROM narrator_beats ORDER BY timestamp_ms"
        ).fetchall()
    # Executemany within a single flush inserts both rows; INSERT OR REPLACE keeps the later one.
    assert len(rows) == 1
    assert rows[0] == ("same", "v2")


# ──────────────────────────── close / context manager / empty flush ────────────────────────────


def test_close_flushes_pending(tmp_path: Path) -> None:
    """close() must flush pending queues before closing the connection."""
    db = tmp_path / "p.duckdb"
    w = DuckDBWriter(db, match_id="utr_01")
    w.queue_signal(_signal_sample(t_ms=100))
    w.queue_signal(_signal_sample(t_ms=200))
    w.close()  # Note: no manual flush()

    with duckdb.connect(str(db), read_only=True) as conn:
        count = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
    assert count == 2


def test_context_manager_closes_on_exit(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    with DuckDBWriter(db, match_id="utr_01") as w:
        w.queue_signal(_signal_sample(t_ms=100))
    # After block exits, signal must be persisted
    with duckdb.connect(str(db), read_only=True) as conn:
        count = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
    assert count == 1


def test_flush_on_empty_queues_is_noop(tmp_path: Path) -> None:
    db = tmp_path / "p.duckdb"
    with DuckDBWriter(db, match_id="utr_01") as w:
        # No crash, no rows
        w.flush()
        w.flush()
    with duckdb.connect(str(db), read_only=True) as conn:
        for tbl in ("signals", "keypoints", "anomalies", "coach_insights", "narrator_beats"):
            count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            assert count == 0


# ──────────────────────────── dump_match_data_json ────────────────────────────


def test_dump_match_data_json_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    path = dump_match_data_json(
        out,
        meta=_match_meta(),
        keypoints=[_frame_keypoints(100)],
        signals=[_signal_sample(100)],
        anomalies=[_anomaly()],
        coach_insights=[_coach_insight()],
        hud_layouts=[_hud_layout()],
        transitions=[_state_transition()],
    )
    assert path == out
    assert out.exists()

    data = json.loads(out.read_text())
    # Top-level structure
    assert set(data.keys()) >= {
        "meta",
        "keypoints",
        "signals",
        "anomalies",
        "coach_insights",
        "hud_layouts",
        "transitions",
    }
    assert data["meta"]["match_id"] == "utr_01"
    assert len(data["keypoints"]) == 1
    assert len(data["signals"]) == 1
    assert data["signals"][0]["signal_name"] == "recovery_latency_ms"


def test_dump_match_data_json_rounds_floats_to_4_decimals(tmp_path: Path) -> None:
    """USER-CORRECTION-015: Pydantic field_serializer propagates through nested models.

    We pass a high-precision float to SignalSample.value; the serialized JSON must
    round it to 4 decimal places automatically — no manual rounding needed.
    """
    out = tmp_path / "rounded.json"
    dump_match_data_json(
        out,
        meta=_match_meta(),
        keypoints=[],
        signals=[_signal_sample(t_ms=100, value=0.123456789)],
        anomalies=[],
        coach_insights=[],
        hud_layouts=[],
        transitions=[],
    )
    data = json.loads(out.read_text())
    assert data["signals"][0]["value"] == pytest.approx(0.1235, abs=1e-9)


def test_dump_match_data_json_creates_parent_dir(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "deeper" / "out.json"
    assert not out.parent.exists()
    dump_match_data_json(
        out,
        meta=_match_meta(),
        keypoints=[],
        signals=[],
        anomalies=[],
        coach_insights=[],
        hud_layouts=[],
        transitions=[],
    )
    assert out.parent.is_dir()
    assert out.exists()


def test_dump_match_data_json_excludes_none_fields(tmp_path: Path) -> None:
    """exclude_none=True: optional fields with value None must be OMITTED from output."""
    out = tmp_path / "excluded.json"
    sample = _signal_sample(t_ms=100, value=None, baseline_z_score=None)
    dump_match_data_json(
        out,
        meta=_match_meta(),
        keypoints=[],
        signals=[sample],
        anomalies=[],
        coach_insights=[],
        hud_layouts=[],
        transitions=[],
    )
    data = json.loads(out.read_text())
    s0 = data["signals"][0]
    # Since exclude_none=True, keys with None value must not be present
    assert "value" not in s0
    assert "baseline_z_score" not in s0
    # Required (non-null) fields still present
    assert s0["signal_name"] == "recovery_latency_ms"
    assert s0["state"] == "ACTIVE_RALLY"


def test_dump_match_data_json_includes_narrator_beats(tmp_path: Path) -> None:
    """Narrator beats must round-trip through the JSON export with their text intact."""
    out = tmp_path / "with_beats.json"
    dump_match_data_json(
        out,
        meta=_match_meta(),
        keypoints=[],
        signals=[],
        anomalies=[],
        coach_insights=[],
        hud_layouts=[],
        transitions=[],
        narrator_beats=[
            _narrator_beat(beat_id="nb1", t_ms=1000, text="First up: Nadal's serve routine."),
            _narrator_beat(beat_id="nb2", t_ms=2000, text="Djokovic breaks tension with a baseline drive."),
        ],
    )
    data = json.loads(out.read_text())
    assert "narrator_beats" in data
    assert len(data["narrator_beats"]) == 2
    assert data["narrator_beats"][0]["beat_id"] == "nb1"
    assert data["narrator_beats"][0]["text"] == "First up: Nadal's serve routine."
    assert data["narrator_beats"][1]["input_tokens"] == 80


def test_dump_match_data_json_default_narrator_beats_empty(tmp_path: Path) -> None:
    """Omitting narrator_beats keyword must default to empty list (backward-compat for Phase-1 callers)."""
    out = tmp_path / "no_beats.json"
    dump_match_data_json(
        out,
        meta=_match_meta(),
        keypoints=[],
        signals=[],
        anomalies=[],
        coach_insights=[],
        hud_layouts=[],
        transitions=[],
    )
    data = json.loads(out.read_text())
    assert data["narrator_beats"] == []


def test_dump_match_data_json_accepts_iterables(tmp_path: Path) -> None:
    """The signature takes Iterable[...] — generators must work too."""
    out = tmp_path / "iter.json"
    dump_match_data_json(
        out,
        meta=_match_meta(),
        keypoints=(kp for kp in [_frame_keypoints(100), _frame_keypoints(200)]),
        signals=iter([_signal_sample(100), _signal_sample(200)]),
        anomalies=iter([]),
        coach_insights=iter([]),
        hud_layouts=iter([]),
        transitions=iter([]),
    )
    data = json.loads(out.read_text())
    assert len(data["keypoints"]) == 2
    assert len(data["signals"]) == 2
