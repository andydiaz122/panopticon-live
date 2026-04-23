"""YOLO11m-Pose wrapper + player identity attribution for PANOPTICON LIVE.

Implements:
- USER-CORRECTION-003: ankle -> knee -> hip fallback chain (robust_foot_point)
- USER-CORRECTION-007: Absolute Court Half Assignment (assign_players)
- MPS safeguards: @torch.inference_mode, periodic empty_cache, imgsz=1280, conf=0.001
- Zero-Disk ingestion: no cv2.VideoCapture; frames arrive from the caller
"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence

import numpy as np
import torch

from backend.cv.homography import CourtMapper
from backend.db.schema import (
    KP_LEFT_ANKLE,
    KP_LEFT_HIP,
    KP_LEFT_KNEE,
    KP_RIGHT_ANKLE,
    KP_RIGHT_HIP,
    KP_RIGHT_KNEE,
    NET_Y_M,
    FallbackMode,
    PlayerDetection,
    PlayerSide,
    RawDetection,
)

# ──────────────────────────── Constants ────────────────────────────

FALLBACK_CONF_THRESHOLD: float = 0.3
"""Minimum per-keypoint confidence before we fall back to the next body segment.

Module-level default — used by external callers (signal extractors) that do NOT
benefit from the bbox_conf pre-filter. assign_players uses a LOWER threshold
(see ASSIGN_PLAYERS_FALLBACK_THRESHOLD) because its ghosts are already killed by
the bbox_conf gate."""

BBOX_CONF_THRESHOLD: float = 0.5
"""USER-CORRECTION-030: reject any YOLO detection whose bbox_conf falls below this
BEFORE the identity-assignment half-split. The Apr 22 skeleton-sanitation audit
surfaced a bimodal bbox_conf distribution: real players score 0.8-0.95, ghosts
(line judges, ball kids, shadows, banner images, scoreboard graphics) score
≤0.05. There's a clean empty gap between 0.2 and 0.5, so 0.5 is the canonical
cutoff. 55.7% of pre-filter detections in the golden v4 run are ghosts."""

ASSIGN_PLAYERS_FALLBACK_THRESHOLD: float = 0.15
"""PATTERN-039 (Max Recall at Sensor, High Precision at Selector): once ghosts
are rejected by BBOX_CONF_THRESHOLD, we can TRUST lower-confidence keypoints
on bounding boxes YOLO is ≥50% sure are humans. The far-court player is small
in frame, so their ankle/knee/hip keypoints often score 0.15-0.25. Raising
this from 0.3 to 0.15 rescues Player B without admitting new ghosts, because
the chicken-and-egg paradox (can't test 'far-court-player-only' until after
projection) is resolved by filtering upstream instead of by player role."""

ASSIGN_PLAYERS_LATERAL_MARGIN_M: float = 0.5
"""Tight lateral tolerance for on-court player selection. CourtMapper's own
bounds-check uses margin_m=2.0 (so a player chasing a ball 2m past the
sideline still maps), but for IDENTITY assignment we require tighter bounds.
Ball kids and line judges sit at x ≈ -0.5 to -2.0 and x ≈ 11.5 to 13 (just
outside the doubles alleys); 0.5m margin drops them without affecting real
on-court play."""

MPS_EMPTY_CACHE_EVERY_N_FRAMES: int = 50


# ──────────────────────────── USER-CORRECTION-003: robust_foot_point ────────────────────────────


def _mid(
    keypoints_xyn: Sequence[tuple[float, float]], idx_left: int, idx_right: int
) -> tuple[float, float]:
    lx, ly = keypoints_xyn[idx_left]
    rx, ry = keypoints_xyn[idx_right]
    return ((lx + rx) / 2.0, (ly + ry) / 2.0)


def _try_segment(
    keypoints_xyn: Sequence[tuple[float, float]],
    confidence: Sequence[float],
    idx_left: int,
    idx_right: int,
    threshold: float,
) -> tuple[float, float] | None:
    if confidence[idx_left] < threshold or confidence[idx_right] < threshold:
        return None
    return _mid(keypoints_xyn, idx_left, idx_right)


def robust_foot_point(
    keypoints_xyn: Sequence[tuple[float, float]],
    confidence: Sequence[float],
    threshold: float = FALLBACK_CONF_THRESHOLD,
) -> tuple[float, float] | None:
    """Return the most reliable lower-body reference point.

    Tries ankle -> knee -> hip midpoint in order. Both sides of a segment must clear
    `threshold` for that segment to be used (otherwise fall through).

    Returns None if no segment is confident enough.
    """
    for idx_l, idx_r in [
        (KP_LEFT_ANKLE, KP_RIGHT_ANKLE),
        (KP_LEFT_KNEE, KP_RIGHT_KNEE),
        (KP_LEFT_HIP, KP_RIGHT_HIP),
    ]:
        point = _try_segment(keypoints_xyn, confidence, idx_l, idx_r, threshold)
        if point is not None:
            return point
    return None


def infer_fallback_mode(
    confidence: Sequence[float], threshold: float = FALLBACK_CONF_THRESHOLD
) -> FallbackMode | None:
    """Return which segment would succeed for robust_foot_point, or None if none do."""
    if (
        confidence[KP_LEFT_ANKLE] >= threshold
        and confidence[KP_RIGHT_ANKLE] >= threshold
    ):
        return "ankle"
    if (
        confidence[KP_LEFT_KNEE] >= threshold
        and confidence[KP_RIGHT_KNEE] >= threshold
    ):
        return "knee"
    if (
        confidence[KP_LEFT_HIP] >= threshold
        and confidence[KP_RIGHT_HIP] >= threshold
    ):
        return "hip"
    return None


# ──────────────────────────── USER-CORRECTION-007: Absolute Court Half Assignment ────────────────────────────


def assign_players(
    raw_detections: Sequence[RawDetection],
    court_mapper: CourtMapper,
) -> dict[PlayerSide, PlayerDetection | None]:
    """Attribute raw YOLO detections to Player A / Player B via court-half topology.

    Algorithm (USER-CORRECTION-030 Skeleton Sanitation Sprint, Apr 2026):
      1. REJECT any detection with bbox_conf < BBOX_CONF_THRESHOLD (0.5). YOLO at
         conf=0.001 emits garbage detections (line judges, shadows, banner images);
         these score <0.05 in bbox_conf while real players score ≥0.5. Kills ghosts.
      2. Compute robust foot point using the LOWERED threshold (0.15) — safe now
         that ghosts are dead; rescues the small far-court player whose keypoints
         often fall below the 0.3 module-level default.
      3. Project the foot point to court meters via homography; discard if off-court.
      4. REJECT detections whose x_m falls outside [-0.5, court_width_m + 0.5].
         Ball kids / line judges sit in the 0.5-2m off-court zone that CourtMapper
         accepts by default. Identity assignment uses the tighter bound.
      5. Split by net line: y_m > NET_Y_M = Player A's half; y_m <= NET_Y_M = Player B's.
      6. Within each half, pick the detection with highest mean keypoint confidence.

    PATTERN-039 (Max Recall at Sensor, High Precision at Selector): The YOLO sensor
    stays at conf=0.001 to maximize recall — we never miss a real person who's
    partially occluded. The GUARDS live in the selector layer (this function),
    where we can use bbox_conf to discriminate real-vs-ghost cleanly.
    """
    a_candidates: list[tuple[RawDetection, tuple[float, float], tuple[float, float], FallbackMode, float]] = []
    b_candidates: list[tuple[RawDetection, tuple[float, float], tuple[float, float], FallbackMode, float]] = []

    for det in raw_detections:
        # 1. bbox_conf gate — kill ghosts BEFORE any expensive processing
        if det.bbox_conf < BBOX_CONF_THRESHOLD:
            continue
        # 2. Foot point with lowered threshold (safe because ghosts are gone)
        foot_xyn = robust_foot_point(
            det.keypoints_xyn, det.confidence,
            threshold=ASSIGN_PLAYERS_FALLBACK_THRESHOLD,
        )
        if foot_xyn is None:
            continue  # no reliable lower-body reference even at the permissive threshold
        # 3. Homography projection
        foot_m = court_mapper.to_court_meters(foot_xyn)
        if foot_m is None:
            continue  # off-court (SP1 bounds guard, CourtMapper's 2m margin)
        # 4. Tight lateral polygon — drop ball kids / line judges in the side zones
        if not (
            -ASSIGN_PLAYERS_LATERAL_MARGIN_M
            <= foot_m[0]
            <= court_mapper.court_width_m + ASSIGN_PLAYERS_LATERAL_MARGIN_M
        ):
            continue
        fallback = infer_fallback_mode(det.confidence, threshold=ASSIGN_PLAYERS_FALLBACK_THRESHOLD)
        assert fallback is not None, "robust_foot_point succeeded so infer_fallback_mode must too"
        # Mean keypoint confidence drives the within-half tiebreaker (not bbox_conf)
        mean_conf = float(np.mean(det.confidence))

        entry = (det, foot_xyn, foot_m, fallback, mean_conf)
        if foot_m[1] > NET_Y_M:
            a_candidates.append(entry)
        else:
            b_candidates.append(entry)

    def _top_conf(cands: list) -> tuple | None:
        if not cands:
            return None
        return max(cands, key=lambda e: e[4])

    a_top = _top_conf(a_candidates)
    b_top = _top_conf(b_candidates)

    return {
        "A": _to_player_detection(a_top, "A") if a_top else None,
        "B": _to_player_detection(b_top, "B") if b_top else None,
    }


def _to_player_detection(
    entry: tuple[RawDetection, tuple[float, float], tuple[float, float], FallbackMode, float],
    side: PlayerSide,
) -> PlayerDetection:
    det, foot_xyn, foot_m, fallback, _ = entry
    return PlayerDetection(
        player=side,
        keypoints_xyn=det.keypoints_xyn,
        confidence=det.confidence,
        bbox_conf=det.bbox_conf,
        feet_mid_xyn=foot_xyn,
        feet_mid_m=foot_m,
        fallback_mode=fallback,
    )


# ──────────────────────────── YOLO wrapper ────────────────────────────


class PoseExtractor:
    """Ultralytics YOLO11m-Pose wrapper with MPS safeguards + Court Half Assignment.

    Usage:
        extractor = PoseExtractor("checkpoints/yolo11m-pose.pt", "mps", court_mapper)
        players = extractor.infer(frame_bgr)  # dict[PlayerSide, PlayerDetection | None]
    """

    def __init__(
        self,
        weights: str,
        device: str,
        court_mapper: CourtMapper,
        conf: float = 0.001,
        imgsz: int = 1280,
    ) -> None:
        from ultralytics import YOLO  # lazy import to keep backend.cv.pose importable without YOLO

        self._device = device
        self._court_mapper = court_mapper
        self._model = YOLO(weights)
        self._conf = conf
        self._imgsz = imgsz
        self._frame_count = 0

    @torch.inference_mode()
    def infer(self, frame_bgr: np.ndarray) -> dict[PlayerSide, PlayerDetection | None]:
        results = self._model(
            frame_bgr,
            device=self._device,
            conf=self._conf,
            imgsz=self._imgsz,
            verbose=False,
        )

        self._frame_count += 1
        if self._frame_count % MPS_EMPTY_CACHE_EVERY_N_FRAMES == 0 and self._device == "mps":
            with contextlib.suppress(RuntimeError):
                torch.mps.empty_cache()

        raw: list[RawDetection] = []
        for r in results:
            if r.keypoints is None or r.keypoints.xyn is None or r.boxes is None:
                continue
            xyn_batch = r.keypoints.xyn.cpu().numpy()  # (N, 17, 2)
            conf_batch = (
                r.keypoints.conf.cpu().numpy()
                if r.keypoints.conf is not None
                else np.ones((xyn_batch.shape[0], 17), dtype=np.float32)
            )
            bbox_conf_batch = r.boxes.conf.cpu().numpy() if r.boxes.conf is not None else np.ones(xyn_batch.shape[0])

            for i in range(xyn_batch.shape[0]):
                raw.append(
                    RawDetection(
                        keypoints_xyn=[tuple(pt) for pt in xyn_batch[i].tolist()],
                        confidence=conf_batch[i].tolist(),
                        bbox_conf=float(bbox_conf_batch[i]),
                    )
                )

        return assign_players(raw, self._court_mapper)
