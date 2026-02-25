"""
性能监控API路由
"""

import logging
from typing import Any, Dict, Tuple
from flask import request, Blueprint
from backend.core.utils import json_success_response, json_error_response
from backend.core.monitoring.performance_monitor import (
    PerformanceMonitor,
    PerformanceAlerts,
    performance_monitor
)

logger = logging.getLogger(__name__)

monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route("/api/monitoring/metrics", methods=["GET"])
def api_get_metrics() -> Tuple[Dict[str, Any], int]:
    """
    API: 获取性能指标
    
    Returns:
        性能指标数据
    """
    try:
        metrics = performance_monitor.get_all_metrics()
        return json_success_response(data=metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return json_error_response("Failed to get metrics", status_code=500)


@monitoring_bp.route("/api/monitoring/cache-stats", methods=["GET"])
def api_get_cache_stats() -> Tuple[Dict[str, Any], int]:
    """
    API: 获取缓存统计
    
    Returns:
        缓存统计数据
    """
    try:
        stats = {
            'cache_hit_ratio': performance_monitor.get_cache_hit_ratio(),
            'cache_hits': performance_monitor.metrics['cache_hits'],
            'cache_misses': performance_monitor.metrics['cache_misses']
        }
        return json_success_response(data=stats)
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return json_error_response("Failed to get cache stats", status_code=500)


@monitoring_bp.route("/api/monitoring/api-stats", methods=["GET"])
def api_get_api_stats() -> Tuple[Dict[str, Any], int]:
    """
    API: 获取API统计
    
    Query Parameters:
        endpoint: 特定API端点（可选）
    
    Returns:
        API统计数据
    """
    try:
        endpoint = request.args.get('endpoint')
        
        if endpoint:
            stats = performance_monitor.get_api_stats(endpoint)
        else:
            # 返回所有API的统计
            stats = {}
            for ep in performance_monitor.metrics['api_calls'].keys():
                stats[ep] = performance_monitor.get_api_stats(ep)
        
        return json_success_response(data=stats)
    except Exception as e:
        logger.error(f"Error getting API stats: {e}")
        return json_error_response("Failed to get API stats", status_code=500)


@monitoring_bp.route("/api/monitoring/alerts", methods=["GET"])
def api_get_alerts() -> Tuple[Dict[str, Any], int]:
    """
    API: 获取性能告警
    
    Returns:
        告警状态
    """
    try:
        alerts = PerformanceAlerts.check_all_alerts(performance_monitor)
        return json_success_response(data=alerts)
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return json_error_response("Failed to get alerts", status_code=500)


@monitoring_bp.route("/api/monitoring/reset", methods=["POST"])
def api_reset_metrics() -> Tuple[Dict[str, Any], int]:
    """
    API: 重置性能指标
    
    Returns:
        重置结果
    """
    try:
        performance_monitor.reset_metrics()
        logger.info("Performance metrics reset")
        return json_success_response(message="Metrics reset successfully")
    except Exception as e:
        logger.error(f"Error resetting metrics: {e}")
        return json_error_response("Failed to reset metrics", status_code=500)
