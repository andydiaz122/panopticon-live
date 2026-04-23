/**
 * Design tokens for the PANOPTICON LIVE HUD.
 *
 * Single source of truth for colors, motion, spacing, radii, and typography.
 * Every widget in `dashboard/src/components/Broadcast/` reads from these tokens,
 * NOT raw hex / raw strings. Matches `.claude/skills/2k-sports-hud-aesthetic/SKILL.md`.
 */

/** Color tokens. Hex values match the 2k-sports-hud-aesthetic skill. */
export const colors = {
  // Player identifiers
  playerA: '#00E5FF', // analytics cyan (NOT pure #00FFFF — canonical per skill)
  playerB: '#FF3D71', // coral red (retained for token completeness; drawing disabled per DECISION-008)

  // Signal state (tone mapping from z-score via zScoreToTone.ts)
  baseline: '#64748B', // slate — |z| < 1
  energized: '#34D399', // emerald — z ≥ 1, higherIs: 'energy'
  fatigued: '#F59E0B', // amber — z ≥ 1, higherIs: 'fatigue' | 'drift'
  anomaly: '#EF4444', // red — |z| ≥ 2 in any direction
  opusThinking: '#A855F7', // purple — Opus voice

  // Background layers
  bg0: '#0A0E1A', // deep near-black
  bg1: '#0F1524', // card background
  bg2: '#1A2238', // elevated widget
  border: '#243049',
  borderAccent: '#3B4F7E',

  // Text
  textPrimary: '#F8FAFC',
  textSecondary: '#CBD5E1',
  textMuted: '#64748B',
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
