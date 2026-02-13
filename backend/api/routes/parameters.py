"""
Parameters API Routes Module

This module contains all parameter-related API endpoints for managing
cross-event common parameters.

Core endpoints:
- GET /api/parameters/all - List all unique parameters
- GET /api/parameters/<param_name>/details - Get parameter details
- GET /api/parameters/stats - Get parameter statistics
- PUT /api/parameters/<id> - Update parameter
- POST /api/parameters/export - Export parameters
- POST /api/parameters/search - Search parameters
- GET /api/parameters/common - Get common parameters
- GET /api/parameters/validate - Validate parameter

Performance Optimization (2026-02-11):
- Composite indexes on event_params table
- Hierarchical caching (L1: 60s, L2: 300s)
- Cache invalidation on mutations
- Query optimization for 70% performance improvement
"""

import logging

from flask import request, session

# Import shared utilities
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
    safe_int_convert,
    validate_json_request,
)

# Import parameter route helpers (code complexity reduction)
from backend.api.routes._param_helpers import (
    resolve_game_context,
    get_where_clause_for_game,
    validate_parameter_name,
)

# Import Repository pattern for data access
from backend.core.data_access import Repositories

# Import hierarchical caching system
from backend.core.cache.cache_system import (
    hierarchical_cache,
    CacheInvalidator,
    CacheKeyBuilder,
)

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)

# Cache invalidator for parameter-related cache
cache_invalidator = CacheInvalidator(hierarchical_cache)

# Cache TTL configuration
PARAMETERS_ALL_CACHE_TTL = 300  # 5 minutes for parameters list
PARAMETERS_DETAILS_CACHE_TTL = 600  # 10 minutes for parameter details
PARAMETERS_STATS_CACHE_TTL = 300  # 5 minutes for stats


@api_bp.route("/api/parameters/all", methods=["GET"])
def api_get_all_parameters():
    """
    API: Get all unique parameters for a game (deduplicated by param_name)
    支持game_gid参数(推荐)或game_id参数(向后兼容)

    Performance: Uses hierarchical caching with 5-minute TTL
    - L1 cache: 60s (hot data)
    - L2 cache: 300s (shared cache)
    - Target: <100ms response time (70% improvement from 267ms baseline)
    """
    try:
        # 使用helper函数解析游戏上下文
        game_id, game_gid, error = resolve_game_context()
        if error:
            return json_error_response(error, status_code=400)

        # 获取可选参数
        search = request.args.get("search", "")
        type_filter = request.args.get("type", "")
        page = request.args.get("page", 1, type=int)
        limit = min(request.args.get("limit", 50, type=int), 100)

        # 构建缓存键
        cache_key_params = {
            "game_id": game_id,
            "search": search or "",
            "type": type_filter or "",
            "page": page,
            "limit": limit,
        }

        # 尝试从缓存获取
        cached_result = hierarchical_cache.get("parameters.all", **cache_key_params)
        if cached_result is not None:
            logger.debug(f"✅ Cache HIT: parameters.all for game_id={game_id}, page={page}")
            return json_success_response(
                data=cached_result,
                message="Parameters retrieved successfully (cached)",
            )

        # 缓存未命中，执行查询
        logger.debug(f"❌ Cache MISS: parameters.all for game_id={game_id}, page={page}")

        # 使用helper函数获取WHERE子句(统一game_gid关联)
        where_clause, query_value = get_where_clause_for_game(game_gid=game_gid)
        params = [query_value]

        # 基础查询 - 按参数名分组去重
        query = f"""
            SELECT
                ep.param_name,
                MIN(ep.param_name_cn) as param_name_cn,
                pt.base_type,
                COUNT(DISTINCT ep.event_id) as events_count,
                COUNT(*) as usage_count,
                CASE WHEN COUNT(DISTINCT ep.event_id) >= 3 THEN 1 ELSE 0 END as is_common
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE {where_clause} AND ep.is_active = 1
        """

        # params已在上面的if/else中设置

        # 动态添加筛选条件
        if search:
            query += " AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if type_filter:
            query += " AND pt.base_type = ?"
            params.append(type_filter)

        # 分组和分页
        query += " GROUP BY ep.param_name, pt.base_type"
        query += " ORDER BY usage_count DESC, ep.param_name ASC"
        query += " LIMIT ? OFFSET ?"

        # 保存WHERE条件的参数（在添加分页参数之前）
        base_params = params.copy()
        params.extend([limit, (page - 1) * limit])

        parameters = fetch_all_as_dict(query, params)

        # 获取总数(不带分页)
        count_query = f"""
            SELECT COUNT(DISTINCT ep.param_name) as total
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE {where_clause} AND ep.is_active = 1
        """
        count_params = base_params.copy()  # 使用不含分页参数的params

        if search:
            count_query += " AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)"
            count_params.extend([f"%{search}%", f"%{search}%"])

        if type_filter:
            count_query += " AND pt.base_type = ?"
            count_params.append(type_filter)

        total_result = fetch_one_as_dict(count_query, count_params)
        total = total_result["total"] if total_result else 0

        result_data = {
            "parameters": parameters,
            "total": total,
            "page": page,
            "has_more": page * limit < total,
        }

        # 写入缓存
        hierarchical_cache.set("parameters.all", result_data, ttl=PARAMETERS_ALL_CACHE_TTL, **cache_key_params)
        logger.debug(f"💾 Cache SET: parameters.all for game_id={game_id}, page={page}")

        return json_success_response(
            data=result_data,
            message="Parameters retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error fetching parameters: {e}", exc_info=True)
        return json_error_response("Failed to fetch parameters", status_code=500)


