#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存监控和告警系统单元测试
===========================

测试覆盖:
- 指标采集功能
- 告警规则触发
- 持续时间验证
- 告警去重机制
- 指标趋势分析
- Prometheus指标导出

版本: 1.0.0
日期: 2026-02-24
"""

import pytest
import time
from unittest.mock import Mock, patch

from backend.core.cache.monitoring import (
    CacheAlertManager,
    AlertRule,
    AlertLevel,
    AlertEvent,
    MetricsHistory,
    MetricSnapshot,
    export_prometheus_metrics
)


@pytest.fixture
def mock_cache():
    """模拟三级缓存实例"""
    cache = Mock()
    cache.get_stats = Mock(return_value={
        "l1_size": 850,
        "l1_capacity": 1000,
        "l1_usage": "85.0%",
        "l1_hits": 500,
        "l2_hits": 200,
        "misses": 300,
        "hit_rate": "70.0%",
        "l1_evictions": 50,
        "total_requests": 1000
    })
    cache.l1_size = 1000
    return cache


@pytest.fixture
def alert_manager(mock_cache):
    """创建告警管理器实例"""
    return CacheAlertManager(mock_cache)


class TestMetricsHistory:
    """测试指标历史记录"""

    def test_add_snapshot(self):
        """测试添加快照"""
        history = MetricsHistory(max_size=10)
        snapshot = MetricSnapshot(
            timestamp=time.time(),
            l1_hit_rate=0.7,
            l2_hit_rate=0.2,
            overall_hit_rate=0.9,
            l1_usage=0.85,
            l2_memory_usage=0.5,
            qps=100.0,
            avg_response_time_ms=5.0
        )

        history.add(snapshot)

        assert len(history.history) == 1
        assert history.get_latest() == snapshot

    def test_max_size_enforcement(self):
        """测试最大容量限制"""
        history = MetricsHistory(max_size=5)

        # 添加6个快照
        for i in range(6):
            snapshot = MetricSnapshot(
                timestamp=time.time(),
                l1_hit_rate=float(i) / 10,
                l2_hit_rate=0.2,
                overall_hit_rate=0.9,
                l1_usage=0.5,
                l2_memory_usage=0.5,
                qps=100.0,
                avg_response_time_ms=5.0
            )
            history.add(snapshot)

        # 应该只保留最新的5个
        assert len(history.history) == 5

    def test_get_recent(self):
        """测试获取最近快照"""
        history = MetricsHistory(max_size=100)

        # 添加不同时间的快照
        now = time.time()
        old_snapshot = MetricSnapshot(
            timestamp=now - 200,  # 200秒前
            l1_hit_rate=0.5,
            l2_hit_rate=0.2,
            overall_hit_rate=0.7,
            l1_usage=0.5,
            l2_memory_usage=0.5,
            qps=100.0,
            avg_response_time_ms=5.0
        )
        recent_snapshot = MetricSnapshot(
            timestamp=now - 50,  # 50秒前
            l1_hit_rate=0.8,
            l2_hit_rate=0.3,
            overall_hit_rate=0.95,
            l1_usage=0.6,
            l2_memory_usage=0.5,
            qps=150.0,
            avg_response_time_ms=3.0
        )

        history.add(old_snapshot)
        history.add(recent_snapshot)

        # 获取最近100秒的快照
        recent = history.get_recent(100)

        assert len(recent) == 1
        assert recent[0].l1_hit_rate == 0.8

    def test_get_trend(self):
        """测试趋势计算"""
        history = MetricsHistory(max_size=100)

        # 添加上升趋势的快照
        now = time.time()
        for i in range(5):
            snapshot = MetricSnapshot(
                timestamp=now - (5 - i) * 10,  # 0, 10, 20, 30, 40秒前
                l1_hit_rate=0.5 + i * 0.1,  # 0.5, 0.6, 0.7, 0.8, 0.9
                l2_hit_rate=0.2,
                overall_hit_rate=0.9,
                l1_usage=0.5,
                l2_memory_usage=0.5,
                qps=100.0,
                avg_response_time_ms=5.0
            )
            history.add(snapshot)

        trend = history.get_trend("l1_hit_rate", duration_seconds=100)

        assert trend is not None
        assert trend["min"] == 0.5
        assert trend["max"] == 0.9
        assert trend["avg"] == 0.7
        assert trend["count"] == 5
        assert trend["trend"] == 0.4  # 上升趋势


class TestCacheAlertManager:
    """测试缓存告警管理器"""

    def test_initialization(self, alert_manager):
        """测试初始化"""
        assert alert_manager.cache is not None
        assert len(alert_manager.alert_rules) == 6  # 应该有6条告警规则
        assert alert_manager.metrics_history is not None

    def test_collect_metrics(self, alert_manager):
        """测试指标采集"""
        snapshot = alert_manager.collect_metrics()

        assert isinstance(snapshot, MetricSnapshot)
        assert 0 <= snapshot.l1_hit_rate <= 1
        assert 0 <= snapshot.l1_usage <= 1
        assert snapshot.qps >= 0
        assert snapshot.avg_response_time_ms >= 0

    def test_record_request(self, alert_manager):
        """测试请求记录"""
        # 记录一些请求
        for _ in range(10):
            alert_manager.record_request(5.0)

        # 采集指标应该计算QPS
        snapshot = alert_manager.collect_metrics()

        assert snapshot.qps > 0
        assert snapshot.avg_response_time_ms == 5.0

    def test_alert_rule_l1_hit_rate_low(self, alert_manager):
        """测试L1命中率低告警"""
        # 模拟低命中率
        with patch.object(alert_manager.cache, 'get_stats', return_value={
            "l1_size": 500,
            "l1_capacity": 1000,
            "l1_usage": "50.0%",
            "hit_rate": "50.0%",  # 低于60%阈值
            "l1_hits": 50,  # L1命中50次
            "l2_hits": 0,   # L2命中0次
            "misses": 50,   # 未命中50次
            "l1_evictions": 0,
            "total_requests": 100  # 总请求100次
        }):
            # Mock _check_duration返回足够的时间
            with patch.object(alert_manager, '_check_duration', return_value=301):
                alerts = alert_manager.check_alerts()

                # 应该触发WARNING告警
                l1_alerts = [a for a in alerts if a.metric == "l1_hit_rate"]
                assert len(l1_alerts) > 0

    def test_alert_rule_l1_capacity_critical(self, alert_manager):
        """测试L1容量严重告警"""
        # 模拟L1容量超过95%
        with patch.object(alert_manager.cache, 'get_stats', return_value={
            "l1_size": 960,
            "l1_capacity": 1000,
            "l1_usage": "96.0%",  # 超过95%阈值
            "hit_rate": "70.0%",
            "l1_hits": 700,
            "l2_hits": 200,
            "misses": 100,
            "l1_evictions": 50,
            "total_requests": 1000
        }):
            # Mock _check_duration返回足够的时间
            with patch.object(alert_manager, '_check_duration', return_value=31):
                alerts = alert_manager.check_alerts()

                # 应该触发CRITICAL告警（使用"usage"而不是"capacity"）
                usage_alerts = [a for a in alerts if "usage" in a.metric]
                assert len(usage_alerts) > 0

    def test_alert_deduplication(self, alert_manager):
        """测试告警去重"""
        # 第一次触发告警
        with patch.object(alert_manager.cache, 'get_stats', return_value={
            "l1_size": 960,
            "l1_capacity": 1000,
            "l1_usage": "96.0%",
            "hit_rate": "50.0%",
            "l1_hits": 50,
            "l2_hits": 0,
            "misses": 50,
            "l1_evictions": 0,
            "total_requests": 100
        }):
            # Mock _check_duration返回足够的时间
            with patch.object(alert_manager, '_check_duration', return_value=31):
                alerts_first = alert_manager.check_alerts()
                assert len(alerts_first) > 0

                # 立即再次检查，不应该重复触发
                alerts_second = alert_manager.check_alerts()
                # 由于去重机制，第二次应该没有新告警
                assert len(alerts_second) == 0

    def test_alert_resolution(self, alert_manager):
        """测试告警解除"""
        # 先触发告警
        with patch.object(alert_manager.cache, 'get_stats', return_value={
            "l1_size": 960,
            "l1_capacity": 1000,
            "l1_usage": "96.0%",
            "hit_rate": "50.0%",
            "l1_hits": 50,
            "l2_hits": 0,
            "misses": 50,
            "l1_evictions": 0,
            "total_requests": 100
        }):
            # Mock _check_duration返回足够的时间
            with patch.object(alert_manager, '_check_duration', return_value=31):
                alerts = alert_manager.check_alerts()
                assert len(alerts) > 0

        # 恢复正常
        with patch.object(alert_manager.cache, 'get_stats', return_value={
            "l1_size": 500,
            "l1_capacity": 1000,
            "l1_usage": "50.0%",
            "hit_rate": "80.0%",
            "l1_hits": 800,
            "l2_hits": 150,
            "misses": 50,
            "l1_evictions": 0,
            "total_requests": 1000
        }):
            alert_manager.collect_metrics()
            alerts = alert_manager.check_alerts()

            # 活跃告警应该被清除
            active_alerts = alert_manager.get_active_alerts()
            # 告警应该被标记为已解决
            assert len([a for a in alert_manager.alert_history if a.resolved]) > 0

    def test_get_active_alerts(self, alert_manager):
        """测试获取活跃告警"""
        active = alert_manager.get_active_alerts()
        assert isinstance(active, list)

    def test_get_alert_history(self, alert_manager):
        """测试获取告警历史"""
        history = alert_manager.get_alert_history(limit=10)
        assert isinstance(history, list)

    def test_get_metrics_summary(self, alert_manager):
        """测试获取指标摘要"""
        alert_manager.collect_metrics()
        summary = alert_manager.get_metrics_summary()

        assert isinstance(summary, dict)
        assert "timestamp" in summary
        assert "l1_hit_rate" in summary
        assert "trends" in summary

    def test_reset(self, alert_manager):
        """测试重置"""
        # 添加一些告警
        with patch.object(alert_manager.cache, 'get_stats', return_value={
            "l1_size": 960,
            "l1_capacity": 1000,
            "l1_usage": "96.0%",
            "hit_rate": "50.0%",
            "l1_hits": 50,
            "l2_hits": 0,
            "misses": 50,
            "l1_evictions": 0,
            "total_requests": 100
        }):
            for _ in range(30):
                alert_manager.collect_metrics()
                time.sleep(0.01)

            alert_manager.check_alerts()

        # 重置
        alert_manager.reset()

        # 活跃告警应该被清除
        assert len(alert_manager.get_active_alerts()) == 0


class TestAlertEvent:
    """测试告警事件"""

    def test_to_dict(self):
        """测试转换为字典"""
        event = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING,
            duration=300
        )

        event_dict = event.to_dict()

        assert event_dict["rule_name"] == "test_rule"
        assert event_dict["metric"] == "l1_hit_rate"
        assert "50.00%" in event_dict["current_value"]
        assert event_dict["level"] == "WARNING"


class TestPrometheusExport:
    """测试Prometheus指标导出"""

    def test_export_prometheus_metrics(self, alert_manager):
        """测试Prometheus指标导出"""
        alert_manager.collect_metrics()

        metrics = export_prometheus_metrics(alert_manager)

        assert isinstance(metrics, str)
        assert "cache_hit_rate" in metrics
        assert "cache_l1_usage" in metrics
        assert "cache_l1_capacity" in metrics
        assert "cache_alerts" in metrics

    def test_prometheus_metrics_format(self, alert_manager):
        """测试Prometheus指标格式"""
        alert_manager.collect_metrics()

        metrics = export_prometheus_metrics(alert_manager)
        lines = metrics.split("\n")

        # 每行应该符合Prometheus格式
        for line in lines:
            if line.strip():
                # 格式: metric_name{labels} value
                assert "{" in line or " " in line


class TestAlertRule:
    """测试告警规则"""

    def test_alert_rule_creation(self):
        """测试告警规则创建"""
        rule = AlertRule(
            name="test_rule",
            metric="l1_hit_rate",
            threshold=0.6,
            duration=300,
            level=AlertLevel.WARNING,
            description="Test rule"
        )

        assert rule.name == "test_rule"
        assert rule.metric == "l1_hit_rate"
        assert rule.threshold == 0.6
        assert rule.duration == 300
        assert rule.level == AlertLevel.WARNING

    def test_alert_rule_str(self):
        """测试告警规则的字符串表示"""
        rule = AlertRule(
            name="test_rule",
            metric="l1_hit_rate",
            threshold=0.6,
            duration=300,
            level=AlertLevel.WARNING
        )

        str_repr = str(rule)
        assert "AlertRule" in str_repr
        assert "test_rule" in str_repr


class TestAlertEventDetails:
    """测试告警事件详细信息"""

    def test_alert_event_timestamp(self):
        """测试告警事件时间戳"""
        before_time = time.time()
        event = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING
        )
        after_time = time.time()

        assert before_time <= event.timestamp <= after_time

    def test_alert_event_resolved(self):
        """测试告警事件解决状态"""
        event = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING
        )

        assert event.resolved is False

        event.resolved = True
        assert event.resolved is True

    def test_alert_event_to_dict_non_rate_metric(self):
        """测试非百分比指标转换为字典"""
        event = AlertEvent(
            rule_name="test_rule",
            metric="qps",
            current_value=100.5,
            threshold=200.0,
            level=AlertLevel.WARNING
        )

        event_dict = event.to_dict()

        assert event_dict["current_value"] == "100.50"
        assert event_dict["threshold"] == "200.00"


class TestMetricsHistoryDetails:
    """测试指标历史详细功能"""

    def test_get_latest_empty(self):
        """测试空历史的get_latest"""
        history = MetricsHistory(max_size=10)
        assert history.get_latest() is None

    def test_get_trend_empty(self):
        """测试空历史的get_trend"""
        history = MetricsHistory(max_size=10)
        assert history.get_trend("l1_hit_rate") is None

    def test_get_trend_no_snapshots_in_range(self):
        """测试时间范围内无快照"""
        history = MetricsHistory(max_size=10)
        now = time.time()

        # 添加旧快照（超过时间范围）
        old_snapshot = MetricSnapshot(
            timestamp=now - 500,
            l1_hit_rate=0.5,
            l2_hit_rate=0.2,
            overall_hit_rate=0.7,
            l1_usage=0.5,
            l2_memory_usage=0.5,
            qps=100.0,
            avg_response_time_ms=5.0
        )
        history.add(old_snapshot)

        # 获取最近100秒的快照（应该为空）
        recent = history.get_recent(100)
        assert len(recent) == 0

    def test_get_trend_with_no_matching_attribute(self, alert_manager):
        """测试获取不存在属性的趋势"""
        # 添加快照
        now = time.time()
        for i in range(5):
            snapshot = MetricSnapshot(
                timestamp=now - i * 10,
                l1_hit_rate=0.8,
                l2_hit_rate=0.2,
                overall_hit_rate=0.9,
                l1_usage=0.5,
                l2_memory_usage=0.5,
                qps=100.0,
                avg_response_time_ms=5.0
            )
            alert_manager.metrics_history.add(snapshot)

        # 尝试获取不存在的指标趋势 - 应该抛出AttributeError
        with pytest.raises(AttributeError):
            alert_manager.metrics_history.get_trend("nonexistent_metric")

    def test_get_trend_with_empty_values_list(self):
        """测试get_trend处理空值列表"""
        history = MetricsHistory(max_size=10)

        # 创建一个属性存在但值为None的快照（通过getattr处理）
        # 这在实际中不太可能，但可以测试代码的健壮性
        snapshot = MetricSnapshot(
            timestamp=time.time(),
            l1_hit_rate=0.8,
            l2_hit_rate=0.2,
            overall_hit_rate=0.9,
            l1_usage=0.5,
            l2_memory_usage=0.5,
            qps=100.0,
            avg_response_time_ms=5.0
        )
        history.add(snapshot)

        # 获取趋势应该正常工作
        trend = history.get_trend("l1_hit_rate")
        assert trend is not None
        assert trend["count"] == 1


class TestCacheAlertManagerDetails:
    """测试缓存告警管理器详细功能"""

    def test_collect_metrics_with_zero_requests(self, alert_manager):
        """测试零请求情况下的指标采集"""
        # Mock返回零请求
        alert_manager.cache.get_stats.return_value = {
            "l1_size": 500,
            "l1_capacity": 1000,
            "l1_usage": "50.0%",
            "hit_rate": "0.0%",
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "l1_evictions": 0,
            "total_requests": 0
        }

        snapshot = alert_manager.collect_metrics()

        # 应该不抛出异常
        assert snapshot.l1_hit_rate == 0
        assert snapshot.l2_hit_rate == 0
        assert snapshot.overall_hit_rate == 0

    def test_collect_metrics_parse_usage_percentage(self, alert_manager):
        """测试解析使用率百分比"""
        alert_manager.cache.get_stats.return_value = {
            "l1_size": 750,
            "l1_capacity": 1000,
            "l1_usage": "75.5%",  # 带小数
            "hit_rate": "70.0%",
            "l1_hits": 700,
            "l2_hits": 200,
            "misses": 100,
            "l1_evictions": 0,
            "total_requests": 1000
        }

        snapshot = alert_manager.collect_metrics()

        assert snapshot.l1_usage == 0.755

    def test_collect_metrics_numeric_usage(self, alert_manager):
        """测试数值类型的使用率"""
        alert_manager.cache.get_stats.return_value = {
            "l1_size": 750,
            "l1_capacity": 1000,
            "l1_usage": 0.75,  # 数值类型
            "hit_rate": "70.0%",
            "l1_hits": 700,
            "l2_hits": 200,
            "misses": 100,
            "l1_evictions": 0,
            "total_requests": 1000
        }

        snapshot = alert_manager.collect_metrics()

        assert snapshot.l1_usage == 0.75

    def test_should_trigger_alert_no_existing(self, alert_manager):
        """测试无活跃告警时应该触发"""
        alert_event = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING
        )

        result = alert_manager._should_trigger_alert(alert_event)
        assert result is True

    def test_should_trigger_alert_different_level(self, alert_manager):
        """测试不同级别告警应该触发"""
        # 添加WARNING级别告警
        existing_alert = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING,
            timestamp=time.time()
        )
        alert_manager.active_alerts["test_rule"] = existing_alert

        # 创建CRITICAL级别告警
        new_alert = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.3,
            threshold=0.4,
            level=AlertLevel.CRITICAL
        )

        result = alert_manager._should_trigger_alert(new_alert)
        # 级别不同，应该触发
        assert result is True

    def test_should_trigger_alert_timeout(self, alert_manager):
        """测试超时后应该重新触发"""
        # 添加旧告警（超过1分钟）
        old_alert = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING,
            timestamp=time.time() - 61
        )
        alert_manager.active_alerts["test_rule"] = old_alert

        # 创建新告警
        new_alert = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING
        )

        result = alert_manager._should_trigger_alert(new_alert)
        # 超过1分钟，应该重新触发
        assert result is True

    def test_log_alert_warning(self, alert_manager):
        """测试WARNING级别日志"""
        alert = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING,
            duration=300
        )

        rule = AlertRule(
            name="test_rule",
            metric="l1_hit_rate",
            threshold=0.6,
            duration=300,
            level=AlertLevel.WARNING,
            description="Test warning"
        )

        # 只测试不抛出异常
        alert_manager._log_alert(alert, rule)

    def test_log_alert_critical(self, alert_manager):
        """测试CRITICAL级别日志"""
        alert = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.3,
            threshold=0.4,
            level=AlertLevel.CRITICAL,
            duration=180
        )

        rule = AlertRule(
            name="test_rule",
            metric="l1_hit_rate",
            threshold=0.4,
            duration=180,
            level=AlertLevel.CRITICAL,
            description="Test critical"
        )

        # 只测试不抛出异常
        alert_manager._log_alert(alert, rule)

    def test_auto_expand_l1(self, alert_manager):
        """测试自动扩容L1"""
        initial_size = alert_manager.cache.l1_size

        alert_manager._auto_expand_l1()

        # 应该扩容50%
        assert alert_manager.cache.l1_size == int(initial_size * 1.5)

    def test_auto_expand_l1_failure(self, alert_manager):
        """测试L1扩容失败"""
        # Mock cache抛出异常
        alert_manager.cache.l1_size = None

        # 应该不抛出异常，只记录错误
        alert_manager._auto_expand_l1()

    def test_alert_action_failure(self, alert_manager):
        """测试告警动作执行失败"""
        # 创建一个会抛出异常的动作
        def failing_action():
            raise RuntimeError("Action failed")

        # 添加带失败动作的规则
        rule = AlertRule(
            name="test_failing_rule",
            metric="l1_hit_rate",
            threshold=0.6,
            duration=300,
            level=AlertLevel.WARNING,
            action=failing_action,
            description="Test failing action"
        )

        # Mock _check_duration返回足够的时间
        with patch.object(alert_manager, '_check_duration', return_value=301):
            with patch.object(alert_manager.cache, 'get_stats', return_value={
                "l1_size": 500,
                "l1_capacity": 1000,
                "l1_usage": "50.0%",
                "hit_rate": "50.0%",
                "l1_hits": 50,
                "l2_hits": 0,
                "misses": 50,
                "l1_evictions": 0,
                "total_requests": 100
            }):
                # 添加临时规则
                original_rules = alert_manager.alert_rules
                alert_manager.alert_rules = [rule]

                # 应该不抛出异常
                alerts = alert_manager.check_alerts()

                # 恢复原始规则
                alert_manager.alert_rules = original_rules

    def test_trigger_warm_up(self, alert_manager):
        """测试触发预热"""
        # 只测试不抛出异常
        alert_manager._trigger_warm_up()

    def test_get_metrics_summary_empty_history(self, alert_manager):
        """测试空历史的指标摘要"""
        # 清空历史
        alert_manager.metrics_history.history.clear()

        summary = alert_manager.get_metrics_summary()

        # 应该返回空字典
        assert summary == {}

    def test_check_duration_no_anomaly(self, alert_manager):
        """测试无异常时的持续时间"""
        # 添加正常快照
        now = time.time()
        for i in range(10):
            snapshot = MetricSnapshot(
                timestamp=now - i * 10,
                l1_hit_rate=0.8,  # 高于阈值
                l2_hit_rate=0.2,
                overall_hit_rate=0.9,
                l1_usage=0.5,
                l2_memory_usage=0.5,
                qps=100.0,
                avg_response_time_ms=5.0
            )
            alert_manager.metrics_history.add(snapshot)

        rule = AlertRule(
            name="test_rule",
            metric="l1_hit_rate",
            threshold=0.6,
            duration=300,
            level=AlertLevel.WARNING
        )

        duration = alert_manager._check_duration(rule, 0.8)

        # 应该返回0
        assert duration == 0

    def test_get_alert_history_limit(self, alert_manager):
        """测试告警历史数量限制"""
        # 添加20个告警
        for i in range(20):
            alert = AlertEvent(
                rule_name=f"rule_{i}",
                metric="l1_hit_rate",
                current_value=0.5,
                threshold=0.6,
                level=AlertLevel.WARNING
            )
            alert_manager.alert_history.append(alert)

        history = alert_manager.get_alert_history(limit=10)

        # 应该只返回10个
        assert len(history) == 10


class TestGlobalAlertManager:
    """测试全局告警管理器"""

    def test_get_cache_alert_manager_requires_cache_on_first_call(self):
        """测试首次调用需要cache参数"""
        from backend.core.cache.monitoring import get_cache_alert_manager

        # 重置全局实例
        import backend.core.cache.monitoring as monitoring_module
        monitoring_module._global_alert_manager = None

        with pytest.raises(ValueError, match="hierarchical_cache is required"):
            get_cache_alert_manager()

    def test_get_cache_alert_manager_creates_instance(self):
        """测试创建全局实例"""
        from backend.core.cache.monitoring import get_cache_alert_manager

        # 重置全局实例
        import backend.core.cache.monitoring as monitoring_module
        monitoring_module._global_alert_manager = None

        mock_cache = Mock()
        mock_cache.get_stats.return_value = {
            "l1_size": 500,
            "l1_capacity": 1000,
            "l1_usage": "50.0%",
            "hit_rate": "70.0%",
            "l1_hits": 700,
            "l2_hits": 200,
            "misses": 100,
            "l1_evictions": 0,
            "total_requests": 1000
        }
        mock_cache.l1_size = 1000

        manager = get_cache_alert_manager(mock_cache)

        assert manager is not None
        assert isinstance(manager, CacheAlertManager)

    def test_get_cache_alert_manager_returns_same_instance(self):
        """测试返回相同实例"""
        from backend.core.cache.monitoring import get_cache_alert_manager

        # 重置全局实例
        import backend.core.cache.monitoring as monitoring_module
        monitoring_module._global_alert_manager = None

        mock_cache = Mock()
        mock_cache.get_stats.return_value = {
            "l1_size": 500,
            "l1_capacity": 1000,
            "l1_usage": "50.0%",
            "hit_rate": "70.0%",
            "l1_hits": 700,
            "l2_hits": 200,
            "misses": 100,
            "l1_evictions": 0,
            "total_requests": 1000
        }
        mock_cache.l1_size = 1000

        manager1 = get_cache_alert_manager(mock_cache)
        manager2 = get_cache_alert_manager()

        assert manager1 is manager2


class TestPrometheusExportDetails:
    """测试Prometheus导出详细功能"""

    def test_export_prometheus_metrics_with_alerts(self, alert_manager):
        """测试带告警的Prometheus导出"""
        # 添加告警
        alert = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.5,
            threshold=0.6,
            level=AlertLevel.WARNING
        )
        alert_manager.active_alerts["test_rule"] = alert

        alert_manager.collect_metrics()

        metrics = export_prometheus_metrics(alert_manager)

        assert "cache_alerts" in metrics
        assert "warning" in metrics

    def test_export_prometheus_metrics_critical_alerts(self, alert_manager):
        """测试CRITICAL级别告警的Prometheus导出"""
        # 添加CRITICAL告警
        alert = AlertEvent(
            rule_name="test_rule",
            metric="l1_hit_rate",
            current_value=0.3,
            threshold=0.4,
            level=AlertLevel.CRITICAL
        )
        alert_manager.active_alerts["test_rule"] = alert

        alert_manager.collect_metrics()

        metrics = export_prometheus_metrics(alert_manager)

        assert "critical" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
