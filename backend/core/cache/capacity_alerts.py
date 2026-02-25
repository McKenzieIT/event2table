#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
容量监控和告警
==============

提供缓存容量监控和告警功能

作者: Event2Table Development Team
版本: 1.0.0
日期: 2026-02-25
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CapacityAlertManager:
    """容量告警管理器"""

    # 告警阈值
    ALERT_THRESHOLDS = {
        'l1_memory_usage': 0.9,      # L1内存使用率 > 90%
        'l2_memory_usage': 0.9,      # L2内存使用率 > 90%
        'hit_rate_low': 0.7,          # 命中率 < 70%
        'eviction_rate_high': 100,    # 驱逐速率 > 100/分钟
    }

    def __init__(self):
        self._alerts = []
        self._alert_history = []

    def check_capacity_alerts(self, cache_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检查容量告警

        Args:
            cache_stats: 缓存统计信息

        Returns:
            告警列表
        """
        alerts = []

        # 检查L1内存使用率
        if 'l1_memory_usage' in cache_stats:
            l1_usage = cache_stats['l1_memory_usage']
            if l1_usage > self.ALERT_THRESHOLDS['l1_memory_usage']:
                alerts.append({
                    'type': 'l1_memory_high',
                    'severity': 'warning',
                    'message': f'L1 memory usage above {l1_usage*100:.1f}%',
                    'threshold': self.ALERT_THRESHOLDS['l1_memory_usage'],
                    'current_value': l1_usage,
                    'timestamp': datetime.now().isoformat()
                })

        # 检查L2内存使用率
        if 'l2_memory_usage' in cache_stats:
            l2_usage = cache_stats['l2_memory_usage']
            if l2_usage > self.ALERT_THRESHOLDS['l2_memory_usage']:
                alerts.append({
                    'type': 'l2_memory_high',
                    'severity': 'warning',
                    'message': f'L2 memory usage above {l2_usage*100:.1f}%',
                    'threshold': self.ALERT_THRESHOLDS['l2_memory_usage'],
                    'current_value': l2_usage,
                    'timestamp': datetime.now().isoformat()
                })

        # 检查命中率
        if 'hit_rate' in cache_stats:
            hit_rate = cache_stats['hit_rate']
            if hit_rate < self.ALERT_THRESHOLDS['hit_rate_low']:
                alerts.append({
                    'type': 'hit_rate_low',
                    'severity': 'warning',
                    'message': f'Cache hit rate below {hit_rate*100:.1f}%',
                    'threshold': self.ALERT_THRESHOLDS['hit_rate_low'],
                    'current_value': hit_rate,
                    'timestamp': datetime.now().isoformat()
                })

        # 检查驱逐速率
        if 'eviction_rate' in cache_stats:
            eviction_rate = cache_stats['eviction_rate']
            if eviction_rate > self.ALERT_THRESHOLDS['eviction_rate_high']:
                alerts.append({
                    'type': 'eviction_rate_high',
                    'severity': 'critical',
                    'message': f'Cache eviction rate above {eviction_rate}/min',
                    'threshold': self.ALERT_THRESHOLDS['eviction_rate_high'],
                    'current_value': eviction_rate,
                    'timestamp': datetime.now().isoformat()
                })

        # 保存告警历史
        for alert in alerts:
            self._alert_history.append(alert)

        self._alerts = alerts
        return alerts

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """获取当前活动告警"""
        return self._alerts

    def get_alert_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取告警历史

        Args:
            limit: 返回的告警数量限制

        Returns:
            告警历史列表
        """
        return self._alert_history[-limit:]

    def clear_alerts(self):
        """清除所有告警"""
        self._alerts = []

    def get_summary(self) -> Dict[str, Any]:
        """
        获取告警摘要

        Returns:
            告警摘要
        """
        active_count = len(self._alerts)
        history_count = len(self._alert_history)

        # 按严重程度分类
        critical_count = sum(1 for a in self._alerts if a.get('severity') == 'critical')
        warning_count = sum(1 for a in self._alerts if a.get('severity') == 'warning')

        return {
            'active_alerts': active_count,
            'critical_alerts': critical_count,
            'warning_alerts': warning_count,
            'total_history': history_count,
            'last_alert_time': self._alert_history[-1]['timestamp'] if self._alert_history else None
        }


# 全局告警管理器实例
_alert_manager = CapacityAlertManager()


def get_alert_manager() -> CapacityAlertManager:
    """获取告警管理器实例"""
    return _alert_manager


def setup_alert_monitoring(app):
    """
    设置告警监控

    Args:
        app: Flask应用实例

    Returns:
        告警管理器
    """
    manager = get_alert_manager()

    # 注册告警检查路由
    from flask import jsonify

    @app.route('/api/cache/alerts/active')
    def get_active_alerts():
        """获取活动告警"""
        alerts = manager.get_active_alerts()
        return jsonify({
            'alerts': alerts,
            'count': len(alerts),
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/api/cache/alerts/history')
    def get_alert_history():
        """获取告警历史"""
        limit = int(request.args.get('limit', 100))
        history = manager.get_alert_history(limit=limit)
        return jsonify({
            'alerts': history,
            'count': len(history)
        })

    @app.route('/api/cache/alerts/summary')
    def get_alert_summary():
        """获取告警摘要"""
        summary = manager.get_summary()
        return jsonify(summary)

    @app.route('/api/cache/alerts/clear', methods=['POST'])
    def clear_alerts():
        """清除告警"""
        manager.clear_alerts()
        return jsonify({'message': 'Alerts cleared'})

    logger.info("✅ Cache alert monitoring endpoints registered")

    return manager
