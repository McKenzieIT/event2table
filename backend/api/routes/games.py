"""
Games API Routes Module (精简架构)

This module contains all game-related API endpoints:
- GET /api/games - List all games
- POST /api/games - Create a new game
- GET /api/games/<gid> - Get a single game by business GID
- GET /api/games/by-gid/<gid> - Get a single game by business GID (semantic alias)
- PUT/PATCH /api/games/<gid> - Update a game by business GID
- DELETE /api/games/<gid> - Delete a game by business GID
- DELETE /api/games/batch - Batch delete games
- PUT /api/games/batch-update - Batch update games

架构变更:
- 使用统一Entity模型 (GameEntity) 进行请求验证和响应序列化
- 移除手动验证,改用Pydantic自动验证
- 返回GameEntity.model_dump()而非字典

NOTE: All game queries use business GID (e.g., 10000147), not database ID.
"""

import logging
from typing import List, Tuple, Dict, Any
from pydantic import ValidationError

from flask import request

# 导入统一Entity模型
from backend.models.entities import GameEntity

# 导入响应工具
from backend.core.utils import json_error_response, json_success_response

# 导入Service层
from backend.services.games.game_service import GameService

# 导入缓存失效器 (用于兼容性)
try:
    from backend.core.cache.cache_system import CacheInvalidator
except ImportError:
    CacheInvalidator = None

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


# ============================================================================
# API Endpoints
# ============================================================================


@api_bp.route("/api/games", methods=["GET"])
def list_games():
    """
    获取所有游戏列表

    Query Parameters:
        include_stats (bool): 是否包含统计信息 (事件数量、流程数量)

    Returns:
        JSON响应: {"success": true, "data": [...]}
    """
    try:
        include_stats = request.args.get("include_stats", "false").lower() == "true"

        service = GameService()
        games = service.get_all_games(include_stats=include_stats)

        # 序列化Entity为字典
        data = [game.model_dump() for game in games]

        return json_success_response(data=data)
    except Exception as e:
        logger.error(f"Error listing games: {e}")
        return json_error_response("Failed to list games", status_code=500)


@api_bp.route("/api/games/<int:game_gid>", methods=["GET"])
def get_game(game_gid: int):
    """
    根据GID获取单个游戏

    Args:
        game_gid: 游戏业务GID (如 10000147)

    Returns:
        JSON响应: {"success": true, "data": {...}}
    """
    try:
        service = GameService()
        game = service.get_game_by_gid(game_gid)

        if game is None:
            return json_error_response(f"Game GID {game_gid} not found", status_code=404)

        # 序列化Entity为字典
        return json_success_response(data=game.model_dump())
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error getting game {game_gid}: {e}")
        return json_error_response("Failed to get game", status_code=500)


@api_bp.route("/api/games", methods=["POST"])
def create_game():
    """
    创建新游戏

    Request Body:
        {
            "gid": 10000147,
            "name": "STAR001",
            "ods_db": "ieu_ods",
            "description": "测试游戏" (可选)
        }

    Returns:
        JSON响应: {"success": true, "data": {...}}
    """
    try:
        # 使用Pydantic Entity自动验证
        game_data = GameEntity(**request.get_json())

        service = GameService()
        created_game = service.create_game(game_data)

        # 序列化Entity为字典
        return json_success_response(
            data=created_game.model_dump(),
            message="Game created successfully",
        )
    except ValidationError as e:
        return json_error_response(f"Validation error: {e}", status_code=400)
    except ValueError as e:
        return json_error_response(str(e), status_code=409)
    except Exception as e:
        logger.error(f"Error creating game: {e}")
        return json_error_response("Failed to create game", status_code=500)


@api_bp.route("/api/games/<int:game_gid>", methods=["PUT", "PATCH"])
def update_game(game_gid: int):
    """
    更新游戏信息

    Args:
        game_gid: 游戏业务GID

    Request Body:
        {
            "name": "新名称" (可选),
            "ods_db": "ieu_ods" (可选)
        }

    Returns:
        JSON响应: {"success": true, "data": {...}}
    """
    try:
        # 获取更新字段
        updates = request.get_json()

        if not updates:
            return json_error_response("No update fields provided", status_code=400)

        service = GameService()
        updated_game = service.update_game(game_gid, updates)

        # 序列化Entity为字典
        return json_success_response(
            data=updated_game.model_dump(),
            message="Game updated successfully",
        )
    except ValueError as e:
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error updating game {game_gid}: {e}")
        return json_error_response("Failed to update game", status_code=500)


