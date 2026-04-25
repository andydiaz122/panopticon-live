import { describe, expect, it } from 'vitest';

import { computePlaybackRate } from '../useSlowMoAtAnomalies';

/**
 * A2a — playbackRate ramp/hold behavior around anomaly timestamps.
 *
 * The pure function is easy to unit-test; the surrounding hook is harder
 * (video ref + rAF) and is covered by visual QA at record time.
 */

const CONFIG = { slowRate: 0.25, rampMs: 500, holdMs: 3000 } as const;
const ANOMALIES = [35_900, 45_300, 59_100] as const;

describe('computePlaybackRate — outside any anomaly window', () => {
  it('returns 1.0 well before the first anomaly', () => {
    expect(computePlaybackRate(0, ANOMALIES, CONFIG)).toBe(1.0);
    expect(computePlaybackRate(30_000, ANOMALIES, CONFIG)).toBe(1.0);
  });

  it('returns 1.0 between two non-overlapping anomaly windows', () => {
    // Window around 35_900 ends at 35_900 + 500 + 3000 = 39_400
    // Window around 45_300 starts at 44_800
    expect(computePlaybackRate(40_000, ANOMALIES, CONFIG)).toBe(1.0);
    expect(computePlaybackRate(44_000, ANOMALIES, CONFIG)).toBe(1.0);
  });

  it('returns 1.0 after all anomaly windows', () => {
    // Last anomaly 59_100, window ends 59_100 + 500 + 3000 = 62_600
    expect(computePlaybackRate(62_601, ANOMALIES, CONFIG)).toBe(1.0);
    expect(computePlaybackRate(100_000, ANOMALIES, CONFIG)).toBe(1.0);
  });

  it('returns 1.0 when anomalies array is empty', () => {
    expect(computePlaybackRate(45_300, [], CONFIG)).toBe(1.0);
  });
});

describe('computePlaybackRate — ramp-in (500ms before anomaly)', () => {
  it('returns 1.0 at the exact ramp-in start boundary', () => {
    // Ramp-in starts at anomaly - rampMs = 45_300 - 500 = 44_800
    const rate = computePlaybackRate(44_800, ANOMALIES, CONFIG);
    expect(rate).toBeCloseTo(1.0, 3);
  });

  it('is between 1.0 and slowRate during ramp-in', () => {
    const rate = computePlaybackRate(45_050, ANOMALIES, CONFIG); // mid-ramp
    expect(rate).toBeGreaterThan(CONFIG.slowRate);
    expect(rate).toBeLessThan(1.0);
    // Midpoint (250ms into 500ms ramp) = lerp(1.0, 0.25, 0.5) = 0.625
    expect(rate).toBeCloseTo(0.625, 3);
  });

  it('reaches slowRate at the anomaly timestamp', () => {
    const rate = computePlaybackRate(45_300, ANOMALIES, CONFIG);
    expect(rate).toBeCloseTo(CONFIG.slowRate, 3);
  });
});

describe('computePlaybackRate — hold phase (3000ms after anomaly)', () => {
  it('holds at slowRate immediately after anomaly', () => {
    expect(computePlaybackRate(45_301, ANOMALIES, CONFIG)).toBe(CONFIG.slowRate);
    expect(computePlaybackRate(46_000, ANOMALIES, CONFIG)).toBe(CONFIG.slowRate);
  });

  it('holds at slowRate through the entire hold window', () => {
    // Hold ends at anomaly + holdMs = 45_300 + 3000 = 48_300
    expect(computePlaybackRate(48_000, ANOMALIES, CONFIG)).toBe(CONFIG.slowRate);
    expect(computePlaybackRate(48_300, ANOMALIES, CONFIG)).toBe(CONFIG.slowRate);
  });
});

describe('computePlaybackRate — ramp-out (500ms after hold)', () => {
  it('starts ramping back toward 1.0 after hold ends', () => {
    // Ramp-out starts at anomaly + holdMs = 48_300
    const rate = computePlaybackRate(48_550, ANOMALIES, CONFIG); // mid ramp-out
    expect(rate).toBeGreaterThan(CONFIG.slowRate);
    expect(rate).toBeLessThan(1.0);
    // Midpoint = lerp(0.25, 1.0, 0.5) = 0.625
    expect(rate).toBeCloseTo(0.625, 3);
  });

  it('reaches 1.0 at the ramp-out end boundary', () => {
    // Ramp-out ends at anomaly + holdMs + rampMs = 48_800
    const rate = computePlaybackRate(48_800, ANOMALIES, CONFIG);
    expect(rate).toBeCloseTo(1.0, 3);
  });
});

describe('computePlaybackRate — multiple anomalies', () => {
  it('applies slow-mo at each of the three hero-clip anomalies', () => {
    expect(computePlaybackRate(35_900, ANOMALIES, CONFIG)).toBeCloseTo(0.25, 3);
    expect(computePlaybackRate(45_300, ANOMALIES, CONFIG)).toBeCloseTo(0.25, 3);
    expect(computePlaybackRate(59_100, ANOMALIES, CONFIG)).toBeCloseTo(0.25, 3);
  });

  it('returns 1.0 between anomaly windows', () => {
    // Between anomaly 1 window end (35_900 + 3500 = 39_400) and anomaly 2 window start (45_300 - 500 = 44_800)
    expect(computePlaybackRate(42_000, ANOMALIES, CONFIG)).toBe(1.0);
  });
});

describe('computePlaybackRate — config overrides', () => {
  it('respects custom slowRate', () => {
    const cfg = { ...CONFIG, slowRate: 0.5 };
    expect(computePlaybackRate(45_300, ANOMALIES, cfg)).toBeCloseTo(0.5, 3);
  });

  it('respects custom rampMs', () => {
    const cfg = { ...CONFIG, rampMs: 1000 };
    // With 1000ms ramp, window starts at 45_300 - 1000 = 44_300
    expect(computePlaybackRate(44_299, ANOMALIES, cfg)).toBe(1.0);
    expect(computePlaybackRate(44_800, ANOMALIES, cfg)).toBeCloseTo(0.625, 3); // midpoint
  });
});
