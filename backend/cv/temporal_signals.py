"""Temporal kinematic primitives that run BEFORE the MatchStateMachine each tick.

Implements USER-CORRECTION-013 (Bounce Deadlock resolution):
    The MatchStateMachine needs bounce-detected events to transition both players
    into PRE_SERVE_RITUAL. But signal extractors (which might compute bounce as a
    byproduct) only run AFTER state transitions. That's a Chicken-and-Egg deadlock.
    The resolution is a continuous rolling primitive that runs UNCONDITIONALLY
    every frame, independent of the state machine.

Implements USER-CORRECTION-012 (Camera-Pan Aliasing):
    Broadcast cameras pan/tilt during serves. The raw `wrist_y` coordinate carries
    both biomechanical motion AND camera motion superposed. Operating on the
    difference `wrist_y - hip_y` (relative kinematics) removes the camera's
    common-mode drift, leaving pure arm-swing oscillation.

Implements USER-CORRECTION-014 (Null-Safety + Ambidextrous Wrist):
    YOLO keypoints can be None (occlusion) or low-confidence. We ingest np.nan for
    missing measurements and use np.nan{var,max,min,mean} to evaluate the buffer
    gracefully. Ambidextrous wrist selection picks the confident wrist with the
    lower screen position (max y), which is the wrist closer to the ball at bounce.

Implements USER-CORRECTION-015 (Zero-Variance Guard):
    Buffers with ~zero variance (still player, all NaN, or initializing) cannot
    report meaningful spectral content. A variance floor of 1e-5 (below YOLO
    keypoint noise) short-circuits to "no bounce" and prevents division-by-zero in
    downstream Lomb-Scargle computations.
"""

from __future__ import annotations

import math
from collections import deque

import numpy as np


class RollingBounceDetector:
    """Continuous bounce-event detector on relative wrist-Y (USER-CORRECTION-013)."""

    WINDOW_FRAMES: int = 90
    """Rolling-buffer depth: ~3 seconds at 30 fps (captures 3-4 bounces at 1 Hz)."""

    AMP_THRESHOLD_REL: float = 0.02
    """Minimum relative-y amplitude for a bounce signature (~2% of frame height)."""

    BOUNCE_PERIOD_RANGE_S: tuple[float, float] = (0.25, 1.5)
    """Physically plausible tennis bounce period: 0.25-1.5 s (~0.67-4 Hz)."""

    MIN_SAMPLES: int = 10
    """Below this many samples the detector cannot decide."""

    VARIANCE_FLOOR: float = 1e-5
    """Below this, relative-y is effectively constant → no spectral content."""

    WRIST_CONF_THRESHOLD: float = 0.3
    """YOLO confidence below this is treated as occluded."""

    def __init__(self, fps: float = 30.0) -> None:
        self._fps = fps
        self._bufs: dict[str, deque[float]] = {
            "A": deque(maxlen=self.WINDOW_FRAMES),
            "B": deque(maxlen=self.WINDOW_FRAMES),
        }

    @property
    def _buf_a(self) -> deque[float]:
        return self._bufs["A"]

    @property
    def _buf_b(self) -> deque[float]:
        return self._bufs["B"]

    def ingest_player_frame(
        self,
        buffer_key: str,
        left_wrist_y: float | None,
        left_wrist_conf: float | None,
        right_wrist_y: float | None,
        right_wrist_conf: float | None,
        hip_y: float | None,
        hip_conf: float | None,
    ) -> None:
        """Append one frame's relative-y to the rolling buffer.

        Appends np.nan when:
          - No confident wrist is available
          - Hip is occluded or low-confidence
          - Either input is None

        Raises KeyError on unknown buffer_key (not silently routed).
        """
        chosen_wrist_y = self._pick_wrist(left_wrist_y, left_wrist_conf, right_wrist_y, right_wrist_conf)
        if chosen_wrist_y is None or hip_y is None or (hip_conf or 0.0) < self.WRIST_CONF_THRESHOLD:
            rel_y = float("nan")
        else:
            rel_y = chosen_wrist_y - hip_y
        self._bufs[buffer_key].append(rel_y)

    def evaluate(self) -> tuple[bool, bool]:
        """Return (a_bounce, b_bounce) — True if buffer holds a recent bounce signature."""
        return (self._has_bounce(self._buf_a), self._has_bounce(self._buf_b))

    def reset(self) -> None:
        """Clear both player buffers (e.g., at match start or between ablations)."""
        for buf in self._bufs.values():
            buf.clear()

    # ──────────────────────────── Internals ────────────────────────────

    def _pick_wrist(
        self,
        left_y: float | None,
        left_conf: float | None,
        right_y: float | None,
        right_conf: float | None,
    ) -> float | None:
        """Return the confident wrist with the lower screen position (max y).

        Tennis ball at bounce is BELOW the hand path origin; the tossing/receiving wrist
        temporarily reaches its lowest screen position (highest y in image coords). Picking
        max-y among confident wrists is a stable ambidextrous heuristic.
        """
        candidates: list[float] = []
        if left_y is not None and (left_conf or 0.0) >= self.WRIST_CONF_THRESHOLD:
            candidates.append(left_y)
        if right_y is not None and (right_conf or 0.0) >= self.WRIST_CONF_THRESHOLD:
            candidates.append(right_y)
        return max(candidates) if candidates else None

    def _has_bounce(self, buf: deque[float]) -> bool:
        if len(buf) < self.MIN_SAMPLES:
            return False
        arr = np.asarray(buf, dtype=float)

        # Early exit: all-NaN buffer cannot decide (also silences nanvar DoF warning).
        non_nan_count = int(np.sum(~np.isnan(arr)))
        if non_nan_count < self.MIN_SAMPLES:
            return False

        # Zero-variance guard (USER-CORRECTION-015)
        var = float(np.nanvar(arr))
        if not math.isfinite(var) or var < self.VARIANCE_FLOOR:
            return False

        # Amplitude gate (relative units)
        amp_max = np.nanmax(arr)
        amp_min = np.nanmin(arr)
        if not (math.isfinite(float(amp_max)) and math.isfinite(float(amp_min))):
            return False
        amplitude = float(amp_max - amp_min)
        if amplitude < self.AMP_THRESHOLD_REL:
            return False

        # Period check via mean-crossings
        mean = float(np.nanmean(arr))
        crossings = _count_mean_crossings(arr, mean)
        if crossings == 0:
            return False
        # Each full cycle has 2 mean crossings; implied period = duration / cycles
        valid_samples = int(np.sum(~np.isnan(arr)))
        if valid_samples < self.MIN_SAMPLES:
            return False
        duration_s = valid_samples / self._fps
        cycles = max(crossings / 2.0, 1.0)
        implied_period_s = duration_s / cycles
        lo, hi = self.BOUNCE_PERIOD_RANGE_S
        return lo <= implied_period_s <= hi


def _count_mean_crossings(arr: np.ndarray, mean: float) -> int:
    """Count how many times the series crosses the mean (NaN-safe)."""
    signs = np.sign(arr - mean)
    # Treat zeros as "no crossing direction" — drop them for robust sign comparison.
    signs_no_zero = signs[np.logical_and(signs != 0, ~np.isnan(signs))]
    if signs_no_zero.size < 2:
        return 0
    flips = np.sum(signs_no_zero[1:] != signs_no_zero[:-1])
    return int(flips)
