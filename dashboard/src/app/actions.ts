'use server';

/**
 * Next.js Server Actions for PANOPTICON LIVE.
 *
 * `generateScoutingReport` wires Tab 3 to Claude Opus 4.7 via the official
 * `@anthropic-ai/sdk`. It follows the Client-Driven Payload pattern
 * (PATTERN-054): the client passes the telemetry it already has loaded,
 * stripped of high-volume keys (keypoints / hud_layouts / narrator_beats).
 *
 * Why Client-Driven Payload and not `fs.readFile(...)` (USER-CORRECTION-032):
 *   Vercel's Node File Trace (NFT) cannot statically analyze dynamic paths,
 *   so `fs.readFile(path.join(process.cwd(), 'public', 'match_data',
 *   `${matchId}.json`))` won't bundle the JSON into the Serverless Function.
 *   Works in `next dev`, 500s on Vercel. Passing the payload as an argument
 *   sidesteps NFT entirely and keeps the action Vercel-bulletproof.
 *
 * DECISION-009 (biometrics-first) is encoded in the system prompt: every
 * tactical claim must cite a signal name + numeric value.
 *
 * USER-CORRECTION-027: Opus 4.7 uses `thinking: { type: "adaptive" }`. The
 * older `{ type: "enabled", budget_tokens: N }` shape is rejected HTTP 400.
 */

import Anthropic from '@anthropic-ai/sdk';

import type {
  AnomalyEvent,
  CoachInsight,
  MatchMeta,
  SignalSample,
  StateTransition,
} from '@/lib/types';

export const maxDuration = 60;

const MODEL = 'claude-opus-4-7';

/**
 * Exact set of fields the Opus analyst needs. Keypoints are per-frame noise;
 * hud_layouts are LLM-generated design metadata irrelevant to sports-science
 * reasoning; narrator_beats are broadcast-tick prose that would bias the
 * scouting voice. The remaining keys give the analyst meta + the five
 * quantitative streams (signals, transitions, anomalies, coach_insights).
 */
export type ScoutingPayload = {
  meta: MatchMeta;
  signals: ReadonlyArray<SignalSample>;
  transitions: ReadonlyArray<StateTransition>;
  anomalies: ReadonlyArray<AnomalyEvent>;
  coach_insights: ReadonlyArray<CoachInsight>;
};

