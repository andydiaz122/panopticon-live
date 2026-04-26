# Sunday Execution Plan — Submission Day (2026-04-26)

**Authored:** 2026-04-25 ~23:30 EDT (overnight, while Andrew sleeps)
**Submission deadline:** Sunday 2026-04-26 @ **20:00 EDT** (8 PM)
**Hard lockout (do NOT submit after):** **19:55 EDT** (7:55 PM)
**Soft target (recommended submission window):** **17:00 EDT** (5 PM) — gives 3 hours of buffer

---

## ⚡ THE FIRST 15 MINUTES OF YOUR DAY (do these in order)

1. **Coffee.** Don't skip.
2. **Read `docs/RECORDING_LAG_RECIPE.md`** (in repo) — the overnight agent's findings on the OBS lag investigation. **TL;DR: GOOD NEWS** — OBS was the amplifier of a real React perf bug. Use macOS QuickTime via `Cmd+Shift+5` instead of OBS; re-enable the slow-mo + coach pauses you loved; re-record Tab 1 with the explosive pacing back. Agent could NOT pre-produce the clean recording (chrome-devtools-mcp screencast was flag-gated), so this is your first concrete morning task.
3. **Open `CAPCUT_TUTORIAL.html`** (project root) in your browser. Skim — don't deeply read. ~5 min.
4. **Open this document on a second monitor** (or print it). Reference throughout the day.
5. **Open CapCut** with the project from last night.

You should now be in execution mode by ~07:30 EDT.

## 🎬 NEW FIRST TASK (UPDATED 2026-04-26 ~04:30 EDT after team-lead review)

**Re-record Tab 1 with pauses RE-ENABLED + QuickTime against LOCALHOST.** ~30 minutes. This unlocks the "explosive" demo you loved.

> **Team-lead VETO on Vercel deploy.** Do NOT deploy to production on submission day. Pixels are 100% identical between localhost dev server and Vercel CDN as far as QuickTime is concerned. Your stable Vercel deployment stays untouched; deployment risk = zero.

**Source code is already uncommented for you** (Claude did this overnight after team-lead review). Just run dev server + record:

1. Open terminal: `cd /Users/andrew/Documents/Coding/hackathon-research/dashboard && bun run dev`
2. Wait for "ready in Xms" message (~3 seconds). Dev server is at `http://localhost:3000`
3. Open Chrome, navigate to `http://localhost:3000`. Hit **Cmd+Ctrl+F** to full-screen the window (hides URL bar — recording surface is clean)
4. Open QuickTime alternative: **Cmd+Shift+5** → click "**Record Selected Portion**" → drag selection box around your Chrome window's video area (the dashboard, not the browser chrome)
5. Do a **10-second test recording first** — hit play on the dashboard video, let it run for 10s, stop QuickTime (click the recording icon in menu bar), watch back. **Confirm: NO lag, NO replay glitches, smooth slow-mo at anomaly moments around 35.9s, coach panel pauses for typewriter.**
6. If clean → record FULL ~150s take (the with-pauses version is longer because of slow-mo + 7 typewriter pauses, ~150s expected wall-clock). Save to `~/Documents/Panopticon_Captures/full_tab1_with_pauses_v2_QUICKTIME.mov`
7. Import to CapCut. You now have THREE versions in your bin:
   - `full_tab1_run_NO_pauses.mov` (clean playback, fallback)
   - `full_tab1_run_v1_with_pauses.mov` (Saturday OBS recording with the lag baked in — DO NOT USE)
   - `full_tab1_with_pauses_v2_QUICKTIME.mov` (NEW — clean explosive version) ← use this one

If QuickTime recording STILL has lag (unexpected per `docs/RECORDING_LAG_RECIPE.md`), fall back to `full_tab1_run_NO_pauses.mov`. Don't burn more than 30 minutes on this.

**When done with the recording, kill the dev server (`Ctrl+C` in the terminal). You're done with localhost — the rest of Sunday is CapCut work.**

---

## 🎙️ Communication Strategy (UPDATED — replaces voice-over directive)

> **Andrew override 2026-04-26 ~04:00 EDT**: skip voice-over entirely. Communicate to the audience by TYPING messages on a black background — same aesthetic as the intro typing. One unified communication device throughout the demo = professional + on-brand.

**Where typed-interludes land in the timeline** (each ~3s, total ~10s of communication):

| Time | Interlude text | Style |
|---|---|---|
| 0:00-0:22 | (Already exists: 4-stage intro typing in claude.ai UI) | Full Claude UI |
| ~0:30 | "Now: live HUD over broadcast" | Black bg, white text, typewriter |
| ~1:30 | "The dashboard is just the showcase" | Black bg, white text, typewriter |
| ~1:58 | "The final product: the raw telemetry" | Black bg, white text, typewriter |
| 2:43-2:55 | (Already exists: closing card "capture the signal nobody else is reading") | Black bg, white serif |

**Specs for the 3 NEW interludes** (build in CapCut as text overlays, NOT separate QuickTime takes — saves 30 minutes):

