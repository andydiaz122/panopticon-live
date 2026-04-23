import { describe, expect, it } from 'vitest';

import { SIGNAL_COPY, anomalyCopy } from '../signalCopy';
import type { SignalName } from '../types';

/**
 * Fan-copy contract (DECISION-009 + .claude/skills/biometric-fan-experience).
 *
 * Every SignalName MUST have an entry in SIGNAL_COPY. Every entry MUST
 * satisfy the length budgets + no-Player-B rule.
 */
const ALL_SIGNAL_NAMES: SignalName[] = [
  'recovery_latency_ms',
  'serve_toss_variance_cm',
  'ritual_entropy_delta',
  'crouch_depth_degradation_deg',
  'baseline_retreat_distance_m',
  'lateral_work_rate',
  'split_step_latency_ms',
];

describe('SIGNAL_COPY completeness', () => {
  it('has an entry for every SignalName', () => {
    for (const name of ALL_SIGNAL_NAMES) {
      expect(SIGNAL_COPY[name]).toBeDefined();
    }
  });

  it('has no extra entries beyond the canonical SignalNames', () => {
    const entries = Object.keys(SIGNAL_COPY);
    expect(entries.length).toBe(ALL_SIGNAL_NAMES.length);
    for (const key of entries) {
      expect(ALL_SIGNAL_NAMES).toContain(key as SignalName);
    }
  });
});

describe('SIGNAL_COPY length budgets', () => {
  for (const name of ALL_SIGNAL_NAMES) {
    it(`${name}: label ≤22 chars, unit ≤8 chars, fanDescription ≤110 chars`, () => {
      const e = SIGNAL_COPY[name];
      expect(e.label.length).toBeLessThanOrEqual(22);
      expect(e.unit.length).toBeLessThanOrEqual(8);
      expect(e.fanDescription.length).toBeLessThanOrEqual(110);
      expect(e.label.length).toBeGreaterThan(0);
      expect(e.fanDescription.length).toBeGreaterThan(0);
      expect(['fatigue', 'energy', 'drift']).toContain(e.higherIs);
    });
  }
});

describe('SIGNAL_COPY jargon discipline (DECISION-008 single-player scope)', () => {
  it('no entry references Player B by name (DECISION-008 — "opponent" generic is OK)', () => {
    for (const name of ALL_SIGNAL_NAMES) {
      const e = SIGNAL_COPY[name];
      expect(e.label).not.toMatch(/player b/i);
      expect(e.fanDescription).not.toMatch(/player b/i);
    }
  });

  it('every label uses Title Case (no underscores, no units)', () => {
    for (const name of ALL_SIGNAL_NAMES) {
      const e = SIGNAL_COPY[name];
      expect(e.label).not.toMatch(/_/);
      expect(e.label).not.toMatch(/\(cm\)|\(ms\)|\(deg\)|\(°\)|\(m\)|\(rel\)/);
    }
  });

  it('every fanDescription mentions Player A (subject discipline)', () => {
    // Player A must be the subject — never "the player" or anonymous.
    for (const name of ALL_SIGNAL_NAMES) {
      const e = SIGNAL_COPY[name];
      expect(e.fanDescription).toMatch(/Player A/);
    }
  });
});

describe('anomalyCopy', () => {
  it('emits fatigue-above-baseline for fatigue signal with positive z', () => {
    const msg = anomalyCopy('recovery_latency_ms', 2.3);
    expect(msg).toMatch(/fatigu/i);
    expect(msg).toMatch(/2\.3σ/);
  });

  it('emits drift-from-warmup for drift signal with positive z', () => {
    const msg = anomalyCopy('baseline_retreat_distance_m', 2.5);
    expect(msg).toMatch(/drift/i);
  });

  it('emits coverage-collapse for energy signal with negative z', () => {
    const msg = anomalyCopy('lateral_work_rate', -2.2);
    expect(msg).toMatch(/collaps|coverage/i);
  });

  it('emits surging for energy signal with positive z', () => {
    const msg = anomalyCopy('lateral_work_rate', 2.1);
    expect(msg).toMatch(/surg|over baseline/i);
  });

  it('keeps sentence short (≤64 chars)', () => {
    for (const name of ALL_SIGNAL_NAMES) {
      for (const z of [-2.5, -2, 2, 2.5]) {
        expect(anomalyCopy(name, z).length).toBeLessThanOrEqual(64);
      }
    }
  });
});
