#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Events Management Module
Handles all event-related operations including Excel import
"""

import os
import sqlite3
import time
from typing import Optional, List, Dict, Any, Tuple

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
import pandas as pd

from backend.core.database import get_db_connection, DB_PATH
from backend.core.config import UPLOAD_DIR
from backend.core.logging import get_logger
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    execute_write,
    success_response,
    error_response,
    validate_json_request,
    validate_game_exists,
    find_column_by_keywords,
    get_event_with_game_info,
    get_active_parameters,
    json_success_response,
    json_error_response,
    db_transaction,
)
from backend.core.cache.cache_system import clear_event_cache, clear_game_cache, cache_result
from backend.core.config import CacheConfig
from backend.core.exceptions import DatabaseError, ValidationError, NotFoundError
from backend.middleware.validation import validate_event_input, log_request_details

logger = get_logger(__name__)

events_bp = Blueprint("events", __name__)


# ==================== Event Builder Pattern ==================== #

from dataclasses import dataclass, field
from typing import List


@dataclass
class EventData:
    """事件数据类"""

    game_gid: int
    event_name: str
    event_name_cn: str
    category_id: int
    source_table: str
    target_table: str
    include_in_common_params: int = 0
    parameters: List[Dict[str, Any]] = field(default_factory=list)


class EventBuilder:
    """
    事件建造者类

    使用建造者模式构建事件数据，降低复杂度，提高可读性
    """

    def __init__(self):
        """初始化建造者"""
        self.game_gid: Optional[int] = None
        self.ods_db: Optional[str] = None
        self.event_name: Optional[str] = None
        self.event_name_cn: Optional[str] = None
        self.category_id: Optional[int] = None
        self.include_in_common_params: int = 0
        self.parameters: List[Dict[str, Any]] = []

    def set_game(self, game_gid: int, ods_db: str) -> "EventBuilder":
        """
        设置游戏信息

        Args:
            game_gid: 游戏GID
            ods_db: ODS数据库

        Returns:
            self (fluent interface)
        """
        self.game_gid = game_gid
        self.ods_db = ods_db
        return self

    def set_names(self, event_name: str, event_name_cn: str) -> "EventBuilder":
        """
        设置事件名称

        Args:
            event_name: 事件英文名
            event_name_cn: 事件中文名

        Returns:
            self (fluent interface)
        """
        self.event_name = event_name
        self.event_name_cn = event_name_cn
        return self

    def set_category(self, category_id: int) -> "EventBuilder":
        """
        设置事件分类

        Args:
            category_id: 分类ID

        Returns:
            self (fluent interface)
        """
        self.category_id = category_id
        return self

    def set_parameters(self, parameters: List[Dict[str, Any]]) -> "EventBuilder":
        """
        设置事件参数

        Args:
            parameters: 参数列表

        Returns:
            self (fluent interface)
        """
        self.parameters = parameters
        return self

    def set_include_in_common(self, include: bool) -> "EventBuilder":
        """
        设置是否包含在公共参数中

        Args:
            include: 是否包含

        Returns:
            self (fluent interface)
        """
        self.include_in_common_params = 1 if include else 0
        return self

    def build(self) -> EventData:
        """
        构建事件数据

        Returns:
            EventData 对象

        Raises:
            ValueError: 缺少必需字段
        """
        # 验证必需字段
        if not self.game_gid:
            raise ValueError("game_gid is required")
        if not self.event_name:
            raise ValueError("event_name is required")
        if not self.event_name_cn:
            raise ValueError("event_name_cn is required")
        if not self.category_id:
            raise ValueError("category_id is required")

        # 计算源表名
        source_table = f"{self.ods_db}.ods_{self.game_gid}_all_view"

        # 确定DWD库前缀
        dwd_prefix = "ieu_cdm" if self.ods_db == "ieu_ods" else self.ods_db

        # 清理事件名中的特殊字符
        clean_name = self.event_name.replace(".", "_")

        # 计算目标表名
        target_table = f"{dwd_prefix}.v_dwd_{self.game_gid}_{clean_name}_di"

        return EventData(
            game_gid=self.game_gid,
            event_name=self.event_name,
            event_name_cn=self.event_name_cn,
            category_id=self.category_id,
            source_table=source_table,
            target_table=target_table,
            include_in_common_params=self.include_in_common_params,
            parameters=self.parameters,
        )


# ==================== Event Routes ==================== #


def _parse_event_parameters(request_data) -> List[Dict[str, Any]]:
    """
    从表单数据解析事件参数

    Args:
        request_data: Flask request.form 数据

    Returns:
        参数列表
    """
    param_names = request_data.getlist("param_name[]")
    param_names_cn = request_data.getlist("param_name_cn[]")
    param_types = request_data.getlist("param_type[]")
    param_descriptions = request_data.getlist("param_description[]")

    parameters = []
    for i, name in enumerate(param_names):
        if name.strip():
            parameters.append(
                {
                    "name": name.strip(),
                    "name_cn": param_names_cn[i] if i < len(param_names_cn) else "",
                    "type": (
                        int(param_types[i])
                        if i < len(param_types) and param_types[i].isdigit()
                        else 1
                    ),
                    "description": param_descriptions[i] if i < len(param_descriptions) else "",
                }
            )

    return parameters


def _build_event_from_form(request_data) -> EventData:
    """
    使用EventBuilder从表单数据构建事件

    Args:
        request_data: Flask request.form 数据

    Returns:
        EventData 对象

    Raises:
        ValueError: 缺少必需字段
    """
    # 提取并验证表单数据
    game_gid = request_data.get("game_gid", "").strip()
    event_name = request_data.get("event_name", "").strip()
    event_name_cn = request_data.get("event_name_cn", "").strip()
    category_id = request_data.get("category_id", "").strip()

    # 基础验证
    if not game_gid:
        raise ValueError("请选择游戏")
    if not event_name:
        raise ValueError("请输入事件英文名")
    if not event_name_cn:
        raise ValueError("请输入事件中文名")
    if not category_id:
        raise ValueError("请选择事件分类")

    # 获取游戏信息
    game = fetch_one_as_dict("SELECT * FROM games WHERE id = ?", (game_gid,))
    if not game:
        raise ValueError("游戏不存在")

    # 解析参数
    parameters = _parse_event_parameters(request_data)
    if not parameters:
        raise ValueError("请至少添加一个参数")

    # 使用EventBuilder构建事件数据
    include_in_common = bool(request_data.get("include_in_common_params"))

    return (
        EventBuilder()
        .set_game(int(game["gid"]), game["ods_db"])
        .set_names(event_name, event_name_cn)
        .set_category(int(category_id))
        .set_parameters(parameters)
        .set_include_in_common(include_in_common)
        .build()
    )


# ==============================================================================
# Cached Data Access Functions
# ==============================================================================


@cache_result(
    "events:list_by_game:{game_gid}:{page}:{per_page}", timeout=CacheConfig.CACHE_TIMEOUT_EVENTS
)
def get_events_paginated_cached(game_gid: int, page: int, per_page: int) -> List[Dict[str, Any]]:
    """
    **性能优化**: Cached function to get paginated events with parameter counts

    Args:
        game_gid: Game ID to filter events
        page: Page number (1-indexed)
        per_page: Number of events per page

    Returns:
        List of event dictionaries with param_count included
    """
    offset = (page - 1) * per_page

    return fetch_all_as_dict(
        """
        SELECT
            le.*,
            g.gid, g.name as game_name, g.ods_db,
            ec.name as category_name,
            COALESCE(COUNT(DISTINCT ep.id), 0) as param_count
        FROM log_events le
        LEFT JOIN games g ON le.game_gid = g.gid
        LEFT JOIN event_categories ec ON le.category_id = ec.id
        LEFT JOIN event_params ep ON le.id = ep.event_id AND ep.is_active = 1
        WHERE le.game_gid = ?
        GROUP BY le.id
        ORDER BY le.id DESC
        LIMIT ? OFFSET ?
    """,
        (game_gid, per_page, offset),
    )


@cache_result("params:active_by_event:{event_id}", timeout=CacheConfig.CACHE_TIMEOUT_PARAMS)
def get_active_parameters_cached(event_id: int) -> List[Dict[str, Any]]:
    """
    **性能优化**: Cached function to get active parameters for an event

    Args:
        event_id: Event ID

    Returns:
        List of active parameter dictionaries
    """
    return fetch_all_as_dict(
        """
        SELECT
            ep.*,
            pt.template_name,
            pt.display_name as type_display_name
        FROM event_params ep
        LEFT JOIN param_templates pt ON ep.template_id = pt.id
        WHERE ep.event_id = ? AND ep.is_active = 1
        ORDER BY ep.id
    """,
        (event_id,),
    )


@cache_result("events:count_by_game:{game_gid}", timeout=CacheConfig.CACHE_TIMEOUT_EVENTS)
def get_events_count_cached(game_gid: int) -> int:
    """
    **性能优化**: Cached function to get event count for a game

    Args:
        game_gid: Game ID

    Returns:
        Number of events for the game
    """
    result = fetch_one_as_dict(
        """
        SELECT COUNT(*) as total
        FROM log_events
        WHERE game_gid = ?
    """,
        (game_gid,),
    )
    return result["total"] if result else 0


@events_bp.route("/events")
def list_events():
    """
    List all log events with pagination

    **Game Context Required**: This page requires a game to be selected first.
    All operations must be performed within the context of a specific game.
    """
    # Get game_gid from query parameter or session
    game_gid = request.args.get("game_gid", type=int) or session.get("current_game_gid")

    # Pagination parameters
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page not in [10, 20, 50, 100]:
        per_page = 20

    offset = (page - 1) * per_page

    # Check if there are any games in database
    result = fetch_one_as_dict("SELECT COUNT(*) as count FROM games")
    games_exist = result["count"] > 0 if result else False

    if not games_exist:
        flash("请先创建游戏", "error")
        return redirect(url_for("games.list_games"))

    # **游戏上下文强制验证**: 必须选择游戏后才能查看事件
    if not game_gid:
        flash("请先选择游戏", "error")
        return redirect(url_for("games.list_games"))

    # Set session for game context
    session["current_game_gid"] = game_gid

    # **性能优化**: Use cached function for event count
    total_events = get_events_count_cached(game_gid)
    total_pages = max(1, (total_events + per_page - 1) // per_page)

    # **游戏上下文过滤**: 只显示当前游戏的事件 with pagination
    # **性能优化**: Use cached function to get events with parameter counts
    events = get_events_paginated_cached(game_gid, page, per_page)

    # Get current game info
    current_game = fetch_one_as_dict("SELECT id, name, gid FROM games WHERE id = ?", (game_gid,))

    return render_template(
        "events.html",
        events=events,
        selected_game_id=game_gid,
        current_game=current_game,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        total_events=total_events,
    )


@events_bp.route("/events/new", methods=["GET", "POST"])
@validate_event_input
@log_request_details
def new_event():
    """Create a new log event"""
    from backend.core.common import (
        get_reference_data,
        validate_form_fields,
        parse_form_list_fields,
        generate_dwd_table_names,
        clear_entity_caches,
    )

    # GET请求：获取参考数据
    ref_data = get_reference_data(["games", "event_categories"])
    games, categories = ref_data["games"], ref_data["event_categories"]

    if request.method == "POST":
        # 1. 表单验证（使用通用函数）
        field_defs = [
            {"name": "game_gid", "required": True, "alias": "游戏ID"},
            {"name": "event_name", "required": True, "alias": "事件名"},
            {"name": "event_name_cn", "required": True, "alias": "中文名"},
            {"name": "category_id", "required": True, "alias": "分类"},
        ]

        is_valid, form_data, error = validate_form_fields(field_defs)
        if not is_valid:
            flash(error, "error")
            return render_template("event_form.html", games=games, categories=categories)

        game_gid, event_name, event_name_cn, category_id = (
            form_data["game_gid"],
            form_data["event_name"],
            form_data["event_name_cn"],
            form_data["category_id"],
        )

        # 2. 验证游戏存在
        game = fetch_one_as_dict("SELECT * FROM games WHERE id = ?", (game_gid,))
        if not game:
            flash("游戏不存在", "error")
            return render_template("event_form.html", games=games, categories=categories)

        # 3. 生成表名（使用通用函数）
        tables = generate_dwd_table_names(game, event_name)
        source_table, target_table = tables["source_table"], tables["target_table"]

        # 4. 解析参数（使用通用函数）
        param_fields = parse_form_list_fields(
            ["param_name", "param_name_cn", "param_type", "param_description"]
        )

        # 验证至少有一个参数
        valid_params = [name for name in param_fields["param_name"] if name.strip()]
        if not valid_params:
            flash("请至少添加一个参数", "error")
            return render_template("event_form.html", games=games, categories=categories)

        # 5. 事务处理：创建事件和参数
        try:
            include_in_common = 1 if request.form.get("include_in_common_params") else 0

            with db_transaction() as conn:
                # 插入事件
                cursor = conn.execute(
                    """INSERT INTO log_events
                           (game_gid, event_name, event_name_cn, category_id, source_table, target_table, include_in_common_params)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        game_gid,
                        event_name,
                        event_name_cn,
                        category_id,
                        source_table,
                        target_table,
                        include_in_common,
                    ),
                )
                event_id = cursor.lastrowid

                # 插入参数
                for i, name in enumerate(param_fields["param_name"]):
                    if name.strip():
                        conn.execute(
                            """INSERT INTO event_params
                                   (event_id, param_name, param_name_cn, template_id, param_description, is_active, version)
                                   VALUES (?, ?, ?, ?, ?, 1, 1)""",
                            (
                                event_id,
                                name.strip(),
                                (
                                    param_fields["param_name_cn"][i]
                                    if i < len(param_fields["param_name_cn"])
                                    else ""
                                ),
                                (
                                    int(param_fields["param_type"][i])
                                    if i < len(param_fields["param_type"])
                                    and param_fields["param_type"][i].isdigit()
                                    else 1
                                ),
                                (
                                    param_fields["param_description"][i]
                                    if i < len(param_fields["param_description"])
                                    else ""
                                ),
                            ),
                        )

            # 6. 清理缓存（使用通用函数）
            clear_entity_caches("event", event_id, game_gid=game_gid)

            logger.info(
                f"Successfully created event {event_id} with {len(valid_params)} parameters"
            )
            flash(f"日志事件 {event_name_cn} 创建成功", "success")
            return redirect(url_for("events.view_event", event_id=event_id))

        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error creating event: {e}")
            flash("创建失败: 数据完整性错误（可能是重复的事件名）", "error")
            return render_template("event_form.html", games=games, categories=categories)
        except sqlite3.Error as e:
            logger.error(f"Database error creating event: {e}", exc_info=True)
            flash("创建失败: 数据库错误，请稍后重试", "error")
            return render_template("event_form.html", games=games, categories=categories)
        except Exception as e:
            logger.error(f"Unexpected error creating event: {e}", exc_info=True)
            flash("创建失败: 系统错误，请联系管理员", "error")
            return render_template("event_form.html", games=games, categories=categories)

    return render_template("event_form.html", games=games, categories=categories)


