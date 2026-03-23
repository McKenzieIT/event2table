#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存性能测试
"""

import time
import sys

sys.path.insert(0, '.')

from unittest.mock import patch
from backend.models.repositories.parameters import ParameterRepository


def benchmark_cache_performance():
    """测试缓存性能提升"""

    repo = ParameterRepository()
    mock_data = [
        {
            'id': i,
            'event_id': 100 + i,
            'param_name': f'param_{i}',
            'game_gid': 90000001,
        }
        for i in range(100)
    ]

    with patch('backend.models.repositories.parameters.fetch_all_as_dict') as mock_fetch:
        mock_fetch.return_value = mock_data

        # 预热缓存
        repo.get_paginated_params(page=1, per_page=50)

        # 测试缓存命中性能
        start = time.time()
        for _ in range(1000):
            repo.get_paginated_params(page=1, per_page=50)
        elapsed = time.time() - start

        print(f"✅ 1000次缓存命中耗时: {elapsed:.3f}秒")
        print(f"   平均响应时间: {elapsed/1000*1000:.2f}毫秒")

        if elapsed < 1.0:
            print("   性能: 优秀 (<1秒)")
        elif elapsed < 5.0:
            print("   性能: 良好 (<5秒)")
        else:
            print("   性能: 需要优化 (>5秒)")


if __name__ == '__main__':
    benchmark_cache_performance()
