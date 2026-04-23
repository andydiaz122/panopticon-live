"""Kinematic state machine for PANOPTICON LIVE.

Implements:
- USER-CORRECTION-009: 2D speed magnitude drives transitions (caller provides math.hypot(vx, vy))
- USER-CORRECTION-010: match-level coupling — server's bounce forces returner's PRE_SERVE_RITUAL

Two classes:
- PlayerStateMachine: per-player 3-state FSM (PRE_SERVE_RITUAL / ACTIVE_RALLY / DEAD_TIME)
- MatchStateMachine: wraps two PlayerStateMachines and couples them via bounce detection
"""

from __future__ import annotations

from backend.cv.thresholds import KINEMATIC
from backend.db.schema import PlayerSide, PlayerState, StateTransition

# ──────────────────────────── Tunable thresholds (PATTERN-057) ────────────────────────────
#
# All kinematic gates are sourced from `backend/cv/thresholds.py::KINEMATIC`.
# The module-level names below are thin re-exports preserved for backward
# compatibility with existing imports + tests. When re-tuning on post-RTS
# telemetry, edit `thresholds.py` — never shadow here.

ACTIVE_RALLY_SPEED_THRESHOLD_MPS: float = KINEMATIC.active_rally_speed_mps
"""Minimum 2D speed to enter ACTIVE_RALLY from PRE_SERVE_RITUAL (or resume from DEAD_TIME)."""

DEAD_TIME_SPEED_THRESHOLD_MPS: float = KINEMATIC.dead_time_speed_mps
"""Speed must stay below this to transition ACTIVE_RALLY -> DEAD_TIME."""

CONSECUTIVE_FRAMES_TO_RALLY: int = KINEMATIC.consecutive_frames_to_rally
"""Number of consecutive frames above ACTIVE_RALLY_SPEED_THRESHOLD to trigger the transition."""

CONSECUTIVE_FRAMES_TO_DEAD_TIME: int = KINEMATIC.consecutive_frames_to_dead_time
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
    """Couples two PlayerStateMachines via match-level events.

    Contract (per `match-state-coupling` skill):
      1. Each tick, both per-player FSMs update on their own kinematics first.
      2. USER-CORRECTION-011 (Conditional DEAD_TIME uncoupling): if EITHER player transitions
         into DEAD_TIME this tick AND the opponent is in PRE_SERVE_RITUAL (the Ace/Fault
         deadlock — standing still, never moved), force the opponent into DEAD_TIME.
         CRITICAL: only rescue PRE_SERVE_RITUAL opponents — NEVER force ACTIVE_RALLY
         opponents into DEAD_TIME, as that would truncate their legitimate deceleration
         curve and destroy recovery_latency_ms + lateral_work_rate.
      3. USER-CORRECTION-010 + PATTERN-053 (edge-triggered bounce coupling):
         RollingBounceDetector.evaluate() is a pure spectral probe over a ~3s rolling
         buffer — it returns True every frame while a bounce signature lives in the
         buffer. We must couple only on the RISING EDGE (False → True) per player,
         not on every True tick. Otherwise continuous True pins the FSM in
         PRE_SERVE_RITUAL for the entire signature window, across the actual rally.
      4. Consumers drain transitions via `drain_transitions()`.
    """

    def __init__(self) -> None:
        self._a = PlayerStateMachine(player="A")
        self._b = PlayerStateMachine(player="B")
        # PATTERN-053: track prior-tick bounce levels for rising-edge detection.
        # The detector is a pure spectral probe (idempotent evaluate()); the edge
        # semantics live here at the consumer boundary.
        self._last_bounce_state: tuple[bool, bool] = (False, False)

    def update(
        self,
        a_speed_mps: float | None,
        b_speed_mps: float | None,
        a_bounce: bool,
        b_bounce: bool,
        t_ms: int,
    ) -> dict[PlayerSide, PlayerState]:
        """Advance both players one tick, applying match-level coupling.

        Coupling order per tick:
          i.   Per-player kinematic update (independent).
          ii.  USER-CORRECTION-011: Conditional DEAD_TIME uncoupling (PRE_SERVE_RITUAL-only rescue).
          iii. USER-CORRECTION-010 + PATTERN-053: Rising-edge bounce → PRE_SERVE_RITUAL
               (runs last; a simultaneous DEAD_TIME + bounce rising edge correctly
               lands everyone in PRE_SERVE_RITUAL).
        """
        a_prev, b_prev = self._a.state, self._b.state
        self._a.update(a_speed_mps, t_ms)
        self._b.update(b_speed_mps, t_ms)

        # USER-CORRECTION-011: Conditional DEAD_TIME uncoupling.
        # Only rescue a player stuck in PRE_SERVE_RITUAL (the Ace/Fault deadlock).
        # Do NOT force ACTIVE_RALLY players into DEAD_TIME — that would truncate
        # legitimate deceleration curves and destroy recovery_latency_ms / lateral_work_rate.
        a_entered_dead = (a_prev != "DEAD_TIME" and self._a.state == "DEAD_TIME")
        b_entered_dead = (b_prev != "DEAD_TIME" and self._b.state == "DEAD_TIME")
        if a_entered_dead and self._b.state == "PRE_SERVE_RITUAL":
            self._b.force_state("DEAD_TIME", t_ms)
        if b_entered_dead and self._a.state == "PRE_SERVE_RITUAL":
            self._a.force_state("DEAD_TIME", t_ms)

        # PATTERN-053: edge-trigger the bounce coupling.
        # RollingBounceDetector.evaluate() returns True every frame the signature is
        # in its ~90-frame buffer. Firing force_state on every True tick would pin
        # the players in PRE_SERVE_RITUAL for the whole ~3s window, across the rally.
        # Rising-edge detection (False → True per player) fires once per bounce signature.
        prev_a_bounce, prev_b_bounce = self._last_bounce_state
        a_bounce_edge = a_bounce and not prev_a_bounce
        b_bounce_edge = b_bounce and not prev_b_bounce
        self._last_bounce_state = (a_bounce, b_bounce)

        if a_bounce_edge or b_bounce_edge:
            # USER-CORRECTION-010: bouncer is server, non-bouncer is returner re-syncing.
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
