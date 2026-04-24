# CLAUDE.md — demo-presentation/ scope

**Inherits from** `/Users/andrew/Documents/Coding/hackathon-demo-v1/CLAUDE.md` (parent).

> Scope: everything done under `demo-presentation/` — the 3-minute demo video, the voice-over scripts, the Remotion compositions, the rendered MP4, the YouTube upload, and the CV submission. The parent CLAUDE.md still applies. This file narrows it.

---

## 1. Prime directive (narrows parent's)

Ship a 3-minute demo video by **Sun 2026-04-26 at 17:00 EST** (soft-submit target — 3 hr buffer before the 8:00 PM deadline).

Optimize the 3-minute video for:

| Judging criterion | % | Our move |
|---|---|---|
| Impact (30) | — | "Biometric data nobody else extracts from 2D broadcast pixels" |
| Demo (25) | — | Sportradar-aesthetic slow-mo anomaly reveal + 2K-Sports HUD |
| Opus 4.7 Use (25) | — | Visible extended-thinking block + prompt-caching indicator + Managed Agents *future vision* |
| Depth & Execution (20) | — | Honest narration — promise only what we built |

**Hard rule**: never over-promise in the voice-over. If the code doesn't do it live, say it's pre-computed or a future vision. Judges reward integrity.

---

## 2. Hard constraints (additive to parent)

1. **Dashboard code freeze**: Fri 2026-04-24 23:59 EST. `dashboard/src/` is locked except for approved Saturday add-ons (see PLAN.md §6).
2. **Video output spec**: H.264 MP4, 1920×1080 @ 60 FPS, total ≤ 180 s, file ≤ 500 MB, audio AAC 320 kbps.
3. **No third-party copyrighted music.** Royalty-free or silence.
4. **No pre-existing footage** except the tennis clip we've been processing (allowed under "New Work Only" because WE processed it).
5. **Submission buffer**: target CV submit by Sun 17:00 EST. **Absolute lockout** at Sun 19:55 EST — do NOT submit in the last 5 minutes under any circumstance.
6. **One branch for demo work**: `demo-v1` (create when Saturday starts). Merge to `main` only after submission.
7. **API keys**: Vercel-only. No `.env` files in this directory or the repo. See parent's GOTCHA-020 / PATTERN-056.
8. **Live Vercel prod URL** is the demo's recording surface. Confirm `vercel deploy --prod --yes` passes Saturday morning BEFORE recording.

---

## 3. Narrative discipline (demo-specific guardrails)

### 3.1 Don't overclaim what's built

The parent CLAUDE.md lists three promised Opus features: generative UI, visible extended thinking, Managed Agents. The Phase-5 audit confirmed:

- **Generative UI** → HUD layouts are static precomputed JSON. Demo narration says *"Opus-designed HUD layouts"* (they were, offline) — never *"Opus recomposes the HUD live"*.
- **Visible extended thinking** → CoachPanel `Show thinking ▾` expands static precomputed text. Demo narration says *"Opus's reasoning preserved and expandable on demand"* — never *"thinking tokens streaming"*.
- **Managed Agents** → not implemented. Demo includes a **future-vision segment** (≤ 15 s) reasoned from first principles: one Managed Agent pre-trained per top-100 ATP/WTA player. See `PLAN.md §5 Scene 5B`.

Do NOT cross these lines without returning here to update them.

### 3.2 Tone: technical-clinical, not theatrical

The judges are Anthropic engineers + Cerebral Valley moderators. They value:
- Clear, simple, useful ideas
- Novel, interesting, technically credible implementations
- Clever Claude Code + tool usage
- Beautifully aesthetic, well-polished products

They do NOT value:
- Childish or overly dramatic narration
- Theatrical cadence
- Emotional voice-over that the visuals don't earn
- SaaS-keynote voice

### 3.3 Narration rules

- **Every line carries information** — a fact, a number, a mechanism. No "watch this", no "here's where it gets interesting", no "the legs are going" unless backed by a sigma value.
- **Minimize footprint** — target < 15 total narration lines across the 3 minutes. Silence is OK. Silence + a pulsing red bar is better than McEnroe-voice.
- **Cadence**: measured, calm, deliberate. Think Tim Cook at WWDC explaining a feature. Not a sports broadcaster emoting on a break point.
- **Let the product speak** — the HUD, SignalBars, anomaly pulses, Opus markdown report ARE the demo. Narration is scaffolding.

### 3.4 Visibility of Claude Code as the build environment

The hackathon is ABOUT Claude Code. Make it visible:
- Prompt-caching indicator on CoachPanel (already in the product)
- Extended thinking expandable block (already in the product)
- Architecture slide lists "Built with Claude Code · 5 days · MIT license"
- Optional Scene-2 flash of the `.claude/skills/` file tree showing the skill packs used

This is a demo-specific editorial choice, not a technical requirement — but it maps directly to the "Opus 4.7 Use" (25 %) criterion.

---

## 4. Directory convention

