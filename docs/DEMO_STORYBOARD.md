# PANOPTICON LIVE — 3-Minute Demo Storyboard

**Target runtime**: 2:55 (5-second safety margin under the 3:00 hard cap).
**Submission deadline**: Sunday 2026-04-26, 8:00 PM EST. Target upload: 7:30 PM EST.
**Founder-voiced**: first-person plural, short sentences, numbers over adjectives, zero hedging.

---

## OBS Recording Setup (Saturday evening, before first take)

| Setting | Value |
|---|---|
| Canvas + output resolution | 1920×1080 |
| FPS | 60 |
| Encoder | Apple VT H.264 hardware, bitrate ~15 Mbps |
| Audio | MacBook Pro built-in mic @ 48 kHz, 320 kbps AAC |
| Browser source | Chromium pointed at the production Vercel URL, window maximized, bookmarks bar hidden, dev tools closed |
| Cursor | `defaults write -g com.apple.mouse.scaling -1` to disable acceleration during recording; system setting "Show location when I move cursor" ON for the pointer ring |
| Mouse-click highlight | Enable Mousepose (or equivalent) — yellow halo on click; only enable for Tab 3 scenes |
| Scene hotkeys | `⌘1` = full HUD tab, `⌘2` = Raw Telemetry tab, `⌘3` = Orchestration Console, `⌘P` = pause recording |
| Pre-record checklist | Close Slack / Mail / Messages / any tab playing audio; lock screen notifications OFF (Focus = "Do Not Disturb"); AirPods out |
| Safe area | Keep all critical copy within 80% center frame; browser chrome fits the outer 10% bezel |

**Audio level target**: peaks at −6 dBFS, noise floor below −50 dBFS. Re-take if peaks clip above −3 dBFS.

**Rehearsal cadence**: 150 words/minute; 1-second pause after each major callout. Rehearse Saturday (2 takes), final Sunday morning (1 keeper take).

**Editing budget**: 2 hours Sunday morning. `ffmpeg -ss ... -to ... -c copy` for cuts; cross-fades `fade=in:0:30,fade=out:st=T:d=1`; no DaVinci unless title cards need compositing.

---

## Four Time-Buckets (founder's exact structure)

Each segment specifies: camera / screen / voiceover (verbatim) / on-screen action / highlight.

---

## 0:00 – 0:30 — The Hook & The Moat

**Segment 1A (0:00 – 0:12) — Cold open on raw broadcast**

- **Camera**: full-bleed Chromium window showing the `utr_match_01_segment_a.mp4` clip playing at 1× on the dashboard home page. **No HUD active yet.** Canvas overlay is invisible. The viewer sees 12 seconds of unedited pro tennis footage — forehand, recovery, bounce.
- **Voiceover (verbatim)**: *"This is a 30-year-old broadcast feed. 2D pixels. No sensors. No wearables. Nothing on the player's body. This is what every other sports-AI company also has access to."*
- **On-screen**: the raw video plays. Nothing else. Let it breathe.
- **Highlight**: we deliberately withhold the UI to make the reveal hit harder.

**Segment 1B (0:12 – 0:22) — HUD snaps on**

- **Camera**: same window. At 0:12 exactly, we snap the Canvas overlay on. Cyan Player A skeleton traces over the athlete. SignalBar stack slides in from the right rail. PlayerNameplate renders top-left.
- **Voiceover (verbatim)**: *"Nobody else is extracting clinical-grade fatigue telemetry from standard 2D broadcast pixels. We are."*
- **On-screen**: 17 COCO keypoints pulsing at 30 FPS, 7 SignalBars animating their baselines. One bar — Recovery Lag — pulses amber as the player returns slow after a wide forehand.
- **Highlight**: the cyan skeleton is the visual anchor. Anyone watching understands instantly that we are reading the body.

**Segment 1C (0:22 – 0:30) — Name the moat**

