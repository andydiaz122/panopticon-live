import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

import { AmbientGrid } from '../primitives/AmbientGrid';
import { ChapterMarker } from '../primitives/ChapterMarker';
import { GitGraph, type GitAnchor } from '../primitives/GitGraph';
import { TypingLine } from '../primitives/TypingLine';

const { fontFamily: FRAUNCES_FAMILY } = loadFraunces();

/**
 * B0OpenerV2 — Tier-1 world-class opener (USER-CORRECTION-037 response).
 *
 * Replaces B0Opener (toy-tier — 25s, 3-beat, single-element, no chapter
 * identity, no music-bed timing). This V2 is authored to the
 * `remotion-cinematic-craft` skill's standards:
 *
 *   • 36s duration (skill min for story moments: 8s; opener should be longest)
 *   • 6 internal beats with explicit hard-cut transitions on bar lines
 *   • All 5 anatomy layers active (L1 field, L2 chrome, L3 hero, L4 context, L5 motion)
 *   • Pseudo-tempo 120 BPM = beat every 30 frames; 4-bar phrases at 240 frames
 *     → beat boundaries land on bar lines (4s/12s/18s/27s/32s/36s)
 *   • Typography animation: kerning sweep on hero wordmark + italic reveal beat
 *   • Chapter identity: persistent ChapterMarker showing "ch.00 / ORIGIN"
 *   • Numerai cinematic-plate slow drift (existing GitGraph drift) + AmbientGrid L5
 *
 * Beat structure (60 fps):
 *   B1  0-240    (0:00-0:04, 4s)   VOID BREATH    Chrome materializes, cursor blinks
 *   B2  240-720  (0:04-0:12, 8s)   USER QUESTION  Types "hey claude, is the world",
 *                                                  italic-reveal "malleable?" as accent
 *                                                  beat, then 4.5s philosophical hang
 *   B3  720-1080 (0:12-0:18, 6s)   CLAUDE RESPONSE  Cyan typing "yes — build what
 *                                                  you need" with italic accent on
 *                                                  "build", then 3s hold
 *   B4  1080-1620 (0:18-0:27, 9s)  GIT TIMELINE   Dialog dims, line draws, 5
 *                                                  staggered anchors with kerning-
 *                                                  sweep labels, slow-drift parallax
 *   B5  1620-1920 (0:27-0:32, 5s)  IGNITION       Final anchor cyan-pulses, hero
 *                                                  wordmark materializes below with
 *                                                  kerning sweep + italic reveal beat
 *                                                  + brightness-glow ignition curve
 *   B6  1920-2160 (0:32-0:36, 4s)  HOLD + EXIT    Kicker subtitle + built-with
 *                                                  attribution fade in, glow pulse
 *                                                  on cyan word, gentle exit fade
 *                                                  for hard-cut to B1 in DaVinci
 *
 * Persistent chrome (all beats):
 *   • AmbientGrid (L5)        — slow-drifting faint grid, 18s drift cycle
 *   • ChapterMarker (L2)      — 4-corner framing chrome, fades in B1
 *
 * Total = 2160 frames @ 60fps = 36.000s = 18 bars at 120 BPM.
 */

// ──────────────────────────── Palette (cool slate broadcast HUD) ────────────────────────────
// Rationale: stays in our DECISION-007 cyan-on-cool-slate register. The
// register-shift to true-void happens in B5Thesis (final card). Inside B0,
// beats shift but register is constant — the "register-braiding" Numerai
// pattern is adapted to "beat-braiding" within one register (PATTERN-083).

const BG = '#05080F';                    // cool slate-black, matches dashboard bg0
const INK_PRIMARY = '#F8FAFC';           // hero wordmark — bright (it IS the logo)
const INK_USER = '#7B8BA8';              // cool gray — user prompt voice
const INK_CLAUDE = '#00E5FF';            // analytics cyan — Claude voice + accent
const INK_KICKER = '#B8B8B8';            // Numerai whispered subtitle (PATTERN-082)
const INK_MUTED = '#5A6678';             // chrome whisper
const ACCENT_CYAN = '#00E5FF';

const FONT_MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';

// ──────────────────────────── Beat boundaries ────────────────────────────

