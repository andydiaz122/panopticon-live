"""A7 — Precomputed Opus 4.7 vision pass on the t=45.3s broadcast frame.

PLAN.md §6 A7 + Iter-3 Q10 hackathon decision. One-shot precompute:

  1. Read the extracted JPEG at t=45.3s
  2. Call Opus 4.7 with vision enabled + forensic biomech prompt
  3. Write result to dashboard/public/match_data/vision_pass.json

The output is consumed by the Detective Cut's B1 cold-open overlay
(demo-presentation/PLAN.md §5) — the crosshair + on-screen annotation
that hits before the first narration line.

Run once, commit the JSON, never re-invoke unless the prompt changes.

Usage:
    ANTHROPIC_API_KEY=<key> python -m backend.scripts.run_vision_pass

Environment:
    ANTHROPIC_API_KEY  required
    PANOPTICON_FRAME   optional, override the input frame path
    PANOPTICON_OUT     optional, override the output JSON path
"""

from __future__ import annotations

import base64
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from anthropic import Anthropic

# ──────────────────────────── Config ────────────────────────────

DEFAULT_FRAME_PATH = Path(
    "dashboard/public/match_data/vision/frame_t_45300ms.jpg",
)
DEFAULT_OUTPUT_PATH = Path(
    "dashboard/public/match_data/vision_pass.json",
)

FRAME_TIMESTAMP_MS = 45_300
MODEL = "claude-opus-4-7"
MAX_TOKENS = 800

SYSTEM_PROMPT = """You are a sports-biomechanics observer.

Your job: read ONE still frame of a pro tennis broadcast and produce a
forensic biomechanics observation in a broadcast-legible register. Your
output is overlaid onto a demo video; judges read it in under 5 seconds.

Constraints:
  - Indicative voice ("his knee is bent", "he's crouched below baseline")
  - Numbers are speculative ("looks roughly 110°", "about 3 inches behind
    the baseline") — NEVER claim exact degrees or centimeters you can't
    measure from a 2D still
  - Focus on Player A (the near-court player, bottom of frame, closer to
    camera) — if he is not visible in frame, say so and describe whatever
    is visible about the match state (opponent position, scoreboard)
  - ≤ 80 words total. One declarative sentence, one biomech annotation
  - DO NOT invent player identity; refer as "Player A" / "the server" / "he"
"""

USER_PROMPT = """Describe what is biomechanically observable in this frame.

If a visible crouch or knee angle is clear, ESTIMATE it (range, e.g.,
"knee flexion ~100-120°"). If posture or body angle is clear, call it
out in the register of a team physiologist briefing a coach.

Output in this exact JSON shape, wrapped in ```json fences:

{
  "visible_action": "one-sentence description of what Player A is doing",
  "biomech_annotation": {
    "label": "short label for the key biomechanical observation (e.g., 'crouch depth' or 'shoulder loading')",
    "value": "estimated value with units if applicable, or 'qualitative' if not measurable",
    "confidence": 0.0 to 1.0
  },
  "coach_takeaway": "one-sentence takeaway a broadcast analyst would narrate"
}

NOTHING outside the JSON block."""


# ──────────────────────────── Types ────────────────────────────


@dataclass(frozen=True)
class VisionPassResult:
    timestamp_ms: int
    model: str
    frame_path: str
    raw_response: str
    parsed: dict | None
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int

    def as_dict(self) -> dict:
        return {
            "timestamp_ms": self.timestamp_ms,
            "model": self.model,
            "frame_path": self.frame_path,
            "raw_response": self.raw_response,
            "parsed": self.parsed,
            "usage": {
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "cache_read_tokens": self.cache_read_tokens,
            },
        }


# ──────────────────────────── Core ────────────────────────────


def _load_frame_b64(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f"Frame missing: {path} — extract via ffmpeg first "
            "(see backend/scripts/run_vision_pass.py docstring).",
        )
    return base64.standard_b64encode(path.read_bytes()).decode("ascii")


def _parse_json_block(text: str) -> dict | None:
    """Extract the first ```json ... ``` block from a response string."""
    start = text.find("```json")
    if start < 0:
        # Fallback: some responses omit the fence.
        start = text.find("{")
        if start < 0:
            return None
        end = text.rfind("}")
        if end < 0:
            return None
        return _safe_json_loads(text[start : end + 1])
    start = text.find("\n", start) + 1
    end = text.find("```", start)
    if end < 0:
        return None
    return _safe_json_loads(text[start:end])


def _safe_json_loads(s: str) -> dict | None:
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None


def run_vision_pass(
    frame_path: Path = DEFAULT_FRAME_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> VisionPassResult:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set in the environment.")

    frame_b64 = _load_frame_b64(frame_path)
    client = Anthropic(api_key=api_key)

    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": frame_b64,
                        },
                    },
                    {"type": "text", "text": USER_PROMPT},
                ],
            },
        ],
    )

    text_blocks = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    raw_text = "\n".join(text_blocks) or ""

    parsed = _parse_json_block(raw_text)

    usage = getattr(resp, "usage", None)
    input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
    output_tokens = getattr(usage, "output_tokens", 0) if usage else 0
    cache_read = getattr(usage, "cache_read_input_tokens", 0) if usage else 0

    result = VisionPassResult(
        timestamp_ms=FRAME_TIMESTAMP_MS,
        model=MODEL,
        frame_path=str(frame_path),
        raw_response=raw_text,
        parsed=parsed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result.as_dict(), indent=2))
    return result


# ──────────────────────────── CLI ────────────────────────────


def main(argv: list[str] | None = None) -> int:
    frame_path = Path(os.environ.get("PANOPTICON_FRAME", str(DEFAULT_FRAME_PATH)))
    output_path = Path(os.environ.get("PANOPTICON_OUT", str(DEFAULT_OUTPUT_PATH)))

    try:
        result = run_vision_pass(frame_path, output_path)
    except Exception as exc:
        print(f"[FATAL] vision pass failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(f"[OK] vision pass saved to {output_path}")
    print(f"     input_tokens={result.input_tokens} output_tokens={result.output_tokens} "
          f"cache_read={result.cache_read_tokens}")
    if result.parsed:
        print(f"     label={result.parsed.get('biomech_annotation', {}).get('label')!r}")
        print(f"     value={result.parsed.get('biomech_annotation', {}).get('value')!r}")
    else:
        print("     WARN: response could not be parsed as JSON; raw text saved to output")
    return 0


if __name__ == "__main__":
    sys.exit(main())
