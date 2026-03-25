#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Module Integration Tests

测试Flow模块的端到端功能:
- FlowEntity序列化/反序列化
- FlowRepository返回Entity
- FlowService业务逻辑
- 缓存失效机制
"""

import pytest

from backend.models.entities import FlowEntity
from backend.models.repositories.flow_repository import FlowRepository
from backend.services.flows.flow_service import FlowService


@pytest.mark.integration
class TestFlowModuleIntegration:
    """Flow模块集成测试"""

    def test_entity_serialization(self):
        """测试FlowEntity序列化/反序列化"""
        # 创建Entity
        flow = FlowEntity(
            game_gid=90000101,
            flow_name="Test Flow",
            flow_graph={"nodes": [{"id": "1", "type": "table"}], "edges": []},
            variables={"var1": "value1"},
            description="Test description",
        )

        # 序列化
        flow_dict = flow.model_dump()
        assert flow_dict["flow_name"] == "Test Flow"
        assert flow_dict["flow_graph"]["nodes"][0]["id"] == "1"
        assert flow_dict["variables"]["var1"] == "value1"

        # 反序列化
        flow2 = FlowEntity(**flow_dict)
        assert flow2.flow_name == flow.flow_name
        assert flow2.flow_graph == flow.flow_graph
        assert flow2.variables == flow.variables

    def test_repository_returns_entities(self):
        """测试FlowRepository返回Entity对象"""
        repo = FlowRepository()

        # 创建测试Flow
        flow = FlowEntity(
            game_gid=90000101,
            flow_name="Test Flow for Repository",
            flow_graph={"nodes": [], "edges": []},
        )
        flow_id = repo.create(flow)

        # 查询并验证返回Entity
        retrieved_flow = repo.find_by_id(flow_id)
        assert retrieved_flow is not None
        assert isinstance(retrieved_flow, FlowEntity)
        assert retrieved_flow.flow_name == "Test Flow for Repository"
        assert isinstance(retrieved_flow.flow_graph, dict)

        # 清理
        repo.hard_delete(flow_id)

    def test_service_returns_entities(self):
        """测试FlowService返回增强的业务数据"""
        service = FlowService()

        # 创建测试Flow
        flow = FlowEntity(
            game_gid=None,  # 不关联游戏
            flow_name="Test Flow for Service",
            flow_graph={"nodes": [], "edges": []},
        )
        created_flow = service.create_flow(flow)

        # 验证创建时返回Entity
        assert isinstance(created_flow, FlowEntity)
        assert created_flow.flow_name == "Test Flow for Service"

        # 查询并验证增强数据(GREEN阶段: 包含业务逻辑)
        retrieved_flow = service.get_flow_by_id(created_flow.id)
        assert retrieved_flow is not None
        assert isinstance(retrieved_flow, dict)  # 返回增强的字典, 而非Entity

        # 验证业务状态检查
        assert 'status' in retrieved_flow
        assert retrieved_flow['status'] in ['active', 'inactive', 'archived']
        assert retrieved_flow['status'] == 'active'  # 新创建的flow应该是active

        # 验证数据增强: 使用统计
        assert 'usage_stats' in retrieved_flow
        assert 'views' in retrieved_flow['usage_stats']
        assert 'last_used' in retrieved_flow['usage_stats']

        # 验证数据增强: 最后修改时间
        assert 'last_modified' in retrieved_flow

        # 验证原始数据仍然存在
        assert retrieved_flow['flow_name'] == "Test Flow for Service"
        assert retrieved_flow['flow_graph'] == {"nodes": [], "edges": []}

        # 清理
        service.hard_delete_flow(created_flow.id)

    def test_json_field_serialization(self):
        """测试JSON字段的自动序列化"""
        repo = FlowRepository()

        # 创建包含复杂JSON的Flow (不关联game)
        flow = FlowEntity(
            game_gid=None,  # 不关联游戏
            flow_name="Complex Flow",
            flow_graph={
                "nodes": [
                    {"id": "1", "type": "table", "data": {"table": "ods_event_log"}},
                    {"id": "2", "type": "filter", "data": {"conditions": []}},
                ],
                "edges": [{"source": "1", "target": "2", "label": "filter"}],
            },
            variables={"database": "ieu_ods", "date_range": "2024-01-01:2024-12-31"},
        )

        flow_id = repo.create(flow)

        # 读取并验证JSON字段正确反序列化
        retrieved_flow = repo.find_by_id(flow_id)
        assert retrieved_flow is not None
        assert len(retrieved_flow.flow_graph["nodes"]) == 2
        assert retrieved_flow.flow_graph["edges"][0]["source"] == "1"
        assert retrieved_flow.variables["database"] == "ieu_ods"

        # 清理
        repo.hard_delete(flow_id)

    def test_create_flow_flow(self):
        """测试创建Flow完整流程"""
        service = FlowService()

        # 创建Flow (不关联game)
        flow = FlowEntity(
            game_gid=None,  # 不关联游戏
            flow_name="Complete Test Flow",
            flow_graph={"nodes": [], "edges": []},
            description="Complete flow test",
        )

        created_flow = service.create_flow(flow)

        # 验证创建成功
        assert created_flow.id is not None
        assert created_flow.flow_name == "Complete Test Flow"
        assert created_flow.is_active is True

        # 清理
        service.hard_delete_flow(created_flow.id)

    def test_update_flow_flow(self):
        """测试更新Flow流程"""
        service = FlowService()

        # 创建Flow (不关联game)
        flow = FlowEntity(
            game_gid=None, flow_name="Flow to Update", flow_graph={"nodes": [], "edges": []}
        )
        created_flow = service.create_flow(flow)

        # 更新Flow
        updated_flow_data = FlowEntity(
            flow_name="Updated Flow Name",
            description="Updated description",
            flow_graph={"nodes": [{"id": "1"}], "edges": []},
        )

        updated_flow = service.update_flow(created_flow.id, updated_flow_data)

        # 验证更新成功
        assert updated_flow.flow_name == "Updated Flow Name"
        assert updated_flow.description == "Updated description"

        # 清理
        service.hard_delete_flow(created_flow.id)

    def test_delete_flow_flow(self):
        """测试删除Flow流程"""
        service = FlowService()

        # 创建Flow (不关联game)
        flow = FlowEntity(
            game_gid=None, flow_name="Flow to Delete", flow_graph={"nodes": [], "edges": []}
        )
        created_flow = service.create_flow(flow)

        # 删除Flow
        success = service.delete_flow(created_flow.id)
        assert success is True

        # 验证已软删除(返回增强数据, 包含status字段)
        deleted_flow = service.get_flow_by_id(created_flow.id)
        assert deleted_flow is not None
        assert deleted_flow['status'] == 'inactive'  # 软删除后状态为inactive
        assert deleted_flow['flow_name'] == "Flow to Delete"
        assert deleted_flow['is_active'] is False  # 原始字段仍然存在

    def test_get_flows_by_game_gid(self):
        """测试查询所有激活Flow"""
        service = FlowService()

        # 创建多个Flow (不关联game)
        flow1 = FlowEntity(
            game_gid=None, flow_name="Test Flow 1", flow_graph={"nodes": [], "edges": []}
        )
        flow2 = FlowEntity(
            game_gid=None, flow_name="Test Flow 2", flow_graph={"nodes": [], "edges": []}
        )

        service.create_flow(flow1)
        service.create_flow(flow2)

        # 查询所有Flow
        flows = service.get_all_active_flows()
        assert len(flows) >= 2
        assert all(isinstance(f, FlowEntity) for f in flows)

    def test_count_flows_by_game_gid(self):
        """测试统计Flow数量"""
        service = FlowService()

        count = service.count_flows_by_game_gid(90000101)
        assert isinstance(count, int)
        assert count >= 0
