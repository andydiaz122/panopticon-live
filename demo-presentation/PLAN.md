# PLAN.md — Phase 6 Demo Production (storyboard + timeline + assets)

**Owned by**: `demo-presentation/` scope
**Governed by**: `demo-presentation/CLAUDE.md` (rules) + parent `CLAUDE.md`
**Locked decisions**: §4 below (Andrew answered 2026-04-24 AM)
**Open questions**: §13 (for Andrew before Saturday starts)

---

## 1. Context

Hackathon submission deadline: **Sun 2026-04-26 @ 20:00 EST**. Target submit by **17:00 EST** (3-hour buffer). Parent project (PANOPTICON LIVE) is 90 % demo-ready as of Fri 2026-04-24: 3-tab dashboard live on Vercel, 7 biomechanical signals end-to-end, 3 visible anomalies at t=35.9 / 45.3 / 59.1 s, Opus 4.7 Scouting Report working with adaptive thinking + prompt caching.

This plan governs the production of the 3-minute video that IS the submission.

---

## 2. The narrative arc (elevator pitch)

> *Biometric data extracted live from 2D broadcast pixels. Seven fatigue signals. A 2K-Sports HUD. Claude Opus 4.7 reasoning over the telemetry. Built in five days with Claude Code. Managed Agents are the next step: one agent per pro, pre-trained on their biomechanical fingerprint, persistent across a five-hour match.*

**Tone**: technical-clinical. Engineers-judging-engineers. The product speaks; narration stays minimal, dense, concrete. No adjectives that don't carry information. No drama that the visuals aren't earning on their own.

---

## 3. Prime audience (for judges)

Judges scored ~200 submissions of Built with Opus 4.6. The median submission looks like "ChatGPT-for-X with a chat UI." Winning submissions shared:

- Real domain problem, real stakes (CrossBeam = building-permit letters; TARA = Ugandan road appraisal)
- Complete artifact output (PDFs, briefs, fully-designed UIs), not raw text
- Heavy parallel agent use (visible choreography)
- Real demo data (actual dashcam footage, not Lorem Ipsum)

Our alignment:
- ✅ Real domain — pro tennis biomechanics
- ✅ Real stakes — $10B+ sports-analytics industry, prediction markets, coaching
- ✅ Complete artifact — Opus-generated scouting report with signal-cited tactical claims
- ⚠️ Parallel agents — we pivoted away from Managed Agents due to time; we'll paint the *vision* instead (§5 Scene 5B)
- ✅ Real data — actual ATP/WTA broadcast footage, YOLO11m-Pose output, our 7-signal extractors

---

## 4. Decisions locked (Andrew, 2026-04-24)

### Original 7
| # | Question | Andrew's answer |
|---|---|---|
| 1 | Managed Agents integration | **A (skip implementation) + paint the future vision in the demo** — reason from first principles, technically credible, not hand-wavy |
| 2 | Voice-over source | **B (MacBook mic)** for first take; stretch goal circle back to ElevenLabs if extra time |
| 3 | "Weird / playful" feature | **SKIP dramatic features** — Opus Dreams cut as too theatrical for engineering judges |
| 4 | Live tickertape bar | **A (add)** — Palantir-density move, Sat morning add-on |
| 5 | Hero clip | **A (existing 60 s segment)** — all anomalies tuned for this |
| 6 | Remotion scope | **A (chrome only)** — title card + scene breaks + closing card |
| 7 | YouTube visibility | **B (public)** — on Andrew's channel |

