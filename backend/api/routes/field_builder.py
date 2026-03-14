"""
Field Builder API Routes Module (ERS架构)

This module contains all field builder-related API endpoints for managing
field configurations, generating HQL previews, and managing view configurations.

架构:
- API Layer: 处理HTTP请求/响应
- Service Layer: FieldBuilderService实现业务逻辑
- Repository Layer: JoinConfigRepository访问数据
- Entity Layer: FieldBuilderConfigEntity统一数据模型

Core endpoints:
- POST /api/field-builder/config - Save field builder configuration
- GET /api/field-builder/config/<int:id> - Get field builder configuration
- POST /api/field-builder/preview - Preview HQL from field builder configuration
- GET /api/field-builder/configs - List field builder configurations
- DELETE /api/field-builder/config/<int:id> - Delete field builder configuration
"""

import logging

from flask import request

# Import shared utilities
from backend.core.utils import json_error_response, json_success_response

# Import Service Layer
from backend.services.field_builder import FieldBuilderService

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)

# Initialize Service
field_builder_service = FieldBuilderService()


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
        "display_name": "Custom View Display Name",
        "id": 1  # Optional, for update
    }

    Returns:
        Saved configuration with ID
    """
    try:
        data = request.get_json()

        # 验证必填字段
        config = data.get("config")
        view_name = data.get("view_name")
        display_name = data.get("display_name", view_name)
        config_id = data.get("id")  # 可选, 用于更新

        # 调用Service层
        result = field_builder_service.save_config(
            config=config, view_name=view_name, display_name=display_name, config_id=config_id
        )

        return json_success_response(
            data=result,
            message="Field builder configuration saved successfully",
        )

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error saving field builder config: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


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
        # 调用Service层
        config = field_builder_service.get_config_by_id(id)

        if not config:
            return json_error_response("Configuration not found", status_code=404)

        return json_success_response(data=config)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
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

        # 验证必填字段
        config = data.get("config")
        source_events = data.get("source_events", [])
        view_name = data.get("view_name", "v_dwd_preview")
        date_var = data.get("date_var", "${bizdate}")

        # 调用Service层
        hql = field_builder_service.preview_hql(
            config=config, source_events=source_events, view_name=view_name, date_var=date_var
        )

        return json_success_response(data={"hql": hql})

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error previewing HQL: {e}", exc_info=True)
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
        # 获取查询参数
        limit = request.args.get("limit", 50, type=int)
        search = request.args.get("search", "").strip()

        # 调用Service层
        configs = field_builder_service.list_configs(limit=limit, search=search if search else None)

        return json_success_response(data=configs)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
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
        # 调用Service层
        field_builder_service.delete_config(id)

        return json_success_response(message="Configuration deleted successfully")

    except ValueError as e:
        if "not found" in str(e).lower():
            return json_error_response(str(e), status_code=404)
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error deleting field builder config {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)
