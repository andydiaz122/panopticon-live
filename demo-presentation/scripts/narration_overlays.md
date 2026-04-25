# Narration Overlay Script — Path C Detective Cut + DECISION-019 Closing Thesis

**Version**: locked 2026-04-25 ~04:00 EDT
**Total overlays**: 6 timed text inserts (B1-B4) + 0 in B0 + 1 dedicated thesis card after B5
**Voiceover**: ELIMINATED per §5.5.2 — every line below is a TEXT OVERLAY, not spoken narration
**Use this in DaVinci Resolve** to author the on-screen text inserts during the Saturday composite.

---

## Visual styling for ALL B1-B4 overlays

Match the §5.5.2 spec verbatim:
- **Font**: monospace (JetBrains Mono or system mono fallback)
- **Size**: 14 px relative (≈18-20 pt in DaVinci at 1080p)
- **Position**: bottom-third of frame (broadcast subtitle position) — y ≈ 80%
- **Color**: `#F8FAFC` on a thin `#05080F` strip (so the text reads against any video frame)
- **Animation**: 400 ms fade-in → 600 ms hold → 400 ms fade-out (1.4 s total per overlay)
- **Letter-spacing**: `+0.04 em` (matches our HUD register)
- **Case**: lowercase preferred (per the §5.5.2 mapping table) — feels analytical, not promotional

DaVinci tip: build ONE Fusion text template with these params, then duplicate per overlay and swap the text. Saves time vs styling six separately.

---

## The 6 overlays + 1 thesis card

### B0 — The Personal Journey Opener (0:00 – 0:25)

> **NO OVERLAYS HERE.** B0 is already the most narrative-dense beat. The typing animation ("Hey Claude, is the world malleable?" → "yes — build what you need") + GitGraph timelapse + "Panopticon Live" wordmark IS the narration. Adding overlay text on top would compete with the typing animation for the same eye attention. Per Andrew's confirmed direction Q3, leave it alone.

### B1 — The Miss (0:25 – 0:43)

| Overlay # | Cue (final cut) | In | Out | Text |
|---|---|---|---|---|
| **#1** | After clip pauses on the anomaly frame; Vision-Pass overlay visible | **0:35.000** | 0:36.400 | `flagged · frame 1,359 · σ 2.5 crouch-depth anomaly` |

**Visual placement note**: B1's hero frame is the Vision-Pass annotated pose overlaid on the paused video. Place the text overlay BELOW the annotation so they don't compete. The overlay grounds the visual proof with a number.

### B2 — The Sensor (0:43 – 1:00)

| Overlay # | Cue (final cut) | In | Out | Text |
|---|---|---|---|---|
| **#2** | HUD snap-in begins; SignalBars + tickertape become visible | **0:43.500** | 0:44.900 | `yolo11m-pose · kalman on court meters · 7 biomech signals` |
| **#3** | `.claude/skills/` file tree flash appears bottom-left | **0:53.000** | 0:54.400 | `12 skill packs · 2d pixels → clinical telemetry` |

### B3 — The Second Miss (1:00 – 1:40)

| Overlay # | Cue (final cut) | In | Out | Text |
|---|---|---|---|---|
| **#4** | At t≈59.1s in clip, Crouch Depth SignalBar flashes red the second time | **1:00.500** | 1:01.900 | `recurring · Δ −11.69° · 13.8 s apart · fatigue pattern locked` |
| **#5** | Switch to Tab 2 (Raw Telemetry) — firehose visible AND the Download CSV button is now in frame top-right | **1:15.000** | 1:16.400 | `proprietary stream · every signal, every state — downloadable as .csv` |

**Why overlay #5 is updated from §5.5.2**: per DECISION-019, the FINAL PRODUCT is the downloadable data file. Tab 2's Download CSV button is now the tangible artifact. The narration should explicitly call this out — judges who read the overlay land on the realization that this isn't just a dashboard, it's a data-extraction platform.

### B4 — Opus Reads the Body (1:40 – 2:40) — THE CLIMAX

