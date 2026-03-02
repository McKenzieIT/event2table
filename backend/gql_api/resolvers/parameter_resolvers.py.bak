"""
GraphQL Parameter Management Resolvers

This module provides GraphQL resolver implementations for parameter management features.
Resolvers use Application Services (not direct repository access) following the DDD architecture.

Author: Event2Table Development Team
Date: 2026-02-23
"""

import logging
from typing import Dict, Any, List, Optional
from graphene import GraphQLError

from backend.application.services.parameter_app_service_enhanced import (
    ParameterAppServiceEnhanced,
    get_parameter_app_service
)
from backend.application.services.event_builder_app_service import (
    EventBuilderAppService
)
from backend.gql_api.schema_parameter_management import (
    ParameterManagementType,
    CommonParameterType,
    FieldTypeType,
    ParameterChangeType,
    BatchOperationResultType
)

logger = logging.getLogger(__name__)


# ============================================================================
# QUERY RESOLVERS
# ============================================================================

def resolve_parameters_management(
    info,
    game_gid: int,
    mode: str = 'all',
    event_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Resolve parameters_management query

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
            raise GraphQLError(
                f"Invalid mode: {mode}. Must be one of: {', '.join(valid_modes)}"
            )

        # Get filtered parameters from service
        parameters = service.get_filtered_parameters(
            game_gid=game_gid,
            mode=mode,
            event_id=event_id
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


def resolve_common_parameters(
    info,
    game_gid: int,
    threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Resolve common_parameters query

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
            raise GraphQLError(
                f"Invalid threshold: {threshold}. Must be between 0 and 1"
            )

        # Get all parameters and filter common ones
        # Note: The service uses 0.8 threshold internally, we'll filter by our threshold
        all_params = service.get_filtered_parameters(
            game_gid=game_gid,
            mode='all'
        )

        # Get total events count for percentage calculation
        from backend.core.utils.converters import fetch_one_as_dict
        total_events_result = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
            (game_gid,)
        )
        total_events = total_events_result[0]['count'] if total_events_result else 0

        if total_events == 0:
            return []

        # Group by param_name and calculate occurrence
        param_occurrences: Dict[str, Dict[str, Any]] = {}
        for param in all_params:
            param_name = param.get('param_name')
            if not param_name:
                continue

            if param_name not in param_occurrences:
                param_occurrences[param_name] = {
                    'param_name': param_name,
                    'param_type': param.get('param_type', 'string'),
                    'param_description': param.get('description', ''),
                    'occurrence_count': 0,
                    'event_codes': [],
                    'is_common': False
                }

            param_occurrences[param_name]['occurrence_count'] += 1

            # Track event codes
            event_code = param.get('event_code')
            if event_code and event_code not in param_occurrences[param_name]['event_codes']:
                param_occurrences[param_name]['event_codes'].append(event_code)

        # Filter by threshold and add metadata
        common_params = []
        threshold_count = int(total_events * threshold)

        for param_data in param_occurrences.values():
            occurrence_count = param_data['occurrence_count']
            is_common = occurrence_count >= threshold_count
            commonality_score = occurrence_count / total_events if total_events > 0 else 0

            if is_common:
                common_params.append({
                    **param_data,
                    'total_events': total_events,
                    'threshold': threshold,
                    'is_common': True,
                    'commonality_score': commonality_score
                })

        # Sort by occurrence count
        common_params.sort(key=lambda x: x['occurrence_count'], reverse=True)

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


def resolve_parameter_changes(
    info,
    game_gid: int,
    parameter_id: Optional[int] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Resolve parameter_changes query

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
        This is a placeholder implementation. The actual parameter_changes table
        should be created and populated by the domain events system.
    """
    try:
        # Validate limit
        if limit < 1 or limit > 1000:
            raise GraphQLError(
                f"Invalid limit: {limit}. Must be between 1 and 1000"
            )

        # Placeholder: Return empty list since parameter_changes table doesn't exist yet
        # In production, this would query the parameter_changes table
        logger.warning(
            f"parameter_changes query not yet implemented: "
            f"game_gid={game_gid}, parameter_id={parameter_id}"
        )

        return []

    except GraphQLError:
        raise
    except Exception as e:
        logger.error(f"Error resolving parameter_changes: {e}", exc_info=True)
        raise GraphQLError(f"Failed to fetch parameter changes: {str(e)}")


def resolve_event_fields(
    info,
    event_id: int,
    field_type: str = 'all'
) -> List[Dict[str, Any]]:
    """
    Resolve event_fields query for EventBuilder

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
        valid_types = ['all', 'params', 'non-common', 'common', 'base']
        if field_type not in valid_types:
            raise GraphQLError(
                f"Invalid field_type: {field_type}. Must be one of: {', '.join(valid_types)}"
            )

        # Get fields from service
        fields = service.get_fields_by_type(
            event_id=event_id,
            field_type=field_type
        )

        # Transform to GraphQL format
        graphql_fields = []
        for field in fields:
            graphql_field = {
                'name': field.get('name'),
                'display_name': field.get('description', field.get('name')),
                'type': field.get('type'),
                'category': _determine_field_category(field),
                'is_common': field.get('is_common', False),
                'data_type': _infer_data_type(field),
                'json_path': field.get('json_path'),
                'usage_count': 0  # TODO: Implement usage tracking
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

def mutate_change_parameter_type(
    info,
    parameter_id: int,
    new_type: str
) -> Dict[str, Any]:
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
            raise GraphQLError(
                f"Invalid parameter_id: {parameter_id}. Must be a positive integer"
            )

        # Validate new_type
        valid_types = ['int', 'string', 'array', 'boolean', 'map']
        if new_type not in valid_types:
            raise GraphQLError(
                f"Invalid new_type: {new_type}. Must be one of: {', '.join(valid_types)}"
            )

        # Change parameter type
        updated_param = service.change_parameter_type(
            parameter_id=parameter_id,
            new_type=new_type
        )

        logger.info(
            f"Changed parameter type: parameter_id={parameter_id}, new_type={new_type}"
        )

        return {
            'success': True,
            'message': f'Parameter type changed to {new_type}',
            'parameter': updated_param
        }

    except ValueError as e:
        logger.error(f"Validation error in change_parameter_type: {e}")
        raise GraphQLError(str(e))
    except Exception as e:
        logger.error(f"Error changing parameter type: {e}", exc_info=True)
        raise GraphQLError(f"Failed to change parameter type: {str(e)}")


def mutate_auto_sync_common_parameters(
    info,
    game_gid: int,
    force_recalculate: bool = False
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
            raise GraphQLError(
                f"Invalid game_gid: {game_gid}. Must be a positive integer"
            )

        # Sync common parameters
        result = service.auto_sync_common_parameters(
            game_gid=game_gid,
            force=force_recalculate
        )

        logger.info(
            f"Auto-synced common parameters: game_gid={game_gid}, "
            f"force={force_recalculate}, result={result.get('message')}"
        )

        return {
            'success': True,
            'message': result.get('message', 'Sync completed'),
            'result': result
        }

    except ValueError as e:
        logger.error(f"Validation error in auto_sync_common_parameters: {e}")
        raise GraphQLError(str(e))
    except Exception as e:
        logger.error(f"Error syncing common parameters: {e}", exc_info=True)
        raise GraphQLError(f"Failed to sync common parameters: {str(e)}")


def mutate_batch_add_fields_to_canvas(
    info,
    event_id: int,
    field_type: str
) -> Dict[str, Any]:
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
            raise GraphQLError(
                f"Invalid event_id: {event_id}. Must be a positive integer"
            )

        # Validate field_type
        valid_types = ['all', 'params', 'non-common', 'common', 'base']
        if field_type not in valid_types:
            raise GraphQLError(
                f"Invalid field_type: {field_type}. Must be one of: {', '.join(valid_types)}"
            )

        # Batch add fields
        result = service.batch_add_fields(
            event_id=event_id,
            field_type=field_type
        )

        logger.info(
            f"Batch added fields to canvas: event_id={event_id}, "
            f"field_type={field_type}, result={result.get('message')}"
        )

        # Transform to GraphQL format
        batch_result = {
            'success': result.get('success', False),
            'message': result.get('message', ''),
            'total_count': result.get('total_fields', 0),
            'success_count': result.get('added_count', 0),
            'failed_count': 0,
            'errors': []
        }

        return {
            'success': batch_result['success'],
            'message': batch_result['message'],
            'result': batch_result
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
        'ts': 'string'
    }

    if field_name in base_field_types:
        return base_field_types[field_name]

    # Default to string
    return 'string'
