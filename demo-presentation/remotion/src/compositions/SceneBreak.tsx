import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';

/**
 * SceneBreak — between-beat transition card (PLAN.md §6 A6, §5.6).
 *
 * Sits between major B-beats in the DaVinci composite. Hard-cut in, hard-cut
 * out (Anthropic motion vocabulary — PATTERN-078). Brief enough to feel like
 * a beat-marker, long enough to read.
 *
 * Anthropic editorial layout pattern:
 *   - small kicker label above (mono caps, muted) — e.g., "BEAT 02"
 *   - big scene title below (Fraunces serif) — e.g., "The Sensor"
 *   - thin cyan rule under the title (subtle accent, like an underline pass)
 *   - centered, generous air, ~85% breath / 15% content
 *
 * Total duration: 1.5 seconds = 90 frames at 60 fps.
 *
 * Motion (per PATTERN-078 restraint vocabulary):
 *   - kicker fades in 0-0.3s
 *   - title scale-pops 0.2-0.6s (mild overshoot)
 *   - cyan rule wipes left-to-right 0.4-0.7s
 *   - HOLD 0.7-1.2s
 *   - exit fade 1.2-1.5s
 */

const { fontFamily: FRAUNCES_FAMILY } = loadFraunces();

const BG = '#05080F';
const INK_PRIMARY = '#F8FAFC';
const INK_MUTED = '#5A6678';
const ACCENT_CYAN = '#00E5FF';
const FONT_MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';

export interface SceneBreakProps {
  /** Beat number — e.g., "BEAT 02". Use "01", "02", etc. as a string. */
  beatNumber: string;
  /** Beat title — e.g., "The Sensor", "Opus Reads the Body". */
  title: string;
  /** Optional subtitle / kicker (sits under the title rule). Mono caps. */
  subtitle?: string;
}

export const SceneBreak = ({
  beatNumber,
  title,
  subtitle,
}: SceneBreakProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Kicker fades in 0-0.3s (frames 0-18)
  const kickerOpacity = interpolate(frame, [0, 18], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Title spring-pops at frame 12 (0.2s)
  const titleSpring = spring({
    frame: Math.max(0, frame - 12),
    fps,
    config: { damping: 14, stiffness: 180 },
  });
  const titleScale = interpolate(titleSpring, [0, 1], [0.94, 1]);
  const titleOpacity = interpolate(frame, [12, 36], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Cyan rule wipes left-to-right 0.4-0.7s (frames 24-42)
  const ruleProgress = interpolate(frame, [24, 42], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Subtitle fades in 0.6-0.9s (frames 36-54)
  const subtitleOpacity = interpolate(frame, [36, 54], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Exit fade 1.2-1.5s (frames 72-90)
  const exitOpacity = interpolate(frame, [72, 90], [1, 0], {
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
      <div style={{ textAlign: 'center', minWidth: 720 }}>
        {/* Kicker — beat number */}
        <div
          style={{
            fontFamily: FONT_MONO,
            fontSize: 14,
            letterSpacing: '0.32em',
            color: INK_MUTED,
            textTransform: 'uppercase',
            marginBottom: 28,
            opacity: kickerOpacity,
          }}
        >
          beat {beatNumber}
        </div>

        {/* Title — Fraunces serif, title-case */}
        <div
          style={{
            fontFamily: FRAUNCES_FAMILY,
            fontSize: 96,
            fontWeight: 600,
            letterSpacing: '-0.015em',
            color: INK_PRIMARY,
            lineHeight: 1.0,
            fontFeatureSettings: '"ss01" 1, "ss02" 1',
            transform: `scale(${titleScale})`,
            opacity: titleOpacity,
            marginBottom: 24,
          }}
        >
          {title}
        </div>

        {/* Cyan rule — wipes left-to-right under the title */}
        <div
          style={{
            margin: '0 auto',
            height: 2,
            background: ACCENT_CYAN,
            width: `${ruleProgress * 280}px`,
            transformOrigin: 'left center',
          }}
        />

        {/* Optional subtitle below the rule */}
        {subtitle && (
          <div
            style={{
              fontFamily: FONT_MONO,
              fontSize: 13,
              letterSpacing: '0.22em',
              color: INK_MUTED,
              textTransform: 'uppercase',
              marginTop: 28,
              opacity: subtitleOpacity,
            }}
          >
            {subtitle}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ──────────────────────────── Demo composition ────────────────────────────
// One concrete instance — the B2 "Sensor" scene-break. Other beats wrap
// SceneBreak with their own props; this is the canonical one for testing +
// a usable artifact for the DaVinci composite.

export const SceneBreakB2 = () => (
  <SceneBreak
    beatNumber="02"
    title="The Sensor"
    subtitle="yolo11m-pose · kalman on court meters · 7 biomech signals"
  />
);

export const SceneBreakB3 = () => (
  <SceneBreak
    beatNumber="03"
    title="The Recurrence"
    subtitle="anomaly · t = 45.3s · σ 2.5 crouch-depth"
  />
);

export const SceneBreakB4 = () => (
  <SceneBreak
    beatNumber="04"
    title={'Opus Reads the Body'}
    subtitle="adaptive thinking · cached · dual-hypothesis discipline"
  />
);
