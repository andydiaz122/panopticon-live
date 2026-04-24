import { loadFont as loadFraunces } from '@remotion/google-fonts/Fraunces';
import { AbsoluteFill, Sequence, useCurrentFrame, interpolate } from 'remotion';

import { GitGraph, type GitAnchor } from '../primitives/GitGraph';
import { TypingLine } from '../primitives/TypingLine';

// Load Fraunces serif (free Google Fonts substitute for Copernicus/Tiempos
// which Anthropic uses on the Opus 4.6 wordmark). Adopted per Andrew's
// directive 2026-04-24 evening: "use everything from Anthropic's video demo
// generation workflows" minus the palette. Cyan stays as the accent color
// (sports-broadcast domain convention), but typography upgrades to Anthropic's
// transitional serif for the hero wordmark — broadcast HUD register paired
// with editorial typography.
const { fontFamily: FRAUNCES_FAMILY } = loadFraunces();

/**
 * B0 — Personal-journey opener (PLAN.md §5.5).
 *
 * Target duration: 25 s = 1500 frames at 60 fps.
 * No voiceover (Path C directive).
 *
 * Beat structure:
 *   0:00 – 0:02   (frames 0-120)     black + cursor blink (silent tension)
 *   0:02 – 0:07   (frames 120-420)   user types question
 *   0:07 – 0:09   (frames 420-540)   pause — question hangs
 *   0:09 – 0:12   (frames 540-720)   claude responds
 *   0:12 – 0:23   (frames 720-1380)  dialog fades out, gitgraph timelapse
 *   0:23 – 0:25   (frames 1380-1500) title card + handoff to B1 cold-open
 *
 * Seamless cut to B1 (dashboard OBS capture on anomaly) at frame 1500 in the
 * DaVinci Sunday composite. The title card gives a visual landing point for
 * the handoff.
 */

// ──────────────────────────── Palette (v4 cyan-on-blue, restored 2026-04-24 evening) ────────────────────────────
//
// User-correction: tried v5 warm-clay-on-warm-slate (Anthropic-style) per the
// 3-agent research wave; visually didn't land for THIS product context (dark
// broadcast HUD register, not editorial paper register). Reverted at user
// direction. The cyan-on-cool-slate palette aligns with the dashboard's
// existing 2K-sports HUD identity — broadcast/sports context where saturated
// data-cyan reads as "live telemetry," not as sci-fi bloat. Research findings
// preserved in demo-presentation/assets/references/ for future reference.

const BG = '#05080F'; // cool slate-black, matches dashboard bg0
const USER_COLOR = '#7B8BA8'; // cool gray — user prompt reads as ambient
const CLAUDE_COLOR = '#00E5FF'; // analytics cyan — Claude's voice, matches dashboard playerA
const META_COLOR = '#5A6678'; // cool muted — terminal header, sublabels

// ──────────────────────────── Beat timings (60 fps) ────────────────────────────

const USER_TYPE_START_FRAME = 120;
const USER_TEXT = 'hey claude, is the world malleable?';

const CLAUDE_TYPE_START_FRAME = 540;
const CLAUDE_TEXT = 'yes — build what you need';

const DIALOG_FADE_OUT_START = 660; // 11.0 s
const DIALOG_FADE_OUT_END = 720; //   12.0 s

const GITGRAPH_START_FRAME = 720; // 12.0 s
const GITGRAPH_END_FRAME = 1380; //  23.0 s

const TITLE_START_FRAME = 1380; //   23.0 s
const TITLE_FULL_OPACITY_FRAME = 1440; // 24.0 s

// ──────────────────────────── Journey anchors ────────────────────────────
// Placeholder project progression. Andrew can edit labels/sublabels to reflect
// the actual trajectory. Last anchor = landing point (pulsed cyan).

const JOURNEY_ANCHORS: ReadonlyArray<GitAnchor> = [
  { label: 'Czech Liga Explore', sublabel: '2023 · predictive modeling' },
  { label: 'Kalshi Quant', sublabel: '2024 · event markets' },
  { label: 'Alternative Data', sublabel: '2025 · sports CV' },
  { label: 'Table-Tennis Forge', sublabel: '2025 · pose + physics' },
  { label: 'PANOPTICON LIVE', sublabel: 'april 2026 · 64 commits · 6 days' },
];

// ──────────────────────────── B0 composition ────────────────────────────

