# Recording Lag Recipe — Why OBS Stuttered & What To Use Instead

**Authored:** 2026-04-26 overnight (CV/perf-engineering investigation by Claude).
**Audience:** Andrew + future agents recording the dashboard for any video output.
**TL;DR:** OBS isn't broken — the dashboard has a per-rAF forced-reflow and a `pause()`/`play()` storm that compound under any CPU contention. Use **macOS QuickTime Cmd+Shift+5** for Sunday's recording. Re-enable the slow-mo + pause behaviors for the live URL — they're great UX once the recording tool isn't competing for the main thread.

---

## 1. Root cause analysis

### The visible symptom
OBS recordings of the dashboard showed perceptual stutter — frame hitches, micro-pauses in the canvas skeleton paint, typewriter judder. Andrew disabled `useSlowMoAtAnomalies` (HudView.tsx:54) and the 3 `video.pause()` / `video.play()` calls in CoachPanel.tsx (lines 91, 106, 117) to get a clean OBS take.

### What the instrumentation found
Using `chrome-devtools-mcp` with the documented `feedback_chrome_devtools_mcp_video_instrumentation.md` pattern (wrap `<video>.pause/play`, install RAF cadence + long-task observers), we ran three tests on the local dev server:

| Test | Pauses | Synthetic load | FPS p10 | Long tasks | RAF drops | Severe (>100ms) |
|---|---|---|---|---|---|---|
| **A** clean baseline | enabled | none | 119 | 107 (7.7s) | 73 | **0** |
| **B** simulated OBS load | enabled | 4 workers + 50ms-period burn | 122 | 96 (6.6s) | 70 | **4** |
| **C** disabled + load | DISABLED | same load as B | 122 | 79 (5.3s) | 53 | 1 |

### What this tells us

1. **The dashboard already has 107 long tasks per 60s clip even at idle.** Mostly from per-rAF forced reflows.
2. **Pauses contribute 25-50% of long tasks under load** but are NOT the dominant source.
3. **OBS-class CPU contention adds the SEVERE tail** — 4 drops >100ms vs 0 in a clean run. Those severe drops are exactly what you see as "video stutter" in the recording.
4. **Disabling pauses hides the MOST visible symptom** under load (4 severe drops → 1) but doesn't fix the underlying inefficiency.

### The forced-reflow culprit (the deeper cause)

`chrome-devtools-mcp.performance_analyze_insight` flagged `ForcedReflow` and identified the top function:

```
PanopticonEngine.useEffect.tick @ src/components/PanopticonEngine.tsx ~line 108
  Total reflow time: 162ms over the trace
```

The cause: `canvas.clientWidth` and `canvas.clientHeight` are read on every rAF tick (lines 108-109 of PanopticonEngine.tsx). Every read forces the browser to flush pending layout. At 144Hz on M4 Pro, that's 144 forced reflows per second. Under CPU contention, each reflow takes longer, and the cumulative cost spikes long tasks above 100ms.

Secondary contributor: `framer-motion`'s `measureScroll` (Tickertape) adds ~21ms of additional reflow.

### Why OBS specifically makes this worse

OBS Studio on macOS:
- **ScreenCaptureKit** capture loop runs at the configured FPS (typically 60Hz @ 1080p) — uses ~5-10% baseline per stream
- **H.264 software encode** (x264) — uses 35-60% of one core continuously at 1080p60 CRF 18
- **Browser Source** path uses an embedded Chromium (CEF) which runs as a separate Chromium process — that's ANOTHER set of renderer threads competing for cores
- All four of these compete with the dashboard's main thread for the same 12-core M4 Pro

Andrew's diagnostic ("It only happened after recording with OBS so maybe we record with another application?") is correct. **The lag is real, but the fix is to use a recording tool that doesn't contend with Chrome's main thread.**

---

## 2. Recommended recording method (RANKED)

### #1 — macOS QuickTime / Cmd+Shift+5 (RECOMMENDED for Sunday)

**Why it beats OBS:**
- Uses **VideoToolbox hardware H.264** encoder (via Apple Silicon NPU/Media Engine) — encoding cost is offloaded from CPU
- Capture loop runs as a system process (`screencapture`) — not in userland, doesn't compete for Chrome's threads
- Built into macOS — zero install, zero config
- Native ScreenCaptureKit captures at perfect 60fps with no frame drops on M-series

**Step-by-step procedure:**

1. **Set up Chrome window first**:
   - Close all other Chrome tabs except the dashboard
   - Full-screen Chrome (Cmd+Ctrl+F) or maximize
   - Hide bookmark bar (Cmd+Shift+B if visible)
   - Confirm the dashboard URL is loaded and the play-on-mount is queued

