# ⚠️ PERFORMANCE: N+1 query detected - needs refactor
# TODO: Replace loop queries with JOIN or prefetch

# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
"""
GraphQL Parameter Management Resolvers

This module provides GraphQL resolver implementations for parameter management features.
Resolvers use Application Services (not direct repository access) following the DDD architecture.

Author: Event2Table Development Team
Date: 2026-02-23
"""

import logging
from typing import Any, Dict, List, Optional

from graphql.error import GraphQLError

from backend.core.cache.decorators import cached
from backend.gql_api.schema_parameter_management import (
    BatchOperationResultType,
    CommonParameterType,
    FieldTypeType,
    ParameterChangeType,
    ParameterManagementType,
)
from backend.services.events.event_builder_app_service import EventBuilderAppService
from backend.services.parameters.parameter_app_service_enhanced import (
    ParameterAppServiceEnhanced,
    get_parameter_app_service,
)

logger = logging.getLogger(__name__)


# ============================================================================
# QUERY RESOLVERS
# ============================================================================


@cached(ttl=1800, key_prefix="parameters_management")
def resolve_parameters_management(
    info, game_gid: int, mode: str = 'all', event_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Resolve parameters_management query

    PERF: Cache decorator improves performance significantly

    Args:
        info: GraphQL resolve info
        game_gid: Game GID
        mode: Filter mode (all, common, non_common)
        event_id: Optional event ID filter

    Returns:
        List of parameter dictionaries

    Raises:
        GraphQLError: If service operation fails
    """
    try:
        service = get_parameter_app_service()

        # Validate mode
        valid_modes = ['all', 'common', 'non_common']
        if mode not in valid_modes:
            raise GraphQLError(f"Invalid mode: {mode}. Must be one of: {', '.join(valid_modes)}")

        # Get filtered parameters from service
        parameters = service.get_filtered_parameters(
            game_gid=game_gid, mode=mode, event_id=event_id
        )

        logger.info(
            f"Resolved parameters_management: game_gid={game_gid}, "
            f"mode={mode}, count={len(parameters)}"
        )

        return parameters

    except ValueError as e:
        logger.error(f"Validation error in resolve_parameters_management: {e}")
        raise GraphQLError(str(e))
    except Exception as e:
        logger.error(f"Error resolving parameters_management: {e}", exc_info=True)
        raise GraphQLError(f"Failed to fetch parameters: {str(e)}")


@cached(ttl=1800, key_prefix="common_parameters")
def resolve_common_parameters(info, game_gid: int, threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Resolve common_parameters query

    PERF: Cache decorator improves performance significantly

    Args:
        info: GraphQL resolve info
        game_gid: Game GID
        threshold: Commonality threshold (0-1)

    Returns:
        List of common parameter dictionaries

    Raises:
        GraphQLError: If service operation fails
    """
    try:
        service = get_parameter_app_service()

        # Validate threshold
        if not 0 <= threshold <= 1:
            raise GraphQLError(f"Invalid threshold: {threshold}. Must be between 0 and 1")

        # Get total events count for percentage calculation
        from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict

        total_events_result = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?", (game_gid,)
        )
        # FIX: fetch_one_as_dict returns Dict directly, not List
        total_events = total_events_result['count'] if total_events_result else 0

        if total_events == 0:
            return []

        # Use SQL GROUP BY aggregation instead of Python loops
        # This is O(n) instead of O(n²) and much faster
        threshold_count = int(total_events * threshold)

        query = """
            SELECT
                ep.param_name,
                ep.param_type,
                ep.param_description,
                COUNT(DISTINCT ep.event_id) as occurrence_count,
                GROUP_CONCAT(DISTINCT le.event_code) as event_codes
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = ?
            GROUP BY ep.param_name, ep.param_type, ep.param_description
            HAVING COUNT(DISTINCT ep.event_id) >= ?
            ORDER BY occurrence_count DESC
        """

        aggregated_params = fetch_all_as_dict(query, (game_gid, threshold_count))

        # Convert to GraphQL format
        common_params = []
        for param in aggregated_params:
            commonality_score = param['occurrence_count'] / total_events if total_events > 0 else 0
            common_params.append(
                {
                    'param_name': param['param_name'],
                    'param_type': param['param_type'],
                    'param_description': param['param_description'] or '',
                    'occurrence_count': param['occurrence_count'],
                    'event_codes': param['event_codes'].split(',') if param['event_codes'] else [],
                    'total_events': total_events,
                    'threshold': threshold,
                    'is_common': True,
                    'commonality_score': commonality_score,
                }
            )

        logger.info(
            f"Resolved common_parameters: game_gid={game_gid}, "
            f"threshold={threshold}, count={len(common_params)}"
        )

        return common_params

    except GraphQLError:
        raise
    except Exception as e:
        logger.error(f"Error resolving common_parameters: {e}", exc_info=True)
        raise GraphQLError(f"Failed to fetch common parameters: {str(e)}")


