"""RecoveryLatency — milliseconds from last moving tick to first still tick during ACTIVE_RALLY.

Fatigue indicator. As a player tires across sets, the time to decelerate from
rally speed to standing still grows — muscular control of deceleration is the
first biomechanic to degrade.

Definition (per USER-CORRECTION-018, Compiler Flush Contract):
- required_state = ("ACTIVE_RALLY",) — accumulate only during rally
- ingest() buffers (t_ms, speed_mps) where speed_mps = hypot(vx, vy)
- flush(t_ms) is called by the compiler when the player EXITS ACTIVE_RALLY.
  The extractor is state-blind beyond the required_state gate.

Math on flush:
1. Walk the buffer forward; find the LAST index where speed >= 0.5 m/s
   (call this t_rally_end).
2. Find the FIRST subsequent index where speed < 0.5 m/s
   (call this t_at_stillness).
3. Emit latency_ms = t_at_stillness - t_rally_end.
4. If either is missing (never moved, or never decelerated) → None.

USER-CORRECTION-017 (physics guardrail): speed comes ONLY from the Kalman-fused
2D velocity (target_kalman[2], target_kalman[3]). No CoM reconstruction, no
CourtMapper projection, no manual keypoint derivatives.

USER-CORRECTION-022 (fail-fast): `self.deps["match_id"]` is strict; a missing
dep corrupts the DuckDB PK — fail LOUDLY, never silently default.
"""

from __future__ import annotations

import math
from typing import Any

from backend.cv.signals.base import BaseSignalExtractor
from backend.cv.thresholds import KINEMATIC
from backend.db.schema import FrameKeypoints, PlayerSide, PlayerState, SignalSample

# Speed threshold distinguishing "moving" from "still" (PATTERN-057: sourced from
# backend/cv/thresholds.py::KINEMATIC so re-tuning is one-file-diff, not grep-safari).
RECOVERY_SPEED_THRESHOLD_MPS: float = KINEMATIC.recovery_speed_mps


class RecoveryLatency(BaseSignalExtractor):
    """Latency (ms) between last rally motion tick and first still tick within a rally window."""

    signal_name = "recovery_latency_ms"
    required_state: tuple[PlayerState, ...] = ("ACTIVE_RALLY",)

    def __init__(self, target_player: PlayerSide, dependencies: dict[str, Any]) -> None:
        super().__init__(target_player, dependencies)
        # (t_ms, speed_mps) pairs accumulated during ACTIVE_RALLY.
        self._buffer: list[tuple[int, float]] = []

    def ingest(
        self,
        frame: FrameKeypoints,
        target_state: PlayerState,
        opponent_state: PlayerState,
        target_kalman: tuple[float, float, float, float] | None,
        opponent_kalman: tuple[float, float, float, float] | None,
        t_ms: int,
    ) -> None:
        """Append (t_ms, 2D-speed) iff ACTIVE_RALLY and target_kalman present."""
        if target_state != "ACTIVE_RALLY":
            return
        if target_kalman is None:
            return
        vx = target_kalman[2]
        vy = target_kalman[3]
        speed_mps = math.hypot(vx, vy)
        self._buffer.append((t_ms, speed_mps))

    def flush(self, t_ms: int) -> SignalSample | None:
        """Emit recovery_latency_ms sample or None; ALWAYS clears the buffer on exit."""
        if not self._buffer:
            return None

        # Walk forward: find LAST index i with speed >= threshold.
        last_moving_idx: int | None = None
        for i, (_, speed) in enumerate(self._buffer):
            if speed >= RECOVERY_SPEED_THRESHOLD_MPS:
                last_moving_idx = i

        # If no tick was above threshold, the player never actually moved — None.
        if last_moving_idx is None:
            self._buffer.clear()
            return None

        # Find FIRST subsequent index j > last_moving_idx with speed < threshold.
        t_rally_end = self._buffer[last_moving_idx][0]
        t_at_stillness: int | None = None
        for j in range(last_moving_idx + 1, len(self._buffer)):
            if self._buffer[j][1] < RECOVERY_SPEED_THRESHOLD_MPS:
                t_at_stillness = self._buffer[j][0]
                break

        # If player was still moving at rally end, no deceleration completed — None.
        if t_at_stillness is None:
            self._buffer.clear()
            return None

        latency_ms = float(t_at_stillness - t_rally_end)
        sample = SignalSample(
            timestamp_ms=t_ms,
            match_id=self.deps["match_id"],
            player=self.target_player,
            signal_name=self.signal_name,
            value=latency_ms,
            baseline_z_score=None,
            state="ACTIVE_RALLY",
        )
        self._buffer.clear()
        return sample

    def reset(self) -> None:
        """Clear buffer on match start / between ablations."""
        super().reset()
        self._buffer.clear()
