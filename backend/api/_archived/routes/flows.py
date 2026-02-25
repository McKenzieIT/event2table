"""
Flows API Routes Module

This module contains all flow-related API endpoints for managing
canvas flows.

Core endpoints:
- GET /api/flows - List all flows
- POST /api/flows - Create a new flow
- GET /api/flows/<int:flow_id> - Get flow details
- PUT /api/flows/<int:flow_id> - Update a flow
- DELETE /api/flows/<int:flow_id> - Delete a flow
- POST /api/flows/<int:flow_id>/load - Load flow data
- POST /api/flows/generate - Generate flow
"""

import logging

# Import cache functions
import sys

from flask import request

# Import shared utilities
from backend.core.utils import (
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
    sanitize_and_validate_string,
    validate_json_request,
)

# Import Repository pattern for data access
from backend.core.data_access import Repositories

sys.path.append("..")
try:
    from backend.core.cache.cache_system import clear_cache_pattern
except ImportError:

    def clear_cache_pattern(pattern):
        """
        Clear cache entries matching a pattern (fallback implementation).

            This is a fallback function used when the cache_system module
        is not available. It does nothing but prevents ImportError.

            Args:
                pattern (str): Cache key pattern to match (unused in fallback)

            Returns:
                None
        """
        pass


# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/flows", methods=["GET"])
def api_list_flows():
    """API: List all flows with pagination"""
    try:
        game_gid = request.args.get("game_gid", type=int)

        page = request.args.get("page", 1, type=int)
        page_size = request.args.get("page_size", 50, type=int)
        page_size = min(max(page_size, 1), 100)

        offset = (page - 1) * page_size

        where_clauses = ["1=1"]
        params = []

        if game_gid:
            where_clauses.append("game_gid = ?")
            params.append(game_gid)

        where_sql = " AND ".join(where_clauses)

        total_result = fetch_one_as_dict(
            f"SELECT COUNT(*) as count FROM flow_templates WHERE {where_sql}",
            tuple(params),
        )
        total = total_result["count"] if total_result else 0

        flows = fetch_all_as_dict(
            f"""
            SELECT * FROM flow_templates
            WHERE {where_sql}
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """,
            tuple(params) + (page_size, offset),
        )

        return json_success_response(
            data={
                "flows": flows,
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }
        )

    except Exception as e:
        logger.error(f"Error fetching flows: {e}")
        return json_error_response("Failed to fetch flows", status_code=500)


