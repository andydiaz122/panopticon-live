"""Tests for backend/cv/pose.py.

Enforces:
- USER-CORRECTION-003: ankle -> knee -> hip fallback chain
- USER-CORRECTION-007: Absolute Court Half Assignment (anti-identity-swap)

These tests exercise `robust_foot_point` and `assign_players` directly using synthetic
keypoint arrays. The PoseExtractor class (which wraps real YOLO inference) is not tested
here to keep tests fast and deterministic.

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import pytest

from backend.cv.homography import CourtMapper
from backend.cv.pose import (
    FALLBACK_CONF_THRESHOLD,
    assign_players,
    robust_foot_point,
)
from backend.db.schema import (
    COCO_KEYPOINTS,
    KP_LEFT_ANKLE,
    KP_LEFT_HIP,
    KP_LEFT_KNEE,
    KP_RIGHT_ANKLE,
    KP_RIGHT_HIP,
    KP_RIGHT_KNEE,
    CornersNormalized,
    RawDetection,
)

# ──────────────────────────── Keypoint builders ────────────────────────────


def kp_all_valid(x: float, y: float) -> tuple[list[tuple[float, float]], list[float]]:
    """All 17 keypoints set to (x, y) with confidence 0.9."""
    return [(x, y)] * 17, [0.9] * 17


def kp_with_hidden_ankles(
    body_x: float,
    body_y: float,
    ankle_conf: float = 0.1,
) -> tuple[list[tuple[float, float]], list[float]]:
    """Upper body visible, ankles low confidence."""
    kp = [(body_x, body_y)] * 17
    conf = [0.9] * 17
    conf[KP_LEFT_ANKLE] = ankle_conf
    conf[KP_RIGHT_ANKLE] = ankle_conf
    return kp, conf


def kp_with_only_hip_visible(
    body_x: float, body_y: float
) -> tuple[list[tuple[float, float]], list[float]]:
    """Ankles AND knees low confidence; only hips remain."""
    kp = [(body_x, body_y)] * 17
    conf = [0.9] * 17
    conf[KP_LEFT_ANKLE] = 0.1
    conf[KP_RIGHT_ANKLE] = 0.1
    conf[KP_LEFT_KNEE] = 0.1
    conf[KP_RIGHT_KNEE] = 0.1
    return kp, conf


# ──────────────────────────── robust_foot_point (USER-CORRECTION-003) ────────────────────────────


def test_robust_foot_point_prefers_ankles_when_confident() -> None:
    kp = [(0.0, 0.0)] * 17
    kp[KP_LEFT_ANKLE] = (0.4, 0.8)
    kp[KP_RIGHT_ANKLE] = (0.5, 0.8)
    conf = [0.1] * 17
    conf[KP_LEFT_ANKLE] = 0.9
    conf[KP_RIGHT_ANKLE] = 0.9

    out = robust_foot_point(kp, conf)
    assert out == (0.45, 0.8)


def test_robust_foot_point_falls_back_to_knees_when_ankles_obscured() -> None:
    kp = [(0.0, 0.0)] * 17
    kp[KP_LEFT_ANKLE] = (99.0, 99.0)  # nonsense pixel (occluded by net)
    kp[KP_RIGHT_ANKLE] = (99.0, 99.0)
    kp[KP_LEFT_KNEE] = (0.3, 0.6)
    kp[KP_RIGHT_KNEE] = (0.5, 0.6)
    conf = [0.1] * 17
    conf[KP_LEFT_ANKLE] = FALLBACK_CONF_THRESHOLD - 0.05
    conf[KP_RIGHT_ANKLE] = FALLBACK_CONF_THRESHOLD - 0.05
    conf[KP_LEFT_KNEE] = 0.8
    conf[KP_RIGHT_KNEE] = 0.8

    out = robust_foot_point(kp, conf)
    assert out == (0.4, 0.6)


def test_robust_foot_point_falls_through_to_hips_when_ankles_and_knees_obscured() -> None:
    kp = [(0.0, 0.0)] * 17
    kp[KP_LEFT_HIP] = (0.35, 0.5)
    kp[KP_RIGHT_HIP] = (0.45, 0.5)
    conf = [0.1] * 17
    conf[KP_LEFT_HIP] = 0.9
    conf[KP_RIGHT_HIP] = 0.9

    out = robust_foot_point(kp, conf)
    assert out == (0.4, 0.5)


def test_robust_foot_point_returns_none_when_everything_obscured() -> None:
    kp = [(0.0, 0.0)] * 17
    conf = [0.1] * 17  # nothing confident

    out = robust_foot_point(kp, conf)
    assert out is None


def test_robust_foot_point_requires_both_sides_confident() -> None:
    """If only one ankle is confident, we can't reliably compute the midpoint — fall through."""
    kp = [(0.0, 0.0)] * 17
    kp[KP_LEFT_ANKLE] = (0.4, 0.8)
    kp[KP_RIGHT_ANKLE] = (0.5, 0.8)
    conf = [0.9] * 17
    conf[KP_LEFT_ANKLE] = 0.9
    conf[KP_RIGHT_ANKLE] = 0.1  # one side missing — fall through to knees
    # Set up knees so we can verify the fallback went there
    kp[KP_LEFT_KNEE] = (0.3, 0.7)
    kp[KP_RIGHT_KNEE] = (0.5, 0.7)
    conf[KP_LEFT_KNEE] = 0.9
    conf[KP_RIGHT_KNEE] = 0.9

    out = robust_foot_point(kp, conf)
    assert out == (0.4, 0.7)  # midpoint of knees, not of ankles


