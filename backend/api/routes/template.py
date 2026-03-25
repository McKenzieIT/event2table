#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Templates API Routes Module

提供HQL模板库相关的API端点:
- 模板分类查询
- 模板搜索
- 模板导入导出
- 热门模板查询
"""

import logging
from typing import Any, Dict, List

from flask import jsonify, request

# Import shared utilities
from backend.core.utils import json_error_response, json_success_response

# Import Service layer
from backend.services.template_service import TemplateService

# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/templates/categories", methods=["GET"])
def api_get_template_categories():
    """
    API: 获取所有模板分类

    Query Parameters:
        无

    Response:
    {
        "success": true,
        "data": [
            {
                "category": "登录事件",
                "template_count": 10,
                "total_usage": 150
            },
            ...
        ]
    }
    """
    try:
        service = TemplateService()
        categories = service.get_categories()

        return json_success_response(data=categories)

    except Exception as e:
        logger.error(f"Error fetching template categories: {e}")
        return json_error_response("Failed to fetch template categories", status_code=500)


@api_bp.route("/api/templates/categories/<category>/subcategories", methods=["GET"])
def api_get_template_subcategories(category: str):
    """
    API: 获取指定分类的子分类

    Path Parameters:
        category: 模板分类

    Response:
    {
        "success": true,
        "data": [
            "基础登录",
            "设备登录",
            ...
        ]
    }
    """
    try:
        service = TemplateService()
        subcategories = service.get_subcategories(category)

        return json_success_response(data=subcategories)

    except Exception as e:
        logger.error(f"Error fetching template subcategories: {e}")
        return json_error_response("Failed to fetch template subcategories", status_code=500)


@api_bp.route("/api/templates/search", methods=["POST"])
def api_search_templates():
    """
    API: 搜索模板

    Request Body:
    {
        "keyword": "login",           // 可选: 搜索关键词
        "category": "登录事件",       // 可选: 分类过滤
        "subcategory": "基础登录",    // 可选: 子分类过滤
        "tags": ["常用"],             // 可选: 标签过滤
        "game_gid": 10000147,         // 可选: 游戏GID过滤
        "limit": 50,                  // 可选: 返回数量限制 (默认50)
        "offset": 0                   // 可选: 偏移量 (默认0)
    }

    Response:
    {
        "success": true,
        "data": {
            "templates": [...],
            "total": 10,
            "limit": 50,
            "offset": 0
        }
    }
    """
    try:
        service = TemplateService()
        data = request.get_json() or {}

        keyword = data.get("keyword")
        category = data.get("category")
        subcategory = data.get("subcategory")
        tags = data.get("tags")
        game_gid = data.get("game_gid")
        limit = data.get("limit", 50)
        offset = data.get("offset", 0)

        # 验证参数
        if limit < 1 or limit > 100:
            return json_error_response("limit must be between 1 and 100", status_code=400)
        if offset < 0:
            return json_error_response("offset must be non-negative", status_code=400)

        result = service.search_templates(
            keyword=keyword,
            category=category,
            subcategory=subcategory,
            tags=tags,
            game_gid=game_gid,
            limit=limit,
            offset=offset,
        )

        return json_success_response(data=result)

    except Exception as e:
        logger.error(f"Error searching templates: {e}")
        return json_error_response("Failed to search templates", status_code=500)


@api_bp.route("/api/templates/popular", methods=["GET"])
def api_get_popular_templates():
    """
    API: 获取热门模板

    Query Parameters:
        limit: 返回数量 (默认10)

    Response:
    {
        "success": true,
        "data": [...]
    }
    """
    try:
        service = TemplateService()
        limit = request.args.get("limit", 10, type=int)

        # 验证参数
        if limit < 1 or limit > 50:
            limit = 10

        templates = service.get_popular_templates(limit=limit)

        return json_success_response(data=templates)

    except Exception as e:
        logger.error(f"Error fetching popular templates: {e}")
        return json_error_response("Failed to fetch popular templates", status_code=500)


@api_bp.route("/api/templates/<int:template_id>/export", methods=["GET"])
def api_export_template(template_id: int):
    """
    API: 导出模板

    Path Parameters:
        template_id: 模板ID

    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "name": "login_template",
            "display_name": "登录事件模板",
            "category": "登录事件",
            "hql_content": "...",
            "variables": {...},
            "tags": [...],
            ...
        }
    }
    """
    try:
        service = TemplateService()
        template = service.export_template(template_id)

        if not template:
            return json_error_response("Template not found", status_code=404)

        return json_success_response(data=template)

    except Exception as e:
        logger.error(f"Error exporting template {template_id}: {e}")
        return json_error_response("Failed to export template", status_code=500)


@api_bp.route("/api/templates/import", methods=["POST"])
def api_import_template():
    """
    API: 导入模板

    Request Body:
    {
        "name": "login_template",
        "display_name": "登录事件模板",
        "category": "登录事件",
        "subcategory": "基础登录",
        "hql_content": "...",
        "variables": {...},
        "description": "...",
        "tags": [...],
        "game_gid": 10000147,
        "is_featured": false,
        "is_system": false
    }

    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "name": "login_template",
            ...
        }
    }
    """
    try:
        service = TemplateService()
        data = request.get_json()

        if not data:
            return json_error_response("Request body is required", status_code=400)

        # 导入模板
        template = service.import_template(data)

        if not template:
            return json_error_response("Failed to import template", status_code=500)

        return json_success_response(data=template, message="Template imported successfully")

    except ValueError as e:
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error importing template: {e}")
        return json_error_response("Failed to import template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>", methods=["GET"])
def api_get_template(template_id: int):
    """
    API: 获取模板详情

    Path Parameters:
        template_id: 模板ID

    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "name": "login_template",
            ...
        }
    }
    """
    try:
        service = TemplateService()
        template = service.get_template_by_id(template_id)

        if not template:
            return json_error_response("Template not found", status_code=404)

        return json_success_response(data=template)

    except Exception as e:
        logger.error(f"Error fetching template {template_id}: {e}")
        return json_error_response("Failed to fetch template", status_code=500)


@api_bp.route("/api/templates/<int:template_id>/usage", methods=["POST"])
def api_increment_template_usage(template_id: int):
    """
    API: 增加模板使用次数

    Path Parameters:
        template_id: 模板ID

    Response:
    {
        "success": true,
        "data": {
            "template_id": 1,
            "usage_count": 10
        }
    }
    """
    try:
        service = TemplateService()
        success = service.increment_usage(template_id)

        if not success:
            return json_error_response("Template not found", status_code=404)

        # 获取更新后的模板
        template = service.get_template_by_id(template_id)

        return json_success_response(
            data={
                "template_id": template_id,
                "usage_count": template.get('usage_count', 0) if template else 0,
            }
        )

    except Exception as e:
        logger.error(f"Error incrementing template usage: {e}")
        return json_error_response("Failed to increment template usage", status_code=500)
