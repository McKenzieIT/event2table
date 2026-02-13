"""
统一错误处理
"""

from datetime import datetime
from typing import Tuple, Dict, Any


class DWDGeneratorError(Exception):
    """基础错误类"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(DWDGeneratorError):
    """参数验证错误"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class DatabaseError(DWDGeneratorError):
    """数据库操作错误"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class HQLGenerationError(DWDGeneratorError):
    """HQL生成错误"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


def json_error_response(message: str, status_code: int = 400) -> Tuple[Dict[str, Any], int]:
    """
    统一JSON错误响应

    Args:
        message: 错误消息
        status_code: HTTP状态码

    Returns:
        (响应字典, 状态码)
    """
    return {
        "success": False,
        "error": message,
        "timestamp": datetime.now().isoformat(),
    }, status_code


def json_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """
    统一JSON成功响应

    Args:
        data: 响应数据
        message: 成功消息

    Returns:
        响应字典
    """
    response = {"success": True, "timestamp": datetime.now().isoformat()}

    if message:
        response["message"] = message

    if data is not None:
        response["data"] = data

    return response
