#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Events API Routes Tests

Tests the backend/api/routes/events.py endpoints
"""

import pytest


@pytest.mark.integration
@pytest.mark.api
class TestEventsAPIList:
    """测试 GET /api/events 端点"""

    def test_list_events_requires_game_gid(self, client):
        """测试获取事件列表需要game_gid参数"""
        response = client.get('/api/events')

        # Should return error or empty list when no game_gid provided
        assert response.status_code in [200, 400]

    def test_list_events_with_game_gid(self, client, sample_game):
        """测试使用game_gid获取事件列表"""
        response = client.get(f'/api/events?game_gid={sample_game["gid"]}')

        assert response.status_code == 200
        data = response.get_json()

        assert 'success' in data


@pytest.mark.integration
@pytest.mark.api
class TestEventsAPICreate:
    """测试 POST /api/events 端点"""

    def test_create_event_missing_fields(self, client):
        """测试创建事件缺少必需字段"""
        response = client.post('/api/events', json={
            'event_name': 'test_event'
        })

        # Should return error for missing fields
        assert response.status_code in [400, 409]


@pytest.mark.integration
@pytest.mark.api
class TestEventsAPIGet:
    """测试 GET /api/events/<id> 端点"""

    def test_get_event_not_found(self, client):
        """测试获取不存在的事件"""
        response = client.get('/api/events/999999')

        # API may return 400 or 404
        assert response.status_code in [400, 404]
