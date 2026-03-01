"""
HQL Generation API Routes Module

This module contains all HQL generation-related API endpoints for generating,
validating, and managing HQL scripts.

Core endpoints:
- POST /api/generate - Generate HQL scripts for selected events/joins
- GET /api/hql/<int:id> - Get HQL content by ID
- POST /api/validate-hql - Validate HQL syntax and structure
"""

import logging
import re

from flask import request

# Import shared utilities
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
    validate_json_request,
)

# Import cached HQL service
from backend.services.hql.hql_service_cached import HQLServiceCached

# Import HQL Facade for HQL generation
from backend.services.hql.hql_facade import HQLFacade

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)

# Initialize cached HQL service
hql_service = HQLServiceCached()


@api_bp.route("/api/generate", methods=["POST"])
def api_generate_hql():
    """API: Generate HQL scripts for selected events and joins

    Request body:
    {
        "selected_events": [{"event_name": "login", "table_name": "ods_10000147_all_view"}],
        "selected_fields": [{"param_name": "zone_id", "param_type": "param", "json_path": "$.zoneId"}],
        "selected_conditions": [{"field": "zone_id", "operator": "=", "value": "1"}],
        "date_str": "${bizdate}",
        "mode": "single"  # or "join", "union"
    }

    Response:
    {
        "success": true,
        "data": {
            "hql": "CREATE OR REPLACE VIEW ...",
            "tables": ["dwd.v_dwd_10000147_login_di"]
        }
    }
    """
    is_valid, data, error = validate_json_request()
    if not is_valid:
        return json_error_response(error)

    selected_events = data.get("selected_events", [])
    selected_fields = data.get("selected_fields", [])
    selected_conditions = data.get("selected_conditions", [])
    date_str = data.get("date_str", "${bizdate}")
    mode = data.get("mode", "single")

    if not selected_events:
        return json_error_response("No events selected", status_code=400)

    try:
        # Use HQLFacade for HQL generation
        hql_facade = HQLFacade()

        # Convert input to HQL models
        from backend.services.hql.models.event import Event, Field, Condition

        events = [
            Event(
                name=e.get("event_name"),
                table_name=e.get("table_name")
            )
            for e in selected_events
        ]

        fields = []
        if selected_fields:
            for f in selected_fields:
                field_kwargs = {
                    "name": f.get("param_name"),
                    "type": f.get("param_type", "param")
                }
                if f.get("json_path"):
                    field_kwargs["json_path"] = f.get("json_path")
                fields.append(Field(**field_kwargs))

        conditions = []
        if selected_conditions:
            for c in selected_conditions:
                conditions.append(
                    Condition(
                        field=c.get("field"),
                        operator=c.get("operator", "="),
                        value=c.get("value")
                    )
                )

        # Generate HQL using HQLFacade
        result = hql_facade.generate_hql(
            events=events,
            fields=fields,
            conditions=conditions,
            mode=mode,
            date_str=date_str
        )

        return json_success_response(
            data={"hql": result["hql"], "tables": result.get("tables", [])},
            message="Generated HQL successfully"
        )
    except Exception as e:
        logger.error(f"Error generating HQL: {e}", exc_info=True)
        return json_error_response("Failed to generate HQL", status_code=500)


@api_bp.route("/api/hql/<int:id>", methods=["GET"])
def api_get_hql(id):
    """API: Get HQL content by ID

    Note: This endpoint uses direct database access as a simple fallback.
    In the future, this should be migrated to use HQLRepository or HQLService.
    """
    try:
        # Query from hql_statements table
        hql = fetch_one_as_dict(
            """
            SELECT * FROM hql_statements
            WHERE id = ?
            ORDER BY hql_version DESC
            LIMIT 1
        """,
            (id,),
        )

        if hql:
            return json_success_response(data=hql)
        return json_error_response("HQL not found", status_code=404)
    except Exception as e:
        logger.error(f"Error getting HQL {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/validate-hql", methods=["POST"])
