# DaVinci Resolve Composite Workflow — Saturday Morning Guide

**Status**: written 2026-04-25 ~04:30 EDT for Andrew's Saturday morning composite session
**Goal**: assemble the 3-minute demo video from 6 Remotion MP4s + 4 OBS dashboard captures + 7 text overlays
**Output**: `renders/panopticon_live_final.mp4` — H.264 1920×1080 @ 60 fps, CRF 18, AAC 320 kbps, ≤500 MB

---

## Phase 0 — Project setup (~2 min)

1. Open DaVinci Resolve → File → New Project → name `panopticon_live_final`
2. **Project Settings** (⌘`,`):
   - Master Settings → Timeline frame rate: **60 fps** (must match Remotion + OBS)
   - Master Settings → Timeline resolution: **1920 × 1080 HD**
   - Master Settings → Video monitoring: matches HDR/SDR of recording surface (likely SDR)
3. Save (⌘S) immediately — DaVinci is more crash-prone than Premiere

---

## Phase 1 — Asset import (~3 min)

Drop these into the Media Pool (left panel):

### Remotion-rendered chrome (`demo-presentation/remotion/out/`)

| File | Duration | Role |
|---|---|---|
| `b0-opener.mp4` | 25 s | Personal-journey opener (typing → gitgraph → Panopticon Live wordmark) |
| `scene-break-b2.mp4` | 1.5 s | Beat-marker between B1 → B2 ("BEAT 02 · The Sensor") |
| `scene-break-b3.mp4` | 1.5 s | Beat-marker between B2 → B3 ("BEAT 03 · The Recurrence") |
| `scene-break-b4.mp4` | 1.5 s | Beat-marker between B3 → B4 ("BEAT 04 · Opus Reads the Body") |
| `b5-closing.mp4` | 5 s | Brand wordmark + URL + repo + attribution |
| `b5-thesis.mp4` | 4 s | "capture the signal nobody else is reading." (NEW — pure void thesis) |

**If b0-opener and others aren't in `out/`**: re-render with `cd demo-presentation/remotion && ./node_modules/.bin/remotion render <id> out/<id>.mp4` per id.

### OBS captures (TBD — record Saturday morning)

You'll record these 4 captures from `https://panopticon-live.vercel.app` during your morning session per PLAN.md §10:

| File (suggested name) | Duration | What to capture |
|---|---|---|
| `obs_b1_anomaly.mp4` | ~18 s | Tab 1 Live HUD playing through the t=45.3s anomaly. Pause on anomaly frame, hold ~3s. SignalBar pulse + Vision-Pass overlay visible. |
| `obs_b2_huddrop.mp4` | ~17 s | Tab 1 with HUD snap-in shown, signal naming cadence, then `.claude/skills/` file tree flash bottom-left for ≥2s. |
| `obs_b3_secondmiss_tab2.mp4` | ~40 s | Tab 1 second anomaly at t≈59.1s + slow-mo (A2a `playbackRate` 1.0× → 0.25×) → switch to Tab 2 Raw Telemetry → DOWNLOAD CSV BUTTON VISIBLE on the firehose + scrolling events for ~15s. |
| `obs_b4_scouting.mp4` | ~60 s | Tab 3 Scouting Committee, click ▶ PLAY COMMITTEE, let the trace play through. Watch for the FINAL TACTICAL BRIEF render moment. |

**OBS settings**: H.264, 1920×1080, 60 fps, CRF 18 (quality), audio off (we add silence in DaVinci). Save to `~/Movies/panopticon_obs_takes/` so they're easy to find.

---

## Phase 2 — Timeline assembly (~10 min)

Drag from Media Pool to the timeline (V1 video track) in this order:

```
[0:00 ──── 0:25]  b0-opener.mp4
[0:25 ──── 0:43]  obs_b1_anomaly.mp4
[0:43 ──── 0:44.5]  scene-break-b2.mp4         ← 1.5 s beat marker
[0:44.5 ── 1:01.5]  obs_b2_huddrop.mp4         ← 17 s
[1:01.5 ── 1:03]    scene-break-b3.mp4         ← 1.5 s beat marker
[1:03 ─── 1:43]     obs_b3_secondmiss_tab2.mp4 ← 40 s
[1:43 ─── 1:44.5]   scene-break-b4.mp4         ← 1.5 s beat marker
[1:44.5 ── 2:44.5]  obs_b4_scouting.mp4        ← 60 s climax
[2:44.5 ── 2:49.5]  b5-closing.mp4             ← 5 s brand card
[2:49.5 ── 2:53.5]  b5-thesis.mp4              ← 4 s thesis (NEW)
[2:53.5 ── 2:58]    BLACK (Generators → Solid Color → Black)  ← silent black hold
```

