import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

/**
 * B5 — Closing card (PLAN.md §6 A6, §5.6 / §5.7 Vimeo-Numerai influence).
 *
 * Layered influence:
 *   - Anthropic editorial layout (kicker → hero wordmark → URL → attribution)
 *   - Vimeo 205032211 / Numerai craft moves (PATTERN-082, PATTERN-084):
 *       1. Wordmark IGNITION via brightness + glow curve (NOT scale-pop).
 *          Numerai's "logo-ignition" reads as neon-tube voltage; matches our
 *          broadcast-HUD register where cyan = "live telemetry powering on."
 *       2. URL line softened from #F8FAFC to #B8B8B8 — Numerai's "whispered
 *          70-75% gray" rule. Kicker/attribution stay at #5A6678 (already
 *          softer than the Numerai recommendation; no change needed).
 *          Hero wordmark stays bright (#F8FAFC) — it IS the logo.
 *       3. Slow ~2% drift across full 5s composition. Camera-alive cue
 *          (Numerai cinematic plates) without Ken Burns aggression.
 *
 * Cyan palette retained per USER-CORRECTION-036 — broadcast HUD context where
 * cyan is the native data color. Fraunces + italic emphasis is the typography
 * upgrade that survives the palette decision (PATTERN-078).
 *
 * Why ONE card and not Numerai's two-card (sigil-monument → URL-void):
 *   The structural magic of Numerai's two-card is the VISUAL REGISTER SWITCH
 *   between cinematic plate and typographic void. Our composition has only
 *   ONE register (typographic void on cool slate). Splitting one register
 *   into two cards is just longer dwell time without the magic. We adopt
 *   the smaller surgical wins instead. See PATTERN-083.
 *
 * Total duration: 5 seconds = 300 frames at 60 fps.
 */

const { fontFamily: FRAUNCES_FAMILY } = loadFraunces();

const BG = '#05080F';
const INK_PRIMARY = '#F8FAFC';        // hero wordmark — bright (it IS the logo)
const INK_URL = '#B8B8B8';            // URL line — Numerai 70-75% gray "whispered, not shouted" (PATTERN-082)
const INK_MUTED = '#5A6678';          // kicker, repo, attribution — already softer than Numerai recommends
const ACCENT_CYAN = '#00E5FF';
const FONT_MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';

export const B5Closing = () => {
  const frame = useCurrentFrame();

  // Kicker fades in 0-0.5s (frames 0-30)
  const kickerOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Wordmark IGNITION 0.3-0.8s (frames 18-48) — brightness + glow curve.
  // Replaces prior scale-pop spring per PATTERN-082 ("logo ignition vs scale-pop").
  const ignitionProgress = interpolate(frame, [18, 48], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const wordmarkBrightness = interpolate(ignitionProgress, [0, 1], [0.55, 1.0]);
  const wordmarkGlowBlur = interpolate(ignitionProgress, [0, 1], [0, 18]);
  const wordmarkOpacity = ignitionProgress;

  // URL + attribution fade in 1.0-1.5s (frames 60-90)
  const metaOpacity = interpolate(frame, [60, 90], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Slow ~2% drift across full 5s — Numerai cinematic-plate "camera alive" cue.
  const driftScale = interpolate(frame, [0, 300], [1.0, 1.02], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Subtle exit fade in last 30 frames (270-300)
  const exitOpacity = interpolate(frame, [270, 300], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: BG,
        justifyContent: 'center',
        alignItems: 'center',
        opacity: exitOpacity,
      }}
    >
      <div
        style={{
          textAlign: 'center',
          transform: `scale(${driftScale})`,
          transformOrigin: 'center center',
        }}
      >
        {/* Kicker — small label above the wordmark, mono caps */}
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 12,
            letterSpacing: '0.28em',
            color: INK_MUTED,
            textTransform: 'uppercase',
            marginBottom: 36,
            opacity: kickerOpacity,
          }}
        >
          biomechanical fatigue telemetry · from 2d broadcast pixels
        </div>

        {/* Hero wordmark — Fraunces serif, italic "Live" in cyan accent.
            IGNITION via brightness + cyan-glow drop-shadow (Numerai DNA, PATTERN-082).
            Replaces prior scale-pop spring. The cyan halo on the white "Panopticon"
            text is the "neon-tube voltage" effect; the white text reads as the
            tube's filament, the cyan halo as the gas glow. */}
        <div
          style={{
            fontFamily: FRAUNCES_FAMILY,
            fontSize: 144,
            fontWeight: 600,
            letterSpacing: '-0.02em',
            color: INK_PRIMARY,
            whiteSpace: 'nowrap',
            lineHeight: 0.95,
            fontFeatureSettings: '"ss01" 1, "ss02" 1',
            filter: `brightness(${wordmarkBrightness}) drop-shadow(0 0 ${wordmarkGlowBlur}px rgba(0, 229, 255, 0.35))`,
            opacity: wordmarkOpacity,
          }}
        >
          Panopticon <span style={{ color: ACCENT_CYAN, fontStyle: 'italic' }}>Live</span>
        </div>

        {/* URL line — softened to #B8B8B8 per Numerai's "whispered" body-copy rule
            (PATTERN-082). Still WCAG AAA contrast on #05080F (~7.5:1). */}
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 18,
            letterSpacing: '0.06em',
            color: INK_URL,
            marginTop: 56,
            opacity: metaOpacity,
          }}
        >
          panopticon-live.vercel.app
        </div>
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 13,
            letterSpacing: '0.18em',
            color: INK_MUTED,
            textTransform: 'uppercase',
            marginTop: 14,
            opacity: metaOpacity,
          }}
        >
          github.com / andydiaz122 / panopticon-live
        </div>

        {/* Built-with-Claude attribution — bottom-most, smallest */}
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 11,
            letterSpacing: '0.24em',
            color: INK_MUTED,
            textTransform: 'uppercase',
            marginTop: 56,
            opacity: metaOpacity,
          }}
        >
          built with claude opus 4.7 · april 2026 · MIT licensed
        </div>
      </div>
    </AbsoluteFill>
  );
};
