"""
测试所有新模块可以正确导入

这是第一个测试，验证模块导入是否正常 (TDD Red阶段)
预期: 所有测试失败，因为导入路径错误
"""


def test_bloom_filter_enhanced_import():
    """测试布隆过滤器模块导入"""
    from core.cache.bloom_filter_enhanced import EnhancedBloomFilter
    from core.cache.bloom_filter_enhanced import get_enhanced_bloom_filter
    assert EnhancedBloomFilter is not None
    assert get_enhanced_bloom_filter is not None


def test_monitoring_import():
    """测试监控告警模块导入"""
    from core.cache.monitoring import CacheAlertManager
    from core.cache.monitoring import cache_alert_manager
    assert CacheAlertManager is not None
    assert cache_alert_manager is not None


def test_capacity_monitor_import():
    """测试容量监控模块导入"""
    from core.cache.capacity_monitor import CacheCapacityMonitor
    from core.cache.capacity_monitor import get_capacity_monitor
    from core.cache.capacity_monitor import init_capacity_monitor
    assert CacheCapacityMonitor is not None
    assert get_capacity_monitor is not None
    assert init_capacity_monitor is not None
    # cache_capacity_monitor 可能是 None (需要初始化)


def test_consistency_import():
    """测试读写锁模块导入"""
    from core.cache.consistency import CacheReadWriteLock
    from core.cache.consistency import cache_rw_lock
    assert CacheReadWriteLock is not None
    assert cache_rw_lock is not None


def test_degradation_import():
    """测试降级策略模块导入"""
    from core.cache.degradation import CacheDegradationManager
    from core.cache.degradation import cache_degradation_manager
    assert CacheDegradationManager is not None
    assert cache_degradation_manager is not None


def test_intelligent_warmer_import():
    """测试智能预热模块导入"""
    from core.cache.intelligent_warmer import IntelligentCacheWarmer
    from core.cache.intelligent_warmer import intelligent_cache_warmer
    assert IntelligentCacheWarmer is not None
    assert intelligent_cache_warmer is not None
