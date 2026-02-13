"""
HQL历史版本数据库迁移脚本

创建hql_history表用于存储HQL生成历史
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def migrate_hql_history(db_path: str):
    """
    创建hql_history表

    Args:
        db_path: 数据库文件路径
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建hql_history表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hql_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            session_id TEXT,
            events_json TEXT NOT NULL,
            fields_json TEXT NOT NULL,
            conditions_json TEXT,
            mode TEXT NOT NULL DEFAULT 'single',
            hql TEXT NOT NULL,
            performance_score INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime')),
            metadata_json TEXT
        )
    """)

    # 创建索引以提高查询性能
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hql_history_user_created
        ON hql_history(user_id, created_at DESC)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_hql_history_session_created
        ON hql_history(session_id, created_at DESC)
    """)

    conn.commit()
    conn.close()

    print("✅ hql_history表创建成功")


def rollback_hql_history(db_path: str):
    """
    回滚hql_history表（用于测试清理）

    Args:
        db_path: 数据库文件路径
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS hql_history")

    conn.commit()
    conn.close()

    print("✅ hql_history表已删除")


if __name__ == "__main__":
    # 测试迁移
    test_db = "/tmp/test_hql_history.db"
    migrate_hql_history(test_db)
