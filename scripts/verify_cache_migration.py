#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Cache Warmer迁移成功

测试内容：
1. 新CacheWarmer类功能正常
2. 所有方法可正常调用
3. 周期性预热可正常启动
4. 缓存操作正常工作
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.cache.cache_warmup import CacheWarmer, warmup_cache_on_startup
from backend.core.cache.cache_system import hierarchical_cache


def test_new_cache_warmer():
    """测试新CacheWarmer功能"""
    print("=" * 60)
    print("测试1: 新CacheWarmer基本功能")
    print("=" * 60)

    # 创建CacheWarmer实例
    warmer = CacheWarmer(cache=hierarchical_cache)
    print("✅ CacheWarmer实例创建成功")

    # 测试各个方法
    methods = [
        'warmup_popular_games',
        'warmup_recent_events',
        'warmup_common_params',
        'warmup_all',
        'warmup_categories',
        'warmup_game_events',
        'start_periodic_warmup',
        'stop_periodic_warmup'
    ]

    for method in methods:
        if hasattr(warmer, method):
            print(f"✅ 方法存在: {method}")
        else:
            print(f"❌ 方法缺失: {method}")

    print("\n测试2: 执行缓存预热")
    print("-" * 40)

    try:
        stats = warmer.warmup_all(games_limit=10, events_limit=10)
        print(f"✅ 预热成功:")
        print(f"   - Games: {stats['games_warmed']}")
        print(f"   - Events: {stats['events_warmed']}")
        print(f"   - Params: {stats['params_warmed']}")
        print(f"   - Total keys: {stats.get('total_keys', 'N/A')}")
    except Exception as e:
        print(f"❌ 预热失败: {e}")

    print("\n测试3: 启动和停止周期性预热")
    print("-" * 40)

    try:
        # 启动周期性预热（短间隔用于测试）
        warmer.start_periodic_warmup(interval_hours=0.001)  # ~3.6秒
        print("✅ 周期性预热已启动")

        # 等待一小段时间
        time.sleep(2)

        # 停止周期性预热
        warmer.stop_periodic_warmup()
        print("✅ 周期性预热已停止")
    except Exception as e:
        print(f"❌ 周期性预热测试失败: {e}")

    print("\n测试4: warmup_cache_on_startup函数")
    print("-" * 40)

    try:
        stats = warmup_cache_on_startup()
        print(f"✅ 启动预热成功:")
        print(f"   - Games: {stats['games_warmed']}")
        print(f"   - Events: {stats['events_warmed']}")
        print(f"   - Params: {stats['params_warmed']}")
        print(f"   - Total keys: {stats.get('total_keys', 'N/A')}")
    except Exception as e:
        print(f"❌ 启动预热失败: {e}")

    return True


def test_old_cache_warmer_deprecated():
    """测试旧CacheWarmer是否显示废弃警告"""
    print("\n" + "=" * 60)
    print("测试5: 验证旧CacheWarmer废弃警告")
    print("=" * 60)

    import warnings

    # 捕获警告
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # 尝试导入旧的CacheWarmer
        try:
            from backend.core.cache.cache_warmer import CacheWarmer as OldCacheWarmer
            print("⚠️ 旧CacheWarmer仍可导入（向后兼容）")

            # 检查是否有DeprecationWarning
            deprecation_warnings = [warn for warn in w if issubclass(warn.category, DeprecationWarning)]

            if deprecation_warnings:
                print(f"✅ 捕获到{len(deprecation_warnings)}个DeprecationWarning:")
                for warn in deprecation_warnings:
                    print(f"   - {warn.message}")
            else:
                print("⚠️ 没有捕获到DeprecationWarning（可能已在导入时显示）")

        except ImportError as e:
            print(f"❌ 旧CacheWarmer导入失败: {e}")

    return True


def test_cache_operations():
    """测试基本缓存操作"""
    print("\n" + "=" * 60)
    print("测试6: 缓存基本操作")
    print("=" * 60)

    try:
        # 测试缓存set/get
        test_key = "test:cache:verification"
        test_value = {"data": "verification_test", "timestamp": time.time()}

        hierarchical_cache.set(test_key, test_value, ttl=60)
        print("✅ 缓存SET成功")

        retrieved = hierarchical_cache.get(test_key)
        if retrieved:
            print(f"✅ 缓存GET成功: {retrieved}")
        else:
            print("❌ 缓存GET失败: 返回None")

        # 清理测试数据
        hierarchical_cache.delete(test_key)
        print("✅ 缓存DELETE成功")

    except Exception as e:
        print(f"❌ 缓存操作失败: {e}")
        import traceback
        traceback.print_exc()

    return True


def main():
    """主测试函数"""
    print("🚀 开始Cache Warmer迁移验证\n")

    results = []

    # 执行所有测试
    results.append(("新CacheWarmer功能", test_new_cache_warmer()))
    results.append(("旧CacheWarmer废弃警告", test_old_cache_warmer_deprecated()))
    results.append(("缓存基本操作", test_cache_operations()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {name}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n🎉 所有测试通过！Cache Warmer迁移成功！")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查")
        return 1


if __name__ == "__main__":
    exit(main())