### Follow-ups (2026-04-24 PM)
| # | Question | Andrew's answer |
|---|---|---|
| Q1 | Sportradar Scene 3 fidelity | **Full annotation is desired but deprioritized** — leave for end-of-Saturday polish only. Ship demo with or without it. No early time investment. |
| Q2 | Managed Agents graph visual | **Remotion animated fan-out** (Path II) — build rigorously with best tools per task |
| Q3 | Opus Dreams placement | **SKIP** — judges are Anthropic engineers. They value technical vision + clever Claude Code usage + clean aesthetic. Dramatic narration reads childish, not clever. |
| Q4 | Narration tone | **Tennis analyst register** BUT **minimize narration overall**. Focus on the core value prop: *biometric signals extracted from the physical world in real time for more sophisticated prediction systems*. Be very selective about where narration appears. |
| Q5 | Tickertape signal order | **Phase-weighted** — during `PRE_SERVE_RITUAL`: toss_variance + ritual_entropy + crouch_depth; during `ACTIVE_RALLY`: lateral_work + baseline_retreat + recovery_latency. Mirrors the main HUD's state-gating. |
| Q7 | Tab 2 firehose row filter | **All row kinds** — state + signal + insight + anomaly. Maximal density sells the moment. |
| Q8 | "Built with Claude Code" treatment | **Both (C)** — Scene 5A overlay ("Built with Claude Code · 5 days · MIT") + Scene 2 3-second flash of `.claude/skills/` file tree showing the 12+ skill packs. Shows the meta-engineering; judges respect skill-pack orchestration. |

### Narrative discipline (derived from Q3 + Q4)

- **Let the product speak.** The HUD, the SignalBars, the anomaly pulses, the Opus markdown report — these ARE the demo. Narration is a scaffold, not the substance.
- **Every narration line must carry technical information.** No "watch this" moments. No "here's where it gets interesting" phrases. Every sentence states a fact, a number, or a mechanism.
- **Show the clever Claude Code + tool usage as a theme.** Prompt caching indicator. Extended thinking block. Architecture citing Claude Code in the stack. This hackathon is *about* Claude Code — make it visible.
- **No theatrical cadence.** Measured, clear, calm. Tim-Cook-explaining-a-feature-at-WWDC, not McEnroe-calling-a-breakpoint.

---

## 5. The 5-scene storyboard (v3 — minimal-narration, technical-clinical tone)

> **Narration rule**: every line states a fact, a number, or a mechanism. No "watch this", no "here's where it gets interesting", no drama. Measured, calm, deliberate cadence. If a line doesn't carry technical information, cut it.

### Scene 1 (0:00 – 0:20) — The Claim

| t | Visual | Audio |
|---|---|---|
| 0:00 | Tennis clip playing muted. Right-rail SignalBar already pulsing red on first frame. Skeleton overlay tracing the player. | Silence (5 s) |
| 0:05 | Narration starts, calm and technical. | *"Pro tennis broadcast. Standard 2D feed."* |
| 0:10 | Camera pushes in on the SignalBar pulse. | *"Seven biomechanical fatigue signals, extracted live from skeleton keypoints."* |
| 0:15 | Remotion title card: `PANOPTICON LIVE` in 2K-Sports typography (Rajdhani/Eurostile), cyan glow on near-black. 3-second hold. | — |

**Must-have frame**: anomaly pulse visible within 5 s, title card visible at 0:15.
**Differentiation**: no "Introducing". No corporate framing. Two sentences of narration in 15 seconds.

---

### Scene 2 (0:20 – 1:00) — The Stack (7 signals + Opus 4.7 extended thinking)

