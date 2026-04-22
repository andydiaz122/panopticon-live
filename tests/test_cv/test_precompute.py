"""Tests for backend/precompute.py — master CV pre-compute CLI.

TDD-first: these tests were written BEFORE precompute.py existed.

All tests run in CI without ffmpeg binaries and without ML weights.
`subprocess.Popen` + `subprocess.run` are monkeypatched; a `FakePoseExtractor`
stands in for the real YOLO-backed `PoseExtractor`.

Covered:
- probe_video_meta ffprobe JSON parsing (fractional fps, integer fps, ffprobe missing)
- iter_frames_from_ffmpeg chunked stdout reading (yield-and-stop semantics)
- compute_clip_sha256 streaming hash
- run_precompute end-to-end with mocked pose + iter
- Empty-video tolerance
- Re-run overwrites match_data.json (no appending)
- CLI arg parsing
- MPS empty_cache cadence (every 50 frames)
- Corner JSON error paths
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pydantic
import pytest

from backend.db.schema import PlayerDetection, PlayerSide

# ──────────────────────────── Helpers ────────────────────────────


def _valid_corners_dict() -> dict:
    """Canonical normalized trapezoid for a broadcast tennis view."""
    return {
        "top_left": [0.25, 0.20],
        "top_right": [0.75, 0.20],
        "bottom_right": [0.95, 0.88],
        "bottom_left": [0.05, 0.88],
    }


def _write_corners_json(tmp_path: Path, name: str = "corners.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(_valid_corners_dict()))
    return path


class FakePoseExtractor:
    """Minimal stand-in for PoseExtractor that satisfies the DAG contract.

    Yields 2 PlayerDetection objects per frame — one per half-court (A and B) —
    constructed so feet_mid_m lands on opposite sides of the net at y=11.885.
    No YOLO weights, no torch, nothing external.
    """

    def __init__(self) -> None:
        self._call_count = 0

    def infer(self, frame_bgr: np.ndarray) -> dict[PlayerSide, PlayerDetection | None]:
        self._call_count += 1
        # Construct keypoints: all at (0.5, 0.75) for A (near side → y_m large),
        # and all at (0.5, 0.25) for B (far side → y_m small). Confidence 0.9 everywhere.
        kp_a: list[tuple[float, float]] = [(0.5, 0.75)] * 17
        kp_b: list[tuple[float, float]] = [(0.5, 0.25)] * 17
        conf = [0.9] * 17

        detection_a = PlayerDetection(
            player="A",
            keypoints_xyn=kp_a,
            confidence=conf,
            bbox_conf=0.92,
            feet_mid_xyn=(0.5, 0.75),
            feet_mid_m=(4.0, 20.0),  # near court half (y_m > 11.885)
            fallback_mode="ankle",
        )
        detection_b = PlayerDetection(
            player="B",
            keypoints_xyn=kp_b,
            confidence=conf,
            bbox_conf=0.88,
            feet_mid_xyn=(0.5, 0.25),
            feet_mid_m=(4.0, 4.0),  # far court half (y_m < 11.885)
            fallback_mode="ankle",
        )
        return {"A": detection_a, "B": detection_b}


class _FakePopen:
    """Fake subprocess.Popen for iter_frames_from_ffmpeg tests.

    `stdout` is a MagicMock with .read(N) returning the next preloaded chunk.
    """

    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = list(chunks)
        self.stdout = MagicMock()
        self.stdout.read = MagicMock(side_effect=self._read)
        self.stderr = MagicMock()
        self.returncode: int | None = None

    def _read(self, n: int) -> bytes:
        if not self._chunks:
            return b""
        return self._chunks.pop(0)

    def wait(self, timeout: float | None = None) -> int:
        self.returncode = 0
        return 0


# ──────────────────────────── probe_video_meta ────────────────────────────


def test_probe_video_meta_parses_ffprobe_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from backend import precompute

    ffprobe_payload = json.dumps({
        "streams": [{
            "width": 1920,
            "height": 1080,
            "r_frame_rate": "30000/1001",  # 29.97 fps
            "duration": "10.5",
        }]
    })
    fake_result = SimpleNamespace(stdout=ffprobe_payload, stderr="", returncode=0)
    monkeypatch.setattr(precompute.subprocess, "run", lambda *a, **kw: fake_result)

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"fake")

    width, height, fps, duration_ms = precompute.probe_video_meta(clip)

    assert width == 1920
    assert height == 1080
    assert fps == pytest.approx(30000 / 1001, rel=1e-6)
    assert duration_ms == 10500


def test_probe_video_meta_handles_integer_fps(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from backend import precompute

    ffprobe_payload = json.dumps({
        "streams": [{
            "width": 640,
            "height": 360,
            "r_frame_rate": "30/1",
            "duration": "2.0",
        }]
    })
    fake_result = SimpleNamespace(stdout=ffprobe_payload, stderr="", returncode=0)
    monkeypatch.setattr(precompute.subprocess, "run", lambda *a, **kw: fake_result)

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"fake")

    width, height, fps, duration_ms = precompute.probe_video_meta(clip)
    assert width == 640
    assert height == 360
    assert fps == 30.0
    assert duration_ms == 2000


def test_probe_video_meta_raises_on_ffprobe_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from backend import precompute

    def _raise_not_found(*args, **kwargs):
        raise FileNotFoundError("ffprobe not installed")

    monkeypatch.setattr(precompute.subprocess, "run", _raise_not_found)

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"fake")

    with pytest.raises(RuntimeError, match="ffprobe"):
        precompute.probe_video_meta(clip)


def test_probe_video_meta_handles_missing_duration(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Some MKV/WebM streams omit `duration` — probe returns 0 and caller reconciles later."""
    from backend import precompute

    ffprobe_payload = json.dumps({
        "streams": [{
            "width": 1280,
            "height": 720,
            "r_frame_rate": "24/1",
            # no "duration" key
        }]
    })
    fake_result = SimpleNamespace(stdout=ffprobe_payload, stderr="", returncode=0)
    monkeypatch.setattr(precompute.subprocess, "run", lambda *a, **kw: fake_result)

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"fake")

    width, height, fps, duration_ms = precompute.probe_video_meta(clip)
    assert width == 1280
    assert height == 720
    assert fps == 24.0
    assert duration_ms == 0  # fallback sentinel


