import HudView from '@/components/Hud/HudView';
import ScoutingReportTab from '@/components/Scouting/ScoutingReportTab';
import SignalFeed from '@/components/Telemetry/SignalFeed';
import TabShell from '@/components/TabShell';
import PanopticonProvider from '@/lib/PanopticonProvider';

/**
 * The PANOPTICON LIVE application shell.
 *
 * PanopticonProvider wraps the TabShell so all tabs share ONE video ref,
 * ONE match_data fetch, and ONE rAF loop. Tab content stays MOUNTED across
 * tab switches (PATTERN-050), so video playback + feed scroll position +
 * scouting-report state all survive navigation.
 *
 * Tab 1 — Live HUD: video + skeleton + signal rail + coach panel
 * Tab 2 — Raw Telemetry: terminal-style signal log, streams with currentTime
 * Tab 3 — Opus Scouting: Server-Action-triggered scouting report (Opus 4.7)
 */
export default function Home() {
  return (
    <PanopticonProvider
      videoSrc="/clips/utr_match_01_segment_a.mp4"
      matchDataSrc="/match_data/utr_01_segment_a.json"
    >
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
            label: 'Opus Scouting',
            sublabel: 'On-demand brief',
            content: <ScoutingReportTab />,
          },
        ]}
      />
    </PanopticonProvider>
  );
}