| t | Visual | Audio |
|---|---|---|
| 0:20 | Full dashboard view. Camera pans across the 3 right-rail SignalBars. | *"YOLO11m-Pose on Apple Silicon. Kalman smoother for occlusion. Seven signal extractors running on the keypoints."* |
| 0:32 | **3-second `.claude/skills/` file-tree flash** overlaid bottom-left of frame: monospace tree showing `cv-pipeline-engineering`, `2k-sports-hud-aesthetic`, `biomech-signal-architect`, `hackathon-demo-director`, `topological-identity-stability`, `opus-47-creative-medium`, `vercel-ts-server-actions`, `match-state-coupling`, `physical-kalman-tracking`, `duckdb-pydantic-contracts`, `react-30fps-canvas-architecture`, `temporal-kinematic-primitives`. Subtle cyan tint. | *"Built with Claude Code. Twelve project-scoped skill packs — CV, biomech, HUD, state-machine, Vercel deployment — each an orthogonal domain."* |
| 0:38 | File-tree flash fades. Camera moves to CoachPanel with "⚡ cached" indicator visible. | *"Opus 4.7 reasons over the telemetry. Adaptive thinking enabled. System prompt cached — the indicator shows cache-read tokens."* |
| 0:52 | Click `Show thinking ▾` button. Opus's extended-thinking block fills CoachPanel. Hold 5 s. | *"Extended thinking, preserved. Every coaching line grounded in a signal value."* |
| 0:58 | Close thinking block. | — |

**Must-have frames**:
- `.claude/skills/` file tree readable ≥ 2 s (Q8 deliverable)
- Expanded thinking block readable ≥ 3 s
- Cache-read indicator visible

---

### Scene 3 (1:00 – 1:45) — The Anomaly (minimal narration, visual drama)

**Baseline build**: SignalBar pulse + Tab-2 firehose cut. No dramatic narration. Ship without A2 annotation overlay unless time permits (see §6).

| t | Visual | Audio |
|---|---|---|
| 1:00 | Video playing. t ≈ 45 s in the clip: Crouch Depth SignalBar goes red. Tickertape bar at bottom highlights the firing signal. | *"Crouch depth: minus 11.69 degrees. Sigma two-point-five."* (clinical, flat) |
| 1:10 | Second anomaly at t ≈ 59 s in clip (Crouch Depth red pulse again). TelemetryLog bottom strip writes the ANOMALY row. | *"Recurring pattern."* |
| 1:18 | Switch to Tab 2 (Raw Telemetry). Dense monospace firehose scrolling, red ANOMALY rows visible. Hold 10 s. | *"Proprietary data stream. Every sample, every state transition, every Opus insight, timestamped."* |
| 1:30 | *(if A2 polish shipped)* Switch back to Tab 1, slow-mo playback to 0.25x for 5 s with geometric annotation overlay (hip-knee-ankle wedge + floating `crouch_angle: -11.69°` label sportradar-style). Otherwise: hold on Tab 2. | *(A2 present)* *"Geometry behind the measurement."* *(A2 absent)* — silence. |

**Must-have frame**: ≥ 1 red ANOMALY row visible on Tab 2 firehose.
**Polish frame (if A2 ships)**: sportradar-style angle wedge + label on the player for ≥ 3 s.

---

### Scene 4 (1:45 – 2:25) — The Opus Scouting Report

| t | Visual | Audio |
|---|---|---|
| 1:45 | Click Tab 3 "Opus Scouting". Click "Generate Report". Button text → "Opus thinking…" | *"Server Action. Opus 4.7. The full telemetry passed as a structured payload — signals, anomalies, state transitions."* |
| 1:50 | Fast-forward the Opus generation 4× (~20 s real-time → ~5 s screen time). | — |
| 1:55 | Markdown streams in. Scroll slowly through the "Biomechanical Fatigue Profile" and "Kinematic Breakdowns" sections. Highlight a table cell showing a signal name + numeric value. | *"Every tactical claim grounded in a signal name and a numeric value. No hand-waving."* |
| 2:15 | End on the "Tactical Exploitations" bullet list. Hold for 3 s. | *"A coaching brief that takes a scout three hours. Opus generates it in thirty seconds."* |

**Must-have frame**: visible `signal_name` + numeric value inline in the markdown.

---

### Scene 5 (2:25 – 2:58) — Architecture + Managed Agents future vision + Close

#### Scene 5A (2:25 – 2:40) — Architecture + "Built with Claude Code"

