"""
GraphQL Schema for Parameter Management

This module defines the GraphQL schema for advanced parameter management features including:
- Parameter type management and filtering
- Common parameter detection and synchronization
- Parameter change tracking
- Event field management

Author: Event2Table Development Team
Date: 2026-02-23
"""

import graphene
from graphene import ObjectType, Field, List, Int, String, Boolean, Float, Argument
from graphene import Enum
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class ParameterTypeEnum(Enum):
    """
    Parameter Type Enumeration

    Defines the supported data types for event parameters.
    """
    INT = "int"
    STRING = "string"
    ARRAY = "array"
    BOOLEAN = "boolean"
    MAP = "map"

    class Meta:
        description = "参数数据类型"


class ParameterFilterModeEnum(Enum):
    """
    Parameter Filter Mode Enumeration

    Defines filtering modes for parameter queries.
    """
    ALL = "all"
    COMMON = "common"
    NON_COMMON = "non_common"

    class Meta:
        description = "参数过滤模式"


class FieldTypeEnum(Enum):
    """
    Field Type Enumeration

    Defines categories of fields available for event configuration.
    """
    ALL = "all"
    PARAMS = "params"
    NON_COMMON = "non-common"
    COMMON = "common"
    BASE = "base"

    class Meta:
        description = "字段类型分类"


# ============================================================================
# TYPES
# ============================================================================

class ParameterManagementType(graphene.ObjectType):
    """
    Parameter Management GraphQL Type

    Extended parameter type with usage statistics and event associations.
    Includes advanced metadata for parameter analysis and management.
    """

    class Meta:
        description = "事件参数（管理类型）"

    # Basic fields
    id = Int(required=True, description="参数ID")
    event_id = Int(required=True, description="事件ID")
    param_name = String(required=True, description="参数英文名")
    param_name_cn = String(description="参数中文名")
    param_type = ParameterTypeEnum(description="参数类型")
    param_description = String(description="参数描述")
    json_path = String(description="JSON路径")
    is_active = Boolean(description="是否活跃")
    version = Int(description="版本号")

    # Statistics fields
    usage_count = Int(description="使用次数（跨事件）")
    events_count = Int(description="关联事件数量")
    is_common = Boolean(description="是否为公共参数")

    # Event association
    event_code = String(description="事件代码")
    event_name = String(description="事件名称")
    game_gid = Int(description="游戏GID")

    # Metadata
    created_at = String(description="创建时间")
    updated_at = String(description="更新时间")

    @classmethod
    def from_dict(cls, data: dict) -> 'ParameterManagementType':
        """Create ParameterManagementType instance from dictionary."""
        return cls(
            id=data.get('id'),
            event_id=data.get('event_id'),
            param_name=data.get('param_name'),
            param_name_cn=data.get('param_name_cn'),
            param_type=data.get('param_type'),
            param_description=data.get('param_description'),
            json_path=data.get('json_path'),
            is_active=bool(data.get('is_active', 1)),
            version=data.get('version', 1),
            usage_count=data.get('usage_count', 0),
            events_count=data.get('events_count', 0),
            is_common=bool(data.get('is_common', False)),
            event_code=data.get('event_code'),
            event_name=data.get('event_name'),
            game_gid=data.get('game_gid'),
            created_at=str(data.get('created_at')) if data.get('created_at') else None,
            updated_at=str(data.get('updated_at')) if data.get('updated_at') else None,
        )


class CommonParameterType(graphene.ObjectType):
    """
    Common Parameter GraphQL Type

    Represents parameters that appear across multiple events within a game.
    Includes occurrence statistics for commonality analysis.
    """

    class Meta:
        description = "公共参数"

    # Parameter identification
    param_name = String(required=True, description="参数名称")
    param_type = String(description="参数类型")
    param_description = String(description="参数描述")

    # Statistics
    occurrence_count = Int(required=True, description="出现次数（事件数）")
    total_events = Int(required=True, description="游戏总事件数")
    threshold = Float(description="公共参数阈值（百分比）")

    # Events using this parameter
    event_codes = List(String, description="使用该参数的事件代码列表")

    # Classification
    is_common = Boolean(description="是否为公共参数（超过阈值）")
    commonality_score = Float(description="公共性评分（0-1）")

    @classmethod
    def from_dict(cls, data: dict) -> 'CommonParameterType':
        """Create CommonParameterType instance from dictionary."""
        return cls(
            param_name=data.get('param_name'),
            param_type=data.get('param_type'),
            param_description=data.get('param_description'),
            occurrence_count=data.get('occurrence_count', 0),
            total_events=data.get('total_events', 0),
            threshold=data.get('threshold', 0.0),
            event_codes=data.get('event_codes', []),
            is_common=bool(data.get('is_common', False)),
            commonality_score=data.get('commonality_score', 0.0),
        )


