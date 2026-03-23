#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration v21: HQL Templates Table

创建HQL模板库表,支持模板分类、搜索、导入导出和使用统计
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)


def migrate(conn: sqlite3.Connection):
    """
    执行数据库迁移 v21

    创建 hql_templates 表和相关索引
    """
    cursor = conn.cursor()

    try:
        logger.info("Migration v21: Creating hql_templates table...")

        # 创建 hql_templates 表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hql_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                hql_content TEXT NOT NULL,
                variables TEXT,
                description TEXT,
                tags TEXT,
                game_gid INTEGER,
                usage_count INTEGER DEFAULT 0,
                is_featured INTEGER DEFAULT 0,
                is_system INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP
            )
        """
        )

        logger.info("Migration v21: hql_templates table created")

        # 创建索引
        indexes = [
            ("idx_hql_templates_category", "category"),
            ("idx_hql_templates_game_gid", "game_gid"),
            ("idx_hql_templates_usage_count", "usage_count"),
            ("idx_hql_templates_is_featured", "is_featured"),
            ("idx_hql_templates_is_active", "is_active"),
            ("idx_hql_templates_name", "name"),
        ]

        for index_name, column in indexes:
            try:
                cursor.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS {index_name}
                    ON hql_templates({column})
                """
                )
                logger.info(f"Migration v21: index {index_name} created")
            except Exception as e:
                logger.warning(f"Migration v21: Could not create index {index_name}: {e}")

        conn.commit()
        logger.info("Migration v21 completed: HQL templates support added")

    except Exception as e:
        conn.rollback()
        logger.error(f"Migration v21 failed: {e}")
        raise