| t | Visual | Audio |
|---|---|---|
| 2:25 | Static architecture slide (Remotion or Canva). Flow: `YOLO11m-Pose → Kalman → 7-signal extractor → DuckDB → Next.js Server Action → Opus 4.7 → 2K HUD`. Overlay: "Built with Claude Code · 5 days · MIT license". | *"Stack is all open-source. Built in five days with Claude Code — skill packs for CV, biomech, HUD, deployment, demo production."* |

#### Scene 5B (2:40 – 2:55) — Managed Agents future vision

| t | Visual | Audio |
|---|---|---|
| 2:40 | Remotion animated fan-out graph: central Opus 4.7 node, 8 branches for top players (Alcaraz, Sinner, Djokovic, Medvedev, Gauff, Swiatek, Sabalenka, Rybakina), each tagged with a specialist skill (`biomech-forensics`, `serve-analyst`, `return-analyst`, `injury-risk-officer`). Nodes fade in sequentially over 8 s. | *"Today: one player, one clip. Next: a Claude Managed Agent pre-trained on every pro on tour. Each carrying that player's biomechanical fingerprint. Persistent across a five-hour match. Coach queries the player's scouting brain."* |

#### Scene 5C (2:55 – 2:58) — Close

| t | Visual | Audio |
|---|---|---|
| 2:55 | Closing card (Remotion): `PANOPTICON LIVE | panopticon-live.vercel.app | github.com/andydiaz122/panopticon-live | Built with Opus 4.7 · April 2026`. Hold 3 s. | Silent. |
| 2:58 | Hard cut to black. | — |

**Must-have frame**: Managed Agents fan-out graph + repo URL visible ≥ 2 s.
**Opus 4.7 narrative anchor**: Scene 5B targets the $5K "Best Use of Managed Agents" prize via first-principles vision, not false claim of current implementation.

---

### Total target: 2:58 (2-second margin under 3:00 hard cap)
### Narration footprint: ~12 lines total, down from v2's ~25 lines

---

## 6. Approved Saturday add-ons (code-freeze exceptions)

**Priority order** (top = highest ROI per hour). All time-boxed; if budget exceeded, fall back per row.

| # | Add-on | Priority | Budget | Fallback if over |
|---|---|---|---|---|
| A1 | Live tickertape bar at Tab 1 bottom | **High** | 1 h | Skip — storyboard works without |
| A4 | Managed Agents future-vision fan-out graph (Remotion animated, Scene 5B) | **High** | 1.5 h | Static Canva diagram (fade-in via Ken Burns pan) |
| A5 | Architecture diagram (Scene 5A) | **High** | 1 h | Hand-drawn Canva slide |
| A6 | Remotion title card + scene breaks + closing card (Scene 1 + Scene 5C) | **High** | 2 h | ffmpeg `drawtext` + Canva PNG exports |
| A2 | Sportradar slow-mo + geometric annotation (angle wedge + velocity arrow + floating labels) | **Low — end-of-Saturday polish ONLY** | 4 h | Ship demo WITHOUT it; demo works at full technical bar without this. Incremental "safe" additions welcome — full playback-rate slow-mo at anomalies (30 min) without annotations is the minimal worthwhile slice if we have a spare hour. |
| ~~A3~~ | ~~Opus Dreams interstitial~~ | **CUT** | — | Dropped per Andrew 2026-04-24 — too theatrical for engineering-judge audience |

**Realistic Saturday build plan**: A1 + A4 + A5 + A6 = ~5.5 h core. Remaining Saturday time → narration script + rehearsal takes. A2 becomes Sunday-morning polish if and only if the rough cut is already solid and we have ≥ 2 h spare.

---

## 7. Sportradar-aesthetic geometric annotation spec (Add-on A2)

The visual signature of Scene 3. Reference screenshots live in `demo-presentation/assets/references/`:
- `sportradar_tennis.png` — dark navy, tennis player, red vector overlay on racket/ball trajectory, floating `"y": -38.05` label
- `sportradar_mma.png` — same aesthetic on MMA fighter

**What we build**:

