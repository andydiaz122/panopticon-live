"""LateralWorkRate — 95th-percentile |vx| during ACTIVE_RALLY (m/s).

Fatigue indicator. Elite players trend DOWN in p95 across sets as their
explosive lateral acceleration degrades.

USER-CORRECTION-017 (physics guardrail): Kalman vx is ALREADY the ground-plane
lateral velocity in m/s — the Kalman filter runs on `robust_foot_point` which
lives on the ground plane. We therefore:

- DO NOT recompute Center of Mass from upper-body keypoints (parallax fiction).
- DO NOT project anything through CourtMapper (Z=0 homography warps non-ground
  points unboundedly).
- DO NOT manually diff position to get velocity (Kalman already fused noise).

We simply read `target_kalman[2]`, take `abs()`, and buffer during ACTIVE_RALLY.

USER-CORRECTION-013 (symmetric API): one instance per player. `opponent_kalman`
is ignored here (this signal is single-player); the compiler still passes it so
cross-player signals share the same ingest signature.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from backend.cv.signals.base import BaseSignalExtractor
from backend.db.schema import FrameKeypoints, PlayerSide, PlayerState, SignalSample


class LateralWorkRate(BaseSignalExtractor):
    """p95 of |vx| over ACTIVE_RALLY ticks, flushed per window."""

    signal_name = "lateral_work_rate"
    required_state: tuple[PlayerState, ...] = ("ACTIVE_RALLY",)

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        super().__init__(target_player, dependencies)
        self._buffer: list[float] = []

    def ingest(
        self,
        frame: FrameKeypoints,
        target_state: PlayerState,
        opponent_state: PlayerState,
        target_kalman: tuple[float, float, float, float] | None,
        opponent_kalman: tuple[float, float, float, float] | None,
        t_ms: int,
    ) -> None:
        """Append |vx| to the buffer iff ACTIVE_RALLY and target_kalman present."""
        if target_state != "ACTIVE_RALLY":
            return
        if target_kalman is None:
            return
        vx_mps = target_kalman[2]
        self._buffer.append(abs(vx_mps))

    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit p95 of the buffered |vx| values; clear buffer; return sample.

        USER-CORRECTION-022: Strict `self.deps["match_id"]` — fail LOUDLY if the
        orchestrator forgets to inject deps. Silently defaulting to "unknown"
        would corrupt the DuckDB PK `(timestamp_ms, match_id, player, signal_name)`
        and pollute downstream analysis.
        """
        if not self._buffer:
            return None
        p95 = float(np.percentile(self._buffer, 95))
        sample = SignalSample(
            timestamp_ms=t_ms,
            match_id=self.deps["match_id"],
            player=self.target_player,
            signal_name=self.signal_name,
            value=p95,
            baseline_z_score=None,
            state="ACTIVE_RALLY",
        )
        self._buffer.clear()
        return sample

    def reset(self) -> None:
        """Clear buffer on match start / between ablations."""
        super().reset()
        self._buffer.clear()
