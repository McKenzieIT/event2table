#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Event Nodes game_gid Migration

Tests the migration of event_nodes table from game_id to game_gid
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
import sys

# Add project root to path (4 levels up: unit -> tests -> backend -> dwd_generator)
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import migration functions from scripts directory
from scripts.fix_event_nodes_game_gid import migrate_event_nodes_game_gid, verify_migration


class TestEventNodesGameGidMigration:
    """测试 event_nodes 表 game_gid 迁移"""

    def test_migration_adds_game_gid_column(self):
        """测试：迁移添加 game_gid 列"""
        fd, db_path = tempfile.mkstemp(suffix=".db")

        try:
            # 初始化数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 创建基础表
            cursor.execute("""
                CREATE TABLE games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gid INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL
                )
            """)

            # 创建使用 game_id 的 event_nodes 表（旧版本）
            cursor.execute("""
                CREATE TABLE event_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    game_id INTEGER NOT NULL,
                    event_id INTEGER,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (game_id) REFERENCES games(id)
                )
            """)

            # 插入测试数据
            cursor.execute("INSERT INTO games (gid, name) VALUES (10000147, 'Test Game 1')")
            cursor.execute("INSERT INTO games (gid, name) VALUES (99999999, 'Test Game 2')")

            cursor.execute("""
                INSERT INTO event_nodes (name, game_id, event_id)
                VALUES ('Test Node 1', 1, 1)
            """)
            cursor.execute("""
                INSERT INTO event_nodes (name, game_id, event_id)
                VALUES ('Test Node 2', 1, 2)
            """)
            cursor.execute("""
                INSERT INTO event_nodes (name, game_id, event_id)
                VALUES ('Test Node 3', 2, 3)
            """)

            conn.commit()
            conn.close()

            # 执行迁移
            migrate_event_nodes_game_gid(db_path)

            # 验证 game_gid 列存在
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(event_nodes)")
            columns = [col[1] for col in cursor.fetchall()]
            conn.close()

            assert "game_gid" in columns

        finally:
            import os

            try:
                os.unlink(db_path)
            except:
                pass

    def test_migration_migrates_existing_data(self):
        """测试：迁移正确转换现有数据"""
        fd, db_path = tempfile.mkstemp(suffix=".db")

        try:
            # 初始化数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 创建基础表
            cursor.execute("""
                CREATE TABLE games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gid INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL
                )
            """)

            # 创建使用 game_id 的 event_nodes 表
            cursor.execute("""
                CREATE TABLE event_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    game_id INTEGER NOT NULL,
                    event_id INTEGER
                )
            """)

            # 插入测试数据
            cursor.execute("INSERT INTO games (gid, name) VALUES (10000147, 'Game A')")
            cursor.execute("INSERT INTO games (gid, name) VALUES (99999999, 'Game B')")

            cursor.execute(
                "INSERT INTO event_nodes (name, game_id, event_id) VALUES ('Node 1', 1, 100)"
            )
            cursor.execute(
                "INSERT INTO event_nodes (name, game_id, event_id) VALUES ('Node 2', 2, 101)"
            )

            conn.commit()
            conn.close()

            # 执行迁移
            migrate_event_nodes_game_gid(db_path)

            # 验证 game_gid 已正确设置
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, game_id, game_gid FROM event_nodes ORDER BY id")
            results = cursor.fetchall()
            conn.close()

            assert len(results) == 2
            # results[0] = (id, name, game_id, game_gid)
            assert results[0][2] == 1  # game_id
            assert results[0][3] == 10000147  # game_gid for game_id=1
            assert results[1][2] == 2  # game_id
            assert results[1][3] == 99999999  # game_gid for game_id=2

        finally:
            import os

            try:
                os.unlink(db_path)
            except:
                pass

    def test_migration_creates_index(self):
        """测试：迁移创建 game_gid 索引"""
        fd, db_path = tempfile.mkstemp(suffix=".db")

        try:
            # 初始化数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 创建基础表
            cursor.execute("""
                CREATE TABLE games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gid INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE event_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    game_id INTEGER NOT NULL
                )
            """)

            cursor.execute("INSERT INTO games (gid, name) VALUES (10000147, 'Test Game')")
            cursor.execute("INSERT INTO event_nodes (name, game_id) VALUES ('Test Node', 1)")

            conn.commit()
            conn.close()

            # 执行迁移
            migrate_event_nodes_game_gid(db_path)

            # 验证索引存在
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name='idx_event_nodes_game_gid'
            """)
            index_exists = cursor.fetchone() is not None
            conn.close()

            assert index_exists

        finally:
            import os

            try:
                os.unlink(db_path)
            except:
                pass

    def test_migration_preserves_game_id_column(self):
        """测试：迁移保留 game_id 列（向后兼容）"""
        fd, db_path = tempfile.mkstemp(suffix=".db")

        try:
            # 初始化数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 创建基础表
            cursor.execute("""
                CREATE TABLE games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gid INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE event_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    game_id INTEGER NOT NULL
                )
            """)

            cursor.execute("INSERT INTO games (gid, name) VALUES (10000147, 'Test Game')")
            cursor.execute("INSERT INTO event_nodes (name, game_id) VALUES ('Test Node', 1)")

            conn.commit()
            conn.close()

            # 执行迁移
            migrate_event_nodes_game_gid(db_path)

            # 验证 game_id 列仍然存在
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(event_nodes)")
            columns = [col[1] for col in cursor.fetchall()]
            conn.close()

            assert "game_id" in columns
            assert "game_gid" in columns

        finally:
            import os

            try:
                os.unlink(db_path)
            except:
                pass

    def test_verify_migration_function(self):
        """测试：验证函数正确检测迁移状态"""
        fd, db_path = tempfile.mkstemp(suffix=".db")

        try:
            # 初始化数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 创建基础表
            cursor.execute("""
                CREATE TABLE games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gid INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE event_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    game_id INTEGER NOT NULL
                )
            """)

            cursor.execute("INSERT INTO games (gid, name) VALUES (10000147, 'Test Game')")
            cursor.execute("INSERT INTO event_nodes (name, game_id) VALUES ('Test Node', 1)")

            conn.commit()
            conn.close()

            # 执行迁移
            migrate_event_nodes_game_gid(db_path)

            # 验证迁移
            success = verify_migration(db_path)

            assert success is True

        finally:
            import os

            try:
                os.unlink(db_path)
            except:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
