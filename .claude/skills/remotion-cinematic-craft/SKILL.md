---
name: remotion-cinematic-craft
description: World-class Remotion authoring at the Anthropic-release-video standard. Owns motion density, layered reveals, typography animation, music sync, and chapter narrative structure. Prevents the toy-tier output documented in USER-CORRECTION-037.
when_to_use: Authoring or refactoring any Remotion composition where the output will be shown to external judges, customers, or in any context where production quality affects perception. NOT for internal hello-world tests, dev scratchpads, or one-off internal artifacts.
---

# Remotion Cinematic Craft

This skill exists because tonight's Remotion outputs (B0Opener, B5Closing, B5Thesis, SceneBreak instances) were judged TOY-TIER by Andrew (USER-CORRECTION-037). The patterns below are the operationalized response — what world-class Remotion actually requires beyond "use Fraunces serif and hard cuts."

## Orthogonal Responsibility

**This skill OWNS**:
- Motion density per second (3-5 events vs 1)
- Layered element timing (staggered reveals, parallax, secondary animations)
- Typography animation (kerning sweep, weight modulation, italic accent reveal as separate beat)
- Music sync (cuts on beats, holds on sustains, builds aligned to crescendos)
- Chapter narrative structure (Chapter 1 / 2 / 3 progression with visual continuity)
- Composition duration discipline (≥ 8s for story moments, never < 4s for non-interstitial)

**This skill DELEGATES**:
- Color palette + typography family choices → `2k-sports-hud-aesthetic` (already canonical)
- React/state/canvas patterns → `react-30fps-canvas-architecture`
- HUD widget design → `hud-auteur-frontend`
- Video assembly + DaVinci composite → `hackathon-demo-director`
- Asset rendering pipeline → no skill, direct Bun toolchain

## World-Class Reference Standards

The bar to clear is **Anthropic's Opus 4.6 release video** (`https://www.youtube.com/watch?v=dPn3GBI8lII`) and **Claude for Chrome release video** (`https://www.youtube.com/watch?v=rBJnWMD0Pho`). Frame-sampled hex codes + motion analysis archived in `demo-presentation/assets/references/anthropic_video_dna.md`.

Secondary reference (chapter structure + register-braiding): **Numerai's *Introducing Numeraire***, analysis in `demo-presentation/assets/references/vimeo_205032211_dna.md`.

When in doubt, screen-capture an Anthropic frame, count the simultaneous moving elements, count the cuts in the surrounding 5-second window, and match those numbers in our composition.

## The 6 Failure Modes (memorize, never repeat)

These are the specific patterns that produced tonight's TOY-TIER output. Audit any new composition against this list BEFORE rendering:

1. **Composition too short to tell a story** → Anthropic chapter beats are 15-20s. Ours were 1.5-5s. Even a "transition" composition like SceneBreak should be 6-8s with internal motion progression, not a 1.5s text fade.

2. **Single-element frames** → If your composition has ONE wordmark + ONE URL + ONE date and that's it, you've authored a PowerPoint slide. Anthropic frames have 3-5 layered elements: hero text + secondary label + accent line + background motion + framing rule + timecode chip.

3. **Motion density too low** → Count motion EVENTS per second of your composition. Target ≥ 3. Tonight's average was 1. Anthropic averages 3-5. Density comes from staggered overlapping animations, not faster individual ones.

4. **No music — no rhythmic anchor** → Without music, the eye has no rhythm to align to and motion feels arbitrary. ALWAYS author with a music bed in mind, even if the bed is added in DaVinci. Map cuts and entrances to imagined beats. (Per PATTERN-085: music sustains across compositions; mix automation in DaVinci.)

5. **Typography choice without typography craft** → Loading Fraunces is necessary, not sufficient. World-class Fraunces usage requires: kerning sweep on entrance (e.g., letterSpacing: 0.5em → 0.0em over 600ms), weight modulation if variable axis available, italic accent reveal as a separate beat (the italic word arrives 200ms after the upright word), per-character stagger, optical sizing per font-size threshold.

6. **No chapter / narrative structure** → A composition is a paragraph; the video is a chapter; the chapters form an arc. Each composition should have an explicit "this is Chapter N — the [theme]" identity. Anthropic uses chapter numerals + theme labels visibly. The viewer should never wonder "where am I in the story."

