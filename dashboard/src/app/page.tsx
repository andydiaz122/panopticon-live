import HudView from '@/components/Hud/HudView';
import OrchestrationConsoleTab from '@/components/Scouting/OrchestrationConsoleTab';
import SignalFeed from '@/components/Telemetry/SignalFeed';
import TabShell from '@/components/TabShell';
import PanopticonProvider from '@/lib/PanopticonProvider';

/**
 * The PANOPTICON LIVE application shell.
 *
 * PanopticonProvider wraps the TabShell so all tabs share ONE video ref,
 * ONE match_data fetch, and ONE rAF loop. Tab content stays MOUNTED across
 * tab switches (PATTERN-050), so video playback + feed scroll position +
 * orchestration-console playback state all survive navigation.
 *
 * Tab 1 — Live HUD: video + skeleton + signal rail + coach panel
 * Tab 2 — Raw Telemetry: terminal-style signal log, streams with currentTime
 * Tab 3 — Scouting Committee: Multi-agent Opus 4.7 swarm trace playback
 *         (PATTERN-056 / USER-CORRECTION-024 — the 2030-vision UX showcased
 *         via offline-trace-capture + client-side pacing)
 */
export default function Home() {
  return (
    <PanopticonProvider
      videoSrc="/clips/utr_match_01_segment_a.mp4"
      matchDataSrc="/match_data/utr_01_segment_a.json"
    >
      {/* <main> landmark — Lighthouse landmark-one-main / WCAG 2.1 a11y. GOTCHA-050.
          className="contents" contributes the WCAG landmark without inserting
          a box into the layout algorithm — preserves TabShell's min-h-screen
          resolution against the viewport. */}
      <main className="contents">
        <TabShell
          initialTabId="hud"
          tabs={[
            {
              id: 'hud',
              label: 'Live HUD',
              sublabel: 'Broadcast overlay',
              content: <HudView />,
            },
            {
              id: 'telemetry',
              label: 'Raw Telemetry',
              sublabel: 'Signal feed',
              content: <SignalFeed />,
            },
            {
              id: 'scouting',
              label: 'Scouting Committee',
              sublabel: '3-agent swarm',
              content: <OrchestrationConsoleTab />,
            },
          ]}
        />
      </main>
    </PanopticonProvider>
  );
}
