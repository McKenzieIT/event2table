#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Type Manager
Handles parameter type templates and type-related operations
"""

import json
import re
from typing import Dict, List, Optional, Any
from functools import lru_cache
from backend.core.database import get_db
from backend.core.logging import get_logger
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict, execute_write

logger = get_logger(__name__)


class ParamTypeManager:
    """Parameter type template management"""

    # 基础类型定义
    PRIMITIVE_TYPES = ["string", "int", "bigint", "float", "double", "boolean", "datetime"]

    # 复杂类型定义
    COMPLEX_TYPES = ["array", "map"]

    def __init__(self):
        """Initialize type manager"""
        pass

    def get_all_templates(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """获取所有类型模板（带缓存）"""
        return _get_all_templates_cached(include_system)

    def get_template_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取类型模板（带缓存）"""
        return _get_template_by_name_cached(template_name)

    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取类型模板（带缓存）"""
        return _get_template_by_id_cached(template_id)

    def create_template(self, template_data: Dict[str, Any]) -> int:
        """创建自定义类型模板"""
        from backend.core.database import get_db_connection

        # 解析类型定义
        type_def = json.loads(template_data["type_definition"])

        # 自动生成HQL解析模板
        if "hql_parse_template" not in template_data or not template_data["hql_parse_template"]:
            template_data["hql_parse_template"] = self._generate_hql_template(type_def)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO param_templates
            (template_name, display_name, base_type, element_type, nesting_level,
             type_definition, hql_parse_template, description, is_system)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """,
            (
                template_data["template_name"],
                template_data["display_name"],
                type_def.get("base_type", type_def.get("type")),
                type_def.get("element_type"),
                type_def.get("nesting_level", 1),
                template_data["type_definition"],
                template_data["hql_parse_template"],
                template_data.get("description", ""),
            ),
        )

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"Created custom template: {template_data['template_name']}")
        return template_id

    def _generate_hql_template(self, type_def: Dict[str, Any]) -> str:
        """根据类型定义自动生成HQL解析模板"""
        type_name = type_def.get("type", "string")

        if type_name == "primitive":
            # 基础类型
            return "get_json_object(params, '$.{param_name}')"

        elif type_name == "array":
            # 数组类型
            element_type = type_def.get("element_type", "string")
            if element_type == "map":
                return "get_json_object(params, '$.{param_name}')"
            else:
                return f"get_json_object(params, '$.{param_name}')"

        elif type_name == "map":
            # Map类型
            return "get_json_object(params, '$.{param_name}')"

        else:
            # 默认
            return "get_json_object(params, '$.{param_name}')"

    def parse_type_string(self, type_str: str) -> Dict[str, Any]:
        """解析类型字符串 (如 'array<string>', 'map<string,int>')

        Args:
            type_str: 类型字符串，如 'array<string>', 'map<string,int>', 'array<map<string,int>>'

        Returns:
            类型定义字典
        """
        type_str = type_str.strip()

        # 基础类型
        if type_str in self.PRIMITIVE_TYPES or type_str in ["map"]:
            return {"type": type_str, "base_type": type_str, "nesting_level": 1}

        # 复杂类型: array<T>, map<K,V>
        if "<" in type_str and ">" in type_str:
            base_type = type_str.split("<")[0]
            inner = type_str[type_str.find("<") + 1 : type_str.rfind(">")]

            result = {"type": base_type, "base_type": base_type, "nesting_level": 1}

            if base_type == "array":
                result["element_type"] = inner.strip()
                # 检查嵌套
                if "<" in inner:
                    result["nesting_level"] = 2

            elif base_type == "map":
                if "," in inner:
                    key_type, value_type = [t.strip() for t in inner.split(",", 1)]
                    result["key_type"] = key_type
                    result["value_type"] = value_type

            return result

        # 默认视为string
        return {"type": "string", "base_type": "string", "nesting_level": 1}

    def validate_type_definition(self, type_def: Dict[str, Any]) -> tuple[bool, str]:
        """验证类型定义是否合法

        Args:
            type_def: 类型定义字典

        Returns:
            (是否合法, 错误信息)
        """
        type_name = type_def.get("type")

        if not type_name:
            return False, "缺少type字段"

        if type_name in self.PRIMITIVE_TYPES:
            return True, ""

        if type_name == "array":
            element_type = type_def.get("element_type")
            if not element_type:
                return False, "array类型必须指定element_type"
            return True, ""

        if type_name == "map":
            # Map类型可选key_type和value_type
            return True, ""

        return False, f"未知类型: {type_name}"

    def get_available_types(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取可用的类型列表（分组）

        Returns:
            分组的类型列表
        """
        templates = self.get_all_templates()

        grouped = {"基础类型": [], "数组类型": [], "Map类型": [], "复杂嵌套": [], "自定义": []}

        for t in templates:
            if t["base_type"] in self.PRIMITIVE_TYPES:
                grouped["基础类型"].append(t)
            elif t["base_type"] == "array":
                if t["nesting_level"] == 1:
                    grouped["数组类型"].append(t)
                else:
                    grouped["复杂嵌套"].append(t)
            elif t["base_type"] == "map":
                grouped["Map类型"].append(t)
            elif not t["is_system"]:
                grouped["自定义"].append(t)

        return grouped

    def get_cast_type(self, param_type: str) -> str:
        """获取参数对应的CAST类型

        Args:
            param_type: 参数类型，如 'int', 'bigint', 'float'

        Returns:
            SQL CAST类型字符串
        """
        cast_map = {
            "int": "INT",
            "bigint": "BIGINT",
            "float": "FLOAT",
            "double": "DOUBLE",
            "boolean": "BOOLEAN",
        }
        return cast_map.get(param_type, "")

    def needs_cast(self, param_type: str) -> bool:
        """判断参数类型是否需要CAST转换"""
        return param_type in ["int", "bigint", "float", "double", "boolean"]

    def format_param_field(self, param_name: str, param_type: str, param_name_cn: str = "") -> str:
        """格式化参数字段为HQL

        Args:
            param_name: 参数名
            param_type: 参数类型
            param_name_cn: 参数中文名

        Returns:
            HQL字段定义字符串
        """
        comment = param_name_cn or param_name

        if self.needs_cast(param_type):
            cast_type = self.get_cast_type(param_type)
            return f"CAST(get_json_object(params, '$.{param_name}') AS {cast_type}) AS {param_name} COMMENT '{comment}'"
        else:
            return f"get_json_object(params, '$.{param_name}') AS {param_name} COMMENT '{comment}'"

    def create_complex_type_template(self, type_str: str) -> Optional[int]:
        """创建复杂类型模板（如 array<map<string,int>>）

        Args:
            type_str: 类型字符串，如 'array<map<string,int>>'

        Returns:
            创建的模板ID，失败返回None
        """
        from backend.core.database import get_db_connection

        # 解析类型定义
        type_def = self.parse_type_string(type_str)

        # 生成模板名称
        template_name = type_str.replace(" ", "")

        # 检查是否已存在
        existing = self.get_template_by_name(template_name)
        if existing:
            return existing["id"]

        # 生成显示名称
        if type_def["type"] == "array":
            element_type = type_def.get("element_type", "unknown")
            display_name = f"{element_type}数组"
        elif type_def["type"] == "map":
            display_name = "Map对象"
        else:
            display_name = template_name

        # 类型定义JSON
        type_definition = json.dumps(type_def, ensure_ascii=False)

        # 生成HQL解析模板
        hql_template = self._generate_hql_template(type_def)

        # 插入数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO param_templates
                (template_name, display_name, base_type, element_type, nesting_level,
                 type_definition, hql_parse_template, description, is_system)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
                (
                    template_name,
                    display_name,
                    type_def["type"],
                    type_def.get("element_type"),
                    type_def.get("nesting_level", 1),
                    type_definition,
                    hql_template,
                    f"自定义复杂类型: {template_name}",
                ),
            )

            template_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Created complex type template: {template_name}")
            return template_id
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create complex type template {template_name}: {e}")
            return None
        finally:
            conn.close()

    def parse_complex_type(self, type_str: str) -> Dict[str, Any]:
        """解析复杂类型字符串，返回完整结构

        Args:
            type_str: 类型字符串，如 'array<map<string,int>>'

        Returns:
            完整的类型定义字典
        """
        result = self.parse_type_string(type_str)

        # 对于嵌套类型，递归解析内部类型
        if result.get("type") == "array":
            element_type = result.get("element_type", "")
            if "<" in element_type and ">" in element_type:
                # 嵌套类型，如 array<map<string,int>>
                inner_def = self.parse_complex_type(element_type)
                result["element_definition"] = inner_def

        return result


# Module-level cached functions (to work with singleton pattern)
@lru_cache(maxsize=8)
def _get_all_templates_cached(include_system: bool = True) -> List[Dict[str, Any]]:
    """获取所有类型模板（缓存层）"""
    query = "SELECT * FROM param_templates"
    if not include_system:
        query += " WHERE is_system = 0"
    query += " ORDER BY base_type, nesting_level, template_name"
    return fetch_all_as_dict(query)


@lru_cache(maxsize=32)
def _get_template_by_name_cached(template_name: str) -> Optional[Dict[str, Any]]:
    """根据名称获取类型模板（缓存层）"""
    return fetch_one_as_dict(
        "SELECT * FROM param_templates WHERE template_name = ?", (template_name,)
    )


@lru_cache(maxsize=32)
def _get_template_by_id_cached(template_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取类型模板（缓存层）"""
    return fetch_one_as_dict("SELECT * FROM param_templates WHERE id = ?", (template_id,))


# Singleton instance
param_type_manager = ParamTypeManager()
