"""Static-validation tests for tools/court_annotator.html.

These exist to prevent the ID-COLLISION class of bug we hit on 2026-04-22,
where `<input type="file" id="video">` and `<video id="video">` both carried
the same id. `document.getElementById("video")` returned the input (first in
document order), so script-side `video.src = ...` silently set a property on
the wrong element. No events fired, no error surfaced, 5 debugging iterations
lost.

Cheap, fast, no browser dependency — they catch the bug at the HTML level.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pytest

ANNOTATOR_PATH = (
    Path(__file__).resolve().parent.parent.parent / "tools" / "court_annotator.html"
)

_ID_ATTR_RE = re.compile(r'\bid\s*=\s*"([^"]+)"', re.IGNORECASE)
_FOR_ATTR_RE = re.compile(r'\bfor\s*=\s*"([^"]+)"', re.IGNORECASE)
_GET_BY_ID_RE = re.compile(r'getElementById\(\s*["\']([^"\']+)["\']\s*\)')
_QUERY_ID_SELECTOR_RE = re.compile(r'querySelector(?:All)?\(\s*["\']#([\w-]+)', re.IGNORECASE)


_SCRIPT_BLOCK_RE = re.compile(r"<script\b[^>]*>.*?</script>", flags=re.DOTALL | re.IGNORECASE)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", flags=re.DOTALL)


@pytest.fixture(scope="module")
def html_text() -> str:
    """Load the annotator HTML once per module."""
    assert ANNOTATOR_PATH.exists(), f"annotator missing at {ANNOTATOR_PATH}"
    return ANNOTATOR_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def html_body(html_text: str) -> str:
    """HTML with <script>...</script> blocks and HTML comments stripped.

    Attribute-level checks (id, for) run against THIS, not the raw text — otherwise
    a JS comment containing `id="video"` produces a false-positive duplicate.
    """
    no_scripts = _SCRIPT_BLOCK_RE.sub("", html_text)
    no_comments = _HTML_COMMENT_RE.sub("", no_scripts)
    return no_comments


def test_annotator_file_exists(html_text: str) -> None:
    """Guard against accidental deletion / rename."""
    assert len(html_text) > 500
    assert "<!doctype html>" in html_text.lower()


def test_no_duplicate_ids(html_body: str) -> None:
    """THE regression test: every id="..." must be unique across the whole document.

    The 2026-04-22 bug: `<input id="video">` AND `<video id="video">`.
    `document.getElementById('video')` returned the input, silently binding
    every script reference to the wrong element. No errors, no events.
    """
    ids = _ID_ATTR_RE.findall(html_body)
    counts = Counter(ids)
    duplicates = {id_: n for id_, n in counts.items() if n > 1}
    assert not duplicates, (
        f"Duplicate HTML ids detected (forbidden): {duplicates}. "
        "Remember: this exact pattern cost 5 debugging iterations on 2026-04-22 — "
        "input + video both had id='video' and getElementById returned the input."
    )


def test_expected_critical_ids_present(html_body: str) -> None:
    """The script expects these specific IDs; their absence would break things silently."""
    ids = set(_ID_ATTR_RE.findall(html_body))
    required = {
        "video",         # <video> element
        "videoPicker",   # <input type="file">
        "canvas",        # corner-capture canvas
        "placeholder",   # initial empty-state hint
        "errorBanner",   # red error line
        "statusBanner",  # green progress banner
        "cornerList",    # corner-status list
        "jsonOut",       # JSON preview textarea
        "btnCaptureFrame",
        "btnReset",
        "btnDownload",
        "btnTestDirect",
    }
    missing = required - ids
    assert not missing, f"Critical IDs missing from annotator HTML: {sorted(missing)}"


def test_video_id_is_on_video_element_not_input(html_body: str) -> None:
    """The element with id='video' MUST be a <video>, never an <input>.

    This is the SPECIFIC check that would have caught the 2026-04-22 bug instantly.
    """
    m = re.search(r'<(\w+)\b[^>]*\bid\s*=\s*"video"', html_body)
    assert m is not None, "no element found with id='video'"
    assert m.group(1).lower() == "video", (
        f"id='video' is on a <{m.group(1)}> tag, not a <video> tag — "
        "this reintroduces the 2026-04-22 ID collision bug."
    )


def test_label_for_points_to_existing_id(html_body: str) -> None:
    """Every <label for="X">'s target ID must actually exist."""
    ids = set(_ID_ATTR_RE.findall(html_body))
    labels = re.findall(r"<label\b[^>]*>", html_body, flags=re.IGNORECASE)
    bad = []
    for label in labels:
        m = _FOR_ATTR_RE.search(label)
        if m and m.group(1) not in ids:
            bad.append(m.group(1))
    assert not bad, f"Label 'for=' attributes reference missing IDs: {bad}"


def test_script_get_element_by_id_references_exist(html_text: str, html_body: str) -> None:
    """Every `getElementById('X')` call's target must exist in the DOM.

    Catches typos + stale refs after renames. Script is inline in `html_text`;
    valid DOM IDs come from `html_body` (with script blocks stripped).
    """
    ids = set(_ID_ATTR_RE.findall(html_body))
    referenced = set(_GET_BY_ID_RE.findall(html_text))
    referenced |= set(_QUERY_ID_SELECTOR_RE.findall(html_text))
    missing = referenced - ids
    assert not missing, (
        f"Script references IDs that don't exist in the DOM: {sorted(missing)}. "
        f"Existing IDs: {sorted(ids)}."
    )


def test_video_element_has_required_media_attrs(html_text: str) -> None:
    """<video> must have muted + playsinline (Chrome autoplay policy) + a reasonable preload."""
    m = re.search(r"<video\b[^>]*>", html_text, flags=re.IGNORECASE)
    assert m is not None, "no <video> tag found"
    tag = m.group(0)
    assert "muted" in tag, "<video> must have 'muted' (Chrome autoplay policy)"
    assert "playsinline" in tag, "<video> must have 'playsinline' (iOS Safari)"
    assert 'preload="auto"' in tag or "preload='auto'" in tag, (
        "<video> should have preload='auto' — 'metadata' has stalled on faststart clips in Chrome"
    )


def test_script_attaches_critical_media_listeners(html_text: str) -> None:
    """Research-agent finding #1: media events fire on the next microtask after src-set.

    If a listener isn't attached BEFORE that microtask drains, it can miss the event
    entirely. The safe pattern is to attach all media listeners at module scope (so
    they're in place before any user interaction can trigger src=). We can't easily
    verify runtime order statically, but we CAN verify that the listeners for the
    three events we rely on are attached somewhere in the script.
    """
    required_listeners = ("loadedmetadata", "error", "loadstart")
    missing = []
    for event_name in required_listeners:
        pattern = r'video\.addEventListener\(\s*["\']' + event_name + r'["\']'
        if not re.search(pattern, html_text):
            missing.append(event_name)
    assert not missing, (
        f"Missing video.addEventListener for: {missing}. "
        "These are required for diagnostic visibility — 'loadedmetadata' confirms load; "
        "'error' surfaces decode failures; 'loadstart' proves the media load algorithm started "
        "(its absence on 2026-04-22 was the smoking gun for the ID-collision bug)."
    )


def test_script_has_id_collision_runtime_guard(html_text: str) -> None:
    """The script should fail-loud at page load if the id='video' element is not a <video>.

    We wrote this as defense against FUTURE regressions of the ID-collision bug.
    """
    assert "video.tagName" in html_text, (
        "Missing the runtime guard that checks video.tagName — restore the check added 2026-04-22 "
        "that catches the ID-collision bug at page-load time."
    )
