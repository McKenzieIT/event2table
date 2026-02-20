"""
HQL Preview V2 API Blueprint

新的HQL预览API，与现有API并行运行
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any

# Import HQL V2 core service
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.adapters.project_adapter import ProjectAdapter

# Import HQL API helpers (code complexity reduction)
from backend.api.routes._hql_helpers import (
    parse_json_request,
    validate_required_fields,
    handle_hql_generation_error,
    build_success_response,
)
from backend.core.utils import success_response, error_response

hql_preview_v2_bp = Blueprint("hql_preview_v2", __name__)


@hql_preview_v2_bp.route("/hql-preview-v2/api/generate", methods=["POST"])
def generate_hql_v2():
    """
    V2版本的HQL生成API

    使用新的HQL V2核心服务生成HQL

    Request Body:
    {
        "events": [
            {
                "game_gid": 10000147,
                "event_id": 1
            }
        ],
        "fields": [
            {
                "fieldName": "role_id",
                "fieldType": "base",
                "alias": "role"
            },
            {
                "fieldName": "zone_id",
                "fieldType": "param",
                "jsonPath": "$.zone_id"
            }
        ],
        "where_conditions": [
            {
                "field": "zone_id",
                "operator": "=",
                "value": 1,
                "logicalOp": "AND"
            }
        ],
        "options": {
            "mode": "single",
            "sql_mode": "VIEW",
            "include_comments": true
        }
    }

    Response:
    {
        "success": true,
        "data": {
            "hql": "-- Event Node: login\\nSELECT ...",
            "generated_at": "2026-02-06T10:00:00Z"
        }
    }
    """
    # 使用helper解析JSON
    is_valid, data, error = parse_json_request()
    if not is_valid:
        return jsonify(error_response(error, status_code=400)[0]), 400

    # 使用helper验证必填字段
    is_valid, error = validate_required_fields(data, ["events", "fields"])
    if not is_valid:
        return jsonify(error_response(error, status_code=400)[0]), 400

    if not data["events"]:
        return jsonify(
            error_response("events cannot be empty", status_code=400)[0]
        ), 400
    if not data["fields"]:
        return jsonify(
            error_response("fields cannot be empty", status_code=400)[0]
        ), 400

    try:
        # Support both formats:
        # Format 1 (standard): {"events": [{"game_gid": X, "event_id": Y}, ...]}
        # Format 2 (E2E test style): {"game_gid": X, "events": [{"event_id": Y}, ...]}
        # For Format 2, merge top-level game_gid into each event
        events_data = data["events"]
        if "game_gid" in data and not any("game_gid" in event for event in events_data):
            # Top-level game_gid provided, merge into events that don't have it
            for event in events_data:
                if "game_gid" not in event:
                    event["game_gid"] = data["game_gid"]

        # 1. 通过适配层转换数据
        events = ProjectAdapter.events_from_api_request(events_data)
        fields = ProjectAdapter.fields_from_api_request(data["fields"])
        conditions = ProjectAdapter.conditions_from_api_request(
            data.get("where_conditions", [])
        )

        # 获取选项
        options = data.get("options", {})

        # 2. 检查缓存（如果启用）
        from backend.services.hql.core.cache import get_global_cache

        cache = get_global_cache()
        cache_key = cache.get_cache_key(
            events_data, data["fields"], data.get("where_conditions", []), options
        )

        # 尝试从缓存获取
        cached_hql = cache.get(cache_key)
        if cached_hql is not None:
            from datetime import datetime

            result = {
                "hql": cached_hql,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "cached": True,
            }
            return jsonify(success_response(data=result)[0])

        # 3. 调用核心服务（完全无业务依赖）
        generator = HQLGenerator()
        hql = generator.generate(
            events=events, fields=fields, conditions=conditions, **options
        )

        # 4. 存储到缓存
        cache.set(cache_key, hql)

        # 5. 性能分析（如果请求）
        from datetime import datetime

        result = {"hql": hql, "generated_at": datetime.utcnow().isoformat() + "Z"}

        if options.get("include_performance"):
            from backend.services.hql.validators.performance_analyzer import (
                HQLPerformanceAnalyzer,
            )

            analyzer = HQLPerformanceAnalyzer()
            report = analyzer.analyze(hql)

            # 转换为可序列化的格式
            result["performance"] = {
                "score": report.score,
                "issues": [
                    {
                        "type": issue.type.value,
                        "message": issue.message,
                        "suggestion": issue.suggestion,
                    }
                    for issue in report.issues
                ],
                "metrics": {
                    "hasPartitionFilter": report.metrics.has_partition_filter,
                    "hasSelectStar": report.metrics.has_select_star,
                    "joinCount": report.metrics.join_count,
                    "crossJoinCount": report.metrics.cross_join_count,
                    "subqueryCount": report.metrics.subquery_count,
                    "udfCount": report.metrics.udf_count,
                    "complexity": report.metrics.complexity,
                },
            }

        return jsonify(success_response(data=result)[0])

    except Exception as e:
        # 使用helper统一处理错误
        return handle_hql_generation_error(e, "generate_hql_v2")


@hql_preview_v2_bp.route("/hql-preview-v2/api/generate-debug", methods=["POST"])
def generate_hql_debug():
    """
    V2版本的HQL生成API - 调试模式

    返回完整的生成跟踪信息，包括每个步骤的中间结果

    Request Body:
    {
        "events": [...],
        "fields": [...],
        "where_conditions": [...],
        "debug": true
    }

    Response:
    {
        "success": true,
        "data": {
            "hql": "...",
            "steps": [...],
            "events": [...],
            "fields": [...]
        }
    }
    """
    try:
        # 尝试解析JSON
        from werkzeug.exceptions import BadRequest

        try:
            data = request.get_json(force=False)
        except BadRequest:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        if data is None:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        # 验证必填字段
        if "events" not in data or not data["events"]:
            return jsonify(
                error_response("events is required", status_code=400)[0]
            ), 400

        if "fields" not in data or not data["fields"]:
            return jsonify(
                error_response("fields is required", status_code=400)[0]
            ), 400

        # 1. 通过适配层转换数据
        events = ProjectAdapter.events_from_api_request(data["events"])
        fields = ProjectAdapter.fields_from_api_request(data["fields"])
        conditions = ProjectAdapter.conditions_from_api_request(
            data.get("where_conditions", [])
        )

        # 获取选项
        options = data.get("options", {})
        debug = data.get("debug", True)

        if not debug:
            # 非调试模式，调用普通生成器
            from backend.services.hql.core.generator import HQLGenerator

            generator = HQLGenerator()
            hql = generator.generate(
                events=events, fields=fields, conditions=conditions, **options
            )

            from datetime import datetime

            result = {"hql": hql, "generated_at": datetime.utcnow().isoformat() + "Z"}

            return jsonify(success_response(data=result)[0])

        # 2. 调试模式 - 使用DebuggableHQLGenerator
        from backend.services.hql.core.generator import DebuggableHQLGenerator

        generator = DebuggableHQLGenerator()

        # 使用options中的debug值，避免参数重复
        debug_mode = options.pop("debug", True)

        trace = generator.generate(
            events=events,
            fields=fields,
            conditions=conditions,
            debug=debug_mode,
            **options,
        )

        # 重命名 final_hql 为 hql 以匹配API契约
        if "final_hql" in trace:
            trace["hql"] = trace.pop("final_hql")

        return jsonify(success_response(data=trace)[0])

    except ValueError as e:
        # 检查是否为"not found"错误，返回404而不是400
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify(error_response(error_msg, status_code=404)[0]), 404
        return jsonify(error_response(error_msg, status_code=400)[0]), 400
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


@hql_preview_v2_bp.route("/hql-preview-v2/api/validate", methods=["POST"])
def validate_hql():
    """
    验证HQL语法（完整版本）

    Request Body:
    {
        "hql": "SELECT role_id, account_id FROM ieu_ods.ods_10000147_all_view WHERE ds = '${bizdate}'"
    }

    Response:
    {
        "success": true,
        "data": {
            "is_valid": true,
            "syntax_errors": [],
            "warnings": [],
            "parse_details": {...}
        }
    }
    """
    try:
        data = request.get_json()

        if "hql" not in data:
            return jsonify(error_response("hql is required", status_code=400)[0]), 400

        hql = data["hql"]

        # 使用SyntaxValidator进行完整语法验证
        from backend.services.hql.validators.syntax_validator import SyntaxValidator

        validator = SyntaxValidator()
        result = validator.validate(hql)

        # 构建响应
        response_data = {
            "is_valid": result.is_valid,
            "syntax_errors": [
                {
                    "line": err.line,
                    "column": err.column,
                    "message": err.message,
                    "error_type": err.error_type,
                    "suggestion": err.suggestion,
                }
                for err in result.errors
            ],
            "warnings": [
                {
                    "line": warn.line,
                    "column": warn.column,
                    "message": warn.message,
                    "error_type": warn.error_type,
                    "suggestion": warn.suggestion,
                }
                for warn in result.warnings
            ],
        }

        # 添加解析详情（可选）
        if result.is_valid and result.parse_tree:
            response_data["parse_details"] = {
                "statements": (
                    len(list(result.parse_tree.flatten()))
                    if hasattr(result.parse_tree, "flatten")
                    else 1
                )
            }

        return jsonify(success_response(data=response_data)[0])

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


@hql_preview_v2_bp.route("/hql-preview-v2/api/recommend-fields", methods=["GET"])
def recommend_fields():
    """
    推荐字段（智能推荐）

    Query Parameters:
        event_name: 事件名称（如login, purchase等）
        partial: 部分字段名（用于模糊匹配）
        limit: 返回数量限制（默认10）
        use_history: 是否使用历史统计（默认true）

    Response:
    {
        "success": true,
        "data": {
            "suggestions": [
                {
                    "name": "role_id",
                    "type": "base",
                    "description": "Role ID (角色ID)",
                    "frequency": 150,
                    "score": 5.0
                }
            ],
            "count": 1
        }
    }

    推荐策略：
    1. 历史频率统计（权重5.0）- 从hql_history表统计
    2. 事件特定推荐（权重3.0）- 业务规则
    3. 协同过滤（权重2.0）- 相似事件组合
    4. 模糊匹配（权重1.5）- 部分字段名
    """
    from backend.services.hql.services.field_recommender import FieldRecommender
    from backend.core.config.config import get_db_path

    event_name = request.args.get("event_name", "")
    partial = request.args.get("partial", "")
    limit = request.args.get("limit", 10, type=int)
    use_history = request.args.get("use_history", "true", type=str).lower() == "true"

    try:
        # 获取数据库路径
        db_path = get_db_path()

        # 创建推荐器
        recommender = FieldRecommender(db_path=db_path)

        # 获取推荐
        suggestions = recommender.recommend_fields(
            event_name=event_name if event_name else None,
            partial=partial if partial else None,
            limit=limit,
            use_history=use_history,
        )

        return jsonify(
            success_response(
                data={"suggestions": suggestions, "count": len(suggestions)}
            )[0]
        )

    except Exception as e:
        import traceback

        traceback.print_exc()

        # 降级到常用字段列表
        common_fields = [
            {
                "name": "ds",
                "type": "base",
                "description": "Partition field",
                "score": 1.0,
            },
            {"name": "role_id", "type": "base", "description": "Role ID", "score": 1.0},
            {
                "name": "account_id",
                "type": "base",
                "description": "Account ID",
                "score": 1.0,
            },
            {
                "name": "zone_id",
                "type": "param",
                "description": "Zone ID",
                "score": 1.0,
            },
        ]

        if partial:
            common_fields = [
                f for f in common_fields if partial.lower() in f["name"].lower()
            ]

        return jsonify(
            success_response(
                data={
                    "suggestions": common_fields[:limit],
                    "count": len(common_fields[:limit]),
                    "fallback": True,  # 标记为降级方案
                }
            )[0]
        )


@hql_preview_v2_bp.route("/hql-preview-v2/api/generate-incremental", methods=["POST"])
def generate_hql_incremental():
    """
    增量生成HQL API

    相比完整生成，增量生成只重新生成变化的部分，性能提升3-5x

    Request Body:
    {
        "events": [...],
        "fields": [...],
        "where_conditions": [...],
        "previous_hql": "CREATE OR REPLACE VIEW ...",
        "options": {
            "mode": "single",
            "include_comments": true
        }
    }

    Response:
    {
        "success": true,
        "data": {
            "hql": "CREATE OR REPLACE VIEW ...",
            "incremental": true,
            "diff": {
                "added_fields": [],
                "removed_fields": [],
                "events_changed": false
            },
            "performance_gain": 3.3,
            "generation_time": 0.05
        }
    }
    """
    try:
        from werkzeug.exceptions import BadRequest

        try:
            data = request.get_json(force=False)
        except BadRequest:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        if data is None:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        # 验证必填字段
        if "events" not in data or not data["events"]:
            return jsonify(
                error_response("events is required", status_code=400)[0]
            ), 400

        if "fields" not in data or not data["fields"]:
            return jsonify(
                error_response("fields is required", status_code=400)[0]
            ), 400

        # 1. 通过适配层转换数据
        events = ProjectAdapter.events_from_api_request(data["events"])
        fields = ProjectAdapter.fields_from_api_request(data["fields"])
        conditions = ProjectAdapter.conditions_from_api_request(
            data.get("where_conditions", [])
        )

        # 获取选项和previous_hql
        options = data.get("options", {})
        previous_hql = data.get("previous_hql")

        # 2. 调用增量生成器
        from backend.services.hql.core.incremental_generator import (
            IncrementalHQLGenerator,
        )
        from datetime import datetime

        generator = IncrementalHQLGenerator()
        result = generator.generate_incremental(
            events=events,
            fields=fields,
            conditions=conditions,
            previous_hql=previous_hql,
            **options,
        )

        # 3. 构建响应
        response_data = {
            "hql": result["hql"],
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "incremental": result["incremental"],
            "performance_gain": result["performance_gain"],
            "generation_time": result["generation_time"],
        }

        # 如果有差异信息，添加到响应
        if result.get("diff"):
            diff = result["diff"]
            response_data["diff"] = {
                "added_fields": diff.added_fields,
                "removed_fields": diff.removed_fields,
                "modified_fields": diff.modified_fields,
                "added_conditions": diff.added_conditions,
                "removed_conditions": diff.removed_conditions,
                "modified_conditions": diff.modified_conditions,
                "events_changed": diff.events_changed,
            }

        return jsonify(success_response(data=response_data)[0])

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify(error_response(error_msg, status_code=404)[0]), 404
        return jsonify(error_response(error_msg, status_code=400)[0]), 400
    except Exception as e:
        import traceback

        traceback.print_exc()

        return (
            jsonify(
                error_response(
                    f"Failed to generate incremental HQL: {str(e)}", status_code=500
                )[0]
            ),
            500,
        )


@hql_preview_v2_bp.route("/hql-preview-v2/api/status", methods=["GET"])
def api_status():
    """
    API状态检查

    Returns:
        API版本和状态信息
    """
    # 获取缓存统计
    from backend.services.hql.core.cache import get_global_cache

    cache_stats = get_global_cache().get_stats()

    return jsonify(
        success_response(
            data={
                "version": "2.1.0",
                "status": "running",
                "features": [
                    "single_event_hql",
                    "param_fields",
                    "custom_fields",
                    "where_conditions",
                    "join_events",
                    "union_events",
                    "incremental_generation",
                    "syntax_validation",
                    "performance_analysis",
                    "lru_cache",  # 新增
                ],
                "cache_stats": cache_stats,
                "coming_soon": ["template_engine", "redis_cache"],
            }
        )[0]
    )


@hql_preview_v2_bp.route("/hql-preview-v2/api/cache-stats", methods=["GET"])
def cache_stats():
    """
    缓存统计信息API

    返回LRU缓存的详细统计信息

    Returns:
        缓存统计：大小、命中率、未命中数等
    """
    from backend.services.hql.core.cache import get_global_cache

    cache = get_global_cache()
    stats = cache.get_stats()

    return jsonify(
        success_response(
            data={
                "cache_size": stats["size"],
                "cache_maxsize": stats["maxsize"],
                "cache_hits": stats["hits"],
                "cache_misses": stats["misses"],
                "hit_rate": stats["hit_rate"],
                "keys_count": len(cache.get_keys()),
            }
        )[0]
    )


@hql_preview_v2_bp.route("/hql-preview-v2/api/cache-clear", methods=["POST"])
def cache_clear():
    """
    清空缓存API

    清空LRU缓存中的所有条目

    Returns:
        操作结果
    """
    from backend.services.hql.core.cache import clear_global_cache

    clear_global_cache()

    return jsonify(success_response(data={"message": "Cache cleared successfully"})[0])


@hql_preview_v2_bp.route("/hql-preview-v2/api/analyze", methods=["POST"])
def analyze_hql():
    """
    HQL性能分析API

    分析HQL的性能并提供优化建议

    Request Body:
    {
        "hql": "SELECT * FROM table WHERE ds = '${ds}'"
    }

    Returns:
        性能分析报告，包括：
        - 复杂度评分
        - 潜在问题列表
        - 优化建议
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(
                error_response("Request body is required", status_code=400)[0]
            ), 400

        hql = data.get("hql")
        if not hql:
            return jsonify(error_response("hql is required", status_code=400)[0]), 400

        # 使用性能分析器
        from backend.services.hql.validators.performance_analyzer import (
            HQLPerformanceAnalyzer,
        )

        # 执行分析
        analyzer = HQLPerformanceAnalyzer()
        report = analyzer.analyze(hql)

        # 确定复杂度级别
        complexity_score = report.score
        if complexity_score >= 80:
            complexity_level = "low"
        elif complexity_score >= 50:
            complexity_level = "medium"
        else:
            complexity_level = "high"

        # 转换为API响应格式
        response_data = {
            "complexity_score": report.score,
            "complexity_level": complexity_level,
            "issue_count": len(report.issues),
            "issues": [
                {
                    "issue_type": issue.type.value,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                }
                for issue in report.issues
            ],
            "metrics": {
                "select_star": report.metrics.has_select_star,
                "has_partition_filter": report.metrics.has_partition_filter,
                "join_count": report.metrics.join_count,
                "subquery_depth": report.metrics.subquery_count,
                "estimated_rows": report.metrics.complexity,  # 使用complexity作为估算
            },
            "summary": f"HQL分析完成，复杂度评分: {report.score}/100，发现{len(report.issues)}个问题",
        }

        return jsonify(success_response(data=response_data)[0])

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


