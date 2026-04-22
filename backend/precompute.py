"""Master pre-compute CLI for PANOPTICON LIVE.

Canonical per-tick DAG (USER-CORRECTIONs 011, 013, 017, 018):
    ffmpeg stdout -> numpy frame
        -> YOLO11m-Pose (MPS, @torch.inference_mode, conf=0.001, imgsz=1280)
        -> dict[PlayerSide, PlayerDetection | None]   (pose.assign_players fires inside)
        -> PhysicalKalman2D.update(meters) per player (predict-only on None)
        -> build_frame_wrist_hip_inputs -> RollingBounceDetector.ingest_player_frame
        -> RollingBounceDetector.evaluate()
        -> MatchStateMachine.update(...)
        -> FeatureCompiler.tick(...)
    On EOF: FeatureCompiler.finalize(t_ms=last_t_ms)
    Flush DuckDB and export match_data.json (floats rounded via Pydantic serializers).

Hard constraints (USER-CORRECTION-017, CLAUDE.md):
    - Zero-Disk video: subprocess.Popen(ffmpeg, ..., stdout=PIPE) -> np.frombuffer
      (NEVER cv2.VideoCapture — caches to swap on macOS)
    - @torch.inference_mode() around the main loop
    - torch.mps.empty_cache() every 50 frames on 'mps' device
    - YOLO imgsz=1280, conf=0.001 (delegated to PoseExtractor defaults)

Testability:
    - probe_video_meta, iter_frames_from_ffmpeg, compute_clip_sha256 are module-level.
    - run_precompute accepts an injected pose_extractor for mocking.
    - No torch dependency at import time (imported lazily for MPS safeguards).
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import subprocess
import sys
from collections.abc import Iterator
from contextlib import nullcontext
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from backend.cv.compiler import FeatureCompiler, build_frame_wrist_hip_inputs
from backend.cv.homography import CourtMapper
from backend.cv.kalman import PhysicalKalman2D
from backend.cv.state_machine import MatchStateMachine
from backend.cv.temporal_signals import RollingBounceDetector
from backend.db.schema import (
    CornersNormalized,
    FrameKeypoints,
    MatchMeta,
    PlayerDetection,
    SignalSample,
    StateTransition,
)
from backend.db.writer import DuckDBWriter, dump_match_data_json

if TYPE_CHECKING:
    from backend.cv.pose import PoseExtractor


# ──────────────────────────── Video metadata ────────────────────────────


def probe_video_meta(clip_path: Path) -> tuple[int, int, float, int]:
    """Return (width, height, fps, duration_ms) for the clip via ffprobe.

    Parses r_frame_rate like "30000/1001" -> 29.97. If `duration` is absent
    from the stream (common for MKV / some WebM), returns duration_ms=0 so the
    caller can recompute from the emitted frame count.

    Raises RuntimeError if ffprobe is unavailable or returns invalid JSON.
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-of", "json",
        str(clip_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "ffprobe binary not found on PATH — install ffmpeg or add it to PATH"
        ) from exc

    if not result.stdout:
        raise RuntimeError(f"ffprobe returned no stdout for {clip_path}")

    try:
        payload = json.loads(result.stdout)
        stream = payload["streams"][0]
    except (json.JSONDecodeError, KeyError, IndexError) as exc:
        raise RuntimeError(f"ffprobe output could not be parsed: {result.stdout!r}") from exc

    width = int(stream["width"])
    height = int(stream["height"])

    # r_frame_rate is "num/den"
    raw_fps_str = str(stream["r_frame_rate"])
    num_s, _, den_s = raw_fps_str.partition("/")
    den = float(den_s) if den_s else 1.0
    fps = float(num_s) / den if den else float(num_s)

    # Reviewer HIGH: guard fps > 0 to avoid ZeroDivisionError deep inside run_precompute
    # with a confusing traceback. Fire the error at the probe site with the raw string.
    if fps <= 0.0:
        raise RuntimeError(
            f"ffprobe reported non-positive fps={fps!r} (raw r_frame_rate={raw_fps_str!r}) "
            f"for {clip_path}. Clip is likely corrupted or ffprobe returned '0/0'."
        )

    duration_str = stream.get("duration")
    duration_ms = int(float(duration_str) * 1000) if duration_str is not None else 0

    return width, height, fps, duration_ms


