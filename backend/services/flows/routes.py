#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEPRECATED: Flows Service Routes

⚠️ DEPRECATION NOTICE (2026-02-20)
=================================
This module is DEPRECATED and should not be used for new development.

All flow endpoints have been migrated to:
  - backend/api/routes/flows.py (using api_bp)

Migration Status:
  ✅ GET /api/flows -> backend/api/routes/flows.py::api_list_flows()
  ✅ POST /api/flows -> backend/api/routes/flows.py::api_create_flow()
  ✅ GET /api/flows/<id> -> backend/api/routes/flows.py::api_get_flow()
  ✅ PUT /api/flows/<id> -> backend/api/routes/flows.py::api_update_flow()
  ✅ DELETE /api/flows/<id> -> backend/api/routes/flows.py::api_delete_flow()
  ✅ /canvas/api/flows/save -> backend/api/routes/flows.py::canvas_api_flows_save()
  ✅ /canvas/api/flows/<id> -> backend/api/routes/flows.py::canvas_api_flows_get()
  ✅ /canvas/api/health -> backend/api/routes/flows.py::canvas_api_health()

This module is kept for backward compatibility only.
DO NOT add new routes to this file.

To be removed after full migration and testing.

Original module description:
=============================
Flows Service Routes

流程/Canvas管理路由

