import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

/**
 * HelloWorld — toolchain-pre-warm composition.
 *
 * Minimum-viable Remotion composition to verify the render pipeline end-to-end.
 * 60 frames at 60 FPS = 1 second. Monochrome, JetBrains Mono, PANOPTICON palette
 * so the render artifact already matches our visual identity.
 *
 * Discarded after B0 opener prototype lands — this is scaffolding, not a
 * shippable composition.
 */
export const HelloWorld = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20, 40, 60], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#05080F',
        fontFamily: '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace',
        color: '#00E5FF',
        fontSize: 48,
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
      }}
    >
      <div style={{ opacity, fontSize: 14, color: '#7B8BA8', marginBottom: 24 }}>
        panopticon live · remotion pre-warm
      </div>
      <div style={{ opacity, fontSize: 72, fontWeight: 700 }}>hello</div>
      <div
        style={{
          opacity,
          fontSize: 12,
          color: '#5A6678',
          marginTop: 24,
          letterSpacing: '0.22em',
        }}
      >
        toolchain ready · 60 fps · 1920×1080
      </div>
    </AbsoluteFill>
  );
};
