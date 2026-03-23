#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Node Builder Routes
事件节点构建器路由 - 提供前端 EventNodeBuilder 页面需要的 API 路由

ERS架构迁移 (Phase 3 - Task A6):
- 使用EventNodeService替代直接数据库访问
- 使用GameService进行游戏验证
- 保持API兼容性的同时提升架构合规性
"""

from flask import Blueprint, request

from backend.core.cache.decorators import cached, invalidate_cache
from backend.core.logging import get_logger
from backend.core.utils import json_error_response, json_success_response

# ERS架构 - 使用Service层
from backend.services.events.event_node_service import EventNodeService
from backend.services.games.game_service import GameService

logger = get_logger(__name__)

event_node_builder_bp = Blueprint("event_node_builder", __name__, url_prefix="/event_node_builder")

# 初始化Service实例 (全局单例模式)
event_node_service = EventNodeService()
game_service = GameService()


def validate_game_exists(game_gid: int) -> bool:
    """
    验证游戏是否存在 (ERS架构)

    迁移后使用GameService替代直接数据库访问
    """
    game = game_service.get_game_by_gid(game_gid)
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
            logger.error(f"Missing required params: game_gid={game_gid}, event_id={event_id}")
            return json_error_response("game_gid and event_id are required", status_code=400)

        # 添加详细日志用于调试
        logger.info(f"Generating HQL for game_gid={game_gid}, event_id={event_id}")
        logger.info(f"Fields count: {len(fields)}, Filter conditions: {filter_conditions}")

        # 导入 HQL V2 生成器
        from backend.services.hql.adapters.project_adapter import ProjectAdapter
        from backend.services.hql.core.generator import HQLGenerator

        # 创建 HQL 生成器
        generator = HQLGenerator()
        adapter = ProjectAdapter()

        # 使用 ProjectAdapter 创建 Event 对象
        try:
            event_obj = adapter.event_from_project(game_gid, event_id)
        except ValueError as e:
            return json_error_response(str(e), status_code=404)

        events_data = [event_obj]

        # 转换字段格式(使用 adapter)
        fields = []
        for idx, field in enumerate(fields):
            try:
                logger.debug(f"Processing field {idx}: {field}")
                field_obj = adapter.field_from_project(field)
                fields.append(field_obj)
            except ValueError as e:
                logger.error(f"Invalid field at index {idx}: {field}, error: {str(e)}")
                return json_error_response(
                    f"Invalid field at index {idx}: {str(e)}", status_code=400
                )

        # 转换 WHERE 条件格式(使用 adapter)
        where_conditions = []
        if filter_conditions:
            conditions = filter_conditions.get("conditions", [])
            for cond in conditions:
                try:
                    condition_obj = adapter.condition_from_project(cond)
                    where_conditions.append(condition_obj)
                except (KeyError, ValueError) as e:
                    return json_error_response(f"Invalid condition: {str(e)}", status_code=400)

        # 生成 HQL
        hql_result = generator.generate(
            events_data,  # 位置参数1: events
            fields,  # 位置参数2: fields
            where_conditions,  # 位置参数3: conditions
            mode="single",  # 关键字参数
            sql_mode=sql_mode.upper(),
            include_comments=True,
        )

        return json_success_response(data=hql_result, message="HQL preview generated")

    except Exception as e:
        logger.error(f"Error generating HQL preview: {e}", exc_info=True)
        return json_error_response(f"Failed to generate HQL preview: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/params", methods=["GET"])
def get_event_params():
    """
    API: 获取事件的参数列表 (ERS架构)

    迁移后使用EventService替代直接数据库访问
    注意: 不使用缓存装饰器，因为event_id是动态参数，会导致不同事件的缓存冲突
    """
    try:
        event_id = request.args.get("event_id", type=int)

        if not event_id:
            return json_error_response("event_id is required", status_code=400)

        # 使用EventService获取事件的参数
        from backend.services.events.event_service import EventService

        event_service = EventService()
        params = event_service.get_event_parameters(event_id)

        logger.info(f"EventService返回 {len(params)} 个参数，event_id={event_id}")
        if params:
            logger.info(f"第一个参数: {params[0]}")

        # 转换为适合前端的格式(仅包含需要的字段)
        # 注意: EventService返回的字段名为 description, param_type 等
        params_data = [
            {
                "id": p.get("id"),
                "param_name": p.get("param_name"),
                "param_name_cn": p.get("param_name_cn"),
                "param_description": p.get("description"),  # EventService返回的是description字段
                "param_type": p.get("param_type"),  # param_type从template_name获取
                "is_active": p.get("is_active"),
                # hql_config和json_path字段不在SQL查询中, 如果需要需要添加到查询中
                "hql_config": None,
                "json_path": None,
            }
            for p in params
        ]

        logger.info(f"转换后的params_data包含 {len(params_data)} 个参数")
        return json_success_response(data=params_data, message="Event parameters retrieved")

    except Exception as e:
        logger.error(f"Error fetching event params: {e}")
        return json_error_response(f"Failed to fetch event params: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/save", methods=["POST"])
@invalidate_cache("event_nodes:stats:*")  # Explicitly invalidate stats cache when node is created
def save_config():
    """
    API: 保存事件节点配置 (ERS架构)

    迁移后使用EventNodeService替代直接数据库访问
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Request body is required", status_code=400)

        # 验证必填字段
        game_gid = data.get("game_gid")
        name = data.get("name")
        event_id = data.get("event_id")
        config = data.get("config")

        if not all([game_gid, name, event_id, config is not None]):
            return json_error_response(
                "game_gid, name, event_id, and config are required", status_code=400
            )

        # ✅ 新增: 请求入口日志
        logger.info(
            f"[SAVE_CONFIG] Request received: game_gid={game_gid}, "
            f"name='{name}', event_id={event_id}, "
            f"config_keys={list(config.keys()) if config else 0}"
        )

        # 导入Entity模型
        import json

        from backend.models.entities import EventNodeEntity

        # 使用EventNodeService创建节点
        try:
            node_entity = EventNodeEntity(
                game_gid=game_gid,
                name=name,
                event_id=event_id,
                config_json=json.dumps(config, ensure_ascii=False),
                is_active=True,
            )

            # ✅ 新增: 创建节点前的日志
            logger.debug(
                f"[SAVE_CONFIG] Creating node entity: "
                f"game_gid={node_entity.game_gid}, name='{node_entity.name}', "
                f"event_id={node_entity.event_id}"
            )

            created_node = event_node_service.create_node(node_entity)

            # ✅ 新增: 创建成功日志
            logger.info(
                f"[SAVE_CONFIG] Node created successfully: "
                f"node_id={created_node.id}, game_gid={game_gid}, name='{name}'"
            )

            # ✅ 新增: 验证数据库写入
            # ✅ BUGFIX #6: 使用get_node_with_details而不是find_by_id
            verification = event_node_service.get_node_with_details(created_node.id)
            if not verification:
                logger.error(
                    f"[SAVE_CONFIG] CRITICAL: Node {created_node.id} not found in DB after creation!"
                )
                return json_error_response("Node creation verification failed", status_code=500)

            logger.debug(
                f"[SAVE_CONFIG] Verification passed: node_id={created_node.id} exists in DB"
            )

            # 获取带详情的节点数据
            node_with_details = event_node_service.get_node_with_details(created_node.id)

            # ✅ 新增: 返回前的日志
            logger.debug(
                f"[SAVE_CONFIG] Returning node details: node_id={created_node.id}, "
                f"details_keys={list(node_with_details.keys()) if node_with_details else 0}"
            )

            return json_success_response(
                data={"node": node_with_details}, message="Event node created", status_code=201
            )

        except ValueError as e:
            # Service层的验证错误 (游戏不存在, 事件不存在, 名称重复等)
            # ✅ 新增: 更详细的错误日志
            logger.error(
                f"[SAVE_CONFIG] Validation error: game_gid={game_gid}, name='{name}', "
                f"error={str(e)}"
            )
            return json_error_response(
                str(e), status_code=404 if "not found" in str(e).lower() else 400
            )

    except Exception as e:
        # ✅ 新增: 更详细的异常日志
        logger.error(f"[SAVE_CONFIG] Unexpected error: {str(e)}", exc_info=True)
        return json_error_response(f"Failed to save config: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/update", methods=["POST"])
