"""FeatureCompiler — per-tick orchestrator for the PANOPTICON CV pipeline.

Implements the canonical Stage 4.5/5 dispatch order per
`cv-pipeline-engineering` skill:

    Per tick:
      1. RollingBounceDetector.ingest_player_frame(A, wrists+hip)
      2. RollingBounceDetector.ingest_player_frame(B, wrists+hip)
      3. (a_bounce, b_bounce) = RollingBounceDetector.evaluate()
      4. MatchStateMachine.update(a_speed, b_speed, a_bounce, b_bounce, t_ms)
      5. For each of 14 extractor instances:
           - if target_state in extractor.required_state:
               extractor.ingest(frame, target_state, opponent_state,
                                target_kalman, opponent_kalman, t_ms)
      6. Compiler-Flush (USER-CORRECTION-018): for each extractor,
         detect prev_state in required_state AND curr_state NOT in
         required_state. If true, call flush(t_ms). Collect emitted samples.

Responsibilities held HERE (not in extractors):
  - Holding 14 extractor instances (7 x 2 players)
  - Tracking per-player `prev_state` to detect state exits
  - Routing target/opponent state + kalman into each extractor by target_player
  - Injecting dependencies (match_id, court_mapper, clip_fps) into each extractor
  - Emitting SignalSamples in deterministic per-tick order

Responsibilities held by extractors (not here):
  - Per-signal math
  - Per-signal state-gate short-circuit in ingest()
  - Per-signal buffer management

Extractors DO NOT track their own state-exit transitions. That belongs to
the compiler, per USER-CORRECTION-018.
"""

from __future__ import annotations

from typing import Any

from backend.cv.signals import ALL_EXTRACTOR_CLASSES, BaseSignalExtractor
from backend.db.schema import (
    FrameKeypoints,
    PlayerDetection,
    PlayerSide,
    PlayerState,
    SignalSample,
)

KalmanState = tuple[float, float, float, float]  # (x_m, y_m, vx_mps, vy_mps)


