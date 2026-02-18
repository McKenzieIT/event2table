"""
V2 to V1 HQL Response Transformer

This module provides transformation functions to convert V2 HQL API responses
back to V1 format, ensuring backward compatibility with existing frontend code.

V2 Response Format:
{
    "success": true,
    "data": {
        "hql": "SELECT ...",
        "final_hql": "SELECT ...",  # In debug mode
        "steps": [...],             # In debug mode
        "events": [...],            # In debug mode
        "fields": [...],            # In debug mode
        "conditions": [...],        # In debug mode
        "generated_at": "2026-02-17T..."
    }
}

V1 Response Format:
{
    "success": true,
    "data": {
        "hql": "SELECT ...",
        "view_name": "v_dwd_custom_view"
    }
}

Author: Event2Table Development Team
Version: 1.0.0 (2026-02-17)
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class TransformationError(Exception):
    """Raised when V2 to V1 transformation fails"""

    pass


def transform_hql_response(
    v2_response: Dict[str, Any], view_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transform V2 HQL response to V1 format.

    This function extracts the essential HQL content from a V2 API response
    and reformats it to match the V1 API contract expected by the frontend.

    Args:
        v2_response: V2 API response dictionary
        view_name: Optional view name to include in response (default: "v_dwd_custom_view")

    Returns:
        V1-formatted response dictionary with structure:
        {
            "success": bool,
            "data": {
                "hql": str,
                "view_name": str
            }
        }

    Raises:
        TransformationError: If transformation fails due to invalid input

    Examples:
        >>> v2_response = {
        ...     "success": True,
        ...     "data": {"hql": "SELECT role_id FROM table", "generated_at": "2026-02-17T..."}
        ... }
        >>> transform_hql_response(v2_response, "v_dwd_test")
        {'success': True, 'data': {'hql': 'SELECT role_id FROM table', 'view_name': 'v_dwd_test'}}

        >>> # Debug mode response with final_hql
        >>> v2_debug = {
        ...     "success": True,
        ...     "data": {
        ...         "final_hql": "SELECT role_id FROM table",
        ...         "steps": [...]
        ...     }
        ... }
        >>> transform_hql_response(v2_debug)
        {'success': True, 'data': {'hql': 'SELECT role_id FROM table', 'view_name': 'v_dwd_custom_view'}}
    """
    if not isinstance(v2_response, dict):
        raise TransformationError(
            f"Invalid V2 response type: expected dict, got {type(v2_response).__name__}"
        )

    # Validate V2 response structure
    if "success" not in v2_response:
        raise TransformationError("Missing 'success' field in V2 response")

    if "data" not in v2_response:
        raise TransformationError("Missing 'data' field in V2 response")

    if not isinstance(v2_response["data"], dict):
        raise TransformationError(
            f"Invalid V2 data type: expected dict, got {type(v2_response['data']).__name__}"
        )

    # Extract HQL from V2 response
    hql = extract_hql(v2_response["data"])

    if not hql:
        raise TransformationError("No HQL found in V2 response")

    # Set default view name if not provided
    if view_name is None:
        view_name = "v_dwd_custom_view"

    # Build V1 response
    v1_response = {
        "success": v2_response.get("success", True),
        "data": {"hql": hql, "view_name": view_name},
    }

    logger.debug(f"Transformed V2 response to V1 format (view_name={view_name})")
    return v1_response


