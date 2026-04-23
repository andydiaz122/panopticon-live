/**
 * Map a z-score + signal direction to a visual tone token.
 *
 * Rules (tested in `__tests__/zScoreToTone.test.ts`):
 *  - |z| < 1           → 'baseline'  (slate)
 *  - 1 ≤ |z| < 2       → 'energized' (emerald)  if sign matches `higherIs === 'energy'`
 *                        'fatigued'  (amber)    otherwise
 *  - |z| ≥ 2           → 'anomaly'   (red)
 *  - null / undefined  → 'baseline'  (treat missing data as baseline)
 */
import type { SignalDirection } from './signalCopy';

export type Tone = 'baseline' | 'energized' | 'fatigued' | 'anomaly';

/**
 * Does the sign of z align with the "good" direction for this signal?
 *
 * For `higherIs: 'energy'`, positive z = energized (good).
 * For `higherIs: 'fatigue'` or `'drift'`, positive z = degrading (bad).
 */
function signAlignsWithEnergy(z: number, higherIs: SignalDirection): boolean {
  if (higherIs === 'energy') return z > 0;
  return z < 0; // fatigue/drift: unusually LOW = good (player is fresh/steady)
}

export function zScoreToTone(
  zScore: number | null | undefined,
  higherIs: SignalDirection,
): Tone {
  if (zScore == null || !Number.isFinite(zScore)) return 'baseline';
  const magnitude = Math.abs(zScore);
  if (magnitude >= 2) return 'anomaly';
  if (magnitude < 1) return 'baseline';
  return signAlignsWithEnergy(zScore, higherIs) ? 'energized' : 'fatigued';
}