## The Cinematic Composition Anatomy

Every world-class composition has FIVE layers. Not all are visible simultaneously, but all are present:

| Layer | Role | Example |
|---|---|---|
| **L1 — Background field** | Establishes register (slate, void, plate, gradient) | `#05080F` solid OR slow-drift cinematic plate OR animated noise |
| **L2 — Framing chrome** | Persistent visual identity (ticker, timecode, chapter marker) | Top-left wordmark + bottom-right "ch.02 — the sensor" |
| **L3 — Hero element** | The main thing happening this composition | Wordmark, headline, hero stat, central animated graphic |
| **L4 — Supporting context** | Elements that contextualize L3 | Subtitle, attribution, related stat, accent line |
| **L5 — Secondary motion** | Subliminal "alive" cues | Slow drift, breathing scale, particulate, parallax |

A toy composition has only L3. A world-class composition uses 4-5 layers. Each layer has its own animation timing, NOT the same as L3.

## The Motion Vocabulary (≥ 3 events/s requires combinatorial chaining)

To hit 3+ motion events per second, chain primitives — don't just sequence them. Examples:

**Bad (one event per second)**:
```
0.0s — opacity 0 → 1
1.0s — y: 20 → 0
2.0s — scale: 0.95 → 1.0
```

**Good (three events at every moment)**:
```
0.0s — Hero opacity 0 → 1 (over 0.4s) ─┐
0.0s — Hero letterSpacing 0.5em → 0.0em (over 0.6s) ├── 4 simultaneous animations
0.0s — Background scale 1.0 → 1.02 (over 8s drift)  │   = density at t=0.0s
0.2s — Subtitle opacity 0 → 1 (over 0.4s) ─────────┘
0.6s — Accent rule width: 0 → 280px (over 0.4s) ─┐
0.6s — Italic-word color: white → cyan (over 0.3s) ├── 3 simultaneous at t=0.6s
0.6s — Background drift continues               ─┘
```

The chaining rule: every 200ms, AT LEAST ONE NEW animation fires. Existing animations may still be in-flight.

## Typography Animation Patterns (Anthropic playbook)

### Pattern A — The Kerning Sweep
Letters start spaced apart and snap to their natural kerning over 600ms. Reads as "thought crystallizing."
```tsx
const kerningProgress = interpolate(frame, [0, 36], [0, 1], { ...clamp });
const letterSpacing = interpolate(kerningProgress, [0, 1], [0.5, -0.02]);
// CSS: letterSpacing: `${letterSpacing}em`
```

### Pattern B — The Italic Reveal Beat
Hero word (upright) appears at frame 0. The italic accent word appears at frame +12 (200ms later) with its own scale-pop. Two-beat reveal feels typographic, not just text.
```tsx
const heroOpacity = interpolate(frame, [0, 24], [0, 1], { ...clamp });
const italicOpacity = interpolate(frame, [12, 36], [0, 1], { ...clamp });
const italicScale = interpolate(spring({ frame: frame - 12, fps, config: { damping: 14, stiffness: 200 } }), [0, 1], [0.92, 1]);
```

### Pattern C — Per-Character Stagger
Headline reveals one character at a time over 600-800ms. Use `<span>` per character with calculated per-char delay.
```tsx
const text = "PANOPTICON LIVE";
return text.split('').map((char, i) => {
  const charOpacity = interpolate(frame, [i * 3, i * 3 + 12], [0, 1], { ...clamp });
  return <span key={i} style={{ opacity: charOpacity }}>{char}</span>;
});
```

### Pattern D — Weight Modulation (variable font axis)
Fraunces is a variable font with weight axis 100-900. Animate the weight from 300 to 600 over 500ms for a "thickening" effect on emphasis words.
```tsx
const weight = interpolate(frame, [12, 42], [300, 600], { ...clamp });
// CSS: fontVariationSettings: `"wght" ${weight}`
```

## Music Sync Patterns

Even if music is added in DaVinci, AUTHOR THE COMPOSITION as if music drives it. Pseudo-tempo = 120 BPM = beat every 30 frames. Cut/snap on beats:

| Frame | Beat | Visual event |
|---|---|---|
| 0 | beat 1 | hero appears |
| 30 | beat 2 | subtitle appears |
| 60 | beat 3 | accent rule wipes |
| 90 | beat 4 | hero settles, secondary motion takes over |
| 120 | bar 2 | chapter label fades in (downbeat emphasis) |

