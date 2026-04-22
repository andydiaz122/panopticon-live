"""Tests for backend/cv/signals/serve_toss_variance.py — variance of pre-serve wrist-apex height in cm.

Enforces USER-CORRECTION-012 (relative kinematics — `wrist_y - hip_y`),
USER-CORRECTION-014 (ambidextrous wrist selection — max-y among confident L/R),
USER-CORRECTION-015 (variance floor — drop when std < 1e-5),
USER-CORRECTION-017 (no CourtMapper — torso is the biological ruler),
USER-CORRECTION-020 (amplitude floor — phantom serves below 0.05 normalized amplitude are dropped),
USER-CORRECTION-022 (fail-fast — `self.deps["match_id"]` must raise KeyError when missing).

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import pytest

from backend.cv.signals.serve_toss_variance import ServeTossVariance
from backend.db.schema import FrameKeypoints, PlayerDetection, SignalSample

# ──────────────────────────── Frame builder ────────────────────────────


def _stub_confident_keypoints() -> tuple[list[tuple[float, float]], list[float]]:
    """17 keypoints with high confidence — used for indices this test doesn't care about."""
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
    shoulder_l_y: float,
    shoulder_l_conf: float,
    shoulder_r_y: float,
    shoulder_r_conf: float,
    t_ms: int,
) -> FrameKeypoints:
    """Build a FrameKeypoints with the target player's wrist/hip/shoulder coords + confs set.

    Per-index override matters: 5 (LShoulder), 6 (RShoulder), 9 (LWrist), 10 (RWrist),
    11 (LHip), 12 (RHip). All other indices stay at (0.5, 0.5) conf 0.9.
    """
    kpts, conf = _stub_confident_keypoints()
    # shoulders
    kpts[5] = (0.5, shoulder_l_y)
    conf[5] = shoulder_l_conf
    kpts[6] = (0.5, shoulder_r_y)
    conf[6] = shoulder_r_conf
    # wrists
    kpts[9] = (0.5, wrist_l_y)
    conf[9] = wrist_l_conf
    kpts[10] = (0.5, wrist_r_y)
    conf[10] = wrist_r_conf
    # hips
    kpts[11] = (0.5, hip_l_y)
    conf[11] = hip_l_conf
    kpts[12] = (0.5, hip_r_y)
    conf[12] = hip_r_conf

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


def _ingest_sequence(
    ext: ServeTossVariance,
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


# ──────────────────────────── 1. Class metadata ────────────────────────────


def test_class_attributes_signal_name_and_required_state() -> None:
    """Class-level wiring must match the SignalName literal + PRE_SERVE_RITUAL gate."""
    assert ServeTossVariance.signal_name == "serve_toss_variance_cm"
    assert ServeTossVariance.required_state == ("PRE_SERVE_RITUAL",)
    assert isinstance(ServeTossVariance.required_state, tuple)


# ──────────────────────────── 2. Non-PSR states ignored ────────────────────────────


def test_active_rally_state_is_ignored() -> None:
    """ACTIVE_RALLY ticks do not touch the buffers — flush returns None."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = [
        build_frame(
            player="A",
            wrist_l_y=0.2 + 0.01 * i, wrist_l_conf=0.9,
            wrist_r_y=0.5, wrist_r_conf=0.9,
            hip_l_y=0.5, hip_l_conf=0.9,
            hip_r_y=0.5, hip_r_conf=0.9,
            shoulder_l_y=0.35, shoulder_l_conf=0.9,
            shoulder_r_y=0.35, shoulder_r_conf=0.9,
            t_ms=100 * (i + 1),
        )
        for i in range(20)
    ]
    _ingest_sequence(ext, "ACTIVE_RALLY", frames)
    assert ext.flush(t_ms=3000) is None


def test_dead_time_state_is_ignored() -> None:
    """DEAD_TIME ticks do not touch the buffers — flush returns None."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = [
        build_frame(
            player="A",
            wrist_l_y=0.3, wrist_l_conf=0.9,
            wrist_r_y=0.5, wrist_r_conf=0.9,
            hip_l_y=0.5, hip_l_conf=0.9,
            hip_r_y=0.5, hip_r_conf=0.9,
            shoulder_l_y=0.35, shoulder_l_conf=0.9,
            shoulder_r_y=0.35, shoulder_r_conf=0.9,
            t_ms=100 * (i + 1),
        )
        for i in range(20)
    ]
    _ingest_sequence(ext, "DEAD_TIME", frames)
    assert ext.flush(t_ms=3000) is None