@events_bp.route("/events/<int:id>")
def view_event(id):
    """View details of a specific log event"""
    # Use helper function to get event with game and category info
    event = get_event_with_game_info(id)

    if not event:
        flash("日志事件不存在", "error")
        return redirect(url_for("events.list_events"))

    # Use helper function to get active parameters
    parameters = get_active_parameters(id)

    return render_template("event_detail.html", event=event, parameters=parameters)


@events_bp.route("/events/<int:id>/edit", methods=["GET", "POST"])
def edit_event(id):
    """Edit an existing log event"""
    from backend.core.common import get_reference_data, validate_form_fields, clear_entity_caches

    # Use helper function to get event with game and category info
    event = get_event_with_game_info(id)

    # GET请求：获取参考数据
    ref_data = get_reference_data(["games", "event_categories"])
    games, categories = ref_data["games"], ref_data["event_categories"]
    parameters = get_active_parameters(id)

    if not event:
        flash("日志事件不存在", "error")
        return redirect(url_for("events.list_events"))

    if request.method == "POST":
        # 表单验证（使用通用函数）
        field_defs = [
            {"name": "event_name_cn", "required": True, "alias": "中文名"},
            {"name": "category_id", "required": True, "alias": "分类"},
        ]

        is_valid, form_data, error = validate_form_fields(field_defs)
        if not is_valid:
            flash(error, "error")
            return render_template(
                "event_form.html",
                event=event,
                games=games,
                categories=categories,
                parameters=parameters,
                edit_mode=True,
            )

        event_name_cn, category_id = form_data["event_name_cn"], form_data["category_id"]

        # 更新事件
        include_in_common = 1 if request.form.get("include_in_common_params") else 0

        execute_write(
            "UPDATE log_events SET event_name_cn = ?, category_id = ?, include_in_common_params = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (event_name_cn, category_id, include_in_common, id),
        )

        # 清理缓存（使用通用函数）
        clear_entity_caches("event", id, game_gid=event["game_gid"])

        flash(f"日志事件 {event_name_cn} 更新成功", "success")
        return redirect(url_for("events.view_event", id=id))

    return render_template(
        "event_form.html",
        event=event,
        games=games,
        categories=categories,
        parameters=parameters,
        edit_mode=True,
    )


