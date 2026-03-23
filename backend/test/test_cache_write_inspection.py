#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspect cache writes
"""

import sys

sys.path.insert(0, '.')

from unittest.mock import patch
from backend.models.repositories.parameters import ParameterRepository

# Track cache operations
cache_ops = []

original_get = None
original_set = None


def mock_get(key):
    result = original_get(key)
    cache_ops.append(('GET', key, result is not None))
    print(f"   Cache GET: {key[:80]}... → {'HIT' if result else 'MISS'}")
    return result


def mock_set(key, value, **kwargs):
    cache_ops.append(('SET', key, value))
    print(f"   Cache SET: {key[:80]}... → {type(value).__name__}")
    return original_set(key, value, **kwargs)


# Monkey-patch cache
from backend.core.cache import decorators

original_get = decorators._cache.get
original_set = decorators._cache.set
decorators._cache.get = mock_get
decorators._cache.set = mock_set

# Create repo
repo = ParameterRepository()

# Mock data
mock_param_data = [
    {
        'id': 1,
        'event_id': 100,
        'param_name': 'test_param',
        'game_gid': 90000001,
    }
]

print("=" * 60)
print("Cache Write Inspection")
print("=" * 60)

with patch('backend.models.repositories.parameters.fetch_all_as_dict') as mock_fetch:
    mock_fetch.return_value = mock_param_data

    print("\n1. First call (should SET cache):")
    result1 = repo.get_paginated_params(page=1, per_page=50)

    print("\n2. Second call (should GET cache):")
    result2 = repo.get_paginated_params(page=1, per_page=50)

    print(f"\n3. Cache operations: {len(cache_ops)}")
    get_ops = [op for op in cache_ops if op[0] == 'GET']
    set_ops = [op for op in cache_ops if op[0] == 'SET']
    print(f"   GET ops: {len(get_ops)}")
    print(f"   SET ops: {len(set_ops)}")

    print(f"\n4. GET results:")
    for i, (op, key, hit) in enumerate(get_ops, 1):
        if 'get_paginated_params' in key:
            print(f"   {i}. {'HIT' if hit else 'MISS'}")

print("\n" + "=" * 60)