@api_bp.route("/api/games/<int:game_gid>", methods=["DELETE"])
def delete_game(game_gid: int):
    """
    删除游戏

    Args:
        game_gid: 游戏业务GID

    Returns:
        JSON响应: {"success": true, "message": "..."}
    """
    try:
        service = GameService()
        service.delete_game(game_gid)

        return json_success_response(message=f"Game GID {game_gid} deleted successfully")
    except ValueError as e:
        return json_error_response(str(e), status_code=404)
    except Exception as e:
        logger.error(f"Error deleting game {game_gid}: {e}")
        return json_error_response("Failed to delete game", status_code=500)


@api_bp.route("/api/games/batch", methods=["DELETE"])
def batch_delete_games():
    """
    批量删除游戏

    Request Body:
        {
            "game_gids": [10000147, 10000148, ...]
        }

    Returns:
        JSON响应: {"success": true, "data": {"deleted_count": 3}}
    """
    try:
        data = request.get_json()
        game_gids = data.get("game_gids", [])

        if not game_gids:
            return json_error_response("No game GIDs provided", status_code=400)

        service = GameService()
        deleted_count = service.batch_delete_games(game_gids)

        return json_success_response(
            data={"deleted_count": deleted_count},
            message=f"Deleted {deleted_count} games successfully",
        )
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error batch deleting games: {e}")
        return json_error_response("Failed to batch delete games", status_code=500)

logger = logging.getLogger(__name__)


@api_bp.route("/api/games", methods=["GET"])
def api_list_games() -> Tuple[Dict[str, Any], int]:
    """
    API: List all games with statistics

    PERFORMANCE OPTIMIZATION:
    This endpoint was optimized to eliminate N+1 query problem and implement caching.
    - Previous implementation used 4 correlated subqueries per game (212+ queries for 53 games)
    - Now uses LEFT JOINs with GROUP BY to aggregate all data in a single query
    - Implements Flask-Caching with Redis backend for sub-10ms response times
    - Cache TTL: 1 hour (static data)
    - Cache key: "games:list:v1"

    Returns:
        Tuple containing response dictionary and HTTP status code

    Response Format:
        {
            "success": true,
            "data": [
                {
                    "id": int,
                    "gid": int,
                    "name": str,
                    "ods_db": str,
                    "icon_path": str,
                    "created_at": str,
                    "updated_at": str,
                    "event_count": int,
                    "param_count": int,
                    "event_node_count": int,
                    "flow_template_count": int
                }
            ]
        }
    """
    from flask import current_app

    # Try to get from cache first
    cache_key = "games:list:v1"
    try:
        cached_games = current_app.cache.get(cache_key)
        # Only use cached data if it's non-empty (prevent serving stale empty cache)
        if cached_games is not None and len(cached_games) > 0:
            logger.debug(f"Cache HIT: {len(cached_games)} games from cache")
            return json_success_response(data=cached_games)
        elif cached_games is not None and len(cached_games) == 0:
            # Empty cache - treat as cache miss and re-query
            logger.warning(f"Cache contains empty array, treating as cache miss")
    except (AttributeError, RuntimeError) as e:
        logger.warning(f"Cache not available: {e}")

    # Cache miss - execute query and cache the result
    games = fetch_all_as_dict("""
        SELECT
            g.id,
            g.gid,
            g.name,
            g.ods_db,
            g.icon_path,
            g.created_at,
            g.updated_at,
            COUNT(DISTINCT le.id) as event_count,
            COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as param_count,
            COUNT(DISTINCT enc.id) as event_node_count,
            COUNT(DISTINCT CASE WHEN ft.is_active = 1 THEN ft.id END) as flow_template_count
        FROM games g
        LEFT JOIN log_events le ON le.game_gid = g.gid
        LEFT JOIN event_params ep ON ep.event_id = le.id
        LEFT JOIN event_node_configs enc ON enc.game_gid = CAST(g.gid AS INTEGER)
        LEFT JOIN flow_templates ft ON ft.game_gid = g.gid
        GROUP BY g.id, g.gid, g.name, g.ods_db, g.icon_path, g.created_at, g.updated_at
        ORDER BY g.id
    """)

    # Only cache non-empty results (prevent caching empty arrays on errors)
    try:
        if games and len(games) > 0:
            current_app.cache.set(cache_key, games, timeout=3600)
            logger.info(f"Cached {len(games)} games for {3600}s")
        else:
            logger.warning(f"Not caching empty games result")
    except (AttributeError, RuntimeError) as e:
        logger.warning(f"Cache set failed: {e}")

    return json_success_response(data=games)


