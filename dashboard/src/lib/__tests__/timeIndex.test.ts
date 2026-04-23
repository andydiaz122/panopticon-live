import { describe, expect, it } from 'vitest';

import {
  pickActiveLayoutAtTime,
  pickActiveTransitionForPlayer,
  pickLatestBeforeOrAt,
  pickLatestSignalsPerName,
} from '../timeIndex';

// Minimal shapes matching the generics in timeIndex.ts
type TimedItem = { timestamp_ms: number; id: string };
type Layout = { timestamp_ms: number; valid_until_ms: number; id: string };
type Transition = {
  timestamp_ms: number;
  player: 'A' | 'B';
  to_state: string;
};
type Signal = {
  timestamp_ms: number;
  player: 'A' | 'B';
  signal_name: string;
  value: number;
};

describe('pickLatestBeforeOrAt', () => {
  const items: TimedItem[] = [
    { timestamp_ms: 1000, id: 'a' },
    { timestamp_ms: 2000, id: 'b' },
    { timestamp_ms: 3000, id: 'c' },
    { timestamp_ms: 5000, id: 'd' },
  ];

  it('returns null for empty array', () => {
    expect(pickLatestBeforeOrAt([], 500)).toBeNull();
  });

  it('returns null when timeMs precedes first item', () => {
    expect(pickLatestBeforeOrAt(items, 500)).toBeNull();
  });

  it('returns first item at exact first timestamp', () => {
    expect(pickLatestBeforeOrAt(items, 1000)?.id).toBe('a');
  });

  it('returns latest item at exact match', () => {
    expect(pickLatestBeforeOrAt(items, 2000)?.id).toBe('b');
    expect(pickLatestBeforeOrAt(items, 3000)?.id).toBe('c');
  });

  it('returns latest item before a between-timestamp time', () => {
    expect(pickLatestBeforeOrAt(items, 2500)?.id).toBe('b');
    expect(pickLatestBeforeOrAt(items, 4999)?.id).toBe('c');
  });

  it('returns last item when timeMs exceeds all timestamps', () => {
    expect(pickLatestBeforeOrAt(items, 99999)?.id).toBe('d');
  });

  it('returns null on non-finite input (NaN, Infinity — defensive default)', () => {
    expect(pickLatestBeforeOrAt(items, NaN)).toBeNull();
    expect(pickLatestBeforeOrAt(items, Infinity)).toBeNull();
    expect(pickLatestBeforeOrAt(items, -Infinity)).toBeNull();
  });

  it('handles single-item array', () => {
    const single: TimedItem[] = [{ timestamp_ms: 100, id: 'only' }];
    expect(pickLatestBeforeOrAt(single, 0)).toBeNull();
    expect(pickLatestBeforeOrAt(single, 100)?.id).toBe('only');
    expect(pickLatestBeforeOrAt(single, 500)?.id).toBe('only');
  });
});

describe('pickActiveLayoutAtTime', () => {
  const layouts: Layout[] = [
    { timestamp_ms: 11000, valid_until_ms: 20000, id: 'L1' },
    { timestamp_ms: 20000, valid_until_ms: 35000, id: 'L2' },
    { timestamp_ms: 35000, valid_until_ms: 60000, id: 'L3' },
  ];

  it('returns null before first layout', () => {
    expect(pickActiveLayoutAtTime(layouts, 10999)).toBeNull();
  });

  it('returns the bracketing layout at the window start', () => {
    expect(pickActiveLayoutAtTime(layouts, 11000)?.id).toBe('L1');
  });

  it('returns the bracketing layout mid-window', () => {
    expect(pickActiveLayoutAtTime(layouts, 15000)?.id).toBe('L1');
  });

  it('returns the NEXT layout at boundary valid_until_ms', () => {
    // L1.valid_until_ms === L2.timestamp_ms === 20000
    expect(pickActiveLayoutAtTime(layouts, 20000)?.id).toBe('L2');
  });

  it('returns null after last layout expires', () => {
    expect(pickActiveLayoutAtTime(layouts, 60000)).toBeNull();
    expect(pickActiveLayoutAtTime(layouts, 99999)).toBeNull();
  });

  it('returns null on empty array', () => {
    expect(pickActiveLayoutAtTime([], 12345)).toBeNull();
  });
});

describe('pickActiveTransitionForPlayer', () => {
  const transitions: Transition[] = [
    { timestamp_ms: 500, player: 'A', to_state: 'UNKNOWN' },
    { timestamp_ms: 1000, player: 'B', to_state: 'PRE_SERVE_RITUAL' },
    { timestamp_ms: 1500, player: 'A', to_state: 'PRE_SERVE_RITUAL' },
    { timestamp_ms: 2000, player: 'A', to_state: 'ACTIVE_RALLY' },
  ];

  it('returns null before any transition', () => {
    expect(pickActiveTransitionForPlayer(transitions, 100, 'A')).toBeNull();
  });

  it('returns only the requested players transitions', () => {
    // At 1200ms, only A's 500ms UNKNOWN transition has fired
    expect(pickActiveTransitionForPlayer(transitions, 1200, 'A')?.to_state).toBe(
      'UNKNOWN',
    );
  });

  it('returns latest player-A transition across interleaved B transitions', () => {
    expect(pickActiveTransitionForPlayer(transitions, 1800, 'A')?.to_state).toBe(
      'PRE_SERVE_RITUAL',
    );
    expect(pickActiveTransitionForPlayer(transitions, 5000, 'A')?.to_state).toBe(
      'ACTIVE_RALLY',
    );
  });
});

describe('pickLatestSignalsPerName', () => {
  const signals: Signal[] = [
    { timestamp_ms: 100, player: 'A', signal_name: 'x', value: 1 },
    { timestamp_ms: 200, player: 'A', signal_name: 'y', value: 10 },
    { timestamp_ms: 300, player: 'A', signal_name: 'x', value: 2 },
    { timestamp_ms: 300, player: 'B', signal_name: 'x', value: 999 }, // filtered
    { timestamp_ms: 400, player: 'A', signal_name: 'y', value: 20 },
  ];

  it('picks latest per signal_name for Player A only', () => {
    const out = pickLatestSignalsPerName(signals, 500);
    expect(out.x?.value).toBe(2);
    expect(out.y?.value).toBe(20);
  });

  it('ignores Player B samples (DECISION-008 scope)', () => {
    const out = pickLatestSignalsPerName(signals, 500);
    expect(out.x?.player).toBe('A');
  });

  it('respects timeMs cutoff', () => {
    const out = pickLatestSignalsPerName(signals, 250);
    expect(out.x?.value).toBe(1);
    expect(out.y?.value).toBe(10);
  });

  it('returns empty object before first sample', () => {
    expect(pickLatestSignalsPerName(signals, 0)).toEqual({});
  });
});
