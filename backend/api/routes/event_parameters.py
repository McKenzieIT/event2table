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

Architecture Update (V9.0.0):
- Uses ParameterService for business logic and caching
- Uses unified Entity model (ParameterEntity)
- Service layer handles business logic and caching
- Repository layer handles data access
- Note: History and config endpoints still use deprecated event_param_manager
"""

import logging

# Import cache functions
import sys

from flask import request

# Import shared utilities
from backend.core.utils import json_error_response, json_success_response

# Import ParameterService for business logic
from backend.services.parameters.parameter_service import ParameterService

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
    """
    API: 更新事件参数

    Uses ParameterService for business logic and cache management.
    """
    try:
        service = ParameterService()
        data = request.get_json()

        # Extract update data
        update_data = {}
        if "param_name" in data:
            update_data["name"] = data["param_name"]
        if "param_name_cn" in data:
            update_data["param_name_cn"] = data["param_name_cn"]
        if "param_type" in data:
            update_data["param_type"] = data["param_type"]
        if "json_path" in data:
            update_data["json_path"] = data["json_path"]

        # Update parameter via service
        updated_param = service.update_parameter(id, update_data)

        return json_success_response(data=updated_param.model_dump(), message="参数更新成功")

    except ValueError as e:
        logger.error(f"Validation error updating event parameter {id}: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error updating event parameter {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>", methods=["DELETE"])
def api_delete_event_parameter(id):
    """
    API: 删除事件参数

    Uses ParameterService for business logic and cache management.
    """
    try:
        service = ParameterService()

        # Delete parameter via service
        success = service.delete_parameter(id)

        if success:
            clear_cache_pattern("dashboard_statistics")
            return json_success_response(message="参数删除成功")
        else:
            return json_error_response("参数不存在", status_code=404)

    except ValueError as e:
        logger.error(f"Validation error deleting event parameter {id}: {e}")
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error deleting event parameter {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/history", methods=["GET"])
def api_get_parameter_history(id):
    """
    API: 获取参数变更历史

    NOTE: Still using EventParamManager for history tracking.
    TODO: Migrate to ParameterService when history tracking is implemented.
    """
    try:
        from backend.services.parameters import event_param_manager

        history = event_param_manager.get_parameter_history(id)

        return json_success_response(data=history)
    except Exception as e:
        logger.error(f"Error getting parameter history for {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/config", methods=["GET"])
def api_get_parameter_config(id):
    """
    API: 获取参数配置

    NOTE: Still using EventParamManager for config management.
    TODO: Migrate to ParameterService when config management is implemented.
    """
    try:
        from backend.services.parameters import event_param_manager

        config = event_param_manager.get_parameter_config(id)

        return json_success_response(data=config)
    except Exception as e:
        logger.error(f"Error getting parameter config for {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@api_bp.route("/api/event-parameters/<int:id>/config", methods=["PUT"])
def api_set_parameter_config(id):
    """
    API: 设置参数配置

    NOTE: Still using EventParamManager for config management.
    TODO: Migrate to ParameterService when config management is implemented.
    """
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
    """
    API: 回滚参数到指定版本

    NOTE: Still using EventParamManager for rollback functionality.
    TODO: Migrate to ParameterService when rollback is implemented.
    """
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
                return json_error_response(f"Missing required field: {field}", status_code=400)

        rule_id = validation_manager.create_validation_rule(
            event_param_id=id,
            rule_type=data["rule_type"],
            rule_config=data["rule_config"],
            error_message=data.get("error_message"),
        )

        return json_success_response(data={"rule_id": rule_id}, message="Validation rule created")
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error creating validation rule for parameter {id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)
