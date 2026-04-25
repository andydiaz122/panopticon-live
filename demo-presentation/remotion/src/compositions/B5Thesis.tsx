import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

/**
 * B5b — Closing thesis card (PLAN.md §5.6 / DECISION-019).
 *
 * Sequenced AFTER B5Closing in the DaVinci composite:
 *   B5a (B5Closing.tsx)  — brand wordmark + URL + attribution on cool slate (#05080F)
 *   HARD CUT (DaVinci)
 *   B5b (this composition) — pure void + thesis line on #000
 *
 * Why a SECOND closing card and not a single one (PATTERN-083):
 *   The structural magic of Numerai's two-card closing is the VISUAL REGISTER
 *   SWITCH between cards. B5a lives in the broadcast-HUD register (cool slate
 *   + cyan accent + Fraunces+Mono pairing). B5b lives in pure typographic
 *   void register (#000 + Fraunces only, no cyan). The register switch is
 *   what makes the thesis LAND as a thesis rather than additional brand
 *   chrome. Without the switch, it's just a longer brand card.
 *
 * Per DECISION-019 the demo's closing thesis is (verbatim from Andrew's
 * Notion notes 2026-04-25): "capture the signal nobody else is reading."
 *
 * Motion vocabulary (Numerai DNA, PATTERN-082):
 *   - hard cut entry from B5a brand card (DaVinci edits the cut)
 *   - thesis fades in 0-0.5s (250-350ms is Numerai's title-card fade range;
 *     we use 500ms so the line settles deliberately rather than appears)
 *   - holds for ~3s
 *   - hard cut to black at composition end (DaVinci appends silent black)
 *
 * Total duration: 4 seconds = 240 frames at 60 fps.
 */

const { fontFamily: FRAUNCES_FAMILY } = loadFraunces();

const VOID_BG = '#000000';        // pure black, NOT B5a's #05080F slate-black
const THESIS_INK = '#F8FAFC';     // near-white, no cyan accent (restraint = thesis as stated, not styled)

export const B5Thesis = () => {
  const frame = useCurrentFrame();

  // Thesis fades in 0-0.5s (frames 0-30) — Numerai title-card range
  const thesisOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Hold from 0.5s to 3.5s (frames 30-210)
  // Exit fade 3.5-4.0s (frames 210-240) — gentle so DaVinci's hard cut to
  // black feels intentional rather than abrupt
  const exitOpacity = interpolate(frame, [210, 240], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: VOID_BG,
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      <div
        style={{
          fontFamily: FRAUNCES_FAMILY,
          fontSize: 64,
          fontWeight: 400,
          letterSpacing: '-0.01em',
          color: THESIS_INK,
          lineHeight: 1.15,
          textAlign: 'center',
          maxWidth: 1280,
          padding: '0 80px',
          opacity: thesisOpacity * exitOpacity,
          fontFeatureSettings: '"ss01" 1, "ss02" 1',
        }}
      >
        capture the signal nobody else is reading.
      </div>
    </AbsoluteFill>
  );
};
