#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database package - exports all database functions
"""

# Import DB_PATH from config
from ..config import DB_PATH

# Import from database module to make them available at package level
from .database import create_indexes, get_db, get_db_connection, init_db, migrate_db

# Import connection pool for performance optimization
from .connection_pool import (
    ConnectionPool,
    ConnectionPoolConfig,
    PoolExhaustedError,
    get_connection_pool,
    get_db_connection as get_pooled_connection,
)

__all__ = [
    "get_db_connection",
    "get_db",
    "init_db",
    "migrate_db",
    "create_indexes",
    "DB_PATH",
    # Connection pool exports
    "ConnectionPool",
    "ConnectionPoolConfig",
    "PoolExhaustedError",
    "get_connection_pool",
    "get_pooled_connection",
]
