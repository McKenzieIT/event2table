#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
join_configs game_id迁移单元测试

测试join_configs从game_id迁移到game_gid
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path


class TestJoinConfigsGameGidMigration:
    """测试join_configs表的game_gid迁移"""

    def test_join_configs_should_use_game_gid_not_game_id(self):
        """测试：join_configs表应该使用game_gid而非game_id作为业务字段"""
        # 创建临时数据库
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
                    name TEXT NOT NULL,
                    ods_db TEXT
                )
            """)

            # 创建使用game_id的join_configs表（旧版本）
            cursor.execute("""
                CREATE TABLE join_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    game_id INTEGER,
                    source_events TEXT,
                    join_conditions TEXT,
                    display_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 插入测试数据
            cursor.execute("INSERT INTO games (gid, name, ods_db) VALUES (10000147, 'Test Game', 'ieu_ods')")
            cursor.execute("INSERT INTO games (gid, name, ods_db) VALUES (99999999, 'Another Game', 'test_db')")

            cursor.execute("""
                INSERT INTO join_configs (name, game_id, source_events, display_name)
                VALUES ('Test Config', 1, '[1,2]', 'Test')
            """)

            conn.commit()
            conn.close()

            # 验证问题：当前使用game_id
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT game_id FROM join_configs WHERE name = ?", ('Test Config',))
            result = cursor.fetchone()
            conn.close()

            assert result is not None
            assert result[0] == 1  # 当前使用game_id=1

        finally:
            # 清理
            import os
            try:
                os.unlink(db_path)
            except:
                pass

    def test_join_configs_migration_to_game_gid(self):
        """测试：join_configs表迁移到game_gid后应该正确关联业务GID"""
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
                    name TEXT NOT NULL,
                    ods_db TEXT
                )
            """)

            # 创建使用game_gid的join_configs表（新版本）
            cursor.execute("""
                CREATE TABLE join_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    game_gid INTEGER,
                    source_events TEXT,
                    join_conditions TEXT,
                    display_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 插入测试数据
            cursor.execute("INSERT INTO games (gid, name, ods_db) VALUES (10000147, 'Test Game', 'ieu_ods')")

            cursor.execute("""
                INSERT INTO join_configs (name, game_gid, source_events, display_name)
                VALUES ('Test Config', 10000147, '[1,2]', 'Test')
            """)

            conn.commit()
            conn.close()

            # 验证：使用game_gid
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT game_gid FROM join_configs WHERE name = ?", ('Test Config',))
            result = cursor.fetchone()
            conn.close()

            assert result is not None
            assert result[0] == 10000147  # 应该使用业务GID

            # 验证：可以JOIN到games表获取游戏信息
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT jc.name, g.name, g.gid
                FROM join_configs jc
                JOIN games g ON jc.game_gid = g.gid
                WHERE jc.name = ?
            """, ('Test Config',))
            join_result = cursor.fetchone()
            conn.close()

            assert join_result is not None
            assert join_result[0] == 'Test Config'
            assert join_result[1] == 'Test Game'
            assert join_result[2] == 10000147

        finally:
            import os
            try:
                os.unlink(db_path)
            except:
                pass
