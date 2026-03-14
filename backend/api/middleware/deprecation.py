"""
V1 API废弃警告中间件

为V1 API添加废弃警告,引导用户迁移到V2 API
"""

import logging
from functools import wraps

from flask import jsonify, make_response, request

from backend.core.cache.cache_system import CacheInvalidator

logger = logging.getLogger(__name__)


# V1 API废弃警告消息
DEPRECATION_WARNING = """
⚠️  API废弃警告

您正在使用REST API,该API已被标记为废弃,将在未来版本中移除. 

请迁移到GraphQL API:
- REST: /api/games → GraphQL: games query
- REST: /api/events → GraphQL: events query
- REST: /api/parameters → GraphQL: parameters query
- REST: /api/categories → GraphQL: categories query

GraphQL API优势:
✅ 更好的性能(DataLoader批量加载)
✅ 灵活的查询(按需获取字段)
✅ 类型安全(强类型Schema)
✅ 实时订阅(Subscriptions)
✅ 更好的开发体验(GraphiQL IDE)

迁移指南: docs/api/REST_TO_GRAPHQL_MIGRATION.md
GraphQL端点: /api/graphql
GraphiQL IDE: http://localhost:5001/api/graphql
"""

# REST API到GraphQL映射
REST_TO_GRAPHQL_MAPPING = {
    '/api/games': 'games query',
    '/api/events': 'events query',
    '/api/parameters': 'parameters query',
    '/api/categories': 'categories query',
    '/api/hql': 'generateHQL mutation',
}


def add_deprecation_header(response):
    """
    为V1 API响应添加废弃警告头

    Args:
        response: Flask响应对象

    Returns:
        添加了废弃警告头的响应对象
    """
    # 检查是否是V1 API请求
    path = request.path

    # 排除V2 API和GraphQL
    if path.startswith('/api/v2') or path.startswith('/graphql'):
        return response

    # 检查是否是V1 API
    if path.startswith('/api/'):
        # 添加废弃警告头
        response.headers['X-API-Deprecated'] = 'true'
        response.headers['X-API-Deprecation-Date'] = '2026-04-30'
        response.headers['X-API-Sunset'] = '2026-07-31'

        # 添加替代API头
        v2_path = _get_v2_path(path)
        if v2_path:
            response.headers['X-API-Replacement'] = v2_path

        # 记录废弃API使用
        logger.warning(f"V1 API使用警告: {path} -> 建议迁移到 {v2_path}")

    return response


def deprecation_warning(f):
    """
    废弃警告装饰器

    为V1 API端点添加废弃警告

    Example:
        @api_bp.route('/api/games', methods=['GET'])
        @deprecation_warning
        def get_games_v1():
            # V1 API实现
            pass
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 执行原函数
        response = f(*args, **kwargs)

        # 如果返回的是元组,解包
        if isinstance(response, tuple):
            response_obj, status_code = response
        else:
            response_obj = response
            status_code = 200

        # 如果是JSON响应,添加废弃警告
        if isinstance(response_obj, dict):
            response_obj['_deprecated'] = True
            response_obj['_warning'] = DEPRECATION_WARNING.strip()
            response_obj['_migration_guide'] = 'docs/api/MIGRATION_GUIDE.md'

            v2_path = _get_v2_path(request.path)
            if v2_path:
                response_obj['_v2_endpoint'] = v2_path

            return jsonify(response_obj), status_code

        return response

    return decorated_function


def _get_v2_path(v1_path: str) -> str:
    """
    获取V2 API路径

    Args:
        v1_path: V1 API路径

    Returns:
        V2 API路径,如果没有对应的V2路径则返回空字符串
    """
    # 精确匹配
    if v1_path in REST_TO_GRAPHQL_MAPPING:
        return REST_TO_GRAPHQL_MAPPING[v1_path]

    # 前缀匹配
    for v1_prefix, v2_prefix in REST_TO_GRAPHQL_MAPPING.items():
        if v1_path.startswith(v1_prefix):
            return v1_path.replace(v1_prefix, v2_prefix, 1)

    # 默认替换
    if v1_path.startswith('/api/'):
        return v1_path.replace('/api/', '/api/v2/', 1)

    return ''


def log_v1_api_usage():
    """
    记录V1 API使用情况

    用于监控V1 API的使用频率,帮助确定废弃时间表
    """
    path = request.path

    if path.startswith('/api/') and not path.startswith('/api/v2'):
        # 记录V1 API使用
        logger.info(f"V1 API使用: {path} - {request.method}")

        # TODO: 可以将使用情况记录到数据库或监控系统
        # 例如: AnalyticsService.track_api_usage(path, 'v1', request.method)


def init_deprecation_middleware(app):
    """
    初始化废弃警告中间件

    Args:
        app: Flask应用实例
    """

    # 添加响应后处理器
    @app.after_request
    def after_request(response):
        return add_deprecation_header(response)

    # 添加请求前处理器
    @app.before_request
    def before_request():
        log_v1_api_usage()

    logger.info("✅ V1 API废弃警告中间件已启用")