@invalidate_cache("event_nodes:stats:*")  # Explicitly invalidate stats cache when node is updated
def update_config():
    """
    API: 更新事件节点配置 (ERS架构)

    迁移后使用EventNodeService替代直接数据库访问
    """
    try:
        data = request.get_json()

        if not data:
            return json_error_response("Request body is required", status_code=400)

        node_id = data.get("node_id")

        if not node_id:
            return json_error_response("node_id is required", status_code=400)

        # 导入Entity模型
        import json

        from backend.models.entities import EventNodeEntity

        # 准备更新数据
        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]
        if "event_id" in data:
            update_data["event_id"] = data["event_id"]
        if "config" in data:
            update_data["config_json"] = json.dumps(data["config"], ensure_ascii=False)
        if "is_active" in data:
            update_data["is_active"] = data["is_active"]

        # 使用EventNodeService更新节点
        try:
            updated_node = event_node_service.update_node(node_id, update_data)

            # 获取带详情的节点数据
            node_with_details = event_node_service.get_node_with_details(node_id)

            return json_success_response(
                data={"node": node_with_details}, message="Event node updated"
            )

        except ValueError as e:
            return json_error_response(
                str(e), status_code=404 if "not found" in str(e).lower() else 400
            )

    except Exception as e:
        logger.error(f"Error updating config: {e}", exc_info=True)
        return json_error_response(f"Failed to update config: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/load/<int:config_id>", methods=["GET"])
