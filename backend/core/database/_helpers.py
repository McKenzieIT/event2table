#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database helper functions for common operations
"""

import sqlite3
from typing import Optional
from pathlib import Path

from backend.core.logging import get_logger
from ._constants import PRAGMA_SETTINGS

logger = get_logger(__name__)


def _apply_pragma_settings(conn: sqlite3.Connection) -> None:
    """
    Apply SQLite PRAGMA settings to a connection

    Args:
        conn: SQLite connection
    """
    for key, value in PRAGMA_SETTINGS.items():
        conn.execute(f"PRAGMA {key}={value}")


def _execute_sql_file(conn: sqlite3.Connection, sql_file: Path) -> None:
    """
    Execute SQL from a file

    Args:
        conn: SQLite connection
        sql_file: Path to SQL file
    """
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
        conn.executescript(sql_script)
    logger.info(f"Executed SQL file: {sql_file.name}")


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    """
    Check if a table exists in the database

    Args:
        conn: SQLite connection
        table_name: Name of the table to check

    Returns:
        True if table exists, False otherwise
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def _create_table_if_not_exists(
    conn: sqlite3.Connection,
    table_name: str,
    table_sql: str
) -> bool:
    """
    Create a table if it doesn't exist

    Args:
        conn: SQLite connection
        table_name: Name of the table
        table_sql: SQL to create the table

    Returns:
        True if table was created, False if it already existed
    """
    if _table_exists(conn, table_name):
        logger.info(f"Table {table_name} already exists")
        return False

    logger.info(f"Creating table {table_name}...")
    conn.execute(table_sql)
    conn.commit()
    logger.info(f"Table {table_name} created successfully")
    return True


def _create_index_if_not_exists(
    conn: sqlite3.Connection,
    index_sql: str
) -> None:
    """
    Create an index if it doesn't exist

    Args:
        conn: SQLite connection
        index_sql: SQL to create the index (should include IF NOT EXISTS)
    """
    try:
        conn.execute(index_sql)
        conn.commit()
    except sqlite3.OperationalError as e:
        # Index might already exist, log and continue
        logger.warning(f"Index creation warning: {e}")


def _get_table_count(conn: sqlite3.Connection, table_name: str) -> int:
    """
    Get the row count of a table

    Args:
        conn: SQLite connection
        table_name: Name of the table

    Returns:
        Number of rows in the table
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.OperationalError:
        return 0


def _validate_table_structure(
    conn: sqlite3.Connection,
    table_name: str,
    required_columns: list
) -> bool:
    """
    Validate that a table has all required columns

    Args:
        conn: SQLite connection
        table_name: Name of the table
        required_columns: List of required column names

    Returns:
        True if all columns exist, False otherwise
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}

    missing_columns = set(required_columns) - existing_columns
    if missing_columns:
        logger.warning(
            f"Table {table_name} missing columns: {missing_columns}"
        )
        return False

    return True