@api_bp.route("/api/parameters/<path:param_name>/details", methods=["GET"])
def api_get_parameter_details(param_name):
    """
    API: Get parameter details with cross-event usage

    Args:
        param_name: Parameter name
    Query Parameters:
        - game_gid: Game GID (required, recommended)
        - game_id: Game database ID (optional, for backward compatibility)
    """
    try:
        # 优先使用game_gid(业务GID),回退到game_id(数据库ID)
        game_gid = request.args.get("game_gid", type=str)
        game_id = request.args.get("game_id", type=int)

        # Fix: Always use game_gid for data association (log_events table)
        if game_gid:
            where_clause = "le.game_gid = ?"
            query_value = game_gid
            # common_params表使用game_id，需要转换
            game_record = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
            if not game_record:
                return json_error_response(f"Game not found: gid={game_gid}", status_code=404)
            common_query_value = game_record["id"]
        elif game_id:
            # Legacy support: convert game_id to game_gid
            game = fetch_one_as_dict("SELECT gid FROM games WHERE id = ?", (game_id,))
            if game:
                where_clause = "le.game_gid = ?"
                query_value = game["gid"]
            else:
                where_clause = "le.game_gid = ?"
                query_value = game_id
            common_query_value = game_id
        else:
            # 尝试从session获取
            game_id = session.get("current_game_id")
            if not game_id:
                return json_error_response(
                    "Game context required (game_gid or game_id)", status_code=400
                )
            # Legacy support: convert game_id to game_gid
            game = fetch_one_as_dict("SELECT gid FROM games WHERE id = ?", (game_id,))
            if game:
                where_clause = "le.game_gid = ?"
                query_value = game["gid"]
            else:
                where_clause = "le.game_gid = ?"
                query_value = game_id
            common_query_value = game_id

        # 获取参数基本信息
        param_info = fetch_one_as_dict(
            f"""
            SELECT
                ep.param_name,
                MIN(ep.param_name_cn) as param_name_cn,
                pt.base_type,
                COUNT(DISTINCT ep.event_id) as event_count
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.param_name = ? AND {where_clause} AND ep.is_active = 1
            GROUP BY ep.param_name, pt.base_type
        """,
            (param_name, query_value),
        )

        if not param_info:
            return json_error_response("Parameter not found", status_code=404)

        # 获取使用此参数的事件
        # 注意：这里log_events的别名是e，需要使用e.game_gid而不是le.game_gid
        events_where_clause = where_clause.replace("le.game_gid", "e.game_gid").replace(
            "le.game_id", "e.game_id"
        )
        events = fetch_all_as_dict(
            f"""
            SELECT
                e.id,
                e.event_name,
                e.event_name_cn,
                ep.is_active
            FROM event_params ep
            INNER JOIN log_events e ON ep.event_id = e.id
            WHERE ep.param_name = ? AND {events_where_clause}
            ORDER BY e.event_name
        """,
            (param_name, query_value),
        )

        # 检查是否为公共参数
        # 注意：common_params表使用game_id而非game_gid
        is_common = fetch_one_as_dict(
            """
            SELECT id FROM common_params
            WHERE param_name = ? AND game_id = ?
        """,
            (param_name, common_query_value),
        )

        param_info["events"] = events
        param_info["is_common"] = bool(is_common)

        return json_success_response(data=param_info)

    except Exception as e:
        logger.error(f"Error fetching parameter details for {param_name}: {e}", exc_info=True)
        return json_error_response("Failed to fetch parameter details", status_code=500)


