/**
 * TypeScript mirrors of backend/db/schema.py Pydantic models.
 *
 * IMPORTANT: keep field names + casing IDENTICAL to Python (snake_case).
 * The JSON export via `dump_match_data_json` uses Pydantic's default serialization
 * which preserves Python field names — no camelCase transform.
 *
 * Numeric invariants (enforced by Pydantic `@field_serializer`):
 *  - All floats rounded to 4 decimals in the JSON (USER-CORRECTION-015)
 *  - Keypoints are in normalized [0, 1] coords (via Ultralytics `.xyn`)
 *  - feet_mid_m / baseline_retreat_distance_m are in COURT METERS
 */

// ──────────────────────────── Enums (Literal unions) ────────────────────────────

export type PlayerSide = 'A' | 'B';

export type PlayerState =
  | 'PRE_SERVE_RITUAL'
  | 'ACTIVE_RALLY'
  | 'DEAD_TIME'
  | 'UNKNOWN';

export type MatchPhase =
  | 'WARMUP'
  | 'SET_1'
  | 'SET_2'
  | 'SET_3'
  | 'TIEBREAK'
  | 'CHANGEOVER'
  | 'UNKNOWN';

export type SignalName =
  | 'recovery_latency_ms'
  | 'serve_toss_variance_cm'
  | 'ritual_entropy_delta'
  | 'crouch_depth_degradation_deg'
  | 'baseline_retreat_distance_m'
  | 'lateral_work_rate'
  | 'split_step_latency_ms';

export type FallbackMode = 'ankle' | 'knee' | 'hip';

export type TransitionReason = 'kinematic' | 'match_coupling' | 'initial';

export type WidgetKind =
  | 'PlayerNameplate'
  | 'SignalBar'
  | 'MomentumMeter'
  | 'PredictiveOverlay'
  | 'TossTracer'
  | 'FootworkHeatmap';

export type WidgetSlot =
  | 'top-left'
  | 'top-right'
  | 'top-center'
  | 'right-1'
  | 'right-2'
  | 'right-3'
  | 'right-4'
  | 'center-overlay'
  | 'bottom';

// ──────────────────────────── COCO-17 keypoint layout ────────────────────────────

/**
 * COCO 17-keypoint order — MUST match backend.db.schema.COCO_KEYPOINTS.
 * Used to index into PlayerDetection.keypoints_xyn and confidence arrays.
 */
export const COCO_KEYPOINTS = [
  'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
  'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
  'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
  'left_knee', 'right_knee', 'left_ankle', 'right_ankle',
] as const;

export type CocoKeypointName = (typeof COCO_KEYPOINTS)[number];

/**
 * Connectivity for drawing the skeleton as line segments.
 * Each tuple is [from_index, to_index] into the 17-keypoint array.
 * Matches the canonical COCO pose skeleton used by Ultralytics.
 */
export const COCO_SKELETON_EDGES: ReadonlyArray<[number, number]> = [
  // Head
  [0, 1], [0, 2], [1, 3], [2, 4],
  // Torso
  [5, 6], [5, 11], [6, 12], [11, 12],
  // Arms
  [5, 7], [7, 9], [6, 8], [8, 10],
  // Legs
  [11, 13], [13, 15], [12, 14], [14, 16],
];

// ──────────────────────────── Core records ────────────────────────────

/**
 * One player's detection for a single frame.
 *
 * `keypoints_xyn` is an array of 17 [x, y] pairs in NORMALIZED [0, 1] image coords.
 * `confidence` is 17 floats in [0, 1].
 * `feet_mid_m` is the robust foot point projected into COURT METERS (may be null
 * when the foot-fallback chain can't produce a reliable point).
 */
export interface PlayerDetection {
  player: PlayerSide;
  keypoints_xyn: ReadonlyArray<readonly [number, number]>;
  confidence: ReadonlyArray<number>;
  bbox_conf: number;
  feet_mid_xyn: readonly [number, number] | null;
  feet_mid_m: readonly [number, number] | null;
  fallback_mode: FallbackMode;
}

/**
 * Per-frame keypoints for both players. `player_a` / `player_b` may be null
 * on occlusion or assignment failure.
 */
export interface FrameKeypoints {
  t_ms: number;
  frame_idx: number;
  player_a: PlayerDetection | null;
  player_b: PlayerDetection | null;
}

export interface SignalSample {
  timestamp_ms: number;
  match_id: string;
  player: PlayerSide;
  signal_name: SignalName;
  value: number | null;
  baseline_z_score: number | null;
  state: PlayerState;
}

