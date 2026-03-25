"""
Batch Operation Types Module

Provides GraphQL types for batch operations.
"""

from typing import Any, Dict
from typing import List as TypingList

import graphene
from graphene import Boolean, Int, List, String


class BatchOperationErrorType(graphene.ObjectType):
    """批量操作错误类型"""

    class Meta:
        description = "批量操作错误信息"

    id = Int(required=True, description="失败的ID")
    error = String(required=True, description="错误消息")

    @classmethod
    def from_dict(cls, data: dict) -> 'BatchOperationErrorType':
        """Create BatchOperationErrorType instance from dictionary."""
        return cls(
            id=data.get('id'),
            error=data.get('error'),
        )


class BatchOperationResultType(graphene.ObjectType):
    """批量操作结果类型"""

    class Meta:
        description = "批量操作结果"

    success = Boolean(required=True, description="操作是否成功")
    message = String(description="操作消息")
    affected_count = Int(required=True, description="影响的数量")
    failed_count = Int(required=True, description="失败的数量")
    errors = List(BatchOperationErrorType, description="错误列表")

    @classmethod
    def success_result(
        cls, affected_count: int, message: str = "批量操作成功"
    ) -> 'BatchOperationResultType':
        """Create a successful result."""
        return cls(
            success=True, message=message, affected_count=affected_count, failed_count=0, errors=[]
        )

    @classmethod
    def partial_success_result(
        cls,
        affected_count: int,
        failed_count: int,
        errors: TypingList[Dict[str, Any]],
        message: str = "部分成功",
    ) -> 'BatchOperationResultType':
        """Create a partial success result."""
        error_types = [BatchOperationErrorType.from_dict(e) for e in errors]
        return cls(
            success=False,
            message=message,
            affected_count=affected_count,
            failed_count=failed_count,
            errors=error_types,
        )

    @classmethod
    def failure_result(
        cls, message: str, errors: TypingList[Dict[str, Any]] | None = None
    ) -> 'BatchOperationResultType':
        """Create a failure result."""
        error_types = [BatchOperationErrorType.from_dict(e) for e in errors] if errors else []
        return cls(
            success=False,
            message=message,
            affected_count=0,
            failed_count=len(errors) if errors else 0,
            errors=error_types,
        )


class EventUpdateInput(graphene.InputObjectType):
    """Event update input for batch operations"""

    event_name = String(description="事件名称")
    event_name_cn = String(description="事件中文名称")
    category_id = Int(description="分类ID")
    include_in_common_params = Int(description="是否包含在通用参数中")


class FlowUpdateInput(graphene.InputObjectType):
    """Flow update input for batch operations"""

    name = String(description="流程名称")
    description = String(description="流程描述")
    is_active = Int(description="是否活跃")
