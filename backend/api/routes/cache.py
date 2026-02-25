#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理API路由
===============

提供缓存管理相关的REST API

版本: 2.0.0
日期: 2026-02-24

API端点:
- GET  /api/cache/stats          - 获取缓存统计信息
- GET  /api/cache/stats/detailed - 获取详细统计信息
- GET  /api/cache/keys           - 获取缓存键列表
- GET  /api/cache/keys/search    - 搜索缓存键
- GET  /api/cache/keys/<key>     - 获取单个缓存键详情
- DELETE /api/cache/keys/<key>   - 删除单个缓存键
- POST /api/cache/clear          - 清空所有缓存
- POST /api/cache/invalidate/game/<game_gid> - 失效游戏相关缓存
- POST /api/cache/invalidate/event/<event_id> - 失效事件相关缓存

🆕 新增端点 (2.0.0):
监控和告警:
- GET  /api/cache/monitoring/alerts   - 获取当前告警列表
- GET  /api/cache/monitoring/metrics  - 获取Prometheus格式的指标
- GET  /api/cache/monitoring/trends   - 获取性能趋势数据

容量监控:
- GET  /api/cache/capacity/l1         - 获取L1容量详情
- GET  /api/cache/capacity/l2         - 获取L2容量详情
- GET  /api/cache/capacity/prediction - 获取容量预测

布隆过滤器:
- POST /api/cache/bloom-filter/rebuild - 手动重建布隆过滤器
- GET  /api/cache/bloom-filter/stats  - 获取布隆过滤器统计

智能预热:
- POST /api/cache/warm-up/predict     - 预测热点键
- POST /api/cache/warm-up/execute     - 执行预热任务

降级管理:
- GET  /api/cache/degradation/status  - 获取降级状态
- POST /api/cache/degradation/switch  - 手动切换降级模式
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

from backend.core.cache.cache_system import (
    hierarchical_cache,
    get_redis_client,
    CacheKeyBuilder
)
from backend.core.cache.protection import cache_protection
from backend.core.cache.invalidator import cache_invalidator_enhanced
from backend.core.cache.statistics import cache_statistics
from backend.core.config.config import CacheConfig

logger = logging.getLogger(__name__)

cache_bp = Blueprint('cache', __name__)


# ============================================================================
# 缓存统计API
# ============================================================================

@cache_bp.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """
    获取缓存统计信息
    
    返回L1、L2缓存的统计信息
    
    Returns:
        {
            "success": true,
            "timestamp": "2026-02-20T21:00:00",
            "l1_cache": {...},
            "l2_cache": {...},
            "overall": {...}
        }
    """
    try:
        # 获取L1统计
        l1_stats = hierarchical_cache.get_stats()
        
        # 获取L2统计（Redis）
        redis_client = get_redis_client()
        l2_stats = {}
        if redis_client:
            try:
                info = redis_client.info()
                hits = info.get("keyspace_hits", 0)
                misses = info.get("keyspace_misses", 0)
                total = hits + misses
                hit_rate = (hits / total * 100) if total > 0 else 0
                
                l2_stats = {
                    "total_keys": redis_client.dbsize(),
                    "memory_used": info.get("used_memory_human", "0B"),
                    "memory_bytes": info.get("used_memory", 0),
                    "hit_rate": f"{hit_rate:.2f}%",
                    "keyspace_hits": hits,
                    "keyspace_misses": misses,
                    "uptime_days": round(info.get("uptime_in_seconds", 0) / 86400, 2),
                    "connected_clients": info.get("connected_clients", 0),
                }
            except Exception as e:
                logger.warning(f"获取Redis统计失败: {e}")
                l2_stats = {"error": str(e)}
        
        # 获取防护统计
        protection_stats = cache_protection.get_stats()
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "l1_cache": {
                "size": l1_stats["l1_size"],
                "capacity": l1_stats["l1_capacity"],
                "usage": l1_stats["l1_usage"],
                "hits": l1_stats["l1_hits"],
                "sets": l1_stats.get("l1_sets", 0),
                "evictions": l1_stats["l1_evictions"],
            },
            "l2_cache": l2_stats,
            "protection": protection_stats,
            "overall": {
                "total_requests": l1_stats["total_requests"],
                "total_hits": l1_stats["l1_hits"] + l1_stats["l2_hits"],
                "total_misses": l1_stats["misses"],
                "hit_rate": l1_stats["hit_rate"],
                "empty_hits": l1_stats.get("empty_hits", 0),
            },
        })
    
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取缓存统计失败"
        }), 500


