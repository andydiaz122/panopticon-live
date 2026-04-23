'use client';

import { motion } from 'framer-motion';
import { useState, useTransition } from 'react';
import ReactMarkdown from 'react-markdown';

import { generateScoutingReport, type ScoutingPayload } from '@/app/actions';
import { colors, motion as motionTokens } from '@/lib/design-tokens';
import { usePanopticonState } from '@/lib/PanopticonProvider';

/**
 * Tab 3 — Opus Scouting Report.
 *
 * Phase 4 (live): the button triggers a Next.js Server Action that calls
 * Claude Opus 4.7 via the `@anthropic-ai/sdk`. We follow PATTERN-054
 * (Client-Driven Payload): strip the high-volume keys on the client, then
 * pass the remaining ~100 KB telemetry as an argument to the Server Action.
 * This sidesteps Vercel's Node File Trace (NFT) limitation on dynamic fs
 * reads (USER-CORRECTION-032) and keeps the action Vercel-bulletproof.
 *
 * The Server Action round-trip is the "creative Opus" demo moment the judges
 * score against. This tab is intentionally minimal UI — the narrative IS the
 * product. Keep the chrome out of the way; let the markdown breathe.
 */
export default function ScoutingReportTab() {
  const { matchData } = usePanopticonState();
  const [report, setReport] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [error, setError] = useState<string | null>(null);

  const matchId = matchData?.meta.match_id ?? 'utr_01_segment_a';

  const onGenerate = () => {
    setError(null);
    if (!matchData) {
      setError(
        'Match data not loaded yet. Wait for the telemetry payload to finish loading before generating a scouting report.',
      );
      return;
    }

    // PATTERN-054: Client-Driven Payload. Strip keypoints (huge per-frame data),
    // hud_layouts (LLM design metadata — irrelevant to sports-science reasoning),
    // and narrator_beats (broadcast prose that would bias the scouting voice).
    // What remains is the LLM-relevant slice: meta + signals + transitions +
    // anomalies + coach_insights — typically ~100 KB, well under Next.js's 1 MB
    // Server Action payload limit, and well under Opus's context budget.
    const payload: ScoutingPayload = {
      meta: matchData.meta,
      signals: matchData.signals,
      transitions: matchData.transitions,
      anomalies: matchData.anomalies,
      coach_insights: matchData.coach_insights,
    };

    startTransition(() => {
      generateScoutingReport(matchId, payload)
        .then((md) => setReport(md))
        .catch((err: unknown) => {
          setError(err instanceof Error ? err.message : String(err));
        });
    });
  };

  return (
    <div
      className="flex min-h-[calc(100vh-72px)] flex-col gap-6 p-6 lg:p-10"
      style={{ background: colors.bg0 }}
    >
      <header className="mx-auto w-full max-w-[900px]">
        <h2
          className="text-[22px] font-bold tracking-tight"
          style={{ color: colors.textPrimary }}
        >
          Opus Scouting Report
        </h2>
        <p
          className="mt-1 max-w-[60ch] text-[13px]"
          style={{ color: colors.textSecondary }}
        >
          Claude Opus 4.7 reasons over Player A&apos;s biomechanical telemetry,
          grounds tactical claims in numeric evidence, and delivers a
          coach-grade brief in seconds.
        </p>

        <div className="mt-5 flex items-center gap-3">
          <button
            type="button"
            onClick={onGenerate}
            disabled={isPending}
            className="relative overflow-hidden rounded-lg border px-4 py-2.5 text-[13px] font-semibold tracking-wide transition-colors disabled:cursor-wait disabled:opacity-70"
            style={{
              background: isPending
                ? `${colors.opusThinking}22`
                : colors.opusThinking,
              borderColor: colors.opusThinking,
              color: isPending ? colors.opusThinking : '#FFFFFF',
              boxShadow: isPending ? 'none' : `0 0 24px ${colors.opusThinking}55`,
            }}
          >
            {isPending ? 'Opus thinking…' : 'Generate Report'}
          </button>

          <span
            className="mono text-[10px] uppercase tracking-[0.16em]"
            style={{ color: colors.textMuted }}
          >
            match {matchId} · model: claude-opus-4-7
          </span>
        </div>

        {error && (
          <p
            className="mt-3 text-[12px]"
            style={{ color: colors.anomaly }}
          >
            {error}
          </p>
        )}
      </header>

      <section
        className="mx-auto w-full max-w-[900px] flex-1 overflow-y-auto rounded-xl border p-8"
        style={{
          background: colors.bg1,
          borderColor: colors.border,
          minHeight: 420,
        }}
      >
        {report ? (
          <motion.article
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={motionTokens.springStandard}
            className="prose prose-invert prose-sm max-w-none"
            style={{ color: colors.textPrimary }}
          >
            <div className="scouting-markdown">
              <ReactMarkdown>{report}</ReactMarkdown>
            </div>
          </motion.article>
        ) : (
          <EmptyState isPending={isPending} />
        )}
      </section>

      <style>{`
        .scouting-markdown h1 {
          font-size: 1.6rem;
          font-weight: 800;
          color: ${colors.textPrimary};
          letter-spacing: -0.01em;
          margin: 0 0 0.6em 0;
        }
        .scouting-markdown h2 {
          font-size: 1.2rem;
          font-weight: 700;
          color: ${colors.textPrimary};
          letter-spacing: -0.005em;
          margin: 1.8em 0 0.4em 0;
          padding-bottom: 0.35em;
          border-bottom: 1px solid ${colors.border};
        }
        .scouting-markdown h3 {
          font-size: 1rem;
          font-weight: 600;
          color: ${colors.textPrimary};
          margin: 1.4em 0 0.3em 0;
        }
        .scouting-markdown p {
          color: ${colors.textSecondary};
          line-height: 1.6;
          margin: 0.9em 0;
        }
        .scouting-markdown strong {
          color: ${colors.playerA};
          font-weight: 600;
        }
        .scouting-markdown em {
          color: ${colors.textMuted};
          font-style: italic;
        }
        .scouting-markdown ol,
        .scouting-markdown ul {
          margin: 0.8em 0 0.8em 1.4em;
          color: ${colors.textSecondary};
        }
        .scouting-markdown li {
          margin: 0.35em 0;
          line-height: 1.55;
        }
        .scouting-markdown li::marker {
          color: ${colors.playerA};
        }
        .scouting-markdown table {
          width: 100%;
          border-collapse: collapse;
          margin: 1em 0;
          font-size: 0.85rem;
        }
        .scouting-markdown thead th {
          text-align: left;
          padding: 0.55em 0.7em;
          color: ${colors.textMuted};
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          font-size: 0.7rem;
          border-bottom: 1px solid ${colors.border};
        }
        .scouting-markdown tbody td {
          padding: 0.6em 0.7em;
          border-bottom: 1px solid ${colors.border}55;
          color: ${colors.textSecondary};
        }
        .scouting-markdown tbody tr:hover td {
          background: ${colors.bg2}44;
        }
        .scouting-markdown hr {
          border: 0;
          border-top: 1px solid ${colors.border};
          margin: 1.5em 0;
        }
        .scouting-markdown code {
          font-family: var(--font-mono);
          color: ${colors.playerA};
          background: ${colors.bg2};
          padding: 0.15em 0.4em;
          border-radius: 3px;
          font-size: 0.88em;
        }
      `}</style>
    </div>
  );
}

function EmptyState({ isPending }: { isPending: boolean }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
      <div
        className="inline-flex h-12 w-12 items-center justify-center rounded-full"
        style={{
          background: `${colors.opusThinking}1A`,
          border: `1px solid ${colors.opusThinking}55`,
        }}
      >
        <span style={{ color: colors.opusThinking, fontSize: 20 }}>◈</span>
      </div>
      <p
        className="mono text-[11px] uppercase tracking-[0.18em]"
        style={{ color: colors.textMuted }}
      >
        {isPending ? 'Opus is reading the telemetry…' : 'Scouting brief on demand'}
      </p>
      {!isPending && (
        <p
          className="max-w-[40ch] text-[12px]"
          style={{ color: colors.textSecondary }}
        >
          Click <span style={{ color: colors.opusThinking }}>Generate Report</span> to ask Opus 4.7 for a coach-grade breakdown of Player A&apos;s fatigue arc.
        </p>
      )}
    </div>
  );
}
