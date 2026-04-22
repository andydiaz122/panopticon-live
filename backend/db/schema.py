"""Pydantic v2 data contracts + DuckDB DDL for Panopticon Live.

Every inter-module interface is a Pydantic v2 model. No dict crosses a module boundary.
Every model is frozen and forbids extras — prevents dict hallucination.

DuckDB DDL is idempotent (CREATE TABLE IF NOT EXISTS). Never destructively alter;
re-precompute if schema evolves.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ──────────────────────────── Type aliases ────────────────────────────

PlayerSide = Literal["A", "B"]
PlayerState = Literal["PRE_SERVE_RITUAL", "ACTIVE_RALLY", "DEAD_TIME", "UNKNOWN"]
MatchPhase = Literal["WARMUP", "SET_1", "SET_2", "SET_3", "TIEBREAK", "CHANGEOVER", "UNKNOWN"]
SignalName = Literal[
    "recovery_latency_ms",
    "serve_toss_variance_cm",
    "ritual_entropy_delta",
    "crouch_depth_degradation_deg",
    "baseline_retreat_distance_m",
    "lateral_work_rate",
    "split_step_latency_ms",
]

# COCO keypoint indices (17 total)
COCO_KEYPOINTS = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]
assert len(COCO_KEYPOINTS) == 17

# COCO keypoint indices (named) — used by signal extractors + robust_foot_point
KP_LEFT_SHOULDER = 5
KP_RIGHT_SHOULDER = 6
KP_LEFT_WRIST = 9
KP_RIGHT_WRIST = 10
KP_LEFT_HIP = 11
KP_RIGHT_HIP = 12
KP_LEFT_KNEE = 13
KP_RIGHT_KNEE = 14
KP_LEFT_ANKLE = 15
KP_RIGHT_ANKLE = 16

# Court dimensions (singles). Fixed by the ITF. Do not change.
SINGLES_COURT_LENGTH_M: float = 23.77
SINGLES_COURT_WIDTH_M: float = 8.23
NET_Y_M: float = SINGLES_COURT_LENGTH_M / 2.0  # = 11.885 — used by Absolute Court Half Assignment


# ──────────────────────────── Fallback modes ────────────────────────────

FallbackMode = Literal["ankle", "knee", "hip"]


# ──────────────────────────── Pydantic base ────────────────────────────

class PanopticonBase(BaseModel):
    """Strict base: frozen, no surprise keys."""

    model_config = ConfigDict(frozen=True, extra="forbid")


# ──────────────────────────── Court corners ────────────────────────────

class CornersNormalized(PanopticonBase):
    """Four court corners in normalized [0.0, 1.0] image coordinates.

    Convention (frozen):
      top_left     = far baseline, far-left sideline
      top_right    = far baseline, far-right sideline
      bottom_right = near baseline, near-right sideline
      bottom_left  = near baseline, near-left sideline
    """

    top_left: tuple[float, float]
    top_right: tuple[float, float]
    bottom_right: tuple[float, float]
    bottom_left: tuple[float, float]

    @field_validator("top_left", "top_right", "bottom_right", "bottom_left")
    @classmethod
    def _bounds(cls, v: tuple[float, float]) -> tuple[float, float]:
        x, y = v
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            raise ValueError(f"Corner ({x}, {y}) must be in normalized [0.0, 1.0]")
        return v


# ──────────────────────────── Keypoints ────────────────────────────

class KeypointFrame(PanopticonBase):
    """One player's 17 COCO keypoints at a single frame, normalized to [0, 1]."""

    timestamp_ms: int = Field(ge=0)
    match_id: str = Field(min_length=1)
    player: PlayerSide
    keypoints_xyn: list[tuple[float, float]] = Field(
        description="17 (x, y) pairs normalized to [0.0, 1.0] via Ultralytics .xyn.",
        min_length=17, max_length=17,
    )
    confidence: list[float] | None = Field(default=None, min_length=17, max_length=17)

    @field_validator("keypoints_xyn")
    @classmethod
    def _bounds_check(cls, v: list[tuple[float, float]]) -> list[tuple[float, float]]:
        for x, y in v:
            if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                raise ValueError(f"Keypoint ({x}, {y}) out of normalized [0.0, 1.0] bounds")
        return v


# ──────────────────────────── Raw YOLO detection (pre-assignment) ────────────────────────────

class RawDetection(PanopticonBase):
    """One YOLO-Pose detection before we know which player it represents.

    Produced by YOLO inference. Consumed by `assign_players` which splits by court half
    (USER-CORRECTION-007) to produce PlayerDetection records.
    """

    keypoints_xyn: list[tuple[float, float]] = Field(min_length=17, max_length=17)
    confidence: list[float] = Field(min_length=17, max_length=17)
    bbox_conf: float = Field(ge=0.0, le=1.0)


# ──────────────────────────── Player detection (post-assignment) ────────────────────────────

class PlayerDetection(PanopticonBase):
    """A YOLO detection attributed to a specific player via Absolute Court Half Assignment."""

    player: PlayerSide
    keypoints_xyn: list[tuple[float, float]] = Field(min_length=17, max_length=17)
    confidence: list[float] = Field(min_length=17, max_length=17)
    bbox_conf: float = Field(ge=0.0, le=1.0)
    feet_mid_xyn: tuple[float, float]  # normalized [0,1], for canvas rendering
    feet_mid_m: tuple[float, float]    # court meters, for Kalman input (USER-CORRECTION-008)
    fallback_mode: FallbackMode        # which segment produced feet_mid (USER-CORRECTION-003)


# ──────────────────────────── State transitions ────────────────────────────

