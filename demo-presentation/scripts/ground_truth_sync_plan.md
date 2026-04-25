# Ground-Truth Sync Plan — PANOPTICON LIVE Demo

**Authored:** 2026-04-25 ~06:30 EDT.

**Trigger:** Andrew delivered a second-by-second ground-truth log of `utr_match_01_segment_a.mp4` at ~06:15 EDT. Discovery against the canonical `dashboard/public/match_data/utr_01_segment_a.json` revealed **MAJOR drift** between authored display data and what the clip actually shows. This plan synchronizes the dashboard's authored layer to ground-truth, with the rigor Andrew specified ("the highest level out of anything we've executed so far").

**Status:** PLAN — awaiting Andrew's approval + 3 decisions before execution.

**Owner of this plan:** Andrew (decisions) + Claude (execution).

---

## 1. The Source-of-Truth (verbatim from Andrew's 06:15 EDT message)

A canonical timestamp table consolidating Andrew's prose log into machine-readable form. **THIS is the contract** — every authored field in `utr_01_segment_a.json` must align to this table.

| Time (s) | Player A state | Player A action | Notes |
|---|---|---|---|
| 0–9 | DEAD_TIME | Off court (previous point just finished) | |
| 10 | WALKING_TO_BASELINE | Appears on court, walking to baseline | |
| 11–12 | PRE_SERVE_INFORMAL | Approaching baseline, informal bouncing of ball against floor with racket | NOT yet at baseline |
| 13 | PRE_SERVE_FORMAL | Arrived at baseline, official pre-serve routine, **bounce 1** | |
| 14 | PRE_SERVE_FORMAL | Catches ball with left hand | |
| 15 | PRE_SERVE_FORMAL | **bounce 2** | |
| 16 | PRE_SERVE_FORMAL | **bounce 3** | |
| 17 | SERVING | Final bounce, catch, ball-against-racket, weight rocks forward to left leg, **serving motion officially starts** | State transition at this exact second |
| 18 | SERVING | Weight rocks from front-left to back-right leg | |
| 19 | SERVING | **Ball releases off fingertips for toss; ball peaks; deepest LEG BEND** | Showcase moment per Andrew |
| 20 | SERVE_CONTACT | Extension, contact with ball, serve out wide to Player B's backhand | |
| 21 | RALLY | Player B returns slice deep middle of quad, pushes Player A back | |
| 22 | RALLY | Player A sets up center, Player B hits deep, Player A rolls out, hits inside-in forehand | |
| 23 | RALLY | Ball mid-air to Player B's forehand on deuce court | |
| 24 | RALLY | Player B receives, loads, contacts, hits heavy topspin forehand to Player A's deuce side | |
| 25 | RALLY | Player A loaded, open stance, hitting forehand down-the-line | |
| 26 | RALLY | Player A makes contact, hits down-the-line, ball mid-air to Player B's backhand | |
| 27 | RALLY | Player B receives, loading for backhand slice | |
| 28 | RALLY | Player B contacts, hits backhand slice mid-court slightly to Player A's deuce side | |
| 29 | RALLY | Slice falls in zone 2 (short), Player A takes 2 steps forward inside court, hits forehand slice inside-out | |
| 30 | RALLY | Player B receives ad side, sets up backhand slice | |
| 31 | RALLY | Player B slice cross-court mid-air to Player A's ad side | |
| 32 | RALLY | Player A reaches out wide ad side for backhand slice, contact, cross-court to Player B's ad side | |
| 33 | RALLY | Player B sets up one step inside baseline ad side for slice | |
| 34 | RALLY | Player B contacts slice, tries down-the-line to Player A's deuce side | |
| 35 | POINT_ENDED | Player A on the run wide on forehand, ~3-5ft behind baseline. **Ball lands OUT. Player A lets it go. Point over.** | State transition at this exact second |
| 36 | OFF_COURT_RUNNING | Running off court past the ball, outside doubles alley | |
| 37 | OFF_COURT | Off camera (still off court) | |
| 38 | OFF_COURT_RETURNING | Foot reappears on camera, returning from where he ran off | |
| 39 | OFF_COURT_RETURNING | Walking back, ~8ft from doubles alley | |
| 40 | OFF_COURT_RETURNING | ~4ft from doubles alley | |
| 41 | OFF_COURT_RETURNING | ~2-3ft from doubles alley | |
| 42 | OFF_COURT_RETURNING | Torso facing camera, back turned, ~1.5ft from doubles alley | |
| 43 | OFF_COURT | Reached outside line of doubles alley at corner of baseline. Walking back (towel/ball pickup) | |
| 44 | OFF_COURT | Still walking toward back | |
| 45 | OFF_COURT | Top half of torso cut off by camera, still in doubles alley ad side | |
| 46 | OFF_COURT | Fully off camera except right arm + racket | |
| 47–54 | OFF_COURT | Completely off camera | |
| 55 | RETURNING_TO_BASELINE | Head reappears center of court, returning from towel/ball pickup | |
| 56 | RETURNING_TO_BASELINE | Torso, then bottom half + feet appear | |
| 57 | RETURNING_TO_BASELINE | Heading toward baseline | |
| 58 | PRE_SERVE_INFORMAL | ~1ft from baseline, starts bouncing ball (2 bounces) | |
| 59 | PRE_SERVE_FORMAL | Continues bouncing (2 more), officially enters serve routine at last split second | Cut off by clip end |

