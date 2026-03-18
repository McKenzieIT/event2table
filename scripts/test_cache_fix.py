#!/usr/bin/env python3
"""
测试缓存系统修复效果
"""
import sys
import time

# 添加backend路径
sys.path.insert(0, '/Users/mckenzie/Documents/event2table')

def test_cached_decorator_fix():
    """测试@cached装饰器修复"""
    try:
        from backend.core.cache.cache_system import HierarchicalCache, cached

        # 创建缓存实例
        cache = HierarchicalCache()

        # 测试装饰器
        @cached('test.key', timeout=60)
        def get_data(value: str):
            return f"Processed: {value}"

        # 第一次调用（缓存未命中）
        start = time.time()
        result1 = get_data(value="test123")
        time1 = time.time() - start

        # 第二次调用（应该缓存命中）
        start = time.time()
        result2 = get_data(value="test123")
        time2 = time.time() - start

        print(f"✅ @cached装饰器修复成功")
        print(f"  第一次调用: {result1} ({time1*1000:.2f}ms)")
        print(f"  第二次调用: {result2} ({time2*1000:.2f}ms)")

        # 验证结果一致
        assert result1 == result2, "缓存结果不一致"

        return True

    except Exception as e:
        print(f"❌ 缓存装饰器测试失败: {e}")
        return False

if __name__ == '__main__':
    success = test_cached_decorator_fix()
    if success:
        print("\n🎉 缓存系统修复验证通过！")
        sys.exit(0)
    else:
        print("\n⚠️ 缓存系统修复需要进一步调试")
        sys.exit(1)
