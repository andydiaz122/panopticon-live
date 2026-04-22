---
name: duckdb-pydantic-contracts
description: DuckDB schema and Pydantic v2 data contract patterns for PANOPTICON LIVE. Use when defining any inter-module interface, writing a DB query, or creating a new table. Enforces frozen immutability, extra="forbid", parameterized queries, and read_only=True for Vercel.
---

# DuckDB + Pydantic v2 Contracts

Every boundary in Panopticon Live is a Pydantic v2 model. Every DB query is parameterized. This skill documents the canonical schemas and query patterns.

## DuckDB Scope Is Local Pre-Compute Only (USER-CORRECTION-006)

DuckDB lives on Andrew's Mac Mini as a pre-compute intermediate and as the data source for the scouting-report Managed Agent's tool queries. **DuckDB does NOT ship to Vercel's Next.js deploy.** The frontend consumes pre-computed `dashboard/public/match_data/<match_id>.json` directly.

| Surface | DuckDB? | Why |
|---|---|---|
| `backend/precompute.py` | Yes (writable) | Populates keypoints / signals / anomalies / coach_insights |
| `backend/agents/*` | Yes (read-only) | Opus tool calls query signal windows |
| `dashboard/public/match_data/*.json` | No | Pre-computed static JSON is the single source of truth at runtime |
| Next.js Server Actions | No | Managed Agent backend can use its own tools; we don't bundle DuckDB into Vercel |

If the Managed Agent's tool queries need historical data at runtime, the options are (in order of preference):
1. Inline relevant signal summaries into the agent's initial `input` payload (fastest, simplest)
2. Include the DuckDB file as a bundled static asset under `dashboard/public/` and query via `@duckdb/duckdb-wasm` (heavier but possible)
3. Use the Managed Agent's `agent_toolset_20260401` which includes file ops — read the JSON directly

Default to option 1 for the hackathon.

## Pydantic v2 Canonical Schemas

```python
# backend/db/schema.py
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Base config applied to ALL schemas
class PanopticonBase(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ────────────────── Keypoints ──────────────────
class KeypointFrame(PanopticonBase):
    timestamp_ms: int = Field(ge=0)
    match_id: str
    player: Literal["A", "B"]
    keypoints_xyn: list[tuple[float, float]] = Field(
        description="17 COCO keypoints normalized to [0.0, 1.0]",
        min_length=17, max_length=17,
    )
    confidence: list[float] | None = Field(default=None, min_length=17, max_length=17)

    @field_validator("keypoints_xyn")
    @classmethod
    def _bounds_check(cls, v):
        for (x, y) in v:
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                raise ValueError(f"Keypoint ({x}, {y}) out of normalized bounds")
        return v


# ────────────────── State ──────────────────
PlayerState = Literal["PRE_SERVE_RITUAL", "ACTIVE_RALLY", "DEAD_TIME", "UNKNOWN"]
MatchPhase = Literal["WARMUP", "SET_1", "SET_2", "SET_3", "TIEBREAK", "CHANGEOVER", "UNKNOWN"]


# ────────────────── Signals ──────────────────
SignalName = Literal[
    "recovery_latency_ms",
    "serve_toss_variance_cm",
    "ritual_entropy_delta",
    "crouch_depth_degradation_deg",
    "baseline_retreat_distance_m",
    "lateral_work_rate",
    "split_step_latency_ms",
]

class SignalSample(PanopticonBase):
    timestamp_ms: int = Field(ge=0)
    match_id: str
    player: Literal["A", "B"]
    signal_name: SignalName
    value: float | None
    baseline_z_score: float | None = Field(default=None, ge=-10.0, le=10.0)
    state: PlayerState


class FatigueVector(PanopticonBase):
    window_start_ms: int = Field(ge=0)
    window_end_ms: int = Field(ge=0)
    match_id: str
    player: Literal["A", "B"]
    signals: dict[SignalName, float | None]
    state: PlayerState

    @field_validator("window_end_ms")
    @classmethod
    def _window_order(cls, v, info):
        if "window_start_ms" in info.data and v <= info.data["window_start_ms"]:
            raise ValueError("window_end_ms must be > window_start_ms")
        return v


# ────────────────── Anomalies ──────────────────
class AnomalyEvent(PanopticonBase):
    event_id: str
    timestamp_ms: int = Field(ge=0)
    match_id: str
    player: Literal["A", "B"]
    signal_name: SignalName
    value: float
    baseline_mean: float
    baseline_std: float = Field(ge=0.0)
    z_score: float = Field(ge=-10.0, le=10.0)
    severity: float = Field(ge=0.0, le=1.0)


# ────────────────── Opus outputs ──────────────────
class CoachInsight(PanopticonBase):
    insight_id: str
    timestamp_ms: int
    match_id: str
    thinking: str | None = None
    commentary: str
    tool_calls: list[dict]  # JSON-serializable
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0


class HUDWidgetSpec(PanopticonBase):
    widget: Literal[
        "PlayerNameplate", "SignalBar", "MomentumMeter",
        "PredictiveOverlay", "TossTracer", "FootworkHeatmap",
    ]
    slot: Literal["top-left", "top-right", "top-center", "right-1", "right-2", "right-3", "right-4", "center-overlay"]
    props: dict  # widget-specific


class HUDLayoutSpec(PanopticonBase):
    layout_id: str
    timestamp_ms: int
    reason: str  # Opus's explanation
    widgets: list[HUDWidgetSpec]
    valid_until_ms: int  # recompute after this
```