export interface AnomalyEvent {
  event_id: string;
  timestamp_ms: number;
  match_id: string;
  player: PlayerSide;
  signal_name: SignalName;
  value: number;
  baseline_mean: number;
  baseline_std: number;
  z_score: number;
  severity: number;
}

export interface StateTransition {
  timestamp_ms: number;
  player: PlayerSide;
  from_state: PlayerState;
  to_state: PlayerState;
  reason: TransitionReason;
}

// ──────────────────────────── Opus outputs ────────────────────────────

export interface CoachInsight {
  insight_id: string;
  timestamp_ms: number;
  match_id: string;
  thinking: string | null;
  commentary: string;
  // tool_calls is free-form JSON on the backend side; we type it as unknown[] on the frontend.
  tool_calls: ReadonlyArray<unknown>;
  input_tokens: number;
  output_tokens: number;
  cache_read_tokens: number;
  cache_creation_tokens: number;
}

export interface HUDWidgetSpec {
  widget: WidgetKind;
  slot: WidgetSlot;
  // Widget-specific props — free-form dict on the backend; kept loose here and
  // narrowed at the widget component boundary.
  props: Record<string, unknown>;
}

export interface HUDLayoutSpec {
  layout_id: string;
  timestamp_ms: number;
  reason: string;
  widgets: ReadonlyArray<HUDWidgetSpec>;
  valid_until_ms: number;
}

export interface NarratorBeat {
  beat_id: string;
  timestamp_ms: number;
  match_id: string;
  text: string;
  input_tokens: number;
  output_tokens: number;
}

// ──────────────────────────── Match metadata ────────────────────────────

export interface MatchMeta {
  match_id: string;
  clip_sha256: string;
  clip_fps: number;
  duration_ms: number;
  width: number;
  height: number;
  player_a: string;
  player_b: string;
  court_corners_json: string;
}

// ──────────────────────────── Full match_data.json payload ────────────────────────────

/**
 * Top-level shape of the file at `/match_data/<match_id>.json`.
 * Matches `backend/db/writer.py:_MatchData` exactly.
 *
 * The engine loads this ONCE into a `useRef` at mount and never re-reads it —
 * keypoints are too high-frequency to live in React state.
 */
export interface MatchData {
  meta: MatchMeta;
  keypoints: ReadonlyArray<FrameKeypoints>;
  signals: ReadonlyArray<SignalSample>;
  anomalies: ReadonlyArray<AnomalyEvent>;
  coach_insights: ReadonlyArray<CoachInsight>;
  narrator_beats: ReadonlyArray<NarratorBeat>;
  hud_layouts: ReadonlyArray<HUDLayoutSpec>;
  transitions: ReadonlyArray<StateTransition>;
}

// ──────────────────────────── Multi-Agent Trace (PATTERN-056) ────────────────────────────
//
// Mirrors `backend/db/schema.py::AgentTrace`. Discriminated union on `kind`
// lets the Orchestration Console narrow safely at render time.

export interface TraceThinking {
  kind: 'thinking';
  t_ms: number;
  content: string;
}
export interface TraceToolCall {
  kind: 'tool_call';
  t_ms: number;
  tool_name: string;
  input_json: string;
}
export interface TraceToolResult {
  kind: 'tool_result';
  t_ms: number;
  tool_name: string;
  output_json: string;
  is_error: boolean;
}
export interface TraceText {
  kind: 'text';
  t_ms: number;
  content: string;
}
export interface TraceHandoff {
  kind: 'handoff';
  t_ms: number;
  from_agent: string;
  to_agent: string;
  payload_summary: string;
}
export type TraceEvent =
  | TraceThinking
  | TraceToolCall
  | TraceToolResult
  | TraceText
  | TraceHandoff;

export interface AgentStep {
  agent_name: string;
  agent_role: string;
  started_at_ms: number;
  completed_at_ms: number;
  events: ReadonlyArray<TraceEvent>;
}

export interface AgentTrace {
  match_id: string;
  generated_at: string;
  committee_goal: string;
  steps: ReadonlyArray<AgentStep>;
  final_report_markdown: string;
  total_compute_ms: number;
  /**
   * Match-timecode anchor: [start_ms, end_ms] of the match-time window the
   * committee analyzed. Drives the "Analyzing match X:XX–Y:YY" chip in the
   * Orchestration Console header (lets judges map the swarm's reasoning to
   * the video timecode they're watching). Null when no signals were analyzed.
   * Optional for backwards-compat with pre-Phase-4-audit traces.
   */
  match_time_range_ms?: [number, number] | null;
}
