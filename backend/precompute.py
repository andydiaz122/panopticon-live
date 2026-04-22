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
import asyncio
import contextlib
import hashlib
import json
import math
import os
import subprocess
import sys
from collections.abc import Coroutine, Iterator
from contextlib import nullcontext
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from backend.agents.haiku_narrator import generate_narrator_beat
from backend.agents.hud_designer import generate_hud_layout
from backend.agents.opus_coach import AnthropicClientLike, generate_coach_insight
from backend.agents.tools import ToolContext
from backend.cv.compiler import FeatureCompiler, build_frame_wrist_hip_inputs
from backend.cv.homography import CourtMapper
from backend.cv.kalman import PhysicalKalman2D
from backend.cv.state_machine import MatchStateMachine
from backend.cv.temporal_signals import RollingBounceDetector
from backend.db.schema import (
    DOUBLES_COURT_WIDTH_M,
    CoachInsight,
    CornersNormalized,
    FrameKeypoints,
    HUDLayoutSpec,
    MatchMeta,
    NarratorBeat,
    PlayerDetection,
    SignalSample,
    StateTransition,
)
from backend.db.writer import DuckDBWriter, dump_match_data_json

if TYPE_CHECKING:
    from backend.cv.pose import PoseExtractor

# ──────────────────────────── Phase 2 agent defaults ────────────────────────────

DEFAULT_COACH_CAP: int = 5
"""Hard cap on Coach insights per clip. Prevents API-spend blowouts on long clips."""

DEFAULT_DESIGN_CAP: int = 10
"""Hard cap on HUD-layout generations per clip."""

DEFAULT_BEAT_PERIOD_SEC: float = 10.0
"""Narrator beat cadence. 10s means ~6 beats/minute — balanced cost vs coverage."""

DEFAULT_BEAT_CAP: int = 20
"""Hard cap on Narrator beats per clip (reviewer HIGH-2). Mirrors coach_cap/design_cap.

Without this, a 15-minute clip at 10s cadence fires 90 concurrent Haiku calls via
asyncio.gather, tripping Anthropic's rate limiter — output becomes mostly [narrator_error]
beats and the demo looks broken. 20 beats covers ~3 minutes at 10s, which matches the
demo-video budget."""

DEFAULT_WARMUP_MS: int = 10_000
"""Skip ACTIVE_RALLY-exit / PRE_SERVE_RITUAL-entry transitions that fire in the first
10s of a clip — the CV pipeline emits warm-up noise during Kalman convergence +
RollingBounceDetector buffer fill. Without this filter, `coach_cap` and `design_cap`
are consumed by spurious early transitions and the ACTUAL rally later in the clip
gets zero Coach/Designer coverage — the "demo killer" GOTCHA-015 scenario.

10s is conservative; most broadcast clips open with ≥3-5s of crowd/setup before play
starts, plus we need to let the FeatureCompiler's state machine settle."""

DEFAULT_MIN_TRIGGER_GAP_MS: int = 2_000
"""Companion to DEFAULT_WARMUP_MS: dedupe rapid-fire triggers by requiring ≥2s between
consecutive kept triggers for the SAME player. Observed in the Apr 22 smoke run:
post-warmup noise bursts at 150ms cadence still exist (PRE_SERVE_RITUAL↔ACTIVE_RALLY
flapping via match_coupling). Without this, the coach_cap is consumed by a
11.5-13s flicker instead of spreading across real rallies at 20s, 40s, etc.
2s = roughly one natural rally cadence (serve-to-next-serve)."""


def _dedupe_close_triggers(
    triggers: list[StateTransition], min_gap_ms: int,
) -> list[StateTransition]:
    """Drop each trigger that is within `min_gap_ms` of the previously kept trigger
    for the SAME player. Preserves chronological order. O(n) single pass."""
    out: list[StateTransition] = []
    last_t_by_player: dict[str, int] = {}
    for tr in triggers:
        prev = last_t_by_player.get(tr.player)
        if prev is None or tr.timestamp_ms - prev >= min_gap_ms:
            out.append(tr)
            last_t_by_player[tr.player] = tr.timestamp_ms
    return out


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


