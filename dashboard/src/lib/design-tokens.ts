/**
 * Design tokens for the PANOPTICON LIVE HUD.
 *
 * Single source of truth for colors, motion, spacing, radii, and typography.
 * Every widget in `dashboard/src/components/Broadcast/` reads from these tokens,
 * NOT raw hex / raw strings.
 *
 * v2 PALETTE — warm dark broadcast (DECISION-017, 2026-04-24 evening).
 *
 * v1 → v2 pivot rationale (3-agent research wave + Andrew framing "how would
 * Anthropic release this demo if they built our product?"):
 *   - 2025-2026 craft language across Anthropic / Linear / Vercel / Tendril / Arc
 *     converges on monochrome warm foundation + ONE saturated accent (PATTERN-077).
 *   - v1's #00E5FF cyan-on-#0A0E1A was the "sci-fi HUD bloat" anti-pattern (GOTCHA-044).
 *   - v2 adopts Anthropic's published Clay #D97757 as the lone accent + warm dark
 *     slate foundation. Matches the Remotion B0 opener (demo-presentation/remotion/src/tokens.ts).
 *   - Insurance: cyan-baseline preserved at git commit 708b536. `git revert` to roll back.
 */

/** Color tokens — v2 warm dark broadcast palette. */
export const colors = {
  // Player identifiers — v2: clay accent, no cyan
  playerA: '#D97757', // Anthropic Clay — THE saturated accent (was #00E5FF cyan)
  playerB: '#A89E92', // warm gray (was coral red — drawing disabled per DECISION-008 anyway)

  // Signal state (tone mapping from z-score via zScoreToTone.ts)
  // v2: state scale lives within the warm family; fatigue = brand accent (it IS our hero signal).
  baseline: '#7E7060', // warm slate — |z| < 1, neutral state (was cool slate #64748B)
  energized: '#8A9474', // muted olive — z ≥ 1, higherIs: 'energy' (rare, low-saturation complement to clay)
  fatigued: '#E89B6F', // clay-bright — z ≥ 1, higherIs: 'fatigue' | 'drift' (matches accent family)
  anomaly: '#C04A2C', // rust red — |z| ≥ 2 in any direction (warm danger signal, was #EF4444)
  opusThinking: '#D97757', // Anthropic Clay — Opus voice = brand accent (consistent identity)

  // Background layers — v2: warm slate progression
  bg0: '#1A1614', // warm slate-black (was #0A0E1A cool deep-blue)
  bg1: '#26201D', // warm card background (was #0F1524)
  bg2: '#332B25', // warm elevated widget (was #1A2238)
  border: '#3A3128', // warm hairline (was #243049)
  borderAccent: '#7E4634', // clay-dim — accent borders (was cool blue #3B4F7E)

  // Text — v2: warm cream/gray progression
  textPrimary: '#F2EAE0', // warm cream (was cool #F8FAFC)
  textSecondary: '#A89E92', // warm gray (was cool slate #CBD5E1)
  textMuted: '#5A5247', // warm muted (was cool slate #64748B)
} as const;

/**
 * Motion tokens.
 *
 * Every `<motion.*>` transition in the Broadcast layer MUST reference one of
 * these springs (PATTERN-044). No `easeOutQuart` / fixed-duration tweens on
 * any value that updates from the 10Hz state stream — spring physics is the
 * bridge between 10Hz data and 60FPS displayed motion.
 */
export const motion = {
  /** Widget mount/exit — natural snap without overshoot. */
  springStandard: { type: 'spring' as const, stiffness: 260, damping: 22 },
  /** Bar fill / value chases — stiff, quick chase. */
  springFirm: { type: 'spring' as const, stiffness: 300, damping: 30 },
  /** Layout shifts / large rearrangements — slower + more damped. */
  springGentle: { type: 'spring' as const, stiffness: 180, damping: 26 },

  /** Short tweens — only for small non-data transitions (chevron flip, chip cross-fade). */
  tweenQuick: { duration: 0.2, ease: [0.25, 1, 0.5, 1] as const },
  tweenRegular: { duration: 0.4, ease: [0.25, 1, 0.5, 1] as const },
} as const;

/** Spacing scale (px). */
export const space = {
  xxs: 4,
  xs: 8,
  sm: 12,
  md: 16,
  lg: 20,
  xl: 28,
  xxl: 40,
} as const;

/** Border radii (px). */
export const radii = {
  sm: 4,
  md: 8,
  lg: 12,
  pill: 999,
} as const;

/** Typography sizes (px). */
export const typography = {
  size: {
    micro: 10,
    caption: 11,
    small: 12,
    body: 14,
    subheading: 16,
    heading: 18,
    title: 24,
  },
  weight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
} as const;

/** Shadow tokens (used sparingly — broadcast UIs are flat). */
export const shadows = {
  glowPlayerA: `0 0 24px ${colors.playerA}33`,
  glowAnomaly: `0 0 20px ${colors.anomaly}66`,
  cardElevation: '0 4px 24px rgba(0, 0, 0, 0.4)',
} as const;