def extract_hql(v2_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract HQL from various V2 response formats.

    This function handles both simple and debug response formats, with
    prioritization: final_hql > hql > fallback.

    Args:
        v2_data: V2 response data dictionary

    Returns:
        Extracted HQL string, or None if not found

    Examples:
        >>> # Simple format
        >>> extract_hql({"hql": "SELECT * FROM table"})
        'SELECT * FROM table'

        >>> # Debug mode with final_hql
        >>> extract_hql({"final_hql": "SELECT * FROM table", "steps": [...]})
        'SELECT * FROM table'

        >>> # Both present - final_hql takes priority
        >>> extract_hql({"hql": "SELECT 1", "final_hql": "SELECT 2"})
        'SELECT 2'

        >>> # No HQL found
        >>> extract_hql({"steps": []}) is None
        True
    """
    if not isinstance(v2_data, dict):
        logger.warning(f"Invalid v2_data type: expected dict, got {type(v2_data).__name__}")
        return None

    # Priority 1: final_hql (from debug mode)
    if "final_hql" in v2_data:
        hql = v2_data["final_hql"]
        if isinstance(hql, str) and hql.strip():
            logger.debug("Extracted HQL from 'final_hql' field")
            return hql.strip()
        else:
            logger.warning("'final_hql' field exists but is not a valid string")

    # Priority 2: hql (from simple mode)
    if "hql" in v2_data:
        hql = v2_data["hql"]
        if isinstance(hql, str) and hql.strip():
            logger.debug("Extracted HQL from 'hql' field")
            return hql.strip()
        else:
            logger.warning("'hql' field exists but is not a valid string")

    # No HQL found
    logger.warning("No valid HQL found in V2 response data")
    return None


def transform_performance_data(v2_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert V2 performance data to V1 format (if needed).

    This function extracts timing and optimization information from V2 debug
    responses, making it compatible with V1 frontend expectations.

    Args:
        v2_data: V2 response data dictionary

    Returns:
        V1-formatted performance data dictionary

    Examples:
        >>> v2_data = {
        ...     "generated_at": "2026-02-17T10:30:00Z",
        ...     "steps": [
        ...         {"step": "build_fields", "result": [...], "count": 5},
        ...         {"step": "build_where", "result": "..."}
        ...     ]
        ... }
        >>> transform_performance_data(v2_data)
        {
            'generated_at': '2026-02-17T10:30:00Z',
            'step_count': 2,
            'field_count': 5,
            'has_where_clause': True
        }
    """
    if not isinstance(v2_data, dict):
        logger.warning(f"Invalid v2_data type: expected dict, got {type(v2_data).__name__}")
        return {}

    performance_data = {}

    # Extract timestamp
    if "generated_at" in v2_data:
        generated_at = v2_data["generated_at"]
        if isinstance(generated_at, str):
            performance_data["generated_at"] = generated_at

    # Extract step information
    steps = v2_data.get("steps", [])
    if isinstance(steps, list):
        performance_data["step_count"] = len(steps)

        # Count fields if build_fields step exists
        for step in steps:
            if isinstance(step, dict) and step.get("step") == "build_fields":
                performance_data["field_count"] = step.get("count", 0)

            # Check if WHERE clause was built
            if isinstance(step, dict) and step.get("step") == "build_where":
                where_result = step.get("result", "")
                performance_data["has_where_clause"] = bool(where_result and where_result.strip())

    # Extract event and field counts if available
    events = v2_data.get("events", [])
    fields = v2_data.get("fields", [])

    if isinstance(events, list):
        performance_data["event_count"] = len(events)

    if isinstance(fields, list):
        performance_data["total_fields"] = len(fields)

    logger.debug(f"Transformed performance data: {performance_data}")
    return performance_data


def transform_debug_info(v2_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert V2 debug steps to V1 format (if needed).

    This function transforms the detailed debug information from V2 responses
    into a format compatible with V1 frontend components.

    Args:
        v2_data: V2 response data dictionary

    Returns:
        V1-formatted debug information dictionary

    Examples:
        >>> v2_data = {
        ...     "steps": [
        ...         {"step": "build_fields", "result": ["role_id", "account_id"], "count": 2},
        ...         {"step": "build_where", "result": "WHERE ds = '${bizdate}'"},
        ...         {"step": "assemble", "result": "SELECT ..."}
        ...     ],
        ...     "events": [{"name": "login", "table": "..."}],
        ...     "fields": [{"name": "role_id", "type": "base"}]
        ... }
        >>> result = transform_debug_info(v2_data)
        >>> 'steps' in result
        True
        >>> 'events' in result
        True
        >>> 'fields' in result
        True
    """
    if not isinstance(v2_data, dict):
        logger.warning(f"Invalid v2_data type: expected dict, got {type(v2_data).__name__}")
        return {}

    debug_info = {}

    # Transform steps
    steps = v2_data.get("steps", [])
    if isinstance(steps, list):
        # Simplify step format for V1 compatibility
        debug_info["steps"] = [
            {
                "name": step.get("step", "unknown"),
                "description": _get_step_description(step.get("step", "")),
                "details": _extract_step_details(step),
            }
            for step in steps
            if isinstance(step, dict)
        ]

    # Transform events (simplified format)
    events = v2_data.get("events", [])
    if isinstance(events, list):
        debug_info["events"] = [
            {
                "name": event.get("name", "unknown"),
                "table": event.get("table_name", ""),
            }
            for event in events
            if isinstance(event, dict)
        ]

    # Transform fields (simplified format)
    fields = v2_data.get("fields", [])
    if isinstance(fields, list):
        debug_info["fields"] = [
            {
                "name": field.get("name", "unknown"),
                "type": field.get("field_type", field.get("type", "unknown")),
            }
            for field in fields
            if isinstance(field, dict)
        ]

    # Transform conditions (simplified format)
    conditions = v2_data.get("conditions", [])
    if isinstance(conditions, list):
        debug_info["conditions"] = [
            {
                "field": cond.get("field", ""),
                "operator": cond.get("operator", ""),
                "value": cond.get("value", ""),
            }
            for cond in conditions
            if isinstance(cond, dict)
        ]

    logger.debug(f"Transformed debug info: {len(debug_info.get('steps', []))} steps")
    return debug_info


def _get_step_description(step_name: str) -> str:
    """
    Get human-readable description for a generation step.

    Args:
        step_name: Step identifier (e.g., "build_fields", "build_where")

    Returns:
        Human-readable description
    """
    descriptions = {
        "build_fields": "Building field expressions",
        "build_where": "Building WHERE clause",
        "assemble": "Assembling final HQL",
        "validate": "Validating input parameters",
        "optimize": "Optimizing HQL query",
    }
    return descriptions.get(step_name, f"Executing step: {step_name}")


def _extract_step_details(step: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant details from a step result.

    Args:
        step: Step dictionary with result information

    Returns:
        Simplified details dictionary
    """
    details = {}

    # Extract count if available
    if "count" in step:
        details["count"] = step["count"]

    # Extract result if it's not too large
    result = step.get("result")
    if result is not None:
        if isinstance(result, str):
            # Truncate long strings
            if len(result) > 200:
                details["result_preview"] = result[:200] + "..."
            else:
                details["result"] = result
        elif isinstance(result, list):
            # Just show count for lists
            details["item_count"] = len(result)
        elif isinstance(result, dict):
            # Show keys for dicts
            details["keys"] = list(result.keys())[:5]

    return details


def transform_batch_responses(
    v2_responses: List[Dict[str, Any]], view_names: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Transform multiple V2 responses to V1 format.

    This is useful for batch processing where multiple HQL generations
    need to be transformed.

    Args:
        v2_responses: List of V2 API response dictionaries
        view_names: Optional list of view names (must match length of v2_responses)

    Returns:
        List of V1-formatted response dictionaries

    Raises:
        TransformationError: If view_names length doesn't match v2_responses length

    Examples:
        >>> v2_responses = [
        ...     {"success": True, "data": {"hql": "SELECT ..."}},
        ...     {"success": True, "data": {"hql": "SELECT ..."}}
        ... ]
        >>> view_names = ["v_dwd_view1", "v_dwd_view2"]
        >>> transform_batch_responses(v2_responses, view_names)
        [
            {'success': True, 'data': {'hql': 'SELECT ...', 'view_name': 'v_dwd_view1'}},
            {'success': True, 'data': {'hql': 'SELECT ...', 'view_name': 'v_dwd_view2'}}
        ]
    """
    if view_names is not None and len(view_names) != len(v2_responses):
        raise TransformationError(
            f"view_names length ({len(view_names)}) must match "
            f"v2_responses length ({len(v2_responses)})"
        )

    v1_responses = []
    for i, v2_response in enumerate(v2_responses):
        view_name = view_names[i] if view_names else None
        try:
            v1_response = transform_hql_response(v2_response, view_name)
            v1_responses.append(v1_response)
        except TransformationError as e:
            logger.error(f"Failed to transform response at index {i}: {e}")
            # Include error information in the response
            v1_responses.append(
                {
                    "success": False,
                    "error": f"Transformation failed: {str(e)}",
                    "data": {"hql": "", "view_name": view_name or "v_dwd_custom_view"},
                }
            )

    logger.info(f"Transformed {len(v1_responses)} batch responses")
    return v1_responses


def validate_v2_response(v2_response: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate V2 response structure before transformation.

    Args:
        v2_response: V2 API response dictionary to validate

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_v2_response({"success": True, "data": {"hql": "SELECT ..."}})
        (True, None)

        >>> validate_v2_response({"success": True})
        (False, "Missing 'data' field in V2 response")
    """
    if not isinstance(v2_response, dict):
        return False, f"Invalid response type: expected dict, got {type(v2_response).__name__}"

    if "success" not in v2_response:
        return False, "Missing 'success' field in V2 response"

    if "data" not in v2_response:
        return False, "Missing 'data' field in V2 response"

    if not isinstance(v2_response["data"], dict):
        return False, f"Invalid data type: expected dict, got {type(v2_response['data']).__name__}"

    # Check if data contains HQL
    if "hql" not in v2_response["data"] and "final_hql" not in v2_response["data"]:
        return False, "V2 response data must contain either 'hql' or 'final_hql'"

    return True, None


# Convenience function for most common use case
def v2_to_v1(v2_response: Dict[str, Any], view_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience alias for transform_hql_response.

    This is the most commonly used transformation function, converting
    a single V2 HQL response to V1 format.

    Args:
        v2_response: V2 API response dictionary
        view_name: Optional view name to include in response

    Returns:
        V1-formatted response dictionary

    Examples:
        >>> v2_response = {"success": True, "data": {"hql": "SELECT ..."}}
        >>> v2_to_v1(v2_response, "v_dwd_test")
        {'success': True, 'data': {'hql': 'SELECT ...', 'view_name': 'v_dwd_test'}}
    """
    return transform_hql_response(v2_response, view_name)