class StateTransition(PanopticonBase):
    """Emitted by PlayerStateMachine / MatchStateMachine on every state change."""

    timestamp_ms: int = Field(ge=0)
    player: PlayerSide
    from_state: PlayerState
    to_state: PlayerState
    reason: Literal["kinematic", "match_coupling", "initial"]


# ──────────────────────────── Frame keypoints (for match_data.json) ────────────────────────────

class FrameKeypoints(PanopticonBase):
    """Per-frame keypoints for both players. Consumed by the frontend canvas loop."""

    t_ms: int = Field(ge=0)
    frame_idx: int = Field(ge=0)
    player_a: PlayerDetection | None
    player_b: PlayerDetection | None


# ──────────────────────────── Signals ────────────────────────────

class SignalSample(PanopticonBase):
    """Single sample of one biomechanical signal for one player at one moment."""

    timestamp_ms: int = Field(ge=0)
    match_id: str = Field(min_length=1)
    player: PlayerSide
    signal_name: SignalName
    value: float | None
    baseline_z_score: float | None = Field(default=None, ge=-10.0, le=10.0)
    state: PlayerState


class FatigueVector(PanopticonBase):
    """Aggregated signal state for a ~1-second window during which player state is stable."""

    window_start_ms: int = Field(ge=0)
    window_end_ms: int = Field(ge=0)
    match_id: str = Field(min_length=1)
    player: PlayerSide
    signals: dict[SignalName, float | None]
    state: PlayerState

    @field_validator("window_end_ms")
    @classmethod
    def _window_order(cls, v: int, info) -> int:
        start = info.data.get("window_start_ms")
        if start is not None and v <= start:
            raise ValueError("window_end_ms must be strictly greater than window_start_ms")
        return v


# ──────────────────────────── Anomalies ────────────────────────────

class AnomalyEvent(PanopticonBase):
    """A statistically significant deviation from a player's own baseline."""

    event_id: str = Field(min_length=1)
    timestamp_ms: int = Field(ge=0)
    match_id: str = Field(min_length=1)
    player: PlayerSide
    signal_name: SignalName
    value: float
    baseline_mean: float
    baseline_std: float = Field(ge=0.0)
    z_score: float = Field(ge=-10.0, le=10.0)
    severity: float = Field(ge=0.0, le=1.0)


# ──────────────────────────── Opus outputs ────────────────────────────

class CoachInsight(PanopticonBase):
    """One structured Opus 4.7 coach response, including visible thinking tokens."""

    insight_id: str = Field(min_length=1)
    timestamp_ms: int = Field(ge=0)
    match_id: str = Field(min_length=1)
    thinking: str | None = None
    commentary: str
    tool_calls: list[dict]  # free-form; only JSON-serializable content
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cache_read_tokens: int = Field(default=0, ge=0)
    cache_creation_tokens: int = Field(default=0, ge=0)


WidgetKind = Literal[
    "PlayerNameplate", "SignalBar", "MomentumMeter",
    "PredictiveOverlay", "TossTracer", "FootworkHeatmap",
]
WidgetSlot = Literal[
    "top-left", "top-right", "top-center",
    "right-1", "right-2", "right-3", "right-4",
    "center-overlay", "bottom",
]


class HUDWidgetSpec(PanopticonBase):
    """One widget's placement + props within a HUD layout."""

    widget: WidgetKind
    slot: WidgetSlot
    props: dict  # widget-specific; Pydantic child models would be nicer but dict is fine at the UI boundary


class HUDLayoutSpec(PanopticonBase):
    """A HUD layout produced by Opus 4.7 Designer for the current match state."""

    layout_id: str = Field(min_length=1)
    timestamp_ms: int = Field(ge=0)
    reason: str  # Opus's natural-language explanation of why THIS layout
    widgets: list[HUDWidgetSpec]
    valid_until_ms: int = Field(ge=0)


# ──────────────────────────── Match metadata ────────────────────────────

class MatchMeta(PanopticonBase):
    """One row per processed clip — pre-compute manifest."""

    match_id: str = Field(min_length=1)
    clip_sha256: str = Field(min_length=64, max_length=64)
    clip_fps: float = Field(gt=0.0, le=240.0)
    duration_ms: int = Field(ge=0)
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    player_a: str = Field(min_length=1)
    player_b: str = Field(min_length=1)
    court_corners_json: str  # 4 corners as JSON


# ──────────────────────────── DDL ────────────────────────────

SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS match_meta (
  match_id   TEXT PRIMARY KEY,
  clip_sha256 TEXT NOT NULL,
  clip_fps   DOUBLE NOT NULL,
  duration_ms INTEGER NOT NULL,
  width      INTEGER NOT NULL,
  height     INTEGER NOT NULL,
  player_a   TEXT NOT NULL,
  player_b   TEXT NOT NULL,
  court_corners_json TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keypoints (
  timestamp_ms INTEGER NOT NULL,
  match_id     TEXT NOT NULL,
  player       TEXT NOT NULL CHECK (player IN ('A', 'B')),
  keypoints_xyn BLOB NOT NULL,   -- packed float32 34-vector (17 * (x, y))
  confidence    BLOB,            -- packed float32 17-vector, nullable
  PRIMARY KEY (timestamp_ms, match_id, player)
);
CREATE INDEX IF NOT EXISTS idx_keypoints_match ON keypoints (match_id, timestamp_ms);

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
CREATE INDEX IF NOT EXISTS idx_signals_name ON signals (signal_name, timestamp_ms);

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
CREATE INDEX IF NOT EXISTS idx_coach_match ON coach_insights (match_id, timestamp_ms);
"""
