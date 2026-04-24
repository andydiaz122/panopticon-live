'use client';

import { useEffect, useRef } from 'react';

import { usePanopticonStatic } from '@/lib/PanopticonProvider';
import { clampFrameIdx } from '@/lib/timeIndex';
import { COCO_SKELETON_EDGES, type PlayerDetection } from '@/lib/types';

/**
 * PanopticonEngine — the zero-render canvas owner.
 *
 * Contract:
 *  - Consumes ONLY `usePanopticonStatic()` (refs + getters). NEVER
 *    `usePanopticonState()`. The static context never changes after mount, so
 *    this component renders ≤3 times (mount + StrictMode double).
 *  - Owns the `<video>` + `<canvas>` DOM pair. Canvas is `position: absolute;
 *    inset: 0` over the video; pointer events pass through to video controls.
 *  - A native `requestAnimationFrame` loop reads `videoRef.current.currentTime`,
 *    indexes `matchDataRef.current.keypoints[frame_idx]` (bounds-clamped, per
 *    PATTERN-045), and paints directly to canvas via `ctx.moveTo`/`ctx.lineTo`.
 *    Zero React renders per frame.
 *  - `ResizeObserver` updates the canvas's `width`/`height` ATTRIBUTES on
 *    container resize so the drawing buffer stays in 1:1 pixel alignment.
 *  - Skips drawing when `bbox_conf < MIN_BBOX_CONF` (USER-CORRECTION-030).
 *
 * Single-player scope (DECISION-008 + GOTCHA-016): only Player A is drawn.
 * Player B is not detected reliably on broadcast clips; drawing the (absent)
 * magenta skeleton was removed.
 */

const COLOR_PLAYER_A = '#00E5FF'; // canonical analytics cyan — mirrors design-tokens.ts
const SKELETON_LINE_WIDTH = 3;
const JOINT_RADIUS = 4;
const MIN_JOINT_CONFIDENCE = 0.3;

// USER-CORRECTION-030: Skeleton sanitation. Bimodal bbox_conf distribution —
// real players score ≥0.5, ghosts (line judges, banners) score <0.05.
const MIN_BBOX_CONF = 0.5;

export default function PanopticonEngine() {
  const { videoRef, matchDataRef, videoSrc } = usePanopticonStatic();
  const containerRef = useRef<HTMLDivElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!video || !canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // PATTERN-067 — Canvas Resize Hardening ("judge's laptop bug"):
    // Observe the <video> element directly (canonical per
    // react-30fps-canvas-architecture skill), not the container. On viewport
    // breakpoint changes, fullscreen toggles, or DPR changes between monitors,
    // the video's bounding rect is the authoritative source for where the
    // skeleton must be drawn. Canvas BUFFER dimensions are set to
    // clientW*DPR × clientH*DPR so retina laptops render crisp strokes; the
    // ctx is `scale(DPR, DPR)`'d so per-frame `x * canvas.width` math stays
    // correct in CSS pixels (not buffer pixels).
    const resizeCanvasToVideo = () => {
      const rect = video.getBoundingClientRect();
      if (rect.width <= 0 || rect.height <= 0) return;
      const dpr = Math.max(1, window.devicePixelRatio || 1);
      canvas.width = Math.round(rect.width * dpr);
      canvas.height = Math.round(rect.height * dpr);
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resizeCanvasToVideo();

    // Observe BOTH the video (direct size signal) and container (breakpoint +
    // aspect-ratio changes). Same callback is idempotent.
    const ro = new ResizeObserver(resizeCanvasToVideo);
    ro.observe(video);
    ro.observe(container);
    // DPR can change when the user drags the window between a retina + non-
    // retina monitor mid-demo. `matchMedia` fires on DPR change; fall through
    // to a resize so the canvas buffer stays aligned.
    const dprMql = window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`);
    const onDprChange = () => resizeCanvasToVideo();
    dprMql.addEventListener('change', onDprChange);

    let rafId = 0;
    const tick = () => {
      rafId = requestAnimationFrame(tick);

      const data = matchDataRef.current;
      if (!data || video.readyState < 2) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        return;
      }

      const fps = data.meta.clip_fps;
      // PATTERN-045: bounds-clamp every frame index.
      const frameIdx = clampFrameIdx(
        video.currentTime,
        fps,
        data.keypoints.length,
      );
      const frame = data.keypoints[frameIdx];
      // PATTERN-067: with DPR scaling, the canvas BUFFER is clientW*DPR but
      // ctx is `setTransform(DPR, 0, 0, DPR, 0, 0)`'d. Paint math uses CSS
      // pixel space — pull from style dimensions, not buffer dimensions.
      const cssW = canvas.clientWidth;
      const cssH = canvas.clientHeight;
      if (!frame) {
        ctx.clearRect(0, 0, cssW, cssH);
        return;
      }

      ctx.clearRect(0, 0, cssW, cssH);
      // Single-player scope — Player A only (DECISION-008).
      if (frame.player_a && frame.player_a.bbox_conf >= MIN_BBOX_CONF) {
        drawPlayerSkeleton(
          ctx,
          cssW,
          cssH,
          frame.player_a,
          COLOR_PLAYER_A,
        );
      }
    };
    rafId = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(rafId);
      ro.disconnect();
      dprMql.removeEventListener('change', onDprChange);
    };
    // videoRef + matchDataRef are stable across renders from the provider.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div
      ref={containerRef}
      className="relative h-full w-full"
      style={{ aspectRatio: '16 / 9' }}
    >
      <video
        ref={videoRef}
        src={videoSrc}
        controls
        playsInline
        className="block h-full w-full bg-black object-contain"
      />
      <canvas
        ref={canvasRef}
        className="pointer-events-none absolute inset-0"
      />
    </div>
  );
}

function drawPlayerSkeleton(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  detection: PlayerDetection,
  color: string,
): void {
  const { keypoints_xyn: kps, confidence: conf } = detection;
  if (kps.length !== 17 || conf.length !== 17) return;

  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = SKELETON_LINE_WIDTH;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  for (const [fromIdx, toIdx] of COCO_SKELETON_EDGES) {
    if (conf[fromIdx] < MIN_JOINT_CONFIDENCE) continue;
    if (conf[toIdx] < MIN_JOINT_CONFIDENCE) continue;
    const from = kps[fromIdx];
    const to = kps[toIdx];
    ctx.beginPath();
    ctx.moveTo(from[0] * width, from[1] * height);
    ctx.lineTo(to[0] * width, to[1] * height);
    ctx.stroke();
  }

  for (let i = 0; i < 17; i += 1) {
    if (conf[i] < MIN_JOINT_CONFIDENCE) continue;
    const [x, y] = kps[i];
    ctx.beginPath();
    ctx.arc(x * width, y * height, JOINT_RADIUS, 0, Math.PI * 2);
    ctx.fill();
  }
}
