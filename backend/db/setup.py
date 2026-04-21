"""DuckDB initialization + connection helpers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import duckdb

from backend.config import settings
from backend.db.schema import SCHEMA_DDL


def init_schema(db_path: str | Path | None = None) -> Path:
    """Initialize DuckDB schema in-place (idempotent). Returns the db path."""
    path = Path(db_path) if db_path is not None else settings().duckdb_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as conn:
        conn.execute(SCHEMA_DDL)
    return path


@lru_cache(maxsize=1)
def ro_connect() -> duckdb.DuckDBPyConnection:
    """Open a READ-ONLY connection to the pre-computed DuckDB. Used in Vercel production."""
    path = settings().duckdb_path
    if not path.exists():
        raise FileNotFoundError(f"Pre-computed DuckDB not found at {path}")
    return duckdb.connect(str(path), read_only=True)


def writable_connect(db_path: str | Path | None = None) -> duckdb.DuckDBPyConnection:
    """Open a writable connection (local pre-compute only)."""
    path = Path(db_path) if db_path is not None else settings().duckdb_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))
