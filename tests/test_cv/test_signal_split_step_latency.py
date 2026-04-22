"""Tests for backend/cv/signals/split_step_latency.py — returner reaction latency.

Per USER-CORRECTION-019: DO NOT hunt raw keypoint wrist-peak velocity (noisy derivative).
Use MatchStateMachine transitions as smoothed proxies:
- opponent PRE_SERVE_RITUAL → ACTIVE_RALLY  ≈ serve contact (server committed)
- target   PRE_SERVE_RITUAL → ACTIVE_RALLY  ≈ returner commits to moving

split_step_latency_ms = target_entered_t_ms - opponent_entered_t_ms

Server-side (target transitions first) → None (not a returner event).
Only emitted when BOTH transitioned in the same rally window AND opponent was first.

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import pytest

from backend.cv.signals.split_step_latency import SplitStepLatency
from backend.db.schema import FrameKeypoints, PlayerDetection, SignalSample

# ──────────────────────────── Stub frame ────────────────────────────


def _stub_frame(t_ms: int = 0) -> FrameKeypoints:
    """Minimal FrameKeypoints; signal is state-only, keypoint content is irrelevant."""
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


def simulate_state_sequence(
    ext: SplitStepLatency,
    sequence: list[tuple[str, str, int]],
) -> None:
    """Feed (target_state, opponent_state, t_ms) tuples into ingest().

    Both kalman args are None — this signal is state-only.
    """
    for target_state, opponent_state, t_ms in sequence:
        ext.ingest(
            frame=_stub_frame(t_ms),
            target_state=target_state,  # type: ignore[arg-type]
            opponent_state=opponent_state,  # type: ignore[arg-type]
            target_kalman=None,
            opponent_kalman=None,
            t_ms=t_ms,
        )


# ──────────────────────────── Construction / class metadata ────────────────────────────


def test_class_attributes_signal_name_and_required_state() -> None:
    """Class-level signal_name and required_state wired for compiler routing."""
    assert SplitStepLatency.signal_name == "split_step_latency_ms"
    assert SplitStepLatency.required_state == ("PRE_SERVE_RITUAL", "ACTIVE_RALLY")
    assert isinstance(SplitStepLatency.required_state, tuple)


# ──────────────────────────── Returner-side (emits sample) ────────────────────────────


def test_returner_case_opponent_transitions_first_emits_latency() -> None:
    """Opponent PRE_SERVE_RITUAL → ACTIVE_RALLY at t=133, target at t=300 → latency 167."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            # Both in PRE_SERVE_RITUAL; opponent transitions first
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 133),  # opponent (server) commits
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 200),  # still tracking
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),  # target (returner) commits
        ],
    )
    sample = ext.flush(t_ms=400)
    assert isinstance(sample, SignalSample)
    assert sample.value == pytest.approx(167.0, abs=1e-12)
    assert sample.signal_name == "split_step_latency_ms"
    assert sample.player == "A"
    assert sample.timestamp_ms == 400
    assert sample.match_id == "m1"


def test_both_transitions_at_identical_t_ms_emits_zero() -> None:
    """Edge case: simultaneous transitions → latency 0.0 (still valid)."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 200),  # both transition same tick
        ],
    )
    sample = ext.flush(t_ms=300)
    assert sample is not None
    assert sample.value == pytest.approx(0.0, abs=1e-12)


# ──────────────────────────── Server-side / partial sequences (returns None) ────────────────────────────


def test_server_side_target_transitions_first_returns_none() -> None:
    """Target transitions first → target IS the server, not returner. None."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("ACTIVE_RALLY", "PRE_SERVE_RITUAL", 100),  # target commits first (server)
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),  # opponent later
        ],
    )
    assert ext.flush(t_ms=400) is None


def test_only_opponent_transitions_returns_none() -> None:
    """Opponent transitions to ACTIVE_RALLY but target never does → None."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 200),
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 300),
        ],
    )
    assert ext.flush(t_ms=400) is None


def test_only_target_transitions_returns_none() -> None:
    """Target transitions but opponent never does → None (no server event detected)."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("ACTIVE_RALLY", "PRE_SERVE_RITUAL", 200),
            ("ACTIVE_RALLY", "PRE_SERVE_RITUAL", 300),
        ],
    )
    assert ext.flush(t_ms=400) is None


def test_neither_transitions_returns_none() -> None:
    """Both stay in PRE_SERVE_RITUAL → no transitions → None."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 200),
        ],
    )
    assert ext.flush(t_ms=300) is None


# ──────────────────────────── Flush / reset semantics ────────────────────────────


def test_after_flush_both_timestamps_reset() -> None:
    """After a successful emit, internal timestamps are cleared; next flush returns None."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 133),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),
        ],
    )
    first = ext.flush(t_ms=400)
    assert first is not None
    # No new transitions → second flush must be None
    second = ext.flush(t_ms=500)
    assert second is None


def test_reset_clears_tracked_timestamps() -> None:
    """reset() wipes timestamps — even with a pending returner-case transition."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 133),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),
        ],
    )
    ext.reset()
    assert ext.flush(t_ms=400) is None


# ──────────────────────────── USER-CORRECTION-022: Fail-fast dependency lookup ────────────────────────────


def test_missing_match_id_raises_keyerror_on_flush() -> None:
    """With a valid returner-case pending emit and no 'match_id' in deps, flush raises KeyError."""
    ext = SplitStepLatency(target_player="A", dependencies={})  # no match_id
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 133),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),
        ],
    )
    with pytest.raises(KeyError, match="match_id"):
        ext.flush(t_ms=400)
