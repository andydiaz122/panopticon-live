"""Tests for backend/precompute.load_corners_json — handles BOTH shapes.

The 2026-04-22 gotcha: tools/court_annotator.html emits a WRAPPED JSON like
{"clip": ..., "annotated_at": ..., "corners": {...}, "notes": ...} — but the
earlier precompute.py code tried to pass the whole wrapper into
CornersNormalized(**data), which failed because Pydantic v2 frozen models
forbid extras.

load_corners_json accepts BOTH wrapper and bare shapes and returns
(raw_text, CornersNormalized). The raw text is preserved for MatchMeta
provenance.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from backend.db.schema import CornersNormalized
from backend.precompute import load_corners_json

# ──────────────────────────── Fixtures ────────────────────────────

_VALID_CORNERS = {
    "top_left": [0.25, 0.20],
    "top_right": [0.75, 0.20],
    "bottom_right": [0.95, 0.88],
    "bottom_left": [0.05, 0.88],
}


def _write_bare(tmp_path: Path) -> Path:
    p = tmp_path / "bare.json"
    p.write_text(json.dumps(_VALID_CORNERS))
    return p


def _write_wrapped(tmp_path: Path) -> Path:
    """Mirrors exactly what tools/court_annotator.html emits."""
    p = tmp_path / "wrapped.json"
    p.write_text(json.dumps({
        "clip": "utr_match_01_segment_a",
        "annotated_at": "2026-04-22T20:11:15.637Z",
        "corners": _VALID_CORNERS,
        "notes": "Normalized [0,1] coordinates.",
    }))
    return p


# ──────────────────────────── Tests ────────────────────────────


def test_load_corners_bare_shape(tmp_path: Path) -> None:
    """Bare shape (back-compat with hand-edited JSONs) still works."""
    path = _write_bare(tmp_path)
    raw, corners = load_corners_json(path)
    assert isinstance(corners, CornersNormalized)
    assert corners.top_left == (0.25, 0.20)
    assert corners.bottom_right == (0.95, 0.88)
    # raw_text preserved for provenance
    assert '"top_left"' in raw


def test_load_corners_wrapped_shape(tmp_path: Path) -> None:
    """Wrapped shape (what tools/court_annotator.html actually emits) works."""
    path = _write_wrapped(tmp_path)
    raw, corners = load_corners_json(path)
    assert isinstance(corners, CornersNormalized)
    assert corners.top_left == (0.25, 0.20)
    assert corners.bottom_left == (0.05, 0.88)
    # raw_text preserves the full wrapper (including clip, annotated_at, notes)
    assert '"annotated_at"' in raw
    assert '"notes"' in raw


def test_load_corners_invalid_content_raises(tmp_path: Path) -> None:
    """Malformed JSON surfaces as a JSONDecodeError — no swallowing."""
    path = tmp_path / "bad.json"
    path.write_text("this is not json")
    with pytest.raises(json.JSONDecodeError):
        load_corners_json(path)


def test_load_corners_missing_fields_raises(tmp_path: Path) -> None:
    """If corners field is missing key entries, Pydantic validation should raise."""
    path = tmp_path / "incomplete.json"
    path.write_text(json.dumps({"top_left": [0.1, 0.1]}))  # missing 3 corners
    with pytest.raises(ValidationError):
        load_corners_json(path)


def test_load_corners_wrapper_with_missing_corners_key_falls_through(tmp_path: Path) -> None:
    """If the file has OTHER keys but no 'corners' key, we still try to parse the top level."""
    path = tmp_path / "no_corners_key.json"
    path.write_text(json.dumps(_VALID_CORNERS))  # no wrapper, bare
    _raw, corners = load_corners_json(path)
    assert corners.top_left == (0.25, 0.20)
