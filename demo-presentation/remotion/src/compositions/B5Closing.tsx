import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

/**
 * B5 — Closing card (PLAN.md §6 A6, §5.6 Anthropic-workflow-minus-palette).
 *
 * Anthropic editorial layout pattern (frame-sampled from Opus 4.6 + Chrome films):
 *   - small caption above (kicker)
 *   - big wordmark below — Fraunces serif, italic emphasis on accent term
 *   - URL / repo line
 *   - "Built with Claude Opus 4.7" attribution
 *   - All lines centered, generous vertical air
 *   - Hard cut entry, ~3-5 second hold (Anthropic closing convention)
 *
 * Cyan palette retained per USER-CORRECTION-036 — broadcast HUD context where
 * cyan is the native data color. Fraunces + italic emphasis is the typography
 * upgrade that survives the palette decision (PATTERN-078 / 5.6.1).
 *
 * Motion vocabulary (PATTERN-078 — restraint IS the brand):
 *   - kicker fades in 0-0.5s
 *   - wordmark spring-pops 0.3-0.8s (scale 0.9 -> 1.0, mild overshoot)
 *   - URL + attribution fade in 1.0-1.5s
 *   - everything HOLDS for ~3.5s
 *   - subtle exit fade (or hard cut to black in DaVinci composite)
 *
 * Total duration: 5 seconds = 300 frames at 60 fps.
 */

const { fontFamily: FRAUNCES_FAMILY } = loadFraunces();

const BG = '#05080F';
const INK_PRIMARY = '#F8FAFC';
const INK_MUTED = '#5A6678';
const ACCENT_CYAN = '#00E5FF';
const FONT_MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';

export const B5Closing = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Kicker fades in 0-0.5s (frames 0-30)
  const kickerOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Wordmark spring-pop at frame 18 (0.3s)
  const wordmarkSpring = spring({
    frame: Math.max(0, frame - 18),
    fps,
    config: { damping: 14, stiffness: 160 },
  });
  const wordmarkScale = interpolate(wordmarkSpring, [0, 1], [0.92, 1]);
  const wordmarkOpacity = interpolate(frame, [18, 48], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // URL + attribution fade in 1.0-1.5s (frames 60-90)
  const metaOpacity = interpolate(frame, [60, 90], [0, 1], {
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
      <div style={{ textAlign: 'center' }}>
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

        {/* Hero wordmark — Fraunces serif, italic "Live" in cyan accent */}
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
            transform: `scale(${wordmarkScale})`,
            opacity: wordmarkOpacity,
          }}
        >
          Panopticon <span style={{ color: ACCENT_CYAN, fontStyle: 'italic' }}>Live</span>
        </div>

        {/* URL + repo */}
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 18,
            letterSpacing: '0.06em',
            color: INK_PRIMARY,
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
