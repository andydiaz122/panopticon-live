---
name: nextjs-hydration-traps
description: Next.js Server-Component hydration pitfalls for PANOPTICON LIVE. Covers the "15MB JSON prop kills the 60fps video" trap (GOTCHA-026) and the canonical fix (static /public asset + fetch in useEffect). Use when deciding how to load match_data.json, agent_trace.json, or any large pre-computed JSON in the Next.js dashboard.
---

# Next.js Hydration Traps

## The core trap (GOTCHA-026)

Any large JSON passed through a Next.js Server Component prop is SERIALIZED INTO THE INITIAL HTML DOCUMENT as `__NEXT_DATA__`. React hydration parses that blob on the MAIN THREAD before the UI becomes interactive. For Panopticon's match_data.json (15-25MB: 1800 frames × 30fps × 2 players × 17 keypoints × 7 signals × states) plus agent_trace.json, that parse blocks the UI for 500-2000ms — exactly when the 60fps demo video is trying to start playing.

The observable symptom: the video stutters violently for the first 1-2 seconds of the demo. That's the window in which judges form their first impression. We cannot afford this.

## The rule

**Treat `match_data.json` and `agent_trace.json` as STATIC CLIENT-SIDE ASSETS.** Place them in `dashboard/public/match_data/`. Load via `fetch()` inside `useEffect()`. Never `import` them at module top-level. Never pass them as props through a Server Component.

## Canonical loader pattern

```tsx
// dashboard/src/components/MatchDataLoader.tsx  (client component)
"use client";

import { useEffect, useState } from "react";
import type { MatchData } from "@/lib/schema";

export function useMatchData(matchId: string): {
  data: MatchData | null;
  error: Error | null;
} {
  const [data, setData] = useState<MatchData | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`/match_data/${matchId}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`match_data fetch ${r.status}`);
        return r.json();
      })
      .then((json: MatchData) => {
        if (!cancelled) setData(json);
      })
      .catch((e) => {
        if (!cancelled) setError(e);
      });
    return () => {
      cancelled = true;
    };
  }, [matchId]);

  return { data, error };
}
```

## Forbidden patterns

```tsx
// ❌ Hydration-death (Server Component passing 15MB prop)
export default async function Dashboard() {
  const match = await import("@/match_data/utr_01.json");  // BANNED
  return <HUD match={match} />;  // 15MB in __NEXT_DATA__
}

// ❌ Also bad (top-level JSON import in any component)
import matchData from "@/match_data/utr_01.json";  // BANNED — bundled into JS
```

```tsx
// ✅ Correct — static asset + client fetch
export default function DashboardPage() {
  return <HUDClient matchId="utr_01" />;  // HUDClient uses useMatchData inside
}
```

## Why `public/` and not `src/`

- `dashboard/public/*` is served directly by Next.js's static file server — Brotli-compressed, CDN-cacheable on Vercel, not parsed by React, not bundled into JS.
- `dashboard/src/*` imports are BUNDLED into the JS payload. A 15MB import blows your serverless function size past Vercel's 250MB limit AND runs through hydration.

## Progressive rendering tip

For match_data.json specifically: consider splitting into:
- `match_data/{match_id}.meta.json` — ~5KB (MatchMeta + signal-count summary) — fetched first for fast first paint
- `match_data/{match_id}.keypoints.json` — the 15MB bulk — fetched in parallel but not blocking

The meta-first split lets the HUD render identity chrome (PlayerNameplate, match title) in <100ms even when the keypoint blob is still streaming. Deferred rendering pattern matches `react-30fps-canvas-architecture`.

## Orthogonality

- **Owns**: asset-loading contract + file placement convention
- **Delegates to `react-30fps-canvas-architecture`**: everything about rendering the data once loaded (refs + rAF + canvas, zero React renders per video frame)
- **Delegates to `duckdb-pydantic-contracts`**: the TypeScript types used by the loader

## References
- `GOTCHA-026` in MEMORY.md (origin gotcha)
- `react-30fps-canvas-architecture` skill (the rendering pattern this loader feeds)
