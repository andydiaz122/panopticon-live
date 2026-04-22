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
"""Minimum per-keypoint confidence before we fall back to the next body segment."""

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

    Algorithm (canonical per topological-identity-stability skill):
      1. For each detection, compute robust foot point (ankle -> knee -> hip fallback).
      2. Project the foot point to court meters; discard if off-court.
      3. Split by net line: y_m > NET_Y_M = Player A's half; y_m <= NET_Y_M = Player B's.
      4. Within each half, pick the detection with highest mean keypoint confidence.

    Immune to occlusion-induced identity swapping: a linesman with high bbox_conf on
    Player A's half cannot steal Player B's identity.
    """
    a_candidates: list[tuple[RawDetection, tuple[float, float], tuple[float, float], FallbackMode, float]] = []
    b_candidates: list[tuple[RawDetection, tuple[float, float], tuple[float, float], FallbackMode, float]] = []

    for det in raw_detections:
        foot_xyn = robust_foot_point(det.keypoints_xyn, det.confidence)
        if foot_xyn is None:
            continue  # no reliable lower-body reference
        foot_m = court_mapper.to_court_meters(foot_xyn)
        if foot_m is None:
            continue  # off-court (SP1 bounds guard)
        fallback = infer_fallback_mode(det.confidence)
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
