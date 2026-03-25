#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Operations Module

Provides database write operations and transaction management functions.
"""

from contextlib import contextmanager
from typing import List, Tuple

from backend.core.database import get_db_connection
from backend.core.logging import get_logger

logger = get_logger(__name__)


def execute_write(query: str, params: Tuple | None = None, return_last_id: bool = False) -> int:
    """
    Execute a write query (INSERT, UPDATE, DELETE) and return affected row count or last inserted ID

    Args:
        query: SQL query string
        params: Query parameters (optional)
        return_last_id: If True, return last inserted row ID instead of rowcount

    Returns:
        Number of rows affected, or last inserted ID if return_last_id=True

    Example:
        execute_write('INSERT INTO games (name) VALUES (?)', ('Game1',))
        last_id = execute_write('INSERT INTO games (name) VALUES (?)', ('Game1',), return_last_id=True)
    """
    conn = get_db_connection()
    try:
        cursor = conn.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid if return_last_id else cursor.rowcount
    finally:
        conn.close()


def execute_transaction(operations: List[Tuple[str, Tuple]]) -> int:
    """
    Execute multiple SQL operations in a single transaction

    Args:
        operations: List of (query, params) tuples

    Returns:
        Total number of rows affected

    Example:
        execute_transaction([
            ('UPDATE users SET score = score + 10 WHERE id = ?', (1,)),
            ('INSERT INTO logs (user_id, action) VALUES (?, ?)', (1, 'bonus'))
        ])
    """
    conn = get_db_connection()
    try:
        total_affected = 0
        for query, params in operations:
            cursor = conn.execute(query, params or ())
            total_affected += cursor.rowcount
        conn.commit()
        return total_affected
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def db_transaction():
    """
    Context manager for database transactions with automatic commit/rollback

    Usage:
        with db_transaction() as conn:
            conn.execute(...)
            # Auto commits on success, rolls back on exception
    """
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
        logger.debug("Database transaction committed successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        conn.close()


def batch_execute(conn, sql: str, params_list: List[Tuple]) -> int:
    """
    Execute SQL statement multiple times with different parameters

    Args:
        conn: Database connection
        sql: SQL statement with placeholders
        params_list: List of parameter tuples

    Returns:
        Number of rows affected
    """
    cursor = conn.cursor()
    for params in params_list:
        cursor.execute(sql, params)
    return cursor.rowcount


__all__ = [
    'execute_write',
    'execute_transaction',
    'db_transaction',
    'batch_execute',
]
