"""
Template GraphQL Type

Defines the GraphQL type for Canvas Flow Template entity.
"""

import graphene
from graphene import Int, String, Boolean
import logging

logger = logging.getLogger(__name__)


class TemplateType(graphene.ObjectType):
    """
    Template GraphQL Type

    Represents a canvas flow template.
    """

    class Meta:
        description = "画布流程模板"

    # Basic fields
    id = Int(required=True, description="模板ID")
    name = String(required=True, description="模板名称")
    description = String(description="模板描述")
    category = String(description="模板分类")
    game_gid = Int(description="关联游戏GID")
    config = String(description="模板配置JSON")
    is_active = Boolean(description="是否活跃")
    version = Int(description="版本号")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")

    @classmethod
    def from_dict(cls, data: dict) -> 'TemplateType':
        """Create TemplateType instance from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            game_gid=data.get('game_gid'),
            config=data.get('config'),
            is_active=bool(data.get('is_active', 1)),
            version=data.get('version', 1),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
        )
