#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Join Config Module Integration Tests

集成测试验证Join Config模块的完整流程:
- API → Service → Repository → Entity → Database
- 缓存失效机制
- 错误处理
- 数据验证
"""

import os
import pytest
from datetime import datetime
from backend.models.entities import JoinConfigEntity
from backend.services.join_configs.join_config_service import JoinConfigService
from backend.models.repositories.join_config_repository import JoinConfigRepository
from backend.core.utils.converters import get_db_connection


class TestJoinConfigModuleIntegration:
    """Join Config模块集成测试"""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """测试前设置数据库"""
        # 设置测试环境
        os.environ["FLASK_ENV"] = "testing"

        # 确保测试数据库存在
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建join_configs表(如果不存在或schema不正确)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='join_configs'")
        table_exists = cursor.fetchone() is not None

        if table_exists:
            # 检查表是否有game_gid列
            cursor.execute("PRAGMA table_info(join_configs)")
            columns = {col[1] for col in cursor.fetchall()}
            if 'game_gid' not in columns:
                # 旧schema, 删除并重建
                cursor.execute("DROP TABLE join_configs")
                table_exists = False

        if not table_exists:
            cursor.execute(
                '''
                CREATE TABLE join_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_gid INTEGER NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    join_type TEXT NOT NULL DEFAULT 'join',
                    source_events TEXT NOT NULL,
                    join_conditions TEXT,
                    output_fields TEXT NOT NULL,
                    output_table TEXT NOT NULL,
                    where_conditions TEXT,
                    field_mappings TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
            )
            cursor.execute(
                'CREATE INDEX IF NOT EXISTS idx_join_configs_game_gid ON join_configs(game_gid)'
            )
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_join_configs_name ON join_configs(name)')
            conn.commit()

        # 确保games表有测试数据
        cursor.execute("SELECT COUNT(*) FROM games WHERE gid >= 91000000")
        if cursor.fetchone()[0] == 0:
            # 添加测试游戏
            for i in range(100):
                try:
                    cursor.execute(
                        "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                        (91000000 + i, f"Test Game {i}", "ieu_ods"),
                    )
                except:
                    pass
            conn.commit()

        yield

        # 清理测试数据
        cursor.execute("DELETE FROM join_configs WHERE game_gid >= 91000000")
        cursor.execute("DELETE FROM games WHERE cast(gid as integer) >= 91000000")
        conn.commit()

    def test_create_join_config_flow(self):
        """测试完整的Join Config创建流程"""
        # 1. 准备Join Config数据(使用已存在的测试游戏)
        config_data = JoinConfigEntity(
            name="test_join_config",
            display_name="Test Join Config",
            game_gid=91000001,  # 使用setup中创建的游戏（91000000-91000099范围）
            join_type="join",
            source_events=[1, 2, 3],
            join_config={"on": "event1.role_id = event2.role_id"},
            output_fields=["role_id", "zone_id", "level"],
            output_table="dwd.test_output",
            description="Test join configuration",
        )

        # 3. 通过Service创建Join Config
        service = JoinConfigService()
        created_config = service.create_join_config(config_data)

        # 4. 验证创建结果
        assert created_config is not None
        assert created_config.name == "test_join_config"
        assert created_config.display_name == "Test Join Config"
        assert created_config.game_gid == 91000001
        assert created_config.join_type == "join"

        # 5. 验证数据库记录
        repo = JoinConfigRepository()
        retrieved_config = repo.find_by_id(created_config.id)
        assert retrieved_config is not None
        assert retrieved_config.name == "test_join_config"
        assert retrieved_config.game_gid == 91000001

    def test_get_join_config_by_id(self):
        """测试通过ID获取Join Config"""
        # 1. 准备测试数据(使用setup中创建的游戏)
        repo = JoinConfigRepository()
        config_data = JoinConfigEntity(
            name="get_test_config",
            display_name="Get Test Config",
            game_gid=91000002,
            join_type="union_all",
            source_events=[1, 2],
            output_fields=["role_id"],
            output_table="dwd.union_test",
        )
        created = repo.create(config_data.model_dump())

        # 2. 通过Service获取Join Config
        service = JoinConfigService()
        config = service.get_join_config_by_id(created.id)

        # 3. 验证结果
        assert config is not None
        assert config.name == "get_test_config"
        assert config.join_type == "union_all"

    def test_list_join_configs_by_game(self):
        """测试按游戏列出Join Configs"""
        # 1. 准备测试数据(使用setup中创建的游戏)
        service = JoinConfigService()
        for i in range(3):
            config_data = JoinConfigEntity(
                name=f"list_test_config_{i}",
                display_name=f"List Test Config {i}",
                game_gid=91000003,
                join_type="join",
                join_config={"on": f"t{i}.id = t{i+1}.id"},
                source_events=[i],
                output_fields=["field1"],
                output_table=f"dwd.test_{i}",
            )
            service.create_join_config(config_data)

        # 2. 获取该游戏的所有Join Configs
        configs = service.list_join_configs(game_gid=91000003)

        # 3. 验证结果
        assert len(configs) >= 3
        test_configs = [c for c in configs if c.name.startswith("list_test_config_")]
        assert len(test_configs) == 3

    def test_update_join_config_flow(self):
        """测试Join Config更新流程"""
        # 1. 准备测试数据(使用setup中创建的游戏)
        service = JoinConfigService()
        config_data = JoinConfigEntity(
            name="update_test_config",
            display_name="Original Name",
            game_gid=91000004,
            join_type="join",
            join_config={"on": "t1.id = t2.id"},
            source_events=[1],
            output_fields=["field1"],
            output_table="dwd.test",
        )
        created = service.create_join_config(config_data)

        # 2. 更新Join Config
        updates = {"display_name": "Updated Name", "description": "Updated description"}
        updated_config = service.update_join_config(created.id, updates)

        # 3. 验证更新结果
        assert updated_config.display_name == "Updated Name"
        assert updated_config.description == "Updated description"

    def test_delete_join_config_flow(self):
        """测试Join Config删除流程"""
        # 1. 准备测试数据(使用setup中创建的游戏)
        service = JoinConfigService()
        config_data = JoinConfigEntity(
            name="delete_test_config",
            display_name="To Be Deleted",
            game_gid=91000005,
            join_type="join",
            join_config={"on": "t1.id = t2.id"},
            source_events=[1],
            output_fields=["field1"],
            output_table="dwd.test",
        )
        created = service.create_join_config(config_data)

        # 2. 删除Join Config
        service.delete_join_config(created.id)

        # 3. 验证删除结果
        config = service.get_join_config_by_id(created.id)
        assert config is None

    def test_join_config_validation(self):
        """测试Join Config数据验证"""
        service = JoinConfigService()

        # 测试1: 无效的join_type
        with pytest.raises(ValueError) as exc_info:
            config_data = JoinConfigEntity(
                name="invalid_type_config",
                display_name="Invalid Type",
                game_gid=91000006,
                join_type="invalid_type",  # 无效的join_type
                source_events=[1],
                output_fields=["field1"],
                output_table="dwd.test",
            )
            service.create_join_config(config_data)
        assert "join_type" in str(exc_info.value).lower()

        # 测试2: join类型必须提供join_config
        with pytest.raises(ValueError) as exc_info:
            config_data = JoinConfigEntity(
                name="missing_condition_config",
                display_name="Missing Condition",
                game_gid=91000006,
                join_type="join",
                join_config={},  # 空的join_config
                source_events=[1, 2],
                output_fields=["field1"],
                output_table="dwd.test",
            )
            service.create_join_config(config_data)
        assert "join_config" in str(exc_info.value).lower()

    def test_entity_serialization(self):
        """测试Entity序列化"""
        # 1. 创建Entity
        config = JoinConfigEntity(
            id=1,
            name="serialization_test",
            display_name="Serialization Test",
            game_gid=91000999,
            join_type="join",
            source_events=[1, 2, 3],
            join_config={"on": "t1.id = t2.id"},
            output_fields=["id", "name"],
            output_table="dwd.test",
            description="Test serialization",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        # 2. 序列化为字典
        data = config.model_dump()

        # 3. 验证序列化结果
        assert data["name"] == "serialization_test"
        assert data["join_type"] == "join"
        assert data["game_gid"] == 91000999
        assert "id" in data
        assert "created_at" in data
        # source_events 和 join_config 在 model_dump() 时保持原类型(list/dict)
        assert isinstance(data["source_events"], list)
        assert isinstance(data["join_config"], dict)

        # 4. 反序列化
        restored_config = JoinConfigEntity(**data)
        assert restored_config.name == config.name
        assert restored_config.join_type == config.join_type

    def test_repository_returns_entities(self):
        """测试Repository返回Entity而非字典"""
        # 1. 准备测试数据(使用setup中创建的游戏)
        repo = JoinConfigRepository()
        config_data = JoinConfigEntity(
            name="repository_test",
            display_name="Repository Test",
            game_gid=91000007,
            join_type="join",
            join_config={"on": "t1.id = t2.id"},
            source_events=[1],
            output_fields=["field1"],
            output_table="dwd.test",
        )
        repo.create(config_data.model_dump())

        # 2. 通过Repository查询
        configs = repo.find_by_game_gid(91000007)
        assert len(configs) > 0

        # 3. 验证返回的是Entity类型
        config = configs[0]
        assert isinstance(config, JoinConfigEntity)
        assert hasattr(config, 'model_dump')  # Entity应该有model_dump方法
        assert config.game_gid == 91000007

    def test_service_returns_entities(self):
        """测试Service返回Entity而非字典"""
        # 1. 准备测试数据(使用setup中创建的游戏)
        service = JoinConfigService()
        config_data = JoinConfigEntity(
            name="service_test",
            display_name="Service Test",
            game_gid=91000008,
            join_type="union_all",
            source_events=[1, 2],
            output_fields=["field1"],
            output_table="dwd.test",
        )
        service.create_join_config(config_data)

        # 2. 通过Service查询
        configs = service.list_join_configs(game_gid=91000008)
        assert len(configs) > 0

        # 3. 验证返回的是Entity类型
        config = configs[0]
        assert isinstance(config, JoinConfigEntity)
        assert hasattr(config, 'model_dump')
        assert config.game_gid == 91000008

    def test_json_field_serialization(self):
        """测试JSON字段序列化/反序列化"""
        # 1. 准备测试数据(包含复杂的JSON字段, 使用setup中创建的游戏)
        service = JoinConfigService()
        config_data = JoinConfigEntity(
            name="json_test_config",
            display_name="JSON Test Config",
            game_gid=91000010,
            join_type="join",
            source_events=[1, 2, 3],
            join_config={
                "on": "t1.role_id = t2.role_id AND t1.zone_id = t2.zone_id",
                "type": "inner",
            },
            output_fields=["role_id", "zone_id", "level", "vip_level"],
            output_table="dwd.json_test",
            field_mappings={
                "role_id": {"source": "event1", "field": "roleId"},
                "zone_id": {"source": "event1", "field": "zoneId"},
            },
        )

        # 2. 创建Join Config
        created = service.create_join_config(config_data)

        # 3. 重新获取并验证JSON字段
        retrieved = service.get_join_config_by_id(created.id)
        assert retrieved is not None
        assert isinstance(retrieved.join_config, dict)
        assert retrieved.join_config["on"] == "t1.role_id = t2.role_id AND t1.zone_id = t2.zone_id"
        assert isinstance(retrieved.field_mappings, dict)
        assert len(retrieved.field_mappings) == 2

    def test_filter_by_join_type(self):
        """测试按join_type过滤"""
        # 1. 准备测试数据(使用setup中创建的游戏)
        service = JoinConfigService()
        # 创建不同类型的Join Configs
        service.create_join_config(
            JoinConfigEntity(
                name="union_config",
                display_name="Union Config",
                game_gid=91000011,
                join_type="union_all",
                source_events=[1, 2],
                output_fields=["field1"],
                output_table="dwd.union_test",
            )
        )
        service.create_join_config(
            JoinConfigEntity(
                name="join_config",
                display_name="Join Config",
                game_gid=91000011,
                join_type="join",
                join_config={"on": "t1.id = t2.id"},
                source_events=[1, 2],
                output_fields=["field1"],
                output_table="dwd.join_test",
            )
        )

        # 2. 按join_type过滤
        union_configs = service.list_join_configs(game_gid=91000011, join_type="union_all")
        join_configs = service.list_join_configs(game_gid=91000011, join_type="join")

        # 3. 验证过滤结果
        assert len(union_configs) >= 1
        assert len(join_configs) >= 1
        assert all(c.join_type == "union_all" for c in union_configs)
        assert all(c.join_type == "join" for c in join_configs)
