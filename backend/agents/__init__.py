"""Opus 4.7 agent layer for PANOPTICON LIVE.

Runs OFFLINE inside backend/precompute.py (USER-CORRECTION-002).
Emits timestamp-tagged CoachInsight + HUDLayoutSpec + NarratorBeat records
that the frontend replays synchronized to videoRef.currentTime.

Modules:
    tools          — deterministic DuckDB/in-memory query tools exposed to Opus
    system_prompt  — biomechanics primer (prompt-cached, 5-10K tokens)
    opus_coach     — Opus 4.7 Reasoner role (anomaly-triggered CoachInsight)
    hud_designer   — Opus 4.7 Designer role (state-transition-triggered HUDLayoutSpec)
    haiku_narrator — Haiku 4.5 Voice role (per-second NarratorBeat)
"""
