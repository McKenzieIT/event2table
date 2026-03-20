#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存统计增强测试
==============

测试命中率统计, 性能指标, 热点键分析等功能

版本: 1.0.0
日期: 2026-02-20
"""

import pytest
import time
from datetime import datetime, timedelta

from backend.core.cache.statistics import cache_statistics
from backend.core.cache.cache_system import hierarchical_cache


class TestCacheStatistics:
    """缓存统计测试"""

    def test_record_access(self):
        """测试记录访问"""
        # 重置统计
        cache_statistics.reset_stats()

        # 记录访问
        cache_statistics.record_access(key="test:key:1", hit=True, level="l1", response_time=0.5)

        cache_statistics.record_access(
            key="test:key:2", hit=False, level="miss", response_time=100.0
        )

        print(f"✅ 访问记录成功")

    def test_get_hit_rate_stats(self):
        """测试获取命中率统计"""
        # 重置统计
        hierarchical_cache.clear_l1()
        hierarchical_cache.reset_stats()

        # 设置一些缓存
        hierarchical_cache.set('test.stats', {'id': 1}, id=1)
        hierarchical_cache.set('test.stats', {'id': 2}, id=2)

        # 访问缓存(命中)
        hierarchical_cache.get('test.stats', id=1)
        hierarchical_cache.get('test.stats', id=2)

        # 访问不存在的缓存(未命中)
        hierarchical_cache.get('test.stats', id=999)

        # 获取命中率统计
        stats = cache_statistics.get_hit_rate_stats()

        print(f"✅ 命中率统计:")
        print(f"   L1命中率: {stats.get('l1_hit_rate', 'N/A')}")
        print(f"   L2命中率: {stats.get('l2_hit_rate', 'N/A')}")
        print(f"   总体命中率: {stats.get('overall_hit_rate', 'N/A')}")
        print(f"   未命中率: {stats.get('miss_rate', 'N/A')}")

        assert 'overall_hit_rate' in stats

    def test_get_performance_stats(self):
        """测试获取性能统计"""
        # 记录一些响应时间
        for i in range(10):
            cache_statistics.record_access(
                key=f"test:perf:{i}", hit=True, level="l1", response_time=0.5 + i * 0.1
            )

        # 获取性能统计
        stats = cache_statistics.get_performance_stats()

        print(f"✅ 性能统计:")
        print(f"   L1平均响应时间: {stats.get('response_times', {}).get('l1_avg_ms', 'N/A')}ms")
        print(f"   L2平均响应时间: {stats.get('response_times', {}).get('l2_avg_ms', 'N/A')}ms")
        print(
            f"   未命中平均响应时间: {stats.get('response_times', {}).get('miss_avg_ms', 'N/A')}ms"
        )

        assert 'response_times' in stats

    def test_get_hot_keys(self):
        """测试获取热点键"""
        # 重置统计
        cache_statistics.reset_stats()

        # 记录访问(模拟热点键)
        for i in range(10):
            cache_statistics.record_access(
                key="test:hot:1", hit=True, level="l1", response_time=0.5
            )

        for i in range(5):
            cache_statistics.record_access(
                key="test:hot:2", hit=True, level="l1", response_time=0.5
            )

        for i in range(3):
            cache_statistics.record_access(
                key="test:hot:3", hit=True, level="l1", response_time=0.5
            )

        # 获取热点键
        hot_keys = cache_statistics.get_hot_keys(limit=10)

        print(f"✅ 热点键:")
        for i, key_info in enumerate(hot_keys, 1):
            print(f"   {i}. {key_info['key']}: {key_info['access_count']}次")

        assert len(hot_keys) > 0
        assert hot_keys[0]['key'] == "test:hot:1"
        assert hot_keys[0]['access_count'] == 10

    def test_record_performance_snapshot(self):
        """测试记录性能快照"""
        # 记录快照
        cache_statistics.record_performance_snapshot()

        print(f"✅ 性能快照已记录")

        # 验证历史记录
        assert len(cache_statistics.performance_history) > 0
        print(f"   历史记录数: {len(cache_statistics.performance_history)}")

    def test_get_performance_trend(self):
        """测试获取性能趋势"""
        # 记录多个快照
        for i in range(5):
            cache_statistics.record_performance_snapshot()
            time.sleep(0.1)

        # 获取性能趋势
        trend = cache_statistics.get_performance_trend(hours=24)

        print(f"✅ 性能趋势:")
        print(f"   时间范围: {trend.get('period_hours', 'N/A')}小时")
        print(f"   快照数量: {trend.get('snapshot_count', 'N/A')}")

        if 'trend' in trend:
            print(f"   时间戳数量: {len(trend['trend'].get('timestamps', []))}")

    def test_get_detailed_stats(self):
        """测试获取详细统计"""
        # 获取详细统计
        stats = cache_statistics.get_detailed_stats()

        print(f"✅ 详细统计:")
        print(f"   时间戳: {stats.get('timestamp', 'N/A')}")
        print(f"   访问键数量: {stats.get('access_key_count', 'N/A')}")
        print(f"   历史记录大小: {stats.get('history_size', 'N/A')}")

        assert 'timestamp' in stats
        assert 'hit_rate_stats' in stats
        assert 'performance_stats' in stats
        assert 'hot_keys' in stats

    def test_reset_stats(self):
        """测试重置统计"""
        # 记录一些数据
        cache_statistics.record_access(key="test:reset:1", hit=True, level="l1", response_time=0.5)

        # 重置统计
        cache_statistics.reset_stats()

        # 验证已重置
        assert len(cache_statistics.access_counts) == 0
        assert len(cache_statistics.performance_history) == 0

        print(f"✅ 统计已重置")

    def test_cleanup_old_records(self):
        """测试清理旧记录"""
        # 记录一些快照
        for i in range(5):
            cache_statistics.record_performance_snapshot()

        # 清理旧记录(保留最近1小时)
        cache_statistics.cleanup_old_records(max_age_hours=1)

        print(f"✅ 旧记录已清理")
        print(f"   剩余历史记录数: {len(cache_statistics.performance_history)}")


class TestStatisticsIntegration:
    """统计集成测试"""

    def test_full_statistics_flow(self):
        """测试完整统计流程"""
        # 重置
        cache_statistics.reset_stats()
        hierarchical_cache.clear_l1()
        hierarchical_cache.reset_stats()

        # 模拟缓存访问
        for i in range(20):
            # 设置缓存
            hierarchical_cache.set('test.flow', {'id': i}, id=i)

            # 访问缓存
            result = hierarchical_cache.get('test.flow', id=i)

            # 记录访问
            cache_statistics.record_access(
                key=f"test:flow:{i}",
                hit=result is not None,
                level="l1" if result is not None else "miss",
                response_time=0.5 if result is not None else 100.0,
            )

        # 记录快照
        cache_statistics.record_performance_snapshot()

        # 获取统计
        detailed_stats = cache_statistics.get_detailed_stats()
        hot_keys = cache_statistics.get_hot_keys(limit=5)
        performance_trend = cache_statistics.get_performance_trend(hours=1)

        print(f"✅ 完整统计流程测试成功")
        print(f"   详细统计: {detailed_stats.get('timestamp', 'N/A')}")
        print(f"   热点键数量: {len(hot_keys)}")
        print(f"   性能趋势快照数: {performance_trend.get('snapshot_count', 0)}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
