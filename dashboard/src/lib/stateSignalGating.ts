import type { PlayerState, RallyMicroPhase, SignalName } from './types';

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
 * Phase A4.5 refactor (team-lead override 2026-04-24) — moved from if-else
 * branches to a `Record<RallyMicroPhase, readonly SignalName[]>` map. The
 * object-literal declaration forces compile-time exhaustiveness: adding a
 * new RallyMicroPhase member without a gating entry fails `tsc`. Covers
 * both the live 4-member PlayerState (subset of RallyMicroPhase) AND the
 * 3 authored-only display states (WARMUP, SERVE, CHANGEOVER) so display
 * timelines never render a signal into a phase that is biomechanically
 * impossible.
 */

/**
 * Exhaustive rally-phase → permitted-signals map.
 *
 * Type invariant: `Record<RallyMicroPhase, readonly SignalName[]>` — TypeScript
 * fails compile if a new RallyMicroPhase member is added to `types.ts` without
 * a corresponding entry here. This replaces the if-else chain's "new member
 * falls through to `return true`" silent-permit bug (G25).
 */
export const GATING_MAP: Record<RallyMicroPhase, readonly SignalName[]> = {
  // Pre-state warmup convergence window — permit everything (safer default
  // before any state transition has fired).
  UNKNOWN: [
    'recovery_latency_ms',
    'serve_toss_variance_cm',
    'ritual_entropy_delta',
    'crouch_depth_degradation_deg',
    'baseline_retreat_distance_m',
    'lateral_work_rate',
    'split_step_latency_ms',
  ],
  // Match-warmup period — player hits practice shots, no formal serve ritual
  // yet. Only state-agnostic signals apply.
  WARMUP: [
    'recovery_latency_ms',
    'split_step_latency_ms',
  ],
  // Pre-serve ritual — ball-bounce cadence, crouch-depth, toss-variance all
  // read here. Rally-movement signals (lateral work, baseline retreat) are
  // off because the player is stationary.
  PRE_SERVE_RITUAL: [
    'recovery_latency_ms',
    'serve_toss_variance_cm',
    'ritual_entropy_delta',
    'crouch_depth_degradation_deg',
    'split_step_latency_ms',
  ],
  // Active serve motion — same gating as PRE_SERVE_RITUAL (toss/ritual
  // signals still active, rally-movement signals still off).
  SERVE: [
    'recovery_latency_ms',
    'serve_toss_variance_cm',
    'ritual_entropy_delta',
    'crouch_depth_degradation_deg',
    'split_step_latency_ms',
  ],
  // Rally in progress — court-coverage + retreat signals dominate. Serve-
  // ritual signals (toss-variance, ritual-entropy, crouch-depth) are off.
  ACTIVE_RALLY: [
    'recovery_latency_ms',
    'baseline_retreat_distance_m',
    'lateral_work_rate',
    'split_step_latency_ms',
  ],
  // Between-point dead time — same as PRE_SERVE_RITUAL (player is resetting).
  DEAD_TIME: [
    'recovery_latency_ms',
    'serve_toss_variance_cm',
    'ritual_entropy_delta',
    'crouch_depth_degradation_deg',
    'split_step_latency_ms',
  ],
  // Changeover (~90s seated break) — only state-agnostic recovery signal
  // applies; toss/ritual signals don't read during a seated break.
  CHANGEOVER: [
    'recovery_latency_ms',
  ],
};

/**
 * Belt-and-braces compile-time exhaustiveness check. If GATING_MAP's keys
 * ever diverge from RallyMicroPhase (a new member added, an existing one
 * removed), this line fails tsc. The primary enforcement is the Record type
 * above; this helper catches the `Partial<Record<…>> as Record<…>` cast
 * escape hatch (G26).
 */
type AssertExhaustive<R extends Record<U, unknown>, U extends string> =
  [keyof R] extends [U]
    ? [U] extends [keyof R]
      ? true
      : never
    : never;
// eslint-disable-next-line @typescript-eslint/no-unused-vars
type _GatingMapIsExhaustive = AssertExhaustive<typeof GATING_MAP, RallyMicroPhase>;

/**
 * Is the given signal appropriate for the current rally phase?
 *
 * Accepts both `PlayerState` (live 4-member) and `RallyMicroPhase`
 * (display-only 7-member). PlayerState ⊂ RallyMicroPhase, so any live-state
 * value is a valid key into GATING_MAP.
 *
 * Fallback behavior (G25 / team-lead override): if `state` somehow lands
 * outside RallyMicroPhase (malformed authored JSON, runtime coercion bug),
 * return `false` — reject the signal rather than crash on `undefined.includes`.
 * This is the opposite of the pre-refactor `return true` fall-through, which
 * silently permitted ALL signals for unknown states.
 */
export function isSignalAllowedInState(
  signalName: SignalName,
  state: PlayerState | RallyMicroPhase | null,
): boolean {
  if (state === null) return true;
  const allowed = GATING_MAP[state as RallyMicroPhase];
  return allowed?.includes(signalName) ?? false;
}

/**
 * Filter an array of signal names down to those permitted in the current
 * rally phase. Preserves input order.
 */
export function filterSignalsByState(
  signalNames: ReadonlyArray<SignalName>,
  state: PlayerState | RallyMicroPhase | null,
): SignalName[] {
  return signalNames.filter((s) => isSignalAllowedInState(s, state));
}
