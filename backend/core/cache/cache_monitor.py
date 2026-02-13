#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Monitor Module v3.0
==========================
Provides comprehensive cache statistics and monitoring endpoints

版本: 3.0.0
日期: 2026-01-27

API端点:
- GET /admin/cache/status - 缓存状态（健康检查）
- GET /admin/cache/stats - 缓存统计信息（L1/L2/预热）
- GET /admin/cache/performance - 性能指标（响应时间、QPS）
- GET /admin/cache/keys - 列出所有缓存键
- POST /admin/cache/clear - 清空所有缓存
"""

from datetime import datetime
from flask import Blueprint, jsonify
from backend.core.logging import get_logger
from backend.core.cache.cache_system import get_cache, get_redis_client
from backend.core.cache.cache_system import hierarchical_cache
from cache_warmer import cache_warmer
from backend.core.config import CacheConfig

logger = get_logger(__name__)

cache_monitor_bp = Blueprint("cache_monitor", __name__)


@cache_monitor_bp.route("/admin/cache/status")
def cache_status():
    """获取缓存状态信息"""
    cache = get_cache()

    if cache is None:
        return jsonify(
            {
                "success": False,
                "status": "unavailable",
                "message": "缓存未初始化",
                "recommendations": [
                    "1. 安装Redis: pip install redis",
                    "2. 启动Redis服务: redis-server",
                    "3. 重启应用",
                ],
            }
        )

    try:
        # 测试Redis连接
        cache.set("health_check", "ok", timeout=10)
        result = cache.get("health_check")

        if result != "ok":
            raise Exception("缓存读写测试失败")

        # 获取Redis客户端和统计信息
        redis_client = get_redis_client()
        if redis_client is None:
            raise Exception("无法获取Redis客户端")

        info = redis_client.info()

        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        hit_rate = round(hits / total * 100, 2) if total > 0 else 0

        return jsonify(
            {
                "success": True,
                "status": "active",
                "message": "✅ Redis缓存运行正常",
                "stats": {
                    "keyspace_hits": hits,
                    "keyspace_misses": misses,
                    "hit_rate": f"{hit_rate}%",
                    "total_keys": redis_client.dbsize(),
                    "memory_used": info.get("used_memory_human", "0B"),
                    "uptime_days": round(info.get("uptime_in_seconds", 0) / 86400, 2),
                },
            }
        )

    except Exception as e:
        logger.error(f"缓存状态检查失败: {e}")
        return jsonify(
            {
                "success": False,
                "status": "error",
                "message": f"缓存错误: {str(e)}",
                "recommendations": [
                    "检查Redis服务是否运行",
                    "检查Redis连接配置",
                    "查看应用日志获取详细错误信息",
                ],
            }
        )


@cache_monitor_bp.route("/admin/cache/keys")
def list_cache_keys():
    """列出所有缓存键"""
    redis_client = get_redis_client()

    if redis_client is None:
        return jsonify({"error": "缓存不可用"})

    try:
        key_prefix = CacheConfig.CACHE_KEY_PREFIX

        # 获取所有键
        all_keys = redis_client.keys(f"{key_prefix}*")

        # 移除前缀以便显示
        keys = [key.replace(key_prefix, "") for key in all_keys]

        # 获取每个键的TTL
        keys_with_ttl = []
        for key in keys:
            full_key = f"{key_prefix}{key}"
            ttl = redis_client.ttl(full_key)
            keys_with_ttl.append(
                {"key": key, "ttl_seconds": ttl, "expires_in": f"{ttl}s" if ttl > 0 else "永久"}
            )

        return jsonify(
            {"total_keys": len(keys), "keys": sorted(keys_with_ttl, key=lambda x: x["key"])}
        )

    except Exception as e:
        return jsonify({"error": str(e)})


@cache_monitor_bp.route("/admin/cache/stats")
def cache_stats():
    """
    获取缓存统计信息（v3.0）

    返回L1、L2、预热三方面的统计
    """
    try:
        # L1统计（从hierarchical_cache）
        l1_stats = hierarchical_cache.get_stats()

        # L2统计（Redis）
        redis_client = get_redis_client()
        l2_stats = {}
        if redis_client:
            try:
                info = redis_client.info()
                l2_stats = {
                    "total_keys": redis_client.dbsize(),
                    "memory_used": info.get("used_memory_human", "0B"),
                    "memory_bytes": info.get("used_memory", 0),
                    "hit_rate": calculate_redis_hit_rate(info),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "uptime_days": round(info.get("uptime_in_seconds", 0) / 86400, 2),
                }
            except Exception as e:
                logger.warning(f"获取Redis统计失败: {e}")
                l2_stats = {"error": str(e)}

        # 预热统计
        warmup_stats = cache_warmer.get_warmup_stats()

        return jsonify(
            {
                "timestamp": datetime.now().isoformat(),
                "l1_cache": {
                    "size": l1_stats["l1_size"],
                    "capacity": l1_stats["l1_capacity"],
                    "usage": l1_stats["l1_usage"],
                    "hits": l1_stats["l1_hits"],
                    "sets": l1_stats["l1_sets"],
                    "evictions": l1_stats["l1_evictions"],
                },
                "l2_cache": l2_stats,
                "warmup": {
                    "warmed_games": warmup_stats["warmed_games"],
                    "warmed_events": warmup_stats["warmed_events"],
                    "warmed_templates": warmup_stats["warmed_templates"],
                    "total": warmup_stats["total"],
                },
                "overall": {
                    "total_requests": l1_stats["total_requests"],
                    "total_hits": l1_stats["l1_hits"] + l1_stats["l2_hits"],
                    "total_misses": l1_stats["misses"],
                    "hit_rate": l1_stats["hit_rate"],
                },
            }
        )

    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        return jsonify({"error": str(e), "message": "获取缓存统计失败"}), 500


@cache_monitor_bp.route("/admin/cache/performance")
def cache_performance():
    """
    获取缓存性能指标（v3.0）

    返回响应时间、吞吐量、效率等性能指标
    """
    try:
        # 获取L1统计
        l1_stats = hierarchical_cache.get_stats()

        # 获取Redis统计
        redis_client = get_redis_client()
        redis_info = {}
        if redis_client:
            try:
                redis_info = redis_client.info()
            except Exception:
                pass

        # 计算响应时间（基于统计数据估算）
        # L1: <1ms, L2: 5-10ms, L3: 50-200ms
        total_requests = l1_stats["total_requests"]

        if total_requests > 0:
            # 估算平均响应时间
            l1_ratio = l1_stats["l1_hits"] / total_requests
            l2_ratio = l1_stats["l2_hits"] / total_requests
            l3_ratio = l1_stats["misses"] / total_requests

            avg_response_time_ms = (
                l1_ratio * 0.5  # L1: 0.5ms
                + l2_ratio * 7.5  # L2: 7.5ms
                + l3_ratio * 125.0  # L3: 125ms
            )
        else:
            avg_response_time_ms = 0

        # 计算QPS（基于Redis统计）
        if redis_info:
            instantaneous_ops_per_sec = redis_info.get("instantaneous_ops_per_sec", 0)
        else:
            instantaneous_ops_per_sec = 0

        return jsonify(
            {
                "timestamp": datetime.now().isoformat(),
                "response_times": {
                    "l1_avg_ms": 0.5,
                    "l2_avg_ms": 7.5,
                    "l3_avg_ms": 125.0,
                    "overall_avg_ms": round(avg_response_time_ms, 2),
                },
                "throughput": {
                    "qps": instantaneous_ops_per_sec,
                    "hits_per_sec": round(
                        instantaneous_ops_per_sec
                        * (l1_stats["l1_hits"] + l1_stats["l2_hits"])
                        / max(total_requests, 1)
                    ),
                    "misses_per_sec": round(
                        instantaneous_ops_per_sec * l1_stats["misses"] / max(total_requests, 1)
                    ),
                },
                "efficiency": {
                    "hit_rate": l1_stats["hit_rate"],
                    "l1_contribution": f"{l1_stats['l1_hits'] / max(total_requests, 1) * 100:.1f}%",
                    "l2_contribution": f"{l1_stats['l2_hits'] / max(total_requests, 1) * 100:.1f}%",
                    "miss_rate": f"{l1_stats['misses'] / max(total_requests, 1) * 100:.1f}%",
                },
                "cache_levels": {
                    "l1": {
                        "size": l1_stats["l1_size"],
                        "capacity": l1_stats["l1_capacity"],
                        "usage_pct": float(l1_stats["l1_usage"].rstrip("%")),
                    },
                    "l2": {
                        "total_keys": redis_client.dbsize() if redis_client else 0,
                        "memory_used": (
                            redis_info.get("used_memory_human", "0B") if redis_info else "0B"
                        ),
                    },
                },
            }
        )

    except Exception as e:
        logger.error(f"获取性能指标失败: {e}")
        return jsonify({"error": str(e), "message": "获取性能指标失败"}), 500


@cache_monitor_bp.route("/admin/cache/clear", methods=["POST"])
def clear_all_cache():
    """
    清空所有缓存（v3.0）

    清空L1和L2缓存
    """
    try:
        # 清空L1缓存
        l1_before = hierarchical_cache.get_stats()["l1_size"]
        hierarchical_cache.clear_l1()
        l1_after = hierarchical_cache.get_stats()["l1_size"]
        l1_cleared = l1_before - l1_after

        # 清空L2缓存
        redis_client = get_redis_client()
        l2_cleared = 0
        if redis_client:
            try:
                pattern = f"{CacheConfig.CACHE_KEY_PREFIX}*"
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
                    l2_cleared = len(keys)
            except Exception as e:
                logger.warning(f"清空L2缓存失败: {e}")

        return jsonify(
            {
                "success": True,
                "message": f"✅ 缓存已清空: L1={l1_cleared}条, L2={l2_cleared}个键",
                "details": {
                    "l1_cleared": l1_cleared,
                    "l2_cleared": l2_cleared,
                    "total_cleared": l1_cleared + l2_cleared,
                },
            }
        )

    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# 辅助函数
# ============================================================================


def calculate_redis_hit_rate(redis_info: dict) -> str:
    """
    计算Redis命中率

    Args:
        redis_info: Redis INFO 命令返回的信息

    Returns:
        命中率字符串（如 "85.5%"）
    """
    hits = redis_info.get("keyspace_hits", 0)
    misses = redis_info.get("keyspace_misses", 0)
    total = hits + misses

    if total == 0:
        return "0.00%"

    hit_rate = round(hits / total * 100, 2)
    return f"{hit_rate}%"
