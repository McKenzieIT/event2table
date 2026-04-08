#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database initialization and connection management

This module provides database connection management and initialization
functions for the SQLite database used by the application.
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


def init_db(db_path: Optional[Path] = None):
    """
    Initialize database with all tables

    Args:
        db_path: Optional database path. If not provided, uses default database from config.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Check if hql_statements table exists, if not create it
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hql_statements'")
    if not cursor.fetchone():
        logger.info("Creating hql_statements table...")
        cursor.execute(
            """
            CREATE TABLE hql_statements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                hql_type TEXT NOT NULL,
                hql_content TEXT NOT NULL,
                hql_version INTEGER DEFAULT 1,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
            )
        """
        )
        conn.commit()
        logger.info("hql_statements table created successfully")
    else:
        logger.info("hql_statements table already exists")

    # Create tables
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            ods_db TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS event_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS log_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            event_name_cn TEXT NOT NULL,
            category_id INTEGER,
            source_table TEXT NOT NULL,
            target_table TEXT NOT NULL,
            include_in_common_params INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS parameters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            param_name TEXT NOT NULL,
            param_name_cn TEXT,
            param_type TEXT NOT NULL,
            param_description TEXT,
            is_common_param INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS common_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            param_name TEXT NOT NULL,
            param_name_cn TEXT,
            param_type TEXT NOT NULL,
            param_description TEXT,
            table_name TEXT NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS event_category_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES event_categories(id) ON DELETE CASCADE,
            UNIQUE(event_id, category_id)
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS event_common_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            common_param_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE,
            FOREIGN KEY (common_param_id) REFERENCES common_params(id) ON DELETE CASCADE
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS join_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            source_events TEXT NOT NULL,
            join_conditions TEXT,
            output_fields TEXT NOT NULL,
            output_table TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS event_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            config_json TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (event_id) REFERENCES log_events(id) ON DELETE CASCADE
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS parameter_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            param_id INTEGER NOT NULL,
            alias TEXT NOT NULL,
            display_name TEXT,
            usage_count INTEGER DEFAULT 0,
            last_used_at TIMESTAMP,
            is_preferred INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY (param_id) REFERENCES parameters(id) ON DELETE CASCADE,
            UNIQUE(game_id, param_id, alias)
        )
    """
    )

    # Create sql_optimizations table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sql_optimizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_hql TEXT NOT NULL,
            optimized_hql TEXT NOT NULL,
            applied_rules TEXT,
            suggested_rules TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create index on sql_optimizations
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_sql_optimizations_created_at
        ON sql_optimizations(created_at)
    """
    )

    # Seed default categories if table is empty
    _seed_default_categories(cursor)

    conn.commit()
    conn.close()


def _seed_default_categories(cursor: sqlite3.Cursor):
    """
    Seed default event categories if the table is empty

    Args:
        cursor: Database cursor
    """
    # Check if categories already exist
    cursor.execute("SELECT COUNT(*) FROM event_categories")
    count = cursor.fetchone()[0]

    if count > 0:
        logger.info(f"Categories already exist ({count} found), skipping seed")
        return

    logger.info("Seeding default event categories...")

    default_categories = [
        ("登录/认证", "Login"),
        ("游戏进度", "Progress"),
        ("经济/交易", "Economy"),
        ("社交/聊天", "Social"),
        ("战斗/PVP", "Battle"),
        ("系统", "System"),
        ("充值/付费", "Payment"),
        ("行为/点击", "Behavior"),
    ]

    # ⚡ Performance Optimization: N+1 query fixed
    # 使用 executemany() 批量插入默认分类
    # 修复前: N次 INSERT 语句(N = 分类数量)
    # 修复后: 1次 executemany() 调用
    # 预期性能提升: 从10次SQL执行降至1次
    cursor.executemany(
        "INSERT INTO event_categories (name) VALUES (?)",
        [(category_name[0],) for category_name in default_categories],
    )

    for category_name in default_categories:
        logger.info(f"  - Created category: {category_name[0]}")

    logger.info(f"Successfully seeded {len(default_categories)} default categories")


def migrate_db():
    """
    执行数据库迁移

    使用迁移类系统进行增量数据库升级。
    所有迁移逻辑已移至 backend/core/database/migrations/ 目录。
    """
    from backend.core.database.migrations import MigrationRunner

    db_path = get_db_path()
    runner = MigrationRunner(str(db_path))

    # 获取迁移注册表中的最新版本
    target_version = max(runner.registry.keys())

    # 执行迁移
    runner.migrate_to_version(target_version)

    logger.info(f"Database migration completed. Current version: {runner.get_current_version()}")


def create_indexes():
    """Create database indexes for performance optimization"""
    from backend.core.database.indexes import create_indexes as _create_indexes

    _create_indexes()


# ==================== Convenience exports ==================== #
# 重导出常用函数，保持向后兼容

__all__ = [
    "get_db_connection",
    "get_db",
    "init_db",
    "migrate_db",
    "create_indexes",
]
