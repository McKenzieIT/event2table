"""
User-Friendly Error Messages Module

Provides standardized, user-friendly error messages for common API errors.
All error messages are in Chinese to match the application's language.

Error Message Format:
- Clear and actionable
- Specific to the error type
- Suggest solutions when possible
- Avoid technical jargon
"""

from typing import Dict, Any, Optional
from datetime import datetime


class ErrorMessages:
    """Centralized error message definitions"""

    # ==================== Validation Errors ====================

    @staticmethod
    def required_field(field_name: str) -> str:
        """Required field is missing"""
        return f"{field_name}不能为空"

    @staticmethod
    def invalid_format(field_name: str, expected_format: str) -> str:
        """Field format is invalid"""
        return f"{field_name}格式不正确，应为{expected_format}"

    @staticmethod
    def invalid_game_gid_format() -> str:
        """Game GID format is invalid"""
        return "游戏GID必须是正整数（例如：10000147或90000001）"

    @staticmethod
    def invalid_game_id_format() -> str:
        """Game ID format is invalid"""
        return "游戏ID必须是正整数"

    @staticmethod
    def invalid_event_name_format() -> str:
        """Event name format is invalid"""
        return "事件名称只能包含字母、数字和下划线，且必须以字母开头"

    @staticmethod
    def invalid_param_name_format() -> str:
        """Parameter name format is invalid"""
        return "参数名称只能包含字母、数字和下划线，且必须以字母开头"

    # ==================== Duplicate/Conflict Errors ====================

    @staticmethod
    def duplicate_game_gid(gid: str) -> str:
        """Game GID already exists"""
        return f"游戏GID '{gid}' 已存在，请使用其他GID或更新现有游戏"

    @staticmethod
    def duplicate_event_name(name: str, game_gid: Optional[int] = None) -> str:
        """Event name already exists"""
        if game_gid:
            return f"游戏 {game_gid} 中已存在事件 '{name}'，请使用其他名称"
        return f"事件 '{name}' 已存在，请使用其他名称"

    @staticmethod
    def duplicate_param_name(name: str, event_name: Optional[str] = None) -> str:
        """Parameter name already exists"""
        if event_name:
            return f"事件 '{event_name}' 中已存在参数 '{name}'，请使用其他名称"
        return f"参数 '{name}' 已存在，请使用其他名称"

    # ==================== Not Found Errors ====================

    @staticmethod
    def game_not_found(gid: Any) -> str:
        """Game not found"""
        return f"游戏GID '{gid}' 不存在，请检查GID是否正确"

    @staticmethod
    def event_not_found(event_id: Any) -> str:
        """Event not found"""
        return f"事件ID '{event_id}' 不存在，请检查事件ID是否正确"

    @staticmethod
    def event_not_found_by_name(name: str, game_gid: Optional[int] = None) -> str:
        """Event not found by name"""
        if game_gid:
            return f"游戏 {game_gid} 中不存在事件 '{name}'"
        return f"事件 '{name}' 不存在"

    @staticmethod
    def param_not_found(param_id: Any) -> str:
        """Parameter not found"""
        return f"参数ID '{param_id}' 不存在"

    @staticmethod
    def resource_not_found(resource_type: str, identifier: Any) -> str:
        """Generic resource not found"""
        return f"{resource_type} '{identifier}' 不存在"

    # ==================== Business Logic Errors ====================

    @staticmethod
    def game_has_events(game_gid: Any) -> str:
        """Cannot delete game with events"""
        return f"无法删除游戏 '{game_gid}'：该游戏下仍有事件，请先删除所有事件"

    @staticmethod
    def event_has_parameters(event_name: str) -> str:
        """Cannot delete event with parameters"""
        return f"无法删除事件 '{event_name}'：该事件下仍有参数，请先删除所有参数"

    @staticmethod
    def invalid_game_context() -> str:
        """Game context missing"""
        return "缺少游戏上下文，请先选择一个游戏"

    @staticmethod
    def invalid_database_choice(choice: str) -> str:
        """Invalid database choice"""
        return f"无效的数据库选择 '{choice}'，必须为 'ieu_ods' 或 'overseas_ods'"

    # ==================== SQL/HQL Errors ====================

    @staticmethod
    def hql_generation_failed(reason: str = "") -> str:
        """HQL generation failed"""
        if reason:
            return f"HQL生成失败：{reason}"
        return "HQL生成失败，请检查字段配置和WHERE条件"

    @staticmethod
    def invalid_hql_mode(mode: str) -> str:
        """Invalid HQL mode"""
        return f"无效的HQL模式 '{mode}'，应为 'single', 'join', 或 'union'"

    @staticmethod
    def sql_injection_detected() -> str:
        """SQL injection detected"""
        return "检测到潜在的SQL注入攻击，请求已被拒绝"

    # ==================== Network/System Errors ====================

    @staticmethod
    def database_error(operation: str = "操作") -> str:
        """Database operation failed"""
        return f"数据库{operation}失败，请稍后重试或联系管理员"

    @staticmethod
    def network_error() -> str:
        """Network error"""
        return "网络连接失败，请检查网络连接后重试"

    @staticmethod
    def server_error() -> str:
        """Internal server error"""
        return "服务器内部错误，请稍后重试或联系管理员"

    # ==================== File/Import Errors ====================

    @staticmethod
    def invalid_json_format() -> str:
        """Invalid JSON format"""
        return "JSON格式不正确，请检查文件内容"

    @staticmethod
    def missing_required_field_in_json(field_name: str) -> str:
        """Missing required field in JSON"""
        return f"JSON中缺少必填字段：{field_name}"

    @staticmethod
    def invalid_file_format(file_type: str = "文件") -> str:
        """Invalid file format"""
        return f"{file_type}格式不正确，请上传有效的{file_type}文件"

    # ==================== Permission Errors ====================

    @staticmethod
    def unauthorized_access() -> str:
        """Unauthorized access"""
        return "未授权的访问，请先登录"

    @staticmethod
    def forbidden_operation() -> str:
        """Forbidden operation"""
        return "无权限执行此操作"

    # ==================== Rate Limit/Throttling ====================

    @staticmethod
    def too_many_requests() -> str:
        """Too many requests"""
        return "请求过于频繁，请稍后再试"

    # ==================== Generic Errors ====================

    @staticmethod
    def unknown_error() -> str:
        """Unknown error"""
        return "发生未知错误，请稍后重试"