@api_bp.route("/api/flows", methods=["POST"])
def api_create_flow():
    """API: Create a new flow"""
    try:
        data = request.get_json()

        # Validate required fields
        if "game_gid" not in data or "flow_name" not in data:
            return json_error_response(
                "Missing required fields: game_gid, flow_name", status_code=400
            )

        # Validate game_gid exists using Repository
        game = Repositories.GAMES.find_by_field("gid", data["game_gid"])
        if not game:
            return json_error_response(
                f"Game with gid {data['game_gid']} not found", status_code=404
            )

        # 验证和清理流程名称
        is_valid, result = sanitize_and_validate_string(
            data.get("flow_name"),
            max_length=200,
            field_name="flow_name",
            allow_empty=False,
        )
        if not is_valid:
            return json_error_response(result, status_code=400)
        flow_name = result

        # 验证和清理分类
        is_valid, result = sanitize_and_validate_string(
            data.get("category", "custom"),
            max_length=100,
            field_name="category",
            allow_empty=True,
        )
        if not is_valid:
            return json_error_response(result, status_code=400)
        category = result

        # 验证和清理描述
        is_valid, result = sanitize_and_validate_string(
            data.get("description", ""),
            max_length=1000,
            field_name="description",
            allow_empty=True,
        )
        if not is_valid:
            return json_error_response(result, status_code=400)
        description = result

        flow_id = execute_write(
            """INSERT INTO flow_templates (game_gid, name, category, description, flow_data, is_active)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                data["game_gid"],
                flow_name,
                category,
                description,
                data.get("flow_data", "{}"),
                1,
            ),
            return_last_id=True,
        )

        clear_cache_pattern("flows")
        logger.info(f"Flow created: {flow_name} (ID: {flow_id})")
        return json_success_response(
            data={"flow_id": flow_id}, message="Flow created successfully"
        )

    except Exception as e:
        logger.error(f"Error creating flow: {e}")
        return json_error_response("Failed to create flow", status_code=500)


@api_bp.route("/api/flows/<int:flow_id>", methods=["GET"])
def api_get_flow(flow_id):
    """API: Get flow details"""
    try:
        flow = Repositories.FLOW_TEMPLATES.find_by_id(flow_id)

        if not flow:
            return json_error_response("Flow not found", status_code=404)

        return json_success_response(data=flow)

    except Exception as e:
        logger.error(f"Error getting flow {flow_id}: {e}")
        return json_error_response("Failed to get flow", status_code=500)


@api_bp.route("/api/flows/<int:flow_id>", methods=["PUT"])
def api_update_flow(flow_id):
    """API: Update a flow"""
    flow = Repositories.FLOW_TEMPLATES.find_by_id(flow_id)
    if not flow:
        return json_error_response("Flow not found", status_code=404)

    try:
        data = request.get_json()

        # 验证和清理流程名称
        if "name" in data:
            is_valid, result = sanitize_and_validate_string(
                data.get("name"), max_length=200, field_name="name", allow_empty=False
            )
            if not is_valid:
                return json_error_response(result, status_code=400)
            flow_name = result
        else:
            flow_name = flow["name"]

        # 验证和清理分类
        if "category" in data:
            is_valid, result = sanitize_and_validate_string(
                data.get("category"),
                max_length=100,
                field_name="category",
                allow_empty=True,
            )
            if not is_valid:
                return json_error_response(result, status_code=400)
            category = result
        else:
            category = flow["category"]

        # 验证和清理描述
        if "description" in data:
            is_valid, result = sanitize_and_validate_string(
                data.get("description"),
                max_length=1000,
                field_name="description",
                allow_empty=True,
            )
            if not is_valid:
                return json_error_response(result, status_code=400)
            description = result
        else:
            description = flow["description"]

        execute_write(
            "UPDATE flow_templates SET name = ?, category = ?, description = ?, flow_data = ? WHERE id = ?",
            (
                flow_name,
                category,
                description,
                data.get("flow_data", flow["flow_data"]),
                flow_id,
            ),
        )

        clear_cache_pattern("flows")
        logger.info(f"Flow updated: {flow_id}")
        return json_success_response(message="Flow updated successfully")

    except Exception as e:
        logger.error(f"Error updating flow {flow_id}: {e}")
        return json_error_response("Failed to update flow", status_code=500)


@api_bp.route("/api/flows/<int:flow_id>", methods=["DELETE"])
def api_delete_flow(flow_id):
    """API: Delete a flow"""
    flow = Repositories.FLOW_TEMPLATES.find_by_id(flow_id)
    if not flow:
        return json_error_response("Flow not found", status_code=404)

    try:
        Repositories.FLOW_TEMPLATES.delete(flow_id)

        clear_cache_pattern("flows")
        logger.info(f"Flow deleted: {flow_id}")
        return json_success_response(message="Flow deleted successfully")

    except Exception as e:
        logger.error(f"Error deleting flow {flow_id}: {e}")
        return json_error_response("Failed to delete flow", status_code=500)


@api_bp.route("/api/flows/<int:flow_id>/load", methods=["POST"])
def api_load_flow(flow_id):
    """API: Load flow data"""
    try:
        # Import flow manager from backend services
        from backend.services.flows import flow_manager

        flow = Repositories.FLOW_TEMPLATES.find_by_id(flow_id)
        if not flow:
            return json_error_response("Flow not found", status_code=404)

        # Load flow using flow manager
        flow_data = flow_manager.load_flow(flow_id)

        return json_success_response(data=flow_data)

    except Exception as e:
        logger.error(f"Error loading flow {flow_id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/flows/generate", methods=["POST"])
def api_generate_flow():
    """API: Generate flow HQL"""
    try:
        from backend.services.hql.generator import hql_generator

        data = request.get_json()

        # Validate required fields
        if "flow_id" not in data:
            return json_error_response("Missing flow_id", status_code=400)

        # Generate HQL using HQL generator
        result = hql_generator.generate_flow_hql(
            data["flow_id"], data.get("options", {})
        )

        return json_success_response(
            data=result, message="Flow HQL generated successfully"
        )

    except Exception as e:
        logger.error(f"Error generating flow HQL: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


# ============================================================================
# Canvas API Aliases (for frontend compatibility)
# ============================================================================


@api_bp.route("/canvas/api/flows/save", methods=["POST"])
def canvas_api_flows_save():
    """API: Save flow (alias for POST /api/flows)"""
    return api_create_flow()


@api_bp.route("/canvas/api/flows/<int:flowId>", methods=["GET"])
def canvas_api_flows_get(flowId):
    """API: Get flow details (alias for GET /api/flows/<id>)"""
    return api_get_flow(flowId)


@api_bp.route("/canvas/api/execute", methods=["POST"])
def canvas_api_execute():
    """API: Execute flow/generate HQL (alias for POST /api/flows/generate)"""
    return api_generate_flow()


@api_bp.route("/api/flows/execute", methods=["POST"])
def api_flows_execute():
    """API: Execute flow/generate HQL (alias for /canvas/api/execute)

    Compatibility alias for frontend that expects /api/flows/execute path.
    This provides the same functionality as /canvas/api/execute but with a different URL.
    """
    return canvas_api_execute()


@api_bp.route("/canvas/api/canvas/health", methods=["GET"])
def canvas_api_health():
    """API: Canvas health check endpoint"""
    return json_success_response(
        data={"status": "healthy", "service": "canvas"},
        message="Canvas service is healthy",
    )


@api_bp.route("/canvas/api/preview-results", methods=["POST"])
def canvas_api_preview_results():
    """API: Preview flow execution results"""
    try:
        data = request.get_json()

        # Validate required fields
        if "flow_id" not in data:
            return json_error_response("Missing flow_id", status_code=400)

        # Get flow details
        flow = Repositories.FLOW_TEMPLATES.find_by_id(data["flow_id"])
        if not flow:
            return json_error_response("Flow not found", status_code=404)

        # For now, return a placeholder response
        # In a real implementation, this would execute the flow and return results
        return json_success_response(
            data={
                "flow_id": data["flow_id"],
                "status": "preview_ready",
                "message": "Flow preview results (placeholder)",
            },
            message="Flow preview generated successfully",
        )

    except Exception as e:
        logger.error(f"Error previewing flow results: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/flows/batch", methods=["DELETE"])
def api_batch_delete_flows():
    """API: Batch delete flow templates"""
    is_valid, data, error = validate_json_request(["ids"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    flow_ids = data.get("ids", [])

    if not flow_ids or not isinstance(flow_ids, list):
        return json_error_response("Invalid flow IDs", status_code=400)

    try:
        # Delete flows using Repository batch delete
        deleted_count = Repositories.FLOW_TEMPLATES.delete_batch(flow_ids)

        clear_cache_pattern("flows")  # Clear cache after delete
        logger.info(f"Batch deleted {deleted_count} flows")
        return json_success_response(
            message=f"Deleted {deleted_count} flows",
            data={"deleted_count": deleted_count},
        )
    except Exception as e:
        logger.error(f"Error batch deleting flows: {e}")
        return json_error_response("Failed to delete flows", status_code=500)


@api_bp.route("/api/flows/batch-update", methods=["PUT"])
def api_batch_update_flows():
    """API: Batch update flow templates

    Example request body:
    {
        "ids": [1, 2, 3],
        "updates": {"name": "Updated Name", "is_active": 1}
    }
    """
    is_valid, data, error = validate_json_request(["ids", "updates"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    flow_ids = data.get("ids", [])
    updates = data.get("updates", {})

    if not flow_ids or not updates:
        return json_error_response("Invalid request data", status_code=400)

    try:
        # Validate and sanitize update fields
        if "name" in updates:
            is_valid, result = sanitize_and_validate_string(
                updates["name"], max_length=200, field_name="name", allow_empty=False
            )
            if not is_valid:
                return json_error_response(result, status_code=400)
            updates["name"] = result

        # Use Repository batch update
        updated_count = Repositories.FLOW_TEMPLATES.update_batch(flow_ids, updates)

        clear_cache_pattern("flows")  # Clear cache after update
        logger.info(f"Batch updated {updated_count} flows")
        return json_success_response(
            message=f"Updated {updated_count} flows",
            data={"updated_count": updated_count},
        )
    except Exception as e:
        logger.error(f"Error batch updating flows: {e}")
        return json_error_response("Failed to update flows", status_code=500)