class FieldTypeType(graphene.ObjectType):
    """
    Field Type GraphQL Type

    Represents a field available for event configuration in the Canvas system.
    Fields can be base fields (common to all events) or parameter fields.
    """

    class Meta:
        description = "事件字段"

    # Field identification
    name = String(required=True, description="字段名称")
    display_name = String(description="显示名称")
    type = FieldTypeEnum(description="字段类型")
    category = String(description="字段分类（base, common, param）")

    # Metadata
    is_common = Boolean(description="是否为公共字段")
    data_type = String(description="数据类型（int, string, array, boolean, map）")
    json_path = String(description="JSON路径（用于参数字段）")

    # Usage statistics
    usage_count = Int(description="使用次数")

    @classmethod
    def from_dict(cls, data: dict) -> 'FieldTypeType':
        """Create FieldTypeType instance from dictionary."""
        return cls(
            name=data.get('name'),
            display_name=data.get('display_name'),
            type=data.get('type'),
            category=data.get('category'),
            is_common=bool(data.get('is_common', False)),
            data_type=data.get('data_type'),
            json_path=data.get('json_path'),
            usage_count=data.get('usage_count', 0),
        )


class ParameterChangeType(graphene.ObjectType):
    """
    Parameter Change GraphQL Type

    Tracks modifications to parameter definitions over time.
    """

    class Meta:
        description = "参数变更记录"

    # Change identification
    id = Int(required=True, description="变更记录ID")
    parameter_id = Int(required=True, description="参数ID")
    param_name = String(required=True, description="参数名称")

    # Change details
    change_type = String(description="变更类型（create, update, delete）")
    old_value = String(description="旧值")
    new_value = String(description="新值")
    changed_field = String(description="变更字段")

    # Metadata
    changed_at = String(description="变更时间")
    changed_by = String(description="变更者")

    @classmethod
    def from_dict(cls, data: dict) -> 'ParameterChangeType':
        """Create ParameterChangeType instance from dictionary."""
        return cls(
            id=data.get('id'),
            parameter_id=data.get('parameter_id'),
            param_name=data.get('param_name'),
            change_type=data.get('change_type'),
            old_value=data.get('old_value'),
            new_value=data.get('new_value'),
            changed_field=data.get('changed_field'),
            changed_at=str(data.get('changed_at')) if data.get('changed_at') else None,
            changed_by=data.get('changed_by'),
        )


class BatchOperationResultType(graphene.ObjectType):
    """
    Batch Operation Result GraphQL Type

    Represents the result of a batch operation on multiple items.
    """

    class Meta:
        description = "批量操作结果"

    success = Boolean(required=True, description="操作是否成功")
    message = String(description="结果消息")
    total_count = Int(description="总数量")
    success_count = Int(description="成功数量")
    failed_count = Int(description="失败数量")
    errors = List(String, description="错误列表")

    @classmethod
    def from_dict(cls, data: dict) -> 'BatchOperationResultType':
        """Create BatchOperationResultType instance from dictionary."""
        return cls(
            success=data.get('success', False),
            message=data.get('message'),
            total_count=data.get('total_count', 0),
            success_count=data.get('success_count', 0),
            failed_count=data.get('failed_count', 0),
            errors=data.get('errors', []),
        )


# ============================================================================
# QUERY RESOLVERS
# ============================================================================

