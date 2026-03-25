#!/usr/bin/env python3
"""
Verify cache hit rate for Parameter Repository

This script verifies that the cache is working correctly by:
1. Calling get_paginated_params twice with the same arguments
2. Checking that the database is only called once (cache hit)
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))


def test_cache_hit_rate():
    """Test that cache hit rate is 100% for repeated calls"""
    from backend.core.cache.decorators import _cache
    from backend.models.repositories.parameters import ParameterRepository

    # Clear cache before test
    _cache.clear()

    # Create repository
    repo = ParameterRepository()

    # Mock database
    mock_data = [
        {
            'id': 1,
            'event_id': 100,
            'param_name': 'test_param',
            'param_name_cn': '',
            'param_description': 'Test parameter',
            'game_gid': 90000001,
            'json_path': None,
            'is_active': 1,
            'created_at': None,
            'updated_at': None,
        }
    ]

    with patch('backend.models.repositories.parameters.fetch_all_as_dict') as mock_fetch:
        mock_fetch.return_value = mock_data

        # First call - should be cache miss
        result1 = repo.get_paginated_params(game_gid=90000001, page=1, per_page=10, search=None)

        # Second call - should be cache hit
        result2 = repo.get_paginated_params(game_gid=90000001, page=1, per_page=10, search=None)

        # Verify cache hit
        if mock_fetch.call_count == 1:
            print("✅ 缓存命中成功！只调用了一次数据库")
            print(f"   第一次调用结果: {len(result1)} 条记录")
            print(f"   第二次调用结果: {len(result2)} 条记录")
            print(f"   数据库调用次数: {mock_fetch.call_count}")
            return True
        else:
            print(f"❌ 缓存未命中！数据库调用了 {mock_fetch.call_count} 次")
            return False


if __name__ == '__main__':
    success = test_cache_hit_rate()
    sys.exit(0 if success else 1)
