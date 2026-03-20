#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试缓存预热功能
验证表名修复和app_context修复是否有效
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.core.database import get_db_connection
from backend.core.utils import fetch_all_as_dict

# 使用新CacheWarmer (2026-02-26迁移)
from backend.services.cache.cache_warmup import CacheWarmer
from backend.core.cache.cache_hierarchical import hierarchical_cache


def test_cache_warming():
    """测试缓存预热功能"""

    print("=" * 60)
    print("测试缓存预热功能")
    print("=" * 60)

    # 测试1: 检查event_categories表是否存在
    print("\n📝 测试1: 检查event_categories表...")
    try:
        categories = fetch_all_as_dict('SELECT * FROM event_categories ORDER BY id LIMIT 5')
        print(f"✅ event_categories表存在, 找到 {len(categories)} 个分类")
        for cat in categories[:3]:
            print(f"   - {cat.get('name', 'N/A')} (ID: {cat.get('id', 'N/A')})")
    except Exception as e:
        print(f"❌ event_categories表查询失败: {e}")
        return False

    # 测试2: 测试预热功能
    print("\n🔥 测试2: 执行缓存预热...")
    try:
        # 使用新CacheWarmer API (2026-02-26)
        warmer = CacheWarmer(cache=hierarchical_cache)
        warmer.warmup_all(games_limit=100, events_limit=50)

        # 检查预热统计 - 使用新stats字段名
        stats = warmer.stats
        print(f"✅ 缓存预热完成:")
        print(f"   - 游戏: {stats['games_warmed']}个")
        print(f"   - 事件: {stats['events_warmed']}个")
        print(f"   - 参数: {stats['params_warmed']}个")
        print(f"   - 总计: {stats['total_keys']}个")

        # 验证缓存中的数据
        print("\n📊 测试3: 验证缓存数据...")
        cache_stats = hierarchical_cache.get_stats()
        print(f"✅ 缓存统计:")
        print(f"   - L1命中: {cache_stats.get('l1_hits', 0)}次")
        print(f"   - L2命中: {cache_stats.get('l2_hits', 0)}次")
        print(f"   - 未命中: {cache_stats.get('misses', 0)}次")
        print(f"   - 命中率: {cache_stats.get('hit_rate', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ 缓存预热失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_cache_warming()
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过！缓存预热功能正常")
    else:
        print("❌ 测试失败！请检查错误信息")
    print("=" * 60)
    sys.exit(0 if success else 1)
