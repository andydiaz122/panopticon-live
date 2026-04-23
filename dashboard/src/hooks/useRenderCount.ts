'use client';

import { useEffect, useRef } from 'react';

/**
 * Dev-only diagnostic — logs render count for a named component.
 *
 * Used to regression-check the React 30-FPS death-spiral defense:
 *   - `PanopticonEngine` should render ≤3 times (mount + StrictMode double).
 *   - `SignalBar` instances should render at ≤10Hz (driven by provider state).
 *   - `CoachPanel` renders only on insight change (≤20 total per 60s clip).
 *
 * No-op in production. Safe to leave in shipped code.
 *
 * NOTE: increments live inside `useEffect` (NOT during render) to satisfy
 * React 19's strict `react-hooks/refs` lint rule.
 */
export function useRenderCount(name: string): void {
  const countRef = useRef(0);
  useEffect(() => {
    countRef.current += 1;
    if (process.env.NODE_ENV !== 'production') {
      console.debug(`[render-count] ${name}: ${countRef.current}`);
    }
  });
}