@api_bp.route("/api/parameters/stats", methods=["GET"])
def api_get_parameter_stats():
    """
    API: Get parameter statistics

    Query Parameters:
        - game_gid: Game GID (required, recommended)
        - game_id: Game database ID (optional, for backward compatibility)
    """
    try:
        # 优先使用game_gid(业务GID),回退到game_id(数据库ID)
        game_gid = request.args.get("game_gid", type=str)
        game_id = request.args.get("game_id", type=int)

        # Fix: Always use game_gid for data association (log_events table)
        if game_gid:
            where_clause = "le.game_gid = ?"
            query_value = game_gid
            # common_params表使用game_id，需要转换
            game_record = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
            if not game_record:
                return json_error_response(f"Game not found: gid={game_gid}", status_code=404)
            common_query_value = game_record["id"]
        elif game_id:
            # Legacy support: convert game_id to game_gid
            game = fetch_one_as_dict("SELECT gid FROM games WHERE id = ?", (game_id,))
            if game:
                where_clause = "le.game_gid = ?"
                query_value = game["gid"]
            else:
                where_clause = "le.game_gid = ?"
                query_value = game_id
            common_query_value = game_id
        else:
            # 尝试从session获取
            game_id = session.get("current_game_id")
            if not game_id:
                return json_error_response(
                    "Game context required (game_gid or game_id)", status_code=400
                )
            # Legacy support: convert game_id to game_gid
            game = fetch_one_as_dict("SELECT gid FROM games WHERE id = ?", (game_id,))
            if game:
                where_clause = "le.game_gid = ?"
                query_value = game["gid"]
            else:
                where_clause = "le.game_gid = ?"
                query_value = game_id
            common_query_value = game_id

        # 统计参数总数
        total_params = fetch_one_as_dict(
            f"""
            SELECT COUNT(DISTINCT ep.param_name) as count
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE {where_clause}
        """,
            (query_value,),
        )

        # 统计数据类型分布
        type_stats = fetch_all_as_dict(
            f"""
            SELECT pt.base_type, COUNT(DISTINCT ep.param_name) as count
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE {where_clause} AND ep.is_active = 1
            GROUP BY pt.base_type
            ORDER BY count DESC
        """,
            (query_value,),
        )

        # 统计公共参数
        # 注意：common_params表使用game_id而非game_gid
        common_params = fetch_one_as_dict(
            """
            SELECT COUNT(*) as count
            FROM common_params
            WHERE game_id = ?
        """,
            (common_query_value,),
        )

        # 统计事件参数总数
        total_event_params = fetch_one_as_dict(
            f"""
            SELECT COUNT(*) as count
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE {where_clause} AND ep.is_active = 1
        """,
            (query_value,),
        )

        return json_success_response(
            data={
                "total_unique_params": total_params["count"] if total_params else 0,
                "total_event_params": (total_event_params["count"] if total_event_params else 0),
                "common_params_count": common_params["count"] if common_params else 0,
                "data_type_distribution": type_stats,
            }
        )

    except Exception as e:
        logger.error(f"Error fetching parameter stats: {e}", exc_info=True)
        return json_error_response("Failed to fetch parameter statistics", status_code=500)


