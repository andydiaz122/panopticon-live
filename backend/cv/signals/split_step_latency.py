"""SplitStepLatency — returner reaction time (ms) from serve contact to first committed motion.

USER-CORRECTION-019 (physics guardrail): DO NOT hunt raw keypoint wrist-peak
velocity — that derivative is noise-dominated and produces garbage. INSTEAD, use
the MatchStateMachine transitions as smoothed proxies:

  opponent: PRE_SERVE_RITUAL → ACTIVE_RALLY  ≈ serve contact (server committed)
  target:   PRE_SERVE_RITUAL → ACTIVE_RALLY  ≈ returner commits to moving

split_step_latency_ms = target_entered_t_ms - opponent_entered_t_ms

Server-side discipline: if target transitions FIRST, this instance represents the
server, not the returner — return None. The opposite instance (target = other
player) will detect the valid returner event.

USER-CORRECTION-022 (fail-fast): `self.deps["match_id"]` is strict; missing
dep corrupts the DuckDB PK — fail LOUDLY.
"""

from __future__ import annotations

from typing import Any

from backend.cv.signals.base import BaseSignalExtractor
from backend.db.schema import FrameKeypoints, PlayerSide, PlayerState, SignalSample


class SplitStepLatency(BaseSignalExtractor):
    """Emits latency_ms between server commit and returner commit — returner-side only."""

    signal_name = "split_step_latency_ms"
    # Both states observed so transitions can be caught (PRE_SERVE → ACTIVE edge).
    required_state: tuple[PlayerState, ...] = ("PRE_SERVE_RITUAL", "ACTIVE_RALLY")

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        super().__init__(target_player, dependencies)
        self._last_target_state: PlayerState | None = None
        self._last_opponent_state: PlayerState | None = None
        self._opp_entered_active_t_ms: int | None = None
        self._target_entered_active_t_ms: int | None = None

    def ingest(
        self,
        frame: FrameKeypoints,
        target_state: PlayerState,
        opponent_state: PlayerState,
        target_kalman: tuple[float, float, float, float] | None,
        opponent_kalman: tuple[float, float, float, float] | None,
        t_ms: int,
    ) -> None:
        """Detect PRE_SERVE → ACTIVE_RALLY transitions for opponent and target.

        When the opponent transitions first, it signals a new serve → reset the
        target timestamp so the returner's transition in this rally is what
        measures the latency.
        """
        # Opponent: PRE_SERVE_RITUAL → ACTIVE_RALLY. Mark serve commit and start
        # a fresh rally window (clear any stale target timestamp).
        if (
            self._last_opponent_state == "PRE_SERVE_RITUAL"
            and opponent_state == "ACTIVE_RALLY"
        ):
            self._opp_entered_active_t_ms = t_ms
            self._target_entered_active_t_ms = None

        # Target: PRE_SERVE_RITUAL → ACTIVE_RALLY. Mark returner commit.
        if (
            self._last_target_state == "PRE_SERVE_RITUAL"
            and target_state == "ACTIVE_RALLY"
        ):
            self._target_entered_active_t_ms = t_ms

        self._last_target_state = target_state
        self._last_opponent_state = opponent_state

    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit split_step_latency_ms iff BOTH transitioned AND opponent was first."""
        opp_t = self._opp_entered_active_t_ms
        tgt_t = self._target_entered_active_t_ms

        if opp_t is None or tgt_t is None:
            return None
        if tgt_t < opp_t:
            # Target moved first → this side is the server, not the returner. Drop.
            self._opp_entered_active_t_ms = None
            self._target_entered_active_t_ms = None
            return None

        latency_ms = float(tgt_t - opp_t)
        sample = SignalSample(
            timestamp_ms=t_ms,
            match_id=self.deps["match_id"],
            player=self.target_player,
            signal_name=self.signal_name,
            value=latency_ms,
            baseline_z_score=None,
            state="ACTIVE_RALLY",
        )
        # Reset both timestamps — next rally starts fresh.
        self._opp_entered_active_t_ms = None
        self._target_entered_active_t_ms = None
        return sample

    def reset(self) -> None:
        """Clear all tracked state — match start / between ablations."""
        super().reset()
        self._last_target_state = None
        self._last_opponent_state = None
        self._opp_entered_active_t_ms = None
        self._target_entered_active_t_ms = None
