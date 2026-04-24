import { colors } from './design-tokens';
import { SIGNAL_COPY } from './signalCopy';
import type {
  AnomalyEvent,
  AuthoredStateTransition,
  CoachInsight,
  MatchData,
  QualitativeNarration,
  SignalSample,
  StateTransition,
} from './types';

/**
 * Shared telemetry-feed helpers — extracted from SignalFeed.tsx so both Tab 2
 * (full-viewport) and Tab 1 (inline log cards) can share one timeline shape,
 * tone palette, and formatting vocabulary.
 */

export type FeedRowKind = 'state' | 'signal' | 'insight' | 'anomaly';

export type FeedRow =
  | { kind: 'state'; t: number; text: string }
  | { kind: 'signal'; t: number; signal: SignalSample; tone: string }
  | { kind: 'insight'; t: number; text: string }
  | { kind: 'anomaly'; t: number; text: string };

/** Build the complete ordered timeline — merges signals, transitions, insights, anomalies. */
export function buildTimeline(data: MatchData): FeedRow[] {
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

  // G43 display-only — authored 7-state RallyMicroPhase timeline. Rendered
  // alongside live transitions with a 📝 AUTHORED prefix so judges can see
  // both realities in the same log. Nullish-coalesce per G28 — pre-migration
  // JSON without display_transitions still renders.
  for (const adt of data.display_transitions ?? []) {
    if (adt.player !== 'A') continue;
    rows.push({
      kind: 'state',
      t: adt.timestamp_ms,
      text: authoredTransitionText(adt),
    });
  }

  for (const insight of data.coach_insights) {
    rows.push({
      kind: 'insight',
      t: insight.timestamp_ms,
      text: oneLineOpener(insight),
    });
  }

  // G43 display-only — authored broadcaster narrations. Prefixed with 👤 so
  // they read as "written by a human broadcaster," not as Opus output.
  for (const narr of data.display_narrations ?? []) {
    rows.push({
      kind: 'insight',
      t: narr.timestamp_ms,
      text: authoredNarrationText(narr),
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

/** Binary search for first index whose timestamp > t. Slice is [0, upperBound). */
export function upperBound(rows: FeedRow[], t: number): number {
  let lo = 0;
  let hi = rows.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (rows[mid].t <= t) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

/** Signal-value color tone by |z-score| magnitude. */
export function toneForSignal(s: SignalSample): string {
  const z = s.baseline_z_score;
  if (z == null) return colors.textSecondary;
  if (Math.abs(z) >= 2) return colors.anomaly;
  if (Math.abs(z) >= 1) return colors.fatigued;
  return colors.energized;
}

/** mm:ss.cc clock format for log timestamps. */
export function fmtClock(ms: number): string {
  const total = Math.max(0, Math.floor(ms));
  const m = Math.floor(total / 60000);
  const s = Math.floor((total % 60000) / 1000);
  const cs = Math.floor((total % 1000) / 10);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(cs).padStart(2, '0')}`;
}

export function transitionText(tr: StateTransition): string {
  return `player=${tr.player} ${tr.from_state} -> ${tr.to_state} reason=${tr.reason}`;
}

/** Authored transition label — prefixed 📝 AUTHORED so judges can visually
 * separate the G43 display-only 7-state timeline from live CV transitions.
 * Reason field is always "hand_authored" for AuthoredStateTransition, so we
 * don't render it (noise). */
export function authoredTransitionText(tr: AuthoredStateTransition): string {
  return `📝 AUTHORED · player=${tr.player} ${tr.from_state} -> ${tr.to_state}`;
}

/** Authored narration one-liner — prefixed 👤 BROADCAST so judges read it as
 * human-authored broadcaster script, not as Opus output. */
export function authoredNarrationText(n: QualitativeNarration): string {
  const flat = n.narration_text.replace(/\s+/g, ' ').trim();
  const truncated = flat.length > 110 ? flat.slice(0, 107) + '…' : flat;
  return `👤 BROADCAST · ${truncated}`;
}

export function oneLineOpener(c: CoachInsight): string {
  const flat = c.commentary.replace(/\s+/g, ' ').trim();
  return flat.length > 110 ? flat.slice(0, 107) + '…' : flat;
}

export function anomalyText(a: AnomalyEvent): string {
  return `${a.signal_name} z=${a.z_score.toFixed(2)} value=${a.value.toFixed(3)} severity=${a.severity.toFixed(2)}`;
}

/** Signal-name → unit lookup for FeedLine rendering. */
export function signalUnit(signalName: string): string {
  const copy = SIGNAL_COPY[signalName as keyof typeof SIGNAL_COPY];
  return copy?.unit ?? '';
}
