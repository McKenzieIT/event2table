"""
Game GraphQL Type

Defines the GraphQL type for Game entity with relationships.
"""

import graphene
from graphene import Field, List, Int, String, Boolean
import logging

logger = logging.getLogger(__name__)


class GameImpactType(graphene.ObjectType):
    """
    Game Impact Type
    
    Represents the impact analysis of a game.
    """
    
    class Meta:
        description = "游戏影响分析"
    
    event_count = Int(description="事件数量")
    parameter_count = Int(description="参数数量")
    flow_count = Int(description="流程数量")
    last_activity = String(description="最后活动时间")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameImpactType':
        """Create GameImpactType instance from dictionary."""
        return cls(
            event_count=data.get('event_count', 0),
            parameter_count=data.get('parameter_count', 0),
            flow_count=data.get('flow_count', 0),
            last_activity=str(data.get('last_activity')) if data.get('last_activity') else None,
        )


class GameStatisticsType(graphene.ObjectType):
    """
    Game Statistics Type
    
    Represents the statistics of a game.
    """
    
    class Meta:
        description = "游戏统计数据"
    
    total_events = Int(description="总事件数")
    active_events = Int(description="活跃事件数")
    total_parameters = Int(description="总参数数")
    total_flows = Int(description="总流程数")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameStatisticsType':
        """Create GameStatisticsType instance from dictionary."""
        return cls(
            total_events=data.get('total_events', 0),
            active_events=data.get('active_events', 0),
            total_parameters=data.get('total_parameters', 0),
            total_flows=data.get('total_flows', 0),
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
    ods_db = String(required=True, description="ODS数据库名称")
    icon_path = String(description="游戏图标路径")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")
    
    # Computed fields
    event_count = Int(description="事件数量")
    parameter_count = Int(description="参数数量")
    event_node_count = Int(description="事件节点数量")
    flow_template_count = Int(description="流程模板数量")
    
    # V2 API fields
    is_active = Boolean(description="是否活跃")
    name_cn = String(description="游戏中文名称")
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
            ods_db=data.get('ods_db'),
            icon_path=data.get('icon_path'),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
            event_count=data.get('event_count', 0),
            parameter_count=data.get('param_count', 0),
            event_node_count=data.get('event_node_count', 0),
            flow_template_count=data.get('flow_template_count', 0),
        )
