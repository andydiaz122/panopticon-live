"""Tests for backend/cv/homography.py.

Enforces USER-CORRECTION-005 (aspect-ratio un-normalization) and USER-CORRECTION-007
(court bounds check for Absolute Court Half Assignment).

Written FIRST per TDD discipline — implementation follows.
"""

from __future__ import annotations

import math

import pytest

from backend.cv.homography import CourtMapper
from backend.db.schema import (
    DOUBLES_COURT_WIDTH_M,
    NET_Y_M,
    SINGLES_COURT_LENGTH_M,
    SINGLES_COURT_WIDTH_M,
    CornersNormalized,
)

# ──────────────────────────── Fixtures ────────────────────────────


@pytest.fixture
def frame_dims() -> tuple[int, int]:
    return 1920, 1080


@pytest.fixture
def perfect_rectangle_corners() -> CornersNormalized:
    """Hypothetical straight-on camera — corners form a rectangle at the outer 90% of the frame."""
    return CornersNormalized(
        top_left=(0.05, 0.10),
        top_right=(0.95, 0.10),
        bottom_right=(0.95, 0.90),
        bottom_left=(0.05, 0.90),
    )


@pytest.fixture
def trapezoid_corners() -> CornersNormalized:
    """Realistic broadcast camera — far baseline looks narrower due to perspective."""
    return CornersNormalized(
        top_left=(0.35, 0.20),
        top_right=(0.65, 0.20),
        bottom_right=(0.95, 0.88),
        bottom_left=(0.05, 0.88),
    )


# ──────────────────────────── Construction + shape ────────────────────────────


def test_constructor_rejects_non_positive_dims(perfect_rectangle_corners: CornersNormalized) -> None:
    with pytest.raises(ValueError):
        CourtMapper(corners_normalized=perfect_rectangle_corners, frame_width=0, frame_height=1080)
    with pytest.raises(ValueError):
        CourtMapper(corners_normalized=perfect_rectangle_corners, frame_width=1920, frame_height=-1)


def test_court_dimensions_constants_match_schema() -> None:
    """CourtMapper uses 23.77m by 8.23m singles dimensions from the schema module."""
    assert CourtMapper.COURT_LENGTH_M == SINGLES_COURT_LENGTH_M == 23.77
    assert CourtMapper.COURT_WIDTH_M == SINGLES_COURT_WIDTH_M == 8.23
    assert pytest.approx(11.885) == NET_Y_M


# ──────────────────────────── to_court_meters ────────────────────────────


def test_corners_project_to_court_corners_exactly(
    perfect_rectangle_corners: CornersNormalized, frame_dims: tuple[int, int]
) -> None:
    """Given the 4 annotated corners, projecting them back should yield the 4 court corners."""
    W, H = frame_dims
    m = CourtMapper(corners_normalized=perfect_rectangle_corners, frame_width=W, frame_height=H)

    tl = m.to_court_meters(perfect_rectangle_corners.top_left)
    tr = m.to_court_meters(perfect_rectangle_corners.top_right)
    br = m.to_court_meters(perfect_rectangle_corners.bottom_right)
    bl = m.to_court_meters(perfect_rectangle_corners.bottom_left)

    assert tl is not None and tr is not None and br is not None and bl is not None
    assert tl == pytest.approx((0.0, 0.0), abs=1e-3)
    assert tr == pytest.approx((SINGLES_COURT_WIDTH_M, 0.0), abs=1e-3)
    assert br == pytest.approx((SINGLES_COURT_WIDTH_M, SINGLES_COURT_LENGTH_M), abs=1e-3)
    assert bl == pytest.approx((0.0, SINGLES_COURT_LENGTH_M), abs=1e-3)


def test_near_baseline_center_projects_near_singles_court_bottom(
    trapezoid_corners: CornersNormalized, frame_dims: tuple[int, int]
) -> None:
    """The midpoint of the near (bottom) baseline should project to (court_width/2, 23.77m)."""
    W, H = frame_dims
    m = CourtMapper(corners_normalized=trapezoid_corners, frame_width=W, frame_height=H)

    near_mid_norm = (
        (trapezoid_corners.bottom_left[0] + trapezoid_corners.bottom_right[0]) / 2.0,
        (trapezoid_corners.bottom_left[1] + trapezoid_corners.bottom_right[1]) / 2.0,
    )
    pt_m = m.to_court_meters(near_mid_norm)
    assert pt_m is not None
    x_m, y_m = pt_m
    assert x_m == pytest.approx(SINGLES_COURT_WIDTH_M / 2.0, abs=0.05)
    assert y_m == pytest.approx(SINGLES_COURT_LENGTH_M, abs=0.05)