# ──────────────────────────── iter_frames_from_ffmpeg ────────────────────────────


def test_iter_frames_from_ffmpeg_yields_frames_then_stops(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from backend import precompute

    width, height = 8, 4
    frame_size = width * height * 3
    # 3 full frames, then empty (EOF)
    chunks = [b"\x00" * frame_size, b"\x11" * frame_size, b"\x22" * frame_size, b""]

    fake_popen = _FakePopen(chunks)
    monkeypatch.setattr(
        precompute.subprocess, "Popen", lambda *a, **kw: fake_popen
    )

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"fake")

    frames = list(precompute.iter_frames_from_ffmpeg(clip, width, height))
    assert len(frames) == 3
    for idx, (frame_idx, arr) in enumerate(frames):
        assert frame_idx == idx
        assert arr.shape == (height, width, 3)
        assert arr.dtype == np.uint8


def test_iter_frames_handles_truncated_final_frame(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Truncated tail (< frame_size) is discarded — no partial yield."""
    from backend import precompute

    width, height = 4, 4
    frame_size = width * height * 3
    # One full frame, then a truncated partial — should stop after 1 yield.
    chunks = [b"\xff" * frame_size, b"\x00" * (frame_size // 2)]

    fake_popen = _FakePopen(chunks)
    monkeypatch.setattr(
        precompute.subprocess, "Popen", lambda *a, **kw: fake_popen
    )

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"fake")

    frames = list(precompute.iter_frames_from_ffmpeg(clip, width, height))
    assert len(frames) == 1


def test_iter_frames_empty_stdout_yields_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from backend import precompute

    fake_popen = _FakePopen(chunks=[b""])
    monkeypatch.setattr(
        precompute.subprocess, "Popen", lambda *a, **kw: fake_popen
    )

    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"fake")

    frames = list(precompute.iter_frames_from_ffmpeg(clip, 4, 4))
    assert frames == []


# ──────────────────────────── compute_clip_sha256 ────────────────────────────


def test_compute_clip_sha256_on_tiny_file(tmp_path: Path) -> None:
    from backend import precompute

    # ~1MB deterministic content
    payload = b"PANOPTICON-LIVE\n" * (65536)  # 16 * 65536 = 1 MiB exactly
    clip = tmp_path / "tiny.mp4"
    clip.write_bytes(payload)

    expected = hashlib.sha256(payload).hexdigest()
    actual = precompute.compute_clip_sha256(clip)
    assert actual == expected
    assert len(actual) == 64


def test_compute_clip_sha256_empty_file(tmp_path: Path) -> None:
    from backend import precompute
    clip = tmp_path / "empty.mp4"
    clip.write_bytes(b"")
    expected = hashlib.sha256(b"").hexdigest()
    assert precompute.compute_clip_sha256(clip) == expected


# ──────────────────────────── run_precompute end-to-end ────────────────────────────


def _monkeypatch_probe_and_iter(
    monkeypatch: pytest.MonkeyPatch,
    width: int,
    height: int,
    fps: float,
    n_frames: int,
    duration_ms: int | None = None,
) -> None:
    """Helper to patch probe_video_meta + iter_frames_from_ffmpeg on the precompute module."""
    from backend import precompute

    duration = duration_ms if duration_ms is not None else int(n_frames * 1000 / fps)
    monkeypatch.setattr(
        precompute, "probe_video_meta", lambda _p: (width, height, fps, duration)
    )

    def _iter(_clip, _w, _h):
        for i in range(n_frames):
            # Shape matches real ffmpeg bgr24: (H, W, 3) uint8
            yield i, np.zeros((height, width, 3), dtype=np.uint8)

    monkeypatch.setattr(precompute, "iter_frames_from_ffmpeg", _iter)


def test_run_precompute_end_to_end_with_mocked_pose_extractor(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from backend import precompute

    _monkeypatch_probe_and_iter(
        monkeypatch, width=1920, height=1080, fps=30.0, n_frames=10
    )

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"pretend-this-is-an-mp4")
    db_path = tmp_path / "panopticon.duckdb"
    json_out = tmp_path / "out" / "match.json"

    fake_extractor = FakePoseExtractor()

    frames_processed, signals_emitted = precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_01",
        player_a_name="Alice",
        player_b_name="Bob",
        db_path=db_path,
        match_data_json_path=json_out,
        pose_extractor=fake_extractor,
        device="cpu",
    )

    assert frames_processed == 10
    # signals_emitted is non-deterministic at this tiny scale, but must be >= 0
    assert signals_emitted >= 0

    # DuckDB must exist + have rows in match_meta and keypoints
    import duckdb
    assert db_path.exists()
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        meta_rows = conn.execute("SELECT match_id, player_a, player_b FROM match_meta").fetchall()
        assert len(meta_rows) == 1
        assert meta_rows[0] == ("utr_01", "Alice", "Bob")

        keypoints_rows = conn.execute(
            "SELECT COUNT(*) FROM keypoints WHERE match_id = 'utr_01'"
        ).fetchone()[0]
        # 10 frames x 2 players = 20 rows
        assert keypoints_rows == 20
    finally:
        conn.close()

    # match_data.json must exist + be valid + include the match_id
    assert json_out.exists()
    data = json.loads(json_out.read_text())
    assert data["meta"]["match_id"] == "utr_01"
    assert isinstance(data["keypoints"], list)
    assert isinstance(data["signals"], list)
    assert isinstance(data["transitions"], list)
    assert len(data["keypoints"]) == 10


def test_run_precompute_handles_empty_video(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from backend import precompute

    _monkeypatch_probe_and_iter(
        monkeypatch, width=1920, height=1080, fps=30.0, n_frames=0, duration_ms=0
    )

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"0")
    db_path = tmp_path / "panopticon.duckdb"
    json_out = tmp_path / "match.json"

    frames, signals = precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_00",
        player_a_name="X",
        player_b_name="Y",
        db_path=db_path,
        match_data_json_path=json_out,
        pose_extractor=FakePoseExtractor(),
        device="cpu",
    )

    assert frames == 0
    assert signals == 0
    assert json_out.exists()
    data = json.loads(json_out.read_text())
    assert data["meta"]["match_id"] == "utr_00"
    assert data["keypoints"] == []
    assert data["signals"] == []
    assert data["anomalies"] == []


def test_run_precompute_rewrites_matchdata_json_on_rerun(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from backend import precompute

    _monkeypatch_probe_and_iter(
        monkeypatch, width=1280, height=720, fps=30.0, n_frames=3
    )

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"same-content")
    db_path = tmp_path / "panopticon.duckdb"
    json_out = tmp_path / "match.json"

    # Run 1
    precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_rerun",
        player_a_name="A1",
        player_b_name="B1",
        db_path=db_path,
        match_data_json_path=json_out,
        pose_extractor=FakePoseExtractor(),
        device="cpu",
    )
    first_text = json_out.read_text()

    # Run 2 — same args, result should overwrite (same content → same bytes)
    precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_rerun",
        player_a_name="A1",
        player_b_name="B1",
        db_path=db_path,
        match_data_json_path=json_out,
        pose_extractor=FakePoseExtractor(),
        device="cpu",
    )
    second_text = json_out.read_text()

    # File must have been rewritten (not appended to: must still parse as one JSON object)
    data = json.loads(second_text)
    assert data["meta"]["match_id"] == "utr_rerun"
    # Must parse cleanly — not double-written
    assert second_text.startswith("{") and second_text.endswith("}")
    # Same inputs → same output
    assert first_text == second_text


def test_run_precompute_fails_fast_on_missing_corners_json(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from backend import precompute

    _monkeypatch_probe_and_iter(monkeypatch, 1920, 1080, 30.0, 1)

    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"fake")
    missing_corners = tmp_path / "does-not-exist.json"
    db_path = tmp_path / "db.duckdb"
    json_out = tmp_path / "out.json"

    with pytest.raises((FileNotFoundError, json.JSONDecodeError)):
        precompute.run_precompute(
            clip_path=clip_path,
            corners_json_path=missing_corners,
            match_id="x",
            player_a_name="A",
            player_b_name="B",
            db_path=db_path,
            match_data_json_path=json_out,
            pose_extractor=FakePoseExtractor(),
            device="cpu",
        )


def test_run_precompute_raises_on_invalid_corners_json_schema(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from backend import precompute

    _monkeypatch_probe_and_iter(monkeypatch, 1920, 1080, 30.0, 1)

    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"fake")
    bad_corners = tmp_path / "corners.json"
    bad_corners.write_text(json.dumps({"top_left": [0.1, 0.2]}))  # missing fields
    db_path = tmp_path / "db.duckdb"
    json_out = tmp_path / "out.json"

    with pytest.raises(pydantic.ValidationError):
        precompute.run_precompute(
            clip_path=clip_path,
            corners_json_path=bad_corners,
            match_id="x",
            player_a_name="A",
            player_b_name="B",
            db_path=db_path,
            match_data_json_path=json_out,
            pose_extractor=FakePoseExtractor(),
            device="cpu",
        )


# ──────────────────────────── MPS empty_cache cadence ────────────────────────────


def test_mps_empty_cache_called_every_50_frames(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """With device='mps' and 110 frames, empty_cache must fire at 50 and 100 (not at 0)."""
    from backend import precompute

    _monkeypatch_probe_and_iter(monkeypatch, 1920, 1080, 30.0, 110)

    # Install a real MagicMock on torch.mps.empty_cache. Torch may or may not be importable;
    # we build a fake torch.mps regardless and route the module lookup through sys.modules.
    import sys
    import types

    fake_torch = types.ModuleType("torch")
    fake_torch.mps = types.SimpleNamespace(empty_cache=MagicMock())  # type: ignore[attr-defined]

    # inference_mode must be a context manager
    class _InferenceMode:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    fake_torch.inference_mode = _InferenceMode  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"x")
    db_path = tmp_path / "db.duckdb"
    json_out = tmp_path / "out.json"

    precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_mps",
        player_a_name="A",
        player_b_name="B",
        db_path=db_path,
        match_data_json_path=json_out,
        pose_extractor=FakePoseExtractor(),
        device="mps",
    )

    # Expect calls at frame_idx 50 and 100 — exactly 2.
    assert fake_torch.mps.empty_cache.call_count == 2


def test_mps_empty_cache_not_called_on_cpu(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """device='cpu' means no MPS empty_cache, no matter how many frames."""
    from backend import precompute

    _monkeypatch_probe_and_iter(monkeypatch, 1920, 1080, 30.0, 150)

    import sys
    import types

    fake_torch = types.ModuleType("torch")
    fake_torch.mps = types.SimpleNamespace(empty_cache=MagicMock())  # type: ignore[attr-defined]

    class _InferenceMode:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    fake_torch.inference_mode = _InferenceMode  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"x")

    precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_cpu",
        player_a_name="A",
        player_b_name="B",
        db_path=tmp_path / "db.duckdb",
        match_data_json_path=tmp_path / "out.json",
        pose_extractor=FakePoseExtractor(),
        device="cpu",
    )

    assert fake_torch.mps.empty_cache.call_count == 0


# ──────────────────────────── CLI ────────────────────────────


def test_main_cli_parses_args_and_invokes_run_precompute(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from backend import precompute

    captured_kwargs: dict = {}

    def _stub(**kwargs) -> tuple[int, int]:
        captured_kwargs.update(kwargs)
        return (42, 7)

    monkeypatch.setattr(precompute, "run_precompute", _stub)

    argv = [
        "--clip", str(tmp_path / "clip.mp4"),
        "--corners", str(tmp_path / "corners.json"),
        "--match-id", "utr_cli",
        "--player-a", "Alice",
        "--player-b", "Bob",
        "--db", str(tmp_path / "panopticon.duckdb"),
        "--out-json", str(tmp_path / "match.json"),
        "--device", "cpu",
    ]

    rc = precompute.main(argv)
    assert rc == 0

    # Verify the stub received the right values
    assert captured_kwargs["clip_path"] == tmp_path / "clip.mp4"
    assert captured_kwargs["corners_json_path"] == tmp_path / "corners.json"
    assert captured_kwargs["match_id"] == "utr_cli"
    assert captured_kwargs["player_a_name"] == "Alice"
    assert captured_kwargs["player_b_name"] == "Bob"
    assert captured_kwargs["db_path"] == tmp_path / "panopticon.duckdb"
    assert captured_kwargs["match_data_json_path"] == tmp_path / "match.json"
    assert captured_kwargs["device"] == "cpu"


def test_main_cli_missing_required_arg_exits_nonzero(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """argparse raises SystemExit(2) when required args missing."""
    from backend import precompute

    with pytest.raises(SystemExit):
        precompute.main(["--clip", str(tmp_path / "clip.mp4")])


# ──────────────────────────── End-to-end: real pipeline produces keypoints + signals ────────────────────────────


def test_run_precompute_writes_match_meta_with_correct_fps_and_dimensions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Meta row must carry the dimensions + fps we probed."""
    from backend import precompute

    _monkeypatch_probe_and_iter(monkeypatch, 1280, 720, 24.0, 5, duration_ms=5000)

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"data")
    db_path = tmp_path / "db.duckdb"
    json_out = tmp_path / "out.json"

    precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_meta",
        player_a_name="A",
        player_b_name="B",
        db_path=db_path,
        match_data_json_path=json_out,
        pose_extractor=FakePoseExtractor(),
        device="cpu",
    )

    import duckdb
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        row = conn.execute(
            "SELECT clip_fps, duration_ms, width, height FROM match_meta"
        ).fetchone()
    finally:
        conn.close()

    assert row == (24.0, 5000, 1280, 720)