If you're using a real music track in DaVinci, use a beat-detection tool (Audacity → Analyze → Beat Finder) to extract the actual frame-precise beats and align Remotion compositions to them.

## Chapter Structure (the missing layer in tonight's work)

A 3-minute video should have explicit chapters. PANOPTICON's chapters per the v4 storyboard:

| Chapter | Beat | Duration | Theme |
|---|---|---|---|
| **Ch 0 — Origin** | B0 | 25s | Personal journey opener |
| **Ch 1 — The Miss** | B1 | 18s | Cold open on anomaly |
| **Ch 2 — The Sensor** | B2 | 17s | YOLO + Kalman + signals reveal |
| **Ch 3 — The Recurrence** | B3 | 40s | Second miss + slow-mo + telemetry |
| **Ch 4 — The Brain** | B4 | 60s | Opus reasoning climax |
| **Ch 5 — The Vision** | B5 | 18s | Brand + thesis closing |

Each chapter should have:
- A visible chapter marker (e.g., "ch.02 — the sensor" in mono caps, top-right corner)
- A consistent visual language for the chapter (e.g., Ch 2 establishes the cyan SignalBar register, Ch 4 establishes the split-screen reasoning register)
- A "callback" to a previous chapter (e.g., Ch 4 reuses the anomaly frame from Ch 1)
- A "setup" for the next chapter (e.g., Ch 2 ends on a tight shot of a SignalBar, Ch 3 opens on the same SignalBar's red flash)

## The Composition Checklist (run BEFORE first render)

Before rendering any new world-class composition, audit against this list. If ANY checkbox is unchecked, the composition is not yet world-class:

- [ ] Duration ≥ 8 seconds (or explicit interstitial-by-design ≥ 4 seconds)
- [ ] At least 3 of the 5 anatomy layers are present (L1 background field + L3 hero + at least one of L2/L4/L5)
- [ ] Motion density audit: count events per second across the composition. Target ≥ 3.
- [ ] At least one typography animation pattern (kerning sweep / italic reveal / per-char stagger / weight modulation)
- [ ] Composition is timed to a pseudo-tempo (cuts on beats, holds on sustains)
- [ ] Composition has chapter identity (visible marker OR consistent register with neighboring compositions)
- [ ] Composition's exit foreshadows next composition's entry (visual or thematic continuity)
- [ ] tsc --noEmit on remotion package: exit 0
- [ ] Render → ffmpeg frame extract at 33%, 66%, 99% → visually inspect each
- [ ] Play full render at 1× speed and watch end-to-end without scrubbing

## Canonical Examples in This Project (LIVING — update as we ship)

**World-class shipped (use as reference)**:
- `B0OpenerV2.tsx` (LANDED 2026-04-25 pre-dawn) — 36s, 6 internal beats (void breath
  → user types → claude responds → git timeline → ignition + wordmark → chapter card
  hold), persistent ChapterMarker chrome ("ch.00 / ORIGIN" with cyan accent),
  AmbientGrid L5 slow-drift, italic-reveal beats on three accent words ("malleable?",
  "build" with cyan glow, "Live" with kerning sweep), 120 BPM pseudo-tempo with beat
  boundaries on bar lines (4s/12s/18s/27s/32s/36s). All 5 anatomy layers active.
  Audit pass on 9 extracted frames; one iteration to fix dialog-ghost over-overlap.
- `B5ClosingV2.tsx` (LANDED 2026-04-25 pre-dawn) — 12s, 4 internal beats (chrome
  arrival → wordmark ignition → URL per-char stagger + repo → attribution), shares
  ChapterMarker + AmbientGrid with B0V2 (theme switched to "ch.05 / VISION"),
  fontSize 168 hero wordmark (more dramatic than B0V2's 132 because it's the sole
  hero), Pattern A+B+ignition on wordmark, Pattern C per-character stagger on URL.
  CLEAN ON FIRST RENDER — no iteration needed.
- `B5ThesisV2.tsx` (LANDED 2026-04-25 pre-dawn) — 8s, 4 internal beats (marker
  arrival → thesis kerning sweep + drift → accent rule wipe → hold + exit), pure
  #000 void register (PATTERN-083 register-switch from B5ClosingV2's slate),
  AmbientGrid suppressed (register-switch discipline), only "ch.05 / VISION"
  chrome retained, 280px cyan accent rule under thesis creates visual rhyme with
  chapter marker's cyan underline (top-right ↔ bottom-center). CLEAN ON FIRST
  RENDER. Bookend with B5ClosingV2.
- New primitives shipped: `ChapterMarker.tsx` (4-corner framing chrome) +
  `AmbientGrid.tsx` (L5 slow-drifting faint grid). Both reusable across V2 family.

**Toy-tier (do NOT use as reference — kept for 1 week as anti-pattern)**:
- `B0Opener.tsx` (V1 — 25s, simple typing + git timeline + bare title) — superseded
  by B0OpenerV2; delete after Sunday submission unless needed for comparison
- `B5Closing.tsx` (V1 — 5s, single wordmark + URL) — superseded by B5ClosingV2
- `B5Thesis.tsx` (V1 — 4s, single line) — superseded by B5ThesisV2
- `SceneBreak.tsx` (current — 1.5s, simple title) — needs T2 rebuild

**World-class targets (still to build, Saturday)**:
- SceneBreak T2 rebuild: 6-8s interstitial cards with mini chapter markers
  (ch.02/THE SENSOR, ch.03/THE RECURRENCE, ch.04/THE BRAIN), shared visual
  vocabulary with B0V2/B5ClosingV2.
- (Stretch) OBS-overlay templates for the dashboard walkthrough segments —
  callout arrow, zoom-insert frame, kinetic-typography text card.

The V2 family's visual continuity is the chrome (ChapterMarker style), the ambient
field (AmbientGrid drift cycle when in HUD register), and the typography animation
language (kerning sweep + italic reveal beat). The chapter ID changes (ch.00 →
ch.02 → ch.03 → ch.04 → ch.05) and the theme labels change (ORIGIN → THE SENSOR →
THE RECURRENCE → THE BRAIN → VISION), but the mechanics stay constant.
**Continuity IS the chapter identity.** Register-switch (HUD slate ↔ pure void) is
the closing structural device per PATTERN-083, used ONLY at the bookend boundary
between B5ClosingV2 and B5ThesisV2.

## Anti-Pattern Cross-Reference

- USER-CORRECTION-037 in MEMORY.md (full failure-mode breakdown)
- PATTERN-082 (logo ignition) — necessary but NOT sufficient on its own
- PATTERN-083 (register-switch for two-card splits) — correct framing, but each card still needs world-class internal craft
- PATTERN-084 (slow drift on cinematic plates) — Numerai-floor; Anthropic adds layered slow zooms + lateral parallax on top

## Saturday Morning Execution Sequence (Tier 1 priority order)

1. **Study reference**: rewatch Anthropic Opus 4.6 video (`dPn3GBI8lII`) for 3 minutes. Note: count motion events per second on the wordmark reveal. Count layers. Note typography animation specifics.
2. **Build B0OpenerV2**: longest composition (30-45s), establishes the visual language for all subsequent compositions. Multi-beat: silent cursor → typed dialog → response → fade-out → git timeline with parallax → chapter card. Music bed considered from frame 0.
3. **Render B0OpenerV2 → review against checklist → iterate** until all checklist items pass.
4. **Build B5ClosingV2 + B5ThesisV2** (the bookend pair). They share visual vocabulary: same chapter-marker style, same typography animation language, same music sync pacing.
5. **Render bookend pair → review → iterate**.
6. **(If time)** Build SceneBreak rebuilds + interstitial chapter-marker compositions.
7. **(Stretch)** Build OBS-overlay templates: callout arrow, zoom-insert frame, kinetic-typography text card.

Total Saturday morning budget: 5-7 hours of focused craft work.

## Skill Maintenance

Update this skill when:
- A new world-class composition lands (move from "Saturday morning rebuild" to "world-class targets" with the V2 file path)
- A new typography animation pattern is invented or borrowed
- A new failure mode is discovered (add to "The 6 Failure Modes" — keep the count growing only if genuinely new)
- The Anthropic playbook publishes new conventions worth absorbing
- An external reference (Numerai, Stripe, Linear) provides a transferable mechanic

Add to quarterly skill audit per `~/.claude/CLAUDE.md` Project-Specific Skill Teams discipline.
