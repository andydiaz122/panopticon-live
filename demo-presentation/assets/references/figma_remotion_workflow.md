# Figma → Remotion Workflow — Research Brief

**Author**: Agent C, 3-agent research wave
**Date**: 2026-04-24
**Audience**: Andrew Diaz, building a 3-min PANOPTICON LIVE demo in Remotion this weekend
**Time budget consumed**: ~6 Perplexity calls
**Status**: Actionable — ready to execute Step 1 (FigJam brainstorm) tonight

---

## 1. Executive Summary — The Workflow in 5 Steps

The canonical Figma → Remotion pipeline used by professional motion designers in 2025-2026 is:

| # | Step | Tool | Output |
|---|------|------|--------|
| **1** | Brainstorm the narrative | **FigJam board** with storyboard template | Sticky-note beats, mood references, "why this shot" rationale |
| **2** | Storyboard each beat | **Figma design file**, one frame per scene @ 1920×1080 | Visual reference frames the demo must match |
| **3** | Lock design tokens | Figma **Variables panel** (colors, type scale, spacing) | JSON export → Remotion `tokens.ts` constants |
| **4** | Implement in Remotion | One `<Composition>` per Figma frame; paste SVG assets; animate via `spring()` + `interpolate()` | MP4 segments rendered headlessly |
| **5** | Review + iterate | Side-by-side Remotion Studio preview vs Figma frame, per beat | Shipped 3-min video |

**Core insight** (corroborated by Figma Config 2025 talk, the Remotion docs, and the Daniel Shapano crash-course): motion never survives the handoff if it only lives in Figma. Figma is the **reference static + the brief**; Remotion is the **ground truth**. Designers who treat Figma as the spec and Remotion as the artifact ship; designers who try to animate IN Figma (smart animate as the destination) don't. Your workflow inverts that failure mode.

---

## 2. Tool Stack & Handoff Points

```
┌─────────────────┐   handoff 1: narrative beats
│ FigJam          │ ─────────────────────────────────┐
│ (brainstorm)    │   (sticky notes → frame titles)  │
└─────────────────┘                                  ▼
                                         ┌─────────────────┐
                                         │ Figma Design    │  handoff 2: SVG + vars
                                         │ (storyboard)    │ ──────────────────────┐
                                         │ 1 frame / beat  │   (Copy-as-SVG;       │
                                         └─────────────────┘    Export Variables)  │
                                                                                   ▼
                                                                      ┌─────────────────┐
                                                                      │ Remotion        │
                                                                      │ (React + MP4)   │
                                                                      │ 1 <Composition> │
                                                                      │  per frame      │
                                                                      └─────────────────┘
                                                                               │
                                                                               │ handoff 3: render
                                                                               ▼
                                                                      ┌─────────────────┐
                                                                      │ demo.mp4        │
                                                                      │ (3 min, 30 fps) │
                                                                      └─────────────────┘
```

**Notion sits alongside, not in-line.** Figma's own Web Experience team (per their Notion blog) embeds FigJam boards *into* Notion pages — Notion is the hub for the written brief, the asset registry, the review-comments log. For a solo hackathon that's overkill; one Notion page with a table of 12 beats × [Figma frame link, Remotion component name, status] is the right density.

**Why not animate in Figma's Smart Animate?** Two reasons from the Config 2025 talk: (a) motion that lives in Figma "slowly fades down from memory" — judges never see it, (b) spring curves available in Figma prototype mode don't 1:1 map to CSS/React springs, so you end up re-tuning everything in code anyway. Use Figma Prototype Mode only as a **timing sketch** (e.g., "scene 3 is ~4 seconds, scene 4 is ~2.5 seconds"), not as the source of truth for curves.

**Key tools — what each owns:**

| Tool | Owns | Explicitly does NOT own |
|------|------|-------------------------|
| FigJam | Narrative structure, stakeholder alignment, "vibe" mood board | Pixel-accurate reference frames |
| Figma Design | Per-beat reference frames, color/type tokens, static SVG assets | Timing, easing curves, final pixel output |
| Figma Prototype | Rough timing sketch ("how long is scene 3?") | Final motion curves, handoff target |
| Notion | Written brief, asset registry, review log, beat-by-beat checklist | Anything visual |
| Remotion | All animation logic, final MP4 render, ground truth | Brainstorming, stakeholder review |

