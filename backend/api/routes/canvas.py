#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canvas Routes

Provides API endpoints for the node canvas module.
"""

from flask import Blueprint, jsonify, render_template, request, session

from backend.core.cache.decorators import cached
from backend.core.logging import get_logger
from backend.core.utils import (
    error_response,
    json_error_response,
    json_success_response,
    success_response,
)
from backend.services.canvas.canvas_service import get_canvas_service
from backend.services.games.game_service import GameService

from . import node_canvas_flows

logger = get_logger(__name__)

canvas_bp = Blueprint("canvas", __name__)

# 获取CanvasService单例
canvas_service = get_canvas_service()
# 获取GameService单例
game_service = GameService()

@canvas_bp.route("/canvas/node_canvas")
def node_canvas():
    """
    节点画布页面

    Query Params:
        game_gid (int): 游戏GID, 必需
        react (bool): 是否使用React应用壳版本（默认false）

    Returns:
        render_template: 渲染node_canvas.html或node_canvas_react.html模板
    """
    game_gid = request.args.get("game_gid", type=int)
    use_react = request.args.get("react", "false").lower() == "true"

    # 验证game_gid参数
    if not game_gid:
        logger.warning("Accessed node_canvas without game_gid")
        from flask import flash, redirect, url_for

        flash("请先选择一个游戏", "warning")
        return redirect(url_for("games.list_games"))

    # 验证游戏是否存在
    game = game_service.get_game_by_gid(game_gid)
    if not game:
        logger.warning(f"Game not found: game_gid={game_gid}")
        return json_error_response("游戏不存在", status_code=404)

    # 设置当前游戏上下文
    session["current_game_gid"] = game_gid
    session["current_game_gid"] = game.gid

    logger.info(f"Accessed node_canvas: game_gid={game_gid}, gid={game.gid}, react={use_react}")

    # 根据react参数选择模板
    template = "node_canvas_react.html" if use_react else "node_canvas.html"
    return render_template(template, game=game)

@canvas_bp.route("/canvas/node_canvas_react")
def node_canvas_react():
    """
    节点画布页面 - React应用壳版本（Phase 2集成）

    Query Params:
        game_gid (int): 游戏GID, 必需

    Returns:
        render_template: 渲染node_canvas_react.html模板（使用React应用壳）
    """
    game_gid = request.args.get("game_gid", type=int)

    # 验证game_gid参数
    if not game_gid:
        logger.warning("Accessed node_canvas_react without game_gid")
        from flask import flash, redirect, url_for

        flash("请先选择一个游戏", "warning")
        return redirect(url_for("games.list_games"))

    # 验证游戏是否存在
    game = game_service.get_game_by_gid(game_gid)
    if not game:
        logger.warning(f"Game not found: game_gid={game_gid}")
        return json_error_response("游戏不存在", status_code=404)

    # 设置当前游戏上下文
    session["current_game_gid"] = game_gid
    session["current_game_gid"] = game.gid

    logger.info(f"Accessed node_canvas_react: game_gid={game_gid}, gid={game.gid}")

    return render_template("node_canvas_react.html", game=game)

@canvas_bp.route("/api/canvas/health", methods=["GET"])
def health_check():
    """
    健康检查端点

    Returns:
        JSON: 健康状态
    """
    return json_success_response(data={"status": "healthy"}, message="Canvas module is working")

@canvas_bp.route("/api/canvas/validate", methods=["POST"])
def validate_flow():
    """
    验证流程图结构

    Request Body:
        {
            "nodes": [...],
            "connections": [...]
        }

    Returns:
        JSON: 验证结果
    """
    try:
        graph_data = request.get_json()

        if not graph_data:
            return json_error_response("Missing request body", status_code=400)

        # 验证流程图
        validation = node_canvas_flows.validate_flow_graph(graph_data)

        if validation["valid"]:
            return jsonify(
                success_response(
                    data={
                        "execution_order": validation["execution_order"],
                        "node_count": len(graph_data.get("nodes", [])),
                        "connection_count": len(graph_data.get("connections", [])),
                    },
                    message="Flow validation successful",
                )[0]
            )
        else:
            return jsonify(error_response("; ".join(validation["errors"]), status_code=400)[0]), 400

    except Exception as e:
        logger.exception(f"Error validating flow: {e}")
        return jsonify(error_response("An internal error occurred", status_code=500)[0]), 500

@canvas_bp.route("/api/canvas/prepare", methods=["POST"])
def prepare_generation():
    """
    准备流程图用于HQL生成

    Request Body:
        {
            "nodes": [...],
            "connections": [...]
        }

    Returns:
        JSON: 准备结果
    """
    try:
        graph_data = request.get_json()

        if not graph_data:
            return json_error_response("Missing request body", status_code=400)

        # 准备流程图
        result = node_canvas_flows.prepare_flow_for_generation(graph_data)

        if result["success"]:
            return json_success_response(data=result, message="Flow prepared successfully")
        else:
            return json_error_response(result["error"], status_code=400)

    except Exception as e:
        logger.exception(f"Error preparing flow: {e}")
        return jsonify(error_response("An internal error occurred", status_code=500)[0]), 500

@canvas_bp.route("/api/canvas/preview-results", methods=["POST"])
def preview_sql_results():
    """
    预览SQL执行结果（MOCK数据 - Phase 1）

    Request Body:
        {
            "sql": "SELECT ds, role_id, ...",
            "output_fields": [
                {"name": "ds", "alias": "ds", "data_type": "string"},
                {"name": "role_id", "alias": "role_id", "data_type": "bigint"}
            ],
            "limit": 5  # Optional, default 5
        }

    Returns:
        JSON: {
            "success": true,
            "data": {
                "columns": ["ds", "role_id"],
                "rows": [["2026-01-18", 123456]],
                "row_count": 1,
                "execution_time_ms": 150
            }
        }
    """
    try:
        request_data = request.get_json()

        if not request_data:
            return json_error_response("Missing request body", status_code=400)

        sql = request_data.get("sql", "")
        output_fields = request_data.get("output_fields", [])
        limit = request_data.get("limit", 5)

        # Validate SQL syntax (basic check)
        if not sql.strip():
            return json_error_response("SQL is empty", status_code=400)

        # Generate mock results
        mock_results = generate_mock_results(output_fields, limit)

        return json_success_response(
            data=mock_results, message="Results generated successfully (MOCK DATA)"
        )

    except Exception as e:
        logger.exception(f"Error generating preview results: {e}")
        return jsonify(error_response("An internal error occurred", status_code=500)[0]), 500

def generate_mock_results(output_fields, limit=5):
    """
    基于输出字段生成Mock结果数据

    Args:
        output_fields: List of field definitions
        limit: Number of rows to generate

    Returns:
        dict: {
            "columns": ["field1", "field2"],
            "rows": [["value1", "value2"]],
            "row_count": 1,
            "execution_time_ms": 100
        }
    """
    import random
    from datetime import datetime, timedelta

    columns = [field.get("alias") or field.get("name") for field in output_fields]
    rows = []
    base_date = datetime.now()

    for i in range(limit):
        row = []
        for field in output_fields:
            field_name = field.get("name", "")
            data_type = field.get("data_type", "string")

            # Generate mock data based on field name
            if "ds" in field_name.lower():
                # Date field
                date = base_date - timedelta(days=random.randint(0, 30))
                row.append(date.strftime("%Y-%m-%d"))

            elif "role_id" in field_name.lower() or data_type == "bigint":
                # Role ID
                row.append(random.randint(100000, 999999))

            elif "account_id" in field_name.lower():
                # Account ID
                row.append(random.randint(1000000, 9999999))

            elif "zone_id" in field_name.lower() or "server_id" in field_name.lower():
                # Zone/Server ID
                row.append(random.randint(1, 100))

            elif "level" in field_name.lower():
                # Level
                row.append(random.randint(1, 100))

            elif "amount" in field_name.lower():
                # Amount
                row.append(random.randint(1, 10000))

            elif "tm" in field_name.lower():
                # Time
                time = base_date - timedelta(hours=random.randint(0, 24))
                row.append(time.strftime("%H:%M:%S"))

            elif "ts" in field_name.lower():
                # Timestamp
                ts = int((base_date - timedelta(seconds=random.randint(0, 86400))).timestamp())
                row.append(str(ts))

            elif data_type == "int":
                row.append(random.randint(0, 1000))

            elif data_type == "float":
                row.append(round(random.uniform(0, 100), 2))

            elif data_type == "boolean":
                row.append(random.choice([True, False]))

            else:
                # Default: string
                row.append(f"sample_{i + 1}")

        rows.append(row)

    return {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "execution_time_ms": random.randint(50, 200),  # Mock execution time
    }

@canvas_bp.route("/api/canvas/flows", methods=["GET"])
def list_flows():
    """
    获取Flow模板列表

    Query Params:
        game_gid (int): 游戏GID (可选, 不提供则返回所有Flow)

    Returns:
        JSON: Flow模板列表
    """
    try:
        game_gid = request.args.get("game_gid", type=int)

        if game_gid:
            flows = canvas_service.get_flows_by_game(game_gid)
        else:
            flows = canvas_service.get_all_flows()

        return json_success_response(
            data={"flows": [flow.model_dump() for flow in flows]},
            message=f"Retrieved {len(flows)} flows",
        )

    except Exception as e:
        logger.exception(f"Error listing flows: {e}")
        return json_error_response("Failed to list flows", status_code=500)

@canvas_bp.route("/api/canvas/flows/<int:flow_id>", methods=["GET"])
@cached(ttl=1800, key_prefix="canvas:flow")  # Cache for 30 minutes
def get_flow(flow_id: int):
    """
    获取单个Flow模板

    Args:
        flow_id: Flow ID

    Returns:
        JSON: Flow模板详情
    """
    try:
        flow = canvas_service.get_flow(flow_id)

        if not flow:
            return json_error_response("Flow not found", status_code=404)

        return json_success_response(data=flow.model_dump(), message="Flow retrieved successfully")

    except Exception as e:
        logger.exception(f"Error getting flow: {e}")
        return json_error_response("Failed to get flow", status_code=500)

@canvas_bp.route("/api/canvas/flows", methods=["POST"])
def create_flow():
    """
    创建Flow模板

    Request Body:
        {
            "game_gid": int,
            "flow_name": str,
            "flow_graph": dict,
            "variables": dict (可选),
            "description": str (可选),
            "created_by": str (可选)
        }

    Returns:
        JSON: 创建的Flow模板
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Missing request body", status_code=400)

        # 创建Flow
        flow = canvas_service.create_flow(
            game_gid=data.get("game_gid"),
            flow_name=data.get("flow_name"),
            flow_graph=data.get("flow_graph", {}),
            variables=data.get("variables"),
            description=data.get("description"),
            created_by=data.get("created_by"),
        )

        return json_success_response(data=flow.model_dump(), message="Flow created successfully")

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.exception(f"Error creating flow: {e}")
        return json_error_response("Failed to create flow", status_code=500)

