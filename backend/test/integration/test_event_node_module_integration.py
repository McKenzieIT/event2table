#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Node Module Integration Tests

测试EventNodeEntity, EventNodeRepository, EventNodeService的集成
"""

import pytest

from backend.models.entities import EventNodeEntity
from backend.models.repositories.event_node_repository import EventNodeRepository
from backend.models.repositories.events import EventRepository
from backend.models.repositories.games import GameRepository
from backend.services.events.event_node_service import EventNodeService


@pytest.mark.integration
class TestEventNodeModuleIntegration:
    """Event Node模块集成测试"""

    def test_entity_serialization(self):
        """测试EventNodeEntity序列化/反序列化"""
        node = EventNodeEntity(
            game_gid=90000101,
            name="Test Event Node",
            event_id=1,
            config_json={"fields": ["role_id", "zone_id"], "mode": "single"},
        )
        node_dict = node.model_dump()

        assert node_dict["game_gid"] == 90000101
        assert node_dict["name"] == "Test Event Node"
        assert node_dict["config_json"]["fields"][0] == "role_id"
        assert node_dict["config_json"]["mode"] == "single"

    def test_repository_returns_entities(self):
        """测试EventNodeRepository返回Entity对象"""
        repo = EventNodeRepository()

        # 创建测试游戏和事件
        game_repo = GameRepository()
        game_repo.create(
            {
                "gid": 92019896,
                "name": "Test Game for EventNode",
                "ods_db": "ieu_ods",
                "dwd_prefix": "dwd",
            }
        )

        event_repo = EventRepository()
        created_event = event_repo.create(
            {
                "game_gid": 92019896,
                "event_name": "test_event",
                "event_name_cn": "测试事件",
            }
        )
        event_id = created_event.id  # 提取ID

        # 创建EventNode
        node = EventNodeEntity(
            game_gid=92019896,
            name="Test Node for Repository",
            event_id=event_id,
            config_json={"fields": [], "mode": "single"},
        )
        node_id = repo.create(node)

        # 查询并验证返回Entity
        retrieved_node = repo.find_by_id(node_id)
        assert isinstance(retrieved_node, EventNodeEntity)
        assert retrieved_node.name == "Test Node for Repository"
        assert retrieved_node.config_json["mode"] == "single"

        # 清理
        repo.hard_delete(node_id)
        game_repo.delete(92019896)

    def test_service_returns_entities(self):
        """测试EventNodeService返回Entity对象"""
        service = EventNodeService()

        # 创建测试游戏和事件
        game_repo = GameRepository()
        game_repo.create(
            {
                "gid": 92019897,
                "name": "Test Game for Service",
                "ods_db": "ieu_ods",
                "dwd_prefix": "dwd",
            }
        )

        event_repo = EventRepository()
        created_event = event_repo.create(
            {
                "game_gid": 92019897,
                "event_name": "test_event_service",
                "event_name_cn": "测试事件服务",
            }
        )
        event_id = created_event.id  # 提取ID

        # 创建测试EventNode
        node = EventNodeEntity(
            game_gid=92019897,
            name="Test Node for Service",
            event_id=event_id,
            config_json={"fields": ["role_id"], "mode": "single"},
        )
        created_node = service.create_node(node)

        # 验证返回Entity
        assert isinstance(created_node, EventNodeEntity)
        assert created_node.name == "Test Node for Service"
        assert created_node.config_json["fields"][0] == "role_id"

        # 查询并验证
        retrieved_node = service.get_node_by_id(created_node.id)
        assert isinstance(retrieved_node, EventNodeEntity)

        # 清理
        service.hard_delete_node(created_node.id)
        game_repo.delete(92019897)

    def test_json_field_serialization(self):
        """测试JSON字段的自动序列化"""
        repo = EventNodeRepository()

        # 创建测试游戏和事件
        game_repo = GameRepository()
        game_repo.create(
            {
                "gid": 92019898,
                "name": "Test Game for JSON",
                "ods_db": "ieu_ods",
                "dwd_prefix": "dwd",
            }
        )

        event_repo = EventRepository()
        created_event = event_repo.create(
            {
                "game_gid": 92019898,
                "event_name": "test_event_json",
                "event_name_cn": "测试事件JSON",
            }
        )
        event_id = created_event.id  # 提取ID

        # 创建包含复杂JSON的EventNode
        node = EventNodeEntity(
            game_gid=92019898,
            name="Complex Node",
            event_id=event_id,
            config_json={
                "fields": ["role_id", "zone_id", "account_id"],
                "conditions": [{"field": "zone_id", "operator": ">", "value": "1"}],
                "mode": "where",
                "joins": [],
            },
        )
        node_id = repo.create(node)

        # 验证JSON正确序列化和反序列化
        retrieved = repo.find_by_id(node_id)
        assert isinstance(retrieved.config_json, dict)
        assert len(retrieved.config_json["fields"]) == 3
        assert len(retrieved.config_json["conditions"]) == 1
        assert retrieved.config_json["conditions"][0]["field"] == "zone_id"

        # 清理
        repo.hard_delete(node_id)
        game_repo.delete(92019898)

    def test_create_event_node(self):
        """测试创建事件节点"""
        service = EventNodeService()

        # 创建测试游戏和事件
        game_repo = GameRepository()
        game_repo.create(
            {
                "gid": 92019899,
                "name": "Test Game for Create",
                "ods_db": "ieu_ods",
                "dwd_prefix": "dwd",
            }
        )

        event_repo = EventRepository()
        created_event = event_repo.create(
            {
                "game_gid": 92019899,
                "event_name": "test_event_create",
                "event_name_cn": "测试事件创建",
            }
        )
        event_id = created_event.id  # 提取ID

        # 创建EventNode
        node = EventNodeEntity(
            game_gid=92019899,
            name="Node to Create",
            event_id=event_id,
            config_json={"fields": [], "mode": "single"},
        )
        created_node = service.create_node(node)

        assert created_node.id is not None
        assert created_node.name == "Node to Create"
        assert created_node.is_active is True

        # 清理
        service.hard_delete_node(created_node.id)
        game_repo.delete(92019899)

    def test_update_event_node(self):
        """测试更新事件节点"""
        service = EventNodeService()

        # 创建测试游戏和事件
        game_repo = GameRepository()
        game_repo.create(
            {
                "gid": 92019900,
                "name": "Test Game for Update",
                "ods_db": "ieu_ods",
                "dwd_prefix": "dwd",
            }
        )

        event_repo = EventRepository()
        created_event = event_repo.create(
            {
                "game_gid": 92019900,
                "event_name": "test_event_update",
                "event_name_cn": "测试事件更新",
            }
        )
        event_id = created_event.id  # 提取ID

        # 创建EventNode
        node = EventNodeEntity(
            game_gid=92019900,
            name="Node to Update",
            event_id=event_id,
            config_json={"fields": ["role_id"], "mode": "single"},
        )
        created_node = service.create_node(node)

        # 更新EventNode
        updated_data = EventNodeEntity(
            game_gid=92019900,
            name="Updated Node Name",
            event_id=event_id,
            config_json={"fields": ["role_id", "zone_id"], "mode": "where"},
        )
        updated_node = service.update_node(created_node.id, updated_data)

        assert updated_node.name == "Updated Node Name"
        assert len(updated_node.config_json["fields"]) == 2
        assert updated_node.config_json["mode"] == "where"

        # 清理
        service.hard_delete_node(created_node.id)
        game_repo.delete(92019900)

    def test_delete_event_node(self):
        """测试删除事件节点(软删除)"""
        service = EventNodeService()

        # 创建测试游戏和事件
        game_repo = GameRepository()
        game_repo.create(
            {
                "gid": 92019901,
                "name": "Test Game for Delete",
                "ods_db": "ieu_ods",
                "dwd_prefix": "dwd",
            }
        )

        event_repo = EventRepository()
        created_event = event_repo.create(
            {
                "game_gid": 92019901,
                "event_name": "test_event_delete",
                "event_name_cn": "测试事件删除",
            }
        )
        event_id = created_event.id  # 提取ID

        # 创建EventNode
        node = EventNodeEntity(
            game_gid=92019901,
            name="Node to Delete",
            event_id=event_id,
            config_json={"fields": [], "mode": "single"},
        )
        created_node = service.create_node(node)

        # 删除EventNode
        success = service.delete_node(created_node.id)
        assert success is True

        # 验证已软删除
        deleted_node = service.get_node_by_id(created_node.id)
        assert deleted_node is None  # 软删除后查询应返回None

        # 清理
        game_repo.delete(92019901)

    def test_get_nodes_by_game_gid(self):
        """测试查询指定游戏的所有EventNode"""
        service = EventNodeService()

        # 创建测试游戏和事件
        game_repo = GameRepository()
        game_repo.create(
            {
                "gid": 92019902,
                "name": "Test Game for Get",
                "ods_db": "ieu_ods",
                "dwd_prefix": "dwd",
            }
        )

        event_repo = EventRepository()
        created_event = event_repo.create(
            {
                "game_gid": 92019902,
                "event_name": "test_event_get",
                "event_name_cn": "测试事件查询",
            }
        )
        event_id = created_event.id  # 提取ID

        # 创建多个EventNode
        node1 = EventNodeEntity(
            game_gid=92019902,
            name="Test Node 1",
            event_id=event_id,
            config_json={"fields": [], "mode": "single"},
        )
        node2 = EventNodeEntity(
            game_gid=92019902,
            name="Test Node 2",
            event_id=event_id,
            config_json={"fields": [], "mode": "single"},
        )

        service.create_node(node1)
        service.create_node(node2)

        # 查询所有EventNode
        nodes = service.get_nodes_by_game_gid(92019902)
        assert len(nodes) >= 2
        node_names = [n.name for n in nodes]
        assert "Test Node 1" in node_names
        assert "Test Node 2" in node_names

        # 清理
        game_repo.delete(92019902)

    def test_count_nodes_by_game_gid(self):
        """测试统计指定游戏的EventNode数量"""
        service = EventNodeService()

        # 创建测试游戏和事件
        game_repo = GameRepository()
        game_repo.create(
            {
                "gid": 92019903,
                "name": "Test Game for Count",
                "ods_db": "ieu_ods",
                "dwd_prefix": "dwd",
            }
        )

        event_repo = EventRepository()
        created_event = event_repo.create(
            {
                "game_gid": 92019903,
                "event_name": "test_event_count",
                "event_name_cn": "测试事件统计",
            }
        )
        event_id = created_event.id  # 提取ID

        # 创建3个EventNode
        for i in range(3):
            node = EventNodeEntity(
                game_gid=92019903,
                name=f"Count Test Node {i+1}",
                event_id=event_id,
                config_json={"fields": [], "mode": "single"},
            )
            service.create_node(node)

        # 统计数量
        count = service.count_nodes_by_game_gid(92019903)
        assert count == 3

        # 清理
        game_repo.delete(92019903)
