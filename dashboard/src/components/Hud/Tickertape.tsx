'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useMemo } from 'react';

import { usePanopticonState } from '@/lib/PanopticonProvider';
import { colors } from '@/lib/design-tokens';
import { SIGNAL_COPY } from '@/lib/signalCopy';
import { signalUnit, toneForSignal } from '@/lib/telemetry';
import type { PlayerState, SignalName, SignalSample } from '@/lib/types';

/**
 * Tickertape — Palantir-density phase-weighted signal strip at Tab 1 bottom (A1).
 *
 * Per PLAN.md §6 A1 + Q5 decision: the signal set shown depends on the
 * current rally phase. The tickertape mirrors the main HUD's state-gating
 * discipline (`stateSignalGating.ts`) so the values on screen ALWAYS match
 * the biomechanics the player is actually in. No mixing serve-ritual
 * signals with rally-movement signals on the same strip.
 *
 * Phase slots (Q5 locked answer):
 *   - `PRE_SERVE_RITUAL` / `DEAD_TIME` → toss_precision, ritual_discipline, crouch_depth
 *   - `ACTIVE_RALLY` → lateral_work, court_position, recovery_lag
 *   - unknown / null → state-agnostic fallback (recovery_lag alone)
 *
 * Rendering: static horizontal strip, mono typography, cyan/fatigued tone by
 * z-score magnitude. No actual scrolling marquee (risk of wrong — a clean
 * tri-column read is the safer Palantir-density move). AnimatePresence on
 * slot swap so phase transitions cross-fade rather than hard-cut.
 */

const PHASE_SLOTS: Record<'PRE_SERVE' | 'RALLY' | 'FALLBACK', ReadonlyArray<SignalName>> = {
  PRE_SERVE: ['serve_toss_variance_cm', 'ritual_entropy_delta', 'crouch_depth_degradation_deg'],
  RALLY: ['lateral_work_rate', 'baseline_retreat_distance_m', 'recovery_latency_ms'],
  FALLBACK: ['recovery_latency_ms'],
};

function slotForState(state: PlayerState | null): keyof typeof PHASE_SLOTS {
  if (state === 'PRE_SERVE_RITUAL' || state === 'DEAD_TIME') return 'PRE_SERVE';
  if (state === 'ACTIVE_RALLY') return 'RALLY';
  return 'FALLBACK';
}

export default function Tickertape() {
  const { activePlayerState, activeSignalsByName } = usePanopticonState();
  const slot = slotForState(activePlayerState);
  const signals = PHASE_SLOTS[slot];

  // Pull the latest sample for each phase-weighted signal. Memoized against
  // activeSignalsByName identity — the provider already ensures stable refs
  // when the underlying samples don't change.
  const entries = useMemo(
    () =>
      signals.map((name) => ({
        name,
        sample: (activeSignalsByName[name] ?? null) as SignalSample | null,
      })),
    [signals, activeSignalsByName],
  );

  return (
    <div
      role="complementary"
      aria-label="Phase-weighted signal tickertape"
      className="mono flex w-full items-stretch gap-1 overflow-hidden rounded-md border"
      style={{
        background: `${colors.bg1}E6`,
        borderColor: colors.border,
        borderLeftWidth: 3,
        borderLeftColor: colors.playerA,
      }}
    >
      <div
        className="flex shrink-0 items-center px-3 py-2 text-[9px] font-semibold uppercase tracking-[0.22em]"
        style={{ color: colors.playerA }}
      >
        Live Telemetry · {slot.replace('_', ' ')}
      </div>
      <AnimatePresence mode="wait">
        <motion.div
          key={slot}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
          className="flex flex-1 items-stretch divide-x"
          style={{ borderColor: colors.border }}
        >
          {entries.map(({ name, sample }) => (
            <TickertapeCell key={name} name={name} sample={sample} />
          ))}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

function TickertapeCell({ name, sample }: { name: SignalName; sample: SignalSample | null }) {
  const copy = SIGNAL_COPY[name];
  const unit = signalUnit(name);
  const value = sample?.value != null ? sample.value.toFixed(2) : '—';
  const z = sample?.baseline_z_score;
  const zStr = z == null ? '' : (z >= 0 ? ' +' : ' ') + z.toFixed(2) + 'σ';
  const tone = sample ? toneForSignal(sample) : colors.textMuted;

  return (
    <div
      className="flex flex-1 min-w-0 items-center gap-3 px-4 py-2"
      style={{ borderColor: colors.border }}
    >
      <span
        className="shrink-0 text-[9px] uppercase tracking-[0.18em]"
        style={{ color: colors.textMuted }}
      >
        {copy.label}
      </span>
      <span
        className="flex-1 truncate text-right text-[14px] font-bold tabular-nums"
        style={{ color: tone }}
      >
        {value}
        <span className="ml-0.5 text-[10px] font-normal" style={{ color: colors.textMuted }}>
          {unit}
        </span>
      </span>
      <span
        className="shrink-0 text-[10px] tabular-nums"
        style={{ color: z != null && Math.abs(z) >= 1 ? tone : colors.textMuted }}
      >
        {zStr}
      </span>
    </div>
  );
}