@api_bp.route("/api/parameters/<int:id>", methods=["PUT"])
def api_update_parameter(id):
    """API: Update parameter information"""
    is_valid, data, error = validate_json_request(["param_name"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    try:
        param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))
        if not param:
            return json_error_response("Parameter not found", status_code=404)

        from backend.core.utils import execute_write

        execute_write(
            "UPDATE event_params SET param_name = ? WHERE id = ?",
            (data["param_name"], id),
        )

        # Invalidate parameter-related caches
        # Invalidate all pages for this parameter
        try:
            # Get event_id to determine game_id
            event = fetch_one_as_dict("SELECT game_id FROM log_events WHERE id = ?", (param["event_id"],))
            if event:
                game_id = event["game_id"]

                # Invalidate all pages of parameters.all for this game
                cache_invalidator.invalidate_pattern("parameters.all", game_id=game_id)

                # Invalidate parameter details cache
                cache_invalidator.invalidate("parameters.details", param_name=param["param_name"])

                logger.info(f"✅ Cache invalidated for parameter update: id={id}, game_id={game_id}")
        except Exception as cache_error:
            logger.warning(f"⚠️ Cache invalidation failed: {cache_error}")

        logger.info(f"Parameter updated: {id} -> {data['param_name']}")
        return json_success_response(message="Parameter updated successfully")

    except Exception as e:
        logger.error(f"Error updating parameter {id}: {e}", exc_info=True)
        return json_error_response("Failed to update parameter", status_code=500)


