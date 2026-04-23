import { describe, expect, it } from 'vitest';

import { zScoreToTone } from '../zScoreToTone';

describe('zScoreToTone — baseline bucket (|z| < 1)', () => {
  it('returns baseline for z=0', () => {
    expect(zScoreToTone(0, 'fatigue')).toBe('baseline');
  });

  it('returns baseline at |z|=0.99', () => {
    expect(zScoreToTone(0.99, 'fatigue')).toBe('baseline');
    expect(zScoreToTone(-0.99, 'drift')).toBe('baseline');
  });

  it('returns baseline for null / undefined / NaN / Infinity (all non-finite defaults to baseline)', () => {
    expect(zScoreToTone(null, 'fatigue')).toBe('baseline');
    expect(zScoreToTone(undefined, 'fatigue')).toBe('baseline');
    expect(zScoreToTone(NaN, 'fatigue')).toBe('baseline');
    expect(zScoreToTone(Infinity, 'fatigue')).toBe('baseline');
    expect(zScoreToTone(-Infinity, 'drift')).toBe('baseline');
  });
});

describe('zScoreToTone — energized bucket (1 ≤ |z| < 2, sign aligns)', () => {
  it('energy signal with positive z → energized', () => {
    expect(zScoreToTone(1.0, 'energy')).toBe('energized');
    expect(zScoreToTone(1.99, 'energy')).toBe('energized');
  });

  it('fatigue signal with negative z → energized (fresh)', () => {
    expect(zScoreToTone(-1.5, 'fatigue')).toBe('energized');
  });

  it('drift signal with negative z → energized (steady)', () => {
    expect(zScoreToTone(-1.5, 'drift')).toBe('energized');
  });
});

describe('zScoreToTone — fatigued bucket (1 ≤ |z| < 2, sign opposes)', () => {
  it('fatigue signal with positive z → fatigued', () => {
    expect(zScoreToTone(1.5, 'fatigue')).toBe('fatigued');
  });

  it('drift signal with positive z → fatigued', () => {
    expect(zScoreToTone(1.5, 'drift')).toBe('fatigued');
  });

  it('energy signal with negative z → fatigued', () => {
    expect(zScoreToTone(-1.5, 'energy')).toBe('fatigued');
  });
});

describe('zScoreToTone — anomaly bucket (|z| ≥ 2)', () => {
  it('returns anomaly at exactly |z|=2', () => {
    expect(zScoreToTone(2, 'fatigue')).toBe('anomaly');
    expect(zScoreToTone(-2, 'drift')).toBe('anomaly');
    expect(zScoreToTone(2, 'energy')).toBe('anomaly');
  });

  it('returns anomaly well above 2σ regardless of direction', () => {
    expect(zScoreToTone(3.5, 'fatigue')).toBe('anomaly');
    expect(zScoreToTone(-4, 'energy')).toBe('anomaly');
  });
});

describe('zScoreToTone — boundary correctness', () => {
  it('transitions at 1.0', () => {
    expect(zScoreToTone(0.999999, 'fatigue')).toBe('baseline');
    expect(zScoreToTone(1.0, 'fatigue')).toBe('fatigued');
  });

  it('transitions at 2.0', () => {
    expect(zScoreToTone(1.999999, 'drift')).toBe('fatigued');
    expect(zScoreToTone(2.0, 'drift')).toBe('anomaly');
  });
});
