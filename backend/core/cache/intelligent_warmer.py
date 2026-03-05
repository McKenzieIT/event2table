from backend.core.cache.decorators import cached

# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能缓存预热系统
================

基于历史访问数据预测热点键并提前预热

版本: 1.0.0
日期: 2026-02-24

功能:
- 访问日志记录
- 热点键预测 (基于频率和趋势)
- 启动时预热 (Top 100)
- 定时预热 (每5分钟)
- 简单预测算法 (可扩展为ARIMA)
"""

from collections import defaultdict, deque
from typing import Dict, List, Optional, Callable, TYPE_CHECKING
import threading
import time
import logging

if TYPE_CHECKING:
    from .cache_hierarchical import HierarchicalCache

try:
    from .cache_system import hierarchical_cache
    from .cache_system import CacheKeyBuilder, get_cache
except ImportError:
    hierarchical_cache = None  # type: ignore
    CacheKeyBuilder = None  # type: ignore
    get_cache = None  # type: ignore

logger = logging.getLogger(__name__)


class CircularBuffer:
    """循环缓冲区"""

    def __init__(self, size: int):
        """
        初始化循环缓冲区

        Args:
            size: 缓冲区大小
        """
        self.buffer: deque = deque(maxlen=size)
        self._lock = threading.Lock()

    def append(self, item):
        """添加项"""
        with self._lock:
            self.buffer.append(item)


    @cached(ttl=1800)  # Cache for 30 minutes
    def get_items(self, count: Optional[int] = None) -> List:
        """
        获取项

        Args:
            count: 数量 (None表示全部)

        Returns:
            项列表
        """
        with self._lock:
            if count is None:
                return list(self.buffer)
            else:
                return list(self.buffer)[-count:]

    def __len__(self):
        """获取长度"""
        return len(self.buffer)


class FrequencyPredictor:
    """基于频率的简单预测器"""

    def predict(
        self,
        key_frequency: Dict[str, int],
        top_n: int = 100
    ) -> List[str]:
        """
        预测热点键

        Args:
            key_frequency: 键频率字典
            top_n: 返回前N个热点键

        Returns:
            热点键列表 (按频率降序)
        """
        # 按频率排序
        sorted_keys = sorted(
            key_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [key for key, _ in sorted_keys[:top_n]]

    def predict_with_decay(
        self,
        access_log: List[Dict],
        top_n: int = 100,
        decay_factor: float = 0.95
    ) -> List[str]:
        """
        预测热点键 (带时间衰减)

        Args:
            access_log: 访问日志
            top_n: 返回前N个热点键
            decay_factor: 衰减因子 (越近的访问权重越高)

        Returns:
            热点键列表
        """
        if not access_log:
            return []

        # 计算加权频率
        key_scores: Dict[str, float] = defaultdict(float)
        current_time = time.time()

        for access in access_log:
            key = access['key']
            timestamp = access['timestamp']

            # 时间衰减
            age_seconds = current_time - timestamp
            age_hours = age_seconds / 3600

            # 计算权重
            weight = decay_factor ** age_hours
            key_scores[key] += weight

        # 按加权分数排序
        sorted_keys = sorted(
            key_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [key for key, _ in sorted_keys[:top_n]]


class IntelligentCacheWarmer:
    """
    智能缓存预热器

    预热策略:
    1. 启动时预热: 从历史日志提取Top 100热点键
    2. 定时预热: 每5分钟预测未来热点并预热
    3. 实时预热: 检测到突发流量时自动预热

    预测算法:
    - 基础: 频率统计
    - 进阶: 时间衰减
    - 未来: ARIMA时间序列预测
    """

    def __init__(
        self,
        access_log_size: int = 10000,
        warm_up_interval: int = 300  # 5分钟
    ):
        """
        初始化预热器

        Args:
            access_log_size: 访问日志大小
            warm_up_interval: 预热间隔 (秒)
        """
        self.access_log: CircularBuffer = CircularBuffer(access_log_size)
        self.predictor: FrequencyPredictor = FrequencyPredictor()
        self.warm_up_interval: int = warm_up_interval

        # 统计信息
        self.stats: Dict[str, float] = {
            'warm_up_count': 0.0,
            'keys_warmed': 0.0,
            'last_warm_up_time': 0.0,
            'prediction_accuracy': 0.0,  # 预测准确率（百分比）
            'predicted_count': 0.0,      # 预测的总键数
            'actual_hits': 0.0,          # 实际命中的键数
        }

        self._lock = threading.Lock()

        logger.info("✅ 智能缓存预热器初始化完成")

    def record_access(self, key: str):
        """
        记录缓存访问

        Args:
            key: 缓存键
        """
        self.access_log.append({
            'key': key,
            'timestamp': time.time()
        })

    def predict_hot_keys(
        self,
        minutes: int = 5,
        top_n: int = 100,
        use_decay: bool = True
    ) -> List[str]:
        """
        预测未来N分钟的热点键

        Args:
            minutes: 预测未来分钟数
            top_n: 返回前N个热点键
            use_decay: 是否使用时间衰减

        Returns:
            热点键列表
        """
        # 获取最近1小时的访问记录
        cutoff_time = time.time() - 3600
        recent_access = [
            access for access in self.access_log.get_items()
            if access['timestamp'] >= cutoff_time
        ]

        if not recent_access:
            logger.debug("没有历史访问数据，无法预测热点键")
            return []

        # 预测热点键
        if use_decay:
            hot_keys = self.predictor.predict_with_decay(
                recent_access,
                top_n=top_n
            )
        else:
            # 统计频率
            key_frequency: Dict[str, int] = defaultdict(int)
            for access in recent_access:
                key_frequency[access['key']] += 1

            hot_keys = self.predictor.predict(
                dict(key_frequency),
                top_n=top_n
            )

        logger.info(
            f"🔮 预测未来{minutes}分钟的热点键: "
            f"{len(hot_keys)}个"
        )

        return hot_keys

    async def warm_up_cache(
        self,
        keys: List[str],
        fetch_callback: Optional[Callable] = None
    ) -> Dict:
        """
        预热缓存

        Args:
            keys: 要预热的键列表
            fetch_callback: 从数据库获取数据的回调函数

        Returns:
            预热统计
        """
        if not keys:
            return {'warmed': 0, 'failed': 0, 'skipped': 0}

        warmed = 0
        failed = 0
        skipped = 0

        for key in keys:
            try:
                # 检查是否已在缓存中
                if hierarchical_cache is not None:
                    if key in hierarchical_cache.l1_cache:
                        skipped += 1
                        continue

                # 从数据库获取数据
                if fetch_callback:
                    data = await fetch_callback(key)
                else:
                    # 默认: 假设键已包含完整信息
                    data = None

                if data is not None:
                    # 写入缓存（如果hierarchical_cache可用）
                    if hierarchical_cache is not None:
                        hierarchical_cache.set_raw(key, data, ttl=3600, level='both')
                    warmed += 1
                else:
                    failed += 1

            except Exception as e:
                logger.error(f"预热失败 {key}: {e}")
                failed += 1

        # 更新统计
        with self._lock:
            self.stats['warm_up_count'] += 1
            self.stats['keys_warmed'] += warmed
            self.stats['last_warm_up_time'] = time.time()

        # 计算预测准确率（对比预测键和实际访问）
        accuracy_stats = self.calculate_prediction_accuracy(keys)

        logger.info(
            f"🔥 缓存预热完成: "
            f"预热{warmed}个, 跳过{skipped}个, 失败{failed}个 | "
            f"准确率: {accuracy_stats['accuracy']:.1f}%"
        )

        return {
            'warmed': warmed,
            'failed': failed,
            'skipped': skipped,
            'accuracy': accuracy_stats['accuracy']
        }

    async def auto_warm_up(self, fetch_callback: Optional[Callable] = None):
        """
        自动预热 (定时任务)

        Args:
            fetch_callback: 从数据库获取数据的回调函数
        """
        try:
            # 预测热点键
            hot_keys = self.predict_hot_keys(minutes=5, top_n=100)

            if not hot_keys:
                return

            # 执行预热
            await self.warm_up_cache(hot_keys, fetch_callback)

        except Exception as e:
            logger.error(f"自动预热失败: {e}")


    @cached(ttl=1800)  # Cache for 30 minutes
    def get_stats(self) -> Dict:
        """
        获取预热统计

        Returns:
            统计字典
        """
        with self._lock:
            return self.stats.copy()


    @cached(ttl=1800)  # Cache for 30 minutes
    def get_access_log_stats(self) -> Dict:
        """
        获取访问日志统计

        Returns:
            日志统计
        """
        total_access = len(self.access_log)

        # 获取最近1小时的访问
        cutoff_time = time.time() - 3600
        recent_access = [
            access for access in self.access_log.get_items()
            if access['timestamp'] >= cutoff_time
        ]

        # 统计唯一键数
        unique_keys = set(access['key'] for access in recent_access)

        buffer_maxlen = self.access_log.buffer.maxlen or 1

        return {
            'total_access': total_access,
            'recent_access': len(recent_access),
            'unique_keys': len(unique_keys),
            'buffer_capacity': buffer_maxlen,
            'buffer_usage': f"{total_access / buffer_maxlen:.1%}"
        }

    def calculate_prediction_accuracy(
        self,
        predicted_keys: List[str],
        actual_access_window_seconds: int = 300
    ) -> Dict[str, float]:
        """
        计算预测准确率

        对比预测的热点键和实际访问的键，计算预测命中率

        Args:
            predicted_keys: 预测的热点键列表
            actual_access_window_seconds: 实际访问时间窗口（秒，默认5分钟）

        Returns:
            准确率统计字典:
            {
                'accuracy': 准确率百分比 (0-100),
                'predicted_count': 预测键数,
                'actual_hits': 实际命中数,
                'hit_rate': 命中率
            }
        """
        if not predicted_keys:
            return {
                'accuracy': 0.0,
                'predicted_count': 0.0,
                'actual_hits': 0.0,
                'hit_rate': 0.0
            }

        # 获取时间窗口内的实际访问
        cutoff_time = time.time() - actual_access_window_seconds
        recent_access = [
            access for access in self.access_log.get_items()
            if access['timestamp'] >= cutoff_time
        ]

        # 统计实际访问的键
        actual_keys = set(access['key'] for access in recent_access)

        # 计算命中数：预测的键中有多少被实际访问
        predicted_set = set(predicted_keys)
        hits = predicted_set.intersection(actual_keys)

        # 计算准确率
        predicted_count = len(predicted_keys)
        actual_hits = len(hits)

        # 避免除零
        accuracy = (actual_hits / predicted_count * 100) if predicted_count > 0 else 0.0
        hit_rate = (actual_hits / predicted_count) if predicted_count > 0 else 0.0

        # 更新统计信息
        with self._lock:
            self.stats['predicted_count'] = predicted_count
            self.stats['actual_hits'] = actual_hits
            self.stats['prediction_accuracy'] = accuracy

        logger.debug(
            f"📊 预测准确率: {accuracy:.2f}% "
            f"(预测{predicted_count}个, 命中{actual_hits}个)"
        )

        return {
            'accuracy': accuracy,
            'predicted_count': float(predicted_count),
            'actual_hits': float(actual_hits),
            'hit_rate': hit_rate
        }


# 全局预热器实例
_intelligent_cache_warmer = None
_warmer_lock = threading.Lock()



@cached(ttl=1800)  # Cache for 30 minutes
def get_intelligent_warmer() -> IntelligentCacheWarmer:
    """
    获取全局预热器实例

    Returns:
        IntelligentCacheWarmer实例
    """
    global _intelligent_cache_warmer

    with _warmer_lock:
        if _intelligent_cache_warmer is None:
            _intelligent_cache_warmer = IntelligentCacheWarmer()
            logger.info("✅ 全局预热器实例已创建")

        return _intelligent_cache_warmer


# 向后兼容的别名
intelligent_cache_warmer = get_intelligent_warmer()


def start_warm_up_scheduler(
    interval_seconds: int = 300,
    fetch_callback: Optional[Callable] = None
):
    """
    启动预热调度器

    Args:
        interval_seconds: 预热间隔 (秒)
        fetch_callback: 从数据库获取数据的回调函数
    """
    async def scheduler_loop():
        while True:
            try:
                await intelligent_cache_warmer.auto_warm_up(fetch_callback)
            except Exception as e:
                logger.error(f"预热调度出错: {e}")
            time.sleep(interval_seconds)

    def run_scheduler():
        import asyncio
        asyncio.run(scheduler_loop())

    thread = threading.Thread(
        target=run_scheduler,
        daemon=True,
        name="CacheWarmUpScheduler"
    )
    thread.start()

    logger.info(f"✅ 缓存预热调度器已启动 (间隔: {interval_seconds}秒)")

    return thread


logger.info("✅ 智能缓存预热系统已加载 (1.0.0)")
