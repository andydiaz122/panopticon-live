# Intro Typing Script — Live Claude UI Recording

**Authored:** 2026-04-25 ~10:45 EDT — supersedes the static Card 1 + Card 2
opener per team-lead pivot.

**Recording target:** Saturday 2026-04-25, 11:00 EDT (first thing in your
recording block — even before OBS dashboard captures).

**Tool:** macOS QuickTime Player → File → New Screen Recording → record selected
portion (the Claude UI window).

**Duration target:** 22 seconds of usable footage. Record 30-45 seconds raw
(give yourself buffer); trim in CapCut to the cleanest 22-second take.

---

## Why this exists (read once, then forget)

You and the team lead pivoted from the static Q+A Anthropic-Minimalism cards
("Hey Claude, is the world malleable?") to a LIVE TYPING intro that
demonstrates the iterative refinement of a real engineering prompt. The
narrative arc IS the journey: naive predictor → tennis-specific → broadcast-
video → biomechanical-signal-extraction. Visually showing Andrew's thinking
shift from "predictor" (wrong attack vector per DECISION-019) to "extractor"
(the actual moat) targets the **$5,000 "Keep Thinking" prize** explicitly.

The 4-stage prompt evolution is the entire point. Don't over-rehearse — the
organic struggle (typos, backspaces, brief pauses) IS the authenticity signal.
Programmatic Remotion typing was VETOED for this reason.

---

## Setup Checklist (5 minutes BEFORE recording)