@cached(ttl=600, key_prefix="parameter_changes")
def resolve_parameter_changes(
    info, game_gid: int, parameter_id: Optional[int] = None, limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Resolve parameter_changes query

    PERF: Cache decorator with shorter TTL (10 min) for change history

    Args:
        info: GraphQL resolve info
        game_gid: Game GID
        parameter_id: Optional parameter ID filter
        limit: Result limit

    Returns:
        List of parameter change dictionaries

    Raises:
        GraphQLError: If service operation fails

    Note:
        This function queries the parameter_changes table to retrieve the
        change history of parameters. The table is created automatically if
        it doesn't exist. Changes are populated by domain events when
        parameters are modified.
    """
    try:
        import sqlite3

        from backend.core.database.database import get_db_connection
        from backend.core.utils.converters import fetch_all_as_dict

        # Validate limit
        if limit < 1 or limit > 1000:
            raise GraphQLError(f"Invalid limit: {limit}. Must be between 1 and 1000")

        # Validate game_gid
        if not game_gid or game_gid < 1:
            raise GraphQLError(f"Invalid game_gid: {game_gid}. Must be a positive integer")

        # Ensure parameter_changes table exists
        _ensure_parameter_changes_table()

        # Build query with optional parameter_id filter
        base_query = """
            SELECT
                pc.id,
                pc.parameter_id,
                pc.old_value,
                pc.new_value,
                pc.change_type,
                pc.changed_at,
                pc.changed_by,
                p.param_name,
                p.param_type,
                e.event_code,
                u.username as changed_by_username
            FROM parameter_changes pc
            LEFT JOIN parameters p ON pc.parameter_id = p.id
            LEFT JOIN log_events e ON p.event_id = e.id
            LEFT JOIN users u ON pc.changed_by = u.id
            WHERE e.game_gid = ?
        """

        params = [game_gid]

        # Add parameter_id filter if provided
        if parameter_id is not None:
            if parameter_id < 1:
                raise GraphQLError(
                    f"Invalid parameter_id: {parameter_id}. Must be a positive integer"
                )
            base_query += " AND pc.parameter_id = ?"
            params.append(parameter_id)

        # Add ordering and limit
        base_query += " ORDER BY pc.changed_at DESC LIMIT ?"
        params.append(limit)

        # Execute query
        changes = fetch_all_as_dict(base_query, tuple(params))

        # Transform results to GraphQL format
        result = []
        for change in changes:
            result.append(
                {
                    'id': change.get('id'),
                    'parameter_id': change.get('parameter_id'),
                    'param_name': change.get('param_name'),
                    'param_type': change.get('param_type'),
                    'event_code': change.get('event_code'),
                    'old_value': change.get('old_value'),
                    'new_value': change.get('new_value'),
                    'change_type': change.get('change_type'),
                    'changed_at': change.get('changed_at'),
                    'changed_by': change.get('changed_by'),
                    'changed_by_username': change.get('changed_by_username'),
                }
            )

        logger.info(
            f"Resolved parameter_changes: game_gid={game_gid}, "
            f"parameter_id={parameter_id}, count={len(result)}"
        )

        return result

    except GraphQLError:
        raise
    except Exception as e:
        logger.error(f"Error resolving parameter_changes: {e}", exc_info=True)
        raise GraphQLError(f"Failed to fetch parameter changes: {str(e)}")


@cached(ttl=1800, key_prefix="event_fields")
def resolve_event_fields(info, event_id: int, field_type: str = 'all') -> List[Dict[str, Any]]:
    """
    Resolve event_fields query for EventBuilder

    PERF: Cache decorator improves performance significantly

    Args:
        info: GraphQL resolve info
        event_id: Event ID
        field_type: Field type filter (all, params, non-common, common, base)

    Returns:
        List of field dictionaries

    Raises:
        GraphQLError: If service operation fails
    """
    try:
        service = EventBuilderAppService()

        # Validate field_type
        valid_types = ['all', 'param', 'non_common', 'common', 'base']
        if field_type not in valid_types:
            raise GraphQLError(
                f"Invalid field_type: {field_type}. Must be one of: {', '.join(valid_types)}"
            )

        # Get fields from service
        fields = service.get_fields_by_type(event_id=event_id, field_type=field_type)

        # Batch calculate field usage (avoid N+1 query)
        field_names = [f.get('name') for f in fields if f.get('name')]
        usage_stats = _calculate_field_usage_batch(field_names, event_id)

        # Transform to GraphQL format
        graphql_fields = []
        for field in fields:
            field_name = field.get('name')
            graphql_field = {
                'name': field_name,
                'display_name': field.get('description', field.get('name')),
                'type': field.get('type'),
                'category': _determine_field_category(field),
                'is_common': field.get('is_common', False),
                'data_type': _infer_data_type(field),
                'json_path': field.get('json_path'),
                'usage_count': usage_stats.get(field_name, 0),
            }
            graphql_fields.append(graphql_field)

        logger.info(
            f"Resolved event_fields: event_id={event_id}, "
            f"field_type={field_type}, count={len(graphql_fields)}"
        )

        return graphql_fields

    except ValueError as e:
        logger.error(f"Validation error in resolve_event_fields: {e}")
        raise GraphQLError(str(e))
    except Exception as e:
        logger.error(f"Error resolving event_fields: {e}", exc_info=True)
        raise GraphQLError(f"Failed to fetch event fields: {str(e)}")


# ============================================================================
# MUTATION RESOLVERS
# ============================================================================


def mutate_change_parameter_type(info, parameter_id: int, new_type: str) -> Dict[str, Any]:
    """
    Change parameter type mutation

    Args:
        info: GraphQL resolve info
        parameter_id: Parameter ID
        new_type: New parameter type

    Returns:
        Mutation result with success status and updated parameter

    Raises:
        GraphQLError: If mutation fails
    """
    try:
        service = get_parameter_app_service()

        # Validate parameter_id
        if not parameter_id or parameter_id < 1:
            raise GraphQLError(f"Invalid parameter_id: {parameter_id}. Must be a positive integer")

        # Validate new_type
        valid_types = ['int', 'string', 'array', 'boolean', 'map']
        if new_type not in valid_types:
            raise GraphQLError(
                f"Invalid new_type: {new_type}. Must be one of: {', '.join(valid_types)}"
            )

        # Change parameter type
        updated_param = service.change_parameter_type(parameter_id=parameter_id, new_type=new_type)

        logger.info(f"Changed parameter type: parameter_id={parameter_id}, new_type={new_type}")

        return {
            'success': True,
            'message': f'Parameter type changed to {new_type}',
            'parameter': updated_param,
        }

    except ValueError as e:
        logger.error(f"Validation error in change_parameter_type: {e}")
        raise GraphQLError(str(e))
    except Exception as e:
        logger.error(f"Error changing parameter type: {e}", exc_info=True)
        raise GraphQLError(f"Failed to change parameter type: {str(e)}")


def mutate_auto_sync_common_parameters(
    info, game_gid: int, force_recalculate: bool = False
) -> Dict[str, Any]:
    """
    Auto-sync common parameters mutation

    Args:
        info: GraphQL resolve info
        game_gid: Game GID
        force_recalculate: Force recalculation even if up to date

    Returns:
        Mutation result with sync statistics

    Raises:
        GraphQLError: If mutation fails
    """
    try:
        service = get_parameter_app_service()

        # Validate game_gid
        if not game_gid or game_gid < 1:
            raise GraphQLError(f"Invalid game_gid: {game_gid}. Must be a positive integer")

        # Sync common parameters
        result = service.auto_sync_common_parameters(game_gid=game_gid, force=force_recalculate)

        logger.info(
            f"Auto-synced common parameters: game_gid={game_gid}, "
            f"force={force_recalculate}, result={result.get('message')}"
        )

        return {
            'success': True,
            'message': result.get('message', 'Sync completed'),
            'result': result,
        }

    except ValueError as e:
        logger.error(f"Validation error in auto_sync_common_parameters: {e}")
        raise GraphQLError(str(e))
    except Exception as e:
        logger.error(f"Error syncing common parameters: {e}", exc_info=True)
        raise GraphQLError(f"Failed to sync common parameters: {str(e)}")


def mutate_batch_add_fields_to_canvas(info, event_id: int, field_type: str) -> Dict[str, Any]:
    """
    Batch add fields to canvas mutation

    Args:
        info: GraphQL resolve info
        event_id: Event ID
        field_type: Field type to add (all, params, non-common, common, base)

    Returns:
        Mutation result with batch operation statistics

    Raises:
        GraphQLError: If mutation fails
    """
    try:
        service = EventBuilderAppService()

        # Validate event_id
        if not event_id or event_id < 1:
            raise GraphQLError(f"Invalid event_id: {event_id}. Must be a positive integer")

        # Validate field_type (accept both enum values and lowercase aliases)
        valid_types = [
            'ALL',
            'PARAM',
            'NON_COMMON',
            'COMMON',
            'BASE',
            'all',
            'param',
            'non_common',
            'common',
            'base',
        ]

        # Convert enum values to lowercase for service layer
        field_type_mapping = {
            'ALL': 'all',
            'PARAM': 'param',
            'NON_COMMON': 'non_common',
            'COMMON': 'common',
            'BASE': 'base',
        }

        if field_type not in valid_types:
            raise GraphQLError(
                f"Invalid field_type: {field_type}. Must be one of: {', '.join(valid_types)}"
            )

        # Convert to lowercase for service layer
        service_field_type = field_type_mapping.get(field_type, field_type)

        # Batch add fields
        result = service.batch_add_fields(event_id=event_id, field_type=service_field_type)

        logger.info(
            f"Batch added fields to canvas: event_id={event_id}, "
            f"field_type={service_field_type}, result={result.get('message')}"
        )

        # Transform to GraphQL format
        batch_result = {
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'total_count': result.get('total_fields', 0),
            'success_count': result.get('added_count', 0),
            'failed_count': 0,
            'errors': [],
        }

        return {
            'success': batch_result['success'],
            'message': batch_result['message'],
            'result': batch_result,
        }

    except ValueError as e:
        logger.error(f"Validation error in batch_add_fields_to_canvas: {e}")
        raise GraphQLError(str(e))
    except Exception as e:
        logger.error(f"Error batching fields to canvas: {e}", exc_info=True)
        raise GraphQLError(f"Failed to batch add fields: {str(e)}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _ensure_parameter_changes_table() -> None:
    """
    Ensure the parameter_changes table exists in the database.

    Creates the table if it doesn't exist. This function is called
    automatically by resolve_parameter_changes to ensure the table
    is available for querying.

    Table Schema:
        - id: Primary key
        - parameter_id: Foreign key to parameters table
        - old_value: Previous value (JSON string)
        - new_value: New value (JSON string)
        - change_type: Type of change (create, update, delete)
        - changed_at: Timestamp of change
        - changed_by: User ID who made the change (nullable)
    """
    from backend.core.database.database import get_db_connection

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS parameter_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parameter_id INTEGER NOT NULL,
            old_value TEXT,
            new_value TEXT,
            change_type TEXT NOT NULL CHECK(change_type IN ('create', 'update', 'delete')),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            changed_by INTEGER,
            FOREIGN KEY (parameter_id) REFERENCES parameters(id) ON DELETE CASCADE,
            FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL
        )
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()

        logger.debug("parameter_changes table ensured to exist")

    except Exception as e:
        logger.error(f"Failed to create parameter_changes table: {e}", exc_info=True)
        # Don't raise - allow the resolver to continue and return empty list


def _determine_field_category(field: Dict[str, Any]) -> str:
    """
    Determine field category based on field properties

    Args:
        field: Field dictionary

    Returns:
        Field category string
    """
    field_type = field.get('type', '')
    is_common = field.get('is_common', False)

    if field_type == 'base':
        return 'base'
    elif is_common:
        return 'common'
    else:
        return 'param'


def _infer_data_type(field: Dict[str, Any]) -> str:
    """
    Infer data type from field properties

    Args:
        field: Field dictionary

    Returns:
        Data type string
    """
    # If field has explicit type, use it
    if 'data_type' in field:
        return field['data_type']

    # Otherwise, infer from field name/category
    field_name = field.get('name', '').lower()

    # Base fields have known types
    base_field_types = {
        'ds': 'string',
        'role_id': 'int',
        'account_id': 'string',
        'utdid': 'string',
        'envinfo': 'string',
        'tm': 'int',
        'ts': 'string',
    }

    if field_name in base_field_types:
        return base_field_types[field_name]

    # Default to string
    return 'string'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


@cached(ttl=300, key_prefix="field_usage")
def _calculate_field_usage(field_name: str, event_id: int) -> int:
    """
    Calculate field usage count from HQL history and flow templates (cached).

    Performance: Uses batch query in resolve_event_fields, this function is kept
    for backward compatibility and individual field lookups.

    Args:
        field_name: Field name to track
        event_id: Event ID

    Returns:
        Usage count (number of times this field is used in HQL/flows)
    """
    try:
        from backend.core.utils import fetch_one_as_dict

        # Count usage in HQL history
        hql_count = fetch_one_as_dict(
            """
            SELECT COUNT(*) as count
            FROM hql_history
            WHERE hql LIKE ?
            """,
            (f'%{field_name}%',),
        )

        # Count usage in flow templates
        flow_count = fetch_one_as_dict(
            """
            SELECT COUNT(*) as count
            FROM flow_templates
            WHERE config LIKE ?
            """,
            (f'%{field_name}%',),
        )

        total_count = (hql_count.get('count', 0) if hql_count else 0) + (
            flow_count.get('count', 0) if flow_count else 0
        )

        logger.debug(f"Field usage: {field_name} used {total_count} times")
        return total_count

    except Exception as e:
        logger.warning(f"Failed to calculate field usage for {field_name}: {e}")
        return 0


@cached(ttl=300, key_prefix="field_usage_batch")
def _calculate_field_usage_batch(field_names: List[str], event_id: int) -> Dict[str, int]:
    """
    Batch calculate field usage counts from HQL history and flow templates (cached).

    Performance optimization: Replaces N individual queries with 2 batch queries.
    For 50 fields: 100 queries → 2 queries (50x reduction).

    Args:
        field_names: List of field names to track
        event_id: Event ID

    Returns:
        Dictionary mapping field names to usage counts
    """
    if not field_names:
        return {}

    try:
        from backend.core.utils import fetch_all_as_dict

        usage_stats = {name: 0 for name in field_names}

        # Single batch query for HQL history - use UNION ALL for each field
        # This is much faster than N separate queries
        hql_query = """
            SELECT SUM(count) as total_count, field_name
            FROM (
        """
        hql_params = []
        for i, field_name in enumerate(field_names):
            if i > 0:
                hql_query += " UNION ALL "
            # Validate field_name before using in SQL (defense in depth)
            from backend.core.security.sql_validator import SQLValidator

            validated_field_name = SQLValidator.validate_column_name(field_name)
            hql_query += f"SELECT COUNT(*) as count, '{validated_field_name}' as field_name FROM hql_history WHERE hql LIKE ?"
            hql_params.append(f'%{validated_field_name}%')
        hql_query += ") GROUP BY field_name"

        hql_results = fetch_all_as_dict(hql_query, tuple(hql_params))
        for row in hql_results:
            usage_stats[row['field_name']] = usage_stats.get(row['field_name'], 0) + (
                row.get('total_count', 0) or 0
            )

        # Single batch query for flow templates
        flow_query = """
            SELECT SUM(count) as total_count, field_name
            FROM (
        """
        flow_params = []
        for i, field_name in enumerate(field_names):
            if i > 0:
                flow_query += " UNION ALL "
            # Validate field_name before using in SQL (defense in depth)
            from backend.core.security.sql_validator import SQLValidator

            validated_field_name = SQLValidator.validate_column_name(field_name)
            flow_query += f"SELECT COUNT(*) as count, '{validated_field_name}' as field_name FROM flow_templates WHERE config LIKE ?"
            flow_params.append(f'%{validated_field_name}%')
        flow_query += ") GROUP BY field_name"

        flow_results = fetch_all_as_dict(flow_query, tuple(flow_params))
        for row in flow_results:
            usage_stats[row['field_name']] = usage_stats.get(row['field_name'], 0) + (
                row.get('total_count', 0) or 0
            )

        logger.debug(f"Batch calculated field usage for {len(field_names)} fields in 2 queries")
        return usage_stats

    except Exception as e:
        logger.warning(f"Failed to batch calculate field usage: {e}")
        return {name: 0 for name in field_names}
