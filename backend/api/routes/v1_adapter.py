"""
V1 Adapter API Routes

This module provides V1-compatible API endpoints backed by V2 logic.
It acts as a compatibility layer, accepting V1-format requests and
transforming them to V2 format, then transforming responses back.

Endpoints:
- POST /api/v1-adapter/preview-hql - Generate HQL from V1 field builder config
- POST /api/v1-adapter/generate-with-debug - Generate HQL with debug info (V1 format)

Created: 2026-02-17
Purpose: Migrate V1 consumers to V2 backend without breaking changes
"""

import logging
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify

# Import core utilities
from backend.core.utils import (
    json_success_response,
    json_error_response,
    success_response,
    error_response,
)

# Import V2 HQL generation service
from backend.services.hql.core.generator import HQLGenerator, DebuggableHQLGenerator
from backend.services.hql.adapters.project_adapter import ProjectAdapter

# Import V2 API helpers
from backend.api.routes._hql_helpers import (
    parse_json_request,
    validate_required_fields,
    handle_hql_generation_error,
)

logger = logging.getLogger(__name__)

# Create blueprint
v1_adapter_bp = Blueprint("v1_adapter", __name__)


# ============================================================================
# Transformer Functions - V1 <-> V2 Format Conversion
# ============================================================================