# ──────────────────────────── ffmpeg frame iterator (Zero-Disk) ────────────────────────────


def iter_frames_from_ffmpeg(
    clip_path: Path, width: int, height: int
) -> Iterator[tuple[int, np.ndarray]]:
    """Yield (frame_idx, frame_bgr) tuples from an ffmpeg stdout pipe.

    Zero-Disk policy (USER-CORRECTION-017): ffmpeg writes raw bgr24 to stdout;
    we read exactly width*height*3 bytes per frame and reshape to (H, W, 3) uint8.
    Never touches cv2.VideoCapture (which caches to macOS swap and destroys MPS
    unified memory).

    End of stream: when read() returns less than frame_size bytes, we stop
    WITHOUT yielding a partial frame.
    """
    frame_size = width * height * 3
    cmd = [
        "ffmpeg", "-nostdin", "-loglevel", "error",
        "-i", str(clip_path),
        "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-",
    ]
    # Reviewer LOW: stderr=PIPE risks kernel-buffer fill blocking ffmpeg on long clips;
    # drain to DEVNULL (ffmpeg is already `-loglevel error` so we don't need stderr).
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        frame_idx = 0
        stdout = proc.stdout
        if stdout is None:
            return
        while True:
            buf = stdout.read(frame_size)
            if buf is None or len(buf) < frame_size:
                break
            frame = np.frombuffer(buf, dtype=np.uint8).reshape(height, width, 3)
            yield frame_idx, frame
            frame_idx += 1
    finally:
        # Reviewer HIGH: terminate() before wait() so abandoned iterators (break mid-loop,
        # downstream exception) don't hang 5 seconds per occurrence. terminate() is a no-op
        # if the process already exited cleanly on EOF.
        with contextlib.suppress(Exception):
            if proc.stdout is not None:
                proc.stdout.close()
        with contextlib.suppress(Exception):
            proc.terminate()
        with contextlib.suppress(Exception):
            proc.wait(timeout=5)


# ──────────────────────────── Content hashing ────────────────────────────


