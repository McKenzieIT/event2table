"""
统一工具函数模块

提供跨模块复用的工具函数，按功能分类组织。

作者: Claude Code
版本: 1.0.0
创建日期: 2026-02-10

模块结构:
- validators: 验证函数（输入验证、安全验证、业务验证）
- formatters: 格式化函数（表名、字段名、HQL格式化）
- converters: 数据转换函数（模型转换、类型转换）

使用示例:
    >>> # 方式1: 从子模块导入
    >>> from backend.core.utils.validators import validate_event_name
    >>> from backend.core.utils.formatters import format_table_name
    >>> from backend.core.utils.converters import game_to_dict
    >>>
    >>> # 方式2: 从主模块导入（推荐）
    >>> from backend.core.utils import (
    ...     # 验证函数
    ...     validate_event_name,
    ...     validate_param_name,
    ...     sanitize_and_validate_string,
    ...     # 格式化函数
    ...     format_table_name,
    ...     format_field_name,
    ...     format_hql,
    ...     # 转换函数
    ...     game_to_dict,
    ...     event_to_dict,
    ...     safe_int,
    ...     safe_str
    ... )
"""

# ============================================================================
# 从 validators 导入
# ============================================================================

from .validators import (
    # 输入验证
    validate_event_name,
    validate_param_name,
    validate_game_gid,
    validate_game_id,
    validate_required_fields,
    # 安全验证
    validate_sql_safe,
    sanitize_and_validate_string,
    # 业务验证
    validate_game_exists,
    check_games_exist,
    # 正则模式
    EVENT_NAME_PATTERN,
    PARAM_NAME_PATTERN,
    SQL_INJECTION_PATTERN,
)

# Error messages
from .error_messages import (
    ErrorMessages,
    format_validation_error,
    format_api_error,
    build_error_response,
    validation_error,
    not_found_error,
    conflict_error,
    server_error,
)

# ============================================================================
# 从 formatters 导入
# ============================================================================

from .formatters import (
    # 表名格式化
    format_table_name,
    format_dwd_table_name,
    format_ods_table_name,
    # 字段名格式化
    format_field_name,
    format_field_list,
    # 错误响应格式化
    format_error_response,
    # HQL格式化
    format_hql_select,
    format_hql_from,
    format_hql_join,
    format_hql_where,
    format_hql_group_by,
    format_hql,
    # 字符串清理
    clean_identifier,
)

# ============================================================================
# 从 converters 导入
# ============================================================================

from .converters import (
    # 模型转字典
    game_to_dict,
    event_to_dict,
    parameter_to_dict,
    # API请求转模型
    api_request_to_model,
    # 类型转换
    safe_int,
    safe_str,
    safe_int_convert,
    safe_bool,
    safe_float,
    # 数据库查询转换
    fetch_all_as_dict,
    fetch_one_as_dict,
    # 辅助函数
    get_game_event_count,
    get_event_parameters,
)

# 从旧的 utils.py 导入剩余函数（向后兼容）
# ============================================================================
# 这些函数仍在父模块 backend.core.utils.py 中定义
# 我们需要直接导入它们以保持向后兼容性

# 注意：这里使用相对导入避免循环引用
# 导入父级目录的 utils.py 模块（不是 __init__.py）
import importlib.util
import sys

# 获取父模块路径
parent_module_path = "/Users/mckenzie/Documents/event2table/backend/core/utils.py"
spec = importlib.util.spec_from_file_location("backend.core.utils_legacy", parent_module_path)
utils_legacy = importlib.util.module_from_spec(spec)
sys.modules["backend.core.utils_legacy"] = utils_legacy
spec.loader.exec_module(utils_legacy)

# 导入所有遗留函数
execute_write = utils_legacy.execute_write
execute_transaction = utils_legacy.execute_transaction
batch_execute = utils_legacy.batch_execute
db_transaction = utils_legacy.db_transaction

success_response = utils_legacy.success_response
error_response = utils_legacy.error_response
json_success_response = utils_legacy.json_success_response
json_error_response = utils_legacy.json_error_response

validate_json_request = utils_legacy.validate_json_request
handle_errors = utils_legacy.handle_errors
handle_api_errors = utils_legacy.handle_api_errors

get_game_gid_param = utils_legacy.get_game_gid_param
require_game_with_redirect = utils_legacy.require_game_with_redirect
get_ods_db_name = utils_legacy.get_ods_db_name
calculate_common_param_threshold = utils_legacy.calculate_common_param_threshold

get_event_with_game_info = utils_legacy.get_event_with_game_info
get_game_by_gid = utils_legacy.get_game_by_gid
get_active_parameters = utils_legacy.get_active_parameters
get_event_with_parameters = utils_legacy.get_event_with_parameters
get_games_with_event_counts = utils_legacy.get_games_with_event_counts
check_game_has_events = utils_legacy.check_game_has_events
get_categories_by_game = utils_legacy.get_categories_by_game

sanitize_html = utils_legacy.sanitize_html
sanitize_user_input = utils_legacy.sanitize_user_input
escape_output = utils_legacy.escape_output

find_column_by_keywords = utils_legacy.find_column_by_keywords
get_or_401 = utils_legacy.get_or_401

# ============================================================================
# 导出列表
# ============================================================================

__all__ = [
    # ========== validators ==========
    # 输入验证
    "validate_event_name",
    "validate_param_name",
    "validate_game_gid",
    "validate_game_id",
    "validate_required_fields",
    # 安全验证
    "validate_sql_safe",
    "sanitize_and_validate_string",
    # 业务验证
    "validate_game_exists",
    "check_games_exist",
    # 正则模式
    "EVENT_NAME_PATTERN",
    "PARAM_NAME_PATTERN",
    "SQL_INJECTION_PATTERN",
    # ========== error messages ==========
    "ErrorMessages",
    "format_validation_error",
    "format_api_error",
    "build_error_response",
    "validation_error",
    "not_found_error",
    "conflict_error",
    "server_error",
    # ========== formatters ==========
    # 表名格式化
    "format_table_name",
    "format_dwd_table_name",
    "format_ods_table_name",
    # 字段名格式化
    "format_field_name",
    "format_field_list",
    # 错误响应格式化
    "format_error_response",
    # HQL格式化
    "format_hql_select",
    "format_hql_from",
    "format_hql_join",
    "format_hql_where",
    "format_hql_group_by",
    "format_hql",
    # 字符串清理
    "clean_identifier",
    # ========== converters ==========
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
    # 数据库查询转换
    "fetch_all_as_dict",
    "fetch_one_as_dict",
    # 辅助函数
    "get_game_event_count",
    "get_event_parameters",
    # ========== legacy utils.py (向后兼容) ==========
    # 数据库操作
    "execute_write",
    "execute_transaction",
    "batch_execute",
    "db_transaction",
    # 响应格式化
    "success_response",
    "error_response",
    "json_success_response",
    "json_error_response",
    # 请求处理
    "validate_json_request",
    "handle_errors",
    "handle_api_errors",
    # 游戏相关
    "get_game_gid_param",
    "require_game_with_redirect",
    "get_ods_db_name",
    "calculate_common_param_threshold",
    # 数据获取
    "get_event_with_game_info",
    "get_game_by_gid",
    "get_active_parameters",
    "get_event_with_parameters",
    "get_games_with_event_counts",
    "check_game_has_events",
    "get_categories_by_game",
    # 安全和清理
    "sanitize_html",
    "sanitize_user_input",
    "escape_output",
    # 工具函数
    "find_column_by_keywords",
    "get_or_401",
]

# 版本信息
__version__ = "1.0.0"
__author__ = "Claude Code"