const B1_END = 240;       // 4s — chrome fade-in complete
const B2_START = 240;
const USER_TYPE_START = 300;          // 5s — user starts typing
const USER_PLAIN_TEXT = 'hey claude, is the world';
const USER_ACCENT_WORD = 'malleable?';
// Plain types at 18 cps (slower for editorial weight): 25 chars / 18 × 60 = 83 frames
const USER_PLAIN_END = USER_TYPE_START + Math.ceil((USER_PLAIN_TEXT.length / 18) * 60); // ~383
const USER_ACCENT_START = USER_PLAIN_END + 6; // 100ms gap before italic reveal beat

const B3_START = 720;     // 12s — Claude responds
const CLAUDE_PRE_HANG = 60;           // 1s pre-response silence
const CLAUDE_TYPE_START = B3_START + CLAUDE_PRE_HANG;  // 780
const CLAUDE_PART_A = 'yes — ';                    // 6 chars cyan plain
const CLAUDE_ACCENT_WORD = 'build';                // italic accent beat
const CLAUDE_PART_C = ' what you need';            // 14 chars cyan plain
const CLAUDE_PART_A_END = CLAUDE_TYPE_START + Math.ceil((CLAUDE_PART_A.length / 18) * 60); // ~800
const CLAUDE_ACCENT_START = CLAUDE_PART_A_END + 6;                                          // ~806
const CLAUDE_ACCENT_END = CLAUDE_ACCENT_START + 30;                                         // ~836
const CLAUDE_PART_C_START = CLAUDE_ACCENT_END + 6;                                          // ~842
const CLAUDE_PART_C_END = CLAUDE_PART_C_START + Math.ceil((CLAUDE_PART_C.length / 18) * 60); // ~889

const B4_START = 1080;    // 18s — dialog dims, GitGraph emerges
const DIALOG_DIM_START = 1020;        // dim begins 60 frames before B4 to overlap
const DIALOG_DIM_END = 1110;          // ~1.5s dim arc
const GITGRAPH_START = B4_START;
const GITGRAPH_DURATION = 1080;       // 18s — generous so drift continues into B5/B6

const B5_START = 1620;    // 27s — ignition + wordmark materialize
const WORDMARK_KERN_START = B5_START + 30;   // 27.5s — kerning sweep begins
const WORDMARK_KERN_END = WORDMARK_KERN_START + 36;  // 0.6s sweep window
const WORDMARK_ITALIC_START = WORDMARK_KERN_START + 12;  // 200ms after upright (Pattern B)

const B6_START = 1920;    // 32s — kicker + built-with fade in
const KICKER_FADE_END = B6_START + 30;
const BUILTWITH_FADE_START = B6_START + 36;
const BUILTWITH_FADE_END = BUILTWITH_FADE_START + 30;
const EXIT_FADE_START = 2130;         // last 30 frames (0.5s) gentle exit
const EXIT_FADE_END = 2160;

// ──────────────────────────── Journey anchors ────────────────────────────

const JOURNEY_ANCHORS: ReadonlyArray<GitAnchor> = [
  { label: 'Czech Liga Explore', sublabel: '2023 · predictive modeling' },
  { label: 'Kalshi Quant', sublabel: '2024 · event markets' },
  { label: 'Alternative Data', sublabel: '2025 · sports CV' },
  { label: 'Table-Tennis Forge', sublabel: '2025 · pose + physics' },
  { label: 'PANOPTICON LIVE', sublabel: 'april 2026 · 64 commits · 6 days' },
];

// ──────────────────────────── B0OpenerV2 composition ────────────────────────────