@events_bp.route("/events/<int:id>/delete", methods=["POST"])
def delete_event(id):
    """Delete a log event"""
    from backend.core.common import clear_entity_caches

    event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (id,))

    if event:
        # Delete parameters and category relations first
        execute_write("DELETE FROM event_params WHERE event_id = ?", (id,))
        execute_write("DELETE FROM event_common_params WHERE event_id = ?", (id,))
        execute_write("DELETE FROM event_category_relations WHERE event_id = ?", (id,))
        execute_write("DELETE FROM log_events WHERE id = ?", (id,))

        # 清理缓存（使用通用函数）
        clear_entity_caches("event", id, game_gid=event["game_gid"])

        flash(f'日志事件 {event["event_name_cn"]} 已删除', "success")
    else:
        flash("日志事件不存在", "error")

    return redirect(url_for("events.list_events"))


def compare_event_with_existing(event_data: Dict[str, Any], game_gid: int) -> Dict[str, Any]:
    """比较导入的事件与已存在的事件是否有差异

    Args:
        event_data: 导入的事件数据
        game_gid: 游戏ID

    Returns:
        Dict: {
            'exists': bool,           # 事件是否已存在
            'has_difference': bool,   # 是否有差异
            'is_identical': bool,     # 是否完全相同
            'differences': list,      # 差异详情
            'existing_event': dict    # 已存在的事件数据
        }
    """
    # 查询已存在的事件
    existing = fetch_one_as_dict(
        """
        SELECT le.id, le.event_name, le.event_name_cn, le.category_id,
               ec.name as category_name
        FROM log_events le
        LEFT JOIN event_categories ec ON le.category_id = ec.id
        WHERE le.game_gid = ? AND le.event_name = ?
    """,
        (game_gid, event_data["event_name"]),
    )

    if not existing:
        return {
            "exists": False,
            "has_difference": True,
            "is_identical": False,
            "differences": [],
            "existing_event": None,
        }

    differences = []

    # 比较 event_name_cn
    if existing["event_name_cn"] != event_data.get("event_name_cn"):
        differences.append(
            {
                "field": "event_name_cn",
                "old": existing["event_name_cn"],
                "new": event_data.get("event_name_cn"),
            }
        )

    # 获取已存在的参数
    existing_params = fetch_all_as_dict(
        """
        SELECT ep.param_name, ep.param_name_cn, pt.template_name as param_type, ep.param_description
        FROM event_params ep
        JOIN param_templates pt ON ep.template_id = pt.id
        WHERE ep.event_id = ? AND ep.is_active = 1
    """,
        (existing["id"],),
    )

    existing_params_dict = {p["param_name"]: p for p in existing_params}

    # 比较参数
    imported_params = event_data.get("parameters", [])
    imported_params_dict = {p["param_name"]: p for p in imported_params}

    # 检查新增或修改的参数
    for param_name, imported_param in imported_params_dict.items():
        if param_name not in existing_params_dict:
            differences.append(
                {
                    "field": "parameter",
                    "param_name": param_name,
                    "type": "new",
                    "data": imported_param,
                }
            )
        else:
            existing_param = existing_params_dict[param_name]
            # 比较参数的各个字段
            if (
                existing_param["param_name_cn"] != imported_param.get("param_name_cn")
                or existing_param["param_type"] != imported_param.get("param_type")
                or existing_param["param_description"]
                != imported_param.get("param_description", "")
            ):

                differences.append(
                    {
                        "field": "parameter",
                        "param_name": param_name,
                        "type": "modified",
                        "old": existing_param,
                        "new": imported_param,
                    }
                )

    # 检查删除的参数（导入文件中缺少但数据库中存在的参数）
    for param_name in existing_params_dict:
        if param_name not in imported_params_dict:
            differences.append(
                {
                    "field": "parameter",
                    "param_name": param_name,
                    "type": "deleted",
                    "data": existing_params_dict[param_name],
                }
            )

    return {
        "exists": True,
        "has_difference": len(differences) > 0,
        "is_identical": len(differences) == 0,
        "differences": differences,
        "existing_event": existing,
    }


