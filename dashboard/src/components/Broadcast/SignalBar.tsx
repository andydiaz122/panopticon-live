'use client';

import { motion } from 'framer-motion';

import {
  colors,
  motion as motionTokens,
  shadows,
} from '@/lib/design-tokens';
import { SIGNAL_COPY, anomalyCopy } from '@/lib/signalCopy';
import type { SignalName, SignalSample } from '@/lib/types';
import { zScoreToTone, type Tone } from '@/lib/zScoreToTone';

/**
 * SignalBar — the hero widget (DECISION-009).
 *
 * Shows one Player-A biometric signal with:
 *   - Fan-facing label (from SIGNAL_COPY, e.g. "Baseline Retreat")
 *   - Current numeric value + unit, tabular-nums
 *   - Horizontal bar whose fill WIDTH is spring-physics animated (PATTERN-044
 *     bridges 10Hz data updates into 60FPS fluid motion)
 *   - Tone color interpolates by z-score severity (baseline → energized /
 *     fatigued → anomaly)
 *   - Pulse animation at |z| ≥ 2
 *   - Plain-English fan caption explaining what the signal means
 *
 * State-frequency budget: re-renders only on provider state updates (≤10Hz).
 * Never subscribes to keypoints.
 */

export interface SignalBarProps {
  signalName: SignalName;
  signal: SignalSample | null;
}

/** Map a signal's value to a fill percentage `[0, 100]` based on its z-score. */
function valueToPct(signal: SignalSample | null): number {
  if (!signal || signal.baseline_z_score == null) return 0;
  // Map z-score [-3, 3] → [0, 100] with clamping. Baseline z=0 sits at 50%.
  const clamped = Math.max(-3, Math.min(3, signal.baseline_z_score));
  return ((clamped + 3) / 6) * 100;
}

const TONE_COLOR: Record<Tone, string> = {
  baseline: colors.baseline,
  energized: colors.energized,
  fatigued: colors.fatigued,
  anomaly: colors.anomaly,
};

export default function SignalBar({ signalName, signal }: SignalBarProps) {
  const copy = SIGNAL_COPY[signalName];
  const zScore = signal?.baseline_z_score ?? null;
  const tone = zScoreToTone(zScore, copy.higherIs);
  const toneColor = TONE_COLOR[tone];
  const isAnomaly = tone === 'anomaly';
  const fillPct = valueToPct(signal);

  const valueDisplay =
    signal?.value != null
      ? `${signal.value.toFixed(signal.value < 10 ? 2 : 1)}`
      : '—';

  return (
    <motion.article
      layout
      initial={{ opacity: 0, x: 28 }}
      animate={
        isAnomaly
          ? { opacity: 1, x: 0, scale: [1, 1.04, 1] }
          : { opacity: 1, x: 0, scale: 1 }
      }
      exit={{ opacity: 0, x: 16 }}
      transition={
        isAnomaly
          ? { duration: 0.9, repeat: Infinity, ease: 'easeInOut' }
          : motionTokens.springStandard
      }
      className="flex flex-col gap-2 rounded-lg border p-3.5"
      style={{
        background: colors.bg1,
        borderColor: isAnomaly ? colors.anomaly : colors.border,
        boxShadow: isAnomaly ? shadows.glowAnomaly : 'none',
      }}
    >
      <header className="flex items-baseline justify-between gap-2">
        <h3
          className="text-[13px] font-semibold tracking-wide"
          style={{ color: colors.textPrimary }}
        >
          {copy.label}
        </h3>
        <span
          className="mono text-[15px] font-semibold leading-none"
          style={{ color: toneColor }}
        >
          {valueDisplay}
          <span
            className="ml-1 text-[11px] font-normal"
            style={{ color: colors.textMuted }}
          >
            {copy.unit}
          </span>
        </span>
      </header>

      <div
        className="relative h-2.5 overflow-hidden rounded-full"
        style={{ background: colors.bg2 }}
      >
        <motion.div
          className="h-full rounded-full"
          style={{ background: toneColor }}
          animate={{ width: `${fillPct}%` }}
          transition={motionTokens.springFirm}
          aria-label={`${copy.label} fill ${fillPct.toFixed(0)}%`}
        />
      </div>

      <p
        className="text-[11px] italic leading-snug"
        style={{ color: colors.textSecondary }}
      >
        {copy.fanDescription}
      </p>

      {isAnomaly && zScore != null && (
        <motion.p
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={motionTokens.tweenQuick}
          className="mono text-[10px] font-semibold uppercase tracking-[0.14em]"
          style={{ color: colors.anomaly }}
        >
          ANOMALY — {anomalyCopy(signalName, zScore)}
        </motion.p>
      )}
    </motion.article>
  );
}
