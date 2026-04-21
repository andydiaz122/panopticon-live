---
name: react-30fps-canvas-architecture
description: The ref + requestAnimationFrame + ResizeObserver + canvas pattern required for PANOPTICON LIVE's 30 FPS skeleton overlay. Use when building any dashboard/ component that consumes per-frame keypoint data. Prevents the React 30-FPS death spiral and keeps skeleton-video alignment on window resize.
---

# React 30-FPS Canvas Architecture

Per-frame keypoint data (30 FPS × ~20 keypoints × 2 players = 1200 updates/sec) CANNOT go through React state. This skill documents the enforced architecture for every high-frequency rendering component in `dashboard/`.

## The Cardinal Rule

**Per-frame data goes into `useRef`, not `useState`.**

React state triggers re-renders. 1200 re-renders/sec = browser tab crash. Refs mutate without re-rendering. Combined with `requestAnimationFrame` + direct canvas paint, we bypass React's render cycle entirely for high-frequency data.

## State Frequency Budget

| Data kind | Update rate | Storage |
|---|---|---|
| Keypoints | 30 Hz | `useRef` |
| Per-frame state flags | 30 Hz | `useRef` |
| Per-frame signals | 30 Hz | `useRef` |
| Match phase transitions | <1 Hz | `useState` |
| Opus commentary chunks | 1-3 Hz | `useState` |
| HUD layout changes | <0.1 Hz | `useState` |
| Anomaly events | <0.1 Hz | `useState` |

If an update happens more than once per second, it goes into a ref, not state.

## Canonical Pattern: `<SkeletonCanvas>`

```tsx
// dashboard/components/Broadcast/SkeletonCanvas.tsx
import { useEffect, useRef } from "react";

type KeypointFrame = {
  t_ms: number;
  players: Array<{
    player: "A" | "B";
    keypoints_xyn: Array<[number, number]>;  // normalized [0, 1]
    confidence: Array<number>;
  }>;
};

const COCO_SKELETON: Array<[number, number]> = [
  [5, 7], [7, 9], [6, 8], [8, 10],           // arms
  [11, 13], [13, 15], [12, 14], [14, 16],    // legs
  [5, 6], [11, 12], [5, 11], [6, 12],        // torso
];

export function SkeletonCanvas({
  videoRef,
  sseFrameSource,
}: {
  videoRef: React.RefObject<HTMLVideoElement>;
  sseFrameSource: () => KeypointFrame | null;  // pulls from ref
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const dimsRef = useRef({ w: 1920, h: 1080 });
  const rafRef = useRef<number | null>(null);

  // 1. ResizeObserver keeps dims fresh
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    const ro = new ResizeObserver(() => {
      const r = video.getBoundingClientRect();
      dimsRef.current = { w: r.width, h: r.height };
      canvas.width = r.width;   // set attribute (not CSS) for pixel-accurate resolution
      canvas.height = r.height;
    });
    ro.observe(video);
    return () => ro.disconnect();
  }, []);

  // 2. requestAnimationFrame loop paints directly
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const paint = () => {
      const frame = sseFrameSource();
      const { w, h } = dimsRef.current;
      ctx.clearRect(0, 0, w, h);

      if (frame) {
        for (const p of frame.players) {
          ctx.strokeStyle = p.player === "A" ? "#00E5FF" : "#FF3D71";
          ctx.lineWidth = 3;
          ctx.lineJoin = "round";

          for (const [a, b] of COCO_SKELETON) {
            const [ax, ay] = p.keypoints_xyn[a];
            const [bx, by] = p.keypoints_xyn[b];
            if (p.confidence[a] < 0.3 || p.confidence[b] < 0.3) continue;
            ctx.beginPath();
            ctx.moveTo(ax * w, ay * h);
            ctx.lineTo(bx * w, by * h);
            ctx.stroke();
          }

          // joint dots
          ctx.fillStyle = p.player === "A" ? "#00E5FF" : "#FF3D71";
          for (let i = 0; i < p.keypoints_xyn.length; i++) {
            if (p.confidence[i] < 0.3) continue;
            const [x, y] = p.keypoints_xyn[i];
            ctx.beginPath();
            ctx.arc(x * w, y * h, 4, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      }

      rafRef.current = requestAnimationFrame(paint);
    };

    rafRef.current = requestAnimationFrame(paint);
    return () => {
      if (rafRef.current != null) cancelAnimationFrame(rafRef.current);
    };
  }, [sseFrameSource]);

  return (
    <canvas
      ref={canvasRef}
      style={{ position: "absolute", inset: 0, pointerEvents: "none" }}
    />
  );
}
```

## SSE Handler Pattern (uses ref, not state)

```tsx
// dashboard/hooks/useKeypointStream.ts
import { useEffect, useRef } from "react";

export function useKeypointStream(url: string) {
  const latestFrameRef = useRef<KeypointFrame | null>(null);

  useEffect(() => {
    const es = new EventSource(url);
    es.addEventListener("frame", (evt) => {
      // CRITICAL: write to ref, not state
      latestFrameRef.current = JSON.parse(evt.data);
    });
    es.addEventListener("error", () => {
      // graceful reconnect handled by EventSource by default
    });
    return () => es.close();
  }, [url]);

  // Returns a getter that SkeletonCanvas can call per rAF tick
  return () => latestFrameRef.current;
}
```

## Video Element Wrapping

```tsx
<div style={{ position: "relative" }}>
  <video ref={videoRef} src={clipUrl} controls playsInline />
  <SkeletonCanvas videoRef={videoRef} sseFrameSource={getKeypoints} />
</div>
```

The parent `<div>` is `position: relative`; the `<canvas>` is `position: absolute; inset: 0`. The video stays interactive (controls work); the canvas is `pointerEvents: none` so clicks pass through.

## Signal Bars: Mixed High+Low Frequency

Signal values update at ~30 Hz (per-frame), but we don't need to re-render bars 30 times/sec. Throttle to ~10 Hz state updates via the existing ref pattern:

```tsx
// Read from ref every 100ms, throttle to state update
useEffect(() => {
  const iv = setInterval(() => {
    const latest = signalRef.current;
    if (latest) setDisplayedSignal(latest);  // setState at 10 Hz is fine
  }, 100);
  return () => clearInterval(iv);
}, []);
```

## Verification

Use React DevTools Profiler. Record 10 seconds of gameplay. Component render count for `<SkeletonCanvas>` should be ≤2 (mount + resize). If it's 300+, the pattern is violated.

## Motion Animations (safe because low-frequency)

`motion/framer-motion` is fine for:
- Typewriter effect on Opus commentary
- Signal bar pulse on anomaly event
- HUD widget slide-in on match-phase change
- Layout re-arrangement on HUD designer output

All of these are sub-1-Hz events; React state is appropriate.

## Do Not

- ❌ `setKeypoints(newFrame)` — triggers 30/sec re-renders
- ❌ Pass keypoints as props to child components — triggers prop-drilling re-renders
- ❌ Store per-frame signals in Context — context updates trigger all consumers
- ❌ Use CSS width/height to size the canvas — always set the attributes directly
- ❌ Assume `<video>` dimensions equal `video.videoWidth/Height` — use `getBoundingClientRect()` via ResizeObserver
