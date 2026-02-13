"""
通用业务逻辑函数模块

包含跨多个模块复用的业务逻辑函数。

作者: Claude Code
版本: 1.0.0
创建日期: 2026-02-09

功能分类:
- 表单处理通用函数
- 缓存管理通用函数
- 数据获取通用函数
- 表名生成通用函数

使用示例:
    >>> from backend.core.common import validate_form_fields, clear_entity_caches
    >>>
    >>> # 表单验证
    >>> field_defs = [
    ...     {'name': 'game_gid', 'required': True, 'alias': '游戏ID'},
    ...     {'name': 'event_name', 'required': True}
    ... ]
    >>> is_valid, values, error = validate_form_fields(field_defs)
    >>>
    >>> # 缓存清理
    >>> clear_entity_caches('event', event_id, game_gid=123)
"""

from typing import Dict, List, Any, Optional, Tuple
from flask import request, flash
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# 表单处理通用函数
# ============================================================================


def validate_form_fields(
    field_definitions: List[Dict[str, Any]], error_message: str = "请填写所有必填字段"
) -> Tuple[bool, Dict[str, str], Optional[str]]:
    """
    通用表单字段验证函数

    Args:
        field_definitions: 字段定义列表，每个元素包含:
            - name: 字段名（对应request.form的key）
            - required: 是否必填（默认True）
            - strip: 是否去除空白（默认True）
            - alias: 可选的字段别名（用于错误消息）
        error_message: 验证失败时的错误消息

    Returns:
        Tuple[is_valid, field_values, error_message]
        - is_valid: 验证是否通过
        - field_values: 字段值字典 {field_name: value}
        - error_message: 错误消息（验证失败时）

    Example:
        >>> field_defs = [
        ...     {'name': 'game_gid', 'required': True},
        ...     {'name': 'event_name', 'required': True}
        ... ]
        >>> is_valid, values, error = validate_form_fields(field_defs)
        >>> if not is_valid:
        ...     flash(error, 'error')
    """
    field_values = {}
    missing_fields = []

    for field_def in field_definitions:
        field_name = field_def["name"]
        required = field_def.get("required", True)
        should_strip = field_def.get("strip", True)
        alias = field_def.get("alias", field_name)

        # 获取字段值
        value = request.form.get(field_name, "")
        if should_strip:
            value = value.strip()

        field_values[field_name] = value

        # 检查必填字段
        if required and not value:
            missing_fields.append(alias)

    if missing_fields:
        error_msg = error_message or f"请填写以下必填字段: {', '.join(missing_fields)}"
        return False, field_values, error_msg

    return True, field_values, None


def parse_form_list_fields(
    field_names: List[str], strip_values: bool = True
) -> Dict[str, List[str]]:
    """
    解析表单中的数组字段（使用<input name="field[]">）

    Args:
        field_names: 数组字段名列表（不含[]）
        strip_values: 是否去除每个值的空白

    Returns:
        Dict[field_name, List[value]]

    Example:
        >>> # HTML: <input name="param_name[]" value="x">
        >>> fields = parse_form_list_fields(['param_name', 'param_type'])
        >>> print(fields['param_name'])  # ['x', 'y', 'z']
    """
    result = {}
    for field_name in field_names:
        values = request.form.getlist(f"{field_name}[]")
        if strip_values:
            values = [v.strip() for v in values]
        result[field_name] = values
    return result


# ============================================================================
# 缓存管理通用函数
# ============================================================================


def clear_entity_caches(entity_type: str, entity_id: int, game_gid: Optional[int] = None) -> None:
    """
    通用的实体缓存清理函数

    Args:
        entity_type: 实体类型 ('event', 'game', 'parameter', etc.)
        entity_id: 实体ID
        game_gid: 关联的游戏GID（可选）

    Example:
        >>> # 清理事件缓存
        >>> clear_entity_caches('event', event_id, game_gid=123)
        >>>
        >>> # 清理游戏缓存（无关联实体）
        >>> clear_entity_caches('game', game_id)
    """
    try:
        # 导入缓存函数（延迟导入避免循环依赖）
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
        except ImportError:
            # Fallback: 使用空操作
            def clear_cache_pattern(pattern):
                pass

        # 清理实体特定缓存
        if entity_type == "event":
            clear_cache_pattern(f"event:*:{entity_id}")
            if game_gid:
                clear_cache_pattern(f"game:{game_gid}:events*")
        elif entity_type == "game":
            clear_cache_pattern(f"game:{entity_id}:*")
        elif entity_type == "parameter":
            clear_cache_pattern(f"param:*:{entity_id}")
            if game_gid:
                clear_cache_pattern(f"game:{game_gid}:params*")
        else:
            logger.warning(f"Unknown entity type for cache clearing: {entity_type}")

    except Exception as e:
        logger.error(f"Error clearing {entity_type} cache: {e}")


