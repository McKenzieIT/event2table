#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transaction Management for Database Operations

Provides transaction decorators and context managers for atomic operations.
Simple and practical implementation without over-engineering.
"""

import functools
import logging
import sqlite3
from contextlib import contextmanager
from typing import Any, Callable, Optional

from backend.core.database.database import get_db_connection

logger = logging.getLogger(__name__)


def transactional(func: Callable) -> Callable:
    """
    Transaction Decorator for automatic commit/rollback

    Usage:
        @transactional
        def create_batch(data):
            # Multiple database operations
            # Any exception will trigger rollback
            pass

    Args:
        func: Function to wrap with transaction

    Returns:
        Wrapped function with transaction support

    Example:
        @transactional
        def batch_create_games(games_data):
            repo.create_batch(games_data)
            # If any exception occurs, automatic rollback
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        conn = None
        try:
            conn = get_db_connection()
            conn.execute("BEGIN")

            # Execute the wrapped function
            result = func(*args, **kwargs)

            conn.commit()
            logger.debug(f"Transaction committed for {func.__name__}")
            return result

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                    logger.debug(f"Transaction rolled back for {func.__name__}: {e}")
                except Exception as rollback_error:
                    logger.error(f"Failed to rollback transaction: {rollback_error}")
            raise e

        finally:
            if conn:
                conn.close()

    return wrapper


@contextmanager
def transaction():
    """
    Transaction Context Manager

    Usage:
        with transaction():
            # Multiple database operations
            # Any exception will trigger rollback
            pass

    Example:
        with transaction():
            repo.create_batch(games_data)
            repo.update_batch(updates)
            # If any exception occurs, automatic rollback
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.execute("BEGIN")

        yield conn

        conn.commit()
        logger.debug("Transaction committed")

    except Exception as e:
        if conn:
            try:
                conn.rollback()
                logger.debug(f"Transaction rolled back: {e}")
            except Exception as rollback_error:
                logger.error(f"Failed to rollback transaction: {rollback_error}")
        raise e

    finally:
        if conn:
            conn.close()


def in_transaction() -> bool:
    """
    Check if currently in a transaction

    Returns:
        True if inside a transaction, False otherwise
    """
    try:
        conn = get_db_connection()
        return conn.in_transaction
    except Exception:
        return False