@api_bp.route("/api/games", methods=["POST"])
def api_create_game() -> Tuple[Dict[str, Any], int]:
    """
    API: Create a new game

    Request Body:
        {
            "gid": int,           # Business GID (required)
            "name": str,          # Game name (required)
            "ods_db": str         # ODS database name (required)
        }

    Returns:
        Tuple containing response dictionary and HTTP status code

    Raises:
        400: If validation fails or GID already exists
        500: If server error occurs
    """
    is_valid, data, error = validate_json_request(["gid", "name", "ods_db"])
    if not is_valid:
        logger.warning(f"Game creation failed: {error}")
        return json_error_response(error, status_code=400)

    # Log received data for debugging
    logger.info(f"Game creation request - GID type: {type(data.get('gid'))}, GID value: {data.get('gid')}")
    logger.info(f"Game creation request - name: {data.get('name')}, ods_db: {data.get('ods_db')}")

    # Validate and convert GID (handle both int and string inputs)
    gid_value = data.get("gid")
    if gid_value is None:
        logger.warning("Game creation failed: GID is missing")
        return json_error_response("Game GID is required", status_code=400)

    # Convert GID to integer (handle string inputs from frontend)
    try:
        if isinstance(gid_value, str):
            gid_value = int(gid_value)
        elif not isinstance(gid_value, int):
            raise ValueError(f"Invalid GID type: {type(gid_value)}")
    except (ValueError, TypeError) as e:
        logger.warning(f"Game creation failed: Invalid GID format - {e}")
        return json_error_response(
            f"Game GID must be a valid integer, received: {gid_value}",
            status_code=400
        )

    # Validate GID is positive
    if gid_value <= 0:
        logger.warning(f"Game creation failed: GID must be positive, received: {gid_value}")
        return json_error_response(
            "Game GID must be a positive integer", status_code=400
        )

    # 验证和清理游戏名称
    is_valid, result = sanitize_and_validate_string(
        data.get("name"), max_length=200, field_name="name", allow_empty=False
    )
    if not is_valid:
        logger.warning(f"Game creation failed: Invalid name - {result}")
        return json_error_response(result, status_code=400)
    name = result

    # 验证和清理数据库名称
    is_valid, result = sanitize_and_validate_string(
        data.get("ods_db", ""), max_length=100, field_name="ods_db", allow_empty=False
    )
    if not is_valid:
        logger.warning(f"Game creation failed: Invalid ods_db - {result}")
        return json_error_response(result, status_code=400)
    ods_db = result

    # 简化INSERT：只包含必需字段
    try:
        query = "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)"
        execute_write(query, (gid_value, name, ods_db))
        if cache_invalidator:
            cache_invalidator.invalidate_pattern("dashboard_statistics:*")  # Clear dashboard cache
        logger.info(f"Game created successfully: {name} (GID: {gid_value})")
        return json_success_response(
            message="Game created successfully",
            data={"gid": gid_value, "name": name, "ods_db": ods_db}
        )
    except sqlite3.IntegrityError:
        logger.warning(f"Game creation failed: GID {gid_value} already exists")
        # 使用标准化的错误消息
        return json_error_response(
            error_messages.ErrorMessages.duplicate_game_gid(gid_value),
            status_code=409
        )
    except Exception as e:
        logger.error(f"Error creating game: {e}", exc_info=True)
        # 使用标准化的错误消息
        return json_error_response(
            error_messages.ErrorMessages.server_error(),
            status_code=500
        )


@api_bp.route("/api/games/<int:gid>", methods=["GET"])
def api_get_game(gid: int) -> Tuple[Dict[str, Any], int]:
    """
    API: Get a single game by business GID

    Args:
        gid: Business GID of the game

    Returns:
        Tuple containing response dictionary with game data and HTTP status code

    Raises:
        404: If game not found
    """
    # 使用Repository模式按gid查询
    game = Repositories.GAMES.find_by_field("gid", gid)
    if not game:
        return json_error_response("Game not found", status_code=404)
    return json_success_response(data=game)


