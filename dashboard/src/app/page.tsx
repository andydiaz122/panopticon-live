import CoachPanel from '@/components/Broadcast/CoachPanel';
import PlayerNameplate from '@/components/Broadcast/PlayerNameplate';
import SignalRail from '@/components/Broadcast/SignalRail';
import PanopticonEngine from '@/components/PanopticonEngine';
import PanopticonProvider from '@/lib/PanopticonProvider';

/**
 * The main HUD stage. 12-column CSS grid:
 *   - Top-left:    PlayerNameplate (cols 1-3)
 *   - Center:      PanopticonEngine (video + skeleton, cols 4-9)
 *   - Right rail:  SignalRail (cols 10-12, rows 1-4)
 *   - Bottom:      CoachPanel (subordinate footer chip, cols 3-10)
 *
 * Single-player scope (DECISION-008): no Player B nameplate, no MomentumMeter,
 * no PredictiveOverlay. SignalBar stack is the hero (DECISION-009).
 */
export default function Home() {
  return (
    <PanopticonProvider
      videoSrc="/clips/utr_match_01_segment_a.mp4"
      matchDataSrc="/match_data/utr_01_segment_a.json"
    >
      <main className="relative flex min-h-screen flex-col items-stretch justify-center gap-6 bg-[var(--color-bg-0)] p-6 lg:p-10">
        <div className="mx-auto grid w-full max-w-[1600px] grid-cols-12 gap-5">
          {/* Top-left: identity chrome */}
          <header className="col-span-12 flex items-start justify-between gap-4 lg:col-span-3">
            <PlayerNameplate />
          </header>

          {/* Center: video + skeleton — the hero of the screen */}
          <section className="col-span-12 lg:col-span-6">
            <div
              className="relative w-full overflow-hidden rounded-[var(--radius-lg,12px)] ring-1 ring-[var(--color-border)]"
              style={{ boxShadow: '0 0 60px rgba(0, 229, 255, 0.12)' }}
            >
              <PanopticonEngine />
            </div>
          </section>

          {/* Right rail: SignalBar stack (the hero widget per DECISION-009) */}
          <aside className="col-span-12 lg:col-span-3">
            <SignalRail />
          </aside>

          {/* Bottom: CoachPanel — subordinate, only visible when insight active */}
          <div className="col-span-12 mt-2 flex justify-center">
            <CoachPanel />
          </div>
        </div>
      </main>
    </PanopticonProvider>
  );
}
