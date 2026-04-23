"""SplitStepLatency — Player A's ritual-to-burst cadence (ms).

Post-GOTCHA-021 + USER-CORRECTION-025 (Founder Override #1, 2026-04-23):
The signal is anchored ENTIRELY on Player A's own kinematic timeline.
The previous "ghost opponent" implementation (latency between opponent's
serve-commit and target's burst) is purged — it was logically impossible
given DECISION-008 (single-player scope) + GOTCHA-016 (Player B often
undetectable on broadcast tennis clips).

New definition:
  split_step_latency_ms = (t_ms_player_a_entered_ACTIVE_RALLY)
                        - (t_ms_player_a_entered_PRE_SERVE_RITUAL)

Semantically: how long Player A spent in their pre-serve ritual before
committing to movement. Works uniformly whether Player A is server or returner.
The `opponent_state` argument to `ingest` is retained for ABC-signature
compatibility with BaseSignalExtractor, but is NEVER read by this extractor.

USER-CORRECTION-019 (physics guardrail) still applies: use the MatchStateMachine
transitions as smoothed proxies for motion-onset events instead of hunting raw
keypoint velocity peaks.

USER-CORRECTION-022 (fail-fast): `self.deps["match_id"]` is strict; missing
dep corrupts the DuckDB PK — fail LOUDLY.
"""

from __future__ import annotations

from typing import Any

from backend.cv.signals.base import BaseSignalExtractor
from backend.db.schema import FrameKeypoints, PlayerSide, PlayerState, SignalSample


class SplitStepLatency(BaseSignalExtractor):
    """Emits latency_ms between Player A entering PRE_SERVE_RITUAL and their
    subsequent transition to ACTIVE_RALLY. Opponent state is NOT consulted."""

    signal_name = "split_step_latency_ms"
    # Both observed so ingest sees the PRE→ACTIVE boundary regardless of which
    # side of it the current frame lands on.
    required_state: tuple[PlayerState, ...] = ("PRE_SERVE_RITUAL", "ACTIVE_RALLY")

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        super().__init__(target_player, dependencies)
        self._last_target_state: PlayerState | None = None
        # Timestamp at which Player A entered PRE_SERVE_RITUAL from another state.
        # Consumed on the subsequent PRE→ACTIVE transition, then cleared.
        self._entered_pre_serve_t_ms: int | None = None
        # Pending latency (ms), set at the PRE→ACTIVE edge and consumed by flush().
        self._pending_latency_ms: float | None = None

    def ingest(
        self,
        frame: FrameKeypoints,
        target_state: PlayerState,
        opponent_state: PlayerState,
        target_kalman: tuple[float, float, float, float] | None,
        opponent_kalman: tuple[float, float, float, float] | None,
        t_ms: int,
    ) -> None:
        """Track Player A's own PRE_SERVE_RITUAL entry + subsequent burst edge.

        opponent_state / opponent_kalman / target_kalman are present in the
        signature for ABC compatibility; this extractor is state-only and
        ignores them (purged Ghost Opponent dependency).
        """
        # Mark the moment Player A ENTERS PRE_SERVE_RITUAL from anywhere else.
        # Simultaneous transitions at the first-observed frame (last_state is None)
        # still count — the CV pipeline often starts mid-match with the first
        # observed state already PRE_SERVE.
        if (
            self._last_target_state != "PRE_SERVE_RITUAL"
            and target_state == "PRE_SERVE_RITUAL"
        ):
            self._entered_pre_serve_t_ms = t_ms

        # Detect the ritual-to-burst edge: PRE → ACTIVE. Compute latency iff
        # we actually observed the PRE entry (prevents spurious emission on
        # DEAD_TIME → ACTIVE or UNKNOWN → ACTIVE paths).
        if (
            self._last_target_state == "PRE_SERVE_RITUAL"
            and target_state == "ACTIVE_RALLY"
            and self._entered_pre_serve_t_ms is not None
        ):
            self._pending_latency_ms = float(t_ms - self._entered_pre_serve_t_ms)
            self._entered_pre_serve_t_ms = None

        self._last_target_state = target_state

    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit the pending latency (if any); always clears pending state."""
        if self._pending_latency_ms is None:
            return None
        latency_ms = self._pending_latency_ms
        self._pending_latency_ms = None
        return SignalSample(
            timestamp_ms=t_ms,
            match_id=self.deps["match_id"],  # fail-fast per USER-CORRECTION-022
            player=self.target_player,
            signal_name=self.signal_name,
            value=latency_ms,
            baseline_z_score=None,
            state="ACTIVE_RALLY",
        )

    def reset(self) -> None:
        """Clear all tracked state — match start / between ablations."""
        super().reset()
        self._last_target_state = None
        self._entered_pre_serve_t_ms = None
        self._pending_latency_ms = None
