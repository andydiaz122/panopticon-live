"""Tests for backend/db/setup.py — DuckDB init + connection helpers.

Drives `init_schema`, `writable_connect`, and `ro_connect` to near-100% coverage.
Tests use pytest `tmp_path` for isolated DuckDB files per test.

`ro_connect` has @lru_cache; every test that exercises it clears the cache BEFORE
the call to prevent a cached connection from leaking across tests.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pytest

from backend.config import Settings
from backend.db import setup as setup_mod
from backend.db.setup import init_schema, ro_connect, writable_connect

# ──────────────────────────── init_schema ────────────────────────────


def test_init_schema_creates_new_duckdb_file(tmp_path: Path) -> None:
    db_path = tmp_path / "p.duckdb"
    assert not db_path.exists()

    result = init_schema(db_path)

    assert db_path.exists()
    assert isinstance(result, Path)
    assert result == db_path


def test_init_schema_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "p.duckdb"
    init_schema(db_path)
    # Second call must not raise — CREATE TABLE IF NOT EXISTS is idempotent
    init_schema(db_path)
    assert db_path.exists()


def test_init_schema_creates_all_expected_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "p.duckdb"
    init_schema(db_path)

    expected_tables = {"match_meta", "keypoints", "signals", "anomalies", "coach_insights"}
    with duckdb.connect(str(db_path)) as conn:
        rows = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
        ).fetchall()
    actual = {row[0] for row in rows}
    for name in expected_tables:
        assert name in actual, f"missing expected table: {name}"


def test_init_schema_creates_parent_dir_if_missing(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "dir" / "p.duckdb"
    assert not db_path.parent.exists()

    init_schema(db_path)

    assert db_path.parent.is_dir()
    assert db_path.exists()


def test_init_schema_accepts_string_path(tmp_path: Path) -> None:
    """Path union type — must accept str as well as Path."""
    db_path = tmp_path / "p.duckdb"
    result = init_schema(str(db_path))
    assert isinstance(result, Path)
    assert db_path.exists()


def test_init_schema_uses_settings_path_when_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Passing None should fall back to settings().duckdb_path."""
    fallback = tmp_path / "fallback.duckdb"
    monkeypatch.setattr("backend.db.setup.settings", lambda: Settings(duckdb_path=fallback))
    result = init_schema(None)
    assert result == fallback
    assert fallback.exists()


# ──────────────────────────── writable_connect ────────────────────────────


def test_writable_connect_returns_duckdb_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "p.duckdb"
    conn = writable_connect(db_path)
    try:
        assert isinstance(conn, duckdb.DuckDBPyConnection)
        row = conn.execute("SELECT 1").fetchone()
        assert row == (1,)
    finally:
        conn.close()


def test_writable_connect_creates_parent_dir(tmp_path: Path) -> None:
    db_path = tmp_path / "deep" / "nest" / "p.duckdb"
    assert not db_path.parent.exists()
    conn = writable_connect(db_path)
    try:
        assert db_path.parent.is_dir()
    finally:
        conn.close()


def test_writable_connect_accepts_string_path(tmp_path: Path) -> None:
    db_path = tmp_path / "p.duckdb"
    conn = writable_connect(str(db_path))
    try:
        assert isinstance(conn, duckdb.DuckDBPyConnection)
    finally:
        conn.close()


def test_writable_connect_uses_settings_when_none(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fallback = tmp_path / "fb.duckdb"
    monkeypatch.setattr("backend.db.setup.settings", lambda: Settings(duckdb_path=fallback))
    conn = writable_connect(None)
    try:
        assert isinstance(conn, duckdb.DuckDBPyConnection)
        assert fallback.exists()
    finally:
        conn.close()


# ──────────────────────────── ro_connect ────────────────────────────


def test_ro_connect_raises_when_file_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bogus = tmp_path / "nonexistent.duckdb"
    monkeypatch.setattr("backend.db.setup.settings", lambda: Settings(duckdb_path=bogus))
    setup_mod.ro_connect.cache_clear()

    with pytest.raises(FileNotFoundError):
        setup_mod.ro_connect()
    setup_mod.ro_connect.cache_clear()


def test_ro_connect_opens_readonly_when_file_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db_path = tmp_path / "p.duckdb"
    init_schema(db_path)

    monkeypatch.setattr("backend.db.setup.settings", lambda: Settings(duckdb_path=db_path))
    setup_mod.ro_connect.cache_clear()

    conn = ro_connect()
    try:
        # Verify connected
        row = conn.execute("SELECT 1").fetchone()
        assert row == (1,)

        # Verify read-only: an INSERT must raise. DuckDB raises a specific
        # subclass of duckdb.Error; we catch the module's base error class.
        with pytest.raises(duckdb.Error):
            conn.execute(
                "INSERT INTO match_meta VALUES ('m1', "
                "'a' || REPEAT('b', 63), 30.0, 1000, 1920, 1080, "
                "'A', 'B', '[]', CURRENT_TIMESTAMP)"
            )
    finally:
        conn.close()
        setup_mod.ro_connect.cache_clear()
