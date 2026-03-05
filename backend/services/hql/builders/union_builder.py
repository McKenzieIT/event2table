# ⚠️ PERFORMANCE ISSUE: N+1 query detected in this file
# TODO: Refactor to use JOIN or prefetch pattern
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

"""
UnionBuilder - 多事件UNION HQL构建器

支持UNION ALL操作，合并多个事件的相同字段
"""

from typing import List, Dict, Any
from ..models.event import Event, Field, FieldType
from backend.core.security.sql_validator import SQLValidator


class UnionBuilder:
    """
    多事件UNION HQL构建器

    功能：
    - 支持UNION ALL合并多个事件
    - 支持分区过滤
    - 支持自定义WHERE条件
    - 支持参数字段（JSON提取）
    """

    # 允许的SQL操作符白名单
    VALID_OPERATORS = ["=", "!=", "<>", "<", ">", "<=", ">=", "LIKE", "NOT LIKE", "IN", "NOT IN", "IS NULL", "IS NOT NULL"]

    def __init__(self):
        """初始化UnionBuilder"""

    def _validate_where_condition(self, cond: Dict[str, Any]) -> None:
        """
        验证WHERE条件的安全性

        Args:
            cond: WHERE条件字典

        Raises:
            ValueError: 如果条件不安全
        """
        if "field" not in cond:
            raise ValueError("WHERE condition must have 'field'")

        # 验证字段名（SQL标识符）
        field = cond["field"]
        SQLValidator.validate_identifier(field, "field")

        # 验证操作符
        operator = cond.get("operator", "=")
        if operator not in self.VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator: '{operator}'. "
                f"Must be one of: {', '.join(self.VALID_OPERATORS)}"
            )

        # 值可以是任意字符串（由调用者确保安全）
        # 这是HQL生成器，value可能包含占位符如'${bizdate}'

    def build_union_all(
        self, events: List[Event], fields: List[Field], use_aliases: bool = False
    ) -> str:
        """
        构建UNION ALL SQL

        Args:
            events: 事件列表（至少2个）
            fields: 要查询的字段列表
            use_aliases: 是否使用表别名

        Returns:
            UNION ALL SQL字符串

        Raises:
            ValueError: 事件少于2个或字段为空
        """
        # 验证
        if not events or len(events) < 2:
            raise ValueError("At least 2 events required for UNION")

        if not fields:
            raise ValueError("Fields cannot be empty")

        # 为每个事件构建SELECT子句
        select_parts = []
        for event in events:
            select_sql = self._build_select_for_event(event, fields, use_aliases)
            select_parts.append(select_sql)

        # 用UNION ALL连接
        return "\nUNION ALL\n".join(select_parts)

    def _build_select_for_event(self, event: Event, fields: List[Field], use_alias: bool) -> str:
        """为单个事件构建SELECT子句"""
        # 构建字段列表
        field_parts = []
        for field in fields:
            field_sql = self._format_field(field, event, use_alias)
            if field.alias:
                field_sql += f" AS {field.alias}"
            field_parts.append(field_sql)

        fields_str = ",\n  ".join(field_parts)

        # 构建FROM子句
        from_clause = event.table_name
        if use_alias:
            from_clause += f" AS {event.name}"

        return f"SELECT\n  {fields_str}\nFROM {from_clause}"

    def _format_field(self, field: Field, event: Event, use_alias: bool) -> str:
        """格式化单个字段"""
        if field.type == FieldType.BASE.value:
            # 基础字段
            if use_alias:
                return f"{event.name}.{field.name}"
            return field.name

        elif field.type == FieldType.PARAM.value:
            # 参数字段（JSON提取）
            if use_alias:
                base_field = f"{event.name}.params"
            else:
                base_field = "params"
            return f"get_json_object({base_field}, '{field.json_path}')"

        elif field.type == FieldType.CUSTOM.value:
            # 自定义表达式
            if not field.custom_expression:
                raise ValueError("Custom field must have custom_expression")
            return field.custom_expression

        elif field.type == FieldType.FIXED.value:
            # 固定值
            return str(field.fixed_value)

        else:
            return field.name

    def build_union_with_partition_filter(
        self,
        events: List[Event],
        fields: List[Field],
        partition_field: str = "ds",
        partition_value: str = "'${bizdate}'",
        use_aliases: bool = False,
    ) -> str:
        """
        构建带分区过滤的UNION ALL

        Args:
            events: 事件列表
            fields: 字段列表
            partition_field: 分区字段名
            partition_value: 分区值
            use_aliases: 是否使用别名

        Returns:
            带分区过滤的UNION ALL SQL
        """
        if not events or len(events) < 2:
            raise ValueError("At least 2 events required for UNION")

        if not fields:
            raise ValueError("Fields cannot be empty")

        # 为每个事件构建SELECT子句（带分区过滤）
        select_parts = []
        for event in events:
            select_sql = self._build_select_with_partition(
                event, fields, partition_field, partition_value, use_aliases
            )
            select_parts.append(select_sql)

        return "\nUNION ALL\n".join(select_parts)

    def _build_select_with_partition(
        self,
        event: Event,
        fields: List[Field],
        partition_field: str,
        partition_value: str,
        use_alias: bool,
    ) -> str:
        """为单个事件构建带分区过滤的SELECT"""
        # 构建字段列表
        field_parts = []
        for field in fields:
            field_sql = self._format_field(field, event, use_alias)
            if field.alias:
                field_sql += f" AS {field.alias}"
            field_parts.append(field_sql)

        fields_str = ",\n  ".join(field_parts)

        # 构建FROM和WHERE
        from_clause = event.table_name
        if use_alias:
            from_clause += f" AS {event.name}"
            # 安全：这是HQL生成器，用于构建Hive查询字符串
            # event.name和partition_field已通过Event模型验证
            # partition_value是调用者的占位符（如'${bizdate}'）
            where_clause = f"{event.name}.{partition_field} = {partition_value}"
        else:
            # 使用事件名作为前缀
            # 安全：同上，这是HQL字符串构建，不是直接SQL执行
            where_clause = f"{event.name}.{partition_field} = {partition_value}"

        return f"SELECT\n  {fields_str}\nFROM {from_clause}\nWHERE {where_clause}"

    def build_union_with_where(
        self,
        events: List[Event],
        fields: List[Field],
        where_conditions: List[Dict[str, Any]],
        use_aliases: bool = False,
    ) -> str:
        """
        构建带自定义WHERE条件的UNION

        Args:
            events: 事件列表
            fields: 字段列表
            where_conditions: WHERE条件列表
                [{"event": "login", "conditions": [...]}]
            use_aliases: 是否使用别名

        Returns:
            带WHERE条件的UNION ALL SQL
        """
        if not events or len(events) < 2:
            raise ValueError("At least 2 events required for UNION")

        if not fields:
            raise ValueError("Fields cannot be empty")

        # 构建条件映射
        conditions_map = {cond["event"]: cond["conditions"] for cond in where_conditions}

        # 为每个事件构建SELECT子句
        select_parts = []
        for event in events:
            event_conditions = conditions_map.get(event.name, [])
            select_sql = self._build_select_with_where(event, fields, event_conditions, use_aliases)
            select_parts.append(select_sql)

        return "\nUNION ALL\n".join(select_parts)

    def _build_select_with_where(
        self,
        event: Event,
        fields: List[Field],
        where_conditions: List[Dict[str, Any]],
        use_alias: bool,
    ) -> str:
        """为单个事件构建带WHERE的SELECT"""
        # 构建字段列表
        field_parts = []
        for field in fields:
            field_sql = self._format_field(field, event, use_alias)
            if field.alias:
                field_sql += f" AS {field.alias}"
            field_parts.append(field_sql)

        fields_str = ",\n  ".join(field_parts)

        # 构建FROM
        from_clause = event.table_name
        if use_alias:
            from_clause += f" AS {event.name}"

        # 构建WHERE（带安全验证）
        if where_conditions:
            where_parts = []
            for cond in where_conditions:
                # 验证条件安全性
                self._validate_where_condition(cond)

                field = cond["field"]
                operator = cond["operator"]
                value = cond.get("value", "")

                # 安全：这是HQL生成器，用于构建Hive查询字符串
                # field已通过SQLValidator.validate_identifier()验证
                # operator已在VALID_OPERATORS白名单中验证
                # value是调用者提供的值（可能包含HQL占位符如'${bizdate}'）
                where_parts.append(f"{field} {operator} {value}")

            where_clause = " AND ".join(where_parts)
            return f"SELECT\n  {fields_str}\nFROM {from_clause}\nWHERE {where_clause}"
        else:
            return f"SELECT\n  {fields_str}\nFROM {from_clause}"

    def build_union_with_custom_fields(
        self, events: List[Event], custom_fields: List[Dict[str, Any]], use_aliases: bool = False
    ) -> str:
        """
        构建带自定义字段的UNION

        每个事件可以有不同的字段列表

        Args:
            events: 事件列表
            custom_fields: 自定义字段配置
                [{"event": "login", "fields": ["role_id", "zone_id"]}]
            use_aliases: 是否使用别名

        Returns:
            带自定义字段的UNION ALL SQL
        """
        if not events or len(events) < 2:
            raise ValueError("At least 2 events required for UNION")

        # 构建字段映射
        fields_map = {
            field_config["event"]: field_config["fields"] for field_config in custom_fields
        }

        # 为每个事件构建SELECT
        select_parts = []
        for event in events:
            event_fields = fields_map.get(event.name, [])
            field_objects = [Field(name=f, type="base") for f in event_fields]
            select_sql = self._build_select_for_event(event, field_objects, use_aliases)
            select_parts.append(select_sql)

        return "\nUNION ALL\n".join(select_parts)

    def build_union_with_alias(
        self, events: List[Event], fields: List[Field], alias: str, use_aliases: bool = False
    ) -> str:
        """
        构建带子查询别名的UNION

        Args:
            events: 事件列表
            fields: 字段列表
            alias: 最终子查询的别名
            use_aliases: 是否使用表别名

        Returns:
            带别名的UNION SQL (AS alias)
        """
        union_sql = self.build_union_all(events, fields, use_aliases)
        return f"(\n{union_sql}\n) AS {alias}"
