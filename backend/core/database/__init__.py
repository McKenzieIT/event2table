#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database package - exports all database functions
"""

# Import from database module to make them available at package level
from .database import (
    get_db_connection,
    get_db,
    init_db,
    migrate_db,
    create_indexes,
)

# Import DB_PATH from config
from ..config import DB_PATH

__all__ = [
    "get_db_connection",
    "get_db",
    "init_db",
    "migrate_db",
    "create_indexes",
    "DB_PATH",
]
