from backend.core.cache.decorators import cached

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Template Repository (HQL模板仓储层)

提供HQL生成模板的数据访问操作
"""

from typing import List, Optional, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.core.utils import execute_write


class HQLTemplateRepository(GenericRepository):
    """
    HQL模板仓储类

    提供HQL生成模板表的CRUD操作和特定查询方法
    """

    def __init__(self):
        """初始化HQL模板仓储"""
        super().__init__(table_name="hql_generation_templates")

    def find_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        根据模板名称获取模板

        Args:
            template_name: 模板名称

        Returns:
            模板字典，不存在返回None
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE template_name = ?
        """
        return fetch_one_as_dict(query, (template_name,))

    def find_by_type(self, template_type: str) -> List[Dict[str, Any]]:
        """
        根据模板类型获取模板列表

        Args:
            template_type: 模板类型 (union, join, where等)

        Returns:
            模板字典列表
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE template_type = ?
            ORDER BY display_name
        """
        return fetch_all_as_dict(query, (template_type,))


@cached(ttl=1800)
    def find_system_templates(self) -> List[Dict[str, Any]]:
        """
        获取所有系统模板

        Returns:
            系统模板字典列表
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE is_system = 1
            ORDER BY template_type, display_name
        """
        return fetch_all_as_dict(query)


@cached(ttl=1800)
    def find_user_templates(self) -> List[Dict[str, Any]]:
        """
        获取所有用户自定义模板

        Returns:
            用户模板字典列表
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE is_system = 0
            ORDER BY created_at DESC
        """
        return fetch_all_as_dict(query)

    def search_by_name(self, keyword: str) -> List[Dict[str, Any]]:
        """
        根据关键词搜索模板

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的模板字典列表
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE template_name LIKE ?
               OR display_name LIKE ?
               OR description LIKE ?
            ORDER BY template_type, display_name
        """
        pattern = f"%{keyword}%"
        return fetch_all_as_dict(query, (pattern, pattern, pattern))


@cached(ttl=1800)
    def get_types(self) -> List[str]:
        """
        获取所有模板类型

        Returns:
            模板类型列表
        """
        query = f"""
            SELECT DISTINCT template_type
            FROM {self.table_name}
            ORDER BY template_type
        """
        results = fetch_all_as_dict(query)
        return [row["template_type"] for row in results]

    def create_template(
        self,
        template_name: str,
        display_name: str,
        template_type: str,
        template_content: str,
        variables: Optional[str] = None,
        description: Optional[str] = None,
        is_system: bool = False,
    ) -> int:
        """
        创建新模板

        Args:
            template_name: 模板名称（唯一）
            display_name: 显示名称
            template_type: 模板类型
            template_content: 模板内容
            variables: 变量定义（JSON格式）
            description: 描述
            is_system: 是否为系统模板

        Returns:
            新创建的模板ID
        """
        data = {
            "template_name": template_name,
            "display_name": display_name,
            "template_type": template_type,
            "template_content": template_content,
            "variables": variables,
            "description": description,
            "is_system": 1 if is_system else 0,
        }
        return self.create(data)

    def update_template(
        self,
        template_id: int,
        display_name: Optional[str] = None,
        template_content: Optional[str] = None,
        variables: Optional[str] = None,
        description: Optional[str] = None,
    ) -> bool:
        """
        更新模板

        Args:
            template_id: 模板ID
            display_name: 显示名称
            template_content: 模板内容
            variables: 变量定义
            description: 描述

        Returns:
            是否更新成功
        """
        updates = {}
        if display_name is not None:
            updates["display_name"] = display_name
        if template_content is not None:
            updates["template_content"] = template_content
        if variables is not None:
            updates["variables"] = variables
        if description is not None:
            updates["description"] = description

        if not updates:
            return False

        updates["updated_at"] = "CURRENT_TIMESTAMP"

        return self.update(template_id, updates)

    def delete_template(self, template_id: int) -> bool:
        """
        删除模板

        Args:
            template_id: 模板ID

        Returns:
            是否删除成功
        """
        # 不允许删除系统模板
        template = self.find_by_id(template_id)
        if not template:
            return False
        if template.get("is_system") == 1:
            raise ValueError("Cannot delete system template")

        return self.delete(template_id)
