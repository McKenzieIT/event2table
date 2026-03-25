#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inspect cache keys directly
"""

import sys

sys.path.insert(0, '.')

from unittest.mock import patch

from backend.models.repositories.parameters import ParameterRepository

# Patch cache.get to see what keys are requested
original_get = None
cache_keys_seen = []


def mock_get(key):
    cache_keys_seen.append(key)
    print(f"   Cache GET: {key}")
    return original_get(key)


# Monkey-patch cache
from backend.core.cache import decorators

original_get = decorators._cache.get
decorators._cache.get = mock_get

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
print("Cache Key Inspection")
print("=" * 60)

with patch('backend.models.repositories.parameters.fetch_all_as_dict') as mock_fetch:
    mock_fetch.return_value = mock_param_data

    print("\n1. First call:")
    result1 = repo.get_paginated_params(page=1, per_page=50)

    print("\n2. Second call:")
    result2 = repo.get_paginated_params(page=1, per_page=50)

    print(f"\n3. Cache keys seen: {len(cache_keys_seen)}")
    for i, key in enumerate(cache_keys_seen, 1):
        print(f"   {i}. {key}")

    print(f"\n4. Unique keys: {len(set(cache_keys_seen))}")

print("\n" + "=" * 60)