1. **Video playback speed control** — `<video>` element `playbackRate` animated between 1.0 and 0.25 via ref + CSS/requestAnimationFrame. Auto-trigger at anomaly timestamps (t=45.3, 59.0). Cost: 30 min.

2. **Geometric primitives layer** — new canvas overlay on top of PanopticonEngine's skeleton canvas. Each primitive takes 2–3 keypoints and renders geometry:
   - **Angle wedge** (crouch angle) — arc between hip-knee-ankle, 20° of visible angle, stroke cyan 2px, fill cyan 15% alpha. Label floats on the wedge's midpoint.
   - **Velocity arrow** (lateral motion) — vector from hip position over 200ms, arrowhead at end, label at midpoint showing m/s.
   - **Trajectory spline** (ball arc, optional) — bezier approximation of the ball in motion. Only if we have ball detection (low prior — skip unless trivial).

3. **Floating labels** — `<div>` positioned via absolute pixel coords, mono font (JetBrains Mono), cyan color, semi-transparent dark bg. Text format: `crouch_angle: -11.69°` matching sportradar's aesthetic.

4. **Fade-in / fade-out animations** — primitives fade in over 200ms when slow-mo engages, fade out over 300ms when it disengages.

**File owner**: `dashboard/src/components/PanopticonEngine.tsx` (extend) + new `dashboard/src/components/AnnotationOverlay.tsx` (create).

**Code-freeze status**: this is the ONE sanctioned violation. Work on `demo-v1` branch only.

**Fallback**: if the annotation math is wrong or the render is buggy by Saturday 14:00, ship with slow-mo ONLY (playbackRate change at anomaly moments). That alone adds significant drama. The annotation is the cherry on top.

---

## 8. Managed Agents future-vision segment — first-principles script (Scene 5B)

This segment paints the vision without overclaiming. Reasoned from first principles:

### The vision in one sentence

> *Every pro on tour has a dedicated Claude Managed Agent, pre-trained on that player's biomechanical fingerprint, running concurrent and persistent during live matches — serving as the opposing coach's scouting brain.*

### Why Managed Agents are the right primitive

- **Long-running sessions** — a match is 2-5 hours. Managed Agents' durable session log + `getEvents()` API handles the persistence natively. Standard Server Actions timeout.
- **Decoupled brain/hands** — the agent reasons; tools (our existing 7-signal extractors + historical baselines) execute. Exactly the pattern Anthropic's "Scaling Managed Agents" post describes.
- **Outcome-defined evaluation** — "did the brief ground every tactical claim in a numeric signal?" is a natural-language success criterion. Fits Managed Agents' outcome-over-assertion model.
- **Specialization via skills** — each player-agent loads a specialized skill pack: `biomech-forensics`, `serve-analyst`, `return-analyst`, `injury-risk-officer`. Skills are the Managed-Agents-native composition primitive.

### What's required for production (the engineering argument judges care about)

1. **Per-player training data** — archive of that player's matches. Already commercially available via ATP data licenses, TennisTV, etc.
2. **Baseline computation** — our Phase 2 pipeline (YOLO → Kalman → 7-signal extractor → DuckDB) runs on the archive to compute rolling Lomb-Scargle baselines per signal per player.
3. **Agent wrapper** — one Managed Agent per top-100 player. Tools: `queryHistoricalBaseline(player, signal)`, `compareLiveToBaseline(...)`, `emitTacticalBrief(...)`, `persistInsightToSession(...)`.
4. **Real-time inference surface** — MPS or CUDA at 10+ FPS on broadcast video. Already demonstrated: our M4 Pro runs YOLO11m-Pose at ~5-8 FPS.
5. **Coach-facing interface** — the HUD you just saw, but with a live Managed Agent channel replacing the static Scouting Tab.

### Timeline to ship (for judge credibility)

