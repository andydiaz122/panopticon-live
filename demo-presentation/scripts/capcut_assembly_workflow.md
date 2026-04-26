# CapCut Assembly Workflow — PANOPTICON LIVE Demo (Anthropic Minimalism Pivot)

**Authored:** 2026-04-25 ~06:00 EDT.

> ⚠️ **AUDIO PIVOT 2026-04-25 ~20:41 EDT** — Andrew made the executive decision
> to SHIP WITHOUT VOICE-OVER for v1 (<24h to deadline). Music bed is now the
> primary audio + carries the editorial through-line. Voice is DEFERRED to a
> potential v2 cut. The "Step 2 — Voiceover track" section below is RETIRED;
> see "Step 2 (NEW) — Music-only audio mix" for the updated audio plan. Total
> tracks reduced from 4 to 3 (top: visuals, middle: music + native intro audio,
> bottom: optional UI SFX).

**Replaces:** `davinci_composite_workflow.md` — DaVinci Resolve was the prior plan; the team-lead pivot to Anthropic Minimalism + free + zero-Fusion-macro toolchain made CapCut Desktop the right choice for solo execution under deadline.

**Execution target:** Saturday 2026-04-25, 15:00–19:00 EDT.

**Tool:** CapCut Desktop (free) — `https://www.capcut.com/tools/desktop-video-editor` — install on macOS, requires ~500 MB.

---

## Why CapCut Over DaVinci Resolve

