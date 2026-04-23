/**
 * Fan-facing copy for the 7 biomechanical signals.
 *
 * Source of truth: `.claude/skills/biometric-fan-experience/SKILL.md`.
 * Every SignalBar and related widget MUST read from this table — never
 * render raw dev names like `baseline_retreat_distance_m` to the fan.
 *
 * Invariants (enforced by signalCopy.test.ts):
 *  - Every SignalName in `types.ts` has an entry.
 *  - label ≤22 chars, fanDescription ≤110 chars, unit ≤8 chars.
 *  - No entry references Player B (DECISION-008 single-player scope).
 */
import type { SignalName } from './types';

/** Directional semantic: does a rising value mean fatigue, energy, or drift? */
export type SignalDirection = 'fatigue' | 'energy' | 'drift';

export interface SignalCopyEntry {
  /** Display title. Title Case. No units. ≤22 chars. */
  label: string;
  /** Number suffix. `m`, `cm`, `°`, `ms`, `rel`. ≤8 chars. */
  unit: string;
  /** Plain-English one-liner. ≤110 chars. Subject is Player A. */
  fanDescription: string;
  /** Directional semantic for tone flip (higher = bad for fatigue/drift, good for energy). */
  higherIs: SignalDirection;
}

export const SIGNAL_COPY: Record<SignalName, SignalCopyEntry> = {
  baseline_retreat_distance_m: {
    label: 'Baseline Retreat',
    unit: 'm',
    fanDescription:
      "How far Player A has drifted behind his warmup baseline. Bigger = giving ground to the opponent's heat.",
    higherIs: 'drift',
  },
  recovery_latency_ms: {
    label: 'Recovery Lag',
    unit: 'ms',
    fanDescription:
      'Time Player A takes to return to a ready stance after each shot. Bigger = getting tired.',
    higherIs: 'fatigue',
  },
  serve_toss_variance_cm: {
    label: 'Toss Consistency',
    unit: 'cm',
    fanDescription:
      "Vertical jitter of Player A's ball toss at apex. Bigger = ritual breaking down under pressure.",
    higherIs: 'drift',
  },
  ritual_entropy_delta: {
    label: 'Ritual Discipline',
    unit: 'rel',
    fanDescription:
      "How much Player A's pre-serve routine deviates from his warmup baseline. Bigger = pattern degrading.",
    higherIs: 'drift',
  },
  crouch_depth_degradation_deg: {
    label: 'Crouch Depth',
    unit: '°',
    fanDescription:
      "Loss of bend in Player A's split-step crouch. Bigger = legs fading.",
    higherIs: 'fatigue',
  },
  lateral_work_rate: {
    label: 'Lateral Work',
    unit: 'rel',
    fanDescription:
      'How much side-to-side ground Player A is covering per second. Bigger = aggressive court coverage.',
    higherIs: 'energy',
  },
  split_step_latency_ms: {
    label: 'Split-Step Timing',
    unit: 'ms',
    fanDescription:
      "Delay between opponent's racket contact and Player A's split-step. Bigger = reading slower.",
    higherIs: 'fatigue',
  },
};

/**
 * Templated anomaly copy when |z_score| ≥ 2.
 *
 * Renders a ≤64-char broadcast-grade sentence derived from the signal's
 * `higherIs` direction and the sign of z.
 */
export function anomalyCopy(signalName: SignalName, zScore: number): string {
  const copy = SIGNAL_COPY[signalName];
  const magnitude = Math.abs(zScore);
  const sigma = `${magnitude.toFixed(1)}σ`;

  if (copy.higherIs === 'fatigue' && zScore > 0) {
    return `Player A fatiguing ${sigma} above baseline`;
  }
  if (copy.higherIs === 'drift' && zScore > 0) {
    return `Player A drifting ${sigma} from warmup`;
  }
  if (copy.higherIs === 'energy' && zScore < 0) {
    return `Player A coverage collapsing ${sigma}`;
  }
  if (copy.higherIs === 'energy' && zScore > 0) {
    return `Player A surging ${sigma} over baseline`;
  }
  // Rare: fatigue signal going negative = unusually fresh. Drift going negative = unusually steady.
  if (copy.higherIs === 'fatigue' && zScore < 0) {
    return `Player A unusually fresh (${sigma})`;
  }
  return `Player A ${sigma} off baseline`;
}