@cache_bp.route('/api/cache/stats/detailed', methods=['GET'])
def get_detailed_stats():
    """
    获取详细统计信息
    
    包括热点键、性能趋势等
    
    Query Parameters:
        hours: 查询的小时数（默认24）
    
    Returns:
        {
            "success": true,
            "timestamp": "2026-02-20T21:00:00",
            "hit_rate_stats": {...},
            "performance_stats": {...},
            "hot_keys": [...],
            "performance_trend": {...}
        }
    """
    try:
        hours = int(request.args.get('hours', 24))
        
        # 获取详细统计
        detailed_stats = cache_statistics.get_detailed_stats()
        
        # 获取性能趋势
        performance_trend = cache_statistics.get_performance_trend(hours=hours)
        
        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            **detailed_stats,
            "performance_trend": performance_trend,
        })
    
    except Exception as e:
        logger.error(f"获取详细统计失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取详细统计失败"
        }), 500


# ============================================================================
# 缓存键管理API
# ============================================================================

@cache_bp.route('/api/cache/keys', methods=['GET'])
def list_cache_keys():
    """
    列出所有缓存键
    
    Query Parameters:
        pattern: 键模式（可选，如 "games:*"）
        limit: 返回数量限制（默认100）
    
    Returns:
        {
            "success": true,
            "total_keys": 50,
            "keys": [...]
        }
    """
    try:
        pattern = request.args.get('pattern', f"{CacheKeyBuilder.PREFIX}*")
        limit = int(request.args.get('limit', 100))
        
        redis_client = get_redis_client()
        if redis_client is None:
            return jsonify({
                "success": False,
                "error": "Redis不可用"
            }), 503
        
        # 获取所有键
        all_keys = redis_client.keys(pattern)
        
        # 移除前缀以便显示
        keys = []
        for key in all_keys[:limit]:
            ttl = redis_client.ttl(key)
            key_str = key.decode() if isinstance(key, bytes) else key
            keys.append({
                "key": key_str.replace(CacheKeyBuilder.PREFIX, ""),
                "full_key": key_str,
                "ttl_seconds": ttl,
                "expires_in": f"{ttl}s" if ttl > 0 else "永久",
            })
        
        return jsonify({
            "success": True,
            "total_keys": len(all_keys),
            "returned_keys": len(keys),
            "keys": sorted(keys, key=lambda x: x["key"]),
        })
    
    except Exception as e:
        logger.error(f"列出缓存键失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "列出缓存键失败"
        }), 500


@cache_bp.route('/api/cache/keys/search', methods=['GET'])
def search_cache_keys():
    """
    搜索缓存键
    
    Query Parameters:
        query: 搜索关键词
        limit: 返回数量限制（默认50）
    
    Returns:
        {
            "success": true,
            "query": "games",
            "total_matches": 10,
            "keys": [...]
        }
    """
    try:
        query = request.args.get('query', '')
        limit = int(request.args.get('limit', 50))
        
        if not query:
            return jsonify({
                "success": False,
                "error": "缺少搜索关键词"
            }), 400
        
        redis_client = get_redis_client()
        if redis_client is None:
            return jsonify({
                "success": False,
                "error": "Redis不可用"
            }), 503
        
        # 获取所有键
        all_keys = redis_client.keys(f"{CacheKeyBuilder.PREFIX}*")
        
        # 过滤匹配的键
        matched_keys = []
        for key in all_keys:
            key_str = key.decode() if isinstance(key, bytes) else key
            if query.lower() in key_str.lower():
                ttl = redis_client.ttl(key)
                matched_keys.append({
                    "key": key_str.replace(CacheKeyBuilder.PREFIX, ""),
                    "full_key": key_str,
                    "ttl_seconds": ttl,
                    "expires_in": f"{ttl}s" if ttl > 0 else "永久",
                })
                
                if len(matched_keys) >= limit:
                    break
        
        return jsonify({
            "success": True,
            "query": query,
            "total_matches": len(matched_keys),
            "keys": matched_keys,
        })
    
    except Exception as e:
        logger.error(f"搜索缓存键失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "搜索缓存键失败"
        }), 500


