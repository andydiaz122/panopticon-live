"""Day-0 validation: run YOLO11m-Pose on a real UTR tennis clip, dump keypoints,
and produce a 3-line verdict on whether the pipeline is viable.

Zero-Disk ingestion: reads BGR24 frames from ffmpeg stdout via a piped subprocess.
MPS-safe: @torch.inference_mode(), torch.mps.empty_cache() every 50 frames, imgsz=1280, conf=0.001.

Usage:
    python -m scripts.probe_clip \\
        --clip /abs/path/to/utr_match_01_segment_a.mp4 \\
        --out data/probe_out.parquet \\
        --max-frames 1800   # 60s at 30 FPS

Outputs:
    - Parquet of per-5th-frame detections
    - Memory-sample CSV (for slope-based leak detection)
    - stdout summary + Go/No-Go verdict
"""

from __future__ import annotations

import argparse
import json
import subprocess as sp  # noqa: N813
import sys
import time
from pathlib import Path

import numpy as np
import psutil
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.config import resolve_device  # noqa: E402


FRAME_SHAPE = (1080, 1920, 3)  # H, W, C (BGR24)
FRAME_BYTES = 1080 * 1920 * 3


# ──────────────────── ffmpeg stdout piping (Zero-Disk) ────────────────────


def open_ffmpeg_pipe(clip_path: str) -> sp.Popen:
    """Launch ffmpeg as a subprocess, streaming BGR24 rawvideo to stdout."""
    cmd = [
        "ffmpeg",
        "-loglevel", "error",
        "-i", clip_path,
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-",
    ]
    return sp.Popen(
        cmd,
        stdout=sp.PIPE,
        stderr=sp.DEVNULL,
        bufsize=FRAME_BYTES * 4,
    )


def iter_frames(clip_path: str, max_frames: int | None):
    """Generator yielding BGR24 frames from an ffmpeg pipe."""
    proc = open_ffmpeg_pipe(clip_path)
    assert proc.stdout is not None
    count = 0
    try:
        while True:
            buf = proc.stdout.read(FRAME_BYTES)
            if len(buf) < FRAME_BYTES:
                break
            frame = np.frombuffer(buf, dtype=np.uint8).reshape(FRAME_SHAPE)
            yield frame
            count += 1
            if max_frames is not None and count >= max_frames:
                break
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5.0)
        except sp.TimeoutExpired:
            proc.kill()


# ──────────────────── YOLO inference with MPS safeguards ────────────────────


class PoseProber:
    """Minimal YOLO11m-Pose wrapper with MPS safeguards for Day-0 probing."""

    def __init__(self, weights: str, device: str) -> None:
        from ultralytics import YOLO

        self.device = device
        self.model = YOLO(weights)
        self._frame_count = 0

    @torch.inference_mode()
    def infer(self, frame_bgr: np.ndarray) -> list[dict]:
        results = self.model(
            frame_bgr,
            device=self.device,
            conf=0.001,
            imgsz=1280,
            verbose=False,
        )

        self._frame_count += 1
        if self._frame_count % 50 == 0 and self.device == "mps":
            torch.mps.empty_cache()

        detections: list[dict] = []
        for r in results:
            if r.keypoints is None or r.keypoints.xyn is None:
                continue
            xyn_batch = r.keypoints.xyn.cpu().numpy()  # (N, 17, 2)
            conf_batch = (
                r.keypoints.conf.cpu().numpy()
                if r.keypoints.conf is not None
                else np.ones((xyn_batch.shape[0], 17), dtype=np.float32)
            )
            for i in range(xyn_batch.shape[0]):
                detections.append(
                    {
                        "player_idx": int(i),
                        "keypoints_xyn": xyn_batch[i].tolist(),
                        "confidence": conf_batch[i].tolist(),
                    }
                )
        return detections


# ──────────────────── Memory profiling ────────────────────


def sample_memory(proc: psutil.Process) -> tuple[int, int]:
    """Return (rss_bytes, mps_allocated_bytes)."""
    rss = proc.memory_info().rss
    mps_alloc = 0
    try:
        mps_alloc = int(torch.mps.current_allocated_memory())
    except Exception:
        pass
    return rss, mps_alloc


# ──────────────────── Main ────────────────────