def load_corners_json(corners_json_path: Path) -> tuple[str, CornersNormalized]:
    """Load a corners JSON emitted by tools/court_annotator.html.

    Accepts BOTH shapes (tested 2026-04-22 after annotator sent a wrapper):
      1. Wrapped (what the annotator actually emits):
         {"clip": ..., "annotated_at": ..., "corners": {"top_left": [...], ...}, "notes": ...}
      2. Bare (manual JSON hand-edits, back-compat):
         {"top_left": [...], "top_right": [...], "bottom_right": [...], "bottom_left": [...]}

    Returns (raw_text, CornersNormalized). The raw text is preserved for MatchMeta
    provenance so the full annotation metadata travels with the pre-computed artifact.
    """
    raw_text = corners_json_path.read_text()
    data = json.loads(raw_text)
    # Unwrap if the annotator's wrapper shape is present.
    inner = data.get("corners", data) if isinstance(data, dict) else data
    return raw_text, CornersNormalized(**inner)


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


# ──────────────────────────── Phase 2 agent-phase helpers ────────────────────────────


def _build_state_summary(
    signals: list[SignalSample], transitions: list[StateTransition], t_ms: int,
    window_sec: float = 15.0,
) -> str:
    """Natural-language summary of recent signals + transitions for Designer context.

    Designer doesn't query tools; this string is the sole context it receives. Keep
    under ~100 words — Designer's max_tokens budget is low.
    """
    lo = t_ms - int(window_sec * 1000)
    recent_signals = [s for s in signals if lo <= s.timestamp_ms <= t_ms and s.value is not None]
    recent_transitions = [t for t in transitions if lo <= t.timestamp_ms <= t_ms]

    lines: list[str] = [f"Window: last {window_sec:.0f}s up to t={t_ms}ms"]
    if recent_transitions:
        last_t = recent_transitions[-1]
        lines.append(
            f"Latest transition: player {last_t.player} "
            f"{last_t.from_state} -> {last_t.to_state} ({last_t.reason})"
        )
    # Most recent sample per player+signal
    by_key: dict[tuple[str, str], SignalSample] = {}
    for s in recent_signals:
        by_key[(s.player, s.signal_name)] = s
    if by_key:
        lines.append("Recent signals:")
        for (player, name), s in sorted(by_key.items()):
            lines.append(f"  {player} {name}: {s.value} (state={s.state})")
    else:
        lines.append("No recent signals in window.")
    return "\n".join(lines)


def _build_signal_snapshot(signals: list[SignalSample], t_ms: int, window_sec: float = 3.0) -> str:
    """Short snapshot for Narrator — what's happening RIGHT NOW."""
    lo = t_ms - int(window_sec * 1000)
    recent = [s for s in signals if lo <= s.timestamp_ms <= t_ms and s.value is not None]
    if not recent:
        return f"Quiet moment at t={t_ms}ms — no recent signals."
    most_recent = max(recent, key=lambda s: s.timestamp_ms)
    return (
        f"t={t_ms}ms. Player {most_recent.player} in {most_recent.state}. "
        f"Latest {most_recent.signal_name}={most_recent.value}."
    )


async def _safe_gather(
    tasks: list[Coroutine[Any, Any, Any]],
) -> list[Any]:
    """asyncio.gather that returns [] on empty task list (gather() on zero args would also work but is noisier)."""
    if not tasks:
        return []
    return list(await asyncio.gather(*tasks))


