"""Tests for backend/cv/state_machine.py.

Enforces:
- USER-CORRECTION-009: 2D speed magnitude `math.hypot(vx, vy)` drives transitions
- USER-CORRECTION-010: match-level coupling — server's bounce forces returner's PRE_SERVE_RITUAL

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import math

import pytest

from backend.cv.state_machine import (
    ACTIVE_RALLY_SPEED_THRESHOLD_MPS,
    CONSECUTIVE_FRAMES_TO_DEAD_TIME,
    CONSECUTIVE_FRAMES_TO_RALLY,
    DEAD_TIME_SPEED_THRESHOLD_MPS,
    MatchStateMachine,
    PlayerStateMachine,
)

# ──────────────────────────── Single-player FSM ────────────────────────────


def test_initial_state_is_pre_serve_ritual() -> None:
    fsm = PlayerStateMachine()
    assert fsm.state == "PRE_SERVE_RITUAL"


def test_moves_to_active_rally_after_sustained_motion() -> None:
    """5+ consecutive frames of speed > 0.2 m/s -> PRE_SERVE_RITUAL -> ACTIVE_RALLY."""
    fsm = PlayerStateMachine()
    for t in range(1, CONSECUTIVE_FRAMES_TO_RALLY):
        fsm.update(speed_mps=0.5, t_ms=t * 33)
        assert fsm.state == "PRE_SERVE_RITUAL"
    # The CONSECUTIVE_FRAMES_TO_RALLY-th consecutive frame triggers the transition
    fsm.update(speed_mps=0.5, t_ms=CONSECUTIVE_FRAMES_TO_RALLY * 33)
    assert fsm.state == "ACTIVE_RALLY"


def test_moves_to_dead_time_after_sustained_stillness() -> None:
    fsm = PlayerStateMachine()
    # Get into ACTIVE_RALLY first
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        fsm.update(speed_mps=0.5, t_ms=(t + 1) * 33)
    assert fsm.state == "ACTIVE_RALLY"

    # Then sustained stillness
    for t in range(CONSECUTIVE_FRAMES_TO_DEAD_TIME - 1):
        fsm.update(speed_mps=0.01, t_ms=(100 + t) * 33)
        assert fsm.state == "ACTIVE_RALLY", f"premature DEAD_TIME at frame {t}"
    fsm.update(speed_mps=0.01, t_ms=(100 + CONSECUTIVE_FRAMES_TO_DEAD_TIME) * 33)
    assert fsm.state == "DEAD_TIME"


def test_transient_stillness_does_not_trigger_dead_time() -> None:
    """A single still frame mid-rally should not flip state."""
    fsm = PlayerStateMachine()
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        fsm.update(speed_mps=0.5, t_ms=(t + 1) * 33)
    assert fsm.state == "ACTIVE_RALLY"
    fsm.update(speed_mps=0.01, t_ms=100)  # one still frame
    fsm.update(speed_mps=0.5, t_ms=200)  # back to motion
    assert fsm.state == "ACTIVE_RALLY"


# ──────────────────────────── USER-CORRECTION-009: 2D speed ────────────────────────────


def test_state_machine_accepts_speed_magnitude_as_input() -> None:
    """Canonical contract: input is pre-computed 2D speed, not raw vx/vy.

    The caller does math.hypot(vx, vy) and passes the result. This matches the
    cv-pipeline-engineering skill's stage-4 contract.
    """
    fsm = PlayerStateMachine()
    # Purely lateral motion: vx=1.0, vy=0.0 => speed = 1.0 m/s
    vx, vy = 1.0, 0.0
    speed = math.hypot(vx, vy)
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        fsm.update(speed_mps=speed, t_ms=(t + 1) * 33)
    assert fsm.state == "ACTIVE_RALLY", (
        "Purely lateral motion (vx=1, vy=0) must trigger ACTIVE_RALLY. "
        "USER-CORRECTION-009: states must use hypot, not |vy| alone."
    )


# ──────────────────────────── Force-state for match-level coupling ────────────────────────────


def test_force_state_overrides_kinematic_state() -> None:
    fsm = PlayerStateMachine()
    # Drive to ACTIVE_RALLY
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        fsm.update(speed_mps=0.5, t_ms=(t + 1) * 33)
    assert fsm.state == "ACTIVE_RALLY"

    transition = fsm.force_state("PRE_SERVE_RITUAL", t_ms=999)
    assert fsm.state == "PRE_SERVE_RITUAL"
    assert transition is not None
    assert transition.from_state == "ACTIVE_RALLY"
    assert transition.to_state == "PRE_SERVE_RITUAL"
    assert transition.reason == "match_coupling"


def test_force_state_resets_consecutive_counters() -> None:
    """After force_state, a single non-matching speed should not immediately flip back."""
    fsm = PlayerStateMachine()
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        fsm.update(speed_mps=0.5, t_ms=(t + 1) * 33)
    fsm.force_state("PRE_SERVE_RITUAL", t_ms=1000)
    assert fsm.state == "PRE_SERVE_RITUAL"

    # Even though speed is still > 0.2 m/s, we shouldn't immediately jump back to ACTIVE_RALLY
    # until we accumulate 5 new consecutive frames at that speed
    fsm.update(speed_mps=0.5, t_ms=1001 * 33)
    assert fsm.state == "PRE_SERVE_RITUAL"


# ──────────────────────────── USER-CORRECTION-010: MatchStateMachine ────────────────────────────


def test_match_state_machine_couples_returner_to_server_bounce() -> None:
    """Canonical USER-CORRECTION-010 test.

    Server (Player A) emits BOUNCE_DETECTED while in DEAD_TIME.
    Returner (Player B) is motionless in DEAD_TIME throughout.
    Expected: both players are forced into PRE_SERVE_RITUAL on the bounce tick.
    Then B can transition to ACTIVE_RALLY when the return motion begins,
    giving split_step_latency the PRE_SERVE_RITUAL -> ACTIVE_RALLY transition it needs.
    """
    msm = MatchStateMachine()

    # First, drive both to DEAD_TIME (via stillness after a rally)
    # Seed them to ACTIVE_RALLY then stillness
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        msm.update(a_speed_mps=0.5, b_speed_mps=0.5, a_bounce=False, b_bounce=False, t_ms=t * 33)
    for t in range(CONSECUTIVE_FRAMES_TO_DEAD_TIME):
        msm.update(
            a_speed_mps=0.01,
            b_speed_mps=0.01,
            a_bounce=False,
            b_bounce=False,
            t_ms=(100 + t) * 33,
        )
    states = msm.update(
        a_speed_mps=0.0, b_speed_mps=0.0, a_bounce=False, b_bounce=False, t_ms=200 * 33
    )
    assert states["A"] == "DEAD_TIME"
    assert states["B"] == "DEAD_TIME"

    # Player A emits bounce signature; Player B is motionless
    states = msm.update(
        a_speed_mps=0.0, b_speed_mps=0.0, a_bounce=True, b_bounce=False, t_ms=201 * 33
    )
    assert states["A"] == "PRE_SERVE_RITUAL"
    assert states["B"] == "PRE_SERVE_RITUAL", (
        "USER-CORRECTION-010: Server's bounce must force Returner into PRE_SERVE_RITUAL."
    )


def test_match_state_machine_no_coupling_without_bounce() -> None:
    """Without a bounce signature, player states evolve independently on their own kinematics."""
    msm = MatchStateMachine()
    # A runs, B stays still
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        states = msm.update(
            a_speed_mps=0.5,
            b_speed_mps=0.0,
            a_bounce=False,
            b_bounce=False,
            t_ms=(t + 1) * 33,
        )
    assert states["A"] == "ACTIVE_RALLY"
    # B should NOT have been forced into PRE_SERVE_RITUAL-by-coupling — it stays in whatever
    # state its own kinematics dictated. B never moved, so it remains in the initial state.
    assert states["B"] == "PRE_SERVE_RITUAL"
    # Critically: B is not yanked by A's motion alone.


def test_split_step_transition_fires_for_returner_after_coupling() -> None:
    """Integration scenario: after forced PRE_SERVE_RITUAL, returner's transition to ACTIVE_RALLY emits."""
    msm = MatchStateMachine()
    # Set both to DEAD_TIME
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        msm.update(a_speed_mps=0.5, b_speed_mps=0.5, a_bounce=False, b_bounce=False, t_ms=t * 33)
    for t in range(CONSECUTIVE_FRAMES_TO_DEAD_TIME):
        msm.update(a_speed_mps=0.0, b_speed_mps=0.0, a_bounce=False, b_bounce=False, t_ms=(100 + t) * 33)

    # Bounce -> both in PRE_SERVE_RITUAL
    msm.update(a_speed_mps=0.0, b_speed_mps=0.0, a_bounce=True, b_bounce=False, t_ms=200 * 33)

    # Collect transitions emitted since last drain
    _ = msm.drain_transitions()

    # Returner (B) now starts moving — accumulate speed until transition
    for t in range(CONSECUTIVE_FRAMES_TO_RALLY):
        msm.update(
            a_speed_mps=0.5, b_speed_mps=0.4, a_bounce=False, b_bounce=False, t_ms=(300 + t) * 33
        )

    transitions = msm.drain_transitions()
    b_transitions = [tr for tr in transitions if tr.player == "B"]
    # B must have a PRE_SERVE_RITUAL -> ACTIVE_RALLY transition
    found = any(
        tr.from_state == "PRE_SERVE_RITUAL" and tr.to_state == "ACTIVE_RALLY" for tr in b_transitions
    )
    assert found, (
        "USER-CORRECTION-010: After match-level coupling, returner must be able to emit "
        "PRE_SERVE_RITUAL -> ACTIVE_RALLY (the gate for split_step_latency)."
    )


def test_transitions_drain_emptying() -> None:
    msm = MatchStateMachine()
    msm.update(a_speed_mps=0.0, b_speed_mps=0.0, a_bounce=True, b_bounce=False, t_ms=33)
    first_drain = msm.drain_transitions()
    assert len(first_drain) >= 2, "bounce forces both players into PRE_SERVE_RITUAL"
    # Second drain should be empty
    second_drain = msm.drain_transitions()
    assert second_drain == []


# ──────────────────────────── Threshold constants match skill docs ────────────────────────────


def test_thresholds_match_skill_definitions() -> None:
    """Per cv-pipeline-engineering skill: 0.2 m/s up, 0.05 m/s down."""
    assert pytest.approx(0.2) == ACTIVE_RALLY_SPEED_THRESHOLD_MPS
    assert pytest.approx(0.05) == DEAD_TIME_SPEED_THRESHOLD_MPS
    assert CONSECUTIVE_FRAMES_TO_RALLY == 5
    assert CONSECUTIVE_FRAMES_TO_DEAD_TIME == 15
