#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Migration 单元测试

测试新的数据库迁移系统，使用迁移类模式重构原有的migrate_db函数
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from backend.core.database.database import MigrationRunner, get_migration_registry


class TestMigrationRegistry:
    """测试迁移注册表"""

    def test_registry_exists(self):
        """测试迁移注册表存在"""
        registry = get_migration_registry()

        assert registry is not None
        assert isinstance(registry, dict)
        assert len(registry) > 0  # 应该有迁移注册

    def test_registry_has_version_1_migration(self):
        """测试注册表包含版本1迁移"""
        registry = get_migration_registry()

        assert 1 in registry
        migration = registry[1]

        assert hasattr(migration, 'version')
        assert migration.version == 1
        assert hasattr(migration, 'upgrade')
        assert callable(migration.upgrade)

    def test_registry_migrations_are_sequential(self):
        """测试迁移版本号是连续的"""
        registry = get_migration_registry()
        versions = sorted(registry.keys())

        # 版本号应该是1, 2, 3, ... 18
        assert versions[0] == 1
        for i in range(len(versions) - 1):
            assert versions[i + 1] == versions[i] + 1

    def test_each_migration_has_required_methods(self):
        """测试每个迁移都有必需的方法"""
        registry = get_migration_registry()

        for version, migration in registry.items():
            assert hasattr(migration, 'version'), f"Migration {version} missing version attribute"
            assert hasattr(migration, 'upgrade'), f"Migration {version} missing upgrade method"
            assert callable(migration.upgrade), f"Migration {version} upgrade not callable"