@cache_bp.route('/api/cache/keys/<path:key>', methods=['GET'])
def get_cache_key_detail(key: str):
    """
    获取单个缓存键详情
    
    Args:
        key: 缓存键（不含前缀）
    
    Returns:
        {
            "success": true,
            "key": "games:detail:gid:10000147",
            "exists": true,
            "value": {...},
            "ttl_seconds": 300
        }
    """
    try:
        redis_client = get_redis_client()
        if redis_client is None:
            return jsonify({
                "success": False,
                "error": "Redis不可用"
            }), 503
        
        # 构建完整键
        full_key = f"{CacheKeyBuilder.PREFIX}{key}"
        
        # 检查键是否存在
        if not redis_client.exists(full_key):
            return jsonify({
                "success": True,
                "key": key,
                "full_key": full_key,
                "exists": False,
            })
        
        # 获取值和TTL
        value = redis_client.get(full_key)
        ttl = redis_client.ttl(full_key)
        
        # 尝试解析JSON
        import json
        parsed_value = None
        if value:
            try:
                value_str = value.decode() if isinstance(value, bytes) else value
                parsed_value = json.loads(value_str)
            except (json.JSONDecodeError, UnicodeDecodeError):
                parsed_value = value_str if 'value_str' in locals() else str(value)
        
        return jsonify({
            "success": True,
            "key": key,
            "full_key": full_key,
            "exists": True,
            "value": parsed_value,
            "ttl_seconds": ttl,
            "expires_in": f"{ttl}s" if ttl > 0 else "永久",
        })
    
    except Exception as e:
        logger.error(f"获取缓存键详情失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取缓存键详情失败"
        }), 500


@cache_bp.route('/api/cache/keys/<path:key>', methods=['DELETE'])
def delete_cache_key(key: str):
    """
    删除单个缓存键
    
    Args:
        key: 缓存键（不含前缀）
    
    Returns:
        {
            "success": true,
            "message": "缓存键已删除",
            "key": "games:detail:gid:10000147"
        }
    """
    try:
        redis_client = get_redis_client()
        
        # 构建完整键
        full_key = f"{CacheKeyBuilder.PREFIX}{key}"
        
        # 删除L1缓存
        if full_key in hierarchical_cache.l1_cache:
            del hierarchical_cache.l1_cache[full_key]
            del hierarchical_cache.l1_timestamps[full_key]
        
        # 删除L2缓存
        if redis_client:
            redis_client.delete(full_key)
        
        logger.info(f"删除缓存键: {key}")
        
        return jsonify({
            "success": True,
            "message": "缓存键已删除",
            "key": key,
        })
    
    except Exception as e:
        logger.error(f"删除缓存键失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "删除缓存键失败"
        }), 500


# ============================================================================
# 缓存清理API
# ============================================================================

