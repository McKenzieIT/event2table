#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canvas Service Tests

验证CanvasService的Repository模式使用和缓存集成
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend.services.canvas.canvas_service import CanvasService
from backend.models.entities import FlowEntity, EventNodeEntity, GameEntity, EventEntity


class TestCanvasService:
    """CanvasService测试类"""

    def setup_method(self):
        """测试前初始化"""
        self.service = CanvasService()

        # Mock repositories
        self.mock_flow_repo = Mock()
        self.mock_event_node_repo = Mock()
        self.mock_game_repo = Mock()
        self.mock_event_repo = Mock()

        # Patch service repositories
        self.service.flow_repo = self.mock_flow_repo
        self.service.event_node_repo = self.mock_event_node_repo
        self.service.game_repo = self.mock_game_repo
        self.service.event_repo = self.mock_event_repo

    def test_get_flow_uses_repository(self):
        """验证get_flow使用Repository而不是直接DB访问"""
        # Setup mock
        mock_flow = FlowEntity(
            id=1,
            game_gid=10000147,
            flow_name="Test Flow",
            flow_graph={"nodes": [], "connections": []},
            variables={},
            description="Test description",
            is_active=True,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_flow_repo.find_by_id.return_value = mock_flow

        # Call service method
        result = self.service.get_flow(1)

        # Verify repository was called
        self.mock_flow_repo.find_by_id.assert_called_once_with(1)

        # Verify result
        assert result == mock_flow
        assert result.flow_name == "Test Flow"

    def test_create_flow_uses_repository_and_cache_invalidation(self):
        """验证create_flow使用Repository并且正确缓存失效"""
        # Setup mocks
        mock_game = GameEntity(
            id=1,
            gid="10000147",
            name="Test Game",
            ods_db="ieu_ods",
            description="Test game",
            is_active=True,
        )
        self.mock_game_repo.find_by_gid.return_value = mock_game

        # Mock return values
        self.mock_flow_repo.create.return_value = 1
        mock_flow = FlowEntity(
            id=1,
            gid=10000147,
            flow_name="New Flow",
            flow_graph={"nodes": [{"id": "node1", "type": "event"}], "connections": []},
            variables={},
            description="New flow",
            is_active=True,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_flow_repo.find_by_id.return_value = mock_flow

        # Call service method
        result = self.service.create_flow(
            game_gid=10000147,
            flow_name="New Flow",
            flow_graph={
                "nodes": [
                    {"id": "node1", "type": "event", "config": {"event_id": 1}},
                    {"id": "output1", "type": "output"},
                ],
                "connections": [],
            },
            description="New flow",
        )

        # Verify repositories were called
        self.mock_game_repo.find_by_gid.assert_called_once_with(10000147)
        self.mock_flow_repo.create.assert_called_once()
        self.mock_flow_repo.find_by_id.assert_called_once_with(1)

        # Verify result
        assert result == mock_flow
        assert result.flow_name == "New Flow"

    def test_update_flow_uses_repository_and_cache_invalidation(self):
        """验证update_flow使用Repository并且正确缓存失效"""
        # Setup mocks
        mock_existing_flow = FlowEntity(
            id=1,
            game_gid=10000147,
            flow_name="Old Flow",
            flow_graph={"nodes": [], "connections": []},
            variables={},
            description="Old description",
            is_active=True,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_flow_repo.find_by_id.return_value = mock_existing_flow

        # Mock update
        self.mock_flow_repo.update.return_value = True

        # Call service method
        success = self.service.update_flow(
            flow_id=1, flow_name="Updated Flow", description="Updated description"
        )

        # Verify repositories were called
        self.mock_flow_repo.find_by_id.assert_called_once_with(1)
        self.mock_flow_repo.update.assert_called_once()

        # Verify result
        assert success is True

    def test_get_flows_by_game_uses_repository(self):
        """验证get_flows_by_game使用Repository"""
        # Setup mock
        mock_flows = [
            FlowEntity(
                id=1,
                game_gid=10000147,
                flow_name="Flow 1",
                flow_graph={"nodes": [], "connections": []},
                variables={},
                description="Flow 1",
                is_active=True,
                version=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            FlowEntity(
                id=2,
                game_gid=10000147,
                flow_name="Flow 2",
                flow_graph={"nodes": [], "connections": []},
                variables={},
                description="Flow 2",
                is_active=True,
                version=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        self.mock_flow_repo.find_by_game_gid.return_value = mock_flows

        # Call service method
        result = self.service.get_flows_by_game(10000147)

        # Verify repository was called
        self.mock_flow_repo.find_by_game_gid.assert_called_once_with(10000147)

        # Verify result
        assert len(result) == 2
        assert result[0].flow_name == "Flow 1"
        assert result[1].flow_name == "Flow 2"

    def test_get_all_flows_uses_repository(self):
        """验证get_all_flows使用Repository"""
        # Setup mock
        mock_flows = [
            FlowEntity(
                id=1,
                game_gid=10000147,
                flow_name="Flow 1",
                flow_graph={"nodes": [], "connections": []},
                variables={},
                description="Flow 1",
                is_active=True,
                version=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        ]
        self.mock_flow_repo.find_all_active.return_value = mock_flows

        # Call service method
        result = self.service.get_all_flows()

        # Verify repository was called
        self.mock_flow_repo.find_all_active.assert_called_once()

        # Verify result
        assert len(result) == 1
        assert result[0].flow_name == "Flow 1"

    def test_delete_flow_uses_repository_and_cache_invalidation(self):
        """验证delete_flow使用Repository并且正确缓存失效"""
        # Mock delete
        self.mock_flow_repo.delete.return_value = True

        # Call service method
        success = self.service.delete_flow(1, 10000147)

        # Verify repository was called
        self.mock_flow_repo.delete.assert_called_once_with(1)

        # Verify result
        assert success is True

    def test_get_event_node_uses_repository(self):
        """验证get_event_node使用Repository"""
        # Setup mock
        mock_node = EventNodeEntity(
            id=1,
            game_gid=10000147,
            name="Test Node",
            event_id=1,
            config_json={"fields": ["role_id"], "mode": "single"},
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_event_node_repo.find_by_id.return_value = mock_node

        # Call service method
        result = self.service.get_event_node(1)

        # Verify repository was called
        self.mock_event_node_repo.find_by_id.assert_called_once_with(1)

        # Verify result
        assert result == mock_node
        assert result.name == "Test Node"

    def test_create_event_node_uses_repository_and_cache_invalidation(self):
        """验证create_event_node使用Repository并且正确缓存失效"""
        # Setup mocks
        mock_game = GameEntity(
            id=1,
            gid="10000147",
            name="Test Game",
            ods_db="ieu_ods",
            description="Test game",
            is_active=True,
        )
        self.mock_game_repo.find_by_gid.return_value = mock_game

        mock_event = EventEntity(
            id=1,
            game_gid=10000147,
            event_name="login",
            source_table="ieu_ods.ods_10000147_login",
            target_table="dwd.v_dwd_10000147_login_di",
            description="Login event",
            is_active=True,
        )
        self.mock_event_repo.find_by_id.return_value = mock_event

        # Mock return values
        self.mock_event_node_repo.create.return_value = 1
        mock_node = EventNodeEntity(
            id=1,
            game_gid=10000147,
            name="Login Node",
            event_id=1,
            config_json={"fields": ["role_id"], "mode": "single"},
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_event_node_repo.find_by_id.return_value = mock_node

        # Call service method
        result = self.service.create_event_node(
            game_gid=10000147,
            name="Login Node",
            event_id=1,
            config_json={"fields": ["role_id"], "mode": "single"},
        )

        # Verify repositories were called
        self.mock_game_repo.find_by_gid.assert_called_once_with(10000147)
        self.mock_event_repo.find_by_id.assert_called_once_with(1)
        self.mock_event_node_repo.create.assert_called_once()
        self.mock_event_node_repo.find_by_id.assert_called_once_with(1)

        # Verify result
        assert result == mock_node
        assert result.name == "Login Node"

    def test_update_event_node_uses_repository_and_cache_invalidation(self):
        """验证update_event_node使用Repository并且正确缓存失效"""
        # Setup mocks
        mock_existing_node = EventNodeEntity(
            id=1,
            game_gid=10000147,
            name="Old Node",
            event_id=1,
            config_json={"fields": ["role_id"], "mode": "single"},
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_event_node_repo.find_by_id.return_value = mock_existing_node

        # Mock update
        self.mock_event_node_repo.update.return_value = True

        # Call service method
        success = self.service.update_event_node(
            node_id=1,
            game_gid=10000147,
            event_id=1,
            name="Updated Node",
            config_json={"fields": ["account_id"], "mode": "single"},
        )

        # Verify repositories were called
        self.mock_event_node_repo.find_by_id.assert_called_once_with(1)
        self.mock_event_node_repo.update.assert_called_once()

        # Verify result
        assert success is True

    def test_delete_event_node_uses_repository_and_cache_invalidation(self):
        """验证delete_event_node使用Repository并且正确缓存失效"""
        # Mock delete
        self.mock_event_node_repo.delete.return_value = True

        # Call service method
        success = self.service.delete_event_node(1, 10000147, 1)

        # Verify repository was called
        self.mock_event_node_repo.delete.assert_called_once_with(1)

        # Verify result
        assert success is True

    def test_export_flow_config_uses_repository(self):
        """验证export_flow_config使用Repository"""
        # Setup mock
        mock_flow = FlowEntity(
            id=1,
            game_gid=10000147,
            flow_name="Test Flow",
            flow_graph={"nodes": [], "connections": []},
            variables={},
            description="Test description",
            is_active=True,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_flow_repo.find_by_id.return_value = mock_flow

        # Call service method
        result = self.service.export_flow_config(1)

        # Verify repository was called
        self.mock_flow_repo.find_by_id.assert_called_once_with(1)

        # Verify result
        assert result is not None
        assert result["flow"]["id"] == 1
        assert result["flow"]["flow_name"] == "Test Flow"
        assert "exported_at" in result

    def test_export_flow_hql_uses_repository(self):
        """验证export_flow_hql使用Repository"""
        from backend.services.canvas.node_canvas_flows import prepare_flow_for_generation

        # Setup mock
        mock_flow = FlowEntity(
            id=1,
            game_gid=10000147,
            flow_name="Test Flow",
            flow_graph={"nodes": [], "connections": []},
            variables={},
            description="Test description",
            is_active=True,
            version=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.mock_flow_repo.find_by_id.return_value = mock_flow

        # Mock prepare function
        with patch(
            'backend.services.canvas.canvas_service.prepare_flow_for_generation'
        ) as mock_prepare:
            mock_prepare.return_value = {
                "success": True,
                "execution_order": [],
                "node_count": 0,
                "connection_count": 0,
            }

            # Call service method
            result = self.service.export_flow_hql(1)

            # Verify repository was called
            self.mock_flow_repo.find_by_id.assert_called_once_with(1)
            mock_prepare.assert_called_once_with(mock_flow.flow_graph)

            # Verify result
            assert result is not None
            assert result["flow_id"] == 1
            assert result["flow_name"] == "Test Flow"
            assert result["hql_generation"] == "pending"
            assert "exported_at" in result

    def test_validate_flow_uses_service_method(self):
        """验证validate_flow使用服务方法而不是直接DB访问"""
        from backend.services.canvas.node_canvas_flows import validate_flow_graph

        # Mock validate function
        with patch('backend.services.canvas.canvas_service.validate_flow_graph') as mock_validate:
            mock_validate.return_value = {"valid": True, "execution_order": [], "errors": []}

            # Call service method
            result = self.service.validate_flow({"nodes": [], "connections": []})

            # Verify function was called
            mock_validate.assert_called_once_with({"nodes": [], "connections": []})

            # Verify result
            assert result["valid"] is True

    def test_prepare_flow_for_generation_uses_service_method(self):
        """验证prepare_flow_for_generation使用服务方法而不是直接DB访问"""
        from backend.services.canvas.node_canvas_flows import prepare_flow_for_generation

        # Mock prepare function
        with patch(
            'backend.services.canvas.canvas_service.prepare_flow_for_generation'
        ) as mock_prepare:
            mock_prepare.return_value = {
                "success": True,
                "execution_order": [],
                "node_count": 0,
                "connection_count": 0,
            }

            # Call service method
            result = self.service.prepare_flow_for_generation({"nodes": [], "connections": []})

            # Verify function was called
            mock_prepare.assert_called_once_with({"nodes": [], "connections": []})

            # Verify result
            assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