- **Camera**: pan to the SignalBar column. Full-focus on the 7 stacked bars.
- **Voiceover (verbatim)**: *"Seven biomechanical fatigue signals. Recovery lag, crouch depth, toss precision, court coverage, ritual discipline, court position, reaction timing. All from the pixels. This is our moat."*
- **On-screen**: each SignalBar label briefly lights up in sequence as it's named — 1 second per signal, synced to the VO.
- **Highlight**: the fan-facing labels (not `recovery_latency_ms`) match `dashboard/src/lib/signalCopy.ts` verbatim.

**If this bucket runs long**: cut Segment 1A from 12s to 8s. Compress the cold-open. Do NOT cut the signal-naming cadence in 1C — judges need to hear all 7.

---

## 0:30 – 1:15 — Under the Hood

**Segment 2A (0:30 – 0:45) — The physics engine**

- **Camera**: cut to a split view — left half is the cyan skeleton continuing to track; right half overlays a kinetic trail of the Kalman-smoothed hip position in court meters.
- **Voiceover (verbatim)**: *"The Kalman filter we built operates on physical court meters, not screen pixels. YOLO11m-Pose runs on Apple Silicon MPS. Every signal is physics-grounded — radians, meters, milliseconds. Not vibes."*
- **On-screen**: subtle dimensional labels appear — `0.47 m`, `1.8°`, `612 ms` — tied to the skeleton joints they describe.
- **Highlight**: USER-CORRECTION-008 discipline visible. Meters, not pixels.

**Segment 2B (0:45 – 1:00) — Single-player focus**

- **Camera**: zoom out. The far-court player is deliberately un-tracked. We let the viewer see what we DON'T track.
- **Voiceover (verbatim)**: *"We deliberately scope to one player. The near-court athlete, at full forensic resolution. Moneyball for tennis — one player, deeper than any broadcast commentator can see. Not a toy that half-works on two."*
- **On-screen**: a ghost outline appears briefly around Player B, then fades. Caption subtitle: *"DECISION-008 — single-player scope."*
- **Highlight**: we are honest about scope. That honesty is the story.

**Segment 2C (1:00 – 1:15) — The 3-Pass DAG and the Raw Telemetry tab**

- **Camera**: `⌘2` to Tab 2 "Raw Telemetry." The signal stream scrolls live — timestamped signal emissions, one per line, in a monospace feed.
- **Voiceover (verbatim)**: *"Offline, we run a three-pass DAG. Pass one decodes frames and forward-Kalmans. Pass two runs the RTS backward smoother — zero-lag velocities. Pass three gates signals through the state machine. The smoother compresses peak velocity by 47 percent against forward-only noise. Measured on a real UTR clip."*
- **On-screen**: the raw telemetry feed shows roughly 46 signal emissions scrolling — `recovery_latency_ms: 612`, `crouch_depth_degradation_deg: 1.8`, `baseline_retreat_distance_m: 0.47`, etc. A small badge reads `3-Pass DAG · RTS Smoother`.
- **Highlight**: the 47% number is load-bearing credibility. It is a real measurement from `utr_match_01_segment_a.mp4`, 60s, 1800 frames. Do not round.

**If this bucket runs long**: cut Segment 2A to 10s. Keep 2C at full length — the 47% number is the engineering-craft proof.

---

## 1:15 – 2:30 — The 2030 Vision (The Opus 4.7 Moment)

**Segment 3A (1:15 – 1:27) — The reveal**

- **Camera**: `⌘3` to Tab 3 "Orchestration Console." The screen transitions from scrolling telemetry to a 3-column agent console. Column headers: **Analytics Specialist** · **Technical Biomechanics Coach** · **Tactical Strategist**.
- **Voiceover (verbatim)**: *"To process this telemetry, we built a three-agent Opus 4.7 Multi-Agent Swarm. Real multi-agent reasoning. Real tool use. Real handoffs."*
- **On-screen**: banner at top reads *"ARCHITECTURAL PREVIEW: SWARM ACCELERATED FOR DEMO."* Transport controls visible: Play · Pause · Skip · Replay · [▶ 1× SPEED] toggle.
- **Highlight**: read the banner aloud is optional — let it sit visible on screen. Honesty is the differentiator.

