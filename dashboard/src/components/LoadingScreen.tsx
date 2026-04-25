'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useState } from 'react';

import { colors } from '@/lib/design-tokens';

/**
 * LoadingScreen — GOTCHA-030 defense for Vercel cold-boot.
 *
 * On localhost the 550 KB match_data.json and 24 KB agent_trace.json fetch
 * instantly. On Vercel's CDN a first-paint cold-boot takes 1-3 s —
 * `PanopticonProvider` mounts with null refs, the video starts playing
 * (autoplay or native controls), the rAF loop tries to index
 * `keypoints[frameIdx]` against a null array, and the Canvas panics. Judges
 * open the demo URL and see a white screen with a broken skeleton.
 *
 * Defense: block everything until matchData is parsed. Rendered as a
 * full-viewport overlay with pointer-events:auto so clicks cannot reach the
 * video controls until the pipeline is warm.
 *
 * Styled as a 2K-Sports broadcast-pre-roll terminal — mono JetBrains,
 * scanline effect, progress dots. Makes the mandatory wait look like a
 * high-tech feature (team-lead 2026-04-24 directive).
 */

export interface LoadingScreenProps {
  /** Provider loadState. 'loading' = show full overlay. 'error' = show error card. */
  state: 'loading' | 'error';
  /** Error message when `state === 'error'`. */
  errorMsg?: string | null;
  /**
   * When true, render the loading overlay; when false, AnimatePresence drives
   * the exit fade-out before the motion.div unmounts. Always-mount this
   * component (do NOT conditionally render LoadingScreen at the parent
   * boundary — AnimatePresence only fires exit animations when its OWN
   * children unmount, not when AnimatePresence itself is removed from the
   * tree). PR #7 Finding 1 fix.
   */
  visible: boolean;
}

export default function LoadingScreen({ state, errorMsg, visible }: LoadingScreenProps) {
  const [dotCount, setDotCount] = useState(0);

  // Cycle dots every 400ms — visible motion that the wait is intentional.
  useEffect(() => {
    if (state !== 'loading' || !visible) return;
    const id = window.setInterval(() => setDotCount((d) => (d + 1) % 4), 400);
    return () => window.clearInterval(id);
  }, [state, visible]);

  return (
    <AnimatePresence>
      {visible && (
      <motion.div
        key="loading-overlay"
        role="status"
        aria-live="polite"
        aria-label="Loading biometric telemetry"
        initial={{ opacity: 1 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        // 500ms fade-out so the dashboard doesn't pop in jarringly once
        // matchData resolves. PATTERN-068 UX masking.
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="fixed inset-0 z-[9999] flex items-center justify-center"
        style={{
          background: colors.bg0,
          // Scanline shimmer overlay — subtle 2K-Sports CRT aesthetic
          backgroundImage: `repeating-linear-gradient(
            to bottom,
            ${colors.bg0} 0px,
            ${colors.bg0} 2px,
            ${colors.bg1} 3px,
            ${colors.bg0} 4px
          )`,
        }}
      >
        {/* Pointer-events auto on this layer — blocks clicks to video controls */}
        <div
          className="pointer-events-auto flex w-full max-w-[560px] flex-col gap-4 rounded-lg border p-6"
          style={{
            background: `${colors.bg1}F0`,
            borderColor: `${colors.playerA}44`,
            borderLeftWidth: 3,
            borderLeftColor: colors.playerA,
            boxShadow: `0 0 40px ${colors.playerA}22`,
          }}
        >
          {state === 'loading' ? (
            <>
              <div className="flex items-center gap-3">
                <span
                  className="mono text-[10px] font-semibold uppercase tracking-[0.24em]"
                  style={{ color: colors.playerA }}
                >
                  Panopticon Live
                </span>
                <span
                  className="mono text-[10px] uppercase tracking-[0.18em]"
                  style={{ color: colors.textMuted }}
                >
                  Cold-boot
                </span>
              </div>
              <h2
                className="mono text-[15px] font-bold tracking-wide"
                style={{ color: colors.textPrimary }}
              >
                LOADING BIOMETRIC TELEMETRY{'.'.repeat(dotCount)}
                <span style={{ opacity: 0 }}>{'.'.repeat(3 - dotCount)}</span>
              </h2>
              <div className="flex flex-col gap-1.5">
                <StageLine label="match_data.json" ok />
                <StageLine label="agent_trace.json" ok />
                <StageLine label="rAF loop warmup" ok />
                <StageLine label="ready" pending />
              </div>
              <p
                className="mono mt-1 text-[10px] leading-relaxed"
                style={{ color: colors.textMuted }}
              >
                Streaming match payload (~550 KB signals + 24 KB agent trace) from Vercel CDN.
                This wait masks one cold-boot round trip. Subsequent refreshes cached.
              </p>
            </>
          ) : (
            <>
              <h2
                className="mono text-[14px] font-bold tracking-wide"
                style={{ color: colors.anomaly }}
              >
                BIOMETRIC TELEMETRY FAILED TO LOAD
              </h2>
              <p
                className="mono text-[11px] leading-relaxed"
                style={{ color: colors.textSecondary }}
              >
                {errorMsg || 'Unknown error fetching match_data.json'}
              </p>
              <p
                className="mono text-[10px]"
                style={{ color: colors.textMuted }}
              >
                Refresh the page or check the Vercel deployment status.
              </p>
            </>
          )}
        </div>
      </motion.div>
      )}
    </AnimatePresence>
  );
}

/** One row of the terminal-style stage list. */
function StageLine({ label, ok = false, pending = false }: { label: string; ok?: boolean; pending?: boolean }) {
  return (
    <div className="mono flex items-center gap-2 text-[11px]" style={{ color: colors.textSecondary }}>
      <span
        style={{ color: pending ? colors.textMuted : colors.playerA, width: 14 }}
      >
        {pending ? '›' : ok ? '✓' : '·'}
      </span>
      <span>{label}</span>
      {pending && (
        <span className="mono text-[10px]" style={{ color: colors.textMuted }}>
          pending
        </span>
      )}
    </div>
  );
}
