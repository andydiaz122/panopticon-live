"""Tests for backend/cv/signals/ritual_entropy.py — Lomb-Scargle spectral entropy delta of pre-serve wrist cadence.

Enforces USER-CORRECTION-012 (relative kinematics — `wrist_y - hip_y`),
USER-CORRECTION-014 (ambidextrous wrist selection — max-y among confident L/R),
USER-CORRECTION-015 (variance floor — drop when var < 1e-5),
USER-CORRECTION-017 (no CourtMapper — wrist is airborne; homography is fiction),
USER-CORRECTION-022 (fail-fast — `self.deps["match_id"]` must raise KeyError when missing).

The "delta" is relative to the player's match-opening baseline. First successful flush = baseline
(value=0.0). Each subsequent flush emits `entropy - baseline`.

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import math

import pytest

from backend.cv.signals.ritual_entropy import RitualEntropy
from backend.db.schema import FrameKeypoints, PlayerDetection, SignalSample

# ──────────────────────────── Frame builder ────────────────────────────


def _stub_confident_keypoints() -> tuple[list[tuple[float, float]], list[float]]:
    kpts = [(0.5, 0.5)] * 17
    conf = [0.9] * 17
    return kpts, conf


def build_frame(
    player: str,
    wrist_l_y: float,
    wrist_l_conf: float,
    wrist_r_y: float,
    wrist_r_conf: float,
    hip_l_y: float,
    hip_l_conf: float,
    hip_r_y: float,
    hip_r_conf: float,
    t_ms: int,
) -> FrameKeypoints:
    """Frame builder for ritual_entropy tests. Only needs wrist + hip (no shoulder)."""
    kpts, conf = _stub_confident_keypoints()
    kpts[9] = (0.5, wrist_l_y)
    conf[9] = wrist_l_conf
    kpts[10] = (0.5, wrist_r_y)
    conf[10] = wrist_r_conf
    kpts[11] = (0.5, hip_l_y)
    conf[11] = hip_l_conf
    kpts[12] = (0.5, hip_r_y)
    conf[12] = hip_r_conf

    det_target = PlayerDetection(
        player=player,  # type: ignore[arg-type]
        keypoints_xyn=kpts,
        confidence=conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.9),
        feet_mid_m=(4.0, 15.0),
        fallback_mode="ankle",
    )
    stub_kpts, stub_conf = _stub_confident_keypoints()
    other = "B" if player == "A" else "A"
    det_other = PlayerDetection(
        player=other,  # type: ignore[arg-type]
        keypoints_xyn=stub_kpts,
        confidence=stub_conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.3),
        feet_mid_m=(4.0, 8.0),
        fallback_mode="ankle",
    )
    if player == "A":
        pa, pb = det_target, det_other
    else:
        pa, pb = det_other, det_target
    return FrameKeypoints(t_ms=t_ms, frame_idx=t_ms // 33, player_a=pa, player_b=pb)


def _ingest_sequence(
    ext: RitualEntropy,
    target_state: str,
    frames: list[FrameKeypoints],
) -> None:
    for f in frames:
        ext.ingest(
            frame=f,
            target_state=target_state,  # type: ignore[arg-type]
            opponent_state="DEAD_TIME",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=f.t_ms,
        )


def _bounce_frames(
    *, freq_hz: float, num_frames: int, fps: int, amplitude: float = 0.1, offset: float = 0.3,
    start_t_ms: int = 100, confident: bool = True,
) -> list[FrameKeypoints]:
    """Build a bouncing-wrist sequence at a given frequency.

    wrist_rel_y = offset + amplitude * sin(2π f t)  (hip fixed at 0.5, so wrist_abs = 0.5 + wrist_rel)
    """
    frames = []
    dt_ms = int(1000 / fps)
    for i in range(num_frames):
        t_ms = start_t_ms + i * dt_ms
        t_s = t_ms / 1000.0
        rel = offset + amplitude * math.sin(2.0 * math.pi * freq_hz * t_s)
        wrist_abs = 0.5 + rel
        wrist_l_conf = 0.9 if confident else 0.1
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=wrist_abs, wrist_l_conf=wrist_l_conf,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                t_ms=t_ms,
            )
        )
    return frames


# ──────────────────────────── 1. Class metadata ────────────────────────────


def test_class_attributes_signal_name_and_required_state() -> None:
    assert RitualEntropy.signal_name == "ritual_entropy_delta"
    assert RitualEntropy.required_state == ("PRE_SERVE_RITUAL",)
    assert isinstance(RitualEntropy.required_state, tuple)


# ──────────────────────────── 2. Below MIN_SAMPLES → None ────────────────────────────


def test_below_min_samples_returns_none() -> None:
    """5 bouncing frames < MIN_SAMPLES (10) → flush None."""
    ext = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})
    frames = _bounce_frames(freq_hz=2.0, num_frames=5, fps=30)
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    assert ext.flush(t_ms=5000) is None


# ──────────────────────────── 3. Variance floor → None ────────────────────────────


def test_constant_relative_y_returns_none() -> None:
    """20 frames at constant wrist/hip position → var < 1e-5 → None."""
    ext = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    for i in range(20):
        t_ms = 100 + i * 33
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=0.8, wrist_l_conf=0.9,   # constant
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                t_ms=t_ms,
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    assert ext.flush(t_ms=3000) is None


# ──────────────────────────── 4. First flush → baseline, value = 0.0 ────────────────────────────


def test_first_successful_flush_emits_zero_and_sets_baseline() -> None:
    """First successful flush sets baseline; emitted SignalSample value is exactly 0.0."""
    ext = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})
    frames = _bounce_frames(freq_hz=2.0, num_frames=30, fps=30)
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    sample = ext.flush(t_ms=5000)
    assert isinstance(sample, SignalSample)
    assert sample.signal_name == "ritual_entropy_delta"
    assert sample.state == "PRE_SERVE_RITUAL"
    assert sample.player == "A"
    assert sample.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── 5. Second flush emits (entropy - baseline) ────────────────────────────


def test_second_flush_with_different_rhythm_emits_delta_from_baseline() -> None:
    """Second toss at different frequency → spectral entropy differs → value = entropy - baseline.

    Magnitude should be a real number; it can go positive or negative depending on rhythm regularity.
    """
    ext = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})

    # First toss: very clean 2 Hz bounce → concentrated spectrum → low entropy baseline
    frames1 = _bounce_frames(freq_hz=2.0, num_frames=30, fps=30, start_t_ms=100)
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames1)
    first = ext.flush(t_ms=2000)
    assert first is not None
    assert first.value == pytest.approx(0.0, abs=1e-12)

    # Second toss: multi-frequency mixture → more distributed spectrum → higher entropy
    frames2 = []
    for i in range(30):
        t_ms = 5000 + i * 33
        t_s = t_ms / 1000.0
        # Two distinct frequencies mixed — more distributed power
        rel = 0.3 + 0.05 * math.sin(2.0 * math.pi * 1.5 * t_s) + 0.05 * math.sin(2.0 * math.pi * 3.5 * t_s)
        wrist_abs = 0.5 + rel
        frames2.append(
            build_frame(
                player="A",
                wrist_l_y=wrist_abs, wrist_l_conf=0.9,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                t_ms=t_ms,
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames2)
    second = ext.flush(t_ms=7000)
    assert second is not None
    # Delta is a real, finite number; magnitude bounded (entropy fits within log(N_freqs) ≈ log(100) ≈ 4.6)
    assert second.value is not None
    assert math.isfinite(second.value)
    assert abs(second.value) < 10.0


# ──────────────────────────── 6. Non-PSR states ignored ────────────────────────────


def test_active_rally_state_is_ignored() -> None:
    """ACTIVE_RALLY ticks do not accumulate; flush None."""
    ext = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})
    frames = _bounce_frames(freq_hz=2.0, num_frames=30, fps=30)
    _ingest_sequence(ext, "ACTIVE_RALLY", frames)
    assert ext.flush(t_ms=5000) is None


def test_dead_time_state_is_ignored() -> None:
    ext = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})
    frames = _bounce_frames(freq_hz=2.0, num_frames=30, fps=30)
    _ingest_sequence(ext, "DEAD_TIME", frames)
    assert ext.flush(t_ms=5000) is None


# ──────────────────────────── 7. Occlusion (NaNs) filtered before lombscargle ────────────────────────────


def test_occlusion_nans_are_filtered_not_crashed() -> None:
    """Mix confident + occluded frames — NaNs must be filtered; lombscargle must not crash."""
    ext = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    for i in range(30):
        t_ms = 100 + i * 33
        t_s = t_ms / 1000.0
        rel = 0.3 + 0.1 * math.sin(2.0 * math.pi * 2.0 * t_s)
        wrist_abs = 0.5 + rel
        # Every 3rd frame has low wrist conf → NaN
        wrist_conf = 0.9 if i % 3 != 0 else 0.1
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=wrist_abs, wrist_l_conf=wrist_conf,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                t_ms=t_ms,
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    # Should not raise, and with 20 finite samples (out of 30), should produce a first baseline (0.0)
    sample = ext.flush(t_ms=5000)
    assert sample is not None
    assert sample.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── 8. After reset() baseline resets → next flush → 0.0 again ────────────────────────────


def test_reset_clears_baseline_so_next_flush_is_zero_again() -> None:
    """reset() wipes baseline; the next successful flush re-emits 0.0 (fresh baseline)."""
    ext = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})
    frames = _bounce_frames(freq_hz=2.0, num_frames=30, fps=30, start_t_ms=100)
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    first = ext.flush(t_ms=5000)
    assert first is not None
    assert first.value == pytest.approx(0.0, abs=1e-12)

    ext.reset()

    frames2 = _bounce_frames(freq_hz=2.0, num_frames=30, fps=30, start_t_ms=6000)
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames2)
    second = ext.flush(t_ms=10000)
    assert second is not None
    assert second.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── 9. Fail-fast match_id missing ────────────────────────────


def test_missing_match_id_raises_keyerror_on_flush() -> None:
    """Missing match_id in deps → flush raises KeyError with 'match_id' in message."""
    ext = RitualEntropy(target_player="A", dependencies={})
    frames = _bounce_frames(freq_hz=2.0, num_frames=30, fps=30)
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    with pytest.raises(KeyError, match="match_id"):
        ext.flush(t_ms=5000)


# ──────────────────────────── 10. Target/opponent symmetry ────────────────────────────


def test_two_instances_for_a_and_b_accumulate_independently() -> None:
    """A and B maintain independent buffers and baselines."""
    ext_a = RitualEntropy(target_player="A", dependencies={"match_id": "m1"})
    ext_b = RitualEntropy(target_player="B", dependencies={"match_id": "m1"})

    # Feed only A valid bouncing frames; B sees the same frame (target=A, so player_b stub).
    frames = _bounce_frames(freq_hz=2.0, num_frames=30, fps=30)
    for f in frames:
        ext_a.ingest(
            frame=f,
            target_state="PRE_SERVE_RITUAL",
            opponent_state="PRE_SERVE_RITUAL",
            target_kalman=(0.0, 0.0, 42.0, 42.0),  # distractor — ritual entropy must ignore
            opponent_kalman=(0.0, 0.0, 84.0, 84.0),
            t_ms=f.t_ms,
        )
        ext_b.ingest(
            frame=f,
            target_state="PRE_SERVE_RITUAL",
            opponent_state="PRE_SERVE_RITUAL",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=f.t_ms,
        )

    sample_a = ext_a.flush(t_ms=5000)
    sample_b = ext_b.flush(t_ms=5000)
    # A has a valid bouncing signal → baseline = 0.0
    assert sample_a is not None
    assert sample_a.player == "A"
    assert sample_a.value == pytest.approx(0.0, abs=1e-12)
    # B's frames have wrist/hip both at 0.5 (stub constant) → var < 1e-5 → None
    assert sample_b is None