- 0-3 months: historical match archive pipeline + per-player baseline computation for top 20 men + top 20 women
- 3-6 months: Managed Agent wrappers + specialized skills per agent
- 6-9 months: live-inference pipeline on broadcast feeds + coach dashboard
- 9-12 months: pilot with a single ATP coach / WTA coach during 2027 season

**This is what gets said in the demo (condensed to 10 s of narration)**:

> *"What you just saw was one player, one clip. Here's where we go next — a Claude Managed Agent pre-trained on every pro on tour. Each agent carries that player's biomechanical fingerprint. Each persists a durable match memory across five-hour sessions. The coach doesn't query a chatbot. The coach queries the player's own scouting brain."*

---

## 9. Asset registry

| Asset | Path | Source | Status |
|---|---|---|---|
| Hero tennis clip (60 s) | `dashboard/public/clips/utr_match_01_segment_a.mp4` | Force-added PR #4 | ✅ live on Vercel |
| Golden match data | `dashboard/public/match_data/utr_01_segment_a.json` | Phase 4 crucible + Phase 5 anomaly injection | ✅ anomalies at 35.9/45.3/59.1 s |
| Backup full-match footage | `/Users/andrew/Documents/Coding/Predictive_Modeling/Alternative_Data/data/videos/utr_match_0{1,5,8}_ANCHOR_OK.mp4` | Pre-hackathon downloads (no broadcast cuts, camera-locked) | ✅ 3 matches available |
| Sportradar reference screenshots | `demo-presentation/assets/references/sportradar_tennis.png`, `sportradar_mma.png` | Screenshot from sportradar.com landing | ⬜ TODO — save screenshots into folder |
| 2K Sports HUD screenshots | `demo-presentation/assets/references/2k_sports_*.png` | Study material | ⬜ TODO (optional — skill `.claude/skills/2k-sports-hud-aesthetic` already codifies this) |
| Voice-over script | `demo-presentation/scripts/narration.md` | Hand-written Sat AM | ⬜ TODO — draft Sat 10:00 |
| Shot list | `demo-presentation/scripts/shot_list.md` | Hand-written Sat AM | ⬜ TODO — draft Sat 09:00 |
| Opus Dreams script (if time) | `demo-presentation/scripts/opus_dreams.md` | Hand-written Sat PM | ⬜ OPTIONAL |
| Title card composition | `demo-presentation/remotion/OpeningTitle.tsx` | Remotion (new) | ⬜ TODO — Sat 15:00 |
| Scene break card | `demo-presentation/remotion/SceneBreak.tsx` | Remotion | ⬜ TODO |
| Managed Agents graph | `demo-presentation/remotion/ManagedAgentsGraph.tsx` | Remotion OR Canva PNG | ⬜ TODO |
| Architecture diagram | `demo-presentation/remotion/ArchDiagram.tsx` OR `assets/diagrams/architecture.png` | Remotion OR Canva PNG | ⬜ TODO |
| Closing card | `demo-presentation/remotion/ClosingCard.tsx` | Remotion | ⬜ TODO |
| Raw OBS takes | `demo-presentation/renders/raw/take_1.mp4`, `take_2.mp4`, `take_3.mp4` | OBS recordings Sat/Sun | ⬜ TODO |
| Narration WAV | `demo-presentation/audio/narration_final.wav` | MacBook Pro mic via QuickTime or Audacity | ⬜ TODO — Sat 14:00 |
| Rough cut | `demo-presentation/renders/panopticon_live_rough.mp4` | DaVinci Resolve Free | ⬜ TODO — Sat 17:00 |
| Final render | `demo-presentation/renders/panopticon_live_final.mp4` | DaVinci Resolve Free → H.264 export | ⬜ TODO — Sun 13:00 |
| YouTube URL | (runtime artifact) | Andrew's YouTube | ⬜ TODO — Sun 14:30 |
| Written summary | `demo-presentation/scripts/submission_summary.md` | Hand-written Sun morning, 100–200 words | ⬜ TODO — Sun 15:00 |

---

## 10. Timeline (Sat–Sun)

