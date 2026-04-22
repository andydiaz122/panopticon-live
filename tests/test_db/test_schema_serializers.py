"""Tests for Pydantic @field_serializer float-rounding in backend/db/schema.py.

Enforces USER-CORRECTION-015 payload hygiene:
- All float-bearing fields round to 4 decimal places at JSON serialization
- In-memory values retain full precision (serializer does NOT mutate)
- Round-trip drift is bounded
- None values serialize as null without crashing
- Float rounding prevents 10MB+ JSON bloat from YOLO keypoint streams

Written FIRST per TDD discipline.
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from backend.db.schema import (
    AnomalyEvent,
    FatigueVector,
    KeypointFrame,
    PlayerDetection,
    SignalSample,
)

# ──────────────────────────── Helpers ────────────────────────────


def _high_precision_keypoints() -> list[tuple[float, float]]:
    """17 keypoints with digits far beyond 4 decimal places."""
    return [(0.123456789012, 0.987654321098) for _ in range(17)]


def _high_precision_conf() -> list[float]:
    return [0.987654321098 for _ in range(17)]


def _make_player_detection(**overrides) -> PlayerDetection:
    defaults: dict = {
        "player": "A",
        "keypoints_xyn": _high_precision_keypoints(),
        "confidence": _high_precision_conf(),
        "bbox_conf": 0.876543210987,
        "feet_mid_xyn": (0.123456789, 0.987654321),
        "feet_mid_m": (4.123456789, 15.987654321),
        "fallback_mode": "ankle",
    }
    defaults.update(overrides)
    return PlayerDetection(**defaults)


def _max_decimal_places(value: float | str) -> int:
    """Count digits after the decimal point in a serialized number."""
    s = str(value) if not isinstance(value, str) else value
    if "." not in s:
        return 0
    # Trim scientific notation and signs
    s = s.split("e")[0].split("E")[0].rstrip("0").rstrip(".")
    if "." not in s:
        return 0
    return len(s.split(".")[1])


# ──────────────────────────── PlayerDetection rounding ────────────────────────────


def test_player_detection_keypoints_rounded_in_json_output() -> None:
    det = _make_player_detection()
    dumped = det.model_dump_json()
    parsed = json.loads(dumped)
    for x, y in parsed["keypoints_xyn"]:
        assert _max_decimal_places(x) <= 4
        assert _max_decimal_places(y) <= 4


def test_player_detection_confidence_rounded() -> None:
    det = _make_player_detection()
    parsed = json.loads(det.model_dump_json())
    for conf in parsed["confidence"]:
        assert _max_decimal_places(conf) <= 4


def test_player_detection_bbox_conf_rounded() -> None:
    det = _make_player_detection()
    parsed = json.loads(det.model_dump_json())
    assert _max_decimal_places(parsed["bbox_conf"]) <= 4
    assert parsed["bbox_conf"] == pytest.approx(0.8765, abs=1e-9)


def test_player_detection_feet_mid_xyn_rounded() -> None:
    det = _make_player_detection()
    parsed = json.loads(det.model_dump_json())
    for v in parsed["feet_mid_xyn"]:
        assert _max_decimal_places(v) <= 4
    assert parsed["feet_mid_xyn"] == [pytest.approx(0.1235, abs=1e-9), pytest.approx(0.9877, abs=1e-9)]


def test_player_detection_feet_mid_m_rounded() -> None:
    det = _make_player_detection()
    parsed = json.loads(det.model_dump_json())
    for v in parsed["feet_mid_m"]:
        assert _max_decimal_places(v) <= 4


# ──────────────────────────── In-memory precision preserved ────────────────────────────


def test_in_memory_values_retain_full_precision() -> None:
    """Serializer is serialization-only; attribute access returns original float."""
    det = _make_player_detection()
    # Access via attribute — serializer must NOT have mutated construction-time values
    x0, y0 = det.keypoints_xyn[0]
    assert x0 == pytest.approx(0.123456789012, abs=1e-12)
    assert y0 == pytest.approx(0.987654321098, abs=1e-12)
    assert det.bbox_conf == pytest.approx(0.876543210987, abs=1e-12)


# ──────────────────────────── Round-trip determinism ────────────────────────────


def test_round_trip_drift_is_bounded() -> None:
    """round → JSON → parse → reconstruct → JSON → parse → equal rounded values."""
    det = _make_player_detection()
    json1 = det.model_dump_json()
    parsed1 = json.loads(json1)
    # Reconstruct from the serialized (rounded) payload
    det2 = PlayerDetection(
        player=parsed1["player"],
        keypoints_xyn=[(x, y) for x, y in parsed1["keypoints_xyn"]],
        confidence=parsed1["confidence"],
        bbox_conf=parsed1["bbox_conf"],
        feet_mid_xyn=tuple(parsed1["feet_mid_xyn"]),
        feet_mid_m=tuple(parsed1["feet_mid_m"]),
        fallback_mode=parsed1["fallback_mode"],
    )
    json2 = det2.model_dump_json()
    parsed2 = json.loads(json2)
    # Deep-equal on rounded representation (no further drift on second round)
    assert parsed1["keypoints_xyn"] == parsed2["keypoints_xyn"]
    assert parsed1["bbox_conf"] == parsed2["bbox_conf"]
    assert parsed1["feet_mid_xyn"] == parsed2["feet_mid_xyn"]


# ──────────────────────────── KeypointFrame ────────────────────────────


def test_keypoint_frame_keypoints_rounded() -> None:
    kf = KeypointFrame(
        timestamp_ms=100,
        match_id="utr_01",
        player="A",
        keypoints_xyn=_high_precision_keypoints(),
        confidence=_high_precision_conf(),
    )
    parsed = json.loads(kf.model_dump_json())
    for x, y in parsed["keypoints_xyn"]:
        assert _max_decimal_places(x) <= 4
        assert _max_decimal_places(y) <= 4
    for c in parsed["confidence"]:
        assert _max_decimal_places(c) <= 4


def test_keypoint_frame_confidence_none_serializes_null() -> None:
    kf = KeypointFrame(
        timestamp_ms=100,
        match_id="utr_01",
        player="A",
        keypoints_xyn=_high_precision_keypoints(),
        confidence=None,
    )
    parsed = json.loads(kf.model_dump_json())
    assert parsed["confidence"] is None


# ──────────────────────────── SignalSample ────────────────────────────


def test_signal_sample_value_rounded() -> None:
    sample = SignalSample(
        timestamp_ms=100,
        match_id="utr_01",
        player="A",
        signal_name="recovery_latency_ms",
        value=123.456789012,
        baseline_z_score=1.234567890,
        state="ACTIVE_RALLY",
    )
    parsed = json.loads(sample.model_dump_json())
    assert _max_decimal_places(parsed["value"]) <= 4
    assert _max_decimal_places(parsed["baseline_z_score"]) <= 4
    assert parsed["value"] == pytest.approx(123.4568, abs=1e-9)


def test_signal_sample_none_values_serialize_as_null() -> None:
    sample = SignalSample(
        timestamp_ms=100,
        match_id="utr_01",
        player="A",
        signal_name="recovery_latency_ms",
        value=None,
        baseline_z_score=None,
        state="ACTIVE_RALLY",
    )
    parsed = json.loads(sample.model_dump_json())
    assert parsed["value"] is None
    assert parsed["baseline_z_score"] is None


# ──────────────────────────── FatigueVector (dict values) ────────────────────────────


def test_fatigue_vector_signal_dict_values_rounded() -> None:
    fv = FatigueVector(
        window_start_ms=100,
        window_end_ms=1100,
        match_id="utr_01",
        player="A",
        signals={
            "recovery_latency_ms": 123.456789012,
            "serve_toss_variance_cm": 4.987654321,
        },
        state="ACTIVE_RALLY",
    )
    parsed = json.loads(fv.model_dump_json())
    for v in parsed["signals"].values():
        assert _max_decimal_places(v) <= 4


def test_fatigue_vector_none_signal_values_serialize_as_null() -> None:
    fv = FatigueVector(
        window_start_ms=100,
        window_end_ms=1100,
        match_id="utr_01",
        player="A",
        signals={"recovery_latency_ms": None, "lateral_work_rate": 0.123456789},
        state="ACTIVE_RALLY",
    )
    parsed = json.loads(fv.model_dump_json())
    assert parsed["signals"]["recovery_latency_ms"] is None
    assert _max_decimal_places(parsed["signals"]["lateral_work_rate"]) <= 4


# ──────────────────────────── AnomalyEvent ────────────────────────────


def test_anomaly_event_numeric_fields_rounded() -> None:
    evt = AnomalyEvent(
        event_id="evt_001",
        timestamp_ms=100,
        match_id="utr_01",
        player="A",
        signal_name="recovery_latency_ms",
        value=123.456789012,
        baseline_mean=100.987654321,
        baseline_std=12.345678901,
        z_score=2.987654321,
        severity=0.876543210,
    )
    parsed = json.loads(evt.model_dump_json())
    for key in ("value", "baseline_mean", "baseline_std", "z_score", "severity"):
        assert _max_decimal_places(parsed[key]) <= 4, f"field {key} not rounded: {parsed[key]}"


# ──────────────────────────── Existing construction tests still pass ────────────────────────────


def test_player_detection_validates_fallback_mode() -> None:
    """Regression: validator for fallback_mode literal still runs."""
    with pytest.raises(ValidationError):
        _make_player_detection(fallback_mode="invalid_mode")  # type: ignore[arg-type]


def test_player_detection_validates_keypoint_count() -> None:
    """Regression: min_length=17 / max_length=17 still enforced."""
    with pytest.raises(ValidationError):
        _make_player_detection(keypoints_xyn=[(0.5, 0.5)] * 16)