const SCOUTING_SYSTEM_PROMPT = `You are an elite sports biomechanics analyst for PANOPTICON LIVE — a world-class single-player deep-dive system targeting Player A in pro tennis broadcast footage.

## SINGLE-PLAYER FOCUS (DECISION-008)
Your target is Player A. Player B data will typically be missing (far-court CV resolution gap on broadcast clips); treat absent B as "opponent unknown," never fabricate. All recommendations frame what Player A's OPPONENT should do to exploit Player A.

## BIOMETRICS → TACTICS MANDATE (DECISION-009 — NON-NEGOTIABLE)
Panopticon's proprietary value is the 7 biomechanical fatigue-telemetry streams extracted from standard 2D broadcast pixels with zero hardware sensors. EVERY tactical claim you emit MUST cite a signal name + numeric value from the payload.

- BAD: "Player A is retreating."
- GOOD: "Player A's \`baseline_retreat_distance_m\` drifted from 0.10 m → 1.67 m over the last four rallies (z=+1.67) — he's conceding court position."

Frame tactics as consequences of physiology. If a broadcast analyst could see it without our CV data, it's not worth writing. Never invent numbers. If a signal's value is null or not present in the payload window, say so explicitly and pivot.

## THE 7 SIGNALS (all per-player, rounded to 4 decimals)
1. \`recovery_latency_ms\` — ms between leaving ACTIVE_RALLY and velocity dropping below 0.5 m/s. Elite fresh: 400–800 ms. Fatigued: 800–2000 ms.
2. \`serve_toss_variance_cm\` — std-dev of toss-apex height across serves within PRE_SERVE_RITUAL. Elite: 5–12 cm. Pressure drift: >15 cm.
3. \`ritual_entropy_delta\` — change in spectral entropy of wrist/hand kinematics during PRE_SERVE_RITUAL via Lomb-Scargle. Positive = messier ritual.
4. \`crouch_depth_degradation_deg\` — change in knee-bend angle during PRE_SERVE_RITUAL vs match-opening baseline. Positive = more upright = loss of coil.
5. \`baseline_retreat_distance_m\` — meters retreated behind the baseline during ACTIVE_RALLY. Sustained = defensive posture.
6. \`lateral_work_rate\` — 95th-percentile absolute lateral velocity (m/s) during ACTIVE_RALLY. High = getting run.
7. \`split_step_latency_ms\` — delay between opponent entering ACTIVE_RALLY and A's own transition. Often null (needs B detection). Elite: 200–400 ms.

## OUTPUT: heavily styled Markdown in this EXACT structure

# Player A — Scouting Brief

## 1. Biomechanical Fatigue Profile

2–3 tight paragraphs. Open with the overall fatigue arc (cognitive-motor vs cardiovascular vs ritual-drift). Cite ≥3 specific signals with numeric values and z-scores where available. Connect numbers to a physiological story.

## 2. Kinematic Breakdowns

A markdown table with columns: **Signal** | **Plain-English Label** | **Value** | **z-score** | **Read**. Include every signal present in the payload. Follow with 1–2 paragraphs interpreting outliers (which signal fires first, which lags, which are hotter than others).

## 3. Tactical Exploitations

A numbered list of 3–5 concrete, actionable tactics the OPPONENT should use against Player A. Each tactic must be grounded in a specific signal + numeric value. Include a **"Timeout trigger"** final item specifying the numeric threshold that should prompt coaching intervention (e.g., "call timeout if \`baseline_retreat_distance_m\` exceeds 2.0 m AND \`ritual_entropy_delta\` crosses +0.5").

## Methodology

One short paragraph noting CV methodology (YOLO11m-Pose + Kalman in court-meters, USER-CORRECTION-030 \`bbox_conf ≥ 0.5\`), baseline window (opening 10 s filtered), and any data limitations (Player B absent, etc.).

## RULES
- No frontmatter. No HTML. No code fences around the whole document.
- Signal names in backticks. Bold key numeric anchors. Tables use standard markdown pipes.
- Keep the total brief under ~900 words.
- Speak in present tense, broadcast-coach register — direct, confident, terse, adversarial.`;

export async function generateScoutingReport(
  matchId: string,
  payload: ScoutingPayload,
): Promise<string> {
  if (!process.env.ANTHROPIC_API_KEY) {
    throw new Error(
      'ANTHROPIC_API_KEY is not set. Create dashboard/.env.local with ANTHROPIC_API_KEY=sk-ant-... and restart the dev server.',
    );
  }

  if (!payload?.meta?.match_id) {
    throw new Error(`Invalid scouting payload for match ${matchId}: missing meta.match_id`);
  }

  const client = new Anthropic();

  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 4096,
    thinking: { type: 'adaptive' }, // USER-CORRECTION-027
    system: [
      {
        type: 'text',
        text: SCOUTING_SYSTEM_PROMPT,
        cache_control: { type: 'ephemeral' },
      },
    ],
    messages: [
      {
        role: 'user',
        content:
          `Match ID: ${matchId}\n\n` +
          `Full telemetry payload (meta + signals + transitions + anomalies + coach_insights; ` +
          `keypoints, hud_layouts, narrator_beats stripped by the client per PATTERN-054):\n\n` +
          '```json\n' +
          JSON.stringify(payload, null, 2) +
          '\n```\n\n' +
          `Generate the scouting brief per the system prompt format. Every tactical claim MUST ` +
          `cite a specific signal name and numeric value from the payload above. If a signal is ` +
          `absent or its value is null in the relevant window, state so and pivot to what IS present.`,
      },
    ],
  });

  const markdown = response.content
    .filter((block): block is Anthropic.TextBlock => block.type === 'text')
    .map((block) => block.text)
    .join('\n\n')
    .trim();

  if (!markdown) {
    throw new Error(
      'Opus returned no text blocks. Raw response had ' +
        `${response.content.length} blocks (${response.content.map((b) => b.type).join(', ')}).`,
    );
  }

  return markdown;
}
