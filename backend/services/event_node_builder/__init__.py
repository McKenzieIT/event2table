#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Node Builder Module
事件节点构建器模块 - 提供前端 EventNodeBuilder 页面需要的 API 路由

这些路由作为现有 API 的包装器，将 /event_node_builder/* 请求转发到相应的后端服务
"""

from flask import Blueprint, request, jsonify
from backend.core.logging import get_logger
from backend.core.utils import (
    json_success_response,
    json_error_response,
    fetch_one_as_dict,
    fetch_all_as_dict,
)

logger = get_logger(__name__)

event_node_builder_bp = Blueprint(
    "event_node_builder", __name__, url_prefix="/event_node_builder"
)


def validate_game_exists(game_gid: int) -> bool:
    """验证游戏是否存在"""
    game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
    return game is not None


@event_node_builder_bp.route("/api/preview-hql", methods=["POST"])
def preview_hql():
    """
    API: 预览 HQL

    转发到现有的 HQL 生成逻辑
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Request body is required", status_code=400)

        game_gid = data.get("game_gid")
        event_id = data.get("event_id")
        fields = data.get("fields", [])
        filter_conditions = data.get("filter_conditions", {})
        sql_mode = data.get("sql_mode", "view")

        if not game_gid or not event_id:
            logger.error(
                f"Missing required params: game_gid={game_gid}, event_id={event_id}"
            )
            return json_error_response(
                "game_gid and event_id are required", status_code=400
            )

        # 添加详细日志用于调试
        logger.info(f"Generating HQL for game_gid={game_gid}, event_id={event_id}")
        logger.info(
            f"Fields count: {len(fields)}, Filter conditions: {filter_conditions}"
        )

        # 导入 HQL V2 生成器
        from backend.services.hql.core.generator import HQLGenerator
        from backend.services.hql.adapters.project_adapter import ProjectAdapter

        # 创建 HQL 生成器
        generator = HQLGenerator()
        adapter = ProjectAdapter()

        # 使用 ProjectAdapter 创建 Event 对象
        try:
            event_obj = adapter.event_from_project(game_gid, event_id)
        except ValueError as e:
            return json_error_response(str(e), status_code=404)

        events_data = [event_obj]

        # 转换字段格式（使用 adapter）
        fields_v2 = []
        for idx, field in enumerate(fields):
            try:
                logger.debug(f"Processing field {idx}: {field}")
                field_obj = adapter.field_from_project(field)
                fields_v2.append(field_obj)
            except ValueError as e:
                logger.error(f"Invalid field at index {idx}: {field}, error: {str(e)}")
                return json_error_response(
                    f"Invalid field at index {idx}: {str(e)}", status_code=400
                )

        # 转换 WHERE 条件格式（使用 adapter）
        where_conditions_v2 = []
        if filter_conditions:
            conditions = filter_conditions.get("conditions", [])
            for cond in conditions:
                try:
                    condition_obj = adapter.condition_from_project(cond)
                    where_conditions_v2.append(condition_obj)
                except (KeyError, ValueError) as e:
                    return json_error_response(
                        f"Invalid condition: {str(e)}", status_code=400
                    )

        # 生成 HQL
        hql_result = generator.generate(
            events_data,  # 位置参数1: events
            fields_v2,  # 位置参数2: fields
            where_conditions_v2,  # 位置参数3: conditions
            mode="single",  # 关键字参数
            sql_mode=sql_mode.upper(),
            include_comments=True,
        )

        return json_success_response(data=hql_result, message="HQL preview generated")

    except Exception as e:
        logger.error(f"Error generating HQL preview: {e}", exc_info=True)
        return json_error_response(
            f"Failed to generate HQL preview: {str(e)}", status_code=500
        )


@event_node_builder_bp.route("/api/params", methods=["GET"])
def get_event_params():
    """
    API: 获取事件的参数列表

    转发到现有的 /api/events/<id>/params 路由
    """
    try:
        event_id = request.args.get("event_id", type=int)

        if not event_id:
            return json_error_response("event_id is required", status_code=400)

        # 查询事件的参数
        params = fetch_all_as_dict(
            """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                ep.param_description,
                ep.hql_config,
                ep.json_path,
                ep.is_active
            FROM event_params ep
            WHERE ep.event_id = ? AND ep.is_active = 1
            ORDER BY ep.id
        """,
            (event_id,),
        )

        return json_success_response(data=params, message="Event parameters retrieved")

    except Exception as e:
        logger.error(f"Error fetching event params: {e}")
        return json_error_response(
            f"Failed to fetch event params: {str(e)}", status_code=500
        )


@event_node_builder_bp.route("/api/save", methods=["POST"])
def save_config():
    """
    API: 保存事件节点配置

    转发到现有的 /api/event-nodes 路由（POST）
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Request body is required", status_code=400)

        # 导入 event_nodes 模块的创建逻辑
        from backend.services.events.event_nodes import create_event_node

        # 模拟 request 对象，因为 create_event_node 从 request.get_json() 读取数据
        # 我们需要将当前请求数据注入到 Flask 的 request context 中
        # 更简单的方法是直接调用 create_event_node 的逻辑

        # 验证必填字段
        game_gid = data.get("game_gid")
        name = data.get("name")
        event_id = data.get("event_id")
        config = data.get("config")

        if not all([game_gid, name, event_id, config is not None]):
            return json_error_response(
                "game_gid, name, event_id, and config are required", status_code=400
            )

        # 导入必要的函数
        from backend.core.utils import execute_write
        import json

        # 验证游戏存在并获取 game_id
        game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
        if not game:
            return json_error_response("Game not found", status_code=404)
        game_id = game["id"]

        # 验证事件存在
        event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))
        if not event:
            return json_error_response("Event not found", status_code=404)

        # 检查是否已存在同名配置
        existing = fetch_one_as_dict(
            "SELECT * FROM event_nodes WHERE game_id = ? AND name = ?", (game_id, name)
        )
        if existing:
            return json_error_response(
                "Event node with this name already exists", status_code=400
            )

        # 创建事件节点
        config_json = json.dumps(config, ensure_ascii=False)
        node_id = execute_write(
            """
            INSERT INTO event_nodes (game_id, name, event_id, config_json)
            VALUES (?, ?, ?, ?)
        """,
            (game_id, name, event_id, config_json),
        )

        # 返回新创建的节点
        node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (node_id,))

        return json_success_response(
            data={"node": node}, message="Event node created", status_code=201
        )

    except Exception as e:
        logger.error(f"Error saving config: {e}", exc_info=True)
        return json_error_response(f"Failed to save config: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/update", methods=["POST"])
def update_config():
    """
    API: 更新事件节点配置

    转发到现有的 /api/event-nodes/<id> 路由（PUT）
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Request body is required", status_code=400)

        node_id = data.get("node_id")

        if not node_id:
            return json_error_response("node_id is required", status_code=400)

        # 获取现有节点
        node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (node_id,))
        if not node:
            return json_error_response("Event node not found", status_code=404)

        # 导入必要的函数
        from backend.core.utils import execute_write
        import json

        # 更新字段
        update_fields = []
        update_values = []

        if "name" in data:
            update_fields.append("name = ?")
            update_values.append(data["name"])

        if "event_id" in data:
            update_fields.append("event_id = ?")
            update_values.append(data["event_id"])

        if "config" in data:
            config_json = json.dumps(data["config"], ensure_ascii=False)
            update_fields.append("config_json = ?")
            update_values.append(config_json)

        if "is_active" in data:
            update_fields.append("is_active = ?")
            update_values.append(data["is_active"])

        if update_fields:
            update_values.append(node_id)
            execute_write(
                f"""
                UPDATE event_nodes
                SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                update_values,
            )

        # 返回更新后的节点
        updated_node = fetch_one_as_dict(
            "SELECT * FROM event_nodes WHERE id = ?", (node_id,)
        )

        return json_success_response(
            data={"node": updated_node}, message="Event node updated"
        )

    except Exception as e:
        logger.error(f"Error updating config: {e}", exc_info=True)
        return json_error_response(
            f"Failed to update config: {str(e)}", status_code=500
        )


@event_node_builder_bp.route("/api/load/<int:config_id>", methods=["GET"])
def load_config(config_id):
    """
    API: 加载事件节点配置
    """
    try:
        node = fetch_one_as_dict(
            """
            SELECT en.*, le.event_name, le.event_name_cn
            FROM event_nodes en
            LEFT JOIN log_events le ON en.event_id = le.id
            WHERE en.id = ?
        """,
            (config_id,),
        )

        if not node:
            return json_error_response("Event node not found", status_code=404)

        # 解析 config_json
        import json

        try:
            node["config"] = json.loads(node["config_json"])
        except (json.JSONDecodeError, TypeError, ValueError):
            node["config"] = {}

        return json_success_response(data={"node": node}, message="Event node loaded")

    except Exception as e:
        logger.error(f"Error loading config: {e}", exc_info=True)
        return json_error_response(f"Failed to load config: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/list", methods=["GET"])
def list_configs():
    """
    API: 获取事件节点配置列表
    """
    try:
        game_gid = request.args.get("game_gid", type=str)
        if not game_gid:
            return json_error_response("game_gid is required", status_code=400)

        # 转换 game_gid 为 game_id
        game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
        if not game:
            return json_error_response("Game not found", status_code=404)
        game_id = game["id"]

        nodes = fetch_all_as_dict(
            """
            SELECT en.*, le.event_name, le.event_name_cn
            FROM event_nodes en
            LEFT JOIN log_events le ON en.event_id = le.id
            WHERE en.game_id = ? AND en.is_active = 1
            ORDER BY en.created_at DESC
        """,
            (game_id,),
        )

        # 解析 config_json
        import json

        for node in nodes:
            try:
                node["config"] = json.loads(node["config_json"])
            except (json.JSONDecodeError, TypeError, ValueError):
                node["config"] = {}

        return json_success_response(data=nodes, message="Event nodes retrieved")

    except Exception as e:
        logger.error(f"Error fetching config list: {e}", exc_info=True)
        return json_error_response(
            f"Failed to fetch config list: {str(e)}", status_code=500
        )


@event_node_builder_bp.route("/api/delete/<int:config_id>", methods=["DELETE"])
def delete_config(config_id):
    """
    API: 删除事件节点配置
    """
    try:
        from backend.core.utils import execute_write

        node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (config_id,))
        if not node:
            return json_error_response("Event node not found", status_code=404)

        # 软删除
        execute_write("UPDATE event_nodes SET is_active = 0 WHERE id = ?", (config_id,))

        return json_success_response(message="Event node deleted")

    except Exception as e:
        logger.error(f"Error deleting config: {e}", exc_info=True)
        return json_error_response(
            f"Failed to delete config: {str(e)}", status_code=500
        )


@event_node_builder_bp.route("/api/copy/<int:node_id>", methods=["POST"])
def copy_node(node_id):
    """
    API: 复制事件节点
    """
    try:
        from backend.core.utils import execute_write
        import json

        # 获取原节点
        node = fetch_one_as_dict("SELECT * FROM event_nodes WHERE id = ?", (node_id,))

        if not node:
            return json_error_response("Event node not found", status_code=404)

        # 复制节点（修改名称）
        original_name = node["name"]
        new_name = f"{original_name} (Copy)"

        # 创建新节点
        new_node_id = execute_write(
            """
            INSERT INTO event_nodes (game_id, name, event_id, config_json)
            VALUES (?, ?, ?, ?)
        """,
            (node["game_id"], new_name, node["event_id"], node["config_json"]),
        )

        # 返回新节点
        new_node = fetch_one_as_dict(
            "SELECT * FROM event_nodes WHERE id = ?", (new_node_id,)
        )

        return json_success_response(
            data={"node": new_node}, message="Event node copied", status_code=201
        )

    except Exception as e:
        logger.error(f"Error copying node: {e}", exc_info=True)
        return json_error_response(f"Failed to copy node: {str(e)}", status_code=500)


# ============================================
# Event Nodes Search & Stats Endpoints
# Added 2026-02-15 to support EventNodes.tsx frontend
# ============================================


@event_node_builder_bp.route("/api/search", methods=["GET"])
def search_event_nodes():
    """
    Search event nodes with filters

    Query Parameters:
        game_gid (int, required): Game GID
        keyword (str, optional): Search keyword for event name
        today_modified (bool, optional): Filter by today's modifications
        event_id (int, optional): Filter by specific event ID
        field_count_min (int, optional): Minimum field count
        field_count_max (int, optional): Maximum field count
    """
    try:
        # Validate game exists
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return json_error_response(
                "game_gid parameter is required", status_code=400
            )

        if not validate_game_exists(game_gid):
            return json_error_response("Game not found", status_code=404)

        # Get filters
        keyword = request.args.get("keyword", "")
        event_id = request.args.get("event_id", type=int)
        field_count_min = request.args.get("field_count_min", type=int)
        field_count_max = request.args.get("field_count_max", type=int)
        today_modified = request.args.get("today_modified", type=bool)

        # Build query
        query = """SELECT
                en.*,
                e.name as event_name,
                COUNT(DISTINCT ep.id) as field_count
            FROM event_nodes en
            INNER JOIN log_events e ON en.event_id = e.id
            LEFT JOIN event_params ep ON en.id = ep.event_node_id
            WHERE e.game_gid = ?
            GROUP BY en.id
        """
        params = [game_gid]

        # Apply filters
        if keyword:
            query += " AND e.name LIKE ?"
            params.append(f"%{keyword}%")

        if event_id:
            query += " AND en.event_id = ?"
            params.append(event_id)

        if field_count_min is not None:
            query += " HAVING COUNT(DISTINCT ep.id) >= ?"
            params.append(field_count_min)

        if field_count_max is not None:
            query += " HAVING COUNT(DISTINCT ep.id) <= ?"
            params.append(field_count_max)

        limit = request.args.get("limit", 100, type=int)
        limit = min(max(limit, 1), 100)
        offset = request.args.get("offset", 0, type=int)
        offset = max(offset, 0)

        query += f" ORDER BY en.updated_at DESC LIMIT {limit} OFFSET {offset}"

        nodes = fetch_all_as_dict(query, tuple(params))

        # 包装成符合 EventNodesListResponse 的格式
        return json_success_response(
            data={
                "nodes": nodes,
                "total": len(nodes),
                "page": 1,
                "per_page": 100,
                "total_pages": 1,
            },
            message="Event nodes retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error searching event nodes: {e}")
        return json_error_response("Failed to search event nodes", status_code=500)


@event_node_builder_bp.route("/api/stats", methods=["GET"])
def get_event_nodes_stats():
    """
    Get event nodes statistics for a game

    Query Parameters:
        game_gid (int, required): Game GID
    """
    try:
        logger.info(
            f"get_event_nodes_stats called with game_gid={request.args.get('game_gid')}"
        )
        # Validate game exists
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return json_error_response(
                "game_gid parameter is required", status_code=400
            )

        if not validate_game_exists(game_gid):
            return json_error_response("Game not found", status_code=404)

        # Get statistics
        query = """SELECT
                COUNT(DISTINCT en.id) as total_nodes,
                COUNT(DISTINCT en.event_id) as unique_events,
                COUNT(DISTINCT ep.id) as total_fields
            FROM event_nodes en
            INNER JOIN log_events e ON en.event_id = e.id
            LEFT JOIN event_params ep ON en.id = ep.event_node_id
            WHERE e.game_gid = ?
        """

        stats = fetch_one_as_dict(query, (game_gid,))

        if not stats:
            # Return zero stats if no nodes found
            stats = {"total_nodes": 0, "unique_events": 0, "total_fields": 0}

        # 计算平均字段数（avg_fields）
        total_nodes = stats.get("total_nodes", 0)
        total_fields = stats.get("total_fields", 0)
        avg_fields = round(total_fields / total_nodes, 2) if total_nodes > 0 else 0

        return json_success_response(
            data={
                "total_nodes": stats["total_nodes"],
                "unique_events": stats["unique_events"],
                "avg_fields": avg_fields,
            },
            message="Event nodes statistics retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error getting event nodes stats: {e}")
        return json_error_response(
            "Failed to get event nodes statistics", status_code=500
        )