**Total runtime: 2:58** — under the 3:00 hard cap with 2-second margin (matches PLAN.md §5.5.4).

**All cuts are HARD CUTS** — no crossfades anywhere except an optional 4-frame dissolve between OBS captures and scene-break cards if the cuts feel jarring (test in playback first; HARD CUT is the Numerai-correct default per PATTERN-082).

---

## Phase 3 — Narration text overlays (~25 min)

Reference: `demo-presentation/scripts/narration_overlays.md` for full spec.

### Build the text template ONCE

Edit page → Effects → Titles → Text+ → drag onto V2 track. Open Inspector. Set:

- Font: **JetBrains Mono** (or system mono if missing)
- Size: **42** (~14px relative on 1080p, scales OK)
- Color: `#F8FAFC`
- Tracking: `+40` (Inspector slider, equivalent to ~+0.04em CSS)
- Background: enabled, color `#05080F`, opacity 90%, padding 12px H × 8px V
- Position: Y = 80% (bottom-third subtitle position), X = center
- **Animation**: enable Opacity keyframes
  - 0:00 → opacity 0
  - 0:00.4 → opacity 100
  - 0:01.0 → opacity 100 (hold)
  - 0:01.4 → opacity 0

Right-click → Save as Macro → name "PanopticonOverlay". Now reusable.

### Drop the 6 overlays at these timecodes

Drop "PanopticonOverlay" macro on V2 track at each In time below, set duration = 1.4s, edit text:

| # | In | Text |
|---|---|---|
| 1 | 0:35.000 | `flagged · frame 1,359 · σ 2.5 crouch-depth anomaly` |
| 2 | 0:43.500 | `yolo11m-pose · kalman on court meters · 7 biomech signals` |
| 3 | 0:53.000 | `12 skill packs · 2d pixels → clinical telemetry` |
| 4 | 1:00.500 | `recurring · Δ −11.69° · 13.8 s apart · fatigue pattern locked` |
| 5 | 1:15.000 | `proprietary stream · every signal, every state — downloadable as .csv` |
| 6 | 1:40.500 | `opus 4.7 · adaptive thinking · cached system prompt` |
| 7 | 2:08.000 | `✗ serve-mechanics hypothesis rejected — crouch preceded toss by 8.2 s` |

**Overlay #5** ("downloadable as .csv") presumes the OBS capture shows the Download button on screen at 1:15. Confirm during scrub — adjust ±1-2 s if Tab 2 hasn't fully loaded by then.

**Overlay #7** is the climax-frame overlay (B4's 1:58 "money shot" frame, now at ~2:08 in the final cut). Must land in sync with the Rejected Thought chip flash. Adjust ±500ms during scrub to land precisely.

---

## Phase 4 — Audio (~5 min)

**Decision**: silent demo + light music bed.

**Option A — silent** (safer, fastest): no audio bed. The 2:58 plays in silence except for the typing-on-keyboard SFX in B0 (which Remotion already includes if added — check b0-opener.mp4). Judge experience: "calm, technical, restrained." Matches Detective Cut tone.

**Option B — light music bed**: import a royalty-free instrumental (recommend Epidemic Sound search "tense documentary minimal" or "tech ambient slow build"). Drop on A2 track at -28 LUFS integrated. Sustained pad with no melodic drama. Cut at 2:58 with the final hard-cut to black.

**Option C — Numerai-style music build to closing**: like Option B but with a final crescendo at 2:50 that sustains through B5b thesis card. Most cinematic; requires picking the right track.

My recommendation: **Option A (silent)** — preserves the Detective Cut's "let the data speak" tone. If you have time after the rough cut, layer Option B as a 5-min experiment.

---

## Phase 5 — Color grading (~3 min)

