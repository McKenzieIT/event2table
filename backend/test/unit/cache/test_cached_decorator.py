#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@cached装饰器集成测试
"""

import pytest
from unittest.mock import patch, MagicMock
from backend.core.cache.decorators import cached


class TestCachedDecorator:
    """测试@cached装饰器"""

    def test_cache_hit_with_self_parameter(self):
        """测试带self参数的缓存命中"""

        class TestRepo:
            def __init__(self):
                self.call_count = 0

            @cached(ttl=60)
            def get_data(self, page=1):
                self.call_count += 1
                return {'page': page, 'data': 'value'}

        repo = TestRepo()

        with patch('backend.core.cache.decorators._cache') as mock_cache:
            # 第一次调用（cache miss）
            mock_cache.get.return_value = None
            result1 = repo.get_data(page=1)
            assert repo.call_count == 1
            assert result1 == {'page': 1, 'data': 'value'}

            # 第二次调用（cache hit）
            mock_cache.get.return_value = result1
            result2 = repo.get_data(page=1)
            assert repo.call_count == 1  # 没有再次调用函数
            assert result2 == result1

    def test_cache_miss_different_parameters(self):
        """测试不同参数导致cache miss"""

        class TestRepo:
            def __init__(self):
                self.call_count = 0

            @cached(ttl=60)
            def get_data(self, page=1):
                self.call_count += 1
                return {'page': page}

        repo = TestRepo()

        with patch('backend.core.cache.decorators._cache') as mock_cache:
            mock_cache.get.return_value = None

            # 第一次调用 page=1
            repo.get_data(page=1)
            assert repo.call_count == 1

            # 第二次调用 page=2（应该cache miss）
            repo.get_data(page=2)
            assert repo.call_count == 2

    def test_fallback_on_error(self):
        """测试错误时fallback到旧方式"""

        @cached(ttl=60)
        def problematic_func(data):
            return {'data': 'value'}

        class UnhandledObject:
            pass

        with patch('backend.core.cache.decorators._cache') as mock_cache:
            mock_cache.get.return_value = None
            mock_cache.set.return_value = None

            # 应该fallback而不是抛出异常
            result = problematic_func(UnhandledObject())
            assert result == {'data': 'value'}

            # 验证缓存操作被调用（新方式尝试缓存）
            assert mock_cache.get.call_count >= 1
            assert mock_cache.set.call_count >= 1
