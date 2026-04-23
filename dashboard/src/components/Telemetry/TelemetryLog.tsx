'use client';

import { useEffect, useMemo, useRef } from 'react';

import { usePanopticonState } from '@/lib/PanopticonProvider';
import { colors } from '@/lib/design-tokens';
import {
  buildTimeline,
  fmtClock,
  signalUnit,
  upperBound,
  type FeedRow,
  type FeedRowKind,
} from '@/lib/telemetry';

/**
 * TelemetryLog — reusable scrolling log primitive.
 *
 * Used twice in Tab 1 (right-aside firehose + bottom headlines strip) and once
 * in Tab 2 (full-viewport comfortable-density feed). Driven by the shared
 * 10Hz-throttled state from PanopticonProvider so there's no per-frame cost.
 *
 * Auto-scrolls to the tail as rows stream in, UNLESS the user scrolls up —
 * then it releases the tail until they scroll back near the bottom.
 */

export interface TelemetryLogProps {
  /** Which row kinds to include. Defaults to all four. */
  rowKinds?: ReadonlyArray<FeedRowKind>;
  /** Tailwind height class (e.g. `h-[360px]` or `flex-1`). Required so each slot has an explicit clamp. */
  heightClass: string;
  /** Additional width/class tokens (e.g. `w-full max-w-[920px]`). */
  className?: string;
  /** Render a compact header strip showing the event counter. */
  showHeader?: boolean;
  /** `compact` = 11px font / tighter gutters for inline slots. `comfortable` = full Tab-2 density. */
  density?: 'comfortable' | 'compact';
}

const ALL_KINDS: ReadonlyArray<FeedRowKind> = ['state', 'signal', 'insight', 'anomaly'];

export default function TelemetryLog({
  rowKinds = ALL_KINDS,
  heightClass,
  className = '',
  showHeader = false,
  density = 'comfortable',
}: TelemetryLogProps) {
  const { matchData, currentTimeMs } = usePanopticonState();
  const listRef = useRef<HTMLDivElement>(null);
  const followRef = useRef(true);

  const timeline = useMemo<FeedRow[]>(
    () => (matchData ? buildTimeline(matchData) : []),
    [matchData],
  );

  const filtered = useMemo(() => {
    if (rowKinds.length === ALL_KINDS.length) return timeline;
    const allowed = new Set(rowKinds);
    return timeline.filter((r) => allowed.has(r.kind));
  }, [timeline, rowKinds]);

  const visibleRows = useMemo(() => {
    const endIdx = upperBound(filtered, currentTimeMs);
    return filtered.slice(0, endIdx);
  }, [filtered, currentTimeMs]);

  useEffect(() => {
    const el = listRef.current;
    if (!el || !followRef.current) return;
    el.scrollTop = el.scrollHeight;
  }, [visibleRows.length]);

  const onScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const el = e.currentTarget;
    const distFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    followRef.current = distFromBottom < 48;
  };

  const isCompact = density === 'compact';
  const fontSize = isCompact ? 'text-[11px]' : 'text-[12px]';
  const leading = isCompact ? 'leading-snug' : 'leading-relaxed';
  const padding = isCompact ? 'p-3' : 'p-4';

  return (
    <div className={`flex ${heightClass} flex-col ${className}`}>
      {showHeader && (
        <header className="mono flex items-center justify-between pb-2 text-[10px] uppercase tracking-[0.14em]">
          <span style={{ color: colors.textMuted }}>Telemetry</span>
          <span style={{ color: colors.playerA }}>
            {visibleRows.length.toLocaleString()} / {filtered.length.toLocaleString()} events
          </span>
        </header>
      )}
      <div
        ref={listRef}
        onScroll={onScroll}
        role="log"
        aria-live="polite"
        className={`mono flex-1 overflow-y-auto rounded-lg border ${padding} ${fontSize} ${leading}`}
        style={{
          background: '#05080F',
          borderColor: colors.border,
          color: colors.textSecondary,
        }}
      >
        {visibleRows.length === 0 ? (
          <div className="italic" style={{ color: colors.textMuted }}>
            # telemetry buffer clear — play the video to stream events
          </div>
        ) : (
          visibleRows.map((row, i) => (
            <FeedLine
              key={`${row.t}-${row.kind}-${
                row.kind === 'signal' ? row.signal.signal_name : i
              }`}
              row={row}
              compact={isCompact}
            />
          ))
        )}
      </div>
    </div>
  );
}

// ──────────────────────────── FeedLine ────────────────────────────

function FeedLine({ row, compact }: { row: FeedRow; compact: boolean }) {
  const ts = fmtClock(row.t);
  const labelWidth = compact ? 'w-14' : 'w-16';

  if (row.kind === 'signal') {
    const value = row.signal.value == null ? '—' : row.signal.value.toFixed(3);
    const z = row.signal.baseline_z_score;
    const zStr = z == null ? '  — ' : (z >= 0 ? ' +' : ' ') + z.toFixed(2) + 'σ';
    return (
      <div className="flex gap-2">
        <span style={{ color: colors.textMuted }}>[{ts}]</span>
        <span className={`${labelWidth} shrink-0`} style={{ color: colors.playerA }}>
          SIGNAL
        </span>
        <span className="flex-1 truncate">
          <span style={{ color: colors.textPrimary }}>{row.signal.signal_name}</span>
          <span style={{ color: colors.textSecondary }}> = </span>
          <span style={{ color: row.tone }}>{value}</span>
          <span style={{ color: colors.textMuted }}> {signalUnit(row.signal.signal_name)}</span>
          <span style={{ color: colors.textSecondary }}>{zStr}</span>
          {!compact && (
            <span style={{ color: colors.textMuted }}>
              {' '}
              state={row.signal.state.toLowerCase()}
            </span>
          )}
        </span>
      </div>
    );
  }

  if (row.kind === 'state') {
    return (
      <div className="flex gap-2">
        <span style={{ color: colors.textMuted }}>[{ts}]</span>
        <span className={`${labelWidth} shrink-0`} style={{ color: colors.fatigued }}>
          STATE
        </span>
        <span className="truncate" style={{ color: colors.textSecondary }}>
          {row.text}
        </span>
      </div>
    );
  }

  if (row.kind === 'insight') {
    return (
      <div className="flex gap-2">
        <span style={{ color: colors.textMuted }}>[{ts}]</span>
        <span className={`${labelWidth} shrink-0`} style={{ color: colors.opusThinking }}>
          INSIGHT
        </span>
        <span className="flex-1 truncate" style={{ color: colors.textSecondary }}>
          {row.text}
        </span>
      </div>
    );
  }

  return (
    <div className="flex gap-2">
      <span style={{ color: colors.textMuted }}>[{ts}]</span>
      <span className={`${labelWidth} shrink-0`} style={{ color: colors.anomaly }}>
        ANOMALY
      </span>
      <span className="flex-1 truncate" style={{ color: colors.anomaly }}>
        {row.text}
      </span>
    </div>
  );
}
