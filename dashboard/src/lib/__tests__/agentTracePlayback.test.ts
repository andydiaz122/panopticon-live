import { describe, expect, it } from 'vitest';

import {
  TEXT_BAUD_CHARS_PER_SEC,
  TEXT_MIN_DELAY_MS,
  TRACE_TRUNCATION_MARKER,
  delayForEvent,
  flattenTraceForPlayback,
  formatMatchTimecode,
  formatMatchTimeRange,
  isTruncatedToolOutput,
  safeParseOutputJson,
  totalPlaybackDurationMs,
} from '@/lib/agentTracePlayback';
import type { AgentStep, AgentTrace, TraceEvent } from '@/lib/types';

// ──────────────────────────── Fixtures ────────────────────────────

function makeStep(
  agentName: string,
  startMs: number,
  endMs: number,
  events: TraceEvent[],
): AgentStep {
  return {
    agent_name: agentName,
    agent_role: 'Test Role',
    started_at_ms: startMs,
    completed_at_ms: endMs,
    events,
  };
}

function makeTrace(steps: AgentStep[]): AgentTrace {
  return {
    match_id: 'utr_01',
    generated_at: '2026-04-23T12:00:00Z',
    committee_goal: 'test',
    steps,
    final_report_markdown: '# test',
    total_compute_ms: 1000,
  };
}

// ──────────────────────────── Delay pacing ────────────────────────────

describe('delayForEvent', () => {
  it('assigns dramatic pause to thinking events', () => {
    expect(delayForEvent({ kind: 'thinking', t_ms: 0, content: 'x' })).toBeGreaterThanOrEqual(500);
  });

  it('assigns longest pause to handoff events', () => {
    const handoff = delayForEvent({
      kind: 'handoff',
      t_ms: 0,
      from_agent: 'A',
      to_agent: 'B',
      payload_summary: 'x',
    });
    const thinking = delayForEvent({ kind: 'thinking', t_ms: 0, content: 'x' });
    expect(handoff).toBeGreaterThan(thinking);
  });

  it('scales text delay with content length', () => {
    const short = delayForEvent({ kind: 'text', t_ms: 0, content: 'short' });
    const long = delayForEvent({
      kind: 'text', t_ms: 0,
      content: 'A'.repeat(500),
    });
    expect(long).toBeGreaterThan(short);
  });

  it('text delay scales linearly at the baud rate', () => {
    const CHARS = 250;
    const delay = delayForEvent({
      kind: 'text', t_ms: 0,
      content: 'A'.repeat(CHARS),
    });
    // 250 chars / 25 cps = 10s → 10000ms
    const expected = Math.ceil((CHARS / TEXT_BAUD_CHARS_PER_SEC) * 1000);
    expect(delay).toBeGreaterThanOrEqual(expected - 200);
    expect(delay).toBeLessThanOrEqual(expected + 200);
  });

  it('long text outputs take realistically long (no artificial cap)', () => {
    // Under baud-rate pacing, 10k chars = 400 seconds. This is BY DESIGN —
    // long reasoning blocks feel long; Fast Forward is how judges skip.
    const veryLong = delayForEvent({
      kind: 'text', t_ms: 0,
      content: 'A'.repeat(10_000),
    });
    const expected = Math.ceil((10_000 / TEXT_BAUD_CHARS_PER_SEC) * 1000);
    expect(veryLong).toBe(expected);
    expect(veryLong).toBeGreaterThan(300_000); // sanity: >5 minutes
  });

  it('minimum delay floor prevents near-instant text flashes', () => {
    const empty = delayForEvent({ kind: 'text', t_ms: 0, content: '' });
    const oneChar = delayForEvent({ kind: 'text', t_ms: 0, content: 'x' });
    expect(empty).toBeGreaterThanOrEqual(200);
    expect(oneChar).toBeGreaterThanOrEqual(200);
    expect(empty).toBe(TEXT_MIN_DELAY_MS);
  });
});

// ──────────────────────────── GOTCHA-030: JSON Syntax Trap ────────────────────────────

