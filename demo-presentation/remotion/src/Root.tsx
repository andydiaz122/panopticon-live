import { Composition } from 'remotion';

import { B0Opener } from './compositions/B0Opener';
import { B0OpenerV2 } from './compositions/B0OpenerV2';
import { B5Closing } from './compositions/B5Closing';
import { B5ClosingV2 } from './compositions/B5ClosingV2';
import { B5Thesis } from './compositions/B5Thesis';
import { B5ThesisV2 } from './compositions/B5ThesisV2';
import { GitGraphDemo } from './compositions/GitGraphDemo';
import { SceneBreakB2, SceneBreakB3, SceneBreakB4 } from './compositions/SceneBreak';
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
        id="b0-opener-v2"
        component={B0OpenerV2}
        durationInFrames={2160}
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
      <Composition
        id="b5-closing"
        component={B5Closing}
        durationInFrames={300}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="b5-closing-v2"
        component={B5ClosingV2}
        durationInFrames={720}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="b5-thesis"
        component={B5Thesis}
        durationInFrames={240}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="b5-thesis-v2"
        component={B5ThesisV2}
        durationInFrames={480}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="scene-break-b2"
        component={SceneBreakB2}
        durationInFrames={90}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="scene-break-b3"
        component={SceneBreakB3}
        durationInFrames={90}
        fps={60}
        width={1920}
        height={1080}
      />
      <Composition
        id="scene-break-b4"
        component={SceneBreakB4}
        durationInFrames={90}
        fps={60}
        width={1920}
        height={1080}
      />
    </>
  );
};
