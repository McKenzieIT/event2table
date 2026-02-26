"""
Game V2 GraphQL Type

Defines the GraphQL types for Game V2 API with enhanced features.
"""

import graphene
from graphene import Field, List, Int, String, Boolean, InputObjectType
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GameV2Type(graphene.ObjectType):
    """
    Game V2 GraphQL Type
    
    Represents a game entity with V2 API enhancements.
    """
    
    class Meta:
        description = "游戏实体 (V2 API)"
    
    # Basic fields
    id = Int(required=True, description="数据库ID")
    gid = Int(required=True, description="游戏业务GID")
    name = String(required=True, description="游戏名称")
    name_cn = String(description="游戏中文名称")
    ods_db = String(required=True, description="ODS数据库名称")
    is_active = Boolean(required=True, description="是否活跃")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")
    description = String(description="游戏描述")
    
    # Computed fields
    event_count = Int(description="事件数量")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameV2Type':
        """Create GameV2Type instance from dictionary."""
        return cls(
            id=data.get('id'),
            gid=data.get('gid'),
            name=data.get('name'),
            name_cn=data.get('name_cn'),
            ods_db=data.get('ods_db'),
            is_active=data.get('is_active', True),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
            description=data.get('description'),
            event_count=data.get('event_count', 0),
        )


class GameV2CreateInput(InputObjectType):
    """
    Game V2 Create Input
    
    Input type for creating a new game.
    """
    
    class Meta:
        description = "创建游戏输入 (V2 API)"
    
    gid = Int(required=True, description="游戏业务GID")
    name = String(required=True, description="游戏名称")
    name_cn = String(description="游戏中文名称")
    ods_db = String(required=True, description="ODS数据库名称")
    description = String(description="游戏描述")
    is_active = Boolean(description="是否活跃")


class GameV2UpdateInput(InputObjectType):
    """
    Game V2 Update Input
    
    Input type for updating an existing game.
    """
    
    class Meta:
        description = "更新游戏输入 (V2 API)"
    
    name = String(description="游戏名称")
    name_cn = String(description="游戏中文名称")
    ods_db = String(description="ODS数据库名称")
    description = String(description="游戏描述")
    is_active = Boolean(description="是否活跃")


class GameV2Result(graphene.ObjectType):
    """
    Game V2 Operation Result
    
    Result type for game operations.
    """
    
    class Meta:
        description = "游戏操作结果 (V2 API)"
    
    success = Boolean(required=True, description="操作是否成功")
    message = String(description="操作消息")
    game = Field(lambda: GameV2Type, description="游戏对象")
    errors = List(String, description="错误信息列表")
    
    @classmethod
    def success_result(cls, game: GameV2Type, message: str = "操作成功") -> 'GameV2Result':
        """Create a successful result."""
        return cls(
            success=True,
            message=message,
            game=game,
            errors=[]
        )
    
    @classmethod
    def error_result(cls, errors: list, message: str = "操作失败") -> 'GameV2Result':
        """Create an error result."""
        return cls(
            success=False,
            message=message,
            game=None,
            errors=errors
        )


class BatchOperationResult(graphene.ObjectType):
    """
    Batch Operation Result
    
    Result type for batch operations.
    """
    
    class Meta:
        description = "批量操作结果"
    
    success = Boolean(required=True, description="操作是否成功")
    message = String(description="操作消息")
    deleted_count = Int(description="删除数量")
    failed_count = Int(description="失败数量")
    errors = List(String, description="错误信息列表")
    
    @classmethod
    def success_result(cls, deleted_count: int, message: str = "批量操作成功") -> 'BatchOperationResult':
        """Create a successful batch result."""
        return cls(
            success=True,
            message=message,
            deleted_count=deleted_count,
            failed_count=0,
            errors=[]
        )
    
    @classmethod
    def error_result(cls, errors: list, message: str = "批量操作失败") -> 'BatchOperationResult':
        """Create an error batch result."""
        return cls(
            success=False,
            message=message,
            deleted_count=0,
            failed_count=len(errors),
            errors=errors
        )


class OperationResult(graphene.ObjectType):
    """
    Generic Operation Result
    
    Result type for generic operations.
    """
    
    class Meta:
        description = "通用操作结果"
    
    success = Boolean(required=True, description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息列表")
    
    @classmethod
    def success_result(cls, message: str = "操作成功") -> 'OperationResult':
        """Create a successful result."""
        return cls(
            success=True,
            message=message,
            errors=[]
        )
    
    @classmethod
    def error_result(cls, errors: list, message: str = "操作失败") -> 'OperationResult':
        """Create an error result."""
        return cls(
            success=False,
            message=message,
            errors=errors
        )
