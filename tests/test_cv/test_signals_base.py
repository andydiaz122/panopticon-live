"""Tests for backend/cv/signals/base.py — BaseSignalExtractor ABC contract.

Enforces USER-CORRECTION-013 (Symmetric Extractor API + Dependency Injection):
- __init__ accepts target_player + dependencies: dict
- ingest takes (target_state, opponent_state, target_kalman, opponent_kalman)
- flush identifies the player from target_player (no arg needed beyond t_ms)

Also enforces USER-CORRECTION-015 contract groundwork:
- Every concrete signal inherits from this ABC
- Reset is a default no-op (subclasses override if they have state)

Written FIRST per TDD discipline (Citadel-level).
"""

from __future__ import annotations

import pytest

from backend.cv.signals.base import BaseSignalExtractor
from backend.db.schema import FrameKeypoints, PlayerDetection

# ──────────────────────────── Minimal concrete subclass for testing ────────────────────────────


class _EchoExtractor(BaseSignalExtractor):
    """Minimal concrete subclass: counts ingest calls, records last inputs."""

    signal_name = "recovery_latency_ms"
    required_state = ("ACTIVE_RALLY",)

    def __init__(self, target_player, dependencies):
        super().__init__(target_player, dependencies)
        self.ingest_calls = 0
        self.last_target_state = None
        self.last_opponent_state = None
        self.last_target_kalman = None
        self.last_opponent_kalman = None
        self.last_t_ms = None
        self.reset_called = False

    def ingest(
        self,
        frame,
        target_state,
        opponent_state,
        target_kalman,
        opponent_kalman,
        t_ms,
    ):
        self.ingest_calls += 1
        self.last_target_state = target_state
        self.last_opponent_state = opponent_state
        self.last_target_kalman = target_kalman
        self.last_opponent_kalman = opponent_kalman
        self.last_t_ms = t_ms

    def flush(self, t_ms):
        return None  # no samples in this minimal stub

    def reset(self):
        super().reset()
        self.reset_called = True
        self.ingest_calls = 0


# ──────────────────────────── ABC contract tests ────────────────────────────


def test_abc_cannot_be_instantiated_directly() -> None:
    """BaseSignalExtractor is abstract: instantiating raises TypeError."""
    with pytest.raises(TypeError):
        BaseSignalExtractor(target_player="A", dependencies={})  # type: ignore[abstract]


def test_subclass_must_implement_ingest_and_flush() -> None:
    """Subclass missing abstract methods cannot be instantiated."""

    class _Incomplete(BaseSignalExtractor):
        signal_name = "recovery_latency_ms"
        required_state = ("ACTIVE_RALLY",)
        # missing ingest + flush

    with pytest.raises(TypeError):
        _Incomplete(target_player="A", dependencies={})  # type: ignore[abstract]


def test_target_player_routing() -> None:
    """Separate instances for A and B retain distinct target_player values."""
    a_ext = _EchoExtractor(target_player="A", dependencies={})
    b_ext = _EchoExtractor(target_player="B", dependencies={})
    assert a_ext.target_player == "A"
    assert b_ext.target_player == "B"
    assert a_ext is not b_ext


def test_dependencies_injection_stores_dict() -> None:
    """Dependencies dict is stored on self.deps for subclass access."""
    mock_court_mapper = object()  # opaque sentinel — real type tested in compiler integration
    deps = {"court_mapper": mock_court_mapper, "clip_fps": 30.0}
    ext = _EchoExtractor(target_player="A", dependencies=deps)
    assert ext.deps["court_mapper"] is mock_court_mapper
    assert ext.deps["clip_fps"] == 30.0


def test_dependencies_empty_dict_is_allowed() -> None:
    """Extractors with no dependencies get an empty dict without error."""
    ext = _EchoExtractor(target_player="A", dependencies={})
    assert ext.deps == {}


def test_reset_default_noop_on_base_class() -> None:
    """reset() on the base class is a no-op (doesn't raise)."""

    class _MinimalReset(BaseSignalExtractor):
        signal_name = "recovery_latency_ms"
        required_state = ("ACTIVE_RALLY",)

        def ingest(self, frame, target_state, opponent_state, target_kalman, opponent_kalman, t_ms):
            pass

        def flush(self, t_ms):
            return None

    ext = _MinimalReset(target_player="A", dependencies={})
    ext.reset()  # should not raise


def test_reset_subclass_override_is_invoked() -> None:
    """Subclasses that override reset() can clear their own state."""
    ext = _EchoExtractor(target_player="A", dependencies={})
    ext.ingest_calls = 5
    ext.reset()
    assert ext.reset_called is True
    assert ext.ingest_calls == 0


