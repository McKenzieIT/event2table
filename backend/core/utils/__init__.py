"""
统一工具函数模块

提供跨模块复用的工具函数, 按功能分类组织.

模块结构:
- validators: 验证函数（输入验证, 安全验证, 业务验证）
- formatters: 格式化函数（表名, 字段名, HQL格式化）
- converters: 数据转换函数（模型转换, 类型转换）
- sanitizers: SQL标识符清理和HTML安全函数
- database: 数据库写操作和事务管理
- response: API响应格式化
- request_helpers: 请求验证和错误处理装饰器
- business_helpers: 业务辅助函数（游戏、事件、参数查询）
- error_messages: 错误消息构建
- common: 日期时间、分页、批量操作等通用工具

使用示例:
    >>> from backend.core.utils import (
    ...     validate_event_name,
    ...     format_table_name,
    ...     fetch_all_as_dict,
    ...     execute_write,
    ...     success_response,
    ... )
"""

# ============================================================================
# 从 validators 导入
# ============================================================================
from .validators import (
    EVENT_NAME_PATTERN,
    PARAM_NAME_PATTERN,
    SQL_INJECTION_PATTERN,
    check_games_exist,
    sanitize_and_validate_string,
    validate_event_name,
    validate_game_exists,
    validate_game_gid,
    validate_game_id,
    validate_param_name,
    validate_required_fields,
    validate_sql_safe,
)

# ============================================================================
# 从 error_messages 导入
# ============================================================================
from .error_messages import (
    ErrorMessages,
    build_error_response,
    conflict_error,
    format_api_error,
    format_validation_error,
    not_found_error,
    server_error,
    validation_error,
)

# ============================================================================
# 从 formatters 导入
# ============================================================================
from .formatters import (
    clean_identifier,
    format_dwd_table_name,
    format_error_response,
    format_field_list,
    format_field_name,
    format_hql,
    format_hql_from,
    format_hql_group_by,
    format_hql_join,
    format_hql_select,
    format_hql_where,
    format_ods_table_name,
    format_table_name,
)

# ============================================================================
# 从 sanitizers 导入
# ============================================================================
from .sanitizers import (
    IdentifierSanitizer,
    escape_output,
    sanitize_html,
    sanitize_identifier,
    sanitize_user_input,
)

# ============================================================================
# 从 converters 导入
# ============================================================================
from .converters import (
    api_request_to_model,
    event_to_dict,
    fetch_all_as_dict,
    fetch_one_as_dict,
    game_to_dict,
    get_event_parameters,
    get_game_event_count,
    parameter_to_dict,
    safe_bool,
    safe_float,
    safe_int,
    safe_int_convert,
    safe_str,
)

# ============================================================================
# 从 database 导入
# ============================================================================
from .database import (
    batch_execute,
    db_transaction,
    execute_transaction,
    execute_write,
)

# ============================================================================
# 从 response 导入
# ============================================================================
from .response import (
    error_response,
    json_error_response,
    json_success_response,
    success_response,
)

# ============================================================================
# 从 request_helpers 导入
# ============================================================================
from .request_helpers import (
    handle_api_errors,
    handle_errors,
    validate_json_request,
)

# ============================================================================
# 从 business_helpers 导入
# 注意: validate_game_gid 和 validate_event_name 已从 validators 导入
# business_helpers 中的同名函数签名不同(抛异常 vs 返回元组),
# 需要通过 business_helpers 模块直接访问
# ============================================================================
from .business_helpers import (
    build_cache_key,
    build_event_cache_key,
    build_game_cache_key,
    build_hql_field_alias,
    calculate_common_param_threshold,
    calculate_event_statistics,
    calculate_param_usage,
    check_game_has_events,
    find_column_by_keywords,
    format_hql_field,
    format_json_path,
    generate_dwd_table_name,
    generate_table_name,
    get_active_parameters,
    get_categories_by_game,
    get_event_with_game_info,
    get_event_with_parameters,
    get_game_by_gid,
    get_game_gid_param,
    get_games_with_event_counts,
    get_ods_db_name,
    get_or_401,
    is_safe_table_name,
    is_valid_game_gid,
    python_type_to_hive_type,
    require_game_with_redirect,
    sanitize_name,
    validate_table_name,
)

# ============================================================================
# 从 errors 导入自定义异常
# ============================================================================
from backend.core.errors import (
    EmptyFieldListError,
    HQLGenerationError,
    InvalidNodeTypeError,
    MissingJoinConfigError,
    MissingJoinKeyError,
)

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
    # ========== sanitizers ==========
    "IdentifierSanitizer",
    "sanitize_identifier",
    "sanitize_html",
    "sanitize_user_input",
    "escape_output",
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
    # ========== database ==========
    "execute_write",
    "execute_transaction",
    "batch_execute",
    "db_transaction",
    # ========== response ==========
    "success_response",
    "error_response",
    "json_success_response",
    "json_error_response",
    # ========== request_helpers ==========
    "validate_json_request",
    "handle_errors",
    "handle_api_errors",
    # ========== business_helpers ==========
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
    "get_or_401",
    "find_column_by_keywords",
    # 业务验证函数 (注意: validate_game_gid/validate_event_name 已从 validators 导出)
    "validate_table_name",
    # 统计函数
    "calculate_event_statistics",
    "calculate_param_usage",
    # 数据转换函数
    "sanitize_name",
    "generate_table_name",
    "generate_dwd_table_name",
    # HQL生成辅助函数
    "format_json_path",
    "build_hql_field_alias",
    "format_hql_field",
    # 缓存相关函数
    "build_cache_key",
    "build_game_cache_key",
    "build_event_cache_key",
    # 数据验证辅助函数
    "is_valid_game_gid",
    "is_safe_table_name",
    # 类型转换辅助函数
    "python_type_to_hive_type",
    # ========== custom exceptions ==========
    "HQLGenerationError",
    "EmptyFieldListError",
    "MissingJoinKeyError",
    "InvalidNodeTypeError",
    "MissingJoinConfigError",
]

# 版本信息
__version__ = "2.0.0"
__author__ = "Claude Code"
