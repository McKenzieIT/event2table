#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for Games API Routes

Tests the backend/api/routes/games.py endpoints
"""

import pytest


@pytest.mark.integration
@pytest.mark.api
class TestGamesAPIList:
    """测试 GET /api/games 端点"""

    def test_list_games_success(self, client):
        """测试成功获取游戏列表"""
        response = client.get('/api/games')

        assert response.status_code == 200
        data = response.get_json()

        assert 'success' in data
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)

    def test_list_games_includes_statistics(self, client):
        """测试游戏列表包含统计信息"""
        response = client.get('/api/games')

        data = response.get_json()
        games = data['data']

        # 检查第一个游戏是否包含统计字段
        if len(games) > 0:
            game = games[0]
            assert 'event_count' in game
            assert 'param_count' in game
            assert 'event_node_count' in game
            assert 'flow_template_count' in game


@pytest.mark.integration
@pytest.mark.api
class TestGamesAPICreate:
    """测试 POST /api/games 端点"""

    def test_create_game_missing_fields(self, client):
        """测试创建游戏缺少必需字段"""
        response = client.post('/api/games', json={
            'name': 'Test Game'
        })

        assert response.status_code == 400
        data = response.get_json()

        assert 'error' in data

    def test_create_game_invalid_gid(self, client):
        """测试创建游戏时使用无效GID"""
        response = client.post('/api/games', json={
            'gid': -1,
            'name': 'Test Game',
            'ods_db': 'test_db'
        })

        assert response.status_code == 400
        data = response.get_json()

        assert 'error' in data

    def test_create_game_empty_ods_db(self, client):
        """测试创建游戏时ODS数据库名称为空"""
        response = client.post('/api/games', json={
            'gid': 999999,
            'name': 'Test Game',
            'ods_db': ''
        })

        assert response.status_code == 400
        data = response.get_json()

        assert 'error' in data


@pytest.mark.integration
@pytest.mark.api
class TestGamesAPIGet:
    """测试 GET /api/games/<id> 端点"""

    def test_get_game_success(self, client, sample_game):
        """测试成功获取单个游戏"""
        # API使用业务GID而非数据库ID
        response = client.get(f'/api/games/{sample_game["gid"]}')

        assert response.status_code == 200
        data = response.get_json()

        assert data['success'] is True
        assert 'data' in data

    def test_get_game_not_found(self, client):
        """测试获取不存在的游戏"""
        response = client.get('/api/games/999999')

        assert response.status_code == 404
        data = response.get_json()

        assert 'error' in data