| Dimension | CapCut Desktop | DaVinci Resolve |
|---|---|---|
| Cost | Free | Free (paid for color science features we don't need) |
| Install time | 5 minutes | 20+ minutes (codecs, Fairlight, Fusion) |
| Learning curve | Drag, drop, slice, render. ~10 min to ship a first cut. | Requires Fusion macro authoring for text overlays — overhead under deadline |
| Macro authoring | Not needed (built-in text + transition presets handle 100% of our needs) | Custom Fusion macros take 30+ min each to author and debug |
| Audio mixing | Auto-leveling + voice enhancement filter (one click) | Fairlight panel — pro-grade but requires audio-engineering knowledge |
| Export speed | Hardware-accelerated H.264 on Apple Silicon (~30s for 3 min @ 1080p) | Comparable but more configuration required |
| Quality ceiling | More than enough for YouTube 1080p submission | Higher ceiling for color grading + VFX, not needed here |

CapCut wins on speed-to-ship. Use it.

---

## Pre-Flight Checklist (BEFORE opening CapCut)

Confirm all assets exist on disk:

```bash
# Live typing intro (QuickTime screen-record — see intro_typing_script.md)
ls ~/Documents/Panopticon_Captures/intro_typing_raw.mov
# Recorded ~60s raw; trimmed to 22s in CapCut

# Terminal precompute screen-record (QuickTime — see "Terminal Precompute Capture Spec" below)
ls ~/Documents/Panopticon_Captures/terminal_precompute_raw.mov
# Recorded full pipeline run; speed-ramped 20x in CapCut to ~5s

# Title cards (now 1 PNG from Keynote — Cards 1+2 RETIRED, see title_card_specs.md)
ls ~/Documents/Panopticon_TitleCards/
# Expected: card_03_closing.png  (only Card 3 — closing thesis — remains)

# OBS dashboard captures (4 MP4s — see "OBS Capture Spec" section below)
ls ~/Documents/Panopticon_OBS_Captures/
# Expected: obs_b1_anomaly.mp4  obs_b2_huddrop.mp4  obs_b3_secondmiss_tab2.mp4  obs_b4_scouting.mp4

# Voiceover audio (1 file — see voiceover_script.md)
ls ~/Documents/Panopticon_Audio/
# Expected: vo_master.m4a (or vo_master.wav)

# Optional: music bed (no keyboard SFX needed — live typing intro captures real keystrokes via laptop mic)
ls ~/Documents/Panopticon_Audio/
# Expected (if present): music_bed_instrumental.mp3
```

If ANY of these are missing, stop and produce them BEFORE opening CapCut. Working sequentially in CapCut while assets arrive is how cuts drift out of sync.

---

## Live Typing Intro Capture Spec (NEW opener — record FIRST at 11:00 EDT)

**Full spec lives in `demo-presentation/scripts/intro_typing_script.md`.** Quick summary here:

- **Tool:** QuickTime Player → New Screen Recording → "Record Selected Portion" around the Claude UI window
- **URL:** `https://claude.ai/new` (fresh chat thread, dark mode, full-screen Chrome)
- **Microphone:** **ON** (MacBook Pro mic) — captures authentic keyboard clack sound, NOT stock SFX. Per team-lead directive.
- **Take:** Record ~60 seconds raw. Andrew types the 4-stage prompt evolution (naive predictor → tennis-specific → broadcast-video → biomechanical-extraction). Backspaces and typos stay in — that's authenticity. Hits ENTER once at the end. Captures first 1-2s of Claude's response, then stops recording.
- **Output:** `~/Documents/Panopticon_Captures/intro_typing_raw.mov`
- **CapCut treatment:** speed-ramp typing portions to ~1.4x, preserve natural pause beats; trim to **22 seconds** final.

## Terminal Precompute Capture Spec (NEW — record SECOND at 11:00 EDT)

- **Tool:** QuickTime Player → New Screen Recording → "Record Selected Portion" around the iTerm2/Terminal window
- **Setup:**
  - Open iTerm2 (or Terminal). Dark theme. Cmd+Plus to bump font size to ~16-18pt for visual clarity in 1080p capture
  - `cd ~/Documents/Coding/hackathon-research`
  - Clear scrollback (`Cmd+K` in iTerm2)
  - Pre-stage the command in your shell history so you can up-arrow to it
- **Recording:**
  - Hit record
  - Up-arrow + ENTER to run: `python -m backend.precompute utr_match_01_segment_a` (or whatever the actual precompute command is — confirm with `ls scripts/` or `make` recipes)
  - Let the pipeline run end-to-end. Will scroll lots of output: "Loading YOLO11m-Pose...", "Processing frame 100/1800...", "Extracting biomechanical signals...", "Writing match_data.json... ✓"
  - When the final ✓ line appears, give it a 1-second hold, then stop the recording
  - Total raw recording duration: 30 seconds to 5 minutes depending on how fast precompute runs
- **Microphone:** **OFF** (no value in capturing fan noise + keyboard clacks of you idle-watching the terminal). The visual is enough.
- **Output:** `~/Documents/Panopticon_Captures/terminal_precompute_raw.mov`
- **CapCut treatment:** **SPEED-RAMP TO 20x or 50x** — the entire pipeline run compresses to **3-5 seconds final** (logs blur past, ending cleanly on `Writing match_data.json... ✓`). Per team-lead directive: "It is literal tech-porn for engineering judges."

**Why speed-ramp vs trim:** trimming would jump from "starting" to "done" — feels fake. Speed-ramping shows the FULL pipeline running but in compressed time — feels honest AND fast. The motion blur of scrolling text is its own visual signature.

---

## OBS Capture Spec (the 4 silent MP4s Andrew records 11:00–13:00 EDT, AFTER intro + terminal captures)

> **2026-04-26 OVERNIGHT UPDATE — RECORDING-TOOL CHANGE**: do NOT use OBS for these
> captures. The forensic investigation in `docs/RECORDING_LAG_RECIPE.md` showed that
> OBS x264 software encode contends with Chrome's main thread and amplifies the
> dashboard's existing per-rAF forced reflow into visible 100ms+ stutters. Use
> **macOS QuickTime via Cmd+Shift+5 → Record Selected Portion** instead. It uses
> hardware VideoToolbox H.264 encoding and runs as a system process, leaving Chrome's
> 144Hz rAF loop unburdened. The 4 capture filenames + scene specs below stay the
> same; ONLY the recording tool changes. If for some reason QuickTime is unavailable,
> the OBS-with-VideoToolbox-encoder fallback is documented in §2 of that recipe doc.

| File | Raw record duration | On-timeline target | What it captures |
|---|---|---|---|
| `obs_b1_anomaly.mp4` | ~35s (record full anomaly window with 2-3s pad on each side) | 30s | Tab 1 raw tennis playback into the anomaly frame. Skeleton overlay snaps on. **No live React red blink** (that branch is not deployed) — visual hook is reconstructed in CapCut (see "B1 Visual-Hook Reconstruction" below). Mouse stays out of frame. |
| `obs_b2_huddrop.mp4` | **Full 60s from clip 0:00 → 1:00** (per team-lead correction 2026-04-25 ~16:51 EDT) | ~50-53s after dead-time speed-ramp | Tab 1 sustained playback through one full point. **DO NOT skip 0:00-0:10** — the empty-court window shows the RecoveryLatencyBar initialize from 0, which IS our "first telemetry datapoint" data-moat moment. Speed-ramp the dead time in CapCut (see "B2 Dead-Time Speed-Ramp" below) to preserve the demonstration while reclaiming timeline budget. ALL widgets visible — SignalBars, skeleton overlay, court diagram, tickertape. |
| `obs_b3_secondmiss_tab2.mp4` | 25s | 25s | Mouse moves to "Tab 2 — Match Data". Click. Mouse moves to "Download Match Data (.csv)" button. Click. File-download chrome animation visible (browser saves CSV). 2-second hold on the downloaded file in browser bar. |
| `obs_b4_scouting.mp4` | 35s | 30-32s (trim 3-5s if needed to compensate for B2 expansion) | Click Tab 3. Multi-agent swarm trace begins replay. The 3 agents' messages appear in sequence (Analytics → Biomechanics → Strategy). Let the trace play through ONE point's reasoning chain. |

**Record at 1920×1080 @ 60 FPS, H.264 CRF 18, NO AUDIO** (audio comes from VO recording separately).

**Pre-flight before each OBS take:**
- **Bump cursor size** (System Settings → Accessibility → Display → Pointer size, +1 to +2 notches above default) — M4 Mac Mini default cursor at 1080p is tiny and gets lost in YouTube compression
- Close all Chrome tabs except `panopticon-live.vercel.app`
- Hide bookmarks bar (Cmd+Shift+B)
- Full-screen window (Cmd+Ctrl+F)
- Notifications OFF (Do Not Disturb)
- Mouse cursor: enabled (judges need to see the click), but move DELIBERATELY in smooth arcs — like Anthropic's Chrome demo "cream-gloved cursor"

**Take 2-3 of each clip.** Pick the cleanest in CapCut.

---

## ⚠️ THREE EDITORIAL TRAPS (corrected per team-lead directive 2026-04-25 ~16:51 EDT)

### Trap 1 — DO NOT use hard freeze-frames on dashboard captures

**Why this kills the demo:** the React dashboard runs a continuous `requestAnimationFrame` loop that paints the canvas, ticks the tickertape, breathes the SignalBars. A hard CapCut freeze-frame stops the entire MP4, which means the canvas freezes mid-pixel. To an Anthropic engineering judge that looks like the React tree locked up or the tab crashed — exactly the opposite signal we want to send.

**Use one of these instead at hero moments:**
- **(Preferred) 20% slow-mo via CapCut Speed Curve** — the video gives judges 5x the time to read the coach panel, but the tickertape still slightly crawls and the canvas keeps painting. UI looks alive.
- **Callout-paired hard freeze** — if you must hard-freeze, apply a distinct CapCut text callout or digital bounding box at the EXACT moment of the freeze. The post-production overlay tells the judge "the editor paused this to highlight the data," which excuses the frozen UI as editorial choice rather than browser crash.

### Trap 2 — B2 Dead-Time Speed-Ramp (clip 0:00-0:10 in obs_b2_huddrop)

**Why we record the full 60s and don't skip the empty-court opening:** the RecoveryLatencyBar visibly initializes during this window. That's the "first telemetry datapoint on the field" moment — a clean demonstration of telemetry initialization that judges will read as serious data-pipeline craft. Hard-cutting past it discards a unique data-moat showcase.

**CapCut treatment:**
1. Drop `obs_b2_huddrop.mp4` onto the timeline
2. Select the 0:00-0:10 portion (empty court / Recovery Clock initializing)
3. Right-click → Speed → Speed Curve → drag the curve to **3-5x speed** for that segment ONLY
4. Result: the 10s dead time compresses to ~2-3s on the timeline; the recovery clock ticks UP rapidly which actually looks like a deliberate, technical UI feature
5. Leave the remaining 50s (clip 0:10-1:00, the actual HUD walkthrough through the point) at **1x normal speed**

Final on-timeline duration: ~52-53s. To compensate, trim B3+B4 segment by 2-3s — they have slack.

### Trap 3 — B1 Visual-Hook Reconstruction (compensating for the missing live red blink)

**Context:** the live React red-blink anomaly visualization exists on a different branch (`hackathon-demo-v1`) and was NOT ported to the deployed branch (architecturally correct decision — porting a Saturday-afternoon React change risks breaking the deployed dashboard 36 hours before deadline). But the cold-open beat needs a visual hook so judges see the "missed call" moment register, not just raw playback of a guy walking around the baseline.

**CapCut reconstruction at the anomaly frame:**
1. Identify the exact frame in `obs_b1_anomaly.mp4` where the anomaly fires (cross-reference with `coach_insights[k].timestamp_ms` in the synced match_data — anomalies fire at ~35.9s, ~45.3s, ~59.1s in the source clip)
2. At that frame, layer **ONE** of these on top:
   - **Subtle red border flash** (CapCut → Effects → Borders → red @ 60% opacity, 0.5s duration with quick fade-out) — most cinematic, recommended
   - **Sleek post-production text callout** (CapCut → Text → "ANOMALY DETECTED" or similar, JetBrains Mono 24pt, cyan/red, 1.5s on-screen) — most forensic, least likely to read as gimmicky
3. **DO NOT use digital zoom** (TL listed it as an option but it's vetoed elsewhere in this doc — at 1080p source, scaling crops fidelity AND distorts UI text, breaking the "live dashboard" illusion)

The post-production overlay is acceptable editorial craft (judges expect editors to highlight key moments) — it's NOT pretending the live React did something it didn't.

---

## CapCut Project Setup

1. **Open CapCut Desktop**
2. **New Project** → name it `panopticon_live_demo_v1`
3. **Project Settings** (top-right gear):
   - Resolution: **1920 × 1080**
   - Frame rate: **60 fps**
   - Aspect ratio: **16:9**
4. **Save** (Cmd+S) — CapCut auto-saves but be paranoid

---

## Asset Import Sequence

1. **Drag the 1 title-card PNG** (Card 3 only — Cards 1+2 retired) into the Media bin (left panel)
2. **Drag the 2 QuickTime intro captures** (`intro_typing_raw.mov`, `terminal_precompute_raw.mov`)
3. **Drag the 4 OBS dashboard captures** into the Media bin
4. **Drag the VO file (`vo_master.m4a`)** into the Media bin
5. *(Optional)* Drag music bed if you have it (no keyboard SFX needed — typing audio is in `intro_typing_raw.mov`'s native audio track)

CapCut auto-thumbnails everything. Confirm all assets appear.

---

## Timeline Assembly — Sequential Steps

The timeline has 4 tracks:

```
Track 4 (top):    Title cards + OBS captures (the visual)
Track 3:          Voiceover audio (vo_master.m4a slices)
Track 2:          Music bed (continuous, if present)
Track 1 (bottom): SFX (keyboard typing on Beat 1, optional click sounds)
```

### Step 1 — Visual track (top)

Drag clips onto Track 4 in this exact sequence at these exact timecodes:

| Start | End | Clip | Notes |
|---|---|---|---|
| 0:00 | 0:22 | `intro_typing_raw.mov` (trimmed + speed-ramped to 1.4x on typing portions) | The 4-stage prompt evolution. Native audio (laptop-mic keystrokes) on its own audio sub-track. |
| 0:22 | 0:27 | `terminal_precompute_raw.mov` (speed-ramped 20x or 50x) | The CV pipeline running in iTerm. Compressed scrolling logs ending on `Writing match_data.json... ✓`. NO audio. |
| 0:27 | 0:30 | *(black hold + tiny "→" transition mark, OR optional 0.5s cross-fade)* | Visual breath separating "input" (typing + terminal) from "output" (dashboard). Hard cut into the dashboard reveal lands cleanly with this micro-pause. |
| 0:30 | 1:00 | `obs_b1_anomaly.mp4` | Cold open on dashboard. Trim to 30s. **Layer post-production red border flash + text callout at the anomaly frame** (see Trap 3 above) to reconstruct the visual hook. **Beat 2 of demo storyboard.** |
| 1:00 | ~1:53 | `obs_b2_huddrop.mp4` | Tab 1 HUD walkthrough — **record full 60s, speed-ramp 0:00-0:10 dead time 3-5x** (see Trap 2 above). On-timeline ≈ 52-53s. **Beat 3.** |
| ~1:53 | 2:45 | `obs_b3_secondmiss_tab2.mp4` + `obs_b4_scouting.mp4` (concatenated) | CSV download (~25s) + Tab 3 swarm replay (~27-30s, trim to absorb B2's 2-3s overflow). Total 52-55s. **Beat 4.** |
| 2:45 | 2:48 | *(black hold)* | Pure black — drag a black slide or use CapCut's built-in "background → solid black" — provides hard cut separation between dashboard footage and closing card. |
| 2:48 | 3:00 | `card_03_closing.png` | Hold static for 12s. **Beat 5: closing thesis.** |

**Total runtime: exactly 3:00.**

**Transition rule:** Almost everything is a HARD CUT. Two soft transitions allowed:
1. The 0.5s cross-fade (or pure black hold) at 0:27-0:30 between terminal capture and dashboard reveal — visual breath between input and output.
2. The black hold at 2:45-2:48 before the closing card — hard cut separation between footage and editorial closing.

Anthropic's vocabulary: "hard cut + occasional scale-pop + typewriter." Don't add additional crossfades. Don't add Ken Burns zooms. Don't add anything to the OBS captures (digital zoom on UI distorts text — team-lead VETO).

### ⚠️ RETIRED — Step 2 — Voiceover track (DO NOT EXECUTE)

> **Voice-over deferred 2026-04-25 ~20:41 EDT** per Andrew's executive call.
> Section preserved below for v2 reference only. Skip this entire block in
> the v1 assembly. Go directly to "Step 2 (NEW) — Music-only audio mix".

> **Timing shift:** the new typing+terminal opener is 30s vs the old static-card 15s opener. **All VO line timings shift forward by +15s** vs `voiceover_script.md`. See the updated timing table at the bottom of `voiceover_script.md` for the new positions.

If you recorded all 12 lines as separate clips: drag each onto Track 3 at the
exact (shifted) timecode from `voiceover_script.md` (e.g., new L1 → 0:33, new L2 → 0:39, ...).

If you recorded it as one long take: import the single file, slice between
each line using the **Split** tool (S key in CapCut), then drag each piece
into position.

**Audio level rule:**
- VO peak: -12 dBFS during spoken lines
- VO completely silent (cut, not muted) between lines — silence is part of the script

---

### ✅ ACTIVE — Step 2 (NEW) — Music-only audio mix

Without voice-over, the music bed becomes the THROUGH-LINE that holds 3
minutes of silent footage together. Choose a track with a CLEAR 3-minute
arc (build → climax → decay), not just a 30-second loop. Indie lo-fi /
ambient electronica / minimal cinematic — SF tech-judge taste.

**Audio track structure (revised):**

```
Track 4 (top):    Title cards + OBS captures (the visual)
Track 2 (mid):    Music bed (continuous, primary audio)
Track 1 (bot):    Live typing intro NATIVE AUDIO (keyboard clacks from QuickTime mic capture, 0:00-0:22 only)
                  + optional UI click SFX on tab transitions
```

**Music placement:**

1. Drag music track onto Track 2, starting at 0:00
2. Trim music end to 3:00 + ~1s ring-out (so the final chord decays into 1-2s of silence after the YouTube cut, per Numerai DNA)
3. **Base level: -14 dBFS** (was -24 with VO; raise to -14 since music is now primary). Should fill the room without overpowering.
4. **Ducking under live-typing intro audio:** if your intro QuickTime captured authentic keyboard clacks at audible volume, duck music to -20 dBFS during 0:00-0:22 so the typing reads clearly. Restore to -14 at 0:22.
5. **Volume swell at editorial pivot points** (use CapCut keyframes):
   - 0:30 (dashboard reveal): +2 dB swell, 0.5s ramp — punctuates the visual transition from "input" (typing+terminal) to "output" (the dashboard)
   - 1:50 (Tab 2 reveal): +1 dB swell, 0.5s ramp — punctuates the value-prop reveal
   - 2:15 (Tab 3 swarm reveal): +2 dB swell, 0.5s ramp — punctuates the agent-orchestration reveal
   - 2:48 (closing card entry): +3 dB swell to -11 dBFS, 1s ramp — sustains for the full 12-second closing hold
6. **Final ring-out:** let music play through 3:00:00, then natural decay to silence by 3:01.5

**No voice-over to duck under** — set CapCut's "Auto Duck" feature OFF for the music track (it has nothing to duck against).

**The native typing audio from `intro_typing_raw.mov`** is the ONLY voice-like audio in the entire demo — keyboard clacks captured by the MacBook mic during live typing. This is the ANTHROPIC SIGNATURE move (real keystrokes, not stock SFX). Make sure it stays audible at -16 dBFS during 0:00-0:22.

### Step 3 — Music bed (optional but recommended)

If you have an instrumental track ~120 BPM:

1. Drag onto Track 2 starting at 0:00
2. Trim to end at 3:00
3. Set base level: -24 dBFS (sits comfortably under VO)
4. **Auto-duck under VO**: CapCut has built-in side-chain ducking — enable
   "Auto Duck" on the music clip, set ducking amount to -12 dB triggered by
   Track 3
5. **Volume swell at 2:48** (Beat 5 entry): keyframe the music level to rise
   from -24 to -18 dBFS as Card 3 appears, then sustain
6. **Final chord ring-out**: let the music play for 1 full second AFTER 3:00
   ends, then hard cut to silence (this is the 1-2s of trailing silence per
   Numerai DNA)

**No music? Skip this track entirely.** The VO + ambient room tone of OBS
captures will carry. Anthropic's Chrome demo has minimal music; silence is
acceptable.

**Where to find royalty-free music:**
- Artlist.io (paid, $15/month, instant download — best quality)
- Pixabay Music (free, lower quality, requires attribution)
- YouTube Audio Library (free, no attribution)
- **Search terms**: "cinematic minimal", "ambient electronica", "tech reveal"
- **Avoid**: trap, EDM drops, vocal house, anything with a hook

### Step 4 — SFX track

**Keyboard typing on Beat 1 (0:00 – 0:08):**
1. Source: free keyboard typing SFX from Pixabay or YouTube Audio Library
2. Drag onto Track 1 starting at 0:01
3. Trim to end at 0:07 (silence as Card 2 appears at 0:09)
4. Level: -18 dBFS (audible, not loud)

**Optional UI click on tab transitions** (1:45, 2:30):
- Free "soft mouse click" SFX from Pixabay
- Drag onto Track 1 at each tab-change timecode
- Level: -22 dBFS (subtle)

---

## Color & Polish Pass (10 minutes)

CapCut's default color is fine for the dashboard captures (the HUD has its own
color identity). The title cards are pure black + white + cyan and need no
adjustment.

ONE polish step: apply CapCut's **"Cinematic"** filter at 15% intensity to the
OBS captures only. This adds a slight warmth + microcontrast that makes the
HUD feel more like footage than a screencast. Skip this if it makes the cyan
SignalBars look off.

**Do NOT apply any LUT, film-grain, or vintage filter.** Anthropic-aligned =
clean digital, NOT filmic-warm.

---

## Export Settings

**File → Export → Custom Settings:**

| Setting | Value |
|---|---|
| Format | MP4 |
| Codec | H.264 |
| Resolution | 1920 × 1080 |
| Frame rate | 60 fps |
| Bitrate | 12 Mbps (CBR) — visually lossless at 1080p |
| Audio codec | AAC |
| Audio bitrate | 320 kbps |
| Audio sample rate | 48 kHz |
| Color space | Rec. 709 / sRGB |
| HDR | OFF |

**File size target:** ≤ 200 MB (well under hackathon's 500 MB limit and YouTube's "no upload size limit but reasonable").

**Export filename:** `panopticon_live_demo_v1_FINAL_<YYYY-MM-DD>.mp4`

**Export location:** `~/Documents/Panopticon_Final/`

---

## Quality Audit (BEFORE YouTube Upload)

Open the exported MP4 in QuickTime and watch end-to-end ONCE without scrubbing:

- [ ] Total runtime is **3:00 ± 1 second** (NOT 3:01 or longer — YouTube algorithm caps social previews at 3 min and may truncate)
- [ ] Title cards are crisp (zoom into a frame in QuickTime; serif edges should be smooth)
- [ ] No audio clipping (VO peaks under -3 dBFS, music never above -12 dBFS)
- [ ] No silent gaps where there shouldn't be (typically: a missing VO line, or music dropping out)
- [ ] Cyan color reads as cyan (`#00E5FF`), not blue or teal
- [ ] All cuts are HARD cuts except the one Card1→Card2 crossfade
- [ ] First frame is the typing animation, NOT a black flash
- [ ] Last frame is the closing card with cyan rule, NOT a black flash
- [ ] No accidental browser chrome visible in OBS captures (toolbar, tabs, dev console)

If ANY checkbox fails: re-export from CapCut after fixing. Better to re-export 3 times than upload a flawed cut.

---

## YouTube Upload Sequence

1. **Sign in** at `studio.youtube.com` (Andrew's channel)
2. **Upload Video** → drag `panopticon_live_demo_v1_FINAL_<DATE>.mp4`
3. **Title:** `PANOPTICON LIVE — Biomechanical Intelligence for Pro Tennis | Built with Opus 4.7 Hackathon`
4. **Description:** paste from `demo-presentation/scripts/submission_summary.md`
5. **Visibility:** **Unlisted** for now (you'll switch to Public after CV submission)
6. **Thumbnail:** custom thumbnail using a frame from `obs_b2_huddrop.mp4` (the HUD looking dramatic). 16:9 PNG, 1280×720 minimum.
7. **Tags:** `claude opus 4.7, anthropic, hackathon, tennis, biomechanics, computer vision, sports analytics, cerebral valley`
8. **End screens / cards:** SKIP. Editorial restraint — no spam links.
9. **Click "Publish"** (still Unlisted)
10. **Wait 5–15 minutes** for YouTube to process the HD version. Watch it on YouTube once playback is HD-ready.
11. **If playback looks correct:** switch to **Public** under Visibility.
12. **Copy the Public URL** for CV submission.

---

## CV Submission Sequence (Sunday 2026-04-26 by 17:00 EDT soft target)

1. Open the CV submission portal (URL from the Cerebral Valley confirmation email)
2. Project name: **PANOPTICON LIVE**
3. YouTube URL: paste from above (must be Public)
4. GitHub URL: `https://github.com/andydiaz122/panopticon-live`
5. Written summary: paste from `demo-presentation/scripts/submission_summary.md` (100–200 word variant)
6. **Click submit.**
7. **Screenshot the confirmation page** for paranoia.

**Hard lockout: do NOT submit after Sunday 19:55 EDT.** Five-minute buffer before 20:00 deadline is mandatory because every previous hackathon I've seen has had platform congestion in the final 5 minutes.

---

## Fallback Plan If CapCut Crashes / Fails to Export

1. **Re-export at lower bitrate** (8 Mbps instead of 12) — sometimes CapCut struggles with H.264 hardware encoder under load
2. **Try Apple's free Mac app "Photos"** to assemble a basic version (drag clips into a project, no transitions, export)
3. **Use QuickTime's built-in "Trim" + iMovie** as last resort
4. **NUCLEAR FALLBACK:** export each segment from CapCut as separate MP4s and concatenate with ffmpeg:
   ```bash
   # Create a concat list
   cat > /tmp/concat.txt <<EOF
   file '/path/to/segment_1.mp4'
   file '/path/to/segment_2.mp4'
   ...
   EOF
   # Concat without re-encoding (fast, lossless)
   ffmpeg -f concat -safe 0 -i /tmp/concat.txt -c copy ~/Documents/Panopticon_Final/panopticon_live_demo_v1_FINAL.mp4
   ```

---

## Time Budget for the Assembly Block (15:00–19:00 EDT, 4 hours)

| Time | Activity | Cumulative |
|---|---|---|
| 15:00–15:15 | CapCut install + project setup + asset import | 15 min |
| 15:15–15:45 | Visual track assembly (drag + sequence + trim) | 45 min |
| 15:45–16:30 | VO track placement + level matching | 90 min |
| 16:30–17:00 | Music bed + SFX + auto-duck setup | 120 min |
| 17:00–17:30 | First export + QuickTime audit + adjustments | 150 min |
| 17:30–18:00 | Second export (post-fixes) + audit | 180 min |
| 18:00–18:30 | YouTube upload + thumbnail + Unlisted publish | 210 min |
| 18:30–19:00 | Wait for HD processing + switch to Public + copy URL | 240 min |

**Total: 4 hours.** Built-in slack for re-exports. Submission ready by 19:00, soft-submit at Sunday 17:00 with a full overnight buffer.

---

## What This Workflow REMOVES from Friday's Plan

- ❌ DaVinci Resolve installation + Fusion macro authoring (~2 hours saved)
- ❌ Custom title-card animation in Remotion + render audit loop (~3 hours saved on Friday's pre-dawn — those V2 renders are now optional fallback)
- ❌ Color science calibration (CapCut's defaults are fine for YouTube 1080p)
- ❌ Audio engineering (CapCut's Voice Enhancement + Auto Duck handle 95% of what Fairlight would)

**Total time saved: ~5+ hours, redirected to sleep + clean execution.**

---

**Ship the cleanest possible version of the team-lead's vision: pristine product captures, clinical disembodied voice, three pure-void title cards, ONE accent color, hard cuts everywhere except one. The Anthropic minimalism standard, executed with the simplest possible toolchain.**
