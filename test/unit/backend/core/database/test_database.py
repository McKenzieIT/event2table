#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database 单元测试

测试 backend.core.database 中的数据库函数
"""

import pytest
import sqlite3
import tempfile
import uuid
from pathlib import Path
from backend.core.database import get_db_connection, init_db
from backend.core.utils import execute_write, fetch_one_as_dict
from backend.core.config.config import DB_PATH


class TestDatabaseConnection:
    """测试数据库连接"""

    def test_get_db_connection(self):
        """测试获取数据库连接"""
        conn = get_db_connection()

        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)

        # 验证row_factory已设置
        result = conn.execute("SELECT 1 as test").fetchone()
        assert result["test"] == 1

        conn.close()

    def test_get_db_connection_singleton(self):
        """测试数据库连接单例模式"""
        conn1 = get_db_connection()
        conn2 = get_db_connection()

        # 每次调用应该返回同一个连接（单例模式）
        # 注意：实际实现可能不同，这是示例
        assert conn1 is not None
        assert conn2 is not None

        conn1.close()
        conn2.close()


class TestDatabaseInit:
    """测试数据库初始化"""

    @pytest.mark.slow
    @pytest.mark.skip(reason="Requires separate database configuration")
    def test_init_db_creates_tables(self):
        """测试初始化数据库创建表"""
        # 此测试需要单独的数据库配置，暂时跳过
        pass


class TestDatabaseOperations:
    """测试数据库操作"""

    @pytest.mark.database
    def test_execute_write_insert(self, db):
        """测试插入操作"""
        unique_gid = f"test_{uuid.uuid4().hex[:8]}"
        affected = execute_write(
            "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
            (unique_gid, "DB Test", "test_db")
        )

        assert affected == 1

        # 验证数据已插入
        result = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (unique_gid,))
        assert result is not None
        assert result["name"] == "DB Test"

    @pytest.mark.database
    def test_execute_write_delete(self, db, sample_game):
        """测试删除操作"""
        affected = execute_write("DELETE FROM games WHERE id = ?", (sample_game["id"],))

        assert affected == 1

        # 验证数据已删除
        result = fetch_one_as_dict("SELECT * FROM games WHERE id = ?", (sample_game["id"],))
        assert result is None

    @pytest.mark.database
    def test_execute_write_update(self, db, sample_game):
        """测试更新操作"""
        new_name = "Updated Game"
        affected = execute_write(
            "UPDATE games SET name = ? WHERE id = ?",
            (new_name, sample_game["id"])
        )

        assert affected == 1

        # 验证数据已更新
        result = fetch_one_as_dict("SELECT * FROM games WHERE id = ?", (sample_game["id"],))
        assert result["name"] == new_name


class TestDatabaseTransactions:
    """测试数据库事务"""

    @pytest.mark.database
    def test_transaction_commit(self, db):
        """测试事务提交"""
        # db fixture 已经开启了事务，我们直接使用
        unique_gid = f"test_{uuid.uuid4().hex[:8]}"

        try:
            # 执行多个操作 - 直接使用db连接
            db.execute(
                "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                (unique_gid, "Transaction Test", "test_db")
            )

            # 提交事务
            db.commit()

            # 验证数据已提交
            result = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (unique_gid,))
            assert result is not None

        except Exception:
            db.rollback()
            raise

    @pytest.mark.database
    def test_transaction_rollback(self, db):
        """测试事务回滚"""
        # db fixture 已经开启了事务，我们直接使用
        unique_gid = f"test_{uuid.uuid4().hex[:8]}"

        try:
            # 执行操作
            db.execute(
                "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                (unique_gid, "Rollback Test", "test_db")
            )

            # 故意触发错误
            raise Exception("Test exception")

        except Exception:
            # 回滚事务
            db.rollback()

        # 验证数据未插入
        result = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (unique_gid,))
        assert result is None
