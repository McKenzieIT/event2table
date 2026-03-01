"""
Event Parameters API Routes Module

This module contains all event parameter management API endpoints.

Core endpoints:
- PUT /api/event-parameters/<int:id> - Update event parameter
- DELETE /api/event-parameters/<int:id> - Delete event parameter
- GET /api/event-parameters/<int:id>/history - Get parameter history
- GET /api/event-parameters/<int:id>/config - Get parameter config
- PUT /api/event-parameters/<int:id>/config - Set parameter config
- POST /api/event-parameters/<int:id>/rollback - Rollback parameter version
- GET /api/event-parameters/<int:id>/validation-rules - Get validation rules
- POST /api/event-parameters/<int:id>/validation-rules - Create validation rule
"""

import logging

# Import cache functions
import sys

from flask import request

# Import shared utilities
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
)

sys.path.append("..")
try:
    from backend.core.cache.cache_system import clear_cache_pattern
except ImportError:

    def clear_cache_pattern(pattern):
        pass


# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/event-parameters/<int:id>", methods=["PUT"])
def api_update_event_parameter(id):
    """API: 更新事件参数"""
    try:
        from backend.services.parameters import event_param_manager

        data = request.get_json()
        change_reason = data.get("change_reason", "更新参数")

        success = event_param_manager.update_parameter(id, data, change_reason)

        if success:
            return json_success_response(message="参数更新成功")
        else:
            return json_error_response("参数不存在", status_code=404)
    except Exception as e:
        logger.error(f"Error updating event parameter {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>", methods=["DELETE"])
def api_delete_event_parameter(id):
    """API: 删除事件参数"""
    try:
        from backend.services.parameters import event_param_manager

        success = event_param_manager.delete_parameter(id)

        if success:
            clear_cache_pattern("dashboard_statistics")
            return json_success_response(message="参数删除成功")
        else:
            return json_error_response("参数不存在", status_code=404)
    except Exception as e:
        logger.error(f"Error deleting event parameter {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/history", methods=["GET"])
def api_get_parameter_history(id):
    """API: 获取参数变更历史"""
    try:
        from backend.services.parameters import event_param_manager

        history = event_param_manager.get_parameter_history(id)

        return json_success_response(data=history)
    except Exception as e:
        logger.error(f"Error getting parameter history for {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/config", methods=["GET"])
def api_get_parameter_config(id):
    """API: 获取参数配置"""
    try:
        from backend.services.parameters import event_param_manager

        config = event_param_manager.get_parameter_config(id)

        return json_success_response(data=config)
    except Exception as e:
        logger.error(f"Error getting parameter config for {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/config", methods=["PUT"])
def api_set_parameter_config(id):
    """API: 设置参数配置"""
    try:
        from backend.services.parameters import event_param_manager

        data = request.get_json()
        success = event_param_manager.set_parameter_config(id, data)

        if success:
            return json_success_response(message="配置更新成功")
        else:
            return json_error_response("配置更新失败", status_code=500)
    except Exception as e:
        logger.error(f"Error setting parameter config for {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/rollback", methods=["POST"])
def api_rollback_parameter(id):
    """API: 回滚参数到指定版本"""
    try:
        from backend.services.parameters import event_param_manager

        data = request.get_json()
        target_version = data.get("target_version")

        if target_version is None:
            return json_error_response("Missing target_version", status_code=400)

        success = event_param_manager.rollback_to_version(id, target_version)

        if success:
            return json_success_response(message=f"成功回滚到版本 {target_version}")
        else:
            return json_error_response("回滚失败", status_code=500)
    except Exception as e:
        logger.error(f"Error rolling back parameter {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/validation-rules", methods=["GET"])
def api_get_validation_rules(id):
    """API: Get validation rules for a parameter"""
    try:
        from backend.services.validation.validation_manager import validation_manager

        rules = validation_manager.get_validation_rules(id)

        return json_success_response(data=rules)
    except Exception as e:
        logger.error(f"Error getting validation rules for {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/validation-rules", methods=["POST"])
def api_create_validation_rule(id):
    """API: Create validation rule for a parameter"""
    try:
        from backend.services.validation.validation_manager import validation_manager

        data = request.get_json()

        # Validate required fields
        required_fields = ["rule_type", "rule_config"]
        for field in required_fields:
            if field not in data:
                return json_error_response(
                    f"Missing required field: {field}", status_code=400
                )

        rule_id = validation_manager.create_validation_rule(
            event_param_id=id,
            rule_type=data["rule_type"],
            rule_config=data["rule_config"],
            error_message=data.get("error_message"),
        )

        return json_success_response(
            data={"rule_id": rule_id}, message="Validation rule created"
        )
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(
            f"Error creating validation rule for parameter {id}: {e}", exc_info=True
        )
        return json_error_response("An internal error occurred", status_code=500)
