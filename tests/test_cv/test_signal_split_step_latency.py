"""Tests for backend/cv/signals/split_step_latency.py — PLAYER-A-ONLY reaction timing.

Post-GOTCHA-021 + USER-CORRECTION-025 (Founder Override #1, 2026-04-23):
The signal is now anchored ENTIRELY on Player A's own kinematic timeline.
Purged the Ghost Opponent dependency — the math no longer reads opponent_state.

New definition:
  split_step_latency_ms = (t_ms_player_a_entered_ACTIVE_RALLY)
                        - (t_ms_player_a_entered_PRE_SERVE_RITUAL)

Semantically: how long Player A spent in their pre-serve ritual before
committing to movement. Works uniformly whether Player A is server or returner —
the signal measures their own ritual-to-burst cadence regardless.

Player B's state is NEVER read. Player B may be fully occluded (GOTCHA-016,
DECISION-008) and this signal still fires correctly.

Written FIRST per TDD discipline — confirms the new contract before patching
the extractor.
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
    # Player B detection included but DELIBERATELY CONTAIN GARBAGE to prove the
    # extractor ignores it under the new Player-A-only contract.
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

    opponent_state values are INTENTIONALLY varied across tests to prove the
    extractor ignores them. Both kalman args are None.
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


# ──────────────────────────── Happy path: Player A's own ritual-to-burst ────────────────────────────


def test_ritual_to_burst_emits_latency_purely_from_target() -> None:
    """Target enters PRE at t=100, transitions PRE→ACTIVE at t=300 → latency 200 ms.

    Opponent state is in a completely different phase the whole time; must be IGNORED.
    """
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("DEAD_TIME", "ACTIVE_RALLY", 50),             # target not in PRE yet
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 100),     # target enters PRE
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 200),     # still in PRE
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),         # target commits → latency fires
        ],
    )
    sample = ext.flush(t_ms=400)
    assert isinstance(sample, SignalSample)
    assert sample.value == pytest.approx(200.0, abs=1e-12)
    assert sample.signal_name == "split_step_latency_ms"
    assert sample.player == "A"
    assert sample.timestamp_ms == 400
    assert sample.match_id == "m1"


def test_emits_regardless_of_opponent_state_even_if_occluded() -> None:
    """Opponent state is UNKNOWN the entire time (fully occluded — GOTCHA-016).
    Signal must STILL fire correctly off Player A's own timeline.
    """
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("DEAD_TIME", "UNKNOWN", 50),
            ("PRE_SERVE_RITUAL", "UNKNOWN", 150),
            ("ACTIVE_RALLY", "UNKNOWN", 450),
        ],
    )
    sample = ext.flush(t_ms=500)
    assert sample is not None
    assert sample.value == pytest.approx(300.0, abs=1e-12)


def test_emits_when_target_moves_before_opponent_server_side_case() -> None:
    """Old 'server-side' test: target transitions BEFORE opponent. Under the
    new Player-A-only contract, this STILL emits — we no longer drop server-side
    events. The signal captures Player A's ritual-to-burst cadence regardless of
    whether they're serving or returning.
    """
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("DEAD_TIME", "DEAD_TIME", 50),
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("ACTIVE_RALLY", "PRE_SERVE_RITUAL", 250),     # target first — old code dropped
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 400),         # opponent lags
        ],
    )
    sample = ext.flush(t_ms=500)
    assert sample is not None, "Server-side case MUST now emit (post-GOTCHA-021)"
    assert sample.value == pytest.approx(150.0, abs=1e-12)


# ──────────────────────────── None / gap cases ────────────────────────────


def test_target_never_enters_pre_serve_returns_none() -> None:
    """Target goes DEAD_TIME → ACTIVE_RALLY directly, skipping PRE_SERVE. Should emit None
    because we never observed a PRE entry to measure ritual duration from.
    """
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("DEAD_TIME", "DEAD_TIME", 100),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),
        ],
    )
    assert ext.flush(t_ms=400) is None


def test_target_stays_in_pre_serve_returns_none() -> None:
    """Target enters PRE but never transitions to ACTIVE → no latency computable."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 100),
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 200),
            ("PRE_SERVE_RITUAL", "ACTIVE_RALLY", 300),
        ],
    )
    assert ext.flush(t_ms=400) is None


