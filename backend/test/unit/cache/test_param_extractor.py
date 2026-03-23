#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test cache parameter extractor
"""

import pytest
from backend.core.cache.param_extractor import _extract_cache_params


class TestExtractCacheParams:
    """Test parameter extraction function"""

    def test_skip_self_parameter(self):
        """Test correctly skipping self parameter"""

        class TestRepo:
            def method(self, arg1, arg2):
                return (arg1, arg2)

        repo = TestRepo()
        args, kwargs = _extract_cache_params(repo.method, (repo, 'a', 'b'), {})

        assert args == ('a', 'b'), f"Expected ('a', 'b'), got {args}"
        assert kwargs == {}, f"Expected {{}}, got {kwargs}"

    def test_regular_function_no_self(self):
        """Test regular function does not skip parameters"""

        def standalone_func(arg1, arg2):
            return (arg1, arg2)

        args, kwargs = _extract_cache_params(standalone_func, ('x', 'y'), {})

        assert args == ('x', 'y'), f"Expected ('x', 'y'), got {args}"

    def test_unhashable_dict_serialization(self):
        """Test dict parameter is JSON serialized"""

        def func(data):
            return data

        args, kwargs = _extract_cache_params(func, (), {'data': {'key': 'value'}})

        assert 'data' in kwargs
        assert kwargs['data'] == '{"key": "value"}'  # JSON string

    def test_unhashable_list_serialization(self):
        """Test list parameter is JSON serialized"""

        def func(items):
            return items

        args, kwargs = _extract_cache_params(func, (), {'items': [1, 2, 3]})

        assert 'items' in kwargs
        assert kwargs['items'] == '[1, 2, 3]'  # JSON string

    def test_mixed_params(self):
        """Test mixed parameter types"""

        def func(page, limit, filters):
            return (page, limit, filters)

        args, kwargs = _extract_cache_params(func, (1, 50), {'filters': {'status': 'active'}})

        assert args == (1, 50)
        assert 'filters' in kwargs
        assert isinstance(kwargs['filters'], str)  # JSON string
