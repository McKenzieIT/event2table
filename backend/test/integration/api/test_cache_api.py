#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存API集成测试
================

测试缓存管理相关的REST API端点

版本: 1.0.0
日期: 2026-02-24
"""

import pytest
from flask import Flask
import json


class TestCacheMonitoringAPI:
    """测试监控和告警API"""

    def test_api_get_alerts(self, integration_client):
        """测试获取告警列表API"""
        response = integration_client.get('/api/cache/monitoring/alerts')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'alerts' in data or 'count' in data

    def test_api_get_metrics(self, integration_client):
        """测试获取Prometheus指标API"""
        response = integration_client.get('/api/cache/monitoring/metrics')
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')

    def test_api_get_trends(self, integration_client):
        """测试获取性能趋势API"""
        response = integration_client.get('/api/cache/monitoring/trends')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'trends' in data


class TestCacheCapacityAPI:
    """测试容量监控API"""

    def test_api_get_l1_capacity(self, integration_client):
        """测试获取L1容量API"""
        response = integration_client.get('/api/cache/capacity/l1')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'capacity' in data

    def test_api_get_l2_capacity(self, integration_client):
        """测试获取L2容量API"""
        response = integration_client.get('/api/cache/capacity/l2')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'capacity' in data

    def test_api_get_capacity_prediction(self, integration_client):
        """测试获取容量预测API"""
        response = integration_client.get('/api/cache/capacity/prediction?days=7')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'prediction' in data
        assert data['prediction_days'] == 7


class TestCacheBloomFilterAPI:
    """测试布隆过滤器API"""

    def test_api_get_bloom_filter_stats(self, integration_client):
        """测试获取布隆过滤器统计API"""
        response = integration_client.get('/api/cache/bloom-filter/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'stats' in data

    def test_api_rebuild_bloom_filter(self, integration_client):
        """测试重建布隆过滤器API"""
        response = integration_client.post('/api/cache/bloom-filter/rebuild')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'stats' in data


class TestCacheWarmUpAPI:
    """测试智能预热API"""

    def test_api_predict_hot_keys(self, integration_client):
        """测试预测热点键API"""
        response = integration_client.post(
            '/api/cache/warm-up/predict', json={'limit': 100}, content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'hot_keys' in data
        assert 'count' in data

    def test_api_execute_warm_up(self, integration_client):
        """测试执行预热API"""
        response = integration_client.post(
            '/api/cache/warm-up/execute', json={'top_n': 50}, content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        # API返回result字段而非warmed_keys
        assert 'result' in data or 'count' in data


class TestCacheDegradationAPI:
    """测试降级管理API"""

    def test_api_get_degradation_status(self, integration_client):
        """测试获取降级状态API"""
        response = integration_client.get('/api/cache/degradation/status')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'status' in data

    def test_api_switch_degradation(self, integration_client):
        """测试切换降级模式API"""
        # 测试降级
        response = integration_client.post(
            '/api/cache/degradation/switch',
            json={'degraded': True},
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert data['degraded'] is True

        # 测试恢复
        response = integration_client.post(
            '/api/cache/degradation/switch',
            json={'degraded': False},
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert data['degraded'] is False


class TestCacheStatsAPI:
    """测试缓存统计API(已有端点)"""

    def test_api_get_cache_stats(self, integration_client):
        """测试获取缓存统计API"""
        response = integration_client.get('/api/cache/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'l1_cache' in data
        assert 'l2_cache' in data
        assert 'overall' in data

    def test_api_get_detailed_stats(self, integration_client):
        """测试获取详细统计API"""
        response = integration_client.get('/api/cache/stats/detailed?hours=24')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True


class TestCacheKeysAPI:
    """测试缓存键管理API(已有端点)"""

    def test_api_list_cache_keys(self, integration_client):
        """测试列出缓存键API"""
        response = integration_client.get('/api/cache/keys?limit=10')
        assert response.status_code in [200, 503]  # 503 if Redis not available
        data = response.get_json()
        assert 'success' in data

    def test_api_search_cache_keys(self, integration_client):
        """测试搜索缓存键API"""
        response = integration_client.get('/api/cache/keys/search?query=games&limit=10')
        assert response.status_code in [200, 503]  # 503 if Redis not available
        data = response.get_json()
        assert 'success' in data


class TestCacheClearAPI:
    """测试缓存清理API(已有端点)"""

    def test_api_clear_all_cache(self, integration_client):
        """测试清空所有缓存API"""
        response = integration_client.post('/api/cache/clear')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'details' in data


class TestCacheInvalidateAPI:
    """测试缓存失效API(已有端点)"""

    def test_api_invalidate_game_cache(self, integration_client):
        """测试失效游戏缓存API"""
        # 使用测试GID (90000000+)
        test_gid = 90000001
        response = integration_client.post(f'/api/cache/invalidate/game/{test_gid}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'game_gid' in data
        assert data['game_gid'] == test_gid

    def test_api_invalidate_event_cache(self, integration_client):
        """测试失效事件缓存API"""
        # 使用测试数据
        test_gid = 90000001
        test_event_id = 99999

        response = integration_client.post(
            f'/api/cache/invalidate/event/{test_event_id}',
            json={'game_gid': test_gid},
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'event_id' in data
        assert data['event_id'] == test_event_id


class TestCacheAPIErrorHandling:
    """测试API错误处理"""

    def test_api_predict_hot_keys_missing_body(self, integration_client):
        """测试预测热点键缺少请求体"""
        response = integration_client.post('/api/cache/warm-up/predict')
        assert response.status_code == 200  # 应该使用默认值
        data = response.get_json()
        assert 'success' in data

    def test_api_execute_warm_up_missing_body(self, integration_client):
        """测试执行预热缺少请求体"""
        response = integration_client.post('/api/cache/warm-up/execute')
        assert response.status_code == 200  # 应该使用默认值
        data = response.get_json()
        assert 'success' in data

    def test_api_switch_degradation_missing_body(self, integration_client):
        """测试切换降级缺少请求体"""
        response = integration_client.post('/api/cache/degradation/switch')
        assert response.status_code == 200  # 应该使用默认值 (degraded=False)
        data = response.get_json()
        assert 'success' in data
        assert data['degraded'] is False

    def test_api_search_cache_keys_missing_query(self, integration_client):
        """测试搜索缓存键缺少查询参数"""
        response = integration_client.get('/api/cache/keys/search')
        assert response.status_code == 400  # Bad Request
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is False

    def test_api_invalidate_event_cache_missing_game_gid(self, integration_client):
        """测试失效事件缓存缺少game_gid"""
        test_event_id = 99999
        response = integration_client.post(
            f'/api/cache/invalidate/event/{test_event_id}', json={}, content_type='application/json'
        )
        assert response.status_code == 400  # Bad Request
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
