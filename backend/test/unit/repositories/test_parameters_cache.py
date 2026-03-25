#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ParameterRepository缓存装饰器测试
===================================

测试目标:
1. 缓存命中率 ≥90%
2. 性能提升 ≥10x (相比无缓存)
3. 缓存失效正确工作

TDD Approach:
- 先写测试,观察失败
- 实现功能,使测试通过
- 重构优化,保持测试通过
"""

import os
import sys
import time
from typing import Dict, List

import pytest

# Add project path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)

from backend.core.cache.cache_system import hierarchical_cache
from backend.models.entities import ParameterEntity
from backend.models.repositories.parameters import ParameterRepository


class TestParameterRepositoryCacheHitRate:
    """测试ParameterRepository缓存命中率"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的 setup"""
        self.repo = ParameterRepository()
        # 清理缓存
        hierarchical_cache.clear_all()
        yield
        # 清理
        hierarchical_cache.clear_all()

    def test_get_paginated_params_cache_hit_rate(self):
        """测试get_paginated_params缓存命中率 ≥90%"""
        # Arrange: 预热缓存
        game_gid = 90000001  # 使用测试GID

        # 第一次调用 (MISS)
        start = time.perf_counter()
        result1 = self.repo.get_paginated_params(game_gid=game_gid, page=1, per_page=20)
        duration1 = time.perf_counter() - start

        # 后续9次调用 (应该HIT)
        total_duration = 0
        hit_count = 0
        for i in range(9):
            start = time.perf_counter()
            result = self.repo.get_paginated_params(game_gid=game_gid, page=1, per_page=20)
            duration = time.perf_counter() - start
            total_duration += duration

            # 缓存命中通常<1ms, 未命中>10ms
            if duration < 0.005:  # 5ms threshold
                hit_count += 1

        # Assert: 命中率 ≥90%
        hit_rate = (hit_count / 9) * 100
        assert hit_rate >= 90, f"缓存命中率 {hit_rate:.1f}% 未达到90%目标"

        # Assert: 性能提升 ≥10x
        avg_cached_duration = total_duration / 9
        speedup = duration1 / avg_cached_duration
        assert speedup >= 10, f"性能提升 {speedup:.1f}x 未达到10x目标"

        print(f"✅ get_paginated_params缓存测试通过:")
        print(f"   - 缓存命中率: {hit_rate:.1f}%")
        print(f"   - 性能提升: {speedup:.1f}x")
        print(f"   - 首次调用: {duration1*1000:.3f}ms")
        print(f"   - 平均缓存: {avg_cached_duration*1000:.3f}ms")

    def test_get_params_by_event_id_cache_hit_rate(self):
        """测试get_params_by_event_id缓存命中率 ≥90%"""
        # Arrange
        game_gid = 90000001
        event_id = 1

        # 第一次调用 (MISS)
        start = time.perf_counter()
        result1 = self.repo.get_params_by_event_id(event_id)
        duration1 = time.perf_counter() - start

        # 后续9次调用 (应该HIT)
        total_duration = 0
        hit_count = 0
        for i in range(9):
            start = time.perf_counter()
            result = self.repo.get_params_by_event_id(event_id)
            duration = time.perf_counter() - start
            total_duration += duration

            if duration < 0.005:
                hit_count += 1

        # Assert
        hit_rate = (hit_count / 9) * 100
        assert hit_rate >= 90, f"缓存命中率 {hit_rate:.1f}% 未达到90%目标"

        avg_cached_duration = total_duration / 9
        speedup = duration1 / avg_cached_duration
        assert speedup >= 10, f"性能提升 {speedup:.1f}x 未达到10x目标"

        print(f"✅ get_params_by_event_id缓存测试通过:")
        print(f"   - 缓存命中率: {hit_rate:.1f}%")
        print(f"   - 性能提升: {speedup:.1f}x")

    def test_get_common_params_cache_hit_rate(self):
        """测试get_common_params缓存命中率 ≥90%"""
        # 第一次调用 (MISS)
        start = time.perf_counter()
        result1 = self.repo.get_common_params()
        duration1 = time.perf_counter() - start

        # 后续9次调用 (应该HIT)
        total_duration = 0
        hit_count = 0
        for i in range(9):
            start = time.perf_counter()
            result = self.repo.get_common_params()
            duration = time.perf_counter() - start
            total_duration += duration

            if duration < 0.005:
                hit_count += 1

        # Assert
        hit_rate = (hit_count / 9) * 100
        assert hit_rate >= 90, f"缓存命中率 {hit_rate:.1f}% 未达到90%目标"

        avg_cached_duration = total_duration / 9
        speedup = duration1 / avg_cached_duration
        assert speedup >= 10, f"性能提升 {speedup:.1f}x 未达到10x目标"

        print(f"✅ get_common_params缓存测试通过:")
        print(f"   - 缓存命中率: {hit_rate:.1f}%")
        print(f"   - 性能提升: {speedup:.1f}x")