# ==============================================================================
# Excel Importer Class (Refactored)
# ==============================================================================


class ExcelImporter:
    """Excel事件导入器（简化版）

    将Excel文件解析、验证、导入逻辑封装在一个类中，
    提高可测试性和可维护性。
    """

    def __init__(self, file, game_gid, form_data):
        """初始化导入器

        Args:
            file: 上传的文件对象
            game_gid: 游戏GID
            form_data: 表单数据（包含列映射等）
        """
        self.file = file
        self.game_gid = game_gid
        self.form_data = form_data
        self.events_data = {}

    def validate(self):
        """验证文件和游戏上下文

        Returns:
            Tuple[bool, str]: (is_valid, error_message)

        Raises:
            ValueError: 如果验证失败
        """
        # 验证文件
        if not self.file or self.file.filename == "":
            raise ValueError("没有选择文件")

        if not self.file.filename.endswith((".xlsx", ".xls")):
            raise ValueError("请上传Excel文件 (.xlsx 或 .xls)")

        # 验证游戏上下文
        if not self.game_gid:
            raise ValueError("请选择游戏")

        return True, ""

    def parse(self):
        """解析Excel文件并返回事件数据

        Returns:
            Dict: 事件数据字典

        Raises:
            ValueError: 如果Excel格式无效
            Exception: 如果解析失败
        """
        # 1. 保存文件
        filepath = self._save_file()

        # 2. 读取Excel
        df = pd.read_excel(filepath, engine="openpyxl")

        # 3. 获取行号配置
        header_row = int(self.form_data.get("header_row", 0))
        data_start_row = int(self.form_data.get("data_start_row", 1))

        # 4. 验证行号
        if header_row < 0 or data_start_row < 0:
            raise ValueError("表头行数和数据起始行必须大于等于0（0-based）")

        # 5. 检测列
        columns = self._detect_columns(df, header_row)

        # 6. 解析数据行
        self.events_data = self._parse_data_rows(df, columns, data_start_row)

        return self.events_data

    def _save_file(self):
        """保存上传的文件到临时目录

        Returns:
            str: 保存的文件路径
        """
        timestamp = int(time.time())
        ext = os.path.splitext(self.file.filename)[1] if self.file.filename else ".xlsx"
        filename = f"import_{timestamp}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        self.file.save(filepath)
        return filepath

    def _detect_columns(self, df, header_row):
        """自动检测列索引

        Args:
            df: DataFrame对象
            header_row: 表头行号（0-based）

        Returns:
            Dict: 列索引映射
        """
        # 从表单获取列索引
        columns = {
            "event_name": self.form_data.get("event_name_col"),
            "event_name_cn": self.form_data.get("event_name_cn_col"),
            "param_name": self.form_data.get("param_name_col"),
            "param_name_cn": self.form_data.get("param_name_cn_col"),
            "param_type": self.form_data.get("param_type_col"),
            "param_description": self.form_data.get("param_description_col"),
        }

        # 如果表头行存在，尝试自动检测
        if header_row < len(df):
            headers = [str(cell).strip() for cell in df.iloc[header_row].values]

            # 自动检测事件名列
            if not columns["event_name"]:
                columns["event_name"] = find_column_by_keywords(
                    headers, ["事件标识", "事件名", "event", "标识"]
                )

            # 自动检测事件中文名列
            if not columns["event_name_cn"]:
                columns["event_name_cn"] = find_column_by_keywords(
                    headers, ["事件名称", "事件中文名", "名称", "name", "中文名"]
                )

            # 自动检测参数名列
            if not columns["param_name"]:
                columns["param_name"] = find_column_by_keywords(
                    headers, ["参数标识", "参数名", "param", "参数"]
                )

            # 自动检测参数中文名列
            if not columns["param_name_cn"]:
                columns["param_name_cn"] = find_column_by_keywords(
                    headers, ["参数名称", "参数中文名", "参数"]
                )

            # 自动检测参数类型列
            if not columns["param_type"]:
                columns["param_type"] = find_column_by_keywords(
                    headers, ["数据类型", "类型", "type", "datatype"]
                )

            # 自动检测参数描述列
            if not columns["param_description"]:
                columns["param_description"] = find_column_by_keywords(
                    headers, ["参数描述", "描述", "description", "备注"]
                )

        # 转换为整数（如果找到）
        for key in columns:
            columns[key] = int(columns[key]) if columns[key] and columns[key] != "" else None

        return columns

    def _parse_data_rows(self, df, columns, data_start_row):
        """解析数据行

        Args:
            df: DataFrame对象
            columns: 列索引映射
            data_start_row: 数据起始行号（0-based）

        Returns:
            Dict: 事件数据字典
        """
        events_data = {}

        for idx in range(data_start_row, len(df)):
            row = df.iloc[idx].values

            # 提取事件名
            event_name = self._get_cell_value(row, columns["event_name"])
            if not event_name:
                continue

            # 提取事件中文名
            event_name_cn = self._get_cell_value(row, columns["event_name_cn"]) or event_name

            # 初始化事件数据
            if event_name not in events_data:
                events_data[event_name] = {"event_name_cn": event_name_cn, "parameters": []}

            # 提取参数名
            param_name = self._get_cell_value(row, columns["param_name"])
            if param_name:
                events_data[event_name]["parameters"].append(
                    {
                        "param_name": param_name,
                        "param_name_cn": self._get_cell_value(row, columns["param_name_cn"]) or "",
                        "param_type": self._get_cell_value(row, columns["param_type"]) or "string",
                        "param_description": self._get_cell_value(row, columns["param_description"])
                        or "",
                    }
                )

        return events_data

    def _get_cell_value(self, row, col_index):
        """安全获取单元格值

        Args:
            row: 数据行
            col_index: 列索引

        Returns:
            str: 单元格值（去除首尾空格）
        """
        if col_index is not None and col_index < len(row):
            return str(row[col_index]).strip()
        return ""

    def compare_with_existing(self):
        """与现有事件比较

        Returns:
            Tuple[List, List, int]: (events_list, duplicates, identical_count)

            - events_list: 事件列表（包含重复标记）
            - duplicates: 重复事件详情
            - identical_count: 完全相同的事件数量
        """
        duplicates = []
        events_list = []
        identical_count = 0

        for event_name, data in self.events_data.items():
            # 使用比较函数检查差异
            comparison = compare_event_with_existing(
                {
                    "event_name": event_name,
                    "event_name_cn": data["event_name_cn"],
                    "parameters": data["parameters"],
                },
                self.game_gid,
            )

            # 跳过完全相同的事件
            if comparison["is_identical"]:
                identical_count += 1
                logger.info(f"Skipping identical event: {event_name}")
                continue

            # 事件是新的或有差异
            has_duplicate = comparison["exists"]
            has_difference = comparison["has_difference"]

            if has_duplicate:
                if has_difference:
                    # 事件存在但有差异
                    duplicates.append(
                        {
                            "type": "事件变更",
                            "message": f"事件 {event_name} 已存在但有变更",
                            "differences": comparison["differences"],
                        }
                    )
                    data["has_duplicate"] = True
                    data["has_difference"] = True
                else:
                    data["has_duplicate"] = True
                    data["has_difference"] = False
            else:
                # 新事件
                data["has_duplicate"] = False
                data["has_difference"] = False

            data["category"] = "未设置"
            data["category_id"] = None
            data["param_count"] = len(data["parameters"])

            # 添加到事件列表
            events_list.append(
                {
                    "event_name": event_name,
                    "event_name_cn": data["event_name_cn"],
                    "has_duplicate": data["has_duplicate"],
                    "has_difference": data.get("has_difference", False),
                    "selected": False,
                    "category": data["category"],
                    "param_count": data["param_count"],
                    "parameters": data["parameters"],
                }
            )

        return events_list, duplicates, identical_count