def test_opponent_transitions_are_completely_irrelevant() -> None:
    """Opponent enters + exits ACTIVE_RALLY but target never touches PRE → None.
    Hard regression guard on the Ghost Opponent purge.
    """
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("DEAD_TIME", "PRE_SERVE_RITUAL", 100),
            ("DEAD_TIME", "ACTIVE_RALLY", 133),             # opponent serves
            ("DEAD_TIME", "ACTIVE_RALLY", 300),             # target still idle
            ("DEAD_TIME", "DEAD_TIME", 400),                # opponent done
        ],
    )
    assert ext.flush(t_ms=500) is None


def test_initial_active_rally_state_produces_no_spurious_latency() -> None:
    """First-observed target state is ACTIVE_RALLY (e.g., clip starts mid-rally).
    No PRE entry observed → no latency. Guards against a false 0.0 or huge value
    from an uninitialized timestamp.
    """
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 100),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 200),
        ],
    )
    assert ext.flush(t_ms=300) is None


# ──────────────────────────── Multi-rally cycling ────────────────────────────


def test_two_consecutive_rallies_each_emit_their_own_latency() -> None:
    """Rally 1: PRE at 100 → ACTIVE at 250 → latency 150.
    Rally 2: PRE at 500 → ACTIVE at 700 → latency 200.
    """
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 250),
        ],
    )
    first = ext.flush(t_ms=300)
    assert first is not None
    assert first.value == pytest.approx(150.0, abs=1e-12)

    simulate_state_sequence(
        ext,
        [
            ("DEAD_TIME", "DEAD_TIME", 400),
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 500),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 700),
        ],
    )
    second = ext.flush(t_ms=800)
    assert second is not None
    assert second.value == pytest.approx(200.0, abs=1e-12)


# ──────────────────────────── Flush / reset semantics ────────────────────────────


def test_after_flush_pending_latency_is_consumed() -> None:
    """After a successful emit, internal pending_latency is cleared; next flush returns None."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),
        ],
    )
    first = ext.flush(t_ms=400)
    assert first is not None
    second = ext.flush(t_ms=500)
    assert second is None


def test_reset_clears_tracked_state() -> None:
    """reset() wipes entered-PRE timestamp AND pending latency, even mid-ritual."""
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),
        ],
    )
    ext.reset()
    assert ext.flush(t_ms=400) is None


def test_reset_mid_pre_serve_prevents_future_emission() -> None:
    """If reset() fires while target is still in PRE (hasn't committed yet), the
    subsequent PRE→ACTIVE transition must NOT pick up the pre-reset timestamp.
    """
    ext = SplitStepLatency(target_player="A", dependencies={"match_id": "m1"})
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
        ],
    )
    ext.reset()
    simulate_state_sequence(
        ext,
        [
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),
        ],
    )
    assert ext.flush(t_ms=400) is None


# ──────────────────────────── USER-CORRECTION-022: Fail-fast dependency lookup ────────────────────────────


def test_missing_match_id_raises_keyerror_on_flush() -> None:
    """With a valid pending emit and no 'match_id' in deps, flush raises KeyError."""
    ext = SplitStepLatency(target_player="A", dependencies={})  # no match_id
    simulate_state_sequence(
        ext,
        [
            ("PRE_SERVE_RITUAL", "PRE_SERVE_RITUAL", 100),
            ("ACTIVE_RALLY", "ACTIVE_RALLY", 300),
        ],
    )
    with pytest.raises(KeyError, match="match_id"):
        ext.flush(t_ms=400)