def format_validation_error(field: str, error: str) -> str:
    """Format a validation error for a specific field"""
    return f"{field}验证失败：{error}"


def format_api_error(error: Exception, context: str = "") -> str:
    """
    Format any exception into a user-friendly error message

    Args:
        error: The exception object
        context: Additional context about where the error occurred

    Returns:
        User-friendly error message in Chinese
    """
    error_type = type(error).__name__
    error_msg = str(error)

    # Map common error types to user-friendly messages
    error_mappings = {
        'ValueError': f"参数错误：{error_msg}",
        'KeyError': f"缺少必要参数：{error_msg}",
        'TypeError': f"类型错误：{error_msg}",
        'AttributeError': f"属性错误：{error_msg}",
        'sqlite3.IntegrityError': f"数据完整性错误：{error_msg}",
        'sqlite3.OperationalError': f"数据库操作错误：{error_msg}",
    }

    if error_type in error_mappings:
        message = error_mappings[error_type]
    else:
        message = ErrorMessages.unknown_error()

    if context:
        message = f"{context} - {message}"

    return message


def build_error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    Build a standardized error response

    Args:
        error_type: Error category (e.g., 'validation_error', 'not_found')
        message: User-friendly error message
        details: Additional error details for debugging
        status_code: HTTP status code

    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "error": message,
        "error_type": error_type,
        "timestamp": datetime.now().isoformat(),
    }

    if details:
        response["details"] = details

    return response, status_code


# Convenience functions for common errors

def validation_error(field: str, reason: str, details: Optional[Dict] = None) -> tuple:
    """Validation error (400)"""
    message = format_validation_error(field, reason)
    return build_error_response("validation_error", message, details, 400)


def not_found_error(resource_type: str, identifier: Any, details: Optional[Dict] = None) -> tuple:
    """Resource not found (404)"""
    message = ErrorMessages.resource_not_found(resource_type, identifier)
    return build_error_response("not_found", message, details, 404)


def conflict_error(resource_type: str, identifier: Any, details: Optional[Dict] = None) -> tuple:
    """Resource conflict (409)"""
    message = f"{resource_type} '{identifier}' 已存在"
    return build_error_response("conflict", message, details, 409)


def server_error(message: str = None, details: Optional[Dict] = None) -> tuple:
    """Internal server error (500)"""
    if message is None:
        message = ErrorMessages.server_error()
    return build_error_response("server_error", message, details, 500)
