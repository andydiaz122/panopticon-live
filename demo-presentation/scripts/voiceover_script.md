# ⚠️ DEFERRED — Voiceover Script (NOT shipping in v1 demo)

> **Status as of 2026-04-25 ~20:41 EDT**: Andrew made the executive decision to
> SKIP voice-over entirely for the v1 hackathon submission (less than 24 hours
> to deadline). Music bed now carries the audio. This script is preserved
> verbatim for: (a) potential v2 / post-hackathon enhancement, (b) reference
> for what facts the silent visuals + on-screen text would need to convey
> if we add subtle text overlays in CapCut, (c) the pacing math (165 wpm,
> ~37s spoken total) which is still useful for sanity-checking music duration.
>
> **DO NOT record this audio for the v1 submission.** The CapCut assembly
> workflow has been updated to remove the voice track entirely. See
> `capcut_assembly_workflow.md` for the music-only audio mix.
>
> **If we revisit voice for a v2 cut**, the closet sound booth setup + 12-line
> structure below is still the right approach — just unlock by removing this
> banner and re-engaging the recording protocol.

---

# Voiceover Script — PANOPTICON LIVE Demo (Anthropic Minimalism Pivot)

**Authored:** 2026-04-25 ~05:50 EDT — incorporating team-lead pivot away from
Remotion-heavy presentation toward Anthropic-minimalism (static title cards +
clinical disembodied VO + pristine OBS captures, assembled in CapCut Desktop).

**Recording target:** Saturday 2026-04-25, 13:00–14:00 EDT.

**Total spoken time:** ~37 seconds across 12 lines (script designed so visuals
breathe — ~2:23 of the 3:00 video is product footage carrying its own weight,
which is the Anthropic-release-video discipline).

> ⚠️ **TIMING SHIFT 2026-04-25 ~10:45 EDT** — the opener was changed from
> static title cards (15s) to a live typing intro + terminal precompute capture
> (30s). **All L1-L12 timings shift forward by +15s** vs the table below.
> Use the updated timing table at the end of this doc when placing VO clips
> in CapCut. The line content + cadence + tone is unchanged — only the
> on-timeline POSITION shifts.

---

## Tone & Performance Notes (read these BEFORE the first take)

- **Register:** Tim Cook at WWDC describing a feature. Forensic analyst delivering
  findings to a client. NOT a sports broadcaster, NOT a SaaS sizzle-reel narrator.
- **Pace:** ~165 words/minute. Slower than conversational. Deliberate. Allows
  every word to land.
- **Pauses:** Full beat (~600ms) between sentences. Half beat (~300ms) at commas.
- **Emphasis:** Italics in the script below mark the operative word — the one
  unexpected qualifier carrying the meaning. Lean ~20% harder on those words,
  but do NOT shout. The contrast is in cadence, not volume.
- **Breath:** Inhale BEFORE you start each line. Don't catch breath mid-sentence.
- **Posture:** Stand if possible. Voice projects better than seated.

## Recording Setup

- **Mic:** iPhone Voice Memos (built-in mic) OR Mac built-in mic via
  QuickTime → New Audio Recording. Both are fine. Avoid USB headset mics
  unless you have a Yeti — they color the voice.
- **Room:** Walk-in closet full of hanging clothes. Stand in the middle. The
  clothes absorb reflections. This is the proven "amateur sound booth" the
  team lead mentioned, and it works as well as a $400 isolation shield.
- **Distance:** 6 inches from mouth, mic angled ~30° off-axis (point past
  your cheek, not directly at your lips) — kills plosives on "P" and "B" sounds.
- **Levels:** Aim for peaks at -12 dBFS. If your loudest word clips, back off
  the mic. If your quietest word is below -30 dBFS, get closer.
- **Multiple takes:** Record EACH LINE 3 times, picking the best in CapCut. Do
  NOT try to nail the whole script in one take — burnout shows in the voice.
- **Listen back IMMEDIATELY** with headphones. If you hear room noise, mouth
  clicks, sibilance — re-record now while you remember the cadence, not later.
- **Silent room is mandatory:** Close the closet door. Turn off any HVAC,
  fans, dehumidifiers. Phone on Do Not Disturb. Computer fan can be a problem
  — record on the iPhone instead if your Mac is loud.

