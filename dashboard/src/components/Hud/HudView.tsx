'use client';

import CoachPanel from '@/components/Broadcast/CoachPanel';
import PlayerNameplate from '@/components/Broadcast/PlayerNameplate';
import SignalRail from '@/components/Broadcast/SignalRail';
import PanopticonEngine from '@/components/PanopticonEngine';
import TelemetryLog from '@/components/Telemetry/TelemetryLog';

// Module-level constants: prevents `useMemo` identity-break inside TelemetryLog
// on every HudView render. TelemetryLog uses `rowKinds` as a memo dependency;
// if we pass an inline `[...]` literal on each render, a new array is allocated
// every tick, the memo invalidates, and `filtered` recomputes at 10 Hz —
// degrading the 30-FPS canvas. Hoisting these to module scope gives stable
// referential identity and lets the memo actually memoize. (Phase 3 TS review finding.)
const SIDE_RAIL_ROW_KINDS = ['signal', 'anomaly'] as const;
const HEADLINE_STRIP_ROW_KINDS = ['anomaly', 'insight', 'state'] as const;

/**
 * Tab 1 — the main Live HUD view.
 *
 * 12-col grid: PlayerNameplate top-left · PanopticonEngine center · SignalRail +
 * live order-book telemetry right · CoachPanel + headline-events strip bottom.
 * Single-player scope (DECISION-008); biometrics-as-hero visual hierarchy
 * (DECISION-009).
 *
 * This component renders inside <TabShell /> and stays mounted when the user
 * switches to other tabs (PATTERN-050 keep-alive).
 */
export default function HudView() {
  return (
    <div className="flex min-h-[calc(100vh-72px)] flex-col bg-[var(--color-bg-0)] p-6 lg:p-10">
      <div className="mx-auto grid w-full max-w-[1600px] grid-cols-12 gap-5">
        {/* Top-left: identity chrome */}
        <header className="col-span-12 flex items-start justify-between gap-4 lg:col-span-3">
          <PlayerNameplate />
        </header>

        {/* Center: video + skeleton — broadcast stage */}
        <section className="col-span-12 lg:col-span-6">
          <div
            className="relative w-full overflow-hidden rounded-[12px] ring-1 ring-[var(--color-border)]"
            style={{ boxShadow: '0 0 60px rgba(0, 229, 255, 0.12)' }}
          >
            <PanopticonEngine />
          </div>
        </section>

        {/* Right rail: 3 SignalBars (hero) + scrolling firehose log (order-book feel) */}
        <aside className="col-span-12 flex flex-col gap-4 lg:col-span-3">
          <SignalRail />
          <TelemetryLog
            rowKinds={SIDE_RAIL_ROW_KINDS}
            heightClass="h-[360px]"
            density="compact"
            showHeader
          />
        </aside>

        {/* Bottom: CoachPanel + wide headline-events strip (anomaly + insight + state) */}
        <div className="col-span-12 mt-2 flex flex-col items-center gap-4">
          <CoachPanel />
          <TelemetryLog
            rowKinds={HEADLINE_STRIP_ROW_KINDS}
            heightClass="h-[260px]"
            className="w-full max-w-[920px]"
            density="compact"
          />
        </div>
      </div>
    </div>
  );
}