class FeatureCompiler:
    """Orchestrates per-tick signal extraction for both players simultaneously.

    Usage (pseudocode):
        compiler = FeatureCompiler(match_id="utr_01", dependencies={
            "match_id": "utr_01",
            "court_mapper": court_mapper,
            "clip_fps": 30.0,
        })
        for frame in frames:
            states = match_state_machine.states   # from external state machine
            kalmans = {"A": kalman_a, "B": kalman_b}
            samples = compiler.tick(
                frame=frame,
                states=states,
                kalmans=kalmans,
                t_ms=frame.t_ms,
            )
            for sample in samples:
                db.write(sample)
    """

    def __init__(self, match_id: str, dependencies: dict[str, Any]) -> None:
        """Instantiate the compiler with 14 extractor instances (7 x 2 players).

        The match_id is mandatory — it's included in dependencies + stored
        here for clarity. Fails loudly if dependencies["match_id"] is missing
        (fail-fast discipline per USER-CORRECTION-022).
        """
        if "match_id" not in dependencies:
            raise KeyError(
                "FeatureCompiler requires dependencies['match_id'] to be set "
                "(USER-CORRECTION-022: no silent defaults in data pipelines)."
            )
        if dependencies["match_id"] != match_id:
            raise ValueError(
                f"dependencies['match_id']={dependencies['match_id']!r} does not "
                f"match positional match_id={match_id!r}."
            )
        self.match_id = match_id
        self._deps = dict(dependencies)

        # Instantiate 14 extractors: one for each of 7 signals x 2 players.
        # Order within each player follows ALL_EXTRACTOR_CLASSES for determinism.
        self._extractors: list[BaseSignalExtractor] = []
        for player_side in ("A", "B"):
            for cls in ALL_EXTRACTOR_CLASSES:
                self._extractors.append(cls(target_player=player_side, dependencies=self._deps))

        # State bookkeeping for compiler-flush contract (USER-CORRECTION-018)
        self._prev_states: dict[PlayerSide, PlayerState | None] = {"A": None, "B": None}

    @property
    def extractors(self) -> list[BaseSignalExtractor]:
        """Read-only view for tests."""
        return list(self._extractors)

    def tick(
        self,
        frame: FrameKeypoints,
        states: dict[PlayerSide, PlayerState],
        kalmans: dict[PlayerSide, KalmanState | None],
        t_ms: int,
    ) -> list[SignalSample]:
        """Drive one pipeline tick. Returns all SignalSamples emitted this tick.

        Canonical order (USER-CORRECTIONs 011, 013, 018):
          1. Ingest into each extractor whose required_state matches target's state.
          2. For each extractor, if target just EXITED its required_state, flush.
          3. Update prev_states bookkeeping.
        """
        samples: list[SignalSample] = []

        # Phase 1 — ingest dispatch.
        for ext in self._extractors:
            target = ext.target_player
            opponent: PlayerSide = "B" if target == "A" else "A"
            target_state = states[target]
            opponent_state = states[opponent]
            # State gate: only ingest when target is in one of the required states.
            if target_state not in ext.required_state:
                continue
            ext.ingest(
                frame=frame,
                target_state=target_state,
                opponent_state=opponent_state,
                target_kalman=kalmans[target],
                opponent_kalman=kalmans[opponent],
                t_ms=t_ms,
            )

        # Phase 2 — compiler-flush contract (USER-CORRECTION-018).
        # Flush ONLY extractors whose target just transitioned OUT of required_state.
        for ext in self._extractors:
            target = ext.target_player
            curr = states[target]
            prev = self._prev_states[target]
            if prev is None:
                # First tick for this player — nothing has "exited" yet.
                continue
            prev_in = prev in ext.required_state
            curr_in = curr in ext.required_state
            if prev_in and not curr_in:
                sample = ext.flush(t_ms)
                if sample is not None:
                    samples.append(sample)

        # Phase 3 — bookkeeping.
        self._prev_states["A"] = states["A"]
        self._prev_states["B"] = states["B"]
        return samples

    def finalize(self, t_ms: int) -> list[SignalSample]:
        """Flush ALL remaining extractor buffers at end of clip.

        Call ONCE after the last frame tick, regardless of whether each
        extractor's target is still in required_state. Emits any partial
        windows that never naturally transitioned out.
        """
        samples: list[SignalSample] = []
        for ext in self._extractors:
            sample = ext.flush(t_ms)
            if sample is not None:
                samples.append(sample)
        return samples

    def reset(self) -> None:
        """Reset all extractors + bookkeeping (new match)."""
        for ext in self._extractors:
            ext.reset()
        self._prev_states = {"A": None, "B": None}


def build_frame_wrist_hip_inputs(
    frame: FrameKeypoints,
    side: PlayerSide,
) -> tuple[float | None, float | None, float | None, float | None, float | None, float | None]:
    """Extract (l_wrist_y, l_wrist_conf, r_wrist_y, r_wrist_conf, hip_y, hip_conf)
    from a FrameKeypoints for the requested player side.

    Returns all-None tuple when the player's detection is absent this tick.
    Used by the pipeline assembly code when feeding RollingBounceDetector —
    the compiler itself does NOT call RollingBounceDetector (that's upstream,
    Stage 4.5), but this helper lives here for import convenience.

    COCO indices:
      9 = left_wrist, 10 = right_wrist, 11 = left_hip, 12 = right_hip
    """
    detection: PlayerDetection | None = frame.player_a if side == "A" else frame.player_b
    if detection is None:
        return (None, None, None, None, None, None)
    kpts = detection.keypoints_xyn
    confs = detection.confidence
    l_wrist_y, l_wrist_conf = kpts[9][1], confs[9]
    r_wrist_y, r_wrist_conf = kpts[10][1], confs[10]
    # Hip: take mean of L/R y-coords; confidence is the min of the two.
    hip_y = (kpts[11][1] + kpts[12][1]) / 2.0
    hip_conf = min(confs[11], confs[12])
    return (l_wrist_y, l_wrist_conf, r_wrist_y, r_wrist_conf, hip_y, hip_conf)
