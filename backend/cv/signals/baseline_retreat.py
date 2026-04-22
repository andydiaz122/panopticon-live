"""BaselineRetreat — mean metres behind the player's own baseline during ACTIVE_RALLY.

USER-CORRECTION-021 (asymmetric baseline geometry):
- Player A's baseline is at y = SINGLES_COURT_LENGTH_M (= 23.77 m, far end in court coords).
- Player B's baseline is at y = 0.0 m (near end).
- A retreats in +y direction; B retreats in -y direction.
- Retreat is clamped to 0.0 when a player is inside the court (a forward position is NOT
  a "negative retreat" — it is simply zero retreat).

USER-CORRECTION-017 (no CourtMapper): `target_kalman[1]` is ALREADY in court meters —
the Kalman filter runs on `robust_foot_point` which lives on the ground plane.
Re-projecting through CourtMapper.to_court_meters() would be a round-trip error source
and violate the "homography is Z=0 only" invariant. The Kalman state IS the canonical
ground-plane y-coordinate; we use it directly.

(The CourtMapper is technically passable via `self.deps["court_mapper"]` for API
uniformity across signals, but this extractor DOES NOT use it — Kalman y is authoritative.)

USER-CORRECTION-022 (fail-fast): `self.deps["match_id"]` is strict; a missing dep
corrupts the DuckDB PK — fail LOUDLY, never silently default to "unknown".
"""

from __future__ import annotations

from typing import Any

from backend.cv.signals.base import BaseSignalExtractor
from backend.db.schema import (
    SINGLES_COURT_LENGTH_M,
    FrameKeypoints,
    PlayerSide,
    PlayerState,
    SignalSample,
)


class BaselineRetreat(BaseSignalExtractor):
    """Mean metres behind the player's own baseline over ACTIVE_RALLY ticks."""

    signal_name = "baseline_retreat_distance_m"
    required_state: tuple[PlayerState, ...] = ("ACTIVE_RALLY",)

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        super().__init__(target_player, dependencies)
        # Per-window buffer of retreat scalars (each ≥ 0.0 by construction).
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
        """Append the (clamped-nonnegative) retreat distance for this frame.

        Uses `target_kalman[1]` directly — Kalman y is already in court meters from
        `robust_foot_point` (which lives on the ground plane). NO CourtMapper call.
        """
        if target_state != "ACTIVE_RALLY":
            return
        if target_kalman is None:
            return

        y_m = target_kalman[1]

        if self.target_player == "A":
            # A's baseline at y = SINGLES_COURT_LENGTH_M; retreat in +y.
            retreat_m = max(0.0, y_m - SINGLES_COURT_LENGTH_M)
        else:
            # B's baseline at y = 0.0; retreat in -y.
            retreat_m = max(0.0, -y_m)

        self._buffer.append(retreat_m)

    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit mean retreat in metres; ALWAYS clears buffer.

        USER-CORRECTION-022: strict `self.deps["match_id"]` — fail LOUDLY if missing.
        """
        if not self._buffer:
            return None

        mean_retreat_m = sum(self._buffer) / len(self._buffer)

        sample = SignalSample(
            timestamp_ms=t_ms,
            match_id=self.deps["match_id"],
            player=self.target_player,
            signal_name=self.signal_name,
            value=mean_retreat_m,
            baseline_z_score=None,
            state="ACTIVE_RALLY",
        )
        self._buffer.clear()
        return sample

    def reset(self) -> None:
        """Clear buffer on match start / between ablations."""
        super().reset()
        self._buffer.clear()