# ──────────────────────────── Court-half assignment (USER-CORRECTION-007) ────────────────────────────


@pytest.fixture
def court_mapper() -> CourtMapper:
    # Symmetric trapezoid that will behave predictably
    corners = CornersNormalized(
        top_left=(0.35, 0.20),
        top_right=(0.65, 0.20),
        bottom_right=(0.95, 0.88),
        bottom_left=(0.05, 0.88),
    )
    return CourtMapper(corners_normalized=corners, frame_width=1920, frame_height=1080)


def _mk_det_with_foot_at(
    normalized_xy: tuple[float, float],
    bbox_conf: float = 0.8,
    kpts_conf: float = 0.85,
) -> RawDetection:
    """Build a RawDetection whose robust_foot_point falls at `normalized_xy`."""
    x, y = normalized_xy
    kp = [(x, y)] * 17  # all keypoints at the same point
    conf = [kpts_conf] * 17
    return RawDetection(keypoints_xyn=kp, confidence=conf, bbox_conf=bbox_conf)


def test_assign_players_splits_by_court_half(court_mapper: CourtMapper) -> None:
    """USER-CORRECTION-007: split by y_m > 11.885 = Player A (near), < 11.885 = Player B (far).

    Note: perspective warp means the image-space net line is ~y_norm=0.34 for this trapezoid,
    NOT y_norm=0.54. The far half of the image is compressed toward the top.
    """
    # Near-side detection (bottom of frame): projects to y_m ~ 22.8
    near = _mk_det_with_foot_at((0.5, 0.80), bbox_conf=0.9)
    # Far-side detection well above the (perspective-warped) net line: projects to y_m ~ 8
    far = _mk_det_with_foot_at((0.5, 0.30), bbox_conf=0.85)

    result = assign_players([near, far], court_mapper)

    assert result["A"] is not None
    assert result["A"].player == "A"
    _, a_y_m = result["A"].feet_mid_m
    assert a_y_m > 11.885

    assert result["B"] is not None
    assert result["B"].player == "B"
    _, b_y_m = result["B"].feet_mid_m
    assert b_y_m < 11.885


def test_assign_players_immune_to_occlusion_swap(court_mapper: CourtMapper) -> None:
    """The critical anti-swap test.

    A real (occluded-but-visible) Player B on the far side has moderate bbox confidence.
    A linesman standing inside Player A's court half has HIGH bbox confidence.

    Naive "top-2 by confidence" would pick: [real A, linesman-in-A-half]
    and since both project to A's half, no one would be assigned to B.
    A worse naive "sort by Y" would assign the linesman (lower-Y in screen)
    to Player B's identity.

    Absolute Court Half Assignment (USER-CORRECTION-007) correctly isolates:
      - Player A's half: [real A, linesman] -> picks real A (highest conf in half)
      - Player B's half: [far-player] -> picks it as the only candidate in its half.

    NOTE (USER-CORRECTION-030): after the Skeleton Sanitation Sprint, all three
    candidates must have bbox_conf ≥ BBOX_CONF_THRESHOLD (0.5). The occluded B
    here is at 0.6 (above gate, below typical-rally 0.9 values) to represent a
    partially-but-legibly occluded far player. bbox_conf values below 0.5 are
    now rejected upstream as ghosts before this test's logic matters.
    """
    real_a = _mk_det_with_foot_at((0.5, 0.85), bbox_conf=0.9, kpts_conf=0.88)
    linesman_in_a_half = _mk_det_with_foot_at((0.9, 0.70), bbox_conf=0.8, kpts_conf=0.82)
    occluded_b = _mk_det_with_foot_at((0.5, 0.28), bbox_conf=0.6, kpts_conf=0.35)

    result = assign_players([real_a, linesman_in_a_half, occluded_b], court_mapper)

    # Player A comes from the high-confidence detection in the near half
    assert result["A"] is not None
    _, a_y_m = result["A"].feet_mid_m
    assert a_y_m > 11.885

    # Player B is the occluded far-half detection (picked as top-1 within its half)
    assert result["B"] is not None
    _, b_y_m = result["B"].feet_mid_m
    assert b_y_m < 11.885