@events_bp.route("/events/import", methods=["GET", "POST"])
def import_events_from_excel():
    """
    Import events from Excel file into the database.

    This function handles batch import of event definitions from Excel files,
    validating data integrity and creating corresponding database records.

    **REFACTORED**: Now uses ExcelImporter class for better maintainability.

    Functionality:
        1. Displays import form on GET request
        2. Validates uploaded file on POST request
        3. Parses Excel file using ExcelImporter
        4. Validates event data against schema
        5. Compares with existing events
        6. Returns JSON response with event data

    Expected Excel Format:
        Column headers should include:
        - event_name: Event identifier (e.g., 'login')
        - event_name_cn: Chinese display name
        - parameter_name: Parameter name
        - parameter_type: Parameter data type
        - (Optional) parameter_description: Description

    Args:
        None (uses Flask request context)

    Returns:
        On GET: Renders import_events.html template
        On POST: JSON response with events list

    Request Parameters:
        - game_gid (int): Game GID to associate events with
        - file (File): Excel file to import (.xlsx or .xls)

    Raises:
        ValueError: If Excel format is invalid
        Exception: If database operation fails

    Flash Messages:
        - Error: Various error messages for validation failures

    Note:
        This function requires proper game_gid context to ensure data
        is associated with the correct game. All imported events will
        have their game_gid set automatically.
    """
    # GET请求：显示导入表单
    if request.method == "GET":
        games = fetch_all_as_dict("SELECT * FROM games ORDER BY name")
        categories = fetch_all_as_dict("SELECT * FROM event_categories ORDER BY name")
        selected_game_id = request.args.get("game_gid", type=int)
        if not selected_game_id and games:
            selected_game_id = games[0]["id"]
        return render_template(
            "import_events.html",
            games=games,
            categories=categories,
            selected_game_id=selected_game_id,
        )

    # POST请求：处理文件上传
    try:
        # 验证文件存在
        if "file" not in request.files:
            flash("没有上传文件", "error")
            return redirect(url_for("events.import_events_from_excel"))

        file = request.files["file"]
        game_gid = request.form.get("game_gid")

        # 使用导入器处理Excel
        importer = ExcelImporter(file, game_gid, request.form)

        # 验证
        try:
            importer.validate()
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("events.import_events_from_excel"))

        # 解析Excel
        events_data = importer.parse()

        # 比较现有事件
        events_list, duplicates, identical_count = importer.compare_with_existing()

        # 返回结果
        return json_success_response(
            data={
                "events": events_list,
                "duplicates": duplicates,
                "total_params": sum(len(v["parameters"]) for v in events_data.values()),
                "identical_count": identical_count,
                "total_parsed": len(events_data),
            }
        )

    except Exception as e:
        logger.error(f"Excel import error: {e}", exc_info=True)
        flash(f"导入失败: {str(e)}", "error")
        return redirect(url_for("events.import_events_from_excel"))


