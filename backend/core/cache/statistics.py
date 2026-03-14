#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存统计模块
============

提供详细的缓存统计和性能监控

版本: 1.0.0
日期: 2026-02-20

功能:
- 命中率统计（L1/L2/总体）
- 性能指标统计（响应时间, QPS）
- 缓存键访问频率统计
- 统计历史记录
- 热点缓存键分析
"""

import logging
import threading
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

from backend.core.cache.cache_system import get_redis_client, hierarchical_cache

logger = logging.getLogger(__name__)


class CacheStatistics:
    """
    缓存统计模块

    提供详细的缓存统计和性能监控:
    1. 命中率统计 - L1/L2/总体命中率
    2. 性能指标统计 - 响应时间, QPS
    3. 缓存键访问频率统计 - 热点键分析
    4. 统计历史记录 - 性能趋势分析
    """

    def __init__(self, history_size: int = 1000):
        """
        初始化缓存统计模块

        Args:
            history_size: 历史记录大小
        """
        self.history_size = history_size

        # 访问频率统计
        self.access_counts: Dict[str, int] = defaultdict(int)
        self._access_lock = threading.Lock()

        # 性能历史记录
        self.performance_history: List[Dict] = []
        self._history_lock = threading.Lock()

        # 响应时间统计
        self.response_times: Dict[str, List[float]] = {
            "l1": [],
            "l2": [],
            "miss": [],
        }
        self._response_lock = threading.Lock()

        # 统计快照(用于计算增量)
        self.last_snapshot = None

        logger.info("✅ 缓存统计模块初始化完成")

    # ========================================================================
    # 访问记录
    # ========================================================================

    def record_access(self, key: str, hit: bool, level: str, response_time: float):
        """
        记录缓存访问

        Args:
            key: 缓存键
            hit: 是否命中
            level: 缓存层级（l1/l2/miss）
            response_time: 响应时间（毫秒）
        """
        # 记录访问频率
        with self._access_lock:
            self.access_counts[key] += 1

        # 记录响应时间
        with self._response_lock:
            if level in self.response_times:
                self.response_times[level].append(response_time)
                # 保留最近1000条记录
                if len(self.response_times[level]) > 1000:
                    self.response_times[level] = self.response_times[level][-1000:]

    def record_performance_snapshot(self):
        """记录性能快照"""
        try:
            # 获取当前统计
            cache_stats = hierarchical_cache.get_stats()

            # 获取Redis统计
            redis_client = get_redis_client()
            redis_stats = {}
            if redis_client:
                try:
                    info = redis_client.info()
                    redis_stats = {
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0),
                        "used_memory": info.get("used_memory", 0),
                        "connected_clients": info.get("connected_clients", 0),
                        "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
                    }
                except Exception:
                    pass

            # 创建快照
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "l1_stats": {
                    "size": cache_stats["l1_size"],
                    "hits": cache_stats["l1_hits"],
                    "evictions": cache_stats["l1_evictions"],
                },
                "l2_stats": redis_stats,
                "overall_stats": {
                    "total_requests": cache_stats["total_requests"],
                    "hit_rate": cache_stats["hit_rate"],
                    "l1_hits": cache_stats["l1_hits"],
                    "l2_hits": cache_stats["l2_hits"],
                    "misses": cache_stats["misses"],
                },
            }

            # 添加到历史记录
            with self._history_lock:
                self.performance_history.append(snapshot)
                # 保留最近的历史记录
                if len(self.performance_history) > self.history_size:
                    self.performance_history = self.performance_history[-self.history_size :]

        except Exception as e:
            logger.error(f"记录性能快照失败: {e}")

    # ========================================================================
    # 统计查询
    # ========================================================================

    def get_hit_rate_stats(self) -> Dict:
        """
        获取命中率统计

        Returns:
            命中率统计字典
        """
        try:
            cache_stats = hierarchical_cache.get_stats()

            total_requests = cache_stats["total_requests"]
            if total_requests == 0:
                return {
                    "l1_hit_rate": "0.00%",
                    "l2_hit_rate": "0.00%",
                    "overall_hit_rate": "0.00%",
                    "miss_rate": "0.00%",
                }

            l1_hit_rate = cache_stats["l1_hits"] / total_requests * 100
            l2_hit_rate = cache_stats["l2_hits"] / total_requests * 100
            overall_hit_rate = (
                (cache_stats["l1_hits"] + cache_stats["l2_hits"]) / total_requests * 100
            )
            miss_rate = cache_stats["misses"] / total_requests * 100

            return {
                "l1_hit_rate": f"{l1_hit_rate:.2f}%",
                "l2_hit_rate": f"{l2_hit_rate:.2f}%",
                "overall_hit_rate": f"{overall_hit_rate:.2f}%",
                "miss_rate": f"{miss_rate:.2f}%",
                "l1_hits": cache_stats["l1_hits"],
                "l2_hits": cache_stats["l2_hits"],
                "misses": cache_stats["misses"],
                "total_requests": total_requests,
            }

        except Exception as e:
            logger.error(f"获取命中率统计失败: {e}")
            return {}

    def get_performance_stats(self) -> Dict:
        """
        获取性能指标统计

        Returns:
            性能指标字典
        """
        try:
            # 计算平均响应时间
            avg_response_times = {}

            with self._response_lock:
                for level, times in self.response_times.items():
                    if times:
                        avg_time = sum(times) / len(times)
                        avg_response_times[f"{level}_avg_ms"] = round(avg_time, 3)
                    else:
                        avg_response_times[f"{level}_avg_ms"] = 0.0

            # 获取Redis性能指标
            redis_client = get_redis_client()
            redis_perf = {}
            if redis_client:
                try:
                    info = redis_client.info()
                    redis_perf = {
                        "ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
                        "used_memory_mb": info.get("used_memory", 0) / 1024 / 1024,
                        "connected_clients": info.get("connected_clients", 0),
                    }
                except Exception:
                    pass

            return {
                "response_times": avg_response_times,
                "redis_performance": redis_perf,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"获取性能统计失败: {e}")
            return {}

    def get_hot_keys(self, limit: int = 10) -> List[Dict]:
        """
        获取热点缓存键

        Args:
            limit: 返回的键数量

        Returns:
            热点键列表
        """
        try:
            with self._access_lock:
                # 按访问次数排序
                sorted_keys = sorted(self.access_counts.items(), key=lambda x: x[1], reverse=True)

                # 返回Top N
                hot_keys = []
                for key, count in sorted_keys[:limit]:
                    hot_keys.append(
                        {
                            "key": key,
                            "access_count": count,
                        }
                    )

                return hot_keys

        except Exception as e:
            logger.error(f"获取热点键失败: {e}")
            return []

    def get_performance_trend(self, hours: int = 24) -> Dict:
        """
        获取性能趋势

        Args:
            hours: 查询的小时数

        Returns:
            性能趋势字典
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            with self._history_lock:
                # 过滤指定时间范围内的快照
                recent_snapshots = [
                    s
                    for s in self.performance_history
                    if datetime.fromisoformat(s["timestamp"]) >= cutoff_time
                ]

            if not recent_snapshots:
                return {
                    "message": f"最近{hours}小时无性能数据",
                    "snapshots": [],
                }

            # 提取趋势数据
            trend_data: Dict[str, List[Any]] = {
                "timestamps": [],
                "hit_rates": [],
                "l1_sizes": [],
                "ops_per_sec": [],
            }

            for snapshot in recent_snapshots:
                trend_data["timestamps"].append(snapshot["timestamp"])
                trend_data["hit_rates"].append(snapshot["overall_stats"]["hit_rate"])
                trend_data["l1_sizes"].append(snapshot["l1_stats"]["size"])

                if "instantaneous_ops_per_sec" in snapshot.get("l2_stats", {}):
                    trend_data["ops_per_sec"].append(
                        snapshot["l2_stats"]["instantaneous_ops_per_sec"]
                    )

            return {
                "period_hours": hours,
                "snapshot_count": len(recent_snapshots),
                "trend": trend_data,
                "latest": recent_snapshots[-1] if recent_snapshots else None,
            }

        except Exception as e:
            logger.error(f"获取性能趋势失败: {e}")
            return {}

    def get_detailed_stats(self) -> Dict:
        """
        获取详细统计信息

        Returns:
            详细统计字典
        """
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "hit_rate_stats": self.get_hit_rate_stats(),
                "performance_stats": self.get_performance_stats(),
                "hot_keys": self.get_hot_keys(limit=20),
                "access_key_count": len(self.access_counts),
                "history_size": len(self.performance_history),
            }

        except Exception as e:
            logger.error(f"获取详细统计失败: {e}")
            return {}

    # ========================================================================
    # 统计管理
    # ========================================================================

    def reset_stats(self):
        """重置所有统计信息"""
        try:
            # 重置访问频率
            with self._access_lock:
                self.access_counts.clear()

            # 重置响应时间
            with self._response_lock:
                for level in self.response_times:
                    self.response_times[level].clear()

            # 重置历史记录
            with self._history_lock:
                self.performance_history.clear()

            # 重置缓存统计
            hierarchical_cache.reset_stats()

            logger.info("📊 缓存统计已重置")

        except Exception as e:
            logger.error(f"重置统计失败: {e}")

    def cleanup_old_records(self, max_age_hours: int = 24):
        """
        清理旧记录

        Args:
            max_age_hours: 最大保留时间（小时）
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

            with self._history_lock:
                # 过滤掉旧记录
                self.performance_history = [
                    s
                    for s in self.performance_history
                    if datetime.fromisoformat(s["timestamp"]) >= cutoff_time
                ]

            logger.info(f"清理旧记录: 保留最近{max_age_hours}小时")

        except Exception as e:
            logger.error(f"清理旧记录失败: {e}")


# 全局缓存统计实例
cache_statistics = CacheStatistics()


logger.info("✅ 缓存统计模块已加载 (1.0.0)")
