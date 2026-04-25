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

### Iteration 1-4 dialectical outcomes (2026-04-24 PM)
| # | Question | Andrew's answer |
|---|---|---|
| Q9 | Narrative arc pivot | **Full Detective Cut + kill Scene 5B** — adopt Builder's arc (judge discovers alongside Opus), shrink Managed Agents to ≤ 15 s still/compressed clip. Iterations 2 + 3 both converged independently. See §5 v4 storyboard. |
| Q10 | Opus 4.7 showcase upgrades | **All three** — unfilter `actions.ts:145` thinking-block filter (5 min) + build `<ThinkingVault>` 3-column component for Scene 4 split-screen climax (~1.5 h) + add precomputed Opus 4.7 vision call on one broadcast frame (~1 h). Addresses the Iter-2 "B-minus" verdict. |
| Q11 | A2 sportradar annotation | **Tier split: A2a low-risk in Saturday core, A2b high-risk as dedicated stretch only**. Andrew's rule: only low-risk/high-value items land in Saturday's core sprint; higher-risk polish gets undivided resources at end. A2a = `HTMLVideoElement.playbackRate` animated to 0.25× at anomaly timestamps (30 min build, zero canvas math). A2b = geometric angle-wedge + velocity-arrow overlay (4 h canvas work, stretch only if everything else green AND ≥ 3 h remaining). |
| Q12 | Operational playbook | **Both adopted** — Saturday dry-runs (14:00 YouTube + 17:00 CV form load) + post-submit amplification (Sun 20:15 X thread + Sun 21:00 47builders.fyi self-listing + Mon 08:00 Discord #BuiltWithClaude + DevRel DM). See §14. |

### Narrative discipline (derived from Q3 + Q4)

- **Let the product speak.** The HUD, the SignalBars, the anomaly pulses, the Opus markdown report — these ARE the demo. Narration is a scaffold, not the substance.
- **Every narration line must carry technical information.** No "watch this" moments. No "here's where it gets interesting" phrases. Every sentence states a fact, a number, or a mechanism.
- **Show the clever Claude Code + tool usage as a theme.** Prompt caching indicator. Extended thinking block. Architecture citing Claude Code in the stack. This hackathon is *about* Claude Code — make it visible.
- **No theatrical cadence.** Measured, clear, calm. Tim-Cook-explaining-a-feature-at-WWDC, not McEnroe-calling-a-breakpoint.

---

## 5. The 5-beat storyboard (v4 — Detective Cut, locked 2026-04-24 PM after 4-iteration dialectical review)

> **Narration rule** (unchanged from v3): every line states a fact, a number, or a mechanism. No "watch this." No drama. Measured, calm, deliberate. Target footprint ~10 lines in 3 minutes.
>
> **Arc principle** (new in v4): the judge DISCOVERS alongside Opus. Open cold on the anomaly, not a title. Opus finds something the commentators miss; we're in the room with it. Climax at 1:58 fuses anomaly geometry + Opus thinking + cached indicator into ONE frame — the only moment where judges see Opus 4.7 *think, reject, re-reason* in real time.

### B1 — The Miss (0:00 – 0:18)

| t | Visual | Audio |
|---|---|---|
| 0:00 | Tennis clip playing muted. SignalBar pulsing red from frame 1. Skeleton overlay tracing the player. No logo. No title. | Silence (8 s) |
| 0:05 | Feed pauses at t=45.3 s in clip. Crosshair zooms to player's knee. On-screen text appears: `CROUCH DEPTH · Δ −11.69° · σ 2.5`. | (still silent) |
| 0:10 | Vision-pass overlay (precomputed Opus 4.7 vision call on this exact frame) shows the annotated pose. | *"Nobody on the broadcast called this. Our system flagged it at frame 1,359."* |

**Must-have frame**: crosshair + on-screen numeric overlay visible ≥ 3 s.
**Differentiation**: no "Introducing". No title card here (deferred to closing). Cold-open with PROOF, not setup.

---

### B2 — The Sensor (0:18 – 0:50)

| t | Visual | Audio |
|---|---|---|
| 0:18 | Playback resumes. Full HUD snaps in: SignalBar rail, skeleton overlay, tickertape, Coach Panel. Smooth entrance. | *"YOLO11m-Pose on Apple Silicon. Kalman on court meters. Seven biomechanical signals — toss variance, ritual entropy, crouch depth, recovery latency, lateral work, baseline retreat, split-step."* |
| 0:35 | 3-second `.claude/skills/` file-tree flash overlaid bottom-left (12 project skill packs — `cv-pipeline-engineering`, `2k-sports-hud-aesthetic`, `biomech-signal-architect`, `hackathon-demo-director`, `topological-identity-stability`, `opus-47-creative-medium`, `vercel-ts-server-actions`, `match-state-coupling`, `physical-kalman-tracking`, `duckdb-pydantic-contracts`, `react-30fps-canvas-architecture`, `temporal-kinematic-primitives`). | *"Built with Claude Code. Twelve skill packs. All extracted from 2D broadcast pixels."* |

**Must-have frames**:
- HUD snap-in smoother than a hard cut
- `.claude/skills/` file tree readable ≥ 2 s (Q8 deliverable)

---

### B3 — The Second Miss (0:50 – 1:30)

| t | Visual | Audio |
|---|---|---|
| 0:50 | Video continues. At t ≈ 59.1 s in clip: Crouch Depth SignalBar flashes red again. TelemetryLog bottom strip writes the ANOMALY row. | *"Recurring. Crouch depth minus 11.69 degrees. Again. Same signature, 13.8 seconds apart. Fatigue, not randomness."* |
| 1:05 | **A2a slow-mo** (mandatory): video `playbackRate` animates from 1.0× → 0.25× for 5 s. Skeleton overlay stays visible. | (silent beat) |
| 1:10 | Switch to Tab 2 (Raw Telemetry). Dense monospace firehose scrolling — all row kinds: STATE amber, SIGNAL cyan, INSIGHT purple, ANOMALY red. Hold 15 s. | *"Proprietary data stream. Every sample, every state transition, every Opus insight, timestamped."* |
| 1:25 | *(A2b stretch only)* brief geometric angle-wedge overlay if A2b shipped. Otherwise hold on firehose. | — |

**Must-have frame**: ≥ 1 red ANOMALY row visible on Tab 2 firehose.
**Polish frame (A2b stretch)**: sportradar-style angle wedge + label for ≥ 3 s.

---

### B4 — Opus Reads the Body (1:30 – 2:30) — THE CLIMAX

**This is the single lean-forward moment. 60 seconds of runtime. Split-screen is the money shot.**

| t | Visual | Audio |
|---|---|---|
| 1:30 | Switch to Tab 3 "Opus Scouting". Click "Generate Report". Button → "Opus thinking…" | *"Opus 4.7. Adaptive thinking. System prompt cached."* |
| 1:35 | **Split-screen opens**: left pane = Scene-3 slow-mo frozen on the anomaly frame with `crouch_angle: -11.69°` floating label (leveraging A2a frozen state); right pane = new `<ThinkingVault>` component streaming extended thinking in 3-column `[Considered] / [Rejected] / [Concluded]` layout. | — |
| 1:45 | Thinking stream speed-up 4× — judges watch tokens accumulate in real time. `⚡ cached` indicator lit with token counter. | *"Extended thinking preserved. Every coaching line grounded in a signal value."* |
| **1:58** | **THE FRAME**: Rejected Thought chip flashes: `✗ "Serve-mechanics narrative" rejected — crouch degrade preceded toss variance by 8.2 s`. Simultaneously: the right-pane thinking mid-stream cites `-11.69°` — which is literally visible on the left-pane frozen player. Pixels left, tokens right, one number connects them. Cache indicator still lit. | *"Opus rejected its first hypothesis because the timing didn't fit the data."* |
| 2:10 | Split-screen closes. Markdown scouting report streams in on full screen. Scroll through Biomechanical Fatigue Profile + Kinematic Breakdowns table. | *"Every tactical claim grounded in a signal name and a numeric value."* |
| 2:25 | Pause on Tactical Exploitations list. | *"A coaching brief that takes a scout three hours."* |

**Must-have frame**: the 1:58 three-element frame (left pixel annotation, right thinking mid-stream citing that exact number, cache indicator lit, Rejected Thought chip visible). This IS the demo.

---

### B5 — The Instrument, At Scale (2:30 – 2:58)

| t | Visual | Audio |
|---|---|---|
| 2:30 | Architecture slide (Remotion or Canva). Flow: `YOLO11m-Pose → Kalman → 7 signals → DuckDB → Server Action → Opus 4.7 → 2K HUD`. Overlay: "Built with Claude Code · 5 days · MIT license". | *"Stack is all open-source. Built in five days."* |
| 2:42 | **Managed Agents fan-out — compressed to ≤ 15 s still/simple fade** per Q9 decision. Central Opus 4.7 node, 8 branches for top players (Alcaraz, Sinner, Djokovic, Medvedev, Gauff, Swiatek, Sabalenka, Rybakina). NO 8-second sequential animation — just fade in as a single frame + hold. | *"Next: one Managed Agent per pro, persistent across a five-hour match."* |
| 2:54 | Closing card: `PANOPTICON LIVE | panopticon-live.vercel.app | github.com/andydiaz122/panopticon-live`. Title card `PANOPTICON LIVE` folded in here (not Scene 1). | Silent. |
| 2:58 | Hard cut to black. | — |

**Must-have frame**: repo URL + title card visible ≥ 2 s.

---

### Total target: 2:58 (2-second margin under 3:00 hard cap)
### Narration footprint: 10 lines total

### v3 → v4 diff summary
- **B1 opens COLD on proof** (vision-pass annotated frame at t=45.3), not on a title card or scene-setter. Title deferred to closing.
- **Climax engineered at 1:58** (B4) — split-screen, Rejected Thought chip, cached thinking stream, same number visible left + right.
- **Scene 5B Managed Agents compressed** from 15-second animated fan-out → ≤ 15-second still/fade (per Q9 decision; advertising un-built feature is net-negative per Iter-3 skeptic).
- **Thinking Vault NEW** (Q10) — 3-column `[Considered] / [Rejected] / [Concluded]` component in B4 split-screen.
- **Vision pass NEW** (Q10) — precomputed Opus 4.7 vision call on t=45.3 frame, rendered as B1 overlay.
- **A2a slow-mo PROMOTED** (Q11) — mandatory `playbackRate` animation in B3; A2b annotation stretch-only.

---

## 5.6. Anthropic-Workflow-Minus-Palette Adoption + Vimeo 2nd Reference (LOCKED 2026-04-24 late evening)

**Andrew's directive 2026-04-24 ~21:00 EST**: *"Let's not use the Anthropic colors for our project; however let's use everything else about their video demo generation workflows. Also, I found a demo video: https://vimeo.com/205032211 — I would like for you to research and reverse engineer."*

After the warm-clay palette experiment was reverted (USER-CORRECTION-036 in MEMORY.md), the 3-agent research wave's craft findings remain durable as universal rules — palette doesn't override product-fit, but motion vocabulary, typography hierarchy, pacing discipline, and Figma → Remotion workflow are PORTABLE across domains. Concretely:

### Adopted from Anthropic (cyan-palette-compatible)

- **Typography hierarchy**: Fraunces serif for hero wordmarks (RE-APPLIED to B0 title 2026-04-24 ~21:30 — `Panopticon Live` with italic "Live" in cyan accent, mono subtitle/attribution). Retains the Anthropic "italic-for-emphasis" signature without copying their palette.
- **Motion vocabulary** (PATTERN-078): hard cuts dominate, ONE scale-pop primitive, word-by-word typewriter for dialog reveals, NO parallax / gradients / glassmorphism / drop shadows. B0 already complies; future B5 + scene-breaks must too.
- **Pacing** (PATTERN-079): 7-9 cuts/min product-demo register. Long dwells (8-12s per beat). Hard cuts only between beats. Silence/stillness as punctuation.
- **Editorial layout**: small label above + big headline below + bleeding context off-frame. 6% headline / 94% margin ratio. Generous air. Apply to scene-break cards + B5 closing.
- **Figma-static / Remotion-truth workflow** (PATTERN-080): Figma frames = scene mockups + color tokens. Remotion = where motion logic lives. Never author motion in Figma Prototype Mode.
- **Source-truth tokens** (PATTERN-081): if/when palette stabilizes, consolidate to a single tokens file. Currently deferred — palette is settled cyan; B0 inlines hex codes since there are only 4.

### NOT adopted (palette stays sports-broadcast / cyan)

- Anthropic cream/sandstone bg (`#F8F8F8` / `#E0D8C8`)
- Anthropic Spark coral accent (`#D97757`)
- Reason: PANOPTICON LIVE is sports-broadcast register, not editorial-paper register. Cyan-on-cool-blue is the native domain convention (ESPN, Hawk-Eye, Sportradar). See MEMORY.md USER-CORRECTION-036 for full rationale.

### Vimeo 205032211 — second design reference (SYNTHESIS LANDED 2026-04-24 ~20:00 EST)

Andrew's note: *"This is the best looking demo I've seen so far in addition to the Anthropic product release videos."* The deconstruction agent identified the video as **Numerai's *Introducing Numeraire*** (Feb 2017, 2:04, 1080p25) — the famous crypto-token launch film featuring on-camera VC interviews intercut with full-CGI vaporwave dystopia, B&W founder portraits over color-coded particulate starfields, and golden-hour cinematic A-roll. Full DNA file at `demo-presentation/assets/references/vimeo_205032211_dna.md` (10 numbered sections, hex-confirmed palette tables, scene-by-scene log).

#### What we ADOPT from Numerai (compatible with broadcast-HUD register)

1. **Logo ignition curve, NOT scale-pop** (PATTERN-082): Numerai's closing N-sigil "switches on" via a +brightness curve + faint cyan glow bloom over ~500ms — neon-tube voltage, not editorial pop-in. Applied to B5Closing.tsx (`B5Closing` wordmark): `filter: brightness(${0.55→1.0}) drop-shadow(0 0 ${0→18}px rgba(0,229,255,0.35))` over frames 18-48. Replaces the prior Anthropic-style scale-pop spring on the wordmark. Reads as "live telemetry powering on" — semantically truer to our register than scale-pop.

2. **Whispered-not-shouted body copy** (PATTERN-082, second clause): Numerai holds body copy at ~70-75% gray (`#B8B8B8`) on true black. Pure-white-on-pure-black always feels louder than the content warrants. Applied to B5 URL line (`panopticon-live.vercel.app`): softened from `#F8FAFC` → `#B8B8B8` (still WCAG AAA contrast on `#05080F`). Hero wordmark stays bright (`#F8FAFC`) — it IS the logo and must be loud. Kicker / repo / attribution stay at `#5A6678` (already softer than Numerai's recommendation).

3. **Slow ~2-3% drift on cinematic plates** (PATTERN-084): Numerai applies a continuous slow zoom or lateral drift to every cinematic plate to keep the camera "alive" without Ken Burns aggression. Applied to:
   - B5Closing entire composition: `transform: scale(${1.0→1.02})` over 300 frames, anchored center-center.
   - GitGraph primitive: optional `driftDurationFrames` prop (default 660 = 11s @ 60fps), applies same drift to the SVG outer transform.

4. **Hard cuts only** (already convergent with Anthropic, PATTERN-078). 95%+ of Numerai's cuts are hard cuts. Crossfades not used. We're already aligned.

#### What we REJECT from Numerai (broadcast-HUD-incompatible)

| Numerai pattern | Why we reject |
|---|---|
| Single-family typography (Maven Pro Light / Source Sans 3 Light, no serif/sans pair) | We deliberately adopted Fraunces serif + JetBrains Mono pairing from Anthropic. The serif/sans pair IS our typographic differentiator. Going single-family loses both the editorial signature AND the broadcast register. |
| 2.39:1 cinematic letterbox on all plates | We need full 1080p vertical real estate for the HUD. Letterbox would consume 12% of the canvas where SignalBars + CoachPanel live. |
| Buried-lede branding (logo withheld until final 8 seconds) | Judges need clear PANOPTICON LIVE identification throughout — we have 3 minutes, not 2:04, and a competition narrative requires earlier brand placement. |
| CGI maximalism (chrome busts, glitch storms, vaporwave gradients) | Reads as 2017-crypto-bro. PANOPTICON's value is forensic clarity, not sensory chaos. Conflicts with the Detective Cut clinical tone. |
| Chromatic aberration / RGB-shift glitch frames | Try-hard digital aesthetics. Conflicts with the clinical-detective tone. |

#### What was CONSIDERED but REJECTED (with reasoning)

**Two-card closing formula** (Numerai's "sigil-monument plate → URL on void" hard cut): rejected per PATTERN-083. The structural magic of Numerai's two-card is the VISUAL REGISTER SWITCH between cinematic plate and typographic void. Our B5 has only ONE register (typographic void on cool slate). Splitting one register into two cards is just longer dwell time without the magic. We adopt the smaller surgical wins (ignition curve, whispered URL, slow drift) instead — these compose within ONE card and produce the Numerai feel without the additional composition file.

#### Architecture diagram (A5) — generated 2026-04-24 ~20:00 EST

Pipeline flowchart created via `mcp__claude_ai_Figma__generate_diagram` (Mermaid LR flowchart, Numerai-style register-switch from typographic to architectural register). FigJam location: `figma.com/board/1McYlYT0isbmTOJshc9ip9`. Edges: `ffmpeg → YOLO11m-Pose → Kalman → 3-Pass DAG → 7 Signal Extractors → DuckDB → Server Action → Opus 4.7 Scouting Committee → 2K-Sports HUD`, plus a dotted "trace replay" loopback from Opus to HUD. Saved to Andrew's team plan (`team::1606985436627625568`). Will be exported as PNG for a B5-architecture beat (or potentially a 4-frame Architecture register-switch card in DaVinci) Saturday morning.

### Tonight's accelerated build sprint (Andrew's 21:00 directive) — STATUS

Andrew explicitly reversed the "fresh eyes Saturday" plan: *"We are not going to wait to have fresh eyes tomorrow; we are going to work through tonight."*

1. ✅ Re-apply Fraunces serif to B0 title card (cyan + serif validation)
2. ✅ Build B5 closing card (Anthropic editorial layout + cyan palette)
3. ✅ Build SceneBreak primitive (between-beat hard-cut transitions, 3 instances B2/B3/B4)
4. ✅ Vimeo 205032211 deconstruction agent returns → synthesize learnings (this section)
5. ✅ A5 architecture diagram via `mcp__claude_ai_Figma__generate_diagram` (Mermaid → FigJam)
6. ✅ B5 ignition curve + slow-drift refit (Numerai DNA application)
7. ✅ GitGraph slow-drift overlay (Numerai DNA application)
8. ✅ Re-render full B0 + B5 + scene-breaks → DaVinci-ready assets (5 MP4s in `remotion/out/`, 3.2MB total)

Sprint complete. One thing at a time, polished, each step rendered + visually verifiable. Saturday morning surface area: DaVinci composite (cuts B-beats together with 3 SceneBreak transitions + B0 opener + B5 closer + dashboard OBS captures), architecture-diagram PNG export from Figma, recording the OBS captures on the Vercel prod URL.

---

## 5.5. Notion Narrative Directives — Path C Integration (LOCKED 2026-04-24 evening)

**Context**: after the v4 Detective Cut was locked earlier on 2026-04-24, Andrew surfaced a Notion-collected set of narrative ideas (Claude mascot as narrator, provocative opening question, typing-on-keyboard SFX, personal-journey arc, "everything is an API" rolling numbers, etc.). On 2026-04-24 evening Andrew confirmed **Path C = hybrid**: keep v4's structural spine (cold-open-on-anomaly, 1:58 climax, Detective Cut narrative arc) AND add Notion creative beats via Remotion chrome. Eliminate Andrew's voiceover entirely — replace with typing animations, on-screen text reveals, and mascot/facsimile motion. Execution principle (Andrew, verbatim): **"one thing at a time, exceptionally well polished — simple and clean execution at a really high level is better than complicated and hard to understand execution done mediocre."**

### 5.5.1 — The personal-journey opener premise (Andrew's core narrative directive)

> *"Prompt Claude to help us think, and go through our personal journey, showcasing prompting Claude to give insights and help and build to solve more problems until we inevitably get to the place in our journey where we build out the current project."*

**How this lands in the storyboard**: a NEW **B0 opener** beat (0:00 – 0:25) replacing nothing but shifting all subsequent beats later by 25 s. This MERGES what was Scene 2B "meta-build reveal" (gitgraph + Opus token counter per Iter-1 Agent B creative finding) into the opener itself — same creative impulse, now at the front.

**B0 shot list**:

| t (s) | Visual | On-screen text (no VO) |
|---|---|---|
| 0:00 | Black frame. Cursor blinks. | — |
| 0:02 | Typing-animation reveals one word at a time with subtle monospace kerning (JetBrains Mono), 0.5 s per word. SFX: single soft key-click per character (optional — muted by default, judge's volume decides). | `hey claude, is the world malleable?` |
| 0:07 | Pause. 1.5 s of silence + blinking cursor. | (cursor blinks) |
| 0:09 | Claude responds — typing back (distinct color/indent for the response). 25 chars/sec reveal. | `yes — build what you need` |
| 0:12 | Cut to a gitgraph timelapse (Remotion SVG animating dots along a timeline) of Andrew's commit history across prior projects — 5 brief anchor points, each a project name title-cased (e.g., "Czech Liga Explore → Kalshi Quant → Panopticon"). 2-3 s per anchor, total 12 s. Subtle Opus-token-counter in the corner increments as the timeline advances — shows cumulative Claude Code leverage. | (project names + dates + commit count) |
| 0:24 | Timeline lands on "PANOPTICON LIVE · April 2026". Brief hold. Seamless fade into B1 cold-open on anomaly. | `PANOPTICON LIVE` |

**Duration**: 25 s. **Structure**: hook (provocative question) → Claude response → journey montage → lands at present. **Information density**: high (shows the engineering + personal-narrative arc + Claude Code leverage WITHOUT voiceover). **Failure mode to avoid**: making it feel like a LinkedIn-influencer origin story. Keep it typographically sparse, monochrome, and FORENSIC in tone — no emotive zooms, no stock-inspirational music.

**Opening question — which to try first**: lead with *"hey claude, is the world malleable?"* because it's the most provocative + the most personally load-bearing (it's the philosophical question that actually motivated the project). Alternates to iterate on if it doesn't land: *"no problem is too hard to solve anymore. the question: is your solution big enough?"* OR *"everything is an api"* (this one goes with the rolling-numbers flicker instead of a philosophical prompt). Iterate visually, pick what lands.

### 5.5.2 — Voiceover eliminated; replaced by Remotion text overlays at v4 narration timestamps

The v4 §5 storyboard currently has 10 narration lines across B1-B5. In Path C, **every narration line becomes a Remotion text overlay** at the same timestamp. Overlay styling: mono, 14 px, bottom-third of frame (broadcast subtitle position), 400-ms fade-in + 600-ms hold + 400-ms fade-out. Overlay text is ~30 % shorter than the corresponding narration line (eye read-speed > listen-speed).

**Concrete v4-narration → overlay-text mapping** (first pass; refine during Saturday authoring):

| v4 narration | Path C overlay text |
|---|---|
| "Nobody on the broadcast called this. Our system flagged it at frame 1,359." | `flagged · frame 1,359 · σ 2.5 crouch-depth anomaly` |
| "YOLO11m-Pose on Apple Silicon. Kalman on court meters. Seven biomechanical signals..." | `YOLO11m-Pose · Kalman on court meters · 7 biomech signals` + list-reveal |
| "Built with Claude Code. Twelve skill packs. All extracted from 2D broadcast pixels." | `12 skill packs · 2D pixels → clinical telemetry` |
| "Recurring. Crouch depth minus 11.69 degrees. Again. Same signature, 13.8 seconds apart. Fatigue, not randomness." | `recurring · Δ −11.69° · 13.8 s apart · fatigue pattern locked` |
| "Opus 4.7. Adaptive thinking. System prompt cached." | `OPUS 4.7 · adaptive thinking · cached system prompt` |
| "Opus rejected its first hypothesis because the timing didn't fit the data." | `✗ serve-mechanics hypothesis rejected — crouch preceded toss by 8.2 s` |

### 5.5.3 — Claude mascot test-drive (non-committal — iterate first, decide later)

Andrew's directive (verbatim): *"I'm tempted to use the Claude mascot; however the other side of me is tempted to not use it because it is not our project and it's IP from Anthropics. Although this is the Anthropics hackathon, we need to be very careful and intelligent about how we would use the Claude mascot. But let's try it out and see how it looks first!"*

**Plan**: background research agent running now to locate the Anthropic brand-kit SVG + verify licensing status. Once verdict returns: render the B0 opener's Claude-response moment (0:09 – 0:12) TWO ways — with the mascot doing a subtle head-tilt / acknowledgment beat, and without (just text response). Visual compare. **Ship the mascot only if**: (a) licensing verdict is SAFE, (b) the mascot genuinely lands as in-culture, not gimmicky, (c) it doesn't dilute Panopticon's own visual identity. Fallback: Remotion-native geometric facsimile (rounded square + eyes) that echoes the mascot shape without using the IP.

### 5.5.4 — Runtime reconciliation (hard cap 3:00)

Current v4 total: 2:58 (2 s margin). B0 adds 25 s. Options:
- **Compress B2 Scene 2** (0:18 → 0:50, 32 s): Scene 2B meta-build reveal has been moved INTO B0 (they were redundant). Remaining B2 = "HUD snaps in + signal naming cadence + skill-pack flash." Can trim to ~15 s. Net: save 17 s.
- **Compress B5 The Instrument, At Scale** (2:30 → 2:58, 28 s): architecture slide + Managed Agents fan-out + closing card. Can trim to ~20 s. Net: save 8 s.
- **Combined savings**: ~25 s → exactly offsets B0. New total: 2:58 (same).

New timeline:
```
B0 NEW   0:00 – 0:25   personal-journey opener (typing + gitgraph + token counter)
B1       0:25 – 0:43   cold-open on anomaly at t=45.3 s  (shifted +25s)
B2       0:43 – 1:00   HUD snap-in + skill-pack flash    (compressed -15s)
B3       1:00 – 1:40   second miss + slow-mo + firehose  (same length)
B4       1:40 – 2:40   Opus Reads the Body (climax)      (same length)
B5       2:40 – 2:58   architecture + Managed Agents + closing  (compressed -10s)
```

**v4 protected invariant**: B4's 1:58 climax frame (left-pane anomaly + right-pane thinking + cache indicator + Rejected Thought chip) is UNTOUCHED by Path C — it remains the single lean-forward moment.

### 5.5.5 — What this changes elsewhere in PLAN.md

- **§6 add-ons**: A1/A2a/A7 already shipped Friday evening. NEW **A10 "Claude mascot test-drive"** (0.5 h, stretch) + **A11 "Remotion text-overlay narration"** (1.5 h, replaces the deleted voice-over recording block). ADD to §6 priority table.
- **§9 Asset Registry**: narration WAV rows (`audio/narration_final.wav`, `audio/elevenlabs_*.wav`) become obsolete. Replace with `remotion/overlays/narration_overlays.tsx` (text-overlay component, not audio).
- **§10 Timeline**:
  - Saturday 15:00 "Narration script draft" → **REPURPOSED** to "Overlay copy draft + polish" (same time budget, different artifact).
  - Saturday 17:00-18:00 "OBS take 1 silent" + 20:00 "OBS take 2 with audio" → **BOTH COLLAPSE to a single OBS silent take** (B1-B5 dashboard capture only; all chrome + overlays are Remotion, composited in DaVinci Sunday). **Saves ~2 h of Saturday**.
  - Friday TONIGHT addition: **B0 opener prototype** (one-thing-at-a-time: typing primitive → gitgraph → token counter → mascot test).
- **§12 Fallback plans**: MacBook-mic roomy-audio risk + ElevenLabs fallback become N/A (no voiceover). Remotion render-failure fallback escalates in importance — ffmpeg `drawtext` becomes the primary fallback for text overlays, not Remotion chrome.
- **CLAUDE.md (demo-presentation/)**: §3.3 Narration rules + §6 Recording discipline → need update on 2026-04-25 morning to reflect zero-voiceover production pipeline. Flagged, not yet edited (scope-separation).

### 5.5.6 — Serial build discipline (Andrew's "one thing at a time" rule)

Every Remotion composition is built + validated + polished in sequence. No parallel "build A+B+C simultaneously." Order for Friday evening:

1. Typing-animation primitive (character-by-character reveal, 60 fps, Remotion `<Series>` or frame-driven). Validate: the question renders cleanly at 30 Hz composition frame rate.
2. Gitgraph timelapse primitive. Validate: 5 anchor-project transitions look like a clean Palantir dashboard timeline, not a Mapbox route.
3. Opus token-counter primitive. Validate: counter reads as "proof of actual usage," not as "stock-ticker chrome."
4. B0 composed scene (all three primitives stitched). Validate end-to-end: 25 s renders to MP4, opens in QuickTime, lands emotionally.
5. THEN decide on mascot (only after 1-4 are solid).

Polish bar: every primitive must render at 60 fps without drops, kern cleanly at 1080p, and be scrubbable frame-by-frame in Remotion preview without stutter.

---

## 6. Approved Saturday add-ons (code-freeze exceptions)

**Priority order** (top = highest ROI per hour). All time-boxed; if budget exceeded, fall back per row.

| # | Add-on | Priority | Budget | Fallback if over |
|---|---|---|---|---|
| A1 | Live tickertape bar at Tab 1 bottom (phase-weighted per Q5) | **High** | 1 h | Skip — storyboard works without |
| A5 | Architecture diagram (B5) — Canva | **High** | 1 h | Hand-drawn Canva slide |
| A6 | Remotion chrome — closing card + scene-break transitions (B5C) | **High** | 1.5 h | ffmpeg `drawtext` + Canva PNG exports |
| **A7** | **Vision pass capability showcase (B1 overlay)** — one precomputed Opus 4.7 vision call on t=45.3 s broadcast frame, rendered as B1 crosshair/annotation overlay | **High** (Q10) | 1 h | Skip — ship with skeleton-only crosshair |
| **A8** | **`<ThinkingVault>` component + unfilter `actions.ts:145`** — 3-column `[Considered] / [Rejected] / [Concluded]` UI for B4 split-screen climax | **High** (Q10) | 2 h | Fallback: simpler 2-pane thinking-block reveal (1 h) without 3-column structure |
| **A2a** | **Video `playbackRate` slow-mo at anomaly timestamps (B3)** — low-risk, HTMLVideoElement API, no canvas math | **High** (Q11 low-risk slice) | 30 min | Skip — B3 works with SignalBar pulse alone |
| A4 | Managed Agents future-vision fan-out (B5, compressed to ≤15 s still/fade per Q9) | **Medium** | 30 min (was 1.5 h — animated version cut) | Static Canva PNG fade-in |
| **A9** | **Submission dry-runs (Sat 14:00 YouTube + 17:00 CV form)** | **High** (Q12 non-negotiable) | 1 h total | None — required |
| A2b | Sportradar geometric annotation (angle wedge + velocity arrow + labels) | **Stretch only — dedicated slot** (Q11 high-risk per Andrew's rule) | 4 h | Ship without. Only build if everything else green AND ≥ 3 h remaining AND we allocate undivided attention |
| ~~A3~~ | ~~Opus Dreams interstitial~~ | **CUT** | — | Dropped — too theatrical for engineering judges |

**Realistic Saturday build plan** (locked after Iter 1-4 decisions):
- **Core (must ship)**: A1 + A5 + A6 + A7 + A8 + A2a + A4 + A9 = ~7.5 h
- **Stretch (only if everything else green)**: A2b = 4 h with dedicated resources
- **Sunday morning buffer**: 2-3 h for rough-cut fixes + A2b if core landed ahead of schedule

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

### Friday 2026-04-24 (TONIGHT — pre-flight)

| Time | Block | Deliverable |
|---|---|---|
| 22:00 | **Remotion pre-warm**: `bunx create-video@latest` + render Hello World → pre-downloads Chrome Headless Shell (~280 MB) and surfaces Rosetta2 traps BEFORE Saturday's deadline pressure (per Iter-1 Agent A) | Hello World MP4 rendered |
| 22:30 | **Arm64 audit**: `node -p process.arch` MUST return `"arm64"` (Rosetta2 2× slowdown trap). `npx remotion versions` to pre-fetch Chromium. | Env verified |
| 22:45 | **Git-log extraction for Scene 2B gitgraph**: `git log --since="2026-04-21" --pretty=format:'%H|%ai|%s' > demo-presentation/assets/git_timeline.txt` | File saved |
| 23:00 | Sleep. | — |

### Saturday 2026-04-25 — REVISED ROADMAP (per DECISION-020 + USER-CORRECTION-037)

> **What changed**: tonight's pre-dawn sprint (2026-04-24 evening → 2026-04-25 ~04:30) shipped A1 tickertape, A5 architecture diagram (in FigJam), A7 vision pass, Q1 Download CSV button, Q2 B5Thesis composition, prod deploy with Lighthouse 100/100/100, narration overlay script, submission summary draft. Andrew's USER-CORRECTION-037 reset the quality bar: tonight's Remotion outputs are TOY-TIER and need Anthropic-release-video-quality rebuild before recording. New Saturday plan reflects the rebuild + recording sequence.

| Time | Block | Deliverable |
|---|---|---|
| **MORNING — Remotion Tier 1 World-Class Overhaul (claude executes; ~5 hours)** | | |
| 08:00 | Andrew wakes; Claude resumes from compact; `/skill-create remotion-cinematic-craft` activates the new skill | Skill loaded into context |
| 08:15 | **Reference study**: rewatch Anthropic Opus 4.6 release video (`dPn3GBI8lII`) for 3 min; cross-reference `assets/references/anthropic_video_dna.md` motion-density notes | Visual vocabulary calibrated |
| 08:30 | **Build B0OpenerV2** — 30-45s, 4 internal beats (silent cursor → typed dialog → response → fade-out → git timeline w/ parallax → chapter card), music bed, kerning sweep on hero, italic-reveal on accent. Audit against remotion-cinematic-craft 6-failure-modes checklist. | `B0OpenerV2.tsx` + render + checklist pass |
| 11:00 | **Build B5ClosingV2 + B5ThesisV2 (bookend pair)** — 12-18s + 8-10s respectively, multi-element frames, weight modulation, kerning sweep, ambient drift. Same chapter-marker treatment as B0V2. | Bookend pair rendered + checklist pass |
| **AFTERNOON — Andrew OBS Recording (Andrew leads; Claude assists by being on-call for any UX issues)** | | |
| 13:00 | **A9a YouTube DRY RUN**: upload throwaway 30-s tennis clip, check Restrictions pane for Content ID flags (Iter-4 critical) | Channel verified |
| 13:30 | **A9b CV submission DRY RUN**: load form in browser, screenshot every field, DO NOT submit | Form fields captured |
| 14:00 | **OBS take 1** — record the 4 dashboard captures from `davinci_composite_workflow.md` Phase 1: `obs_b1_anomaly`, `obs_b2_huddrop`, `obs_b3_secondmiss_tab2`, `obs_b4_scouting`. Silent (audio bed in DaVinci). 1920×1080 @ 60fps. | 4 take-1 OBS files in `~/Movies/panopticon_obs_takes/` |
| 16:00 | **Andrew checkpoint**: review take 1 captures with Claude. If any look off (jitter, timing, mis-trigger), retake those specific scenes. | Take 1 acceptance OR specific retake list |
| 16:30 | **OBS take 2** (only IF take 1 had issues) — re-record problem captures | Final OBS files locked |
| **EVENING — DaVinci Composite (Andrew + Claude pairing)** | | |
| 17:30 | Andrew opens DaVinci Resolve following `davinci_composite_workflow.md`. Claude available for real-time consultation on text-overlay timing, transitions, color choices. | Project setup + asset import |
| 18:00 | Timeline assembly per workflow doc. Drop the 4 OBS captures + 6 Remotion MP4s (the V2 versions from morning) in order. | Rough cut on timeline |
| 19:00 | Dinner + review (45 min break) | — |
| 19:45 | Text overlays via Fusion macro (7 overlays from `narration_overlays.md`). Iterate timing during scrub. | Overlays in place |
| 21:00 | First full-cut export at lower quality (preview only). Watch end-to-end. | `renders/preview_v1.mp4` |
| 21:30 | End-of-Saturday log roll — update MEMORY.md / FORANDREW.md / TOOLS_IMPACT.md with Saturday learnings | Living docs current |
| 22:00 | **A2b decision gate (REVISED)**: IF rough cut feels World-Class → save and sleep. IF cuts feel weak (motion graphics overlay missing on OBS captures, tier-2 work needed) → carve Sunday morning slot for OBS-overlay templates. | Decision locked |

> **Saturday morning Remotion overhaul superseded the original §10 Saturday plan** (A1/A5/A7/A8 etc were completed pre-dawn during the night-of-04-24 sprint). The original schedule below this line is preserved for historical reference / audit trail but should not be executed.

### Saturday 2026-04-25 — ORIGINAL PLAN (SUPERSEDED — DO NOT EXECUTE; preserved for audit)

| Time | Block | Deliverable |
|---|---|---|
| 08:00 | Coffee + re-read §5 (Detective Cut) + §6 priority table | Plan mental model refreshed |
| 08:30 | `git checkout -b demo-v1`. Verify Vercel prod deploy green. `vercel env ls` → ANTHROPIC_API_KEY present in Production (Iter-4 check). Smoke-test `generateScoutingReport` in prod (not just page render). | Dev env + prod verified |
| 09:00 | **A1 tickertape** (phase-weighted signal order per Q5) | `dashboard/src/components/Tickertape.tsx` |
| 10:00 | **A5 architecture diagram** (Canva) — "Built with Claude Code · 5 days · MIT" overlay | `assets/diagrams/architecture.png` |
| 10:30 | **A7 Vision pass (B1 overlay)** — one precomputed Opus 4.7 vision call on t=45.3 s broadcast frame, store annotation JSON | `public/match_data/vision_pass.json` |
| 11:30 | **A8 Thinking Vault (unfilter `actions.ts:145` + build `<ThinkingVault>` component)** — persist `{thinking, text, content_blocks}` response shape; 3-column UI | `dashboard/src/app/actions.ts` + `dashboard/src/components/ThinkingVault.tsx` |
| **13:30** | **Lunch (30 min)** | — |
| 14:00 | **A6 Remotion chrome** — closing URL card + scene-break transitions. Use `@remotion/mcp` for API lookup. | `remotion/ClosingCard.tsx` rendering |
| 15:00 | **A2a slow-mo** (30 min, low-risk) — `<video>`.`playbackRate` animates to 0.25× at anomaly timestamps | Video-element ref wired |
| 15:30 | **A4 Managed Agents fan-out** (≤ 15 s still/fade, compressed per Q9) — Canva PNG preferred, Remotion optional | `assets/diagrams/managed_agents_fanout.png` |
| **16:00** | **A9a DRY RUN — YouTube**: upload throwaway 30-s tennis clip, check Studio → Content → Restrictions pane for Content ID flags (Iter-4 critical; tennis footage triggers auto-mute + 13 % geo-block). If muted/blocked, plan alternate audio. | Channel verified, Content ID clean |
| **16:30** | **A9b DRY RUN — CV submission form**: load `cerebralvalley.ai/e/built-with-4-7-hackathon` submission form in browser, screenshot EVERY field. DO NOT submit. | Field list captured |
| 17:00 | Narration script draft — §5 B1-B5 audio columns → full prose, 10 lines total, technical-clinical | `scripts/narration.md` v1 |
| 18:00 | **OBS take 1 — silent, 2 × 90-s segments** (Iter-1 dual-take mitigation for Sequoia 20-30 min freeze). QuickTime parallel as zero-cost backup. | `renders/raw/take_1a.mp4`, `take_1b.mp4` |
| 19:00 | Dinner + review | Feedback |
| 20:00 | **OBS take 2 with audio — 2 × 90-s segments** via MacBook mic | `renders/raw/take_2a.mp4`, `take_2b.mp4` |
| 21:30 | End-of-Saturday log roll — update MEMORY.md / FORANDREW.md / TOOLS_IMPACT.md via `documentation-librarian` agent | Living docs current |
| 22:00 | **A2b decision gate**: IF all core items green AND ≥ 3 h Sunday buffer likely → allocate UNDIVIDED resources to A2b geometric annotation overlay. ELSE: skip. | A2b decision locked |

### Sunday 2026-04-26 (submission day)

| Time | Block | Deliverable |
|---|---|---|
| 08:00 | Review Saturday takes; select master | Master take locked |
| 09:00 | **Third take (final intent)** if Saturday's takes don't meet bar | `renders/raw/take_3.mp4` (optional) |
| 10:00 | DaVinci rough-cut assembly: master take + Remotion chrome + A4 fade + narration audio | `renders/panopticon_live_rough.mp4` |
| **12:00** | **Upload video UNLISTED to YouTube** (3 h ahead of plan per Iter-4 — processing + Content ID check). | YouTube upload ID |
| 12:15 | Check YouTube Studio → Content → Restrictions. If flagged: re-export alternate audio, re-upload. | Flags reviewed |
| 12:30 | Final cut refinement: color grade, audio mix, fades | Near-final |
| 13:30 | H.264 export at 1920×1080 @ 60 fps, CRF 18, AAC 320 kbps. QA: play full video 3 times. | `renders/panopticon_live_final.mp4` |
| **14:30** | **Flip YouTube Unlisted → Public**. Verify playback in incognito + phone (tests geo-block). | Public URL live |
| 15:00 | Write `scripts/submission_summary.md` — **lead with data moat** per Iter-4 (7 signals nobody else measures) | Summary drafted |
| 15:30 | GitHub repo SEO: description "Biometric tennis HUD powered by Claude Opus 4.7", topics tags (`claude-opus`, `computer-vision`, `tennis`, `anthropic-hackathon`), pinned README hero GIF | Repo updated |
| **16:00** | **HARD DEPLOY FREEZE**. No more Vercel deploys after this. | Freeze begins |
| 16:30 | Final `vercel deploy --prod --yes` + `vercel curl` HTTP 200 + smoke-test ALL Server Actions in prod | Prod verified |
| **17:00** | **SOFT SUBMIT via CV platform**. Immediately screenshot confirmation email. | Submission received |
| 17:30 | **Second submission attempt from different browser/incognito** to confirm edit-ability / lockout | Submission state confirmed |
| 18:00 | Dinner | — |
| 19:00 | Confirmation screenshot → `FORANDREW.md` + commit | Artifact logged |
| **19:55** | **LOCKOUT** — do NOT touch submission after this | Final |
| **20:00** | **DEADLINE** | ✅ |
| 20:15 | **Amplification #1**: X thread-launch (6 tweets, tags `@AnthropicAI @alexalbert__ @CerebralValley @erikschluntz #BuiltWithClaude`) | Thread live |
| 21:00 | **Amplification #2**: 47builders.fyi self-listing with banner + YouTube embed + data-moat blurb | Listing live |

### Monday 2026-04-27 (pre-judging)

| Time | Block |
|---|---|
| 08:00 | **Amplification #3**: Discord `#BuiltWithClaude` post + GIF loop + DevRel DM (Alex Albert OR Erik Schluntz) |
| 10:00 | Cerebral Valley builder profile updated with project + repo |
| Tue 12:00 EST | Top-6 finalists announced (`#announcements`) |
| Tue 12:45 EST | Top-3 + side-prize winners revealed |

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
- [ ] **GitHub SEO** (Iter-4): description leads with "Biometric tennis HUD powered by Claude Opus 4.7"; topics tags `claude-opus`, `computer-vision`, `tennis`, `anthropic-hackathon`; pinned README hero GIF
- [ ] Written summary 100-200 words — draft + reviewed; **LEAD with data moat** per Iter-4 ("Panopticon Live extracts seven biomechanical fatigue signals — recovery latency, serve-toss variance, ritual entropy, crouch degradation, baseline retreat, lateral work rate, split-step latency — from standard 2D broadcast pixels that nobody else is measuring.")
- [ ] CV submission form fields: video URL, GitHub URL, written summary all pasted
- [ ] Screenshot of submission confirmation captured
- [ ] Second submission attempt from incognito browser (confirms edit-ability / lockout state)
- [ ] **Post-submit amplification tracking**:
  - [ ] Sun 20:15 — X thread (6 tweets, tags `@AnthropicAI @alexalbert__ @CerebralValley @erikschluntz #BuiltWithClaude`)
  - [ ] Sun 21:00 — 47builders.fyi self-listing (banner + YouTube embed + data-moat blurb)
  - [ ] Mon 08:00 — Discord `#BuiltWithClaude` post + DevRel DM
  - [ ] Mon 10:00 — Cerebral Valley builder profile updated
- [ ] `FORANDREW.md` updated with submission event
- [ ] Final commit + push

---

## 12. Fallback plans

| Scenario | Fallback | Trigger |
|---|---|---|
| Remotion won't render Sat 14:00 | ffmpeg `drawtext` + Canva PNG exports for closing card | 1.5 h into Remotion chrome without a working render |
| OBS drops frames / Sequoia 20-30 min freeze (Iter-1) | **Dual 90-s takes + QuickTime parallel backup** (Iter-1 mitigation). ScreenCaptureKit Window Capture, not full Screen. | > 5 % frame drop OR any freeze mid-take |
| MacBook mic audio too roomy / noisy | ElevenLabs narration (Sat PM fallback) | Rehearsal take reveals unlistenable audio |
| Vercel prod deploy breaks Sun AM | Submit preview URL (`panopticon-live-1fqx9c4iz-dmg-decisions.vercel.app`) + open prod-fix PR | Build failure at deploy time |
| **Vercel April 2026 security incident rotated ANTHROPIC_API_KEY in Production** (Iter-4 critical) | Re-add via PATTERN-056 incantation: `vercel env add ANTHROPIC_API_KEY production "" --value "..." --yes --sensitive` | `generateScoutingReport` returns 401 in prod (but preview works) |
| Opus API 401 Sun AM | Re-verify key via curl + rotate if needed | Any 401 in `vercel logs` |
| **YouTube Content ID flags tennis footage** (Iter-4 — ~13 % geo-block rate on sports) | Re-export video with silent audio OR different clip; re-upload | Studio → Content → Restrictions pane shows flags |
| **YouTube HD processing lock leaves video at 360p** (Iter-4) | Wait the full 20-60 min; verify 1080p quality in incognito before submitting URL | Public URL plays at 360p when tested |
| **New-channel YouTube upload cap** | Complete phone verification BEFORE Sat 14:00 dry run | Upload blocked at 15-min cap |
| **CV submission form rejects, post-submit edit unavailable** | Discord `#questions` channel + email moderators; also submit backup via any alternate channel CV provides | Form submit fails OR confirmation email doesn't arrive within 15 min |
| A2b geometric annotation math is wrong | Ship with A2a slow-mo only (no annotation overlay). A2b is stretch-only per Q11; has zero demo-critical dependency. | Sat 20:00 gate: A2b not working with ≥ 2 h clean-rendering time |
| Time pressure: no final render by Sun 16:00 | Submit rough cut with brief apology in summary; iterate to v2 if final-round live-judging advances | 16:00 Sun without final render |
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