### Saturday 2026-04-25

| Time | Block | Deliverable |
|---|---|---|
| 08:00 | Coffee + re-read PLAN.md | Plan mental-model refreshed |
| 08:30 | Create `demo-v1` branch. Install Remotion (and MCP). Verify Vercel prod deploy green. | Dev env ready |
| 09:00 | **A1 build** — tickertape bar on Tab 1 | `dashboard/src/components/Tickertape.tsx` created |
| 10:00 | **A5 build** — architecture diagram in Canva (simple boxes + arrows) + "Built with Claude Code · 5 days · MIT" overlay | `assets/diagrams/architecture.png` exported |
| 11:00 | **A6 build** — Remotion opening title card + closing URL card | `remotion/OpeningTitle.tsx`, `remotion/ClosingCard.tsx` rendering |
| 13:00 | Lunch + review morning work | Checkpoint |
| 13:30 | **A4 build** — Remotion animated Managed Agents fan-out graph | `remotion/ManagedAgentsGraph.tsx` rendering |
| 15:00 | Draft narration script — §5 scene audio columns → full prose, minimal, technical | `scripts/narration.md` v1 |
| 16:00 | **First OBS rehearsal take (full 3 min, no audio)** — verify pacing | `renders/raw/take_1.mp4` |
| 17:00 | Review take_1, refine narration pacing + timing marks | Feedback notes |
| 17:30 | **Second OBS take with voice-over via MacBook mic** | `renders/raw/take_2.mp4` |
| 19:00 | Dinner + review take_2 with outside-eye | Feedback |
| 20:00 | **IF TIME REMAINS (≥ 2 h)**: begin A2 minimal slow-mo polish (playbackRate only at anomaly moments, no annotation layer). Otherwise skip. | `A2_minimal.mp4` optional |
| 21:00 | Update MEMORY.md / FORANDREW.md / TOOLS_IMPACT.md with Saturday learnings | Living docs current |

### Sunday 2026-04-26

