'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useMemo } from 'react';

import {
  usePanopticonStatic,
  usePanopticonState,
} from '@/lib/PanopticonProvider';
import { colors } from '@/lib/design-tokens';
import { isSignalAllowedInState } from '@/lib/stateSignalGating';
import type {
  HUDWidgetSpec,
  PlayerState,
  SignalName,
  SignalSample,
} from '@/lib/types';

import SensorCalibratingPlaceholder from './SensorCalibratingPlaceholder';
import SignalBar from './SignalBar';

/**
 * The hero right-rail (DECISION-009).
 *
 * Two states:
 *   1. PRE-CALIBRATION (`currentTimeMs < firstLayoutMs` — PATTERN-048):
 *      Render `<SensorCalibratingPlaceholder />` with a pulsing "BIOMETRIC
 *      SENSORS: CALIBRATING…" UX (GOTCHA-017).
 *   2. ACTIVE: Read `activeHUDLayout.widgets`, pull out the SignalBar specs
 *      for the right-1..right-4 slots, and render up to 4 `<SignalBar>` cards
 *      sourced from `activeSignalsByName`.
 *
 * Every transition between layouts animates via `<AnimatePresence>` with
 * spring physics (PATTERN-044). When the layout_id changes, old cards
 * spring out, new cards spring in.
 */
export default function SignalRail() {
  const {
    activeHUDLayout,
    activeSignalsByName,
    activePlayerState,
    currentTimeMs,
  } = usePanopticonState();
  const { getFirstLayoutMs } = usePanopticonStatic();

  const firstLayoutMs = getFirstLayoutMs();
  const isCalibrating = currentTimeMs < firstLayoutMs || !activeHUDLayout;

  return (
    <div
      role="region"
      aria-label="Biometric signal rail"
      className="flex h-full flex-col gap-3"
    >
      <RailHeader
        layoutId={activeHUDLayout?.layout_id ?? 'calibrating'}
        state={activePlayerState}
      />

      <AnimatePresence mode="wait">
        {isCalibrating ? (
          <SensorCalibratingPlaceholder key="calibrating" />
        ) : (
          <ActiveBars
            key={activeHUDLayout.layout_id}
            widgets={activeHUDLayout.widgets}
            signals={activeSignalsByName}
            state={activePlayerState}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function RailHeader({
  layoutId,
  state,
}: {
  layoutId: string;
  state: PlayerState | null;
}) {
  return (
    <header className="flex items-center justify-between">
      <span
        className="mono text-[10px] uppercase tracking-[0.18em]"
        style={{ color: colors.textMuted }}
      >
        Biometric Telemetry
      </span>
      <span
        className="mono text-[9px] uppercase tracking-[0.14em]"
        style={{ color: colors.textMuted }}
      >
        {layoutId === 'calibrating'
          ? 'warmup'
          : `${formatState(state)} · layout ${layoutId.slice(-6)}`}
      </span>
    </header>
  );
}

function formatState(state: PlayerState | null): string {
  if (!state || state === 'UNKNOWN') return '—';
  return state.toLowerCase().replace(/_/g, ' ');
}

interface ActiveBarsProps {
  widgets: ReadonlyArray<HUDWidgetSpec>;
  signals: Record<string, SignalSample>;
  state: PlayerState | null;
}

function ActiveBars({ widgets, signals, state }: ActiveBarsProps) {
  const barEntries = useMemo(() => {
    // Pull out SignalBar widgets targeting Player A. Belt-and-suspenders filter
    // — the backend already guarantees Player A only (DECISION-008).
    //
    // State-gating (PATTERN-052 / Action 1.2): reject signals inappropriate
    // for the current PlayerState. Frontend defense-in-depth against LLM
    // layout-lag where the Designer selected serve-ritual signals during an
    // ACTIVE_RALLY (or vice versa).
    const entries: Array<{ signalName: SignalName }> = [];
    for (const w of widgets) {
      if (w.widget !== 'SignalBar') continue;
      if (w.props.player !== undefined && w.props.player !== 'A') continue;
      const signalName = w.props.signal as SignalName | undefined;
      if (!signalName) continue;
      if (!isSignalAllowedInState(signalName, state)) continue;
      entries.push({ signalName });
      if (entries.length >= 4) break;
    }
    return entries;
  }, [widgets, state]);

  if (barEntries.length === 0) {
    return (
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="text-[12px] italic"
        style={{ color: colors.textMuted }}
      >
        Telemetry quiet for this phase of play.
      </motion.p>
    );
  }

  return (
    <motion.div
      key="bars"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col gap-3"
    >
      <AnimatePresence initial={false}>
        {barEntries.map(({ signalName }) => (
          <SignalBar
            key={signalName}
            signalName={signalName}
            signal={signals[signalName] ?? null}
          />
        ))}
      </AnimatePresence>
    </motion.div>
  );
}
