"""
Game GraphQL Type

Defines the GraphQL type for Game entity with relationships.
"""

import logging

import graphene
from graphene import Boolean, Field, Int, List, String

logger = logging.getLogger(__name__)


class GameImpactType(graphene.ObjectType):
    """
    Game Impact Type

    Represents the impact analysis of a game.
    """

    class Meta:
        description = "游戏影响分析"

    # ✅ 使用camelCase以符合GraphQL和JavaScript命名约定
    eventCount = Int(description="事件数量")
    parameterCount = Int(description="参数数量")
    flowCount = Int(description="流程数量")
    lastActivity = String(description="最后活动时间")

    @classmethod
    def from_dict(cls, data: dict) -> 'GameImpactType':
        """Create GameImpactType instance from dictionary."""
        return cls(
            # ✅ 映射SQL结果(snake_case)到GraphQL字段(camelCase)
            eventCount=data.get('event_count', 0),
            parameterCount=data.get('parameter_count', 0),
            flowCount=data.get('flow_count', 0),
            lastActivity=str(data.get('last_activity')) if data.get('last_activity') else None,
        )


class GameStatisticsType(graphene.ObjectType):
    """
    Game Statistics Type

    Represents the statistics of a game.
    """

    class Meta:
        description = "游戏统计数据"

    # ✅ 使用camelCase以符合GraphQL和JavaScript命名约定
    totalEvents = Int(description="总事件数")
    activeEvents = Int(description="活跃事件数")
    totalParameters = Int(description="总参数数")
    totalFlows = Int(description="总流程数")

    @classmethod
    def from_dict(cls, data: dict) -> 'GameStatisticsType':
        """Create GameStatisticsType instance from dictionary."""
        return cls(
            # ✅ 映射SQL结果(snake_case)到GraphQL字段(camelCase)
            totalEvents=data.get('total_events', 0),
            activeEvents=data.get('active_events', 0),
            totalParameters=data.get('total_parameters', 0),
            totalFlows=data.get('total_flows', 0),
        )


class GameType(graphene.ObjectType):
    """
    Game GraphQL Type

    Represents a game entity with its associated events and statistics.
    """

    class Meta:
        description = "游戏实体"

    # Basic fields
    id = Int(required=True, description="数据库ID")
    gid = Int(required=True, description="游戏业务GID")
    name = String(required=True, description="游戏名称")
    odsDb = String(required=True, description="ODS数据库名称")
    iconPath = String(description="游戏图标路径")
    createdAt = String(description="创建时间")
    updatedAt = String(description="更新时间")

    # ✅ Computed fields 使用camelCase
    eventCount = Int(description="事件数量")
    parameterCount = Int(description="参数数量")
    eventNodeCount = Int(description="事件节点数量")
    flowTemplateCount = Int(description="流程模板数量")

    # V2 API fields
    isActive = Boolean(description="是否活跃")
    nameCn = String(description="游戏中文名称")
    description = String(description="游戏描述")

    # V2 Impact fields
    # impact = Field(lambda: GameImpactType, description="游戏影响分析")
    # Temporarily disabled - GameImpactType not yet implemented

    # V2 Statistics fields
    # statistics = Field(lambda: GameStatisticsType, description="游戏统计数据")
    # Temporarily disabled - GameStatisticsType not yet implemented

    @classmethod
    def from_dict(cls, data: dict) -> 'GameType':
        """Create GameType instance from dictionary."""
        return cls(
            id=data.get('id'),
            gid=data.get('gid'),
            name=data.get('name'),
            # ✅ 映射SQL结果(snake_case)到GraphQL字段(camelCase)
            odsDb=data.get('ods_db'),
            iconPath=data.get('icon_path'),
            createdAt=str(data.get('created_at')) if data.get('created_at') else None,
            updatedAt=str(data.get('updated_at')) if data.get('updated_at') else None,
            eventCount=data.get('event_count', 0),
            parameterCount=data.get('param_count', 0),
            eventNodeCount=data.get('event_node_count', 0),
            flowTemplateCount=data.get('flow_template_count', 0),
            isActive=data.get('is_active', True),
            nameCn=data.get('name_cn'),
            description=data.get('description'),
        )