## Post-Processing in CapCut (do this AFTER recording, BEFORE assembly)

1. Import VO audio
2. Apply CapCut's built-in **Voice Enhancement** filter (one click — handles
   noise reduction + light EQ + leveling automatically)
3. If needed: **High-pass filter at 80 Hz** to cut rumble
4. **Normalize to -16 LUFS** integrated loudness (broadcast standard for spoken
   content; gives ~6 dB of headroom for music underneath)
5. Slice each line into a clip; you'll position them precisely against the
   video timeline in the assembly stage

---

## The Script — 12 Lines, Distributed Across 5 Beats

> Words in *italics* get gentle emphasis. Words in **bold** are mini-pauses.
> Lines marked **[silent]** are visual-only beats (no VO at all).

---

### Beat 1 — The Philosophical Hook (0:00 – 0:15) **[silent]**

No voiceover. The two title cards speak for themselves with keyboard-typing
SFX underneath. (See `title_card_specs.md` Card 1 + Card 2.)

---

### Beat 2 — The Cold Open / The Moat (0:15 – 0:45)

**L1** *(0:18 – 0:21)*
"The sports analytics market is worth *billions*."

**L2** *(0:24 – 0:28)*
"But everyone is looking at the *exact same* broadcast data."

**L3** *(0:32 – 0:37)*
"We built Panopticon Live to capture the signal *nobody else* is reading."

*Visual underneath: raw tennis broadcast → skeleton snaps on → anomaly bar pulses red.*

---

### Beat 3 — The Panopticon Engine (0:45 – 1:45)

**L4** *(0:48 – 0:52)*
"Built in *five days* with Claude Code."

**L5** *(0:58 – 1:01)*
"*Seven* proprietary biomechanical fatigue signals."

**L6** *(1:08 – 1:13)*
"Extracted directly from *standard* 2D broadcast pixels."

**L7** *(1:22 – 1:28)*
"No hardware. **No depth cameras.** Just *Apple Silicon*."

*Visual underneath: full 2K-Sports HUD, smooth deliberate navigation across
Tab 1 — SignalBars pulse, skeleton tracks, tickertape ticks. Long stretches of
silence between lines so the HUD breathes.*

---

### Beat 4 — The Final Product & The Swarm (1:45 – 2:45)

**L8** *(1:48 – 1:52)*
"The dashboard is *just* the showcase."

**L9** *(1:56 – 2:00)*
"The final product is the *raw telemetry*."

**L10** *(2:10 – 2:16)*
"Behind it: a Managed Agent swarm — *analytics, biomechanics, strategy*."

**L11** *(2:22 – 2:29)*
"They capture the *qualitative story* of what happened in the previous point."

**L12** *(2:35 – 2:39)*
"Grounded in the *physics*."

*Visual underneath: hard cut to Tab 2 → mouse moves to "Download Match Data
(.csv)" button → click → file downloads animation → hard cut to Tab 3 → swarm
trace replay plays through a single point's reasoning chain.*

---

### Beat 5 — The Exit (2:45 – 3:00) **[silent]**

No voiceover. The closing title card carries the thesis (white serif on void
+ cyan github URL underneath). Final musical chord sustains for the full 15s
and decays into 1-2 seconds of silence after the YouTube cut. (See
`title_card_specs.md` Card 3.)

---

## Total Word Count + Timing Audit

| Beat | Lines | Word count | Spoken time | Visual breathing room |
|---|---|---|---|---|
| Beat 1 | 0 | 0 | 0s | 15s |
| Beat 2 | 3 | 30 | ~11s | ~19s |
| Beat 3 | 4 | 26 | ~10s | ~50s |
| Beat 4 | 5 | 38 | ~14s | ~46s |
| Beat 5 | 0 | 0 | 0s | 15s |
| **TOTAL** | **12** | **94** | **~35s** | **~145s** |

**Ratio of voice to silence: 19% / 81%.** This is intentional and matches the
Anthropic standard. The VO is scaffolding; the product is the demo.

---

## Stretch Lines (Use ONLY if you find dead air during assembly)

If a beat feels too long without voice and you can't trim the OBS capture, use
ONE of these to fill — but err on the side of MORE silence, not less.