@canvas_bp.route("/api/canvas/flows/<int:flow_id>", methods=["PUT", "PATCH"])
def update_flow(flow_id: int):
    """
    更新Flow模板

    Request Body:
        {
            "flow_name": str (可选),
            "flow_graph": dict (可选),
            "variables": dict (可选),
            "description": str (可选),
            "is_active": bool (可选)
        }

    Returns:
        JSON: 更新结果
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Missing request body", status_code=400)

        # 获取现有Flow用于获取game_gid
        existing_flow = canvas_service.get_flow(flow_id)
        if not existing_flow:
            return json_error_response("Flow not found", status_code=404)

        # 更新Flow
        success = canvas_service.update_flow(
            flow_id=flow_id,
            flow_name=data.get("flow_name"),
            flow_graph=data.get("flow_graph"),
            variables=data.get("variables"),
            description=data.get("description"),
            is_active=data.get("is_active"),
        )

        if success:
            return json_success_response(message="Flow updated successfully")
        else:
            return json_error_response("Failed to update flow", status_code=500)

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.exception(f"Error updating flow: {e}")
        return json_error_response("Failed to update flow", status_code=500)

@canvas_bp.route("/api/canvas/flows/<int:flow_id>", methods=["DELETE"])
def delete_flow(flow_id: int):
    """
    删除Flow模板 (软删除)

    Args:
        flow_id: Flow ID

    Query Params:
        game_gid (int): 游戏GID (必需, 用于缓存失效)

    Returns:
        JSON: 删除结果
    """
    try:
        game_gid = request.args.get("game_gid", type=int)

        if not game_gid:
            return json_error_response("Missing game_gid parameter", status_code=400)

        # 删除Flow
        success = canvas_service.delete_flow(flow_id, game_gid)

        if success:
            return json_success_response(message="Flow deleted successfully")
        else:
            return json_error_response("Failed to delete flow", status_code=500)

    except Exception as e:
        logger.exception(f"Error deleting flow: {e}")
        return json_error_response("Failed to delete flow", status_code=500)

@canvas_bp.route("/api/canvas/flows/<int:flow_id>/export", methods=["GET"])
def export_flow(flow_id: int):
    """
    导出Flow配置

    Args:
        flow_id: Flow ID

    Query Params:
        format (str): 导出格式 (config/hql, 默认config)

    Returns:
        JSON: Flow导出结果
    """
    try:
        export_format = request.args.get("format", "config")

        if export_format == "hql":
            result = canvas_service.export_flow_hql(flow_id)
        else:
            result = canvas_service.export_flow_config(flow_id)

        if not result:
            return json_error_response("Flow not found", status_code=404)

        return json_success_response(
            data=result, message=f"Flow exported successfully ({export_format})"
        )

    except Exception as e:
        logger.exception(f"Error exporting flow: {e}")
        return json_error_response("Failed to export flow", status_code=500)

logger.info("Canvas blueprint loaded")
