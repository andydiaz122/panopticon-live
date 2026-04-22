"""Tests for backend/cv/signals/crouch_depth.py — angular crouch-depth degradation in degrees.

Enforces USER-CORRECTION-017 (no CourtMapper — angular degradation is camera-invariant
by construction via torso-scalar normalization and arctangent conversion) and
USER-CORRECTION-022 (fail-fast — `self.deps["match_id"]` must raise KeyError when missing).

Physics contract:
- Per-frame: normalized_crouch = (ankle_y - hip_y) / (hip_y - shoulder_y)
  (both scalars positive in image coords: ankles below hips, shoulders above hips).
- Buffer contains np.nan when any required keypoint has confidence < 0.3, or when
  the torso scalar collapses (< 1e-5).
- First successful flush SETS the baseline, emits value = 0.0.
- Subsequent flush: degradation_deg = math.degrees(math.atan(baseline - current)).
  Positive = less crouch = more upright = fatigue signature.

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from backend.cv.signals.crouch_depth import CrouchDepth
from backend.db.schema import FrameKeypoints, PlayerDetection, SignalSample

# ──────────────────────────── Frame builder ────────────────────────────


def _stub_confident_keypoints() -> tuple[list[tuple[float, float]], list[float]]:
    """17 keypoints with high confidence — used for indices this test doesn't care about."""
    kpts = [(0.5, 0.5)] * 17
    conf = [0.9] * 17
    return kpts, conf


