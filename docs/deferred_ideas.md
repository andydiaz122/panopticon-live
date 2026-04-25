# Deferred Ideas — PANOPTICON LIVE

**Purpose:** Save-not-trash. Every idea here was generated during the
hackathon journey, considered, and DEFERRED for one of three reasons:
(a) wrong-attack-vector for the hackathon's 6-day deadline,
(b) blocked by an architectural guardrail (React types, single-player scope),
(c) explicitly vetoed by the team lead but worth revisiting later.

**Maintained:** 2026-04-25 onward. Append new entries; do not delete.
Each entry tagged with deferral date + rationale + revisit-trigger.

**Revisit triggers** (when to come back):
- ⏰ POST-SUBMISSION = after Sunday 2026-04-26 8 PM EST submission
- 🚀 V2-PRODUCT = if PANOPTICON LIVE becomes a productized platform
- 🔬 RESEARCH = exploratory time after hackathon resolves
- 📊 NEEDS-DATA = requires more match clips / multi-set baseline data first

---

## Section 1 — Dashboard / React Widget Ideas

### IDEA-001 — BounceCounter HUD widget
**Deferred:** 2026-04-25 (ground-truth sync planning, Decision #2)
**Reason:** Team-lead VETO on dashboard React code changes during demo prep window. Instead used coach-panel narration at t=13.5s + CapCut text overlay (Option C of three).
**What it would be:** A new HUD widget that displays "PRE-SERVE RITUAL: 1 / 2 / 3 / CATCH" stepping forward each second during 13-17s of every pre-serve routine. Live counter that resets between points.
**Implementation sketch:**
- New WidgetKind `BounceCounter` in `dashboard/src/lib/types.ts`
- New React component reading from `keypoints` ref + a derived "ball-bounce-event" signal
- Bounce-event detection from wrist-velocity inversion patterns (left wrist holding ball, right wrist racket-striking)
- Add to `hud_layouts` via the sync script when phase = PRE_SERVE_RITUAL
**Revisit:** ⏰ POST-SUBMISSION + 🚀 V2-PRODUCT
**Why it's interesting:** Bounce-count IS a real ritual entropy signal. Currently exposed only via coach narration; a live widget would showcase the biometric-extraction story more concretely.

### IDEA-002 — Pose-overlay knee-angle annotation
**Deferred:** 2026-04-25 (ground-truth sync planning, Decision #3)
**Reason:** Team-lead VETO on React code changes; would also require pose-keypoint geometry math live. Instead used coach narration at t=18.5s + CapCut static-text callout (no zoom, per team-lead anti-zoom directive).
**What it would be:** A small angular overlay drawn on the keypoints skeleton rendering during 17-20s of every serve, showing the back-leg knee flexion angle in degrees (e.g., "138°"). Animates as the player loads.
**Implementation sketch:**
- Compute knee angle from `right_hip → right_knee → right_ankle` keypoint vectors
- Draw on existing canvas overlay during SERVE phase only
- Toggle via `display_player_profile.show_knee_angle_during_serve` flag
- Animate the numeric counter as angle changes frame-to-frame
**Revisit:** ⏰ POST-SUBMISSION + 🚀 V2-PRODUCT
**Why it's interesting:** Knee flexion is the most repeatable serve biometric. A live visual would prove we're extracting it (not just claiming it in coach text).

### IDEA-003 — Two-player MomentumMeter widget
**Deferred:** 2026-04-22 (DECISION-008 single-player scope)
**Reason:** Far-court Player B too small for reliable YOLO11m-Pose detection on broadcast tennis clips (GOTCHA-016). Built widget catalog includes MomentumMeter + PredictiveOverlay but they require Player B keypoint data we can't get reliably.
**What it would be:** Live momentum-shift visualization comparing Player A's recent shot quality vs Player B's. Color-bar that slides toward whoever is gaining tactical advantage.
**Revisit:** 🚀 V2-PRODUCT — would require either (a) Player B detection enhancement (different model, multi-frame averaging, manual annotation) or (b) different camera angle (closer-court framing).

### IDEA-004 — PredictiveOverlay widget (next-shot prediction)
**Deferred:** 2026-04-22 (DECISION-008 single-player scope) + 2026-04-25 (Andrew's anti-predictive directive)
**Reason:** Two reasons stacked: (a) requires Player B data we don't have reliably; (b) Andrew's Notion notes explicitly said: "I don't want to make this about the predictive modeling... spending time on ML fine-tuning is an attack vector." We pitch the platform as a Signal Extraction Engine; predictions are downstream consumer territory.
**What it would be:** Heat-map overlay on the court showing where the next shot is likely to land, based on rally pattern + player-positioning telemetry.
**Revisit:** 🚀 V2-PRODUCT — only if/when PANOPTICON becomes a betting / strategy-coaching tool that needs predictions.

### IDEA-005 — FootworkHeatmap widget
**Deferred:** 2026-04-22 (limited demo time)
**Reason:** Widget exists in WidgetKind enum but not used in any current hud_layouts. Would visualize cumulative court-position density.
**What it would be:** A semi-transparent court overlay showing where Player A spent most of the rally (heat density). Updates between points.
**Revisit:** ⏰ POST-SUBMISSION — quick to add as a Tab-2 visualization for the data-product showcase. Already have the keypoints.

### IDEA-006 — Live "extended thinking" stream
**Deferred:** 2026-04-22 (Phase-5 audit found we don't actually stream)
**Reason:** Per `demo-presentation/CLAUDE.md` §3.1: "Visible extended thinking → CoachPanel `Show thinking ▾` expands static precomputed text." We don't actually stream thinking tokens; the demo narration uses "Opus's reasoning preserved and expandable on demand" framing instead.
**What it would be:** During Tab 3 swarm replay, stream Opus's actual `thinking` content as it generates, char-by-char, in a side panel.
**Implementation sketch:** Use `streaming=True` + `thinking_blocks` from Anthropic SDK; pipe to a React state with throttled updates (per 30FPS canvas architecture rules).
**Revisit:** 🚀 V2-PRODUCT — requires re-architecting the agent_trace from pre-computed playback to actual live streaming. Not viable for the current demo's offline-precompute architecture.

---

## Section 2 — Video / Presentation Ideas

### IDEA-007 — Digital zoom in CapCut for leg-bend showcase
**Deferred:** 2026-04-25 (team-lead VETO on the zoom)
**Reason:** "If you apply a digital zoom in post-production to a screen recording of your dashboard, you will also zoom in on your HUD/UI elements. The text and tickertape will become massive and pixelated, instantly breaking the illusion." (Team-lead verbatim.)
**What it would be:** 15% slow zoom into Player A's lower body during 18-20s of the clip, with a "PEAK KNEE FLEXION" callout text overlay.
**Why it's vetoed (and the lesson):** Digital zoom on a UI screen recording is fundamentally different from zooming a cinematic plate. The HUD text loses crispness instantly.
**Better alternatives (current):** Static CapCut text callout at fixed scale; camera-angle-controlled actual zoom would require re-recording at higher native resolution then downsampling.
**Revisit:** Never — vetoed for principled reasons that won't change. Listed here as a CASE STUDY in why screen-recording post-production rules differ from cinematic post.

### IDEA-008 — SceneBreak T2 Remotion rebuilds
**Deferred:** 2026-04-25 (Anthropic-Minimalism pivot retired the entire Remotion path)
**Reason:** Team-lead pivot away from Remotion-heavy presentation. The 3 V2 compositions shipped (B0OpenerV2, B5ClosingV2, B5ThesisV2) became fallback insurance. SceneBreak T2 was queued for Saturday late-AM but the pivot made it unnecessary.
**What it would be:** Interstitial chapter cards for B2/B3/B4 transitions (ch.02 THE SENSOR, ch.03 THE RECURRENCE, ch.04 THE BRAIN). Each 6-8s with mini chapter markers, shared visual vocabulary with B0/B5 V2 family.
**Revisit:** ⏰ POST-SUBMISSION — if/when we make a longer-form product video later, the SceneBreak T2 design is a good interstitial pattern.

### IDEA-009 — OBS motion-graphics overlay templates
**Deferred:** 2026-04-25 (Anthropic-Minimalism pivot)
**Reason:** Same as IDEA-008 — Remotion-based motion graphics layer was retired in favor of CapCut static text callouts. Tier 3 stretch goal that pivot eliminated.
**What it would be:** Reusable Remotion compositions for OBS overlay use: callout arrow, zoom-insert frame, kinetic-typography text card. Designed to layer over OBS dashboard captures in DaVinci/CapCut.
**Revisit:** ⏰ POST-SUBMISSION — useful for any future tutorial/demo video at higher production tier.

### IDEA-010 — Per-character stagger as a reusable Remotion primitive
**Deferred:** 2026-04-25 (Remotion pivot)
**Reason:** Pattern C from `remotion-cinematic-craft` skill, shipped INLINE in B5ClosingV2. Could be extracted to a primitive if a 3rd composition needs it.
**What it would be:** `<PerCharacterStagger text="..." startFrame={...} /> ` primitive that wraps any text and reveals it character-by-character with configurable stagger interval.
**Revisit:** ⏰ POST-SUBMISSION — only if Remotion path resumes for longer-form video work.

### IDEA-011 — Kerning sweep as a reusable Remotion primitive
**Deferred:** 2026-04-25 (Remotion pivot)
**Reason:** Pattern A from skill, shipped INLINE in 3 compositions. Rule of three says EXTRACT — but Remotion path retired before extraction happened.
**What it would be:** `<KerningSweep>` primitive that wraps any text element and animates `letterSpacing` from 0.5em → -0.02em over a configurable window.
**Revisit:** ⏰ POST-SUBMISSION.

---

## Section 3 — CV Pipeline / Data Ideas

### IDEA-012 — Re-run CV pipeline to fix live-FSM calibration drift
**Deferred:** 2026-04-25 (team-lead "no risky elements" directive during sync)
**Reason:** The live FSM (CV-pipeline-extracted `transitions` field) puts ACTIVE_RALLY at 11s when ground-truth says it doesn't start until 20s. The PRE_SERVE_RITUAL nameplate at t=0 is the visible drift symptom. Fixing requires re-running the full CV pipeline with adjusted thresholds, validating outputs, and re-deploying — hours of work + risk of breaking other things.
**What it would be:** Re-run YOLO11m-Pose + Kalman + state machine with the calibration tuned per ground-truth (state transitions at correct timestamps). Then the dashboard's nameplate would also reflect ground-truth phases, removing the dual-layer architectural awkwardness.
**Revisit:** 🚀 V2-PRODUCT — when we have time to re-run pipelines without deadline pressure, this is the principled fix.
**Workaround (current):** Display layer (display_transitions) carries the corrected narrative. Live layer is left untouched. Most viewers see the broadcast overlay + coach panel + voiceover, which carry the right story.

### IDEA-013 — Predictive modeling work (Catboost / weather sniper / etc.)
**Deferred:** 2026-04-25 (Andrew's "wrong attack vector" directive)
**Reason:** Andrew's Notion notes verbatim: "I don't want to make this about the predictive modeling... spending time on ML fine-tuning is an attack vector." Hackathons are won on demonstration of a novel pipeline, not predictive accuracy.
**What it would be:** Use the extracted biometric signals as features in a CatBoost / XGBoost model predicting next-point outcome, win probability, etc.
**Revisit:** Never for hackathon. 🚀 V2-PRODUCT if/when PANOPTICON becomes a betting/quant platform — but per Andrew's directive the PLATFORM (Signal Extraction Engine) is the moat, not the predictions. Predictive products would be a downstream offering.

### IDEA-014 — Multi-clip baseline establishment for z-scoring
**Deferred:** 2026-04-22 (only 1 clip in scope)
**Reason:** All 7 biomechanical fatigue signals require ~10 between-point intervals to establish a meaningful z-score baseline. Current demo has 1 clip with 1 between-point interval. Coach insights honestly say "no baseline yet."
**What it would be:** Process 5-10 additional UTR Pro A clips, extract signals, build per-player baseline distributions. Then z-score live signals against the baseline.
**Revisit:** 🚀 V2-PRODUCT + 📊 NEEDS-DATA — clear next step for productization. Honest framing in the current demo ("first match window — no z-scores yet") sets up this story naturally.

### IDEA-015 — Informal-bouncing as a separate ritual signal
**Deferred:** 2026-04-25 (biomech reviewer LOW finding from sync)
**Reason:** Andrew's ground-truth distinguishes 11-12s "informal bouncing while walking" from 13-17s "formal pre-serve ritual." Current sync conflates them in DEAD_TIME state. Could be a NEW signal candidate.
**What it would be:** Signal `informal_bouncing_duration_ms` measuring time between first-bounce and arrival-at-baseline. Variations correlate with player rhythm.
**Revisit:** ⏰ POST-SUBMISSION + 📊 NEEDS-DATA — interesting if it generalizes across players.

---

## Section 4 — Branding / Naming / Domain Ideas

### IDEA-016 — Ten alternative project names
**Deferred:** 2026-04-25 (Andrew wanted the option to rename later)
**Reason:** Andrew quoted: "I'm not thrilled about the name 'panopticon'... I would like a list of 10 other creative project name alternatives... I just want to reserve the ability to change the name of our project later."
**What we shipped with:** PANOPTICON LIVE
**Alternative names generated** (reproduce the list when revisiting):
- (List was generated earlier in the conversation history; recreate from /sessions if needed)
**Revisit:** ⏰ POST-SUBMISSION — if/when we rename, the GitHub repo + Vercel project + domain all get updated.

### IDEA-017 — live.andrewdiaz.io custom domain CNAME
**Deferred:** 2026-04-25 (later, not now per Andrew's "decisions")
**Reason:** Andrew said about CNAME setup: "later, not now." Current production URL is `panopticon-live.vercel.app` — clean and shippable as-is.
**What it would be:** Set up a CNAME on `andrewdiaz.io` pointing `live.subdomain` to `panopticon-live.vercel.app`, then add the custom domain to the Vercel project.
**Revisit:** ⏰ POST-SUBMISSION — useful for portfolio/showcase. Not worth the GoDaddy DNS configuration risk before submission.

---

## Section 5 — Architecture / Tooling Ideas

### IDEA-018 — Recurring `validate_match_data_schema.py`
**Deferred:** 2026-04-25 (data-integrity-guard LOW finding from sync)
**Reason:** Each ground-truth sync re-validates the JSON via the sync script. A recurring per-commit `validate_match_data_schema.py` would CI-enforce schema compliance even when sync isn't being run.
**What it would be:** Pre-commit hook script that validates every match_data/*.json against the TypeScript types in `dashboard/src/lib/types.ts` (or equivalent Pydantic model).
**Revisit:** ⏰ POST-SUBMISSION + 🚀 V2-PRODUCT — useful when we have multiple match clips in production.

### IDEA-019 — Live extended-thinking streaming via SSE
**Deferred:** 2026-04-22 (Phase 4 SSE-vs-static-JSON architecture decision)
**Reason:** Per USER-CORRECTION-001/006, current architecture uses static `dashboard/public/match_data/<id>.json` not SSE. SSE would enable live streaming of agent thinking + signals as the model runs.
**What it would be:** Switch to SSE backend that streams keypoints + signals + agent thinking live as the model processes. Frontend uses EventSource to receive.
**Revisit:** 🚀 V2-PRODUCT — requires new backend infrastructure (Vercel SSE limits, alternative hosting). Worth it for the live-feel but architectural overhaul.

---

## Section 6 — Demo Production Ideas (Beyond the Current 3-min Plan)

### IDEA-020 — Long-form product video (10-15 min)
**Deferred:** 2026-04-25 (3-minute deadline scope)
**Reason:** Hackathon submission is 3 minutes max. Longer-form would dive deeper into mechanics + multi-agent orchestration + data product story.
**What it would be:** A 10-15 minute walkthrough video covering: (1) the data extraction pipeline; (2) all 7 signals with biomech context; (3) multi-agent swarm with full reasoning chain; (4) data product (CSV download); (5) future vision.
**Revisit:** ⏰ POST-SUBMISSION — useful for portfolio + investor outreach. Use the SceneBreak T2 + OBS overlay templates (IDEA-008, IDEA-009).

### IDEA-021 — Voice clones for each agent in the swarm
**Deferred:** 2026-04-25 (Anthropic-Minimalism pivot — single disembodied VO)
**Reason:** Pivot landed on ONE clinical VO. Distinct voices per agent would risk theatrical drift.
**What it would be:** For Tab 3 swarm replay, each agent (Analytics, Biomechanics, Strategy) gets a distinct voice via ElevenLabs. Conversational handoffs feel like multiple people thinking aloud.
**Revisit:** 🚀 V2-PRODUCT — interesting for a longer-form video where the swarm is a hero, not a feature.

---

## Maintenance Notes

- Append new entries with the same template (IDEA-NNN, deferred date, reason, what-it-is, revisit-trigger).
- When an idea is RESURRECTED and shipped, MOVE it to a new `docs/shipped_resurrected_ideas.md` with the resurrection-date and the PR/commit that landed it.
- When an idea is FORMALLY KILLED (e.g., we decide it's never coming back), MOVE it to `docs/killed_ideas.md` with the kill-date and the reasoning. Do NOT delete from history.
