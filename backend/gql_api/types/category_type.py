"""
Category GraphQL Type

Defines the GraphQL type for Category entity.
"""

import graphene
from graphene import Field, List, Int, String
import logging

logger = logging.getLogger(__name__)


class CategoryType(graphene.ObjectType):
    """
    Category GraphQL Type

    Represents an event category entity.
    """

    class Meta:
        description = "事件分类实体"

    # Basic fields
    id = Int(required=True, description="分类ID")
    name = String(required=True, description="分类名称")
    description = String(description="分类描述")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")

    # Computed fields
    event_count = Int(description="事件数量")

    @classmethod
    def from_dict(cls, data: dict) -> 'CategoryType':
        """Create CategoryType instance from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
            event_count=data.get('event_count', 0),
        )