export const B0OpenerV2 = () => {
  const frame = useCurrentFrame();

  // Whole-scene fade-in (very gentle, avoids hard fade-from-black per Anthropic
  // playbook section 5; tiny opacity window so the grid is "always there").
  const sceneOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Dialog fades fully out for B4 — first audit (f1500/1700/1980) showed that
  // even 18% opacity ghost is readable enough to compete with the GitGraph at
  // the same y-position. Anthropic's hard-cut discipline wins here: when the
  // hero slot swaps, the prior hero leaves the stage entirely.
  const dialogOpacity = interpolate(
    frame,
    [DIALOG_DIM_START, DIALOG_DIM_END],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Last-30-frame gentle exit
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
      {/* L1 BACKGROUND FIELD — cool slate solid (handled by AbsoluteFill bg) */}

      {/* L5 SECONDARY MOTION — ambient slow-drifting grid (continuous through all beats) */}
      <AmbientGrid driftDurationFrames={1080} spacing={80} opacity={0.045} />

      {/* L2 FRAMING CHROME — chapter marker corners (persistent, fades in B1) */}
      <ChapterMarker
        chapterId="ch.00"
        chapterTheme="ORIGIN"
        fadeInFrame={30}
        fadeInDuration={60}
        timecodeStartFrame={0}
      />

      {/* L3 HERO — Beat 2 + 3: dialog block (dims for B4 to become L4 context) */}
      <div style={{ opacity: dialogOpacity }}>
        {/* User prompt line — Beat 2 */}
        <div
          style={{
            position: 'absolute',
            top: '40%',
            left: 240,
            display: 'flex',
            alignItems: 'baseline',
            gap: 20,
          }}
        >
          <CursorChevron color={INK_MUTED} fontSize={40} />
          <TypingLine
            text={USER_PLAIN_TEXT}
            startFrame={USER_TYPE_START}
            charsPerSecond={18}
            color={INK_USER}
            fontSize={44}
            fontWeight={400}
            letterSpacing="0.01em"
            showCursor={frame < USER_ACCENT_START}
          />
          <ItalicAccentBeat
            text={USER_ACCENT_WORD}
            startFrame={USER_ACCENT_START}
            color={INK_USER}
            fontSize={44}
            fontWeight={500}
          />
        </div>

        {/* Claude response line — Beat 3 */}
        <Sequence from={CLAUDE_TYPE_START}>
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: 240,
              display: 'flex',
              alignItems: 'baseline',
              gap: 20,
            }}
          >
            <CursorChevron color={INK_CLAUDE} fontSize={40} />
            <TypingLine
              text={CLAUDE_PART_A}
              startFrame={0}
              charsPerSecond={18}
              color={INK_CLAUDE}
              fontSize={44}
              fontWeight={400}
              letterSpacing="0.01em"
              showCursor={false}
            />
            <ItalicAccentBeat
              text={CLAUDE_ACCENT_WORD}
              startFrame={CLAUDE_ACCENT_START - CLAUDE_TYPE_START}
              color={INK_CLAUDE}
              fontSize={44}
              fontWeight={600}
              withGlow
            />
            <TypingLine
              text={CLAUDE_PART_C}
              startFrame={CLAUDE_PART_C_START - CLAUDE_TYPE_START}
              charsPerSecond={18}
              color={INK_CLAUDE}
              fontSize={44}
              fontWeight={400}
              letterSpacing="0.01em"
              showCursor={true}
            />
          </div>
        </Sequence>
      </div>

      {/* L3 HERO — Beat 4: GitGraph timeline emerges, persists through B5/B6 */}
      <Sequence from={GITGRAPH_START} durationInFrames={GITGRAPH_DURATION}>
        <GitGraph
          anchors={JOURNEY_ANCHORS}
          startFrame={0}
          staggerFrames={96}
          driftDurationFrames={1080}
        />
      </Sequence>

      {/* L4 SUPPORTING CONTEXT — Beat 5: hero wordmark below timeline */}
      <Sequence from={B5_START}>
        <WordmarkHero />
      </Sequence>

      {/* L4 SUPPORTING CONTEXT — Beat 6: kicker + built-with fade in */}
      <Sequence from={B6_START}>
        <ChapterCardFooter />
      </Sequence>
    </AbsoluteFill>
  );
};

// ──────────────────────────── Helper: cursor chevron ────────────────────────────

const CursorChevron = ({ color, fontSize }: { color: string; fontSize: number }) => (
  <span
    style={{
      fontFamily: FONT_MONO,
      fontSize,
      color,
    }}
  >
    ›
  </span>
);

// ──────────────────────────── Helper: italic accent reveal beat (Pattern B) ────────────────────────────

interface ItalicAccentBeatProps {
  text: string;
  startFrame: number;
  color: string;
  fontSize: number;
  fontWeight: number | string;
  withGlow?: boolean;
}