def run(clip_path: str, out_path: str, weights: str, max_frames: int) -> int:
    device = resolve_device()
    print(f"[probe] device={device}  weights={weights}  max_frames={max_frames}")
    print(f"[probe] clip={clip_path}")

    prober = PoseProber(weights=weights, device=device)

    psproc = psutil.Process()
    memory_samples: list[tuple[int, int, int]] = []
    per_frame_records: list[dict] = []
    frames_with_detections = 0
    frames_with_two_players = 0
    total_frames = 0

    t0 = time.perf_counter()
    for frame in iter_frames(clip_path, max_frames=max_frames):
        dets = prober.infer(frame)
        total_frames += 1
        if dets:
            frames_with_detections += 1
        if len(dets) >= 2:
            frames_with_two_players += 1

        if total_frames % 5 == 0:
            per_frame_records.append(
                {
                    "frame_idx": total_frames,
                    "num_detections": len(dets),
                    "detections_json": json.dumps(dets),
                }
            )

        if total_frames % 50 == 0:
            rss, mps_alloc = sample_memory(psproc)
            memory_samples.append((total_frames, rss, mps_alloc))
            elapsed = time.perf_counter() - t0
            fps = total_frames / elapsed if elapsed > 0 else 0.0
            print(
                f"[probe] f={total_frames:>5}  "
                f"dets={len(dets):>2}  "
                f"fps={fps:>5.1f}  "
                f"rss={rss / 1e9:>4.2f}GB  "
                f"mps={mps_alloc / 1e9:>4.2f}GB"
            )

    elapsed = time.perf_counter() - t0
    avg_fps = total_frames / elapsed if elapsed > 0 else 0.0

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import polars as pl

        df = pl.DataFrame(per_frame_records)
        df.write_parquet(str(out))
        print(f"[probe] Wrote {len(per_frame_records)} frame records to {out}")
    except ImportError:
        out = out.with_suffix(".jsonl")
        with open(out, "w") as f:
            for rec in per_frame_records:
                f.write(json.dumps(rec) + "\n")
        print(f"[probe] polars unavailable; wrote JSONL to {out}")

    mem_out = out.with_suffix(".memory.csv")
    with open(mem_out, "w") as f:
        f.write("frame_idx,rss_bytes,mps_allocated_bytes\n")
        for frame_idx, rss, mps_alloc in memory_samples:
            f.write(f"{frame_idx},{rss},{mps_alloc}\n")

    # Linear regression on RSS to detect leak slope
    slope_kb_per_frame = 0.0
    if len(memory_samples) >= 3:
        xs = np.array([s[0] for s in memory_samples], dtype=float)
        rs = np.array([s[1] for s in memory_samples], dtype=float)
        if float(np.var(xs)) > 0:
            slope_kb_per_frame = float(np.polyfit(xs, rs, 1)[0] / 1024.0)

    detection_rate = frames_with_detections / total_frames if total_frames else 0.0
    two_player_rate = frames_with_two_players / total_frames if total_frames else 0.0

    print("\n" + "=" * 60)
    print("DAY-0 PROBE VERDICT")
    print("=" * 60)
    print(f"Total frames processed:       {total_frames}")
    print(f"Average warm FPS:             {avg_fps:.2f}")
    print(f"Frames with >=1 detection:    {frames_with_detections} ({detection_rate:.1%})")
    print(f"Frames with >=2 players:      {frames_with_two_players} ({two_player_rate:.1%})")
    print(f"Memory slope (KB/frame):      {slope_kb_per_frame:+.2f}")
    print(f"Memory samples -> {mem_out}")
    print(f"Keypoint records -> {out}")
    print()

    # Only POSITIVE memory slopes indicate leaks. Negative slopes mean memory freed,
    # which is fine (usually GC after buffer reshuffling).
    leak_concern = slope_kb_per_frame > 200.0

    go = (
        avg_fps >= 8.0
        and detection_rate >= 0.85
        and two_player_rate >= 0.50
        and not leak_concern
    )
    verdict = "GO - proceed with Phase 1" if go else "NO-GO - pivot to Alt Framing A"
    print(f"VERDICT: {verdict}")
    if leak_concern:
        print(f"  ^ memory slope {slope_kb_per_frame:+.1f} KB/frame exceeds 200 KB/frame (LEAK)")
    print("=" * 60)

    return 0 if go else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Day-0 YOLO probe on a real UTR clip.")
    parser.add_argument("--clip", required=True, help="Path to MP4 (trimmed ~60s segment)")
    parser.add_argument("--out", default="data/probe_out.parquet", help="Output path")
    parser.add_argument(
        "--weights",
        default="checkpoints/yolo11m-pose.pt",
        help="YOLO weights path (auto-downloads if missing)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=1800,
        help="Stop after N frames (1800 = 60s at 30 FPS)",
    )
    args = parser.parse_args()

    Path(args.weights).parent.mkdir(parents=True, exist_ok=True)
    return run(args.clip, args.out, args.weights, args.max_frames)


if __name__ == "__main__":
    sys.exit(main())
