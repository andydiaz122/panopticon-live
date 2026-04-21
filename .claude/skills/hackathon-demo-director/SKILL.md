---
name: hackathon-demo-director
description: 3-minute demo video storyboard, pacing, recording discipline, and submission QA for the PANOPTICON LIVE hackathon. Use when writing the video script, recording takes, editing, or preparing Sunday 8pm EST submission materials.
---

# Hackathon Demo Director

The 3-min demo video IS the product for judges. This skill encodes the narrative structure, recording discipline, and submission checklist.

## The 5-Scene Storyboard (3:00 hard cap)

### Scene 1 (0:00-0:30) — The Hook
**Goal**: Immediate visual punch. Judge decides within 15 seconds if they're watching.

- Cold open: pro tennis clip (muted) with skeleton overlay already tracing
- Fade in 2K-Sports HUD: player nameplates, FATIGUE meter, POWER meter, FOOTWORK meter
- Title card overlay: *"PANOPTICON LIVE"*
- Subtitle: *"Biomechanical intelligence from broadcast video"*
- Narration (spoken): "This is what a tennis broadcast looks like when you can read every player's body in real time."

**Must-have frame**: at least one clear anomaly indicator pulsing red (fatigue spike) within first 20 seconds.

### Scene 2 (0:30-1:15) — The Opus Moment
**Goal**: Show Opus 4.7 reasoning visibly. Differentiates us from every other hackathon project.

- Zoom into Opus Coach panel
- A rally plays; Opus's `extended_thinking` tokens stream into a collapsible panel — **viewer sees the tokens appear in real time**
- Then the coach commentary resolves: *"Alcaraz's crouch depth has degraded 1.8° — predict cross-court forehand next."*
- Beat later: the player actually hits cross-court. **Prediction confirmed visually.**
- Narration: "That was Opus 4.7 reasoning about biomechanical state and producing a shot prediction before the shot landed."

**Must-have frame**: clear visible `thinking` tokens. This is THE Opus moment.

### Scene 3 (1:15-2:00) — The Generative UI
**Goal**: "Opus didn't just code this, it designed it." Targets the Creative Opus Exploration prize.

- Match phase changes (serve → rally → break)
- Show HUD layout **re-compose itself**: widgets slide out, new widgets slide in
- Split-screen overlay: *"Opus layout at 12:31:47"* vs *"Opus layout at 12:32:03"*
- Narration: "The HUD layout itself is being designed live by Opus 4.7 — responding to what matters in the match."

**Must-have frame**: two side-by-side HUD states proving the layout changed.

### Scene 4 (2:00-2:30) — The Signal Feed (Business Story)
**Goal**: This is not a toy — this is a B2B product.

- Click the "Signal Feed" tab
- Raw JSON streams with syntax highlighting
- Caption: *"This is what Valence, Sequence, Dome — the YC-funded prediction market layer — subscribes to."*
- Narration: "The visual HUD on the other tab is one surface. The underlying signal is the moat."

**Must-have frame**: visible JSON stream with biomechanical signal fields.

### Scene 5 (2:30-3:00) — The Close
**Goal**: Close strong. Judge remembers the last thing they saw.

- Architecture diagram (1 static frame): YOLO → state machine → signals → Opus → HUD
- Live scouting-report generation demo (sped up 8x) — shows Managed Agents chip
- Tagline text crawl: *"Built from scratch in 6 days. Entirely on Claude Code. Opus 4.7 didn't just help code it — it designed it, reasons inside it, and speaks through it."*
- Closing card: *"panopticon-live.vercel.app · github.com/andydiaz122/panopticon-live"*

**Must-have frame**: the URL visible for 2+ seconds at the end.

## Recording Discipline

### OBS Setup (Saturday evening)
- 1920×1080 @ 60 FPS recording
- Browser source: Chromium at production URL (maximize window, hide bookmarks bar)
- Audio: MacBook Pro mic at 48kHz, minimal post-processing
- Hotkeys: scene switch on `⌘1 / ⌘2 / ⌘3`; pause recording on `⌘P`
- Scene list:
  1. Dashboard full-screen (the HUD view)
  2. Dashboard Signal Feed tab
  3. Architecture diagram static slide
  4. Title card static slides (intro + close)