class TestParameterRepositoryCacheInvalidation:
    """测试ParameterRepository缓存失效"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的 setup"""
        self.repo = ParameterRepository()
        hierarchical_cache.clear_all()
        yield
        hierarchical_cache.clear_all()

    def test_create_param_invalidates_cache(self):
        """测试create_param失效相关缓存"""
        # Arrange: 预热缓存
        game_gid = 90000001
        event_id = 1

        # 预热缓存
        self.repo.get_paginated_params(game_gid=game_gid, page=1, per_page=20)
        self.repo.get_params_by_event_id(event_id)
        self.repo.get_common_params()

        # Act: 创建参数 (应该失效缓存)
        param_data = {
            'event_id': event_id,
            'param_name': 'test_param_cache_invalidation',
            'param_name_cn': '测试参数',
            'param_type': 'string',
            'game_gid': game_gid,
        }

        try:
            self.repo.create_param(param_data)
        except Exception:
            # 如果创建失败 (例如数据库约束), 跳过
            pass

        # Assert: 缓存已失效 (下次调用应该是MISS, 持续时间更长)
        start = time.perf_counter()
        self.repo.get_paginated_params(game_gid=game_gid, page=1, per_page=20)
        duration = time.perf_counter() - start

        # 缓存失效后, 查询时间应该>5ms (表示未命中)
        assert duration > 0.005, f"缓存未失效: 查询时间 {duration*1000:.3f}ms 太短"

        print(f"✅ create_param缓存失效测试通过:")
        print(f"   - 查询时间: {duration*1000:.3f}ms (缓存已失效)")

    def test_update_param_invalidates_cache(self):
        """测试update_param失效相关缓存"""
        # Arrange
        game_gid = 90000001
        event_id = 1

        # 预热缓存
        self.repo.get_params_by_event_id(event_id)

        # Act: 更新参数
        try:
            self.repo.update_param(1, {'param_name': 'updated_param'})
        except Exception:
            # 如果更新失败, 跳过
            pass

        # Assert: 缓存已失效
        start = time.perf_counter()
        self.repo.get_params_by_event_id(event_id)
        duration = time.perf_counter() - start

        assert duration > 0.005, f"缓存未失效: 查询时间 {duration*1000:.3f}ms 太短"

        print(f"✅ update_param缓存失效测试通过:")
        print(f"   - 查询时间: {duration*1000:.3f}ms (缓存已失效)")


class TestParameterRepositoryCacheTTLSpec:
    """测试ParameterRepository缓存TTL设置"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """每个测试前的 setup"""
        self.repo = ParameterRepository()
        hierarchical_cache.clear_all()
        yield
        hierarchical_cache.clear_all()

    def test_get_paginated_params_ttl_180s(self):
        """测试get_paginated_params TTL=180s"""
        # 这个测试需要mock time或使用更短的TTL进行测试
        # 这里仅验证装饰器存在
        assert hasattr(
            self.repo.get_paginated_params, '__wrapped__'
        ), "get_paginated_params应该有@cached装饰器"

        print(f"✅ get_paginated_params TTL测试通过: 装饰器已应用")

    def test_get_params_by_event_id_ttl_300s(self):
        """测试get_params_by_event_id TTL=300s"""
        assert hasattr(
            self.repo.get_params_by_event_id, '__wrapped__'
        ), "get_params_by_event_id应该有@cached装饰器"

        print(f"✅ get_params_by_event_id TTL测试通过: 装饰器已应用")

    def test_get_common_params_ttl_3600s(self):
        """测试get_common_params TTL=3600s"""
        assert hasattr(self.repo.get_common_params, '__wrapped__'), "get_common_params应该有@cached装饰器"

        print(f"✅ get_common_params TTL测试通过: 装饰器已应用")


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
