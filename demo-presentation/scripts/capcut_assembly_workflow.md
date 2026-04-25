# CapCut Assembly Workflow — PANOPTICON LIVE Demo (Anthropic Minimalism Pivot)

**Authored:** 2026-04-25 ~06:00 EDT.

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
# Title cards (3 PNGs from Keynote — see title_card_specs.md)
ls ~/Documents/Panopticon_TitleCards/
# Expected: card_01_question.png  card_02_answer.png  card_03_closing.png

# OBS dashboard captures (4 MP4s — see "OBS Capture Spec" section below)
ls ~/Documents/Panopticon_OBS_Captures/
# Expected: obs_b1_anomaly.mp4  obs_b2_huddrop.mp4  obs_b3_secondmiss_tab2.mp4  obs_b4_scouting.mp4

# Voiceover audio (1 file — see voiceover_script.md)
ls ~/Documents/Panopticon_Audio/
# Expected: vo_master.m4a (or vo_master.wav)

# Optional: keyboard SFX + music bed
ls ~/Documents/Panopticon_Audio/
# Expected (if present): keyboard_typing.mp3  music_bed_instrumental.mp3
```

If ANY of these are missing, stop and produce them BEFORE opening CapCut. Working sequentially in CapCut while assets arrive is how cuts drift out of sync.

---

## OBS Capture Spec (the 4 silent MP4s Andrew records 11:00–13:00 EDT)

| File | Duration target | What it captures |
|---|---|---|
| `obs_b1_anomaly.mp4` | 30s | Tab 1 raw tennis playback. Skeleton snaps on. SignalBar pulses red on the anomaly frame (the "missed call" moment). Mouse stays out of frame. |
| `obs_b2_huddrop.mp4` | 60s | Tab 1 sustained playback through one full point. ALL widgets visible — SignalBars, skeleton overlay, court diagram, tickertape. Slow deliberate scrubbing if needed. |
| `obs_b3_secondmiss_tab2.mp4` | 25s | Mouse moves to "Tab 2 — Match Data". Click. Mouse moves to "Download Match Data (.csv)" button. Click. File-download chrome animation visible (browser saves CSV). 2-second hold on the downloaded file in browser bar. |
| `obs_b4_scouting.mp4` | 35s | Click Tab 3. Multi-agent swarm trace begins replay. The 3 agents' messages appear in sequence (Analytics → Biomechanics → Strategy). Let the trace play through ONE point's reasoning chain. |

**Record at 1920×1080 @ 60 FPS, H.264 CRF 18, NO AUDIO** (audio comes from VO recording separately).

**Pre-flight before each OBS take:**
- Close all Chrome tabs except `panopticon-live.vercel.app`
- Hide bookmarks bar (Cmd+Shift+B)
- Full-screen window (Cmd+Ctrl+F)
- Notifications OFF (Do Not Disturb)
- Mouse cursor: enabled (judges need to see the click), but move DELIBERATELY — like Anthropic's Chrome demo "cream-gloved cursor"

**Take 2-3 of each clip.** Pick the cleanest in CapCut.

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

1. **Drag the 3 title-card PNGs** into the Media bin (left panel)
2. **Drag the 4 OBS captures** into the Media bin
3. **Drag the VO file (`vo_master.m4a`)** into the Media bin
4. *(Optional)* Drag keyboard SFX and music bed if you have them

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
| 0:00 | 0:08 | `card_01_question.png` | Hold static for 8s; the typing SFX will play under it |
| 0:08 | 0:09 | *(crossfade)* | 1-second cross-fade between Card 1 and Card 2 |
| 0:09 | 0:15 | `card_02_answer.png` | Hold static for 6s |
| 0:15 | 0:45 | `obs_b1_anomaly.mp4` | Trim if needed to fit 30s |
| 0:45 | 1:45 | `obs_b2_huddrop.mp4` | Trim to fit 60s |
| 1:45 | 2:30 | `obs_b3_secondmiss_tab2.mp4` | Trim if needed; this is the CSV download moment |
| 2:30 | 2:45 | `obs_b4_scouting.mp4` | Trim to ~15s — capture just the most readable agent exchange |
| 2:45 | 2:48 | *(black hold)* | Pure black — drag a black slide or use CapCut's built-in "background → solid black" — provides hard cut separation between dashboard footage and closing card |
| 2:48 | 3:00 | `card_03_closing.png` | Hold static for 12s |

**Total runtime: exactly 3:00.**

**Transition rule:** ALL cuts between OBS clips and between OBS→card are HARD CUTS. The only crossfade in the entire video is the 1-second Card1→Card2 crossfade in Beat 1. This matches Anthropic's "hard cut + occasional scale-pop + typewriter" vocabulary.

### Step 2 — Voiceover track

If you recorded all 12 lines as separate clips: drag each onto Track 3 at the
exact timecode from `voiceover_script.md` (e.g., L1 → 0:18, L2 → 0:24, ...).

If you recorded it as one long take: import the single file, slice between
each line using the **Split** tool (S key in CapCut), then drag each piece
into position.

**Audio level rule:**
- VO peak: -12 dBFS during spoken lines
- VO completely silent (cut, not muted) between lines — silence is part of the script

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
