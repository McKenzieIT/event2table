"""
Event V2 GraphQL Type

Defines the GraphQL types for Event V2 API with pagination support.
"""

import graphene
from graphene import Field, List, Int, String, Boolean, InputObjectType
import logging

logger = logging.getLogger(__name__)


class EventV2Type(graphene.ObjectType):
    """
    Event V2 GraphQL Type
    
    Represents an event entity with V2 API enhancements.
    """
    
    class Meta:
        description = "事件实体 (V2 API)"
    
    # Basic fields
    id = Int(required=True, description="事件ID")
    event_name = String(required=True, description="事件名称")
    event_name_cn = String(description="事件中文名称")
    description = String(description="事件描述")
    is_active = Boolean(required=True, description="是否活跃")
    category_id = Int(description="分类ID")
    game_gid = Int(required=True, description="游戏业务GID")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EventV2Type':
        """Create EventV2Type instance from dictionary."""
        return cls(
            id=data.get('id'),
            event_name=data.get('event_name'),
            event_name_cn=data.get('event_name_cn'),
            description=data.get('description'),
            is_active=data.get('is_active', True),
            category_id=data.get('category_id'),
            game_gid=data.get('game_gid'),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
        )


class PaginationInfo(graphene.ObjectType):
    """
    Pagination Information
    
    Provides pagination metadata for list queries.
    """
    
    class Meta:
        description = "分页信息"
    
    total = Int(required=True, description="总记录数")
    page = Int(required=True, description="当前页码")
    per_page = Int(required=True, description="每页记录数")
    total_pages = Int(required=True, description="总页数")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PaginationInfo':
        """Create PaginationInfo instance from dictionary."""
        return cls(
            total=data.get('total', 0),
            page=data.get('page', 1),
            per_page=data.get('per_page', 20),
            total_pages=data.get('total_pages', 1),
        )


class PaginatedEventsV2(graphene.ObjectType):
    """
    Paginated Events V2
    
    Represents a paginated list of events.
    """
    
    class Meta:
        description = "分页事件列表 (V2 API)"
    
    data = List(lambda: EventV2Type, required=True, description="事件列表")
    pagination = Field(lambda: PaginationInfo, required=True, description="分页信息")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PaginatedEventsV2':
        """Create PaginatedEventsV2 instance from dictionary."""
        events_data = data.get('data', [])
        pagination_data = data.get('pagination', {})
        
        events = [EventV2Type.from_dict(event) for event in events_data]
        pagination = PaginationInfo.from_dict(pagination_data)
        
        return cls(
            data=events,
            pagination=pagination
        )


class EventV2CreateInput(InputObjectType):
    """
    Event V2 Create Input
    
    Input type for creating a new event.
    """
    
    class Meta:
        description = "创建事件输入 (V2 API)"
    
    game_gid = Int(required=True, description="游戏业务GID")
    event_name = String(required=True, description="事件名称")
    event_name_cn = String(description="事件中文名称")
    description = String(description="事件描述")
    category_id = Int(description="分类ID")
    is_active = Boolean(description="是否活跃")


class EventV2UpdateInput(InputObjectType):
    """
    Event V2 Update Input
    
    Input type for updating an existing event.
    """
    
    class Meta:
        description = "更新事件输入 (V2 API)"
    
    event_name = String(description="事件名称")
    event_name_cn = String(description="事件中文名称")
    description = String(description="事件描述")
    category_id = Int(description="分类ID")
    is_active = Boolean(description="是否活跃")


class EventV2Result(graphene.ObjectType):
    """
    Event V2 Operation Result
    
    Result type for event operations.
    """
    
    class Meta:
        description = "事件操作结果 (V2 API)"
    
    success = Boolean(required=True, description="操作是否成功")
    message = String(description="操作消息")
    event = Field(lambda: EventV2Type, description="事件对象")
    errors = List(String, description="错误信息列表")
    
    @classmethod
    def success_result(cls, event: EventV2Type, message: str = "操作成功") -> 'EventV2Result':
        """Create a successful result."""
        return cls(
            success=True,
            message=message,
            event=event,
            errors=[]
        )
    
    @classmethod
    def error_result(cls, errors: list, message: str = "操作失败") -> 'EventV2Result':
        """Create an error result."""
        return cls(
            success=False,
            message=message,
            event=None,
            errors=errors
        )
