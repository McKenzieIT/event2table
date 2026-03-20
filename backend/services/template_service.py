#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Template Service (HQL模板业务逻辑层)

提供HQL模板库的业务逻辑封装:
- 模板分类管理
- 模板搜索功能
- 模板导入导出
- 模板使用统计
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.cache.decorators import cached_service, invalidate_cache
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict
from backend.services.base_service import BaseService

logger = logging.getLogger(__name__)


class TemplateService(BaseService):
    """
    HQL模板业务服务

    职责:
    - 模板业务逻辑封装
    - 模板分类管理
    - 模板搜索和过滤
    - 模板导入导出
    - 使用统计
    """

    def __init__(self):
        """初始化模板服务"""
        super().__init__()
        logger.info("✅ TemplateService initialized")

    @cached_service(key_template="templates:categories", ttl_l1=1800, ttl_l2=3600)
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有模板分类

        Returns:
            分类字典列表, 包含模板数量和使用统计
        """
        query = """
            SELECT 
                category,
                COUNT(*) as template_count,
                SUM(usage_count) as total_usage
            FROM hql_templates
            WHERE is_active = 1
            GROUP BY category
            ORDER BY total_usage DESC
        """
        return fetch_all_as_dict(query)

    @cached_service(
        key_template="templates:subcategories:{category}",
        ttl_l1=1800,
        ttl_l2=3600,
        key_params=['category']
    )
    def get_subcategories(self, category: str) -> List[str]:
        """
        获取指定分类的所有子分类

        Args:
            category: 模板分类

        Returns:
            子分类列表
        """
        query = """
            SELECT DISTINCT subcategory
            FROM hql_templates
            WHERE category = ? AND is_active = 1 AND subcategory IS NOT NULL
            ORDER BY subcategory
        """
        results = fetch_all_as_dict(query, (category,))
        return [row['subcategory'] for row in results if row['subcategory']]

    def search_templates(
        self,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        tags: Optional[List[str]] = None,
        game_gid: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        搜索模板

        Args:
            keyword: 搜索关键词
            category: 分类过滤
            subcategory: 子分类过滤
            tags: 标签过滤
            game_gid: 游戏GID过滤
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            搜索结果字典
        """
        conditions = ["is_active = 1"]
        params = []

        if keyword:
            conditions.append("(name LIKE ? OR display_name LIKE ? OR description LIKE ?)")
            pattern = f"%{keyword}%"
            params.extend([pattern, pattern, pattern])

        if category:
            conditions.append("category = ?")
            params.append(category)

        if subcategory:
            conditions.append("subcategory = ?")
            params.append(subcategory)

        if game_gid:
            conditions.append("(game_gid = ? OR game_gid IS NULL)")
            params.append(game_gid)

        if tags:
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")

        where_clause = " AND ".join(conditions)

        # 获取总数
        count_query = f"""
            SELECT COUNT(*) as total
            FROM hql_templates
            WHERE {where_clause}
        """
        count_result = fetch_one_as_dict(count_query, tuple(params))
        total = count_result['total'] if count_result else 0

        # 获取模板列表
        query = f"""
            SELECT * FROM hql_templates
            WHERE {where_clause}
            ORDER BY usage_count DESC, created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        templates = fetch_all_as_dict(query, tuple(params))

        return {
            'templates': templates,
            'total': total,
            'limit': limit,
            'offset': offset
        }

    @cached_service(key_template="templates:popular", ttl_l1=1800, ttl_l2=3600)
    def get_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取热门模板

        Args:
            limit: 返回数量

        Returns:
            热门模板字典列表
        """
        query = """
            SELECT * FROM hql_templates
            WHERE is_active = 1 AND usage_count > 0
            ORDER BY usage_count DESC, last_used_at DESC
            LIMIT ?
        """
        return fetch_all_as_dict(query, (limit,))

    @cached_service(key_template="templates:featured", ttl_l1=1800, ttl_l2=3600)
    def get_featured_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取精选模板

        Args:
            limit: 返回数量

        Returns:
            精选模板字典列表
        """
        query = """
            SELECT * FROM hql_templates
            WHERE is_active = 1 AND is_featured = 1
            ORDER BY usage_count DESC
            LIMIT ?
        """
        return fetch_all_as_dict(query, (limit,))

    def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取模板

        Args:
            template_id: 模板ID

        Returns:
            模板字典, 不存在返回None
        """
        query = "SELECT * FROM hql_templates WHERE id = ?"
        return fetch_one_as_dict(query, (template_id,))

    def increment_usage(self, template_id: int) -> bool:
        """
        增加模板使用次数

        Args:
            template_id: 模板ID

        Returns:
            是否成功
        """
        from backend.core.utils import execute_write
        
        query = """
            UPDATE hql_templates
            SET usage_count = usage_count + 1,
                last_used_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        result = execute_write(query, (template_id,))
        
        # 清除缓存
        if result > 0:
            self.invalidate_pattern("templates:*")
        
        return result > 0

    def create_template(self, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        创建新模板

        Args:
            template_data: 模板数据字典

        Returns:
            创建的模板字典, 失败返回None
        """
        from backend.core.utils import execute_write
        
        # 序列化JSON字段
        tags_json = json.dumps(template_data.get('tags', []), ensure_ascii=False)
        variables_json = json.dumps(template_data.get('variables', {}), ensure_ascii=False)
        
        query = """
            INSERT INTO hql_templates (
                name, display_name, category, subcategory,
                hql_content, variables, description, tags,
                game_gid, is_featured, is_system, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            template_data.get('name'),
            template_data.get('display_name'),
            template_data.get('category'),
            template_data.get('subcategory'),
            template_data.get('hql_content'),
            variables_json,
            template_data.get('description'),
            tags_json,
            template_data.get('game_gid'),
            1 if template_data.get('is_featured', False) else 0,
            1 if template_data.get('is_system', False) else 0,
            1 if template_data.get('is_active', True) else 0,
        )
        
        try:
            result = execute_write(query, params)
            if result > 0:
                # 清除缓存
                self.invalidate_pattern("templates:*")
                return self.get_template_by_id(result)
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
        
        return None

    def update_template(self, template_id: int, template_data: Dict[str, Any]) -> bool:
        """
        更新模板

        Args:
            template_id: 模板ID
            template_data: 更新数据字典

        Returns:
            是否成功
        """
        from backend.core.utils import execute_write
        
        updates = []
        params = []
        
        if 'display_name' in template_data:
            updates.append("display_name = ?")
            params.append(template_data['display_name'])
        
        if 'hql_content' in template_data:
            updates.append("hql_content = ?")
            params.append(template_data['hql_content'])
        
        if 'description' in template_data:
            updates.append("description = ?")
            params.append(template_data['description'])
        
        if 'category' in template_data:
            updates.append("category = ?")
            params.append(template_data['category'])
        
        if 'subcategory' in template_data:
            updates.append("subcategory = ?")
            params.append(template_data['subcategory'])
        
        if 'tags' in template_data:
            updates.append("tags = ?")
            params.append(json.dumps(template_data['tags'], ensure_ascii=False))
        
        if 'variables' in template_data:
            updates.append("variables = ?")
            params.append(json.dumps(template_data['variables'], ensure_ascii=False))
        
        if 'is_featured' in template_data:
            updates.append("is_featured = ?")
            params.append(1 if template_data['is_featured'] else 0)
        
        if 'is_active' in template_data:
            updates.append("is_active = ?")
            params.append(1 if template_data['is_active'] else 0)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(template_id)
        
        query = f"UPDATE hql_templates SET {', '.join(updates)} WHERE id = ?"
        
        try:
            result = execute_write(query, tuple(params))
            if result > 0:
                # 清除缓存
                self.invalidate_pattern("templates:*")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to update template: {e}")
            return False

    def delete_template(self, template_id: int) -> bool:
        """
        删除模板

        Args:
            template_id: 模板ID

        Returns:
            是否成功
        """
        from backend.core.utils import execute_write
        
        # 检查是否为系统模板
        template = self.get_template_by_id(template_id)
        if not template:
            return False
        if template.get('is_system') == 1:
            raise ValueError("Cannot delete system template")
        
        query = "DELETE FROM hql_templates WHERE id = ?"
        
        try:
            result = execute_write(query, (template_id,))
            if result > 0:
                # 清除缓存
                self.invalidate_pattern("templates:*")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False

    def export_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """
        导出模板为JSON格式

        Args:
            template_id: 模板ID

        Returns:
            模板JSON数据, 失败返回None
        """
        template = self.get_template_by_id(template_id)
        if not template:
            return None
        
        # 解析JSON字段
        try:
            template['tags'] = json.loads(template['tags']) if template.get('tags') else []
            template['variables'] = json.loads(template['variables']) if template.get('variables') else {}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON fields for template {template_id}")
        
        # 移除内部字段
        template.pop('created_at', None)
        template.pop('updated_at', None)
        template.pop('last_used_at', None)
        
        return template

    def import_template(self, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        导入模板

        Args:
            template_data: 模板JSON数据

        Returns:
            导入的模板字典, 失败返回None
        """
        # 检查必需字段
        required_fields = ['name', 'display_name', 'category', 'hql_content']
        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Missing required field: {field}")
        
        # 检查名称是否已存在
        existing = self.get_template_by_name(template_data['name'])
        if existing:
            raise ValueError(f"Template with name '{template_data['name']}' already exists")
        
        # 创建模板
        return self.create_template(template_data)

    def get_template_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根据名称获取模板

        Args:
            name: 模板名称

        Returns:
            模板字典, 不存在返回None
        """
        query = "SELECT * FROM hql_templates WHERE name = ?"
        return fetch_one_as_dict(query, (name,))
