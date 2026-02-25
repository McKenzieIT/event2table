"""
Field Builder API Routes Module

This module contains all field builder-related API endpoints for managing
field configurations, generating HQL previews, and managing view configurations.

Core endpoints:
- POST /api/field-builder/config - Save field builder configuration
- GET /api/field-builder/config/<int:id> - Get field builder configuration
- POST /api/field-builder/preview - Preview HQL from field builder configuration
"""

import json
import logging

# Import cache functions
import sys
import time

from flask import request

# Import shared utilities
from backend.core.utils import (
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
    validate_json_request,
)

# Import database connection
from backend.core.database.database import get_db_connection
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


@api_bp.route("/api/field-builder/config", methods=["POST"])
@api_bp.route("/api/field-builder/configs", methods=["POST"])
def api_save_field_builder_config():
    """API: Save field builder configuration

    Request body:
    {
        "config": {
            "view_config": {...},
            "base_fields": [...],
            "custom_fields": {...}
        },
        "view_name": "v_dwd_custom_view",
        "display_name": "Custom View Display Name"
    }

        Returns:
        Saved configuration with ID
    """
    data = request.get_json()
    config = data.get("config")
    view_name = data.get("view_name")
    display_name = data.get("display_name", view_name)

    if not config:
        return json_error_response("Missing configuration data", status_code=400)

    if not view_name:
        return json_error_response("Missing view_name", status_code=400)

    # Convert config to JSON
    config_json = json.dumps(config, ensure_ascii=False)

    # Check if updating existing or creating new
    config_id = data.get("id")

    # Retry logic for database lock errors
    max_retries = 3
    delay = 0.1  # 100ms

    for attempt in range(max_retries):
        try:
            if config_id:
                # Update existing configuration
                affected = execute_write(
                    """
                    UPDATE join_configs
                    SET field_mapping_v2 = ?,
                        output_table = ?,
                        display_name = ?
                    WHERE id = ?
                """,
                    (config_json, view_name, display_name, config_id),
                )

                if affected == 0:
                    return json_error_response(
                        "Configuration not found", status_code=404
                    )
            else:
                # Create new configuration
                # Generate a name from view_name (remove v_dwd_ prefix and convert to slug format)
                name = view_name.replace("v_dwd_", "").replace("_", " ").strip().title()

                config_id = execute_write(
                    """
                    INSERT INTO join_configs (
                        name,
                        source_events,
                        field_mapping_v2,
                        output_table,
                        display_name,
                        created_at
                    ) VALUES (?, '[]', ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (name, config_json, view_name, display_name),
                    return_last_id=True,
                )

            clear_cache_pattern("field_builder")
            logger.info(f"Field builder config saved: {config_id}")
            return json_success_response(
                data={"id": config_id, "view_name": view_name},
                message="Field builder configuration saved successfully",
            )

        except Exception as e:
            error_str = str(e).lower()
            # Check if it's a database lock error and we have retries left
            if "database is locked" in error_str and attempt < max_retries - 1:
                wait_time = delay * (2**attempt)
                logger.warning(
                    f"Database locked, retry {attempt + 1}/{max_retries} after {wait_time}s"
                )
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Error saving field builder config: {e}", exc_info=True)
                return json_error_response(
                    "An internal error occurred", status_code=500
                )


@api_bp.route("/api/field-builder/config/<int:id>", methods=["GET"])
@api_bp.route("/api/field-builder/configs/<int:id>", methods=["GET"])
def api_get_field_builder_config(id):
    """API: Load field builder configuration

    Args:
    id: Configuration ID

    Returns:
    Field builder configuration
    """
    try:
        conn = get_db_connection()

        config = conn.execute(
            """
            SELECT id, field_mapping_v2, output_table, display_name
            FROM join_configs
            WHERE id = ?
        """,
            (id,),
        ).fetchone()

        conn.close()

        if not config:
            return json_error_response("Configuration not found", status_code=404)

        field_mapping_v2 = (
            json.loads(config["field_mapping_v2"])
            if config["field_mapping_v2"]
            else None
        )

        return json_success_response(
            data={
                "id": config["id"],
                "config": field_mapping_v2,
                "view_name": config["output_table"],
                "display_name": config["display_name"],
            }
        )

    except Exception as e:
        logger.error(f"Error loading field builder config {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/field-builder/preview", methods=["POST"])
def api_preview_field_builder_hql():
    """API: Preview HQL from field builder configuration

    Request body:
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

        Returns:
        Generated HQL script
    """
    try:
        data = request.get_json()
        config = data.get("config")
        source_events = data.get("source_events", [])
        view_name = data.get("view_name", "v_dwd_preview")
        date_var = data.get("date_var", "${bizdate}")

        if not config:
            return json_error_response("Missing configuration data", status_code=400)

        if not source_events:
            return json_error_response("Missing source_events", status_code=400)

        # Build join_config for v3 generator
        join_config = {
            "source_events": json.dumps(source_events),
            "field_mapping_v2": json.dumps(config),
            "output_table": view_name,
            "display_name": "Preview",
        }

        # Use v3 generator to create HQL
        from backend.services.hql.generator_v3 import hql_generator_v3

        hql = hql_generator_v3.generate_from_field_mapping_v2(join_config, date_var)

        return json_success_response(data={"hql": hql})

    except Exception as e:
        logger.error(f"Error previewing HQL: {e}", exc_info=True)
        import traceback

        traceback.print_exc()
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/field-builder/configs", methods=["GET"])
def api_list_field_builder_configs():
    """API: List all field builder configurations

    Query params:
        - limit: Maximum number of configs to return (default: 50)
        - search: Search in display_name or view_name

        Returns:
        List of configurations
    """
    try:
        limit = request.args.get("limit", 50, type=int)
        search = request.args.get("search", "").strip()

        query = """
            SELECT
                id,
                name,
                output_table as view_name,
                display_name,
                created_at
            FROM join_configs
            WHERE field_mapping_v2 IS NOT NULL
        """
        params = []

        if search:
            query += " AND (display_name LIKE ? OR output_table LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        configs = fetch_all_as_dict(query, tuple(params))

        return json_success_response(data=configs)

    except Exception as e:
        logger.error(f"Error listing field builder configs: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/field-builder/config/<int:id>", methods=["DELETE"])
def api_delete_field_builder_config(id):
    """API: Delete a field builder configuration

    Args:
    id: Configuration ID

    Returns:
    Success message
    """
    try:
        # Check if config exists
        config = Repositories.JOIN_CONFIGS.find_by_id(id)
        if not config:
            return json_error_response("Configuration not found", status_code=404)

        Repositories.JOIN_CONFIGS.delete(id)

        clear_cache_pattern("field_builder")
        logger.info(f"Field builder config deleted: {id}")
        return json_success_response(message="Configuration deleted successfully")

    except Exception as e:
        logger.error(f"Error deleting field builder config {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)
