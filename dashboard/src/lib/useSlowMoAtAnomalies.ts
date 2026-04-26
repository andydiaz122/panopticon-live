'use client';

import { useEffect, type RefObject } from 'react';

/**
 * A2a — Sportradar-aesthetic slow-mo at anomaly timestamps (PLAN.md §6).
 *
 * When the video's `currentTime` enters the slow-mo window around an anomaly,
 * animate `playbackRate` down to `SLOW_RATE`; restore to 1.0 when the window
 * exits. Pure HTMLMediaElement API — no canvas math, no rAF coordination with
 * the skeleton engine. The Detective Cut's B3 "slow the drama" beat.
 *
 * Transition cadence (from PLAN.md + iteration-1 aesthetic review):
 *   - Ramp IN over `RAMP_MS` so the slowdown looks like a broadcast replay
 *     rather than a hard jolt.
 *   - Hold `SLOW_RATE` for `HOLD_MS`.
 *   - Ramp OUT over `RAMP_MS` so playback resumes naturally.
 *
 * Hook is inert when `timestamps` is empty (no anomalies authored yet — safe
 * fallback). Also inert during scrubs: if the user seeks past the window, the
 * hook snaps `playbackRate` back to 1.0 rather than leaving it at 0.25.
 *
 * Implementation: single requestAnimationFrame loop observing
 * `video.currentTime`. Does NOT rely on the `timeupdate` event (fires at ~4 Hz
 * inconsistently across browsers; insufficient for a 500 ms ramp).
 */

export interface SlowMoConfig {
  /** Target rate during slow-mo window. 0.25 = quarter speed (PLAN.md A2a spec). */
  slowRate?: number;
  /** ms to ramp from 1.0 → slowRate (and slowRate → 1.0). 500 ms by default. */
  rampMs?: number;
  /** ms to hold at slowRate before ramping back up. 3000 ms by default. */
  holdMs?: number;
}

// 2026-04-25 ~17:35 EDT — softened from (0.25, 500, 3000) = 4s @ 0.25x to
// (0.5, 300, 900) = 1.5s @ 0.5x. Andrew observed compounding lag during
// recording when slow-mo windows overlapped with CoachPanel auto-pauses
// (insight #5 at t=36000ms fell inside the 35.9s anomaly window: 8.2s pause
// + 13.6s slow-mo crawl = 22s of non-normal playback per event). The new
// values still read as "broadcast replay" but compound less destructively
// with the typewriter-pause pattern. Editorial intent preserved.
const DEFAULT_CONFIG: Required<SlowMoConfig> = {
  slowRate: 0.5,
  rampMs: 300,
  holdMs: 900,
};

/**
 * Linear interpolation for rate ramp. Could use easing curves but linear reads
 * as "broadcast slow-mo" more than ease-in-out, which feels cinematic-but-fake.
 */
function lerp(from: number, to: number, t: number): number {
  return from + (to - from) * Math.max(0, Math.min(1, t));
}

/**
 * Given a list of anomaly timestamps (ms) and the current `currentTimeMs`,
 * compute the desired playbackRate. Pure function — easy to unit-test.
 */
export function computePlaybackRate(
  currentTimeMs: number,
  anomalies: ReadonlyArray<number>,
  config: Required<SlowMoConfig>,
): number {
  const { slowRate, rampMs, holdMs } = config;
  for (const anomalyMs of anomalies) {
    const windowStart = anomalyMs - rampMs;
    const windowEnd = anomalyMs + rampMs + holdMs;
    if (currentTimeMs < windowStart || currentTimeMs > windowEnd) continue;
    // Ramp-in phase
    if (currentTimeMs <= anomalyMs) {
      const t = (currentTimeMs - windowStart) / rampMs;
      return lerp(1.0, slowRate, t);
    }
    // Hold phase
    const holdEnd = anomalyMs + holdMs;
    if (currentTimeMs <= holdEnd) {
      return slowRate;
    }
    // Ramp-out phase
    const t = (currentTimeMs - holdEnd) / rampMs;
    return lerp(slowRate, 1.0, t);
  }
  return 1.0;
}

/**
 * Attach slow-mo behavior to a video ref.
 *
 * @param videoRef stable ref from PanopticonProvider
 * @param anomalyTimestampsMs array of anomaly timestamps in milliseconds.
 *   Defaults to the hero clip's three choreographed anomaly moments
 *   (t=35.9s, 45.3s, 59.1s per PHASE_6_TEAM_LEAD_HANDOFF §2).
 * @param config optional slow-mo config override
 */
// PR #7 Finding 2 fix: hoist default arguments to module scope so their
// identity is stable across renders. Inline defaults `= [35_900, ...]` and
// `= {}` allocate fresh array/object every render, causing the useEffect
// dep array to see new identities and tear down + rebuild the rAF loop on
// every render of the host component. Currently latent because HudView only
// reads from the static context, but a future state-subscribed consumer
// would silently kill demo-day FPS (CLAUDE.md React 30-FPS death-spiral
// rule 1). Module-scope identity is the canonical fix and aligns with the
// same pattern in HudView.tsx for SIDE_RAIL_ROW_KINDS.
const DEFAULT_ANOMALY_TIMESTAMPS_MS: ReadonlyArray<number> = [35_900, 45_300, 59_100];
const DEFAULT_CONFIG_PARAM: SlowMoConfig = {};

export function useSlowMoAtAnomalies(
  videoRef: RefObject<HTMLVideoElement | null>,
  anomalyTimestampsMs: ReadonlyArray<number> = DEFAULT_ANOMALY_TIMESTAMPS_MS,
  config: SlowMoConfig = DEFAULT_CONFIG_PARAM,
): void {
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (anomalyTimestampsMs.length === 0) return;

    const mergedConfig = { ...DEFAULT_CONFIG, ...config };
    let rafId = 0;

    const tick = () => {
      rafId = requestAnimationFrame(tick);
      // 2026-04-25 ~17:35 EDT — early-out when paused. The CoachPanel
      // auto-pauses the video for the typewriter telestrator beat. While
      // paused, currentTime doesn't advance, so the slow-mo decision is
      // stable — no need to recompute every frame. Cheap defensive guard.
      if (video.paused) return;
      const currentTimeMs = video.currentTime * 1000;
      const desired = computePlaybackRate(
        currentTimeMs,
        anomalyTimestampsMs,
        mergedConfig,
      );
      // Only write when the rate actually changes — avoids thrashing
      // the media engine every frame. Float equality is fine because
      // `computePlaybackRate` returns stable values (`slowRate`, `1.0`,
      // or lerp results that differ frame-to-frame during the ramp).
      if (Math.abs(video.playbackRate - desired) > 0.001) {
        video.playbackRate = desired;
      }
    };
    rafId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(rafId);
      // Restore to 1.0 on unmount so the video doesn't get stranded at 0.25
      // if the hook is removed mid-slow-mo.
      if (video.playbackRate !== 1.0) {
        video.playbackRate = 1.0;
      }
    };
  }, [videoRef, anomalyTimestampsMs, config]);
}
