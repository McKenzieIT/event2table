#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Template Repository (参数模板数据访问层)

提供参数模板相关的数据访问方法
- 返回统一字典模型
- 移除直接数据库访问
- 保持GenericRepository继承
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict


class ParamTemplateRepository(GenericRepository):
    """
    参数模板仓储类

    继承 GenericRepository 并添加参数模板特定的查询方法
    """

    def __init__(self):
        """
        初始化参数模板仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="param_templates",
            primary_key="id",
            enable_cache=True,
            cache_timeout=1800,  # 30分钟缓存（模板变化很少）
        )

    def find_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        根据模板名查找模板

        Args:
            template_name: 模板名

        Returns:
            模板字典，不存在返回None

        Example:
            >>> repo = ParamTemplateRepository()
            >>> template = repo.find_by_name('string')
        """
        query = "SELECT * FROM param_templates WHERE template_name = ?"
        return fetch_one_as_dict(query, (template_name,))

    def get_all_templates(self, include_system: bool = True) -> List[Dict[str, Any]]:
        """
        获取所有类型模板

        Args:
            include_system: 是否包含系统模板

        Returns:
            模板字典列表

        Example:
            >>> repo = ParamTemplateRepository()
            >>> templates = repo.get_all_templates(include_system=True)
        """
        query = "SELECT * FROM param_templates"
        if not include_system:
            query += " WHERE is_system = 0"
        query += " ORDER BY base_type, nesting_level, template_name"
        return fetch_all_as_dict(query)

    def get_templates_by_type(
        self, base_type: str, include_system: bool = True
    ) -> List[Dict[str, Any]]:
        """
        根据基础类型获取模板

        Args:
            base_type: 基础类型 (string, int, array, map等)
            include_system: 是否包含系统模板

        Returns:
            模板字典列表

        Example:
            >>> repo = ParamTemplateRepository()
            >>> templates = repo.get_templates_by_type('array')
        """
        query = "SELECT * FROM param_templates WHERE base_type = ?"
        if not include_system:
            query += " AND is_system = 0"
        query += " ORDER BY nesting_level, template_name"
        return fetch_all_as_dict(query, (base_type,))

    def get_primitive_types(self) -> List[Dict[str, Any]]:
        """
        获取所有基础类型

        Returns:
            基础类型模板列表

        Example:
            >>> repo = ParamTemplateRepository()
            >>> primitives = repo.get_primitive_types()
        """
        query = """
            SELECT * FROM param_templates
            WHERE base_type IN ('string', 'int', 'bigint', 'float', 'double', 'boolean', 'datetime')
            ORDER BY template_name
        """
        return fetch_all_as_dict(query)

    def get_complex_types(self) -> List[Dict[str, Any]]:
        """
        获取所有复杂类型（array, map）

        Returns:
            复杂类型模板列表

        Example:
            >>> repo = ParamTemplateRepository()
            >>> complex_types = repo.get_complex_types()
        """
        query = """
            SELECT * FROM param_templates
            WHERE base_type IN ('array', 'map')
            ORDER BY base_type, nesting_level, template_name
        """
        return fetch_all_as_dict(query)

    def get_custom_templates(self) -> List[Dict[str, Any]]:
        """
        获取所有自定义模板

        Returns:
            自定义模板列表

        Example:
            >>> repo = ParamTemplateRepository()
            >>> customs = repo.get_custom_templates()
        """
        query = """
            SELECT * FROM param_templates
            WHERE is_system = 0
            ORDER BY base_type, template_name
        """
        return fetch_all_as_dict(query)

    def create_template(
        self,
        template_name: str,
        display_name: str,
        base_type: str,
        type_definition: Dict[str, Any],
        hql_parse_template: str = "",
        description: str = "",
        element_type: Optional[str] = None,
        nesting_level: int = 1,
    ) -> int:
        """
        创建自定义类型模板

        Args:
            template_name: 模板名
            display_name: 显示名称
            base_type: 基础类型
            type_definition: 类型定义字典
            hql_parse_template: HQL解析模板
            description: 描述
            element_type: 元素类型（用于array/map）
            nesting_level: 嵌套层级

        Returns:
            创建的模板ID

        Example:
            >>> repo = ParamTemplateRepository()
            >>> template_id = repo.create_template('custom', '自定义', 'string', {...})
        """
        import json
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 生成HQL解析模板（如果未提供）
            if not hql_parse_template:
                hql_parse_template = self._generate_hql_template(type_definition)

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
                    base_type,
                    element_type,
                    nesting_level,
                    json.dumps(type_definition, ensure_ascii=False),
                    hql_parse_template,
                    description,
                ),
            )

            template_id = cursor.lastrowid
            conn.commit()
            return template_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update_template(
        self,
        template_id: int,
        display_name: Optional[str] = None,
        hql_parse_template: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """
        更新模板

        Args:
            template_id: 模板ID
            display_name: 新的显示名称（可选）
            hql_parse_template: 新的HQL解析模板（可选）
            description: 新的描述（可选）

        Returns:
            是否更新成功

        Example:
            >>> repo = ParamTemplateRepository()
            >>> success = repo.update_template(1, display_name='新名称')
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 构建更新字段
            update_fields = []
            update_values = []

            if display_name is not None:
                update_fields.append("display_name = ?")
                update_values.append(display_name)

            if hql_parse_template is not None:
                update_fields.append("hql_parse_template = ?")
                update_values.append(hql_parse_template)

            if description is not None:
                update_fields.append("description = ?")
                update_values.append(description)

            if update_fields:
                update_values.append(template_id)

                query = f"""
                    UPDATE param_templates
                    SET {', '.join(update_fields)}
                    WHERE id = ? AND is_system = 0
                """
                cursor.execute(query, tuple(update_values))
                conn.commit()
                return cursor.rowcount > 0

            return False

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_template(self, template_id: int) -> bool:
        """
        删除模板（仅限自定义模板）

        Args:
            template_id: 模板ID

        Returns:
            是否删除成功

        Example:
            >>> repo = ParamTemplateRepository()
            >>> success = repo.delete_template(1)
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 只能删除非系统模板
            cursor.execute(
                "DELETE FROM param_templates WHERE id = ? AND is_system = 0",
                (template_id,),
            )
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count > 0
        finally:
            conn.close()

    def find_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID查询模板

        Args:
            template_id: 模板ID

        Returns:
            模板字典，不存在返回None

        Example:
            >>> repo = ParamTemplateRepository()
            >>> template = repo.find_by_id(1)
        """
        query = "SELECT * FROM param_templates WHERE id = ?"
        return fetch_one_as_dict(query, (template_id,))

    def get_available_types_grouped(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取可用的类型列表（分组）

        Returns:
            分组的类型列表

        Example:
            >>> repo = ParamTemplateRepository()
            >>> grouped = repo.get_available_types_grouped()
        """
        templates = self.get_all_templates()

        grouped = {
            "基础类型": [],
            "数组类型": [],
            "Map类型": [],
            "复杂嵌套": [],
            "自定义": [],
        }

        primitive_types = ["string", "int", "bigint", "float", "double", "boolean", "datetime"]

        for t in templates:
            if t["base_type"] in primitive_types:
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

    def _generate_hql_template(self, type_def: Dict[str, Any]) -> str:
        """
        根据类型定义自动生成HQL解析模板

        Args:
            type_def: 类型定义字典

        Returns:
            HQL解析模板字符串
        """
        type_name = type_def.get("type", "string")

        if type_name == "primitive":
            return "get_json_object(params, '$.{param_name}')"
        elif type_name == "array":
            return "get_json_object(params, '$.{param_name}')"
        elif type_name == "map":
            return "get_json_object(params, '$.{param_name}')"
        else:
            return "get_json_object(params, '$.{param_name}')"

    def template_exists(self, template_name: str) -> bool:
        """
        检查模板是否存在

        Args:
            template_name: 模板名

        Returns:
            是否存在

        Example:
            >>> repo = ParamTemplateRepository()
            >>> exists = repo.template_exists('string')
        """
        template = self.find_by_name(template_name)
        return template is not None

    def get_cast_type(self, template_id: int) -> str:
        """
        获取模板对应的CAST类型

        Args:
            template_id: 模板ID

        Returns:
            SQL CAST类型字符串

        Example:
            >>> repo = ParamTemplateRepository()
            >>> cast_type = repo.get_cast_type(1)
        """
        template = self.find_by_id(template_id)
        if not template:
            return ""

        base_type = template.get("base_type", "")
        cast_map = {
            "int": "INT",
            "bigint": "BIGINT",
            "float": "FLOAT",
            "double": "DOUBLE",
            "boolean": "BOOLEAN",
        }
        return cast_map.get(base_type, "")

    def needs_cast(self, template_id: int) -> bool:
        """
        判断模板类型是否需要CAST转换

        Args:
            template_id: 模板ID

        Returns:
            是否需要CAST

        Example:
            >>> repo = ParamTemplateRepository()
            >>> needs = repo.needs_cast(1)
        """
        template = self.find_by_id(template_id)
        if not template:
            return False

        base_type = template.get("base_type", "")
        return base_type in ["int", "bigint", "float", "double", "boolean"]
