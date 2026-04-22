"""End-to-end integration test for backend/cv/compiler.py::FeatureCompiler.

Exercises:
- 14 extractor instances (7 x 2 players) constructed + dependency injection
- Per-tick state-gated ingest routing (USER-CORRECTION-011 cross-player)
- Compiler-flush contract (USER-CORRECTION-018): flush only on state exit
- Fail-fast match_id (USER-CORRECTION-022)
- Deterministic per-tick sample ordering
- Synthetic multi-player rally simulation producing real SignalSamples

Written after all 7 signal extractors merged; Action 3.5 orchestrator wire-up.
"""

from __future__ import annotations

import math

import pytest

from backend.cv.compiler import FeatureCompiler, build_frame_wrist_hip_inputs
from backend.cv.signals import (
    ALL_EXTRACTOR_CLASSES,
    LateralWorkRate,
)
from backend.db.schema import (
    FrameKeypoints,
    PlayerDetection,
    PlayerSide,
)

KalmanState = tuple[float, float, float, float]


# ──────────────────────────── Helpers ────────────────────────────


def _detection(
    player: PlayerSide,
    hip_y: float = 0.60,
    wrist_y: float = 0.40,
    shoulder_y: float = 0.45,
    feet_mid_m: tuple[float, float] = (4.0, 15.0),
) -> PlayerDetection:
    """Construct a PlayerDetection with plausible keypoint positions.

    Sets hip_y at indices 11/12, wrist_y at 9/10, shoulder_y at 5/6. Other
    keypoints land at (0.5, 0.5) with conf 0.9.
    """
    kp: list[tuple[float, float]] = [(0.5, 0.5)] * 17
    conf: list[float] = [0.9] * 17
    # Shoulders
    kp[5] = (0.48, shoulder_y)
    kp[6] = (0.52, shoulder_y)
    # Wrists
    kp[9] = (0.45, wrist_y)
    kp[10] = (0.55, wrist_y)
    # Hips
    kp[11] = (0.48, hip_y)
    kp[12] = (0.52, hip_y)
    return PlayerDetection(
        player=player,
        keypoints_xyn=kp,
        confidence=conf,
        bbox_conf=0.9,
        feet_mid_xyn=(0.5, 0.95),
        feet_mid_m=feet_mid_m,
        fallback_mode="ankle",
    )


