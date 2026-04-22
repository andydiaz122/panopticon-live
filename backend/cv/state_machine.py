"""Kinematic state machine for PANOPTICON LIVE.

Implements:
- USER-CORRECTION-009: 2D speed magnitude drives transitions (caller provides math.hypot(vx, vy))
- USER-CORRECTION-010: match-level coupling — server's bounce forces returner's PRE_SERVE_RITUAL

Two classes:
- PlayerStateMachine: per-player 3-state FSM (PRE_SERVE_RITUAL / ACTIVE_RALLY / DEAD_TIME)
- MatchStateMachine: wraps two PlayerStateMachines and couples them via bounce detection
"""

from __future__ import annotations

from backend.db.schema import PlayerSide, PlayerState, StateTransition

# ──────────────────────────── Tunable thresholds ────────────────────────────

ACTIVE_RALLY_SPEED_THRESHOLD_MPS: float = 0.2
"""Minimum 2D speed to enter ACTIVE_RALLY from PRE_SERVE_RITUAL (or resume from DEAD_TIME)."""

DEAD_TIME_SPEED_THRESHOLD_MPS: float = 0.05
"""Speed must stay below this to transition ACTIVE_RALLY -> DEAD_TIME."""

CONSECUTIVE_FRAMES_TO_RALLY: int = 5
"""Number of consecutive frames above ACTIVE_RALLY_SPEED_THRESHOLD to trigger the transition."""

CONSECUTIVE_FRAMES_TO_DEAD_TIME: int = 15
"""Number of consecutive frames below DEAD_TIME_SPEED_THRESHOLD to trigger the transition."""


# ──────────────────────────── PlayerStateMachine ────────────────────────────


class PlayerStateMachine:
    """Per-player 3-state FSM driven by 2D speed magnitude (USER-CORRECTION-009)."""

    def __init__(self, player: PlayerSide = "A") -> None:
        self._player = player
        self._state: PlayerState = "PRE_SERVE_RITUAL"
        self._consec_above = 0
        self._consec_below = 0
        self._pending_transitions: list[StateTransition] = []
        # Emit an "initial" transition from UNKNOWN -> PRE_SERVE_RITUAL at t=0 on first update
        self._initial_emitted = False

    @property
    def state(self) -> PlayerState:
        return self._state

    @property
    def player(self) -> PlayerSide:
        return self._player

    def update(self, speed_mps: float | None, t_ms: int) -> PlayerState:
        """Advance the FSM by one frame.

        Args:
            speed_mps: Pre-computed 2D speed magnitude (math.hypot(vx, vy)). None = no measurement.
            t_ms: Wallclock-ms timestamp.

        Returns:
            The new state after this update.
        """
        if not self._initial_emitted:
            self._pending_transitions.append(
                StateTransition(
                    timestamp_ms=t_ms,
                    player=self._player,
                    from_state="UNKNOWN",
                    to_state=self._state,
                    reason="initial",
                )
            )
            self._initial_emitted = True

        if speed_mps is None:
            # Treat missing measurement as "still" for DEAD_TIME accumulation, but DO NOT increment rally accumulator
            self._consec_below += 1
            self._consec_above = 0
        else:
            if speed_mps >= ACTIVE_RALLY_SPEED_THRESHOLD_MPS:
                self._consec_above += 1
                self._consec_below = 0
            elif speed_mps <= DEAD_TIME_SPEED_THRESHOLD_MPS:
                self._consec_below += 1
                self._consec_above = 0
            else:
                # In the "grey zone" between thresholds — reset both counters (no transition)
                self._consec_above = 0
                self._consec_below = 0

        # Transition logic
        if self._state == "PRE_SERVE_RITUAL":
            if self._consec_above >= CONSECUTIVE_FRAMES_TO_RALLY:
                self._transition_to("ACTIVE_RALLY", t_ms, reason="kinematic")
        elif self._state == "ACTIVE_RALLY":
            if self._consec_below >= CONSECUTIVE_FRAMES_TO_DEAD_TIME:
                self._transition_to("DEAD_TIME", t_ms, reason="kinematic")
        elif (
            self._state == "DEAD_TIME"
            and self._consec_above >= CONSECUTIVE_FRAMES_TO_RALLY
        ):
            # Motion during DEAD_TIME lifts us back to PRE_SERVE_RITUAL (ready to play)
            self._transition_to("PRE_SERVE_RITUAL", t_ms, reason="kinematic")
        # "UNKNOWN" state is not used after initialization

        return self._state

    def force_state(self, to_state: PlayerState, t_ms: int) -> StateTransition | None:
        """Privileged entry point for MatchStateMachine coupling (USER-CORRECTION-010).

        Directly sets the state and resets consecutive counters. Returns the emitted transition
        (or None if already in the requested state).
        """
        if self._state == to_state:
            return None
        transition = StateTransition(
            timestamp_ms=t_ms,
            player=self._player,
            from_state=self._state,
            to_state=to_state,
            reason="match_coupling",
        )
        self._state = to_state
        self._consec_above = 0
        self._consec_below = 0
        self._pending_transitions.append(transition)
        return transition

    def drain_transitions(self) -> list[StateTransition]:
        """Return and clear the queue of transitions emitted since last drain."""
        out = self._pending_transitions
        self._pending_transitions = []
        return out

    def _transition_to(self, to_state: PlayerState, t_ms: int, reason: str) -> None:
        assert reason in ("kinematic", "match_coupling", "initial")
        self._pending_transitions.append(
            StateTransition(
                timestamp_ms=t_ms,
                player=self._player,
                from_state=self._state,
                to_state=to_state,
                reason=reason,  # type: ignore[arg-type]
            )
        )
        self._state = to_state
        self._consec_above = 0
        self._consec_below = 0


