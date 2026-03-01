"""
Games API Routes Module (精简架构 - 统一使用 GameService)

This module contains all game-related API endpoints:
- GET /api/games - List all games (with optional statistics)
- POST /api/games - Create a new game
- GET /api/games/<gid> - Get a single game by business GID
- PUT/PATCH /api/games/<gid> - Update a game by business GID
- DELETE /api/games/<gid> - Delete a game by business GID (with cascade support)
- DELETE /api/games/batch - Batch delete games
- PUT /api/games/batch-update - Batch update games

架构变更:
- 使用统一Entity模型 (GameEntity) 进行请求验证和响应序列化
- 所有操作通过 GameService，无直接数据库访问
- 支持级联删除和详细统计查询
- 移除双规制代码，统一架构

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
        include_stats (bool): 是否包含详细统计信息（事件数、参数数、节点数等）
        simple (bool): 如果为 true，返回简单的 Entity 列表（默认 false）

    Returns:
        JSON响应: {"success": true, "data": [...]}
    """
    try:
        service = GameService()

        # 检查是否需要详细统计
        include_detailed_stats = request.args.get("include_stats", "false").lower() == "true"
        simple_mode = request.args.get("simple", "false").lower() == "true"

        if include_detailed_stats and not simple_mode:
            # 使用详细统计查询（LEFT JOIN）
            games = service.get_games_with_detailed_stats()
        else:
            # 使用简单查询（Entity 模型）
            games = service.get_all_games(include_stats=False)
            games = [game.model_dump() for game in games]

        return json_success_response(data=games)
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
    删除游戏（支持级联删除）

    Args:
        game_gid: 游戏业务GID

    Request Body (optional):
        {
            "confirm": true  # 设置为 true 以强制删除有关联数据的游戏
        }

    Returns:
        JSON响应: {"success": true, "message": "...", "data": {...}}
    """
    try:
        service = GameService()

        # 获取确认标志
        data = request.get_json() or {}
        force_delete = data.get("confirm", False)

        # 检查删除影响
        impact = service.check_deletion_impact(game_gid)

        # 如果未确认且有关联数据，返回影响统计
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
        result = service.cascade_delete_game(game_gid, force=force_delete)

        return json_success_response(
            message=f"Game GID {game_gid} and all associated data deleted successfully",
            data=result
        )
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


@api_bp.route("/api/games/batch-update", methods=["PUT"])
def batch_update_games():
    """
    批量更新游戏

    Request Body:
        {
            "game_gids": [10000147, 10000148, ...],
            "updates": {
                "name": "Updated Name",
                "ods_db": "new_db"
            }
        }

    Returns:
        JSON响应: {"success": true, "data": {"updated_count": 3}}
    """
    try:
        data = request.get_json()
        game_gids = data.get("game_gids", [])
        updates = data.get("updates", {})

        if not game_gids:
            return json_error_response("No game GIDs provided", status_code=400)

        if not updates:
            return json_error_response("No update fields provided", status_code=400)

        # 验证更新字段
        if "name" in updates:
            game_data = GameEntity(name=updates["name"])
        if "ods_db" in updates:
            game_data = GameEntity(ods_db=updates["ods_db"])

        service = GameService()
        updated_count = service.batch_update_games(game_gids, updates)

        return json_success_response(
            data={"updated_count": updated_count},
            message=f"Updated {updated_count} games successfully",
        )
    except ValidationError as e:
        return json_error_response(f"Validation error: {e}", status_code=400)
    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error batch updating games: {e}")
        return json_error_response("Failed to batch update games", status_code=500)
