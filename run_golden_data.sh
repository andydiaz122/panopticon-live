#!/usr/bin/env bash
#
# run_golden_data.sh — PANOPTICON LIVE Golden Data generator.
#
# Runs the full 3-Pass DAG precompute pipeline on the canonical UTR clip,
# invokes the Multi-Agent Scouting Committee, and writes all demo-ready
# artifacts into `dashboard/public/match_data/` for Vercel's static server.
#
# This is the FOUNDER-RUN script — Claude Code does NOT invoke this.
# Execution needs the ANTHROPIC_API_KEY set in the caller's environment.
#
# Usage:
#   export ANTHROPIC_API_KEY=<your-anthropic-key>
#   ./run_golden_data.sh
#
# Optional env overrides:
#   PANOPTICON_CLIP       path to the source .mp4 (default: data/clips/utr_match_01_segment_a.mp4)
#   PANOPTICON_CORNERS    path to corners .json    (default: data/corners/utr_match_01_segment_a_corners.json)
#   PANOPTICON_MATCH_ID   match id                 (default: utr_01_segment_a)
#   PANOPTICON_PLAYER_A   near-court player name   (default: Player A)
#   PANOPTICON_PLAYER_B   far-court player name    (default: Player B)
#   PANOPTICON_VENV_PY    path to venv python      (default: sibling-repo venv)
#
# References:
#   PATTERN-055 — Strict 3-Pass DAG (Forward -> RTS -> Semantic)
#   PATTERN-056 — Multi-Agent Trace Playback
#   GOTCHA-029  — Vercel must NEVER touch the Python backend
#
set -euo pipefail
IFS=$'\n\t'

# ──────────────────────────── Config ────────────────────────────

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

CLIP_PATH="${PANOPTICON_CLIP:-data/clips/utr_match_01_segment_a.mp4}"
CORNERS_PATH="${PANOPTICON_CORNERS:-data/corners/utr_match_01_segment_a_corners.json}"
MATCH_ID="${PANOPTICON_MATCH_ID:-utr_01_segment_a}"
PLAYER_A="${PANOPTICON_PLAYER_A:-Player A}"
PLAYER_B="${PANOPTICON_PLAYER_B:-Player B}"

# Sibling-repo venv holds torch+ultralytics+filterpy+duckdb (~2 GB install).
# Avoids re-downloading YOLO + MPS torch wheels in the hackathon-research repo.
VENV_PY="${PANOPTICON_VENV_PY:-/Users/andrew/Documents/Coding/Built_with_Opus_4-7_Hackathon/.venv/bin/python}"

OUT_MATCH_JSON="dashboard/public/match_data/${MATCH_ID}.json"
OUT_TRACE_JSON="dashboard/public/match_data/agent_trace.json"
OUT_DUCKDB="data/panopticon.duckdb"
LOG_FILE="/tmp/panopticon_golden_$(date +%Y%m%d_%H%M%S).log"

# ──────────────────────────── Sanity checks (fail loudly) ────────────────────────────

err()  { printf "\033[31m[FATAL]\033[0m %s\n" "$*" >&2; exit 1; }
info() { printf "\033[36m[INFO]\033[0m  %s\n" "$*"; }
ok()   { printf "\033[32m[OK]\033[0m    %s\n" "$*"; }
warn() { printf "\033[33m[WARN]\033[0m  %s\n" "$*" >&2; }

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  err "ANTHROPIC_API_KEY is not set. Export it and re-run. The Multi-Agent Swarm will not execute without it."
fi

# Partial-key visibility so the operator can sanity-check they exported the right one
KEY_PREFIX="${ANTHROPIC_API_KEY:0:12}"
KEY_SUFFIX="${ANTHROPIC_API_KEY: -4}"
info "ANTHROPIC_API_KEY present (${KEY_PREFIX}...${KEY_SUFFIX})"

[[ -f "$CLIP_PATH" ]]     || err "Clip not found: $CLIP_PATH"
[[ -f "$CORNERS_PATH" ]]  || err "Corners JSON not found: $CORNERS_PATH"
[[ -x "$VENV_PY" ]]       || err "Python interpreter not executable: $VENV_PY"