@hql_preview_v2_bp.route("/hql-preview-v2/api/preview", methods=["POST"])
def preview_hql():
    """
    简化版HQL预览API

    Request Body:
    {
        "game_gid": 10000147,
        "event_id": 1,
        "fields": [
            {"name": "role_id", "type": "base"},
            {"name": "zone_id", "type": "param", "json_path": "$.zone_id", "alias": "zone"}
        ],
        "filter_conditions": {
            "conditions": [
                {"field": "role_id", "operator": "=", "value": 123}
            ]
        }
    }

    Response:
    {
        "success": true,
        "data": {
            "hql_content": "CREATE OR REPLACE VIEW ...",
            "generated_at": "2026-02-07T..."
        }
    }
    """
    try:
        from werkzeug.exceptions import BadRequest

        # 解析请求
        try:
            data = request.get_json(force=False)
        except BadRequest:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        if data is None:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        # 验证必填字段
        if "game_gid" not in data:
            return jsonify(
                error_response("game_gid is required", status_code=400)[0]
            ), 400

        if "event_id" not in data:
            return jsonify(
                error_response("event_id is required", status_code=400)[0]
            ), 400

        if "fields" not in data:
            return jsonify(
                error_response("fields is required", status_code=400)[0]
            ), 400

        game_gid = data["game_gid"]
        event_id = data["event_id"]
        fields_data = data["fields"]
        filter_conditions = data.get("filter_conditions", {})

        # 导入数据访问层
        from backend.core.data_access import Repositories

        # 查询事件信息
        event = Repositories.LOG_EVENTS.find_by_id(event_id)
        if not event:
            return jsonify(
                error_response(f"Event {event_id} not found", status_code=404)[0]
            ), 404

        # 转换为V2格式
        from backend.services.hql.models.event import Event, Field, Condition

        # 创建Event对象
        v2_event = Event(
            name=event["event_name"], table_name=f"ieu_ods.ods_{game_gid}_all_view"
        )

        # 转换字段
        v2_fields = []
        for field_data in fields_data:
            # 验证字段必须有name和type
            if "name" not in field_data:
                return (
                    jsonify(
                        error_response(
                            'Field missing "name" property', status_code=400
                        )[0]
                    ),
                    400,
                )

            if "type" not in field_data:
                return (
                    jsonify(
                        error_response(
                            f'Field "{field_data.get("name", "unknown")}" missing "type" property',
                            status_code=400,
                        )[0]
                    ),
                    400,
                )

            field_kwargs = {"name": field_data["name"], "type": field_data["type"]}

            # 处理不同类型的字段
            if field_data["type"] == "param":
                field_kwargs["json_path"] = field_data.get("json_path")
                field_kwargs["alias"] = field_data.get("alias", field_data["name"])
            elif field_data.get("alias"):
                field_kwargs["alias"] = field_data["alias"]
            elif field_data["type"] == "custom":
                field_kwargs["custom_expression"] = field_data.get("custom_expression")
            elif field_data["type"] == "fixed":
                field_kwargs["fixed_value"] = field_data.get("fixed_value")
            elif field_data.get("aggregate_func"):
                field_kwargs["aggregate_func"] = field_data["aggregate_func"]
                field_kwargs["alias"] = field_data.get("alias")

            v2_fields.append(Field(**field_kwargs))

        # 转换条件
        v2_conditions = []
        conditions_list = filter_conditions.get("conditions", [])
        for cond_data in conditions_list:
            v2_conditions.append(
                Condition(
                    field=cond_data["field"],
                    operator=cond_data["operator"],
                    value=cond_data.get("value"),
                )
            )

        # 生成HQL
        generator = HQLGenerator()
        hql = generator.generate(
            events=[v2_event],
            fields=v2_fields,
            conditions=v2_conditions,
            include_comments=True,
        )

        # 返回结果
        from datetime import datetime

        result = {
            "hql_content": hql,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

        return jsonify(success_response(data=result)[0])

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            return jsonify(error_response(error_msg, status_code=404)[0]), 404
        return jsonify(error_response(error_msg, status_code=400)[0]), 400
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


# ============================================================================
# History API - 历史版本管理
# ============================================================================


@hql_preview_v2_bp.route("/hql-preview-v2/api/history/save", methods=["POST"])
def save_history():
    """
    保存HQL生成历史（增强版）

    Request Body:
    {
        "events": [...],
        "fields": [...],
        "where_conditions": [...],
        "mode": "single",
        "hql": "CREATE OR REPLACE VIEW ...",
        "hql_type": "select",      // NEW: select/ddl/dml/canvas
        "game_gid": 10000147,      // NEW: game filtering
        "name_en": "Login Event",  // NEW: English name
        "name_cn": "登录事件",     // NEW: Chinese name
        "performance_score": 85,
        "user_id": 0,
        "session_id": "optional-session-id",
        "metadata": {...}
    }

    For hql_type="canvas", hql should be a JSON object:
    {
        "hql_type": "canvas",
        "hql": {
            "create_table": "CREATE TABLE...",
            "insert_overwrite": "INSERT OVERWRITE...",
            "select": "SELECT..."
        }
    }

    Response:
    {
        "success": true,
        "data": {
            "history_id": 123,
            "created_at": "2026-02-07T10:00:00Z"
        }
    }
    """
    try:
        from werkzeug.exceptions import BadRequest

        try:
            data = request.get_json(force=False)
        except BadRequest:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        if data is None:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        # 验证必填字段
        required_fields = ["events", "fields", "mode", "hql"]
        for field in required_fields:
            if field not in data:
                return jsonify(
                    error_response(f"{field} is required", status_code=400)[0]
                ), 400

        from backend.services.hql.services.history_service import HQLHistoryService
        from datetime import datetime

        service = HQLHistoryService()

        history_id = service.save_history(
            events=data["events"],
            fields=data["fields"],
            conditions=data.get("where_conditions", []),
            mode=data["mode"],
            hql=data["hql"],
            performance_score=data.get("performance_score"),
            user_id=data.get("user_id", 0),
            session_id=data.get("session_id"),
            metadata=data.get("metadata"),
            hql_type=data.get("hql_type", "select"),
            game_gid=data.get("game_gid"),
            name_en=data.get("name_en"),
            name_cn=data.get("name_cn"),
        )

        return jsonify(
            success_response(
                data={
                    "history_id": history_id,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                }
            )[0]
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


@hql_preview_v2_bp.route("/hql-preview-v2/api/history/list", methods=["GET"])
def get_history_list():
    """
    获取历史记录列表

    Query Parameters:
        user_id: 用户ID (default: 0)
        session_id: 会话ID (可选，优先级高于user_id)
        limit: 返回数量限制 (default: 50)
        offset: 偏移量 (default: 0)

    Response:
    {
        "success": true,
        "data": {
            "history": [
                {
                    "id": 123,
                    "mode": "single",
                    "hql": "CREATE OR REPLACE VIEW ...",
                    "performance_score": 85,
                    "created_at": "2026-02-07T10:00:00Z",
                    ...
                }
            ],
            "count": 1
        }
    }
    """
    try:
        from backend.services.hql.services.history_service import HQLHistoryService

        service = HQLHistoryService()

        user_id = request.args.get("user_id", 0, type=int)
        session_id = request.args.get("session_id")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        history_list = service.get_history_list(
            user_id=user_id, session_id=session_id, limit=limit, offset=offset
        )

        return jsonify(
            success_response(
                data={"history": history_list, "count": len(history_list)}
            )[0]
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


@hql_preview_v2_bp.route(
    "/hql-preview-v2/api/history/<int:history_id>", methods=["GET"]
)
def get_history_by_id(history_id: int):
    """
    获取单个历史记录

    Response:
    {
        "success": true,
        "data": {
            "id": 123,
            "events": [...],
            "fields": [...],
            "conditions": [...],
            "mode": "single",
            "hql": "CREATE OR REPLACE VIEW ...",
            "performance_score": 85,
            "created_at": "2026-02-07T10:00:00Z",
            "metadata": {...}
        }
    }
    """
    try:
        from backend.services.hql.services.history_service import HQLHistoryService

        service = HQLHistoryService()
        history = service.get_history_by_id(history_id)

        if not history:
            return (
                jsonify(
                    error_response(f"History {history_id} not found", status_code=404)[
                        0
                    ]
                ),
                404,
            )

        # 解析JSON字段
        import json

        result = {
            "id": history["id"],
            "events": json.loads(history["events_json"]),
            "fields": json.loads(history["fields_json"]),
            "conditions": (
                json.loads(history["conditions_json"])
                if history["conditions_json"]
                else []
            ),
            "mode": history["mode"],
            "hql": history["hql"],
            "performance_score": history["performance_score"],
            "created_at": history["created_at"],
            "metadata": json.loads(history["metadata_json"])
            if history["metadata_json"]
            else None,
        }

        return jsonify(success_response(data=result)[0])

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


@hql_preview_v2_bp.route(
    "/hql-preview-v2/api/history/<int:history_id>/restore", methods=["POST"]
)
def restore_history(history_id: int):
    """
    恢复历史版本

    返回历史记录的完整配置，用于前端恢复UI状态

    Response:
    {
        "success": true,
        "data": {
            "id": 123,
            "events": [...],
            "fields": [...],
            "conditions": [...],
            "mode": "single",
            "hql": "CREATE OR REPLACE VIEW ...",
            "performance_score": 85,
            "created_at": "2026-02-07T10:00:00Z",
            "metadata": {...}
        }
    }
    """
    try:
        from backend.services.hql.services.history_service import HQLHistoryService

        service = HQLHistoryService()
        restored = service.restore_history(history_id)

        if not restored:
            return (
                jsonify(
                    error_response(f"History {history_id} not found", status_code=404)[
                        0
                    ]
                ),
                404,
            )

        return jsonify(success_response(data=restored)[0])

    except Exception as e:
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                error_response(f"Failed to restore history: {str(e)}", status_code=500)[
                    0
                ]
            ),
            500,
        )


@hql_preview_v2_bp.route(
    "/hql-preview-v2/api/history/<int:history_id>", methods=["DELETE"]
)
def delete_history(history_id: int):
    """
    删除历史记录

    Response:
    {
        "success": true,
        "data": {
            "deleted": true,
            "history_id": 123
        }
    }
    """
    try:
        from backend.services.hql.services.history_service import HQLHistoryService

        service = HQLHistoryService()
        deleted = service.delete_history(history_id)

        if not deleted:
            return (
                jsonify(
                    error_response(f"History {history_id} not found", status_code=404)[
                        0
                    ]
                ),
                404,
            )

        return jsonify(
            success_response(data={"deleted": True, "history_id": history_id})[0]
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                error_response(f"Failed to delete history: {str(e)}", status_code=500)[
                    0
                ]
            ),
            500,
        )


