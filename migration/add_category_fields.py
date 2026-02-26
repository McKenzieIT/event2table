#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本: 为event_categories表添加新字段

添加字段:
- name_cn: 类别中文名
- description: 描述
- color: 颜色代码
- icon: 图标

执行时间: 2026-02-26
"""

import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database(db_path: str):
    """
    执行数据库迁移

    Args:
        db_path: 数据库文件路径
    """
    logger.info(f"开始迁移数据库: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='event_categories'
        """)
        if not cursor.fetchone():
            logger.error("表 event_categories 不存在")
            return

        # 检查列是否已存在
        cursor.execute("PRAGMA table_info(event_categories)")
        existing_columns = {row[1] for row in cursor.fetchall()}

        # 定义要添加的列
        new_columns = {
            "name_cn": "TEXT",
            "description": "TEXT",
            "color": "TEXT",
            "icon": "TEXT"
        }

        # 添加新列
        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                logger.info(f"添加列: {column_name} ({column_type})")
                cursor.execute(f"""
                    ALTER TABLE event_categories
                    ADD COLUMN {column_name} {column_type}
                """)
            else:
                logger.info(f"列已存在，跳过: {column_name}")

        conn.commit()
        logger.info("✅ 数据库迁移完成")

        # 验证迁移结果
        cursor.execute("PRAGMA table_info(event_categories)")
        all_columns = [row[1] for row in cursor.fetchall()]
        logger.info(f"当前表结构: {', '.join(all_columns)}")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()


def main():
    """主函数: 迁移所有数据库"""
    db_files = [
        "data/dwd_generator.db",
        "data/test_database.db",
        "data/dwd_generator_dev.db"
    ]

    for db_file in db_files:
        db_path = Path(db_file)
        if db_path.exists():
            migrate_database(str(db_path))
        else:
            logger.warning(f"数据库文件不存在，跳过: {db_file}")


if __name__ == "__main__":
    main()