# ──────────────────────────── Symmetric ingest API tests ────────────────────────────


def _make_stub_frame(t_ms: int = 0) -> FrameKeypoints:
    """Build a FrameKeypoints with both players present for testing."""
    stub_keypoints = [(0.5, 0.5)] * 17
    stub_conf = [0.9] * 17
    detection_a = PlayerDetection(
        player="A",
        keypoints_xyn=stub_keypoints,
        confidence=stub_conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.9),
        feet_mid_m=(4.0, 15.0),
        fallback_mode="ankle",
    )
    detection_b = PlayerDetection(
        player="B",
        keypoints_xyn=stub_keypoints,
        confidence=stub_conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.3),
        feet_mid_m=(4.0, 8.0),
        fallback_mode="ankle",
    )
    return FrameKeypoints(t_ms=t_ms, frame_idx=t_ms // 33, player_a=detection_a, player_b=detection_b)


def test_ingest_receives_target_and_opponent_kalman_symmetrically() -> None:
    """Ingest receives target_kalman + opponent_kalman — routing handled by compiler."""
    ext_a = _EchoExtractor(target_player="A", dependencies={})
    ext_b = _EchoExtractor(target_player="B", dependencies={})

    kalman_a = (4.0, 15.0, 0.5, 0.0)   # (x_m, y_m, vx, vy)
    kalman_b = (4.0, 8.0, -0.5, 0.0)
    frame = _make_stub_frame(t_ms=100)

    # Compiler passes target/opponent consistent with each extractor's identity
    ext_a.ingest(
        frame=frame,
        target_state="ACTIVE_RALLY",
        opponent_state="PRE_SERVE_RITUAL",
        target_kalman=kalman_a,
        opponent_kalman=kalman_b,
        t_ms=100,
    )
    ext_b.ingest(
        frame=frame,
        target_state="PRE_SERVE_RITUAL",
        opponent_state="ACTIVE_RALLY",
        target_kalman=kalman_b,
        opponent_kalman=kalman_a,
        t_ms=100,
    )

    assert ext_a.last_target_kalman == kalman_a
    assert ext_a.last_opponent_kalman == kalman_b
    assert ext_a.last_target_state == "ACTIVE_RALLY"
    assert ext_a.last_opponent_state == "PRE_SERVE_RITUAL"

    assert ext_b.last_target_kalman == kalman_b
    assert ext_b.last_opponent_kalman == kalman_a
    assert ext_b.last_target_state == "PRE_SERVE_RITUAL"
    assert ext_b.last_opponent_state == "ACTIVE_RALLY"


def test_ingest_accepts_none_kalman_for_occluded_frame() -> None:
    """Kalman may be None during occlusion; extractor must accept without raising."""
    ext = _EchoExtractor(target_player="A", dependencies={})
    frame = _make_stub_frame(t_ms=200)

    ext.ingest(
        frame=frame,
        target_state="ACTIVE_RALLY",
        opponent_state="ACTIVE_RALLY",
        target_kalman=None,
        opponent_kalman=None,
        t_ms=200,
    )
    assert ext.last_target_kalman is None
    assert ext.last_opponent_kalman is None


# ──────────────────────────── Class-level metadata ────────────────────────────


def test_signal_name_is_class_attribute() -> None:
    """signal_name is class-level — the compiler uses it to route SignalSamples."""
    assert _EchoExtractor.signal_name == "recovery_latency_ms"
    # Instance also sees it
    ext = _EchoExtractor(target_player="A", dependencies={})
    assert ext.signal_name == "recovery_latency_ms"


def test_required_state_is_tuple() -> None:
    """required_state is an immutable tuple (not list) so compilers can hash it."""
    assert isinstance(_EchoExtractor.required_state, tuple)
    assert _EchoExtractor.required_state == ("ACTIVE_RALLY",)


def test_required_state_can_have_multiple_entries() -> None:
    """A signal may fire in more than one state (e.g., split_step_latency spans two)."""

    class _MultiState(BaseSignalExtractor):
        signal_name = "split_step_latency_ms"
        required_state = ("PRE_SERVE_RITUAL", "ACTIVE_RALLY")

        def ingest(self, frame, target_state, opponent_state, target_kalman, opponent_kalman, t_ms):
            pass

        def flush(self, t_ms):
            return None

    assert _MultiState.required_state == ("PRE_SERVE_RITUAL", "ACTIVE_RALLY")
