"""
Common Utilities Module - 消除代码重复的共享工具函数

此模块提供跨多个API和Service层共享的工具函数,
目标是消除重复代码,提高代码可维护性。

创建日期: 2026-03-16
作者: Claude Code (Subagent 1: 代码重复消除专家)

主要功能:
1. 日期时间处理
2. 字符串清理和验证
3. 分页参数处理
4. 通用错误处理装饰器
5. API响应构建辅助函数
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar
from datetime import datetime
from flask import request
from pydantic import ValidationError

# 直接从 response 模块导入，避免循环依赖
from .response import json_success_response, json_error_response

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ============================================================================
# 日期时间处理工具
# ============================================================================

def format_date(dt: Optional[datetime], format_str: str = "%Y-%m-%d") -> Optional[str]:
    """
    格式化日期为字符串（简化版本，仅日期部分）

    Args:
        dt: 日期时间对象
        format_str: 格式化字符串（默认为日期格式）

    Returns:
        格式化后的字符串，如果dt为None则返回None

    Example:
        >>> format_date(datetime(2026, 3, 17, 14, 30, 0))
        '2026-03-17'
    """
    if dt is None:
        return None
    return dt.strftime(format_str)


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """
    格式化日期时间为字符串

    Args:
        dt: 日期时间对象
        format_str: 格式化字符串

    Returns:
        格式化后的字符串,如果dt为None则返回None

    Example:
        >>> format_datetime(datetime(2026, 3, 16, 12, 30, 0))
        '2026-03-16 12:30:00'
    """
    if dt is None:
        return None
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析字符串为日期时间对象

    Args:
        date_str: 日期时间字符串
        format_str: 格式化字符串

    Returns:
        日期时间对象,解析失败返回None

    Example:
        >>> parse_datetime("2026-03-16 12:30:00")
        datetime.datetime(2026, 3, 16, 12, 30, 0)
    """
    try:
        return datetime.strptime(date_str, format_str)
    except (ValueError, TypeError):
        return None


# ============================================================================
# 字符串清理和验证工具
# ============================================================================

def sanitize_string(s: Any) -> str:
    """
    清理和标准化字符串（HTML转义 + 去空白）

    Args:
        s: 输入值

    Returns:
        清理后的字符串

    Example:
        >>> sanitize_string("<script>alert('test')</script>  ")
        '&lt;script&gt;alert(&#x27;test&#x27;)&lt;/script&gt;'
    """
    import html

    if s is None:
        return ""

    # 转换为字符串
    if not isinstance(s, str):
        s = str(s)

    # HTML转义（防止XSS攻击）
    sanitized = html.escape(s)

    # 去除首尾空白
    sanitized = sanitized.strip()

    return sanitized


def clean_string(value: Any, max_length: Optional[int] = None) -> Optional[str]:
    """
    清理和标准化字符串

    Args:
        value: 输入值
        max_length: 最大长度限制

    Returns:
        清理后的字符串,如果输入为空或无效则返回None

    Example:
        >>> clean_string("  hello world  ")
        'hello world'
        >>> clean_string("  hello world  ", max_length=5)
        'hello'
    """
    if value is None:
        return None

    if not isinstance(value, str):
        value = str(value)

    # 去除首尾空白
    cleaned = value.strip()

    # 如果为空字符串,返回None
    if not cleaned:
        return None

    # 截断到最大长度
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]

    return cleaned


def normalize_identifier(value: str) -> str:
    """
    标准化标识符(表名、字段名等)

    Args:
        value: 原始标识符

    Returns:
        标准化后的标识符(小写、下划线分隔)

    Example:
        >>> normalize_identifier("EventName")
        'event_name'
        >>> normalize_identifier("event-name")
        'event_name'
    """
    import re

    # 转换为小写
    normalized = value.lower()

    # 替换连字符和空格为下划线
    normalized = re.sub(r'[-\s]+', '_', normalized)

    # 移除特殊字符(只保留字母、数字、下划线)
    normalized = re.sub(r'[^a-z0-9_]', '', normalized)

    # 确保不以数字开头
    if normalized and normalized[0].isdigit():
        normalized = '_' + normalized

    return normalized


# ============================================================================
# 分页参数处理工具
# ============================================================================

