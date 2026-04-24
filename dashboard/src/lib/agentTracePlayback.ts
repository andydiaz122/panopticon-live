/**
 * Pacing helpers for the Orchestration Console (PATTERN-056 — Multi-Agent Trace Playback).
 *
 * The real Scouting Committee runs 20-60+ seconds offline. For the demo we
 * re-time every event onto a deterministic pacing envelope so judges see a
 * watchable ~30-45s sequence that FEELS like real reasoning.
 *
 * IMPORTANT: these delays are UI-only — they do NOT reflect the real agent
 * wall-clock times. The `ARCHITECTURAL PREVIEW: SWARM ACCELERATED FOR DEMO`
 * banner discloses that.
 */

import type { AgentStep, AgentTrace, TraceEvent } from './types';

/**
 * Baud-rate pacing for text reveal (chars/sec). 25 cps is the mid-point of
 * the 20-30 cps range that mimics real LLM token-generation latency. A
 * 500-char block takes ~20s at this rate; a 250-char block takes ~10s.
 * Transport UI exposes a 4× Fast Forward multiplier so judges can skip the
 * wait when they've seen enough.
 */
export const TEXT_BAUD_CHARS_PER_SEC = 25;

/**
 * Floor for text-event delay (ms). Prevents near-instant flashes for
 * empty/single-character outputs while still staying snappier than
 * the thinking/tool-result pacing.
 */
export const TEXT_MIN_DELAY_MS = 300;

/** UI delay (ms) to reveal a single event based on its kind. */
export function delayForEvent(event: TraceEvent): number {
  switch (event.kind) {
    case 'thinking':
      // Dramatic — we want judges to SEE Opus reasoning
      return 800;
    case 'tool_call':
      // Quick — the interesting payload is the result
      return 300;
    case 'tool_result':
      return 700;
    case 'text': {
      // Fixed baud rate: delay scales linearly with content length so a
      // 500-char block takes ~20s (≈ real token-generation cadence). NO upper
      // cap — long outputs ARE expected to feel long. The Orchestration
      // Console provides a Fast Forward button for impatient viewers.
      const len = event.content.length;
      const baudMs = Math.ceil((len / TEXT_BAUD_CHARS_PER_SEC) * 1000);
      return Math.max(TEXT_MIN_DELAY_MS, baudMs);
    }
    case 'handoff':
      // Longest — state transition moment. Let the judge feel it.
      return 1600;
  }
}

/**
 * Sentinel appended by the backend `_EventRecorder` when `TraceToolResult.output_json`
 * exceeds `TRACE_MAX_OUTPUT_JSON_CHARS` (= 2000). Must match the Python constant
 * in `backend/agents/scouting_committee.py::TRACE_TRUNCATION_MARKER` byte-for-byte.
 * (GOTCHA-027: trace payload explosion guard.)
 */
export const TRACE_TRUNCATION_MARKER = ' ... [Array truncated for UI playback]';

/**
 * Format a match-time timestamp in ms to mm:ss (or h:mm:ss for > 1h matches).
 * Used to surface the AgentTrace.match_time_range_ms as a header chip so judges
 * can map the swarm's analysis window to the video timecode they're watching.
 */
export function formatMatchTimecode(ms: number): string {
  if (ms < 0 || !Number.isFinite(ms)) return '0:00';
  const totalSec = Math.floor(ms / 1000);
  const h = Math.floor(totalSec / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return `${m}:${String(s).padStart(2, '0')}`;
}

/** Pretty-print a match-time range. Returns null for null/empty ranges. */
export function formatMatchTimeRange(
  range: readonly [number, number] | null | undefined,
): string | null {
  if (!range) return null;
  const [start, end] = range;
  if (start === end) return formatMatchTimecode(start);
  return `${formatMatchTimecode(start)}–${formatMatchTimecode(end)}`;
}

/**
 * True if the tool-result output carries the truncation sentinel — i.e., the
 * backend had to trim it for UI safety. The frontend uses this to render a
 * "(truncated)" badge; the LLM saw the full payload regardless.
 */
export function isTruncatedToolOutput(outputJson: string): boolean {
  return outputJson.endsWith(TRACE_TRUNCATION_MARKER);
}

/**
 * CRITICAL SAFETY: GOTCHA-030 — the truncation marker produces INVALID JSON
 * when appended to a hard-cut serialized payload. ANY naive `JSON.parse()` call
 * on `TraceToolResult.output_json` will throw `SyntaxError`, trip React's
 * error boundary, and white-screen Tab 3 during the demo. This helper is the
 * ONLY sanctioned way to parse an output_json value — it returns the parsed
 * object on success, OR null on any failure (truncated, malformed, binary, etc).
 * Callers should always fall back to raw-text rendering when `parsed === null`.
 *
 * DO NOT wrap this helper over a tight try/catch yourself and pretend it's
 * safe — use this helper, trust its contract.
 */
export function safeParseOutputJson(outputJson: string): {
  parsed: unknown | null;
  isTruncated: boolean;
  raw: string;
} {
  const isTruncated = isTruncatedToolOutput(outputJson);
  if (isTruncated) {
    // Known-invalid by construction — don't even try.
    return { parsed: null, isTruncated, raw: outputJson };
  }
  try {
    return { parsed: JSON.parse(outputJson), isTruncated: false, raw: outputJson };
  } catch {
    return { parsed: null, isTruncated: false, raw: outputJson };
  }
}

/** Flat list of events in playback order, with 'handoff' events already embedded per step. */
export interface PlaybackItem {
  stepIndex: number;
  agentName: string;
  agentRole: string;
  event: TraceEvent;
  /** Cumulative UI delay (ms) at which this item should be revealed. */
  revealAtMs: number;
}

/** Flatten an AgentTrace into an ordered list of (step, event, revealAt) for playback. */
export function flattenTraceForPlayback(trace: AgentTrace): PlaybackItem[] {
  const items: PlaybackItem[] = [];
  let cumulativeMs = 0;
  for (let i = 0; i < trace.steps.length; i++) {
    const step = trace.steps[i];
    for (const event of step.events) {
      cumulativeMs += delayForEvent(event);
      items.push({
        stepIndex: i,
        agentName: step.agent_name,
        agentRole: step.agent_role,
        event,
        revealAtMs: cumulativeMs,
      });
    }
  }
  return items;
}

/** Total UI playback duration (ms) for a full trace. */
export function totalPlaybackDurationMs(trace: AgentTrace): number {
  const items = flattenTraceForPlayback(trace);
  return items.length === 0 ? 0 : items[items.length - 1].revealAtMs;
}

/** True if the step has produced any visible events by the current playback cursor. */
export function stepHasActivity(
  step: AgentStep,
  stepIndex: number,
  revealedItems: ReadonlyArray<PlaybackItem>,
): boolean {
  return revealedItems.some((it) => it.stepIndex === stepIndex);
}