def load_config(config_id):
    """
    API: 加载事件节点配置 (ERS架构)

    迁移后使用EventNodeService替代直接数据库访问
    """
    try:
        # 使用EventNodeService获取节点
        try:
            node_with_details = event_node_service.get_node_with_details(config_id)
        except ValueError as e:
            return json_error_response(str(e), status_code=404)

        # 解析 config_json
        import json

        try:
            node_with_details["config"] = json.loads(node_with_details["config_json"])
        except (json.JSONDecodeError, TypeError, ValueError):
            node_with_details["config"] = {}

        return json_success_response(data={"node": node_with_details}, message="Event node loaded")

    except Exception as e:
        logger.error(f"Error loading config: {e}", exc_info=True)
        return json_error_response(f"Failed to load config: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/list", methods=["GET"])
def list_configs():
    """
    API: 获取事件节点配置列表 (ERS架构)

    迁移后使用EventNodeService + GameService替代直接数据库访问
    """
    try:
        game_gid = request.args.get("game_gid", type=str)
        if not game_gid:
            return json_error_response("game_gid is required", status_code=400)

        # 验证游戏存在(使用GameService)
        game = game_service.get_game_by_gid(int(game_gid))
        if not game:
            return json_error_response("Game not found", status_code=404)

        # 使用EventNodeService获取节点列表
        nodes = event_node_service.get_nodes_by_game_gid(int(game_gid))

        # 转换为带详情的格式
        nodes_with_details = []
        import json

        for node in nodes:
            node_dict = node.model_dump()
            node_dict["event_name"] = node.event_name if hasattr(node, "event_name") else None
            node_dict["event_name_cn"] = (
                node.event_name_cn if hasattr(node, "event_name_cn") else None
            )

            # 解析 config_json
            try:
                node_dict["config"] = json.loads(node.config_json)
            except (json.JSONDecodeError, TypeError, ValueError):
                node_dict["config"] = {}

            nodes_with_details.append(node_dict)

        return json_success_response(data=nodes_with_details, message="Event nodes retrieved")

    except Exception as e:
        logger.error(f"Error fetching config list: {e}", exc_info=True)
        return json_error_response(f"Failed to fetch config list: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/delete/<int:config_id>", methods=["DELETE"])
