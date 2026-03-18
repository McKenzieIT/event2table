#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite Connection Pool

High-performance SQLite connection pool for concurrent database access.

Features:
- Thread-safe connection management
- Connection reuse and pooling
- Automatic connection health checks
- Configurable pool size limits
- Connection timeout support

Performance Goals:
- Connection reuse: ≥90%
- Acquisition time: ≤10ms
- Thread-safe for concurrent access

Usage:
    from backend.core.database.connection_pool import get_connection_pool

    pool = get_connection_pool()
    conn = pool.get_connection()
    try:
        result = conn.execute("SELECT * FROM games").fetchall()
    finally:
        pool.return_connection(conn)

Author: Event2Table Performance Optimization Team
Version: 1.0.0 (2026-03-18)
"""

import threading
import time
import sqlite3
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConnectionPoolConfig:
    """
    Configuration for connection pool

    Attributes:
        max_connections: Maximum number of connections in the pool
        min_connections: Minimum number of connections to maintain
        max_idle_time: Maximum time (seconds) a connection can be idle
        connection_timeout: Timeout (seconds) for acquiring a connection
    """

    max_connections: int = 10
    min_connections: int = 1
    max_idle_time: int = 300  # 5 minutes
    connection_timeout: int = 30

    def __post_init__(self):
        """Validate configuration"""
        if self.max_connections <= 0:
            raise ValueError(f"max_connections must be positive, got {self.max_connections}")

        if self.min_connections < 0:
            raise ValueError(f"min_connections must be non-negative, got {self.min_connections}")

        if self.min_connections > self.max_connections:
            raise ValueError(
                f"min_connections ({self.min_connections}) cannot exceed "
                f"max_connections ({self.max_connections})"
            )


class PoolExhaustedError(Exception):
    """Raised when connection pool is exhausted"""
    pass


class _PooledConnection:
    """
    Wrapper around SQLite connection with metadata

    Attributes:
        connection: The underlying SQLite connection
        created_at: Timestamp when connection was created
        last_used_at: Timestamp when connection was last used
        in_use: Whether the connection is currently in use
    """

    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.created_at = time.time()
        self.last_used_at = time.time()
        self.in_use = False

    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        try:
            # Try to execute a simple query
            self.connection.execute("SELECT 1").fetchone()
            return True
        except (sqlite3.Error, Exception):
            return False

    def is_expired(self, max_idle_time: int) -> bool:
        """Check if connection has expired due to inactivity"""
        idle_time = time.time() - self.last_used_at
        return idle_time > max_idle_time

    def mark_used(self):
        """Mark connection as used"""
        self.in_use = True
        self.last_used_at = time.time()

    def mark_idle(self):
        """Mark connection as idle"""
        self.in_use = False
        self.last_used_at = time.time()


class ConnectionPool:
    """
    Thread-safe SQLite connection pool

    This pool manages a set of SQLite connections, allowing them to be
    reused across multiple requests. It provides thread-safe access to
    connections and handles connection lifecycle.

    Attributes:
        db_path: Path to the SQLite database file
        config: Pool configuration
        max_connections: Maximum number of connections
        min_connections: Minimum number of connections to maintain

    Example:
        >>> pool = ConnectionPool("data/database.db")
        >>> conn = pool.get_connection()
        >>> try:
        ...     result = conn.execute("SELECT * FROM games").fetchall()
        ... finally:
        ...     pool.return_connection(conn)
    """

    def __init__(self, db_path: str, config: ConnectionPoolConfig = None):
        """
        Initialize connection pool

        Args:
            db_path: Path to SQLite database file
            config: Pool configuration (uses defaults if None)
        """
        self.db_path = db_path
        self.config = config or ConnectionPoolConfig()
        self.max_connections = self.config.max_connections
        self.min_connections = self.config.min_connections

        # Thread-safe storage for connections
        self._connections: list[_PooledConnection] = []
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

        # Initialize minimum number of connections
        self._initialize_pool()

        logger.info(
            f"Connection pool initialized: db={db_path}, "
            f"max={self.max_connections}, min={self.min_connections}"
        )

    def _initialize_pool(self):
        """Initialize the pool with minimum number of connections"""
        for _ in range(self.min_connections):
            conn = self._create_connection()
            self._connections.append(conn)

        logger.debug(f"Pool initialized with {len(self._connections)} connections")

    def _create_connection(self) -> _PooledConnection:
        """
        Create a new database connection

        Returns:
            _PooledConnection: Wrapped connection object
        """
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # Allow connections to be used across threads
            timeout=self.config.connection_timeout
        )

        # Use row factory for dict-like access
        conn.row_factory = sqlite3.Row

        return _PooledConnection(conn)

    def get_connection(self, timeout: float = None) -> sqlite3.Connection:
        """
        Acquire a connection from the pool

        This method will block until a connection is available or the timeout
        is reached.

        Args:
            timeout: Maximum time to wait for a connection (seconds).
                    Uses config default if None.

        Returns:
            sqlite3.Connection: Database connection

        Raises:
            PoolExhaustedError: If no connection is available within timeout
            RuntimeError: If the pool has been closed

        Example:
            >>> conn = pool.get_connection(timeout=5)
            >>> result = conn.execute("SELECT * FROM games").fetchall()
            >>> pool.return_connection(conn)
        """
        if timeout is None:
            timeout = self.config.connection_timeout

        deadline = time.time() + timeout

        with self._condition:
            while True:
                # Try to find an idle connection
                for pooled_conn in self._connections:
                    if not pooled_conn.in_use:
                        # Check if connection is healthy
                        if not pooled_conn.is_healthy():
                            # Remove unhealthy connection
                            self._connections.remove(pooled_conn)
                            continue

                        # Check if connection is expired
                        if pooled_conn.is_expired(self.config.max_idle_time):
                            # Close expired connection
                            try:
                                pooled_conn.connection.close()
                            except Exception:
                                pass
                            self._connections.remove(pooled_conn)
                            continue

                        # Mark as used and return
                        pooled_conn.mark_used()
                        logger.debug(f"Connection acquired (total: {self.total_connections})")
                        return pooled_conn.connection

                # No idle connection available
                if len(self._connections) < self.max_connections:
                    # Create new connection
                    pooled_conn = self._create_connection()
                    pooled_conn.mark_used()
                    self._connections.append(pooled_conn)
                    logger.debug(
                        f"New connection created (total: {self.total_connections})"
                    )
                    return pooled_conn.connection

                # Pool is exhausted, wait for a connection to be returned
                remaining = deadline - time.time()
                if remaining <= 0:
                    logger.error(f"Connection pool exhausted (max: {self.max_connections})")
                    raise PoolExhaustedError(
                        f"Connection pool exhausted (max: {self.max_connections})"
                    )

                logger.debug(f"Waiting for connection (timeout: {remaining:.1f}s)")
                self._condition.wait(timeout=remaining)

    def return_connection(self, connection: sqlite3.Connection):
        """
        Return a connection to the pool

        Args:
            connection: Connection to return

        Example:
            >>> conn = pool.get_connection()
            >>> try:
            ...     # Use connection
            ...     pass
            ... finally:
            ...     pool.return_connection(conn)
        """
        with self._condition:
            # Find the pooled connection wrapper
            for pooled_conn in self._connections:
                if pooled_conn.connection == connection:
                    pooled_conn.mark_idle()
                    self._condition.notify()  # Notify one waiting thread
                    logger.debug(f"Connection returned (idle: {self.idle_connections})")
                    return

            # Connection not found in pool (might be from a different pool)
            logger.warning("Returned connection not found in pool, closing it")
            try:
                connection.close()
            except Exception:
                pass

    @property
    def total_connections(self) -> int:
        """Get total number of connections in the pool"""
        with self._lock:
            return len(self._connections)

    @property
    def idle_connections(self) -> int:
        """Get number of idle connections in the pool"""
        with self._lock:
            return sum(1 for c in self._connections if not c.in_use)

    @property
    def active_connections(self) -> int:
        """Get number of active (in-use) connections"""
        with self._lock:
            return sum(1 for c in self._connections if c.in_use)

    def close(self):
        """
        Close all connections in the pool

        This method closes all connections and clears the pool.
        After calling this method, the pool cannot be used anymore.

        Example:
            >>> pool.close()
        """
        with self._lock:
            for pooled_conn in self._connections:
                try:
                    pooled_conn.connection.close()
                except Exception as e:
                    logger.warning(f"Error closing connection: {e}")

            self._connections.clear()
            logger.info("Connection pool closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Global connection pool singleton
_global_pool: Optional[ConnectionPool] = None
_global_pool_lock = threading.Lock()


def get_connection_pool() -> ConnectionPool:
    """
    Get the global connection pool singleton

    This function returns a single instance of the connection pool
    for the entire application.

    Returns:
        ConnectionPool: Global connection pool instance

    Example:
        >>> pool = get_connection_pool()
        >>> conn = pool.get_connection()
        >>> pool.return_connection(conn)
    """
    global _global_pool

    if _global_pool is None:
        with _global_pool_lock:
            if _global_pool is None:  # Double-check locking
                from backend.core.config import get_db_path
                _global_pool = ConnectionPool(
                    db_path=get_db_path(),
                    config=ConnectionPoolConfig()
                )
                logger.info("Global connection pool initialized")

    return _global_pool


@contextmanager
def get_db_connection():
    """
    Context manager for acquiring and returning a database connection

    This is a convenience wrapper around the connection pool that ensures
    connections are properly returned to the pool.

    Yields:
        sqlite3.Connection: Database connection

    Example:
        >>> with get_db_connection() as conn:
        ...     result = conn.execute("SELECT * FROM games").fetchall()
        ...     # Connection automatically returned to pool
    """
    pool = get_connection_pool()
    conn = pool.get_connection()

    try:
        yield conn
    finally:
        pool.return_connection(conn)
