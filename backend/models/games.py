#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Games Management Module
Handles all game-related operations
"""

import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from backend.core.database import get_db_connection
from backend.core.config import ODSDatabase
from backend.core.logging import get_logger
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    execute_write,
    success_response,
    error_response,
    validate_json_request,
    json_success_response,
    json_error_response,
)
from backend.core.cache.cache_system import clear_game_cache

logger = get_logger(__name__)

games_bp = Blueprint("games", __name__)


@games_bp.route("/games")
def list_games():
    """List all games"""
    try:
        games = fetch_all_as_dict("SELECT * FROM games ORDER BY id")
        return render_template("games.html", games=games)
    except Exception as e:
        logger.error(f"Error listing games: {e}")
        flash("获取游戏列表失败", "error")
        return render_template("games.html", games=[])


@games_bp.route("/games/new", methods=["GET", "POST"])
def new_game():
    """Create a new game"""
    if request.method == "POST":
        gid = request.form.get("gid", "").strip()
        name = request.form.get("name", "").strip()
        ods_type = request.form.get("ods_type", "").strip()

        if not gid or not name or not ods_type:
            flash("请填写所有必填字段", "error")
            return render_template("game_form.html")

        ods_db = ODSDatabase.get_db_name(ods_type)
        if ods_type not in ["domestic", "overseas"]:
            flash("请选择有效的ODS数据库类型", "error")
            return render_template("game_form.html")

        try:
            # Check if game ID already exists
            existing = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
            if existing:
                flash(f"游戏ID {gid} 已存在，请使用其他ID", "error")
                return render_template("game_form.html")

            execute_write(
                "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)", (gid, name, ods_db)
            )
            clear_game_cache()  # Clear game cache after creation
            logger.info(f"Game created: {name} (GID: {gid}, ODS: {ods_db})")
            flash(f"游戏 {name} 创建成功", "success")
            return redirect(url_for("games.list_games"))
        except sqlite3.IntegrityError as e:
            logger.error(f"IntegrityError creating game: {e}")
            flash(f"游戏ID {gid} 已存在", "error")
            return render_template("game_form.html")
        except Exception as e:
            logger.error(f"Error creating game: {e}")
            flash("创建游戏失败", "error")
            return render_template("game_form.html")

    return render_template("game_form.html")


@games_bp.route("/games/<int:id>/edit", methods=["GET", "POST"])
def edit_game(id):
    """Edit an existing game using business GID"""
    game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (id,))

    if not game:
        flash("游戏不存在", "error")
        return redirect(url_for("games.list_games"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        ods_type = request.form.get("ods_type", "").strip()

        if not name or not ods_type:
            flash("请填写所有必填字段", "error")
            return render_template("game_form.html", game=game, edit_mode=True)

        ods_db = ODSDatabase.get_db_name(ods_type)
        if ods_type not in ["domestic", "overseas"]:
            flash("请选择有效的ODS数据库类型", "error")
            return render_template("game_form.html", game=game, edit_mode=True)

        try:
            execute_write(
                "UPDATE games SET name = ?, ods_db = ?, updated_at = CURRENT_TIMESTAMP WHERE gid = ?",
                (name, ods_db, id),
            )
            clear_game_cache()  # Clear game cache after update
            logger.info(f"Game updated: {name} (GID: {id}, ODS: {ods_db})")
            flash(f"游戏 {name} 更新成功", "success")
            return redirect(url_for("games.list_games"))
        except Exception as e:
            logger.error(f"Error editing game {id}: {e}")
            flash("更新游戏失败", "error")
            return render_template("game_form.html", game=game, edit_mode=True)

    return render_template("game_form.html", game=game, edit_mode=True)


@games_bp.route("/games/<int:id>/delete", methods=["POST"])
def delete_game(id):
    """Delete a game using business GID"""
    try:
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (id,))

        if game:
            execute_write("DELETE FROM games WHERE gid = ?", (id,))
            clear_game_cache()  # Clear game cache after deletion
            logger.info(f"Game deleted: {game['name']} (GID: {id})")
            flash(f'游戏 {game["name"]} 已删除', "success")
        else:
            flash("游戏不存在", "error")
    except Exception as e:
        logger.error(f"Error deleting game {id}: {e}")
        flash("删除游戏失败", "error")

    return redirect(url_for("games.list_games"))