def test_assign_players_handles_missing_side(court_mapper: CourtMapper) -> None:
    """Singles warmup has only one player on-court; the other side returns None."""
    only_near = _mk_det_with_foot_at((0.5, 0.80))
    result = assign_players([only_near], court_mapper)
    assert result["A"] is not None
    assert result["B"] is None


def test_assign_players_handles_empty_frame(court_mapper: CourtMapper) -> None:
    result = assign_players([], court_mapper)
    assert result == {"A": None, "B": None}


def test_assign_players_filters_off_court_detections(court_mapper: CourtMapper) -> None:
    """Bleacher detections must not appear as players."""
    bleacher = _mk_det_with_foot_at((0.5, 0.02), bbox_conf=0.95)  # top of frame, far above court
    sideline = _mk_det_with_foot_at((0.99, 0.5), bbox_conf=0.95)  # off right sideline
    result = assign_players([bleacher, sideline], court_mapper)
    assert result == {"A": None, "B": None}


def test_assign_players_populates_fallback_mode(court_mapper: CourtMapper) -> None:
    """PlayerDetection records which segment produced feet_mid (ankle / knee / hip)."""
    # Player A with visible ankles
    kp_a = [(0.5, 0.80)] * 17
    conf_a = [0.9] * 17
    # Player B with only hips (net-occluded ankles AND knees)
    kp_b = [(0.5, 0.30)] * 17
    conf_b = [0.9] * 17
    conf_b[KP_LEFT_ANKLE] = 0.1
    conf_b[KP_RIGHT_ANKLE] = 0.1
    conf_b[KP_LEFT_KNEE] = 0.1
    conf_b[KP_RIGHT_KNEE] = 0.1

    a = RawDetection(keypoints_xyn=kp_a, confidence=conf_a, bbox_conf=0.9)
    b = RawDetection(keypoints_xyn=kp_b, confidence=conf_b, bbox_conf=0.7)
    result = assign_players([a, b], court_mapper)

    assert result["A"] is not None and result["A"].fallback_mode == "ankle"
    assert result["B"] is not None and result["B"].fallback_mode == "hip"


def test_assign_players_carries_keypoints_and_confidence(court_mapper: CourtMapper) -> None:
    """PlayerDetection should preserve the original keypoints (for canvas render)."""
    d = _mk_det_with_foot_at((0.5, 0.82))
    result = assign_players([d], court_mapper)
    assert result["A"] is not None
    assert result["A"].keypoints_xyn == d.keypoints_xyn
    assert result["A"].confidence == d.confidence


# ──────────────────────────── USER-CORRECTION-030: Skeleton Sanitation Sprint ────────────────────────────


def test_assign_players_rejects_low_bbox_conf(court_mapper: CourtMapper) -> None:
    """Ghost detections (bbox_conf < 0.5) must be rejected BEFORE the half-split.

    Without this gate, YOLO at conf=0.001 emits garbage (line judges, scoreboard
    graphics, shadows) with low bbox_conf but high mean_kp_conf, and the
    mean_kp-based tiebreaker picks them as 'Player A'.

    The Apr 22 golden v4 data showed 55.7% of 'Player A' detections were these
    ghosts (bbox_conf < 0.05). Post-fix: all ghosts land in the None bucket.
    """
    ghost = _mk_det_with_foot_at((0.5, 0.85), bbox_conf=0.001, kpts_conf=0.75)
    result = assign_players([ghost], court_mapper)
    assert result == {"A": None, "B": None}