@cache_bp.route('/api/cache/clear', methods=['POST'])
def clear_all_cache():
    """
    清空所有缓存
    
    Returns:
        {
            "success": true,
            "message": "缓存已清空",
            "details": {
                "l1_cleared": 100,
                "l2_cleared": 500
            }
        }
    """
    try:
        # 清空缓存
        l1_count, l2_count = cache_invalidator_enhanced.clear_all()
        
        logger.info(f"清空所有缓存: L1={l1_count}, L2={l2_count}")
        
        return jsonify({
            "success": True,
            "message": f"✅ 缓存已清空: L1={l1_count}条, L2={l2_count}个键",
            "details": {
                "l1_cleared": l1_count,
                "l2_cleared": l2_count,
                "total_cleared": l1_count + l2_count,
            },
        })
    
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "清空缓存失败"
        }), 500


# ============================================================================
# 缓存失效API
# ============================================================================

@cache_bp.route('/api/cache/invalidate/game/<int:game_gid>', methods=['POST'])
def invalidate_game_cache(game_gid: int):
    """
    失效游戏相关的所有缓存
    
    Args:
        game_gid: 游戏业务GID
    
    Returns:
        {
            "success": true,
            "message": "游戏缓存已失效",
            "game_gid": 10000147,
            "invalidated_keys": [...]
        }
    """
    try:
        # 失效游戏相关缓存
        invalidated_keys = cache_invalidator_enhanced.invalidate_game_related(game_gid)
        
        logger.info(f"失效游戏缓存: game_gid={game_gid}, {len(invalidated_keys)}个键")
        
        return jsonify({
            "success": True,
            "message": f"✅ 游戏缓存已失效: {len(invalidated_keys)}个键",
            "game_gid": game_gid,
            "invalidated_keys": list(invalidated_keys),
        })
    
    except Exception as e:
        logger.error(f"失效游戏缓存失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "失效游戏缓存失败"
        }), 500


@cache_bp.route('/api/cache/invalidate/event/<int:event_id>', methods=['POST'])
def invalidate_event_cache(event_id: int):
    """
    失效事件相关的所有缓存
    
    Args:
        event_id: 事件ID
    
    Request Body:
        {
            "game_gid": 10000147
        }
    
    Returns:
        {
            "success": true,
            "message": "事件缓存已失效",
            "event_id": 123,
            "invalidated_keys": [...]
        }
    """
    try:
        # 获取game_gid
        data = request.get_json() or {}
        game_gid = data.get('game_gid')
        
        if not game_gid:
            return jsonify({
                "success": False,
                "error": "缺少game_gid参数"
            }), 400
        
        # 失效事件相关缓存
        invalidated_keys = cache_invalidator_enhanced.invalidate_event_related(event_id, game_gid)
        
        logger.info(f"失效事件缓存: event_id={event_id}, game_gid={game_gid}, {len(invalidated_keys)}个键")
        
        return jsonify({
            "success": True,
            "message": f"✅ 事件缓存已失效: {len(invalidated_keys)}个键",
            "event_id": event_id,
            "game_gid": game_gid,
            "invalidated_keys": list(invalidated_keys),
        })
    
    except Exception as e:
        logger.error(f"失效事件缓存失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "失效事件缓存失败"
        }), 500


# ============================================================================
# 监控和告警API
# ============================================================================

@cache_bp.route('/api/cache/monitoring/alerts', methods=['GET'])
def get_alerts():
    """
    获取当前告警列表

    Returns:
        {
            "success": true,
            "alerts": [...],
            "count": 5
        }
    """
    try:
        from backend.core.cache.monitoring import get_cache_alert_manager

        alert_manager = get_cache_alert_manager()
        alerts = alert_manager.get_active_alerts()

        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "count": len(alerts),
        })

    except Exception as e:
        logger.error(f"获取告警列表失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取告警列表失败"
        }), 500


@cache_bp.route('/api/cache/monitoring/metrics', methods=['GET'])
def get_metrics():
    """
    获取Prometheus格式的指标

    Returns:
        Prometheus格式的文本指标
    """
    try:
        from backend.core.cache.monitoring import get_cache_alert_manager, export_prometheus_metrics

        alert_manager = get_cache_alert_manager()
        metrics = export_prometheus_metrics(alert_manager)

        return metrics, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        logger.error(f"获取Prometheus指标失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取Prometheus指标失败"
        }), 500