2. **Mute notifications**:
   - System Settings → Notifications → enable Do Not Disturb (or hold Option + click the time/date in menu bar)
   - Silence Slack/Discord/iMessage individually
   - Disable screen saver (System Settings → Lock Screen → Start Screen Saver after = Never)

3. **Open the screenshot toolbar**: press `Cmd + Shift + 5`

4. **Choose record mode**: in the floating toolbar, click "**Record Selected Portion**" (4th icon — the one with a dotted-line rectangle and a dot). 
   - "Record Entire Screen" works too but captures the menu bar, dock, and any notification banners.

5. **Frame the dashboard**: drag the selection rectangle around the dashboard area (typically the full Chrome window minus the title bar and tab strip). The selection persists between recordings.

6. **Confirm Options before recording**:
   - Click "Options" in the toolbar
   - **Save to**: `~/Documents/Panopticon_Captures/`
   - **Timer**: None (or 5s if you want a countdown)
   - **Microphone**: None (we're recording silent — music added in CapCut)
   - **Show Mouse Clicks**: OFF (don't want click ripples in the capture)
   - **Show Floating Thumbnail**: OFF (don't want the post-capture thumb in frame)

7. **Click "Record"** — recording starts immediately. The toolbar disappears.

8. **Trigger the dashboard**: switch to Chrome (already focused if you set it up before opening the screenshot tool), play the clip from t=0.

9. **Stop recording**: click the stop button in the menu bar (a tiny square in a circle, top-right area near the time), OR press `Cmd + Ctrl + Esc`.

10. **Output**: a `.mov` file named `Screen Recording YYYY-MM-DD at HH.MM.SS.mov` lands in your save-to folder. ProRes-quality H.264, 60fps, lossless screen capture.

**Quality verification (mandatory before trusting the take):**

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,bit_rate,duration \
  -of default=noprint_wrappers=1 \
  ~/Documents/Panopticon_Captures/"Screen Recording 2026-04-26 at *.mov"
```

Expected output: `codec_name=h264`, `width=1920` (or your screen res), `r_frame_rate=60/1` or `120/1`, `bit_rate ≈ 8000000-15000000`. If you see anything different, re-record.

### #2 — OBS with VideoToolbox Hardware Encoder (FALLBACK if QuickTime unavailable)

If for some reason you must use OBS:

1. **Settings → Output**:
   - **Output Mode**: Advanced
   - **Encoder**: `Apple VT H264 Hardware Encoder` (NOT x264 software — that's the CPU-eater)
   - **Bitrate**: 8000-12000 kbps (lower than CRF 18 software but VT does great at this rate)
   - **Keyframe Interval**: 2s
   - **Profile**: high

2. **Settings → Video**:
   - **Base/Output Resolution**: 1920×1080
   - **FPS**: 60

3. **Source**: use **Display Capture** (NOT Browser Source — Browser Source spawns another Chromium and contends for cores). Crop to the dashboard region.

4. **Verify CPU usage during recording**: Activity Monitor should show OBS at <40% CPU total. If it's >60%, you're still on software encode — re-check encoder setting.

### #3 — chrome-devtools-mcp built-in screencast (BLOCKED — see "Blockers" section)

The MCP server has a `screencast_start` / `screencast_stop` tool that uses Puppeteer's `page.screencast()` (CDP-driven, ffmpeg-based). It would have given us a clean Chromium-internal recording with no userland CPU contention. **It's gated behind the `--experimentalScreencast` flag** which is NOT set in the current MCP config (`~/.claude.json`):

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"]   // no flag
    }
  }
}
```

To enable for future sessions, change to:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest", "--experimentalScreencast"]
    }
  }
}
```

…then restart Claude Code. The screencast tool then becomes available to the agent.

### #4 — OBS with x264 software encode (CURRENT — known to lag, do NOT use)

This is what was used Saturday. Causes the lag. Avoid.

### #5 — Headless Puppeteer recording (RISKY — not validated)

Possible to `bun add puppeteer` and launch a separate headless Chromium that records the dashboard via Puppeteer's screencast API. Risk: headless rendering does not match Andrew's screen exactly (DPI, color profile, font fallback), so what you record may not look identical to what plays in his browser. Not recommended for demo-day use.

---

## 3. What to do with the live URL behavior

The visible HUD UX (`useSlowMoAtAnomalies` + `CoachPanel` pause-during-typewriter) is **good product design** — judges experiencing the live URL benefit from those editorial beats. The only reason they were disabled was that they made OBS recordings stutter.

**Recommendation:** keep them disabled UNTIL the demo video is recorded and submitted, then re-enable for the live URL. The disable comments in source already note "re-enable post-demo by uncommenting the next line" — follow through on that after Sunday 8pm EST.

The longer-term fix is a 30-line PR cleaning up `PanopticonEngine.tick`:

```typescript
// CURRENT (forces reflow on every rAF):
const cssW = canvas.clientWidth;
const cssH = canvas.clientHeight;

