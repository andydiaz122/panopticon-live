"""RitualEntropy — Lomb-Scargle spectral entropy delta of pre-serve wrist cadence.

Definition: during a player's PRE_SERVE_RITUAL window, sample the relative
wrist height (`wrist_y - hip_y`). On flush, compute a Lomb-Scargle periodogram
over 0.5-5.0 Hz and take the Shannon entropy of the normalized power spectrum.
The FIRST successful flush becomes the player's match-opening baseline and
emits `value = 0.0`. Every subsequent flush emits `value = entropy - baseline`
— the delta from the player's own early-match rhythm.

Rationale: a pro's pre-serve bounce cadence is highly periodic (one dominant
tempo, low entropy). Under mental-game pressure or fatigue, the cadence
destabilizes — more distributed power → higher entropy. The delta normalizes
for player idiosyncrasy (some players have slow, deliberate bounces; others
rapid patter) by referencing their own baseline.

USER-CORRECTION-012 (relative kinematics): use `wrist_y - hip_y`, not raw
`wrist_y`. Player height and framing otherwise contaminate the signal.

USER-CORRECTION-014 (ambidextrous wrist): among (left wrist, right wrist)
candidates with conf ≥ 0.3, pick the max-y (lowest on screen, dominant arm
during the bounce phase).

USER-CORRECTION-015 (variance floor): if `np.nanvar(rel_y) < 1e-5`, return
None. A zero-variance buffer has no rhythm to measure.

USER-CORRECTION-017 (no CourtMapper): wrists during the bounce are close to
the ball plane but above the ground; Z=0 homography would lie.

USER-CORRECTION-022 (fail-fast): `self.deps["match_id"]` is strict — missing
dep corrupts the DuckDB PK; fail LOUDLY.

Implementation notes:
- Time array is in seconds (NOT ms) — Lomb-Scargle frequencies are in rad/s
  (convert Hz via multiplying by 2 pi). Non-uniform sampling is why we use Lomb-Scargle
  instead of an FFT: YOLO/occlusion introduces missing frames.
- Before calling `scipy.signal.lombscargle`, mask to ONLY finite (t, y) pairs;
  lombscargle cannot tolerate NaNs.
- Baseline persists across flushes; it is cleared only by `reset()`.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.signal import lombscargle

from backend.cv.signals.base import BaseSignalExtractor
from backend.db.schema import FrameKeypoints, PlayerSide, PlayerState, SignalSample

# Frequency grid for Lomb-Scargle (Hz). 0.5-5.0 covers realistic pre-serve bounce tempos.
_FREQS_HZ: np.ndarray = np.linspace(0.5, 5.0, 100)
_FREQS_RAD: np.ndarray = _FREQS_HZ * (2.0 * np.pi)

MIN_SAMPLES: int = 10
KP_CONF_THRESHOLD: float = 0.3
VARIANCE_FLOOR: float = 1e-5


class RitualEntropy(BaseSignalExtractor):
    """Spectral entropy delta of pre-serve wrist cadence."""

    signal_name = "ritual_entropy_delta"
    required_state: tuple[PlayerState, ...] = ("PRE_SERVE_RITUAL",)

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        super().__init__(target_player, dependencies)
        self._rel_y: list[float] = []
        self._t_s: list[float] = []
        self._baseline_entropy: float | None = None

    def ingest(
        self,
        frame: FrameKeypoints,
        target_state: PlayerState,
        opponent_state: PlayerState,
        target_kalman: tuple[float, float, float, float] | None,
        opponent_kalman: tuple[float, float, float, float] | None,
        t_ms: int,
    ) -> None:
        """Append (t_s, wrist_rel_y) for this PRE_SERVE_RITUAL frame."""
        if target_state != "PRE_SERVE_RITUAL":
            return

        detection = frame.player_a if self.target_player == "A" else frame.player_b
        if detection is None:
            self._rel_y.append(float("nan"))
            self._t_s.append(t_ms / 1000.0)
            return

        kpts = detection.keypoints_xyn
        confs = detection.confidence

        # Ambidextrous wrist: pick max-y among confident candidates.
        wrist_candidates: list[float] = []
        if confs[9] >= KP_CONF_THRESHOLD:
            wrist_candidates.append(kpts[9][1])
        if confs[10] >= KP_CONF_THRESHOLD:
            wrist_candidates.append(kpts[10][1])
        wrist_y = max(wrist_candidates) if wrist_candidates else float("nan")

        # Hip: mean L/R when both confident.
        if confs[11] >= KP_CONF_THRESHOLD and confs[12] >= KP_CONF_THRESHOLD:
            hip_y = (kpts[11][1] + kpts[12][1]) / 2.0
        else:
            hip_y = float("nan")

        self._rel_y.append(wrist_y - hip_y)
        self._t_s.append(t_ms / 1000.0)

    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit ritual_entropy_delta (entropy - baseline). First successful emit = baseline (0.0)."""
        y_arr = np.asarray(self._rel_y, dtype=float)
        t_arr = np.asarray(self._t_s, dtype=float)

        # Filter to finite (t, y) pairs before lombscargle.
        finite_mask = np.isfinite(y_arr) & np.isfinite(t_arr)
        y_clean = y_arr[finite_mask]
        t_clean = t_arr[finite_mask]

        if y_clean.size < MIN_SAMPLES:
            self._rel_y.clear()
            self._t_s.clear()
            return None

        if float(np.var(y_clean)) < VARIANCE_FLOOR:
            self._rel_y.clear()
            self._t_s.clear()
            return None

        # Lomb-Scargle periodogram (normalize=True → unit-area power spectrum).
        power = lombscargle(t_clean, y_clean, _FREQS_RAD, normalize=True)
        # Normalize power to a probability distribution for Shannon entropy.
        total = float(power.sum())
        if total <= 0.0:
            self._rel_y.clear()
            self._t_s.clear()
            return None
        p = power / total
        spectral_entropy = float(-np.sum(p * np.log(p + 1e-10)))

        # First successful emit establishes baseline; value = 0.0.
        if self._baseline_entropy is None:
            self._baseline_entropy = spectral_entropy
            delta = 0.0
        else:
            delta = spectral_entropy - self._baseline_entropy

        sample = SignalSample(
            timestamp_ms=t_ms,
            match_id=self.deps["match_id"],
            player=self.target_player,
            signal_name=self.signal_name,
            value=delta,
            baseline_z_score=None,
            state="PRE_SERVE_RITUAL",
        )
        self._rel_y.clear()
        self._t_s.clear()
        return sample

    def reset(self) -> None:
        """Clear both buffers AND the baseline — match start / between ablations."""
        super().reset()
        self._rel_y.clear()
        self._t_s.clear()
        self._baseline_entropy = None