@cache_bp.route('/api/cache/monitoring/trends', methods=['GET'])
def get_trends():
    """
    获取性能趋势数据

    Query Parameters:
        hours: 查询的小时数（默认24）

    Returns:
        {
            "success": true,
            "trends": {...}
        }
    """
    try:
        from backend.core.cache.monitoring import get_cache_alert_manager

        hours = int(request.args.get('hours', 24))

        alert_manager = get_cache_alert_manager()
        summary = alert_manager.get_metrics_summary()

        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "hours": hours,
            "trends": summary,
        })

    except Exception as e:
        logger.error(f"获取性能趋势失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取性能趋势失败"
        }), 500


# ============================================================================
# 容量监控API
# ============================================================================

@cache_bp.route('/api/cache/capacity/l1', methods=['GET'])
def get_l1_capacity():
    """
    获取L1容量详情

    Returns:
        {
            "success": true,
            "capacity": {...}
        }
    """
    try:
        from backend.core.cache.capacity_monitor import get_capacity_monitor

        monitor = get_capacity_monitor()
        stats = monitor.get_capacity_stats()

        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "capacity": stats.get('l1', {}),
        })

    except Exception as e:
        logger.error(f"获取L1容量失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取L1容量失败"
        }), 500


@cache_bp.route('/api/cache/capacity/l2', methods=['GET'])
def get_l2_capacity():
    """
    获取L2容量详情

    Returns:
        {
            "success": true,
            "capacity": {...}
        }
    """
    try:
        from backend.core.cache.capacity_monitor import get_capacity_monitor

        monitor = get_capacity_monitor()
        stats = monitor.get_capacity_stats()

        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "capacity": stats.get('l2', {}),
        })

    except Exception as e:
        logger.error(f"获取L2容量失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取L2容量失败"
        }), 500


@cache_bp.route('/api/cache/capacity/prediction', methods=['GET'])
def get_capacity_prediction():
    """
    获取容量预测

    Query Parameters:
        days: 预测天数（默认7）

    Returns:
        {
            "success": true,
            "prediction": {...}
        }
    """
    try:
        from backend.core.cache.capacity_monitor import get_capacity_monitor

        days = int(request.args.get('days', 7))

        monitor = get_capacity_monitor()
        prediction = monitor.predict_capacity_limit(days=days)

        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "prediction_days": days,
            "prediction": prediction,
        })

    except Exception as e:
        logger.error(f"获取容量预测失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取容量预测失败"
        }), 500


# ============================================================================
# 布隆过滤器API
# ============================================================================

@cache_bp.route('/api/cache/bloom-filter/rebuild', methods=['POST'])
def rebuild_bloom_filter():
    """
    手动重建布隆过滤器

    Returns:
        {
            "success": true,
            "message": "布隆过滤器已重建",
            "stats": {...}
        }
    """
    try:
        from backend.core.cache.bloom_filter_enhanced import get_enhanced_bloom_filter

        bloom = get_enhanced_bloom_filter()
        stats = bloom.force_rebuild()

        logger.info(f"布隆过滤器已重建: {stats}")

        return jsonify({
            "success": True,
            "message": "✅ 布隆过滤器已重建",
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
        })

    except Exception as e:
        logger.error(f"重建布隆过滤器失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "重建布隆过滤器失败"
        }), 500


@cache_bp.route('/api/cache/bloom-filter/stats', methods=['GET'])
def get_bloom_filter_stats():
    """
    获取布隆过滤器统计

    Returns:
        {
            "success": true,
            "stats": {...}
        }
    """
    try:
        from backend.core.cache.bloom_filter_enhanced import get_enhanced_bloom_filter

        bloom = get_enhanced_bloom_filter()
        stats = bloom.get_stats()

        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
        })

    except Exception as e:
        logger.error(f"获取布隆过滤器统计失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取布隆过滤器统计失败"
        }), 500


