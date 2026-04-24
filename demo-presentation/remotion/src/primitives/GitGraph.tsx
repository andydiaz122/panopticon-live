import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

/**
 * GitGraph — horizontal-timeline commit-graph primitive.
 *
 * Visual: a faint horizontal line left→right. Dots (commits or project anchors)
 * appear along it at staggered times with a spring pop-in. Labels fade in
 * under each dot. Designed to sit at the middle of the B0 opener (0:12 – 0:24)
 * showing the personal-journey arc from prior projects to PANOPTICON LIVE.
 *
 * Palantir-density, zero frills. Anchor labels are title-cased mono.
 *
 * Props:
 *   anchors         — ordered list of {label, sublabel} showing the journey.
 *                     The LAST anchor is treated as "the landing point" and
 *                     gets a larger dot + a distinct tone.
 *   startFrame      — when the timeline starts (line draws in)
 *   staggerFrames   — frames between each anchor's pop-in
 *   durationFrames  — total on-screen time
 *   width           — width of the horizontal line in px (default 1400)
 *   y               — vertical position of the line (px from top of 1080 canvas, default 540)
 */
export interface GitAnchor {
  label: string;
  sublabel?: string;
}

export interface GitGraphProps {
  anchors: ReadonlyArray<GitAnchor>;
  startFrame?: number;
  staggerFrames?: number;
  width?: number;
  y?: number;
}

// Restored cyan-on-blue palette (2026-04-24 evening) — matches dashboard's
// design-tokens.ts after warm-clay revert. v5 warm-clay variant didn't land
// for this product's broadcast/sports register; research findings preserved
// in demo-presentation/assets/references/ for any future palette experiment.
const LINE_COLOR = '#1F2B3F'; // cool border / inactive timeline
const LINE_LIVE_COLOR = '#00E5FF'; // analytics cyan — the live progress line
const DOT_COLOR = '#7B8BA8'; // cool gray — already-passed anchors
const DOT_LANDING_COLOR = '#00E5FF'; // cyan — the landing anchor (PANOPTICON LIVE)
const LABEL_COLOR = '#B8C4D6'; // cool light gray — anchor labels
const SUBLABEL_COLOR = '#5A6678'; // cool muted — dates / sublabels

export const GitGraph = ({
  anchors,
  startFrame = 0,
  staggerFrames = 36, // 0.6 s at 60 fps
  width = 1400,
  y = 540,
}: GitGraphProps) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = Math.max(0, frame - startFrame);

  // Line draws in over 30 frames
  const lineProgress = interpolate(localFrame, [0, 30], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Centered on 1920-wide canvas
  const canvasWidth = 1920;
  const leftEdge = (canvasWidth - width) / 2;

  // X coordinate for each anchor (evenly spaced)
  const anchorXs = anchors.map((_, i) =>
    anchors.length === 1 ? leftEdge + width / 2 : leftEdge + (i / (anchors.length - 1)) * width,
  );

  // When each anchor pops in (relative to startFrame)
  const anchorPopFrames = anchors.map((_, i) => 30 + i * staggerFrames);

  return (
    <svg
      width={canvasWidth}
      height={1080}
      style={{ position: 'absolute', top: 0, left: 0 }}
    >
      {/* Background line (full) */}
      <line
        x1={leftEdge}
        y1={y}
        x2={leftEdge + width * lineProgress}
        y2={y}
        stroke={LINE_COLOR}
        strokeWidth={2}
      />

      {/* "Live" line up to most-recent-visible anchor */}
      {(() => {
        const lastVisibleIdx = Math.max(
          -1,
          ...anchorPopFrames
            .map((popFrame, i) => (localFrame >= popFrame ? i : -1))
            .filter((i) => i >= 0),
        );
        if (lastVisibleIdx < 0) return null;
        const liveEnd = anchorXs[lastVisibleIdx];
        return (
          <line
            x1={leftEdge}
            y1={y}
            x2={liveEnd}
            y2={y}
            stroke={LINE_LIVE_COLOR}
            strokeWidth={2}
            opacity={0.6}
          />
        );
      })()}

      {/* Anchors — dots + labels */}
      {anchors.map((anchor, i) => {
        const popFrame = anchorPopFrames[i];
        const isLanding = i === anchors.length - 1;
        const popProgress = spring({
          frame: localFrame - popFrame,
          fps,
          config: { damping: 12, stiffness: 180 },
        });
        if (localFrame < popFrame) return null;
        const dotR = interpolate(popProgress, [0, 1], [0, isLanding ? 12 : 7], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const labelOpacity = interpolate(
          localFrame - popFrame,
          [0, 12],
          [0, 1],
          { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
        );
        const x = anchorXs[i];

        return (
          <g key={i}>
            {/* Pulse ring for the landing anchor */}
            {isLanding && (
              <circle
                cx={x}
                cy={y}
                r={interpolate(
                  (localFrame - popFrame) % 60,
                  [0, 60],
                  [12, 36],
                  { extrapolateRight: 'clamp' },
                )}
                fill="none"
                stroke={DOT_LANDING_COLOR}
                strokeWidth={2}
                opacity={interpolate(
                  (localFrame - popFrame) % 60,
                  [0, 60],
                  [0.5, 0],
                  { extrapolateRight: 'clamp' },
                )}
              />
            )}
            {/* The dot */}
            <circle
              cx={x}
              cy={y}
              r={dotR}
              fill={isLanding ? DOT_LANDING_COLOR : DOT_COLOR}
            />
            {/* Label text */}
            <text
              x={x}
              y={y + 42}
              textAnchor="middle"
              fill={isLanding ? DOT_LANDING_COLOR : LABEL_COLOR}
              opacity={labelOpacity}
              style={{
                fontFamily: '"JetBrains Mono", monospace',
                fontSize: isLanding ? 18 : 14,
                fontWeight: isLanding ? 700 : 500,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
              }}
            >
              {anchor.label}
            </text>
            {/* Sublabel (date / count) */}
            {anchor.sublabel && (
              <text
                x={x}
                y={y + 68}
                textAnchor="middle"
                fill={SUBLABEL_COLOR}
                opacity={labelOpacity}
                style={{
                  fontFamily: '"JetBrains Mono", monospace',
                  fontSize: 11,
                  letterSpacing: '0.12em',
                }}
              >
                {anchor.sublabel}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
};
