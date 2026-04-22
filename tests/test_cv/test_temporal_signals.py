"""Tests for backend/cv/temporal_signals.py — RollingBounceDetector.

Enforces:
- USER-CORRECTION-013: detector runs BEFORE MatchStateMachine (continuous rolling primitive)
- USER-CORRECTION-012: relative kinematics (wrist_y - hip_y) rejects camera pan/tilt
- USER-CORRECTION-014: np.nan + np.nanvar/nanmax/nanmin on occlusion; ambidextrous wrist selection
- USER-CORRECTION-015: zero-variance guard prevents division-by-zero in downstream spectral math

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import math

from backend.cv.temporal_signals import RollingBounceDetector

# ──────────────────────────── Helpers ────────────────────────────


def _ingest_sine(
    det: RollingBounceDetector,
    player: str,
    frequency_hz: float,
    amplitude: float = 0.05,
    fps: float = 30.0,
    frames: int = 90,
    hip_y: float = 0.65,
    hip_conf: float = 0.9,
    wrist_conf: float = 0.9,
) -> None:
    """Inject a sinusoid in wrist_y around a mean, with a stationary hip."""
    for i in range(frames):
        t = i / fps
        wrist_y = 0.40 + amplitude * math.sin(2 * math.pi * frequency_hz * t)
        det.ingest_player_frame(
            buffer_key=player,
            left_wrist_y=wrist_y,
            left_wrist_conf=wrist_conf,
            right_wrist_y=None,
            right_wrist_conf=None,
            hip_y=hip_y,
            hip_conf=hip_conf,
        )


def _ingest_constant(det: RollingBounceDetector, player: str, frames: int = 90) -> None:
    for _ in range(frames):
        det.ingest_player_frame(
            buffer_key=player,
            left_wrist_y=0.40, left_wrist_conf=0.9,
            right_wrist_y=None, right_wrist_conf=None,
            hip_y=0.65, hip_conf=0.9,
        )


# ──────────────────────────── Basic detection ────────────────────────────


def test_synthetic_bounce_detected_on_relative_y() -> None:
    """A 2 Hz sine in (wrist_y - hip_y) with adequate amplitude triggers a_bounce=True."""
    det = RollingBounceDetector(fps=30.0)
    _ingest_sine(det, "A", frequency_hz=2.0, amplitude=0.05)
    a, b = det.evaluate()
    assert a is True, "2 Hz bounce in relative_y should be detected"
    assert b is False, "B buffer empty → no bounce"


def test_no_bounce_when_static() -> None:
    """Constant relative_y → variance near zero → no bounce (via variance floor guard)."""
    det = RollingBounceDetector(fps=30.0)
    _ingest_constant(det, "A")
    a, b = det.evaluate()
    assert a is False
    assert b is False


def test_buffer_below_min_returns_false() -> None:
    """Fewer than MIN_SAMPLES → cannot decide → False."""
    det = RollingBounceDetector(fps=30.0)
    for _ in range(5):   # below MIN_SAMPLES (10)
        det.ingest_player_frame(
            buffer_key="A",
            left_wrist_y=0.40, left_wrist_conf=0.9,
            right_wrist_y=None, right_wrist_conf=None,
            hip_y=0.65, hip_conf=0.9,
        )
    assert det.evaluate() == (False, False)


def test_per_player_independence() -> None:
    """A bouncing, B static → only a_bounce=True."""
    det = RollingBounceDetector(fps=30.0)
    _ingest_sine(det, "A", frequency_hz=2.0)
    _ingest_constant(det, "B")
    a, b = det.evaluate()
    assert a is True
    assert b is False


# ──────────────────────────── Frequency-band selectivity ────────────────────────────


def test_too_slow_rejected() -> None:
    """0.2 Hz is below tennis bounce cadence → False."""
    det = RollingBounceDetector(fps=30.0)
    _ingest_sine(det, "A", frequency_hz=0.2, frames=180)
    a, _ = det.evaluate()
    assert a is False, "0.2 Hz oscillation must be rejected as too slow"


def test_too_fast_rejected() -> None:
    """10 Hz is above tennis bounce cadence (hand tremor) → False."""
    det = RollingBounceDetector(fps=30.0)
    _ingest_sine(det, "A", frequency_hz=10.0, amplitude=0.05)
    a, _ = det.evaluate()
    assert a is False, "10 Hz oscillation must be rejected as too fast"


# ──────────────────────────── USER-CORRECTION-012: Relative kinematics ────────────────────────────


def test_camera_pan_rejected_via_relative_kinematics() -> None:
    """Both wrist_y AND hip_y drift linearly in lockstep (camera tilt) → relative_y is constant → no bounce."""
    det = RollingBounceDetector(fps=30.0)
    for i in range(90):
        # Simulate camera tilting: wrist and hip both drift up linearly, but their difference is constant
        drift = i * 0.001
        det.ingest_player_frame(
            buffer_key="A",
            left_wrist_y=0.40 + drift,
            left_wrist_conf=0.9,
            right_wrist_y=None,
            right_wrist_conf=None,
            hip_y=0.65 + drift,
            hip_conf=0.9,
        )
    a, _ = det.evaluate()
    assert a is False, (
        "USER-CORRECTION-012: Camera pan causes raw wrist_y to drift, but relative_y "
        "(wrist_y - hip_y) is invariant. Detector must see NO bounce here."
    )


def test_camera_pan_with_superposed_bounce_still_detects() -> None:
    """Camera pans while player actually bounces → bounce still detected via relative-y."""
    det = RollingBounceDetector(fps=30.0)
    for i in range(90):
        t = i / 30.0
        drift = i * 0.001
        bounce = 0.05 * math.sin(2 * math.pi * 2.0 * t)
        det.ingest_player_frame(
            buffer_key="A",
            left_wrist_y=0.40 + drift + bounce,
            left_wrist_conf=0.9,
            right_wrist_y=None,
            right_wrist_conf=None,
            hip_y=0.65 + drift,   # pans with the camera, does NOT bounce
            hip_conf=0.9,
        )
    a, _ = det.evaluate()
    assert a is True, "True bounce under camera pan must survive via relative kinematics"


# ──────────────────────────── USER-CORRECTION-014: Null-safety + ambidextrous ────────────────────────────


def test_occlusion_nan_does_not_crash() -> None:
    """Passing None wrists repeatedly causes np.nan ingest — evaluate() must not raise."""
    det = RollingBounceDetector(fps=30.0)
    for _ in range(20):
        det.ingest_player_frame(
            buffer_key="A",
            left_wrist_y=None, left_wrist_conf=None,
            right_wrist_y=None, right_wrist_conf=None,
            hip_y=0.65, hip_conf=0.9,
        )
    # Must not raise TypeError; must return False (no data to decide)
    a, _ = det.evaluate()
    assert a is False


def test_low_confidence_wrist_treated_as_missing() -> None:
    """Wrists below WRIST_CONF_THRESHOLD are ignored (treated as occluded)."""
    det = RollingBounceDetector(fps=30.0)
    # Send a bouncing sine but at confidence 0.1 (below threshold 0.3)
    for i in range(90):
        t = i / 30.0
        wrist_y = 0.40 + 0.05 * math.sin(2 * math.pi * 2.0 * t)
        det.ingest_player_frame(
            buffer_key="A",
            left_wrist_y=wrist_y, left_wrist_conf=0.1,   # low conf
            right_wrist_y=None, right_wrist_conf=None,
            hip_y=0.65, hip_conf=0.9,
        )
    a, _ = det.evaluate()
    assert a is False, "Low-confidence wrists must be ignored → no bounce signal"


def test_ambidextrous_wrist_selection_right_hand() -> None:
    """Left wrist occluded, right wrist bouncing with confidence → bounce detected."""
    det = RollingBounceDetector(fps=30.0)
    for i in range(90):
        t = i / 30.0
        right_y = 0.40 + 0.05 * math.sin(2 * math.pi * 2.0 * t)
        det.ingest_player_frame(
            buffer_key="A",
            left_wrist_y=None, left_wrist_conf=None,
            right_wrist_y=right_y, right_wrist_conf=0.9,
            hip_y=0.65, hip_conf=0.9,
        )
    a, _ = det.evaluate()
    assert a is True, "Right-hand server: right wrist bouncing must be detected"


def test_hip_occlusion_yields_nan_rejection() -> None:
    """Hip occluded → cannot compute relative_y → NaN in buffer → no bounce."""
    det = RollingBounceDetector(fps=30.0)
    for i in range(90):
        t = i / 30.0
        wrist_y = 0.40 + 0.05 * math.sin(2 * math.pi * 2.0 * t)
        det.ingest_player_frame(
            buffer_key="A",
            left_wrist_y=wrist_y, left_wrist_conf=0.9,
            right_wrist_y=None, right_wrist_conf=None,
            hip_y=None, hip_conf=None,   # hip occluded
        )
    a, _ = det.evaluate()
    assert a is False, "Hip occlusion prevents relative-y computation → no bounce"


# ──────────────────────────── USER-CORRECTION-015: Zero-variance guard ────────────────────────────


def test_zero_variance_returns_no_bounce() -> None:
    """Constant relative_y (variance well below 1e-5 floor) → no bounce."""
    det = RollingBounceDetector(fps=30.0)
    _ingest_constant(det, "A", frames=90)
    a, _ = det.evaluate()
    assert a is False


def test_all_nan_buffer_returns_no_bounce() -> None:
    """All-NaN buffer → nanvar is nan → guard triggers → no crash."""
    det = RollingBounceDetector(fps=30.0)
    for _ in range(90):
        det.ingest_player_frame(
            buffer_key="A",
            left_wrist_y=None, left_wrist_conf=None,
            right_wrist_y=None, right_wrist_conf=None,
            hip_y=None, hip_conf=None,
        )
    a, _ = det.evaluate()
    assert a is False


# ──────────────────────────── Ordering contract ────────────────────────────


def test_detector_evaluate_is_idempotent() -> None:
    """Multiple evaluate() calls between ingests return the same decision."""
    det = RollingBounceDetector(fps=30.0)
    _ingest_sine(det, "A", frequency_hz=2.0)
    first = det.evaluate()
    second = det.evaluate()
    third = det.evaluate()
    assert first == second == third


def test_buffer_window_caps_at_window_frames() -> None:
    """Buffer is a deque with maxlen WINDOW_FRAMES — older samples drop out."""
    det = RollingBounceDetector(fps=30.0)
    # Fill with bounces, then fill with constants → eventually constants dominate
    _ingest_sine(det, "A", frequency_hz=2.0, frames=det.WINDOW_FRAMES)
    assert det.evaluate()[0] is True
    _ingest_constant(det, "A", frames=det.WINDOW_FRAMES + 5)
    assert det.evaluate()[0] is False


# ──────────────────────────── Parameter constants ────────────────────────────


def test_class_constants_in_range() -> None:
    """Sanity-check tunables are within physically reasonable bounds."""
    lo, hi = RollingBounceDetector.BOUNCE_PERIOD_RANGE_S
    assert 0.1 < lo < hi < 3.0
    assert RollingBounceDetector.WINDOW_FRAMES >= 30
    assert 1e-9 < RollingBounceDetector.VARIANCE_FLOOR < 1e-3
    assert 0.0 < RollingBounceDetector.WRIST_CONF_THRESHOLD < 1.0