def test_assign_players_rejects_ghost_even_when_alone_on_court_half(court_mapper: CourtMapper) -> None:
    """Even if no real player exists in a half, a ghost must not fill the slot."""
    only_ghost = _mk_det_with_foot_at((0.5, 0.30), bbox_conf=0.2, kpts_conf=0.8)
    real_a = _mk_det_with_foot_at((0.5, 0.85), bbox_conf=0.9, kpts_conf=0.88)
    result = assign_players([only_ghost, real_a], court_mapper)
    assert result["A"] is not None
    assert result["B"] is None, "ghost at bbox_conf=0.2 must NOT be promoted to B"


def test_assign_players_accepts_low_keypoint_conf_when_bbox_is_high(court_mapper: CourtMapper) -> None:
    """PATTERN-039 (Max Recall at Sensor, High Precision at Selector): once
    bbox_conf ≥ 0.5 gate kills ghosts, we can trust lower-confidence keypoints
    on real humans. The far-court player is small in frame; their ankles/knees
    often score 0.15-0.25, below the module-default 0.3 threshold. Inside
    assign_players, we use ASSIGN_PLAYERS_FALLBACK_THRESHOLD=0.15 so this
    detection is rescued.

    Without this, Player B is 0% detected in real broadcast clips (Apr 22 v4).
    """
    # Far-court player: bbox YOLO is sure (0.75) but keypoints are shaky (0.2)
    far_player = _mk_det_with_foot_at((0.5, 0.30), bbox_conf=0.75, kpts_conf=0.2)
    result = assign_players([far_player], court_mapper)
    assert result["B"] is not None, "low-kp but high-bbox far player must be kept"
    _, b_y_m = result["B"].feet_mid_m
    assert b_y_m < 11.885


def test_assign_players_rejects_ball_kid_past_left_edge(court_mapper: CourtMapper) -> None:
    """Tighter lateral polygon: ball kids at x_m < -0.5 (past the left alley)
    must be rejected even though CourtMapper's 2m margin would otherwise accept them.
    (0.001, 0.85) projects to x_m ≈ -0.586 with the trapezoid fixture — past the
    tight margin but inside the permissive margin."""
    ball_kid_left = _mk_det_with_foot_at((0.001, 0.85), bbox_conf=0.9, kpts_conf=0.9)
    result = assign_players([ball_kid_left], court_mapper)
    assert result["A"] is None, "x_m=-0.586 detection must be rejected by tight lateral polygon"


def test_assign_players_rejects_ball_kid_past_right_edge(court_mapper: CourtMapper) -> None:
    """Symmetric right-edge test. (0.999, 0.85) projects to x_m ≈ 8.816 with the
    trapezoid singles fixture — past court_width_m + 0.5 = 8.73."""
    ball_kid_right = _mk_det_with_foot_at((0.999, 0.85), bbox_conf=0.9, kpts_conf=0.9)
    result = assign_players([ball_kid_right], court_mapper)
    assert result["A"] is None, "x_m=8.816 detection must be rejected by tight lateral polygon"


def test_assign_players_keeps_on_court_player_near_sideline(court_mapper: CourtMapper) -> None:
    """Sanity: a real player NEAR the sideline (x_m ≈ 0.2) must still be kept.
    The tight margin is 0.5m — players well inside the court must not be caught
    by the ball-kid filter."""
    # Normalized x=0.10 with the trapezoid fixture projects to x_m well inside 0-8.23m.
    on_court = _mk_det_with_foot_at((0.10, 0.85), bbox_conf=0.9, kpts_conf=0.9)
    result = assign_players([on_court], court_mapper)
    assert result["A"] is not None


# ──────────────────────────── Meta checks ────────────────────────────


def test_coco_indices_match_schema() -> None:
    assert COCO_KEYPOINTS[KP_LEFT_ANKLE] == "left_ankle"
    assert COCO_KEYPOINTS[KP_RIGHT_ANKLE] == "right_ankle"
    assert COCO_KEYPOINTS[KP_LEFT_KNEE] == "left_knee"
    assert COCO_KEYPOINTS[KP_RIGHT_KNEE] == "right_knee"
    assert COCO_KEYPOINTS[KP_LEFT_HIP] == "left_hip"
    assert COCO_KEYPOINTS[KP_RIGHT_HIP] == "right_hip"


def test_fallback_threshold_is_conservative() -> None:
    """0.3 is the canonical threshold per biomech-signal-semantics skill."""
    assert FALLBACK_CONF_THRESHOLD == 0.3
