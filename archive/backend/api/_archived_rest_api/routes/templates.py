"""
Templates API Routes Module

This module contains all template-related API endpoints for managing
canvas flow templates.

Core endpoints:
- GET /api/templates - List all templates with pagination
- POST /api/templates - Create a new template
- GET /api/templates/<int:template_id> - Get template details
- PUT /api/templates/<int:template_id> - Update a template
- DELETE /api/templates/<int:template_id> - Delete a template
- POST /api/templates/<int:template_id>/apply - Apply template
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
)


def escape_like_wildcards(search: str) -> str:
    """Escape SQL LIKE wildcards in search string."""
    return search.replace("%", r"\%").replace("_", r"\_")


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


# Import Repository pattern for data access
from backend.core.data_access import Repositories

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/templates", methods=["GET"])
def api_list_templates():
    """API: List canvas templates with pagination and filtering"""
    try:
        game_gid = request.args.get("game_gid", type=int)
        category = request.args.get("category")
        search = request.args.get("search")
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 20, type=int)

        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        # Build WHERE clause
        where_clauses = ["1=1"]
        params = []

        if game_gid:
            where_clauses.append("game_gid = ?")
            params.append(game_gid)

        if category:
            where_clauses.append("category = ?")
            params.append(category)

        if search:
            where_clauses.append(
                "(name LIKE ? ESCAPE '\\' OR flow_name LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\')"
            )
            escaped = escape_like_wildcards(search)
            params.extend([f"%{escaped}%", f"%{escaped}%", f"%{escaped}%"])

        where_sql = " AND ".join(where_clauses)

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM flow_templates WHERE {where_sql}"
        total_result = fetch_one_as_dict(count_sql, params)
        total = total_result["COUNT(*)"] if total_result else 0

        # Get templates
        offset = (page - 1) * per_page
        list_sql = f"""
            SELECT * FROM flow_templates
            WHERE {where_sql}
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """

        templates = fetch_all_as_dict(list_sql, params + [per_page, offset])

        return json_success_response(
            data={
                "templates": templates,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": total,
                    "pages": (total + per_page - 1) // per_page,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error fetching templates: {e}")
        return json_error_response("Failed to fetch templates", status_code=500)


@api_bp.route("/api/templates", methods=["POST"])
def api_create_template():
    """API: Create a new template"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["name", "game_gid", "category"]
        for field in required_fields:
            if field not in data:
                return json_error_response(
                    f"Missing required field: {field}", status_code=400
                )

        # Validate game_gid exists
        game = fetch_one_as_dict(
            "SELECT gid FROM games WHERE gid = ?", (data["game_gid"],)
        )
        if not game:
            return json_error_response(
                f"Game with gid {data['game_gid']} not found", status_code=404
            )

        template_id = execute_write(
            """INSERT INTO flow_templates (name, game_gid, category, description, flow_data, is_public)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                data["name"],
                data["game_gid"],
                data["category"],
                data.get("description", ""),
                data.get("flow_data", "{}"),
                data.get("is_public", 0),
            ),
            return_last_id=True,
        )

        logger.info(f"Template created: {data['name']} (ID: {template_id})")
        return json_success_response(
            data={"template_id": template_id}, message="Template created successfully"
        )

    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return json_error_response("Failed to create template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>", methods=["GET"])
def api_get_template(template_id):
    """API: Get template details"""
    try:
        template = Repositories.FLOW_TEMPLATES.find_by_id(template_id)

        if not template:
            return json_error_response("Template not found", status_code=404)

        return json_success_response(data=template)

    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}")
        return json_error_response("Failed to get template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>", methods=["PUT"])
def api_update_template(template_id):
    """API: Update a template"""
    template = Repositories.FLOW_TEMPLATES.find_by_id(template_id)
    if not template:
        return json_error_response("Template not found", status_code=404)

    try:
        data = request.get_json()

        execute_write(
            "UPDATE flow_templates SET name = ?, category = ?, description = ?, flow_data = ? WHERE id = ?",
            (
                data.get("name", template["name"]),
                data.get("category", template["category"]),
                data.get("description", template["description"]),
                data.get("flow_data", template["flow_data"]),
                template_id,
            ),
        )

        logger.info(f"Template updated: {template_id}")
        return json_success_response(message="Template updated successfully")

    except Exception as e:
        logger.error(f"Error updating template {template_id}: {e}")
        return json_error_response("Failed to update template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>", methods=["DELETE"])
def api_delete_template(template_id):
    """API: Delete a template"""
    template = Repositories.FLOW_TEMPLATES.find_by_id(template_id)
    if not template:
        return json_error_response("Template not found", status_code=404)

    try:
        Repositories.FLOW_TEMPLATES.delete(template_id)

        logger.info(f"Template deleted: {template_id}")
        return json_success_response(message="Template deleted successfully")

    except Exception as e:
        logger.error(f"Error deleting template {template_id}: {e}")
        return json_error_response("Failed to delete template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>/apply", methods=["POST"])
def api_apply_template(template_id):
    """API: Apply template to create new flow"""
    try:
        from modules.flow_template_manager import flow_template_manager

        template = Repositories.FLOW_TEMPLATES.find_by_id(template_id)
        if not template:
            return json_error_response("Template not found", status_code=404)

        data = request.get_json()
        target_flow_name = data.get("target_flow_name")

        if not target_flow_name:
            return json_error_response("Missing target_flow_name", status_code=400)

        # Apply template using template manager
        flow_id = flow_template_manager.apply_template(
            template_id, target_flow_name, data.get("parameters", {})
        )

        return json_success_response(
            data={"flow_id": flow_id}, message="Template applied successfully"
        )

    except Exception as e:
        logger.error(f"Error applying template {template_id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)