# ──────────────────────────── MatchStateMachine ────────────────────────────


class MatchStateMachine:
    """Couples two PlayerStateMachines via bounce-detected match phase (USER-CORRECTION-010).

    Contract (per `match-state-coupling` skill):
      1. Each tick, both per-player FSMs update on their own kinematics first.
      2. If EITHER player emits a BOUNCE_DETECTED event, force BOTH into PRE_SERVE_RITUAL.
         (The bouncer is implicitly the server; the non-bouncer is the returner who needs to sync.)
      3. Consumers drain transitions via `drain_transitions()`.
    """

    def __init__(self) -> None:
        self._a = PlayerStateMachine(player="A")
        self._b = PlayerStateMachine(player="B")

    def update(
        self,
        a_speed_mps: float | None,
        b_speed_mps: float | None,
        a_bounce: bool,
        b_bounce: bool,
        t_ms: int,
    ) -> dict[PlayerSide, PlayerState]:
        """Advance both players one tick, applying match-level bounce coupling."""
        self._a.update(a_speed_mps, t_ms)
        self._b.update(b_speed_mps, t_ms)

        if a_bounce or b_bounce:
            # Force both into PRE_SERVE_RITUAL; the bouncer is the server, non-bouncer is returner.
            # This is the canonical USER-CORRECTION-010 coupling.
            self._a.force_state("PRE_SERVE_RITUAL", t_ms)
            self._b.force_state("PRE_SERVE_RITUAL", t_ms)

        return {"A": self._a.state, "B": self._b.state}

    def drain_transitions(self) -> list[StateTransition]:
        """Return transitions from both players since last drain, sorted by timestamp."""
        transitions = self._a.drain_transitions() + self._b.drain_transitions()
        transitions.sort(key=lambda tr: (tr.timestamp_ms, tr.player))
        return transitions

    @property
    def states(self) -> dict[PlayerSide, PlayerState]:
        return {"A": self._a.state, "B": self._b.state}