@api_bp.route("/api/games/by-gid/<int:gid>", methods=["GET"])
def api_get_game_by_gid(gid: int) -> Tuple[Dict[str, Any], int]:
    """
    API: Get a single game by business GID (semantic route)

    This is a semantic alias for /api/games/<gid> with clearer naming.
    Route /by-gid/ explicitly indicates querying by business GID.

    Args:
        gid: Business GID of game (e.g., 10000147)

    Returns:
        Tuple containing response dictionary with game data and HTTP status code

    Raises:
        404: If game not found
    """
    # 使用Repository模式按gid查询
    game = Repositories.GAMES.find_by_field("gid", gid)
    if not game:
        return json_error_response("Game not found", status_code=404)
    return json_success_response(data=game)


@api_bp.route("/api/games/<int:gid>", methods=["PUT", "PATCH"])
def api_update_game(gid):
    """API: Update an existing game by business GID

    Supports partial updates - only provide fields you want to update.
    Valid fields: name, ods_db

    Example:
        PUT /api/games/10000147
        {"name": "Updated Name"}  # Only updates name
        {"ods_db": "new_db"}  # Only updates ods_db
        {"name": "Updated", "ods_db": "new_db"}  # Updates both
    """
    # 使用Repository模式按gid查询
    game = Repositories.GAMES.find_by_field("gid", gid)
    if not game:
        return json_error_response("Game not found", status_code=404)

    # Validate JSON format (but don't require specific fields for partial updates)
    if not request.is_json:
        return json_error_response("Request must be JSON", status_code=400)

    data = request.get_json()
    if data is None:
        return json_error_response("Invalid JSON data", status_code=400)

    # Build update fields dynamically based on what's provided
    update_fields = []
    update_values = []

    # Validate input fields against whitelist
    provided_fields = set(data.keys())
    invalid_fields = provided_fields - ALLOWED_UPDATE_FIELDS
    if invalid_fields:
        return json_error_response(
            f"Invalid fields: {', '.join(sorted(invalid_fields))}. "
            f"Allowed fields: {', '.join(sorted(ALLOWED_UPDATE_FIELDS))}",
            status_code=400,
        )

    # Validate and sanitize name if provided
    if "name" in data:
        is_valid, result = sanitize_and_validate_string(
            data.get("name"), max_length=200, field_name="name", allow_empty=False
        )
        if not is_valid:
            return json_error_response(result, status_code=400)
        update_fields.append("name = ?")
        update_values.append(result)

    # Validate and sanitize ods_db if provided
    if "ods_db" in data:
        is_valid, result = sanitize_and_validate_string(
            data.get("ods_db"), max_length=100, field_name="ods_db", allow_empty=False
        )
        if not is_valid:
            return json_error_response(result, status_code=400)
        update_fields.append("ods_db = ?")
        update_values.append(result)

    # Check if at least one field is being updated
    if not update_fields:
        return json_error_response(
            "No valid fields to update. Provide 'name' and/or 'ods_db'", status_code=400
        )

    # Add gid to the values for the WHERE clause
    update_values.append(gid)

    try:
        # Build dynamic UPDATE query
        query = f"UPDATE games SET {', '.join(update_fields)} WHERE gid = ?"
        execute_write(query, tuple(update_values))

        # ✅ Fix: Query and return updated game data
        updated_game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))

        # ✅ Fix: Clear Flask-Caching cache using cache_invalidator
        if cache_invalidator:
            cache_invalidator.invalidate_pattern("games:list:*")
            cache_invalidator.invalidate_pattern("games:list:v1")
            cache_invalidator.invalidate_pattern("dashboard_statistics:*")
        logger.info(f"Game updated: GID {gid}, fields: {', '.join(update_fields)}")

        # ✅ Fix: Return updated game data in response
        return json_success_response(data=updated_game, message="Game updated successfully")
    except Exception as e:
        logger.error(f"Error updating game: {e}")
        return json_error_response("Failed to update game", status_code=500)


