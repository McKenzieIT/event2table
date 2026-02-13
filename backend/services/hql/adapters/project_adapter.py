"""
项目适配器

这是HQL V2核心服务中唯一依赖项目业务逻辑的地方

负责将当前项目的数据模型转换为抽象的Event/Field/Condition模型
"""

from typing import Dict, Any, List, Optional
from ..models.event import Event, Field, Condition
from backend.core.utils import fetch_one_as_dict


class ProjectAdapter:
    """
    项目适配器

    将项目特定的数据结构转换为HQL核心服务所需的抽象模型

    这是唯一的业务依赖点！
    """

    @staticmethod
    def event_from_project(game_gid: int, event_id: int) -> Event:
        """
        从项目数据构建抽象Event

        这是业务逻辑的核心：
        - 查询log_events表获取事件信息
        - 查询games表获取数据库信息
        - 构建完整的表名

        Args:
            game_gid: 游戏GID（业务ID）
            event_id: 事件ID（数据库主键）

        Returns:
            Event: 抽象事件模型

        Raises:
            ValueError: 如果事件或游戏不存在
        """
        # Convert to int if needed (handles string inputs)
        try:
            game_gid = int(game_gid)
            event_id = int(event_id)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid game_gid or event_id: must be integers, got game_gid={game_gid}, event_id={event_id}")

        # 查询事件
        event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))

        if not event:
            raise ValueError(f"Event not found: id={event_id}")

        # 查询游戏
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))

        if not game:
            raise ValueError(f"Game not found: gid={game_gid}")

        # 构建抽象Event
        # 表名格式: {ods_db}.ods_{game_gid}_all_view
        table_name = f"{game['ods_db']}.ods_{game['gid']}_all_view"

        return Event(name=event["event_name"], table_name=table_name, partition_field="ds")

    @staticmethod
    def event_from_request_data(data: Dict[str, Any]) -> Event:
        """
        从请求数据构建Event（简化版）

        用于API请求中已包含完整信息的情况

        Args:
            data: 包含event_name/name, table_name等字段的字典

        Returns:
            Event: 抽象事件模型
        """
        # Support both 'name' and 'event_name'
        event_name = data.get("event_name") or data.get("name")

        if not event_name:
            raise ValueError("Event must have either 'event_name' or 'name'")

        return Event(
            name=event_name,
            table_name=data["table_name"],
            partition_field=data.get("partition_field", "ds"),
        )

    @staticmethod
    def field_from_project(field_data: Dict[str, Any]) -> Field:
        """
        从前端字段数据构建抽象Field

        前端字段格式:
        {
            'fieldName': 'role_id',
            'fieldType': 'base',
            'alias': 'role',
            'aggregateFunc': 'COUNT'
        }

        OR (snake_case alternative):
        {
            'field_name': 'role_id',
            'field_type': 'base',
            'alias': 'role',
            'aggregate_func': 'COUNT'
        }

        Args:
            field_data: 前端字段数据

        Returns:
            Field: 抽象字段模型
        """
        # Support both camelCase and snake_case naming conventions
        field_name = field_data.get("fieldName") or field_data.get("field_name")
        field_type = field_data.get("fieldType") or field_data.get("field_type")

        if not field_name:
            raise ValueError("Field must have either 'fieldName' or 'field_name'")
        if not field_type:
            raise ValueError("Field must have either 'fieldType' or 'field_type'")

        return Field(
            name=field_name,
            type=field_type,
            alias=field_data.get("alias"),
            aggregate_func=field_data.get("aggregateFunc") or field_data.get("aggregate_func"),
            json_path=field_data.get("jsonPath") or field_data.get("json_path"),
            custom_expression=field_data.get("customExpression") or field_data.get("custom_expression"),
            fixed_value=field_data.get("fixedValue") or field_data.get("fixed_value"),
        )

    @staticmethod
    def condition_from_project(condition_data: Dict[str, Any]) -> Condition:
        """
        从前端条件数据构建抽象Condition

        前端条件格式:
        {
            'field': 'role_id',
            'operator': '=',
            'value': 123,
            'logicalOp': 'AND'
        }

        OR (snake_case alternative):
        {
            'field': 'role_id',
            'operator': '=',
            'value': 123,
            'logical_op': 'AND'
        }

        Args:
            condition_data: 前端条件数据

        Returns:
            Condition: 抽象条件模型
        """
        return Condition(
            field=condition_data["field"],
            operator=condition_data["operator"],
            value=condition_data.get("value"),
            logical_op=condition_data.get("logicalOp") or condition_data.get("logical_op", "AND"),
        )

    @staticmethod
    def events_from_api_request(events_data: List[Dict[str, Any]]) -> List[Event]:
        """
        从API请求数据批量构建Event列表

        Args:
            events_data: 事件数据列表

        Returns:
            List[Event]: 事件列表
        """
        events = []
        for event_data in events_data:
            if "game_gid" in event_data and "event_id" in event_data:
                # 需要查询数据库
                event = ProjectAdapter.event_from_project(
                    event_data["game_gid"], event_data["event_id"]
                )
            else:
                # 直接使用请求数据
                event = ProjectAdapter.event_from_request_data(event_data)

            events.append(event)

        return events

    @staticmethod
    def fields_from_api_request(fields_data: List[Dict[str, Any]]) -> List[Field]:
        """
        从API请求数据批量构建Field列表

        Args:
            fields_data: 字段数据列表

        Returns:
            List[Field]: 字段列表
        """
        return [ProjectAdapter.field_from_project(f) for f in fields_data]

    @staticmethod
    def conditions_from_api_request(conditions_data: List[Dict[str, Any]]) -> List[Condition]:
        """
        从API请求数据批量构建Condition列表

        Args:
            conditions_data: 条件数据列表

        Returns:
            List[Condition]: 条件列表
        """
        return [ProjectAdapter.condition_from_project(c) for c in conditions_data]