def build_crouch_frame(
    player: str,
    hip_y: float,
    hip_conf: float,
    knee_y: float,
    knee_conf: float,
    ankle_y: float,
    ankle_conf: float,
    shoulder_y: float,
    shoulder_conf: float,
    t_ms: int,
) -> FrameKeypoints:
    """Build a FrameKeypoints for one target player with symmetric L+R hip/knee/ankle/shoulder.

    Sets both left and right joint copies to the same y with the given confidence, so
    the mean of L+R equals the provided scalar — matches how the extractor reads them.

    Affected COCO indices: 5 (LShoulder), 6 (RShoulder), 11 (LHip), 12 (RHip),
    13 (LKnee), 14 (RKnee), 15 (LAnkle), 16 (RAnkle). Other indices remain at (0.5, 0.5) conf 0.9.
    """
    kpts, conf = _stub_confident_keypoints()
    # shoulders
    kpts[5] = (0.5, shoulder_y)
    conf[5] = shoulder_conf
    kpts[6] = (0.5, shoulder_y)
    conf[6] = shoulder_conf
    # hips
    kpts[11] = (0.5, hip_y)
    conf[11] = hip_conf
    kpts[12] = (0.5, hip_y)
    conf[12] = hip_conf
    # knees (not used by this signal, but kept for future parity)
    kpts[13] = (0.5, knee_y)
    conf[13] = knee_conf
    kpts[14] = (0.5, knee_y)
    conf[14] = knee_conf
    # ankles
    kpts[15] = (0.5, ankle_y)
    conf[15] = ankle_conf
    kpts[16] = (0.5, ankle_y)
    conf[16] = ankle_conf

    detection_target = PlayerDetection(
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
    detection_other = PlayerDetection(
        player=other,  # type: ignore[arg-type]
        keypoints_xyn=stub_kpts,
        confidence=stub_conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.3),
        feet_mid_m=(4.0, 8.0),
        fallback_mode="ankle",
    )
    if player == "A":
        pa, pb = detection_target, detection_other
    else:
        pa, pb = detection_other, detection_target
    return FrameKeypoints(t_ms=t_ms, frame_idx=t_ms // 33, player_a=pa, player_b=pb)


def _ingest_frames(
    ext: CrouchDepth,
    target_state: str,
    frames: list[FrameKeypoints],
) -> None:
    """Ingest a list of frames with a constant target_state."""
    for f in frames:
        ext.ingest(
            frame=f,
            target_state=target_state,  # type: ignore[arg-type]
            opponent_state="DEAD_TIME",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=f.t_ms,
        )


def _canonical_frames(
    hip_y: float,
    ankle_y: float,
    shoulder_y: float,
    count: int = 10,
    player: str = "A",
) -> list[FrameKeypoints]:
    """Build `count` identical frames with the given hip/ankle/shoulder y-values (all confident)."""
    return [
        build_crouch_frame(
            player=player,
            hip_y=hip_y, hip_conf=0.9,
            knee_y=(hip_y + ankle_y) / 2.0, knee_conf=0.9,
            ankle_y=ankle_y, ankle_conf=0.9,
            shoulder_y=shoulder_y, shoulder_conf=0.9,
            t_ms=100 * (i + 1),
        )
        for i in range(count)
    ]


# ──────────────────────────── 1. Class metadata ────────────────────────────


def test_class_attributes_signal_name_and_required_state() -> None:
    """Class-level wiring must match the SignalName literal + ACTIVE_RALLY gate."""
    assert CrouchDepth.signal_name == "crouch_depth_degradation_deg"
    assert CrouchDepth.required_state == ("ACTIVE_RALLY",)
    assert isinstance(CrouchDepth.required_state, tuple)


# ──────────────────────────── 2. Non-rally state ignored ────────────────────────────


def test_pre_serve_ritual_state_is_ignored() -> None:
    """PRE_SERVE_RITUAL ticks are not accumulated — flush returns None (no baseline set)."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    # crouch_norm = (0.9 - 0.5) / (0.5 - 0.3) = 0.4 / 0.2 = 2.0 (well-formed)
    frames = _canonical_frames(hip_y=0.5, ankle_y=0.9, shoulder_y=0.3, count=10)
    _ingest_frames(ext, "PRE_SERVE_RITUAL", frames)
    assert ext.flush(t_ms=2000) is None


def test_dead_time_state_is_ignored() -> None:
    """DEAD_TIME ticks are not accumulated — flush returns None."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames = _canonical_frames(hip_y=0.5, ankle_y=0.9, shoulder_y=0.3, count=10)
    _ingest_frames(ext, "DEAD_TIME", frames)
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── 3. Minimum samples guard ────────────────────────────


def test_below_five_samples_returns_none() -> None:
    """Fewer than 5 non-nan samples → flush returns None (baseline not established)."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames = _canonical_frames(hip_y=0.5, ankle_y=0.9, shoulder_y=0.3, count=4)  # only 4
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── 4. First flush sets baseline, emits 0.0 ────────────────────────────


def test_first_flush_sets_baseline_and_emits_zero() -> None:
    """First successful flush establishes the baseline and emits value=0.0."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    # normalized_crouch = (0.9 - 0.4) / (0.4 - 0.16) = 0.5 / 0.24 ≈ 2.083...
    frames = _canonical_frames(hip_y=0.4, ankle_y=0.9, shoulder_y=0.16, count=10)
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    sample = ext.flush(t_ms=1200)
    assert isinstance(sample, SignalSample)
    assert sample.signal_name == "crouch_depth_degradation_deg"
    assert sample.state == "ACTIVE_RALLY"
    assert sample.player == "A"
    assert sample.value == pytest.approx(0.0, abs=1e-9)


# ──────────────────────────── 5. Second flush: degradation math ────────────────────────────


def test_second_flush_emits_angular_degradation() -> None:
    """After baseline is set, a 10% shallower crouch emits
    value = degrees(atan(baseline - current)) ≈ 14.04°.
    """
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    # Baseline: normalized_crouch = 2.5
    #   hip=0.5, ankle=0.9 → hip_ankle_dist = 0.4
    #   shoulder=0.34, hip=0.5 → torso = 0.16
    #   ratio = 0.4 / 0.16 = 2.5 ✓
    baseline_frames = _canonical_frames(hip_y=0.5, ankle_y=0.9, shoulder_y=0.34, count=10)
    _ingest_frames(ext, "ACTIVE_RALLY", baseline_frames)
    first = ext.flush(t_ms=1200)
    assert first is not None
    assert first.value == pytest.approx(0.0, abs=1e-9)

    # Now "fatigued": normalized_crouch = 2.25 (10% shallower)
    #   hip=0.5, ankle=0.86 → hip_ankle_dist = 0.36
    #   shoulder=0.34, hip=0.5 → torso = 0.16
    #   ratio = 0.36 / 0.16 = 2.25 ✓
    fatigued_frames = [
        build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.86, ankle_conf=0.9,
            shoulder_y=0.34, shoulder_conf=0.9,
            t_ms=2000 + 100 * (i + 1),
        )
        for i in range(10)
    ]
    _ingest_frames(ext, "ACTIVE_RALLY", fatigued_frames)
    second = ext.flush(t_ms=3100)
    assert second is not None
    assert second.value is not None
    expected_deg = math.degrees(math.atan(2.5 - 2.25))
    assert second.value == pytest.approx(expected_deg, abs=1e-6)
    # Sanity range (order of magnitude): a 10% shallower crouch ~ 14° drift.
    assert 10.0 < second.value < 20.0


# ──────────────────────────── 6. Second flush with SAME crouch → ~0° ────────────────────────────


