"""Consolidated kinematic + pose-confidence thresholds for the PANOPTICON CV pipeline.

PATTERN-057 (Threshold Tuning Debt): whenever upstream signal processing changes
(Kalman variant, SG filter, pose model, RTS on/off), every downstream absolute
threshold incurs tuning debt. Keeping them in ONE typed, frozen module means
re-tuning is a single-file diff instead of a grep-and-edit safari through the
extractor suite.

Two distinct threshold classes — do NOT conflate them:

  1. KINEMATIC thresholds — gate on Kalman-derived velocities (m/s). AFFECTED
     by RTS smoothing (amplitude-compressed vs forward-only). Re-tune whenever
     the smoother changes. Owners: MatchStateMachine, recovery_latency.

  2. POSE-CONFIDENCE thresholds — gate on raw YOLO keypoint confidence [0, 1].
     UNAFFECTED by Kalman/RTS (they operate on the pose-inference layer, not
     the tracker). Re-tune only when the pose model itself changes (e.g.,
     YOLO11m → YOLO11x, MediaPipe swap). Owners: signal extractors.

See docs in each constant for provenance and tuning rationale.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# ──────────────────────────── Kinematic thresholds (RTS-affected) ────────────────────────────


@dataclass(frozen=True)
class KinematicThresholds:
    """Velocity thresholds gating state-machine transitions + velocity-dependent signals.

    Under the PRE-RTS forward-only Kalman regime (pre-2026-04-23), these were
    tuned to absorb ±0.05-0.10 m/s jitter from YOLO keypoint flutter. Under the
    POST-RTS regime (3-Pass DAG, PATTERN-055), the noise floor drops ~87% per
    the `test_rts_smoothed_velocity_has_lower_jitter_than_forward_only` measurement.
    This means some thresholds CAN be lowered without introducing false positives
    from noise — but doing so REQUIRES empirical histogram evidence from a real
    post-RTS precompute run (not synthetic-path guessing; see PATTERN-057).

    The values below are the PRE-RTS defaults preserved verbatim. The field
    `post_rts_calibrated` documents whether the value has been empirically
    re-tuned on real post-RTS telemetry. Flip to True when you've histogrammed
    real amplitudes and confirmed the new value.
    """

    # FSM entry-to-rally: sustained-motion gate for PRE_SERVE_RITUAL → ACTIVE_RALLY
    # Pre-RTS rationale: "above walking-start but well under any tennis-motion peak"
    active_rally_speed_mps: float = 0.2

    # FSM exit-to-dead-time: player is essentially stationary
    # Pre-RTS rationale: "absorbs residual YOLO jitter during true rest"
    dead_time_speed_mps: float = 0.05

    # Recovery-latency trigger: movement-onset detection after a shot
    # Pre-RTS rationale: "reliably above walking pace, catches the stride burst"
    recovery_speed_mps: float = 0.5

    # Frame-count debouncers (NOT velocity; structural gates on noise bursts)
    consecutive_frames_to_rally: int = 5
    consecutive_frames_to_dead_time: int = 15

    post_rts_calibrated: bool = False
    """True once values have been empirically histogrammed on a post-RTS run."""


# Single canonical instance. Import THIS, not the class, to prevent drift.
KINEMATIC: Final[KinematicThresholds] = KinematicThresholds()


# ──────────────────────────── Pose-confidence thresholds (RTS-invariant) ────────────────────────────


@dataclass(frozen=True)
class PoseConfidenceThresholds:
    """Thresholds gating raw YOLO keypoint confidence scores [0, 1].

    Unaffected by Kalman or RTS — these live at the pose-inference layer.
    Re-tune ONLY when the pose model changes (YOLO variant swap, MediaPipe,
    OpenPose). Current values calibrated against YOLO11m-Pose at conf=0.001,
    imgsz=1280.
    """

    keypoint_confidence_min: float = 0.3
    """Generic keypoint visibility gate. Used by signal extractors that
    aggregate wrist/hip/ankle/shoulder confidence before computing."""


POSE_CONF: Final[PoseConfidenceThresholds] = PoseConfidenceThresholds()


# ──────────────────────────── Amplitude / numerical guards (algo-invariant) ────────────────────────────


@dataclass(frozen=True)
class NumericalGuards:
    """Variance floors + normalized-amplitude thresholds. These are numerical-
    stability constants, not calibration targets. Do NOT re-tune in PATTERN-057
    sweeps — they'll fire correctly under any signal-processing upgrade.
    """

    variance_floor: float = 1e-5
    """Minimum variance below which std-dev computations return None
    (USER-CORRECTION-015)."""

    torso_collapse_floor: float = 1e-5
    """Minimum torso-length denominator to prevent divide-by-zero in
    crouch-depth normalization."""

    serve_toss_amplitude_floor: float = 0.05
    """Minimum normalized wrist-y amplitude to emit a serve-toss-variance
    signal. Filters out false positives from fully-occluded noise."""

    bounce_amplitude_rel: float = 0.02
    """Minimum relative amplitude in the RollingBounceDetector window.
    Below this, the spectral-period check cannot distinguish bounce from noise."""


NUMERIC: Final[NumericalGuards] = NumericalGuards()
