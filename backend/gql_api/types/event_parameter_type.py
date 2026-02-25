"""
Event Parameter GraphQL Types

Defines the GraphQL types for Event Parameter extended functionality.
"""

import graphene
from graphene import Int, String, Boolean, List
import logging

logger = logging.getLogger(__name__)


class ParamVersionType(graphene.ObjectType):
    """
    Parameter Version GraphQL Type

    Represents a version history entry for a parameter.
    """

    class Meta:
        description = "参数版本历史"

    id = Int(required=True, description="版本ID")
    param_id = Int(required=True, description="参数ID")
    version = Int(description="版本号")
    changes = String(description="变更内容JSON")
    changed_by = String(description="变更人")
    created_at = String(description="创建时间")

    @classmethod
    def from_dict(cls, data: dict) -> 'ParamVersionType':
        """Create ParamVersionType instance from dictionary."""
        return cls(
            id=data.get('id'),
            param_id=data.get('param_id'),
            version=data.get('version'),
            changes=data.get('changes'),
            changed_by=data.get('changed_by'),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
        )


class ParamConfigType(graphene.ObjectType):
    """
    Parameter Configuration GraphQL Type

    Represents configuration for a parameter.
    """

    class Meta:
        description = "参数配置"

    id = Int(required=True, description="配置ID")
    param_id = Int(required=True, description="参数ID")
    array_expand = Boolean(description="是否展开数组")
    map_expand = Boolean(description="是否展开Map")
    custom_hql_template = String(description="自定义HQL模板")
    output_field_name = String(description="输出字段名")
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")

    @classmethod
    def from_dict(cls, data: dict) -> 'ParamConfigType':
        """Create ParamConfigType instance from dictionary."""
        return cls(
            id=data.get('id'),
            param_id=data.get('param_id'),
            array_expand=bool(data.get('array_expand', 0)),
            map_expand=bool(data.get('map_expand', 0)),
            custom_hql_template=data.get('custom_hql_template'),
            output_field_name=data.get('output_field_name'),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
        )


class ValidationRuleType(graphene.ObjectType):
    """
    Validation Rule GraphQL Type

    Represents a validation rule for a parameter.
    """

    class Meta:
        description = "参数验证规则"

    id = Int(required=True, description="规则ID")
    param_id = Int(required=True, description="参数ID")
    rule_type = String(description="规则类型")
    rule_config = String(description="规则配置JSON")
    error_message = String(description="错误消息")
    is_active = Boolean(description="是否活跃")
    created_at = String(description="创建时间")

    @classmethod
    def from_dict(cls, data: dict) -> 'ValidationRuleType':
        """Create ValidationRuleType instance from dictionary."""
        return cls(
            id=data.get('id'),
            param_id=data.get('param_id'),
            rule_type=data.get('rule_type'),
            rule_config=data.get('rule_config'),
            error_message=data.get('error_message'),
            is_active=bool(data.get('is_active', 1)),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
        )


class EventParameterExtendedType(graphene.ObjectType):
    """
    Extended Event Parameter GraphQL Type

    Represents an event parameter with extended information.
    """

    class Meta:
        description = "扩展事件参数"

    id = Int(required=True, description="参数ID")
    event_id = Int(required=True, description="事件ID")
    param_name = String(required=True, description="参数英文名")
    param_name_cn = String(description="参数中文名")
    param_type = String(description="参数类型")
    json_path = String(description="JSON路径")
    is_active = Boolean(description="是否活跃")
    version = Int(description="版本号")
    config = graphene.Field(ParamConfigType, description="参数配置")
    latest_version = graphene.Field(ParamVersionType, description="最新版本")

    @classmethod
    def from_dict(cls, data: dict) -> 'EventParameterExtendedType':
        """Create EventParameterExtendedType instance from dictionary."""
        return cls(
            id=data.get('id'),
            event_id=data.get('event_id'),
            param_name=data.get('param_name'),
            param_name_cn=data.get('param_name_cn'),
            param_type=data.get('param_type'),
            json_path=data.get('json_path'),
            is_active=bool(data.get('is_active', 1)),
            version=data.get('version', 1),
        )