def get_pagination_params() -> Tuple[int, int, int]:
    """
    从请求中获取分页参数

    Returns:
        Tuple of (page, per_page, offset)
        - page: 当前页码(最小为1)
        - per_page: 每页数量(默认20,最小1,最大100)
        - offset: 数据库查询偏移量

    Example:
        >>> page, per_page, offset = get_pagination_params()
        >>> # GET /api/items?page=2&per_page=50
        >>> # page=2, per_page=50, offset=50
    """
    page = max(1, request.args.get('page', 1, type=int))
    per_page = request.args.get('per_page', 20, type=int)

    # 限制per_page范围
    per_page = max(1, min(100, per_page))

    # 计算offset
    offset = (page - 1) * per_page

    return page, per_page, offset


def build_pagination_response(
    items: List[Any],
    total: int,
    page: int,
    per_page: int
) -> Dict[str, Any]:
    """
    构建分页响应

    Args:
        items: 数据项列表
        total: 总数量
        page: 当前页码
        per_page: 每页数量

    Returns:
        包含数据和分页信息的字典

    Example:
        >>> response = build_pagination_response(
        ...     items=[{'id': 1}, {'id': 2}],
        ...     total=100,
        ...     page=1,
        ...     per_page=20
        ... )
        >>> response['pagination']['total_pages']
        5
    """
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


# ============================================================================
# 错误处理装饰器
# ============================================================================

def handle_api_errors(
    error_message: str = "Operation failed",
    validation_error_message: str = "Validation error",
    not_found_message: str = "Resource not found"
) -> Callable:
    """
    API错误处理装饰器

    统一处理API端点中的常见错误,减少重复的try-except代码块

    Args:
        error_message: 通用错误消息
        validation_error_message: 验证错误消息
        not_found_message: 资源未找到消息

    Example:
        @api_bp.route('/api/games', methods=['GET'])
        @handle_api_errors("Failed to list games")
        def list_games():
            service = GameService()
            games = service.get_all()
            return json_success_response(data=games)
    """

    def decorator(func: Callable[..., Tuple[Dict[str, Any], int]]) -> Callable[..., Tuple[Dict[str, Any], int]]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[Dict[str, Any], int]:
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.error(f"Validation error in {func.__name__}: {e}")
                return json_error_response(
                    f"{validation_error_message}: {str(e)}",
                    status_code=400
                )
            except ValueError as e:
                logger.error(f"Value error in {func.__name__}: {e}")
                return json_error_response(str(e), status_code=400)
            except KeyError as e:
                logger.error(f"Missing key in {func.__name__}: {e}")
                return json_error_response(
                    f"Missing required field: {str(e)}",
                    status_code=400
                )
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
                return json_error_response(error_message, status_code=500)

        return wrapper

    return decorator


# ============================================================================
# 请求验证辅助函数
# ============================================================================