describe('safeParseOutputJson', () => {
  it('parses valid JSON and returns the object', () => {
    const { parsed, isTruncated, raw } = safeParseOutputJson('{"count": 5, "ok": true}');
    expect(parsed).toEqual({ count: 5, ok: true });
    expect(isTruncated).toBe(false);
    expect(raw).toBe('{"count": 5, "ok": true}');
  });

  it('returns null (NOT throws) on truncated payload', () => {
    // Backend pattern: serialized JSON hard-cut + marker appended = invalid JSON.
    // If a future component naively JSON.parses this, it would SyntaxError and
    // white-screen Tab 3 during the demo. safeParseOutputJson MUST return null
    // gracefully instead of letting the exception escape.
    const truncated = '{"samples": [1, 2, 3, 4' + TRACE_TRUNCATION_MARKER;
    const { parsed, isTruncated, raw } = safeParseOutputJson(truncated);
    expect(parsed).toBeNull();
    expect(isTruncated).toBe(true);
    expect(raw).toBe(truncated); // raw is always preserved for fallback render
  });

  it('returns null on generic malformed JSON (no truncation marker)', () => {
    const { parsed, isTruncated } = safeParseOutputJson('{not: valid');
    expect(parsed).toBeNull();
    expect(isTruncated).toBe(false);
  });

  it('does not throw on empty string', () => {
    expect(() => safeParseOutputJson('')).not.toThrow();
    const { parsed } = safeParseOutputJson('');
    expect(parsed).toBeNull();
  });

  it('does not throw on binary-ish garbage', () => {
    const garbage = '\x00\x01\xFF\xFE' + TRACE_TRUNCATION_MARKER;
    expect(() => safeParseOutputJson(garbage)).not.toThrow();
  });
});

describe('formatMatchTimecode + formatMatchTimeRange', () => {
  it('formats ms to m:ss for matches under 1 hour', () => {
    expect(formatMatchTimecode(0)).toBe('0:00');
    expect(formatMatchTimecode(5_000)).toBe('0:05');
    expect(formatMatchTimecode(65_000)).toBe('1:05');
    expect(formatMatchTimecode(179_000)).toBe('2:59');
  });

  it('formats ms to h:mm:ss for long matches', () => {
    expect(formatMatchTimecode(3_600_000)).toBe('1:00:00');
    expect(formatMatchTimecode(3_665_000)).toBe('1:01:05');
  });

  it('handles negative / non-finite ms defensively', () => {
    expect(formatMatchTimecode(-10)).toBe('0:00');
    expect(formatMatchTimecode(Number.NaN)).toBe('0:00');
    expect(formatMatchTimecode(Number.POSITIVE_INFINITY)).toBe('0:00');
  });

  it('returns null when range is null/undefined (backwards-compat)', () => {
    expect(formatMatchTimeRange(null)).toBeNull();
    expect(formatMatchTimeRange(undefined)).toBeNull();
  });

  it('collapses a single-point range to one timecode', () => {
    expect(formatMatchTimeRange([5_000, 5_000] as const)).toBe('0:05');
  });

  it('joins a multi-point range with an en-dash', () => {
    expect(formatMatchTimeRange([0, 60_000] as const)).toBe('0:00–1:00');
    expect(formatMatchTimeRange([1_500, 58_200] as const)).toBe('0:01–0:58');
  });
});

describe('isTruncatedToolOutput', () => {
  it('detects the backend truncation sentinel', () => {
    expect(isTruncatedToolOutput('anything' + TRACE_TRUNCATION_MARKER)).toBe(true);
  });

  it('returns false for a complete small payload', () => {
    expect(isTruncatedToolOutput('{"ok": true}')).toBe(false);
  });

  it('only matches the sentinel at the END (prefix match is rejected)', () => {
    const notTruncated = TRACE_TRUNCATION_MARKER + ' followed by more';
    expect(isTruncatedToolOutput(notTruncated)).toBe(false);
  });
});

// ──────────────────────────── Flattening ────────────────────────────

