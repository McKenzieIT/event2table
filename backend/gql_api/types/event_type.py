"""
Event GraphQL Type

Defines the GraphQL type for Event entity.
"""

import graphene
from graphene import Field, List, Int, String, Boolean
import logging

logger = logging.getLogger(__name__)


class EventType(graphene.ObjectType):
    """
    Event GraphQL Type
    
    Represents an event entity with its parameters.
    """
    
    class Meta:
        description = "事件实体"
    
    # Basic fields
    id = Int(required=True, description="事件ID")
    game_gid = Int(required=True, description="游戏GID")
    event_name = String(required=True, description="事件英文名")
    event_name_cn = String(required=True, description="事件中文名")
    category_id = Int(description="分类ID")
    category_name = String(description="分类名称")
    source_table = String(description="源表名")
    target_table = String(description="目标表名")
    include_in_common_params = Boolean(description="是否包含在公共参数中")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")
    
    # Computed fields
    param_count = Int(description="参数数量")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EventType':
        """Create EventType instance from dictionary."""
        return cls(
            id=data.get('id'),
            game_gid=data.get('game_gid'),
            event_name=data.get('event_name'),
            event_name_cn=data.get('event_name_cn'),
            category_id=data.get('category_id'),
            category_name=data.get('category_name'),
            source_table=data.get('source_table'),
            target_table=data.get('target_table'),
            include_in_common_params=bool(data.get('include_in_common_params', 0)),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
            param_count=data.get('param_count', 0),
        )
