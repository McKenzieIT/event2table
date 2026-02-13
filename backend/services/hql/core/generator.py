"""
核心HQL生成器

完全无框架依赖的HQL生成器
"""

from typing import List, Optional, Union
from ..models.event import Event, Field, Condition, HQLContext
from ..builders.field_builder import FieldBuilder
from ..builders.where_builder import WhereBuilder
from ..builders.join_builder import JoinBuilder
from ..builders.union_builder import UnionBuilder


class HQLGenerator:
    """
    核心HQL生成器

    这是完全独立的、无业务依赖的HQL生成器
    可以作为独立Python包使用

    Examples:
        >>> from ... HQLGenerator, Event, Field
        >>>
        >>> generator = HQLGenerator()
        >>>
        >>> event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")
        >>> fields = [
        ...     Field(name="role_id", type="base"),
        ...     Field(name="zone_id", type="param", json_path="$.zone_id")
        ... ]
        >>> conditions = []
        >>>
        >>> hql = generator.generate(events=[event], fields=fields, conditions=conditions)
        >>> print(hql)
    """

    def __init__(self):
        """初始化生成器"""
        self.field_builder = FieldBuilder()
        self.where_builder = WhereBuilder()
        self.join_builder = JoinBuilder()
        self.union_builder = UnionBuilder()

    def generate(
        self, events: List[Event], fields: List[Field], conditions: List[Condition], **options
    ) -> str:
        """
        生成HQL主入口

        Args:
            events: 事件列表（支持多事件）
            fields: 字段列表
            conditions: WHERE条件列表
            **options: 额外选项
                - mode: 生成模式（single/join/union）
                - sql_mode: SQL模式（VIEW/PROCEDURE/CUSTOM）
                - include_comments: 是否包含注释（默认True）

        Returns:
            str: 完整的HQL语句

        Examples:
            >>> generator = HQLGenerator()
            >>> event = Event(name="login", table_name="ods.table")
            >>> fields = [Field(name="role_id", type="base")]
            >>> hql = generator.generate(
            ...     events=[event],
            ...     fields=fields,
            ...     conditions=[]
            ... )
        """
        # 获取选项
        mode = options.get("mode", "single")
        sql_mode = options.get("sql_mode", "VIEW")
        include_comments = options.get("include_comments", True)

        # 根据模式生成HQL
        if mode == "single":
            hql = self._generate_single_event(events, fields, conditions, options)
        elif mode == "join":
            hql = self._generate_join_events(events, fields, conditions, options)
        elif mode == "union":
            hql = self._generate_union_events(events, fields, conditions, options)
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        # 添加注释
        if include_comments:
            hql = self._add_comments(hql, events, options)

        return hql

    def _generate_single_event(
        self, events: List[Event], fields: List[Field], conditions: List[Condition], options: dict
    ) -> str:
        """生成单事件HQL"""
        if len(events) != 1:
            raise ValueError("single mode requires exactly one event")

        event = events[0]

        # 构建字段SQL
        field_sqls = self.field_builder.build_fields(fields)
        fields_clause = ",\n  ".join(field_sqls)

        # 构建WHERE子句
        context = {"event": event}
        where_clause = self.where_builder.build(conditions, context)

        # 组装HQL
        hql = f"""SELECT
  {fields_clause}
FROM {event.table_name}
WHERE
  {where_clause}"""

        return hql

    def _generate_join_events(
        self, events: List[Event], fields: List[Field], conditions: List[Condition], options: dict
    ) -> str:
        """生成多事件JOIN HQL"""
        if len(events) < 2:
            raise ValueError("join mode requires at least two events")

        join_config = options.get("join_config")
        if not join_config:
            raise ValueError("join mode requires join_config")

        # 使用JoinBuilder构建JOIN SQL
        join_type = join_config.get("type", "INNER")
        join_conditions = join_config.get("conditions", [])
        use_aliases = join_config.get("use_aliases", True)

        # 构建SELECT字段
        select_fields = self.join_builder.format_select_fields(
            fields, events, use_event_prefix=use_aliases
        )

        # 构建JOIN部分
        join_sql = self.join_builder.build_join(events, join_conditions, join_type, use_aliases)

        # 构建WHERE条件（包含分区过滤）
        context = {"event": events[0]} if events else None
        where_clause = self.where_builder.build(conditions, context)

        # 组装完整HQL
        hql = f"SELECT\n  {select_fields}\n{join_sql}\nWHERE\n  {where_clause}"

        return hql

    def _generate_union_events(
        self, events: List[Event], fields: List[Field], conditions: List[Condition], options: dict
    ) -> str:
        """生成多事件UNION HQL"""
        if len(events) < 2:
            raise ValueError("union mode requires at least two events")

        # 使用UnionBuilder构建UNION ALL SQL
        use_aliases = options.get("use_aliases", True)
        include_partition_filter = options.get("include_partition_filter", True)

        if include_partition_filter:
            # 使用带分区过滤的UNION
            union_sql = self.union_builder.build_union_with_partition_filter(
                events,
                fields,
                partition_field="ds",
                partition_value="'${ds}'",
                use_aliases=use_aliases,
            )
        else:
            # 普通UNION
            union_sql = self.union_builder.build_union_all(events, fields, use_aliases=use_aliases)

        # 添加额外的WHERE条件（如果有）
        if conditions:
            # TODO: 支持复杂的WHERE条件
            # 目前暂时不支持，因为UNION每个子查询的WHERE可能不同
            pass  # pragma: no cover

        return union_sql

    def _add_comments(self, hql: str, events: List[Event], options: dict) -> str:
        """添加注释信息"""
        # 检查events列表是否为空
        if not events:
            return hql

        event = events[0]

        comments = []
        comments.append(f"-- Event Node: {event.name}")
        comments.append(f"-- 中文: {event.name}")

        return "\n".join(comments) + "\n" + hql


class DebuggableHQLGenerator(HQLGenerator):
    """
    支持调试的HQL生成器

    可以返回生成过程的详细信息
    """

    def generate(
        self,
        events: List[Event],
        fields: List[Field],
        conditions: List[Condition],
        debug: bool = False,
        **options,
    ) -> Union[str, dict]:
        """
        生成HQL（支持调试模式）

        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            debug: 是否启用调试模式
            **options: 额外选项

        Returns:
            str: 普通模式返回HQL字符串
            dict: 调试模式返回详细信息
        """
        if not debug:
            # 普通模式：调用父类方法
            return super().generate(events, fields, conditions, **options)

        # 调试模式：返回详细跟踪
        trace = {
            "steps": [],
            "events": [e.__dict__ for e in events],
            "fields": [f.__dict__ for f in fields],
            "conditions": [c.__dict__ for c in conditions],
        }

        # 步骤1: 字段构建
        field_sqls = self.field_builder.build_fields(fields)
        trace["steps"].append(
            {"step": "build_fields", "result": field_sqls, "count": len(field_sqls)}
        )

        # 步骤2: WHERE构建
        context = {"event": events[0]} if events else {}
        where_clause = self.where_builder.build(conditions, context)
        trace["steps"].append({"step": "build_where", "result": where_clause})

        # 步骤3: HQL组装
        hql = super().generate(events, fields, conditions, **options)
        trace["steps"].append({"step": "assemble", "result": hql})

        trace["final_hql"] = hql

        return trace