# ──────────────────────────── 3. Missing detection → NaN → guard ────────────────────────────


def _make_frame_with_none_target(target: str, t_ms: int) -> FrameKeypoints:
    """Build a frame where the target's PlayerDetection is None (occluded)."""
    stub_kpts, stub_conf = _stub_confident_keypoints()
    other = "B" if target == "A" else "A"
    det_other = PlayerDetection(
        player=other,  # type: ignore[arg-type]
        keypoints_xyn=stub_kpts,
        confidence=stub_conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.3),
        feet_mid_m=(4.0, 8.0),
        fallback_mode="ankle",
    )
    if target == "A":
        return FrameKeypoints(t_ms=t_ms, frame_idx=t_ms // 33, player_a=None, player_b=det_other)
    return FrameKeypoints(t_ms=t_ms, frame_idx=t_ms // 33, player_a=det_other, player_b=None)


def test_missing_target_detection_produces_nan_and_flush_returns_none() -> None:
    """When player_a is None for target='A', NaN is buffered — fails sample-count / amplitude guard."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = [_make_frame_with_none_target("A", t_ms=100 * (i + 1)) for i in range(20)]
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    assert ext.flush(t_ms=3000) is None


# ──────────────────────────── 4. Real toss emits valid cm variance ────────────────────────────


def test_real_toss_emits_signal_sample_with_plausible_cm_value() -> None:
    """A real serve toss - 20 frames with wrist oscillating 0.2->0.4 relative to hip,
    torso constant at 0.15 normalized. Emitted variance should be in 1-30 cm range.
    """
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    import math as _math

    for i in range(20):
        # wrist_rel_y swings sinusoidally 0.2 → 0.4 (amplitude 0.2, well above 0.05 floor)
        # hip at 0.5; so wrist_y absolute = hip_y + wrist_rel_y = 0.5 + (0.3 + 0.1*sin)
        phase = i / 20.0 * 2.0 * _math.pi
        wrist_rel = 0.3 + 0.1 * _math.sin(phase)
        wrist_abs_y = 0.5 + wrist_rel
        # Wait — wrist ABOVE hip means smaller y. But per the spec the test is about `wrist_y - hip_y`.
        # For a toss, wrist oscillates UP and DOWN. Here we just need VARIANCE, sign does not matter.
        # Use wrist_y values that produce rel variance; we set hip fixed and wrist varies.
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=wrist_abs_y, wrist_l_conf=0.9,
                wrist_r_y=0.1, wrist_r_conf=0.0,  # right wrist not confident → only left used
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                shoulder_l_y=0.35, shoulder_l_conf=0.9,  # torso_abs_norm = |0.35 - 0.5| = 0.15
                shoulder_r_y=0.35, shoulder_r_conf=0.9,
                t_ms=100 * (i + 1),
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    sample = ext.flush(t_ms=3000)
    assert isinstance(sample, SignalSample)
    assert sample.signal_name == "serve_toss_variance_cm"
    assert sample.state == "PRE_SERVE_RITUAL"
    assert sample.player == "A"
    assert sample.value is not None
    assert sample.value > 0.0
    # Biological sanity: 1-100 cm. Math: amplitude ~0.1 normalized, std ~0.071,
    # torso 0.15 -> variance_cm = 0.071 * 60 / 0.15 ~28.3 cm.
    assert 1.0 <= sample.value <= 50.0


# ──────────────────────────── 5. Phantom serve (returner) → None ────────────────────────────


def test_phantom_serve_amplitude_below_floor_returns_none() -> None:
    """Returner's wrist jitters with tiny amplitude < 0.05 — should be dropped."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    for i in range(20):
        # Tiny variation: rel_y ∈ [0.30, 0.32] → amplitude 0.02 < 0.05 floor
        wrist_rel = 0.30 + 0.01 * (i % 3)
        wrist_abs_y = 0.5 + wrist_rel
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=wrist_abs_y, wrist_l_conf=0.9,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                shoulder_l_y=0.35, shoulder_l_conf=0.9,
                shoulder_r_y=0.35, shoulder_r_conf=0.9,
                t_ms=100 * (i + 1),
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    assert ext.flush(t_ms=3000) is None


# ──────────────────────────── 6. Ambidextrous (left occluded, right legit) ────────────────────────────


def test_ambidextrous_right_wrist_only_confident_is_detected() -> None:
    """Left wrist always conf < 0.3; right wrist bounces legitimately (amplitude > 0.05).
    Extractor must pick right wrist and emit a valid sample.
    """
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    import math as _math

    for i in range(20):
        phase = i / 20.0 * 2.0 * _math.pi
        rel = 0.30 + 0.08 * _math.sin(phase)  # amplitude 0.16 > 0.05 floor
        right_abs = 0.5 + rel
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=0.0, wrist_l_conf=0.1,   # left occluded
                wrist_r_y=right_abs, wrist_r_conf=0.9,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                shoulder_l_y=0.35, shoulder_l_conf=0.9,
                shoulder_r_y=0.35, shoulder_r_conf=0.9,
                t_ms=100 * (i + 1),
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    sample = ext.flush(t_ms=3000)
    assert sample is not None
    assert sample.value is not None
    assert sample.value > 0.0


# ──────────────────────────── 7. Hip occluded → NaN → guard ────────────────────────────


def test_hip_occluded_causes_flush_none() -> None:
    """When both hip keypoints have low confidence, NaN is ingested → flush None."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    for i in range(20):
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=0.8 + 0.05 * (i % 3), wrist_l_conf=0.9,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.1,   # occluded
                hip_r_y=0.5, hip_r_conf=0.1,   # occluded
                shoulder_l_y=0.35, shoulder_l_conf=0.9,
                shoulder_r_y=0.35, shoulder_r_conf=0.9,
                t_ms=100 * (i + 1),
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    assert ext.flush(t_ms=3000) is None


# ──────────────────────────── 8. Torso collapse (shoulder == hip) → None ────────────────────────────


def test_torso_collapse_guard_returns_none() -> None:
    """shoulder_y == hip_y → mean_torso_norm < 1e-5 → guard returns None (no divide by zero)."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    import math as _math
    for i in range(20):
        phase = i / 20.0 * 2.0 * _math.pi
        wrist_abs = 0.5 + 0.3 + 0.1 * _math.sin(phase)
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=wrist_abs, wrist_l_conf=0.9,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                shoulder_l_y=0.5, shoulder_l_conf=0.9,  # shoulder == hip (torso = 0)
                shoulder_r_y=0.5, shoulder_r_conf=0.9,
                t_ms=100 * (i + 1),
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    assert ext.flush(t_ms=3000) is None


# ──────────────────────────── 9. Variance floor (constant rel_y) → None ────────────────────────────


def test_variance_floor_returns_none_for_constant_wrist() -> None:
    """All wrists identical → std < 1e-5 → None (even if amplitude check hit 0 → amplitude guard first)."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = [
        build_frame(
            player="A",
            wrist_l_y=0.8, wrist_l_conf=0.9,   # constant
            wrist_r_y=0.5, wrist_r_conf=0.0,
            hip_l_y=0.5, hip_l_conf=0.9,
            hip_r_y=0.5, hip_r_conf=0.9,
            shoulder_l_y=0.35, shoulder_l_conf=0.9,
            shoulder_r_y=0.35, shoulder_r_conf=0.9,
            t_ms=100 * (i + 1),
        )
        for i in range(20)
    ]
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    # With amplitude 0 (constant), amplitude floor 0.05 triggers first → None.
    assert ext.flush(t_ms=3000) is None


# ──────────────────────────── 10. Flush clears buffers ────────────────────────────


def test_flush_clears_buffers_so_second_flush_returns_none() -> None:
    """After flush emits a sample, both buffers are empty; subsequent flush returns None."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    import math as _math
    for i in range(20):
        phase = i / 20.0 * 2.0 * _math.pi
        wrist_rel = 0.30 + 0.1 * _math.sin(phase)
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=0.5 + wrist_rel, wrist_l_conf=0.9,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                shoulder_l_y=0.35, shoulder_l_conf=0.9,
                shoulder_r_y=0.35, shoulder_r_conf=0.9,
                t_ms=100 * (i + 1),
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    first = ext.flush(t_ms=3000)
    assert first is not None
    second = ext.flush(t_ms=3100)
    assert second is None


# ──────────────────────────── 11. reset() clears buffers ────────────────────────────


def test_reset_clears_buffers() -> None:
    """reset() empties both wrist_rel_y and torso buffers; flush returns None afterward."""
    ext = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    frames = []
    import math as _math
    for i in range(20):
        phase = i / 20.0 * 2.0 * _math.pi
        wrist_rel = 0.30 + 0.1 * _math.sin(phase)
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=0.5 + wrist_rel, wrist_l_conf=0.9,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                shoulder_l_y=0.35, shoulder_l_conf=0.9,
                shoulder_r_y=0.35, shoulder_r_conf=0.9,
                t_ms=100 * (i + 1),
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    ext.reset()
    assert ext.flush(t_ms=3000) is None


# ──────────────────────────── 12. Fail-fast match_id missing → KeyError ────────────────────────────


def test_missing_match_id_raises_keyerror_on_flush() -> None:
    """Missing `match_id` in deps must raise KeyError on flush with a valid toss buffer."""
    ext = ServeTossVariance(target_player="A", dependencies={})  # no match_id
    frames = []
    import math as _math
    for i in range(20):
        phase = i / 20.0 * 2.0 * _math.pi
        wrist_rel = 0.30 + 0.1 * _math.sin(phase)
        frames.append(
            build_frame(
                player="A",
                wrist_l_y=0.5 + wrist_rel, wrist_l_conf=0.9,
                wrist_r_y=0.5, wrist_r_conf=0.0,
                hip_l_y=0.5, hip_l_conf=0.9,
                hip_r_y=0.5, hip_r_conf=0.9,
                shoulder_l_y=0.35, shoulder_l_conf=0.9,
                shoulder_r_y=0.35, shoulder_r_conf=0.9,
                t_ms=100 * (i + 1),
            )
        )
    _ingest_sequence(ext, "PRE_SERVE_RITUAL", frames)
    with pytest.raises(KeyError, match="match_id"):
        ext.flush(t_ms=3000)


# ──────────────────────────── 13. Target/opponent symmetry (A and B independent) ────────────────────────────


def test_two_instances_for_a_and_b_accumulate_independently() -> None:
    """Parallel instances for A and B accumulate their own buffers only. Opponent kalman ignored."""
    ext_a = ServeTossVariance(target_player="A", dependencies={"match_id": "m1"})
    ext_b = ServeTossVariance(target_player="B", dependencies={"match_id": "m1"})

    import math as _math

    # Feed A only (player-A detection present, player-B in the frame but doesn't matter to A's extractor).
    for i in range(20):
        phase = i / 20.0 * 2.0 * _math.pi
        wrist_rel = 0.30 + 0.1 * _math.sin(phase)
        frame = build_frame(
            player="A",  # target detection is A
            wrist_l_y=0.5 + wrist_rel, wrist_l_conf=0.9,
            wrist_r_y=0.5, wrist_r_conf=0.0,
            hip_l_y=0.5, hip_l_conf=0.9,
            hip_r_y=0.5, hip_r_conf=0.9,
            shoulder_l_y=0.35, shoulder_l_conf=0.9,
            shoulder_r_y=0.35, shoulder_r_conf=0.9,
            t_ms=100 * (i + 1),
        )
        ext_a.ingest(
            frame=frame,
            target_state="PRE_SERVE_RITUAL",
            opponent_state="PRE_SERVE_RITUAL",
            target_kalman=(0.0, 0.0, 999.0, 999.0),  # distractor (A must ignore)
            opponent_kalman=(0.0, 0.0, 888.0, 888.0),
            t_ms=100 * (i + 1),
        )
        # B's extractor runs on the same frame but with target_state probably PSR
        ext_b.ingest(
            frame=frame,
            target_state="PRE_SERVE_RITUAL",
            opponent_state="PRE_SERVE_RITUAL",
            target_kalman=None,
            opponent_kalman=None,
            t_ms=100 * (i + 1),
        )

    sample_a = ext_a.flush(t_ms=3000)
    sample_b = ext_b.flush(t_ms=3000)
    # A saw a valid toss, B got stub keypoints (0.5, 0.5) constant — wrist/hip/shoulder all 0.5 so
    # torso = 0 → guard → None. The key point is A and B produced DIFFERENT results, proving independence.
    assert sample_a is not None
    assert sample_a.player == "A"
    assert sample_b is None
