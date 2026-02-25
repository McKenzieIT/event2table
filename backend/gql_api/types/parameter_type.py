"""
Parameter GraphQL Type

Defines the GraphQL type for Event Parameter entity.
"""

import graphene
from graphene import Field, Int, String, Boolean
import logging

logger = logging.getLogger(__name__)


class ParameterType(graphene.ObjectType):
    """
    Parameter GraphQL Type
    
    Represents an event parameter with its metadata.
    """
    
    class Meta:
        description = "事件参数"
    
    # Basic fields
    id = Int(required=True, description="参数ID")
    event_id = Int(required=True, description="事件ID")
    param_name = String(required=True, description="参数英文名")
    param_name_cn = String(description="参数中文名")
    template_id = Int(description="参数模板ID")
    param_type = String(description="参数类型")
    param_description = String(description="参数描述")
    json_path = String(description="JSON路径")
    is_active = Boolean(description="是否活跃")
    version = Int(description="版本号")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ParameterType':
        """Create ParameterType instance from dictionary."""
        return cls(
            id=data.get('id'),
            event_id=data.get('event_id'),
            param_name=data.get('param_name'),
            param_name_cn=data.get('param_name_cn'),
            template_id=data.get('template_id'),
            param_type=data.get('param_type') or data.get('template_name'),
            param_description=data.get('param_description') or data.get('description'),
            json_path=data.get('json_path'),
            is_active=bool(data.get('is_active', 1)),
            version=data.get('version', 1),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
        )
