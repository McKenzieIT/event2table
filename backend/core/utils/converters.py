"""
数据转换函数模块

提供统一的数据模型转换、字典转换、类型转换功能。

作者: Claude Code
版本: 1.0.0
创建日期: 2026-02-10

功能分类:
- 模型转字典 (game_to_dict, event_to_dict)
- API请求转模型 (api_request_to_model)
- 类型转换 (safe_int, safe_str, safe_int_convert)
- 字典转换 (fetch_all_as_dict, fetch_one_as_dict)

使用示例:
    >>> from backend.core.utils.converters import (
    ...     game_to_dict,
    ...     event_to_dict,
    ...     safe_int,
    ...     safe_str
    ... )
    >>>
    >>> # 转换游戏对象为字典
    >>> game_dict = game_to_dict(game_object)
    >>>
    >>> # 安全转换整数
    >>> value = safe_int("123", default=0)
"""

from typing import Any, Optional, Dict, List, Tuple, Union
from datetime import datetime
from backend.core.database import get_db_connection
from backend.core.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# 模型转字典函数
# ============================================================================


def game_to_dict(game: Any, include_counts: bool = False) -> Dict[str, Any]:
    """
    将游戏对象转换为字典

    Args:
        game: 游戏对象（可以是字典、Row对象或其他）
        include_counts: 是否包含事件计数等统计信息

    Returns:
        游戏字典

    Example:
        >>> game = {'id': 1, 'gid': 10000147, 'name': 'Test Game'}
        >>> game_dict = game_to_dict(game)
        >>> print(game_dict['name'])  # 'Test Game'
    """
    # 如果已经是字典，直接返回
    if isinstance(game, dict):
        result = game.copy()
    else:
        # 尝试从对象获取属性
        try:
            result = {
                "id": game.id,
                "gid": game.gid,
                "name": game.name,
                "description": game.description,
                "ods_db": game.ods_db,
                "created_at": game.created_at,
                "updated_at": game.updated_at,
            }
        except AttributeError as e:
            logger.error(f"Error converting game to dict: {e}")
            # Fallback: 尝试转换为字典
            result = dict(game)

    # 可选：包含统计信息
    if include_counts:
        try:
            result["event_count"] = get_game_event_count(result.get("gid"))
        except Exception:
            result["event_count"] = 0

    return result


def event_to_dict(event: Any, include_parameters: bool = False) -> Dict[str, Any]:
    """
    将事件对象转换为字典

    Args:
        event: 事件对象（可以是字典、Row对象或其他）
        include_parameters: 是否包含参数信息

    Returns:
        事件字典

    Example:
        >>> event = {'id': 1, 'event_name': 'user_login', 'game_gid': 10000147}
        >>> event_dict = event_to_dict(event)
        >>> print(event_dict['event_name'])  # 'user_login'
    """
    # 如果已经是字典，直接返回
    if isinstance(event, dict):
        result = event.copy()
    else:
        # 尝试从对象获取属性
        try:
            result = {
                "id": event.id,
                "event_name": event.event_name,
                "game_gid": event.game_gid,
                "description": event.description,
                "category_id": event.category_id,
                "is_active": event.is_active,
                "created_at": event.created_at,
                "updated_at": event.updated_at,
            }
        except AttributeError as e:
            logger.error(f"Error converting event to dict: {e}")
            # Fallback: 尝试转换为字典
            result = dict(event)

    # 可选：包含参数信息
    if include_parameters and result.get("id"):
        try:
            result["parameters"] = get_event_parameters(result["id"])
        except Exception:
            result["parameters"] = []

    return result


def parameter_to_dict(parameter: Any) -> Dict[str, Any]:
    """
    将参数对象转换为字典

    Args:
        parameter: 参数对象

    Returns:
        参数字典

    Example:
        >>> param = {'id': 1, 'param_name': 'user_id', 'event_id': 1}
        >>> param_dict = parameter_to_dict(param)
        >>> print(param_dict['param_name'])  # 'user_id'
    """
    if isinstance(parameter, dict):
        return parameter.copy()

    try:
        return {
            "id": parameter.id,
            "param_name": parameter.param_name,
            "param_name_cn": parameter.param_name_cn,
            "param_type": parameter.param_type,
            "event_id": parameter.event_id,
            "is_required": parameter.is_required,
            "default_value": parameter.default_value,
            "description": parameter.description,
            "is_active": parameter.is_active,
            "order_index": parameter.order_index,
            "created_at": parameter.created_at,
            "updated_at": parameter.updated_at,
        }
    except AttributeError as e:
        logger.error(f"Error converting parameter to dict: {e}")
        return dict(parameter)