**Segment 3B (1:27 – 1:40) — Why offline, and the honesty frame**

- **Camera**: still on Tab 3. Playback has not started yet.
- **Voiceover (verbatim)**: *"Vercel serverless functions die at 15 seconds. Our real reasoning loop runs 45 to 60. So we capture the full execution trace offline during precompute — thinking, tool calls, tool results, handoffs — and replay it live. This is how the industry will actually ship multi-agent reasoning over the next five years. Cache it. Replay it. Ship it."*
- **On-screen**: a brief diagram overlay: `precompute.py → agent_trace.json → <fetch> → Orchestration Console`. Fades after 6 seconds.
- **Highlight**: the Offline Trace Playback pattern is the technical story. It is not a mock. It is a real architecture.

**Segment 3C (1:40 – 2:00) — Analytics Specialist fires**

- **Camera**: eyes on Column 1. The Analytics Specialist wakes up.
- **Voiceover (verbatim)**: *"The Analytics Specialist queries DuckDB for anomalies. You're watching real Opus 4.7 reasoning replay at baud-rate pacing."*
- **On-screen**: a **thinking** block streams into Column 1 with dim italic text — the agent reasoning about which signal to investigate. Then a **tool_call** pill appears: `compare_to_baseline(player="A", signal_name="crouch_depth_degradation_deg", t_ms=48000)`. Then a **tool_result** pill streams in with a JSON payload: `{ "z_score": 2.7, "delta_pct": 120, "baseline_mean": 1.2, "current_mean": 4.6 }`.
- **Highlight**: the **thinking** token stream is the core Opus 4.7 showcase. Let it run. Do not cut.

**Segment 3D (2:00 – 2:15) — Handoff to Technical Coach**

- **Camera**: a handoff animation — an arrow sweeps from Column 1 to Column 2 with a payload summary ("crouch anomaly z=+2.7 at t=48s"). Column 2 activates.
- **Voiceover (verbatim)**: *"The Technical Biomechanics Coach takes the raw anomaly and grounds it in the literature. Crouch depth degrading 1.8 degrees above baseline means Player A has lost explosive coil. He will arrive late on the next wide return."*
- **On-screen**: Technical Coach's text streams in at ~25 chars/sec — the baud-rate typewriter. Clinical-sounding, grounded prose. Fan-facing labels ("Crouch Depth," not `crouch_depth_degradation_deg`).
- **Highlight**: the cascade is REAL. Each agent's user message contains the prior agent's OUTPUT, per PATTERN-059 Shared Blackboard.

**Segment 3E (2:15 – 2:30) — Tactical Strategist closes**

- **Camera**: handoff animation from Column 2 → Column 3. Tactical Strategist activates.
- **Voiceover (verbatim)**: *"The Tactical Strategist synthesizes a play. Vulnerability: compromised split-step. Exploit pattern: hit behind the player. Watch window: next three service games. Three agents, three orthogonal lenses, one coherent brief. This is the 2030 vision — today."*
- **On-screen**: Final Tactical brief renders as markdown — bold headers, three short paragraphs. The `[>> 4× SPEED]` toggle is briefly clicked at the 2:22 mark to show the judge they can scrub; then reverted to 1×.
- **Highlight**: the `[>> 4× SPEED]` fast-forward is a product feature, not a hack. Call it out visually — mouse-highlight-on-click catches the eye.

**If this bucket runs long**: cut Segment 3B from 13s to 8s (compress the honesty frame). Do NOT cut any of the agent columns — the swarm IS the story.

---

## 2:30 – 3:00 — The Business Case

**Segment 4A (2:30 – 2:42) — Three buyers**