describe('flattenTraceForPlayback', () => {
  it('emits events in step + event order', () => {
    const trace = makeTrace([
      makeStep('Analytics', 0, 1000, [
        { kind: 'text', t_ms: 10, content: 'a1' },
        { kind: 'text', t_ms: 20, content: 'a2' },
      ]),
      makeStep('Technical', 1000, 2000, [
        { kind: 'text', t_ms: 30, content: 'b1' },
      ]),
    ]);
    const items = flattenTraceForPlayback(trace);
    expect(items.map((i) => (i.event as { content: string }).content)).toEqual(['a1', 'a2', 'b1']);
    expect(items[0].stepIndex).toBe(0);
    expect(items[2].stepIndex).toBe(1);
  });

  it('reveal timestamps are monotonically increasing', () => {
    const trace = makeTrace([
      makeStep('Analytics', 0, 1000, [
        { kind: 'thinking', t_ms: 0, content: 'x' },
        { kind: 'tool_call', t_ms: 1, tool_name: 'q', input_json: '{}' },
        { kind: 'text', t_ms: 2, content: 'done' },
      ]),
    ]);
    const items = flattenTraceForPlayback(trace);
    let last = -1;
    for (const item of items) {
      expect(item.revealAtMs).toBeGreaterThan(last);
      last = item.revealAtMs;
    }
  });

  it('empty trace produces empty flattening', () => {
    const trace = makeTrace([]);
    expect(flattenTraceForPlayback(trace)).toEqual([]);
  });

  it('total duration matches last revealAtMs', () => {
    const trace = makeTrace([
      makeStep('A', 0, 100, [
        { kind: 'text', t_ms: 0, content: 'x' },
        { kind: 'handoff', t_ms: 1, from_agent: 'A', to_agent: 'B', payload_summary: 'p' },
      ]),
    ]);
    const items = flattenTraceForPlayback(trace);
    const total = totalPlaybackDurationMs(trace);
    expect(total).toBe(items[items.length - 1].revealAtMs);
  });
});

// ──────────────────────────── Plausible total duration ────────────────────────────

describe('totalPlaybackDurationMs', () => {
  it('keeps a realistic 3-agent trace inside a demo-watchable window', () => {
    // Representative shape: each agent emits 1 thinking + 1 text + (handoffs for 2 gaps).
    // Final Tactical Strategist text is ~500 chars to match a real tactical brief —
    // at 25 cps baud that alone takes 20s. Upper bound is 180s (3 min) because FF
    // is always available; judges who watch the full thing still see a coherent pace.
    const trace = makeTrace([
      makeStep('Analytics Specialist', 0, 5000, [
        { kind: 'thinking', t_ms: 0, content: 'probe signal arrays' },
        { kind: 'tool_call', t_ms: 1, tool_name: 'get_signal_window', input_json: '{}' },
        { kind: 'tool_result', t_ms: 2, tool_name: 'get_signal_window', output_json: '{}', is_error: false },
        { kind: 'text', t_ms: 3, content: 'Found 3 anomalies in crouch depth.' },
        { kind: 'handoff', t_ms: 4, from_agent: 'Analytics Specialist', to_agent: 'Technical Biomechanics Coach', payload_summary: 'z=2.3' },
      ]),
      makeStep('Technical Biomechanics Coach', 5000, 10000, [
        { kind: 'thinking', t_ms: 0, content: 'map to literature' },
        { kind: 'text', t_ms: 1, content: 'Posterior chain fatigue.' },
        { kind: 'handoff', t_ms: 2, from_agent: 'Technical Biomechanics Coach', to_agent: 'Tactical Strategist', payload_summary: 'quad fatigue' },
      ]),
      makeStep('Tactical Strategist', 10000, 15000, [
        { kind: 'thinking', t_ms: 0, content: 'synthesize' },
        { kind: 'text', t_ms: 1, content: 'A'.repeat(500) },
      ]),
    ]);
    const total = totalPlaybackDurationMs(trace);
    // At 25 cps, the 500-char final text alone is ~20s. Full trace should be
    // readable (>= 5s) and fit a 3-minute demo budget even without Fast Forward.
    expect(total).toBeGreaterThanOrEqual(5000);
    expect(total).toBeLessThanOrEqual(180_000);
  });
});