@events_bp.route("/search", methods=["GET"])
def global_search():
    """Global search page"""
    return render_template("search.html")


@events_bp.route("/parameters/analysis", methods=["GET"])
def parameter_analysis():
    """Parameter quality analysis page"""
    return render_template("parameter_analysis.html")


@events_bp.route("/parameters/compare", methods=["GET"])
def parameter_compare():
    """Parameter comparison page"""
    return render_template("parameter_compare.html")


@events_bp.route("/parameters/dashboard", methods=["GET"])
def parameter_dashboard():
    """Parameter statistics dashboard page"""
    return render_template("parameter_dashboard.html")


@events_bp.route("/parameters/network", methods=["GET"])
def parameter_network():
    """Parameter relationship network page"""
    return render_template("parameter_network.html")


# REMOVED: Quick actions page - functionality redundant with homepage and event list
# @events_bp.route('/quick-actions', methods=['GET'])
# def quick_actions():
#     """Quick actions center page"""
#     return render_template('quick_actions.html')


@events_bp.route("/parameters/history", methods=["GET"])
def parameter_history():
    """Parameter change history page"""
    return render_template("parameter_history.html")


@events_bp.route("/api-docs", methods=["GET"])
def api_docs():
    """API documentation page"""
    return render_template("api_docs.html")