class ParameterManagementQueries(ObjectType):
    """
    Parameter Management Query Resolvers

    Provides advanced parameter management query operations.
    """

    # Query field definitions
    parameters_management = Field(
        List(ParameterManagementType),
        game_gid=Int(required=True, description="游戏GID"),
        mode=Argument(ParameterFilterModeEnum, default_value="all", description="过滤模式"),
        event_id=Int(description="事件ID（可选）"),
        description="查询参数列表（支持过滤和统计）"
    )

    common_parameters = Field(
        List(CommonParameterType),
        game_gid=Int(required=True, description="游戏GID"),
        threshold=Float(default_value=0.5, description="公共参数阈值（0-1）"),
        description="查询公共参数列表"
    )

    parameter_changes = Field(
        List(ParameterChangeType),
        game_gid=Int(required=True, description="游戏GID"),
        parameter_id=Int(description="参数ID（可选）"),
        limit=Int(default_value=50, description="返回数量限制"),
        description="查询参数变更记录"
    )

    event_fields = Field(
        List(FieldTypeType),
        event_id=Int(required=True, description="事件ID"),
        field_type=Argument(FieldTypeEnum, default_value="all", description="字段类型"),
        description="查询事件字段列表"
    )

    @staticmethod
    def resolve_parameters_management(root, info, game_gid: int, mode: str = "all", event_id: Optional[int] = None):
        """
        Resolve parameters with filtering and statistics.

        Args:
            root: GraphQL root object
            info: GraphQL resolve info
            game_gid: Game GID
            mode: Filter mode (all, common, non_common)
            event_id: Optional event ID filter

        Returns:
            List of ParameterManagementType objects
        """
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.core.data_access import Repositories

            # Get game_id from game_gid
            game_repo = Repositories.get('games')
            game = game_repo.find_by_gid(game_gid)
            if not game:
                logger.error(f"Game not found: game_gid={game_gid}")
                return []

            game_id = game['id']

            # Build query based on mode
            if mode == "common":
                # Only common parameters
                query = """
                    SELECT
                        ep.*,
                        le.event_code,
                        le.event_name,
                        le.game_gid,
                        COUNT(DISTINCT ep2.event_id) as usage_count,
                        COUNT(DISTINCT ep2.event_id) as events_count,
                        CASE WHEN COUNT(DISTINCT ep2.event_id) >= (
                            SELECT COUNT(*) * 0.5 FROM log_events WHERE game_gid = ?
                        ) THEN 1 ELSE 0 END as is_common
                    FROM event_params ep
                    INNER JOIN log_events le ON ep.event_id = le.id
                    INNER JOIN event_params ep2 ON ep.param_name = ep2.param_name
                    INNER JOIN log_events le2 ON ep2.event_id = le2.id AND le2.game_gid = ?
                    WHERE le.game_gid = ?
                    GROUP BY ep.id, le.event_code, le.event_name, le.game_gid
                    HAVING is_common = 1
                    ORDER BY usage_count DESC, ep.param_name
                """
                params = [game_gid, game_gid, game_gid]

            elif mode == "non_common":
                # Only non-common parameters
                query = """
                    SELECT
                        ep.*,
                        le.event_code,
                        le.event_name,
                        le.game_gid,
                        COUNT(DISTINCT ep2.event_id) as usage_count,
                        COUNT(DISTINCT ep2.event_id) as events_count,
                        0 as is_common
                    FROM event_params ep
                    INNER JOIN log_events le ON ep.event_id = le.id
                    LEFT JOIN event_params ep2 ON ep.param_name = ep2.param_name
                    LEFT JOIN log_events le2 ON ep2.event_id = le2.id AND le2.game_gid = ?
                    WHERE le.game_gid = ?
                    GROUP BY ep.id, le.event_code, le.event_name, le.game_gid
                    HAVING is_common = 0
                    ORDER BY usage_count DESC, ep.param_name
                """
                params = [game_gid, game_gid]

            else:  # mode == "all"
                # All parameters
                query = """
                    SELECT
                        ep.*,
                        le.event_code,
                        le.event_name,
                        le.game_gid,
                        COUNT(DISTINCT ep2.event_id) as usage_count,
                        COUNT(DISTINCT ep2.event_id) as events_count,
                        CASE WHEN COUNT(DISTINCT ep2.event_id) >= (
                            SELECT COUNT(*) * 0.5 FROM log_events WHERE game_gid = ?
                        ) THEN 1 ELSE 0 END as is_common
                    FROM event_params ep
                    INNER JOIN log_events le ON ep.event_id = le.id
                    LEFT JOIN event_params ep2 ON ep.param_name = ep2.param_name
                    LEFT JOIN log_events le2 ON ep2.event_id = le2.id AND le2.game_gid = ?
                    WHERE le.game_gid = ?
                    GROUP BY ep.id, le.event_code, le.event_name, le.game_gid
                    ORDER BY usage_count DESC, ep.param_name
                """
                params = [game_gid, game_gid, game_gid]

            # Add event_id filter if provided
            if event_id:
                query = query.replace("WHERE le.game_gid = ?", "WHERE le.game_gid = ? AND ep.event_id = ?")
                params.append(event_id)

            parameters = fetch_all_as_dict(query, tuple(params))
            return [ParameterManagementType.from_dict(param) for param in parameters]

        except Exception as e:
            logger.error(f"Error resolving parameters_management: {e}", exc_info=True)
            return []

    @staticmethod
    def resolve_common_parameters(root, info, game_gid: int, threshold: float = 0.5):
        """
        Resolve common parameters for a game.

        Args:
            root: GraphQL root object
            info: GraphQL resolve info
            game_gid: Game GID
            threshold: Commonality threshold (0-1)

        Returns:
            List of CommonParameterType objects
        """
        try:
            from backend.core.utils import fetch_all_as_dict

            # Get total event count
            total_events = fetch_all_as_dict(
                "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
                (game_gid,)
            )[0]['count']

            if total_events == 0:
                return []

            # Calculate threshold count
            threshold_count = int(total_events * threshold)

            # Query common parameters
            query = """
                SELECT
                    param_name,
                    param_type,
                    param_description,
                    COUNT(DISTINCT event_id) as occurrence_count,
                    ? as total_events,
                    ? as threshold,
                    GROUP_CONCAT(DISTINCT le.event_code) as event_codes,
                    CASE WHEN COUNT(DISTINCT event_id) >= ? THEN 1 ELSE 0 END as is_common,
                    CAST(COUNT(DISTINCT event_id) AS FLOAT) / ? as commonality_score
                FROM event_params ep
                INNER JOIN log_events le ON ep.event_id = le.id
                WHERE le.game_gid = ?
                GROUP BY param_name, param_type, param_description
                HAVING is_common = 1
                ORDER BY occurrence_count DESC, param_name
            """

            params = fetch_all_as_dict(query, (total_events, threshold, threshold_count, total_events, game_gid))

            # Parse event_codes
            for param in params:
                if param.get('event_codes'):
                    param['event_codes'] = param['event_codes'].split(',')
                else:
                    param['event_codes'] = []

            return [CommonParameterType.from_dict(param) for param in params]

        except Exception as e:
            logger.error(f"Error resolving common_parameters: {e}", exc_info=True)
            return []

    @staticmethod
    def resolve_parameter_changes(root, info, game_gid: int, parameter_id: Optional[int] = None, limit: int = 50):
        """
        Resolve parameter change history.

        Args:
            root: GraphQL root object
            info: GraphQL resolve info
            game_gid: Game GID
            parameter_id: Optional parameter ID filter
            limit: Result limit

        Returns:
            List of ParameterChangeType objects
        """
        try:
            from backend.core.utils import fetch_all_as_dict

            # Build query
            if parameter_id:
                query = """
                    SELECT
                        pc.*,
                        ep.param_name
                    FROM parameter_changes pc
                    INNER JOIN event_params ep ON pc.parameter_id = ep.id
                    WHERE pc.parameter_id = ?
                    ORDER BY pc.changed_at DESC
                    LIMIT ?
                """
                params = (parameter_id, limit)
            else:
                query = """
                    SELECT
                        pc.*,
                        ep.param_name
                    FROM parameter_changes pc
                    INNER JOIN event_params ep ON pc.parameter_id = ep.id
                    INNER JOIN log_events le ON ep.event_id = le.id
                    WHERE le.game_gid = ?
                    ORDER BY pc.changed_at DESC
                    LIMIT ?
                """
                params = (game_gid, limit)

            changes = fetch_all_as_dict(query, params)
            return [ParameterChangeType.from_dict(change) for change in changes]

        except Exception as e:
            logger.error(f"Error resolving parameter_changes: {e}", exc_info=True)
            return []

    @staticmethod
    def resolve_event_fields(root, info, event_id: int, field_type: str = "all"):
        """
        Resolve event fields by type.

        Args:
            root: GraphQL root object
            info: GraphQL resolve info
            event_id: Event ID
            field_type: Field type filter (all, params, non-common, common, base)

        Returns:
            List of FieldTypeType objects
        """
        try:
            from backend.core.utils import fetch_all_as_dict

            # Base fields (common to all events)
            base_fields = [
                {
                    'name': 'ds',
                    'display_name': '日期',
                    'type': 'base',
                    'category': 'base',
                    'is_common': True,
                    'data_type': 'string',
                    'json_path': None,
                    'usage_count': 0
                },
                {
                    'name': 'role_id',
                    'display_name': '角色ID',
                    'type': 'base',
                    'category': 'base',
                    'is_common': True,
                    'data_type': 'int',
                    'json_path': None,
                    'usage_count': 0
                },
                {
                    'name': 'account_id',
                    'display_name': '账号ID',
                    'type': 'base',
                    'category': 'base',
                    'is_common': True,
                    'data_type': 'string',
                    'json_path': None,
                    'usage_count': 0
                },
                {
                    'name': 'utdid',
                    'display_name': '设备ID',
                    'type': 'base',
                    'category': 'base',
                    'is_common': True,
                    'data_type': 'string',
                    'json_path': None,
                    'usage_count': 0
                },
                {
                    'name': 'envinfo',
                    'display_name': '环境信息',
                    'type': 'base',
                    'category': 'base',
                    'is_common': True,
                    'data_type': 'string',
                    'json_path': None,
                    'usage_count': 0
                },
                {
                    'name': 'tm',
                    'display_name': '时间戳',
                    'type': 'base',
                    'category': 'base',
                    'is_common': True,
                    'data_type': 'int',
                    'json_path': None,
                    'usage_count': 0
                },
                {
                    'name': 'ts',
                    'display_name': '时间戳（字符串）',
                    'type': 'base',
                    'category': 'base',
                    'is_common': True,
                    'data_type': 'string',
                    'json_path': None,
                    'usage_count': 0
                }
            ]

            # Get parameter fields
            query = """
                SELECT
                    ep.param_name as name,
                    ep.param_name_cn as display_name,
                    ep.param_type as data_type,
                    ep.json_path,
                    CASE
                        WHEN COUNT(DISTINCT ep2.event_id) >= (
                            SELECT COUNT(*) * 0.5 FROM log_events WHERE game_gid = le.game_gid
                        ) THEN 'common'
                        ELSE 'param'
                    END as category,
                    CASE
                        WHEN COUNT(DISTINCT ep2.event_id) >= (
                            SELECT COUNT(*) * 0.5 FROM log_events WHERE game_gid = le.game_gid
                        ) THEN 1 ELSE 0
                    END as is_common,
                    COUNT(DISTINCT ep2.event_id) as usage_count
                FROM event_params ep
                INNER JOIN log_events le ON ep.event_id = le.id
                LEFT JOIN event_params ep2 ON ep.param_name = ep2.param_name
                LEFT JOIN log_events le2 ON ep2.event_id = le2.id AND le2.game_gid = le.game_gid
                WHERE ep.event_id = ?
                GROUP BY ep.id, le.game_gid
                ORDER BY is_common DESC, usage_count DESC, ep.param_name
            """

            param_fields = fetch_all_as_dict(query, (event_id,))

            # Add type field to param fields
            for field in param_fields:
                field['type'] = 'params'

            # Combine and filter based on field_type
            all_fields = base_fields + param_fields

            if field_type == "all":
                filtered = all_fields
            elif field_type == "params":
                filtered = [f for f in all_fields if f['type'] == 'params']
            elif field_type == "non-common":
                filtered = [f for f in all_fields if not f['is_common']]
            elif field_type == "common":
                filtered = [f for f in all_fields if f['is_common']]
            elif field_type == "base":
                filtered = [f for f in all_fields if f['type'] == 'base']
            else:
                filtered = all_fields

            return [FieldTypeType.from_dict(field) for field in filtered]

        except Exception as e:
            logger.error(f"Error resolving event_fields: {e}", exc_info=True)
            return []


