'use client';

import CoachPanel from '@/components/Broadcast/CoachPanel';
import PlayerNameplate from '@/components/Broadcast/PlayerNameplate';
import SignalRail from '@/components/Broadcast/SignalRail';
import PanopticonEngine from '@/components/PanopticonEngine';

/**
 * Tab 1 — the main Live HUD view.
 *
 * 12-col grid: PlayerNameplate top-left · PanopticonEngine center · SignalRail
 * right · CoachPanel bottom-center. Single-player scope (DECISION-008);
 * biometrics-as-hero visual hierarchy (DECISION-009).
 *
 * This component renders inside <TabShell /> and stays mounted when the user
 * switches to other tabs (PATTERN-050 keep-alive). The video continues playing
 * in the background so the telemetry / scouting tabs can react to currentTime.
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

        {/* Right rail: SignalBar stack (hero widget per DECISION-009) */}
        <aside className="col-span-12 lg:col-span-3">
          <SignalRail />
        </aside>

        {/* Bottom: CoachPanel — subordinate, only when insight active */}
        <div className="col-span-12 mt-2 flex justify-center">
          <CoachPanel />
        </div>
      </div>
    </div>
  );
}