# Verify the venv has our Python deps (fast fail — saves waiting through YOLO load)
"$VENV_PY" -c "import torch, ultralytics, filterpy, duckdb, anthropic" 2>/dev/null \
  || err "Sibling venv missing one of: torch / ultralytics / filterpy / duckdb / anthropic. Run pip install inside $VENV_PY's venv."

# YOLO weights — precompute.py expects them at checkpoints/yolo11m-pose.pt
[[ -f checkpoints/yolo11m-pose.pt ]] || err "YOLO weights missing: checkpoints/yolo11m-pose.pt (symlink or copy from sibling repo)"

# Ensure output directory exists
mkdir -p "$(dirname "$OUT_MATCH_JSON")"
mkdir -p "$(dirname "$OUT_DUCKDB")"

ok "All preflight checks passed"
info "Clip:         $CLIP_PATH"
info "Corners:      $CORNERS_PATH"
info "Match ID:     $MATCH_ID"
info "Player A:     $PLAYER_A"
info "Player B:     $PLAYER_B"
info "Out (match):  $OUT_MATCH_JSON"
info "Out (trace):  $OUT_TRACE_JSON"
info "Out (duckdb): $OUT_DUCKDB"
info "Log:          $LOG_FILE"

# ──────────────────────────── Golden Run ────────────────────────────
#
# Pipeline order (backend/precompute.py):
#   Pass 1 (Forward Sweep) : ffmpeg -> YOLO -> Kalman.update (forward only)
#   Pass 2 (Backward Sweep): Kalman.rts_smooth — zero-lag optimal trajectories
#   Pass 3 (Semantic Sweep): bounce -> state machine -> feature compiler (on smoothed kinematics)
#   Phase 2 agents         : Opus Coach / HUD Designer / Haiku Narrator
#   Phase 3 swarm          : Analytics -> Technical -> Tactical (-> agent_trace.json)
#
info "Starting 3-Pass DAG + Scouting Committee (expect ~2-4 min on M4 Pro MPS)"

# PYTHONPATH=$REPO_ROOT ensures we pick up THIS repo's backend (3-Pass DAG),
# not the sibling repo's older single-pass version (see anti-pattern #31).
PYTHONPATH="$REPO_ROOT" ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  "$VENV_PY" -m backend.precompute \
    --clip        "$CLIP_PATH" \
    --corners     "$CORNERS_PATH" \
    --match-id    "$MATCH_ID" \
    --player-a    "$PLAYER_A" \
    --player-b    "$PLAYER_B" \
    --db          "$OUT_DUCKDB" \
    --out-json    "$OUT_MATCH_JSON" \
    --agent-trace-json "$OUT_TRACE_JSON" \
    --device      mps \
  2>&1 | tee "$LOG_FILE"

# ──────────────────────────── Post-run sanity ────────────────────────────

[[ -s "$OUT_MATCH_JSON" ]] || err "match_data.json not generated (empty/missing)"
[[ -s "$OUT_TRACE_JSON" ]] || err "agent_trace.json not generated (empty/missing)"

MATCH_BYTES=$(stat -f%z "$OUT_MATCH_JSON" 2>/dev/null || stat -c%s "$OUT_MATCH_JSON")
TRACE_BYTES=$(stat -f%z "$OUT_TRACE_JSON" 2>/dev/null || stat -c%s "$OUT_TRACE_JSON")

ok "match_data.json: ${MATCH_BYTES} bytes"
ok "agent_trace.json: ${TRACE_BYTES} bytes"

# GOTCHA-027 size check: agent_trace.json should stay well under 1MB with
# truncation enforced. If it's >5MB, something is leaking big tool outputs.
if (( TRACE_BYTES > 5000000 )); then
  warn "agent_trace.json exceeds 5MB — trace-payload truncation may have regressed"
fi

# GOTCHA-026 size check: match_data.json can reach 15-25MB on a 60s clip.
# If it's >50MB, we may have accidentally unsampled keypoints.
if (( MATCH_BYTES > 50000000 )); then
  warn "match_data.json exceeds 50MB — verify float serialization + keypoint density"
fi

ok "Golden Data run complete. Dashboard artifacts live in dashboard/public/match_data/."
info "Next: cd dashboard && bun run dev   (or record the demo via OBS per docs/DEMO_STORYBOARD.md)"