---

## 3. Storyboard Kit Recommendations — Public Figma Community Files

Ranked by fitness for a 3-min demo (not a feature film). Copy to Andrew's draft first, then mix-and-match.

1. **Maxim Leyzerovich — Storyboard Template** — 9.1k users, clean 16:9 frame layouts with space for caption + duration, battle-tested.
   URL: https://www.figma.com/community/file/853170162772539008/storyboard-template
   **Best for**: the primary 12-beat storyboard. **Clone this one first.**

2. **FigJam Storyboard Template (Figma official)** — the FigJam-native version, designed for Step 1 brainstorm (stickies + beats, not pixel art).
   URL: https://www.figma.com/community/file/1138974279982498289/storyboard-template-in-figjam
   **Best for**: the FigJam brainstorm session in Step 1.

3. **Storyboard Templates: Mobile & Desktop** — purpose-built for motion designers planning UI demos, includes both orientations.
   URL: https://www.figma.com/community/file/1110928965114350241/storyboard-templates-mobile-desktop
   **Best for**: any HUD / UI screen-replay beats (most of PANOPTICON's demo).

4. **Basic Storyboard Template (6/9 panels)** — minimalist, great for rapid single-page overview.
   URL: https://www.figma.com/community/file/1163285550975420735/basic-storyboard-template
   **Best for**: the one-sheet shot-list that Andrew prints (or embeds in Notion) and checks off live.

5. **Patience Lair — Storyboard Template** — neutral animation/video production template, lighter-weight than Leyzerovich.
   URL: https://www.figma.com/community/file/983755057332380629/storyboard-template
   **Alternative** if Leyzerovich feels heavy.

6. **Storyboard Mix-and-match Library** — character poses + backgrounds for UX storyboards. **Probably skip** for PANOPTICON (wrong medium) but noting it for completeness.
   URL: https://www.figma.com/community/file/1024066926350231135/storyboard-mix-and-match-library

---

## 4. Color / Type Token Export — Concrete Pattern

Figma released **native Variables Export** (JSON, DTCG-conforming) in December 2025. This means the full Figma → Remotion token handoff is now a 4-command operation with zero plugins.

### Step 1 — Define variables in Figma

In the Figma file, open the **Variables panel** (View → Panels → Toggle Variables). Create one collection per concern:

- `Colors` collection with modes (`light`, `dark` — PANOPTICON is dark-only, so one mode)
  - `hud/cyan-primary` `#00E5FF`
  - `hud/magenta-accent` `#FF2BAD`
  - `hud/bg-deep` `#0B1020`
  - etc.
- `Type` collection
  - `font/display` "Inter Display"
  - `size/hero` `64`
  - `size/caption` `14`
- `Motion` collection — hackathon-specific token idea
  - `timing/beat-short` `1800ms`
  - `timing/beat-hero` `4500ms`
  - `spring/stiff` (stored as a string like `"stiffness:180, damping:20, mass:0.8"`)

### Step 2 — Export as JSON

Right-click the collection → **Export mode** (or "Export modes" to grab all). Figma downloads a DTCG-conforming JSON file to `~/Downloads/Colors.json`.

### Step 3 — Convert to Remotion TS constants

The simplest pattern is a build script at `scripts/tokens-to-ts.ts`:

```ts
// scripts/tokens-to-ts.ts
import tokens from "../design/Colors.json" assert { type: "json" };
import fs from "fs";

const lines: string[] = ["// AUTO-GENERATED from Figma Variables — do not edit"];
lines.push("export const COLORS = {");
for (const [name, { value }] of Object.entries(tokens.variables)) {
  const camel = name.replace(/[/\-](.)/g, (_, c) => c.toUpperCase());
  lines.push(`  ${camel}: "${value}",`);
}
lines.push("} as const;");

fs.writeFileSync("src/tokens.ts", lines.join("\n"));
```

Result — `src/tokens.ts`:

```ts
export const COLORS = {
  hudCyanPrimary: "#00E5FF",
  hudMagentaAccent: "#FF2BAD",
  hudBgDeep: "#0B1020",
} as const;
```

### Step 4 — Use in Remotion components

```tsx
import { COLORS, TIMING } from "./tokens";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const HeroScene = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { stiffness: 180, damping: 20 } });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.hudBgDeep }}>
      <div style={{ color: COLORS.hudCyanPrimary, transform: `scale(${scale})` }}>
        PANOPTICON LIVE
      </div>
    </AbsoluteFill>
  );
};
```

### Alternative — Plugin route (if native export frustrating)

If Andrew's Figma account was just created, native Export Variables may still be rolling out. Fallback options:

- **Export Variables (CSS, SCSS, Tailwind)** by Ease Studio — https://www.figma.com/community/plugin/1382804904426179542/export-variables-css-scss-tailwind — one click to CSS custom props, convert with a 20-line regex script.
- **Figma Token Exporter** (10.6k users) — similar, supports multiple syntaxes.
- **PRISM Tokens** — https://prismtokens.app/ — SaaS + Figma plugin, has CI/CD sync built in. Probably overkill for a weekend project.

---

## 5. Anti-Patterns — Common Over-Tooling

Things that waste time without improving the demo. Don't do these:

1. **Don't use Figma → React export plugins** (Anima, Builder.io Visual Copilot, etc.) for Remotion scenes. These tools generate absolute-positioned, pixel-locked HTML/CSS that is **hostile to animation**. The whole point of Remotion is `interpolate(frame, ...)` driving style; fixed pixel positions from an export defeat that. Use Figma's **native SVG export** (Copy-as-SVG markup → SVGR playground → React component) per the official Remotion docs. SVGs animate cleanly via `transform`, `opacity`, `strokeDashoffset`.

2. **Don't animate in Figma Prototype Mode and try to "translate" the curves.** Figma's spring presets don't map to Remotion's `spring()` config (stiffness/damping/mass) — you'll spend 30 minutes matching a feel that you could have authored in 5 minutes directly in code. Use prototype mode only for **timing** ("scene 3 takes ~4 seconds"), not curves.

3. **Don't build a Figma component library for the video.** Video scenes are one-shot; components exist for reuse across a design system. Duplicating the HUD pieces into a component set with variants adds maintenance overhead without payoff. A storyboard is flat frames; keep them flat.

4. **Don't over-invest in Notion.** The Figma Config team's post described a 12-month cross-functional event. A solo hackathon needs one Notion page with a beat-list table. If Andrew finds himself creating Notion databases with formulas and rollups, he's in the wrong tool — that time should be spent in Remotion.

5. **Don't rely on FigJam AI diagram generation** (via Notion Custom Agents integration) for the storyboard. The output is flowcharts and Gantt-like diagrams; storyboards need spatial composition (16:9 frame, character/HUD in position, camera angle). Use FigJam's **storyboard template** (a human-built layout) plus your own sticky notes.

6. **Don't treat the Figma file as "the design system."** For this demo, Figma is the **storyboard**. If Andrew starts building a full design system ("I need a button component so I can make a button in scene 7"), he's solving for reuse that doesn't exist. Copy-paste freely across frames.

7. **Don't forget to preview the motion in a browser**, per the Config 2025 rule-number-one. Remotion Studio (`npx remotion studio`) is that browser preview — run it continuously while iterating, not just at render time.

---

## Appendix — Primary Sources

- **Figma Config 2025 — Carmen Ansio, "Design Meets Code: Interactive Animations with Figma"**: https://www.youtube.com/watch?v=AxLIfW9y5yw — the "motion dies between Figma and production" thesis; the Lottie + browser-preview discipline.
- **Remotion Official — Import from Figma**: https://www.remotion.dev/docs/figma — canonical SVG export path + SVGR playground + `<g>` grouping for animated sub-elements. Dated 2026-04-10 (current).
- **Remotion AI Skill**: https://www.remotion.dev/docs/ai/skills — Claude Code skill that converts static Figma designs to animated React components.
- **How I use Figma + Notion as a Freelance Product Designer** (2022-11-10): https://www.youtube.com/watch?v=rcUKk_swRC4 — Notion-for-scope-docs + Figma-for-designs pattern.
- **How Figma's Web Experience team used Notion to plan Config** (2024-07-11): https://www.notion.com/blog/figma — the canonical "embed FigJam in Notion" hub pattern.
- **Native Figma Variables Export launch** (Figma Forum, Nov 2025): https://forum.figma.com/ask-the-community-7/native-variable-export-feature-47831 — confirms DTCG-conforming JSON export is now native in-app.

---

**END OF BRIEF**