const ItalicAccentBeat = ({
  text,
  startFrame,
  color,
  fontSize,
  fontWeight,
  withGlow = false,
}: ItalicAccentBeatProps) => {
  const frame = useCurrentFrame();
  const localFrame = Math.max(0, frame - startFrame);
  if (frame < startFrame) {
    return <span style={{ opacity: 0 }}>{text}</span>;
  }
  // Opacity: 0 → 1 over 18 frames (300ms — fast enough to feel like an arrival)
  const opacity = interpolate(localFrame, [0, 18], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Kerning sweep: 0.3em → -0.005em over 36 frames (Pattern A scaled down for word-level)
  const letterSpacingEm = interpolate(localFrame, [0, 36], [0.3, -0.005], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Optional brightness curve for cyan-glow words (PATTERN-082 ignition shape)
  const brightness = withGlow
    ? interpolate(localFrame, [0, 30], [0.7, 1.05], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : 1;
  const glowBlur = withGlow
    ? interpolate(localFrame, [0, 30], [0, 12], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
    : 0;
  return (
    <span
      style={{
        fontFamily: FONT_MONO,
        fontSize,
        fontWeight,
        fontStyle: 'italic',
        color,
        opacity,
        letterSpacing: `${letterSpacingEm}em`,
        filter: withGlow
          ? `brightness(${brightness}) drop-shadow(0 0 ${glowBlur}px rgba(0, 229, 255, 0.45))`
          : undefined,
        whiteSpace: 'pre',
      }}
    >
      {text}
    </span>
  );
};

// ──────────────────────────── Beat 5: hero wordmark with ignition + kerning sweep + italic reveal ────────────────────────────

const WordmarkHero = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Ignition curve — brightness + glow ramp over 30 frames (PATTERN-082)
  const ignitionFrame = Math.max(0, frame); // local to Sequence (B5_START anchored)
  const ignitionProgress = interpolate(ignitionFrame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const wordmarkBrightness = interpolate(ignitionProgress, [0, 1], [0.5, 1.0]);
  const wordmarkGlowBlur = interpolate(ignitionProgress, [0, 1], [0, 22]);

  // Kerning sweep on the upright "Panopticon" word (Pattern A)
  // Local frames in Sequence: WORDMARK_KERN_START - B5_START = 30, KERN_END = 66
  const kerningProgress = interpolate(ignitionFrame, [30, 66], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const wordmarkLetterSpacingEm = interpolate(kerningProgress, [0, 1], [0.5, -0.02]);

  // Italic "Live" reveal beat — fires 12 frames after upright kerning (Pattern B)
  const italicLocalFrame = Math.max(0, ignitionFrame - 42);
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

  // Whole-wordmark opacity fade-in (matches ignition timing)
  const wordmarkOpacity = ignitionProgress;

  // Subtle pulse on cyan word — 1 cycle over remaining 4s (240 frames after KERN_END)
  // Uses Math.sin for smooth breath; runs only after italic settles
  const pulseLocalFrame = Math.max(0, ignitionFrame - 90);
  const pulseAlpha = pulseLocalFrame > 0
    ? 0.45 + 0.20 * Math.sin((pulseLocalFrame / 120) * Math.PI * 2)
    : 0.45;

  return (
    <div
      style={{
        position: 'absolute',
        top: '64%',
        left: 0,
        right: 0,
        textAlign: 'center',
        opacity: wordmarkOpacity,
      }}
    >
      <div
        style={{
          fontFamily: FRAUNCES_FAMILY,
          fontSize: 132,
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

// ──────────────────────────── Beat 6: chapter card footer (kicker + built-with) ────────────────────────────

const ChapterCardFooter = () => {
  const frame = useCurrentFrame();
  // local to Sequence (B6_START anchored)

  const kickerOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Built-with delayed by 36 frames after kicker
  const builtWithOpacity = interpolate(frame, [36, 66], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        position: 'absolute',
        top: '78%',
        left: 0,
        right: 0,
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 13,
          letterSpacing: '0.24em',
          color: INK_KICKER,
          textTransform: 'uppercase',
          opacity: kickerOpacity,
          marginBottom: 26,
        }}
      >
        biomechanical fatigue telemetry · from 2d broadcast pixels
      </div>
      <div
        style={{
          fontFamily: FONT_MONO,
          fontSize: 11,
          letterSpacing: '0.32em',
          color: INK_MUTED,
          textTransform: 'uppercase',
          opacity: builtWithOpacity,
        }}
      >
        ch.00 — origin · built with claude opus 4.7 · april 2026
      </div>
    </div>
  );
};
