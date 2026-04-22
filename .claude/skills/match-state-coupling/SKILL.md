---
name: match-state-coupling
description: Match-level state-machine synchronization for PANOPTICON LIVE — the "server's bounce forces returner's PRE_SERVE_RITUAL" rule. Use when building or reviewing backend/cv/state_machine.py or any code that couples Player A and Player B's state. Canonical answer to USER-CORRECTION-010.
---

# Match State Coupling

Player states are NOT fully independent. Tennis is a turn-based game whose phase clock is driven by one player at a time (the server). This skill documents how to couple the two per-player state machines.

## The Problem

If state is evaluated purely independently per player:

```
Server:    DEAD_TIME → PRE_SERVE_RITUAL (bounces ball) → ACTIVE_RALLY (serves)
Returner:  DEAD_TIME ————————————————————————————————→ ACTIVE_RALLY (returns)
                         ^                               ^
                         |                               |
                   never enters                    transitions to
                   PRE_SERVE_RITUAL                 ACTIVE_RALLY directly
                   because they are
                   motionless
```

The returner's state transition is **DEAD_TIME → ACTIVE_RALLY**, skipping `PRE_SERVE_RITUAL` entirely. The `split_step_latency` signal gates on `PRE_SERVE_RITUAL → ACTIVE_RALLY` transition (because the split-step happens right before the return). Without that gate firing, `split_step_latency` never emits for the returner.

## The Canonical Fix

A **match-level state machine** wraps two per-player `PlayerStateMachine` instances and couples them via the `BOUNCE_DETECTED` event.

```python
class MatchStateMachine:
    """Couples two per-player FSMs. The server's bounce forces the returner's PRE_SERVE_RITUAL."""

    def __init__(self) -> None:
        self._player_a = PlayerStateMachine()
        self._player_b = PlayerStateMachine()

    def update(
        self,
        a_speed_mps: float | None,  # None = Player A not detected this frame
        b_speed_mps: float | None,
        a_bounce_detected: bool,     # True on the tick a bounce signature fires for Player A
        b_bounce_detected: bool,
        t_ms: int,
    ) -> dict[PlayerSide, PlayerState]:
        # Step 1: each FSM updates on its own kinematics
        state_a = self._player_a.update(a_speed_mps, t_ms)
        state_b = self._player_b.update(b_speed_mps, t_ms)

        # Step 2: match-level coupling
        # If EITHER player emits a bounce, force BOTH into PRE_SERVE_RITUAL.
        # The bouncer is the server (implicitly); the non-bouncer is the returner.
        if a_bounce_detected or b_bounce_detected:
            state_a = self._player_a.force_state("PRE_SERVE_RITUAL", t_ms)
            state_b = self._player_b.force_state("PRE_SERVE_RITUAL", t_ms)

        return {"A": state_a, "B": state_b}
```

## What `BOUNCE_DETECTED` Means

The server's distinctive pre-serve pattern: repeatedly bouncing the ball on the ground while standing still, 3-8 seconds of rhythmic oscillation in the wrist/ball vertical position. Detected via:
- Wrist Y-position buffer over the last 2-3 seconds
- Lomb-Scargle periodogram peak in the 1-4 Hz band
- Power above the player-specific noise floor

This is the same signal that feeds `ritual_entropy_delta`, so the detector is co-located with that extractor. The `BOUNCE_DETECTED` boolean fires on the tick the pattern becomes statistically confident (not every bounce).

## Server vs Returner Identification

We don't need to identify "server" vs "returner" explicitly. The one who bounces IS the server by definition. Match-level coupling forces them both into `PRE_SERVE_RITUAL` simultaneously; then:
- The server's state advances to `ACTIVE_RALLY` when their speed exceeds threshold (their serve motion)
- The returner's state advances to `ACTIVE_RALLY` when their speed exceeds threshold (their return motion)
- `split_step_latency` gate fires for BOTH as they exit `PRE_SERVE_RITUAL`

## `force_state` Semantics

`PlayerStateMachine.force_state(state, t_ms)` is a privileged entry point used ONLY by `MatchStateMachine`. It:
- Immediately sets the current state to the provided value
- Emits a `StateTransition(from_state=prior, to_state=forced, t_ms=t_ms, reason="match_coupling")` event
- Resets internal consecutive-frame counters (so the state machine doesn't immediately bounce back on the next kinematic update)
- Does NOT trigger recursive coupling (force_state only changes one player's state; the caller handles the other)

## Anti-Patterns

- ❌ Do NOT use `force_state` from signal extractors or external code
- ❌ Do NOT skip the independent kinematic update before coupling — we still need both players' baseline kinematic state
- ❌ Do NOT make bounce detection look-ahead (streaming only: a bounce signature must be statistically confident by the time you fire it)
- ❌ Do NOT treat `changeover` as a bounce — bounces during changeovers are ball-bounces against equipment, not serves. The state machine is in DEAD_TIME during changeover; bounce detection should be gated out during extended DEAD_TIME to prevent false couplings.

## Signal Implications

| Signal | Behavior under coupling |
|---|---|
| `recovery_latency_ms` | Unaffected — gates on ACTIVE_RALLY → DEAD_TIME exit |
| `serve_toss_variance_cm` | Attributes to server only (identified by bounce) |
| `ritual_entropy_delta` | Accumulated for server during their PRE_SERVE_RITUAL; returner's buffer is trimmed |
| `crouch_depth_degradation_deg` | Unaffected — computed during ACTIVE_RALLY |
| `baseline_retreat_distance_m` | Unaffected — computed during ACTIVE_RALLY |
| `lateral_work_rate` | Unaffected — computed during ACTIVE_RALLY |
| `split_step_latency_ms` | ENABLED by this coupling. Gates on returner's PRE_SERVE_RITUAL → ACTIVE_RALLY transition — which only exists thanks to match-level sync. |

## Test Cases (must be in tests/test_cv/test_state_machine.py)

1. **Baseline coupling**: Player A emits bounce → both A and B enter PRE_SERVE_RITUAL. Then A speed rises → A transitions to ACTIVE_RALLY. B remains PRE_SERVE_RITUAL until B speed rises → B transitions to ACTIVE_RALLY. `split_step_latency` gate fires for B.
2. **Independence when no bounce**: both players move independently, no bounce → states evolve from each player's own kinematics
3. **Returner stays still during serve**: A bounces and transitions to ACTIVE_RALLY (serve); B has `b_speed_mps = 0.0` throughout. B should still have entered PRE_SERVE_RITUAL at the bounce tick (so when B eventually moves to return, the `PRE_SERVE_RITUAL → ACTIVE_RALLY` transition fires).
4. **False bounce during rally**: mid-rally ball-bounce on the court. Bounce detector should be gated off during ACTIVE_RALLY (not fire), so no spurious coupling.
5. **Match-phase independence after rally**: A transitions to DEAD_TIME; B remains in DEAD_TIME. No coupling fires because no bounce.

## Integration with Other Skills

- `cv-pipeline-engineering` — Stage 4 state machine
- `biomechanical-signal-semantics` — `split_step_latency` and `ritual_entropy` reference this coupling
- `physical-kalman-tracking` — provides the `speed_mps` input
- `panopticon-hackathon-rules` — "player states are coupled via bounce" is a project invariant