def compute_clip_sha256(clip_path: Path) -> str:
    """Stream SHA256 of the file for MatchMeta (8MB chunks).

    Used to detect clip content drift between pre-compute runs (if the SHA
    changes, the pre-computed artifacts are stale).
    """
    h = hashlib.sha256()
    with open(clip_path, "rb") as f:
        while chunk := f.read(8 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


# ──────────────────────────── Inference-mode helpers ────────────────────────────


def _get_inference_mode_ctx() -> object:
    """Return torch.inference_mode() if torch is importable, else a no-op context.

    Keeps import cheap for CI tests that mock torch entirely.
    """
    try:
        import torch
        return torch.inference_mode()
    except ImportError:
        return nullcontext()


def _empty_gpu_cache_if_due(frame_idx: int, device: str) -> None:
    """Fire torch.<backend>.empty_cache() when frame_idx is a multiple of 50.

    Dispatches per device: mps -> torch.mps.empty_cache, cuda -> torch.cuda.empty_cache.
    Reviewer MEDIUM: CUDA code path was omitted — the CLI exposes --device cuda,
    so we must support it even though M4 Pro only uses MPS in the hackathon.

    Skipped when device is cpu / unsupported, or torch module is missing.
    Never raises.
    """
    if frame_idx <= 0 or frame_idx % 50 != 0:
        return
    if device not in ("mps", "cuda"):
        return
    try:
        import torch
    except ImportError:
        return
    # Some macOS versions lack empty_cache when unified memory is healthy —
    # non-fatal, don't crash pre-compute over it.
    with contextlib.suppress(Exception):
        if device == "mps":
            torch.mps.empty_cache()
        else:  # cuda
            torch.cuda.empty_cache()


# Backward-compat alias for existing tests that reference the old name.
_empty_mps_cache_if_due = _empty_gpu_cache_if_due


# ──────────────────────────── Frame wrapping ────────────────────────────


def _build_frame_from_detections(
    t_ms: int,
    frame_idx: int,
    detection_a: PlayerDetection | None,
    detection_b: PlayerDetection | None,
) -> FrameKeypoints:
    return FrameKeypoints(
        t_ms=t_ms,
        frame_idx=frame_idx,
        player_a=detection_a,
        player_b=detection_b,
    )


def _kalman_speed(state: tuple[float, float, float, float] | None) -> float | None:
    """Return hypot(vx, vy) or None when state is None."""
    if state is None:
        return None
    _, _, vx, vy = state
    return math.hypot(vx, vy)


# ──────────────────────────── Main pipeline ────────────────────────────


def run_precompute(
    clip_path: Path,
    corners_json_path: Path,
    match_id: str,
    player_a_name: str,
    player_b_name: str,
    db_path: Path,
    match_data_json_path: Path,
    pose_extractor: PoseExtractor | None = None,
    device: str = "mps",
) -> tuple[int, int]:
    """Run the full pre-compute pipeline on one clip.

    Returns (frames_processed, signals_emitted).

    If `pose_extractor` is None we lazily construct a real PoseExtractor with the
    default weights path. Tests inject a FakePoseExtractor to avoid YOLO weights.

    Pipeline order (per CLAUDE.md + docstring up top):
        probe → corners → init components → main loop (YOLO/Kalman/Bounce/State/Compile)
        → finalize compiler → dump JSON.
    """
    # 1. Probe video meta + corners (fail fast before opening DuckDB).
    width, height, fps, probed_duration_ms = probe_video_meta(clip_path)
    corners_text = corners_json_path.read_text()
    corners_data = json.loads(corners_text)
    corners = CornersNormalized(**corners_data)

    clip_sha = compute_clip_sha256(clip_path)

    # 2. Initialize pipeline components.
    court_mapper = CourtMapper(corners, width, height)
    dt = 1.0 / fps
    kalman_a = PhysicalKalman2D(dt=dt)
    kalman_b = PhysicalKalman2D(dt=dt)
    bounce_detector = RollingBounceDetector(fps=fps)
    state_machine = MatchStateMachine()
    deps = {"match_id": match_id, "court_mapper": court_mapper, "clip_fps": fps}
    compiler = FeatureCompiler(match_id=match_id, dependencies=deps)

    if pose_extractor is None:
        # Lazy import — tests should inject a FakePoseExtractor so we never reach here.
        from backend.cv.pose import PoseExtractor as _PoseExtractor
        pose_extractor = _PoseExtractor(
            weights="checkpoints/yolo11m-pose.pt",
            device=device,
            court_mapper=court_mapper,
        )

    # 3. JSON accumulators (the writer buffers the DuckDB side separately).
    all_keypoints: list[FrameKeypoints] = []
    all_signals: list[SignalSample] = []
    all_transitions: list[StateTransition] = []

    frames_processed = 0
    signals_emitted = 0
    last_t_ms = 0

    # 4. Provisional MatchMeta with the probed duration — we'll rewrite at the end
    #    if ffprobe lacked duration AND we processed frames.
    provisional_meta = MatchMeta(
        match_id=match_id,
        clip_sha256=clip_sha,
        clip_fps=fps,
        duration_ms=probed_duration_ms,
        width=width,
        height=height,
        player_a=player_a_name,
        player_b=player_b_name,
        court_corners_json=corners_text,
    )

    # 5. Main loop — wrap in torch.inference_mode() (or nullcontext when torch absent).
    with DuckDBWriter(db_path, match_id) as writer, _get_inference_mode_ctx():
        writer.write_match_meta(provisional_meta)

        for frame_idx, frame_bgr in iter_frames_from_ffmpeg(clip_path, width, height):
            t_ms = int(frame_idx * 1000.0 / fps)
            last_t_ms = t_ms

            # 5a. YOLO inference (PoseExtractor.infer already calls assign_players internally)
            players = pose_extractor.infer(frame_bgr)
            detection_a = players.get("A")
            detection_b = players.get("B")

            # 5b. Kalman: always call update() — update(None) is predict-only (docs),
            #     returning a valid (x, y, vx, vy) tuple.
            a_meas = detection_a.feet_mid_m if detection_a is not None else None
            b_meas = detection_b.feet_mid_m if detection_b is not None else None
            kalman_a_state = kalman_a.update(a_meas)
            kalman_b_state = kalman_b.update(b_meas)

            # 5c. Build FrameKeypoints wrapper (for DuckDB + JSON).
            frame_kp = _build_frame_from_detections(t_ms, frame_idx, detection_a, detection_b)
            all_keypoints.append(frame_kp)
            writer.queue_keypoint_frame(frame_kp)

            # 5d. Bounce detector (Stage 4.5, pre-state-machine, USER-CORRECTION-013).
            a_inputs = build_frame_wrist_hip_inputs(frame_kp, "A")
            b_inputs = build_frame_wrist_hip_inputs(frame_kp, "B")
            bounce_detector.ingest_player_frame("A", *a_inputs)
            bounce_detector.ingest_player_frame("B", *b_inputs)
            a_bounce, b_bounce = bounce_detector.evaluate()

            # 5e. State machine (USER-CORRECTION-009/010/011). Gate velocity on Kalman convergence.
            a_speed = _kalman_speed(kalman_a_state) if kalman_a.is_converged else None
            b_speed = _kalman_speed(kalman_b_state) if kalman_b.is_converged else None
            states = state_machine.update(a_speed, b_speed, a_bounce, b_bounce, t_ms)
            transitions = state_machine.drain_transitions()
            all_transitions.extend(transitions)

            # 5f. FeatureCompiler tick.
            samples = compiler.tick(
                frame=frame_kp,
                states=states,
                kalmans={"A": kalman_a_state, "B": kalman_b_state},
                t_ms=t_ms,
            )
            for s in samples:
                writer.queue_signal(s)
                all_signals.append(s)
                signals_emitted += 1

            frames_processed += 1
            _empty_mps_cache_if_due(frame_idx, device)

        # 6. Finalize — flush remaining extractor buffers.
        final_samples = compiler.finalize(t_ms=last_t_ms)
        for s in final_samples:
            writer.queue_signal(s)
            all_signals.append(s)
            signals_emitted += 1

        # 7. Reconcile duration if ffprobe returned 0 and we actually processed frames.
        final_meta = provisional_meta
        if probed_duration_ms == 0 and frames_processed > 0:
            recomputed_ms = int(frames_processed * 1000 / fps)
            final_meta = provisional_meta.model_copy(update={"duration_ms": recomputed_ms})
            writer.write_match_meta(final_meta)

    # 8. Export match_data.json — Pydantic nested composition propagates
    #    @field_serializer to every float (USER-CORRECTION-015 / PATTERN-030).
    dump_match_data_json(
        out_path=match_data_json_path,
        meta=final_meta,
        keypoints=all_keypoints,
        signals=all_signals,
        anomalies=[],       # Phase 2 populates
        coach_insights=[],  # Phase 2 populates
        hud_layouts=[],     # Phase 2 populates
        transitions=all_transitions,
    )

    return frames_processed, signals_emitted


# ──────────────────────────── CLI entry point ────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PANOPTICON LIVE pre-compute CLI")
    parser.add_argument("--clip", required=True, type=Path)
    parser.add_argument("--corners", required=True, type=Path)
    parser.add_argument("--match-id", required=True)
    parser.add_argument("--player-a", required=True)
    parser.add_argument("--player-b", required=True)
    parser.add_argument("--db", type=Path, default=Path("data/panopticon.duckdb"))
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("dashboard/public/match_data/match.json"),
    )
    parser.add_argument("--device", default="mps", choices=["mps", "cuda", "cpu"])
    args = parser.parse_args(argv)

    frames, signals = run_precompute(
        clip_path=args.clip,
        corners_json_path=args.corners,
        match_id=args.match_id,
        player_a_name=args.player_a,
        player_b_name=args.player_b,
        db_path=args.db,
        match_data_json_path=args.out_json,
        device=args.device,
    )
    print(f"processed {frames} frames -> {signals} signals")
    print(f"  DuckDB: {args.db}")
    print(f"  match_data.json: {args.out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