| Time | Block | Deliverable |
|---|---|---|
| 08:00 | Coffee + review Saturday takes. Choose best take as master. | Master take locked |
| 09:00 | **Third take (final intent)** if Saturday's takes don't meet bar | `renders/raw/take_3.mp4` (optional) |
| 10:00 | DaVinci rough-cut assembly: master take + Remotion chrome + audio | `renders/panopticon_live_rough.mp4` |
| 12:00 | Lunch + review rough cut with Andrew's outside-eye | Feedback |
| 13:00 | **A4 decision gate** — is the Managed Agents future-vision graph ready? If not, use static Canva image instead | A4 status locked |
| 13:30 | Final cut refinement: color grade, audio mix, fades | `renders/panopticon_live_final.mp4` |
| 14:30 | H.264 export, final render QA (play full video 3 times) | Render verified |
| 15:00 | **YouTube upload** (public, per Decision #7) | YouTube URL copied |
| 15:30 | Write `scripts/submission_summary.md` (100-200 words) | Summary drafted |
| 16:00 | Update GitHub README with live URL + architecture diagram + description | README current |
| 16:30 | Final `vercel deploy --prod --yes` + HTTP 200 verification | Prod URL confirmed |
| 17:00 | **SOFT SUBMIT** via CV platform | Submission received |
| 17:30 | Commit + push final state | git log clean |
| 18:00 | Draft social posts (X/LinkedIn) — do NOT post until submission confirmed | Social drafts ready |
| 19:00 | Submission confirmation screenshot → `FORANDREW.md` + commit | Artifact captured |
| 19:30 | **LOCKOUT** — no further submission changes | Submission final |
| 20:00 | Deadline — we're 2.5 hours ahead | ✅ |

---

## 11. Submission checklist (pre-flight before 17:00 Sun)

- [ ] Vercel production URL serves HTTP 200 (`vercel curl --deployment $URL / -- -I`)
- [ ] Demo video: 1920×1080 H.264 MP4, under 3:00 hard cap, ≤ 500 MB
- [ ] YouTube uploaded, **public**, URL copied
- [ ] Video title: `PANOPTICON LIVE — Biomechanical Intelligence for Pro Tennis | Built with Opus 4.7 Hackathon`
- [ ] Video description (template):
  ```
  Built for the Anthropic × Cerebral Valley "Built with Opus 4.7" hackathon (April 21-26, 2026).

  PANOPTICON LIVE extracts 7 biomechanical fatigue signals from pro tennis broadcast video and renders them as a 2K-Sports-style HUD powered by Claude Opus 4.7.

  🎯 Live demo: https://panopticon-live.vercel.app
  📦 Source: https://github.com/andydiaz122/panopticon-live
  🧠 Model: claude-opus-4-7 with extended thinking + prompt caching
  ⚙️ Stack: Next.js 16 · FastAPI · DuckDB · YOLO11m-Pose · Ultralytics · filterpy · scipy

  Built by Andrew Diaz with Claude Code.
  ```
- [ ] GitHub repo PUBLIC, LICENSE file is MIT, README updated with live URL + architecture diagram + 1-paragraph description
- [ ] Written summary 100-200 words — draft + reviewed
- [ ] CV submission form fields: video URL, GitHub URL, written summary all pasted
- [ ] Screenshot of submission confirmation captured
- [ ] `FORANDREW.md` updated with submission event
- [ ] Final commit + push

---

## 12. Fallback plans

| Scenario | Fallback | Trigger |
|---|---|---|
| Remotion won't render Sat 15:00 | ffmpeg `drawtext` + Canva exports for title/close | 2 h into Remotion without working title |
| OBS drops frames | Playwright scripted recording via `page.video()` | > 5% frame drop in a Saturday rehearsal take |
| MacBook mic audio too roomy / noisy | ElevenLabs narration (Sat PM fallback path — Decision #2 stretch) | Rehearsal take reveals unlistenable audio |
| Vercel prod deploy breaks Sun AM | Submit preview URL (`panopticon-live-1fqx9c4iz-dmg-decisions.vercel.app`) + open prod-fix PR | Build failure at deploy time |
| Opus API 401 Sun AM | Re-verify key via curl + rotate if needed (PATTERN-056 incantation) | Any 401 in `vercel logs` |
| A2 (sportradar annotation overlay) math is wrong | Ship Scene 3 with slow-mo only, no annotation | Sat 14:00 checkpoint fails |
| Time pressure: no final render by Sun 16:00 | Submit best rough cut with apology note in summary | 16:00 Sun |
| CV submission platform errors | Discord #questions channel, screenshot error, email moderators | Any submit error |

---

## 13. Open questions (remaining — lowest priority)

All Q1–Q5, Q7, Q8 answered by Andrew (see §4). The only remaining open item:

### Q6 — Demo-v1 branch merge strategy (defer until post-submit)

After submission:

**Option M1 (recommended)** — Merge `demo-v1` → `main` immediately post-submit. Keeps main as truth. Final-round (Apr 28) plays the same YouTube URL regardless of repo state.

**Option M2** — Keep `demo-v1` frozen until after final-round judging, then merge.

Decision defers to Sunday evening after submission.

---

## 14. Links

- Parent CLAUDE.md: `../CLAUDE.md`
- Demo rules CLAUDE.md: `./CLAUDE.md`
- Hackathon portal: https://cerebralvalley.ai/events/built-with-4-7-hackathon
- Submission form: (add when known — Sunday morning)
- Vercel prod URL: https://panopticon-live.vercel.app (assuming default alias)
- Current preview URL: https://panopticon-live-1fqx9c4iz-dmg-decisions.vercel.app
- 2K Sports reference: https://2k.com
- Sportradar reference: https://sportradar.com
- Palantir Foundry (visual inspiration): https://www.palantir.com/platforms/foundry/
