import { describe, expect, it } from 'vitest';

import { clampFrameIdx } from '../timeIndex';

/**
 * PATTERN-045 regression guard. The demo MUST never crash when the user
 * scrubs to end-of-video or before 0.
 */
describe('clampFrameIdx', () => {
  it('returns 0 for negative currentTime', () => {
    expect(clampFrameIdx(-1, 30, 1800)).toBe(0);
    expect(clampFrameIdx(-0.001, 30, 1800)).toBe(0);
  });

  it('returns 0 at exactly time 0', () => {
    expect(clampFrameIdx(0, 30, 1800)).toBe(0);
  });

  it('returns floored index mid-range', () => {
    expect(clampFrameIdx(10, 30, 1800)).toBe(300);
    expect(clampFrameIdx(10.999, 30, 1800)).toBe(329);
  });

  it('clamps to length-1 past end', () => {
    expect(clampFrameIdx(60, 30, 1800)).toBe(1799);
    expect(clampFrameIdx(60.001, 30, 1800)).toBe(1799);
    expect(clampFrameIdx(99999, 30, 1800)).toBe(1799);
  });

  it('returns 0 on empty array length', () => {
    expect(clampFrameIdx(5, 30, 0)).toBe(0);
    expect(clampFrameIdx(5, 30, -1)).toBe(0);
  });

  it('returns 0 on non-finite currentTime', () => {
    expect(clampFrameIdx(NaN, 30, 1800)).toBe(0);
    expect(clampFrameIdx(Infinity, 30, 1800)).toBe(0);
    expect(clampFrameIdx(-Infinity, 30, 1800)).toBe(0);
  });

  it('returns 0 on invalid fps', () => {
    expect(clampFrameIdx(5, 0, 1800)).toBe(0);
    expect(clampFrameIdx(5, -30, 1800)).toBe(0);
    expect(clampFrameIdx(5, NaN, 1800)).toBe(0);
  });

  it('never returns NaN, undefined, or out-of-range', () => {
    const cases: Array<[number, number, number]> = [
      [0, 30, 1],
      [0.5, 30, 1],
      [1, 30, 1],
      [100, 30, 1],
      [-5, 30, 1],
      [10, 60, 1800],
    ];
    for (const [t, fps, len] of cases) {
      const idx = clampFrameIdx(t, fps, len);
      expect(Number.isFinite(idx)).toBe(true);
      expect(idx).toBeGreaterThanOrEqual(0);
      expect(idx).toBeLessThanOrEqual(Math.max(0, len - 1));
    }
  });
});
