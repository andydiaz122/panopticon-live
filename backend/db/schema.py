"""Pydantic v2 data contracts + DuckDB DDL for Panopticon Live.

Every inter-module interface is a Pydantic v2 model. No dict crosses a module boundary.
Every model is frozen and forbids extras — prevents dict hallucination.

DuckDB DDL is idempotent (CREATE TABLE IF NOT EXISTS). Never destructively alter;
re-precompute if schema evolves.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_serializer, field_validator, model_validator

# ──────────────────────────── Serialization precision ────────────────────────────

FLOAT_SERIALIZE_DECIMALS: int = 4
"""Decimal places for JSON serialization (USER-CORRECTION-015 payload hygiene).

4 decimals ≈ 0.0001 precision. At 1920-wide normalized coords that's ~0.2 px
(below YOLO keypoint jitter ~2-3 px); in court meters that's 0.1 mm (far below
measurement noise). Prevents 10MB+ JSON bloat from full-precision float streams.
"""


def _round_float(v: float | None) -> float | None:
    return None if v is None else round(v, FLOAT_SERIALIZE_DECIMALS)


def _round_pair(v: tuple[float, float]) -> tuple[float, float]:
    return (round(v[0], FLOAT_SERIALIZE_DECIMALS), round(v[1], FLOAT_SERIALIZE_DECIMALS))


def _round_pair_list(v: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [(round(x, FLOAT_SERIALIZE_DECIMALS), round(y, FLOAT_SERIALIZE_DECIMALS)) for x, y in v]


def _round_list(v: list[float] | None) -> list[float] | None:
    return None if v is None else [round(x, FLOAT_SERIALIZE_DECIMALS) for x in v]


def _round_dict(v: dict[str, float | None]) -> dict[str, float | None]:
    """Round dict values (None passes through). Tightly typed per python-reviewer HIGH finding."""
    return {k: (None if val is None else round(val, FLOAT_SERIALIZE_DECIMALS)) for k, val in v.items()}

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
DOUBLES_COURT_WIDTH_M: float = 10.97
"""Outer-sideline width of a doubles court. Court length is identical to singles (23.77m).