def api_validate_hql():
    """
    API: Validate HQL syntax and structure (with caching)

    Request body:
    {
        "hql_content": "CREATE OR REPLACE VIEW..."
    }

    Response:
    {
        "success": true,
        "data": {
            "is_valid": true/false,
            "error_count": 0,
            "sanitized_fields": [
                {"original": "e1.zoneId", "sanitized": "e1_zoneId"}
            ],
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
    }
    """
    is_valid, data, error = validate_json_request(["hql_content"])
    if not is_valid:
        return json_error_response(error)

    hql_content = data["hql_content"]
    use_cache = data.get("use_cache", True)  # 默认使用缓存

    try:
        # 使用缓存增强版服务验证HQL
        validation_result = hql_service.validate_hql(hql_content, use_cache=use_cache)
        
        # 转换为API响应格式
        result = {
            "is_valid": validation_result.get("valid", False),
            "error_count": len(validation_result.get("syntax_errors", [])),
            "sanitized_fields": [],  # TODO: 从验证结果中提取
            "errors": validation_result.get("syntax_errors", []),
            "warnings": [],
            "recommendations": [],
            "performance": validation_result.get("performance", {}),
        }

        # 1. Check for field names with dots and track sanitization
        # Pattern: AS <field_with_dot>
        dot_field_pattern = r"AS\s+([a-zA-Z0-9_]+\.[a-zA-Z0-9_\.]+)"
        matches = re.finditer(dot_field_pattern, hql_content)

        for match in matches:
            original_field = match.group(1)
            sanitized_field = original_field.replace(".", "_")
            result["sanitized_fields"].append(
                {"original": original_field, "sanitized": sanitized_field}
            )
            result["warnings"].append(
                f"Field name with dot detected: {original_field} → {sanitized_field}"
            )

        # 2. Check for CREATE VIEW syntax
        if not re.search(
            r"CREATE\s+(OR\s+REPLACE\s+)?VIEW", hql_content, re.IGNORECASE
        ):
            result["errors"].append("Missing CREATE VIEW statement")
            result["is_valid"] = False
            result["error_count"] += 1

        # 3. Check for SELECT statement
        if not re.search(r"SELECT", hql_content, re.IGNORECASE):
            result["errors"].append("Missing SELECT statement")
            result["is_valid"] = False
            result["error_count"] += 1

        # 4. Check for FROM clause
        if not re.search(r"FROM", hql_content, re.IGNORECASE):
            result["errors"].append("Missing FROM clause")
            result["is_valid"] = False
            result["error_count"] += 1

        # 5. Check for common SQL keywords
        required_keywords = ["SELECT", "FROM"]
        missing_keywords = [
            kw for kw in required_keywords if kw not in hql_content.upper()
        ]
        if missing_keywords:
            result["errors"].append(
                f"Missing required keywords: {', '.join(missing_keywords)}"
            )
            result["is_valid"] = False
            result["error_count"] += len(missing_keywords)

        # 6. Check for balanced parentheses
        open_parens = hql_content.count("(")
        close_parens = hql_content.count(")")
        if open_parens != close_parens:
            result["errors"].append(
                f"Unbalanced parentheses: {open_parens} opening, {close_parens} closing"
            )
            result["is_valid"] = False
            result["error_count"] += 1

        # 7. Recommendations
        if not re.search(r"CREATE\s+OR\s+REPLACE\s+VIEW", hql_content, re.IGNORECASE):
            if re.search(r"CREATE\s+VIEW", hql_content, re.IGNORECASE):
                result["recommendations"].append(
                    "Consider using CREATE OR REPLACE VIEW instead of CREATE VIEW"
                )

        if "${bizdate}" not in hql_content and "ds =" not in hql_content:
            result["recommendations"].append(
                "Consider using ${bizdate} variable for date filtering"
            )

        return json_success_response(data=result)
    except Exception as e:
        logger.error(f"Error validating HQL: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/hql/<int:id>/deactivate", methods=["POST"])
def api_deactivate_hql(id):
    """API: Deactivate an HQL statement

    Note: This endpoint uses direct database access as a simple fallback.
    In the future, this should be migrated to use HQLRepository or HQLService.
    """
    try:
        from backend.core.utils import execute_write

        execute_write("UPDATE hql_statements SET is_active = 0 WHERE id = ?", (id,))
        return json_success_response(message="HQL deactivated successfully")
    except Exception as e:
        logger.error(f"Error deactivating HQL {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/hql/<int:id>/activate", methods=["POST"])
def api_activate_hql(id):
    """API: Activate an HQL statement

    Note: This endpoint uses direct database access as a simple fallback.
    In the future, this should be migrated to use HQLRepository or HQLService.
    """
    try:
        current = fetch_one_as_dict(
            """
            SELECT id, hql_version FROM hql_statements
            WHERE id = ?
            ORDER BY hql_version DESC
            LIMIT 1
        """,
            (id,),
        )

        if current and current["hql_version"] > 1:
            from backend.core.utils import execute_write

            execute_write(
                """
                UPDATE hql_statements
                SET is_active = 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (id,),
            )
            return json_success_response(message="HQL activated successfully")

        return json_error_response("HQL is already the latest version", status_code=400)
    except Exception as e:
        logger.error(f"Error activating HQL {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)
