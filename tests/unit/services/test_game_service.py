#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameService 单元测试
测试缓存集成功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.services.games.game_service import GameService


class TestGameServiceCache:
    """GameService缓存功能测试"""

    @pytest.fixture
    def game_service(self):
        """创建GameService实例"""
        with patch('backend.services.games.game_service.GameRepository'):
            return GameService()

    def test_get_all_games_with_cache(self, game_service):
        """测试获取所有游戏（带缓存）"""
        # Mock数据
        mock_games = [
            {"id": 1, "gid": 100, "name": "Game1", "ods_db": "db1"},
            {"id": 2, "gid": 101, "name": "Game2", "ods_db": "db2"},
        ]
        game_service.game_repo.find_all = Mock(return_value=mock_games)
        game_service._get_event_count = Mock(return_value=0)
        game_service._get_flow_count = Mock(return_value=0)

        # 第一次调用
        result1 = game_service.get_all_games(include_stats=True)
        
        # 验证结果
        assert len(result1) == 2
        assert result1[0]["name"] == "Game1"
        assert result1[0]["event_count"] == 0

    def test_get_game_by_gid_with_cache(self, game_service):
        """测试根据GID获取游戏（带缓存）"""
        # Mock数据
        mock_game = {"id": 1, "gid": 100, "name": "TestGame", "ods_db": "test_db"}
        game_service.game_repo.find_by_gid = Mock(return_value=mock_game)

        # 调用方法
        result = game_service.get_game_by_gid(100)

        # 验证结果
        assert result is not None
        assert result["gid"] == 100
        assert result["name"] == "TestGame"
        game_service.game_repo.find_by_gid.assert_called_once_with(100)

    def test_create_game_invalidates_cache(self, game_service):
        """测试创建游戏时失效缓存"""
        # Mock数据
        game_data = {"gid": 100, "name": "NewGame", "ods_db": "new_db"}
        game_service.game_repo.find_by_gid = Mock(return_value=None)
        game_service.game_repo.create = Mock(return_value={"id": 1})
        game_service.game_repo.find_by_id = Mock(return_value={
            "id": 1, "gid": 100, "name": "NewGame", "ods_db": "new_db"
        })

        with patch('backend.services.games.game_service.CacheInvalidator') as mock_cache:
            # 调用方法
            result = game_service.create_game(game_data)

            # 验证缓存失效被调用
            mock_cache.invalidate_key.assert_called_once_with('games.list')
            assert result["gid"] == 100

    def test_create_game_duplicate_gid(self, game_service):
        """测试创建游戏时GID重复"""
        # Mock数据
        game_data = {"gid": 100, "name": "NewGame", "ods_db": "new_db"}
        game_service.game_repo.find_by_gid = Mock(return_value={
            "id": 1, "gid": 100, "name": "ExistingGame", "ods_db": "existing_db"
        })

        # 验证抛出异常
        with pytest.raises(ValueError, match="already exists"):
            game_service.create_game(game_data)

    def test_update_game_invalidates_cache(self, game_service):
        """测试更新游戏时失效缓存"""
        # Mock数据
        updates = {"name": "UpdatedGame"}
        game_service.game_repo.find_by_gid = Mock(return_value={
            "id": 1, "gid": 100, "name": "OldGame", "ods_db": "test_db"
        })
        game_service.game_repo.update = Mock(return_value=True)
        game_service.game_repo.find_by_gid = Mock(return_value={
            "id": 1, "gid": 100, "name": "UpdatedGame", "ods_db": "test_db"
        })

        with patch('backend.services.games.game_service.CacheInvalidator') as mock_cache:
            # 调用方法
            result = game_service.update_game(100, updates)

            # 验证缓存失效被调用
            mock_cache.invalidate_game.assert_called_once_with(100)

    def test_update_game_not_found(self, game_service):
        """测试更新不存在的游戏"""
        # Mock数据
        updates = {"name": "UpdatedGame"}
        game_service.game_repo.find_by_gid = Mock(return_value=None)

        # 验证抛出异常
        with pytest.raises(ValueError, match="not found"):
            game_service.update_game(999, updates)

    def test_delete_game_invalidates_cache(self, game_service):
        """测试删除游戏时失效缓存"""
        # Mock数据
        game_service.game_repo.find_by_gid = Mock(return_value={
            "id": 1, "gid": 100, "name": "TestGame", "ods_db": "test_db"
        })
        game_service._get_event_count = Mock(return_value=0)
        game_service.game_repo.delete = Mock(return_value=True)

        with patch('backend.services.games.game_service.CacheInvalidator') as mock_cache:
            # 调用方法
            result = game_service.delete_game(100)

            # 验证缓存失效被调用
            mock_cache.invalidate_game.assert_called_once_with(100)
            assert result is True

    def test_delete_game_with_events(self, game_service):
        """测试删除有事件的游戏"""
        # Mock数据
        game_service.game_repo.find_by_gid = Mock(return_value={
            "id": 1, "gid": 100, "name": "TestGame", "ods_db": "test_db"
        })
        game_service._get_event_count = Mock(return_value=5)

        # 验证抛出异常
        with pytest.raises(ValueError, match="Cannot delete game with 5 events"):
            game_service.delete_game(100)

    def test_get_games_with_stats(self, game_service):
        """测试获取游戏统计信息"""
        # Mock数据
        mock_games_with_stats = [
            {"id": 1, "gid": 100, "name": "Game1", "event_count": 10, "flow_count": 5},
            {"id": 2, "gid": 101, "name": "Game2", "event_count": 20, "flow_count": 8},
        ]
        game_service.game_repo.get_all_with_stats = Mock(return_value=mock_games_with_stats)

        # 调用方法
        result = game_service.get_games_with_stats()

        # 验证结果
        assert len(result) == 2
        assert result[0]["event_count"] == 10
        assert result[1]["flow_count"] == 8

    def test_search_games(self, game_service):
        """测试搜索游戏"""
        # Mock数据
        mock_games = [
            {"id": 1, "gid": 100, "name": "TestGame1", "ods_db": "db1"},
            {"id": 2, "gid": 101, "name": "TestGame2", "ods_db": "db2"},
        ]
        game_service.game_repo.search_by_name = Mock(return_value=mock_games)

        # 调用方法
        result = game_service.search_games("Test")

        # 验证结果
        assert len(result) == 2
        game_service.game_repo.search_by_name.assert_called_once_with("%Test%")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
