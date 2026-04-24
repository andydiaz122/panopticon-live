/**
 * Design tokens for PANOPTICON LIVE Remotion compositions.
 *
 * v5 palette — warm dark broadcast, post-research-wave (2026-04-24 evening).
 *
 * THE SINGLE SOURCE OF TRUTH for color and typography across every
 * Remotion composition. Derived from the 3-agent research wave:
 *   - Anthropic release-video frame-sampling (anthropic_video_dna.md)
 *   - Awwwards/Tendril/Linear/Vercel/Arc audit (remotion_craft_patterns.md)
 *   - Figma → Remotion workflow research (figma_remotion_workflow.md)
 *
 * Craft rules embedded in this token set:
 *   1. Monochrome warm foundation + ONE saturated accent (PATTERN-077).
 *   2. The accent is reserved for the product's HERO SIGNAL (fatigue / AI voice).
 *   3. Three fonts max: serif headlines + sans body + mono for data only.
 *
 * To iterate the palette: edit hex values here, re-render, no other file edits.
 * (Per Agent C's Figma Variables → DTCG JSON → tokens.ts pattern, PATTERN-081.)
 */

// ──────────────────────────── Color palette ────────────────────────────

/** Background — primary. Warm slate-black, never pure #000000. */
export const BG_PRIMARY = '#1A1614';

/** Background — panel/card surface. Subtle elevation without drop shadow. */
export const BG_PANEL = '#26201D';

/** Border / hairline. Warm dark gray. */
export const BORDER = '#3A3128';

/** Ink — primary. Hero text, headlines. Warm cream — Anthropic body-ink inverted for dark mode. */
export const INK_PRIMARY = '#F2EAE0';

/** Ink — secondary. Body text, labels. Warm gray. */
export const INK_SECONDARY = '#A89E92';

/** Ink — muted. Sublabels, terminal headers, timestamps. */
export const INK_MUTED = '#5A5247';

/**
 * Accent — Anthropic Clay. THE ONLY SATURATED COLOR ON SCREEN.
 *
 * Reserved for: fatigue/anomaly indicators, AI voice in dialog,
 * hero numerics, the gitgraph's "live progress" line, the landing
 * anchor on the journey timeline. Never used for chrome/borders/dividers.
 *
 * Source: Anthropic published brand kit (#D97757). Frame-sampled at
 * #D07050 in the actual release videos (lighting variance). We use
 * the published canonical.
 */
export const ACCENT_CLAY = '#D97757';

/** Accent — dim variant. Pre-anomaly state, fatigue baseline, dim progress. */
export const ACCENT_CLAY_DIM = '#7E4634';

/** Accent — peak. Anomaly intensity, used sparingly for "the moment." */
export const ACCENT_CLAY_PEAK = '#E89B6F';

// ──────────────────────────── Typography ────────────────────────────

/**
 * Headline / hero display — transitional serif. Free Google Fonts substitute
 * for Copernicus/Tiempos which Anthropic uses on Opus 4.6 wordmark.
 *
 * Wired via @remotion/google-fonts/Fraunces in compositions that use it.
 * Falls back to ui-serif if the font hasn't loaded.
 */
export const FONT_DISPLAY = '"Fraunces", "Iowan Old Style", "Palatino Linotype", ui-serif, serif';

/**
 * Body / UI / captions — humanist sans. Free substitute for Styrene B / "Claude Sans"
 * which Anthropic uses for chat UI and overlays. Inter is the cleanest choice; falls
 * back to system-ui.
 */
export const FONT_BODY = '"Inter", "Helvetica Neue", system-ui, -apple-system, sans-serif';

/**
 * Data / timestamps / terminal — monospace. JetBrains Mono is already wired in
 * the dashboard side; matching here means OBS capture composites cleanly with
 * Remotion chrome.
 */
export const FONT_MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';

// ──────────────────────────── Spacing scale (px) ────────────────────────────

export const SPACE = {
  xxs: 4,
  xs: 8,
  sm: 12,
  md: 16,
  lg: 24,
  xl: 40,
  xxl: 64,
  xxxl: 96,
} as const;

// ──────────────────────────── Motion primitives ────────────────────────────

/**
 * Spring config for the standard "scale-pop" entrance (PATTERN-078).
 * Mild overshoot, ~250 ms resolve. Matches Anthropic's wordmark scale-up.
 */
export const SPRING_SCALE_POP = {
  damping: 12,
  stiffness: 180,
} as const;

/**
 * Spring config for gentler entrances (large layout moves).
 * Lower stiffness = slower, more deliberate.
 */
export const SPRING_GENTLE = {
  damping: 18,
  stiffness: 120,
} as const;

/**
 * Tween durations (ms). Keep the menu small per PATTERN-078.
 *   - QUICK = chevron flip, chip cross-fade
 *   - REGULAR = scene-internal element fade
 *   - SLOW = whole-scene transitions, opening/closing wipes
 */
export const TWEEN_MS = {
  QUICK: 200,
  REGULAR: 400,
  SLOW: 600,
} as const;

/**
 * Typewriter character reveal rate. 25 cps matches the agent_trace
 * playback baud rate in Tab 3 of the dashboard — composites cleanly.
 */
export const TYPEWRITER_CPS = 25;
