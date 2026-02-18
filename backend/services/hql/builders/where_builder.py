"""
WHERE条件构建器

负责将抽象Condition模型转换为SQL WHERE子句
"""

from typing import List, Optional
from ..models.event import Condition, Operator, LogicalOperator


class WhereBuilder:
    """
    WHERE条件SQL构建器

    支持多种操作符和逻辑组合
    """

    def build(self, conditions: List[Condition], context: Optional[dict] = None) -> str:
        """
        构建WHERE子句

        Args:
            conditions: 条件列表
            context: 上下文信息（包含事件、分区信息等）

        Returns:
            str: WHERE子句（不包含WHERE关键字）

        Examples:
            >>> builder = WhereBuilder()
            >>> conditions = [
            ...     Condition(field="role_id", operator="=", value=123),
            ...     Condition(field="level", operator=">", value=10, logical_op="AND")
            ... ]
            >>> builder.build(conditions, {})
            'ds = '${ds}' AND event_name = 'zmpvp.vis' AND role_id = 123 AND level > 10'
        """
        condition_clauses = []

        # 添加分区过滤（总是作为第一个条件）
        partition_filter = self._build_partition_filter(context)
        if partition_filter:
            condition_clauses.append(partition_filter)

        # 添加事件名称过滤（如果有event上下文）
        event_filter = self._build_event_filter(context)
        if event_filter:
            condition_clauses.append(event_filter)

        # 如果没有用户自定义条件，只返回系统过滤条件
        if not conditions:
            return self._join_conditions(condition_clauses)

        # 构建用户自定义条件SQL
        for cond in conditions:
            clause = self._build_single_condition(cond, context)
            condition_clauses.append(clause)

        # 用逻辑操作符连接
        where_clause = self._join_conditions(condition_clauses)

        return where_clause

    def _build_single_condition(self, condition: Condition, context: Optional[dict]) -> str:
        """构建单个条件SQL"""
        # 处理IS NULL和IS NOT NULL（不需要值）
        if condition.is_null_operator():
            return f"{condition.field} {condition.operator}"

        # 处理IN操作符
        if condition.operator in [Operator.IN.value, Operator.NOT_IN.value]:
            return self._build_in_condition(condition)

        # 处理LIKE操作符
        if condition.operator == Operator.LIKE.value:
            return f"{condition.field} LIKE '{condition.value}'"

        # 处理普通比较操作符
        value = self._format_value(condition.value)
        return f"{condition.field} {condition.operator} {value}"

    def _build_in_condition(self, condition: Condition) -> str:
        """构建IN条件SQL"""
        if not isinstance(condition.value, (list, tuple)):
            raise ValueError("IN operator requires a list of values")

        # 检查空列表
        if len(condition.value) == 0:
            raise ValueError("IN operator requires at least one value. " "Empty list provided.")

        values = ", ".join([self._format_value(v) for v in condition.value])
        return f"{condition.field} {condition.operator} ({values})"

    def _build_partition_filter(self, context: Optional[dict]) -> str:
        """
        构建分区过滤条件

        总是添加分区过滤以避免全表扫描
        默认: ds = '${ds}'
        """
        if not context:
            return "ds = '${ds}'"

        event = context.get("event")
        if event:
            return f"{event.partition_field} = '${{ds}}'"

        return "ds = '${ds}'"

    def _build_event_filter(self, context: Optional[dict]) -> Optional[str]:
        """
        构建事件名称过滤条件

        总是添加事件名称过滤以限定查询范围
        格式: event_name = 'zmpvp.vis'

        Args:
            context: 上下文信息（包含event对象）

        Returns:
            str: 事件过滤条件字符串，如果没有event上下文则返回None
        """
        if not context:
            return None

        event = context.get("event")
        if event and event.name:
            return f"event_name = '{event.name}'"

        return None

    def _join_conditions(self, clauses: List[str]) -> str:
        """
        用逻辑操作符连接条件

        注意：这里简化处理，实际应该按logical_op分组
        生产环境应该支持复杂嵌套条件
        """
        if not clauses:
            return ""

        # 简化版：都用AND连接
        return " AND\n  ".join(clauses)

    def _format_value(self, value: any) -> str:
        """
        格式化值

        - 字符串加引号并转义特殊字符
        - 数字直接使用
        - 布尔值转换为TRUE/FALSE
        - NULL直接使用
        """
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            # 转义特殊字符（先转义反斜杠，再转义单引号）
            escaped = value.replace("\\", "\\\\").replace("'", "''")
            return f"'{escaped}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            # 其他类型转为字符串并转义
            escaped = str(value).replace("\\", "\\\\").replace("'", "''")
            return f"'{escaped}'"

    def build_complex_conditions(
        self, conditions: List[Condition], context: Optional[dict] = None
    ) -> str:
        """
        构建复杂的WHERE条件（支持AND/OR分组）

        这是高级版本，支持条件分组和嵌套

        Args:
            conditions: 条件列表（包含logical_op）
            context: 上下文信息

        Returns:
            str: 复杂WHERE子句
        """
        if not conditions:
            return self._build_partition_filter(context)

        # 分组：按AND/OR分组
        and_groups = []
        or_groups = []

        current_group = []
        current_op = LogicalOperator.AND.value

        for cond in conditions:
            if cond.logical_op == LogicalOperator.OR.value:
                # 保存当前AND组
                if current_group:
                    and_groups.append(current_group)
                    current_group = []
                # 添加到OR组
                or_groups.append([cond])
            else:
                # 添加到当前AND组
                current_group.append(cond)

        # 保存最后一组
        if current_group:
            and_groups.append(current_group)

        # 构建SQL
        and_parts = []
        for group in and_groups:
            group_sql = " AND ".join([self._build_single_condition(c, context) for c in group])
            and_parts.append(f"({group_sql})" if len(group) > 1 else group_sql)

        or_parts = []
        for group in or_groups:
            group_sql = " OR ".join([self._build_single_condition(c, context) for c in group])
            or_parts.append(f"({group_sql})" if len(group) > 1 else group_sql)

        # 组合
        all_parts = and_parts + or_parts

        # 添加分区过滤
        partition_filter = self._build_partition_filter(context)
        if partition_filter:
            all_parts.insert(0, f"({partition_filter})")

        # 用AND连接所有组
        if len(all_parts) == 1:
            return all_parts[0]
        else:
            return " AND\n  ".join(all_parts)
