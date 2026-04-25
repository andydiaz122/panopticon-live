import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

import { AmbientGrid } from '../primitives/AmbientGrid';
import { ChapterMarker } from '../primitives/ChapterMarker';

const { fontFamily: FRAUNCES_FAMILY } = loadFraunces();

/**
 * B5ClosingV2 — Tier-1 world-class brand closing card.
 *
 * Replaces B5Closing (toy-tier — 5s, 2-beat single-frame). Per the
 * `remotion-cinematic-craft` skill's bookend-pair spec: shares the V2 family's
 * visual vocabulary with B0OpenerV2 (same ChapterMarker chrome, same AmbientGrid
 * L5, same kerning sweep + italic reveal beat typography). Continuity IS the
 * chapter identity. Chapter ID changes from "ch.00 / ORIGIN" to "ch.05 / VISION"
 * — same chrome style, same cyan accent line, but the theme tells the viewer
 * we've arrived at the closing chapter.
 *
 * Beat structure (60 fps, 12s = 720 frames @ 120 BPM = 6 bars):
 *   B1  0-180   (0:00-0:03, 3s)  CHROME ARRIVAL  ChapterMarker materializes,
 *                                                AmbientGrid drifts, void breath
 *   B2  180-420 (0:03-0:07, 4s)  WORDMARK IGNITE Hero "Panopticon Live" with
 *                                                kerning sweep on upright +
 *                                                italic reveal beat + cyan-glow
 *                                                ignition curve (PATTERN-082)
 *   B3  420-600 (0:07-0:10, 3s)  URL REVEAL      Kicker subtitle fades + URL
 *                                                with per-character stagger
 *                                                (Pattern C from skill) + repo
 *                                                line below
 *   B4  600-720 (0:10-0:12, 2s)  ATTRIBUTION     Built-with line fades in,
 *                                                gentle exit fade for hard-cut
 *                                                to B5ThesisV2
 */

const BG = '#05080F';
const INK_PRIMARY = '#F8FAFC';      // hero wordmark
const INK_KICKER = '#B8B8B8';       // Numerai whispered subtitle (PATTERN-082)
const INK_URL = '#B8B8B8';          // URL — same whispered gray as kicker
const INK_MUTED = '#5A6678';        // repo + attribution chrome
const ACCENT_CYAN = '#00E5FF';
const FONT_MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';

// ──────────────────────────── Beat boundaries ────────────────────────────

const B2_START = 180;       // wordmark begins materializing
const WORDMARK_KERN_START = B2_START + 30;
const WORDMARK_KERN_END = WORDMARK_KERN_START + 36;
// italic reveal fires 12 frames after kerning starts (Pattern B)

const B3_START = 420;       // URL stagger begins
const KICKER_FADE_END = B3_START + 30;
const URL_STAGGER_START = B3_START + 60;
const REPO_FADE_START = URL_STAGGER_START + 90;
const REPO_FADE_END = REPO_FADE_START + 30;

const B4_START = 600;       // attribution fades in
const ATTRIBUTION_FADE_END = B4_START + 30;
const EXIT_FADE_START = 690;
const EXIT_FADE_END = 720;

const URL_TEXT = 'panopticon-live.vercel.app';

// ──────────────────────────── Composition ────────────────────────────

export const B5ClosingV2 = () => {
  const frame = useCurrentFrame();

  const sceneOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const exitOpacity = interpolate(
    frame,
    [EXIT_FADE_START, EXIT_FADE_END],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: BG,
        opacity: sceneOpacity * exitOpacity,
        overflow: 'hidden',
      }}
    >
      {/* L1 BG (slate via AbsoluteFill) + L5 ambient grid */}
      <AmbientGrid driftDurationFrames={720} spacing={80} opacity={0.045} />

      {/* L2 chrome — "ch.05 / VISION", brand mark suppressed (wordmark IS the brand here) */}
      <ChapterMarker
        chapterId="ch.05"
        chapterTheme="VISION"
        fadeInFrame={30}
        fadeInDuration={60}
        showTimecode={true}
        showBreadcrumb={true}
        showBrandMark={false}
        timecodeStartFrame={0}
      />

      {/* L3 hero — wordmark with ignition curve + kerning sweep + italic reveal beat */}
      <Sequence from={B2_START}>
        <WordmarkHero />
      </Sequence>

      {/* L4 supporting — URL stagger + repo + attribution */}
      <Sequence from={B3_START}>
        <ClosingFooter />
      </Sequence>
    </AbsoluteFill>
  );
};

// ──────────────────────────── Hero wordmark (Pattern A + B + ignition) ────────────────────────────