export const B0Opener = () => {
  const frame = useCurrentFrame();

  // Whole-scene fade-in (first 20 frames)
  const sceneOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Dialog fades out at 11-12s to transition into gitgraph
  const dialogOpacity = interpolate(
    frame,
    [DIALOG_FADE_OUT_START, DIALOG_FADE_OUT_END],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' },
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: BG,
        opacity: sceneOpacity,
      }}
    >
      {/* Header — always visible (reads like a terminal session header) */}
      <div
        style={{
          position: 'absolute',
          top: 80,
          left: 180,
          fontFamily: '"JetBrains Mono", monospace',
          fontSize: 12,
          letterSpacing: '0.22em',
          textTransform: 'uppercase',
          color: META_COLOR,
        }}
      >
        andrew@panopticon ~ · claude-code
      </div>

      {/* Dialog block (0-12 s) — fades out as gitgraph enters */}
      <div style={{ opacity: dialogOpacity }}>
        {/* User prompt line */}
        <div
          style={{
            display: 'flex',
            alignItems: 'baseline',
            gap: 20,
            position: 'absolute',
            top: '44%',
            left: 180,
          }}
        >
          <span
            style={{
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: 40,
              color: META_COLOR,
            }}
          >
            ›
          </span>
          <TypingLine
            text={USER_TEXT}
            startFrame={USER_TYPE_START_FRAME}
            charsPerSecond={12}
            color={USER_COLOR}
            fontSize={44}
            fontWeight={400}
            letterSpacing="0.01em"
            showCursor={frame < CLAUDE_TYPE_START_FRAME}
          />
        </div>

        {/* Claude response line */}
        <Sequence from={CLAUDE_TYPE_START_FRAME}>
          <div
            style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: 20,
              position: 'absolute',
              top: '52%',
              left: 180,
            }}
          >
            <span
              style={{
                fontFamily: '"JetBrains Mono", monospace',
                fontSize: 40,
                color: CLAUDE_COLOR,
              }}
            >
              ›
            </span>
            <TypingLine
              text={CLAUDE_TEXT}
              startFrame={0}
              charsPerSecond={25}
              color={CLAUDE_COLOR}
              fontSize={44}
              fontWeight={500}
              letterSpacing="0.01em"
              showCursor={true}
            />
          </div>
        </Sequence>
      </div>

      {/* GitGraph timelapse (12-23 s) */}
      <Sequence
        from={GITGRAPH_START_FRAME}
        durationInFrames={GITGRAPH_END_FRAME - GITGRAPH_START_FRAME}
      >
        <GitGraph anchors={JOURNEY_ANCHORS} startFrame={0} staggerFrames={96} />
      </Sequence>

      {/* Title card (23-25 s) — PANOPTICON LIVE handoff */}
      <Sequence from={TITLE_START_FRAME}>
        <TitleCard />
      </Sequence>
    </AbsoluteFill>
  );
};

// ──────────────────────────── Title card ────────────────────────────

const TitleCard = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill
      style={{
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: BG,
        opacity,
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontFamily: '"JetBrains Mono", monospace',
            fontSize: 12,
            letterSpacing: '0.28em',
            color: META_COLOR,
            textTransform: 'uppercase',
            marginBottom: 36,
          }}
        >
          biomechanical fatigue telemetry · from 2d broadcast pixels
        </div>
        {/* Fraunces serif hero wordmark — title-case, italic "Live" in cyan.
         *  Italic-for-emphasis is an Anthropic signature move ("Website
         *  analytics that *actually* make sense"). Cool ink + cyan accent
         *  keeps us in the broadcast HUD palette while adopting their
         *  editorial typography hierarchy. */}
        <div
          style={{
            fontFamily: FRAUNCES_FAMILY,
            fontSize: 132,
            fontWeight: 600,
            letterSpacing: '-0.02em',
            color: '#F8FAFC',
            whiteSpace: 'nowrap',
            lineHeight: 0.95,
            fontFeatureSettings: '"ss01" 1, "ss02" 1',
          }}
        >
          Panopticon <span style={{ color: CLAUDE_COLOR, fontStyle: 'italic' }}>Live</span>
        </div>
        <div
          style={{
            fontSize: 13,
            letterSpacing: '0.24em',
            color: META_COLOR,
            textTransform: 'uppercase',
            marginTop: 28,
          }}
        >
          built with claude opus 4.7 · april 2026
        </div>
      </div>
    </AbsoluteFill>
  );
};
