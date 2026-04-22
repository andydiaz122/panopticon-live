---
name: signal-extractor-contract
description: Contract discipline for every PANOPTICON signal extractor — BaseSignalExtractor ABC, symmetric target/opponent API (USER-CORRECTION-013), dependency injection, Pydantic @field_serializer float rounding (USER-CORRECTION-015). Use when creating ANY new signal module under backend/cv/signals/, writing signal tests, or reviewing fleet-agent deliverables.
---

# Signal Extractor Contract

This skill is the INTERFACE discipline for the 7 biomechanical signal extractors. It owns exactly two concerns:

1. **Inheritance and API shape** (the ABC) — USER-CORRECTION-013
2. **JSON payload hygiene** (the `@field_serializer`) — USER-CORRECTION-015

It deliberately does NOT own:
- **Signal math / semantics** → `biomechanical-signal-semantics`
- **Temporal primitives (bounce, rolling buffers, Lomb-Scargle)** → `temporal-kinematic-primitives`
- **Pipeline orchestration** → `cv-pipeline-engineering`

## 1 — The BaseSignalExtractor ABC

Every signal module under `backend/cv/signals/<signal_name>.py` MUST:

1. Import `BaseSignalExtractor` from `backend.cv.signals.base`.
2. Subclass it.
3. Define **class-level** `signal_name: str` (matching a `SignalName` literal in `schema.py`) and `required_state: tuple[PlayerState, ...]`.
4. Implement `ingest(frame, target_state, opponent_state, target_kalman, opponent_kalman, t_ms)` and `flush(t_ms)`.
5. Override `reset()` if the extractor holds buffers.

**NO alternative shapes are allowed.** Fleet agents that invent their own `ingest(player_a_state, player_b_state, ...)` are rejected at review.

### Symmetric API (USER-CORRECTION-013)

The API is **symmetric around the target player** (not the absolute "A/B" axis):

```python
class MySignal(BaseSignalExtractor):
    signal_name = "recovery_latency_ms"
    required_state = ("ACTIVE_RALLY", "DEAD_TIME")  # fires across the transition

    def ingest(self, frame, target_state, opponent_state,
               target_kalman, opponent_kalman, t_ms):
        if target_kalman is None:
            return  # occluded, skip
        tx, ty, tvx, tvy = target_kalman
        # write math using 'target' and 'opponent' — never branch on self.target_player
        ...

    def flush(self, t_ms):
        if self._pending_sample is not None:
            return SignalSample(
                timestamp_ms=t_ms,
                match_id=self.deps["match_id"],
                player=self.target_player,   # <-- known from __init__
                signal_name=self.signal_name,
                value=self._pending_sample,
                baseline_z_score=None,
                state=self._last_target_state,
            )
        return None
```

**Cross-player signals** read `opponent_state` / `opponent_kalman` directly. No branching:

```python
# split_step_latency_ms — fires after opponent serves and target first accelerates
def ingest(self, frame, target_state, opponent_state, target_kalman, opponent_kalman, t_ms):
    if opponent_state == "PRE_SERVE_RITUAL" and self._last_opp_state == "PRE_SERVE_RITUAL":
        # still pre-serve; waiting
        pass
    elif opponent_state == "ACTIVE_RALLY" and self._last_opp_state == "PRE_SERVE_RITUAL":
        self._opponent_contact_ms = t_ms   # opponent just started swinging → serve contact
    ...
    self._last_opp_state = opponent_state
```

### Dependency Injection (USER-CORRECTION-013)

Shared resources travel through `dependencies: dict[str, Any]` in `__init__`. The FeatureCompiler owns the canonical deps and passes them verbatim to every extractor:

```python
# orchestrator
deps = {
    "court_mapper": CourtMapper(corners, W, H),
    "clip_fps": 30.0,
    "match_id": "utr_01_seg_a",
}
compiler = FeatureCompiler(match_id="utr_01_seg_a", dependencies=deps)

# inside an extractor
class BaselineRetreat(BaseSignalExtractor):
    signal_name = "baseline_retreat_distance_m"
    required_state = ("ACTIVE_RALLY",)

    def ingest(self, frame, target_state, opponent_state,
               target_kalman, opponent_kalman, t_ms):
        mapper = self.deps["court_mapper"]   # CourtMapper, injected
        x_m, y_m, _, _ = target_kalman or (None, None, None, None)
        ...
```

**Unused deps are ignored** per extractor. `serve_toss_variance_cm` doesn't need `court_mapper`; it simply doesn't reference `self.deps["court_mapper"]`.

## 2 — Pydantic @field_serializer Payload Hygiene

Per USER-CORRECTION-015, every float-bearing field in `backend/db/schema.py` serializes to 4 decimal places. The rounding happens at `model_dump_json()` ONLY — in-memory values retain full precision (Kalman, state machine, and signal math see original floats).

Why 4 decimals:
- 0.0001 in normalized coords ≈ 0.2 px at 1920-wide (below YOLO jitter ~2-3 px)
- 0.0001 m = 0.1 mm in court meters (far below measurement noise)
- Shrinks keypoint-heavy JSON payloads ~3x — prevents the 10MB+ browser-OOM trap on mobile Safari

**Pattern** (already applied to `KeypointFrame`, `PlayerDetection`, `SignalSample`, `FatigueVector`, `AnomalyEvent`):

```python
from pydantic import field_serializer
from backend.db.schema import FLOAT_SERIALIZE_DECIMALS

class MyNewModel(PanopticonBase):
    value: float | None

    @field_serializer("value")
    def _ser_value(self, v: float | None) -> float | None:
        return None if v is None else round(v, FLOAT_SERIALIZE_DECIMALS)
```

**Invariants**:
- `None` values always pass through as `null`, never crash.
- Round-trip (JSON → parse → construct → JSON) is idempotent (no drift on second pass).
- Validators + serializers coexist: validators run on construction, serializers run on dump.

**What you MUST NOT do**:
- Do NOT add a serializer that mutates the in-memory value (e.g., `round()` in a `@field_validator`).
- Do NOT skip the serializer on new models with float fields — the FeatureCompiler exports to `match_data.json` and payload bloat is real.

## When this skill fires

- Creating a new signal module in `backend/cv/signals/`
- Reviewing fleet-agent deliverables (Action 3)
- Adding a new float-bearing Pydantic model to `schema.py`
- Writing tests that verify the ABC contract or serializer behavior

## Delegation graph

- Delegates math semantics → `biomechanical-signal-semantics`
- Delegates temporal primitives (bounce, Lomb-Scargle) → `temporal-kinematic-primitives`
- Delegates orchestration → `cv-pipeline-engineering`
- Referenced by `test-forensic-validator` when writing ABC contract tests
- Referenced by `cv-pipeline-engineer` when implementing the FeatureCompiler
