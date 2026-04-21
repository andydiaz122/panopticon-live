---
name: 2k-sports-hud-aesthetic
description: Design language for the PANOPTICON LIVE HUD — color palette, typography, motion timings, widget variants, aesthetic references. Use when building or styling any dashboard/components/Broadcast/* component. Inspired by NBA 2K, FIFA, Madden, NFL broadcast overlays, and F1 telemetry.
---

# 2K-Sports HUD Aesthetic

The visual language that wins the 25% Demo criterion. Every HUD widget should feel like a AAA sports video game — premium, alive, informative, confident.

## Reference Inspirations

- **NBA 2K** — player attribute meters, clutch indicators, momentum bars
- **FIFA EA SPORTS** — stat radars, predictive ghosts, pressing intensity
- **Madden NFL** — QB vision cones, pressure meters, fatigue icons
- **ESPN / Sky Sports broadcast overlays** — serve speed, ball toss tracers, rally counts
- **F1 telemetry** — multi-meter panels, live sparklines, anomaly highlights
- **Awwwards motion** — smooth enter/exit, purposeful easing, no gratuitous animation

## Color System

Tokens in `dashboard/lib/design-tokens.ts`:

```ts
export const colors = {
  // Player identifiers
  playerA: "#00E5FF",    // cyan (analytics blue)
  playerB: "#FF3D71",    // coral red

  // Signal state
  baseline: "#64748B",    // slate (neutral / calm)
  energized: "#34D399",   // emerald (positive deviation)
  fatigued: "#F59E0B",    // amber (concerning drift)
  anomaly: "#EF4444",     // red (critical deviation)
  opusThinking: "#A855F7",  // purple (Opus's voice)

  // Background
  bg0: "#0A0E1A",         // deep near-black
  bg1: "#0F1524",         // card background
  bg2: "#1A2238",         // elevated widget
  border: "#243049",       // subtle divider
  borderAccent: "#3B4F7E", // highlighted border

  // Text
  textPrimary: "#F8FAFC",
  textSecondary: "#CBD5E1",
  textMuted: "#64748B",
};

export const motion = {
  // Easing curves (cubic-bezier)
  easeOutQuart: [0.25, 1, 0.5, 1] as const,
  easeInOutExpo: [0.87, 0, 0.13, 1] as const,
  spring: { type: "spring", stiffness: 260, damping: 20 } as const,

  // Timings (ms)
  instant: 0.15,
  quick: 0.25,
  regular: 0.4,
  slow: 0.7,
  slower: 1.2,
};
```

## Typography

- **Primary**: Inter Variable (weight range 400-900)
- **Mono**: JetBrains Mono Variable (for stat values + JSON)
- Font preload in `app/layout.tsx` (NOT `font-display: swap` — preload hero fonts per CLAUDE.md Vercel deployment trap #28)
- Stat values: tabular-nums enabled (`font-variant-numeric: tabular-nums`)

## Widget Catalog

### PlayerNameplate
- Top-left (Player A) / Top-right (Player B)
- Flag icon + seed + current-server dot
- Accent color = player color
- Enter: fade + slide 20px from edge, 400ms easeOutQuart

### SignalBar
- Horizontal progress bar (height 8px)
- Label left, value right (tabular-nums)
- Base fill color = `baseline`
- Deviation: interpolate fill toward `energized` / `fatigued` / `anomaly` based on z-score
- On anomaly (z ≥ 2): pulse animation (scale 1.0 → 1.04 → 1.0, 900ms loop) + glow shadow
- Sparkline below (~40px tall) via Recharts `<LineChart>`

### MomentumMeter
- Horizontal bar split in the middle
- Left half = Player A fatigue composite; Right half = Player B
- Whichever is higher gets visual emphasis
- Updates on match-state change, not per frame

### PredictiveOverlay
- Floats above a player
- Shows Opus's next-shot prediction: "Cross-court forehand · 68%"
- Glow gradient matching player color
- Fade in 300ms when Opus emits, fade out 600ms on shot lands

### TossTracer
- SVG path traced over the live video during PRE_SERVE_RITUAL
- Stroke color = player color
- Stroke-dashoffset animation (0 → 1) to "draw" the path
- Only visible during toss phase; fades as contact happens

### FootworkHeatmap
- Per-player small heatmap overlay (bottom corner of frame)
- Dots fade from recent = bright to old = dim over ~5 seconds
- Coordinates from normalized keypoints × court dimensions

### CoachPanel (Opus commentary)
- Fixed bottom panel, full-width
- Opus Coach name label with purple accent
- Typewriter effect on commentary text (animate character-by-character, 18ms per char)
- Collapsible "Show thinking" chevron → expands the extended-thinking block
- Thinking block: monospace, `opusThinking` purple text, slightly dimmer than commentary
- Cache-hit indicator: subtle "⚡ cached" chip

## Motion Principles

1. **Purpose over polish.** Every animation earns its place by clarifying state change.
2. **Fast enter, slow exit.** Enter in ~250ms (snappy); exit in ~500ms (graceful).
3. **Pulse on significance.** Anomaly events pulse the affected widget — scale 1.0→1.04→1.0 on a 900ms loop until user interacts or anomaly expires.
4. **No parallax, no confetti.** Avoid decorative motion that doesn't convey info. Tennis is a serious signal product.
5. **Throttle motion on per-frame data.** Motion only runs on state-update events, not on per-frame ref updates (that's canvas territory).

## Motion Implementation

```tsx
import { motion } from "motion/react";

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: 20 }}
  transition={{ duration: motion.regular, ease: motion.easeOutQuart }}
>
  {content}
</motion.div>
```

For pulse-on-anomaly:
```tsx
<motion.div
  animate={isAnomaly ? { scale: [1, 1.04, 1] } : { scale: 1 }}
  transition={isAnomaly ? { duration: 0.9, repeat: Infinity } : { duration: 0.3 }}
>
```

## Layout Grid

- 12-column CSS Grid
- Top row: PlayerA Nameplate (cols 1-3) · MomentumMeter (cols 4-9) · PlayerB Nameplate (cols 10-12)
- Middle rows: Video (8 cols) · SignalBar stack (4 cols)
- Bottom row: CoachPanel (full width, 3-col tall)

## Anti-Patterns

- ❌ Glassmorphism for its own sake (can work if subtle; avoid heavy blurs that tank FPS)
- ❌ Neon gradients everywhere (reserve for single accent element)
- ❌ Over-animated loading spinners (use skeleton placeholders instead)
- ❌ Tiny text over video (ensure ≥14px with heavy weight + subtle background scrim)
- ❌ Red as a baseline color — red means anomaly in our system

## Figma MCP Workflow

1. Use `figma` MCP with Opus 4.7 to generate a HUD layout mockup
2. Extract design tokens manually (copy colors, dimensions, spacing)
3. Translate to Tailwind config + `design-tokens.ts`
4. Do NOT try to auto-generate React code from Figma — reliability is too low
5. Use Figma as looking tool; hand-write Tailwind classes

## Aesthetic Litmus Test

Before committing a HUD change, ask:
1. Could this appear in an NBA 2K in-game HUD? If not, why?
2. Does the motion convey info or just look cool?
3. Is every widget earning its screen real estate?
4. Does the color encode meaning (z-score severity)?
5. Would a judge watching for 3 minutes say "I want that for my sport"?