def transform_v1_request_to_v2(v1_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform V1 field builder request to V2 API format

    V1 Format (from field_builder.py):
    {
        "config": {
            "view_config": {...},
            "base_fields": [...],
            "custom_fields": {...}
        },
        "source_events": [1, 2, 3],
        "view_name": "v_dwd_custom_view",
        "date_var": "${bizdate}"
    }

    V2 Format (expected by hql_preview_v2.py):
    {
        "events": [
            {"game_gid": 10000147, "event_id": 1}
        ],
        "fields": [
            {"fieldName": "role_id", "fieldType": "base"},
            {"fieldName": "zone_id", "fieldType": "param", "jsonPath": "$.zoneId"}
        ],
        "where_conditions": [],
        "options": {
            "mode": "single",
            "include_comments": True
        }
    }

    Args:
        v1_data: V1 format request data

    Returns:
        V2 format request data
    """
    config = v1_data.get("config", {})
    source_events = v1_data.get("source_events", [])
    date_var = v1_data.get("date_var", "${bizdate}")

    # Extract game_gid from source_events (assume first event's game)
    # In V1, source_events are just event IDs, need to look up game_gid
    # For adapter, we'll extract from config if available

    game_gid = config.get("view_config", {}).get("game_gid")
    if not game_gid:
        # Try to get from first event if it contains game info
        if source_events and isinstance(source_events[0], dict):
            game_gid = source_events[0].get("game_gid")

    if not game_gid:
        raise ValueError("Cannot determine game_gid from V1 request")

    # Transform fields from V1 config to V2 format
    v2_fields = _transform_v1_fields_to_v2(config)

    # Build V2 events list
    v2_events = []
    for event_id in source_events:
        if isinstance(event_id, int):
            v2_events.append({"game_gid": game_gid, "event_id": event_id})
        elif isinstance(event_id, dict):
            v2_events.append(event_id)

    # Transform view_config to where_conditions if present
    v2_conditions = _transform_v1_where_conditions(config.get("view_config", {}))

    # Build V2 request
    v2_data = {
        "events": v2_events,
        "fields": v2_fields,
        "where_conditions": v2_conditions,
        "options": {
            "mode": "single",  # V1 field builder defaults to single mode
            "include_comments": True,
            "date_var": date_var,
        },
    }

    return v2_data


def _transform_v1_fields_to_v2(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform V1 field configuration to V2 field format

    V1 fields can be in:
    - base_fields: [{"name": "role_id", "type": "base"}, ...]
    - custom_fields: {"zone_id": {"json_path": "$.zoneId"}, ...}

    V2 fields format:
    [{"fieldName": "role_id", "fieldType": "base"}, ...]

    Args:
        config: V1 configuration object

    Returns:
        List of V2 format fields
    """
    v2_fields = []

    # Process base_fields
    base_fields = config.get("base_fields", [])
    for field in base_fields:
        if isinstance(field, dict):
            v2_fields.append(
                {
                    "fieldName": field.get("name"),
                    "fieldType": field.get("type", "base"),
                    "alias": field.get("alias"),
                }
            )
        elif isinstance(field, str):
            v2_fields.append({"fieldName": field, "fieldType": "base"})

    # Process custom_fields (param fields)
    custom_fields = config.get("custom_fields", {})
    for field_name, field_config in custom_fields.items():
        if isinstance(field_config, dict):
            v2_fields.append(
                {
                    "fieldName": field_name,
                    "fieldType": field_config.get("type", "param"),
                    "jsonPath": field_config.get("json_path"),
                    "alias": field_config.get("alias"),
                    "customExpression": field_config.get("custom_expression"),
                    "fixedValue": field_config.get("fixed_value"),
                }
            )

    return v2_fields


def _transform_v1_where_conditions(view_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform V1 view config filters to V2 where conditions

    Args:
        view_config: V1 view configuration

    Returns:
        List of V2 format where conditions
    """
    conditions = []

    # Extract filter conditions from view_config
    filters = view_config.get("filters", [])
    for filter_item in filters:
        conditions.append(
            {
                "field": filter_item.get("field"),
                "operator": filter_item.get("operator", "="),
                "value": filter_item.get("value"),
                "logicalOp": filter_item.get("logical_op", "AND"),
            }
        )

    return conditions


def transform_v2_response_to_v1(
    v2_response: Dict[str, Any], view_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transform V2 API response to V1-compatible format

    V2 Response:
    {
        "success": true,
        "data": {
            "hql": "CREATE OR REPLACE VIEW ...",
            "generated_at": "2026-02-17T10:00:00Z"
        }
    }

    V1 Response (expected by field_builder.py):
    {
        "success": true,
        "data": {
            "hql": "CREATE OR REPLACE VIEW ..."
        }
    }

    Args:
        v2_response: V2 format response
        view_name: Optional view name for V1 format

    Returns:
        V1 format response
    """
    v2_data = v2_response.get("data", {})
    v1_data = {"hql": v2_data.get("hql")}

    if view_name:
        v1_data["view_name"] = view_name

    return {"success": True, "data": v1_data}


# ============================================================================
# API Endpoints - V1 Adapter Layer
# ============================================================================


@v1_adapter_bp.route("/api/v1-adapter/preview-hql", methods=["POST"])
def preview_hql_v1():
    """
    V1 Adapter: Preview HQL from field builder configuration

    Accepts V1-format request but uses V2 HQL generation logic internally.

    V1 Request Body:
    {
        "config": {
            "view_config": {
                "game_gid": 10000147,
                "filters": [...]
            },
            "base_fields": [
                {"name": "role_id", "type": "base"},
                {"name": "account_id", "type": "base"}
            ],
            "custom_fields": {
                "zone_id": {
                    "type": "param",
                    "json_path": "$.zoneId"
                }
            }
        },
        "source_events": [1, 2, 3],
        "view_name": "v_dwd_custom_view",
        "date_var": "${bizdate}"
    }

    V1 Response:
    {
        "success": true,
        "data": {
            "hql": "CREATE OR REPLACE VIEW ..."
        }
    }

    Error Response:
    {
        "success": false,
        "error": "Error message",
        "status_code": 400
    }
    """
    try:
        # 1. Parse and validate V1 request
        is_valid, data, error = parse_json_request()
        if not is_valid:
            return jsonify(error_response(error, status_code=400)[0]), 400

        # Validate required V1 fields
        required_fields = ["config", "source_events"]
        for field in required_fields:
            if field not in data:
                error_msg = f"Missing required field: {field}"
                return jsonify(error_response(error_msg, status_code=400)[0]), 400

        config = data["config"]
        source_events = data["source_events"]

        if not source_events:
            return jsonify(error_response("source_events cannot be empty", status_code=400)[0]), 400

        view_name = data.get("view_name", "v_dwd_preview")

        # 2. Transform V1 request to V2 format
        logger.info(f"V1 Adapter: Transforming V1 request to V2 format")
        v2_data = transform_v1_request_to_v2(data)

        # 3. Call V2 HQL generation service
        logger.info(f"V1 Adapter: Calling V2 generator with {len(v2_data['events'])} events, {len(v2_data['fields'])} fields")

        events = ProjectAdapter.events_from_api_request(v2_data["events"])
        fields = ProjectAdapter.fields_from_api_request(v2_data["fields"])
        conditions = ProjectAdapter.conditions_from_api_request(v2_data.get("where_conditions", []))

        options = v2_data.get("options", {})

        generator = HQLGenerator()
        hql = generator.generate(
            events=events,
            fields=fields,
            conditions=conditions,
            **options
        )

        # 4. Transform V2 response to V1 format
        v2_response = {
            "success": True,
            "data": {
                "hql": hql,
                "generated_at": "2026-02-17T10:00:00Z"
            }
        }

        v1_response = transform_v2_response_to_v1(v2_response, view_name)

        logger.info(f"V1 Adapter: Successfully generated HQL for view '{view_name}'")
        return jsonify(v1_response)

    except ValueError as e:
        # Handle validation errors (404 for not found, 400 for other validation errors)
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify(error_response(error_msg, status_code=404)[0]), 404
        return jsonify(error_response(error_msg, status_code=400)[0]), 400

    except Exception as e:
        logger.error(f"V1 Adapter error in preview_hql_v1: {e}")
        import traceback
        traceback.print_exc()
        return handle_hql_generation_error(e, "preview_hql_v1")


@v1_adapter_bp.route("/api/v1-adapter/generate-with-debug", methods=["POST"])
def generate_with_debug_v1():
    """
    V1 Adapter: Generate HQL with debug information

    Similar to preview-hql but includes detailed debugging information.
    Useful for troubleshooting field builder configurations.

    V1 Request Body:
    {
        "config": {...},
        "source_events": [1, 2, 3],
        "view_name": "v_dwd_custom_view",
        "debug": true
    }

    V1 Response (with debug info):
    {
        "success": true,
        "data": {
            "hql": "CREATE OR REPLACE VIEW ...",
            "debug": {
                "events_transformed": 3,
                "fields_transformed": 5,
                "conditions_transformed": 2,
                "generation_time_ms": 45,
                "v2_request": {...}
            }
        }
    }
    """
    try:
        import time

        # 1. Parse and validate V1 request
        is_valid, data, error = parse_json_request()
        if not is_valid:
            return jsonify(error_response(error, status_code=400)[0]), 400

        # Validate required V1 fields
        required_fields = ["config", "source_events"]
        for field in required_fields:
            if field not in data:
                error_msg = f"Missing required field: {field}"
                return jsonify(error_response(error_msg, status_code=400)[0]), 400

        config = data["config"]
        source_events = data["source_events"]

        if not source_events:
            return jsonify(error_response("source_events cannot be empty", status_code=400)[0]), 400

        view_name = data.get("view_name", "v_dwd_preview_debug")
        debug_enabled = data.get("debug", True)

        # 2. Transform V1 request to V2 format
        start_time = time.time()
        v2_data = transform_v1_request_to_v2(data)

        # 3. Call V2 HQL generation service (with debug mode)
        events = ProjectAdapter.events_from_api_request(v2_data["events"])
        fields = ProjectAdapter.fields_from_api_request(v2_data["fields"])
        conditions = ProjectAdapter.conditions_from_api_request(v2_data.get("where_conditions", []))

        options = v2_data.get("options", {})

        if debug_enabled:
            # Use debuggable generator
            generator = DebuggableHQLGenerator()
            trace = generator.generate(
                events=events,
                fields=fields,
                conditions=conditions,
                debug=True,
                **options
            )

            # Extract HQL from trace (supports both final_hql and hql keys)
            hql = trace.get("hql") or trace.get("final_hql", "")

            # Build debug info
            debug_info = {
                "events_transformed": len(events),
                "fields_transformed": len(fields),
                "conditions_transformed": len(conditions),
                "generation_time_ms": round((time.time() - start_time) * 1000, 2),
                "v2_request": v2_data if debug_enabled else None,
                "trace": trace if debug_enabled else None,
            }
        else:
            # Use standard generator
            generator = HQLGenerator()
            hql = generator.generate(
                events=events,
                fields=fields,
                conditions=conditions,
                **options
            )

            debug_info = {
                "events_transformed": len(events),
                "fields_transformed": len(fields),
                "conditions_transformed": len(conditions),
                "generation_time_ms": round((time.time() - start_time) * 1000, 2),
            }

        # 4. Build V1 response with debug info
        v1_data = {
            "hql": hql,
            "view_name": view_name,
            "debug": debug_info,
        }

        logger.info(f"V1 Adapter: Generated debug HQL in {debug_info['generation_time_ms']}ms")
        return jsonify(success_response(data=v1_data)[0])

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify(error_response(error_msg, status_code=404)[0]), 404
        return jsonify(error_response(error_msg, status_code=400)[0]), 400

    except Exception as e:
        logger.error(f"V1 Adapter error in generate_with_debug_v1: {e}")
        import traceback
        traceback.print_exc()
        return handle_hql_generation_error(e, "generate_with_debug_v1")


@v1_adapter_bp.route("/api/v1-adapter/status", methods=["GET"])
def adapter_status():
    """
    V1 Adapter status check endpoint

    Returns adapter version, supported features, and migration status.

    Response:
    {
        "success": true,
        "data": {
            "adapter_version": "1.0.0",
            "backend_version": "2.1.0",
            "status": "running",
            "supported_endpoints": [
                "preview-hql",
                "generate-with-debug"
            ],
            "migration_notes": "V1 consumers should migrate to V2 API format"
        }
    }
    """
    return jsonify(
        success_response(
            data={
                "adapter_version": "1.0.0",
                "backend_version": "2.1.0",
                "status": "running",
                "supported_endpoints": ["preview-hql", "generate-with-debug"],
                "migration_notes": "V1 consumers should migrate to V2 API format",
                "v2_api_docs": "/hql-preview-v2/api/status",
            }
        )[0]
    )
