'use client';

import { useEffect, useMemo, useRef } from 'react';

import { usePanopticonState } from '@/lib/PanopticonProvider';
import { colors } from '@/lib/design-tokens';
import { SIGNAL_COPY } from '@/lib/signalCopy';
import type {
  AnomalyEvent,
  CoachInsight,
  MatchData,
  SignalSample,
  StateTransition,
} from '@/lib/types';

/**
 * Tab 2 — Raw Telemetry Feed.
 *
 * Terminal-style log view of every telemetry event the backend emitted, with
 * syntax highlighting per event type. Streams in as the video plays: only
 * rows with `timestamp_ms <= currentTimeMs` render.
 *
 * Rows:
 *   - STATE    transitions for Player A (slate + amber)
 *   - SIGNAL   Player-A signal samples (cyan + value color-toned by direction)
 *   - INSIGHT  Opus Coach commentary openers (purple)
 *   - ANOMALY  signal anomalies (red; empty on utr_01_segment_a)
 *
 * Keep-alive (PATTERN-050): this component stays mounted across tab switches
 * so auto-scroll position and ref state persist. It re-renders at ≤10Hz via
 * the provider state, so the auto-scroll is smooth.
 */

type FeedRow =
  | { kind: 'state'; t: number; text: string }
  | { kind: 'signal'; t: number; signal: SignalSample; tone: string }
  | { kind: 'insight'; t: number; text: string }
  | { kind: 'anomaly'; t: number; text: string };

export default function SignalFeed() {
  const { matchData, currentTimeMs } = usePanopticonState();
  const listRef = useRef<HTMLDivElement>(null);
  const followRef = useRef(true); // follows tail unless user scrolls up

  // Build the complete ordered timeline once matchData is loaded.
  const timeline = useMemo<FeedRow[]>(() => {
    if (!matchData) return [];
    return buildTimeline(matchData);
  }, [matchData]);

  // Visible slice — everything ≤ current video time.
  const visibleRows = useMemo(() => {
    // Binary search for the upper bound, then slice. Sorted by t ascending.
    const endIdx = upperBound(timeline, currentTimeMs);
    return timeline.slice(0, endIdx);
  }, [timeline, currentTimeMs]);

  // Auto-scroll to tail, unless user scrolled away.
  useEffect(() => {
    const el = listRef.current;
    if (!el || !followRef.current) return;
    el.scrollTop = el.scrollHeight;
  }, [visibleRows.length]);

  const onScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const el = e.currentTarget;
    const distFromBottom =
      el.scrollHeight - el.scrollTop - el.clientHeight;
    followRef.current = distFromBottom < 48;
  };

  return (
    <div
      className="flex h-[calc(100vh-72px)] w-full flex-col p-6 lg:p-10"
      style={{ background: colors.bg0 }}
    >
      <FeedHeader
        total={timeline.length}
        visible={visibleRows.length}
        currentTimeMs={currentTimeMs}
      />
      <div
        ref={listRef}
        onScroll={onScroll}
        role="log"
        aria-live="polite"
        className="mono mt-4 flex-1 overflow-y-auto rounded-lg border p-4 text-[12px] leading-relaxed"
        style={{
          background: '#05080F',
          borderColor: colors.border,
          color: colors.textSecondary,
        }}
      >
        {visibleRows.length === 0 ? (
          <div
            className="italic"
            style={{ color: colors.textMuted }}
          >
            # telemetry buffer clear — play the video to stream events
          </div>
        ) : (
          visibleRows.map((row, i) => <FeedLine key={i} row={row} />)
        )}
      </div>
    </div>
  );
}

function FeedHeader({
  total,
  visible,
  currentTimeMs,
}: {
  total: number;
  visible: number;
  currentTimeMs: number;
}) {
  return (
    <header className="flex items-end justify-between gap-3">
      <div>
        <h2
          className="text-[22px] font-bold tracking-tight"
          style={{ color: colors.textPrimary }}
        >
          Raw Telemetry
        </h2>
        <p
          className="mt-1 text-[12px]"
          style={{ color: colors.textSecondary }}
        >
          Live feed of the 7 biometric signals + state machine + Opus insights.
          This is the proprietary data stream — what&apos;s being extracted from
          standard 2D broadcast pixels with zero hardware sensors.
        </p>
      </div>
      <div className="mono flex flex-col items-end text-[10px] uppercase tracking-[0.14em]">
        <span style={{ color: colors.textMuted }}>
          {fmtClock(currentTimeMs)} / {fmtClock(60000)}
        </span>
        <span style={{ color: colors.playerA }}>
          {visible.toLocaleString()} / {total.toLocaleString()} events
        </span>
      </div>
    </header>
  );
}

