"""
HQL模板管理器

管理HQL生成模板, 支持从数据库加载和缓存
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.models.repositories.hql_template_repository import HQLTemplateRepository


class TemplateManager:
    """
    HQL模板管理器

    从数据库加载模板, 提供模板查询和应用功能, 支持缓存
    """

    def __init__(self):
        """初始化模板管理器"""
        self.repo = HQLTemplateRepository()

    def list_templates(
        self,
        template_type: Optional[str] = None,
        is_system: Optional[bool] = None,
        search_keyword: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        列出模板

        Args:
            template_type: 按类型过滤 (union, join, where等)
            is_system: True=仅系统模板, False=仅用户模板, None=全部
            search_keyword: 搜索关键词

        Returns:
            List[Dict]: 模板列表
        """
        # 如果有搜索关键词, 使用搜索
        if search_keyword:
            templates = self.repo.search_by_name(search_keyword)
        # 按类型过滤
        elif template_type:
            templates = self.repo.find_by_type(template_type)
        # 系统模板
        elif is_system is True:
            templates = self.repo.find_system_templates()
        # 用户模板
        elif is_system is False:
            templates = self.repo.find_user_templates()
        # 全部模板
        else:
            templates = self.repo.find_all()

        # 二次过滤(如果需要组合条件)
        if template_type and is_system is not None:
            templates = [t for t in templates if t.get("is_system") == (1 if is_system else 0)]

        return templates

    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取模板

        Args:
            template_id: 模板ID

        Returns:
            Dict: 模板配置, 如果不存在返回None
        """
        return self.repo.find_by_id(template_id)

    def get_template_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        根据名称获取模板

        Args:
            template_name: 模板名称

        Returns:
            Dict: 模板配置, 如果不存在返回None
        """
        return self.repo.find_by_name(template_name)

    def get_template_types(self) -> List[str]:
        """
        获取所有模板类型

        Returns:
            List[str]: 模板类型列表
        """
        return self.repo.get_types()

    def get_popular_templates(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取常用模板（返回系统模板）

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 常用模板列表
        """
        templates = self.repo.find_system_templates()
        return templates[:limit]

    def create_template(
        self,
        template_name: str,
        display_name: str,
        template_type: str,
        template_content: str,
        variables: Optional[Dict[str, Any]] = None,
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
            variables: 变量定义（字典格式）
            description: 描述
            is_system: 是否为系统模板

        Returns:
            新创建的模板ID
        """
        # 将变量字典转为JSON字符串
        variables_json = json.dumps(variables) if variables else None

        return self.repo.create_template(
            template_name=template_name,
            display_name=display_name,
            template_type=template_type,
            template_content=template_content,
            variables=variables_json,
            description=description,
            is_system=is_system,
        )

    def update_template(
        self,
        template_id: int,
        display_name: Optional[str] = None,
        template_content: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
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
        # 将变量字典转为JSON字符串
        variables_json = json.dumps(variables) if variables else None

        return self.repo.update_template(
            template_id=template_id,
            display_name=display_name,
            template_content=template_content,
            variables=variables_json,
            description=description,
        )

    def delete_template(self, template_id: int) -> bool:
        """
        删除模板

        Args:
            template_id: 模板ID

        Returns:
            是否删除成功
        """
        return self.repo.delete_template(template_id)

    def apply_template(
        self, template_id: int, overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        应用模板

        Args:
            template_id: 模板ID
            overrides: 覆盖配置（可选）

        Returns:
            Dict: 完整的生成配置
        """
        template = self.get_template(template_id)

        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # 构建配置
        config = {
            "template_id": template_id,
            "template_name": template["template_name"],
            "display_name": template["display_name"],
            "template_type": template["template_type"],
            "template_content": template["template_content"],
            "variables": json.loads(template["variables"]) if template.get("variables") else {},
            "description": template.get("description", ""),
        }

        # 应用覆盖
        if overrides:
            config = self._deep_merge(config, overrides)

        return config

    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索模板

        Args:
            query: 搜索关键词

        Returns:
            List[Dict]: 匹配的模板列表
        """
        return self.list_templates(search_keyword=query)

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result


# 便捷函数
def list_templates(
    template_type: Optional[str] = None,
    is_system: Optional[bool] = None,
    search_keyword: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    列出模板（便捷函数）

    Args:
        template_type: 按类型过滤
        is_system: True=仅系统模板, False=仅用户模板
        search_keyword: 搜索关键词

    Returns:
        List[Dict]: 模板列表
    """
    manager = TemplateManager()
    return manager.list_templates(
        template_type=template_type,
        is_system=is_system,
        search_keyword=search_keyword,
    )


def get_template(template_id: int) -> Optional[Dict[str, Any]]:
    """
    获取模板（便捷函数）

    Args:
        template_id: 模板ID

    Returns:
        Dict: 模板配置
    """
    manager = TemplateManager()
    return manager.get_template(template_id)


def get_template_by_name(template_name: str) -> Optional[Dict[str, Any]]:
    """
    根据名称获取模板（便捷函数）

    Args:
        template_name: 模板名称

    Returns:
        Dict: 模板配置
    """
    manager = TemplateManager()
    return manager.get_template_by_name(template_name)


# 导出
__all__ = [
    "TemplateManager",
    "list_templates",
    "get_template",
    "get_template_by_name",
]
