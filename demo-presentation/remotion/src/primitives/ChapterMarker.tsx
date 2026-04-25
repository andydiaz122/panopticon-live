import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

/**
 * ChapterMarker — persistent four-corner framing chrome.
 *
 * Layer L2 (framing chrome) per remotion-cinematic-craft anatomy. Lives in the
 * four corners of the 1920x1080 frame and persists across the whole composition,
 * giving the viewer spatial-temporal anchors that the hero slot (L3) can swap
 * against.
 *
 * Top-left: terminal-style breadcrumb     ("andrew@panopticon ~ · claude-code")
 * Top-right: chapter ID + theme           ("ch.00" / "ORIGIN")
 * Bottom-left: live timecode              ("00:00.00")
 * Bottom-right: tiny brand wordmark       ("PANOPTICON LIVE")
 *
 * All four corners are whispered (Numerai 70-75% gray rule, PATTERN-082) so
 * the hero element commands attention. The chapter ID gets a 1px cyan
 * underline (only saturated touch in the chrome layer), establishing chapter
 * identity per the Composition Checklist.
 *
 * Reusable across the V2 family (B0OpenerV2, B5ClosingV2, B5ThesisV2) for the
 * shared visual vocabulary the skill requires.
 *
 * Props:
 *   chapterId       — e.g., "ch.00"
 *   chapterTheme    — uppercase short label, e.g., "ORIGIN"
 *   fadeInFrame     — when the chrome materializes (default 0)
 *   fadeInDuration  — fade-in window in frames (default 30 = 0.5s)
 *   showTimecode    — whether to render the bottom-left timecode (default true)
 *   showBreadcrumb  — whether to render top-left terminal breadcrumb (default true)
 *   showBrandMark   — whether to render bottom-right brand wordmark (default true)
 *   timecodeStartFrame — frame when timecode "starts" (display-time = (frame-start) / fps)
 */
export interface ChapterMarkerProps {
  chapterId: string;
  chapterTheme: string;
  fadeInFrame?: number;
  fadeInDuration?: number;
  showTimecode?: boolean;
  showBreadcrumb?: boolean;
  showBrandMark?: boolean;
  timecodeStartFrame?: number;
}

const FONT_MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace';
const INK_WHISPERED = '#5A6678';   // cool muted — Numerai whispered chrome
const INK_FAINT = '#3A4658';       // even more recessive — bottom-right brand mark
const ACCENT_CYAN = '#00E5FF';     // single saturated touch — chapter underline
const CORNER_INSET = 60;           // px from each corner edge

const formatTimecode = (totalSeconds: number): string => {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = Math.floor(totalSeconds % 60);
  const centis = Math.floor((totalSeconds * 100) % 100);
  const mm = String(minutes).padStart(2, '0');
  const ss = String(seconds).padStart(2, '0');
  const cc = String(centis).padStart(2, '0');
  return `${mm}:${ss}.${cc}`;
};

export const ChapterMarker = ({
  chapterId,
  chapterTheme,
  fadeInFrame = 0,
  fadeInDuration = 30,
  showTimecode = true,
  showBreadcrumb = true,
  showBrandMark = true,
  timecodeStartFrame = 0,
}: ChapterMarkerProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(
    frame,
    [fadeInFrame, fadeInFrame + fadeInDuration],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  // Timecode = elapsed seconds since timecodeStartFrame
  const elapsedSeconds = Math.max(0, (frame - timecodeStartFrame) / fps);
  const timecodeText = formatTimecode(elapsedSeconds);

  return (
    <div style={{ position: 'absolute', inset: 0, opacity, pointerEvents: 'none' }}>
      {/* TOP-LEFT — terminal-style breadcrumb */}
      {showBreadcrumb && (
        <div
          style={{
            position: 'absolute',
            top: CORNER_INSET,
            left: CORNER_INSET,
            fontFamily: FONT_MONO,
            fontSize: 12,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: INK_WHISPERED,
          }}
        >
          andrew@panopticon ~ · claude-code
        </div>
      )}

      {/* TOP-RIGHT — chapter identity (id + theme) with single cyan underline */}
      <div
        style={{
          position: 'absolute',
          top: CORNER_INSET,
          right: CORNER_INSET,
          textAlign: 'right',
          fontFamily: FONT_MONO,
          color: INK_WHISPERED,
        }}
      >
        <div
          style={{
            fontSize: 12,
            letterSpacing: '0.22em',
            textTransform: 'lowercase',
          }}
        >
          {chapterId}
        </div>
        {/* 1px cyan underline — the only saturated chrome accent. ~28px wide,
            right-aligned to match the right-anchored typography. */}
        <div
          style={{
            width: 28,
            height: 1,
            backgroundColor: ACCENT_CYAN,
            marginLeft: 'auto',
            marginTop: 4,
            marginBottom: 6,
            opacity: 0.6,
          }}
        />
        <div
          style={{
            fontSize: 11,
            letterSpacing: '0.32em',
            textTransform: 'uppercase',
            color: INK_FAINT,
          }}
        >
          {chapterTheme}
        </div>
      </div>

      {/* BOTTOM-LEFT — live timecode (mono numerals) */}
      {showTimecode && (
        <div
          style={{
            position: 'absolute',
            bottom: CORNER_INSET,
            left: CORNER_INSET,
            fontFamily: FONT_MONO,
            fontSize: 12,
            letterSpacing: '0.18em',
            color: INK_WHISPERED,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {timecodeText}
        </div>
      )}

      {/* BOTTOM-RIGHT — tiny brand mark, even more whispered than top-left.
          The mark's role is "you've never lost the brand" without ever being
          loud enough to compete with the hero slot. */}
      {showBrandMark && (
        <div
          style={{
            position: 'absolute',
            bottom: CORNER_INSET,
            right: CORNER_INSET,
            fontFamily: FONT_MONO,
            fontSize: 11,
            letterSpacing: '0.32em',
            textTransform: 'uppercase',
            color: INK_FAINT,
          }}
        >
          panopticon · live
        </div>
      )}
    </div>
  );
};
