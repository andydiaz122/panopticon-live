# Vercel Deployment Notes — PANOPTICON LIVE

**Status (2026-04-23):** A parallel branch is already live at
<https://panopticon-live-1fqx9c4iz-dmg-decisions.vercel.app/>. Do NOT deploy
from `hackathon-research` without coordinating with the founder — it will
conflict with the live deploy on the other branch.

## Architecture invariants (GOTCHA-029)

This repo is a Python + Next.js monorepo:

```
hackathon-research/
├── backend/             # Python 3.14, precompute pipeline (DO NOT DEPLOY TO VERCEL)
├── checkpoints/         # YOLO weights (local only; ~40MB)
├── data/                # clips + corners (local/ephemeral)
├── tests/               # pytest (Python)
├── dashboard/           # ← VERCEL BUILDS THIS, nothing else
│   ├── public/
│   │   ├── clips/       # .mp4 (static)
│   │   └── match_data/  # precomputed .json (static)
│   ├── src/             # Next.js App Router (TS)
│   └── package.json
├── vercel.json          # monorepo-aware build/ignore config
├── pyproject.toml       # ← Python; Vercel MUST NOT detect this
└── requirements-local.txt  # ← Python; Vercel MUST NOT install this
```

Vercel's default build detection scans the ROOT for language signals. If it
sees `pyproject.toml` or `requirements-local.txt` at root, it attempts to spin
up a Python runtime and `pip install torch ultralytics opencv-python duckdb` —
which exceeds the 250MB serverless bundle limit and hard-crashes the build.

## What our vercel.json does

- `framework: "nextjs"` — pins Vercel's framework detection so it doesn't
  re-sniff from root.
- `installCommand: "cd dashboard && bun install --frozen-lockfile"` — only
  ever installs Next.js deps; never touches `requirements-local.txt`.
- `buildCommand: "cd dashboard && bun run build"` — builds from inside
  `dashboard/` so the output tree has no Python references.
- `outputDirectory: "dashboard/.next"` — explicit, no ambiguity.
- `ignoreCommand` — exits 0 (skip build) if no changes touched `dashboard/` or
  the Pydantic schema source (`backend/db/schema.py` is the only Python file
  that has a direct contract with the frontend types; changes there warrant a
  re-deploy). Exits 1 (build) when either changes.

## What the dashboard expects to serve

- `/clips/*.mp4` — the source video (long-cache, immutable)
- `/match_data/<match_id>.json` — per-match biomechanical telemetry
- `/match_data/agent_trace.json` — captured Scouting Committee execution
- Everything else is Next.js Router output

## Deploying from `main` (future, not this branch)

1. Set Vercel project's **Root Directory** = `dashboard/` in the dashboard UI
   (preferred) OR leave blank and rely on this `vercel.json`.
2. Ensure **Environment Variables** are set (the agent phases need
   `ANTHROPIC_API_KEY`; but note the KEY IS ONLY USED OFFLINE DURING PRECOMPUTE,
   NOT AT RUNTIME — so setting it in Vercel is optional unless we ever add a
   live route).
3. Push; Vercel's webhook will trigger a build.

## What we do NOT deploy

- Any Python code. Full stop.
- YOLO weights (`checkpoints/*.pt`).
- DuckDB files (`data/*.duckdb`).
- The source clip file (except the pre-demo-selected one in
  `dashboard/public/clips/`).

## Regenerating match_data for a deploy

```bash
# From repo root
export ANTHROPIC_API_KEY=...
PYTHONPATH=. python -m backend.precompute \
  --clip data/clips/utr_match_01_segment_a.mp4 \
  --corners data/corners/utr_match_01_segment_a_corners.json \
  --match-id utr_01_segment_a \
  --player-a "Player A" --player-b "Player B" \
  --db data/panopticon.duckdb \
  --out-json dashboard/public/match_data/utr_01_segment_a.json \
  --agent-trace-json dashboard/public/match_data/agent_trace.json
```

Both output JSONs land in `dashboard/public/match_data/` and are picked up by
Vercel's static asset serving automatically.

## Do-not-deploy checklist for `hackathon-research` sessions

When iterating on this branch:

- [ ] Do NOT run `vercel deploy` / `vercel --prod` / `vercel link`
- [ ] Do NOT push to `main` — the other branch is live there
- [ ] Keep the rebuilt `match_data/*.json` out of git unless the founder asks
  for a commit (they're large + re-generable)
- [ ] If you must test locally: `cd dashboard && bun run dev` (no Vercel
  involvement)