async def run_agent_phase(
    client: AnthropicClientLike,
    *,
    match_id: str,
    player_a_name: str,
    player_b_name: str,
    signals: list[SignalSample],
    transitions: list[StateTransition],
    duration_ms: int,
    coach_cap: int = DEFAULT_COACH_CAP,
    design_cap: int = DEFAULT_DESIGN_CAP,
    beat_period_sec: float = DEFAULT_BEAT_PERIOD_SEC,
    beat_cap: int = DEFAULT_BEAT_CAP,
    warmup_ms: int = DEFAULT_WARMUP_MS,
    min_trigger_gap_ms: int = DEFAULT_MIN_TRIGGER_GAP_MS,
) -> tuple[list[CoachInsight], list[HUDLayoutSpec], list[NarratorBeat]]:
    """Run Coach + Designer + Narrator agents concurrently against pre-computed signals.

    Triggers:
      Coach     → one insight per ACTIVE_RALLY-exit transition, up to coach_cap
      Designer  → one layout per PRE_SERVE_RITUAL-entry transition, up to design_cap
      Narrator  → one beat every beat_period_sec seconds (skipped if beat_period_sec<=0)

    Returns (coach_insights, hud_layouts, narrator_beats) — each list in call order.
    All three agents already swallow their own errors into structured fallback records
    so this function cannot raise from model/API problems.
    """
    ctx = ToolContext(match_id=match_id, signals=signals, transitions=transitions)

    # Coach: rally-end moments — GOTCHA-015 fix: skip warm-up noise (t <= warmup_ms) so the
    # cap isn't consumed by Kalman-convergence / bounce-buffer-fill artifacts in the first
    # ~10s of the clip. Then dedupe rapid-fire triggers (min_trigger_gap_ms) so a 150ms-cadence
    # noise burst post-warmup can't still consume the cap. Without dedupe, observed 5 coaches
    # all firing in an 1.2s window in the Apr 22 smoke run.
    coach_candidates = [
        t for t in transitions
        if t.from_state == "ACTIVE_RALLY" and t.timestamp_ms > warmup_ms
    ]
    coach_triggers = _dedupe_close_triggers(coach_candidates, min_trigger_gap_ms)[:coach_cap]
    coach_tasks = [
        generate_coach_insight(
            client, ctx,
            t_ms=tr.timestamp_ms, match_id=match_id,
            player_a_name=player_a_name, player_b_name=player_b_name,
            insight_id=f"coach_{tr.timestamp_ms}_{tr.player}",
            trigger_description=(
                f"Player {tr.player} exits ACTIVE_RALLY at t={tr.timestamp_ms}ms "
                f"(reason={tr.reason}). Analyze the rally just ended."
            ),
        )
        for tr in coach_triggers
    ]

    # Designer: new-point moments — same warm-up + dedupe as Coach.
    design_candidates = [
        t for t in transitions
        if t.to_state == "PRE_SERVE_RITUAL" and t.timestamp_ms > warmup_ms
    ]
    design_triggers = _dedupe_close_triggers(design_candidates, min_trigger_gap_ms)[:design_cap]
    design_tasks = [
        generate_hud_layout(
            client,
            t_ms=tr.timestamp_ms,
            player_a_name=player_a_name, player_b_name=player_b_name,
            trigger_description=f"Player {tr.player} enters PRE_SERVE_RITUAL ({tr.reason})",
            state_summary=_build_state_summary(signals, transitions, tr.timestamp_ms),
        )
        for tr in design_triggers
    ]

    # Narrator: regular beat cadence (reviewer HIGH-2 — cap at beat_cap to avoid rate-limiter blowout)
    beat_tasks: list[Coroutine[Any, Any, NarratorBeat]] = []
    if beat_period_sec > 0 and duration_ms > 0:
        beat_period_ms = int(beat_period_sec * 1000)
        beat_timestamps = list(range(0, duration_ms, beat_period_ms))[:beat_cap]
        for t_ms in beat_timestamps:
            beat_tasks.append(
                generate_narrator_beat(
                    client,
                    t_ms=t_ms, match_id=match_id,
                    player_a_name=player_a_name, player_b_name=player_b_name,
                    signal_snapshot=_build_signal_snapshot(signals, t_ms),
                ),
            )

    coach_results, design_results, beat_results = await asyncio.gather(
        _safe_gather(coach_tasks),
        _safe_gather(design_tasks),
        _safe_gather(beat_tasks),
    )
    return coach_results, design_results, beat_results


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
    *,
    court_width_m: float | None = None,
    anthropic_client: AnthropicClientLike | None = None,
    coach_cap: int = DEFAULT_COACH_CAP,
    design_cap: int = DEFAULT_DESIGN_CAP,
    beat_period_sec: float = DEFAULT_BEAT_PERIOD_SEC,
    beat_cap: int = DEFAULT_BEAT_CAP,
    warmup_ms: int = DEFAULT_WARMUP_MS,
    min_trigger_gap_ms: int = DEFAULT_MIN_TRIGGER_GAP_MS,
) -> tuple[int, int]:
    """Run the full pre-compute pipeline on one clip.

    Returns (frames_processed, signals_emitted).

    Phase 2 agent integration: if `anthropic_client` is provided, runs Coach/Designer/
    Narrator agents AFTER the main CV loop and writes their outputs into both DuckDB
    and match_data.json. When None (or no ANTHROPIC_API_KEY in env, main() checks),
    the agent phase is skipped entirely. This lets tests mock the whole agent layer
    without touching the real SDK.

    If `pose_extractor` is None we lazily construct a real PoseExtractor with the
    default weights path. Tests inject a FakePoseExtractor to avoid YOLO weights.

    Pipeline order (per CLAUDE.md + docstring up top):
        probe → corners → init components → main loop (YOLO/Kalman/Bounce/State/Compile)
        → finalize compiler → dump JSON.
    """
    # 1. Probe video meta + corners (fail fast before opening DuckDB).
    width, height, fps, probed_duration_ms = probe_video_meta(clip_path)
    # Use load_corners_json — handles BOTH the annotator's wrapper shape AND bare shape.
    corners_text, corners = load_corners_json(corners_json_path)

    clip_sha = compute_clip_sha256(clip_path)

    # 2. Initialize pipeline components. court_width_m=None defaults to singles (8.23m);
    #    pass DOUBLES_COURT_WIDTH_M (10.97m) when the annotation traces the outside of
    #    the doubles alleys instead of the singles sidelines.
    court_mapper = CourtMapper(corners, width, height, court_width_m=court_width_m)
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

        # 8. Phase 2 agent phase (Coach + Designer + Narrator), if a client was provided.
        #    Writer is still open — agent outputs get queued into DuckDB here.
        all_coach_insights: list[CoachInsight] = []
        all_hud_layouts: list[HUDLayoutSpec] = []
        all_narrator_beats: list[NarratorBeat] = []
        if anthropic_client is not None:
            effective_duration = final_meta.duration_ms or last_t_ms
            # Reviewer MEDIUM-3: asyncio.run() is correct here — run_precompute is called from
            # sync contexts (CLI, pytest). If this ever moves into an async FastAPI endpoint,
            # replace with `await run_agent_phase(...)` and make run_precompute async.
            coach_list, design_list, beat_list = asyncio.run(
                run_agent_phase(
                    anthropic_client,
                    match_id=match_id,
                    player_a_name=player_a_name,
                    player_b_name=player_b_name,
                    signals=all_signals,
                    transitions=all_transitions,
                    duration_ms=effective_duration,
                    coach_cap=coach_cap,
                    design_cap=design_cap,
                    beat_period_sec=beat_period_sec,
                    beat_cap=beat_cap,
                    warmup_ms=warmup_ms,
                    min_trigger_gap_ms=min_trigger_gap_ms,
                ),
            )
            all_coach_insights = list(coach_list)
            all_hud_layouts = list(design_list)
            all_narrator_beats = list(beat_list)
            for ci in all_coach_insights:
                writer.queue_coach_insight(ci)
            for nb in all_narrator_beats:
                writer.queue_narrator_beat(nb)
            # HUDLayoutSpec intentionally JSON-only (matches existing pattern, no DDL table).

    # 9. Export match_data.json — Pydantic nested composition propagates
    #    @field_serializer to every float (USER-CORRECTION-015 / PATTERN-030).
    dump_match_data_json(
        out_path=match_data_json_path,
        meta=final_meta,
        keypoints=all_keypoints,
        signals=all_signals,
        anomalies=[],  # Anomaly detection is a future Phase (signals -> anomalies is not yet wired)
        coach_insights=all_coach_insights,
        hud_layouts=all_hud_layouts,
        transitions=all_transitions,
        narrator_beats=all_narrator_beats,
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
    parser.add_argument(
        "--doubles-corners", action="store_true",
        help=(
            "Interpret the corner annotation as tracing the outside of the doubles alleys "
            "(10.97m wide canonical court) instead of the singles sidelines (8.23m). "
            "Required when court_annotator.html is clicked on the outermost court lines."
        ),
    )
    # Phase 2 agent flags
    parser.add_argument(
        "--skip-agents", action="store_true",
        help="Skip Phase 2 Opus/Haiku agents entirely (no API calls, no commentary)",
    )
    parser.add_argument("--coach-cap", type=int, default=DEFAULT_COACH_CAP)
    parser.add_argument("--design-cap", type=int, default=DEFAULT_DESIGN_CAP)
    parser.add_argument("--beat-cap", type=int, default=DEFAULT_BEAT_CAP,
                        help="Hard cap on Narrator beats (rate-limiter safety)")
    parser.add_argument(
        "--beat-period-sec", type=float, default=DEFAULT_BEAT_PERIOD_SEC,
        help="Narrator cadence; 0 disables Narrator",
    )
    parser.add_argument(
        "--warmup-ms", type=int, default=DEFAULT_WARMUP_MS,
        help=(
            "Skip state transitions in the first N ms when selecting Coach/Designer "
            "triggers (default 10000). Prevents cap exhaustion on CV warm-up noise. "
            "See GOTCHA-015."
        ),
    )
    parser.add_argument(
        "--min-trigger-gap-ms", type=int, default=DEFAULT_MIN_TRIGGER_GAP_MS,
        help=(
            "Minimum ms between consecutive Coach/Designer triggers for the same player "
            "(default 2000). Dedupes rapid-fire CV transitions so the cap spreads across "
            "real rallies instead of a single noise burst. See GOTCHA-015."
        ),
    )
    args = parser.parse_args(argv)

    # Build Anthropic client lazily — only if agents are enabled AND key is present
    anthropic_client: AnthropicClientLike | None = None
    if not args.skip_agents:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("WARN: ANTHROPIC_API_KEY not set — skipping Phase 2 agents", file=sys.stderr)
        else:
            from anthropic import AsyncAnthropic  # lazy — avoids import cost when --skip-agents
            anthropic_client = AsyncAnthropic(api_key=api_key)

    frames, signals = run_precompute(
        clip_path=args.clip,
        corners_json_path=args.corners,
        match_id=args.match_id,
        player_a_name=args.player_a,
        player_b_name=args.player_b,
        db_path=args.db,
        match_data_json_path=args.out_json,
        device=args.device,
        court_width_m=(DOUBLES_COURT_WIDTH_M if args.doubles_corners else None),
        anthropic_client=anthropic_client,
        coach_cap=args.coach_cap,
        design_cap=args.design_cap,
        beat_period_sec=args.beat_period_sec,
        beat_cap=args.beat_cap,
        warmup_ms=args.warmup_ms,
        min_trigger_gap_ms=args.min_trigger_gap_ms,
    )
    print(f"processed {frames} frames -> {signals} signals")
    print(f"  DuckDB: {args.db}")
    print(f"  match_data.json: {args.out_json}")
    if anthropic_client is None:
        print("  Phase 2 agents: SKIPPED")
    else:
        print("  Phase 2 agents: invoked (Coach/Designer/Narrator wrote to DuckDB + JSON)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
