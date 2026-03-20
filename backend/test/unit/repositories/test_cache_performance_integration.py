#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存系统集成性能测试
===================

测试ParameterRepository、JoinConfigRepository、FlowRepository的缓存性能

目标指标:
- 缓存命中率 ≥90%
- 性能提升 ≥10x
- 缓存失效正确工作
"""

import sys
import os
import time
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from backend.models.repositories.parameters import ParameterRepository
from backend.models.repositories.join_config_repository import JoinConfigRepository
from backend.models.repositories.flow_repository import FlowRepository
from backend.core.cache.cache_system import hierarchical_cache


class TestParameterRepositoryCachePerformance:
    """ParameterRepository缓存性能测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的 setup"""
        self.repo = ParameterRepository()
        hierarchical_cache.clear_all()
        yield
        hierarchical_cache.clear_all()

    def test_get_common_parameters_cache_hit_rate(self):
        """测试get_common_parameters缓存命中率 ≥90%"""
        # 第一次调用 (MISS)
        start = time.perf_counter()
        result1 = self.repo.get_common_parameters(limit=100)
        duration1 = time.perf_counter() - start

        # 后续9次调用 (应该HIT)
        total_duration = 0
        hit_count = 0
        for i in range(9):
            start = time.perf_counter()
            result = self.repo.get_common_parameters(limit=100)
            duration = time.perf_counter() - start
            total_duration += duration

            if duration < 0.005:  # 5ms threshold
                hit_count += 1

        # Assert: 命中率 ≥90%
        hit_rate = (hit_count / 9) * 100
        assert hit_rate >= 90, f"缓存命中率 {hit_rate:.1f}% 未达到90%目标"

        # Assert: 性能提升 ≥10x
        avg_cached_duration = total_duration / 9
        speedup = duration1 / avg_cached_duration if avg_cached_duration > 0 else 0
        assert speedup >= 10, f"性能提升 {speedup:.1f}x 未达到10x目标"

        print(f"✅ ParameterRepository.get_common_parameters缓存测试通过:")
        print(f"   - 缓存命中率: {hit_rate:.1f}%")
        print(f"   - 性能提升: {speedup:.1f}x")
        print(f"   - 首次调用: {duration1*1000:.3f}ms")
        print(f"   - 平均缓存: {avg_cached_duration*1000:.3f}ms")

    def test_create_invalidates_cache(self):
        """测试create失效缓存"""
        # 预热缓存
        self.repo.get_common_parameters(limit=100)

        # 创建参数 (应该失效缓存)
        try:
            param_data = {
                'event_id': 99999,  # 使用不存在的event_id避免污染
                'name': 'test_cache_invalidation',
                'param_type': 'string',
                'game_gid': 90000001,
            }
            self.repo.create(param_data)
        except Exception:
            pass  # 如果创建失败, 忽略

        # 验证缓存已失效
        start = time.perf_counter()
        self.repo.get_common_parameters(limit=100)
        duration = time.perf_counter() - start

        # 缓存失效后, 查询时间应该>5ms
        assert duration > 0.005, f"缓存未失效: 查询时间 {duration*1000:.3f}ms 太短"

        print(f"✅ ParameterRepository.create缓存失效测试通过:")
        print(f"   - 查询时间: {duration*1000:.3f}ms (缓存已失效)")


class TestJoinConfigRepositoryCachePerformance:
    """JoinConfigRepository缓存性能测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的 setup"""
        self.repo = JoinConfigRepository()
        hierarchical_cache.clear_all()
        yield
        hierarchical_cache.clear_all()

    def test_find_all_cache_hit_rate(self):
        """测试find_all缓存命中率 ≥90%"""
        # 第一次调用 (MISS)
        start = time.perf_counter()
        result1 = self.repo.find_all()
        duration1 = time.perf_counter() - start

        # 后续9次调用 (应该HIT)
        total_duration = 0
        hit_count = 0
        for i in range(9):
            start = time.perf_counter()
            result = self.repo.find_all()
            duration = time.perf_counter() - start
            total_duration += duration

            if duration < 0.005:  # 5ms threshold
                hit_count += 1

        # Assert: 命中率 ≥90%
        hit_rate = (hit_count / 9) * 100
        assert hit_rate >= 90, f"缓存命中率 {hit_rate:.1f}% 未达到90%目标"

        # Assert: 性能提升 ≥10x
        avg_cached_duration = total_duration / 9
        speedup = duration1 / avg_cached_duration if avg_cached_duration > 0 else 0
        assert speedup >= 10, f"性能提升 {speedup:.1f}x 未达到10x目标"

        print(f"✅ JoinConfigRepository.find_all缓存测试通过:")
        print(f"   - 缓存命中率: {hit_rate:.1f}%")
        print(f"   - 性能提升: {speedup:.1f}x")

    def test_create_invalidates_cache(self):
        """测试create失效缓存"""
        # 预热缓存
        self.repo.find_all()

        # 创建配置 (应该失效缓存)
        try:
            config_data = {
                'game_gid': 90000001,
                'name': 'test_cache_invalidation',
                'join_type': 'join',
                'source_events': [],
                'join_config': {},
            }
            self.repo.create(config_data)
        except Exception:
            pass  # 如果创建失败, 忽略

        # 验证缓存已失效
        start = time.perf_counter()
        self.repo.find_all()
        duration = time.perf_counter() - start

        assert duration > 0.005, f"缓存未失效: 查询时间 {duration*1000:.3f}ms 太短"

        print(f"✅ JoinConfigRepository.create缓存失效测试通过:")


class TestFlowRepositoryCachePerformance:
    """FlowRepository缓存性能测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的 setup"""
        self.repo = FlowRepository()
        hierarchical_cache.clear_all()
        yield
        hierarchical_cache.clear_all()

    def test_find_all_active_cache_hit_rate(self):
        """测试find_all_active缓存命中率 ≥90%"""
        # 第一次调用 (MISS)
        start = time.perf_counter()
        result1 = self.repo.find_all_active()
        duration1 = time.perf_counter() - start

        # 后续9次调用 (应该HIT)
        total_duration = 0
        hit_count = 0
        for i in range(9):
            start = time.perf_counter()
            result = self.repo.find_all_active()
            duration = time.perf_counter() - start
            total_duration += duration

            if duration < 0.005:  # 5ms threshold
                hit_count += 1

        # Assert: 命中率 ≥90%
        hit_rate = (hit_count / 9) * 100
        assert hit_rate >= 90, f"缓存命中率 {hit_rate:.1f}% 未达到90%目标"

        # Assert: 性能提升 ≥10x
        avg_cached_duration = total_duration / 9
        speedup = duration1 / avg_cached_duration if avg_cached_duration > 0 else 0
        assert speedup >= 10, f"性能提升 {speedup:.1f}x 未达到10x目标"

        print(f"✅ FlowRepository.find_all_active缓存测试通过:")
        print(f"   - 缓存命中率: {hit_rate:.1f}%")
        print(f"   - 性能提升: {speedup:.1f}x")

    def test_create_invalidates_cache(self):
        """测试create失效缓存"""
        # 预热缓存
        self.repo.find_all_active()

        # 创建流程 (应该失效缓存)
        try:
            from backend.models.entities import FlowEntity
            flow = FlowEntity(
                game_gid=90000001,
                flow_name="test_cache_invalidation",
                flow_graph={"nodes": [], "edges": []},
                description="Test cache invalidation",
            )
            self.repo.create(flow)
        except Exception:
            pass  # 如果创建失败, 忽略

        # 验证缓存已失效
        start = time.perf_counter()
        self.repo.find_all_active()
        duration = time.perf_counter() - start

        assert duration > 0.005, f"缓存未失效: 查询时间 {duration*1000:.3f}ms 太短"

        print(f"✅ FlowRepository.create缓存失效测试通过:")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