- **Camera**: cut to a clean split-screen — three tiles, each with a one-line pitch and a supporting visual.
- **Voiceover (verbatim)**: *"Three markets buy this. Broadcasters, who want every match to feel like Game 7. Sports betting syndicates, who want live edge from biomechanics. Elite coaching, for post-match opponent scouting. Same engine. Three revenue streams."*
- **On-screen tile 1 (Broadcasters)**: ESPN-style chyron mockup, player nameplate with live Recovery Lag value. Caption: *"Broadcast."*
- **On-screen tile 2 (Betting)**: a raw JSON tick — `{ "recovery_latency_ms": 1420, "z_score": 2.7, "t_ms": 48000 }` — styled like a Bloomberg terminal. Caption: *"Live Edge Signals."*
- **On-screen tile 3 (Coaching)**: the Tactical Strategist markdown from Segment 3E, formatted as a post-match PDF scouting report. Caption: *"Post-Match Intelligence."*
- **Highlight**: three tiles on-screen simultaneously. Scan-left-to-right pacing.

**Segment 4B (2:42 – 2:52) — Engineering evidence**

- **Camera**: cut to a full-width text card on black.
- **Voiceover (verbatim)**: *"Solo-built in six days. Five hundred and sixteen tests passing. TypeScript strict mode clean. Next.js production build compiles in 1327 milliseconds. Open source. MIT."*
- **On-screen text (centered, monospace)**:
  - `516 tests passing`
  - `434 Python · 82 TypeScript`
  - `Zero regressions`
  - `Next.js 16.2.4 · 1327ms build`
  - `MIT licensed · github.com/andydiaz122/panopticon-live`
- **Highlight**: numbers > adjectives. The build-time number is unforgettable because it is specific.

**Segment 4C (2:52 – 3:00) — Drop-mic close**

- **Camera**: fade to the closing title card. Black background. Logo centered. URL underneath, visible for the full 8 seconds.
- **Voiceover (verbatim)**: *"Panopticon Live. The sensor didn't exist. So we built it."*
- **On-screen text**:
  - `PANOPTICON LIVE`
  - `panopticon-live.vercel.app`
  - `github.com/andydiaz122/panopticon-live`
  - `Built with Claude Opus 4.7 · Anthropic × Cerebral Valley Hackathon 2026`
- **Highlight**: URL must be legible for 2+ seconds. Do not animate it. Static text. Let it sit.

**If this bucket runs long**: cut Segment 4B to 7s (drop one line from the engineering list — keep tests-passing and build-time). Never cut 4C; the drop-mic is the last thing the judge hears.

---

## Post-Record Submission QA

- [ ] Final runtime ≤ 2:55 (`ffprobe -v error -show_entries format=duration demo.mp4`)
- [ ] 1920×1080, 60 FPS, H.264, ~15 Mbps, AAC 320 kbps
- [ ] Audio peaks ≤ −6 dBFS; noise floor ≤ −50 dBFS
- [ ] All four required phrases spoken OR visible: "Multi-Agent Swarm," "Offline Trace Playback," "2D Broadcast Pixels," "Biomechanical Fatigue Telemetry"
- [ ] "ARCHITECTURAL PREVIEW: SWARM ACCELERATED FOR DEMO" banner visible for the full duration of the Orchestration Console segment (1:15 – 2:30)
- [ ] `[>> 4× SPEED]` toggle visibly demonstrated (Segment 3E)
- [ ] Closing URL visible for ≥ 2 seconds
- [ ] Zero notifications, popups, or dev tools visible in any frame
- [ ] Zero emojis in any text overlay (per hackathon-demo-director skill)
- [ ] YouTube uploaded unlisted, title = *"PANOPTICON LIVE — Biomechanical Fatigue Telemetry from 2D Broadcast Pixels | Built with Opus 4.7 Hackathon"*
- [ ] Submit to CV platform by 7:30 PM EST (30-minute buffer under the 8:00 PM deadline)
