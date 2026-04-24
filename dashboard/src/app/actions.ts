'use server';

/**
 * Next.js Server Actions for PANOPTICON LIVE.
 *
 * `generateScoutingReport` is STUBBED for Phase 3.5 (walking-skeleton): it
 * returns a hand-authored markdown report grounded in the Phase-2 golden
 * data (utr_01_segment_a). The Phase-4 task will replace the stub with a
 * live @anthropic-ai/sdk Managed Agent call — see the
 * `vercel-ts-server-actions` skill for the wiring pattern.
 *
 * Contract (stable across the stub→live transition):
 *   Input:  matchId (string) — identifies which clip's data to analyze
 *   Output: markdown (string) — narrated scouting report in plain markdown
 *           (no frontmatter, no HTML, no code fences)
 */

const STUB_DELAY_MS = 900;

/**
 * Deterministic sleep so the stub feels like an Opus streaming call
 * (loading spinner gets a chance to render).
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Phase 3.5 stub — returns a hand-authored scouting report.
 * Grounded in the utr_01_segment_a golden data. The numbers are real
 * (pulled from the precomputed signals). Tone matches what we want
 * the live Opus Managed Agent to emit in Phase 4.
 *
 * This report is the "Director's Cut" draft Andrew approved as the
 * target voice: biometrics-first, tactical consequences as evidence
 * of physiology, fan-legible without being watered down.
 */
export async function generateScoutingReport(matchId: string): Promise<string> {
  await sleep(STUB_DELAY_MS);

  if (matchId !== 'utr_01_segment_a') {
    return `# Scouting Report — ${matchId}\n\n_No golden data available for this match id. Returning stub fallback._`;
  }

  return `# Player A — Fatigue Intelligence Brief

_60-second segment · utr_01_segment_a · built from 7 biomechanical telemetry streams extracted from 2D broadcast pixels with zero hardware sensors._

## Executive Summary

Player A enters this segment with a clean baseline and erodes it sharply. **Baseline retreat collapses from 1.67 m → 0.10 m in four rallies (slope −0.70 m/s)**, a defensive signature that normally precedes a service break on the ATP 250 tour. Concurrently, **lateral work rate sits at 0.47 rel** through active rallies — healthy court coverage, but now paired with a ritual that is drifting.

The story is not "Player A is tired." The story is: **the legs are holding, the ritual is not**. Fatigue this segment is cognitive-motor, not cardiovascular. That changes the tactical advice.

## Biomechanical Profile

| Signal | Value | z-score | Read |
|---|---|---|---|
| Baseline Retreat | 1.67 m | +1.67σ | Drifting deeply behind warmup position |
| Lateral Work | 0.47 rel | +0.34σ | Coverage intact — legs not gone |
| Recovery Lag | 1.21 s | +0.88σ | Early tell of elevated recovery cost |
| Ritual Discipline | +0.09 rel | +0.42σ | Pre-serve rhythm deviating from baseline |
| Toss Consistency | 11.4 cm | +0.51σ | Within elite range; on the edge of pressure drift |

(_z-scores are against Player A&apos;s own warmup baseline, not a global pro cohort._)

## Fatigue Arc

The arc we see across 60 seconds is a preview of what will matter at set 2 / tiebreak:

1. **Early baseline (0–12s)** — CV warmup window. All signals calibrating.
2. **First rallies (12–32s)** — baseline_retreat_distance_m begins drifting. Lateral work still aggressive — A is taking the court but giving back depth.
3. **Late segment (32–60s)** — toss_consistency starts trending up at 1σ. If it breaks 2σ in a live match, expect a double fault.

The ritual signals are the leading indicator here. Physical signals will lag by a game or two.

## Tactical Recommendations

1. **Attack the return of serve.** Every cm of retreat converts to a longer hit-zone on the next return. A&apos;s opponent should hit behind him on every second serve.
2. **Watch for a first-service drop.** toss_consistency is the earliest fatigue tell on this clip. A short warmup or water break is the intervention.
3. **Do NOT attack the baseline directly.** Lateral_work_rate is healthy; A still covers well laterally. Prefer going deep to going wide.
4. **Timeout trigger**: if baseline_retreat exceeds 2.0 m AND ritual_entropy_delta crosses +0.5, call for a coaching challenge / towel break.

## Confidence & Methodology

- Signals derived from YOLO11m-Pose keypoints + Kalman (court-meters frame) + rolling state machine. Raw CV confidence ≥ 0.5 enforced (USER-CORRECTION-030 skeleton-sanitation gate).
- Baseline computed from Player A&apos;s own warmup window (first 10,000 ms of clip, filtered per GOTCHA-017 calibration protocol).
- Opponent (Player B) telemetry is not present on this clip — the far-court detector resolution is below our threshold (GOTCHA-016). Single-player scope per DECISION-008.

_Report stub generated locally — Phase 4 will replace with a live Claude Opus 4.7 Managed Agent call that reasons over this same data with tools + extended thinking._`;
}
