'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';

import { usePanopticonState } from '@/lib/PanopticonProvider';
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
  const spanRef = useRef<HTMLSpanElement>(null);
  const [thinkingOpen, setThinkingOpen] = useState(false);
  const hasThinking = Boolean(insight.thinking);
  const isCached = insight.cache_read_tokens > 0;

  // Typewriter via DOM mutation — NEVER setState (PATTERN-047).
  useEffect(() => {
    const span = spanRef.current;
    if (!span) return;
    const commentary = insight.commentary;
    span.textContent = '';
    let i = 0;

    const id = setInterval(() => {
      i += 1;
      if (!spanRef.current) {
        clearInterval(id);
        return;
      }
      spanRef.current.textContent = commentary.slice(0, i);
      if (i >= commentary.length) {
        clearInterval(id);
      }
    }, TYPEWRITER_STEP_MS);

    return () => clearInterval(id);
  }, [insight.commentary, insight.insight_id]);

  return (
    <motion.section
      role="status"
      aria-live="polite"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 40 }}
      transition={motionTokens.springStandard}
      className="flex w-full flex-col gap-2 rounded-lg border px-4 py-3"
      style={{
        background: colors.bg1,
        borderColor: colors.border,
        maxHeight: thinkingOpen ? 260 : 88,
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
