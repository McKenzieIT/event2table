#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Field Recommendation API Routes (智能字段推荐API路由)

提供智能字段推荐的API端点:
- POST /api/field-recommendations/recommend - 获取字段推荐
- GET /api/field-recommendations/patterns - 获取常用字段模式
- GET /api/field-recommendations/types - 获取字段类型推断

架构: API Layer (四层架构: API → Service → Repository → Entity)
"""

import logging

from flask import Blueprint, request

from backend.core.utils import json_error_response, json_success_response
from backend.services.field_recommendation_service import FieldRecommendationService

logger = logging.getLogger(__name__)

# 创建Blueprint
field_recommendation_bp = Blueprint("field_recommendations", __name__)


@field_recommendation_bp.route("/api/field-recommendations/recommend", methods=["POST"])
def api_get_recommendations():
    """
    API: 获取字段推荐

    支持多种推荐策略:
    1. 基于字段名称提示的相似度推荐
    2. 基于事件类型的推荐
    3. 基于游戏的全局常用字段推荐

    Request Body:
        {
            "game_gid": Optional[int],  # 游戏GID
            "event_name": Optional[str],  # 事件名称
            "field_name_hint": Optional[str],  # 字段名称提示
            "limit": Optional[int]  # 返回数量限制 (默认20)
        }

    Response:
        {
            "success": true,
            "data": [
                {
                    "param_name": str,
                    "param_name_cn": str,
                    "param_type": str,
                    "inferred_type": str,
                    "usage_count": int,
                    "event_count": int,
                    "is_common": bool,
                    "similarity_score": Optional[float],
                    "recommendation_reason": str
                }
            ],
            "message": "推荐成功"
        }

    Example:
        POST /api/field-recommendations/recommend
        {
            "game_gid": 10000147,
            "field_name_hint": "user",
            "limit": 10
        }
    """
    try:
        data = request.get_json() or {}

        # 获取参数
        game_gid = data.get("game_gid")
        event_name = data.get("event_name")
        field_name_hint = data.get("field_name_hint")
        limit = data.get("limit", 20)

        # 验证limit参数
        try:
            limit = int(limit)
            if limit < 1:
                limit = 1
            elif limit > 100:
                limit = 100
        except (ValueError, TypeError):
            return json_error_response("limit参数必须是整数", status_code=400)

        # 调用服务获取推荐
        service = FieldRecommendationService()
        recommendations = service.get_recommendations(
            game_gid=game_gid,
            event_name=event_name,
            field_name_hint=field_name_hint,
            limit=limit,
        )

        logger.info(
            f"Generated {len(recommendations)} recommendations "
            f"(game_gid={game_gid}, event_name={event_name}, hint={field_name_hint})"
        )

        return json_success_response(
            data=recommendations,
            message=f"获取到{len(recommendations)}条推荐"
        )

    except ValueError as e:
        logger.error(f"Validation error in get_recommendations: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error in get_recommendations: {e}", exc_info=True)
        return json_error_response("获取推荐失败", status_code=500)


@field_recommendation_bp.route("/api/field-recommendations/patterns", methods=["GET"])
def api_get_common_patterns():
    """
    API: 获取常用字段模式

    Query Parameters:
        game_gid: Optional[int]  # 游戏GID
        limit: Optional[int]  # 返回数量限制 (默认50)

    Response:
        {
            "success": true,
            "data": {
                "patterns": [
                    {
                        "param_name": str,
                        "param_name_cn": str,
                        "param_type": str,
                        "usage_count": int,
                        "event_count": int,
                        "is_common": bool,
                        "inferred_type": str
                    }
                ],
                "statistics": {
                    "total_unique_fields": int,
                    "total_field_usage": int,
                    "most_common_fields": List[Dict],
                    "type_distribution": Dict[str, int]
                }
            },
            "message": "获取成功"
        }

    Example:
        GET /api/field-recommendations/patterns?game_gid=10000147&limit=20
    """
    try:
        # 获取查询参数
        game_gid = request.args.get("game_gid", type=int)
        limit = request.args.get("limit", 50, type=int)

        # 验证limit参数
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100

        # 调用服务获取常用模式
        service = FieldRecommendationService()
        patterns_data = service.get_common_patterns(
            game_gid=game_gid,
            limit=limit,
        )

        logger.info(
            f"Retrieved {len(patterns_data['patterns'])} patterns "
            f"for game_gid={game_gid}"
        )

        return json_success_response(
            data=patterns_data,
            message=f"获取到{len(patterns_data['patterns'])}条常用字段模式"
        )

    except ValueError as e:
        logger.error(f"Validation error in get_common_patterns: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error in get_common_patterns: {e}", exc_info=True)
        return json_error_response("获取常用字段模式失败", status_code=500)


@field_recommendation_bp.route("/api/field-recommendations/types", methods=["GET"])
def api_infer_field_type():
    """
    API: 获取字段类型推断

    Query Parameters:
        field_name: str  # 字段名称 (必需)

    Response:
        {
            "success": true,
            "data": {
                "field_name": str,
                "inferred_type": str,
                "confidence": float,
                "suggested_hive_type": str,
                "reasoning": str
            },
            "message": "推断成功"
        }

    Example:
        GET /api/field-recommendations/types?field_name=role_id
    """
    try:
        # 获取查询参数
        field_name = request.args.get("field_name")

        # 验证必需参数
        if not field_name:
            return json_error_response("field_name参数是必需的", status_code=400)

        # 调用服务推断字段类型
        service = FieldRecommendationService()
        type_inference = service.infer_field_type(field_name=field_name)

        logger.info(
            f"Inferred type for '{field_name}': {type_inference['inferred_type']} "
            f"(confidence: {type_inference['confidence']:.2f})"
        )

        return json_success_response(
            data=type_inference,
            message=f"字段类型推断成功: {type_inference['inferred_type']}"
        )

    except ValueError as e:
        logger.error(f"Validation error in infer_field_type: {e}")
        return json_error_response(str(e), status_code=400)
    except Exception as e:
        logger.error(f"Error in infer_field_type: {e}", exc_info=True)
        return json_error_response("字段类型推断失败", status_code=500)


@field_recommendation_bp.route("/api/field-recommendations/cache/invalidate", methods=["POST"])
def api_invalidate_cache():
    """
    API: 失效推荐缓存

    Request Body:
        {
            "game_gid": Optional[int]  # 游戏GID (可选, 不提供则失效所有缓存)
        }

    Response:
        {
            "success": true,
            "message": "缓存失效成功"
        }

    Example:
        POST /api/field-recommendations/cache/invalidate
        {
            "game_gid": 10000147
        }
    """
    try:
        data = request.get_json() or {}
        game_gid = data.get("game_gid")

        # 调用服务失效缓存
        service = FieldRecommendationService()
        service.invalidate_recommendations_cache(game_gid=game_gid)

        if game_gid:
            logger.info(f"Invalidated recommendations cache for game_gid={game_gid}")
            message = f"游戏{game_gid}的推荐缓存已失效"
        else:
            logger.info("Invalidated all recommendations cache")
            message = "所有推荐缓存已失效"

        return json_success_response(message=message)

    except Exception as e:
        logger.error(f"Error in invalidate_cache: {e}", exc_info=True)
        return json_error_response("缓存失效失败", status_code=500)
