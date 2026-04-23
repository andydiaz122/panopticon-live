---
name: biometric-fan-experience
description: Fan-facing copy + UX discipline for PANOPTICON LIVE biometric signals. Owns the plain-English label, one-line physiology caption, calibration/no-data states, and anomaly explanations that make proprietary CV telemetry legible to a casual tennis fan. Use when authoring any widget that renders a biomechanical signal to a non-expert audience — specifically `SignalBar`, `SensorCalibratingPlaceholder`, and any future "Scouting Report" or marketing copy.
---

# Biometric Fan Experience

The translation layer between our proprietary biomechanical CV and the casual tennis fan watching the demo. If a judge squints at a widget and thinks "what does `ritual_entropy_delta` mean?" we have already lost the 25% Demo criterion. This skill owns the copy that stops that from happening.

## Why this skill exists

The 7 signals are our proprietary data moat (DECISION-009) — every insight Panopticon surfaces flows through them. But they only matter if the fan can READ them. Dev-facing names like `baseline_retreat_distance_m` and `ritual_entropy_delta` are engineering artifacts; they are not broadcast copy. A HUD that leaks snake_case to the viewer is indistinguishable from a debug overlay. This skill owns the translation from the signal-extractor contract (engineer-facing) to the SignalBar widget (fan-facing): one canonical label, one unit, one plain-English caption, one directional semantic per signal. Every other skill defers to this one on fan-facing text.

## The fan-copy contract

Every signal rendered to a fan ships exactly four pieces of copy. No more, no less:

- **`label`** (≤22 chars) — the display title. Title Case. No units. This is what the viewer reads at a glance.
- **`unit`** (≤8 chars) — what the number means (`m`, `cm`, `°`, `ms`, `rel`). Lives in its own field so typography can style it separately (smaller, muted).
- **`fanDescription`** (1 sentence, ≤110 chars) — plain-English explanation. No jargon. Tells the fan what higher/lower values mean for the athlete's state.
- **`higherIs`** — directional semantic: `'fatigue' | 'energy' | 'drift'`. Lets the widget flip tone (green vs amber) and select anomaly templates without the copy needing to encode it inline.

These four fields are the skill's charter. If a widget needs a fifth field to render well, the widget is probably doing too much — push the missing behavior into `2k-sports-hud-aesthetic` (visual) or `biomechanical-signal-semantics` (thresholds).

## The canonical SIGNAL_COPY table

This table is the **source of truth** for every fan-facing string tied to a signal. `dashboard/src/lib/signalCopy.ts` MUST mirror this exact copy, character-for-character. If you find yourself tempted to "improve" the copy in widget code, edit this table first, then propagate.

| signal_name | label | unit | higherIs | fanDescription |
|---|---|---|---|---|
| `baseline_retreat_distance_m` | Baseline Retreat | m | drift | How far Player A has drifted behind his warmup baseline. Bigger = giving ground to the opponent's heat. |
| `recovery_latency_ms` | Recovery Lag | ms | fatigue | Time Player A takes to return to a ready stance after each shot. Bigger = getting tired. |
| `serve_toss_variance_cm` | Toss Consistency | cm | drift | Vertical jitter of Player A's ball toss at apex. Bigger = ritual breaking down under pressure. |
| `ritual_entropy_delta` | Ritual Discipline | rel | drift | How much Player A's pre-serve routine deviates from his warmup baseline. Bigger = pattern degrading. |
| `crouch_depth_degradation_deg` | Crouch Depth | ° | fatigue | Loss of bend in Player A's split-step crouch. Bigger = legs fading. |
| `lateral_work_rate` | Lateral Work | rel | energy | How much side-to-side ground Player A is covering per second. Bigger = aggressive court coverage. |
| `split_step_latency_ms` | Split-Step Timing | ms | fatigue | Delay between opponent's racket contact and Player A's split-step. Bigger = reading slower. (Note: often unavailable — Player B is not always detected. DECISION-008.) |

## Jargon discipline checklist

Before shipping any fan-facing copy — whether to the HUD, a scouting report, or a marketing asset — walk this list:

- [ ] No underscores (`_`) visible to the fan — those are dev names, not display strings.
- [ ] No units embedded in the label (units live in a separate field so typography can style them).
- [ ] Length constraints hit (label ≤22 chars, fanDescription ≤110 chars).
- [ ] Subject is "Player A" (never "the player," never "A," never anonymous "player").
- [ ] Verb suggests state change ("drifting," "fading," "breaking down," "collapsing"), not measurement ("distance of," "value of," "coefficient of").
- [ ] Reader doesn't need a biomechanics degree to parse it. If your mom wouldn't get it at a glance, rewrite.