- Background: pure black (`#000000`)
- Text: white (`#F8FAFC`)
- Font: **JetBrains Mono Regular** (matches Claude UI typing aesthetic) OR **Fraunces Italic** (matches closing card register — pick one and stay consistent)
- Size: 36-48pt
- Position: dead center
- Animation: typewriter reveal at ~25 cps (CapCut's "Typewriter" preset)
- Cursor: blinking underscore at end (CapCut text presets often include this)
- Duration: 3 seconds total (text appears in ~2s, holds for 1s, hard cut to next clip)
- NO Claude UI shell — that's reserved for the opener; reuse would dilute the effect

**Why this works** (first-principles): one communication device used consistently throughout = "deeply intentional" reading. Mixed devices = "ad-hoc" reading. Judges associate intentionality with shipped products.

---

## Hour-by-Hour Schedule (CONSERVATIVE — heavy buffer in the back half)

### Block 1: 07:30 – 09:30 EDT — Decision + Restructure (2h)

The current scaffold is the linear-walkthrough cut. Your vision (countdown → serve apex → walkthrough) is a different structure. Decide which to ship:

| Path | Effort | Risk | When to choose |
|---|---|---|---|
| **A. Polish the linear cut** | LOW (~2h) | LOW | If you woke up tired or want to ship safely |
| **B. Implement your countdown vision** | HIGH (~4h) | MEDIUM | If you woke up energized and the vision still feels right |
| **C. Hybrid** — keep current scaffold, replace ONLY the opener with countdown-3-2-1-flicker-then-serve-apex | MEDIUM (~3h) | LOW-MEDIUM | **RECOMMENDED** — gets you 80% of the energy with 50% of the risk |

**Decision criteria** (90 seconds):
- Does the linear cut, on playback, feel like a 3-minute Anthropic release video? If YES → Path A. If NO → Path B or C.
- Did the overnight agent produce a clean "with-pauses" recording? If YES, that re-enables the explosive pacing you loved. Use it.

**By 09:30 EDT** you should have: a chosen path, a v0 timeline of the new opener (countdown + serve apex), and the rest of the demo intact downstream.

### Block 2: 09:30 – 12:30 EDT — Core Assembly (3h)

Execute on chosen path. Reference `CAPCUT_TUTORIAL.html` for any operation you're unsure about. This is the longest block — pace yourself, take a 10-min break at 11:00.

**Path-specific milestones:**

**If A (linear polish):**
- 09:30-10:30: Re-time visual track to land each beat at the storyboard milestone (0:30 dashboard reveal, 1:50 Tab 2 reveal, 2:15 Tab 3 reveal, 2:48 closing)
- 10:30-11:30: Music keyframe swells at editorial pivot points (per capcut_assembly_workflow.md Step 2 NEW)
- 11:30-12:30: Add 1-2 text overlay punches at the strongest moments (e.g., "7 Biomechanical Signals" overlay during Tab 1, "Built in 5 Days with Claude Code" overlay near close)

**If B (full countdown vision):**
- 09:30-11:00: Build the countdown 3-2-1 opener (text overlays, scale/opacity animations, optional Claude UI flicker via brief intro_typing crops)
- 11:00-11:30: Hard cut to serve apex (pre-scrub Tab 1 footage to ~17-19s where serve motion peaks); play out the point through the leave at ~37s
- 11:30-12:30: Walkthrough block (Tab 1 HUD highlights → Tab 2 CSV download → Tab 3 swarm reveal)

**If C (hybrid — RECOMMENDED):**
- 09:30-10:30: Build countdown 3-2-1 opener (10-15 seconds total)
- 10:30-11:00: Hard cut to serve apex moment (5-8 seconds of explosive motion)
- 11:00-12:30: Existing walkthrough scaffold (pre-built last night) but tightened

### Block 3: 12:30 – 13:30 EDT — Lunch + First Export (1h)

- Eat. Stand up. Look at non-screen things for 15 minutes. **Mandatory.**
- 13:00: First export at 1080p/60fps H.264. Watch it FULL-screen, no scrubbing, no taking notes. Just experience it.
- Note 3-5 things that need fixing. Don't try to fix them yet.

### Block 4: 13:30 – 15:30 EDT — Polish Pass (2h)

The "final 20%" you were worried about. Common polish operations:
- Tighten any cut that drags (trim 1-2s off long-feeling clips)
- Smooth any cut that jolts (add 0.3s cross-fade on jarring tab-transitions)
- Adjust music level if VO-less audio mix feels too quiet/loud
- Verify the closing card (`card_03_closing.png`) holds for full 12 seconds with music swell
- Color-grade pass: CapCut's "Cinematic" filter at 15% on OBS captures (skip if cyan looks off)

**Hard rule:** at 15:30, STOP polishing. Diminishing returns kick in hard after 2 hours of polish. The next 30% of "feel-better" takes 3+ hours.

### Block 5: 15:30 – 16:30 EDT — Final Export + QA Audit (1h)

- 15:30: Export final cut as `panopticon_live_demo_v1_FINAL_2026-04-26.mp4` to `~/Documents/Panopticon_Final/`
- 15:45: Open in QuickTime, watch end-to-end ONCE without scrubbing. QA audit:
  - [ ] Total runtime is 3:00 ± 1 second
  - [ ] No black flashes between cuts
  - [ ] Audio levels never clip (peak < -3 dBFS)
  - [ ] Cyan reads as cyan (`#00E5FF`), not blue
  - [ ] Closing card hold is 12 seconds, music decays cleanly
  - [ ] No accidental browser chrome / toolbar visible in OBS captures
  - [ ] First frame is intentional (not a black frame)
  - [ ] Last frame is the closing card or 1s of black
- If anything fails: fix + re-export. Build in time for ONE re-export.

### Block 6: 16:30 – 17:30 EDT — YouTube Upload + Unlisted Publish (1h)

- 16:30: Sign in to `studio.youtube.com`
- 16:35: Upload `panopticon_live_demo_v1_FINAL_2026-04-26.mp4`
- Title: `PANOPTICON LIVE — Biomechanical Intelligence for Pro Tennis | Built with Opus 4.7 Hackathon`
- Description: paste from `demo-presentation/scripts/submission_summary.md` (or compose if missing)
- **Visibility: UNLISTED** for now (DO NOT publish public until you've verified HD playback)
- Custom thumbnail: 1280×720 PNG, frame from Tab 1 HUD looking dramatic
- Tags: `claude opus 4.7, anthropic, hackathon, tennis, biomechanics, computer vision, sports analytics, cerebral valley`
- Click Publish (Unlisted)
- Note the YouTube URL

### Block 7: 17:30 – 18:30 EDT — HD Process Wait + Public Switch (1h)

- 17:30: Wait for YouTube to finish HD processing. Usually 5-15 min for a 3-min 1080p video.
- Watch the URL — the HD indicator (1080p in quality menu) confirms processing complete.
- 18:00: Switch visibility from Unlisted to **Public**.
- Copy Public URL.

### Block 8: 18:30 – 19:00 EDT — CV Submission (30 min)

- 18:30: Open the Cerebral Valley submission portal (URL from confirmation email)
- Project name: **PANOPTICON LIVE**
- YouTube URL: paste (must be Public)
- GitHub URL: `https://github.com/andydiaz122/panopticon-live`
- Written summary: paste from `demo-presentation/scripts/submission_summary.md` (100-200 word variant)
- **Click submit.**
- **Screenshot the confirmation page for paranoia.**

### Block 9: 19:00 – 19:55 EDT — Buffer (55 min)

- If you're done at 19:00: rest, congratulate yourself, screenshot more things for posterity.
- If you hit issues: this is your safety margin. Use it surgically — fix the ONE blocking issue, re-submit.
- **DO NOT make changes after 19:55. Hard lockout.**

---

## What if you fall behind?

Use this fallback hierarchy:

| If you're behind by | Cut this | Don't cut |
|---|---|---|
| 30 min | The optional second polish iteration (Block 4 second hour) | Anything else |
| 1 hour | Color-grade pass + text overlays in Block 4 | Core assembly |
| 2 hours | The countdown opener (default to scaffold + minimal opener trim) | Core walkthrough |
| 3 hours | Path B/C — fall back to Path A (linear polish only) | Submission itself |

**The submission itself is non-negotiable.** Even an unpolished video submitted at 17:00 beats a polished video that misses the lockout at 19:55.

---

## Critical files for Sunday reference

| File | Purpose |
|---|---|
| `CAPCUT_TUTORIAL.html` | Project root — open in browser. ALL the CapCut operations you need. |
| `OVERNIGHT_REPORT.md` | Project root (or `/tmp/obs_overnight_agent_report.md`) — what the overnight agent produced |
| `demo-presentation/scripts/capcut_assembly_workflow.md` | Step-by-step assembly reference (already updated for music-only audio) |
| `demo-presentation/scripts/title_card_specs.md` | Closing card spec (Card 3) |
| `demo-presentation/scripts/intro_typing_script.md` | The original intro typing capture spec |
| `~/Documents/Panopticon_Captures/` | All raw video assets |
| `~/Documents/Panopticon_TitleCards/card_03_closing.png` | The closing card |

---

## Mantras for tomorrow

- **Done > perfect.** Anthropic's Chrome demo isn't perfect either; it's just shipped at the right level.
- **Trust the scaffold.** You built it last night. It works. Polish, don't rebuild.
- **One thing at a time.** Andrew's micro-sprint discipline applies to CapCut polish too — don't try to fix 3 things in one pass.
- **Music carries the silence.** Without VO, every breath in the visual track is the music doing the work. Trust it.
- **5 days. 7 signals. Apple Silicon.** If you can land those 3 facts visibly in the demo (text overlays, closing card, etc.), the value prop is communicated.

---

**Sleep well. The overnight agent + tutorial + this schedule will be waiting when you wake up.**
