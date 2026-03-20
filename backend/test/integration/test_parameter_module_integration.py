#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Module Integration Tests

集成测试验证Parameter模块的完整流程:
- API → Service → Repository → Entity → Database
- 缓存失效机制
- 错误处理
- 数据验证
"""

import pytest
from backend.models.entities import ParameterEntity, EventEntity, GameEntity
from backend.services.parameters.parameter_service import ParameterService
from backend.models.repositories.parameters import ParameterRepository
from backend.models.repositories.events import EventRepository
from backend.services.events.event_service import EventService
from backend.core.utils.converters import get_db_connection


class TestParameterModuleIntegration:
    """Parameter模块集成测试"""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """测试前设置数据库"""
        import os

        os.environ["FLASK_ENV"] = "testing"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 创建测试游戏
            cursor.execute("""
                INSERT OR IGNORE INTO games (gid, name, ods_db, dwd_prefix)
                VALUES (93000001, 'E2E Test Game', 'ieu_ods', 'dwd')
            """)

            # 创建测试事件 (只使用game_gid, 不使用废弃的game_id)
            cursor.execute("""
                INSERT OR IGNORE INTO log_events (game_gid, event_name, event_name_cn, source_table, target_table)
                VALUES (93000001, 'test_event', '测试事件', 'ieu_ods.unknown', 'dwd.unknown')
            """)

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

        yield

        # 清理测试数据
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "DELETE FROM event_params WHERE event_id IN (SELECT id FROM log_events WHERE game_gid >= 93000000)"
            )
            cursor.execute("DELETE FROM log_events WHERE game_gid >= 93000000")
            cursor.execute("DELETE FROM games WHERE cast(gid as integer) >= 93000000")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def test_create_parameter_flow(self):
        """测试完整的参数创建流程"""
        # 1. 获取事件ID
        event_repo = EventRepository()
        event = event_repo.find_by_name("test_event", 93000001)
        assert event is not None

        # 2. 准备参数数据
        param_data = ParameterEntity(
            event_id=event.id,
            game_gid=93000001,
            name="test_param",
            param_type="base",
            json_path="$.testParam",
            hive_type="STRING",
            description="Test parameter",
        )

        # 3. 通过Service创建参数
        service = ParameterService()
        created_param = service.create_parameter(param_data.model_dump())

        # 4. 验证创建结果
        assert created_param is not None
        assert created_param.name == "test_param"
        assert created_param.param_type == "base"

    def test_get_parameter_by_id(self):
        """测试通过ID获取参数"""
        # 1. 获取事件ID
        event_repo = EventRepository()
        event = event_repo.find_by_name("test_event", 93000001)
        assert event is not None

        # 2. 先创建一个参数
        service = ParameterService()
        param_data = {
            "event_id": event.id,
            "game_gid": 93000001,
            "name": "get_by_id_test",
            "param_type": "param",
            "json_path": "$.test",
            "hive_type": "INT",
        }
        created = service.create_parameter(param_data)

        # 3. 通过Service获取参数
        param = service.get_parameter_by_id(created.id)

        # 4. 验证结果
        assert param is not None
        assert param.name == "get_by_id_test"
        assert isinstance(param, ParameterEntity)

    def test_update_parameter_flow(self):
        """测试参数更新流程"""
        # 1. 获取事件ID
        event_repo = EventRepository()
        event = event_repo.find_by_name("test_event", 93000001)
        assert event is not None

        # 2. 创建参数
        service = ParameterService()
        param_data = {
            "event_id": event.id,
            "game_gid": 93000001,
            "name": "update_test",
            "param_type": "base",
            "description": "原始描述",
        }
        created = service.create_parameter(param_data)

        # 3. 更新参数
        updates = {"description": "更新后的描述"}
        updated_param = service.update_parameter(created.id, updates)

        # 4. 验证更新结果
        assert updated_param.description == "更新后的描述"

    def test_delete_parameter_flow(self):
        """测试参数删除流程"""
        # 1. 获取事件ID
        event_repo = EventRepository()
        event = event_repo.find_by_name("test_event", 93000001)
        assert event is not None

        # 2. 创建参数
        service = ParameterService()
        param_data = {
            "event_id": event.id,
            "game_gid": 93000001,
            "name": "delete_test",
            "param_type": "common",
        }
        created = service.create_parameter(param_data)
        param_id = created.id

        # 3. 删除参数
        service.delete_parameter(param_id)

        # 4. 验证删除结果
        param = service.get_parameter_by_id(param_id)
        assert param is None

    def test_get_parameters_by_event(self):
        """测试获取事件的所有参数"""
        # 1. 获取事件ID
        event_repo = EventRepository()
        event = event_repo.find_by_name("test_event", 93000001)
        assert event is not None

        # 2. 创建多个参数
        service = ParameterService()
        for i in range(3):
            param_data = {
                "event_id": event.id,
                "game_gid": 93000001,
                "name": f"test_param_{i}",
                "param_type": "base" if i % 2 == 0 else "param",
            }
            service.create_parameter(param_data)

        # 3. 获取所有参数
        params = service.get_parameters_by_event(event.id)

        # 4. 验证结果
        assert len(params) >= 3
        # 检查所有返回的都是ParameterEntity
        for param in params[:3]:
            assert isinstance(param, ParameterEntity)
            assert param.name.startswith("test_param_")

    def test_parameter_validation(self):
        """测试参数数据验证"""
        # 1. 获取事件ID
        event_repo = EventRepository()
        event = event_repo.find_by_name("test_event", 93000001)
        assert event is not None

        service = ParameterService()

        # 测试1: 创建重复名称的参数(同一事件)
        param_data1 = {
            "event_id": event.id,
            "game_gid": 93000001,
            "name": "duplicate_param",
            "param_type": "base",
        }
        service.create_parameter(param_data1)

        # 尝试创建相同名称的参数
        param_data2 = {
            "event_id": event.id,
            "game_gid": 93000001,
            "name": "duplicate_param",
            "param_type": "param",
        }
        with pytest.raises(ValueError) as exc_info:
            service.create_parameter(param_data2)
        assert "already exists" in str(exc_info.value).lower()

    def test_entity_serialization(self):
        """测试ParameterEntity序列化"""
        # 1. 创建Entity
        param = ParameterEntity(
            id=1,
            event_id=100,
            game_gid=93000001,
            name="test_param",
            param_type="base",
            json_path="$.testPath",
        )

        # 2. 序列化为字典
        data = param.model_dump()

        # 3. 验证序列化结果
        assert data["game_gid"] == 93000001
        assert data["name"] == "test_param"
        assert data["param_type"] == "base"
        assert "id" in data

        # 4. 反序列化
        restored_param = ParameterEntity(**data)
        assert restored_param.game_gid == param.game_gid
        assert restored_param.name == param.name

    def test_repository_returns_entities(self):
        """测试Repository返回Entity而非字典"""
        # 1. 获取事件ID
        event_repo = EventRepository()
        event = event_repo.find_by_name("test_event", 93000001)
        assert event is not None

        repo = ParameterRepository()
        service = ParameterService()

        # 2. 创建测试数据
        param_data = {
            "event_id": event.id,
            "game_gid": 93000001,
            "name": "repo_test",
            "param_type": "calculate",
        }
        created = service.create_parameter(param_data)

        # 3. 通过Repository查询
        param = repo.find_by_id(created.id)

        # 4. 验证返回的是Entity类型
        assert param is not None
        assert isinstance(param, ParameterEntity)
        assert param.name == "repo_test"
        assert hasattr(param, 'model_dump')

    def test_service_returns_entities(self):
        """测试Service返回Entity而非字典"""
        # 1. 获取事件ID
        event_repo = EventRepository()
        event = event_repo.find_by_name("test_event", 93000001)
        assert event is not None

        service = ParameterService()

        # 2. 创建测试数据
        param_data = {
            "event_id": event.id,
            "game_gid": 93000001,
            "name": "service_test",
            "param_type": "common",
        }
        created = service.create_parameter(param_data)

        # 3. 通过Service查询
        param = service.get_parameter_by_id(created.id)

        # 4. 验证返回的是Entity类型
        assert param is not None
        assert isinstance(param, ParameterEntity)
        assert param.name == "service_test"
