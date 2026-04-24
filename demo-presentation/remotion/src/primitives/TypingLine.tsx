import { useCurrentFrame, useVideoConfig } from 'remotion';

/**
 * TypingLine — character-by-character typing animation primitive.
 *
 * Designed for the B0 opener's "hey claude, is the world malleable?" reveal.
 * Character reveal is strictly frame-driven (no timers, no useState) so it's
 * scrub-safe in Remotion Studio and renders deterministically.
 *
 * Props:
 *   text          — the string to type out
 *   startFrame    — frame at which typing BEGINS (earlier frames: nothing shown)
 *   charsPerSecond — reveal rate (default 25 cps matches agent-trace-playback baud rate)
 *   showCursor    — whether to render a blinking `|` cursor (default true)
 *   color         — CSS color (default cyan, matches 2K-Sports playerA)
 *   fontSize      — px (default 48)
 *   fontWeight    — default 400 (monospace bodies want 400; bold reads too loud at 48 px)
 *
 * Behavior:
 *   - Before `startFrame`: nothing rendered (empty string, cursor hidden)
 *   - During reveal: N chars where N = floor((frame - startFrame) * charsPerSecond / fps)
 *   - After reveal completes: full string + blinking cursor (500 ms on / 500 ms off)
 */
export interface TypingLineProps {
  text: string;
  startFrame?: number;
  charsPerSecond?: number;
  showCursor?: boolean;
  color?: string;
  fontSize?: number;
  fontWeight?: number | string;
  letterSpacing?: string;
  fontFamily?: string;
}

export const TypingLine = ({
  text,
  startFrame = 0,
  charsPerSecond = 25,
  showCursor = true,
  color = '#D97757', // Anthropic Clay (default — overridden via tokens.ts)
  fontSize = 48,
  fontWeight = 400,
  letterSpacing = '0',
  fontFamily = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace',
}: TypingLineProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // How many characters should be visible at this frame?
  const elapsedFrames = Math.max(0, frame - startFrame);
  const charsToShow = Math.min(
    text.length,
    Math.floor((elapsedFrames / fps) * charsPerSecond),
  );
  const visibleText = text.slice(0, charsToShow);

  // Cursor visibility — 500ms on / 500ms off blink cycle (1-second period).
  // Also visible during typing (feels more alive).
  const cursorCycleFrame = frame % fps; // 0..fps-1 within each second
  const cursorOn = cursorCycleFrame < fps / 2;
  const isTyping = charsToShow < text.length;
  const showCursorNow = showCursor && (isTyping || cursorOn);

  return (
    <span
      style={{
        fontFamily,
        fontSize,
        fontWeight,
        letterSpacing,
        color,
        whiteSpace: 'pre',
      }}
    >
      {visibleText}
      <span
        style={{
          opacity: showCursorNow ? 1 : 0,
          // Cursor inherits color — matches text tone so it reads as the same token
          color,
          marginLeft: 1,
        }}
      >
        ▍
      </span>
    </span>
  );
};
