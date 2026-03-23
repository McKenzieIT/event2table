#!/usr/bin/env python3
from backend.core.cache.decorators import cached

# -*- coding: utf-8 -*-
"""
Parameter Library Repository (参数库数据访问层)

提供参数库相关的数据访问方法
- 返回统一字典模型
- 移除直接数据库访问
- 保持GenericRepository继承
"""

from typing import Any, Dict, List, Optional

from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict


class ParamLibraryRepository(GenericRepository):
    """
    参数库仓储类

    继承 GenericRepository 并添加参数库特定的查询方法
    """

    def __init__(self):
        """
        初始化参数库仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="param_library",
            primary_key="id",
            enable_cache=True,
            cache_timeout=600,  # 10分钟缓存（参数库变化较少）
        )

    @cached(ttl=1800)  # Cache for 30 minutes
    def find_by_name(self, param_name: str) -> Optional[Dict[str, Any]]:
        """
        根据参数名查找库参数

        Args:
            param_name: 参数名

        Returns:
            库参数字典, 不存在返回None

        Example:
            >>> repo = ParamLibraryRepository()
            >>> param = repo.find_by_name('user_id')
        """
        query = """
            SELECT pl.*, pt.template_name, pt.display_name as type_display_name,
                   pt.hql_parse_template
            FROM param_library pl
            JOIN param_templates pt ON pl.template_id = pt.id
            WHERE pl.param_name = ?
        """
        return fetch_one_as_dict(query, (param_name,))

    @cached(ttl=1800)  # Cache for 30 minutes
    def find_by_id_with_template(self, library_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID查找库参数（包含模板信息）

        Args:
            library_id: 库参数ID

        Returns:
            库参数字典（包含模板信息）, 不存在返回None

        Example:
            >>> repo = ParamLibraryRepository()
            >>> param = repo.find_by_id_with_template(1)
        """
        query = """
            SELECT pl.*, pt.template_name, pt.display_name as type_display_name,
                   pt.hql_parse_template, pt.base_type, pt.element_type
            FROM param_library pl
            JOIN param_templates pt ON pl.template_id = pt.id
            WHERE pl.id = ?
        """
        return fetch_one_as_dict(query, (library_id,))

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_all_parameters(
        self,
        game_gid: Optional[int] = None,
        category: Optional[str] = None,
        is_standard: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取参数库中的所有参数

        Args:
            game_gid: 可选的游戏GID过滤
            category: 可选的类别过滤
            is_standard: 可选的是否标准参数过滤

        Returns:
            库参数字典列表

        Example:
            >>> repo = ParamLibraryRepository()
            >>> params = repo.get_all_parameters(game_gid=10000147, category='custom')
        """
        query = """
            SELECT pl.*, pt.template_name, pt.display_name as type_display_name,
                   pt.hql_parse_template
            FROM param_library pl
            JOIN param_templates pt ON pl.template_id = pt.id
            WHERE 1=1
        """
        params = []

        if game_gid:
            # 查找与指定游戏相关的库参数
            query += """
                AND pl.id IN (
                    SELECT DISTINCT library_id
                    FROM event_params ep
                    JOIN log_events le ON ep.event_id = le.id
                    WHERE le.game_gid = ? AND ep.library_id IS NOT NULL
                )
            """
            params.append(game_gid)

        if category:
            query += " AND pl.category = ?"
            params.append(category)

        if is_standard is not None:
            query += " AND pl.is_standard = ?"
            params.append(1 if is_standard else 0)

        query += " ORDER BY pl.usage_count DESC, pl.param_name"

        return fetch_all_as_dict(query, tuple(params) if params else ())

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_frequently_used_parameters(
        self, min_usage: int = 2, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取频繁使用的库参数

        Args:
            min_usage: 最小使用次数
            limit: 可选的限制数量

        Returns:
            库参数字典列表

        Example:
            >>> repo = ParamLibraryRepository()
            >>> params = repo.get_frequently_used_parameters(min_usage=3, limit=10)
        """
        query = """
            SELECT pl.*, pt.template_name, pt.display_name as type_display_name,
                   pt.hql_parse_template
            FROM param_library pl
            JOIN param_templates pt ON pl.template_id = pt.id
            WHERE pl.usage_count >= ?
            ORDER BY pl.usage_count DESC, pl.param_name
        """
        if limit:
            query += f" LIMIT {limit}"

        return fetch_all_as_dict(query, (min_usage,))

    def create_parameter(
        self,
        param_name: str,
        param_name_cn: str,
        template_id: int,
        param_description: str = "",
        category: str = "custom",
        is_standard: bool = False,
    ) -> int:
        """
        创建新的库参数

        Args:
            param_name: 参数名
            param_name_cn: 参数中文名
            template_id: 模板ID
            param_description: 参数描述
            category: 类别
            is_standard: 是否为标准参数

        Returns:
            创建的库参数ID

        Example:
            >>> repo = ParamLibraryRepository()
            >>> library_id = repo.create_parameter('user_id', '用户ID', 1)
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO param_library
                (param_name, param_name_cn, template_id, param_description, category, is_standard)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    param_name,
                    param_name_cn,
                    template_id,
                    param_description,
                    category,
                    1 if is_standard else 0,
                ),
            )

            library_id = cursor.lastrowid
            conn.commit()
            return library_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update_parameter(
        self,
        library_id: int,
        param_name_cn: Optional[str] = None,
        param_description: Optional[str] = None,
        category: Optional[str] = None,
        is_standard: Optional[bool] = None,
    ) -> bool:
        """
        更新库参数

        Args:
            library_id: 库参数ID
            param_name_cn: 新的参数中文名（可选）
            param_description: 新的参数描述（可选）
            category: 新的类别（可选）
            is_standard: 是否为标准参数（可选）

        Returns:
            是否更新成功

        Example:
            >>> repo = ParamLibraryRepository()
            >>> success = repo.update_parameter(1, param_name_cn='新名称')
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 构建更新字段
            update_fields = []
            update_values = []

            if param_name_cn is not None:
                update_fields.append("param_name_cn = ?")
                update_values.append(param_name_cn)

            if param_description is not None:
                update_fields.append("param_description = ?")
                update_values.append(param_description)

            if category is not None:
                update_fields.append("category = ?")
                update_values.append(category)

            if is_standard is not None:
                update_fields.append("is_standard = ?")
                update_values.append(1 if is_standard else 0)

            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(library_id)

                query = f"""
                    UPDATE param_library
                    SET {', '.join(update_fields)}
                    WHERE id = ?
                """
                cursor.execute(query, tuple(update_values))
                conn.commit()
                return True

            return False

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update_usage_count(self, library_id: int, increment: int = 1) -> bool:
        """
        更新库参数使用次数

        Args:
            library_id: 库参数ID
            increment: 增量（默认1）

        Returns:
            是否更新成功

        Example:
            >>> repo = ParamLibraryRepository()
            >>> success = repo.update_usage_count(1)
        """
        from backend.core.utils import execute_write

        query = f"""
            UPDATE param_library
            SET usage_count = usage_count + {increment},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        result = execute_write(query, (library_id,))
        return result > 0

    def delete_parameter(self, library_id: int) -> bool:
        """
        删除库参数

        Args:
            library_id: 库参数ID

        Returns:
            是否删除成功

        Example:
            >>> repo = ParamLibraryRepository()
            >>> success = repo.delete_parameter(1)
        """
        # 检查是否被引用
        from backend.core.utils.converters import fetch_one_as_dict

        referenced = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM event_params WHERE library_id = ?", (library_id,)
        )

        if referenced and referenced["count"] > 0:
            return False

        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM param_library WHERE id = ?", (library_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count > 0
        finally:
            conn.close()

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_categories(self) -> List[str]:
        """
        获取所有参数类别

        Returns:
            类别列表

        Example:
            >>> repo = ParamLibraryRepository()
            >>> categories = repo.get_categories()
        """
        query = """
            SELECT DISTINCT category
            FROM param_library
            WHERE category IS NOT NULL AND category != ''
            ORDER BY category
        """
        rows = fetch_all_as_dict(query)
        return [row["category"] for row in rows]

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_parameters_by_category(
        self, category: str, include_standard: bool = True
    ) -> List[Dict[str, Any]]:
        """
        根据类别获取参数

        Args:
            category: 类别
            include_standard: 是否包含标准参数

        Returns:
            库参数字典列表

        Example:
            >>> repo = ParamLibraryRepository()
            >>> params = repo.get_parameters_by_category('custom')
        """
        query = """
            SELECT pl.*, pt.template_name, pt.display_name as type_display_name,
                   pt.hql_parse_template
            FROM param_library pl
            JOIN param_templates pt ON pl.template_id = pt.id
            WHERE pl.category = ?
        """
        if not include_standard:
            query += " AND pl.is_standard = 0"

        query += " ORDER BY pl.usage_count DESC, pl.param_name"

        return fetch_all_as_dict(query, (category,))

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取参数库统计信息

        Returns:
            统计信息字典

        Example:
            >>> repo = ParamLibraryRepository()
            >>> stats = repo.get_statistics()
        """
        stats = fetch_one_as_dict(
            """
            SELECT
                COUNT(*) as total_parameters,
                SUM(CASE WHEN is_standard = 1 THEN 1 ELSE 0 END) as standard_parameters,
                SUM(usage_count) as total_usage,
                AVG(usage_count) as avg_usage
            FROM param_library
        """
        )

        category_stats = fetch_all_as_dict(
            """
            SELECT
                category,
                COUNT(*) as count,
                SUM(usage_count) as total_usage
            FROM param_library
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """
        )

        return {
            "total_parameters": stats["total_parameters"] if stats else 0,
            "standard_parameters": stats["standard_parameters"] if stats else 0,
            "total_usage": stats["total_usage"] if stats else 0,
            "avg_usage": stats["avg_usage"] if stats else 0,
            "by_category": category_stats,
        }

    @cached(ttl=1800)  # Cache for 30 minutes
    def find_by_id(self, library_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID查询库参数

        Args:
            library_id: 库参数ID

        Returns:
            库参数字典, 不存在返回None

        Example:
            >>> repo = ParamLibraryRepository()
            >>> param = repo.find_by_id(1)
        """
        return self.find_by_id_with_template(library_id)
