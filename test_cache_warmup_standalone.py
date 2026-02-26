#!/usr/bin/env python3
"""测试缓存预热功能"""

import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_cache_warmup():
    """测试缓存预热"""
    logger.info("=== 开始测试缓存预热 ===")

    # 1. 测试导入
    try:
        from backend.services.cache.cache_warmup import CacheWarmer, warmup_cache_on_startup
        logger.info("✅ 导入成功")
    except Exception as e:
        logger.error(f"❌ 导入失败: {e}")
        return False

    # 2. 测试cache实例
    try:
        from backend.core.cache.cache_system import get_cache
        cache = get_cache()
        if cache is None:
            logger.warning("⚠️  get_cache()返回None（预期，因为Flask app未启动）")
        else:
            logger.info("✅ Cache实例获取成功")
    except Exception as e:
        logger.warning(f"⚠️  Cache实例获取异常: {e}")

    # 3. 测试直接使用缓存系统
    try:
        from backend.core.cache.cache_system import hierarchical_cache

        # 设置测试键
        hierarchical_cache.set("test:warmup", {"status": "success"}, ttl=60)
        result = hierarchical_cache.get("test:warmup")
        if result:
            logger.info(f"✅ 缓存读写测试成功: {result}")
        else:
            logger.warning("⚠️  缓存读取返回None")
    except Exception as e:
        logger.error(f"❌ 缓存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 4. 测试CacheWarmer类（不依赖Flask app context）
    try:
        logger.info("=== 测试CacheWarmer ===")

        # 创建一个简单的模拟cache
        class MockCache:
            def __init__(self):
                self.data = {}

            def set(self, key, value, ttl=3600):
                self.data[key] = value
                print(f"  Cache.set('{key}', ttl={ttl})")

            def get(self, key):
                return self.data.get(key)

        mock_cache = MockCache()
        warmer = CacheWarmer(cache=mock_cache)

        logger.info("✅ CacheWarmer初始化成功")

        # 测试预热少量游戏（限制为3个，加快测试）
        stats = warmer.warmup_popular_games(limit=3)

        logger.info(f"✅ 预热完成: {stats}")
        logger.info(f"  缓存键数量: {len(mock_cache.data)}")
        logger.info(f"  缓存键列表: {list(mock_cache.data.keys())}")

        return True

    except Exception as e:
        logger.error(f"❌ CacheWarmer测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cache_warmup()
    sys.exit(0 if success else 1)