**Total point duration:** rally was ~15 seconds (20→35s). **Recovery latency:** 35s (point end) → 59s (next pre-serve start) = **24 seconds of recovery** between points.

---

## 2. Inventory: Current Authored Data vs Ground-Truth Drift

### 2.1 Files involved
| Path | Role | Current state |
|---|---|---|
| `dashboard/public/match_data/utr_01_segment_a.json` | Canonical match data | ALL `display_*` + `coach_insights` + `narrator_beats` + `hud_layouts` need full re-author |
| `dashboard/public/match_data/agent_trace.json` | Tab 3 swarm trace | NOT timestamp-coupled — likely OK as-is, verify quickly |
| `dashboard/src/lib/PanopticonProvider.tsx` | React state injection | Reads the JSON; should be read-only here |
| `demo-presentation/scripts/voiceover_script.md` | New 12-line VO (just authored) | Beat 2/3/4 timings are within 30s/60s windows — verify each line lands on a ground-truth event |
| `demo-presentation/scripts/narration_overlays.md` | DaVinci/CapCut text inserts (older) | Re-time to ground-truth |

### 2.2 Drift severity table (current data vs ground-truth)

| Field | Drift severity | Symptom |
|---|---|---|
| `display_transitions` | **CRITICAL** | SERVE at 11.2s in data; SERVE at 17s real. ACTIVE_RALLY at 11.2s in data; ACTIVE_RALLY at 20s real. **6-second drift.** Missing all transitions for 35s+ (point end, off-court, return). |
| `display_narrations` | **CRITICAL** | "BREAK POINT" framing throughout — fictional context not in clip. "Toss is up" at 11s — actually no toss until 19s. |
| `coach_insights` | **CRITICAL** | At 11.0s says "first rally just closed" — rally hasn't started. At 20.1s says "Short rally, clean exit" — rally just BEGAN at 20s. At 27.2s says "5.07-second rally just closed" — rally still ongoing. |
| `narrator_beats` | **CRITICAL** | At 40s says "feet blur sideways at sprint" — Player A is WALKING OFF COURT outside doubles alley. At 50s says "lateral shuffle" — Player A is COMPLETELY OFF CAMERA. |
| `hud_layouts` | **HIGH** | At 11.0s, 13.3s, 20.1s, 27.2s, 29.5s, 35.4s, 38.6s, 45.3s, 47.7s, 58.6s says "Player A entered pre-serve ritual" — most of these are during rally or off-court phases. Reasoning text uses fictional events. |
| `display_match_phase` | **MISSING** | Field doesn't exist; phase encoded only in `display_transitions`. Add it OR rely on derived phase from transitions. |

### 2.3 Showcase opportunities Andrew flagged (NEW additions, not drift)

| Time (s) | Showcase | Andrew's framing |
|---|---|---|
| 13–17 | **Pre-serve bounce count** | "How many bounces he makes during his pre-serve routine — cool demo showcase" |
| 17–19 | **Deepest leg bend during serve toss** | "Best place to get a leg-bend angle, consistent across reps. If we had a pre-trained baseline, this is the biometric indicator." |

These need: (a) authored coach_insights at the right times, (b) optionally HUD callout widgets, (c) optionally CapCut text overlays during recording.

---

## 3. The Plan — Phased Execution with Maximum Rigor

Three execution-tier options below; **default recommendation = Tier 3 (max rigor)** because Andrew specified "the highest level we've executed so far."

### Phase 0 — Discovery (COMPLETE, see §1 + §2)

Already done in this turn. Schema mapped, drift quantified, ground-truth tabled.

**Status:** ✓ COMPLETE

---

