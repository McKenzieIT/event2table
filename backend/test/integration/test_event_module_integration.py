#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Module Integration Tests

集成测试验证Event模块的完整流程:
- API → Service → Repository → Entity → Database
- 缓存失效机制
- 错误处理
- 数据验证
"""

from datetime import datetime

import pytest

from backend.core.utils.converters import get_db_connection
from backend.models.entities import EventEntity, GameEntity
from backend.models.repositories.events import EventRepository
from backend.models.repositories.games import GameRepository
from backend.services.events.event_service import EventService


class TestEventModuleIntegration:
    """Event模块集成测试"""

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """测试前设置数据库"""
        import os

        os.environ["FLASK_ENV"] = "testing"

        # 确保测试游戏存在
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 创建测试游戏
            cursor.execute(
                """
                INSERT OR IGNORE INTO games (gid, name, ods_db, dwd_prefix)
                VALUES (92000001, 'E2E Test Game', 'ieu_ods', 'dwd')
            """
            )
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
            cursor.execute("DELETE FROM log_events WHERE game_gid >= 92000000")
            cursor.execute(
                "DELETE FROM event_params WHERE event_id IN (SELECT id FROM log_events WHERE game_gid >= 92000000)"
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def test_create_event_flow(self):
        """测试完整的事件创建流程"""
        # 1. 准备数据
        event_data = EventEntity(
            game_gid=92000001,
            name="e2e_test_event",
            name_cn="E2E测试事件",
            description="Test event for integration testing",
        )

        # 2. 通过Service创建事件
        service = EventService()
        created_event = service.create_event(event_data)

        # 3. 验证创建结果
        assert created_event is not None
        assert created_event.name == "e2e_test_event"
        assert created_event.game_gid == 92000001
        assert created_event.id is not None

        # 4. 验证数据库记录
        repo = EventRepository()
        retrieved_event = repo.find_by_id(created_event.id)
        assert retrieved_event is not None
        assert retrieved_event.name == "e2e_test_event"

    def test_get_event_by_id(self):
        """测试通过ID获取事件"""
        # 1. 创建测试事件
        service = EventService()
        event_data = EventEntity(game_gid=92000001, name="test_get_by_id", name_cn="测试获取")
        created = service.create_event(event_data)

        # 2. 通过Service获取事件
        event = service.get_event_by_id(created.id)

        # 3. 验证结果
        assert event is not None
        assert event.name == "test_get_by_id"
        assert isinstance(event, EventEntity)

    def test_update_event_flow(self):
        """测试事件更新流程"""
        # 1. 创建测试事件
        service = EventService()
        event_data = EventEntity(game_gid=92000001, name="test_update", name_cn="测试更新")
        created = service.create_event(event_data)

        # 2. 更新事件
        updates = {"name_cn": "已更新的测试"}
        updated_event = service.update_event(created.id, updates)

        # 3. 验证更新结果
        assert updated_event.name_cn == "已更新的测试"

    def test_delete_event_flow(self):
        """测试事件删除流程"""
        # 1. 创建测试事件
        service = EventService()
        event_data = EventEntity(game_gid=92000001, name="test_delete", name_cn="测试删除")
        created = service.create_event(event_data)
        event_id = created.id

        # 2. 删除事件
        service.delete_event(event_id)

        # 3. 验证删除结果
        event = service.get_event_by_id(event_id)
        assert event is None

    def test_event_validation(self):
        """测试事件数据验证"""
        service = EventService()

        # 测试1: 创建重复名称的事件
        event_data1 = EventEntity(game_gid=92000001, name="duplicate_test", name_cn="重复测试1")
        service.create_event(event_data1)

        # 尝试创建相同名称的事件
        event_data2 = EventEntity(game_gid=92000001, name="duplicate_test", name_cn="重复测试2")
        with pytest.raises(ValueError) as exc_info:
            service.create_event(event_data2)
        assert "already exists" in str(exc_info.value)

    def test_get_events_by_game(self):
        """测试获取游戏的所有事件"""
        # 1. 创建多个测试事件并保存ID
        service = EventService()
        created_ids = []
        for i in range(3):
            event_data = EventEntity(
                game_gid=92000001,
                name=f"test_event_by_game_{i}",  # 使用唯一名称避免冲突
                name_cn=f"测试事件{i}",
            )
            created = service.create_event(event_data)
            created_ids.append(created.id)

        try:
            # 2. 获取所有事件
            result = service.get_events_by_game(92000001)
            events = result.get('events', []) if isinstance(result, dict) else result

            # 3. 验证结果 - 检查我们创建的事件存在
            created_event_names = [f"test_event_by_game_{i}" for i in range(3)]
            found_events = [e for e in events if e.name in created_event_names]

            assert (
                len(found_events) == 3
            ), f"Expected to find 3 created events, but found {len(found_events)}"
            # 检查所有返回的都是EventEntity
            for event in found_events:
                assert isinstance(event, EventEntity)
                assert event.game_gid == 92000001
        finally:
            # 清理创建的事件
            for event_id in created_ids:
                try:
                    service.delete_event(event_id)
                except:
                    pass

    def test_entity_serialization(self):
        """测试EventEntity序列化"""
        # 1. 创建Entity
        event = EventEntity(
            id=1,
            game_gid=92000001,
            name="test_serialization",
            name_cn="测试序列化",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
        )

        # 2. 序列化为字典
        data = event.model_dump()

        # 3. 验证序列化结果
        assert data["game_gid"] == 92000001
        # EventEntity使用event_name字段
        assert data["event_name"] == "test_serialization"
        assert "id" in data
        assert "created_at" in data

        # 4. 反序列化
        restored_event = EventEntity(**data)
        assert restored_event.game_gid == event.game_gid
        assert restored_event.event_name == event.event_name

    def test_repository_returns_entities(self):
        """测试Repository返回Entity而非字典"""
        repo = EventRepository()

        # 1. 创建测试数据
        service = EventService()
        event_data = EventEntity(game_gid=92000001, name="repo_test", name_cn="仓库测试")
        created = service.create_event(event_data)

        # 2. 通过Repository查询
        event = repo.find_by_id(created.id)

        # 3. 验证返回的是Entity类型
        assert event is not None
        assert isinstance(event, EventEntity)
        assert event.name == "repo_test"
        assert hasattr(event, 'model_dump')  # Entity应该有model_dump方法

    def test_service_returns_entities(self):
        """测试Service返回Entity而非字典"""
        service = EventService()

        # 1. 创建测试数据
        event_data = EventEntity(game_gid=92000001, name="service_test", name_cn="服务测试")
        created = service.create_event(event_data)

        # 2. 通过Service查询
        event = service.get_event_by_id(created.id)

        # 3. 验证返回的是Entity类型
        assert event is not None
        assert isinstance(event, EventEntity)
        assert event.name == "service_test"
