import { AbsoluteFill } from 'remotion';

import { GitGraph, type GitAnchor } from '../primitives/GitGraph';

/**
 * Standalone demo composition to validate the GitGraph primitive in isolation
 * before wiring it into B0. 12 s at 60 fps = 720 frames.
 */

// Placeholder journey — Andrew can edit anchor labels/sublabels to reflect the
// actual project progression. Last anchor = landing point (pulsed cyan).
const JOURNEY_ANCHORS: ReadonlyArray<GitAnchor> = [
  { label: 'Czech Liga Explore', sublabel: '2023 · predictive modeling' },
  { label: 'Kalshi Quant', sublabel: '2024 · event markets' },
  { label: 'Alternative Data', sublabel: '2025 · sports CV' },
  { label: 'Table-Tennis Forge', sublabel: '2025 · pose + physics' },
  { label: 'PANOPTICON LIVE', sublabel: 'april 2026 · 64 commits · 6 days' },
];

const BG = '#05080F';

export const GitGraphDemo = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      {/* Tiny header — contextualizes what we're looking at */}
      <div
        style={{
          position: 'absolute',
          top: 80,
          left: 180,
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: 12,
          letterSpacing: '0.22em',
          textTransform: 'uppercase',
          color: '#5A6678',
        }}
      >
        andrew@panopticon ~ · journey
      </div>
      <GitGraph anchors={JOURNEY_ANCHORS} startFrame={30} staggerFrames={48} />
    </AbsoluteFill>
  );
};