### Phase 1 — Author the Ground-Truth State Machine (~30 min)

**Goal:** rewrite `display_transitions` to align to the table in §1.

**Output:** updated `display_transitions` array with ~12 entries covering all phase changes:

| Timestamp_ms | Player | from_state | to_state | Reason |
|---|---|---|---|---|
| 500 | A | UNKNOWN | DEAD_TIME | Between points, off court |
| 10000 | A | DEAD_TIME | WALKING_TO_BASELINE | Player appears on court |
| 11000 | A | WALKING_TO_BASELINE | PRE_SERVE_INFORMAL | Informal bouncing before reaching baseline |
| 13000 | A | PRE_SERVE_INFORMAL | PRE_SERVE_FORMAL | Arrived at baseline, formal routine starts |
| 17000 | A | PRE_SERVE_FORMAL | SERVING | Final catch, weight rocks forward |
| 20000 | A | SERVING | RALLY | Contact with serve, ball in play |
| 35000 | A | RALLY | POINT_ENDED | Ball lands out, Player A lets it go |
| 36000 | A | POINT_ENDED | OFF_COURT_RUNNING | Running off court past the ball |
| 38000 | A | OFF_COURT_RUNNING | OFF_COURT_RETURNING | Returning from past the doubles alley |
| 43000 | A | OFF_COURT_RETURNING | OFF_COURT | Walking back for towel/ball, off camera |
| 55000 | A | OFF_COURT | RETURNING_TO_BASELINE | Head reappears center of court |
| 58000 | A | RETURNING_TO_BASELINE | PRE_SERVE_INFORMAL | Starts bouncing ball ~1ft from baseline |
| 59500 | A | PRE_SERVE_INFORMAL | PRE_SERVE_FORMAL | Officially enters serve routine (clip cuts off) |

**State machine grammar note:** existing FSM uses `DEAD_TIME, PRE_SERVE_RITUAL, SERVE, ACTIVE_RALLY, UNKNOWN`. New states (WALKING_TO_BASELINE, PRE_SERVE_INFORMAL, PRE_SERVE_FORMAL, RALLY, POINT_ENDED, OFF_COURT_RUNNING, OFF_COURT_RETURNING, OFF_COURT, RETURNING_TO_BASELINE) extend the vocabulary. **Verify the dashboard's TypeScript types accept arbitrary state strings**, OR map our new states to the existing 5-state vocabulary if types are strict. (Likely the types accept strings; will verify in execution.)

**Resource:** Claude direct edit + `data-integrity-guard` agent for Pydantic v2 contract verification (it owns "Pydantic v2 contracts at every module boundary").

**Verification gate:** dashboard renders without TypeScript errors after the edit; phase indicator widget shows the right phase at the right time when scrubbing.

---

### Phase 2 — Re-author display_narrations (Broadcast Voice) (~45 min)

**Goal:** replace all 5 existing narrations (which use the fictional BREAK POINT framing) with new narrations that describe ground-truth events in the team-lead's clinical disembodied voice.

**Important:** these `display_narrations` are TEXT INSERTS that appear ON-SCREEN as broadcast chyrons. They are NOT the voiceover (the VO is `voiceover_script.md`). These show as text overlays in the HUD.