@hql_preview_v2_bp.route("/hql-preview-v2/api/history/search", methods=["POST"])
def search_history():
    """
    搜索HQL历史记录（支持模糊搜索和多条件过滤）

    Request Body:
    {
        "keyword": "login",           // Fuzzy search keyword
        "hql_type": "select",        // Filter by HQL type (select/ddl/dml/canvas)
        "game_gid": 10000147,        // Filter by game
        "user_id": 0,                // Filter by user (optional)
        "date_from": "2026-02-01T00:00:00Z",  // Date range start
        "date_to": "2026-02-17T23:59:59Z",    // Date range end
        "limit": 50,                 // Result limit (default 50)
        "offset": 0                  // Pagination offset
    }

    Response:
    {
        "success": true,
        "data": {
            "history": [
                {
                    "id": 123,
                    "mode": "single",
                    "hql_type": "select",
                    "game_gid": 10000147,
                    "name_en": "Login Event",
                    "name_cn": "登录事件",
                    "hql": "CREATE OR REPLACE VIEW ...",
                    "performance_score": 85,
                    "created_at": "2026-02-07T10:00:00Z",
                    ...
                }
            ],
            "count": 1,
            "limit": 50,
            "offset": 0
        }
    }
    """
    try:
        from werkzeug.exceptions import BadRequest

        try:
            data = request.get_json(force=False)
        except BadRequest:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        if data is None:
            return jsonify(
                error_response("Invalid JSON format", status_code=400)[0]
            ), 400

        from backend.services.hql.services.history_service import HQLHistoryService

        service = HQLHistoryService()

        # Extract search parameters
        keyword = data.get("keyword")
        hql_type = data.get("hql_type")
        game_gid = data.get("game_gid")
        user_id = data.get("user_id")
        date_from = data.get("date_from")
        date_to = data.get("date_to")
        limit = data.get("limit", 50)
        offset = data.get("offset", 0)

        # Validate limit and offset
        if not isinstance(limit, int) or limit < 1 or limit > 500:
            return jsonify(
                error_response("limit must be between 1 and 500", status_code=400)[0]
            ), 400

        if not isinstance(offset, int) or offset < 0:
            return jsonify(
                error_response(
                    "offset must be a non-negative integer", status_code=400
                )[0]
            ), 400

        # Validate hql_type
        valid_hql_types = ["select", "ddl", "dml", "canvas"]
        if hql_type is not None and hql_type not in valid_hql_types:
            return (
                jsonify(
                    error_response(
                        f"hql_type must be one of {valid_hql_types}", status_code=400
                    )[0]
                ),
                400,
            )

        # Perform search
        history_list = service.search_history(
            keyword=keyword,
            hql_type=hql_type,
            game_gid=game_gid,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )

        return jsonify(
            success_response(
                data={
                    "history": history_list,
                    "count": len(history_list),
                    "limit": limit,
                    "offset": offset,
                }
            )[0]
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify(
            error_response("An internal error occurred", status_code=500)[0]
        ), 500


@hql_preview_v2_bp.route("/hql-preview-v2/api/history/global", methods=["GET"])
def global_search_history():
    """
    全局搜索HQL历史记录（跨所有用户和会话）

    Query Parameters:
        keyword: Fuzzy search keyword
        hql_type: Filter by HQL type (select/ddl/dml/canvas)
        limit: Result limit (default 50)
        offset: Pagination offset (default 0)

    Example:
        GET /hql-preview-v2/api/history/global?keyword=login&hql_type=select&limit=10

    Response:
    {
        "success": true,
        "data": {
            "history": [
                {
                    "id": 123,
                    "user_id": 0,
                    "session_id": "session-abc",
                    "mode": "single",
                    "hql_type": "select",
                    "game_gid": 10000147,
                    "name_en": "Login Event",
                    "name_cn": "登录事件",
                    "hql": "CREATE OR REPLACE VIEW ...",
                    "performance_score": 85,
                    "created_at": "2026-02-07T10:00:00Z"
                }
            ],
            "count": 1,
            "limit": 10,
            "offset": 0,
            "note": "Global query requires authentication. This is a development preview."
        }
    }
    """
    try:
        from backend.services.hql.services.history_service import HQLHistoryService

        service = HQLHistoryService()

        # Extract query parameters
        keyword = request.args.get("keyword")
        hql_type = request.args.get("hql_type")
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        # Validate limit and offset
        if limit < 1 or limit > 500:
            return jsonify(
                error_response("limit must be between 1 and 500", status_code=400)[0]
            ), 400

        if offset < 0:
            return jsonify(
                error_response(
                    "offset must be a non-negative integer", status_code=400
                )[0]
            ), 400

        # Validate hql_type
        valid_hql_types = ["select", "ddl", "dml", "canvas"]
        if hql_type is not None and hql_type not in valid_hql_types:
            return (
                jsonify(
                    error_response(
                        f"hql_type must be one of {valid_hql_types}", status_code=400
                    )[0]
                ),
                400,
            )

        # Perform global search
        history_list = service.global_search_history(
            keyword=keyword, hql_type=hql_type, limit=limit, offset=offset
        )

        return jsonify(
            success_response(
                data={
                    "history": history_list,
                    "count": len(history_list),
                    "limit": limit,
                    "offset": offset,
                    "note": "Global query requires authentication. This is a development preview.",
                }
            )[0]
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                error_response(
                    f"Failed to perform global search: {str(e)}", status_code=500
                )[0]
            ),
            500,
        )
