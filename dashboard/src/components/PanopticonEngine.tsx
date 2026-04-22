'use client';

import { useEffect, useRef, useState } from 'react';

import {
  COCO_SKELETON_EDGES,
  type FrameKeypoints,
  type MatchData,
  type PlayerDetection,
} from '@/lib/types';

/**
 * PanopticonEngine — the Zero-Render Sync Loop (PATTERN-040).
 *
 * Core contract:
 *   - High-frequency data (per-frame keypoints) NEVER goes into React state.
 *   - Match JSON is fetched ONCE on mount and stored in a useRef.
 *   - A native `requestAnimationFrame` loop reads `videoRef.current.currentTime`,
 *     indexes `matchDataRef.current.keypoints[frame_idx]`, and draws directly to
 *     the canvas via `ctx.moveTo` / `ctx.lineTo`. Zero React renders per frame.
 *   - The rAF loop is cancelled in `useEffect`'s cleanup to survive React
 *     StrictMode's double-mount in development.
 *   - `ResizeObserver` updates the canvas's `width`/`height` ATTRIBUTES (not CSS)
 *     whenever the video container resizes, so the drawing buffer stays in 1:1
 *     pixel alignment with the rendered video.
 *
 * Keypoints are pre-normalized to [0, 1] by Ultralytics `.xyn`, so drawing is a
 * simple `x = kp[0] * canvas.width`, `y = kp[1] * canvas.height`.
 */

export interface PanopticonEngineProps {
  /** Path to the MP4 under /public (e.g., `/clips/utr_match_01_segment_a.mp4`). */
  videoSrc: string;
  /** Path to the match_data JSON under /public. */
  matchDataSrc: string;
  /** Minimum per-joint confidence required to draw a keypoint (default 0.3). */
  minConfidence?: number;
}

const COLOR_PLAYER_A = '#00FFFF'; // neon cyan
const COLOR_PLAYER_B = '#FF00FF'; // magenta
const SKELETON_LINE_WIDTH = 3;
const JOINT_RADIUS = 4;

export default function PanopticonEngine({
  videoSrc,
  matchDataSrc,
  minConfidence = 0.3,
}: PanopticonEngineProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // The ONLY high-frequency data store. NEVER put into useState.
  const matchDataRef = useRef<MatchData | null>(null);

  // Low-frequency React state — fine for loading status + error banners.
  // Initialize to 'loading' directly (not 'idle' + setState-in-effect) to satisfy
  // React 19's `react-hooks/set-state-in-effect` rule.
  const [loadState, setLoadState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch match_data.json ONCE on mount.
  useEffect(() => {
    let cancelled = false;
    fetch(matchDataSrc)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status} fetching ${matchDataSrc}`);
        return res.json() as Promise<MatchData>;
      })
      .then((data) => {
        if (cancelled) return;
        matchDataRef.current = data;
        setLoadState('ready');
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setErrorMsg(err instanceof Error ? err.message : String(err));
        setLoadState('error');
      });
    return () => {
      cancelled = true;
    };
  }, [matchDataSrc]);

  // rAF loop + ResizeObserver. Set up ONCE, tear down on unmount (StrictMode-safe).
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!video || !canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Keep canvas's drawing-buffer size in sync with the rendered video container.
    const resizeCanvasToContainer = () => {
      const { clientWidth, clientHeight } = container;
      if (clientWidth > 0 && clientHeight > 0) {
        canvas.width = clientWidth;
        canvas.height = clientHeight;
      }
    };
    resizeCanvasToContainer();

    const ro = new ResizeObserver(resizeCanvasToContainer);
    ro.observe(container);

    // Draw loop: reads video.currentTime, indexes into matchDataRef, paints canvas.
    let rafId = 0;
    const tick = () => {
      rafId = requestAnimationFrame(tick);

      const data = matchDataRef.current;
      // Skip draw while video still buffering or data not loaded
      if (!data || video.readyState < 2) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        return;
      }

      const fps = data.meta.clip_fps;
      const frameIdx = Math.floor(video.currentTime * fps);

      // Direct-index into keypoints. Bounds-check in case the list is shorter
      // than expected (e.g., final frames dropped during precompute).
      const frame = data.keypoints[frameIdx];
      if (!frame) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        return;
      }

      drawFrame(ctx, canvas.width, canvas.height, frame, minConfidence);
    };
    rafId = requestAnimationFrame(tick);

    // StrictMode-safe cleanup — cancel the frame + disconnect the observer.
    return () => {
      cancelAnimationFrame(rafId);
      ro.disconnect();
    };
  }, [minConfidence]);

  return (
    <div
      ref={containerRef}
      style={{ position: 'relative', width: '100%', height: '100%' }}
    >
      <video
        ref={videoRef}
        src={videoSrc}
        controls
        playsInline
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
          objectFit: 'contain',
          background: '#000',
        }}
      />
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none', // don't swallow video click-to-play
        }}
      />
      {loadState === 'loading' && (
        <div style={overlayBannerStyle}>Loading match data…</div>
      )}
      {loadState === 'error' && (
        <div style={{ ...overlayBannerStyle, background: '#8B0000' }}>
          Error loading match data: {errorMsg}
        </div>
      )}
    </div>
  );
}

// ──────────────────────────── Drawing ────────────────────────────

function drawFrame(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  frame: FrameKeypoints,
  minConfidence: number,
): void {
  ctx.clearRect(0, 0, width, height);
  if (frame.player_a) {
    drawPlayerSkeleton(ctx, width, height, frame.player_a, COLOR_PLAYER_A, minConfidence);
  }
  if (frame.player_b) {
    drawPlayerSkeleton(ctx, width, height, frame.player_b, COLOR_PLAYER_B, minConfidence);
  }
}

function drawPlayerSkeleton(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  detection: PlayerDetection,
  color: string,
  minConfidence: number,
): void {
  const { keypoints_xyn: kps, confidence: conf } = detection;
  // Defensive — invalid data should be a no-op, not a throw, because rAF runs constantly.
  if (kps.length !== 17 || conf.length !== 17) return;

  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = SKELETON_LINE_WIDTH;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  // Edges first (under the joints for visual depth).
  for (const [fromIdx, toIdx] of COCO_SKELETON_EDGES) {
    if (conf[fromIdx] < minConfidence || conf[toIdx] < minConfidence) continue;
    const from = kps[fromIdx];
    const to = kps[toIdx];
    ctx.beginPath();
    ctx.moveTo(from[0] * width, from[1] * height);
    ctx.lineTo(to[0] * width, to[1] * height);
    ctx.stroke();
  }

  // Joint dots — visual anchor points + helpful when an edge is missing.
  for (let i = 0; i < 17; i += 1) {
    if (conf[i] < minConfidence) continue;
    const [x, y] = kps[i];
    ctx.beginPath();
    ctx.arc(x * width, y * height, JOINT_RADIUS, 0, Math.PI * 2);
    ctx.fill();
  }
}

// ──────────────────────────── Styles ────────────────────────────

const overlayBannerStyle: React.CSSProperties = {
  position: 'absolute',
  top: 12,
  left: 12,
  padding: '8px 12px',
  background: 'rgba(0, 0, 0, 0.75)',
  color: '#fff',
  fontFamily:
    "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, Monaco, monospace",
  fontSize: 13,
  borderRadius: 4,
  pointerEvents: 'none',
};
