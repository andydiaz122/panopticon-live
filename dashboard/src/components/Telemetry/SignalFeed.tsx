'use client';

import { useMemo } from 'react';

import DisclosureBanner from '@/components/Broadcast/DisclosureBanner';
import { usePanopticonState } from '@/lib/PanopticonProvider';
import { colors } from '@/lib/design-tokens';
import { buildTimeline, fmtClock } from '@/lib/telemetry';

import TelemetryLog from './TelemetryLog';

/**
 * Tab 2 — Raw Telemetry Feed.
 *
 * Terminal-style log view of every telemetry event the backend emitted.
 * Delegates rendering to the shared `TelemetryLog` primitive; this file
 * owns the full-viewport shell + big-header chrome.
 */

export default function SignalFeed() {
  const { matchData, currentTimeMs } = usePanopticonState();

  const totalEvents = useMemo(
    () => (matchData ? buildTimeline(matchData).length : 0),
    [matchData],
  );

  return (
    <div
      className="flex h-[calc(100vh-72px)] w-full flex-col p-6 lg:p-10"
      style={{ background: colors.bg0 }}
    >
      <FeedHeader total={totalEvents} currentTimeMs={currentTimeMs} />
      <div className="mt-3">
        <DisclosureBanner />
      </div>
      <div className="mt-4 flex flex-1 flex-col">
        <TelemetryLog heightClass="flex-1" density="comfortable" showHeader />
      </div>
    </div>
  );
}

function FeedHeader({
  total,
  currentTimeMs,
}: {
  total: number;
  currentTimeMs: number;
}) {
  return (
    <header className="flex items-end justify-between gap-3">
      <div>
        <h2
          className="text-[22px] font-bold tracking-tight"
          style={{ color: colors.textPrimary }}
        >
          Raw Telemetry
        </h2>
        <p
          className="mt-1 text-[12px]"
          style={{ color: colors.textSecondary }}
        >
          Live feed of the 7 biometric signals + state machine + Opus insights.
          This is the proprietary data stream — what&apos;s being extracted from
          standard 2D broadcast pixels with zero hardware sensors.
        </p>
      </div>
      <div className="mono flex flex-col items-end text-[10px] uppercase tracking-[0.14em]">
        <span style={{ color: colors.textMuted }}>
          {fmtClock(currentTimeMs)} / {fmtClock(60000)}
        </span>
        <span style={{ color: colors.playerA }}>
          {total.toLocaleString()} events
        </span>
      </div>
    </header>
  );
}