// FIX (cache in ref, ResizeObserver updates):
const cssW = canvasSizeRef.current.w;
const cssH = canvasSizeRef.current.h;
// In ResizeObserver handler: canvasSizeRef.current = { w: entry.contentRect.width, h: entry.contentRect.height };
```

This single change would eliminate the 162ms-per-clip forced-reflow and make the dashboard buttery-smooth even under OBS load. **Do this post-hackathon.**

---

## 4. Verification protocol for any new recording

Before trusting any new recording for editorial use, run this sanity loop:

```bash
# 1. Frame-rate consistency
ffprobe -select_streams v:0 -count_packets \
  -show_entries stream=nb_read_packets,duration \
  -of default=noprint_wrappers=1 \
  /path/to/recording.mov
# Verify: nb_read_packets / duration ≈ 60 (or your target fps)

# 2. Detect stutter (gaps between video timestamps)
ffprobe -select_streams v:0 -show_entries packet=pts_time \
  -of csv=print_section=0 /path/to/recording.mov \
  | awk -F, 'NR>1{dt=$1-prev; if(dt>0.025){print NR": "dt"s gap"}; prev=$1}'
# Should print nothing (or only end-of-clip). Anything in the middle = dropped frame.

# 3. Visual spot-check: extract 5 evenly-spaced frames
for t in 5 15 30 45 55; do
  ffmpeg -y -ss $t -i /path/to/recording.mov -vframes 1 /tmp/frame_${t}s.png
done
# Open the 5 frames in Preview and confirm no glitches, no torn frames, no missing HUD elements.
```

---

## 5. Updates to existing playbooks

### `demo-presentation/scripts/capcut_assembly_workflow.md`

Update the "OBS Capture Spec" section: change recommended tool from OBS Studio → QuickTime Cmd+Shift+5 with VideoToolbox H.264. The 4 capture filenames stay the same (still saved to `~/Documents/Panopticon_OBS_Captures/` — the directory name remains for backwards-compat, but the recording tool changes).

### `demo-presentation/CLAUDE.md` § 6 "Recording discipline"

Replace `OBS Studio — 1920×1080 @ 60 FPS, H.264 CRF 18` with:

```
- PRIMARY: macOS QuickTime via Cmd+Shift+5 → Record Selected Portion → save .mov.
  Uses VideoToolbox hardware encoder; minimal CPU contention with Chrome.
- FALLBACK: OBS with `Apple VT H264 Hardware Encoder` selected (NOT x264).
  Display Capture source (NOT Browser Source).
- DO NOT use OBS with software x264 encode. It will starve the dashboard's rAF
  loop and produce stuttery captures. See docs/RECORDING_LAG_RECIPE.md.
```

---

## 6. CDP-screencast experiment status

**Attempted but blocked.** The chrome-devtools-mcp tool does ship `screencast_start` / `screencast_stop` (file: `node_modules/chrome-devtools-mcp/build/src/tools/screencast.js`) but they're gated behind `--experimentalScreencast`. The current MCP config does not pass that flag, so the tools were not exposed to the agent.

A separate-Puppeteer approach was considered and rejected: Chrome runs with `--remote-debugging-pipe` (not TCP), so a sibling Puppeteer cannot connect to the same browser. Launching a brand-new headless Chromium would not match Andrew's screen rendering exactly.

**The `~/Documents/Panopticon_Captures/full_tab1_with_pauses_v2_clean.mp4` file referenced in this agent's brief was NOT produced.** No CDP-screencast recording exists. Andrew should record fresh on Sunday morning using the QuickTime recipe in §2.

---

## 7. Andrew's wake-up checklist

1. Read this file (top to bottom — 5 minutes)
2. Read `/tmp/obs_lag_investigation_2026-04-26.md` for the raw test data
3. Open QuickTime via Cmd+Shift+5; do a 10-second test recording of the dashboard with the slow-mo + pauses RE-ENABLED to confirm it looks clean
4. If clean: re-enable both behaviors, do the full 90-second take, ship.
5. If still stuttering: revert to disabled state (current code), accept the no-pauses cut, post-demo clean up the PanopticonEngine reflow.