## DuckDB Schema

```python
# backend/db/setup.py
import duckdb

SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS match_meta (
  match_id   TEXT PRIMARY KEY,
  clip_sha256 TEXT NOT NULL,
  clip_fps   DOUBLE NOT NULL,
  duration_ms INTEGER NOT NULL,
  player_a   TEXT NOT NULL,
  player_b   TEXT NOT NULL,
  court_corners TEXT NOT NULL,  -- JSON
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keypoints (
  timestamp_ms INTEGER NOT NULL,
  match_id     TEXT NOT NULL,
  player       TEXT NOT NULL CHECK (player IN ('A', 'B')),
  keypoints_xyn BLOB NOT NULL,  -- packed float32 34-vector (17 × (x, y))
  confidence   BLOB,             -- packed float32 17-vector
  PRIMARY KEY (timestamp_ms, match_id, player)
);

CREATE TABLE IF NOT EXISTS signals (
  timestamp_ms INTEGER NOT NULL,
  match_id     TEXT NOT NULL,
  player       TEXT NOT NULL CHECK (player IN ('A', 'B')),
  signal_name  TEXT NOT NULL,
  value        DOUBLE,
  baseline_z_score DOUBLE,
  state        TEXT NOT NULL,
  PRIMARY KEY (timestamp_ms, match_id, player, signal_name)
);
CREATE INDEX IF NOT EXISTS idx_signals_match ON signals (match_id, timestamp_ms);

CREATE TABLE IF NOT EXISTS anomalies (
  event_id     TEXT PRIMARY KEY,
  timestamp_ms INTEGER NOT NULL,
  match_id     TEXT NOT NULL,
  player       TEXT NOT NULL,
  signal_name  TEXT NOT NULL,
  value        DOUBLE NOT NULL,
  baseline_mean DOUBLE NOT NULL,
  baseline_std DOUBLE NOT NULL,
  z_score      DOUBLE NOT NULL,
  severity     DOUBLE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_anomalies_match ON anomalies (match_id, timestamp_ms);

CREATE TABLE IF NOT EXISTS coach_insights (
  insight_id   TEXT PRIMARY KEY,
  timestamp_ms INTEGER NOT NULL,
  match_id     TEXT NOT NULL,
  thinking     TEXT,
  commentary   TEXT NOT NULL,
  tool_calls   TEXT NOT NULL,  -- JSON
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL,
  cache_read_tokens INTEGER DEFAULT 0,
  cache_creation_tokens INTEGER DEFAULT 0
);
"""

def init_schema(db_path: str) -> None:
    with duckdb.connect(db_path) as conn:
        conn.execute(SCHEMA_DDL)
```

## Parameterized Query Patterns (ALWAYS)

```python
# GOOD — parameterized
def get_signal_window(conn, match_id: str, player: str, signal: str, t_start: int, t_end: int):
    return conn.execute(
        """
        SELECT timestamp_ms, value, baseline_z_score
        FROM signals
        WHERE match_id = ?
          AND player = ?
          AND signal_name = ?
          AND timestamp_ms BETWEEN ? AND ?
        ORDER BY timestamp_ms
        """,
        [match_id, player, signal, t_start, t_end],
    ).fetchall()


# NEVER — f-string interpolation (SQL injection + type drift)
# conn.execute(f"SELECT ... WHERE match_id = '{match_id}'")
```

## Read-Only Connection for Vercel (Prod)

```python
# backend/api/db.py (loaded on Vercel)
import duckdb
from functools import lru_cache
import os

@lru_cache(maxsize=1)
def get_conn():
    db_path = os.getenv("DUCKDB_PATH", "data/panopticon.duckdb")
    return duckdb.connect(db_path, read_only=True)
```

Vercel functions are read-only against the pre-computed DB. Local pre-compute opens writable.

## Migrations Strategy

We don't migrate. The DuckDB file is pre-computed fresh per deploy. If schema changes, re-precompute all clips. This is the right trade-off for a 6-day project with fixed clip set.

## JSON Column Strategy

- `court_corners` stored as TEXT (JSON) — easier introspection than BLOB
- `tool_calls` in coach_insights — TEXT (JSON)
- Keypoints stored as BLOB (float32 packed) — ~10x smaller than JSON, faster read
- Use `numpy.frombuffer` + `.tobytes()` at the Python boundary

## Schema Versioning

Each DuckDB file includes a `match_meta` row. Add a `schema_version` column if you evolve schema across deploys. For hackathon week, one fixed schema is fine.

## Usage in Agents

- `data-integrity-guard` agent owns this schema
- `cv-pipeline-engineer` agent writes to keypoints/signals/anomalies tables
- `opus-coach-architect` agent writes to coach_insights table
- `hud-auteur-frontend` agent reads via FastAPI SSE endpoints