@events_bp.route("/parameters/usage", methods=["GET"])
def parameter_usage():
    """Parameter usage analysis page"""
    return render_template("parameter_usage.html")


@events_bp.route("/parameters/manage", methods=["GET"])
def manage_parameters():
    """Comprehensive parameter management page"""
    try:
        games = fetch_all_as_dict("SELECT * FROM games ORDER BY name")
        categories = fetch_all_as_dict("SELECT * FROM event_categories ORDER BY name")
        return render_template("parameters.html", games=games, categories=categories)
    except Exception as e:
        logger.error(f"Parameter management page error: {e}")
        flash(f"加载页面失败: {str(e)}", "error")
        return redirect(url_for("events.list_events"))


@events_bp.route("/parameters/enhanced", methods=["GET"])
def manage_parameters_enhanced():
    """Enhanced parameter management page with type system"""
    try:
        games = fetch_all_as_dict("SELECT * FROM games ORDER BY name")
        categories = fetch_all_as_dict("SELECT * FROM event_categories ORDER BY name")
        return render_template("parameters_enhanced.html", games=games, categories=categories)
    except Exception as e:
        logger.error(f"Enhanced parameter management page error: {e}")
        flash(f"加载页面失败: {str(e)}", "error")
        return redirect(url_for("events.list_events"))


@events_bp.route("/validation/rules", methods=["GET"])
def validation_rules():
    """Validation rules management page"""
    try:
        games = fetch_all_as_dict("SELECT * FROM games ORDER BY name")
        categories = fetch_all_as_dict("SELECT * FROM event_categories ORDER BY name")
        return render_template("validation_rules.html", games=games, categories=categories)
    except Exception as e:
        logger.error(f"Validation rules page error: {e}")
        flash(f"加载页面失败: {str(e)}", "error")
        return redirect(url_for("index"))


@events_bp.route("/batch/operations", methods=["GET"])
def batch_operations():
    """Batch operations management page"""
    try:
        games = fetch_all_as_dict("SELECT * FROM games ORDER BY name")
        return render_template("batch_operations.html", games=games)
    except Exception as e:
        logger.error(f"Batch operations page error: {e}")
        flash(f"加载页面失败: {str(e)}", "error")
        return redirect(url_for("index"))