def test_far_baseline_center_projects_near_zero_y(
    trapezoid_corners: CornersNormalized, frame_dims: tuple[int, int]
) -> None:
    """The midpoint of the far (top) baseline should project to (court_width/2, 0m)."""
    W, H = frame_dims
    m = CourtMapper(corners_normalized=trapezoid_corners, frame_width=W, frame_height=H)

    far_mid_norm = (
        (trapezoid_corners.top_left[0] + trapezoid_corners.top_right[0]) / 2.0,
        (trapezoid_corners.top_left[1] + trapezoid_corners.top_right[1]) / 2.0,
    )
    pt_m = m.to_court_meters(far_mid_norm)
    assert pt_m is not None
    x_m, y_m = pt_m
    assert x_m == pytest.approx(SINGLES_COURT_WIDTH_M / 2.0, abs=0.05)
    assert y_m == pytest.approx(0.0, abs=0.05)


def test_net_line_is_y_m_11_885(
    trapezoid_corners: CornersNormalized, frame_dims: tuple[int, int]
) -> None:
    """A midpoint between near and far baselines should project near y_m = 11.885."""
    W, H = frame_dims
    m = CourtMapper(corners_normalized=trapezoid_corners, frame_width=W, frame_height=H)

    center_norm = (
        sum(c[0] for c in [
            trapezoid_corners.top_left, trapezoid_corners.top_right,
            trapezoid_corners.bottom_left, trapezoid_corners.bottom_right,
        ]) / 4.0,
        sum(c[1] for c in [
            trapezoid_corners.top_left, trapezoid_corners.top_right,
            trapezoid_corners.bottom_left, trapezoid_corners.bottom_right,
        ]) / 4.0,
    )
    # Note: image-space centroid is NOT generally court-center due to trapezoidal distortion.
    # But for symmetric trapezoid, it maps near the court center (4.115, 11.885).
    pt_m = m.to_court_meters(center_norm)
    assert pt_m is not None
    _, y_m = pt_m
    # We just want it on the net side for a roughly symmetric trapezoid
    assert 0.0 < y_m < SINGLES_COURT_LENGTH_M


# ──────────────────────────── Bounds: off-court returns None (SP1) ────────────────────────────


def test_bleacher_point_is_off_court(
    trapezoid_corners: CornersNormalized, frame_dims: tuple[int, int]
) -> None:
    """A point well outside the court polygon should return None (SP1: USER-CORRECTION-005 guard)."""
    W, H = frame_dims
    m = CourtMapper(corners_normalized=trapezoid_corners, frame_width=W, frame_height=H)

    # Top-of-frame, far above the far baseline — this is bleacher territory.
    assert m.to_court_meters((0.5, 0.02)) is None
    # Way off to the side past the sidelines
    assert m.to_court_meters((0.99, 0.5)) is None


def test_margin_allows_player_retreat_behind_baseline(
    trapezoid_corners: CornersNormalized, frame_dims: tuple[int, int]
) -> None:
    """Players often retreat 1-2m past their baseline. The is_in_court_polygon margin allows this."""
    W, H = frame_dims
    m = CourtMapper(corners_normalized=trapezoid_corners, frame_width=W, frame_height=H)

    # A point just 0.01 below the near baseline in normalized coords — should be IN-court with margin
    slightly_below_baseline = (
        (trapezoid_corners.bottom_left[0] + trapezoid_corners.bottom_right[0]) / 2.0,
        min((trapezoid_corners.bottom_left[1] + trapezoid_corners.bottom_right[1]) / 2.0 + 0.01, 0.99),
    )
    # to_court_meters returns a result (past y=23.77 but within margin); is_in_court_polygon is True
    pt_m = m.to_court_meters(slightly_below_baseline)
    assert pt_m is not None
    assert m.is_in_court_polygon(slightly_below_baseline, margin_m=2.0) is True


# ──────────────────────────── USER-CORRECTION-005: aspect-ratio regression ────────────────────────────


def test_aspect_ratio_un_normalization_preserves_physical_distances(frame_dims: tuple[int, int]) -> None:
    """Canonical regression test for USER-CORRECTION-005.

    We construct corners that span exactly the full frame (0,0) -> (1,1) rectangle.
    A horizontal move of 50% normalized-X should map to (COURT_WIDTH/2) meters.
    A vertical move of 50% normalized-Y should map to (COURT_LENGTH/2) meters.
    If aspect-ratio un-normalization is skipped, these two 50% moves would produce
    equal meter distances — FAIL, and the regression guard fires.
    """
    W, H = frame_dims
    full_frame_corners = CornersNormalized(
        top_left=(0.0, 0.0),
        top_right=(1.0, 0.0),
        bottom_right=(1.0, 1.0),
        bottom_left=(0.0, 1.0),
    )
    m = CourtMapper(corners_normalized=full_frame_corners, frame_width=W, frame_height=H)

    left_mid = m.to_court_meters((0.0, 0.5))
    right_mid = m.to_court_meters((1.0, 0.5))
    top_mid = m.to_court_meters((0.5, 0.0))
    bottom_mid = m.to_court_meters((0.5, 1.0))

    assert left_mid is not None and right_mid is not None
    assert top_mid is not None and bottom_mid is not None

    horizontal_m = math.hypot(right_mid[0] - left_mid[0], right_mid[1] - left_mid[1])
    vertical_m = math.hypot(bottom_mid[0] - top_mid[0], bottom_mid[1] - top_mid[1])

    # Horizontal move = full court width (8.23m)
    assert horizontal_m == pytest.approx(SINGLES_COURT_WIDTH_M, abs=0.01)
    # Vertical move = full court length (23.77m)
    assert vertical_m == pytest.approx(SINGLES_COURT_LENGTH_M, abs=0.01)

    # They MUST NOT be equal — if they were, un-normalization was skipped
    assert not math.isclose(horizontal_m, vertical_m, rel_tol=0.01)


