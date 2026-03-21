#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache debug test with mock
"""

import sys
sys.path.insert(0, '.')

from unittest.mock import patch, MagicMock
from backend.models.repositories.parameters import ParameterRepository
from backend.core.cache.cache_system import cache_result

# Create repo
repo = ParameterRepository()

# Mock data
mock_param_data = {
    'id': 1,
    'event_id': 100,
    'param_name': 'test_param',
    'param_name_cn': '',
    'param_description': 'Test parameter',
    'game_gid': 90000001,
    'json_path': None,
    'is_active': 1,
    'created_at': None,
    'updated_at': None
}

print("=" * 60)
print("Cache Debug Test with Mock")
print("=" * 60)

# Patch fetch_all_as_dict
with patch('backend.models.repositories.parameters.fetch_all_as_dict') as mock_fetch:
    mock_fetch.return_value = [mock_param_data]

    print("\n1. First call (should be cache miss):")
    print(f"   Mock call count BEFORE: {mock_fetch.call_count}")
    result1 = repo.get_paginated_params(page=1, per_page=50)
    print(f"   Mock call count AFTER: {mock_fetch.call_count}")
    print(f"   Result keys: {result1.keys()}")

    print("\n2. Second call (should be cache hit):")
    print(f"   Mock call count BEFORE: {mock_fetch.call_count}")
    result2 = repo.get_paginated_params(page=1, per_page=50)
    print(f"   Mock call count AFTER: {mock_fetch.call_count}")
    print(f"   Result keys: {result2.keys()}")

    print("\n3. Analysis:")
    print(f"   Total mock calls: {mock_fetch.call_count}")
    print(f"   Expected: 1 (cache hit on second call)")
    print(f"   Actual: {mock_fetch.call_count}")

    if mock_fetch.call_count == 1:
        print("   ✅ Cache working correctly!")
    else:
        print("   ❌ Cache NOT working - called {} times".format(mock_fetch.call_count))
        print("\n   Possible reasons:")
        print("   - Cache key mismatch")
        print("   - Mock interfering with cache")
        print("   - Cache not initialized")

print("\n" + "=" * 60)
