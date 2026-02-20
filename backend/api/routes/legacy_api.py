"""
⚠️ DEPRECATED: 此API已废弃，不建议使用
⚠️ DEPRECATED: This API is deprecated, do not use

废弃原因:
- 安全风险：多处未验证的用户输入
- 维护困难：代码结构混乱
- 功能重复：新API已替代

建议迁移到:
- events.py
- games.py
- parameters.py

Legacy API Routes Module

This module contains legacy/compatibility API endpoints for frontend compatibility.
These are aliases and convenience endpoints for existing functionality.

Endpoints:
- HQL APIs: /api/hql, /api/hql/results
- Common Params APIs: /api/common-params, /api/common-params/batch
- Excel Import APIs: /api/preview-excel
- Logs APIs: /api/logs
- Games APIs: /api/games/by-gid/<gid>
- Event Node Builder: /event_node_builder/api/update-param-name
"""

import logging

from flask import request

# Import shared utilities
from backend.core.utils import (
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
)

# Import Repository pattern for data access
from backend.core.data_access import Repositories

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


# ============================================================================
# HQL APIs
# ============================================================================


@api_bp.route("/api/hql", methods=["GET"])
def api_hql_query():
    """API: HQL query endpoint (legacy compatibility)"""
    try:
        # Get query parameters
        game_gid = request.args.get("game_gid", type=int)
        event_ids = request.args.get("event_ids")
        bizdate = request.args.get("bizdate")

        if not game_gid:
            return json_error_response("Missing game_gid parameter", status_code=400)

        # For now, return a placeholder response
        # In production, this would execute HQL generation
        return json_success_response(
            data={
                "game_gid": game_gid,
                "event_ids": event_ids,
                "bizdate": bizdate,
                "hql": "-- HQL query placeholder\n-- Use the HQL generation API",
            },
            message="HQL query (placeholder - use full HQL generation API)",
        )

    except Exception as e:
        logger.error(f"Error in HQL query: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/hql/results", methods=["GET"])