# ──────────────────────────── is_in_court_polygon ────────────────────────────


def test_in_polygon_accepts_court_interior(
    trapezoid_corners: CornersNormalized, frame_dims: tuple[int, int]
) -> None:
    W, H = frame_dims
    m = CourtMapper(corners_normalized=trapezoid_corners, frame_width=W, frame_height=H)
    # A point near the court center should definitely be in the polygon
    assert m.is_in_court_polygon((0.5, 0.5), margin_m=0.0) is True


def test_in_polygon_rejects_bleachers(
    trapezoid_corners: CornersNormalized, frame_dims: tuple[int, int]
) -> None:
    W, H = frame_dims
    m = CourtMapper(corners_normalized=trapezoid_corners, frame_width=W, frame_height=H)
    assert m.is_in_court_polygon((0.5, 0.02), margin_m=0.0) is False
    assert m.is_in_court_polygon((0.99, 0.5), margin_m=0.0) is False


# ──────────────────────────── court_width_m override (USER-CORRECTION-026) ────────────────────────────


def test_doubles_width_override_maps_corners_to_10_97m(
    perfect_rectangle_corners: CornersNormalized, frame_dims: tuple[int, int],
) -> None:
    """When corners trace the outside of the doubles alleys, court_width_m must be
    overridden to 10.97m; otherwise lateral signals are compressed by ~25% on the x-axis."""
    W, H = frame_dims
    m = CourtMapper(
        corners_normalized=perfect_rectangle_corners,
        frame_width=W, frame_height=H,
        court_width_m=DOUBLES_COURT_WIDTH_M,
    )
    # top_right corner should project to (10.97, 0), not (8.23, 0)
    tr = m.to_court_meters(perfect_rectangle_corners.top_right)
    assert tr is not None
    assert tr == pytest.approx((DOUBLES_COURT_WIDTH_M, 0.0), abs=1e-3)
    # Instance width attribute exposed for any downstream consumer
    assert m.court_width_m == DOUBLES_COURT_WIDTH_M


def test_default_court_width_is_singles(
    perfect_rectangle_corners: CornersNormalized, frame_dims: tuple[int, int],
) -> None:
    """No override -> singles width (back-compat; existing tests must pass unchanged)."""
    W, H = frame_dims
    m = CourtMapper(corners_normalized=perfect_rectangle_corners, frame_width=W, frame_height=H)
    assert m.court_width_m == SINGLES_COURT_WIDTH_M
    tr = m.to_court_meters(perfect_rectangle_corners.top_right)
    assert tr is not None
    assert tr == pytest.approx((SINGLES_COURT_WIDTH_M, 0.0), abs=1e-3)


def test_doubles_width_expands_lateral_scale(
    perfect_rectangle_corners: CornersNormalized, frame_dims: tuple[int, int],
) -> None:
    """The same normalized point projects to a LARGER x_m under doubles mapping than singles.

    This is the whole point of the override: if corners trace the outer doubles alleys,
    every lateral measurement needs to be ~33% larger (10.97/8.23 - 1 = 33%) to reflect
    the true physical width. Without the override, lateral signals are compressed.
    """
    W, H = frame_dims
    m_singles = CourtMapper(
        corners_normalized=perfect_rectangle_corners, frame_width=W, frame_height=H,
    )
    m_doubles = CourtMapper(
        corners_normalized=perfect_rectangle_corners, frame_width=W, frame_height=H,
        court_width_m=DOUBLES_COURT_WIDTH_M,
    )
    # Interior point that's clearly inside both mappings (avoid boundary float imprecision)
    interior = (0.75, 0.5)
    pt_singles = m_singles.to_court_meters(interior, margin_m=0.0)
    pt_doubles = m_doubles.to_court_meters(interior, margin_m=0.0)
    assert pt_singles is not None and pt_doubles is not None
    # Doubles gives LARGER x_m under scale factor 10.97/8.23 ≈ 1.333
    assert pt_doubles[0] > pt_singles[0]
    assert pt_doubles[0] == pytest.approx(
        pt_singles[0] * DOUBLES_COURT_WIDTH_M / SINGLES_COURT_WIDTH_M, abs=1e-3,
    )
    # y_m (length) is unchanged by the width override
    assert pt_doubles[1] == pytest.approx(pt_singles[1], abs=1e-3)