```
demo-presentation/
├── CLAUDE.md         # this file — rules + narrative discipline
├── PLAN.md           # storyboard + timeline + asset registry + submission checklist
├── assets/           # stills, screenshots, reference images (sportradar, 2K Sports, Palantir)
├── scripts/          # voice-over scripts (markdown) + shot lists + narration timing
├── remotion/         # Remotion compositions — title, scene-break, closing cards only
├── audio/            # recorded narration (.wav), sfx if any
└── renders/          # final MP4s, rough cuts, YouTube-upload-ready file
```

Each subdirectory has a `.gitkeep` placeholder until populated.

---

## 5. Coding discipline (if we touch Remotion or any add-ons)

1. Remotion compositions go ONLY in `demo-presentation/remotion/`. Do not mix into `dashboard/src/`.
2. Every Remotion `<Composition>` must have a `durationInFrames` and `fps` match the master video spec (60 FPS).
3. If a Saturday add-on modifies `dashboard/src/`, it goes on the `demo-v1` branch with `feat(demo): ...` prefix and merges back to `main` ONLY after final submission.
4. New skills/agents for demo production go in `.claude/skills/` or `.claude/agents/` (project scope, per anti-pattern #27).
5. All voice-over scripts in `scripts/` use markdown with timestamped blocks:
   ```md
   ## Scene 3 — Anomaly Reveal (1:15 – 2:15)
   **[1:28]** *slight pause, then clinical:* "Watch what happens at the break point."
   **[1:35]** "His crouch depth has degraded 2.5 sigma..."
   ```

---

## 6. Recording discipline

- **OBS Studio** — 1920×1080 @ 60 FPS, H.264 CRF 18
- **Browser source** at Vercel production URL (not preview — production only)
- **Pre-flight checklist**: close all Chrome tabs, silence Slack/Discord/iMessage, disable screen sleep + screen saver, full-screen window with bookmarks bar hidden
- **Audio**: MacBook Pro built-in mic at 48 kHz, input level -12 dB peak. Record in the quietest room available.
- **Takes**: ≥ 2 full Saturday, 1 final take Sunday morning. Stop-and-restart on obvious stumble only. Minor stutters stay — authentic > polished. Judges prefer honest over over-edited.
- **Hotkeys**: `⌘1` dashboard scene, `⌘2` signal feed, `⌘3` scouting tab, `⌘P` pause recording.

---

## 7. Submission discipline

Follow the checklist in `PLAN.md §11` step-by-step. Do not deviate.

- Video uploaded to **YouTube (public)** under Andrew's channel — per Decision #7
- Title: *"PANOPTICON LIVE — Biomechanical Intelligence for Pro Tennis | Built with Opus 4.7 Hackathon"*
- Description from template in `PLAN.md §11`
- GitHub repo MUST be public, MIT license, README updated
- Written summary 100–200 words — save to `scripts/submission_summary.md` before pasting into CV form

---

## 8. Fallback plans

If anything breaks, consult `PLAN.md §12`. Do not improvise. The fallbacks are ordered by severity — start at the mildest and escalate only if needed.

---

## 9. Logging discipline (mandatory, not optional)

Every Phase-6 session, update these living docs (parent mandate reaffirmed):

- `FORANDREW.md` → dated section per working day (`## 2026-04-24`, `## 2026-04-25`, `## 2026-04-26`)
- `MEMORY.md` → new entries with Phase-6 numbering (next available — GOTCHA-022+, PATTERN-059+, DECISION-011+)
- `TOOLS_IMPACT.md` → append `## Phase 6` block with ROI for Remotion, OBS, ElevenLabs (if used), DaVinci Resolve
- **Anything non-obvious** → log immediately; do not defer. Especially: Remotion quirks, OBS frame drops, Vercel prod deploy surprises, ElevenLabs credit burn rate, CV submission form field order.

---

## 10. Sub-skills in this scope

Project-scoped skills that apply primarily to demo-presentation/:

| Skill (project) | Location | Applies when |
|---|---|---|
| `hackathon-demo-director` | `.claude/skills/hackathon-demo-director/` | Any demo-production work (storyboard, pacing, submission QA) |
| `2k-sports-hud-aesthetic` | `.claude/skills/2k-sports-hud-aesthetic/` | HUD color/typography decisions + SignalBar spring physics |
| `biometric-fan-experience` | `.claude/skills/biometric-fan-experience/` | Fan-facing copy, plain-English signal labels |

User-global skills worth auto-loading in this scope: `awwwards-animations`, `top-design`, `frontend-slides`.

---

## 11. Agents in this scope

| Agent | Use when |
|---|---|
| `demo-director` (project) | Storyboard refinement, shot-list drafting, submission QA |
| `hud-auteur-frontend` (project) | Any Saturday add-on to dashboard chrome (tickertape bar, etc.) |
| `documentation-librarian` (project) | End-of-day MEMORY.md/FORANDREW.md/TOOLS_IMPACT.md updates |
| `e2e-runner` (user) | Playwright fallback recording if OBS fails |

---

## 12. Scope boundary

Anything NOT about the demo video, submission package, or recording → do NOT do here. If the discussion drifts to dashboard feature work, predictive modeling, or new data pipelines, return to the parent `CLAUDE.md` and treat those as separate phases.