# ============================================================================
# MUTATION RESOLVERS
# ============================================================================

class ChangeParameterTypeMutation(graphene.Mutation):
    """
    Change Parameter Type Mutation

    Updates the data type of an existing parameter.
    """

    class Arguments:
        parameter_id = Int(required=True, description="参数ID")
        new_type = Argument(ParameterTypeEnum, required=True, description="新类型")

    # Output fields
    success = Boolean(description="操作是否成功")
    message = String(description="结果消息")
    parameter = Field(ParameterManagementType, description="更新后的参数")

    def mutate(self, info, parameter_id: int, new_type: str):
        """Execute mutation."""
        from backend.gql_api.resolvers.parameter_resolvers import mutate_change_parameter_type

        result = mutate_change_parameter_type(info, parameter_id, new_type)

        # Convert dict result to Mutation object
        return ChangeParameterTypeMutation(
            success=result['success'],
            message=result['message'],
            parameter=ParameterManagementType.from_dict(result['parameter']) if result.get('parameter') else None
        )


class AutoSyncCommonParametersMutation(graphene.Mutation):
    """
    Auto Sync Common Parameters Mutation

    Automatically detects and syncs common parameters across all events in a game.
    """

    class Arguments:
        game_gid = Int(required=True, description="游戏GID")
        threshold = Float(description="公共参数阈值（0-1），默认0.5")

    # Output fields
    success = Boolean(description="操作是否成功")
    message = String(description="结果消息")
    result = Field(BatchOperationResultType, description="批量操作结果")

    def mutate(self, info, game_gid: int, threshold: Optional[float] = 0.5):
        """Execute mutation."""
        from backend.gql_api.resolvers.parameter_resolvers import mutate_auto_sync_common_parameters

        result = mutate_auto_sync_common_parameters(info, game_gid, False)  # force_recalculate defaults to False

        # Convert dict result to Mutation object
        return AutoSyncCommonParametersMutation(
            success=result['success'],
            message=result['message'],
            result=BatchOperationResultType.from_dict(result['result']) if result.get('result') else None
        )