function FeedLine({ row }: { row: FeedRow }) {
  const ts = fmtClock(row.t);
  if (row.kind === 'signal') {
    const copy = SIGNAL_COPY[row.signal.signal_name];
    const value = row.signal.value == null ? '—' : row.signal.value.toFixed(3);
    const z = row.signal.baseline_z_score;
    const zStr = z == null ? '  — ' : (z >= 0 ? ' +' : ' ') + z.toFixed(2) + 'σ';
    return (
      <div className="flex gap-2">
        <span style={{ color: colors.textMuted }}>[{ts}]</span>
        <span className="w-16 shrink-0" style={{ color: colors.playerA }}>
          SIGNAL
        </span>
        <span className="flex-1 truncate">
          <span style={{ color: colors.textPrimary }}>
            {row.signal.signal_name}
          </span>
          <span style={{ color: colors.textSecondary }}> = </span>
          <span style={{ color: row.tone }}>{value}</span>
          <span style={{ color: colors.textMuted }}> {copy?.unit ?? ''}</span>
          <span style={{ color: colors.textSecondary }}>{zStr}</span>
          <span style={{ color: colors.textMuted }}>
            {' '}
            state={row.signal.state.toLowerCase()}
          </span>
        </span>
      </div>
    );
  }
  if (row.kind === 'state') {
    return (
      <div className="flex gap-2">
        <span style={{ color: colors.textMuted }}>[{ts}]</span>
        <span className="w-16 shrink-0" style={{ color: colors.fatigued }}>
          STATE
        </span>
        <span style={{ color: colors.textSecondary }}>{row.text}</span>
      </div>
    );
  }
  if (row.kind === 'insight') {
    return (
      <div className="flex gap-2">
        <span style={{ color: colors.textMuted }}>[{ts}]</span>
        <span className="w-16 shrink-0" style={{ color: colors.opusThinking }}>
          INSIGHT
        </span>
        <span style={{ color: colors.textSecondary }}>{row.text}</span>
      </div>
    );
  }
  // anomaly
  return (
    <div className="flex gap-2">
      <span style={{ color: colors.textMuted }}>[{ts}]</span>
      <span className="w-16 shrink-0" style={{ color: colors.anomaly }}>
        ANOMALY
      </span>
      <span style={{ color: colors.anomaly }}>{row.text}</span>
    </div>
  );
}

// ──────────────────────────── helpers ────────────────────────────

function fmtClock(ms: number): string {
  const total = Math.max(0, Math.floor(ms));
  const m = Math.floor(total / 60000);
  const s = Math.floor((total % 60000) / 1000);
  const cs = Math.floor((total % 1000) / 10);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(cs).padStart(2, '0')}`;
}

function upperBound(rows: FeedRow[], t: number): number {
  // First index whose timestamp > t. Rows slice is [0, upperBound).
  let lo = 0;
  let hi = rows.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (rows[mid].t <= t) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

function buildTimeline(data: MatchData): FeedRow[] {
  const rows: FeedRow[] = [];

  for (const s of data.signals) {
    if (s.player !== 'A') continue;
    rows.push({
      kind: 'signal',
      t: s.timestamp_ms,
      signal: s,
      tone: toneForSignal(s),
    });
  }

  for (const tr of data.transitions) {
    if (tr.player !== 'A') continue;
    rows.push({
      kind: 'state',
      t: tr.timestamp_ms,
      text: transitionText(tr),
    });
  }

  for (const insight of data.coach_insights) {
    rows.push({
      kind: 'insight',
      t: insight.timestamp_ms,
      text: oneLineOpener(insight),
    });
  }

  for (const a of data.anomalies) {
    rows.push({
      kind: 'anomaly',
      t: a.timestamp_ms,
      text: anomalyText(a),
    });
  }

  rows.sort((a, b) => a.t - b.t);
  return rows;
}

function toneForSignal(s: SignalSample): string {
  const z = s.baseline_z_score;
  if (z == null) return colors.textSecondary;
  if (Math.abs(z) >= 2) return colors.anomaly;
  if (Math.abs(z) >= 1) return colors.fatigued;
  return colors.energized;
}

function transitionText(tr: StateTransition): string {
  return `player=${tr.player} ${tr.from_state} -> ${tr.to_state} reason=${tr.reason}`;
}

function oneLineOpener(c: CoachInsight): string {
  // Strip newlines, take first ~110 chars — keep it log-line-friendly.
  const flat = c.commentary.replace(/\s+/g, ' ').trim();
  return flat.length > 110 ? flat.slice(0, 107) + '…' : flat;
}

function anomalyText(a: AnomalyEvent): string {
  return `${a.signal_name} z=${a.z_score.toFixed(2)} value=${a.value.toFixed(3)} severity=${a.severity.toFixed(2)}`;
}
