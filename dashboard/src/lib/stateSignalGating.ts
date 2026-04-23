import type { PlayerState, SignalName } from './types';

/**
 * Frontend defense-in-depth state-gating (Action 1.2 + PATTERN-052).
 *
 * The backend Opus Designer sometimes produces HUD layouts whose selected
 * signals bleed into the wrong match state (e.g., `serve_toss_variance_cm`
 * recommended during an ACTIVE_RALLY). This is LLM layout-lag — the layout
 * was decided on one state's data and applied as the state transitions.
 *
 * Per Andrew's feedback: "toss consistency is only relevant to the fan…
 * before the serve, during the serve, and at the end of a point going into
 * a new point when the athlete is going to serve again." Signals should
 * be contextually correct for the athlete's current phase of play.
 *
 * This module encodes the hard mapping from PlayerState → permitted signals,
 * applied as a frontend filter on top of whatever the Designer selected.
 *
 * ⚠️ Keep this in sync with the biomechanical-signal-semantics skill's
 * state gating. If the backend Designer gets smarter about state, this
 * filter should relax (the filter is a safety net, not the primary logic).
 */

/**
 * Signals that only make sense BETWEEN points — during serve ritual or dead
 * time when the athlete is stationary / preparing. Hidden during ACTIVE_RALLY.
 */
const PRE_SERVE_EXCLUSIVE: ReadonlySet<SignalName> = new Set([
  'serve_toss_variance_cm',
  'ritual_entropy_delta',
  'crouch_depth_degradation_deg',
]);

/**
 * Signals that only make sense DURING a rally — court coverage, retreat,
 * recovery. Hidden during PRE_SERVE_RITUAL / DEAD_TIME.
 */
const RALLY_EXCLUSIVE: ReadonlySet<SignalName> = new Set([
  'lateral_work_rate',
  'baseline_retreat_distance_m',
]);

/**
 * Signals allowed in every state (state-agnostic). These are either
 * context-invariant (recovery_latency_ms measures post-rally recovery and
 * is valid once a rally has ended) or always-on (split_step_latency_ms
 * fires on opponent contact — rare but not state-restricted).
 */
const STATE_AGNOSTIC: ReadonlySet<SignalName> = new Set([
  'recovery_latency_ms',
  'split_step_latency_ms',
]);

/**
 * Is the given signal appropriate for the current player state?
 *
 * Rules per Andrew's directive:
 *   - ACTIVE_RALLY → reject PRE_SERVE_EXCLUSIVE (serve-ritual signals)
 *   - PRE_SERVE_RITUAL / DEAD_TIME → reject RALLY_EXCLUSIVE (rally-movement signals)
 *   - UNKNOWN (pre-first-transition warmup) → permit everything (safer default)
 *   - null (no active state yet) → permit everything
 */
export function isSignalAllowedInState(
  signalName: SignalName,
  state: PlayerState | null,
): boolean {
  if (STATE_AGNOSTIC.has(signalName)) return true;
  if (state === null || state === 'UNKNOWN') return true;

  if (state === 'ACTIVE_RALLY') {
    return !PRE_SERVE_EXCLUSIVE.has(signalName);
  }
  if (state === 'PRE_SERVE_RITUAL' || state === 'DEAD_TIME') {
    return !RALLY_EXCLUSIVE.has(signalName);
  }
  return true;
}

/**
 * Filter an array of signal names down to those permitted in the current
 * player state. Preserves input order.
 */
export function filterSignalsByState(
  signalNames: ReadonlyArray<SignalName>,
  state: PlayerState | null,
): SignalName[] {
  return signalNames.filter((s) => isSignalAllowedInState(s, state));
}