提供流程模板的CRUD操作和相关功能
"""

import logging
from flask import request, jsonify
from backend.services.flows import flows_bp
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_success_response,
    json_error_response,
    execute_write,
    sanitize_and_validate_string,
)
from backend.models.repositories.flow_repository import FlowRepository
from backend.models.schemas import FlowTemplateCreate, FlowTemplateUpdate

logger = logging.getLogger(__name__)


# ============================================================================
# Flow Template CRUD Endpoints
# ============================================================================


@flows_bp.route("/api/flows", methods=["GET"])
def list_flows():
    """
    获取流程列表

    Query Parameters:
        game_gid: int (required) - 游戏GID

    Returns:
        JSON响应包含流程列表
    """
    game_gid = request.args.get("game_gid", type=int)

    if not game_gid:
        return json_error_response("game_gid required", status_code=400)

    try:
        repo = FlowRepository()
        flows = repo.find_by_game_gid(game_gid)

        return json_success_response(
            data=flows, message=f"Retrieved {len(flows)} flows"
        )

    except Exception as e:
        logger.error(
            f"Failed to list flows for game_gid={game_gid}: {e}", exc_info=True
        )
        return json_error_response("An internal error occurred", status_code=500)


@flows_bp.route("/api/flows", methods=["POST"])
def create_flow():
    """
    创建新流程

    Request Body:
        {
            "game_id": int (required),
            "flow_name": str (required, 1-200 chars),
            "description": str (optional, max 1000 chars),
            "flow_graph": dict (optional),
            "variables": dict (optional),
            "created_by": str (optional),
            "is_active": bool (optional, default true)
        }

    Returns:
        JSON响应包含创建的流程数据
    """
    try:
        # 验证请求数据
        data = FlowTemplateCreate(**request.json)

        repo = FlowRepository()
        flow_id = repo.create(data.dict())

        # 获取创建的流程
        flow = repo.find_by_id(flow_id)

        logger.info(f"Flow created successfully: id={flow_id}, name={data.flow_name}")

        return json_success_response(data=flow, message="Flow created successfully")

    except Exception as e:
        logger.error(f"Failed to create flow: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@flows_bp.route("/api/flows/<int:flow_id>", methods=["GET"])
def get_flow(flow_id):
    """
    获取单个流程详情

    Parameters:
        flow_id: int (path parameter) - 流程ID

    Returns:
        JSON响应包含流程详情
    """
    try:
        repo = FlowRepository()
        flow = repo.find_by_id(flow_id)

        if not flow:
            return json_error_response("Flow not found", status_code=404)

        return json_success_response(data=flow, message="Flow retrieved successfully")

    except Exception as e:
        logger.error(f"Failed to get flow id={flow_id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@flows_bp.route("/api/flows/<int:flow_id>", methods=["PUT"])
def update_flow(flow_id):
    """
    更新流程

    Parameters:
        flow_id: int (path parameter) - 流程ID

    Request Body:
        {
            "flow_name": str (optional),
            "description": str (optional),
            "flow_graph": dict (optional),
            "variables": dict (optional),
            "is_active": bool (optional)
        }

    Returns:
        JSON响应包含更新后的流程数据
    """
    try:
        # 验证请求数据
        data = FlowTemplateUpdate(**request.json)

        repo = FlowRepository()

        # 检查流程是否存在
        existing = repo.find_by_id(flow_id)
        if not existing:
            return json_error_response("Flow not found", status_code=404)

        # 只更新提供的字段
        update_data = data.dict(exclude_unset=True)
        if update_data:
            repo.update(flow_id, update_data)
            logger.info(
                f"Flow updated: id={flow_id}, fields={list(update_data.keys())}"
            )

        # 获取更新后的流程
        flow = repo.find_by_id(flow_id)

        return json_success_response(data=flow, message="Flow updated successfully")

    except Exception as e:
        logger.error(f"Failed to update flow id={flow_id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@flows_bp.route("/api/flows/<int:flow_id>", methods=["DELETE"])
def delete_flow(flow_id):
    """
    删除流程（软删除）

    Parameters:
        flow_id: int (path parameter) - 流程ID

    Returns:
        JSON响应确认删除成功

    Note:
        此操作为软删除，流程将被标记为is_active=0
    """
    try:
        repo = FlowRepository()

        # 检查流程是否存在
        existing = repo.find_by_id(flow_id)
        if not existing:
            return json_error_response("Flow not found", status_code=404)

        # 软删除
        repo.delete(flow_id)

        logger.info(
            f"Flow deleted (soft): id={flow_id}, name={existing.get('flow_name')}"
        )

        return json_success_response(message="Flow deleted successfully")

    except Exception as e:
        logger.error(f"Failed to delete flow id={flow_id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@flows_bp.route("/api/flows/<int:flow_id>/hard-delete", methods=["DELETE"])
def hard_delete_flow(flow_id):
    """
    硬删除流程（从数据库中彻底删除）

    Parameters:
        flow_id: int (path parameter) - 流程ID

    Warning:
        此操作不可恢复，请谨慎使用
    """
    try:
        repo = FlowRepository()

        # 检查流程是否存在
        existing = repo.find_by_id(flow_id)
        if not existing:
            return json_error_response("Flow not found", status_code=404)

        # 硬删除
        repo.hard_delete(flow_id)

        logger.warning(
            f"Flow hard deleted: id={flow_id}, name={existing.get('flow_name')}"
        )

        return json_success_response(message="Flow permanently deleted")

    except Exception as e:
        logger.error(f"Failed to hard delete flow id={flow_id}: {e}", exc_info=True)
        return json_error_response("An internal error occurred", status_code=500)


@flows_bp.route("/api/flows/count", methods=["GET"])
def count_flows():
    """
    统计流程数量

    Query Parameters:
        game_gid: int (required) - 游戏GID

    Returns:
        JSON响应包含流程数量
    """
    game_gid = request.args.get("game_gid", type=int)

    if not game_gid:
        return json_error_response("game_gid required", status_code=400)

    try:
        repo = FlowRepository()
        count = repo.count_by_game_gid(game_gid)

        return json_success_response(
            data={"count": count}, message=f"Game has {count} active flows"
        )

    except Exception as e:
        logger.error(
            f"Failed to count flows for game_gid={game_gid}: {e}", exc_info=True
        )
        return json_error_response("An internal error occurred", status_code=500)


# ============================================================================
# Canvas API Compatibility Endpoints
# ============================================================================


@flows_bp.route("/canvas/api/flows/save", methods=["POST"])
def canvas_save_flow():
    """
    Canvas API: 保存流程（兼容性别名）

    与 POST /api/flows 功能相同，但路径不同，用于前端兼容
    """
    return create_flow()


@flows_bp.route("/canvas/api/flows/<int:flowId>", methods=["GET"])
def canvas_get_flow(flowId):
    """
    Canvas API: 获取流程详情（兼容性别名）

    与 GET /api/flows/<id> 功能相同，但路径不同，用于前端兼容
    """
    return get_flow(flowId)


@flows_bp.route("/canvas/api/health", methods=["GET"])
def canvas_health():
    """
    Canvas API: 健康检查端点

    Returns:
        JSON响应确认Canvas服务健康状态
    """
    return json_success_response(
        data={"status": "healthy", "service": "canvas"},
        message="Canvas service is healthy",
    )


# ============================================================================
# Export All
# ============================================================================

__all__ = [
    "flows_bp",
]