Likely zero work needed — Remotion compositions are already in the dashboard color palette, OBS captures are direct from the rendered dashboard. If anything looks off:

- Color page → Curves → small lift on the lows if blacks crush
- Color page → Saturation → +5 if it feels too cool/dead
- Otherwise leave alone — over-grading is worse than no grading

---

## Phase 6 — Export (~5 min for export + 5 min QA)

**Deliver page**:
- Format: **MP4**
- Codec: **H.264**
- Resolution: **1920 × 1080**
- Frame rate: **60 fps**
- Quality: **Restrict to 30000 Kb/s** (high — file size will be ~225 MB for 3 min, well under 500 MB cap)
- Audio: **AAC, 320 Kbps, 48 kHz, Stereo** (even if silent, Audacity-style tracks need an audio track)

Filename: `renders/panopticon_live_final.mp4`

### QA pass before YouTube upload

1. Play the export at 1× speed all the way through. Watch for: dropped frames, audio sync (if audio), text overlay timing relative to video events.
2. Verify file size: should be 200-300 MB.
3. Verify duration: should be exactly 2:58.
4. Open in QuickTime AND in Chrome (drag onto a tab) — both should play smoothly.
5. Test on phone (AirDrop the file) — confirms portable codec compatibility.

If anything fails, re-export. Don't ship a broken file to YouTube.

---

## Phase 7 — YouTube upload (~30 min upload + processing)

Per PLAN.md §10 Sunday timeline, target upload at 12:00 EDT (3 hours ahead of plan for Content ID processing).

1. YouTube Studio → Upload → drag `panopticon_live_final.mp4`
2. **Visibility: UNLISTED** initially (so we can verify before public)
3. **Title**: `PANOPTICON LIVE — Biomechanical Intelligence for Pro Tennis | Built with Opus 4.7 Hackathon`
4. **Description**: paste from `demo-presentation/scripts/submission_summary.md` → "YouTube video description" section
5. **Tags**: `claude opus 4.7, anthropic hackathon, tennis biomechanics, computer vision, sports analytics, multi-agent, claude code`
6. **Thumbnail**: take a screenshot of the dashboard at the t=45.3s anomaly frame with SignalBar pulsing red. Upload as custom thumbnail.

After upload, hit Save. YouTube processes for ~5-15 min. Check Restrictions tab (Content ID, copyright). If clean, switch Unlisted → **PUBLIC** and copy the URL for the CV submission form.

---

## Open follow-ups / fallbacks

- **If b5-thesis.mp4 looks weird in DaVinci**: re-render via `./node_modules/.bin/remotion render b5-thesis out/b5-thesis.mp4`. The text wrap pattern was visually verified via ffmpeg frame extract — should look identical in DaVinci.
- **If overlay #5's "downloadable as .csv" feels confusing without showing the actual button**: change the text to `proprietary stream · every signal, every state — timestamped` (the original §5.5.2 line). Don't sacrifice clarity for product-callout if the visual doesn't support it.
- **If you have time on Sunday morning**: add a MICRO-PAN ZOOM (Inspector → Zoom 100% → 102% over each shot's duration) to the OBS captures. Numerai's "slow drift" pattern (PATTERN-084) applied to live footage. Subtle "camera alive" cue without Ken Burns aggression.
- **If recording goes long Saturday**: skip the b5-thesis card initially, just use b5-closing as the final beat. Add b5-thesis Sunday morning if there's time. The thesis card is HIGH leverage but not blocking.

---

## What I (Claude) didn't pre-build for Saturday

- **OBS scene presets** — I don't know your OBS layout preferences (windowed vs fullscreen, hotkeys, mic state). Set those up Saturday morning per PLAN.md §6 recording discipline.
- **Architecture-diagram PNG** for B5 (or as a slide before B5) — currently lives in FigJam (`figma.com/board/1McYlYT0isbmTOJshc9ip9`). Open in browser, File → Export → PNG, save to `demo-presentation/assets/architecture-diagram.png`. Drop on V1 track between obs_b4 and b5-closing if you want it (adds ~5 s to runtime, may push past 3:00 cap — test).
- **Mascot test-drive comparison renders** (PLAN.md §5.5.3) — non-blocking, can be Sunday work or skipped entirely.
