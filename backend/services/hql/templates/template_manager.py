"""
HQL模板管理器

管理预定义的HQL模板，支持快速加载和配置
"""

import yaml
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class TemplateManager:
    """
    HQL模板管理器

    从YAML文件加载模板，提供模板查询和应用功能
    """

    def __init__(self, template_file: Optional[str] = None):
        """
        初始化模板管理器

        Args:
            template_file: 模板文件路径（可选）
        """
        if template_file is None:
            # 默认模板文件路径
            current_dir = Path(__file__).parent
            template_file = current_dir / "hql_templates.yaml"

        self.template_file = template_file
        self.templates = []
        self.categories = {}
        self.tags = {}

        self._load_templates()

    def _load_templates(self):
        """从YAML文件加载模板"""
        if not os.path.exists(self.template_file):
            return

        with open(self.template_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.templates = data.get("templates", [])
        self.categories = {cat["id"]: cat for cat in data.get("categories", [])}
        self.tags = {tag["id"]: tag for tag in data.get("tags", [])}

    def list_templates(
        self, category: Optional[str] = None, tag: Optional[str] = None, popular_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        列出模板

        Args:
            category: 按类别过滤
            tag: 按标签过滤
            popular_only: 只返回热门模板

        Returns:
            List[Dict]: 模板列表
        """
        templates = self.templates

        # 过滤条件
        if popular_only:
            templates = [t for t in templates if t.get("popular", False)]

        if category:
            templates = [t for t in templates if t.get("category") == category]

        if tag:
            # TODO: 实现标签过滤
            pass

        return templates

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模板

        Args:
            template_id: 模板ID

        Returns:
            Dict: 模板配置，如果不存在返回None
        """
        for template in self.templates:
            if template["id"] == template_id:
                return template
        return None

    def apply_template(
        self, template_id: str, overrides: Optional[Dict[str, Any]] = None
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

        # 获取默认配置
        config = template.get("default_config", {})

        # 应用覆盖
        if overrides:
            config = self._deep_merge(config, overrides)

        return {
            "template_id": template_id,
            "template_name": template["name"],
            "template_category": template.get("category"),
            "config": config,
        }

    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索模板

        Args:
            query: 搜索关键词

        Returns:
            List[Dict]: 匹配的模板列表
        """
        query_lower = query.lower()

        matches = []
        for template in self.templates:
            # 在名称、描述、ID中搜索
            if (
                query_lower in template["id"].lower()
                or query_lower in template["name"].lower()
                or query_lower in template["description"].lower()
            ):
                matches.append(template)

        return matches

    def get_categories(self) -> List[Dict[str, Any]]:
        """获取所有模板分类"""
        return list(self.categories.values())

    def get_popular_templates(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        获取热门模板

        Args:
            limit: 返回数量限制

        Returns:
            List[Dict]: 热门模板列表
        """
        popular = [t for t in self.templates if t.get("popular", False)]
        return popular[:limit]

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
    category: Optional[str] = None, popular_only: bool = False
) -> List[Dict[str, Any]]:
    """
    列出模板（便捷函数）

    Args:
        category: 按类别过滤
        popular_only: 只返回热门模板

    Returns:
        List[Dict]: 模板列表
    """
    manager = TemplateManager()
    return manager.list_templates(category=category, popular_only=popular_only)


def get_template(template_id: str) -> Optional[Dict[str, Any]]:
    """
    获取模板（便捷函数）

    Args:
        template_id: 模板ID

    Returns:
        Dict: 模板配置
    """
    manager = TemplateManager()
    return manager.get_template(template_id)


# 导出
__all__ = ["TemplateManager", "list_templates", "get_template"]