## Calibration state copy

Signals don't exist before the warmup window closes (GOTCHA-017). That is NOT a bug — it is a broadcast-UX moment. Turn the wait into narrative.

When data hasn't arrived yet (pre-warmup window, signal extractors haven't populated their baselines):

- **Header**: `BIOMETRIC SENSORS`
- **Status**: `CALIBRATING…`
- **Sub-text**: `Establishing player baselines from warmup`
- **Rationale**: a technical constraint reframed as a premium feature. The HUD looks like it's warming up alongside the athlete.

When `activeSignalsByName[name]` is null AFTER calibration (signal didn't fire yet at `currentTimeMs` but the window HAS elapsed):

- Render the bar with a muted track (no fill). The value row shows `—` (em dash, U+2014).
- The fan caption still renders — it pre-explains what's coming, so the viewer is primed when the signal lights up.
- Do NOT render an error state. Do NOT swap in placeholder copy like "No data" or "Waiting." Silence is fine; explanation is better.

## Anomaly copy

Anomalies are the 2K-sports "clutch moment" — the widget goes from ambient telemetry to narrative event. When `|z_score| ≥ 2` on a signal:

- The bar pulses (motion handled by `2k-sports-hud-aesthetic`).
- The value chip switches to `colors.anomaly` red.
- An optional overlay line appears on the widget: `"ANOMALY — "` plus a templated sentence derived from `higherIs`:

  - `higherIs: 'fatigue'` and `z > 0` → `"Player A fatiguing 2σ above baseline"`
  - `higherIs: 'drift'` and `z > 0` → `"Player A drifting 2σ from warmup"`
  - `higherIs: 'energy'` and `z < 0` → `"Player A coverage collapsing 2σ"`
  - `higherIs: 'fatigue'` and `z < 0` → `"Player A recovering 2σ below baseline"`
  - `higherIs: 'drift'` and `z < 0` → `"Player A tightening 2σ toward baseline"`
  - `higherIs: 'energy'` and `z > 0` → `"Player A coverage spiking 2σ"`

Keep every sentence ≤64 chars. One line of broadcast-grade urgency, not a paragraph. The sentence is a headline, not a write-up — leave the write-up to the Opus Coach.

## Progressive disclosure (roadmap, NOT in Core Trio)

The fan caption is the first disclosure layer. Do not build what follows during the hackathon — it is explicit future work flagged here so nobody is tempted to inline it.

Future extension: hover / tap on a SignalBar opens a popover with:

- The formal signal name (`baseline_retreat_distance_m`).
- A 30-word physics explanation linking to `biomechanical-signal-semantics`.
- A link to the academic citation (if any).

This is a post-hackathon feature. If a reviewer asks "where's the deep-dive view?" the answer is "the scouting-report PDF from the Managed Agent" — not the HUD.

## Cross-skill delegation map

Route to the skill that owns the answer:

- "What threshold counts as an anomaly? What does 2σ mean for this specific signal?" → `biomechanical-signal-semantics` (physics, math, thresholds).
- "What color / font / spring curve should the bar use?" → `2k-sports-hud-aesthetic` (tokens, motion).
- "How should the widget re-render at 10Hz without blowing React?" → `react-30fps-canvas-architecture` (rAF + refs).
- "Is this signal / rule in scope for Panopticon at all?" → `panopticon-hackathon-rules` (scope, hard constraints).
- "What does the raw extractor output look like?" → `signal-extractor-contract` (Pydantic schema).

If the question is "what STRING does the fan see?" — the answer lives here. Otherwise, hand off.

## Anti-patterns

- **Leaking dev names.** Rendering `baseline_retreat_distance_m` directly in a widget. Always translate through the `SIGNAL_COPY` table.
- **Copy that references the math.** Writing fan-facing text like "z-score above 2 standard deviations" or "standard error of the toss coefficient." The number is the number; the copy is human. Math lives in `biomechanical-signal-semantics`.
- **Ad-hoc strings in widget code.** Inventing a new label like "Retreat Dist." inline in a JSX file. Always add/edit the canonical table, then import.
- **Using the word "biomechanical" fan-facing.** Internally we say biomechanical; publicly we say **biometric**. Matches broadcast-sports colloquial usage and polls better with non-experts. Engineers read "biomechanical"; fans read "biometric."
- **Five-field creep.** If a widget wants a fifth copy field (like `subtitle`, `icon`, `tooltip`), check whether it's actually a visual concern (`2k-sports-hud-aesthetic`) or a threshold concern (`biomechanical-signal-semantics`) before expanding the contract.
- **Translating too late.** Doing `snake_case → Title Case` at render time with string helpers. Widgets should import finished copy, not compute it.