def test_second_flush_with_same_crouch_emits_zero() -> None:
    """If the post-baseline crouch matches the baseline exactly, degradation ≈ 0°."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames_1 = _canonical_frames(hip_y=0.5, ankle_y=0.9, shoulder_y=0.34, count=10)
    _ingest_frames(ext, "ACTIVE_RALLY", frames_1)
    assert ext.flush(t_ms=1200) is not None

    frames_2 = [
        build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.9, ankle_conf=0.9,
            shoulder_y=0.34, shoulder_conf=0.9,
            t_ms=2000 + 100 * (i + 1),
        )
        for i in range(10)
    ]
    _ingest_frames(ext, "ACTIVE_RALLY", frames_2)
    second = ext.flush(t_ms=3100)
    assert second is not None
    assert second.value == pytest.approx(0.0, abs=1e-9)


# ──────────────────────────── 7. Hip occlusion → NaN ────────────────────────────


def test_hip_occlusion_produces_nan_and_can_fail_min_samples() -> None:
    """When both hips have low confidence, NaN is appended; if < 5 non-nan, flush returns None."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames = [
        build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.1,  # occluded
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.9, ankle_conf=0.9,
            shoulder_y=0.34, shoulder_conf=0.9,
            t_ms=100 * (i + 1),
        )
        for i in range(10)
    ]
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    # All 10 frames contribute NaN → 0 non-nan < 5 → None.
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── 8. Shoulder occlusion → NaN ────────────────────────────


def test_shoulder_occlusion_produces_nan_and_fails_min_samples() -> None:
    """Shoulder confidence below 0.3 → torso unknown → NaN ingested."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames = [
        build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.9, ankle_conf=0.9,
            shoulder_y=0.34, shoulder_conf=0.1,  # occluded
            t_ms=100 * (i + 1),
        )
        for i in range(10)
    ]
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── 9. Ankle occlusion → NaN ────────────────────────────


def test_ankle_occlusion_produces_nan_and_fails_min_samples() -> None:
    """Ankle confidence below 0.3 → hip-ankle unknown → NaN ingested."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames = [
        build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.9, ankle_conf=0.1,  # occluded
            shoulder_y=0.34, shoulder_conf=0.9,
            t_ms=100 * (i + 1),
        )
        for i in range(10)
    ]
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── 10. Torso collapse (shoulder == hip) → NaN ────────────────────────────


def test_torso_collapse_produces_nan() -> None:
    """shoulder_y == hip_y → torso_scalar < 1e-5 → NaN ingested (no divide-by-zero)."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames = [
        build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.9, ankle_conf=0.9,
            shoulder_y=0.5, shoulder_conf=0.9,  # same as hip → torso = 0
            t_ms=100 * (i + 1),
        )
        for i in range(10)
    ]
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── 11. Flush clears the buffer ────────────────────────────


def test_flush_clears_buffer_so_second_flush_without_new_data_returns_none() -> None:
    """After a flush, the buffer is emptied; the next flush without new ingests returns None."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames = _canonical_frames(hip_y=0.5, ankle_y=0.9, shoulder_y=0.34, count=10)
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    first = ext.flush(t_ms=1200)
    assert first is not None
    # Buffer is cleared; a second flush without any new ingest returns None.
    second = ext.flush(t_ms=2200)
    assert second is None


# ──────────────────────────── 12. reset() clears buffer AND baseline ────────────────────────────


def test_reset_clears_buffer_and_baseline() -> None:
    """reset() wipes both the per-window buffer AND the long-lived baseline."""
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    frames = _canonical_frames(hip_y=0.5, ankle_y=0.9, shoulder_y=0.34, count=10)
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    first = ext.flush(t_ms=1200)
    assert first is not None  # baseline now established
    ext.reset()
    # After reset, the next successful flush should AGAIN emit 0.0 (fresh baseline).
    frames_2 = [
        build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.86, ankle_conf=0.9,
            shoulder_y=0.34, shoulder_conf=0.9,
            t_ms=5000 + 100 * (i + 1),
        )
        for i in range(10)
    ]
    _ingest_frames(ext, "ACTIVE_RALLY", frames_2)
    new_baseline = ext.flush(t_ms=6100)
    assert new_baseline is not None
    assert new_baseline.value == pytest.approx(0.0, abs=1e-9)


# ──────────────────────────── 13. Fail-fast missing match_id → KeyError ────────────────────────────


def test_missing_match_id_raises_keyerror_on_flush() -> None:
    """USER-CORRECTION-022: missing match_id must raise KeyError on flush (never silent default)."""
    ext = CrouchDepth(target_player="A", dependencies={})  # no match_id
    frames = _canonical_frames(hip_y=0.5, ankle_y=0.9, shoulder_y=0.34, count=10)
    _ingest_frames(ext, "ACTIVE_RALLY", frames)
    with pytest.raises(KeyError, match="match_id"):
        ext.flush(t_ms=1200)


# ──────────────────────────── 14. Symmetric A/B independence ────────────────────────────


