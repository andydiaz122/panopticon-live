# PANOPTICON LIVE — Design DNA Synthesis (2026-04-24 evening)

**Source research** (3 parallel agents, all converge):
- `anthropic_video_dna.md` — frame-sampled hex codes from `dPn3GBI8lII` + `rBJnWMD0Pho`
- `remotion_craft_patterns.md` — 2025-2026 Awwwards/Tendril/Linear/Vercel/Arc patterns
- `figma_remotion_workflow.md` — Figma-as-brief + Remotion-as-truth workflow

**Andrew's directive** (verbatim):
> *"What colors would a world-class designer use for our very specific project?"* + *"warmer colors, like Anthropic uses, but our application is much different than the work Anthropic does."*

---

## The single most important finding

**All three research streams converge on the SAME craft language**: monochrome foundation + ONE saturated accent + restraint to the point of austerity. Tendril, Linear, Vercel, Arc, AND Anthropic itself all live here. **My current B0 cyan-on-cool-blue palette is the literal anti-pattern** — it reads as "sci-fi HUD bloat" (Agent B's term) and would be filed by judges as derivative-of-2K-Sports rather than as serious tech demo craft.

The fix is not "add more colors." The fix is **MORE monochrome, warmer foundation, ONE accent reserved exclusively for the product's hero signal (fatigue telemetry).**

---

## What we steal from Anthropic specifically

Their craft is a closed system. The minimum-viable subset that lets us land in-culture without being derivative:

1. **Warm background, never pure black or pure white.** Anthropic uses `#F8F8F8` (cream) for model-launch films and `#E0D8C8` (sandstone) for product demos. We are a product demo — sandstone register applies, but we're dark mode (broadcast / dashboard context), so we INVERT to a warm dark slate.
2. **Exactly ONE saturated color on screen at any time.** Anthropic uses Claude Spark coral (`#D97757`/`#D07050`). We adopt this verbatim — it's the in-culture move for an Anthropic hackathon AND it's exactly the warm forensic-orange Agent B independently recommended for fatigue telemetry.
3. **Serif headlines + sans body + mono for data only.** Three fonts max. Anthropic uses Copernicus/Tiempos serif → Fraunces is the free Google Fonts substitute. Anthropic uses Styrene B sans → Inter or Geist is the free substitute. We keep JetBrains Mono for terminal/data lines (already wired).
4. **Motion menu is TINY**: hard cuts + scale pops (0.9 → 1 spring) + typewriter reveals. NO parallax, gradients, glassmorphism, drop shadows except subtle window chrome.
5. **Pacing inversion to study**: Opus-launch film = 77 cuts/min (storm). Chrome demo = 7 cuts/min (calm). **We are calm.** Our Detective Cut is forensic — long dwells, deliberate cuts, silence as punctuation.
6. **Editorial layout discipline**: small label above + big headline below + bleed of context off-frame. 6% headline / 94% margin ratio. Generous air.
7. **Italics for emphasis** (Anthropic's signature: "Website analytics that *actually* make sense") — we adopt for moments of emphasis where bold would feel sales-y.

---

## Proposed PANOPTICON LIVE palette (warm dark broadcast)

| Role | Hex | Usage |
|---|---|---|
| Background — primary | `#1A1614` | Full-bleed warm slate-black. Replaces current `#05080F` cool blue-black. |
| Background — panel | `#26201D` | Subtle elevation for cards / panels |
| Border | `#3A3128` | Hairline borders, dividers |
| Ink — primary | `#F2EAE0` | Hero text, headlines. Cream — matches Anthropic's body ink, inverted for dark mode. |
| Ink — secondary | `#A89E92` | Body text, labels |
| Ink — muted | `#5A5247` | Subdued meta, timestamps |
| **Accent — fatigue / signal** | `#D97757` | **THE ONLY SATURATED COLOR.** Used exclusively for fatigue/anomaly indication, "Claude voice" in dialog, hero numerics. This IS Anthropic's published Clay color. |
| Accent — fatigue (dim) | `#7E4634` | Pre-anomaly state, fatigue baseline, dim variant |
| Anomaly intensity | `#E89B6F` | Brighter clay for anomaly peak — used sparingly |

**Typography**:

| Role | Font | Where |
|---|---|---|
| Headline / display | **Fraunces** (Google Fonts) | Hero text, scene titles, closing card |
| Body / UI | **Inter** (Google Fonts) | Paragraphs, captions, button text, narration overlays |
| Data / mono | **JetBrains Mono** (already wired) | Terminal lines, numerics, timestamps, signal values |

---

## Concrete implications for our build

### B0 opener (priority #1 — the first 25s judges see)

Current v4 colors → v5 swaps:
- `BG = '#05080F'` → `'#1A1614'`
- `USER_COLOR = '#7B8BA8'` (cool gray) → `'#A89E92'` (warm gray)
- `CLAUDE_COLOR = '#00E5FF'` (cyan) → `'#D97757'` (Anthropic clay)
- `META_COLOR = '#5A6678'` (cool muted) → `'#5A5247'` (warm muted)

Add Fraunces font for the closing-card title (`PANOPTICON LIVE` set in serif instead of mono). Keep the dialog + gitgraph in JetBrains Mono — those ARE machine output.

### Dashboard tokens (HUD / SignalRail / Tickertape / etc.)

Current `dashboard/src/lib/design-tokens.ts` uses:
- `bg0: '#05080F'` cool blue-black
- `playerA: '#00E5FF'` cyan (THE BLOAT)
- `fatigued: ?` / `energized: ?` / `anomaly: ?`

To stay consistent across B0 (Remotion) + B1-B5 (OBS dashboard capture), the dashboard needs the same swaps. **Scope of dashboard pivot**: ~30-50 LoC across `design-tokens.ts` + a few component files that hardcode hex. ~30 min of work. Manageable, but a strategic call — see questions below.

### Pacing

The Detective Cut is already calm (Chrome-film register). Confirm: each B-beat dwells 8-12 s, hard cuts between beats, NO crossfades or parallax in B0/B5 chrome.

---

## Strategic questions for Andrew (the call I need from you)

**Q1**: Adopt Anthropic Clay `#D97757` verbatim, or shift to a more forensic-clinical `#C75A3F` (burnt orange) to differentiate?
- **Recommend**: Clay `#D97757`. It's an in-culture move on the Anthropic hackathon. Differentiation comes from how we USE the color (forensic timestamps, anomaly pulses), not from the color itself.

**Q2**: Scope of dashboard pivot.
- **(a)** B0-only swap. Dashboard stays cyan; B0 is warm-orange. DaVinci composite uses the contrast intentionally — warm "narrative" frames cool "data."
- **(b)** Full dashboard + B0 swap. Consistent palette across all 25-178 s of the video. ~30 min build cost.
- **Recommend**: **(b)**. Consistency reads as deliberate craft; contrast reads as "two demos taped together." 30 min is cheap insurance.

**Q3**: Add Fraunces font?
- **Recommend**: yes. Hero text in serif vs mono is a HUGE signal of seriousness. Free Google Fonts download, ~5 min wire-up via `@remotion/google-fonts/Fraunces`.

**Q4**: Should I render B0 v5 NOW for visual comparison, or wait for your call on Q1-Q3?
- **Recommend**: render now. Andrew said "let's not throw away ideas until we've actually tried them, and we see what lands." Visual comparison is the only honest answer.

---

## What I'm NOT proposing (to keep scope tight)

- Adding inter/Fraunces to the dashboard `<body>` — stays mono terminal aesthetic per current design
- Reworking the SignalBar physics (springs are Anthropic-aligned)
- Replacing JetBrains Mono with Geist Mono — JetBrains Mono is already established and works

---

## Saturday plan adjustment if palette pivots

If we go (b) full pivot:
- Saturday 08:30 first 30 min: token swap in `design-tokens.ts` + visual QA of dashboard
- 09:00 onward: continue PLAN.md §10 schedule unchanged
- Add B0 v5 re-render to the morning checklist

If we go (a) B0-only:
- B0 v5 ships tonight, no Saturday adjustment
- Accept palette mismatch in DaVinci compositing; lean into "narrative frames data" framing

---

**Cross-references**:
- `anthropic_video_dna.md` (Agent A) — full frame-sampled cheatsheet
- `remotion_craft_patterns.md` (Agent B) — 487 lines, 10 patterns + 5 anti-patterns
- `figma_remotion_workflow.md` (Agent C) — the "Figma static + Remotion ground-truth" pattern
- `competitor_audit.md` (earlier) — positioning narrative ("Hawk-Eye for fatigue")
- `mascot_research.md` (earlier) — RISKY/lean FORBIDDEN; Spark Clay color is published + safe to use as a color hex
