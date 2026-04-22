"""CrouchDepth — angular drift of the player's crouch depth from match-opening baseline.

USER-CORRECTION-017 (no CourtMapper): broadcast camera tilt invalidates absolute meters.
We use a camera-invariant scalar ratio (hip→ankle distance / shoulder→hip torso) and convert
the baseline-delta to DEGREES via an arctangent. Projecting skeleton points through the Z=0
homography would warp airborne joints unboundedly; a torso-relative ratio stays well-
conditioned under camera angle changes.

Math contract:
- Per-frame during ACTIVE_RALLY, if all three required means (hip/ankle/shoulder) have
  both L+R confidences ≥ 0.3, compute:
      hip_ankle_dist = ankle_y - hip_y   (positive: ankles below hips in image coords)
      torso_scalar   = hip_y - shoulder_y (positive: shoulders above hips)
      normalized_crouch = hip_ankle_dist / torso_scalar  (dimensionless)
  else append np.nan.
- If torso_scalar < 1e-5 (collapsed skeleton / divide-by-zero), append np.nan.

Flush:
- Need ≥ 5 non-nan samples → else None.
- First flush: SET baseline = nanmean(buffer), emit value = 0.0.
- Subsequent flush: emit math.degrees(math.atan(baseline - current_mean)).
  Positive = less crouch = more upright = fatigue signature (player loses the athletic
  stance as legs fatigue). Small-angle arctangent smooths the signal and gives it a
  physically-intuitive unit (degrees of postural drift).

Lifecycle:
- flush() ALWAYS clears the per-window buffer.
- reset() clears BOTH the buffer AND the baseline (match start / between ablations).

USER-CORRECTION-022 (fail-fast): `self.deps["match_id"]` is strict — missing dep corrupts
the DuckDB PK `(timestamp_ms, match_id, player, signal_name)`. Fail LOUDLY.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from backend.cv.signals.base import BaseSignalExtractor
from backend.db.schema import (
    KP_LEFT_ANKLE,
    KP_LEFT_HIP,
    KP_LEFT_SHOULDER,
    KP_RIGHT_ANKLE,
    KP_RIGHT_HIP,
    KP_RIGHT_SHOULDER,
    FrameKeypoints,
    PlayerSide,
    PlayerState,
    SignalSample,
)

# Confidence threshold to consider a keypoint usable.
KP_CONF_THRESHOLD: float = 0.3
# Minimum non-nan samples required before a flush is meaningful.
MIN_VALID_SAMPLES: int = 5
# Below this torso scalar, the skeleton has collapsed (divide-by-zero risk).
TORSO_COLLAPSE_FLOOR: float = 1e-5


class CrouchDepth(BaseSignalExtractor):
    """Angular drift (degrees) of player's crouch depth from match-opening baseline."""

    signal_name = "crouch_depth_degradation_deg"
    required_state: tuple[PlayerState, ...] = ("ACTIVE_RALLY",)

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        super().__init__(target_player, dependencies)
        # Per-window buffer of normalized_crouch scalars (may contain np.nan).
        self._normalized_crouch: list[float] = []
        # Long-lived baseline — set on the FIRST successful flush; preserved across flushes.
        self._baseline_crouch: float | None = None

    def ingest(
        self,
        frame: FrameKeypoints,
        target_state: PlayerState,
        opponent_state: PlayerState,
        target_kalman: tuple[float, float, float, float] | None,
        opponent_kalman: tuple[float, float, float, float] | None,
        t_ms: int,
    ) -> None:
        """Append normalized_crouch (or np.nan) for this frame during ACTIVE_RALLY.

        NOTE: no CourtMapper lookup. The angular signal is camera-invariant by
        construction — torso-scalar normalization eliminates parallax scaling.
        """
        if target_state != "ACTIVE_RALLY":
            return

        detection = frame.player_a if self.target_player == "A" else frame.player_b
        if detection is None:
            self._normalized_crouch.append(float("nan"))
            return

        kpts = detection.keypoints_xyn
        confs = detection.confidence

        # Hip: mean of L/R if BOTH confident.
        if confs[KP_LEFT_HIP] >= KP_CONF_THRESHOLD and confs[KP_RIGHT_HIP] >= KP_CONF_THRESHOLD:
            hip_y = (kpts[KP_LEFT_HIP][1] + kpts[KP_RIGHT_HIP][1]) / 2.0
        else:
            hip_y = float("nan")

        # Ankle: mean of L/R if BOTH confident.
        if confs[KP_LEFT_ANKLE] >= KP_CONF_THRESHOLD and confs[KP_RIGHT_ANKLE] >= KP_CONF_THRESHOLD:
            ankle_y = (kpts[KP_LEFT_ANKLE][1] + kpts[KP_RIGHT_ANKLE][1]) / 2.0
        else:
            ankle_y = float("nan")

        # Shoulder: mean of L/R if BOTH confident.
        if confs[KP_LEFT_SHOULDER] >= KP_CONF_THRESHOLD and confs[KP_RIGHT_SHOULDER] >= KP_CONF_THRESHOLD:
            shoulder_y = (kpts[KP_LEFT_SHOULDER][1] + kpts[KP_RIGHT_SHOULDER][1]) / 2.0
        else:
            shoulder_y = float("nan")

        # Compute normalized_crouch. Any NaN propagates → NaN appended.
        hip_ankle_dist = ankle_y - hip_y
        torso_scalar = hip_y - shoulder_y

        if (
            math.isnan(hip_ankle_dist)
            or math.isnan(torso_scalar)
            or torso_scalar < TORSO_COLLAPSE_FLOOR
        ):
            self._normalized_crouch.append(float("nan"))
            return

        self._normalized_crouch.append(hip_ankle_dist / torso_scalar)

    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit a crouch_depth_degradation_deg sample or None; ALWAYS clears the per-window buffer.

        USER-CORRECTION-022: strict `self.deps["match_id"]` — fail LOUDLY if missing.
        """
        buf_arr = np.asarray(self._normalized_crouch, dtype=float)
        n_valid = int(np.sum(np.isfinite(buf_arr)))

        if n_valid < MIN_VALID_SAMPLES:
            self._normalized_crouch.clear()
            return None

        current_mean = float(np.nanmean(buf_arr))

        if self._baseline_crouch is None:
            # First flush: establish baseline and emit 0.0 degradation.
            self._baseline_crouch = current_mean
            value_deg = 0.0
        else:
            # Subsequent flush: angular degradation via arctangent.
            delta = self._baseline_crouch - current_mean
            value_deg = math.degrees(math.atan(delta))

        sample = SignalSample(
            timestamp_ms=t_ms,
            match_id=self.deps["match_id"],
            player=self.target_player,
            signal_name=self.signal_name,
            value=value_deg,
            baseline_z_score=None,
            state="ACTIVE_RALLY",
        )
        self._normalized_crouch.clear()
        return sample

    def reset(self) -> None:
        """Clear BOTH the per-window buffer AND the long-lived baseline.

        Called on match start or between ablations — a new baseline should be
        established from the FIRST rally of the new context.
        """
        super().reset()
        self._normalized_crouch.clear()
        self._baseline_crouch = None
