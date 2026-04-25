import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { AbsoluteFill, Sequence, useCurrentFrame, interpolate } from 'remotion';

import { ChapterMarker } from '../primitives/ChapterMarker';

const { fontFamily: FRAUNCES_FAMILY } = loadFraunces();

/**
 * B5ThesisV2 — Tier-1 world-class thesis card (final composition).
 *
 * Replaces B5Thesis (toy-tier — 4s, single-element fade). Per the
 * `remotion-cinematic-craft` skill's bookend-pair spec: pairs with
 * B5ClosingV2 via VISUAL REGISTER SWITCH (PATTERN-083) — B5ClosingV2 lives in
 * the broadcast-HUD register (cool slate + cyan accent + AmbientGrid),
 * B5ThesisV2 switches to the typographic-void register (true #000, NO ambient
 * grid, NO chrome other than the chapter marker) so the thesis lands as
 * thought rather than chrome.
 *
 * The chapter marker continues from B5ClosingV2 (ch.05 / VISION) but with most
 * chrome elements suppressed — only the chapter ID and theme remain. This is
 * the most stripped-down composition in the V2 family. The cyan accent line on
 * the chapter marker provides the only saturated touch, echoing the wordmark's
 * cyan italic from B5ClosingV2.
 *
 * Beat structure (60 fps, 8s = 480 frames @ 120 BPM = 4 bars):
 *   B1  0-90    (0:00-1.5s, 1.5s)  MARKER ARRIVAL  ChapterMarker fades in
 *                                                  (top-right only, void bg)
 *   B2  90-300  (1.5-5s, 3.5s)     THESIS REVEAL   Thesis line with kerning
 *                                                  sweep + slow scale-up drift
 *                                                  (PATTERN-084 cinematic
 *                                                  drift on a typographic plate)
 *   B3  300-420 (5-7s, 2s)          ACCENT RULE     1px cyan rule wipes left-to-
 *                                                  right under thesis (~280px,
 *                                                  same width as chapter
 *                                                  marker's cyan underline —
 *                                                  visual rhyme between chrome
 *                                                  and hero)
 *   B4  420-480 (7-8s, 1s)          HOLD + EXIT     Held, then last 30 frames
 *                                                  gentle fade-out for hard cut
 *                                                  to silent black in DaVinci
 *
 * The thesis (verbatim from Andrew's Notion notes 2026-04-25 per DECISION-019):
 *   "capture the signal nobody else is reading."
 */

const VOID_BG = '#000000';            // pure black, NOT B5ClosingV2's #05080F slate
const THESIS_INK = '#F8FAFC';         // near-white (no cyan — the thesis IS the
                                       // hero, no decoration)
const ACCENT_CYAN = '#00E5FF';

// ──────────────────────────── Beat boundaries ────────────────────────────

const B2_START = 90;            // thesis begins kerning sweep
const KERN_DURATION = 60;       // 1s sweep — slower than B0V2/B5ClosingV2 because
                                 // this composition's tempo is more deliberate
const B3_START = 300;           // accent rule begins wipe
const RULE_WIPE_DURATION = 60;  // 1s wipe
const EXIT_FADE_START = 450;
const EXIT_FADE_END = 480;

const THESIS_TEXT = 'capture the signal nobody else is reading.';

// ──────────────────────────── Composition ────────────────────────────

export const B5ThesisV2 = () => {
  const frame = useCurrentFrame();

  // Whole-scene fade-in (gentle, void register doesn't need a hard cut from
  // black — DaVinci's hard cut from B5ClosingV2 already provides the register
  // switch impact)
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
        backgroundColor: VOID_BG,
        opacity: sceneOpacity * exitOpacity,
        overflow: 'hidden',
      }}
    >
      {/* L1 BG (true black via AbsoluteFill) — NO AmbientGrid (register switch) */}

      {/* L2 chrome — minimal: chapter ID only, no breadcrumb, no timecode, no brand */}
      <ChapterMarker
        chapterId="ch.05"
        chapterTheme="VISION"
        fadeInFrame={0}
        fadeInDuration={60}
        showTimecode={false}
        showBreadcrumb={false}
        showBrandMark={false}
        timecodeStartFrame={0}
      />

      {/* L3 hero — thesis with kerning sweep + slow scale drift + accent rule below */}
      <Sequence from={B2_START}>
        <ThesisHero />
      </Sequence>
    </AbsoluteFill>
  );
};

// ──────────────────────────── Thesis hero ────────────────────────────

const ThesisHero = () => {
  const frame = useCurrentFrame();
  // local to B2_START Sequence

  // Kerning sweep — slower than B0V2/B5ClosingV2 (1s vs 0.6s) for editorial weight
  const kerningProgress = interpolate(frame, [0, KERN_DURATION], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const letterSpacingEm = interpolate(kerningProgress, [0, 1], [0.18, -0.005]);
  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Slow ~1.5% scale drift across the full thesis dwell — Numerai cinematic-
  // plate "alive" cue applied to a typographic plate (PATTERN-084 generalized).
  // Total drift over: 480 - B2_START = 390 frames. Settled drift target 1.015.
  const driftScale = interpolate(frame, [0, 390], [1.0, 1.015], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Accent rule wipe — fires at local frame B3_START - B2_START = 210
  const ruleLocalStart = B3_START - B2_START; // = 210
  const ruleLocalEnd = ruleLocalStart + RULE_WIPE_DURATION;
  const ruleProgress = interpolate(frame, [ruleLocalStart, ruleLocalEnd], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ruleWidth = ruleProgress * 280; // px

  return (
    <div
      style={{
        position: 'absolute',
        top: '40%',
        left: 0,
        right: 0,
        textAlign: 'center',
      }}
    >
      <div
        style={{
          fontFamily: FRAUNCES_FAMILY,
          fontSize: 64,
          fontWeight: 400,
          letterSpacing: `${letterSpacingEm}em`,
          color: THESIS_INK,
          lineHeight: 1.15,
          maxWidth: 1280,
          margin: '0 auto',
          padding: '0 80px',
          opacity,
          fontFeatureSettings: '"ss01" 1, "ss02" 1',
          transform: `scale(${driftScale})`,
          transformOrigin: 'center center',
        }}
      >
        {THESIS_TEXT}
      </div>

      {/* Accent rule — 1px cyan, wipes left-to-right under thesis. Width 280px
          matches the chapter-marker's cyan underline — visual rhyme between
          chrome and hero. Sits ~48px below thesis text. */}
      <div
        style={{
          width: ruleWidth,
          height: 1,
          backgroundColor: ACCENT_CYAN,
          marginLeft: 'auto',
          marginRight: 'auto',
          marginTop: 56,
          opacity: 0.7,
        }}
      />
    </div>
  );
};
