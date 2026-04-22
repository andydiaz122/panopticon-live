"""ServeTossVariance — std-dev of pre-serve wrist-apex height, in centimeters.

USER-CORRECTION-020 (math): variance of the wrist-apex height during the
PRE_SERVE_RITUAL window, converted from normalized image coordinates to
centimeters via the torso scalar (shoulder-hip span ≈ 60 cm).

USER-CORRECTION-012 (relative kinematics): the signal uses `wrist_y - hip_y`,
NEVER raw `wrist_y`. Player height, camera distance, and vertical framing all
shift raw `wrist_y` without any biomechanical change — relative-to-hip isolates
the true toss geometry.

USER-CORRECTION-014 (ambidextrous wrist): among (left wrist, right wrist)
candidates, keep those with confidence >= 0.3, and choose the one with the MAX
y (lowest screen position). At toss apex the tossing wrist is high (small y),
so later in the window the dominant wrist will have larger y as it descends —
but the more reliable sampling is the chosen arm's path. Picking max-y per
frame biases toward the wrist closest to the ball at bounce/impact moments.

USER-CORRECTION-015 (variance floor): if `np.nanstd(rel_y) < 1e-5`, return
None. A stationary wrist is not a "zero-variance toss" — it is either phantom
or fully occluded noise; emitting 0.0 would pollute the anomaly baseline.

USER-CORRECTION-017 (no CourtMapper): wrists are airborne at apex. Z=0
homography would project them wildly; torso span is the biological ruler that
stays well-conditioned under camera angle changes.

USER-CORRECTION-020 (amplitude floor): on flush, if
`np.nanmax(rel_y) - np.nanmin(rel_y) < 0.05`, return None. A returner's
wrist-jitter during opponent's PRE_SERVE produces nonzero variance but tiny
amplitude; the 0.05 normalized floor filters those out.

USER-CORRECTION-022 (fail-fast): `self.deps["match_id"]` is strict — missing
dep corrupts the DuckDB PK; fail LOUDLY.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from backend.cv.signals.base import BaseSignalExtractor
from backend.db.schema import FrameKeypoints, PlayerSide, PlayerState, SignalSample

# Minimum per-buffer non-nan count before a variance/torso estimate is meaningful.
MIN_VALID_SAMPLES: int = 5
# Confidence threshold to consider a keypoint usable.
KP_CONF_THRESHOLD: float = 0.3
# Below this normalized wrist std, consider the signal numerically zero and drop.
VARIANCE_FLOOR: float = 1e-5
# Below this normalized wrist amplitude (max - min), consider the ritual a phantom serve.
AMPLITUDE_FLOOR: float = 0.05
# Biological ruler: torso (shoulder→hip span) assumed 60 cm for the conversion.
TORSO_LENGTH_CM: float = 60.0


class ServeTossVariance(BaseSignalExtractor):
    """Std-dev of pre-serve wrist-apex height in cm, via torso-scalar calibration."""

    signal_name = "serve_toss_variance_cm"
    required_state: tuple[PlayerState, ...] = ("PRE_SERVE_RITUAL",)

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        super().__init__(target_player, dependencies)
        self._wrist_rel_y: list[float] = []
        self._torso_abs_norm: list[float] = []

    def ingest(
        self,
        frame: FrameKeypoints,
        target_state: PlayerState,
        opponent_state: PlayerState,
        target_kalman: tuple[float, float, float, float] | None,
        opponent_kalman: tuple[float, float, float, float] | None,
        t_ms: int,
    ) -> None:
        """Append (wrist_rel_y, torso_abs_norm) for this frame during PRE_SERVE_RITUAL."""
        if target_state != "PRE_SERVE_RITUAL":
            return

        detection = frame.player_a if self.target_player == "A" else frame.player_b
        if detection is None:
            self._wrist_rel_y.append(float("nan"))
            self._torso_abs_norm.append(float("nan"))
            return

        kpts = detection.keypoints_xyn
        confs = detection.confidence

        # Ambidextrous wrist: collect confident L/R candidates, pick max-y.
        wrist_candidates: list[float] = []
        if confs[9] >= KP_CONF_THRESHOLD:
            wrist_candidates.append(kpts[9][1])
        if confs[10] >= KP_CONF_THRESHOLD:
            wrist_candidates.append(kpts[10][1])
        wrist_y = max(wrist_candidates) if wrist_candidates else float("nan")

        # Hip: mean of L/R if BOTH confident (USER-CORRECTION-012: not-confident → NaN).
        if confs[11] >= KP_CONF_THRESHOLD and confs[12] >= KP_CONF_THRESHOLD:
            hip_y = (kpts[11][1] + kpts[12][1]) / 2.0
        else:
            hip_y = float("nan")

        # Shoulder: same symmetric treatment; only needed for torso span.
        if confs[5] >= KP_CONF_THRESHOLD and confs[6] >= KP_CONF_THRESHOLD:
            shoulder_y = (kpts[5][1] + kpts[6][1]) / 2.0
        else:
            shoulder_y = float("nan")

        # Relative wrist (y-up is smaller-y; sign doesn't matter for variance).
        self._wrist_rel_y.append(wrist_y - hip_y)
        self._torso_abs_norm.append(abs(shoulder_y - hip_y))

    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit serve_toss_variance_cm; return None when any guard trips. Always clears buffers."""
        wrist_arr = np.asarray(self._wrist_rel_y, dtype=float)
        torso_arr = np.asarray(self._torso_abs_norm, dtype=float)

        # Guard 1: minimum samples in each buffer.
        if int(np.sum(np.isfinite(wrist_arr))) < MIN_VALID_SAMPLES:
            self._wrist_rel_y.clear()
            self._torso_abs_norm.clear()
            return None
        if int(np.sum(np.isfinite(torso_arr))) < MIN_VALID_SAMPLES:
            self._wrist_rel_y.clear()
            self._torso_abs_norm.clear()
            return None

        # Guard 2: amplitude floor (phantom-serve filter).
        amplitude = float(np.nanmax(wrist_arr) - np.nanmin(wrist_arr))
        if amplitude < AMPLITUDE_FLOOR:
            self._wrist_rel_y.clear()
            self._torso_abs_norm.clear()
            return None

        # Guard 3: variance floor.
        std_norm = float(np.nanstd(wrist_arr))
        if std_norm < VARIANCE_FLOOR:
            self._wrist_rel_y.clear()
            self._torso_abs_norm.clear()
            return None

        # Guard 4: torso collapse (divide-by-zero).
        mean_torso_norm = float(np.nanmean(torso_arr))
        if mean_torso_norm < VARIANCE_FLOOR:
            self._wrist_rel_y.clear()
            self._torso_abs_norm.clear()
            return None

        # Biological ruler conversion.
        variance_cm = std_norm * (TORSO_LENGTH_CM / mean_torso_norm)

        sample = SignalSample(
            timestamp_ms=t_ms,
            match_id=self.deps["match_id"],
            player=self.target_player,
            signal_name=self.signal_name,
            value=variance_cm,
            baseline_z_score=None,
            state="PRE_SERVE_RITUAL",
        )
        self._wrist_rel_y.clear()
        self._torso_abs_norm.clear()
        return sample

    def reset(self) -> None:
        """Clear buffers on match start / between ablations."""
        super().reset()
        self._wrist_rel_y.clear()
        self._torso_abs_norm.clear()
