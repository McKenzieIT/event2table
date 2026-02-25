"""
Node GraphQL Type

Defines the GraphQL type for Canvas Node entity.
"""

import graphene
from graphene import Int, String, Boolean, Float
import logging

logger = logging.getLogger(__name__)


class NodeType(graphene.ObjectType):
    """
    Node GraphQL Type

    Represents a canvas node configuration.
    """

    class Meta:
        description = "画布节点配置"

    # Basic fields
    id = Int(required=True, description="节点ID")
    name = String(required=True, description="节点名称")
    description = String(description="节点描述")
    game_gid = Int(description="关联游戏GID")
    node_type = String(description="节点类型")
    config = String(description="节点配置JSON")
    position_x = Float(description="X坐标")
    position_y = Float(description="Y坐标")
    is_active = Boolean(description="是否活跃")
    version = Int(description="版本号")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")

    @classmethod
    def from_dict(cls, data: dict) -> 'NodeType':
        """Create NodeType instance from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            game_gid=data.get('game_gid'),
            node_type=data.get('node_type'),
            config=data.get('config'),
            position_x=data.get('position_x', 0),
            position_y=data.get('position_y', 0),
            is_active=bool(data.get('is_active', 1)),
            version=data.get('version', 1),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
        )


class FlowType(graphene.ObjectType):
    """
    Flow GraphQL Type

    Represents a canvas flow configuration.
    """

    class Meta:
        description = "画布流程配置"

    # Basic fields
    id = Int(required=True, description="流程ID")
    name = String(required=True, description="流程名称")
    description = String(description="流程描述")
    game_gid = Int(description="关联游戏GID")
    flow_type = String(description="流程类型")
    config = String(description="流程配置JSON")
    nodes = String(description="节点数据JSON")
    edges = String(description="边数据JSON")
    is_active = Boolean(description="是否活跃")
    version = Int(description="版本号")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")

    @classmethod
    def from_dict(cls, data: dict) -> 'FlowType':
        """Create FlowType instance from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            game_gid=data.get('game_gid'),
            flow_type=data.get('flow_type'),
            config=data.get('config'),
            nodes=data.get('nodes'),
            edges=data.get('edges'),
            is_active=bool(data.get('is_active', 1)),
            version=data.get('version', 1),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
        )
