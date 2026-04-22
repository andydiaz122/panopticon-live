"""BaseSignalExtractor — abstract contract for all 7 biomechanical signal extractors.

Implements USER-CORRECTION-013 (Symmetric Extractor API + Dependency Injection):
- Constructor takes `target_player: PlayerSide` + `dependencies: dict[str, Any]`
- `ingest()` receives (target_state, opponent_state, target_kalman, opponent_kalman) symmetrically
- `flush()` knows which player it serves from `self.target_player` (no routing flag needed)

Rationale: a per-player compiler cannot compute `split_step_latency_ms` (needs opponent's
PRE_SERVE → ACTIVE_RALLY transition timestamp). Passing both players' state symmetrically
means the FeatureCompiler instantiates each extractor TWICE (target="A", target="B") and
routes `target_*` + `opponent_*` consistently. Each subclass writes pure math on "target"
and "opponent" without branching on self-identity.

Dependency injection carries shared resources (e.g. CourtMapper for homography-gated signals,
clip_fps for per-second normalization). Unused deps are ignored per extractor.
"""

from __future__ import annotations

import abc
from typing import Any

from backend.db.schema import FrameKeypoints, PlayerSide, PlayerState, SignalSample


class BaseSignalExtractor(abc.ABC):
    """Abstract base for all biomechanical signal extractors."""

    signal_name: str
    """Class-level attribute — the SignalName this extractor emits."""

    required_state: tuple[PlayerState, ...]
    """Class-level attribute — states during which this signal is active.

    The FeatureCompiler gates `ingest()`/`flush()` calls by checking `target_state`
    against this tuple. Immutable tuple so compilers can hash-cache the gate.
    """

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        """Construct a per-player extractor with injected dependencies.

        Args:
            target_player: Which player this instance serves. The compiler instantiates
                every extractor twice — once for "A", once for "B".
            dependencies: Shared resources. Common keys:
                - "court_mapper": CourtMapper (required for baseline_retreat, other
                  homography-gated signals)
                - "clip_fps": float (required for per-second normalization in
                  lateral_work_rate, recovery_latency, etc.)
                Unused keys are ignored per extractor.
        """
        self.target_player: PlayerSide = target_player
        self.deps: dict[str, Any] = dependencies

    @abc.abstractmethod
    def ingest(
        self,
        frame: FrameKeypoints,
        target_state: PlayerState,
        opponent_state: PlayerState,
        target_kalman: tuple[float, float, float, float] | None,
        opponent_kalman: tuple[float, float, float, float] | None,
        t_ms: int,
    ) -> None:
        """Consume one frame of match state.

        Args:
            frame: Both players' keypoints for this tick.
            target_state: State of the player this extractor serves.
            opponent_state: State of the other player (for cross-player signals).
            target_kalman: (x_m, y_m, vx_mps, vy_mps) for target, or None if occluded.
            opponent_kalman: Same for opponent.
            t_ms: Wallclock-ms timestamp of this frame.

        Subclasses mutate internal buffers. No return value.
        """

    @abc.abstractmethod
    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit a SignalSample for `self.target_player` at `t_ms`, or None.

        None means "no sample this tick" — e.g., state gate not met, buffer insufficient,
        or signal is event-triggered and no event fired.
        """

    def reset(self) -> None:
        """Clear internal buffers — called on match start or between ablations.

        Default no-op; subclasses override when they carry state between frames.
        """
        return None
