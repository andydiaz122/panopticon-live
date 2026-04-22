"""Homography-based court mapping for PANOPTICON LIVE.

Enforces USER-CORRECTION-005 (aspect-ratio un-normalization) and implements the court-bounds
guard required by USER-CORRECTION-007 (Absolute Court Half Assignment).

Flow:
    normalized [0,1] pt   --(multiply by W, H)-->   pixel-space pt
    pixel-space pt        --(cv2.perspectiveTransform(M))-->   court meters
    court meters          --(bounds check vs 23.77 x 8.23 with margin)-->   (x_m, y_m) or None
"""

from __future__ import annotations

import cv2
import numpy as np

from backend.db.schema import (
    SINGLES_COURT_LENGTH_M,
    SINGLES_COURT_WIDTH_M,
    CornersNormalized,
)


class CourtMapper:
    """Projects normalized [0,1] image points to court meters via 4-corner homography.

    Canonical convention (FROZEN):
      top_left (image)     -> (0, 0)                (far baseline, far-left sideline)
      top_right (image)    -> (W_court, 0)          (far baseline, far-right sideline)
      bottom_right (image) -> (W_court, L_court)    (near baseline, near-right sideline)
      bottom_left (image)  -> (0, L_court)          (near baseline, near-left sideline)

    Therefore in court meters:
      y_m close to 0      = far player's baseline (Player B / camera-far)
      y_m close to 11.885 = net
      y_m close to 23.77  = near player's baseline (Player A / camera-near)
    """

    COURT_LENGTH_M: float = SINGLES_COURT_LENGTH_M
    COURT_WIDTH_M: float = SINGLES_COURT_WIDTH_M

    def __init__(
        self,
        corners_normalized: CornersNormalized,
        frame_width: int,
        frame_height: int,
        court_width_m: float | None = None,
    ) -> None:
        """
        Args:
            corners_normalized: 4 corners in [0,1] normalized image coords.
            frame_width, frame_height: source frame pixel dimensions (for un-normalization).
            court_width_m: canonical court width to map corners to. Defaults to
                SINGLES_COURT_WIDTH_M (8.23m). Pass DOUBLES_COURT_WIDTH_M (10.97m)
                when the corners trace the OUTSIDE of the doubles alleys — otherwise
                lateral signals are compressed by ~25% on the x-axis.
        """
        if frame_width <= 0 or frame_height <= 0:
            raise ValueError(
                f"frame_width and frame_height must be positive; got {frame_width}x{frame_height}"
            )
        self._frame_wh = (frame_width, frame_height)
        self._corners_normalized = corners_normalized
        # Per-instance override (preserves class attribute for back-compat with existing tests).
        self.court_width_m: float = (
            court_width_m if court_width_m is not None else self.COURT_WIDTH_M
        )

        # USER-CORRECTION-005: un-normalize BEFORE cv2.getPerspectiveTransform
        corners_pixels = (
            np.array(
                [
                    corners_normalized.top_left,
                    corners_normalized.top_right,
                    corners_normalized.bottom_right,
                    corners_normalized.bottom_left,
                ],
                dtype=np.float32,
            )
            * np.array([[frame_width, frame_height]], dtype=np.float32)
        )

        court_corners_m = np.array(
            [
                [0.0, 0.0],
                [self.court_width_m, 0.0],
                [self.court_width_m, self.COURT_LENGTH_M],
                [0.0, self.COURT_LENGTH_M],
            ],
            dtype=np.float32,
        )

        self._homography = cv2.getPerspectiveTransform(corners_pixels, court_corners_m)

    def to_court_meters(
        self, pt_normalized_xy: tuple[float, float], margin_m: float = 2.0
    ) -> tuple[float, float] | None:
        """Project a normalized [0,1] point to court meters.

        Returns None if the projection falls outside the singles court extended by `margin_m`
        on all sides (SP1 bounds guard — prevents bleacher hallucinations).
        """
        x_norm, y_norm = pt_normalized_xy
        if not (0.0 <= x_norm <= 1.0 and 0.0 <= y_norm <= 1.0):
            return None

        W, H = self._frame_wh
        pt_px = np.array([[[x_norm * W, y_norm * H]]], dtype=np.float32)  # shape (1, 1, 2)
        mapped = cv2.perspectiveTransform(pt_px, self._homography)
        x_m, y_m = float(mapped[0, 0, 0]), float(mapped[0, 0, 1])

        if (
            -margin_m <= x_m <= self.court_width_m + margin_m
            and -margin_m <= y_m <= self.COURT_LENGTH_M + margin_m
        ):
            return (x_m, y_m)
        return None

    def is_in_court_polygon(
        self, pt_normalized_xy: tuple[float, float], margin_m: float = 2.0
    ) -> bool:
        """True if a normalized point projects into the court (+ margin). Pure convenience wrapper."""
        return self.to_court_meters(pt_normalized_xy, margin_m=margin_m) is not None