def _frame(
    t_ms: int,
    a_kwargs: dict | None = None,
    b_kwargs: dict | None = None,
) -> FrameKeypoints:
    """Build a FrameKeypoints with both player detections."""
    a = _detection("A", **(a_kwargs or {}))
    b = _detection("B", **(b_kwargs or {}))
    return FrameKeypoints(t_ms=t_ms, frame_idx=t_ms // 33, player_a=a, player_b=b)


# ──────────────────────────── Construction ────────────────────────────


def test_compiler_constructs_14_extractors_deterministic_order() -> None:
    compiler = FeatureCompiler(
        match_id="utr_01",
        dependencies={"match_id": "utr_01", "clip_fps": 30.0},
    )
    exts = compiler.extractors
    assert len(exts) == 14

    # First 7: target="A" in canonical class order
    a_exts = exts[:7]
    b_exts = exts[7:]
    for ext in a_exts:
        assert ext.target_player == "A"
    for ext in b_exts:
        assert ext.target_player == "B"
    assert [type(e) for e in a_exts] == list(ALL_EXTRACTOR_CLASSES)
    assert [type(e) for e in b_exts] == list(ALL_EXTRACTOR_CLASSES)


def test_compiler_missing_match_id_raises_keyerror() -> None:
    """USER-CORRECTION-022 fail-fast: no silent default."""
    with pytest.raises(KeyError, match="match_id"):
        FeatureCompiler(match_id="utr_01", dependencies={})


def test_compiler_mismatched_match_id_raises_valueerror() -> None:
    """Positional match_id must match deps['match_id'] (belt-and-suspenders)."""
    with pytest.raises(ValueError, match="match_id"):
        FeatureCompiler(
            match_id="utr_01",
            dependencies={"match_id": "utr_09"},
        )


def test_dependencies_threaded_into_each_extractor() -> None:
    """Each extractor receives the same deps dict (read-only reference)."""
    deps = {"match_id": "utr_01", "clip_fps": 30.0, "court_mapper": object()}
    compiler = FeatureCompiler(match_id="utr_01", dependencies=deps)
    for ext in compiler.extractors:
        # Identity not required (compiler copies to dict(dependencies)); value equality is.
        assert ext.deps["match_id"] == "utr_01"
        assert ext.deps["clip_fps"] == 30.0


# ──────────────────────────── State-gated ingest dispatch ────────────────────────────


def test_tick_during_pre_serve_ritual_routes_only_psr_signals() -> None:
    compiler = FeatureCompiler(
        match_id="utr_01", dependencies={"match_id": "utr_01", "clip_fps": 30.0}
    )

    # Both players in PRE_SERVE_RITUAL — ACTIVE_RALLY-only extractors should NOT ingest.
    samples = compiler.tick(
        frame=_frame(100),
        states={"A": "PRE_SERVE_RITUAL", "B": "PRE_SERVE_RITUAL"},
        kalmans={"A": (0.0, 20.0, 0.0, 0.0), "B": (0.0, 4.0, 0.0, 0.0)},
        t_ms=100,
    )
    # No flushes on the very first tick (no prev_state). No samples expected.
    assert samples == []

    # Inspect which extractors have state: PRE_SERVE-only signals should have buffers populated.
    # ACTIVE_RALLY-only signals (LateralWorkRate, RecoveryLatency, CrouchDepth, BaselineRetreat)
    # must NOT have been ingested (their internal buffers remain empty).
    a_lateral = next(
        e for e in compiler.extractors
        if e.target_player == "A" and isinstance(e, LateralWorkRate)
    )
    # LateralWorkRate uses private _buffer; we test via flush returning None post-gate.
    flushed = a_lateral.flush(t_ms=200)
    assert flushed is None


def test_tick_during_active_rally_routes_rally_signals_and_split_step() -> None:
    """ACTIVE_RALLY state should fire: lateral, recovery, crouch, baseline, + split-step."""
    compiler = FeatureCompiler(
        match_id="utr_01", dependencies={"match_id": "utr_01", "clip_fps": 30.0}
    )
    # Feed 10 ACTIVE_RALLY ticks
    for i in range(10):
        compiler.tick(
            frame=_frame(
                (i + 1) * 33,
                a_kwargs={"hip_y": 0.60, "wrist_y": 0.40},
                b_kwargs={"hip_y": 0.62, "wrist_y": 0.42},
            ),
            states={"A": "ACTIVE_RALLY", "B": "ACTIVE_RALLY"},
            kalmans={"A": (0.0, 25.0, 2.5, 0.0), "B": (0.0, -1.0, -1.0, 0.0)},
            t_ms=(i + 1) * 33,
        )
    # LateralWorkRate (A) should have buffered some |vx| values; flush should now emit.
    a_lateral = next(
        e for e in compiler.extractors
        if e.target_player == "A" and isinstance(e, LateralWorkRate)
    )
    sample = a_lateral.flush(t_ms=1000)
    assert sample is not None
    assert sample.signal_name == "lateral_work_rate"
    assert sample.player == "A"


# ──────────────────────────── Compiler-flush contract (USER-CORRECTION-018) ────────────────────────────


def test_flush_fires_only_on_state_exit_not_every_tick() -> None:
    """Compiler-flush must fire EXACTLY ONCE when target exits required_state."""
    compiler = FeatureCompiler(
        match_id="utr_01", dependencies={"match_id": "utr_01", "clip_fps": 30.0}
    )

    # 5 ACTIVE_RALLY ticks — no flush yet
    for i in range(5):
        samples = compiler.tick(
            frame=_frame((i + 1) * 33),
            states={"A": "ACTIVE_RALLY", "B": "ACTIVE_RALLY"},
            kalmans={"A": (0.0, 25.0, 2.0, 0.0), "B": (0.0, -1.5, -2.0, 0.0)},
            t_ms=(i + 1) * 33,
        )
        assert samples == [], f"no flush expected mid-rally at tick {i+1}"

    # Transition BOTH to DEAD_TIME → ACTIVE_RALLY-only signals MUST flush
    samples = compiler.tick(
        frame=_frame(200),
        states={"A": "DEAD_TIME", "B": "DEAD_TIME"},
        kalmans={"A": (0.0, 25.0, 0.0, 0.0), "B": (0.0, -1.5, 0.0, 0.0)},
        t_ms=200,
    )
    # Expect LateralWorkRate + BaselineRetreat + CrouchDepth flushes for BOTH A and B.
    # RecoveryLatency may return None if the stillness tick hasn't been captured in its own buffer
    # (because ACTIVE_RALLY ingest stops the moment we transition out — its buffer only has
    # ACTIVE_RALLY ticks, all with |v|>=2.0 — no stillness detected → None).
    emitted_names = {(s.signal_name, s.player) for s in samples}
    # LateralWorkRate and BaselineRetreat emit easily. CrouchDepth may or may not (needs >=5 valid).
    assert ("lateral_work_rate", "A") in emitted_names
    assert ("lateral_work_rate", "B") in emitted_names
    assert ("baseline_retreat_distance_m", "A") in emitted_names
    assert ("baseline_retreat_distance_m", "B") in emitted_names


def test_repeated_exits_do_not_double_flush_without_re_entry() -> None:
    """Flush fires once on exit; staying in DEAD_TIME does NOT re-flush."""
    compiler = FeatureCompiler(
        match_id="utr_01", dependencies={"match_id": "utr_01", "clip_fps": 30.0}
    )
    # Ingest one ACTIVE_RALLY tick
    compiler.tick(
        frame=_frame(33),
        states={"A": "ACTIVE_RALLY", "B": "ACTIVE_RALLY"},
        kalmans={"A": (0.0, 25.0, 2.0, 0.0), "B": (0.0, -1.0, -2.0, 0.0)},
        t_ms=33,
    )
    # Transition to DEAD_TIME
    samples1 = compiler.tick(
        frame=_frame(66),
        states={"A": "DEAD_TIME", "B": "DEAD_TIME"},
        kalmans={"A": (0.0, 25.0, 0.0, 0.0), "B": (0.0, -1.0, 0.0, 0.0)},
        t_ms=66,
    )
    # Stay in DEAD_TIME — no new flushes
    samples2 = compiler.tick(
        frame=_frame(99),
        states={"A": "DEAD_TIME", "B": "DEAD_TIME"},
        kalmans={"A": (0.0, 25.0, 0.0, 0.0), "B": (0.0, -1.0, 0.0, 0.0)},
        t_ms=99,
    )
    # samples1 may or may not have content (depends on buffer state), but samples2 MUST be empty.
    assert samples2 == []
    _ = samples1  # silence linter


# ──────────────────────────── End-to-end rally simulation ────────────────────────────


def test_full_rally_cycle_emits_multiple_signals() -> None:
    """Simulate PRE_SERVE → ACTIVE_RALLY → DEAD_TIME. Expect flushes at each transition."""
    compiler = FeatureCompiler(
        match_id="utr_01", dependencies={"match_id": "utr_01", "clip_fps": 30.0}
    )
    all_samples: list = []

    # Phase 1: 20 ticks of PRE_SERVE_RITUAL — player A tosses ball (wrist rises then falls)
    # Wrist going up (low y) then down — oscillation around hip
    for i in range(20):
        t = (i + 1) * 33
        wrist_osc = 0.40 + 0.1 * math.sin(2 * math.pi * 2.0 * (t / 1000.0))
        samples = compiler.tick(
            frame=_frame(t, a_kwargs={"hip_y": 0.60, "wrist_y": wrist_osc, "shoulder_y": 0.45}),
            states={"A": "PRE_SERVE_RITUAL", "B": "PRE_SERVE_RITUAL"},
            kalmans={"A": (0.0, 23.5, 0.0, 0.0), "B": (0.0, 0.5, 0.0, 0.0)},
            t_ms=t,
        )
        all_samples.extend(samples)

    # Phase 2: transition A and B to ACTIVE_RALLY (PRE_SERVE-only signals must flush now)
    samples = compiler.tick(
        frame=_frame(700),
        states={"A": "ACTIVE_RALLY", "B": "ACTIVE_RALLY"},
        kalmans={"A": (0.0, 24.0, 2.0, 0.0), "B": (0.0, -0.5, -2.0, 0.0)},
        t_ms=700,
    )
    all_samples.extend(samples)

    # Phase 2-cont: 10 more ACTIVE_RALLY ticks
    for i in range(10):
        t = 700 + (i + 1) * 33
        samples = compiler.tick(
            frame=_frame(t),
            states={"A": "ACTIVE_RALLY", "B": "ACTIVE_RALLY"},
            kalmans={"A": (0.0, 24.0 + i * 0.1, 2.0, 0.1), "B": (0.0, -0.5 - i * 0.1, -2.0, -0.1)},
            t_ms=t,
        )
        all_samples.extend(samples)

    # Phase 3: both to DEAD_TIME (ACTIVE_RALLY signals must flush)
    samples = compiler.tick(
        frame=_frame(1100),
        states={"A": "DEAD_TIME", "B": "DEAD_TIME"},
        kalmans={"A": (0.0, 25.0, 0.0, 0.0), "B": (0.0, -1.0, 0.0, 0.0)},
        t_ms=1100,
    )
    all_samples.extend(samples)

    # Assertions: the cycle should have emitted AT LEAST these samples:
    emitted = {(s.signal_name, s.player) for s in all_samples}

    # PRE_SERVE flushes on entry to ACTIVE_RALLY at t=700:
    # serve_toss_variance (A, B), ritual_entropy (A, B) ARE possible IF the variance-floor
    # and amplitude-floor thresholds are met. Player A has 0.1 amplitude toss (>0.05), so
    # serve_toss_variance_cm should emit for A. B has no toss (phantom-serve guard → None).
    assert ("serve_toss_variance_cm", "A") in emitted, (
        "A's real toss (amplitude ~0.2 rel) should emit serve_toss_variance_cm on flush"
    )

    # ACTIVE_RALLY flushes on entry to DEAD_TIME:
    assert ("lateral_work_rate", "A") in emitted
    assert ("lateral_work_rate", "B") in emitted
    assert ("baseline_retreat_distance_m", "A") in emitted
    assert ("baseline_retreat_distance_m", "B") in emitted

    # All samples should have the correct match_id (USER-CORRECTION-022):
    for s in all_samples:
        assert s.match_id == "utr_01"


def test_finalize_flushes_all_remaining_buffers() -> None:
    """After the last tick, finalize() emits any still-buffered samples."""
    compiler = FeatureCompiler(
        match_id="utr_01", dependencies={"match_id": "utr_01", "clip_fps": 30.0}
    )
    # Ingest some ACTIVE_RALLY ticks, then finalize WITHOUT a state transition.
    for i in range(10):
        compiler.tick(
            frame=_frame((i + 1) * 33),
            states={"A": "ACTIVE_RALLY", "B": "ACTIVE_RALLY"},
            kalmans={"A": (0.0, 25.0, 2.0, 0.0), "B": (0.0, -1.0, -2.0, 0.0)},
            t_ms=(i + 1) * 33,
        )
    final_samples = compiler.finalize(t_ms=500)
    emitted = {(s.signal_name, s.player) for s in final_samples}
    # Buffers had content — should emit at least lateral + baseline for both players.
    assert ("lateral_work_rate", "A") in emitted
    assert ("baseline_retreat_distance_m", "B") in emitted


def test_reset_clears_all_extractor_state() -> None:
    compiler = FeatureCompiler(
        match_id="utr_01", dependencies={"match_id": "utr_01", "clip_fps": 30.0}
    )
    # Populate some state
    for i in range(5):
        compiler.tick(
            frame=_frame((i + 1) * 33),
            states={"A": "ACTIVE_RALLY", "B": "ACTIVE_RALLY"},
            kalmans={"A": (0.0, 25.0, 2.0, 0.0), "B": (0.0, -1.0, -2.0, 0.0)},
            t_ms=(i + 1) * 33,
        )
    compiler.reset()
    # After reset, a finalize on the same compiler should emit nothing
    final_samples = compiler.finalize(t_ms=500)
    assert final_samples == []


# ──────────────────────────── build_frame_wrist_hip_inputs helper ────────────────────────────


def test_build_frame_wrist_hip_inputs_with_detection() -> None:
    frame = _frame(33)
    result = build_frame_wrist_hip_inputs(frame, "A")
    # Shape: (l_wrist_y, l_wrist_conf, r_wrist_y, r_wrist_conf, hip_y, hip_conf)
    assert result[0] == pytest.approx(0.40)  # l_wrist_y
    assert result[1] == pytest.approx(0.9)   # l_wrist_conf
    assert result[4] == pytest.approx(0.60)  # hip_y (mean)
    assert result[5] == pytest.approx(0.9)   # hip_conf (min)


def test_build_frame_wrist_hip_inputs_missing_detection_returns_all_none() -> None:
    # Construct a frame where player_b is None
    a = _detection("A")
    frame = FrameKeypoints(t_ms=100, frame_idx=3, player_a=a, player_b=None)
    result = build_frame_wrist_hip_inputs(frame, "B")
    assert result == (None, None, None, None, None, None)