class TestMigrationClasses:
    """测试单个迁移类"""

    def test_migration_1_adds_category_id_column(self, temp_db):
        """测试迁移1：添加category_id列"""
        runner = MigrationRunner(temp_db)

        # 执行迁移1
        runner.migrate_to_version(1)

        # 验证category_id列存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(log_events)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        assert "category_id" in columns

    def test_migration_2_creates_event_category_relations_table(self, temp_db):
        """测试迁移2：创建event_category_relations表"""
        runner = MigrationRunner(temp_db)

        # 先执行到版本1，然后到版本2
        runner.migrate_to_version(2)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='event_category_relations'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_3_adds_include_in_common_params_column(self, temp_db):
        """测试迁移3：添加include_in_common_params列"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(3)

        # 验证列存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(log_events)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        assert "include_in_common_params" in columns

    def test_migration_6_creates_param_templates_table(self, temp_db):
        """测试迁移6：创建param_templates表"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(6)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='param_templates'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_6_inserts_predefined_templates(self, temp_db):
        """测试迁移6：插入预定义类型模板"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(6)

        # 验证预定义模板存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM param_templates")
        count = cursor.fetchone()[0]
        conn.close()

        # 应该插入至少11个预定义模板
        assert count >= 11

    def test_migration_6_creates_param_library_table(self, temp_db):
        """测试迁移6：创建param_library表"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(6)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='param_library'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_6_creates_event_params_table(self, temp_db):
        """测试迁移6：创建event_params表"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(6)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='event_params'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_6_creates_param_versions_table(self, temp_db):
        """测试迁移6：创建param_versions表"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(6)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='param_versions'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_6_creates_param_configs_table(self, temp_db):
        """测试迁移6：创建param_configs表"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(6)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='param_configs'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_6_renames_old_parameters_table(self, temp_db):
        """测试迁移6：重命名旧的parameters表"""
        runner = MigrationRunner(temp_db)

        # 首先创建旧的parameters表
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parameters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                param_name TEXT NOT NULL,
                param_name_cn TEXT,
                param_type TEXT,
                param_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        runner.migrate_to_version(6)

        # 验证旧表被重命名
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='parameters_old_v5'"
        )
        old_table_exists = cursor.fetchone() is not None
        conn.close()

        assert old_table_exists

    def test_migration_7_creates_param_validation_rules_table(self, temp_db):
        """测试迁移7：创建param_validation_rules表"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(7)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='param_validation_rules'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_7_creates_batch_import_records_table(self, temp_db):
        """测试迁移7：创建batch_import_records表"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(7)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='batch_import_records'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_7_creates_batch_import_details_table(self, temp_db):
        """测试迁移7：创建batch_import_details表"""
        runner = MigrationRunner(temp_db)

        runner.migrate_to_version(7)

        # 验证表存在
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='batch_import_details'"
        )
        table_exists = cursor.fetchone() is not None
        conn.close()

        assert table_exists

    def test_migration_18_adds_game_gid_column(self, temp_db_with_game_id):
        """测试迁移18：添加game_gid列到log_events表并迁移数据"""
        runner = MigrationRunner(temp_db_with_game_id)

        # 执行到版本18
        runner.migrate_to_version(18)

        # 验证game_gid列存在
        conn = sqlite3.connect(temp_db_with_game_id)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(log_events)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        assert "game_gid" in columns

        # 验证索引存在
        conn = sqlite3.connect(temp_db_with_game_id)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_log_events_game_gid'"
        )
        index_exists = cursor.fetchone() is not None
        conn.close()

        assert index_exists

    def test_migration_18_migrates_existing_data(self, temp_db_with_game_id):
        """测试迁移18正确迁移现有数据"""
        runner = MigrationRunner(temp_db_with_game_id)

        # 插入一条测试数据（使用旧的game_id）
        conn = sqlite3.connect(temp_db_with_game_id)
        cursor = conn.cursor()

        # 插入游戏
        cursor.execute("INSERT INTO games (gid, name, ods_db) VALUES (99999, 'Test Game', 'test_db')")
        game_id = cursor.lastrowid

        # 插入事件（使用game_id）
        cursor.execute(
            "INSERT INTO log_events (game_id, event_name, event_name_cn, category_id, source_table, target_table) VALUES (?, 'test', '测试', 1, 'test_source', 'test_target')",
            (game_id,)
        )
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # 执行迁移18
        runner.migrate_to_version(18)

        # 验证game_gid已正确设置
        conn = sqlite3.connect(temp_db_with_game_id)
        cursor = conn.cursor()
        cursor.execute("SELECT game_gid FROM log_events WHERE id = ?", (event_id,))
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 99999  # 应该是游戏的gid，不是id


class TestMigrationRunner:
    """测试迁移运行器"""

    def test_runner_gets_current_version(self, temp_db):
        """测试运行器能获取当前版本"""
        runner = MigrationRunner(temp_db)

        version = runner.get_current_version()

        assert isinstance(version, int)
        assert version >= 0

    def test_runner_migrates_from_zero_to_target(self, temp_db):
        """测试运行器从版本0迁移到目标版本"""
        runner = MigrationRunner(temp_db)

        # 从0迁移到版本5
        runner.migrate_to_version(5)

        final_version = runner.get_current_version()

        assert final_version == 5

    def test_runner_skips_already_applied_migrations(self, temp_db):
        """测试运行器跳过已应用的迁移"""
        runner = MigrationRunner(temp_db)

        # 迁移到版本3
        runner.migrate_to_version(3)
        version_after_first = runner.get_current_version()

        # 再次迁移到版本3（应该跳过）
        runner.migrate_to_version(3)
        version_after_second = runner.get_current_version()

        assert version_after_first == 3
        assert version_after_second == 3

    def test_runner_migrates_incrementally(self, temp_db):
        """测试运行器支持增量迁移"""
        runner = MigrationRunner(temp_db)

        # 先迁移到版本2
        runner.migrate_to_version(2)
        assert runner.get_current_version() == 2

        # 然后迁移到版本5
        runner.migrate_to_version(5)
        assert runner.get_current_version() == 5

    def test_runner_updates_version_after_migration(self, temp_db):
        """测试运行器在迁移后更新版本号"""
        runner = MigrationRunner(temp_db)

        initial_version = runner.get_current_version()
        runner.migrate_to_version(1)
        final_version = runner.get_current_version()

        # PRAGMA user_version应该被更新
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        db_version = cursor.fetchone()[0]
        conn.close()

        assert db_version == final_version
        assert final_version > initial_version


class TestMigrationIntegration:
    """集成测试：完整迁移流程"""

    @pytest.mark.slow
    def test_full_migration_from_zero_to_latest(self, temp_db):
        """测试从0迁移到最新版本的完整流程"""
        runner = MigrationRunner(temp_db)

        # 获取最新版本号
        registry = get_migration_registry()
        latest_version = max(registry.keys())

        # 执行完整迁移
        runner.migrate_to_version(latest_version)

        # 验证最终版本
        assert runner.get_current_version() == latest_version

        # 验证数据库结构完整性（不抛出异常）
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # 检查关键表存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert "games" in tables
        assert "log_events" in tables
        assert "event_categories" in tables

        conn.close()

    def test_migration_is_idempotent(self, temp_db):
        """测试迁移是幂等的（多次执行结果相同）"""
        runner = MigrationRunner(temp_db)

        # 第一次迁移到版本3
        runner.migrate_to_version(3)

        conn = sqlite3.connect(temp_db)
        cursor1 = conn.cursor()
        cursor1.execute("SELECT COUNT(*) FROM log_events")
        count1 = cursor1.fetchone()[0]
        conn.close()

        # 第二次迁移到版本3（应该不改变数据）
        runner.migrate_to_version(3)

        conn = sqlite3.connect(temp_db)
        cursor2 = conn.cursor()
        cursor2.execute("SELECT COUNT(*) FROM log_events")
        count2 = cursor2.fetchone()[0]
        conn.close()

        assert count1 == count2


# ===== Fixtures =====


@pytest.fixture
def temp_db():
    """创建临时数据库用于测试"""
    fd, path = tempfile.mkstemp(suffix=".db")

    # 初始化数据库结构（但不执行迁移）
    import sqlite3

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # 创建基础表结构（模拟旧版本数据库）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            ods_db TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_gid INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            FOREIGN KEY (game_gid) REFERENCES games(gid)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # 为迁移5创建hql_statements表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hql_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_gid INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            hql_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_gid) REFERENCES games(gid),
            FOREIGN KEY (event_id) REFERENCES log_events(id)
        )
    """)

    # 为迁移9创建join_configs表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS join_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source_events TEXT,
            join_conditions TEXT,
            display_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    yield path

    # 清理
    import os
    try:
        os.unlink(path)
    except:
        pass


@pytest.fixture
def temp_db_with_game_id():
    """创建临时数据库用于测试game_gid迁移（模拟旧版本数据库，使用game_id外键）"""
    fd, path = tempfile.mkstemp(suffix=".db")

    import sqlite3

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # 创建基础表结构（旧版本：使用game_id外键）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL,
            ods_db TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            event_name TEXT NOT NULL,
            event_name_cn TEXT,
            category_id INTEGER,
            source_table TEXT,
            target_table TEXT,
            FOREIGN KEY (game_id) REFERENCES games(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # 为迁移5创建hql_statements表（迁移18之前需要的表）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hql_statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            hql_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (event_id) REFERENCES log_events(id)
        )
    """)

    # 为迁移9创建join_configs表（迁移18之前需要的表）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS join_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source_events TEXT,
            join_conditions TEXT,
            display_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    yield path

    # 清理
    import os
    try:
        os.unlink(path)
    except:
        pass
