#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON字段序列化辅助函数

用于处理Entity模型中的JSON字段:
- serialize_json_field: 将Dict/List序列化为JSON字符串（存储到数据库）
- deserialize_json_field: 将JSON字符串反序列化为Dict/List（从数据库读取）

用途:
- FlowEntity.flow_graph / variables
- EventNodeEntity.config
- HQLHistoryEntity.events / fields / conditions / metadata
"""

import json
from typing import Dict, List, Any, Union, Optional


def serialize_json_field(value: Union[Dict, List, str, None]) -> Optional[str]:
    """
    序列化JSON字段为字符串（用于存储到数据库）

    Args:
        value: 要序列化的值（Dict, List, 或已序列化的字符串）

    Returns:
        JSON字符串，None返回None

    Examples:
        >>> serialize_json_field({"key": "value"})
        '{"key": "value"}'

        >>> serialize_json_field([1, 2, 3])
        '[1, 2, 3]'

        >>> serialize_json_field(None)
        None
    """
    if value is None:
        return None
    if isinstance(value, str):
        # 已经是字符串，直接返回
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    # 其他类型（如int, float）转为字符串
    return str(value)


def deserialize_json_field(value: Union[str, Dict, List, None]) -> Union[Dict, List, None]:
    """
    反序列化JSON字段（从数据库读取）

    Args:
        value: 要反序列化的值（JSON字符串或已反序列化的对象）

    Returns:
        Dict或List对象，None返回None，解析失败返回空Dict

    Examples:
        >>> deserialize_json_field('{"key": "value"}')
        {'key': 'value'}

        >>> deserialize_json_field('[1, 2, 3]')
        [1, 2, 3]

        >>> deserialize_json_field(None)
        None

        >>> deserialize_json_field('invalid json')
        {}
    """
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        # 已经是反序列化对象，直接返回
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # 解析失败，返回空字典
            return {}
    # 其他类型，返回空字典
    return {}


# 保留旧函数以保持向后兼容
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