- [ ] **Browser:** Chrome (full-screen, hide bookmarks bar `Cmd+Shift+B`)
- [ ] **URL:** `https://claude.ai/new` (fresh chat thread, blinking cursor in input box)
- [ ] **Account:** logged in as Andrew (paid tier — shows the "Claude Sonnet 4.6 / Opus 4.7" model selector subtly in the corner; that's free advertising for the hackathon's host)
- [ ] **Theme:** **dark mode** (matches the Panopticon dashboard aesthetic; clean visual continuity into the dashboard scenes that follow)
- [ ] **Window size:** maximize the window so QuickTime captures the full Claude UI
- [ ] **Notifications OFF:** Do Not Disturb on macOS so no Slack/iMessage banners crash the take
- [ ] **All other Chrome tabs:** CLOSED (don't want extension popups or favicon noise visible)
- [ ] **System sound:** muted (not strictly required, but keystroke audio comes from your laptop mic anyway)
- [ ] **Microphone:** **ON** during screen recording (per team-lead directive — real MacBook keyboard clacks sound infinitely more authentic than stock SFX added later. In QuickTime Screen Recording → click the down-chevron next to the record button → select "MacBook Pro Microphone")
- [ ] **Recording area:** "Record Selected Portion" → drag a rectangle around just the Claude UI (skip macOS chrome, browser tabs — keeps the visual clean)

---

## The 4-Stage Prompt Script

> Type these IN-PLACE in the Claude input box. Each stage REPLACES the previous
> via deletes/backspaces — it's ONE evolving prompt, not 4 separate messages.
> Hit ENTER only ONCE, after Stage 4 is complete.

### Stage 1 (the naive ask) — type all chars, then PAUSE 2-3 sec

```
hey claude, build me a predictive model
```

*39 chars · ~8 sec organic typing · then PAUSE briefly, like you're thinking*

**Cadence note:** Type at your natural pace. Tiny hesitations are fine. If you
backspace a typo, leave it in.

---

### Stage 2 (gets sport-specific) — append " for tennis", then PAUSE 1-2 sec

After the pause from Stage 1, just keep typing — append `" for tennis"` to the
end. Don't delete anything yet.

```
hey claude, build me a predictive model for tennis
```

*Adds 11 chars · ~3 sec organic typing · then PAUSE briefly*

**Cadence note:** This addition shows you specifying a domain. Quick beat.

---

### Stage 3 (gets technical about input) — significant rewrite

After the Stage-2 pause, START BACKSPACING. Delete back to `"hey claude, build
me a "` (keep through "a "). Then type the new ending:

```
hey claude, build me a model that predicts tennis matches from broadcast video
```

*Backspace ~28 chars (~3 sec), type ~55 chars (~12 sec), total ~15 sec · then PAUSE 2-3 sec*

**Cadence note:** This is the longest stage. The backspacing is GOOD —
viewers see the editing process. After typing, PAUSE longer than between
stages 1+2. This is the moment before the breakthrough.

---

### Stage 4 (the pivot — extraction not prediction) — significant rewrite

After the longer Stage-3 pause, START BACKSPACING again. Delete back to
`"hey claude, build me a "` (same starting point as Stage 3). Then type the
final polished prompt:

```
hey claude, build me a tool that extracts biomechanical fatigue signals from tennis broadcast video — no hardware needed
```

*Backspace ~62 chars (~5 sec), type ~96 chars (~20 sec), total ~25 sec*

**Cadence note:** This is the longest typing portion. Type with intention —
the WORDS ARE THE MOAT. Special characters:
- The em-dash `—` (Cmd+Option+Hyphen) NOT a regular hyphen — looks more
  editorial. If you can't type it cleanly, two regular hyphens `--` works.
- "biomechanical fatigue signals" is the hero phrase. Don't rush it.

After typing, **PAUSE 1 second**, then **HIT ENTER**. Let Claude's response
START to stream — capture the first 1-2 seconds of Claude beginning to think
or respond, then **stop the recording**.

---

## Total Timing Budget

| Stage | Action | Duration |
|---|---|---|
| 1 | Type naive ask | ~8 sec |
| | Pause | ~2 sec |
| 2 | Append " for tennis" | ~3 sec |
| | Pause | ~1 sec |
| 3 | Backspace + retype technical | ~15 sec |
| | Pause (the breakthrough beat) | ~3 sec |
| 4 | Backspace + retype final | ~25 sec |
| | Hit ENTER + Claude starts response | ~3 sec |
| **TOTAL RAW** | | **~60 sec** |
| **EDIT TARGET** | Speed-ramp + cut deadwood | **22 sec final** |

**You will record 60 sec of raw footage; in CapCut you'll speed-ramp the
typing portions to ~1.4x to compress to 22 sec while preserving the natural
pause beats. Don't worry about hitting 22 sec on the live take.**

---

## Visual Continuity into the Dashboard Capture

When Claude's response starts streaming, **stop the recording**. The next clip
in the timeline is the **terminal precompute screen-record** (showing
`python precompute.py utr_match_01.mp4` running on your M4 Pro). After that,
hard cut to the dashboard OBS capture.

Narrative arc visible to viewer:
1. Andrew formulates the prompt iteratively (live typing) ← THIS RECORDING
2. Andrew runs the actual CV pipeline on a video file (terminal capture)
3. Output: the dashboard with biometric signals (OBS capture) ← THIS IS WHAT WE BUILT

The viewer sees the WHOLE story: prompt → tool → result.

---

## DO NOT (anti-patterns)

- ❌ Don't pre-type and just hit play — the typing has to be LIVE, organic.
- ❌ Don't backspace AWAY all visible typos. A typo + backspace IS authenticity.
- ❌ Don't smile at the camera or break the fourth wall. There's no camera.
  This is screen-only.
- ❌ Don't add commentary out loud. The mic captures keyboard clacks ONLY;
  no voiceover here (your VO records separately at 13:00).
- ❌ Don't record the full claude.ai page chrome (left sidebar, conversation
  history, etc.). Only the input box + immediate response area.
- ❌ Don't worry about Claude's actual response content — it'll be cut off
  by the next clip. We just need the first 1-2 sec of "Claude is thinking..."
  or the start of the response stream.

---

## After Recording

1. **Save the recording** as `~/Documents/Panopticon_Captures/intro_typing_raw.mov`
2. **Quick playback check** in QuickTime — confirm:
   - Audio captured (you should hear keystrokes)
   - Full Claude UI visible (input box + response area both in frame)
   - All 4 stages visible if you scrub through
   - Final prompt correctly says "build me a tool that extracts biomechanical fatigue signals from tennis broadcast video — no hardware needed"
3. **Re-take if any issue.** ~60 sec recording is cheap; do 2 takes max for safety.
4. **Move on to terminal precompute capture** (next section in `capcut_assembly_workflow.md`).

---

## The Final Polished Prompt (cheat sheet — type from this)

Print this or have it on a second screen while you record:

> ```
> hey claude, build me a tool that extracts biomechanical fatigue signals from tennis broadcast video — no hardware needed
> ```

That's the destination. The 4 stages are the journey. The journey IS the
demo's opening narrative.
