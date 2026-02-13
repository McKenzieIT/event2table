#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Games Management Module (API Only)
===================================

Handles all game-related API endpoints.
Frontend is now handled by React SPA (modules/react_shell.py).

Legacy template routes have been removed as part of frontend-backend separation.
Created: 2026-01-25
"""

import sqlite3

from flask import Blueprint, jsonify, request, session

from backend.core.cache.cache_system import clear_game_cache
from backend.core.database import get_db_connection
from backend.core.logging import get_logger
from backend.core.utils import (
    error_response,
    execute_write,
    fetch_all_as_dict,
    fetch_one_as_dict,
    success_response,
    validate_json_request,
)

logger = get_logger(__name__)

games_bp = Blueprint("games_service", __name__)


@games_bp.route("/api/set-game-context", methods=["POST"])
def set_game_context():
    """
    设置游戏上下文到session

    Request JSON:
        game_gid (int): 游戏数据库ID

    Returns:
        JSON response with success/error status
    """
    try:
        data = request.get_json()
        game_gid = data.get("game_gid")

        if not game_gid:
            logger.warning("[SetGameContext] No game_gid provided in request")
            return jsonify(error_response("Missing game_gid", status_code=400)[0]), 400

        # 查询游戏信息 - 使用 game_gid 而非 id
        game = fetch_one_as_dict("SELECT id, gid, name FROM games WHERE gid = ?", (game_gid,))

        if not game:
            logger.warning(f"[SetGameContext] Game not found: game_gid={game_gid}")
            return jsonify(error_response("Game not found", status_code=404)[0]), 404

        # 设置session（同时设置id和gid，兼容旧代码）
        session["current_game_gid"] = game["id"]
        session["current_game_gid"] = game["gid"]

        logger.info(
            f'[SetGameContext] Session set: game_gid={game["id"]}, '
            f'game_gid={game["gid"]}, game_name={game["name"]}'
        )

        return jsonify(
            success_response(
                data={"game_gid": game["id"], "game_gid": game["gid"], "game_name": game["name"]}
            )[0]
        )

    except Exception as e:
        logger.error(f"[SetGameContext] Error: {str(e)}", exc_info=True)
        return jsonify(error_response(f"Server error: {str(e)}", status_code=500)[0]), 500


# @games_bp.route('/api/games/<int:id>')  # CONFLICTS with api_bp
def get_game(id):
    """
    获取单个游戏信息

    Args:
        id: 游戏ID

    Returns:
        JSON: 游戏信息
    """
    try:
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (id,))
        if not game:
            response, _ = error_response("Game not found", status_code=404)
            return jsonify(response), 404

        response, _ = success_response(data=game)
        return jsonify(response)

    except Exception as e:
        logger.error(f"[GetGame] Error: {str(e)}", exc_info=True)
        response, _ = error_response(f"Server error: {str(e)}", status_code=500)
        return jsonify(response), 500


@games_bp.route("/api/games/by-gid/<gid>")
def get_game_by_gid(gid):
    """
    根据业务GID获取游戏信息（非数据库ID）

    Args:
        gid: 游戏业务GID (如 10000147)

    Returns:
        JSON: 游戏信息
    """
    try:
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
        if not game:
            response, _ = error_response("Game not found", status_code=404)
            return jsonify(response), 404

        response, _ = success_response(data=game)
        return jsonify(response)

    except Exception as e:
        logger.error(f"[GetGameByGID] Error: {str(e)}", exc_info=True)
        response, _ = error_response(f"Server error: {str(e)}", status_code=500)
        return jsonify(response), 500


# DISABLED: Conflicts with backend/api/routes/games.py
# @games_bp.route('/api/games', methods=['GET'])
# def list_games():
#     """
#     获取所有游戏列表
#
#     Returns:
#         JSON: 游戏列表
#     """
#     try:
#         games = fetch_all_as_dict('SELECT * FROM games ORDER BY id')
#         response, _ = success_response(data=games)
#         return jsonify(response)
#     except Exception as e:
#         logger.error(f'[ListGames] Error: {str(e)}', exc_info=True)
#         response, _ = error_response(f'Server error: {str(e)}', status_code=500)
#         return jsonify(response), 500
#
#
# DISABLED: Conflicts with backend/api/routes/games.py
# @games_bp.route('/api/games', methods=['POST'])
# def create_game():
#     """
#     创建新游戏
#
#     Request JSON:
#         gid (str): 游戏业务GID
#         name (str): 游戏名称
#         ods_db (str): ODS数据库名称
#
#     Returns:
#         JSON: 创建的游戏信息
#     """
#     try:
#         # 验证JSON请求
#         is_valid, data, error_msg = validate_json_request(required_fields=['gid', 'name', 'ods_db'])
#         if not is_valid:
#             response, _ = error_response(error_msg, status_code=400)
#             return jsonify(response), 400
#
#         gid = data.get('gid', '').strip()
#         name = data.get('name', '').strip()
#         ods_db = data.get('ods_db', '').strip()
#
#         # 验证必填字段
#         if not gid:
#             response, _ = error_response('GID is required', status_code=400)
#             return jsonify(response), 400
#         if not name:
#             response, _ = error_response('Name is required', status_code=400)
#             return jsonify(response), 400
#         if not ods_db:
#             response, _ = error_response('ODS database is required', status_code=400)
#             return jsonify(response), 400
#
#         # 检查GID是否已存在
#         existing = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))
#         if existing:
#             response, _ = error_response(f'Game GID {gid} already exists', status_code=409)
#             return jsonify(response), 409
#
#         # 创建游戏
#         execute_write(
#             'INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)',
#             (gid, name, ods_db)
#         )
#         clear_game_cache()
#
#         # 获取创建的游戏
#         game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (gid,))
#
#         logger.info(f'[CreateGame] Game created: {name} (GID: {gid}, ODS: {ods_db})')
#         response, _ = success_response(data=game, message='Game created successfully', status_code=201)
#         return jsonify(response), 201
#
#     except sqlite3.IntegrityError as e:
#         logger.error(f'[CreateGame] IntegrityError: {e}')
#         response, _ = error_response(f'Game GID already exists', status_code=409)
#         return jsonify(response), 409
#     except Exception as e:
#         logger.error(f'[CreateGame] Error: {str(e)}', exc_info=True)
#         response, _ = error_response(f'Server error: {str(e)}', status_code=500)
#         return jsonify(response), 500
#
#
# @games_bp.route('/api/games/<int:id>', methods=['PUT'])  # CONFLICTS with api_bp
def update_game(id):
    """
    更新游戏信息

    Args:
        id: 游戏数据库ID

    Request JSON:
        name (str): 游戏名称
        ods_db (str): ODS数据库名称

    Returns:
        JSON: 更新后的游戏信息
    """
    try:
        # 验证JSON请求
        is_valid, data, error_msg = validate_json_request(required_fields=[])
        if not is_valid:
            response, _ = error_response(error_msg, status_code=400)
            return jsonify(response), 400

        # 检查游戏是否存在
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (id,))
        if not game:
            response, _ = error_response("Game not found", status_code=404)
            return jsonify(response), 404

        name = data.get("name", "").strip()
        ods_db = data.get("ods_db", "").strip()

        # 验证必填字段
        if not name:
            response, _ = error_response("Name is required", status_code=400)
            return jsonify(response), 400
        if not ods_db:
            response, _ = error_response("ODS database is required", status_code=400)
            return jsonify(response), 400

        # 更新游戏
        execute_write(
            "UPDATE games SET name = ?, ods_db = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, ods_db, id),
        )
        clear_game_cache()

        # 获取更新后的游戏
        updated_game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (id,))

        logger.info(f"[UpdateGame] Game updated: {name} (ID: {id}, ODS: {ods_db})")
        response, _ = success_response(data=updated_game, message="Game updated successfully")
        return jsonify(response)

    except Exception as e:
        logger.error(f"[UpdateGame] Error: {str(e)}", exc_info=True)
        response, _ = error_response(f"Server error: {str(e)}", status_code=500)
        return jsonify(response), 500


# @games_bp.route('/api/games/<int:id>', methods=['DELETE'])  # CONFLICTS with api_bp
def delete_game(id):
    """
    删除游戏

    Args:
        id: 游戏数据库ID

    Returns:
        JSON: 删除结果
    """
    try:
        # 检查游戏是否存在
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (id,))
        if not game:
            response, _ = error_response("Game not found", status_code=404)
            return jsonify(response), 404

        # 删除游戏
        execute_write("DELETE FROM games WHERE id = ?", (id,))
        clear_game_cache()

        logger.info(f'[DeleteGame] Game deleted: {game["name"]} (ID: {id})')
        response, _ = success_response(message="Game deleted successfully")
        return jsonify(response)

    except Exception as e:
        logger.error(f"[DeleteGame] Error: {str(e)}", exc_info=True)
        response, _ = error_response(f"Server error: {str(e)}", status_code=500)
        return jsonify(response), 500
