#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
节点画布模块 - Node Canvas Module

提供可视化的节点式查询构建器功能
"""

from flask import Blueprint, render_template, request, jsonify, session
from backend.core.logging import get_logger
from backend.core.utils import (
    fetch_one_as_dict,
    success_response,
    error_response,
    json_success_response,
    json_error_response,
)
from . import node_canvas_flows

logger = get_logger(__name__)

canvas_bp = Blueprint("canvas", __name__)


@canvas_bp.route("/canvas/node_canvas")
def node_canvas():
    """
    节点画布页面

    Query Params:
        game_gid (int): 游戏GID，必需
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
    game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
    if not game:
        logger.warning(f"Game not found: game_gid={game_gid}")
        return json_error_response("游戏不存在", status_code=404)

    # 设置当前游戏上下文
    session["current_game_gid"] = game_gid
    session["current_game_gid"] = game.get("gid")

    logger.info(
        f"Accessed node_canvas: game_gid={game_gid}, gid={game.get('gid')}, react={use_react}"
    )

    # 根据react参数选择模板
    template = "node_canvas_react.html" if use_react else "node_canvas.html"
    return render_template(template, game=game)


@canvas_bp.route("/canvas/node_canvas_react")
def node_canvas_react():
    """
    节点画布页面 - React应用壳版本（Phase 2集成）

    Query Params:
        game_gid (int): 游戏GID，必需

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
    game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
    if not game:
        logger.warning(f"Game not found: game_gid={game_gid}")
        return json_error_response("游戏不存在", status_code=404)

    # 设置当前游戏上下文
    session["current_game_gid"] = game_gid
    session["current_game_gid"] = game.get("gid")

    logger.info(
        f"Accessed node_canvas_react: game_gid={game_gid}, gid={game.get('gid')}"
    )

    return render_template("node_canvas_react.html", game=game)


@canvas_bp.route("/api/canvas/health", methods=["GET"])
def health_check():
    """
    健康检查端点

    Returns:
        JSON: 健康状态
    """
    return json_success_response(
        data={"status": "healthy"}, message="Canvas module is working"
    )


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
            return jsonify(
                error_response("; ".join(validation["errors"]), status_code=400)[0]
            ), 400

    except Exception as e:
        logger.exception(f"Error validating flow: {e}")
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


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
            return json_success_response(
                data=result, message="Flow prepared successfully"
            )
        else:
            return json_error_response(result["error"], status_code=400)

    except Exception as e:
        logger.exception(f"Error preparing flow: {e}")
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


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
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


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
                ts = int(
                    (
                        base_date - timedelta(seconds=random.randint(0, 86400))
                    ).timestamp()
                )
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


logger.info("Canvas blueprint loaded")
