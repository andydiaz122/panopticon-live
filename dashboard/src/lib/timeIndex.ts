/**
 * Pure time-indexing helpers for PanopticonProvider.
 *
 * All functions in this module are:
 *  - Pure (no side effects, no refs, no state)
 *  - Deterministic (same inputs → same outputs)
 *  - Framework-agnostic (no React, no DOM)
 *
 * They are the algorithmic backbone of the provider — "given the video's
 * current time, which HUD layout / coach insight / signal sample is active?"
 *
 * Guards:
 *  - PATTERN-045: frame-index clamping on video-indexed lookups
 *  - Binary search is used for O(log n) on sorted-by-timestamp arrays
 *
 * All tested in `__tests__/timeIndex.test.ts` + `__tests__/frameClamp.test.ts`.
 */

/**
 * Clamp a raw frame index (from `Math.floor(currentTime * fps)`) to the valid
 * range `[0, length-1]`. Handles negative times, past-end times, NaN.
 *
 * Returns 0 when length is 0 — callers should guard against empty arrays
 * before indexing, but the clamp function itself never throws.
 */
export function clampFrameIdx(
  currentTimeSec: number,
  fps: number,
  length: number,
): number {
  if (length <= 0) return 0;
  if (!Number.isFinite(currentTimeSec) || !Number.isFinite(fps) || fps <= 0) {
    return 0;
  }
  const raw = Math.floor(currentTimeSec * fps);
  if (raw < 0) return 0;
  if (raw > length - 1) return length - 1;
  return raw;
}

/**
 * Binary search for the largest index `i` such that `items[i].timestamp_ms <= timeMs`.
 * Returns -1 if no such index exists (i.e., timeMs precedes items[0].timestamp_ms).
 *
 * Items MUST be sorted by `timestamp_ms` ascending. The provider guarantees
 * this via the backend's ordered writes.
 */
export function pickLatestBeforeOrAt<T extends { timestamp_ms: number }>(
  items: ReadonlyArray<T>,
  timeMs: number,
): T | null {
  if (items.length === 0) return null;
  if (!Number.isFinite(timeMs)) return null;
  if (timeMs < items[0].timestamp_ms) return null;
  if (timeMs >= items[items.length - 1].timestamp_ms) {
    return items[items.length - 1];
  }

  let lo = 0;
  let hi = items.length - 1;
  // Invariant: items[lo].timestamp_ms <= timeMs < items[hi].timestamp_ms
  while (hi - lo > 1) {
    const mid = (lo + hi) >>> 1;
    if (items[mid].timestamp_ms <= timeMs) {
      lo = mid;
    } else {
      hi = mid;
    }
  }
  return items[lo];
}

/**
 * Pick the HUDLayoutSpec whose `[timestamp_ms, valid_until_ms]` bracket the
 * input time. Returns null if no layout is currently active (e.g., pre-first-layout).
 *
 * Uses the same binary search as `pickLatestBeforeOrAt`, then validates the
 * bracket. A layout is active iff `timestamp_ms <= timeMs < valid_until_ms`.
 */
export function pickActiveLayoutAtTime<
  T extends { timestamp_ms: number; valid_until_ms: number },
>(layouts: ReadonlyArray<T>, timeMs: number): T | null {
  const candidate = pickLatestBeforeOrAt(layouts, timeMs);
  if (!candidate) return null;
  if (timeMs >= candidate.valid_until_ms) return null;
  return candidate;
}

/**
 * Pick the latest state transition for a given player whose `timestamp_ms`
 * is ≤ input time. Returns null if no transition has happened yet for this
 * player. The returned transition's `to_state` is the player's active state.
 */
export function pickActiveTransitionForPlayer<
  T extends { timestamp_ms: number; player: 'A' | 'B' },
>(transitions: ReadonlyArray<T>, timeMs: number, player: 'A' | 'B'): T | null {
  // Transitions are sorted by timestamp across both players, so we can't use
  // generic binary search directly. Linear scan is fine here — ~282 items
  // max, called at 10Hz = 2820 iters/sec — negligible.
  let latest: T | null = null;
  for (const t of transitions) {
    if (t.player !== player) continue;
    if (t.timestamp_ms > timeMs) break;
    latest = t;
  }
  return latest;
}

/**
 * For each signal name, find the latest sample (Player A only per DECISION-008)
 * whose `timestamp_ms` is ≤ input time. Returns a Record keyed by signal name.
 *
 * This is called at 10Hz. It allocates a new object each call (by design — the
 * returned object is the state-context value; changing identity is what
 * triggers re-renders).
 */
export function pickLatestSignalsPerName<
  T extends { timestamp_ms: number; player: 'A' | 'B'; signal_name: string },
>(signals: ReadonlyArray<T>, timeMs: number): Record<string, T> {
  const out: Record<string, T> = {};
  for (const s of signals) {
    if (s.player !== 'A') continue;
    if (s.timestamp_ms > timeMs) continue;
    const prev = out[s.signal_name];
    if (!prev || s.timestamp_ms > prev.timestamp_ms) {
      out[s.signal_name] = s;
    }
  }
  return out;
}