# ============================================================================
# API请求转模型函数
# ============================================================================


def api_request_to_model(
    request_data: Dict[str, Any], model_type: str, exclude_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    将API请求数据转换为模型数据

    Args:
        request_data: 请求数据字典
        model_type: 模型类型（game, event, parameter等）
        exclude_fields: 要排除的字段列表

    Returns:
        模型数据字典

    Example:
        >>> data = {"name": "Test", "gid": 10000147}
        >>> model_data = api_request_to_model(data, "game")
        >>> print(model_data)  # {'name': 'Test', 'gid': 10000147}
    """
    exclude_fields = exclude_fields or []

    # 通用字段排除
    common_excludes = ["id", "created_at", "updated_at"]
    all_excludes = set(exclude_fields + common_excludes)

    # 根据模型类型进行特定处理
    if model_type == "game":
        field_mapping = {
            "name": str,
            "gid": int,
            "description": str,
            "ods_db": str,
        }
    elif model_type == "event":
        field_mapping = {
            "event_name": str,
            "game_gid": int,
            "description": str,
            "category_id": int,
            "is_active": bool,
        }
    elif model_type == "parameter":
        field_mapping = {
            "param_name": str,
            "param_name_cn": str,
            "param_type": str,
            "event_id": int,
            "is_required": bool,
            "default_value": str,
            "description": str,
            "is_active": bool,
            "order_index": int,
        }
    else:
        # 默认：保留所有字段
        field_mapping = None

    result = {}
    for key, value in request_data.items():
        # 跳过排除的字段
        if key in all_excludes:
            continue

        # 类型转换（如果有字段映射）
        if field_mapping and key in field_mapping:
            try:
                target_type = field_mapping[key]
                if value is not None:
                    value = target_type(value)
            except (ValueError, TypeError) as e:
                logger.warning(f"Type conversion failed for {key}: {e}")

        result[key] = value

    return result


# ============================================================================
# 类型转换函数
# ============================================================================


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全地将值转换为整数

    Args:
        value: 要转换的值
        default: 转换失败时的默认值

    Returns:
        转换后的整数值

    Example:
        >>> safe_int("123")  # 123
        >>> safe_int("abc", default=0)  # 0
        >>> safe_int(None, default=0)  # 0
    """
    if value is None:
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    安全地将值转换为字符串

    Args:
        value: 要转换的值
        default: 转换失败时的默认值

    Returns:
        转换后的字符串值

    Example:
        >>> safe_str(123)  # "123"
        >>> safe_str(None, default="N/A")  # "N/A"
    """
    if value is None:
        return default

    try:
        return str(value)
    except (ValueError, TypeError):
        return default


def safe_int_convert(
    value: Any, default: int = 0, min_value: Optional[int] = None, max_value: Optional[int] = None
) -> int:
    """
    安全地转换整数并进行范围验证

    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        min_value: 最小值（可选）
        max_value: 最大值（可选）

    Returns:
        转换并验证后的整数值

    Example:
        >>> safe_int_convert("100", min_value=1, max_value=1000)  # 100
        >>> safe_int_convert("0", min_value=1, max_value=1000)  # 1
        >>> safe_int_convert("2000", min_value=1, max_value=1000)  # 1000
    """
    result = safe_int(value, default)

    # 应用最小值限制
    if min_value is not None and result < min_value:
        result = min_value

    # 应用最大值限制
    if max_value is not None and result > max_value:
        result = max_value

    return result


def safe_bool(value: Any, default: bool = False) -> bool:
    """
    安全地将值转换为布尔值

    Args:
        value: 要转换的值
        default: 转换失败时的默认值

    Returns:
        转换后的布尔值

    Example:
        >>> safe_bool("true")  # True
        >>> safe_bool("1")  # True
        >>> safe_bool(0)  # False
        >>> safe_bool(None)  # False
    """
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ("true", "1", "yes", "on")

    if isinstance(value, (int, float)):
        return bool(value)

    return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全地将值转换为浮点数

    Args:
        value: 要转换的值
        default: 转换失败时的默认值

    Returns:
        转换后的浮点数值

    Example:
        >>> safe_float("3.14")  # 3.14
        >>> safe_float("abc", default=0.0)  # 0.0
    """
    if value is None:
        return default

    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def ensure_game_gid_int(value: Any) -> int:
    """
    确保game_gid是整数类型

    用于类型一致性验证，确保game_gid在整个应用中保持为INTEGER类型。

    Args:
        value: game_gid值（可以是int、str或其他类型）

    Returns:
        game_gid作为整数

    Raises:
        ValueError: 如果值无法转换为整数

    Example:
        >>> ensure_game_gid_int(10000147)
        10000147
        >>> ensure_game_gid_int("10000147")
        10000147
        >>> ensure_game_gid_int("invalid")
        Traceback (most recent call last):
            ...
        ValueError: Invalid game_gid: 'invalid' cannot be converted to integer
    """
    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValueError("game_gid cannot be empty")
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid game_gid: '{value}' cannot be converted to integer")

    # Try to convert other types to int
    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid game_gid type: {type(value).__name__}")


# ============================================================================
# 数据库查询转换函数
# ============================================================================


def fetch_all_as_dict(query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
    """
    执行查询并返回字典列表

    Args:
        query: SQL查询语句
        params: 查询参数（可选）

    Returns:
        字典列表

    Example:
        >>> events = fetch_all_as_dict("SELECT * FROM events WHERE game_gid = ?", (10000147,))
        >>> for event in events:
        ...     print(event['event_name'])
    """
    try:
        conn = get_db_connection()
        conn.row_factory = None  # 使用默认的行工厂
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        conn.close()

        # 转换为字典列表
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in rows]

    except Exception as e:
        logger.error(f"Error fetching all as dict: {e}")
        return []


def fetch_one_as_dict(query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
    """
    执行查询并返回单个字典

    Args:
        query: SQL查询语句
        params: 查询参数（可选）

    Returns:
        字典或None（如果没有结果）

    Example:
        >>> event = fetch_one_as_dict("SELECT * FROM events WHERE id = ?", (1,))
        >>> if event:
        ...     print(event['event_name'])
    """
    try:
        conn = get_db_connection()
        conn.row_factory = None
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        conn.close()

        if row:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return dict(zip(columns, row))

        return None

    except Exception as e:
        logger.error(f"Error fetching one as dict: {e}")
        return None


# ============================================================================
# 辅助函数
# ============================================================================


def get_game_event_count(game_gid: int) -> int:
    """
    获取游戏的事件计数

    Args:
        game_gid: 游戏GID

    Returns:
        事件数量
    """
    try:
        result = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM events WHERE game_gid = ?", (game_gid,)
        )
        return result["count"] if result else 0
    except Exception:
        return 0


def get_event_parameters(event_id: int) -> List[Dict[str, Any]]:
    """
    获取事件的参数列表

    Args:
        event_id: 事件ID

    Returns:
        参数字典列表
    """
    try:
        return fetch_all_as_dict(
            "SELECT * FROM event_parameters WHERE event_id = ? ORDER BY order_index", (event_id,)
        )
    except Exception:
        return []


# 导出列表
__all__ = [
    # 模型转字典
    "game_to_dict",
    "event_to_dict",
    "parameter_to_dict",
    # API请求转模型
    "api_request_to_model",
    # 类型转换
    "safe_int",
    "safe_str",
    "safe_int_convert",
    "safe_bool",
    "safe_float",
    "ensure_game_gid_int",
    # 数据库查询转换
    "fetch_all_as_dict",
    "fetch_one_as_dict",
    # 辅助函数
    "get_game_event_count",
    "get_event_parameters",
]
