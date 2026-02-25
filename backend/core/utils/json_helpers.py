"""
JSON辅助函数
"""

import json
from typing import Dict, Any, Optional


def parse_config_json(config_str: Optional[str]) -> Dict[str, Any]:
    """
    安全的JSON配置解析

    Args:
        config_str: JSON字符串

    Returns:
        解析后的字典，解析失败返回空字典
    """
    if not config_str:
        return {}

    try:
        return json.loads(config_str)
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    安全的JSON序列化

    Args:
        obj: 要序列化的对象
        default: 序列化失败时返回的默认值

    Returns:
        JSON字符串
    """
    try:
        return json.dumps(obj, ensure_ascii=False)
    except (TypeError, ValueError):
        return default


def merge_json_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个JSON配置

    后面的配置会覆盖前面的
    """
    result = {}
    for config in configs:
        if config:
            result.update(config)
    return result