def check_deletion_impact(game_gid: int) -> Dict[str, Any]:
    """
    检查删除游戏的影响范围

    Args:
        game_gid: 游戏业务GID

    Returns:
        影响统计字典
    """
    # fetch_one_as_dict is already imported from backend.core.utils (line 27)

    impact = {
        "game_gid": game_gid,
        "has_associated_data": False,
        "event_count": 0,
        "param_count": 0,
        "node_config_count": 0,
    }

    # 检查事件数量
    event_count = fetch_one_as_dict(
        "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?", (game_gid,)
    )
    impact["event_count"] = event_count["count"]

    # 检查参数数量（通过事件关联）
    param_count = fetch_one_as_dict(
        """
        SELECT COUNT(*) as count
        FROM event_params ep
        INNER JOIN log_events le ON ep.event_id = le.id
        WHERE le.game_gid = ?
    """,
        (game_gid,),
    )
    impact["param_count"] = param_count["count"]

    # 检查Canvas节点配置
    node_count = fetch_one_as_dict(
        "SELECT COUNT(*) as count FROM event_node_configs WHERE game_gid = ?",
        (game_gid,),
    )
    impact["node_config_count"] = node_count["count"]

    # 判断是否有关联数据
    impact["has_associated_data"] = any(
        [
            impact["event_count"] > 0,
            impact["param_count"] > 0,
            impact["node_config_count"] > 0,
        ]
    )

    logger.debug(
        f"Deletion impact for game_gid={game_gid}: "
        f"events={impact['event_count']}, "
        f"params={impact['param_count']}, "
        f"nodes={impact['node_config_count']}"
    )

    return impact


def execute_cascade_delete(
    game: Dict[str, Any], impact: Dict[str, Any]
) -> Tuple[Dict[str, Any], int]:
    """
    执行级联删除游戏及其所有关联数据

    Args:
        game: 游戏数据（包含id和gid）
        impact: 影响统计

    Returns:
        (响应字典, HTTP状态码)
    """
    from backend.core.database import get_db_connection

    game_gid = game["gid"]
    game_id = game["id"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("BEGIN IMMEDIATE")  # 立即锁，防止并发修改

            # 验证游戏仍然存在（防止已被其他请求删除）
            cursor.execute("SELECT id FROM games WHERE id = ?", (game_id,))
            game_exists = cursor.fetchone()

            if not game_exists:
                conn.rollback()
                return json_error_response(
                    "Game not found (may have been deleted)", status_code=404
                )

            # 1. 删除事件参数（通过事件ID）
            cursor.execute(
                """
                DELETE FROM event_params
                WHERE event_id IN (
                    SELECT id FROM log_events WHERE game_gid = ?
                )
            """,
                (game_gid,),
            )

            # 2. 删除事件记录
            cursor.execute("DELETE FROM log_events WHERE game_gid = ?", (game_gid,))

            # 3. 删除Canvas节点配置
            cursor.execute(
                "DELETE FROM event_node_configs WHERE game_gid = ?", (game_gid,)
            )

            # 4. 删除游戏记录（在同一事务中完成）
            cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))

            conn.commit()

            logger.info(
                f"Cascade deleted game {game['name']} (GID: {game_gid}): "
                f"{impact['event_count']} events, "
                f"{impact['param_count']} params, "
                f"{impact['node_config_count']} node configs"
            )

            return json_success_response(
                message="Game and all associated data deleted successfully",
                data={
                    "deleted_event_count": impact["event_count"],
                    "deleted_param_count": impact["param_count"],
                    "deleted_node_config_count": impact["node_config_count"],
                },
            )

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            conn.close()

    except Exception as e:
        logger.error(f"Error cascade deleting game: {e}")
        return json_error_response("Failed to delete game", status_code=500)


@api_bp.route("/api/games/<int:gid>", methods=["DELETE"])
def api_delete_game(gid):
    """API: Delete a game by business GID (with confirmation)"""
    logger.info(
        f"*** api_delete_game CALLED with gid={gid}, force_delete={request.get_json() or {}.get('confirm', False)} ***"
    )

    # 获取确认标志
    data = request.get_json() or {}
    force_delete = data.get("confirm", False)

    # 查询游戏
    game = Repositories.GAMES.find_by_field("gid", gid)
    if not game:
        return json_error_response("Game not found", status_code=404)

    # 检查删除影响
    impact = check_deletion_impact(gid)

    # 如果没有确认标志且有关联数据，返回影响统计
    if not force_delete and impact["has_associated_data"]:
        return json_error_response(
            f"Game has {impact['event_count']} events, "
            f"{impact['param_count']} parameters, "
            f"{impact['node_config_count']} node configs. "
            f"Set confirm=true to force delete.",
            status_code=409,
            data={
                "event_count": impact["event_count"],
                "param_count": impact["param_count"],
                "node_config_count": impact["node_config_count"],
            },
        )

    # 执行级联删除
    result, status_code = execute_cascade_delete(game, impact)

    # 清理缓存
    if status_code == 200:
        cache_invalidator.invalidate("games.list")
        cache_invalidator.invalidate("dashboard_statistics")

        # ✅ 显式清除Flask-Caching的列表缓存
        try:
            from flask import current_app

            if hasattr(current_app, "cache"):
                current_app.cache.delete("games:list:v1")
                logger.info("✅ Cleared games:list:v1 Flask-Caching after deletion")
        except (AttributeError, RuntimeError) as e:
            logger.warning(f"Failed to clear Flask-Caching games:list cache: {e}")

    return result, status_code