- "Same broadcast feed. Different signal." *(use after L3 if Beat 2 lags)*
- "Every frame, every player." *(use after L6 if HUD walkthrough drags)*
- "From pixels to physiology." *(use after L7 as a closing flourish)*

Do NOT add these by default. Silence is the strongest editorial choice.

---

## What NOT to Say (Compliance with `demo-presentation/CLAUDE.md` §3.3)

- ❌ "Watch this", "here's where it gets interesting", "the legs are going" —
  no theatrical setup phrases
- ❌ "Opus thinks live" — false (it's pre-computed; the trace replays)
- ❌ "AI predicts the next point" — we don't ship predictive models
- ❌ "Real-time" — the dashboard plays a pre-computed match; do not imply live
- ❌ Any sports broadcaster cadence ("incredible!", "watch as he…", "look at that")

---

## Reference: Why This Script Works

- **Information per word:** every line carries a fact, a number, or a mechanism
  (5 days, 7 signals, 2D pixels, 3 agents, Apple Silicon, qualitative story).
- **No hedging:** "Built in five days." Not "We essentially built this in roughly
  five days." Confidence reads as competence.
- **Buried lede on the agent swarm:** the reveal that there's a Managed Agent
  swarm under the dashboard hits at 2:10 — saved for the back half so judges
  thinking "another HUD demo" get a second-act surprise.
- **Closing on physics:** L12 ("Grounded in the physics.") deliberately ends on
  the word that distinguishes us from every other LLM-only sports analytics
  pitch. Physics = the moat.

---

**Author this voice with calm authority. The product is brilliant. Let your
voice tell the judges you know it.**

---

## 📍 UPDATED Timeline Positions (post-2026-04-25 opener pivot)

The new opener (live typing 22s + terminal precompute 5s + visual breath 3s
= 30s total) replaces the old static-card opener (15s). **VO lines shift
forward by ~15s.** Beat 3 (HUD walkthrough) compressed from 60s → 50s; Beat 4
compressed from 60s → 55s. Use these positions in CapCut, not the old
timestamps in the script body above.

| Line | OLD timestamp (pre-pivot) | NEW timestamp (use this in CapCut) | Beat |
|---|---|---|---|
| L1 | 0:18 – 0:21 | **0:33 – 0:36** | Beat 2 cold open |
| L2 | 0:24 – 0:28 | **0:39 – 0:43** | Beat 2 |
| L3 | 0:32 – 0:37 | **0:47 – 0:52** | Beat 2 |
| L4 | 0:48 – 0:52 | **1:03 – 1:07** | Beat 3 HUD walkthrough |
| L5 | 0:58 – 1:01 | **1:11 – 1:14** | Beat 3 |
| L6 | 1:08 – 1:13 | **1:21 – 1:26** | Beat 3 |
| L7 | 1:22 – 1:28 | **1:35 – 1:41** | Beat 3 (closing flourish) |
| L8 | 1:48 – 1:52 | **1:55 – 1:59** | Beat 4 CSV download |
| L9 | 1:56 – 2:00 | **2:03 – 2:07** | Beat 4 |
| L10 | 2:10 – 2:16 | **2:18 – 2:24** | Beat 4 swarm reveal |
| L11 | 2:22 – 2:29 | **2:30 – 2:37** | Beat 4 |
| L12 | 2:35 – 2:39 | **2:40 – 2:44** | Beat 4 (close) |

**Visual landing notes** (for fine-tuning during CapCut assembly):
- L1-L3 land during the cold-open OBS B1 capture (anomaly pulse)
- L4-L7 land during the OBS B2 huddrop capture (HUD walkthrough)
- L8-L9 land at/around the CSV download click (OBS B3)
- L10-L12 land during the Tab 3 swarm replay (OBS B4)
- The 2:45-2:48 black hold + 2:48-3:00 closing card play in **silence** —
  no VO from L12 onward. The closing thesis card "speaks for itself" per
  Anthropic-Minimalism doctrine.

If your recorded VO lines drift slightly from these targets (you might speak
faster or slower than the 165 wpm assumed pace), adjust positions in CapCut
to land each line on a thematically relevant visual moment, not on the exact
millisecond.