# ============================================================================
# 数据获取通用函数
# ============================================================================


def get_reference_data(data_types: List[str]) -> Dict[str, List[Dict]]:
    """
    通用的参考数据获取函数

    用于获取games、categories等参考表数据，支持缓存。

    Args:
        data_types: 数据类型列表，支持:
            - 'games': 游戏列表
            - 'event_categories': 事件分类
            - 'param_types': 参数类型

    Returns:
        Dict[data_type, List[Dict]]

    Example:
        >>> ref_data = get_reference_data(['games', 'event_categories'])
        >>> games = ref_data['games']
        >>> categories = ref_data['event_categories']
    """
    from backend.core.utils import fetch_all_as_dict

    result = {}

    queries = {
        "games": "SELECT * FROM games ORDER BY name",
        "event_categories": "SELECT * FROM event_categories ORDER BY name",
        "param_types": "SELECT * FROM param_types WHERE is_active = 1 ORDER BY id",
    }

    for data_type in data_types:
        if data_type in queries:
            # 尝试使用缓存查询（如果可用）
            try:
                from backend.core.cache.cache_system import cached_fetch

                result[data_type] = cached_fetch(queries[data_type], timeout=300)
            except:
                # Fallback to普通查询
                try:
                    result[data_type] = fetch_all_as_dict(queries[data_type])
                except Exception:
                    # 表不存在或其他错误，返回空列表
                    logger.warning(f"Failed to fetch reference data for {data_type}")
                    result[data_type] = []

    return result


# ============================================================================
# 表名生成通用函数
# ============================================================================


def generate_dwd_table_names(
    game: Dict[str, Any], event_name: str, ods_db: Optional[str] = None
) -> Dict[str, str]:
    """
    生成DWD层表的源表名和目标表名

    Args:
        game: 游戏字典，需包含:
            - gid: 游戏业务GID
            - ods_db: ODS数据库名
        event_name: 事件名称
        ods_db: 可选的ODS数据库名（覆盖game中的值）

    Returns:
        Dict {
            'source_table': 'ieu_ods.ods_10000147_all_view',
            'target_table': 'ieu_cdm.v_dwd_10000147_login_di',
            'dwd_prefix': 'ieu_cdm'
        }

    Example:
        >>> game = {'gid': 10000147, 'ods_db': 'ieu_ods'}
        >>> tables = generate_dwd_table_names(game, 'login')
        >>> print(tables['target_table'])
        'ieu_cdm.v_dwd_10000147_login_di'
    """
    # 确定ODS数据库
    ods_db = ods_db or game.get("ods_db")

    # 源表名: {ods_db}.ods_{gid}_all_view
    source_table = f'{ods_db}.ods_{game["gid"]}_all_view'

    # 确定DWD库前缀
    # 国内游戏(ieu_ods)使用ieu_cdm，海外游戏使用原ods_db
    dwd_prefix = "ieu_cdm" if ods_db == "ieu_ods" else ods_db

    # 清理事件名中的特殊字符（点号替换为下划线）
    clean_name = event_name.replace(".", "_")

    # 目标表名: {prefix}.v_dwd_{game_gid}_{event}_di
    target_table = f'{dwd_prefix}.v_dwd_{game["gid"]}_{clean_name}_di'

    return {"source_table": source_table, "target_table": target_table, "dwd_prefix": dwd_prefix}


# 导出列表
__all__ = [
    # 表单处理
    "validate_form_fields",
    "parse_form_list_fields",
    # 缓存管理
    "clear_entity_caches",
    # 数据获取
    "get_reference_data",
    # 表名生成
    "generate_dwd_table_names",
]