const WordmarkHero = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Ignition curve — brightness + glow over 30 frames (PATTERN-082)
  const ignitionProgress = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const wordmarkBrightness = interpolate(ignitionProgress, [0, 1], [0.5, 1.0]);
  const wordmarkGlowBlur = interpolate(ignitionProgress, [0, 1], [0, 24]);

  // Kerning sweep on upright "Panopticon" (Pattern A) — local frames 30-66
  const kerningProgress = interpolate(frame, [30, 66], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const wordmarkLetterSpacingEm = interpolate(kerningProgress, [0, 1], [0.5, -0.02]);

  // Italic reveal beat (Pattern B) — fires 12 frames after upright kerning starts
  const italicLocalFrame = Math.max(0, frame - 42);
  const italicSpring = spring({
    frame: italicLocalFrame,
    fps,
    config: { damping: 14, stiffness: 200 },
  });
  const italicOpacity = interpolate(italicLocalFrame, [0, 24], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const italicScale = interpolate(italicSpring, [0, 1], [0.92, 1]);

  // Subtle pulse on cyan word — 1.5 cycle over remaining ~6s
  const pulseLocalFrame = Math.max(0, frame - 90);
  const pulseAlpha = pulseLocalFrame > 0
    ? 0.45 + 0.20 * Math.sin((pulseLocalFrame / 180) * Math.PI * 2)
    : 0.45;

  return (
    <div
      style={{
        position: 'absolute',
        top: '38%',
        left: 0,
        right: 0,
        textAlign: 'center',
        opacity: ignitionProgress,
      }}
    >
      <div
        style={{
          fontFamily: FRAUNCES_FAMILY,
          fontSize: 168,
          fontWeight: 600,
          letterSpacing: `${wordmarkLetterSpacingEm}em`,
          color: INK_PRIMARY,
          whiteSpace: 'nowrap',
          lineHeight: 0.95,
          fontFeatureSettings: '"ss01" 1, "ss02" 1',
          filter: `brightness(${wordmarkBrightness}) drop-shadow(0 0 ${wordmarkGlowBlur}px rgba(0, 229, 255, ${pulseAlpha}))`,
          display: 'inline-block',
        }}
      >
        Panopticon{' '}
        <span
          style={{
            color: ACCENT_CYAN,
            fontStyle: 'italic',
            opacity: italicOpacity,
            display: 'inline-block',
            transform: `scale(${italicScale})`,
            transformOrigin: 'left center',
          }}
        >
          Live
        </span>
      </div>
    </div>
  );
};

// ──────────────────────────── Closing footer (kicker + URL stagger + repo + attribution) ────────────────────────────

const ClosingFooter = () => {
  const frame = useCurrentFrame();
  // local to B3_START Sequence

  // Kicker fades in 0-30
  const kickerOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // URL per-character stagger — Pattern C from skill. Starts at local frame 60.
  const urlStaggerLocalStart = URL_STAGGER_START - B3_START; // = 60
  const urlChars = URL_TEXT.split('');

  // Repo line fades in at local frame 150 (URL stagger ends ~134)
  const repoLocalStart = REPO_FADE_START - B3_START; // = 150
  const repoLocalEnd = REPO_FADE_END - B3_START;     // = 180
  const repoOpacity = interpolate(frame, [repoLocalStart, repoLocalEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Attribution — fades in at local frame 180 (= absolute B4_START 600 - B3_START 420)
  const attribLocalStart = B4_START - B3_START;          // = 180
  const attribLocalEnd = ATTRIBUTION_FADE_END - B3_START; // = 210
  const attribOpacity = interpolate(frame, [attribLocalStart, attribLocalEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        top: '60%',
        left: 0,
        right: 0,
        textAlign: 'center',
      }}
    >
      {/* Kicker subtitle — Anthropic-style mono caps editorial label */}
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 13,
          letterSpacing: '0.28em',
          color: INK_KICKER,
          textTransform: 'uppercase',
          opacity: kickerOpacity,
          marginBottom: 64,
        }}
      >
        biomechanical fatigue telemetry · from 2d broadcast pixels
      </div>

      {/* URL with per-character stagger (Pattern C) */}
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 22,
          letterSpacing: '0.04em',
          color: INK_URL,
          marginBottom: 18,
          fontVariantNumeric: 'tabular-nums',
        }}
      >
        {urlChars.map((char, i) => {
          const charStart = urlStaggerLocalStart + i * 2;
          const charOpacity = interpolate(frame, [charStart, charStart + 12], [0, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          return (
            <span key={i} style={{ opacity: charOpacity }}>
              {char === ' ' ? ' ' : char}
            </span>
          );
        })}
      </div>

      {/* Repo line — fades in after URL stagger completes */}
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 13,
          letterSpacing: '0.18em',
          color: INK_MUTED,
          textTransform: 'uppercase',
          opacity: repoOpacity,
          marginBottom: 64,
        }}
      >
        github.com / andydiaz122 / panopticon-live
      </div>

      {/* Built-with attribution — final beat */}
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          letterSpacing: '0.32em',
          color: INK_MUTED,
          textTransform: 'uppercase',
          opacity: attribOpacity,
        }}
      >
        built with claude opus 4.7 · april 2026 · MIT licensed
      </div>
    </div>
  );
};
