"""
Templates API Routes Module (Refactored to Entity-Repository-Service Architecture)

This module contains all template-related API endpoints for managing
canvas flow templates.

Architecture:
- Uses FlowService for business logic
- Uses FlowEntity for data validation
- Uses FlowRepository for data access
- Integrates with cache system

Core endpoints:
- GET /api/templates - List all flow templates with pagination
- POST /api/templates - Create a new flow template
- GET /api/templates/<int:template_id> - Get template details
- PUT /api/templates/<int:template_id> - Update a template
- DELETE /api/templates/<int:template_id> - Delete a template
- POST /api/templates/<int:template_id>/apply - Apply template
"""

import logging
from typing import Dict, Any, List
from flask import request

# Import shared utilities
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
)

# Import Service layer
from backend.services.flows.flow_service import FlowService

# Import Entity layer
from backend.models.entities import FlowEntity

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/templates", methods=["GET"])
def api_list_templates():
    """API: List canvas flow templates with pagination and filtering"""
    try:
        service = FlowService()

        game_gid = request.args.get("game_gid", type=int)
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)
        search = request.args.get("search")

        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # Get templates based on filters
        if game_gid:
            # Get flows for specific game
            flows = service.get_flows_by_game_gid(game_gid)

            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                flows = [
                    f
                    for f in flows
                    if search_lower in f.flow_name.lower()
                    or (f.description and search_lower in f.description.lower())
                ]

            # Pagination
            total = len(flows)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_flows = flows[start:end]
        else:
            # Get all active flows
            flows = service.get_all_active_flows()

            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                flows = [
                    f
                    for f in flows
                    if search_lower in f.flow_name.lower()
                    or (f.description and search_lower in f.description.lower())
                ]

            # Pagination
            total = len(flows)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_flows = flows[start:end]

        # Convert entities to dicts
        templates_data = [flow.model_dump() for flow in paginated_flows]

        return json_success_response(
            data={
                "templates": templates_data,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page,
                },
            }
        )

    except ValueError as e:
        logger.error(f"Validation error in api_list_templates: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        return json_error_response("Failed to fetch templates", status_code=500)


@api_bp.route("/api/templates", methods=["POST"])
def api_create_template():
    """API: Create a new flow template"""
    try:
        service = FlowService()
        data = request.get_json()

        # Validate required fields
        if not data.get("flow_name") and not data.get("name"):
            return json_error_response(
                "Missing required field: flow_name or name", status_code=400
            )

        # Use flow_name if provided, otherwise use name
        flow_name = data.get("flow_name") or data.get("name")
        game_gid = data.get("game_gid")

        # Build FlowEntity
        flow_data = {
            "flow_name": flow_name,
            "game_gid": game_gid,
            "flow_graph": data.get("flow_graph", {"nodes": [], "edges": []}),
            "variables": data.get("variables", {}),
            "description": data.get("description", ""),
            "created_by": data.get("created_by", ""),
            "is_active": data.get("is_active", True),
            "version": data.get("version", 1),
        }

        # Create flow
        flow = FlowEntity(**flow_data)
        created_flow = service.create_flow(flow)

        logger.info(f"Template created: {flow_name} (ID: {created_flow.id})")
        return json_success_response(
            data={"template_id": created_flow.id, "flow": created_flow.model_dump()},
            message="Template created successfully",
        )

    except ValueError as e:
        logger.error(f"Validation error in api_create_template: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return json_error_response("Failed to create template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>", methods=["GET"])
def api_get_template(template_id):
    """API: Get template details"""
    try:
        service = FlowService()
        flow = service.get_flow_by_id(template_id)

        if not flow:
            return json_error_response("Template not found", status_code=404)

        return json_success_response(data=flow.model_dump())

    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}")
        return json_error_response("Failed to get template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>", methods=["PUT"])
def api_update_template(template_id):
    """API: Update a template"""
    try:
        service = FlowService()
        data = request.get_json()

        # Get existing flow
        existing_flow = service.get_flow_by_id(template_id)
        if not existing_flow:
            return json_error_response("Template not found", status_code=404)

        # Build updated FlowEntity
        update_data = {
            "flow_name": data.get("flow_name") or data.get("name") or existing_flow.flow_name,
            "flow_graph": data.get("flow_graph", existing_flow.flow_graph),
            "variables": data.get("variables", existing_flow.variables),
            "description": data.get("description", existing_flow.description),
            "is_active": data.get("is_active", existing_flow.is_active),
            "version": data.get("version", existing_flow.version),
        }

        # Update flow
        updated_flow = FlowEntity(**update_data)
        result = service.update_flow(template_id, updated_flow)

        logger.info(f"Template updated: {template_id}")
        return json_success_response(
            data=result.model_dump(), message="Template updated successfully"
        )

    except ValueError as e:
        logger.error(f"Validation error in api_update_template: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error updating template {template_id}: {e}")
        return json_error_response("Failed to update template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>", methods=["DELETE"])
def api_delete_template(template_id):
    """API: Delete a template (soft delete)"""
    try:
        service = FlowService()

        # Verify flow exists
        flow = service.get_flow_by_id(template_id)
        if not flow:
            return json_error_response("Template not found", status_code=404)

        # Soft delete
        success = service.delete_flow(template_id)

        if success:
            logger.info(f"Template deleted: {template_id}")
            return json_success_response(message="Template deleted successfully")
        else:
            return json_error_response("Failed to delete template", status_code=500)

    except ValueError as e:
        logger.error(f"Validation error in api_delete_template: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {e}")
        return json_error_response("Failed to delete template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>/apply", methods=["POST"])
def api_apply_template(template_id):
    """API: Apply template to create new flow"""
    try:
        service = FlowService()
        data = request.get_json()

        # Get template
        template = service.get_flow_by_id(template_id)
        if not template:
            return json_error_response("Template not found", status_code=404)

        target_flow_name = data.get("target_flow_name")
        if not target_flow_name:
            return json_error_response(
                "Missing required field: target_flow_name", status_code=400
            )

        # Create new flow from template
        new_flow_data = {
            "flow_name": target_flow_name,
            "game_gid": data.get("game_gid", template.game_gid),
            "flow_graph": template.flow_graph.copy(),
            "variables": data.get("parameters", template.variables.copy()),
            "description": data.get(
                "description", f"Created from template: {template.flow_name}"
            ),
            "created_by": data.get("created_by", "system"),
            "is_active": True,
            "version": 1,
        }

        new_flow = FlowEntity(**new_flow_data)
        created_flow = service.create_flow(new_flow)

        return json_success_response(
            data={"flow_id": created_flow.id, "flow": created_flow.model_dump()},
            message="Template applied successfully",
        )

    except ValueError as e:
        logger.error(f"Validation error in api_apply_template: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error applying template {template_id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)