class BatchAddFieldsToCanvasMutation(graphene.Mutation):
    """
    Batch Add Fields to Canvas Mutation

    Adds multiple fields to a Canvas node configuration.
    """

    class Arguments:
        event_id = Int(required=True, description="事件ID")
        field_type = Argument(FieldTypeEnum, required=True, description="字段类型")

    # Output fields
    success = Boolean(description="操作是否成功")
    message = String(description="结果消息")
    result = Field(BatchOperationResultType, description="批量操作结果")

    def mutate(self, info, event_id: int, field_type: str):
        """Execute mutation."""
        from backend.gql_api.resolvers.parameter_resolvers import mutate_batch_add_fields_to_canvas

        result = mutate_batch_add_fields_to_canvas(info, event_id, field_type)

        # Convert dict result to Mutation object
        return BatchAddFieldsToCanvasMutation(
            success=result['success'],
            message=result['message'],
            result=BatchOperationResultType.from_dict(result['result']) if result.get('result') else None
        )


class ParameterManagementMutations(ObjectType):
    """
    Parameter Management Mutation Resolvers

    Provides advanced parameter management mutation operations.
    """

    # Mutation field definitions
    change_parameter_type = ChangeParameterTypeMutation.Field(
        description="修改参数类型"
    )

    auto_sync_common_parameters = AutoSyncCommonParametersMutation.Field(
        description="自动同步公共参数"
    )

    batch_add_fields_to_canvas = BatchAddFieldsToCanvasMutation.Field(
        description="批量添加字段到画布"
    )