# ============================================================================
# 智能预热API
# ============================================================================

@cache_bp.route('/api/cache/warm-up/predict', methods=['POST'])
def predict_hot_keys():
    """
    预测热点键

    Request Body:
        {
            "minutes": 5,
            "top_n": 100,
            "use_decay": true
        }

    Returns:
        {
            "success": true,
            "hot_keys": [...],
            "count": 100
        }
    """
    try:
        from backend.core.cache.intelligent_warmer import get_intelligent_warmer

        # Handle case where Content-Type is not set
        try:
            data = request.get_json() or {}
        except Exception:
            data = {}

        minutes = data.get('minutes', 5)
        top_n = data.get('top_n', 100)
        use_decay = data.get('use_decay', True)

        warmer = get_intelligent_warmer()
        hot_keys = warmer.predict_hot_keys(minutes=minutes, top_n=top_n, use_decay=use_decay)

        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "hot_keys": hot_keys,
            "count": len(hot_keys),
        })

    except Exception as e:
        logger.error(f"预测热点键失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "预测热点键失败"
        }), 500


@cache_bp.route('/api/cache/warm-up/execute', methods=['POST'])
def execute_warm_up():
    """
    执行预热任务

    Request Body:
        {
            "keys": ["key1", "key2", ...]
        }

    Returns:
        {
            "success": true,
            "message": "预热完成",
            "result": {...}
        }
    """
    try:
        from backend.core.cache.intelligent_warmer import get_intelligent_warmer
        import asyncio

        # Handle case where Content-Type is not set
        try:
            data = request.get_json() or {}
        except Exception:
            data = {}

        keys = data.get('keys', [])

        if not keys:
            # 如果没有提供keys，先预测热点键
            warmer = get_intelligent_warmer()
            keys = warmer.predict_hot_keys(minutes=5, top_n=100)

        warmer = get_intelligent_warmer()

        # warm_up_cache is async, need to run it in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(warmer.warm_up_cache(keys=keys))
        finally:
            loop.close()

        logger.info(f"缓存预热完成: {len(keys)}个键")

        return jsonify({
            "success": True,
            "message": f"✅ 预热完成: {len(keys)}个键",
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "count": len(keys),
        })

    except Exception as e:
        logger.error(f"执行预热失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "执行预热失败"
        }), 500


# ============================================================================
# 降级管理API
# ============================================================================

@cache_bp.route('/api/cache/degradation/status', methods=['GET'])
def get_degradation_status():
    """
    获取降级状态

    Returns:
        {
            "success": true,
            "status": {...}
        }
    """
    try:
        from backend.core.cache.degradation import get_degradation_manager

        manager = get_degradation_manager()
        status = manager.get_status()

        return jsonify({
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "status": status,
        })

    except Exception as e:
        logger.error(f"获取降级状态失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "获取降级状态失败"
        }), 500


@cache_bp.route('/api/cache/degradation/switch', methods=['POST'])
def switch_degradation():
    """
    手动切换降级模式

    Request Body:
        {
            "degraded": true
        }

    Returns:
        {
            "success": true,
            "message": "降级模式已切换",
            "degraded": true
        }
    """
    try:
        from backend.core.cache.degradation import get_degradation_manager

        # Handle case where Content-Type is not set
        try:
            data = request.get_json() or {}
        except Exception:
            data = {}

        degraded = data.get('degraded', False)

        manager = get_degradation_manager()

        if degraded:
            manager.force_degrade()
            action = "降级"
        else:
            manager.force_recover()
            action = "恢复"

        logger.info(f"降级模式已切换: {action}")

        return jsonify({
            "success": True,
            "message": f"✅ 降级模式已切换: {action}",
            "timestamp": datetime.now().isoformat(),
            "degraded": manager.degraded,
        })

    except Exception as e:
        logger.error(f"切换降级模式失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "切换降级模式失败"
        }), 500


logger.info("✅ 缓存管理API路由已加载 (2.0.0)")
