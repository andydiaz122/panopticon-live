import { Composition } from 'remotion';

import { B0Opener } from './compositions/B0Opener';
import { GitGraphDemo } from './compositions/GitGraphDemo';
import { HelloWorld } from './HelloWorld';

/**
 * Root — registers every Remotion composition the demo uses.
 *
 * Every `<Composition>` MUST declare durationInFrames + fps + width + height.
 * fps = 60 per PLAN.md §2 hard constraint (master video spec matches OBS).
 * width/height = 1920×1080 per PLAN.md §2.
 *
 * Conventions:
 *   - id slugs use kebab-case (URL-safe for `remotion render <id>`)
 *   - durationInFrames = (target_seconds * 60)
 *   - Every composition's visual vocabulary matches 2K-Sports HUD palette
 *     (bg0=#05080F, playerA=#00E5FF, textMuted=#7B8BA8) so chrome + dashboard
 *     capture composite seamlessly in DaVinci.
 */
export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="hello-world"
        component={HelloWorld}
        durationInFrames={60}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="b0-opener"
        component={B0Opener}
        durationInFrames={1500}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="gitgraph-demo"
        component={GitGraphDemo}
        durationInFrames={720}
        fps={60}
        width={1920}
        height={1080}
      />
    </>
  );
};
