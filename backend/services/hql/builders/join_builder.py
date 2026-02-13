"""
JoinBuilder - 多事件JOIN HQL构建器

支持INNER JOIN, LEFT JOIN, RIGHT JOIN, CROSS JOIN
"""

from typing import List, Dict, Any
from ..models.event import Event, Field


class JoinBuilder:
    """
    多事件JOIN HQL构建器

    功能：
    - 支持INNER/LEFT/RIGHT/CROSS JOIN
    - 支持多条件JOIN
    - 支持事件别名
    - 支持分区过滤
    """

    VALID_JOIN_TYPES = ["INNER", "LEFT", "RIGHT", "CROSS"]

    def __init__(self):
        """初始化JoinBuilder"""
        self.event_aliases = {}

    def build_join(
        self,
        events: List[Event],
        join_conditions: List[Dict[str, Any]],
        join_type: str = "INNER",
        use_aliases: bool = False,
    ) -> str:
        """
        构建JOIN SQL

        Args:
            events: 事件列表
            join_conditions: JOIN条件列表
            join_type: JOIN类型 (INNER/LEFT/RIGHT/CROSS)
            use_aliases: 是否使用事件别名

        Returns:
            JOIN SQL字符串

        Raises:
            ValueError: JOIN条件为空或JOIN类型无效
        """
        # 验证
        if not events or len(events) < 2:
            raise ValueError("At least 2 events required for JOIN")

        if join_type not in self.VALID_JOIN_TYPES:
            raise ValueError(
                f"Invalid join type: {join_type}. Must be one of {self.VALID_JOIN_TYPES}"
            )

        if join_type != "CROSS" and not join_conditions:
            raise ValueError("Join conditions required for non-CROSS JOIN")

        # 生成事件别名
        if use_aliases:
            self.event_aliases = {event.name: event.name for event in events}
        else:
            self.event_aliases = {}

        # 构建JOIN
        base_event = events[0]
        join_parts = [f"FROM {base_event.table_name}"]

        if use_aliases:
            join_parts[0] += f" AS {base_event.name}"

        for i, event in enumerate(events[1:], start=1):
            join_sql = self._build_single_join(
                base_event.name, event, join_conditions, join_type, use_aliases
            )
            join_parts.append(join_sql)

        return "\n".join(join_parts)

    def _build_single_join(
        self,
        base_event_name: str,
        join_event: Event,
        join_conditions: List[Dict[str, Any]],
        join_type: str,
        use_aliases: bool,
    ) -> str:
        """构建单个JOIN语句"""
        # 表名和别名
        if use_aliases:
            table_clause = f"{join_event.table_name} AS {join_event.name}"
        else:
            table_clause = join_event.table_name

        # JOIN类型
        join_clause = f"{join_type} JOIN {table_clause}"

        # JOIN条件
        if join_type == "CROSS":
            return join_clause

        # 筛选当前JOIN的条件
        relevant_conditions = [
            cond
            for cond in join_conditions
            if cond.get("left_event") == base_event_name
            or cond.get("right_event") == join_event.name
        ]

        if not relevant_conditions:
            # 如果没有找到相关条件，使用所有条件
            relevant_conditions = join_conditions

        on_conditions = []
        for cond in relevant_conditions:
            left_field = f"{cond['left_event']}.{cond['left_field']}"
            right_field = f"{cond['right_event']}.{cond['right_field']}"
            operator = cond.get("operator", "=")
            on_conditions.append(f"{left_field} {operator} {right_field}")

        on_clause = " AND ".join(on_conditions)
        return f"{join_clause} ON {on_clause}"

    def build_join_with_where(
        self,
        events: List[Event],
        join_conditions: List[Dict[str, Any]],
        where_conditions: List[Dict[str, Any]],
        join_type: str = "INNER",
        use_aliases: bool = False,
    ) -> str:
        """
        构建JOIN + WHERE完整SQL

        Args:
            events: 事件列表
            join_conditions: JOIN条件
            where_conditions: WHERE条件
            join_type: JOIN类型
            use_aliases: 是否使用别名

        Returns:
            完整SQL (SELECT ... FROM ... JOIN ... WHERE ...)
        """
        # 构建JOIN部分
        join_sql = self.build_join(events, join_conditions, join_type, use_aliases)

        # 构建WHERE条件
        where_parts = []
        for cond in where_conditions:
            field = cond["field"]
            operator = cond["operator"]
            value = cond.get("value", "")
            where_parts.append(f"{field} {operator} {value}")

        where_clause = " AND ".join(where_parts)

        # 组装完整SQL
        full_sql = f"SELECT *\n{join_sql}\nWHERE {where_clause}"

        return full_sql

    def build_join_with_partition_filter(
        self,
        events: List[Event],
        join_conditions: List[Dict[str, Any]],
        partition_field: str = "ds",
        partition_value: str = "'${bizdate}'",
        join_type: str = "INNER",
        use_aliases: bool = False,
    ) -> str:
        """
        构建带分区过滤的JOIN SQL

        Args:
            events: 事件列表
            join_conditions: JOIN条件
            partition_field: 分区字段名
            partition_value: 分区值
            join_type: JOIN类型
            use_aliases: 是否使用别名

        Returns:
            带分区过滤的完整SQL
        """
        # 为每个事件添加分区过滤条件
        where_conditions = []
        for event in events:
            if use_aliases:
                where_conditions.append(
                    {
                        "field": f"{event.name}.{partition_field}",
                        "operator": "=",
                        "value": partition_value,
                    }
                )
            else:
                # 需要推断表别名，暂时使用事件名
                where_conditions.append(
                    {
                        "field": f"{event.name}.{partition_field}",
                        "operator": "=",
                        "value": partition_value,
                    }
                )

        return self.build_join_with_where(
            events, join_conditions, where_conditions, join_type, use_aliases
        )

    def build_cross_join(self, events: List[Event], use_aliases: bool = False) -> str:
        """
        构建CROSS JOIN SQL

        Args:
            events: 事件列表
            use_aliases: 是否使用别名

        Returns:
            CROSS JOIN SQL
        """
        if len(events) < 2:
            raise ValueError("At least 2 events required for CROSS JOIN")

        base_event = events[0]
        join_parts = [f"FROM {base_event.table_name}"]

        if use_aliases:
            join_parts[0] += f" AS {base_event.name}"

        for event in events[1:]:
            if use_aliases:
                join_parts.append(f"CROSS JOIN {event.table_name} AS {event.name}")
            else:
                join_parts.append(f"CROSS JOIN {event.table_name}")

        return "\n".join(join_parts)

    def format_select_fields(
        self, fields: List[Field], events: List[Event], use_event_prefix: bool = True
    ) -> str:
        """
        格式化SELECT字段（带事件前缀）

        Args:
            fields: 字段列表
            events: 事件列表
            use_event_prefix: 是否使用事件前缀

        Returns:
            SELECT字段SQL
        """
        if not fields:
            return "*"

        select_parts = []
        for field in fields:
            if use_event_prefix:
                # 假设字段来自第一个事件
                event_name = events[0].name if events else ""
                field_sql = f"{event_name}.{field.name}"
            else:
                field_sql = field.name

            # 添加别名
            if field.alias:
                field_sql += f" AS {field.alias}"

            select_parts.append(field_sql)

        return ",\n  ".join(select_parts)