def api_hql_results():
    """API: Get HQL generation results"""
    try:
        job_id = request.args.get("job_id")
        limit = request.args.get("limit", 50, type=int)

        if job_id:
            # Get specific job results
            result = fetch_one_as_dict(
                "SELECT * FROM hql_results WHERE job_id = ? ORDER BY created_at DESC LIMIT 1",
                (job_id,),
            )
        else:
            # Get recent results
            result = fetch_all_as_dict(
                "SELECT * FROM hql_results ORDER BY created_at DESC LIMIT ?", (limit,)
            )

        return json_success_response(data=result or [])

    except Exception as e:
        logger.error(f"Error fetching HQL results: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


# ============================================================================
# Common Params APIs
# ============================================================================


@api_bp.route("/api/common-params", methods=["GET"])
def api_list_common_params():
    """API: List common parameters for a specific game"""
    try:
        # Get game_gid from query parameters
        game_gid = request.args.get("game_gid", type=int)

        if not game_gid:
            return json_error_response("game_gid is required", status_code=400)

        # Get game_id from game_gid
        game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
        if not game:
            return json_error_response(f"Game {game_gid} not found", status_code=404)

        game_id = game["id"]

        # Fetch common params for this game only
        common_params = fetch_all_as_dict(
            """
            SELECT
                id,
                game_id,
                param_name,
                param_name_cn,
                param_type,
                table_name,
                status,
                created_at,
                updated_at
            FROM common_params
            WHERE game_id = ?
            ORDER BY created_at DESC
        """,
            (game_id,),
        )

        # Map param_type to data_type for frontend compatibility
        for param in common_params:
            param["data_type"] = param.get("param_type", "string")
            param["key"] = param.get("param_name", "")
            param["name"] = param.get("param_name_cn", param.get("param_name", ""))
            param["description"] = param.get("param_description", "")

        return json_success_response(data=common_params)

    except Exception as e:
        logger.error(f"Error fetching common params: {e}")
        return json_error_response("Failed to fetch common params", status_code=500)


@api_bp.route("/api/common-params/<int:id>", methods=["DELETE"])
def api_delete_common_param(id):
    """API: Delete a common parameter"""
    try:
        # Verify parameter exists
        param = Repositories.COMMON_PARAMS.find_by_id(id)
        if not param:
            return json_error_response("Parameter not found", status_code=404)

        Repositories.COMMON_PARAMS.delete(id)

        logger.info(f"Common param deleted: {param['name']} (ID: {id})")
        return json_success_response(message="Parameter deleted successfully")

    except Exception as e:
        logger.error(f"Error deleting common param: {e}")
        return json_error_response("Failed to delete parameter", status_code=500)


@api_bp.route("/api/common-params/batch", methods=["GET"])
def api_batch_get_common_params():
    """API: Batch fetch common parameters by IDs"""
    try:
        param_ids = request.args.get("ids", "")

        if not param_ids:
            # Return all common parameters if no IDs specified
            common_params = fetch_all_as_dict("""
                SELECT
                    cp.*,
                    u.username as created_by_name
                FROM common_params cp
                LEFT JOIN users u ON cp.created_by = u.id
                ORDER BY cp.name
            """)
            return json_success_response(data=common_params)

        # Parse IDs from comma-separated string
        ids_list = [
            int(id_str.strip())
            for id_str in param_ids.split(",")
            if id_str.strip().isdigit()
        ]

        if not ids_list:
            return json_error_response("Invalid ids parameter", status_code=400)

        placeholders = ",".join(["?" for _ in ids_list])
        common_params = fetch_all_as_dict(
            f"""
            SELECT
                cp.*,
                u.username as created_by_name
            FROM common_params cp
            LEFT JOIN users u ON cp.created_by = u.id
            WHERE cp.id IN ({placeholders})
            ORDER BY cp.name
        """,
            tuple(ids_list),
        )

        return json_success_response(data=common_params)

    except Exception as e:
        logger.error(f"Error batch fetching common params: {e}")
        return json_error_response("Failed to fetch parameters", status_code=500)


@api_bp.route("/api/common-params/batch", methods=["DELETE"])
def api_batch_delete_common_params():
    """API: Batch delete common parameters"""
    try:
        data = request.get_json()
        param_ids = data.get("ids", [])

        if not param_ids:
            return json_error_response("Missing ids parameter", status_code=400)

        placeholders = ",".join(["?" for _ in param_ids])
        affected = execute_write(
            f"DELETE FROM common_params WHERE id IN ({placeholders})", tuple(param_ids)
        )

        logger.info(f"Batch deleted {affected} common params")
        return json_success_response(
            message=f"Deleted {affected} parameters successfully",
            data={"deleted_count": affected},
        )

    except Exception as e:
        logger.error(f"Error batch deleting common params: {e}")
        return json_error_response("Failed to batch delete parameters", status_code=500)


# ============================================================================
# Excel Import APIs
# ============================================================================


@api_bp.route("/api/preview-excel", methods=["POST"])
def api_preview_excel():
    """
    API: Preview Excel file data

    Expects multipart/form-data with:
        file: Excel file to preview
        header_row: Header row index (default: 0)
        data_start_row: Data start row index (default: 1)
        preview_rows: Number of rows to preview (default: 10)

    Returns:
        JSON response with preview data and column information
    """
    import openpyxl
    from io import BytesIO
    from werkzeug.utils import secure_filename

    try:
        # Check if file is present
        if "file" not in request.files:
            return json_error_response("No file provided", status_code=400)

        file = request.files["file"]

        # Check if filename is empty
        if file.filename == "":
            return json_error_response("No file selected", status_code=400)

        # Get optional parameters
        header_row = request.form.get("header_row", 0, type=int)
        data_start_row = request.form.get("data_start_row", 1, type=int)
        preview_rows = request.form.get("preview_rows", 10, type=int)

        # Validate file extension
        if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
            return json_error_response(
                "Invalid file format. Please upload an Excel file (.xlsx or .xls)",
                status_code=400,
            )

        # Read file
        file_stream = BytesIO(file.read())
        workbook = openpyxl.load_workbook(file_stream, read_only=True, data_only=True)

        # Get first sheet
        sheet = workbook.active

        # Read all data
        all_data = []
        for row in sheet.iter_rows(values_only=True):
            all_data.append(row)

        # Extract headers
        headers = []
        if 0 <= header_row < len(all_data):
            headers = [
                str(cell) if cell is not None else "" for cell in all_data[header_row]
            ]

        # Extract data rows
        data_rows = []
        start = max(data_start_row, 0)
        end = min(start + preview_rows, len(all_data))

        for i in range(start, end):
            if i < len(all_data):
                row = all_data[i]
                # Convert to string and handle None values
                processed_row = [str(cell) if cell is not None else "" for cell in row]
                data_rows.append(processed_row)

        # Get column count
        column_count = (
            len(headers) if headers else (len(all_data[0]) if all_data else 0)
        )

        workbook.close()

        logger.info(
            f"Excel preview: {file.filename}, {len(data_rows)} rows, {column_count} columns"
        )

        return json_success_response(
            data={
                "filename": secure_filename(file.filename),
                "headers": headers,
                "rows": data_rows,
                "total_rows": len(all_data),
                "column_count": column_count,
                "preview_rows_count": len(data_rows),
            },
            message=f"Successfully previewed {len(data_rows)} rows from {file.filename}",
        )

    except openpyxl.utils.exceptions.InvalidFileException as e:
        logger.error(f"Invalid Excel file: {e}")
        return json_error_response(
            "Invalid Excel file format. Please upload a valid .xlsx or .xls file.",
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error previewing Excel file: {e}", exc_info=True)
        return json_error_response(
            f"Failed to preview Excel file: {str(e)}", status_code=500
        )


# ============================================================================
# Logs APIs
# ============================================================================


@api_bp.route("/api/logs/<int:id>", methods=["GET"])
def api_get_log(id):
    """API: Get a log entry by ID"""
    try:
        log = fetch_one_as_dict("SELECT * FROM logs WHERE id = ?", (id,))

        if not log:
            return json_error_response("Log not found", status_code=404)

        return json_success_response(data=log)

    except Exception as e:
        logger.error(f"Error fetching log {id}: {e}")
        return json_error_response("Failed to fetch log", status_code=500)


@api_bp.route("/api/logs/<int:id>", methods=["PUT"])
def api_update_log(id):
    """API: Update a log entry"""
    try:
        log = fetch_one_as_dict("SELECT * FROM logs WHERE id = ?", (id,))
        if not log:
            return json_error_response("Log not found", status_code=404)

        data = request.get_json()

        execute_write(
            "UPDATE logs SET log_name = ?, description = ? WHERE id = ?",
            (
                data.get("log_name", log["log_name"]),
                data.get("description", log.get("description")),
                id,
            ),
        )

        logger.info(f"Log updated: {id}")
        return json_success_response(message="Log updated successfully")

    except Exception as e:
        logger.error(f"Error updating log: {e}")
        return json_error_response("Failed to update log", status_code=500)


# ============================================================================
# Games APIs
# ============================================================================
# NOTE: Games endpoints have been migrated to backend/api/routes/games.py
# The following routes are now defined in:
# - GET /api/games/by-gid/<int:gid> -> games.py:api_get_game_by_gid


# ============================================================================
# Event Node Builder APIs
# ============================================================================
#
# NOTE: The following route has been REMOVED to avoid conflicts with event_node_builder_bp
#
# The real implementation is in backend/services/node/event_node_builder.py:1388
# which is registered with url_prefix='/event_node_builder'
#
# Removed route:
# - /event_node_builder/api/update-param-name (line 1388 in event_node_builder.py)
#
# Frontend should call: PUT /event_node_builder/api/update-param-name
# ============================================================================
