'use client';

import { AnimatePresence, motion } from 'framer-motion';

import { usePanopticonState } from '@/lib/PanopticonProvider';
import { colors, motion as motionTokens } from '@/lib/design-tokens';
import type { PlayerState } from '@/lib/types';

/**
 * PlayerNameplate — identity chrome, top-left (DECISION-008 + DECISION-009).
 *
 * Hard-bound to Player A (Player B drawing disabled per GOTCHA-016 + DECISION-008).
 * Reads `activePlayerState` from provider to flip the state chip copy on
 * transitions. Mounts with a spring slide-in from the left edge.
 */

const STATE_COPY: Record<PlayerState, { label: string; tone: string }> = {
  PRE_SERVE_RITUAL: { label: 'Pre-Serve Ritual', tone: colors.playerA },
  ACTIVE_RALLY: { label: 'Active Rally', tone: colors.energized },
  DEAD_TIME: { label: 'Dead Time', tone: colors.textMuted },
  UNKNOWN: { label: 'Reading…', tone: colors.textMuted },
};

/** Safe fallback for any state value that slips past the 4-member PlayerState
 * union at runtime (malformed match_data JSON, schema drift, race condition).
 * Prevents React white-screen on undefined.label (team-lead override 2026-04-24). */
const STATE_FALLBACK = { label: 'Unknown State', tone: colors.textMuted };

export default function PlayerNameplate() {
  const { matchData, activePlayerState } = usePanopticonState();
  const playerName =
    matchData?.display_player_profile?.name ?? matchData?.meta.player_a ?? 'Player A';

  const stateEntry = activePlayerState
    ? (STATE_COPY[activePlayerState] ?? STATE_FALLBACK)
    : { label: 'Warmup', tone: colors.textMuted };

  return (
    <motion.section
      aria-label="Player identity"
      initial={{ opacity: 0, x: -24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={motionTokens.springStandard}
      className="flex w-full items-center gap-3 rounded-lg border p-3 pr-5"
      style={{
        background: colors.bg1,
        borderColor: colors.border,
      }}
    >
      {/* Cyan player-A accent bar */}
      <span
        aria-hidden
        className="inline-block h-10 w-1.5 shrink-0 rounded-full"
        style={{ background: colors.playerA }}
      />

      <div className="flex min-w-0 flex-col">
        <span
          className="mono text-[9px] uppercase tracking-[0.22em]"
          style={{ color: colors.textMuted }}
        >
          Player A
        </span>
        <span
          className="truncate text-[17px] font-bold leading-tight"
          style={{ color: colors.textPrimary }}
        >
          {playerName}
        </span>
      </div>

      <AnimatePresence mode="wait">
        <motion.span
          key={stateEntry.label}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 4 }}
          transition={motionTokens.tweenQuick}
          className="ml-auto rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em]"
          style={{
            color: stateEntry.tone,
            borderColor: `${stateEntry.tone}55`,
            background: `${stateEntry.tone}11`,
          }}
        >
          {stateEntry.label}
        </motion.span>
      </AnimatePresence>
    </motion.section>
  );
}
