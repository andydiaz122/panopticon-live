'use client';

import { colors } from '@/lib/design-tokens';

/**
 * Persistent "two realities" disclosure banner for Tab 1 (Live HUD) and
 * Tab 2 (Raw Telemetry) per the G43 display-only architecture.
 *
 * Honest disclosure that broadcaster narration (display_transitions +
 * display_narrations + display_player_profile) runs as a separate stream
 * from the live CV signal extraction. Every signal in signals[] comes
 * from the 4-state live FSM; every AUTHORED row in the TelemetryLog comes
 * from the 7-state hand-authored timeline.
 *
 * Styled as a subtle 2K-Sports broadcast overlay (mono caps, thin cyan
 * accent bar, low-contrast background) so judges read it as intentional
 * production chrome, not as a debug warning (team-lead override 2026-04-24).
 */
export default function DisclosureBanner() {
  return (
    <div
      role="note"
      aria-label="Two-reality disclosure"
      className="relative flex items-center gap-3 rounded-md border px-4 py-2"
      style={{
        background: `${colors.bg1}CC`,
        borderColor: `${colors.playerA}33`,
        borderLeftWidth: 3,
        borderLeftColor: colors.playerA,
      }}
    >
      <span
        className="mono shrink-0 text-[10px] font-semibold uppercase tracking-[0.22em]"
        style={{ color: colors.playerA }}
      >
        Broadcast · Signal
      </span>
      <span
        className="text-[11px] leading-snug"
        style={{ color: colors.textSecondary }}
      >
        Broadcast narration timeline is hand-authored; live biometric signal extraction runs independently.
      </span>
    </div>
  );
}