def test_two_instances_for_a_and_b_accumulate_independently() -> None:
    """Parallel instances for A and B maintain independent buffers AND baselines."""
    ext_a = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    ext_b = CrouchDepth(target_player="B", dependencies={"match_id": "m1"})

    # Build frames where A has a deep crouch (norm=2.5) and B has a shallow crouch (norm=1.5).
    # Since build_crouch_frame sets target to the given `player`, we need both perspectives.
    # For each tick we build TWO frames — one targeted at A, one at B — and ingest into each.
    for i in range(10):
        frame_a_target = build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.9, ankle_conf=0.9,
            shoulder_y=0.34, shoulder_conf=0.9,
            t_ms=100 * (i + 1),
        )
        frame_b_target = build_crouch_frame(
            player="B",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.6, knee_conf=0.9,
            ankle_y=0.7, ankle_conf=0.9,
            shoulder_y=0.367, shoulder_conf=0.9,  # torso=0.133, hip_ankle=0.2 → ratio ≈ 1.5
            t_ms=100 * (i + 1),
        )
        ext_a.ingest(
            frame=frame_a_target,
            target_state="ACTIVE_RALLY",
            opponent_state="ACTIVE_RALLY",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=100 * (i + 1),
        )
        ext_b.ingest(
            frame=frame_b_target,
            target_state="ACTIVE_RALLY",
            opponent_state="ACTIVE_RALLY",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=100 * (i + 1),
        )

    sample_a = ext_a.flush(t_ms=1200)
    sample_b = ext_b.flush(t_ms=1200)
    assert sample_a is not None and sample_a.player == "A"
    assert sample_b is not None and sample_b.player == "B"
    # Both should emit 0.0 for their first flush (each established its own baseline).
    assert sample_a.value == pytest.approx(0.0, abs=1e-9)
    assert sample_b.value == pytest.approx(0.0, abs=1e-9)

    # Now degrade A: shallower crouch. B stays identical to its baseline.
    for i in range(10):
        frame_a = build_crouch_frame(
            player="A",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.7, knee_conf=0.9,
            ankle_y=0.86, ankle_conf=0.9,  # 10% shallower
            shoulder_y=0.34, shoulder_conf=0.9,
            t_ms=2000 + 100 * (i + 1),
        )
        frame_b = build_crouch_frame(
            player="B",
            hip_y=0.5, hip_conf=0.9,
            knee_y=0.6, knee_conf=0.9,
            ankle_y=0.7, ankle_conf=0.9,
            shoulder_y=0.367, shoulder_conf=0.9,
            t_ms=2000 + 100 * (i + 1),
        )
        ext_a.ingest(
            frame=frame_a,
            target_state="ACTIVE_RALLY",
            opponent_state="ACTIVE_RALLY",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=2000 + 100 * (i + 1),
        )
        ext_b.ingest(
            frame=frame_b,
            target_state="ACTIVE_RALLY",
            opponent_state="ACTIVE_RALLY",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=2000 + 100 * (i + 1),
        )

    sample_a2 = ext_a.flush(t_ms=3100)
    sample_b2 = ext_b.flush(t_ms=3100)
    assert sample_a2 is not None
    assert sample_b2 is not None
    # A degraded, B did not. Their values MUST differ.
    assert sample_a2.value != pytest.approx(sample_b2.value, abs=1e-6)
    assert sample_a2.value is not None
    assert sample_a2.value > 5.0  # meaningful angular degradation
    assert sample_b2.value == pytest.approx(0.0, abs=1e-9)


# ──────────────────────────── 15. Missing target detection → NaN path ────────────────────────────


def test_missing_target_detection_produces_nan() -> None:
    """When the target player's PlayerDetection is None (occluded track), NaN is ingested.
    Covers the `detection is None` branch in ingest().
    """
    stub_kpts, stub_conf = _stub_confident_keypoints()
    detection_b = PlayerDetection(
        player="B",
        keypoints_xyn=stub_kpts,
        confidence=stub_conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.3),
        feet_mid_m=(4.0, 8.0),
        fallback_mode="ankle",
    )
    ext = CrouchDepth(target_player="A", dependencies={"match_id": "m1"})
    for i in range(10):
        frame = FrameKeypoints(
            t_ms=100 * (i + 1),
            frame_idx=i,
            player_a=None,  # target missing
            player_b=detection_b,
        )
        ext.ingest(
            frame=frame,
            target_state="ACTIVE_RALLY",
            opponent_state="DEAD_TIME",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=100 * (i + 1),
        )
    # All 10 contributions are NaN → 0 non-nan < 5 → None.
    assert ext.flush(t_ms=2000) is None


# ──────────────────────────── Smoke: numpy import guard ────────────────────────────


def test_numpy_is_available_for_nanmean() -> None:
    """Sanity check that numpy's nanmean is available — used internally by the extractor."""
    assert float(np.nanmean([1.0, np.nan, 2.0])) == pytest.approx(1.5, abs=1e-9)
