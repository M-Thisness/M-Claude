#!/usr/bin/env python3
"""
M-Claude Database Connection Manager

Provides thread-safe SQLite connections with transaction support,
automatic schema initialization, and connection pooling.
"""

from __future__ import annotations

import logging
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Optional

from .schema import SCHEMA_VERSION, get_schema_sql

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class ConnectionManager:
    """
    Thread-safe SQLite connection manager with transaction support.

    Usage:
        db = ConnectionManager("/path/to/index.db")
        with db.transaction() as cursor:
            cursor.execute("INSERT INTO ...")
    """

    _instance: Optional[ConnectionManager] = None
    _lock = threading.Lock()

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self._local = threading.local()
        self._initialized = False

    @classmethod
    def get_instance(cls, db_path: Optional[Path | str] = None) -> ConnectionManager:
        """Get singleton instance of ConnectionManager."""
        with cls._lock:
            if cls._instance is None:
                if db_path is None:
                    raise DatabaseError("Database path required for first initialization")
                cls._instance = cls(db_path)
            return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing)."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close_all()
            cls._instance = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Get thread-local connection, creating if needed."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = self._create_connection()
        return self._local.connection

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with optimized settings."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            isolation_level=None,  # Autocommit mode, we manage transactions
            timeout=30.0
        )

        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")

        # Performance optimizations
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        conn.execute("PRAGMA temp_store = MEMORY")

        # Row factory for dict-like access
        conn.row_factory = sqlite3.Row

        # Initialize schema if needed
        if not self._initialized:
            self._init_schema(conn)
            self._initialized = True

        return conn

    def _init_schema(self, conn: sqlite3.Connection) -> None:
        """Initialize database schema."""
        cursor = conn.cursor()

        try:
            # Check if schema exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_info'"
            )
            schema_exists = cursor.fetchone() is not None

            if not schema_exists:
                # Fresh database - create schema
                logger.info(f"Initializing database schema v{SCHEMA_VERSION}")
                # executescript handles its own transactions
                cursor.executescript(get_schema_sql())
                cursor.execute(
                    "INSERT INTO schema_info (key, value) VALUES (?, ?)",
                    ("version", SCHEMA_VERSION)
                )
                cursor.execute(
                    "INSERT INTO schema_info (key, value) VALUES (?, ?)",
                    ("created_at", datetime.now().isoformat())
                )
            else:
                # Check version for migrations
                cursor.execute("SELECT value FROM schema_info WHERE key = 'version'")
                row = cursor.fetchone()
                current_version = row["value"] if row else "0.0.0"

                if current_version != SCHEMA_VERSION:
                    logger.info(f"Schema migration needed: {current_version} -> {SCHEMA_VERSION}")
                    self._migrate_schema(cursor, current_version)

        except Exception as e:
            raise DatabaseError(f"Schema initialization failed: {e}") from e

    def _migrate_schema(self, cursor: sqlite3.Cursor, from_version: str) -> None:
        """Run schema migrations."""
        # For now, just update version - add migrations as needed
        cursor.execute(
            "UPDATE schema_info SET value = ? WHERE key = 'version'",
            (SCHEMA_VERSION,)
        )
        logger.info(f"Schema migrated to v{SCHEMA_VERSION}")

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context manager for database transactions.

        Automatically commits on success, rolls back on exception.

        Usage:
            with db.transaction() as cursor:
                cursor.execute("INSERT INTO ...")
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            yield cursor
            cursor.execute("COMMIT")
        except Exception:
            cursor.execute("ROLLBACK")
            raise

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single SQL statement."""
        return self.connection.execute(sql, params)

    def executemany(self, sql: str, params_list: list) -> sqlite3.Cursor:
        """Execute SQL statement for each set of params."""
        return self.connection.executemany(sql, params_list)

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute and fetch one result."""
        return self.connection.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        """Execute and fetch all results."""
        return self.connection.execute(sql, params).fetchall()

    def close(self) -> None:
        """Close the thread-local connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None

    def close_all(self) -> None:
        """Close all connections (call on shutdown)."""
        self.close()


def get_db(db_path: Optional[Path | str] = None) -> ConnectionManager:
    """
    Get the database connection manager.

    Args:
        db_path: Path to database file (required on first call)

    Returns:
        ConnectionManager singleton instance
    """
    return ConnectionManager.get_instance(db_path)