def test_run_precompute_duration_ms_recovered_when_ffprobe_missing_duration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """If ffprobe returned duration_ms=0, run_precompute should recompute from frame count."""
    from backend import precompute

    # probe returns duration_ms=0 (missing from stream metadata)
    _monkeypatch_probe_and_iter(monkeypatch, 640, 480, 30.0, 30, duration_ms=0)

    corners_path = _write_corners_json(tmp_path)
    clip_path = tmp_path / "clip.mp4"
    clip_path.write_bytes(b"x")
    db_path = tmp_path / "db.duckdb"
    json_out = tmp_path / "out.json"

    precompute.run_precompute(
        clip_path=clip_path,
        corners_json_path=corners_path,
        match_id="utr_dur",
        player_a_name="A",
        player_b_name="B",
        db_path=db_path,
        match_data_json_path=json_out,
        pose_extractor=FakePoseExtractor(),
        device="cpu",
    )

    import duckdb
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        dur = conn.execute("SELECT duration_ms FROM match_meta").fetchone()[0]
    finally:
        conn.close()

    # 30 frames at 30fps → 1000 ms (reconstructed post-loop)
    assert dur == 1000


# ──────────────────────────── Reviewer-hardening regression tests ────────────────────────────


def test_probe_video_meta_raises_on_zero_fps(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Reviewer HIGH: ffprobe '0/0' must fail LOUDLY at the probe site, not
    cascade to an opaque ZeroDivisionError deep inside run_precompute.
    """
    from backend import precompute

    fake_stream = {
        "streams": [
            {"width": 1920, "height": 1080, "r_frame_rate": "0/0", "duration": "5.0"}
        ]
    }
    fake_result = SimpleNamespace(
        stdout=json.dumps(fake_stream), stderr="", returncode=0
    )
    monkeypatch.setattr("backend.precompute.subprocess.run", lambda *a, **k: fake_result)

    clip = tmp_path / "bad.mp4"
    clip.write_bytes(b"x")
    with pytest.raises(RuntimeError, match="non-positive fps"):
        precompute.probe_video_meta(clip)


def test_iter_frames_calls_proc_terminate_on_abandon(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Reviewer HIGH: when the frame iterator is abandoned mid-stream, proc.terminate()
    must fire before proc.wait() so ffmpeg doesn't hang 5 seconds per abandoned clip.
    """
    from backend import precompute

    W, H = 64, 48
    frame_size = W * H * 3
    # Popen returns a fake with stdout that ALWAYS has data (infinite stream) — we
    # abandon via `break` after the first frame so terminate() must interrupt the
    # otherwise-unbounded loop.
    terminate_mock = MagicMock()
    wait_mock = MagicMock()

    fake_stdout = MagicMock()
    fake_stdout.read = MagicMock(return_value=b"\x00" * frame_size)
    fake_stdout.close = MagicMock()

    fake_proc = MagicMock()
    fake_proc.stdout = fake_stdout
    fake_proc.terminate = terminate_mock
    fake_proc.wait = wait_mock

    monkeypatch.setattr(
        "backend.precompute.subprocess.Popen", lambda *a, **k: fake_proc
    )

    it = precompute.iter_frames_from_ffmpeg(tmp_path / "clip.mp4", W, H)
    # Consume one frame, then abandon
    first = next(it)
    assert first[0] == 0
    assert first[1].shape == (H, W, 3)
    # Trigger the generator's finally block by closing it early
    it.close()

    terminate_mock.assert_called_once()
    wait_mock.assert_called_once()


def test_iter_frames_uses_devnull_for_stderr(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Reviewer LOW: ffmpeg stderr must be DEVNULL to prevent kernel-buffer fill
    on long clips. Verify the Popen kwargs.
    """
    from backend import precompute

    captured_kwargs: dict = {}

    def _fake_popen(cmd, **kwargs):
        captured_kwargs.update(kwargs)
        fake_proc = MagicMock()
        fake_proc.stdout = MagicMock()
        fake_proc.stdout.read = MagicMock(return_value=b"")  # immediate EOF
        fake_proc.stdout.close = MagicMock()
        fake_proc.terminate = MagicMock()
        fake_proc.wait = MagicMock()
        return fake_proc

    monkeypatch.setattr("backend.precompute.subprocess.Popen", _fake_popen)

    it = precompute.iter_frames_from_ffmpeg(tmp_path / "clip.mp4", 64, 48)
    list(it)  # exhaust

    import subprocess as sp
    assert captured_kwargs.get("stderr") == sp.DEVNULL


def test_empty_gpu_cache_fires_on_cuda_too(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reviewer MEDIUM: the CLI exposes --device cuda, so cache-clearing must
    dispatch to torch.cuda.empty_cache, not just torch.mps.empty_cache.
    """
    import sys as _sys
    from types import ModuleType as _ModuleType

    fake_torch = _ModuleType("torch")
    fake_torch.cuda = SimpleNamespace(empty_cache=MagicMock())  # type: ignore[attr-defined]
    fake_torch.mps = SimpleNamespace(empty_cache=MagicMock())  # type: ignore[attr-defined]
    monkeypatch.setitem(_sys.modules, "torch", fake_torch)

    from backend import precompute
    precompute._empty_gpu_cache_if_due(100, "cuda")
    assert fake_torch.cuda.empty_cache.call_count == 1
    assert fake_torch.mps.empty_cache.call_count == 0


def test_writer_rejects_keypoints_with_wrong_length(tmp_path: Path) -> None:
    """Reviewer HIGH: BLOB reshape contract requires 17 keypoints. If a future
    YOLO model or a corrupted detection sneaks through Pydantic validation
    (e.g., via .model_construct bypassing checks), writer.flush() must raise
    a clear error rather than silently corrupt DuckDB blobs.

    Belt-and-suspenders check — Pydantic schema already enforces
    min_length=17/max_length=17 on PlayerDetection.keypoints_xyn. The
    write-time guard catches model_construct or similar validation bypasses.
    """
    from backend.db.schema import FrameKeypoints, PlayerDetection
    from backend.db.writer import DuckDBWriter

    bad_detection = PlayerDetection.model_construct(
        player="A",
        keypoints_xyn=[(0.5, 0.5)] * 15,   # 15 instead of 17 (bypass via model_construct)
        confidence=[0.9] * 15,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.95),
        feet_mid_m=(4.0, 12.0),
        fallback_mode="ankle",
    )
    bad_frame = FrameKeypoints.model_construct(
        t_ms=100, frame_idx=3, player_a=bad_detection, player_b=None
    )

    # NOT using `with DuckDBWriter(...)` context manager: __exit__ calls flush()
    # a second time, which would re-raise and confuse pytest.raises. Construct
    # manually, assert the raise, clear the queue, then close cleanly.
    writer = DuckDBWriter(tmp_path / "db.duckdb", match_id="m")
    try:
        writer.queue_keypoint_frame(bad_frame)
        with pytest.raises(ValueError, match="keypoint length mismatch"):
            writer.flush()
        writer._pending_keypoints.clear()  # clear so close() doesn't re-raise
    finally:
        writer.close()
