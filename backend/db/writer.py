"""Batch writer + JSON exporter for the pre-compute DuckDB.

Consumes Pydantic v2 models directly — no dict-crosses-boundary per CLAUDE.md.
Single-match scope per writer instance. Reuses one writable DuckDB connection
for the writer's lifetime.

Schema invariants (see backend/db/schema.py SCHEMA_DDL):
- keypoints table stores `keypoints_xyn` + `confidence` as packed float32 BLOBs.
  Each FrameKeypoints produces up to 2 rows (one per player side).
- coach_insights stores `tool_calls` as a JSON TEXT column.
- All four signal/keypoint/anomaly/coach tables use INSERT OR REPLACE so retries
  are idempotent on primary keys.

JSON export uses Pydantic's own nested composition so `@field_serializer`
propagates through every level (USER-CORRECTION-015 4-decimal float rounding).
We do NOT call json.dumps on manually-dumped dicts — that can bypass
field_serializer depending on Pydantic's code path.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

import duckdb
import numpy as np
from pydantic import BaseModel, ConfigDict

from backend.db.schema import (
    AnomalyEvent,
    CoachInsight,
    FrameKeypoints,
    HUDLayoutSpec,
    MatchMeta,
    SignalSample,
    StateTransition,
)
from backend.db.setup import init_schema, writable_connect


class DuckDBWriter:
    """Batch-insert Pydantic models into the pre-compute DuckDB.

    Single-match scope: constructed with a match_id; all writes share it.
    Reuses one writable connection for the lifetime of the writer.

    Typical usage:

        with DuckDBWriter(db_path, match_id="utr_01") as w:
            w.write_match_meta(meta)
            for frame in frames:
                w.queue_keypoint_frame(frame)
            for sample in samples:
                w.queue_signal(sample)
            # w.close() is called automatically on __exit__, flushing all queues.
    """

    BATCH_SIZE: int = 1000
    """Auto-flush trigger — prevents unbounded queue growth during long runs."""

    def __init__(self, db_path: Path | str, match_id: str) -> None:
        self.match_id = match_id
        # Ensure schema is present before any writes — init_schema is idempotent
        # and also creates parent dirs, so a fresh db_path works out of the box.
        init_schema(db_path)
        self._conn: duckdb.DuckDBPyConnection = writable_connect(db_path)
        self._pending_signals: list[SignalSample] = []
        self._pending_keypoints: list[FrameKeypoints] = []
        self._pending_anomalies: list[AnomalyEvent] = []
        self._pending_coach: list[CoachInsight] = []

    # ──────────────────────────── Direct write ────────────────────────────

    def write_match_meta(self, meta: MatchMeta) -> None:
        """Upsert the match_meta row. Call once before any other writes."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO match_meta
            (match_id, clip_sha256, clip_fps, duration_ms, width, height,
             player_a, player_b, court_corners_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                meta.match_id,
                meta.clip_sha256,
                meta.clip_fps,
                meta.duration_ms,
                meta.width,
                meta.height,
                meta.player_a,
                meta.player_b,
                meta.court_corners_json,
            ],
        )

    # ──────────────────────────── Queueing ────────────────────────────

    def queue_signal(self, s: SignalSample) -> None:
        self._pending_signals.append(s)
        if len(self._pending_signals) >= self.BATCH_SIZE:
            self.flush()

    def queue_keypoint_frame(self, kf: FrameKeypoints) -> None:
        self._pending_keypoints.append(kf)
        if len(self._pending_keypoints) >= self.BATCH_SIZE:
            self.flush()

    def queue_anomaly(self, a: AnomalyEvent) -> None:
        self._pending_anomalies.append(a)
        if len(self._pending_anomalies) >= self.BATCH_SIZE:
            self.flush()

    def queue_coach_insight(self, ci: CoachInsight) -> None:
        self._pending_coach.append(ci)
        if len(self._pending_coach) >= self.BATCH_SIZE:
            self.flush()

    # ──────────────────────────── Flush ────────────────────────────

    def flush(self) -> None:
        """Flush all pending queues to DuckDB.

        Uses executemany for batch efficiency. Idempotent — safe to call with
        empty queues.
        """
        if self._pending_signals:
            rows = [
                (
                    s.timestamp_ms,
                    s.match_id,
                    s.player,
                    s.signal_name,
                    s.value,
                    s.baseline_z_score,
                    s.state,
                )
                for s in self._pending_signals
            ]
            self._conn.executemany(
                "INSERT OR REPLACE INTO signals "
                "(timestamp_ms, match_id, player, signal_name, value, baseline_z_score, state) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            self._pending_signals.clear()

        if self._pending_keypoints:
            # Each FrameKeypoints expands to up to 2 rows (one per PlayerDetection).
            # Reviewer HIGH: enforce 17-keypoint invariant at write time. The BLOB
            # readback contract `np.frombuffer(blob, dtype=np.float32).reshape(17, 2)`
            # assumes exactly 17 keypoints. If YOLO ever returns a different keypoint
            # count (model upgrade, corrupted detection), we want to fail LOUDLY at
            # write time rather than silently corrupt DuckDB blobs.
            rows: list[tuple] = []
            for kf in self._pending_keypoints:
                for side, detection in (("A", kf.player_a), ("B", kf.player_b)):
                    if detection is None:
                        continue
                    if len(detection.keypoints_xyn) != 17 or len(detection.confidence) != 17:
                        raise ValueError(
                            f"keypoint length mismatch: expected 17, got "
                            f"{len(detection.keypoints_xyn)} keypoints / "
                            f"{len(detection.confidence)} confidences "
                            f"(player={side}, t_ms={kf.t_ms}). "
                            f"Would corrupt BLOB reshape contract."
                        )
                    kp_arr = np.asarray(detection.keypoints_xyn, dtype=np.float32).tobytes()
                    conf_arr = np.asarray(detection.confidence, dtype=np.float32).tobytes()
                    rows.append((kf.t_ms, self.match_id, side, kp_arr, conf_arr))
            if rows:
                self._conn.executemany(
                    "INSERT OR REPLACE INTO keypoints "
                    "(timestamp_ms, match_id, player, keypoints_xyn, confidence) "
                    "VALUES (?, ?, ?, ?, ?)",
                    rows,
                )
            self._pending_keypoints.clear()

        if self._pending_anomalies:
            rows = [
                (
                    a.event_id,
                    a.timestamp_ms,
                    a.match_id,
                    a.player,
                    a.signal_name,
                    a.value,
                    a.baseline_mean,
                    a.baseline_std,
                    a.z_score,
                    a.severity,
                )
                for a in self._pending_anomalies
            ]
            self._conn.executemany(
                "INSERT OR REPLACE INTO anomalies "
                "(event_id, timestamp_ms, match_id, player, signal_name, value, "
                "baseline_mean, baseline_std, z_score, severity) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            self._pending_anomalies.clear()

        if self._pending_coach:
            rows = [
                (
                    ci.insight_id,
                    ci.timestamp_ms,
                    ci.match_id,
                    ci.thinking,
                    ci.commentary,
                    json.dumps(ci.tool_calls),
                    ci.input_tokens,
                    ci.output_tokens,
                    ci.cache_read_tokens,
                    ci.cache_creation_tokens,
                )
                for ci in self._pending_coach
            ]
            self._conn.executemany(
                "INSERT OR REPLACE INTO coach_insights "
                "(insight_id, timestamp_ms, match_id, thinking, commentary, tool_calls, "
                "input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                rows,
            )
            self._pending_coach.clear()

    # ──────────────────────────── Lifecycle ────────────────────────────

    def close(self) -> None:
        """Flush + close the connection."""
        self.flush()
        self._conn.close()

    def __enter__(self) -> DuckDBWriter:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


# ──────────────────────────── JSON exporter ────────────────────────────


class _MatchData(BaseModel):
    """Ad-hoc wrapper model for match_data.json serialization.

    Declared frozen + extra="forbid" to match the rest of the schema.
    Nested composition ensures `@field_serializer` propagates to every level —
    per USER-CORRECTION-015, this is how we avoid manual float rounding.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    meta: MatchMeta
    keypoints: list[FrameKeypoints]
    signals: list[SignalSample]
    anomalies: list[AnomalyEvent]
    coach_insights: list[CoachInsight]
    hud_layouts: list[HUDLayoutSpec]
    transitions: list[StateTransition]


def dump_match_data_json(
    out_path: Path | str,
    meta: MatchMeta,
    keypoints: Iterable[FrameKeypoints],
    signals: Iterable[SignalSample],
    anomalies: Iterable[AnomalyEvent],
    coach_insights: Iterable[CoachInsight],
    hud_layouts: Iterable[HUDLayoutSpec],
    transitions: Iterable[StateTransition],
) -> Path:
    """Export full match payload as a single JSON file.

    Uses Pydantic's nested composition so `@field_serializer` propagates
    through every level — every float is rounded to FLOAT_SERIALIZE_DECIMALS
    automatically (USER-CORRECTION-015). No manual rounding needed.

    Materializes each Iterable via list() before composing the root model
    so generators are OK.
    """
    data = _MatchData(
        meta=meta,
        keypoints=list(keypoints),
        signals=list(signals),
        anomalies=list(anomalies),
        coach_insights=list(coach_insights),
        hud_layouts=list(hud_layouts),
        transitions=list(transitions),
    )
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # by_alias=True for forward-compat (no current aliases).
    # exclude_none=True keeps the JSON tight and mirrors the React frontend's contract.
    out.write_text(data.model_dump_json(by_alias=True, exclude_none=True))
    return out
