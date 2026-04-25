#!/usr/bin/env python3
"""
sync_match_data_to_ground_truth.py
==================================

Surgically rewrite ``dashboard/public/match_data/utr_01_segment_a.json`` to
align ALL display-layer authored fields to Andrew's second-by-second ground-
truth log delivered 2026-04-25 06:15 EDT.

What this script DOES (mutates):
  - display_transitions      — rebuilt as 6 phase boundaries in 5-state vocab
  - display_narrations       — rebuilt as 8 short broadcast-voice overlays
  - coach_insights           — rebuilt as 7 biomechanically-defensible insights
                               including 2 new showcase moments (bounce-count
                               at t=13.5s + leg-flexion at t=18.5s)
  - narrator_beats           — rebuilt as 10 Opus-voice streaming beats
  - hud_layouts              — rebuilt as 6 phase-aligned widget layouts
  - display_player_profile   — pre_serve_ritual_style upgraded with the
                               now-observable bounce sequence

What this script DOES NOT touch (CV pipeline output, must not change):
  - meta, keypoints, signals, anomalies, transitions

Constraints encoded:
  - Only the 5 RallyMicroPhase values in active use:
      UNKNOWN, PRE_SERVE_RITUAL, SERVE, ACTIVE_RALLY, DEAD_TIME
    Forensic granular detail (walking, bouncing-while-walking, off-camera,
    etc.) lives in the TEXT of narrations + coach_insights, never in the
    state enum (per team-lead architectural guardrail).
  - WidgetKind limited to {PlayerNameplate, SignalBar, TossTracer} —
    MomentumMeter / PredictiveOverlay / FootworkHeatmap excluded
    (single-player scope per DECISION-008; FootworkHeatmap not needed here).
  - SignalName drawn from the canonical 7 (recovery_latency_ms,
    serve_toss_variance_cm, ritual_entropy_delta, crouch_depth_degradation_deg,
    baseline_retreat_distance_m, lateral_work_rate, split_step_latency_ms).
  - WidgetSlot drawn from the canonical 9.
  - reason on AuthoredStateTransition is the literal "hand_authored" per
    types.ts; semantic explanation goes in authoring_note.
  - source on AuthoredStateTransition + QualitativeNarration is the literal
    "hand_authored" per NarrationSource enum.
  - narration_kind = "broadcast" (could also be "coach_strategy"; we use
    broadcast for the on-screen text overlays).
  - coach_insights for hand-authored content set tool_calls=[],
    input_tokens=0, output_tokens=0 (honest about provenance).

Idempotency:
  - Backs up the original to .bak.pre-ground-truth-sync ONLY if the backup
    doesn't already exist (so re-running the script preserves the true original).
  - Each entry's ID is deterministic from its timestamp + descriptive slug,
    so re-running the script produces byte-identical output.

Usage:
  cd /Users/andrew/Documents/Coding/hackathon-research
  python3 scripts/sync_match_data_to_ground_truth.py

Verification after run:
  - Script asserts the JSON re-parses cleanly.
  - Script prints before/after counts per array.
  - Caller should then run `cd dashboard && bun run build` to verify
    TypeScript still compiles (no schema breakage downstream).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# ============ Paths ============

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = REPO_ROOT / "dashboard" / "public" / "match_data" / "utr_01_segment_a.json"
# Backup intentionally lives OUTSIDE dashboard/public/ — anything in public/
# gets deployed to Vercel as a static asset. Keeping the backup under data/
# avoids shipping the pre-sync JSON to production. (data-integrity-guard
# 2026-04-25 LOW finding L3.)
BACKUP_DIR = REPO_ROOT / "data" / "match_data_backups"
BACKUP_FILE = BACKUP_DIR / "utr_01_segment_a.json.bak.pre-ground-truth-sync"
MATCH_ID = "utr_01_segment_a"
SYNC_NOTE_TAG = "2026-04-25 ground-truth sync"

# ============ Authored Content: display_transitions ============
# Each tuple: (timestamp_ms, from_state, to_state, authoring_note)
# `reason` is always "hand_authored" per AuthoredStateTransition schema.
# `visible_action_ref` derived as frames/t_<seconds>.jpg (preserves field shape).

NEW_DISPLAY_TRANSITIONS: list[tuple[int, str, str, str]] = [
    (
        0,
        "UNKNOWN",
        "DEAD_TIME",
        "Initial state. Per ground-truth log: 0-9s, Player A is off-court — "
        "the previous point closed just before clip start. Mapped to DEAD_TIME "
        "in the 5-state RallyMicroPhase vocabulary.",
    ),
    (
        13_000,
        "DEAD_TIME",
        "PRE_SERVE_RITUAL",
        "Player A reaches the baseline; FORMAL pre-serve routine begins. "
        "Per ground-truth log: 11-12s = informal bouncing while walking-to-"
        "baseline (still classified DEAD_TIME — informal motion, no telemetry "
        "anchor); 13s = arrived at baseline + first formal bounce. The formal "
        "ritual is the consistent telemetry anchor.",
    ),
    (
        17_000,
        "PRE_SERVE_RITUAL",
        "SERVE",
        "Final ball-catch + weight transfer to front leg; serving motion fires. "
        "Per ground-truth log: 17s = 'official start of the serving motion' "
        "(Andrew's wording). Catch + rock + load is the SERVE phase.",
    ),
    (
        20_000,
        "SERVE",
        "ACTIVE_RALLY",
        "Contact with serve. Ball in play. Serve placed wide to Player B's "
        "backhand. Per ground-truth log: 20s = serve contact, rally begins.",
    ),
    (
        35_000,
        "ACTIVE_RALLY",
        "DEAD_TIME",
        "Point closes on a leave. Per ground-truth log: 35s = Player B's slice "
        "down-the-line lands OUT; Player A steps ~1.5m INSIDE the baseline to "
        "read it and lets it go (per Andrew's 2026-04-25 ~17:30 EDT correction "
        "— prior wording 'behind the baseline' was incorrect). Court-awareness "
        "telemetry, not fatigue. Recovery clock starts here.",
    ),
    (
        58_000,
        "DEAD_TIME",
        "PRE_SERVE_RITUAL",
        "Next pre-serve ritual begins. Per ground-truth log: 36-54s = off-court "
        "for towel/regroup; 55-57s = returning to baseline; 58-59s = bouncing "
        "ball at baseline (formal routine just engaging at clip cut). Mapped "
        "to PRE_SERVE_RITUAL transition at 58s.",
    ),
]

# ============ Authored Content: display_narrations ============
# Each tuple: (range_start_ms, range_end_ms, narration_text, narration_id_slug, authoring_note)
# narration_kind = "broadcast" for all; source = "hand_authored".

NEW_DISPLAY_NARRATIONS: list[tuple[int, int, str, str, str]] = [
    # Per multi-agent review (demo-director HIGH H1): display_narrations and
    # narrator_beats were 90-100% redundant in content. Resolution: narrations
    # collapsed to PHASE LABELS (3-7 words). Beats carry the observational
    # prose. Two channels, distinct registers.
    (
        0,
        9_000,
        "Between points · recovery clock active",
        "n_0000_dead_time_offcourt",
        "Phase label only. Narrator_beat at t=0 carries the prose.",
    ),
    (
        9_000,
        13_000,
        "Returning to baseline",
        "n_0009_walking_in",
        "Phase label. Narrator_beat at t=10s carries the prose.",
    ),
    (
        13_000,
        17_000,
        "Pre-serve ritual · formal phase",
        "n_0013_formal_pre_serve",
        "Phase label. Narrator_beat at t=13s carries the bounce-sequence prose.",
    ),
    (
        17_000,
        20_000,
        "Serving motion · toss → contact",
        "n_0017_serve_mechanics",
        "Phase label. Narrator_beats at t=17s and t=19.5s carry the prose.",
    ),
    (
        20_000,
        35_000,
        "Rally engaged · baseline exchange",
        "n_0020_rally_engaged",
        "Phase label. Narrator_beats at t=22s and t=28s carry the rally prose.",
    ),
    (
        35_000,
        38_000,
        "Point ends · ball lands out",
        "n_0035_point_closes_on_leave",
        "Phase label. Narrator_beat at t=35.5s carries the leave-vs-fatigue prose.",
    ),
    (
        38_000,
        55_000,
        "Recovery walk · off-camera",
        "n_0038_recovery_walk",
        "Phase label. Narrator_beat at t=45s carries the towel/breath prose (the "
        "demo-director review flagged that beat as the strongest line in the corpus).",
    ),
    (
        55_000,
        60_000,
        "Returning · next pre-serve",
        "n_0055_returning_for_next_serve",
        "Phase label. Narrator_beat at t=58.5s carries the loop-closure prose.",
    ),
]

# ============ Authored Content: coach_insights ============
# Each tuple: (timestamp_ms, slug, commentary)
# All hand-authored: thinking=null, tool_calls=[], all token counts = 0.

NEW_COACH_INSIGHTS: list[tuple[int, str, str]] = [
    # Per multi-agent review:
    #   - biomech CRITICAL C1: removed fabricated "~0.6m behind baseline" claim
    #     (actual signal value at t=21933 is 0.041m — 14x error). Replaced with
    #     prose that doesn't make spurious telemetry claims.
    #   - biomech HIGH H1: fixed "17s" → "20s" (35→55s = 20, not 17). Math now
    #     internally consistent.
    #   - biomech MEDIUM M1: softened "most repeatable / most consistent"
    #     superlative (unfalsifiable on n=1) → "high-repeatability anchor".
    #   - biomech MEDIUM M2: dropped "pace-management exchange" causation
    #     claim from a 2-shot slice sample.
    #   - demo-director HIGH H2: "five baseline biometric signals" → "seven
    #     biomechanical fatigue signals" (matches the pitch's 7-signal moat).
    #   - demo-director HIGH H3: "~5ft" → "~1.5m" (unit consistency).
    #   - demo-director MEDIUM: trimmed entries to ≤55 words each (down from
    #     56-100); removed methodology disclaimers from [1] and [2].
    (
        500,
        "match_observation_begins",
        "Match observation begins. Player A off-camera between points; the "
        "previous rally exited just before clip start. The seven biomechanical "
        "fatigue signals start populating their rolling baselines now — "
        "no z-scores yet, raw values only.",
    ),
    (
        13_500,
        "pre_serve_bounce_showcase",
        "Pre-serve routine engaged at the baseline. Bounce sequence: bounce-1, "
        "mid-routine catch (left-hand reset), bounce-2, bounce-3, then final "
        "catch + ball-against-racket. Bounce counts are part of his ritual "
        "entropy signature; deviations correlate with pre-serve cognitive load.",
    ),
    (
        18_500,
        "leg_flexion_at_toss_showcase",
        "Toss release. Back-leg knee at peak flexion — a high-repeatability "
        "kinematic anchor across his serves. Once 3-5 first serves are "
        "sampled, knee-angle z-score becomes a viable serve-mechanic fatigue "
        "indicator. First sample logged.",
    ),
    (
        22_500,
        "inside_in_forehand_observation",
        "First attacking shot of the rally — an inside-in forehand. A "
        "high-percentage ball that turns the exchange from defensive to "
        "neutral. Worth flagging for the Strategy agent in the scouting "
        "committee (Tab 3).",
    ),
    (
        31_000,
        "slice_exchange_observation",
        "Slice exchange across the baseline. Lateral coverage rises "
        "monotonically through the rally arc (0.10 → 0.70 m/s). Within his "
        "early-match envelope; no degradation tells. Notable: both players "
        "defaulting to slice rather than topspin — atypical for the modern "
        "pro-tour baseline game.",
    ),
    (
        36_000,
        "point_closes_on_leave",
        "Point closes on a leave, not a winner. Player A steps ~1.5m INSIDE "
        "the baseline to read Player B's down-the-line slice and lets the "
        "ball clear the line. Court-awareness telemetry, not fatigue "
        "telemetry — leave-ratio and recovery-latency stay separated downstream.",
    ),
    (
        55_000,
        "recovery_interval_observation",
        "Off-court recovery interval ≈ 20 seconds (point ended at 35s, "
        "returned to baseline at 55s). First recovery-latency datapoint of "
        "the match. Sits at the long end of the typical 15-25s between-point "
        "baseline; ~10 intervals needed before z-scoring becomes meaningful.",
    ),
]

# ============ Authored Content: narrator_beats ============
# Each tuple: (timestamp_ms, slug, text). All hand-authored, tokens=0.

NEW_NARRATOR_BEATS: list[tuple[int, str, str]] = [
    (
        0,
        "beat_0_camera_holds_empty_baseline",
        "Camera holds on the empty baseline. Player A off-frame; the "
        "recovery clock from the prior point is the first telemetry "
        "datapoint of the match.",
    ),
    (
        10_000,
        "beat_10_player_enters_frame",
        "Player A enters from the right edge, racket low at his hip. "
        "Walking deliberately — the approach itself is part of the cadence.",
    ),
    (
        13_000,
        "beat_13_settles_to_baseline",
        "Settles to the baseline. The ritual begins: bounce, catch, bounce, "
        "bounce — three bounces of consistency, the cognitive anchor before "
        "mechanics fire.",
    ),
    (
        17_000,
        "beat_17_final_catch_load",
        "Final catch. Weight transfer to the rear leg; the load begins.",
    ),
    (
        19_500,
        "beat_19_5_toss_release_peak_knee",
        "Toss release. Back-leg knee at peak flexion — the most repeatable "
        "biometric across his serves.",
    ),
    (
        22_000,
        "beat_22_inside_in_forehand",
        "Inside-in forehand. First attacking shot of the rally — a "
        "high-percentage ball that turns the exchange.",
    ),
    (
        28_000,
        "beat_28_slice_exchange",
        "Slice exchange — both players grinding angles, no winner attempted "
        "yet. Court coverage rising; lateral recoveries still unhurried.",
    ),
    (
        35_500,
        "beat_35_5_point_closes_on_leave",
        "Ball clears the baseline. He reads it cleanly and lets it go. "
        "Court awareness, not fatigue — important to keep those signals "
        "separated downstream.",
    ),
    (
        45_000,
        "beat_45_off_court_recovery",
        "Off-court recovery. The towel walk, the breath, the silence. "
        "Recovery latency is being measured even when nothing visible is "
        "happening on screen.",
    ),
    (
        58_500,
        "beat_58_5_pre_serve_restart",
        "Pre-serve restart. The pattern returns — bounce, bounce — and the "
        "next point will begin against the same ritual entropy baseline.",
    ),
]

# ============ Authored Content: hud_layouts ============
# Each tuple: (timestamp_ms, valid_until_ms, slug, reason, widgets[])
# Each widget: (widget, slot, props_dict)
# z_score=0.0 set on every SignalBar (no baseline yet — honest).

def _signal_bar(slot: str, signal: str, label: str) -> tuple[str, str, dict[str, Any]]:
    return ("SignalBar", slot, {"player": "A", "signal": signal, "z_score": 0.0, "label": label})

def _player_nameplate() -> tuple[str, str, dict[str, Any]]:
    return ("PlayerNameplate", "top-left", {"player": "A", "highlight": True})

def _toss_tracer() -> tuple[str, str, dict[str, Any]]:
    return ("TossTracer", "center-overlay", {"player": "A"})

NEW_HUD_LAYOUTS: list[tuple[int, int, str, str, list[tuple[str, str, dict[str, Any]]]]] = [
    (
        0,
        13_000,
        "hud_0_dead_time_initial",
        "Player A off-court between points. Foreground recovery clock and "
        "rally-summary biometrics; rally-era widgets dimmed since no live "
        "rally is in progress.",
        [
            _player_nameplate(),
            _signal_bar("right-1", "recovery_latency_ms", "Recovery Latency"),
            _signal_bar("right-2", "lateral_work_rate", "Lateral Work Rate"),
            _signal_bar("right-3", "baseline_retreat_distance_m", "Baseline Retreat"),
        ],
    ),
    (
        13_000,
        17_000,
        "hud_13_pre_serve_ritual_formal",
        "Formal pre-serve routine engaged at the baseline. Foreground toss "
        "tracer and ritual entropy; serve-mechanic widgets queued behind.",
        [
            _player_nameplate(),
            _toss_tracer(),
            _signal_bar("right-1", "ritual_entropy_delta", "Ritual Entropy"),
            _signal_bar("right-2", "serve_toss_variance_cm", "Toss Variance"),
            _signal_bar("right-3", "crouch_depth_degradation_deg", "Crouch Depth"),
        ],
    ),
    (
        17_000,
        20_000,
        "hud_17_serve_mechanics_fire",
        "Serving motion: weight transfer, toss, peak knee flexion. "
        "Foreground crouch depth and toss variance — the serve-mechanic "
        "biometrics. Toss tracer remains visible for the toss arc.",
        [
            _player_nameplate(),
            _toss_tracer(),
            _signal_bar("right-1", "crouch_depth_degradation_deg", "Crouch Depth"),
            _signal_bar("right-2", "serve_toss_variance_cm", "Toss Variance"),
            _signal_bar("right-3", "ritual_entropy_delta", "Ritual Entropy"),
        ],
    ),
    (
        20_000,
        35_000,
        "hud_20_rally_engaged",
        "Rally engaged: slice-heavy exchange across the baseline. "
        "Foreground lateral telemetry and baseline retreat — the rally "
        "biometrics. Toss tracer dismissed (mechanics complete).",
        [
            _player_nameplate(),
            _signal_bar("right-1", "lateral_work_rate", "Lateral Work Rate"),
            _signal_bar("right-2", "baseline_retreat_distance_m", "Baseline Retreat"),
            _signal_bar("right-3", "split_step_latency_ms", "Split Step Latency"),
        ],
    ),
    (
        35_000,
        58_000,
        "hud_35_recovery_clock_active",
        "Point closed on a leave. Recovery clock starts; foreground recovery "
        "latency and the lateral peak summary from the rally just ended.",
        [
            _player_nameplate(),
            _signal_bar("right-1", "recovery_latency_ms", "Recovery Latency"),
            _signal_bar("right-2", "lateral_work_rate", "Rally Peak: Lateral"),
            _signal_bar("right-3", "baseline_retreat_distance_m", "Baseline Retreat"),
        ],
    ),
    (
        58_000,
        60_000,
        "hud_58_pre_serve_restart",
        "Pre-serve restart: bounces resume at the baseline. Foreground "
        "ritual entropy and toss tracer for the upcoming serve.",
        [
            _player_nameplate(),
            _toss_tracer(),
            _signal_bar("right-1", "ritual_entropy_delta", "Ritual Entropy"),
            _signal_bar("right-2", "serve_toss_variance_cm", "Toss Variance"),
            _signal_bar("right-3", "recovery_latency_ms", "Recovery Latency"),
        ],
    ),
]

# ============ Authored Content: display_player_profile UPGRADE ============
# Andrew's ground-truth NOW provides the previously-unobservable bounce count.
# Upgrade pre_serve_ritual_style; preserve all other fields.

NEW_PRE_SERVE_RITUAL_STYLE = {
    "value": (
        "Right-handed; settle at baseline with racket held at hip before load. "
        "Formal pre-serve sequence over 0:13–0:17: bounce-1, mid-routine catch "
        "(left hand), bounce-2, bounce-3, then final catch + ball-against-"
        "racket setup. Approach phase (0:11–0:12) includes informal bouncing "
        "while walking to the baseline. Total formal-ritual duration ≈ 4 "
        "seconds. Serving motion fires from the final catch (0:17) through "
        "contact (0:20), peaking at back-leg knee flexion at toss release "
        "(0:19)."
    ),
    "data_as_of": "2026-04-25",
    "verification_status": (
        "qualitative — observed across the full 0-60s clip via Andrew's "
        "second-by-second ground-truth log (2026-04-25 06:15 EDT). Bounce "
        "count and timing visually verified frame-by-frame."
    ),
}

# ============ Builder Helpers ============

def build_display_transition(ts: int, from_s: str, to_s: str, note: str) -> dict[str, Any]:
    return {
        "timestamp_ms": ts,
        "player": "A",
        "from_state": from_s,
        "to_state": to_s,
        "reason": "hand_authored",
        "source": "hand_authored",
        "authoring_note": note,
        "visible_action_ref": f"frames/t_{ts // 1000:04d}.jpg",
    }

def build_display_narration(
    range_start: int,
    range_end: int,
    text: str,
    slug: str,
    note: str,
) -> dict[str, Any]:
    return {
        "narration_id": slug,
        "timestamp_ms": range_start,
        "match_time_range_ms": [range_start, range_end],
        "narration_text": text,
        "source": "hand_authored",
        "narration_kind": "broadcast",
        "visible_action_ref": f"frames/t_{range_start // 1000:04d}.jpg",
        "authoring_note": note,
    }

def build_coach_insight(ts: int, slug: str, commentary: str) -> dict[str, Any]:
    return {
        "insight_id": f"coach_{ts:06d}_{slug}",
        "timestamp_ms": ts,
        "match_id": MATCH_ID,
        "thinking": None,
        "commentary": commentary,
        "tool_calls": [],
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_creation_tokens": 0,
    }

def build_narrator_beat(ts: int, slug: str, text: str) -> dict[str, Any]:
    return {
        "beat_id": slug,
        "timestamp_ms": ts,
        "match_id": MATCH_ID,
        "text": text,
        "input_tokens": 0,
        "output_tokens": 0,
    }

def build_hud_layout(
    ts: int,
    valid_until: int,
    slug: str,
    reason: str,
    widget_specs: list[tuple[str, str, dict[str, Any]]],
) -> dict[str, Any]:
    widgets = [
        {"widget": w_kind, "slot": w_slot, "props": w_props}
        for (w_kind, w_slot, w_props) in widget_specs
    ]
    return {
        "layout_id": slug,
        "timestamp_ms": ts,
        "reason": reason,
        "widgets": widgets,
        "valid_until_ms": valid_until,
    }

# ============ Validation Helpers ============

VALID_RALLY_MICRO_PHASES = {
    "UNKNOWN", "WARMUP", "PRE_SERVE_RITUAL", "SERVE", "ACTIVE_RALLY",
    "DEAD_TIME", "CHANGEOVER",
}
VALID_WIDGETS = {
    "PlayerNameplate", "SignalBar", "MomentumMeter", "PredictiveOverlay",
    "TossTracer", "FootworkHeatmap",
}
VALID_SLOTS = {
    "top-left", "top-right", "top-center",
    "right-1", "right-2", "right-3", "right-4",
    "center-overlay", "bottom",
}
VALID_SIGNALS = {
    "recovery_latency_ms", "serve_toss_variance_cm", "ritual_entropy_delta",
    "crouch_depth_degradation_deg", "baseline_retreat_distance_m",
    "lateral_work_rate", "split_step_latency_ms",
}

def validate_authored_data() -> None:
    """Sanity-check the in-script content tables BEFORE writing to disk.

    Uses ``raise ValueError`` (not ``assert``) so validation survives the
    ``python3 -O`` optimization flag, per python-reviewer 2026-04-25 HIGH H2.
    Also checks ID uniqueness within each array per python-reviewer M2.
    """
    def _check(cond: bool, msg: str) -> None:
        if not cond:
            raise ValueError(msg)

    # Per-entry validation
    for ts, from_s, to_s, _note in NEW_DISPLAY_TRANSITIONS:
        _check(from_s in VALID_RALLY_MICRO_PHASES, f"Invalid from_state: {from_s}")
        _check(to_s in VALID_RALLY_MICRO_PHASES, f"Invalid to_state: {to_s}")
        _check(0 <= ts <= 60_000, f"Timestamp {ts} outside clip duration")

    for rs, re_ms, _text, slug, _note in NEW_DISPLAY_NARRATIONS:
        _check(0 <= rs <= re_ms <= 60_000, f"Bad range [{rs}, {re_ms}] for {slug}")

    for ts, slug, _commentary in NEW_COACH_INSIGHTS:
        _check(0 <= ts <= 60_000, f"Bad insight timestamp {ts} for {slug}")

    for ts, slug, _text in NEW_NARRATOR_BEATS:
        _check(0 <= ts <= 60_000, f"Bad beat timestamp {ts} for {slug}")

    for ts, valid_until, slug, _reason, widget_specs in NEW_HUD_LAYOUTS:
        _check(0 <= ts < valid_until <= 60_000,
               f"Bad layout window [{ts}, {valid_until}] for {slug}")
        for w_kind, w_slot, w_props in widget_specs:
            _check(w_kind in VALID_WIDGETS, f"Invalid widget {w_kind} in {slug}")
            _check(w_slot in VALID_SLOTS, f"Invalid slot {w_slot} in {slug}")
            if w_kind == "SignalBar":
                signal = w_props.get("signal")
                _check(signal in VALID_SIGNALS,
                       f"Invalid signal {signal} in {slug}/{w_slot}")

    # ID uniqueness across each array (python-reviewer MEDIUM M2)
    narration_slugs = [slug for _rs, _re, _t, slug, _n in NEW_DISPLAY_NARRATIONS]
    insight_slugs = [slug for _ts, slug, _c in NEW_COACH_INSIGHTS]
    beat_slugs = [slug for _ts, slug, _t in NEW_NARRATOR_BEATS]
    hud_slugs = [slug for _ts, _vu, slug, _r, _w in NEW_HUD_LAYOUTS]
    for label, slugs in (("narrations", narration_slugs), ("insights", insight_slugs),
                         ("beats", beat_slugs), ("hud_layouts", hud_slugs)):
        seen: set[str] = set()
        for s in slugs:
            if s in seen:
                raise ValueError(f"Duplicate {label} slug: {s}")
            seen.add(s)

    print("✓ Validated all authored content tables (incl. ID uniqueness)")

# ============ Main ============

def main() -> int:
    if not INPUT_FILE.exists():
        print(f"✗ INPUT_FILE not found: {INPUT_FILE}", file=sys.stderr)
        return 1

    # 0. Validate in-script tables BEFORE touching disk
    validate_authored_data()

    # 1. Backup if not already backed up (idempotent). Backup lives OUTSIDE
    #    dashboard/public/ to avoid Vercel deploying it as a static asset.
    if not BACKUP_FILE.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        BACKUP_FILE.write_bytes(INPUT_FILE.read_bytes())
        print(f"✓ Backup created: {BACKUP_FILE}")
    else:
        print(f"⊙ Backup already exists (preserved): {BACKUP_FILE}")

    # 2. Load
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    original_size = INPUT_FILE.stat().st_size
    print(f"✓ Loaded {INPUT_FILE.name} — {original_size:,} bytes, "
          f"{len(data.get('keypoints', []))} keypoint frames, "
          f"{len(data.get('signals', []))} signal samples")

    # 3. Capture before counts (for the diff print)
    before = {
        "display_transitions": len(data.get("display_transitions", [])),
        "display_narrations": len(data.get("display_narrations", [])),
        "coach_insights": len(data.get("coach_insights", [])),
        "narrator_beats": len(data.get("narrator_beats", [])),
        "hud_layouts": len(data.get("hud_layouts", [])),
    }

    # 4. Mutate display + coach + narrator + hud arrays
    data["display_transitions"] = [
        build_display_transition(ts, from_s, to_s, note)
        for (ts, from_s, to_s, note) in NEW_DISPLAY_TRANSITIONS
    ]
    data["display_narrations"] = [
        build_display_narration(rs, re, text, slug, note)
        for (rs, re, text, slug, note) in NEW_DISPLAY_NARRATIONS
    ]
    data["coach_insights"] = [
        build_coach_insight(ts, slug, commentary)
        for (ts, slug, commentary) in NEW_COACH_INSIGHTS
    ]
    data["narrator_beats"] = [
        build_narrator_beat(ts, slug, text)
        for (ts, slug, text) in NEW_NARRATOR_BEATS
    ]
    data["hud_layouts"] = [
        build_hud_layout(ts, valid_until, slug, reason, widgets)
        for (ts, valid_until, slug, reason, widgets) in NEW_HUD_LAYOUTS
    ]

    # 5. Upgrade display_player_profile.pre_serve_ritual_style
    #    Idempotent: only append the sync note if it isn't already present
    #    (python-reviewer 2026-04-25 HIGH H3 — without this guard the note
    #    field grows on each re-run, breaking byte-identical idempotency).
    profile = data.get("display_player_profile") or {}
    if profile:
        profile["pre_serve_ritual_style"] = NEW_PRE_SERVE_RITUAL_STYLE
        meta = profile.get("profile_meta") or {}
        meta["authoring_date"] = "2026-04-25"
        existing_note = meta.get("note") or ""
        sync_note_text = (
            f" | {SYNC_NOTE_TAG}: pre_serve_ritual_style upgraded with bounce "
            "sequence newly observed in Andrew's second-by-second log "
            "(3 bounces + 1 mid-routine catch over 13-17s)."
        )
        if SYNC_NOTE_TAG not in existing_note:
            meta["note"] = existing_note + sync_note_text
        profile["profile_meta"] = meta
        data["display_player_profile"] = profile
        print(f"✓ Upgraded display_player_profile.pre_serve_ritual_style")

    # 6. INVARIANT: keypoints / signals / anomalies / transitions UNCHANGED
    #    (these come from the CV pipeline; we only edit the display layer).
    #    Use raise instead of assert (survives python3 -O).
    for invariant_field in ("keypoints", "signals", "anomalies", "transitions", "meta"):
        if invariant_field not in data:
            raise ValueError(f"Lost invariant field {invariant_field} during edit")

    # 7. ATOMIC write — write to a .tmp file first, then os.replace() in one
    #    syscall. Prevents corruption if the process is interrupted mid-write
    #    (python-reviewer 2026-04-25 HIGH H1).
    #    Preserve the original COMPACT format (no indent, no spaces). The
    #    original was written by Pydantic's `.model_dump_json()` which emits
    #    compact JSON. Vercel fetches this file at dashboard mount; file size
    #    matters for bandwidth + initial paint. Using indent=2 would balloon
    #    size from ~550KB to ~1.5MB (+200%).
    import os
    tmp_path = INPUT_FILE.with_suffix(".json.tmp")
    try:
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
        os.replace(tmp_path, INPUT_FILE)
    except Exception:
        # Clean up the .tmp on any error so a partial file doesn't linger.
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise
    new_size = INPUT_FILE.stat().st_size
    print(f"✓ Written {INPUT_FILE.name} atomically — {new_size:,} bytes "
          f"({new_size - original_size:+,} delta from original)")

    # 8. Re-validate by loading the just-written file
    with INPUT_FILE.open("r", encoding="utf-8") as f:
        re_loaded = json.load(f)
    after = {
        "display_transitions": len(re_loaded["display_transitions"]),
        "display_narrations": len(re_loaded["display_narrations"]),
        "coach_insights": len(re_loaded["coach_insights"]),
        "narrator_beats": len(re_loaded["narrator_beats"]),
        "hud_layouts": len(re_loaded["hud_layouts"]),
    }
    expected = {
        "display_transitions": len(NEW_DISPLAY_TRANSITIONS),
        "display_narrations": len(NEW_DISPLAY_NARRATIONS),
        "coach_insights": len(NEW_COACH_INSIGHTS),
        "narrator_beats": len(NEW_NARRATOR_BEATS),
        "hud_layouts": len(NEW_HUD_LAYOUTS),
    }
    if after != expected:
        raise ValueError(f"Re-loaded counts {after} != expected {expected}")
    print("✓ Re-loaded JSON parses cleanly; counts match expected")

    # 9. Summary diff
    print()
    print("=== Counts (before → after / expected) ===")
    for key in ("display_transitions", "display_narrations", "coach_insights",
                "narrator_beats", "hud_layouts"):
        marker = "✓" if after[key] == expected[key] else "✗"
        print(f"  {marker} {key:25s} {before[key]:3d} → {after[key]:3d}  (expected {expected[key]:3d})")

    # 10. Summary timeline
    print()
    print("=== New display_transitions timeline ===")
    for tr in re_loaded["display_transitions"]:
        ts_s = tr["timestamp_ms"] / 1000
        print(f"  t={ts_s:5.1f}s  {tr['from_state']:18s} → {tr['to_state']}")
    print()
    print("=== New display_narrations timeline ===")
    for n in re_loaded["display_narrations"]:
        rs, range_end = n["match_time_range_ms"]
        print(f"  t={rs/1000:5.1f}–{range_end/1000:5.1f}s  {n['narration_text']}")

    print()
    print("✓ DONE — match_data sync complete")
    print(f"  Backup: {BACKUP_FILE}")
    print(f"  Updated: {INPUT_FILE}")
    print()
    print("Next steps:")
    print("  1. cd dashboard && bun run build  # verify TypeScript still compiles")
    print("  2. Open dashboard locally; scrub video; verify visual matches data")
    print("  3. Commit + multi-agent review")
    return 0

if __name__ == "__main__":
    sys.exit(main())