@invalidate_cache("event_nodes:stats:*")  # Explicitly invalidate stats cache when node is deleted
def delete_config(config_id):
    """
    API: 删除事件节点配置 (ERS架构)

    迁移后使用EventNodeService替代直接数据库访问
    """
    try:
        # 使用EventNodeService软删除节点
        try:
            event_node_service.soft_delete_node(config_id)
        except ValueError as e:
            return json_error_response(str(e), status_code=404)

        return json_success_response(message="Event node deleted")

    except Exception as e:
        logger.error(f"Error deleting config: {e}", exc_info=True)
        return json_error_response(f"Failed to delete config: {str(e)}", status_code=500)


@event_node_builder_bp.route("/api/copy/<int:node_id>", methods=["POST"])
@invalidate_cache("event_nodes:stats:*")  # Explicitly invalidate stats cache when node is copied
def copy_node(node_id):
    """
    API: 复制事件节点 (ERS架构)

    迁移后使用EventNodeService替代直接数据库访问
    """
    try:
        # 使用EventNodeService复制节点
        try:
            new_node = event_node_service.copy_node(node_id)
        except ValueError as e:
            return json_error_response(str(e), status_code=404)

        # 获取带详情的节点数据
        node_with_details = event_node_service.get_node_with_details(new_node.id)

        return json_success_response(
            data={"node": node_with_details}, message="Event node copied", status_code=201
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
    Search event nodes with filters (ERS架构)

    迁移后使用EventNodeService + GameService替代直接数据库访问

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
            return json_error_response("game_gid parameter is required", status_code=400)

        if not validate_game_exists(game_gid):
            return json_error_response("Game not found", status_code=404)

        # Get filters
        keyword = request.args.get("keyword", "")
        event_id = request.args.get("event_id", type=int)
        field_count_min = request.args.get("field_count_min", type=int)
        field_count_max = request.args.get("field_count_max", type=int)
        limit = request.args.get("limit", 100, type=int)
        limit = min(max(limit, 1), 100)
        offset = request.args.get("offset", 0, type=int)
        offset = max(offset, 0)

        # 使用EventNodeService搜索节点
        try:
            nodes = event_node_service.search_nodes(
                game_gid=game_gid,
                keyword=keyword,
                event_id=event_id,
                field_count_min=field_count_min,
                field_count_max=field_count_max,
                limit=limit,
                offset=offset,
            )
        except ValueError as e:
            return json_error_response(str(e), status_code=400)

        # 转换为字典格式
        nodes_data = [node.model_dump() for node in nodes]

        # 包装成符合 EventNodesListResponse 的格式
        return json_success_response(
            data={
                "nodes": nodes_data,
                "total": len(nodes_data),
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
@cached(ttl=300, key_prefix="event_nodes:stats")  # Cache for 5 minutes (reduced from 30 min)
def get_event_nodes_stats():
    """
    Get event nodes statistics for a game (ERS架构)

    迁移后使用EventNodeService + GameService替代直接数据库访问

    Query Parameters:
        game_gid (int, required): Game GID
    """
    try:
        logger.info(f"get_event_nodes_stats called with game_gid={request.args.get('game_gid')}")
        # Validate game exists
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return json_error_response("game_gid parameter is required", status_code=400)

        if not validate_game_exists(game_gid):
            return json_error_response("Game not found", status_code=404)

        # 使用EventNodeService获取统计信息
        try:
            stats = event_node_service.get_nodes_stats(game_gid)
        except ValueError as e:
            return json_error_response(str(e), status_code=404)

        return json_success_response(
            data={
                "total_nodes": stats["total_nodes"],
                "unique_events": stats["unique_events"],
                "avg_fields": stats["avg_fields"],
            },
            message="Event nodes statistics retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error getting event nodes stats: {e}")
        return json_error_response("Failed to get event nodes statistics", status_code=500)
