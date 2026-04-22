---
name: vercel-ts-server-actions
description: Next.js Server Actions + TypeScript @anthropic-ai/sdk pattern for PANOPTICON LIVE's scouting-report button. Use when wiring any live Anthropic API call on Vercel. Canonical answer to USER-CORRECTION-006 — replaces all Python backend concerns.
---

# Vercel TypeScript Server Actions for Anthropic

Python is gone from Vercel. The entire runtime surface is Next.js 16 + TypeScript. Live Anthropic calls (scouting-report Managed Agent) go through Server Actions or Route Handlers using `@anthropic-ai/sdk` (TypeScript).

## Why This Architecture

- **Single language on Vercel** → no Python cold starts, no 250MB Serverless limit exposure
- **Server Actions** → typed end-to-end (Next.js client calls a typed function, server executes it, returns typed result)
- **AI Gateway compatible** → if we wrap with Vercel AI Gateway, we get observability + fallback routing for free
- **Managed Agents work natively** → the TS SDK has first-class support

## Canonical Setup

### 1. Install

```bash
cd dashboard
bun add @anthropic-ai/sdk
# or: bun add ai @ai-sdk/anthropic   # if we route through Vercel AI SDK v6
```

### 2. Env vars

`dashboard/.env.local` (and Vercel Production env):
```
ANTHROPIC_API_KEY=sk-ant-...
```

Never imported from a client component. Only Server Actions / Route Handlers access `process.env.ANTHROPIC_API_KEY`.

### 3. The Server Action

```tsx
// dashboard/app/actions/scouting-report.ts
"use server";

import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";

const ScoutingReportInputSchema = z.object({
  match_id: z.string().min(1),
  focus_player: z.enum(["A", "B"]),
});

export type ScoutingReportInput = z.infer<typeof ScoutingReportInputSchema>;

export type ScoutingReportResult =
  | { status: "pending"; run_id: string }
  | { status: "completed"; pdf_url: string; thinking: string | null }
  | { status: "failed"; error: string };

export async function startScoutingReport(
  raw: ScoutingReportInput,
): Promise<ScoutingReportResult> {
  const input = ScoutingReportInputSchema.parse(raw);

  const client = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY!,
  });

  // Use the Managed Agents beta (2026-04-01 header auto-added by client.beta.*)
  const agent = await client.beta.agents.create({
    name: "panopticon-scouting-report",
    model: { id: "claude-opus-4-7" },
    system: SCOUTING_SYSTEM_PROMPT,
    tools: [
      {
        type: "agent_toolset_20260401",
        default_config: { permission_policy: { type: "always_allow" } },
      },
    ],
  });

  const run = await client.beta.sessions.create({
    agent_id: agent.id,
    input: `Generate a scouting report for match ${input.match_id}, focused on player ${input.focus_player}.`,
  });

  return { status: "pending", run_id: run.id };
}

export async function getScoutingReportStatus(
  run_id: string,
): Promise<ScoutingReportResult> {
  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY! });
  const run = await client.beta.sessions.retrieve(run_id);

  if (run.status === "completed") {
    // Extract the PDF URL from the agent's output (generated via file_operations tool)
    // Parse `run.output` to find the created artifact
    return {
      status: "completed",
      pdf_url: "/api/scouting-report-artifact/" + run_id,
      thinking: extractThinking(run.output),
    };
  }
  if (run.status === "failed") {
    return { status: "failed", error: run.error ?? "unknown" };
  }
  return { status: "pending", run_id };
}
```

### 4. Client-side usage with `useActionState`

```tsx
// dashboard/components/ScoutingReport.tsx
"use client";

import { useState, useTransition } from "react";
import {
  startScoutingReport,
  getScoutingReportStatus,
  type ScoutingReportResult,
} from "@/app/actions/scouting-report";

export function ScoutingReportButton({
  matchId,
  focusPlayer,
}: {
  matchId: string;
  focusPlayer: "A" | "B";
}) {
  const [result, setResult] = useState<ScoutingReportResult | null>(null);
  const [isPending, startTransition] = useTransition();

  const handleClick = () => {
    startTransition(async () => {
      const first = await startScoutingReport({ match_id: matchId, focus_player: focusPlayer });
      setResult(first);

      if (first.status === "pending") {
        const poll = setInterval(async () => {
          const next = await getScoutingReportStatus(first.run_id);
          setResult(next);
          if (next.status !== "pending") clearInterval(poll);
        }, 2000);
      }
    });
  };

  return (
    <button onClick={handleClick} disabled={isPending}>
      {isPending ? "Generating..." : "Generate Scouting Report"}
    </button>
  );
}
```

### 5. Reading the pre-computed match JSON

For static data (keypoints, signals, pre-computed Opus insights, HUD layouts), NO server action is required. Client fetches directly:

```ts
// dashboard/hooks/useMatchData.ts
"use client";
import { useEffect, useState } from "react";

export function useMatchData(matchId: string) {
  const [data, setData] = useState<MatchData | null>(null);
  useEffect(() => {
    fetch(`/match_data/${matchId}.json`)
      .then((r) => r.json())
      .then(setData);
  }, [matchId]);
  return data;
}
```

`match_data.json` lives in `dashboard/public/match_data/<match_id>.json` and is produced by the Python `precompute.py` tool.

## Vercel Deployment Checklist

- `dashboard/` is the Vercel project root
- `vercel.ts` uses `framework: "nextjs"`, no Python runtime config
- `bun install` + `bun run build` for CI
- Env vars managed via `vercel env add ANTHROPIC_API_KEY production`
- No `requirements-prod.txt` needed (can be deleted)
- `@anthropic-ai/sdk` is the ONLY Anthropic integration layer on Vercel

## Anti-Patterns

- ❌ Call Anthropic from a client component. Secrets leak to the browser.
- ❌ Return the full agent output to the client in one action. Large payloads stress network; poll via status endpoint instead.
- ❌ Skip Zod validation on action inputs. Server Actions receive whatever the client sends; validate at the boundary.
- ❌ Long-poll a Server Action (>60s). Use short-poll (2-5s interval) with `run_id` continuation.
- ❌ Mix this with an older Python FastAPI path. The project has ONE deployment pattern: Next.js + Server Actions + static JSON.

## Related Skills

- `opus-47-creative-medium` — prompt design for the scouting-report agent
- `panopticon-hackathon-rules` — "No Python on Vercel" is now a hard rule
- `vercel:nextjs`, `vercel:ai-gateway`, `vercel:vercel-functions` (global skills) — platform-level details
