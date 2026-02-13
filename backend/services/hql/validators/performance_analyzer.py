"""
HQL性能分析器

基于规则引擎的性能分析工具
提供HQL性能评分和优化建议
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class IssueType(Enum):
    """问题类型"""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class PerformanceIssue:
    """性能问题"""

    type: IssueType
    message: str
    suggestion: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """性能指标"""

    has_partition_filter: bool
    has_select_star: bool
    join_count: int
    cross_join_count: int
    subquery_count: int
    udf_count: int
    complexity: str  # low/medium/high


@dataclass
class PerformanceReport:
    """性能报告"""

    score: int  # 0-100
    issues: List[PerformanceIssue]
    metrics: PerformanceMetrics


class HQLPerformanceAnalyzer:
    """
    HQL性能分析器

    使用规则引擎分析HQL性能
    """

    # 评分规则
    SCORING_RULES = {
        "partition_filter_missing": -50,
        "select_star": -30,
        "cross_join": -40,
        "multiple_joins": -10,  # per join over 3
        "subquery": -15,
        "udf": -20,
        "complexity_high": -20,
        "complexity_medium": -10,
    }

    # 复杂度阈值
    COMPLEXITY_THRESHOLDS = {
        "low": 10,  # <= 10 tokens
        "medium": 50,  # 11-50 tokens
        "high": 1000,  # > 50 tokens
    }

    def __init__(self):
        """初始化分析器"""
        self.issues = []
        self.score = 100  # 从100分开始

    def analyze(self, hql: str) -> PerformanceReport:
        """
        分析HQL性能

        Args:
            hql: HQL语句

        Returns:
            PerformanceReport: 性能报告
        """
        self.issues = []
        self.score = 100

        # 提取指标
        metrics = self._extract_metrics(hql)

        # 应用规则
        self._apply_partition_filter_rule(metrics)
        self._apply_select_star_rule(metrics)
        self._apply_join_rules(metrics)
        self._apply_complexity_rule(hql, metrics)
        self._apply_subquery_rule(metrics)
        self._apply_udf_rule(metrics)

        # 确保分数在0-100范围内
        self.score = max(0, min(100, self.score))

        return PerformanceReport(score=self.score, issues=self.issues, metrics=metrics)

    def _extract_metrics(self, hql: str) -> PerformanceMetrics:
        """提取HQL指标"""
        import re

        hql_upper = hql.upper()

        # 检查分区过滤（改进检测逻辑）
        has_partition_filter = "DS" in hql_upper and (
            "= ${DS}" in hql_upper
            or "= '${DS}'" in hql_upper
            or "=${DS}" in hql_upper
            or "='${DS}'" in hql_upper
            or "= ${DS}" in hql_upper
            or "= '${DS}" in hql_upper
            or " DS = " in hql_upper
            or " DS=" in hql_upper
        )

        # 检查SELECT *（改进检测）
        has_select_star = (
            "SELECT *" in hql_upper
            or "SELECT\n*" in hql_upper
            or "SELECT\t*" in hql_upper
            or "SELECT\r\n*" in hql_upper
        )

        # 计数JOIN
        join_count = hql_upper.count(" JOIN ")
        cross_join_count = hql_upper.count(" CROSS JOIN ")

        # 计数子查询
        subquery_count = hql_upper.count("(SELECT")

        # 计数UDF (自定义函数) - 改进检测
        standard_functions = {
            "COUNT",
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "DISTINCT",
            "CAST",
            "COALESCE",
            "NULLIF",
            "NVL",
            "IF",
            "CASE",
            "GET_JSON_OBJECT",
            "JSON_TUPLE",
            "CONCAT",
            "SUBSTR",
            "SUBSTRING",
            "LENGTH",
            "UPPER",
            "LOWER",
            "TRIM",
            "LTRIM",
            "RTRIM",
            "FROM",
            "WHERE",
            "AND",
            "OR",
            "NOT",
            "IN",
            "LIKE",
            "IS",
            "NULL",
            "BETWEEN",
            "EXISTS",
            "ORDER",
            "GROUP",
            "HAVING",
            "LIMIT",
            "OFFSET",
            "JOIN",
            "LEFT",
            "RIGHT",
            "INNER",
            "OUTER",
            "ON",
            "AS",
            "BY",
            "ASC",
            "DESC",
            "UNION",
            "ALL",
            "SELECT",
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "DROP",
            "ALTER",
            "TABLE",
            "VIEW",
        }
        udf_count = 0
        # 只检测函数调用模式（word followed by parenthesis）
        function_pattern = r"\b([A-Z_][A-Z0-9_]*)\s*\("
        for match in re.finditer(function_pattern, hql_upper):
            func_name = match.group(1)
            if func_name not in standard_functions:
                udf_count += 1

        # 计算复杂度
        complexity = self._calculate_complexity(hql)

        return PerformanceMetrics(
            has_partition_filter=has_partition_filter,
            has_select_star=has_select_star,
            join_count=join_count,
            cross_join_count=cross_join_count,
            subquery_count=subquery_count,
            udf_count=udf_count,
            complexity=complexity,
        )

    def _calculate_complexity(self, hql: str) -> str:
        """计算SQL复杂度"""
        # 简化版本：基于SQL语句长度
        tokens = len(hql.split())

        if tokens <= self.COMPLEXITY_THRESHOLDS["low"]:
            return "low"
        elif tokens <= self.COMPLEXITY_THRESHOLDS["medium"]:
            return "medium"
        else:
            return "high"

    def _apply_partition_filter_rule(self, metrics: PerformanceMetrics):
        """应用分区过滤规则"""
        if not metrics.has_partition_filter:
            self.score += self.SCORING_RULES["partition_filter_missing"]
            self.issues.append(
                PerformanceIssue(
                    type=IssueType.ERROR,
                    message="Missing partition filter (ds = '${ds}')",
                    suggestion="Always include partition filter to avoid full table scan. "
                    + "Add 'ds = '${ds}'' to WHERE clause.",
                )
            )

    def _apply_select_star_rule(self, metrics: PerformanceMetrics):
        """应用SELECT *规则"""
        if metrics.has_select_star:
            self.score += self.SCORING_RULES["select_star"]
            self.issues.append(
                PerformanceIssue(
                    type=IssueType.WARNING,
                    message="SELECT * detected",
                    suggestion="Select only required columns to reduce data transfer. "
                    + "Replace 'SELECT *' with explicit column list.",
                )
            )

    def _apply_join_rules(self, metrics: PerformanceMetrics):
        """应用JOIN规则"""
        # CROSS JOIN检测
        if metrics.cross_join_count > 0:
            penalty = self.SCORING_RULES["cross_join"] * metrics.cross_join_count
            self.score += penalty
            self.issues.append(
                PerformanceIssue(
                    type=IssueType.ERROR,
                    message=f"CROSS JOIN detected ({metrics.cross_join_count} times)",
                    suggestion="CROSS JOIN can be very expensive. "
                    + "Consider using INNER JOIN with explicit conditions.",
                )
            )

        # 多JOIN检测
        if metrics.join_count > 3:
            excess_joins = metrics.join_count - 3
            penalty = self.SCORING_RULES["multiple_joins"] * excess_joins
            self.score += penalty
            self.issues.append(
                PerformanceIssue(
                    type=IssueType.WARNING,
                    message=f"Multiple JOINs detected ({metrics.join_count} joins)",
                    suggestion=f"Consider if all {metrics.join_count} joins are necessary. "
                    + "Each join adds complexity and potential performance cost.",
                )
            )

    def _apply_complexity_rule(self, hql: str, metrics: PerformanceMetrics):
        """应用复杂度规则"""
        if metrics.complexity == "high":
            self.score += self.SCORING_RULES["complexity_high"]
            self.issues.append(
                PerformanceIssue(
                    type=IssueType.INFO,
                    message="Query complexity is high",
                    suggestion="Consider breaking this query into smaller, simpler queries "
                    + "or using temporary tables/views.",
                )
            )
        elif metrics.complexity == "medium":
            self.score += self.SCORING_RULES["complexity_medium"]

    def _apply_subquery_rule(self, metrics: PerformanceMetrics):
        """应用子查询规则"""
        if metrics.subquery_count > 0:
            penalty = self.SCORING_RULES["subquery"] * metrics.subquery_count
            self.score += penalty

            if metrics.subquery_count > 2:
                self.issues.append(
                    PerformanceIssue(
                        type=IssueType.WARNING,
                        message=f"Multiple subqueries detected ({metrics.subquery_count})",
                        suggestion="Subqueries can be optimized. "
                        + "Consider using WITH clauses (CTEs) or JOINs instead.",
                    )
                )

    def _apply_udf_rule(self, metrics: PerformanceMetrics):
        """应用UDF规则"""
        if metrics.udf_count > 0:
            penalty = self.SCORING_RULES["udf"] * metrics.udf_count
            self.score += penalty

            if metrics.udf_count > 3:
                self.issues.append(
                    PerformanceIssue(
                        type=IssueType.INFO,
                        message=f"Multiple UDFs detected ({metrics.udf_count})",
                        suggestion="UDFs can be slower than built-in functions. "
                        + "Consider using built-in functions when possible.",
                    )
                )


# 便捷函数
def analyze_hql_performance(hql: str) -> PerformanceReport:
    """
    分析HQL性能（便捷函数）

    Args:
        hql: HQL语句

    Returns:
        PerformanceReport: 性能报告
    """
    analyzer = HQLPerformanceAnalyzer()
    return analyzer.analyze(hql)


def format_report_for_api(report: PerformanceReport) -> Dict[str, Any]:
    """
    格式化性能报告为API响应格式

    Args:
        report: 性能报告

    Returns:
        Dict: API响应格式
    """
    return {
        "score": report.score,
        "issues": [
            {"type": issue.type.value, "message": issue.message, "suggestion": issue.suggestion}
            for issue in report.issues
        ],
        "metrics": {
            "has_partition_filter": report.metrics.has_partition_filter,
            "has_select_star": report.metrics.has_select_star,
            "join_count": report.metrics.join_count,
            "complexity": report.metrics.complexity,
        },
    }


# 导出
__all__ = [
    "HQLPerformanceAnalyzer",
    "PerformanceIssue",
    "PerformanceMetrics",
    "PerformanceReport",
    "IssueType",
    "analyze_hql_performance",
    "format_report_for_api",
]
