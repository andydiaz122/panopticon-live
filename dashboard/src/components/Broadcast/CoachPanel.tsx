'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

import {
  usePanopticonState,
  usePanopticonStatic,
} from '@/lib/PanopticonProvider';
import { colors, motion as motionTokens } from '@/lib/design-tokens';
import type { CoachInsight } from '@/lib/types';

/**
 * CoachPanel — SUBORDINATE footer chip (DECISION-009).
 *
 * Explicitly NOT the hero of the HUD. Only visible when an insight is active.
 * Max height ~88px. Typewriter implemented via DOM mutation (PATTERN-047) to
 * avoid the setState-at-55Hz death-spiral.
 *
 * The outer `<motion.div key={insight.insight_id}>` guarantees race-free
 * unmount + remount when the insight changes — the old typewriter interval
 * is cancelled via the effect cleanup, the new one spawns fresh.
 */

const TYPEWRITER_STEP_MS = 18;
// 2026-04-25 ~17:35 EDT — TELESTRATOR_HOLD_MS reduced 3500 → 1500. The
// 3.5s hold compounded badly with anomaly slow-mo at 35-39s window (insight
// #5 fires at 36s INSIDE that window): 4.7s typewriter + 3.5s hold = 8.2s
// pause, then video resumed at 0.25x for ~13s — total 22s of non-normal
// playback per coach insight. The new 1.5s hold gives judges 1.5s read time
// after typewriter completes, which is enough for a forensic reader to
// finish-and-process the last sentence before resume.
const TELESTRATOR_HOLD_MS = 1500;

export default function CoachPanel() {
  const { activeCoachInsight } = usePanopticonState();

  return (
    <div className="flex w-full max-w-[920px] justify-center">
      <AnimatePresence mode="wait">
        {activeCoachInsight ? (
          <InsightCard
            key={activeCoachInsight.insight_id}
            insight={activeCoachInsight}
          />
        ) : null}
      </AnimatePresence>
    </div>
  );
}

function InsightCard({ insight }: { insight: CoachInsight }) {
  const { videoRef } = usePanopticonStatic();
  const spanRef = useRef<HTMLSpanElement>(null);
  const [thinkingOpen, setThinkingOpen] = useState(false);
  const hasThinking = Boolean(insight.thinking);
  const isCached = insight.cache_read_tokens > 0;

  /**
   * Telestrator pacing (PATTERN-051):
   *   1. On insight mount: pause the video so judges can read.
   *   2. Typewriter reveals commentary via DOM mutation (PATTERN-047).
   *   3. When typewriter completes, hold TELESTRATOR_HOLD_MS, then resume.
   *   4. Cleanup (insight changes OR unmount): clear timers and resume video
   *      so the demo never stalls in a forced-pause state.
   *
   * We bind the pause/play calls to the videoRef FROM STATIC CONTEXT so this
   * component remains decoupled from any specific <video> element lifecycle.
   */
  useEffect(() => {
    const span = spanRef.current;
    if (!span) return;
    // Capture the video element at effect start — avoids the
    // react-hooks/exhaustive-deps warning about ref-changed-by-cleanup, and
    // is safe here because videoRef is stable (singleton <video>).
    const video = videoRef.current;

    const commentary = insight.commentary;
    span.textContent = '';
    let i = 0;
    let resumeTimeoutId: number | undefined;

    // 2026-04-26 ~04:30 EDT — RE-ENABLED for QuickTime recording session.
    // OBS was the lag amplifier (see docs/RECORDING_LAG_RECIPE.md). With
    // QuickTime as the recording tool, the slow-mo + telestrator pauses
    // are back. Coach insight #5 was moved from t=36000 to t=37500 in
    // 52b8294 to eliminate the slow-mo+pause collision. TELESTRATOR_HOLD_MS
    // softened from 3500 to 1500 stays in place (better editorial pacing).
    video?.pause();

    const typewriterId = window.setInterval(() => {
      i += 1;
      if (!spanRef.current) {
        window.clearInterval(typewriterId);
        return;
      }
      spanRef.current.textContent = commentary.slice(0, i);
      if (i >= commentary.length) {
        window.clearInterval(typewriterId);
        // Step 3: typewriter ends → hold for TELESTRATOR_HOLD_MS → resume.
        resumeTimeoutId = window.setTimeout(() => {
          video?.play().catch(() => {});
        }, TELESTRATOR_HOLD_MS);
      }
    }, TYPEWRITER_STEP_MS);

    return () => {
      window.clearInterval(typewriterId);
      if (resumeTimeoutId !== undefined) {
        window.clearTimeout(resumeTimeoutId);
      }
      // Step 4: on insight change or unmount, always resume so the demo
      // never leaves the viewer stranded at a paused frame.
      video?.play().catch(() => {});
    };
  }, [insight.commentary, insight.insight_id, videoRef]);

  return (
    <motion.section
      role="status"
      aria-live="polite"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 40 }}
      // PATTERN-068 — Framer Motion UX masking (team-lead 2026-04-24):
      // 500ms opacity fade hides any micro-desync between the Opus
      // commentary typewriter and the video clock. Position (y) still uses
      // the existing spring for natural snap — only opacity needs the
      // longer curve to look like intentional AI-processing flourish.
      transition={{
        ...motionTokens.springStandard,
        opacity: { duration: 0.5, ease: 'easeOut' },
      }}
      className="flex w-full flex-col gap-2 rounded-lg border px-4 py-3"
      style={{
        background: colors.bg1,
        borderColor: colors.border,
        // maxHeight scales to the col-span-6 center column (half width). The
        // previous 88/260 clamps were sized for the col-span-12 full-width
        // layout — at half width the same text wraps to ~6-7 lines and was
        // being clipped by `overflow: hidden`. Allow ~10 lines of body text
        // collapsed (220px) and the additional thinking pre-block when open
        // (380px = 220 + 140 thinking + 16 gap + slack).
        maxHeight: thinkingOpen ? 380 : 220,
        overflow: 'hidden',
      }}
    >
      <header className="flex items-center gap-2">
        <span
          className="rounded-sm px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-[0.18em]"
          style={{
            color: colors.opusThinking,
            background: `${colors.opusThinking}22`,
          }}
        >
          Opus
        </span>
        {isCached && (
          <span
            className="mono text-[9px] uppercase tracking-[0.1em]"
            style={{ color: colors.textMuted }}
            title={`${insight.cache_read_tokens} cached tokens`}
          >
            ⚡ cached
          </span>
        )}
        {hasThinking && (
          <button
            type="button"
            onClick={() => setThinkingOpen((o) => !o)}
            className="ml-auto text-[10px] uppercase tracking-[0.14em] transition-colors hover:text-white"
            style={{ color: colors.textMuted }}
            aria-expanded={thinkingOpen}
          >
            {thinkingOpen ? 'Hide thinking ▴' : 'Show thinking ▾'}
          </button>
        )}
      </header>

      <p
        className="text-[13px] leading-snug"
        style={{ color: colors.textPrimary, minHeight: 34 }}
      >
        <span ref={spanRef} />
      </p>

      {thinkingOpen && hasThinking && (
        <motion.pre
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={motionTokens.tweenQuick}
          className="mono whitespace-pre-wrap rounded p-2 text-[11px] leading-snug"
          style={{
            color: colors.opusThinking,
            background: `${colors.opusThinking}0D`,
            maxHeight: 140,
            overflow: 'auto',
          }}
        >
          {insight.thinking}
        </motion.pre>
      )}
    </motion.section>
  );
}