def validate_request_json(required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    验证JSON请求并返回数据

    Args:
        required_fields: 必需字段列表

    Returns:
        解析后的JSON数据

    Raises:
        ValueError: 如果请求不是JSON或缺少必需字段

    Example:
        @api_bp.route('/api/games', methods=['POST'])
        def create_game():
            try:
                data = validate_request_json(required_fields=['name', 'gid'])
                # 处理数据...
            except ValueError as e:
                return json_error_response(str(e), status_code=400)
    """
    if not request.is_json:
        raise ValueError("Request must be JSON")

    data = request.get_json()

    if data is None:
        raise ValueError("Invalid JSON data")

    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    return data


def get_game_gid_from_request() -> Optional[int]:
    """
    从请求中获取game_gid参数

    Returns:
        game_gid整数,如果不存在或无效则返回None

    Example:
        @api_bp.route('/api/events', methods=['GET'])
        def list_events():
            game_gid = get_game_gid_from_request()
            if not game_gid:
                return json_error_response("game_gid is required", status_code=400)
            # 处理逻辑...
    """
    game_gid_str = request.args.get('game_gid')
    if not game_gid_str:
        return None

    try:
        return int(game_gid_str)
    except (ValueError, TypeError):
        return None


# ============================================================================
# 批量操作辅助函数
# ============================================================================

def process_batch_items(
    items: List[Any],
    processor: Callable[[Any], Tuple[bool, str]],
    success_message: str = "Operation completed",
    partial_message: str = "Operation partially completed"
) -> Dict[str, Any]:
    """
    处理批量操作

    Args:
        items: 要处理的项目列表
        processor: 处理函数,返回(success: bool, message: str)
        success_message: 全部成功时的消息
        partial_message: 部分成功时的消息

    Returns:
        操作结果字典

    Example:
        def delete_game(game_id):
            # 删除逻辑
            return True, "Game deleted"

        result = process_batch_items(
            items=[1, 2, 3],
            processor=delete_game,
            success_message="All games deleted"
        )
    """
    successful = []
    failed = []

    for item in items:
        try:
            success, message = processor(item)
            if success:
                successful.append(item)
            else:
                failed.append({'id': item, 'error': message})
        except Exception as e:
            failed.append({'id': item, 'error': str(e)})
            logger.error(f"Error processing item {item}: {e}")

    total = len(items)
    success_count = len(successful)
    failed_count = len(failed)

    if failed_count == 0:
        return {
            'success': True,
            'message': success_message,
            'stats': {
                'total': total,
                'successful': success_count,
                'failed': failed_count
            }
        }
    else:
        return {
            'success': success_count > 0,
            'message': partial_message,
            'stats': {
                'total': total,
                'successful': success_count,
                'failed': failed_count
            },
            'errors': failed
        }


# ============================================================================
# 数据转换辅助函数
# ============================================================================

def convert_to_dict_list(items: List[Any], keys: List[str]) -> List[Dict[str, Any]]:
    """
    将对象列表转换为字典列表

    Args:
        items: 对象列表(可以是字典、namedtuple、或具有属性的对象)
        keys: 要提取的键列表

    Returns:
        字典列表

    Example:
        >>> rows = [('id1', 'name1'), ('id2', 'name2')]
        >>> convert_to_dict_list(rows, ['id', 'name'])
        [{'id': 'id1', 'name': 'name1'}, {'id': 'id2', 'name': 'name2'}]
    """
    result = []

    for item in items:
        if isinstance(item, dict):
            # 如果是字典,只提取指定的键
            result.append({k: item.get(k) for k in keys})
        elif hasattr(item, '_asdict'):  # namedtuple
            result.append({k: getattr(item, k, None) for k in keys})
        elif hasattr(item, '__dict__'):  # 普通对象
            result.append({k: getattr(item, k, None) for k in keys})
        else:  # 假设是序列类型
            result.append(dict(zip(keys, item)))

    return result


def extract_fields(data: Dict[str, Any], field_map: Dict[str, str]) -> Dict[str, Any]:
    """
    从字典中提取和重命名字段

    Args:
        data: 源数据字典
        field_map: 字段映射 {源字段名: 目标字段名}

    Returns:
        提取后的新字典

    Example:
        >>> data = {'game_gid': 100, 'game_name': 'Test'}
        >>> extract_fields(data, {'game_gid': 'gid', 'game_name': 'name'})
        {'gid': 100, 'name': 'Test'}
    """
    result = {}

    for source_field, target_field in field_map.items():
        if source_field in data:
            result[target_field] = data[source_field]

    return result


# ============================================================================
# 日志辅助函数
# ============================================================================

def log_api_call(
    endpoint: str,
    method: str,
    params: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None
):
    """
    记录API调用日志

    Args:
        endpoint: 端点路径
        method: HTTP方法
        params: 请求参数
        user_id: 用户ID

    Example:
        @api_bp.route('/api/games', methods=['GET'])
        def list_games():
            log_api_call('/api/games', 'GET', request.args.to_dict())
            # 处理逻辑...
    """
    log_data = {
        'endpoint': endpoint,
        'method': method,
        'params': params or {},
    }

    if user_id:
        log_data['user_id'] = user_id

    logger.info(f"API call: {log_data}")


# ============================================================================
# 导出列表
# ============================================================================

__all__ = [
    # 日期时间处理
    'format_date',
    'format_datetime',
    'parse_datetime',
    # 字符串处理
    'sanitize_string',
    'clean_string',
    'normalize_identifier',
    # 分页
    'get_pagination_params',
    'build_pagination_response',
    # 错误处理
    'handle_api_errors',
    # 请求验证
    'validate_request_json',
    'get_game_gid_from_request',
    # 批量操作
    'process_batch_items',
    # 数据转换
    'convert_to_dict_list',
    'extract_fields',
    # 日志
    'log_api_call',
]

__version__ = '1.0.0'
__author__ = 'Claude Code'