@api_bp.route("/api/games/batch", methods=["DELETE"])
def api_batch_delete_games():
    """API: Batch delete games"""
    is_valid, data, error = validate_json_request(["ids"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    game_ids = data.get("ids", [])

    if not game_ids or not isinstance(game_ids, list):
        return json_error_response("Invalid game IDs", status_code=400)

    try:
        # Check all games for associated events before deletion
        games = Repositories.GAMES.find_by_ids(game_ids)

        if not games:
            return json_error_response("No games found", status_code=404)

        # Batch check for associated events (single query)
        gids = [g["gid"] for g in games]
        placeholders = ",".join(["?"] * len(gids))
        event_counts = fetch_all_as_dict(
            f"SELECT game_gid, COUNT(*) as count FROM log_events WHERE game_gid IN ({placeholders}) GROUP BY game_gid",
            tuple(gids),
        )
        count_map = {e["game_gid"]: e["count"] for e in event_counts}

        # Check if any game has associated events
        for game in games:
            event_count = count_map.get(game["gid"], 0)
            if event_count > 0:
                return json_error_response(
                    f"Cannot delete game '{game['name']}' with {event_count} associated events. "
                    "Delete events first.",
                    status_code=409,
                )

        # Delete games using Repository batch delete
        deleted_count = Repositories.GAMES.delete_batch(game_ids)

        if cache_invalidator:
            cache_invalidator.invalidate_pattern("games.list:*")  # Clear cache after delete
        if cache_invalidator:
            cache_invalidator.invalidate_pattern("dashboard_statistics:*")  # Clear dashboard cache
        logger.info(f"Batch deleted {deleted_count} games")
        return json_success_response(
            message=f"Deleted {deleted_count} games",
            data={"deleted_count": deleted_count},
        )
    except Exception as e:
        logger.error(f"Error batch deleting games: {e}")
        return json_error_response("Failed to delete games", status_code=500)


@api_bp.route("/api/games/batch-update", methods=["PUT"])
def api_batch_update_games():
    """API: Batch update games

    Example request body:
    {
        "ids": [1, 2, 3],
        "updates": {"name": "Updated Name", "ods_db": "new_db"}
    }
    """
    is_valid, data, error = validate_json_request(["ids", "updates"])
    if not is_valid:
        return json_error_response(error, status_code=400)

    game_ids = data.get("ids", [])
    updates = data.get("updates", {})

    if not game_ids or not updates:
        return json_error_response("Invalid request data", status_code=400)

    try:
        # Validate and sanitize update fields
        if "name" in updates:
            is_valid, result = sanitize_and_validate_string(
                updates["name"], max_length=200, field_name="name", allow_empty=False
            )
            if not is_valid:
                return json_error_response(result, status_code=400)
            updates["name"] = result

        if "ods_db" in updates:
            is_valid, result = sanitize_and_validate_string(
                updates["ods_db"],
                max_length=100,
                field_name="ods_db",
                allow_empty=False,
            )
            if not is_valid:
                return json_error_response(result, status_code=400)
            updates["ods_db"] = result

        # Use Repository batch update
        updated_count = Repositories.GAMES.update_batch(game_ids, updates)

        if cache_invalidator:
            cache_invalidator.invalidate_pattern("games.list:*")  # Clear cache after update
        if cache_invalidator:
            cache_invalidator.invalidate_pattern("dashboard_statistics:*")  # Clear dashboard cache
        logger.info(f"Batch updated {updated_count} games")
        return json_success_response(
            message=f"Updated {updated_count} games",
            data={"updated_count": updated_count},
        )
    except Exception as e:
        logger.error(f"Error batch updating games: {e}")
        return json_error_response("Failed to update games", status_code=500)