**Decision required (DECISION #1 — see §6):** keep BREAK POINT framing or retire it?
- **My recommendation:** RETIRE. The team-lead pivot was toward "ghost in the machine" clinical truth. Fictional break-point context is the OLD direction. Replace with honest event descriptions.

**New narrations** (assuming RETIRE decision):

| Time range | Narration text (clinical, factual) |
|---|---|
| 0–9s | "Between points. Player A off court, recovery clock running." |
| 10–13s | "Player A returns to baseline. Pre-serve ritual begins informally." |
| 13–17s | "Formal pre-serve routine. Three bounces, then catch." |
| 17–20s | "Serve mechanics: weight transfer, toss release, peak leg flexion." |
| 20–35s | "Rally engaged. Five exchanges across the baseline." |
| 35–38s | "Ball lands out. Player A lets it go. Point ends." |
| 38–55s | "Recovery walk. 17 seconds off-court." |
| 55–60s | "Returning to baseline. Pre-serve ritual restarts." |

These align EXACTLY to ground-truth phases. No fiction.

**Resource:** Claude direct edit + `biometric-fan-experience` skill (owns plain-English fan-facing labels) + a draft pass via `multi-agent-trace-playback` skill (knows the broadcast-voice register).

**Verification gate:** read each narration aloud while watching the corresponding video segment. If the narration describes a different event than what's on screen, redo.

---

### Phase 3 — Re-author coach_insights (Opus Coach Panel) (~60 min)

**Goal:** rewrite all 5 existing coach insights + add 2 new ones for Andrew's showcase moments. These are the "Opus thinking" that displays in the coach panel.

**Important:** these MUST be biomechanically defensible. The `biomech-signal-architect` agent owns the rigor here.

**New coach insights:**

| Timestamp | Topic | Commentary (draft, ~80 words each) |
|---|---|---|
| 11000 ms | Recovery interval observation | "Player A re-enters frame after ~10-second recovery — within typical interval for a baseline-to-baseline rally exit. No fatigue tells in the gait yet; baseline z-score establishment requires multi-point context." |
| 14000 ms | **NEW: Pre-serve ritual entropy** | "Pre-serve routine: 3 ball-bounces with one mid-routine catch. Bounce-count is part of his ritual entropy signature; deviation from baseline (when established) flags pre-point cognitive load." |
| 18500 ms | **NEW: Leg flexion at toss** | "Toss release: peak knee flexion in the back-leg load phase. Knee angle here is the most consistent biometric anchor across his serves — a baseline candidate for fatigue z-scoring once we've sampled enough serves." |
| 22000 ms | Inside-in forehand selection | "Player A's first attacking shot of the rally is an inside-in forehand from defensive position. Court-position telemetry shows ~0.6m behind baseline at contact — high-percentage shot selection under pressure." |
| 32000 ms | Slice exchange court coverage | "Two consecutive slice exchanges. Lateral coverage rising monotonically, peaking at ~0.7 m/s in the wide ad-side recovery. Within his early-match envelope; no degradation tells yet." |
| 36500 ms | Decision to leave the ball | "Point ends not on a winner but on a clean leave — Player A reads the slice trajectory ~5ft behind baseline and lets it go. Court-awareness signal, not fatigue signal." |
| 50000 ms | Recovery latency anchor | "17 seconds off-court for towel/regroup. Recovery latency clock will compare this to baseline; first datapoint, no z-score yet." |

**NEW additions** (the two Andrew flagged):
- 14000ms — **Pre-serve bounce-count showcase** (Decision #2: this format vs visual widget)
- 18500ms — **Leg-flexion-at-toss showcase** (Decision #3: this format vs pose-overlay)

**Resource:** Claude direct draft + `biomech-signal-architect` agent for biomechanical accuracy review + `biometric-fan-experience` skill for plain-English clarity.

**Verification gate:** `biomech-signal-architect` confirms each insight is mathematically defensible (no claims we can't back). `biometric-fan-experience` confirms each is fan-readable (no jargon walls).

---

### Phase 4 — Re-author narrator_beats (Opus Voice/Reasoning Stream) (~30 min)

**Goal:** replace all 6 existing narrator_beats. These are the streaming Opus narration that appears in the broadcast voice overlay.

**Issue with current beats:** narrator_beats at 30s/40s/50s describe lateral pace + sprint motion when Player A is in slice exchanges (30s) or OFF COURT WALKING (40s, 50s).

**New narrator_beats** (aligned to ground-truth):

| Timestamp | Beat text |
|---|---|
| 0 ms | "Camera holds the empty baseline. Player A off-frame; the recovery clock is the first telemetry datapoint of the match." |
| 13000 ms | "Player A settles to the baseline, racket at hip. The ritual begins — three bounces, the first cognitive anchor before the serve mechanics fire." |
| 19000 ms | "Toss release. Back-leg knee flexion at peak load. The single most repeatable biometric across his serves." |
| 28000 ms | "Slice exchange across the baseline. Court coverage ramping but lateral recoveries still unhurried — early-match envelope." |
| 36000 ms | "Ball clears the baseline. Player A reads it cleanly and lets it go. Point closes on a leave, not a winner." |
| 50000 ms | "Off-court recovery. The towel walk, the breath, the silence. Recovery latency is being measured even when nothing is happening." |

**Resource:** Claude direct authoring + `opus-47-creative-medium` skill for voice consistency.

**Verification gate:** read each beat aloud while watching the corresponding 1-second window. Must describe what is visibly happening.

---

### Phase 5 — Re-author hud_layouts (Widget Choreography) (~45 min)

**Goal:** the existing 10 hud_layouts all use the same widget set (PlayerNameplate + TossTracer + SignalBars) and all claim "pre-serve ritual" reasoning. They need phase-appropriate variation.

**New hud_layouts mapped to ground-truth phases:**

| Time | Phase | Widget priorities | Reason text |
|---|---|---|---|
| 500 ms | DEAD_TIME | PlayerNameplate + RecoveryLatencyBar + LastPointSummary | "Between points. Foreground recovery telemetry; rally widgets dimmed." |
| 11000 ms | PRE_SERVE_INFORMAL | PlayerNameplate + BounceCounter + RitualEntropyBar | "Player A approaching baseline. Foreground bounce counter (showcase) + ritual entropy." |
| 13000 ms | PRE_SERVE_FORMAL | PlayerNameplate + BounceCounter (active) + TossTracer (queued) | "Formal pre-serve routine engaged. Bounce counter live; toss tracer ready." |
| 17000 ms | SERVING | PlayerNameplate + LegFlexionAngle + TossTracer | "Serving motion. Foreground leg flexion + toss tracer for the serve mechanics moment." |
| 20000 ms | RALLY | PlayerNameplate + LateralWorkRate + CourtCoverage + ShotTracker | "Rally engaged. Foreground lateral telemetry + shot tracker." |
| 35500 ms | POINT_ENDED | PlayerNameplate + PointSummary (slide-in) | "Point closed on a leave. Foreground point summary; biometric widgets pause." |
| 38000 ms | OFF_COURT_RUNNING | PlayerNameplate + RecoveryLatencyBar (just started) | "Recovery clock running. Foreground recovery latency; no live biometric data while off-camera." |
| 47000 ms | OFF_COURT | RecoveryLatencyBar | "Player off camera. Only the recovery clock advances." |
| 55000 ms | RETURNING_TO_BASELINE | PlayerNameplate (re-acquired) + RecoveryLatencyBar (final reading) | "Player re-acquired. Recovery latency reading completes." |
| 58000 ms | PRE_SERVE_INFORMAL | PlayerNameplate + BounceCounter + RitualEntropyBar | "Pre-serve ritual restarts. Bounce counter resets." |

**Note on widgets that DON'T currently exist in the dashboard codebase:** `BounceCounter`, `LegFlexionAngle`, `LastPointSummary`, `PointSummary`, `RecoveryLatencyBar`, `ShotTracker` — most of these are NOT real widgets. The current dashboard has `PlayerNameplate, TossTracer, SignalBar, CoachPanel`. **We have two options:**

- **Option A — keep widget catalog as-is:** rewrite reasoning text only, keep PlayerNameplate + TossTracer + SignalBar (with different signal_name) for every layout. Honest about what we have.
- **Option B — name new widgets in the data layer:** the JSON references widgets that the React layer doesn't know about. The dashboard would have to handle "unknown widget = render nothing" gracefully. The data describes what the FUTURE dashboard would do; current dashboard shows the existing widgets.

**My recommendation:** Option A — keep the widget catalog, rewrite the reasoning text. Don't promise widgets we don't have. The phase variation comes from changing WHICH SignalBar gets foregrounded (lateral_work_rate during rally, ritual_entropy during pre-serve, recovery_latency during off-court).

**Resource:** Claude direct edit + `2k-sports-hud-aesthetic` skill (owns the design language for HUD widget choreography).

**Verification gate:** scrub the dashboard at every phase boundary; confirm SignalBar foreground visually shifts as expected.

---

### Phase 6 — Showcase Authoring (~45 min, AFTER Decisions #2 + #3)

**Decisions blocking this phase:**
- DECISION #2: Bounce-counting format → coach narration only / new HUD widget / CapCut text overlay only
- DECISION #3: Leg-bend at 19s format → coach narration only / pose overlay annotation / CapCut frame zoom

**Default plan (assuming "coach narration only" for both — minimum scope, maximum honesty):**
- Already covered in Phase 3 coach_insights at 14000ms + 18500ms
- Nothing else needed

**Stretch plan (if Andrew wants visual showcase too):**
- Bounce: add a CapCut text overlay during 13-17s: small mono-caps text bottom-center "PRE-SERVE RITUAL: 1 / 2 / 3 / CATCH" stepping forward each second. Pure CapCut, no dashboard code change.
- Leg bend: add a CapCut zoom (15% slow zoom into Player A's lower body) during 18-20s with tiny callout "PEAK KNEE FLEXION." Pure CapCut, no dashboard code change.

**Resource:** Claude (or Andrew during CapCut assembly).

**Verification gate:** Andrew approves the visual treatment after seeing both options.

---

### Phase 7 — Visual Verification via Dashboard Scrubbing (~45 min)

**Goal:** load the dashboard with the updated match_data and scrub through 60s, frame-by-frame at every phase boundary, confirming visual matches data.

**Method:** use `chrome-devtools-mcp` to load the dashboard, scrub video to each ground-truth timestamp (0, 10, 13, 17, 19, 20, 35, 36, 38, 55, 58, 59), screenshot, visually verify:
- Match phase widget shows the right phase
- Coach panel shows the right insight (or recently displayed it)
- Narration overlay shows the right text
- HUD widget priorities match the layout for that timestamp
- SignalBar values look biomechanically plausible for that phase

**Resource:** `chrome-devtools-mcp` (via deferred-tool load) + `video-frame-validator` agent (already exists — "extracts specific frames from the demo clip using ffmpeg, reads them with Claude vision, then cross-references what is visually observable against DuckDB signal values at that timestamp").

**Verification gate:** every screenshot must show coherent state. Any "data says X, video shows Y" finding triggers a Phase 1-5 patch loop.

---

### Phase 8 — Multi-Agent Review Panel (~60 min)

**Goal:** orthogonal review by 4 agents with distinct lenses to confirm the synced data is bulletproof before commit.

**Panel composition** (per Multi-Agent Review Panels: Orthogonality Over Quantity in CLAUDE.md):
1. **`data-integrity-guard`** — Pydantic v2 contract verification + JSON schema validation + DuckDB schema consistency
2. **`biomech-signal-architect`** — biomechanical accuracy of every coach insight + narrator beat (no claims we can't defend)
3. **`demo-director`** — narrative coherence across the 60s arc + alignment with the team-lead's 5-beat 3-min storyboard
4. **`biometric-fan-experience`** — fan-readability of every narration + signal label + coach insight

Each agent writes findings to `/tmp/<agent>-review.md`. Parent consumes 500-token summaries (avoids 2nd-order context cascade per agent-orchestration discipline).

**Severity gates:**
- CRITICAL → ABORT, fix, re-run review panel
- HIGH → fix in this commit, document in PR body
- MEDIUM → fix if time permits, log otherwise
- LOW → log to MEMORY.md follow-up

**Resource:** parallel Task dispatch (single message with 4 Agent calls).

**Verification gate:** zero CRITICAL findings; HIGH findings addressed.

---

### Phase 9 — Propagate to Presentation Layer (~30 min)

**Goal:** the new ground-truth-aligned data may necessitate adjustments to presentation-layer artifacts authored before sync.

**Files to verify:**
- `demo-presentation/scripts/voiceover_script.md` — re-time L1-L12 to align with the corrected ground-truth events. Specifically:
  - L3 ("nobody else is reading") at 0:32 currently — verify a meaningful visual is on screen at that moment (32s = end of slice exchange in rally; should pair well)
  - L7 ("Just Apple Silicon") at 1:22 currently — that's at 1:22 of the 3-min DEMO, not 1:22 of the 60s clip. The OBS captures will be cuts/segments of the 60s clip. Need to verify which OBS timestamp lands at demo 1:22.
- `demo-presentation/scripts/narration_overlays.md` — re-time text inserts to align with ground-truth phases
- `demo-presentation/scripts/title_card_specs.md` — likely OK (no time-coupling)
- `demo-presentation/scripts/capcut_assembly_workflow.md` — OBS capture spec table may need timestamp adjustments based on which clip seconds we're showing

**Resource:** Claude direct edits.

**Verification gate:** read VO + watch dashboard for each beat; confirm every line lands during the visual moment that motivates it.

---

### Phase 10 — Commit + Document (~15 min)

**Goal:** clean commit with comprehensive message, MEMORY.md update, HANDOFF refresh.

**Commit contents:**
- `dashboard/public/match_data/utr_01_segment_a.json` (the big change)
- Possibly: `demo-presentation/scripts/voiceover_script.md` updates
- Possibly: `demo-presentation/scripts/narration_overlays.md` updates
- `demo-presentation/scripts/capcut_assembly_workflow.md` if OBS spec adjusted
- `MEMORY.md` — DECISION-022 (ground-truth sync executed) + PATTERN-087 (the meta-lesson about authored-data drift catching up to you under deadline)
- `HANDOFF_2026-04-25.md` — updated section noting ground-truth sync complete

**Commit message preview:**
> `feat(match-data): ground-truth sync — utr_01_segment_a.json re-authored to align with Andrew's second-by-second log + bounce/leg-bend showcases`

**Verification gate:** `git status` clean; commit lands.

---

## 4. Time Budget Summary

### Tier 3 (MAX RIGOR — recommended default)

| Phase | Activity | Estimate |
|---|---|---|
| 0 | Discovery (DONE) | 5 min ✓ |
| 1 | State machine | 30 min |
| 2 | display_narrations | 45 min |
| 3 | coach_insights (incl. showcase) | 60 min |
| 4 | narrator_beats | 30 min |
| 5 | hud_layouts | 45 min |
| 6 | Showcase authoring (if visual) | 45 min |
| 7 | Dashboard scrub verification | 45 min |
| 8 | Multi-agent review panel | 60 min |
| 9 | Propagate to scripts | 30 min |
| 10 | Commit + document | 15 min |
| **TOTAL** | | **~6 hours** |

### Tier 2 (FULLER POLISH — drop multi-agent panel + dashboard scrub)

Skip Phases 7 + 8 (rely on TS compile + visual sanity check only). **TOTAL: ~4 hours.**

### Tier 1 (MINIMUM VIABLE — state machine + critical narrations only)

Phases 1 + 2 + 3 (insights only, skip beats + layouts + showcase). **TOTAL: ~2.5 hours.**

---

## 5. Execution Timing — When Does This Happen?

Three options:

### Option A — Execute NOW (autonomous Claude, while Andrew sleeps 06:30–10:00)

**Pros:**
- Maximizes prep time before Andrew's OBS recording at 11:00
- OBS captures land on synced data immediately (no re-recording)
- Saturday team-lead protocol stays intact
- Andrew wakes to a fully-synced dashboard

**Cons:**
- 6 hours fits inside a 3.5-hour sleep window only at Tier 1 or compressed Tier 2
- Tier 3 doesn't fit; must defer Phases 7-8 to Saturday late-AM
- Cannot resolve Decisions #1-3 without Andrew (would need to make defaults)

**Feasible scope inside the sleep window:** Tier 1 + start of Tier 2 (Phases 1+2+3+4 ~ 2.5h). Phases 5-9 deferred to Saturday late-AM.

### Option B — Saturday morning before OBS (10:00–14:00, displaces team-lead protocol by ~1.5h)

**Pros:**
- All 3 decisions resolved with Andrew present
- Tier 3 fits cleanly with Andrew + Claude pairing
- Highest quality outcome

**Cons:**
- OBS recording slips from 11:00 → 14:00
- Voice recording slips from 13:00 → 14:30
- CapCut assembly slips from 15:00 → 16:00 (lose 1 hour of buffer)

### Option C — Sunday morning (8:00–14:00)

**Pros:**
- Saturday team-lead protocol stays untouched
- Saturday produces a DRAFT cut with current data (acceptable submission floor)
- Sunday produces the FINAL cut with synced data

**Cons:**
- OBS captures need to be RE-RECORDED on Sunday with synced dashboard
- CapCut assembly happens TWICE (Sat draft, Sun final)
- High risk Sunday timeline blows up if anything else slips

---

## 6. Three Decisions Andrew Must Make Before Execution

### DECISION #1 — Narrative framing: keep "BREAK POINT" or retire?

**Current:** all `display_narrations` use a fictional "break point" framing ("This is the save", "On a break point, tempo matters as much as pace", etc.). The clip itself shows a regular point — no break-point context exists in the clip.

**My recommendation:** **RETIRE** the break-point framing.

**Rationale:**
- Team-lead pivot was toward "ghost in the machine" clinical truth + Anthropic Minimalism
- Fictional context creates a credibility gap if a judge looks closely at the clip
- The clinical truth ("Player A walks back, ritual restart, deep leg flexion at toss release") is dramatic ENOUGH on its own — no need to invent break-point context
- Aligns with the new `voiceover_script.md` which explicitly omits break-point language

**If you want to KEEP break point:** I can rewrite the narrations to make the fiction internally consistent (e.g., "Player A facing break point at 30-40 with one serve remaining" framing held throughout). But this requires fictional consistency-keeping that's brittle.

### DECISION #2 — Bounce-counting showcase format

**Three options:**
- **A)** Coach narration only (already in plan Phase 3, t=14000ms insight). Minimum scope. Most honest.
- **B)** Coach narration + new BounceCounter HUD widget (requires dashboard React code change, ~1 hour). Ships a NEW widget that displays "Pre-serve bounces: 1 / 2 / 3 / CATCH" stepping during 13-17s.
- **C)** Coach narration + CapCut text overlay during 13-17s (no code change, pure post-production). Mono-caps overlay bottom-center.

**My recommendation:** **C (coach + CapCut overlay)**. Most visible to viewer (CapCut overlay is unmissable in the demo video), zero dashboard code, defers visual decision to CapCut assembly phase Saturday evening.

### DECISION #3 — Leg-bend-at-toss showcase format

**Three options:**
- **A)** Coach narration only (already in plan Phase 3, t=18500ms insight). Minimum scope.
- **B)** Coach narration + pose-overlay annotation (requires dashboard React code change to draw a knee-angle indicator on the keypoints overlay during 17-20s, ~2 hours).
- **C)** Coach narration + CapCut frame zoom (15% slow zoom into Player A's lower body during 18-20s + tiny "PEAK KNEE FLEXION" text overlay).

**My recommendation:** **C (coach + CapCut zoom)**. Same logic as Decision #2 — visible to viewer, zero code, deferred to CapCut.

---

## 7. Risks + Mitigations

| Risk | Mitigation |
|---|---|
| Editing match_data breaks dashboard rendering | TypeScript types + Pydantic v2 schema would catch most. Verify with `bun run dev` (or `bun run build`) after each phase. |
| New state-machine vocabulary not accepted by dashboard React state machine | Phase 1 includes verification step. If types are strict, map new states to existing 5-state vocabulary OR extend types. |
| Re-authoring takes longer than estimated | Tier system (Tier 1 = minimum viable). Can ship Tier 1 + ship demo with that, do Tier 2/3 Sunday morning if time. |
| Showcase visuals (Decisions #2, #3) drift from team-lead "minimalism" principle | Choose narration-only options (A) for both. Adds zero visual chrome; honors minimalism. |
| Multi-agent review panel surfaces critical issues that block commit | Tier 3 only. Tier 1/2 skip the panel. If Tier 3 panel finds CRITICAL issues, drop to Tier 2 and ship. |
| OBS captures recorded with stale data and never re-recorded | Plan execution timing carefully (Option A or B preferred over Option C). |
| Voiceover script timing assumes ground-truth events that may shift slightly | Phase 9 (propagate) covers this. Re-time VO lines AFTER data is synced, BEFORE Andrew records voice. |

---

## 8. Success Criteria (the bar for "highest level we've executed so far")

Tier 3 success means ALL of:

- [ ] Every `display_transitions` entry maps to a ground-truth event in §1 table
- [ ] Every `display_narrations` entry describes only what is visible in its time range
- [ ] Every `coach_insights` entry is biomechanically defensible (claims we can back)
- [ ] Every `narrator_beats` entry describes the visual moment within ±1 second
- [ ] Every `hud_layouts` entry's reason text matches the ground-truth phase
- [ ] Two showcase moments (bounce-count + leg-bend) authored at the right timestamps
- [ ] Dashboard renders without TypeScript errors after match_data changes
- [ ] chrome-devtools-mcp scrub at 12 ground-truth timestamps shows visual-data alignment
- [ ] Multi-agent review panel returns zero CRITICAL findings
- [ ] voiceover_script.md timings re-verified against ground-truth post-sync
- [ ] One clean commit with comprehensive message
- [ ] MEMORY.md DECISION-022 + PATTERN-087 entries documenting the work
- [ ] HANDOFF doc updated to reflect synced state

If any of these is unchecked at the end of execution, we're not at Tier 3. Drop one tier rather than ship partial.

---

## 9. What I Recommend RIGHT NOW

**You have ~3.5 hours of mandated sleep starting now. Here's what I propose:**

1. **You sleep 06:30 – 10:00.** Non-negotiable (per team-lead protocol).
2. **Make the 3 decisions in §6 BEFORE sleeping** so I can execute autonomously. If you give me your answers in your next message, I will:
   - Execute **Tier 2** of this plan in the next ~3.5 hours (Phases 1+2+3+4+5+9 + lightweight verification, skipping Phase 7 chrome-devtools-mcp and Phase 8 review panel)
   - You wake to a fully-synced dashboard ready for OBS recording at 11:00
   - Phases 7 + 8 (verification + review panel) become a Sunday-morning quality-bar pass before final cut
3. **Alternative: defer entire sync to Saturday morning** at 10:00 with us pairing. This shifts OBS to ~14:00 and CapCut to ~16:00. Loses 3 hours of buffer.

**My strong recommendation:** answer the 3 decisions now → I execute Tier 2 autonomously → you sleep → wake at 10:00 to a synced dashboard.

The data drift is severe enough (CRITICAL severity on transitions/narrations/coach insights/narrator beats) that shipping the demo without sync would visibly hurt judging — narration that doesn't match what's on screen is the FIRST thing judges notice. Sync is not optional; only timing is.
