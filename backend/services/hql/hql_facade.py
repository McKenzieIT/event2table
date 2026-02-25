"""
HQL服务门面类

提供统一的HQL生成、验证接口
简化API层对HQL服务的使用
"""

from typing import List, Dict, Any, Optional
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.validators.performance_analyzer import (
    HQLPerformanceAnalyzer,
    PerformanceReport,
)
from backend.services.hql.validators.syntax_validator import SyntaxValidator


class HQLFacade:
    """
    HQL服务门面

    提供统一的HQL生成、验证接口，封装底层实现细节
    """

    def __init__(self):
        self.generator = HQLGenerator()
        self.performance_analyzer = HQLPerformanceAnalyzer()
        self.syntax_validator = SyntaxValidator()

    def generate_hql(
        self,
        events: List[Dict[str, Any]],
        fields: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]],
        mode: str = "single",
    ) -> str:
        """
        生成HQL

        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            mode: 生成模式 (single/join/union)

        Returns:
            str: 生成的HQL语句
        """
        from backend.services.hql.models.event import Event, Field, Condition

        validated_events = [self._dict_to_event(e) for e in events]
        validated_fields = [self._dict_to_field(f) for f in fields]
        validated_conditions = [self._dict_to_condition(c) for c in conditions]

        hql = self.generator.generate(
            events=validated_events,
            fields=validated_fields,
            conditions=validated_conditions,
            mode=mode,
        )

        return hql

    def _dict_to_event(self, data: Dict[str, Any]):
        """将字典转换为Event对象"""
        from backend.services.hql.models.event import Event

        return Event(
            name=data.get("name", ""),
            table_name=data.get("table_name", ""),
            alias=data.get("alias"),
        )

    def _dict_to_field(self, data: Dict[str, Any]):
        """将字典转换为Field对象"""
        from backend.services.hql.models.event import Field

        return Field(
            name=data.get("name", ""),
            type=data.get("type", "base"),
            json_path=data.get("json_path"),
            alias=data.get("alias"),
            aggregate_func=data.get("aggregate_func"),
        )

    def _dict_to_condition(self, data: Dict[str, Any]):
        """将字典转换为Condition对象"""
        from backend.services.hql.models.event import Condition

        return Condition(
            field=data.get("field", ""),
            operator=data.get("operator", "="),
            value=data.get("value", ""),
            logic=data.get("logic", "AND"),
        )

    def validate_hql(self, hql: str) -> Dict[str, Any]:
        """
        验证HQL

        Args:
            hql: HQL语句

        Returns:
            Dict: 验证结果
        """
        syntax_result = self.syntax_validator.validate(hql)
        performance_result = self.performance_analyzer.analyze(hql)

        return {
            "valid": syntax_result.is_valid,
            "syntax_errors": syntax_result.errors if not syntax_result.is_valid else [],
            "performance": {
                "score": performance_result.score,
                "issues": [
                    {
                        "type": issue.type.value,
                        "message": issue.message,
                        "suggestion": issue.suggestion,
                    }
                    for issue in performance_result.issues
                ],
                "metrics": {
                    "has_partition_filter": performance_result.metrics.has_partition_filter,
                    "has_select_star": performance_result.metrics.has_select_star,
                    "join_count": performance_result.metrics.join_count,
                    "complexity": performance_result.metrics.complexity,
                },
            },
        }

    def preview_hql(
        self,
        events: List[Dict[str, Any]],
        fields: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]],
        mode: str = "single",
    ) -> Dict[str, Any]:
        """
        预览HQL（带验证）

        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            mode: 生成模式

        Returns:
            Dict: 包含HQL和验证结果的字典
        """
        try:
            hql = self.generate_hql(events, fields, conditions, mode)
            validation = self.validate_hql(hql)
            return {"success": True, "hql": hql, "validation": validation}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_performance(self, hql: str) -> PerformanceReport:
        """
        分析HQL性能

        Args:
            hql: HQL语句

        Returns:
            PerformanceReport: 性能报告
        """
        return self.performance_analyzer.analyze(hql)

    def validate_syntax(self, hql: str) -> Dict[str, Any]:
        """
        验证HQL语法

        Args:
            hql: HQL语句

        Returns:
            Dict: 语法验证结果
        """
        result = self.syntax_validator.validate(hql)
        return {
            "valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
        }
