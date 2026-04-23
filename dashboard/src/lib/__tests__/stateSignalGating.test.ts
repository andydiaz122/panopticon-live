import { describe, expect, it } from 'vitest';

import {
  filterSignalsByState,
  isSignalAllowedInState,
} from '../stateSignalGating';
import type { SignalName } from '../types';

/**
 * PATTERN-052 regression guard — frontend defense-in-depth against LLM
 * layout-lag. If the backend Designer ever selects a serve-ritual signal
 * during an ACTIVE_RALLY, this filter MUST still hide it.
 */

describe('isSignalAllowedInState — ACTIVE_RALLY', () => {
  it('rejects serve-ritual signals', () => {
    expect(isSignalAllowedInState('serve_toss_variance_cm', 'ACTIVE_RALLY')).toBe(
      false,
    );
    expect(isSignalAllowedInState('ritual_entropy_delta', 'ACTIVE_RALLY')).toBe(
      false,
    );
    expect(
      isSignalAllowedInState('crouch_depth_degradation_deg', 'ACTIVE_RALLY'),
    ).toBe(false);
  });

  it('permits rally movement signals', () => {
    expect(isSignalAllowedInState('lateral_work_rate', 'ACTIVE_RALLY')).toBe(
      true,
    );
    expect(
      isSignalAllowedInState('baseline_retreat_distance_m', 'ACTIVE_RALLY'),
    ).toBe(true);
  });

  it('permits state-agnostic signals', () => {
    expect(isSignalAllowedInState('recovery_latency_ms', 'ACTIVE_RALLY')).toBe(
      true,
    );
    expect(
      isSignalAllowedInState('split_step_latency_ms', 'ACTIVE_RALLY'),
    ).toBe(true);
  });
});

describe('isSignalAllowedInState — PRE_SERVE_RITUAL', () => {
  it('rejects rally movement signals', () => {
    expect(
      isSignalAllowedInState('lateral_work_rate', 'PRE_SERVE_RITUAL'),
    ).toBe(false);
    expect(
      isSignalAllowedInState(
        'baseline_retreat_distance_m',
        'PRE_SERVE_RITUAL',
      ),
    ).toBe(false);
  });

  it('permits serve-ritual signals', () => {
    expect(
      isSignalAllowedInState('serve_toss_variance_cm', 'PRE_SERVE_RITUAL'),
    ).toBe(true);
    expect(
      isSignalAllowedInState('ritual_entropy_delta', 'PRE_SERVE_RITUAL'),
    ).toBe(true);
    expect(
      isSignalAllowedInState(
        'crouch_depth_degradation_deg',
        'PRE_SERVE_RITUAL',
      ),
    ).toBe(true);
  });
});

describe('isSignalAllowedInState — DEAD_TIME', () => {
  it('behaves like PRE_SERVE_RITUAL — rejects rally movement', () => {
    expect(isSignalAllowedInState('lateral_work_rate', 'DEAD_TIME')).toBe(false);
    expect(
      isSignalAllowedInState('baseline_retreat_distance_m', 'DEAD_TIME'),
    ).toBe(false);
  });

  it('permits serve-ritual + state-agnostic signals', () => {
    expect(isSignalAllowedInState('serve_toss_variance_cm', 'DEAD_TIME')).toBe(
      true,
    );
    expect(isSignalAllowedInState('recovery_latency_ms', 'DEAD_TIME')).toBe(
      true,
    );
  });
});

describe('isSignalAllowedInState — permissive defaults', () => {
  it('permits everything when state is null (pre-first-transition)', () => {
    const allNames: SignalName[] = [
      'serve_toss_variance_cm',
      'lateral_work_rate',
      'ritual_entropy_delta',
      'baseline_retreat_distance_m',
      'recovery_latency_ms',
    ];
    for (const name of allNames) {
      expect(isSignalAllowedInState(name, null)).toBe(true);
    }
  });

  it('permits everything when state is UNKNOWN', () => {
    expect(isSignalAllowedInState('serve_toss_variance_cm', 'UNKNOWN')).toBe(
      true,
    );
    expect(isSignalAllowedInState('lateral_work_rate', 'UNKNOWN')).toBe(true);
  });
});

describe('filterSignalsByState', () => {
  it('preserves input order of permitted signals', () => {
    const input: SignalName[] = [
      'serve_toss_variance_cm',
      'lateral_work_rate',
      'recovery_latency_ms',
      'baseline_retreat_distance_m',
    ];
    const out = filterSignalsByState(input, 'ACTIVE_RALLY');
    expect(out).toEqual([
      'lateral_work_rate',
      'recovery_latency_ms',
      'baseline_retreat_distance_m',
    ]);
  });

  it('returns empty array when no signals fit', () => {
    const input: SignalName[] = ['serve_toss_variance_cm', 'ritual_entropy_delta'];
    expect(filterSignalsByState(input, 'ACTIVE_RALLY')).toEqual([]);
  });

  it('returns full input when state is permissive (null)', () => {
    const input: SignalName[] = [
      'serve_toss_variance_cm',
      'lateral_work_rate',
    ];
    expect(filterSignalsByState(input, null)).toEqual(input);
  });
});
