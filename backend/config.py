"""Environment-derived configuration for Panopticon Live.

Pydantic v2 settings model. Any code that needs an env value reads it through `settings()`
rather than `os.getenv()` directly. This gives us type safety, validation, and a single
place to audit all env-derived state.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Device = Literal["mps", "cuda", "cpu", "auto"]


class Settings(BaseModel):
    """Runtime configuration loaded from environment variables."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Claude API
    anthropic_api_key: str | None = Field(
        default=None,
        description="Only required for Phase 2+ agent work. Never log this value.",
    )

    # Inference device. Mac Mini M4 Pro uses MPS. CUDA is unused this week.
    panopticon_device: Device = Field(default="mps")

    # DuckDB path — writable locally, read_only=True on Vercel.
    duckdb_path: Path = Field(default=Path("data/panopticon.duckdb"))

    # Directory containing clipped UTR match segments (gitignored).
    clips_dir: Path = Field(default=Path("data/clips"))

    # Directory containing manual court-corner annotations (JSON per clip).
    corners_dir: Path = Field(default=Path("data/corners"))

    # YOLO weights cache dir (Ultralytics downloads yolo11m-pose.pt on first run).
    yolo_weights_dir: Path = Field(default=Path("checkpoints"))

    # FastAPI bind
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)

    # Vercel env ("production" when deployed)
    vercel_env: str | None = None

    @field_validator("panopticon_device")
    @classmethod
    def _validate_device(cls, v: Device) -> Device:
        # "auto" is resolved lazily at runtime — avoids requiring torch at import time
        return v


def _load_from_env() -> Settings:
    return Settings(
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        panopticon_device=os.getenv("PANOPTICON_DEVICE", "mps"),  # type: ignore[arg-type]
        duckdb_path=Path(os.getenv("DUCKDB_PATH", "data/panopticon.duckdb")),
        clips_dir=Path(os.getenv("CLIPS_DIR", "data/clips")),
        corners_dir=Path(os.getenv("CORNERS_DIR", "data/corners")),
        yolo_weights_dir=Path(os.getenv("YOLO_WEIGHTS_DIR", "checkpoints")),
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        vercel_env=os.getenv("VERCEL_ENV"),
    )


@lru_cache(maxsize=1)
def settings() -> Settings:
    """Return a process-global Settings instance (cached)."""
    return _load_from_env()


def resolve_device(preferred: Device | None = None) -> str:
    """Resolve 'auto' or a Device literal into a concrete torch device string.

    Imports torch lazily so config.py stays import-safe in environments without torch
    (e.g., the Vercel prod environment).
    """
    pref = preferred or settings().panopticon_device
    if pref != "auto":
        return pref

    try:
        import torch  # type: ignore[import-not-found]

        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"