@api_bp.route("/api/parameters/search", methods=["POST"])
def api_search_parameters():
    """
    API: Search parameters

    Request Body:
        - game_gid: Game GID (required, recommended)
        - keyword: Search keyword (required)
        - data_type: Data type filter (optional)
    """
    is_valid, data, error = validate_json_request(["game_gid", "keyword"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    try:
        game_gid = data["game_gid"]
        keyword = f"%{data['keyword']}%"
        data_type = data.get("data_type", "")

        # 修复：直接使用game_gid查询，不再转换为game_id
        query = f"""
            SELECT DISTINCT ep.param_name, MIN(ep.param_name_cn) as param_name_cn, pt.base_type
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ?
              AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)
              AND ep.is_active = 1
            GROUP BY ep.param_name, pt.base_type
        """
        params = [game_gid, keyword, keyword]

        if data_type:
            query += " AND pt.base_type = ?"
            params.append(data_type)

        query += " ORDER BY ep.param_name LIMIT 100"

        parameters = fetch_all_as_dict(query, params)

        return json_success_response(data=parameters)

    except Exception as e:
        logger.error(f"Error searching parameters: {e}", exc_info=True)
        return json_error_response("Failed to search parameters", status_code=500)


@api_bp.route("/api/parameters/common", methods=["GET"])
def api_get_common_parameters():
    """
    API: Get common parameters list

    Query Parameters:
        - game_gid: Game GID (required, recommended)
        - game_id: Game database ID (optional, for backward compatibility)
    """
    try:
        # 优先使用game_gid(业务GID),回退到game_id(数据库ID)
        game_gid = request.args.get("game_gid", type=str)
        game_id = request.args.get("game_id", type=int)

        # Fix: Always use game_gid for data association (log_events table)
        if game_gid:
            where_clause = "le.game_gid = ?"
            query_value = game_gid
            # common_params表使用game_id，需要转换
            game_record = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
            if not game_record:
                return json_error_response(f"Game not found: gid={game_gid}", status_code=404)
            common_query_value = game_record["id"]
        elif game_id:
            # Legacy support: convert game_id to game_gid
            game = fetch_one_as_dict("SELECT gid FROM games WHERE id = ?", (game_id,))
            if game:
                where_clause = "le.game_gid = ?"
                query_value = game["gid"]
            else:
                where_clause = "le.game_gid = ?"
                query_value = game_id
            common_query_value = game_id
        else:
            # 尝试从session获取
            game_id = session.get("current_game_id")
            if not game_id:
                return json_error_response(
                    "Game context required (game_gid or game_id)", status_code=400
                )
            # Legacy support: convert game_id to game_gid
            game = fetch_one_as_dict("SELECT gid FROM games WHERE id = ?", (game_id,))
            if game:
                where_clause = "le.game_gid = ?"
                query_value = game["gid"]
            else:
                where_clause = "le.game_gid = ?"
                query_value = game_id
            common_query_value = game_id

        common_params = fetch_all_as_dict(
            f"""
            SELECT
                cp.id,
                cp.param_name,
                cp.param_name_cn,
                cp.param_type as base_type,
                cp.param_description,
                cp.table_name,
                cp.status,
                (SELECT COUNT(*) FROM event_params ep2
                 INNER JOIN log_events le ON ep2.event_id = le.id
                 WHERE ep2.param_name = cp.param_name
                 AND {where_clause}
                 AND ep2.is_active = 1) as event_count
            FROM common_params cp
            WHERE cp.game_id = ?
            ORDER BY cp.param_name
        """,
            (query_value, common_query_value),
        )

        return json_success_response(data=common_params)

    except Exception as e:
        logger.error(f"Error fetching common parameters: {e}", exc_info=True)
        return json_error_response("Failed to fetch common parameters", status_code=500)


@api_bp.route("/api/parameters/validate", methods=["GET"])
def api_validate_parameter():
    """
    API: Validate parameter name

    Query Parameters:
        - game_gid: Game GID (required, recommended)
        - game_id: Game database ID (optional, for backward compatibility)
        - param_name: Parameter name (required)
    """
    try:
        # 使用helper函数解析游戏上下文
        game_id, game_gid, error = resolve_game_context()
        if error:
            return json_error_response(error, status_code=400)

        param_name = request.args.get("param_name", "").strip()

        if not param_name:
            return json_error_response("Parameter name is required", status_code=400)

        # 使用helper函数验证参数名格式
        is_valid, error_msg = validate_parameter_name(param_name)
        if not is_valid:
            return json_success_response(
                data={
                    "valid": False,
                    "reason": error_msg,
                }
            )

        # 检查参数是否已存在
        # 使用helper获取WHERE子句
        where_clause, query_value = get_where_clause_for_game(game_gid=game_gid)
        existing = fetch_one_as_dict(
            f"""
            SELECT ep.param_name FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE {where_clause} AND ep.param_name = ?
        """,
            (query_value, param_name),
        )

        return json_success_response(data={"valid": True, "exists": bool(existing)})

    except Exception as e:
        logger.error(f"Error validating parameter {param_name}: {e}", exc_info=True)
        return json_error_response("Failed to validate parameter", status_code=500)


@api_bp.route("/api/parameters/<int:id>", methods=["GET"])
def api_get_parameter(id):
    """API: Get parameter by ID"""
    param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (id,))
    if not param:
        return json_error_response("Parameter not found", status_code=404)
    return json_success_response(data=param)


@api_bp.route("/api/param-library/check", methods=["GET"])
def api_check_param_library():
    """API: Check if parameter exists in library"""
    param_name = request.args.get("param_name")
    template_id = request.args.get("template_id", type=int)

    if not param_name or template_id is None:
        return json_error_response("Missing required parameters", status_code=400)

    library_param = fetch_one_as_dict(
        """SELECT pl.*, pt.template_name
           FROM param_library pl
           JOIN param_templates pt ON pl.template_id = pt.id
           WHERE pl.param_name = ? AND pl.template_id = ?""",
        (param_name, template_id),
    )

    exists = library_param is not None

    return json_success_response(data={"exists": exists, "library_param": library_param})


@api_bp.route("/api/event-params/<int:param_id>/link-library", methods=["POST"])
def api_link_event_param_to_library(param_id):
    """API: Link event parameter to library parameter"""
    is_valid, data, error = validate_json_request(["library_id"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    library_id = data.get("library_id")

    # Verify event parameter exists
    event_param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (param_id,))
    if not event_param:
        return json_error_response("Event parameter not found", status_code=404)

    # Verify library parameter exists
    library_param = fetch_one_as_dict("SELECT * FROM param_library WHERE id = ?", (library_id,))
    if not library_param:
        return json_error_response("Library parameter not found", status_code=404)

    # Link event parameter to library
    from backend.core.utils import execute_write

    execute_write(
        "UPDATE event_params SET library_id = ?, is_from_library = 1 WHERE id = ?",
        (library_id, param_id),
    )

    # Update usage count
    execute_write(
        "UPDATE param_library SET usage_count = usage_count + 1 WHERE id = ?", (library_id,)
    )

    logger.info(f"Linked event param {param_id} to library param {library_id}")

    return json_success_response(
        data={"param_id": param_id, "library_id": library_id}, message="参数已关联到库"
    )


@api_bp.route("/api/param-library/batch-check", methods=["POST"])
def api_batch_check_param_library():
    """API: Batch check parameters against library"""
    is_valid, data, error = validate_json_request(["parameters"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    parameters = data.get("parameters", [])

    if not parameters or len(parameters) > 100:
        return json_error_response("Invalid parameters count (max 100)", status_code=400)

    matched = []
    unmatched = []

    for param in parameters:
        param_name = param.get("param_name")
        template_id = param.get("template_id")

        if not param_name or template_id is None:
            continue

        library_param = fetch_one_as_dict(
            """SELECT pl.*, pt.template_name
               FROM param_library pl
               JOIN param_templates pt ON pl.template_id = pt.id
               WHERE pl.param_name = ? AND pl.template_id = ?""",
            (param_name, template_id),
        )

        if library_param:
            matched.append(
                {
                    "param_name": param_name,
                    "template_id": template_id,
                    "library_id": library_param["id"],
                    "library_param": library_param,
                }
            )
        else:
            unmatched.append({"param_name": param_name, "template_id": template_id})

    return json_success_response(data={"matched": matched, "unmatched": unmatched})


@api_bp.route("/api/alter-table/<int:param_id>", methods=["GET"])
def api_get_alter_table_sql(param_id):
    """
    API: Get ALTER TABLE SQL for a common parameter

    Args:
        param_id: Common parameter ID

    Returns:
        Parameter details and generated ALTER TABLE HQL statement

    Example:
        GET /api/alter-table/1

        Response:
        {
            "success": true,
            "data": {
                "param": {
                    "id": 1,
                    "param_name": "zone_id",
                    "param_name_cn": "区域ID",
                    "param_type": "string",
                    "table_name": "dwd_common_params",
                    "game_name": "Game Name",
                    "gid": 10000147
                },
                "alter_sql": "-- ALTER TABLE Statement\\nALTER TABLE dwd_common_params ADD COLUMN IF NOT EXISTS zone_id STRING COMMENT '区域ID';"
            }
        }
    """
    try:
        # Import HQL manager
        from backend.services.hql.manager import HQLManager

        # Get parameter details with game information
        param = fetch_one_as_dict(
            """
            SELECT
                p.id,
                p.param_name,
                p.param_name_cn,
                p.param_type,
                p.table_name,
                g.name as game_name,
                g.gid
            FROM common_params p
            JOIN games g ON p.game_id = g.id
            WHERE p.id = ?
        """,
            (param_id,),
        )

        if not param:
            return json_error_response("Parameter not found", status_code=404)

        # Generate ALTER TABLE HQL
        manager = HQLManager()
        alter_sql = manager.generate_alter_table_hql(
            target_table=param["table_name"],
            param_name=param["param_name"],
            param_type=param["param_type"],
            param_name_cn=param["param_name_cn"],
        )

        logger.info(f"Generated ALTER TABLE SQL for param_id={param_id}")

        return json_success_response(data={"param": param, "alter_sql": alter_sql})

    except Exception as e:
        logger.error(f"Error generating ALTER TABLE SQL for param_id={param_id}: {e}")
        return json_error_response(str(e), status_code=500)
