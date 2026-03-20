#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存API单元测试
================

测试缓存管理API端点的基本功能

版本: 1.0.0
日期: 2026-02-24
更新: 2026-02-28 (使用integration_client)
"""

import pytest

# 注意: 此测试使用integration_client fixture, 由conftest.py提供
# cache API已通过api_bp注册到web_app


class TestCacheMonitoringAPI:
    """测试监控和告警API"""

    def test_api_get_alerts(self, client):
        """测试获取告警列表API"""
        response = client.get('/api/cache/monitoring/alerts')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True

    def test_api_get_metrics(self, client):
        """测试获取Prometheus指标API"""
        response = client.get('/api/cache/monitoring/metrics')
        assert response.status_code == 200
        # Prometheus endpoint returns text/plain
        assert response.content_type.startswith('text/plain')

    def test_api_get_trends(self, client):
        """测试获取性能趋势API"""
        response = client.get('/api/cache/monitoring/trends')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True


class TestCacheCapacityAPI:
    """测试容量监控API"""

    def test_api_get_l1_capacity(self, client):
        """测试获取L1容量API"""
        response = client.get('/api/cache/capacity/l1')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'capacity' in data

    def test_api_get_l2_capacity(self, client):
        """测试获取L2容量API"""
        response = client.get('/api/cache/capacity/l2')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'capacity' in data

    def test_api_get_capacity_prediction(self, client):
        """测试获取容量预测API"""
        response = client.get('/api/cache/capacity/prediction?days=7')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'prediction' in data
        assert data['prediction_days'] == 7


class TestCacheBloomFilterAPI:
    """测试布隆过滤器API"""

    def test_api_get_bloom_filter_stats(self, client):
        """测试获取布隆过滤器统计API"""
        response = client.get('/api/cache/bloom-filter/stats')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True
        assert 'stats' in data

    def test_api_rebuild_bloom_filter(self, client):
        """测试重建布隆过滤器API"""
        response = client.post('/api/cache/bloom-filter/rebuild')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True


class TestCacheWarmUpAPI:
    """测试智能预热API"""

    def test_api_predict_hot_keys(self, client):
        """测试预测热点键API"""
        response = client.post(
            '/api/cache/warm-up/predict',
            json={'minutes': 5, 'top_n': 100, 'use_decay': True},
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True

    def test_api_execute_warm_up(self, client):
        """测试执行预热API"""
        response = client.post(
            '/api/cache/warm-up/execute',
            json={'keys': ['test_key_1', 'test_key_2']},
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True


class TestCacheDegradationAPI:
    """测试降级管理API"""

    def test_api_get_degradation_status(self, client):
        """测试获取降级状态API"""
        response = client.get('/api/cache/degradation/status')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True

    def test_api_switch_degradation(self, client):
        """测试切换降级模式API"""
        # 测试降级
        response = client.post(
            '/api/cache/degradation/switch',
            json={'degraded': True},
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert data['success'] is True

        # 测试恢复
        response = client.post(
            '/api/cache/degradation/switch',
            json={'degraded': False},
            content_type='application/json',
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data


class TestCacheAPIErrorHandling:
    """测试API错误处理"""

    def test_api_predict_hot_keys_missing_body(self, client):
        """测试预测热点键缺少请求体"""
        response = client.post('/api/cache/warm-up/predict')
        assert response.status_code == 200  # Should use default value
        data = response.get_json()
        assert 'success' in data

    def test_api_execute_warm_up_missing_body(self, client):
        """测试执行预热缺少请求体"""
        response = client.post('/api/cache/warm-up/execute')
        assert response.status_code == 200  # Should use default value
        data = response.get_json()
        assert 'success' in data

    def test_api_switch_degradation_missing_body(self, client):
        """测试切换降级缺少请求体"""
        response = client.post('/api/cache/degradation/switch')
        assert response.status_code == 200  # Should use default value
        data = response.get_json()
        assert 'success' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