| Overlay # | Cue (final cut) | In | Out | Text |
|---|---|---|---|---|
| **#6** | "Opus thinking…" button state appears; ThinkingVault component opens in split-screen | **1:40.500** | 1:41.900 | `opus 4.7 · adaptive thinking · cached system prompt` |
| **#7** | THE FRAME — Rejected Thought chip flashes; right-pane thinking cites `-11.69°` | **2:08.000** | 2:09.400 | `✗ serve-mechanics hypothesis rejected — crouch preceded toss by 8.2 s` |

**Overlay #7 is the highest-stakes overlay**. It must land in sync with the Rejected Thought chip flash. If they're 200ms out of sync, the magic breaks.

### B5 — Brand Card (2:40 – 2:54)

> **NO ADDITIONAL OVERLAYS.** The B5Closing Remotion composition (`b5-closing.mp4`) already contains its own typography — Fraunces "Panopticon Live" wordmark, URL, repo, attribution. Adding overlay text on top would create chrome-on-chrome.

### B5b — Closing Thesis (2:54 – 2:58)

> **NO MANUAL OVERLAY NEEDED.** The B5Thesis Remotion composition (`b5-thesis.mp4`) IS the overlay. Pure #000 void background + Fraunces serif "capture the signal nobody else is reading." Hard cut from B5's brand card to this composition. 4-second hold.

> Per DECISION-019, this thesis card is the demo's closing argument. The register switch from B5's cool-slate brand register → B5b's pure void thesis register is what makes the thesis LAND as a thesis rather than additional brand chrome (PATTERN-083).

---

## Total runtime check

```
B0:   0:00 – 0:25   (25 s)   [no overlays]
B1:   0:25 – 0:43   (18 s)   [overlay #1 at 0:35]
B2:   0:43 – 1:00   (17 s)   [overlays #2, #3]
B3:   1:00 – 1:40   (40 s)   [overlays #4, #5]
B4:   1:40 – 2:40   (60 s)   [overlays #6, #7 — climax]
B5a:  2:40 – 2:54   (14 s)   [no manual overlay — B5Closing.mp4 self-contained]
B5b:  2:54 – 2:58   (4 s)    [B5Thesis.mp4 — closing thesis]
═══════════════════════════════════════════════════════════════
TOTAL: 2:58 (2 s margin under 3:00 hard cap) ✅
```

---

## DaVinci Resolve workflow (Saturday morning)

1. **Build the text template ONCE**: in Fusion, create a node tree (Text+ → Background → Merge) styled per the spec above. Save as a Macro called "PanopticonOverlay".
2. **Drop on timeline**: drag the Macro onto the timeline at each In timecode from the table. Set duration = 1.4 s.
3. **Edit the text per overlay**: double-click each instance, change just the text string from the table.
4. **Render check**: scrub through each overlay to confirm fade-in/hold/fade-out feels right relative to the underlying video event.

If Fusion feels heavy, the Edit page's built-in Text+ generator (drop on V2/V3 track) also works — same visual params (size 18-20pt, +0.04em letter-spacing, fade-in/out keyframes on Opacity).

---

## What if Andrew wants to record voiceover anyway (fallback)

Per §5.5.2 voiceover was eliminated, but if Andrew changes his mind during recording, the same 6 lines + thesis can be SPOKEN without retiming. Fits ~5-10 seconds total of speech across the 2:58. Suggested cadence: measured, calm, deliberate (Tim Cook at WWDC), not sportscaster-emoting. Keep mic-off in the silent beats (B0 typing, B5 hold, B5b void) — the visuals carry those moments.

---

## Open follow-ups

- **Overlay #5's text** ("downloadable as .csv") presumes the Download CSV button is visible when the overlay appears. Confirm during DaVinci composite that the timing aligns — if Tab 2 hasn't fully loaded when overlay fires, push the timecode 1-2 s later.
- **Overlay #7's exact timecode** (2:08.000) depends on when the Rejected Thought chip actually flashes in the OBS capture. Adjust ± 500 ms during DaVinci to land on the chip.
- **Font choice in DaVinci**: prefer JetBrains Mono if installed; fall back to SF Mono / Menlo / Consolas if not. Matches the dashboard's HUD register.