When the court-corner annotation traces the OUTSIDE of the doubles alleys (the outermost
sidelines), CourtMapper should canonicalize to 10.97m wide instead of 8.23m. Otherwise
lateral signal values are ~25% compressed on the x-axis."""

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

    @field_serializer("keypoints_xyn")
    def _ser_keypoints(self, v: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return _round_pair_list(v)

    @field_serializer("confidence")
    def _ser_conf(self, v: list[float] | None) -> list[float] | None:
        return _round_list(v)


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

    @field_serializer("keypoints_xyn")
    def _ser_keypoints(self, v: list[tuple[float, float]]) -> list[tuple[float, float]]:
        return _round_pair_list(v)

    @field_serializer("confidence")
    def _ser_conf(self, v: list[float]) -> list[float]:
        return [round(x, FLOAT_SERIALIZE_DECIMALS) for x in v]

    @field_serializer("bbox_conf")
    def _ser_bbox(self, v: float) -> float:
        return round(v, FLOAT_SERIALIZE_DECIMALS)

    @field_serializer("feet_mid_xyn")
    def _ser_feet_xyn(self, v: tuple[float, float]) -> tuple[float, float]:
        return _round_pair(v)

    @field_serializer("feet_mid_m")
    def _ser_feet_m(self, v: tuple[float, float]) -> tuple[float, float]:
        return _round_pair(v)


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

    @field_serializer("value")
    def _ser_value(self, v: float | None) -> float | None:
        return _round_float(v)

    @field_serializer("baseline_z_score")
    def _ser_z_score(self, v: float | None) -> float | None:
        return _round_float(v)


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
    def _window_order(cls, v: int, info: ValidationInfo) -> int:
        start = info.data.get("window_start_ms")
        if start is not None and v <= start:
            raise ValueError("window_end_ms must be strictly greater than window_start_ms")
        return v

    @field_serializer("signals")
    def _ser_signals(self, v: dict[SignalName, float | None]) -> dict:
        return _round_dict(v)


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

    @field_serializer("value", "baseline_mean", "baseline_std", "z_score", "severity")
    def _ser_metric(self, v: float) -> float:
        return round(v, FLOAT_SERIALIZE_DECIMALS)


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


class NarratorBeat(PanopticonBase):
    """One Haiku 4.5 per-second ESPN-style color-commentary beat.

    Pre-computed offline inside precompute.py (Phase 2) alongside CoachInsight.
    Rendered in the frontend as a ticker/crawl synchronized to videoRef.currentTime.
    Haiku intentionally — judges see cost-aware multi-model routing (Opus reasons,
    Haiku narrates) as part of the "Opus 4.7 Use" judging story.

    No cache_* fields: Haiku beat prompts are tiny (<500 tokens) and the 5-minute
    prompt-cache TTL rarely pays off at 1-beat-per-second cadence. Omit for schema
    honesty rather than pad with zeros.
    """

    beat_id: str = Field(min_length=1)
    timestamp_ms: int = Field(ge=0)
    match_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


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


# ──────────────────────────── Multi-Agent Trace (PATTERN-056) ────────────────────────────
#
# Captures every event from a real offline multi-agent run so the frontend can
# REPLAY the reasoning sequence deterministically (USER-CORRECTION-024). The
# discriminated union on `kind` is load-bearing: the TypeScript consumer
# narrows by `kind` to render the right UI pill, and Pydantic routes each
# inbound dict to the correct subclass.


class TraceThinking(PanopticonBase):
    """Extended-thinking block emitted by an agent (Opus 4.7 internal reasoning)."""

    kind: Literal["thinking"] = "thinking"
    t_ms: int = Field(ge=0, description="ms offset from trace start, not wall clock")
    content: str


class TraceToolCall(PanopticonBase):
    """A tool invocation by an agent. `input_json` is pre-serialized to avoid
    arbitrary-dict drift between Python producer and TS consumer."""

    kind: Literal["tool_call"] = "tool_call"
    t_ms: int = Field(ge=0)
    tool_name: str = Field(min_length=1)
    input_json: str


class TraceToolResult(PanopticonBase):
    """A tool result returned to the agent. `output_json` is pre-serialized."""

    kind: Literal["tool_result"] = "tool_result"
    t_ms: int = Field(ge=0)
    tool_name: str = Field(min_length=1)
    output_json: str
    is_error: bool = False


class TraceText(PanopticonBase):
    """A free-form text block emitted by an agent (often the final answer chunk)."""

    kind: Literal["text"] = "text"
    t_ms: int = Field(ge=0)
    content: str


class TraceHandoff(PanopticonBase):
    """An explicit handoff from one agent to the next. `payload_summary` is a
    one-line description; the FULL payload becomes the next agent's input
    (captured in that agent's subsequent events)."""

    kind: Literal["handoff"] = "handoff"
    t_ms: int = Field(ge=0)
    from_agent: str = Field(min_length=1)
    to_agent: str = Field(min_length=1)
    payload_summary: str


# Discriminated union — Pydantic v2 routes by `kind` field
TraceEvent = Annotated[
    Union[TraceThinking, TraceToolCall, TraceToolResult, TraceText, TraceHandoff],
    Field(discriminator="kind"),
]


class AgentStep(PanopticonBase):
    """One agent's turn within the Scouting Committee execution."""

    agent_name: str = Field(min_length=1)
    agent_role: str = Field(min_length=1)
    started_at_ms: int = Field(ge=0)
    completed_at_ms: int = Field(ge=0)
    events: list[TraceEvent]

    @model_validator(mode="after")
    def _validate_timeline(self) -> AgentStep:
        if self.completed_at_ms < self.started_at_ms:
            raise ValueError(
                "completed_at_ms must be >= started_at_ms; "
                f"got started={self.started_at_ms} completed={self.completed_at_ms}"
            )
        last_t: int = -1
        for i, ev in enumerate(self.events):
            if ev.t_ms < last_t:
                raise ValueError(
                    f"events[{i}] t_ms ({ev.t_ms}) is non-monotonic; "
                    f"previous event had t_ms={last_t}. Trace events MUST be "
                    "monotonic for deterministic UI replay."
                )
            last_t = ev.t_ms
        return self


class AgentTrace(PanopticonBase):
    """Full captured execution of a multi-agent Scouting Committee run.

    Written to `dashboard/public/match_data/agent_trace.json` during offline
    precompute; loaded by the Orchestration Console (Tab 3) via fetch()+useEffect
    (GOTCHA-026: never as a Server Component prop).
    """

    match_id: str = Field(min_length=1)
    generated_at: datetime
    committee_goal: str
    steps: list[AgentStep]
    final_report_markdown: str
    total_compute_ms: int = Field(ge=0)
    # Match-timecode anchor (founder audit, 2026-04-23): the MIN/MAX of signal
    # timestamps this committee analyzed, in match milliseconds (NOT UI playback
    # timestamps). Lets the Orchestration Console show "Analyzing match 0:00-1:00"
    # so judges map the swarm's analysis to the video they're watching. Optional
    # for backwards-compat with pre-Phase-4-audit traces.
    match_time_range_ms: tuple[int, int] | None = Field(default=None)

    @model_validator(mode="after")
    def _validate_steps_chronological(self) -> AgentTrace:
        for i in range(1, len(self.steps)):
            prev = self.steps[i - 1]
            curr = self.steps[i]
            if curr.started_at_ms < prev.completed_at_ms:
                raise ValueError(
                    f"steps[{i}] started_at_ms ({curr.started_at_ms}) is before "
                    f"steps[{i - 1}].completed_at_ms ({prev.completed_at_ms}). "
                    "Scouting Committee steps must be chronologically non-overlapping."
                )
        return self


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

CREATE TABLE IF NOT EXISTS narrator_beats (
  beat_id      TEXT PRIMARY KEY,
  timestamp_ms INTEGER NOT NULL,
  match_id     TEXT NOT NULL,
  text         TEXT NOT NULL,
  input_tokens INTEGER NOT NULL,
  output_tokens INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_narrator_match ON narrator_beats (match_id, timestamp_ms);
"""
