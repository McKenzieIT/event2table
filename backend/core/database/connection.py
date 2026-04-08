"""
数据库连接管理

提供数据库连接和上下文管理功能。
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from backend.core.config import get_db_path
from backend.core.logging import get_logger

logger = get_logger(__name__)


def _apply_pragma_settings(conn: sqlite3.Connection):
    """
    应用 PRAGMA 设置到数据库连接

    Args:
        conn: 数据库连接
    """
    cursor = conn.cursor()
    # Enable WAL mode for better concurrent access
    cursor.execute("PRAGMA journal_mode=WAL")
    # Set busy timeout for concurrent access
    cursor.execute("PRAGMA busy_timeout=5000")
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys=ON")
    # Set synchronous mode for performance
    cursor.execute("PRAGMA synchronous=NORMAL")


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Get database connection with row factory and WAL mode

    Args:
        db_path: Optional database path. If not provided, uses get_db_path()

    Returns:
        SQLite connection with Row factory
    """
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _apply_pragma_settings(conn)

    return conn


@contextmanager
def get_db(db_path: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections with WAL mode

    Args:
        db_path: Optional database path. If not provided, uses get_db_path()

    Yields:
        SQLite connection with Row factory
    """
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _apply_pragma_settings(conn)

    try:
        yield conn
    finally:
        conn.close()