### Rehearsal Protocol
- **Saturday evening**: 2 full-length rehearsal takes (stop and re-start if obvious stumble)
- **Sunday morning**: 1 final take with intention to keep
- **Pacing target**: 150 words/minute; pause 1 second after each major callout
- **Authentic > polished**: minor stutters stay; critical glitches trigger reshoot

### Editing (Sunday morning, 2-hour budget)
- `ffmpeg` for clean cuts: `ffmpeg -i raw.mp4 -ss HH:MM:SS -to HH:MM:SS -c copy clip.mp4`
- Simple fades between scenes: `-vf "fade=in:0:30,fade=out:st=T:d=1"`
- DaVinci Resolve Lite only if title cards need compositing
- Export: H.264 MP4, 1920×1080, bitrate ~15 Mbps, audio AAC 320kbps
- Cap total length at 2:55 (5s safety margin under 3:00 hard cap)

### Upload
- YouTube channel: Andrew's primary (andydiaz122 handle if possible)
- Title: *"PANOPTICON LIVE — Biomechanical Intelligence for Pro Tennis | Built with Opus 4.7 Hackathon"*
- Description template:
  ```
  Built for the Anthropic × Cerebral Valley "Built with Opus 4.7" hackathon (April 21-26, 2026).
  
  PANOPTICON LIVE extracts biomechanical fatigue signals from pro tennis broadcast video and renders them as a 2K-Sports-style HUD powered by Claude Opus 4.7 as Reasoner, Designer, and Voice.
  
  🎯 Live demo: https://panopticon-live.vercel.app
  📦 Source: https://github.com/andydiaz122/panopticon-live
  🧠 Model: claude-opus-4-7 with extended thinking, tool use, prompt caching, and Managed Agents
  ⚙️ Tech: Next.js 16 · FastAPI · DuckDB · YOLO11m-Pose · Ultralytics · filterpy · scipy
  
  Built by Andrew Diaz (andrewdiaz.io) with Claude Code.
  ```
- Visibility: **unlisted** (safer for hackathon; Andrew can toggle public later)

## Written Summary (100-200 words)

Draft template (must be revised with final facts):

```
PANOPTICON LIVE is a video-game HUD for pro tennis. It extracts 7 biomechanical fatigue signals from pro tennis broadcast video — recovery latency, serve-toss variance, ritual entropy, crouch depth degradation, baseline retreat, lateral work rate, split-step latency — and streams them to a 2K-Sports-style overlay over live footage.

Claude Opus 4.7 plays three roles: Reasoner (extended thinking over deterministic signal-query tools, with visible thinking tokens streamed to the UI), Designer (generative UI — it dynamically composes the HUD layout based on match state), and Voice (coach-register commentary streamed via SSE). A Claude Managed Agent generates full PDF scouting reports.

Built from scratch in 6 days on Claude Code, using Ultralytics YOLO11m-Pose on Apple Silicon MPS, Kalman occlusion smoothing via filterpy, Lomb-Scargle spectral analysis for ritual entropy, homography-based court mapping, DuckDB for pre-computed signal storage, and Next.js 16 on Vercel for the dashboard. The demo is the product — what you'd see if tennis prediction markets had ESPN-grade biomechanical telemetry.
```

Word count: ~200. Trim to 150-180 for submission.

## Submission Checklist (Sunday by 8pm EST)

- [ ] Production Vercel URL verified live (`curl -I` returns 200)
- [ ] Demo video rendered, under 3:00, 1920×1080, H.264 MP4
- [ ] YouTube uploaded (unlisted), URL copied
- [ ] GitHub repo public
- [ ] README.md updated with live URL + architecture diagram + 1-paragraph description
- [ ] LICENSE file is MIT
- [ ] 100-200 word written summary drafted
- [ ] Submit via CV platform (https://cerebralvalley.ai/events/built-with-4-7-hackathon)
- [ ] Screenshot of submission confirmation → `FORANDREW.md` → commit
- [ ] Post-submit: social (X, LinkedIn) via `social-content` skill

## Hard No-Gos

- ❌ Over-produced (judges smell over-editing)
- ❌ Emoji overload (zero emojis in text overlays — keep it pro-broadcast)
- ❌ Music licensing risk (use royalty-free or silent; NEVER popular tennis-broadcast music)
- ❌ Reading from script robotically (one rehearsal confirms cadence)
- ❌ Submitting at 7:59pm EST (leave 30 min buffer; target 7:30pm EST)
