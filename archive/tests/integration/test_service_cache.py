#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Service层缓存集成测试
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.services.games.game_service import GameService
from backend.services.events.event_service import EventService


class TestGameServiceCache:
    """GameService缓存测试"""

    @patch('backend.core.cache.cache_system.redis_client')
    @patch('backend.models.repositories.games.GameRepository')
    def test_get_all_games_with_cache(self, mock_repo_class, mock_redis):
        """测试获取所有游戏（带缓存）"""
        # 模拟缓存未命中
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        
        # 模拟数据库返回
        mock_repo = MagicMock()
        mock_repo.find_all.return_value = [
            {'id': 1, 'gid': 1001, 'name': '游戏1', 'ods_db': 'db1'},
            {'id': 2, 'gid': 1002, 'name': '游戏2', 'ods_db': 'db2'}
        ]
        mock_repo_class.return_value = mock_repo
        
        service = GameService()
        games = service.get_all_games()
        
        assert len(games) == 2
        mock_repo.find_all.assert_called_once()
        mock_redis.set.assert_called_once()

    @patch('backend.core.cache.cache_system.redis_client')
    @patch('backend.models.repositories.games.GameRepository')
    def test_get_game_by_gid_with_cache(self, mock_repo_class, mock_redis):
        """测试根据GID获取游戏（带缓存）"""
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        
        mock_repo = MagicMock()
        mock_repo.find_by_gid.return_value = {
            'id': 1, 'gid': 1001, 'name': '游戏1', 'ods_db': 'db1'
        }
        mock_repo_class.return_value = mock_repo
        
        service = GameService()
        game = service.get_game_by_gid(1001)
        
        assert game is not None
        assert game['gid'] == 1001
        mock_repo.find_by_gid.assert_called_once_with(1001)

    @patch('backend.core.cache.cache_system.redis_client')
    @patch('backend.models.repositories.games.GameRepository')
    def test_create_game_invalidates_cache(self, mock_repo_class, mock_redis):
        """测试创建游戏失效缓存"""
        mock_redis.delete.return_value = 1
        mock_redis.scan_iter.return_value = ['cache:games.list']
        
        mock_repo = MagicMock()
        mock_repo.find_by_gid.return_value = None  # 不存在
        mock_repo.create.return_value = {'id': 1, 'gid': 1001}
        mock_repo.find_by_id.return_value = {
            'id': 1, 'gid': 1001, 'name': '测试游戏', 'ods_db': 'test_db'
        }
        mock_repo_class.return_value = mock_repo
        
        service = GameService()
        game = service.create_game({
            'gid': 1001,
            'name': '测试游戏',
            'ods_db': 'test_db'
        })
        
        assert game['gid'] == 1001
        # 应该失效 games.list
        mock_redis.delete.assert_called()

    @patch('backend.core.cache.cache_system.redis_client')
    @patch('backend.models.repositories.games.GameRepository')
    def test_update_game_invalidates_cache(self, mock_repo_class, mock_redis):
        """测试更新游戏失效缓存"""
        mock_redis.delete.return_value = 1
        mock_redis.scan_iter.return_value = ['cache:games.detail:1001']
        
        mock_repo = MagicMock()
        mock_repo.find_by_gid.return_value = {
            'id': 1, 'gid': 1001, 'name': '旧名称', 'ods_db': 'db1'
        }
        mock_repo_class.return_value = mock_repo
        
        service = GameService()
        game = service.update_game(1001, {'name': '新名称'})
        
        assert game['name'] == '新名称'
        # 应该失效 games.detail:{gid}
        mock_redis.scan_iter.assert_called()

    @patch('backend.core.cache.cache_system.redis_client')
    @patch('backend.models.repositories.games.GameRepository')
    def test_delete_game_invalidates_cache(self, mock_repo_class, mock_redis):
        """测试删除游戏失效缓存"""
        mock_redis.delete.return_value = 1
        mock_redis.scan_iter.return_value = ['cache:games.detail:1001', 'cache:games.list']
        
        mock_repo = MagicMock()
        mock_repo.find_by_gid.return_value = {
            'id': 1, 'gid': 1001, 'name': '游戏1', 'ods_db': 'db1'
        }
        mock_repo_class.return_value = mock_repo
        
        service = GameService()
        result = service.delete_game(1001)
        
        assert result is True
        mock_repo.delete.assert_called_once_with(1001)
        # 应该失效相关缓存
        mock_redis.scan_iter.assert_called()


class TestEventServiceCache:
    """EventService缓存测试"""

    @patch('backend.core.cache.cache_system.redis_client')
    @patch('backend.models.repositories.events.EventRepository')
    @patch('backend.models.repositories.games.GameRepository')
    def test_get_events_by_game_with_cache(self, mock_game_repo, mock_event_repo, mock_redis):
        """测试获取游戏事件列表（带缓存）"""
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        
        mock_game = MagicMock()
        mock_game.find_by_gid.return_value = {'id': 1, 'gid': 1001}
        mock_game_repo.return_value = mock_game
        
        mock_event = MagicMock()
        mock_event.find_by_game_gid.return_value = [
            {'id': 1, 'event_name': '事件1', 'game_gid': 1001}
        ]
        mock_event.count_by_game_gid.return_value = 1
        mock_event_repo.return_value = mock_event
        
        service = EventService()
        result = service.get_events_by_game(1001)
        
        assert result['total'] == 1
        assert len(result['events']) == 1

    @patch('backend.core.cache.cache_system.redis_client')
    @patch('backend.models.repositories.events.EventRepository')
    @patch('backend.models.repositories.games.GameRepository')
    def test_create_event_invalidates_cache(self, mock_game_repo, mock_event_repo, mock_redis):
        """测试创建事件失效缓存"""
        mock_redis.delete.return_value = 1
        mock_redis.scan_iter.return_value = ['cache:events.list:1001:1:20']
        
        mock_game = MagicMock()
        mock_game.find_by_gid.return_value = {'id': 1, 'gid': 1001}
        mock_game_repo.return_value = mock_game
        
        mock_event = MagicMock()
        mock_event.find_by_name.return_value = None
        mock_event.create.return_value = {'id': 1}
        mock_event.find_by_id.return_value = {
            'id': 1, 'event_name': '登录事件', 'game_gid': 1001
        }
        mock_event_repo.return_value = mock_event
        
        service = EventService()
        event = service.create_event({
            'game_gid': 1001,
            'event_name': '登录事件',
            'category': 'user'
        })
        
        assert event['event_name'] == '登录事件'
        # 应该失效 events.list:* 模式
        mock_redis.scan_iter.assert_called()

    @patch('backend.core.cache.cache_system.redis_client')
    @patch('backend.models.repositories.events.EventRepository')
    def test_update_event_invalidates_cache(self, mock_event_repo, mock_redis):
        """测试更新事件失效缓存"""
        mock_redis.delete.return_value = 1
        mock_redis.scan_iter.return_value = [
            'cache:events.detail:1',
            'cache:events.with_params:1',
            'cache:events.list:1001:1:20'
        ]
        
        mock_event = MagicMock()
        mock_event.find_by_id.return_value = {
            'id': 1, 'event_name': '旧名称', 'game_gid': 1001
        }
        mock_event_repo.return_value = mock_event
        
        service = EventService()
        event = service.update_event(1, {'event_name': '新名称'})
        
        assert event['event_name'] == '新名称'
        # 应该失效相关缓存
        assert mock_redis.scan_iter.call_count == 2
