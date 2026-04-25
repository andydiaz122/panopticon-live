import { useCurrentFrame, interpolate } from 'remotion';

/**
 * AmbientGrid — slow-drifting faint geometric grid for L5 secondary motion.
 *
 * Per remotion-cinematic-craft skill ("The Cinematic Composition Anatomy"),
 * Layer L5 = subliminal "alive" cues that the conscious eye doesn't register
 * but the threshold-detection apparatus IS what reads as production value.
 * Numerai's cinematic plates use 2-3% slow camera drift for this effect.
 * Anthropic does not (deliberate stylistic refusal). Since our broadcast HUD
 * register is its OWN aesthetic, we adopt the Numerai move.
 *
 * Visual: a square grid of 1-px-wide lines at 80px spacing, opacity 0.04
 * (almost invisible against #05080F), slow-drifting both translate AND scale
 * across the composition's duration. The drift makes the grid breathe; the
 * faint opacity makes it disappear if you look directly at it.
 *
 * Props:
 *   driftDurationFrames — frames over which one full drift cycle completes (default 1080 = 18s @ 60fps)
 *   spacing             — px between grid lines (default 80)
 *   opacity             — alpha for the grid lines (default 0.045)
 *   color               — line color (default cool slate #1F2B3F, matches GitGraph LINE_COLOR)
 */
export interface AmbientGridProps {
  driftDurationFrames?: number;
  spacing?: number;
  opacity?: number;
  color?: string;
}

export const AmbientGrid = ({
  driftDurationFrames = 1080,
  spacing = 80,
  opacity = 0.045,
  color = '#1F2B3F',
}: AmbientGridProps) => {
  const frame = useCurrentFrame();

  // Slow X+Y translate — drift completes one spacing-unit shift across drift window.
  // Modulo wraps it back so the grid appears infinite.
  const driftProgress = interpolate(
    frame,
    [0, driftDurationFrames],
    [0, 1],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );
  const translateX = (driftProgress * spacing) % spacing;
  const translateY = (driftProgress * spacing * 0.6) % spacing; // slightly slower vertical for subtle parallax

  // Slow ~1.5% scale drift — independent rate from translate, so grid never
  // feels "tied" to a single transform. The eye sees motion-without-pattern.
  const scale = interpolate(frame, [0, driftDurationFrames], [1.0, 1.015], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Build grid via repeating linear-gradient — single CSS background, GPU-accelerated.
  const gridBg = `
    repeating-linear-gradient(
      0deg,
      transparent 0,
      transparent ${spacing - 1}px,
      ${color} ${spacing - 1}px,
      ${color} ${spacing}px
    ),
    repeating-linear-gradient(
      90deg,
      transparent 0,
      transparent ${spacing - 1}px,
      ${color} ${spacing - 1}px,
      ${color} ${spacing}px
    )
  `;

  return (
    <div
      style={{
        position: 'absolute',
        // Inset negatively so drift never reveals an edge.
        top: -spacing * 2,
        left: -spacing * 2,
        right: -spacing * 2,
        bottom: -spacing * 2,
        backgroundImage: gridBg,
        opacity,
        transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
        transformOrigin: '50% 50%',
        pointerEvents: 'none',
      }}
    />
  );
};
