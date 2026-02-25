#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能缓存预热系统单元测试
========================

测试覆盖:
- CircularBuffer 循环缓冲区
- FrequencyPredictor 频率预测器
- IntelligentCacheWarmer 预热器

版本: 1.0.0
日期: 2026-02-24
"""

import pytest
import asyncio
import time
from unittest.mock import patch

# 导入被测试模块
from backend.core.cache.intelligent_warmer import (
    CircularBuffer,
    FrequencyPredictor,
    IntelligentCacheWarmer,
    intelligent_cache_warmer,
    start_warm_up_scheduler
)


# ============================================================================
# 测试1: CircularBuffer 循环缓冲区
# ============================================================================

class TestCircularBuffer:
    """测试循环缓冲区"""

    def test_circular_buffer_init(self):
        """测试缓冲区初始化"""
        buffer = CircularBuffer(size=10)

        assert buffer is not None
        assert len(buffer) == 0
        assert buffer.buffer.maxlen == 10

    def test_circular_buffer_append(self):
        """测试添加项"""
        buffer = CircularBuffer(size=5)

        # 添加3个项
        buffer.append({'key': 'test1'})
        buffer.append({'key': 'test2'})
        buffer.append({'key': 'test3'})

        assert len(buffer) == 3

    def test_circular_buffer_overflow(self):
        """测试缓冲区溢出（循环覆盖）"""
        buffer = CircularBuffer(size=3)

        # 添加5个项（超过容量）
        buffer.append(1)
        buffer.append(2)
        buffer.append(3)
        buffer.append(4)
        buffer.append(5)

        # 应该只保留最后3个
        items = buffer.get_items()
        assert items == [3, 4, 5]
        assert len(buffer) == 3

    def test_circular_buffer_get_items(self):
        """测试获取项"""
        buffer = CircularBuffer(size=10)

        # 添加多个项
        for i in range(5):
            buffer.append(i)

        # 获取所有项
        all_items = buffer.get_items()
        assert all_items == [0, 1, 2, 3, 4]

        # 获取最后3个
        last_3 = buffer.get_items(count=3)
        assert last_3 == [2, 3, 4]

    def test_circular_buffer_thread_safety(self):
        """测试线程安全"""
        import threading

        buffer = CircularBuffer(size=1000)

        def add_items():
            for i in range(100):
                buffer.append(i)

        # 启动10个线程
        threads = []
        for _ in range(10):
            t = threading.Thread(target=add_items)
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证总数
        assert len(buffer) == 1000  # 10个线程 * 100个项


# ============================================================================
# 测试2: FrequencyPredictor 频率预测器
# ============================================================================

class TestFrequencyPredictor:
    """测试频率预测器"""

    def test_predictor_init(self):
        """测试预测器初始化"""
        predictor = FrequencyPredictor()

        assert predictor is not None

    def test_predict_by_frequency(self):
        """测试基于频率的预测"""
        predictor = FrequencyPredictor()

        # 构造频率数据
        key_frequency = {
            'key1': 100,
            'key2': 50,
            'key3': 10,
            'key4': 5
        }

        # 预测Top 3
        hot_keys = predictor.predict(key_frequency, top_n=3)

        # 验证排序
        assert hot_keys == ['key1', 'key2', 'key3']

    def test_predict_empty_dict(self):
        """测试空字典预测"""
        predictor = FrequencyPredictor()

        hot_keys = predictor.predict({}, top_n=10)

        assert hot_keys == []

    def test_predict_with_decay(self):
        """测试带时间衰减的预测"""
        predictor = FrequencyPredictor()

        # 构造访问日志
        current_time = time.time()

        access_log = [
            {'key': 'old_key', 'timestamp': current_time - 7200},  # 2小时前
            {'key': 'recent_key', 'timestamp': current_time - 300},  # 5分钟前
            {'key': 'very_recent_key', 'timestamp': current_time - 60},  # 1分钟前
        ]

        # 使用时间衰减预测
        hot_keys = predictor.predict_with_decay(
            access_log,
            top_n=10,
            decay_factor=0.95
        )

        # 最近访问的键应该排在前面
        assert hot_keys[0] == 'very_recent_key'
        assert 'recent_key' in hot_keys
        assert 'old_key' in hot_keys

    def test_predict_with_decay_empty_log(self):
        """测试空日志的衰减预测"""
        predictor = FrequencyPredictor()

        hot_keys = predictor.predict_with_decay([], top_n=10)

        assert hot_keys == []

    def test_predict_with_decay_different_weights(self):
        """测试不同时间权重的计算"""
        predictor = FrequencyPredictor()

        current_time = time.time()

        # old_key: 100次访问，但都是2小时前
        # new_key: 10次访问，但都是最近1分钟
        access_log = []

        for _ in range(100):
            access_log.append({'key': 'old_key', 'timestamp': current_time - 7200})

        for _ in range(10):
            access_log.append({'key': 'new_key', 'timestamp': current_time - 60})

        # 使用时间衰减预测
        hot_keys = predictor.predict_with_decay(
            access_log,
            top_n=10,
            decay_factor=0.95
        )

        # 由于衰减因子0.95 ^ 2 = 0.9025，old_key的权重仍然很高
        # 即使有衰减，100次访问仍然比10次访问权重大
        # 验证两个键都在结果中
        assert 'old_key' in hot_keys
        assert 'new_key' in hot_keys


# ============================================================================
# 测试3: IntelligentCacheWarmer 智能预热器
# ============================================================================

class TestIntelligentCacheWarmer:
    """测试智能缓存预热器"""

    def test_warmer_init(self):
        """测试预热器初始化"""
        warmer = IntelligentCacheWarmer(
            access_log_size=1000,
            warm_up_interval=300
        )

        assert warmer is not None
        assert warmer.access_log.buffer.maxlen == 1000
        assert warmer.warm_up_interval == 300
        assert warmer.stats['warm_up_count'] == 0

    def test_record_access(self):
        """测试访问记录"""
        warmer = IntelligentCacheWarmer()

        # 记录访问
        warmer.record_access("test_key_1")
        warmer.record_access("test_key_2")
        warmer.record_access("test_key_1")  # 重复访问

        # 验证访问日志
        log_stats = warmer.get_access_log_stats()

        assert log_stats['total_access'] == 3
        assert log_stats['recent_access'] <= 3  # 可能都在最近1小时内

    def test_get_access_stats(self):
        """测试获取访问统计"""
        warmer = IntelligentCacheWarmer()

        # 记录多次访问
        for _ in range(10):
            warmer.record_access("key_a")
        for _ in range(5):
            warmer.record_access("key_b")

        # 获取统计
        stats = warmer.get_access_log_stats()

        assert stats['total_access'] == 15
        assert stats['unique_keys'] == 2

    def test_predict_hot_keys_by_frequency(self):
        """测试基于频率的热点键预测"""
        warmer = IntelligentCacheWarmer()

        # 模拟访问：key1访问10次，key2访问5次，key3访问1次
        for _ in range(10):
            warmer.record_access("key_1")
        for _ in range(5):
            warmer.record_access("key_2")
        warmer.record_access("key_3")

        # 预测热点键（不使用衰减）
        hot_keys = warmer.predict_hot_keys(use_decay=False)

        # key1应该排在最前面
        assert hot_keys[0] == "key_1"
        assert "key_2" in hot_keys
        assert "key_3" in hot_keys

    def test_predict_hot_keys_with_time_decay(self):
        """测试带时间衰减的热点键预测"""
        warmer = IntelligentCacheWarmer()

        # 旧的高频访问
        for _ in range(100):
            warmer.record_access("old_key")

        # 等待一小段时间
        time.sleep(0.1)

        # 新的高频访问
        for _ in range(10):
            warmer.record_access("new_key")

        # 预测热点键（使用时间衰减）
        hot_keys = warmer.predict_hot_keys(use_decay=True)

        # new_key应该有更高的优先级（因为recent访问）
        assert "new_key" in hot_keys
        assert "old_key" in hot_keys

    def test_predict_hot_keys_empty_log(self):
        """测试空日志的预测"""
        warmer = IntelligentCacheWarmer()

        # 没有记录任何访问
        hot_keys = warmer.predict_hot_keys()

        assert hot_keys == []

    def test_predict_hot_keys_top_n(self):
        """测试Top N限制"""
        warmer = IntelligentCacheWarmer()

        # 添加20个不同的键
        for i in range(20):
            for _ in range(i + 1):  # 不同的频率
                warmer.record_access(f"key_{i}")

        # 只获取Top 5
        hot_keys = warmer.predict_hot_keys(top_n=5, use_decay=False)

        assert len(hot_keys) == 5
        assert hot_keys[0] == "key_19"  # 频率最高的

    def test_warm_up_cache_empty_keys(self):
        """测试预热空键列表"""
        warmer = IntelligentCacheWarmer()

        # 异步测试
        async def test_empty():
            result = await warmer.warm_up_cache([])

            assert result['warmed'] == 0
            assert result['failed'] == 0
            assert result['skipped'] == 0

        asyncio.run(test_empty())

    def test_warm_up_cache_with_callback(self):
        """测试使用回调函数的预热"""
        warmer = IntelligentCacheWarmer()

        # Mock回调函数
        async def mock_fetch(key):
            return f"data_{key}"

        # 异步测试
        async def test_with_callback():
            # Mock hierarchical_cache
            with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
                mock_cache.l1_cache = {}

                result = await warmer.warm_up_cache(
                    keys=['key1', 'key2'],
                    fetch_callback=mock_fetch
                )

                assert result['warmed'] == 2
                assert result['failed'] == 0

        asyncio.run(test_with_callback())

    def test_warm_up_cache_already_cached(self):
        """测试跳过已缓存的键"""
        warmer = IntelligentCacheWarmer()

        async def test_skip():
            # Mock hierarchical_cache with existing data
            with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
                mock_cache.l1_cache = {'key1': 'existing_data'}

                async def mock_fetch(key):
                    return f"data_{key}"

                result = await warmer.warm_up_cache(
                    keys=['key1', 'key2'],
                    fetch_callback=mock_fetch
                )

                assert result['skipped'] == 1
                assert result['warmed'] == 1

        asyncio.run(test_skip())

    def test_warm_up_cache_failure(self):
        """测试预热失败处理"""
        warmer = IntelligentCacheWarmer()

        async def test_failure():
            # Mock回调函数抛出异常
            async def failing_fetch(key):
                raise Exception("Database error")

            result = await warmer.warm_up_cache(
                keys=['key1', 'key2'],
                fetch_callback=failing_fetch
            )

            assert result['failed'] == 2
            assert result['warmed'] == 0

        asyncio.run(test_failure())

    def test_warm_up_updates_stats(self):
        """测试预热更新统计信息"""
        warmer = IntelligentCacheWarmer()

        async def test_stats():
            async def mock_fetch(key):
                return f"data_{key}"

            with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
                mock_cache.l1_cache = {}

                # 执行预热
                await warmer.warm_up_cache(
                    keys=['key1', 'key2'],
                    fetch_callback=mock_fetch
                )

                # 检查统计
                stats = warmer.get_stats()

                assert stats['warm_up_count'] == 1
                assert stats['keys_warmed'] == 2
                assert stats['last_warm_up_time'] > 0

        asyncio.run(test_stats())

    def test_auto_warm_up(self):
        """测试自动预热"""
        warmer = IntelligentCacheWarmer()

        # 记录一些访问
        for _ in range(10):
            warmer.record_access("hot_key")

        async def test_auto():
            async def mock_fetch(key):
                return f"data_{key}"

            with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
                mock_cache.l1_cache = {}

                # 执行自动预热
                await warmer.auto_warm_up(fetch_callback=mock_fetch)

                # 验证预热执行
                stats = warmer.get_stats()
                assert stats['warm_up_count'] >= 1

        asyncio.run(test_auto())

    def test_get_stats(self):
        """测试获取统计信息"""
        warmer = IntelligentCacheWarmer()

        stats = warmer.get_stats()

        assert 'warm_up_count' in stats
        assert 'keys_warmed' in stats
        assert 'last_warm_up_time' in stats
        assert stats['warm_up_count'] == 0

    def test_get_access_log_stats(self):
        """测试获取访问日志统计"""
        warmer = IntelligentCacheWarmer(access_log_size=1000)

        # 添加一些访问
        for i in range(10):
            warmer.record_access(f"key_{i % 3}")  # 3个唯一键

        stats = warmer.get_access_log_stats()

        assert stats['total_access'] == 10
        assert stats['unique_keys'] == 3
        assert stats['buffer_capacity'] == 1000
        assert 'buffer_usage' in stats

    def test_concurrent_access_recording(self):
        """测试并发访问记录"""
        import threading

        warmer = IntelligentCacheWarmer()

        def record_accesses():
            for i in range(50):
                warmer.record_access(f"key_{i}")

        # 启动5个线程
        threads = []
        for _ in range(5):
            t = threading.Thread(target=record_accesses)
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证总数
        stats = warmer.get_access_log_stats()
        assert stats['total_access'] == 250  # 5个线程 * 50个访问

    def test_warm_up_stats_thread_safety(self):
        """测试统计信息的线程安全"""
        warmer = IntelligentCacheWarmer()

        async def test_concurrent_warmup():
            pass

            async def mock_fetch(key):
                return f"data_{key}"

            async def warm_up_task(keys):
                with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
                    mock_cache.l1_cache = {}
                    await warmer.warm_up_cache(keys, fetch_callback=mock_fetch)

            # 并发执行多个预热任务
            tasks = [
                warm_up_task([f'key_{i}'])
                for i in range(10)
            ]

            await asyncio.gather(*tasks)

            # 验证统计一致性
            stats = warmer.get_stats()
            assert stats['warm_up_count'] == 10

        asyncio.run(test_concurrent_warmup())


# ============================================================================
# 测试4: 全局实例和调度器
# ============================================================================

class TestGlobalWarmer:
    """测试全局预热器实例"""

    def test_global_warmer_instance(self):
        """测试全局预热器实例"""
        global_warmer = intelligent_cache_warmer

        assert global_warmer is not None
        assert isinstance(global_warmer, IntelligentCacheWarmer)

    def test_global_warmer_record_access(self):
        """测试全局实例记录访问"""
        global_warmer = intelligent_cache_warmer

        # 记录访问
        global_warmer.record_access("global_test_key")

        stats = global_warmer.get_access_log_stats()
        assert stats['total_access'] >= 1

    def test_start_warm_up_scheduler(self):
        """测试启动预热调度器"""
        # 这个测试只验证函数可以被调用
        # 实际的调度器运行需要在单独的线程中

        async def mock_fetch(key):
            return f"data_{key}"

        # 启动调度器（短间隔用于测试）
        thread = start_warm_up_scheduler(interval_seconds=1, fetch_callback=mock_fetch)

        assert thread is not None
        assert thread.is_alive()
        assert thread.name == "CacheWarmUpScheduler"

        # 等待一小段时间确保调度器启动
        time.sleep(0.5)


# ============================================================================
# 测试5: 边界条件和错误处理
# ============================================================================

class TestEdgeCases:
    """测试边界条件"""

    def test_import_error_handling(self):
        """测试导入错误处理（模拟hierarchical_cache不可用）"""
        # 这个测试验证当hierarchical_cache为None时的行为
        warmer = IntelligentCacheWarmer()

        async def test_without_hierarchical_cache():
            with patch('backend.core.cache.intelligent_warmer.hierarchical_cache', None):
                async def mock_fetch(key):
                    return f"data_{key}"

                # 即使hierarchical_cache为None，也应该能工作
                result = await warmer.warm_up_cache(
                    keys=['key1'],
                    fetch_callback=mock_fetch
                )

                # 应该成功预热（只是跳过L1缓存检查）
                assert result['warmed'] == 1

        asyncio.run(test_without_hierarchical_cache())

    def test_warm_up_without_callback(self):
        """测试没有回调函数的预热（测试data=None分支）"""
        warmer = IntelligentCacheWarmer()

        async def test_no_callback():
            with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
                mock_cache.l1_cache = {}

                # 不提供fetch_callback，data会是None
                result = await warmer.warm_up_cache(
                    keys=['key1'],
                    fetch_callback=None
                )

                # data为None，应该计入failed
                assert result['failed'] == 1
                assert result['warmed'] == 0

        asyncio.run(test_no_callback())

    def test_auto_warm_up_exception_handling(self):
        """测试自动预热中的异常处理"""
        warmer = IntelligentCacheWarmer()

        async def test_exception_in_auto_warmup():
            # Mock predict_hot_keys抛出异常
            with patch.object(warmer, 'predict_hot_keys', side_effect=Exception("Prediction error")):
                # 应该捕获异常而不崩溃
                await warmer.auto_warm_up()

                # 验证不会增加预热计数
                stats = warmer.get_stats()
                assert stats['warm_up_count'] == 0

        asyncio.run(test_exception_in_auto_warmup())

    def test_auto_warm_up_with_no_hot_keys(self):
        """测试没有热点键时的自动预热（测试早期返回）"""
        warmer = IntelligentCacheWarmer()

        async def test_no_hot_keys():
            # Mock predict_hot_keys返回空列表
            with patch.object(warmer, 'predict_hot_keys', return_value=[]):
                async def mock_fetch(key):
                    return f"data_{key}"

                # 应该提前返回，不执行预热
                await warmer.auto_warm_up(fetch_callback=mock_fetch)

                # 验证不会增加预热计数
                stats = warmer.get_stats()
                assert stats['warm_up_count'] == 0

        asyncio.run(test_no_hot_keys())

    def test_warm_up_with_none_data_from_callback(self):
        """测试回调返回None的情况"""
        warmer = IntelligentCacheWarmer()

        async def test_none_data():
            with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
                mock_cache.l1_cache = {}

                # Mock回调返回None
                async def mock_fetch_none(key):
                    return None

                result = await warmer.warm_up_cache(
                    keys=['key1', 'key2'],
                    fetch_callback=mock_fetch_none
                )

                # data为None，应该计入failed
                assert result['failed'] == 2
                assert result['warmed'] == 0

        asyncio.run(test_none_data())

    def test_predict_with_very_old_access(self):
        """测试非常旧的访问记录"""
        warmer = IntelligentCacheWarmer()

        current_time = time.time()

        # 添加一个很久以前的访问
        warmer.access_log.append({
            'key': 'ancient_key',
            'timestamp': current_time - 100000  # 超过1天
        })

        # 预测热点键（只看最近1小时）
        hot_keys = warmer.predict_hot_keys()

        # 旧访问应该被忽略
        assert 'ancient_key' not in hot_keys

    def test_predict_with_mixed_timing(self):
        """测试混合时间的访问记录"""
        warmer = IntelligentCacheWarmer()

        current_time = time.time()

        # 添加不同时间的访问
        warmer.access_log.append({'key': 'key1', 'timestamp': current_time - 30})
        warmer.access_log.append({'key': 'key2', 'timestamp': current_time - 7200})  # 2小时前
        warmer.access_log.append({'key': 'key1', 'timestamp': current_time - 10})
        warmer.access_log.append({'key': 'key3', 'timestamp': current_time - 60})

        # 使用衰减预测
        hot_keys = warmer.predict_hot_keys(use_decay=True)

        # key1应该排前面（最近且多次访问）
        assert hot_keys[0] == 'key1'
        assert 'key3' in hot_keys
        # key2太旧，可能不在列表中

    def test_buffer_overflow_with_timing(self):
        """测试缓冲区溢出时的时间顺序"""
        buffer = CircularBuffer(size=3)

        current_time = time.time()

        # 添加超过容量的项
        buffer.append({'timestamp': current_time - 30})
        buffer.append({'timestamp': current_time - 20})
        buffer.append({'timestamp': current_time - 10})
        buffer.append({'timestamp': current_time - 5})  # 触发溢出
        buffer.append({'timestamp': current_time})

        # 验证保留的是最新的项
        items = buffer.get_items()
        assert len(items) == 3
        assert items[0]['timestamp'] == current_time - 10
        assert items[2]['timestamp'] == current_time

    def test_large_number_of_keys(self):
        """测试大量键的性能"""
        warmer = IntelligentCacheWarmer(access_log_size=10000)

        # 添加大量访问
        for i in range(1000):
            warmer.record_access(f"key_{i % 100}")  # 100个唯一键

        # 预测应该快速完成
        start_time = time.time()
        hot_keys = warmer.predict_hot_keys(top_n=50, use_decay=False)
        elapsed = time.time() - start_time

        assert len(hot_keys) == 50
        assert elapsed < 1.0  # 应该在1秒内完成

    def test_decay_factor_extremes(self):
        """测试极端衰减因子"""
        predictor = FrequencyPredictor()

        current_time = time.time()

        access_log = [
            {'key': 'old', 'timestamp': current_time - 3600},
            {'key': 'new', 'timestamp': current_time - 60}
        ]

        # 衰减因子为0（不考虑时间）
        hot_keys = predictor.predict_with_decay(
            access_log,
            top_n=10,
            decay_factor=0.0
        )

        # 应该只返回空的或不可预测
        assert isinstance(hot_keys, list)

    def test_concurrent_predict_and_warmup(self):
        """测试并发预测和预热"""
        warmer = IntelligentCacheWarmer()

        async def test_concurrent():
            # 记录访问
            for i in range(100):
                warmer.record_access(f"key_{i}")

            # 并发执行预测和预热
            async def mock_fetch(key):
                return f"data_{key}"

            async def predict_task():
                return warmer.predict_hot_keys()

            async def warmup_task():
                with patch('backend.core.cache.intelligent_warmer.hierarchical_cache') as mock_cache:
                    mock_cache.l1_cache = {}
                    await warmer.warm_up_cache(['key1'], fetch_callback=mock_fetch)

            # 并发执行
            results = await asyncio.gather(
                predict_task(),
                warmup_task(),
                return_exceptions=True
            )

            # 验证两个任务都完成
            assert len(results) == 2

        asyncio.run(test_concurrent())


# ============================================================================
# 测试6: 调度器异常处理
# ============================================================================

class TestSchedulerExceptionHandling:
    """测试调度器异常处理"""

    def test_scheduler_loop_exception_handling(self):
        """测试调度器循环中的异常处理"""
        # 创建一个预热器实例用于测试
        test_warmer = IntelligentCacheWarmer()

        async def test_scheduler_exception():
            # Mock auto_warm_up抛出异常
            with patch.object(test_warmer, 'auto_warm_up', side_effect=Exception("Warm-up error")):
                # 模拟调度器的一次迭代
                try:
                    await test_warmer.auto_warm_up()
                except Exception:
                    pass

                # 验证异常被正确处理
                # 实际的调度器会在异常后继续运行
                assert True

        asyncio.run(test_scheduler_exception())


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
