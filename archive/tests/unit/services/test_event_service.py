#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EventService 单元测试
测试缓存集成功能
"""

import pytest
from unittest.mock import Mock, patch
from backend.services.events.event_service import EventService


class TestEventServiceCache:
    """EventService缓存功能测试"""

    @pytest.fixture
    def event_service(self):
        """创建EventService实例"""
        with patch('backend.services.events.event_service.EventRepository'), \
             patch('backend.services.events.event_service.GameRepository'):
            return EventService()

    def test_get_events_by_game_with_cache(self, event_service):
        """测试根据游戏GID获取事件列表（带缓存）"""
        # Mock数据
        mock_events = [
            {"id": 1, "event_name": "Event1", "game_gid": 100},
            {"id": 2, "event_name": "Event2", "game_gid": 100},
        ]
        event_service.game_repo.find_by_gid = Mock(return_value={"id": 1, "gid": 100})
        event_service.event_repo.find_by_game_gid = Mock(return_value=mock_events)
        event_service.event_repo.count_by_game_gid = Mock(return_value=2)

        # 调用方法
        result = event_service.get_events_by_game(100, page=1, per_page=20)

        # 验证结果
        assert result["total"] == 2
        assert len(result["events"]) == 2
        assert result["page"] == 1
        assert result["total_pages"] == 1

    def test_get_events_by_game_not_found(self, event_service):
        """测试获取不存在游戏的事件"""
        # Mock数据
        event_service.game_repo.find_by_gid = Mock(return_value=None)

        # 验证抛出异常
        with pytest.raises(ValueError, match="Game not found"):
            event_service.get_events_by_game(999)

    def test_get_event_by_id_with_cache(self, event_service):
        """测试根据ID获取事件（带缓存）"""
        # Mock数据
        mock_event = {"id": 1, "event_name": "TestEvent", "game_gid": 100}
        event_service.event_repo.find_by_id = Mock(return_value=mock_event)

        # 调用方法
        result = event_service.get_event_by_id(1)

        # 验证结果
        assert result is not None
        assert result["event_name"] == "TestEvent"
        event_service.event_repo.find_by_id.assert_called_once_with(1)

    def test_get_event_with_params_with_cache(self, event_service):
        """测试获取事件及其参数（带缓存）"""
        # Mock数据
        mock_event_with_params = {
            "id": 1,
            "event_name": "TestEvent",
            "game_gid": 100,
            "parameters": [
                {"name": "param1", "type": "string"},
                {"name": "param2", "type": "int"},
            ]
        }
        event_service.event_repo.get_with_parameters = Mock(return_value=mock_event_with_params)

        # 调用方法
        result = event_service.get_event_with_params(1)

        # 验证结果
        assert result is not None
        assert len(result["parameters"]) == 2
        assert result["parameters"][0]["name"] == "param1"

    def test_create_event_invalidates_cache(self, event_service):
        """测试创建事件时失效缓存"""
        # Mock数据
        event_data = {
            "game_gid": 100,
            "event_name": "NewEvent",
            "category": "test"
        }
        event_service.game_repo.find_by_gid = Mock(return_value={"id": 1, "gid": 100})
        event_service.event_repo.find_by_name = Mock(return_value=None)
        event_service.event_repo.create = Mock(return_value={"id": 1})
        event_service.event_repo.find_by_id = Mock(return_value={
            "id": 1, "event_name": "NewEvent", "game_gid": 100
        })

        with patch('backend.services.events.event_service.CacheInvalidator') as mock_cache:
            # 调用方法
            result = event_service.create_event(event_data)

            # 验证缓存失效被调用
            mock_cache.invalidate_pattern.assert_called_once()
            assert result["event_name"] == "NewEvent"

    def test_create_event_missing_game_gid(self, event_service):
        """测试创建事件时缺少game_gid"""
        # Mock数据
        event_data = {"event_name": "NewEvent"}

        # 验证抛出异常
        with pytest.raises(ValueError, match="game_gid is required"):
            event_service.create_event(event_data)

    def test_create_event_missing_event_name(self, event_service):
        """测试创建事件时缺少event_name"""
        # Mock数据
        event_data = {"game_gid": 100}
        event_service.game_repo.find_by_gid = Mock(return_value={"id": 1, "gid": 100})

        # 验证抛出异常
        with pytest.raises(ValueError, match="event_name is required"):
            event_service.create_event(event_data)

    def test_create_event_duplicate_name(self, event_service):
        """测试创建事件时名称重复"""
        # Mock数据
        event_data = {
            "game_gid": 100,
            "event_name": "ExistingEvent",
            "category": "test"
        }
        event_service.game_repo.find_by_gid = Mock(return_value={"id": 1, "gid": 100})
        event_service.event_repo.find_by_name = Mock(return_value={
            "id": 1, "event_name": "ExistingEvent", "game_gid": 100
        })

        # 验证抛出异常
        with pytest.raises(ValueError, match="already exists"):
            event_service.create_event(event_data)

    def test_update_event_invalidates_cache(self, event_service):
        """测试更新事件时失效缓存"""
        # Mock数据
        updates = {"event_name": "UpdatedEvent"}
        event_service.event_repo.find_by_id = Mock(return_value={
            "id": 1, "event_name": "OldEvent", "game_gid": 100
        })
        event_service.event_repo.update = Mock(return_value=True)

        with patch('backend.services.events.event_service.CacheInvalidator') as mock_cache:
            # 调用方法
            result = event_service.update_event(1, updates)

            # 验证缓存失效被调用
            mock_cache.invalidate_event.assert_called_once_with(1)
            mock_cache.invalidate_pattern.assert_called_once()

    def test_update_event_not_found(self, event_service):
        """测试更新不存在的事件"""
        # Mock数据
        updates = {"event_name": "UpdatedEvent"}
        event_service.event_repo.find_by_id = Mock(return_value=None)

        # 验证抛出异常
        with pytest.raises(ValueError, match="not found"):
            event_service.update_event(999, updates)

    def test_delete_event_invalidates_cache(self, event_service):
        """测试删除事件时失效缓存"""
        # Mock数据
        event_service.event_repo.find_by_id = Mock(return_value={
            "id": 1, "event_name": "TestEvent", "game_gid": 100
        })
        event_service.event_repo.delete = Mock(return_value=True)

        with patch('backend.services.events.event_service.CacheInvalidator') as mock_cache:
            # 调用方法
            result = event_service.delete_event(1)

            # 验证缓存失效被调用
            mock_cache.invalidate_event.assert_called_once_with(1)
            mock_cache.invalidate_pattern.assert_called_once()
            assert result is True

    def test_delete_event_not_found(self, event_service):
        """测试删除不存在的事件"""
        # Mock数据
        event_service.event_repo.find_by_id = Mock(return_value=None)

        # 验证抛出异常
        with pytest.raises(ValueError, match="not found"):
            event_service.delete_event(999)

    def test_search_events(self, event_service):
        """测试搜索事件"""
        # Mock数据
        mock_events = [
            {"id": 1, "event_name": "TestEvent1", "game_gid": 100},
            {"id": 2, "event_name": "TestEvent2", "game_gid": 100},
        ]
        event_service.event_repo.search_events = Mock(return_value=mock_events)

        # 调用方法
        result = event_service.search_events("Test", game_gid=100)

        # 验证结果
        assert len(result) == 2
        event_service.event_repo.search_events.assert_called_once_with("Test", 100)

    def test_get_recent_events(self, event_service):
        """测试获取最近事件"""
        # Mock数据
        mock_events = [
            {"id": 1, "event_name": "RecentEvent1"},
            {"id": 2, "event_name": "RecentEvent2"},
        ]
        event_service.event_repo.get_recent_events = Mock(return_value=mock_events)

        # 调用方法
        result = event_service.get_recent_events(limit=2)

        # 验证结果
        assert len(result) == 2
        event_service.event_repo.get_recent_events.assert_called_once_with(None, 2)

    def test_get_event_statistics(self, event_service):
        """测试获取事件统计"""
        # Mock数据
        mock_stats = {
            "event_id": 1,
            "parameter_count": 5,
            "flow_count": 3
        }
        event_service.event_repo.get_event_statistics = Mock(return_value=mock_stats)

        # 调用方法
        result = event_service.get_event_statistics(1)

        # 验证结果
        assert result is not None
        assert result["parameter_count"] == 5
        assert result["flow_count"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
