#!/usr/bin/env python3
from backend.core.cache.decorators import cached

# -*- coding: utf-8 -*-
"""
Parameter Alias Repository (参数别名数据访问层)

提供参数别名相关的数据访问方法
- 返回统一字典模型
- 移除直接数据库访问
- 保持GenericRepository继承
"""

from typing import Optional, List, Dict, Any
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict


class ParameterAliasRepository(GenericRepository):
    """
    参数别名仓储类

    继承 GenericRepository 并添加别名特定的查询方法
    """

    def __init__(self):
        """
        初始化参数别名仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="parameter_aliases",
            primary_key="id",
            enable_cache=True,
            cache_timeout=300,  # 5分钟缓存
        )


    @cached(ttl=1800)  # Cache for 30 minutes
    def find_by_param_and_game(
        self, param_id: int, game_gid: int
    ) -> List[Dict[str, Any]]:
        """
        获取指定参数和游戏的所有别名

        Args:
            param_id: 参数ID (references event_params table)
            game_gid: 游戏GID

        Returns:
            别名字典列表

        Example:
            >>> repo = ParameterAliasRepository()
            >>> aliases = repo.find_by_param_and_game(1, 10000147)
        """
        query = """
            SELECT pa.*, ep.param_name, ep.param_name_cn
            FROM parameter_aliases pa
            LEFT JOIN event_params ep ON pa.param_id = ep.id
            WHERE pa.game_gid = ? AND pa.param_id = ?
            ORDER BY pa.is_preferred DESC, pa.usage_count DESC, pa.last_used_at DESC
        """
        return fetch_all_as_dict(query, (game_gid, param_id))


    @cached(ttl=1800)  # Cache for 30 minutes
    def find_by_alias_and_game(
        self, alias: str, game_gid: int
    ) -> Optional[Dict[str, Any]]:
        """
        根据别名和游戏查找别名记录

        Args:
            alias: 别名
            game_gid: 游戏GID

        Returns:
            别名字典，不存在返回None

        Example:
            >>> repo = ParameterAliasRepository()
            >>> alias = repo.find_by_alias_and_game('user_id', 10000147)
        """
        query = """
            SELECT * FROM parameter_aliases
            WHERE game_gid = ? AND alias = ?
        """
        return fetch_one_as_dict(query, (game_gid, alias))


    @cached(ttl=1800)  # Cache for 30 minutes
    def find_preferred_alias(self, param_id: int, game_gid: int) -> Optional[Dict[str, Any]]:
        """
        获取指定参数的首选别名

        Args:
            param_id: 参数ID
            game_gid: 游戏GID

        Returns:
            首选别名字典，不存在返回None

        Example:
            >>> repo = ParameterAliasRepository()
            >>> alias = repo.find_preferred_alias(1, 10000147)
        """
        query = """
            SELECT * FROM parameter_aliases
            WHERE game_gid = ? AND param_id = ? AND is_preferred = 1
        """
        return fetch_one_as_dict(query, (game_gid, param_id))

    def create_alias(
        self,
        game_id: int,
        game_gid: int,
        param_id: int,
        alias: str,
        display_name: str = "",
        is_preferred: bool = False,
    ) -> int:
        """
        创建参数别名

        Args:
            game_id: 游戏数据库ID
            game_gid: 游戏GID
            param_id: 参数ID
            alias: 别名
            display_name: 显示名称
            is_preferred: 是否为首选别名

        Returns:
            创建的别名ID

        Example:
            >>> repo = ParameterAliasRepository()
            >>> alias_id = repo.create_alias(1, 10000147, 1, 'user_id', '用户ID')
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 如果设置为首选，先取消其他首选别名
            if is_preferred:
                cursor.execute(
                    """
                    UPDATE parameter_aliases
                    SET is_preferred = 0
                    WHERE game_gid = ? AND param_id = ?
                """,
                    (game_gid, param_id),
                )

            # 创建别名
            cursor.execute(
                """
                INSERT INTO parameter_aliases
                (game_id, game_gid, param_id, alias, display_name, is_preferred, usage_count, last_used_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, NULL)
            """,
                (game_id, game_gid, param_id, alias, display_name, 1 if is_preferred else 0),
            )

            alias_id = cursor.lastrowid
            conn.commit()
            return alias_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def update_alias(
        self,
        alias_id: int,
        alias: Optional[str] = None,
        display_name: Optional[str] = None,
        is_preferred: Optional[bool] = None,
    ) -> bool:
        """
        更新参数别名

        Args:
            alias_id: 别名ID
            alias: 新别名（可选）
            display_name: 新显示名称（可选）
            is_preferred: 是否设为首选（可选）

        Returns:
            是否更新成功

        Example:
            >>> repo = ParameterAliasRepository()
            >>> success = repo.update_alias(1, display_name='新显示名称')
        """
        from backend.core.utils.converters import get_db_connection

        # 获取现有别名
        existing = self.find_by_id(alias_id)
        if not existing:
            return False

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 如果设置为首选，先取消其他首选别名
            if is_preferred and not existing.get("is_preferred"):
                cursor.execute(
                    """
                    UPDATE parameter_aliases
                    SET is_preferred = 0
                    WHERE game_gid = ? AND param_id = ? AND id != ?
                """,
                    (existing["game_gid"], existing["param_id"], alias_id),
                )

            # 构建更新字段
            update_fields = []
            update_values = []

            if alias is not None:
                update_fields.append("alias = ?")
                update_values.append(alias)

            if display_name is not None:
                update_fields.append("display_name = ?")
                update_values.append(display_name)

            if is_preferred is not None:
                update_fields.append("is_preferred = ?")
                update_values.append(1 if is_preferred else 0)

            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                update_values.append(alias_id)

                query = f"""
                    UPDATE parameter_aliases
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

    def set_preferred_alias(self, alias_id: int) -> bool:
        """
        设置别名为首选

        Args:
            alias_id: 别名ID

        Returns:
            是否设置成功

        Example:
            >>> repo = ParameterAliasRepository()
            >>> success = repo.set_preferred_alias(1)
        """
        # 获取别名信息
        alias = self.find_by_id(alias_id)
        if not alias:
            return False

        return self.update_alias(alias_id, is_preferred=True)

    def increment_usage(self, alias_id: int) -> bool:
        """
        增加别名使用次数

        Args:
            alias_id: 别名ID

        Returns:
            是否更新成功

        Example:
            >>> repo = ParameterAliasRepository()
            >>> success = repo.increment_usage(1)
        """
        from backend.core.utils import execute_write

        query = """
            UPDATE parameter_aliases
            SET usage_count = usage_count + 1,
                last_used_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        result = execute_write(query, (alias_id,))
        return result > 0


    @cached(ttl=1800)  # Cache for 30 minutes
    def find_by_id(self, alias_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID查询别名

        Args:
            alias_id: 别名ID

        Returns:
            别名字典，不存在返回None

        Example:
            >>> repo = ParameterAliasRepository()
            >>> alias = repo.find_by_id(1)
        """
        query = """
            SELECT id, param_id, alias, display_name, usage_count, last_used_at,
                   is_preferred, game_gid, created_at, updated_at
            FROM parameter_aliases
            WHERE id = ?
        """
        return fetch_one_as_dict(query, (alias_id,))

    def delete(self, alias_id: int) -> bool:
        """
        删除别名

        Args:
            alias_id: 别名ID

        Returns:
            是否删除成功

        Example:
            >>> repo = ParameterAliasRepository()
            >>> success = repo.delete(1)
        """
        from backend.core.utils.converters import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM parameter_aliases WHERE id = ?", (alias_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count > 0
        finally:
            conn.close()


    @cached(ttl=1800)  # Cache for 30 minutes
    def get_all_aliases_by_game(self, game_gid: int) -> List[Dict[str, Any]]:
        """
        获取游戏的所有别名

        Args:
            game_gid: 游戏GID

        Returns:
            别名字典列表

        Example:
            >>> repo = ParameterAliasRepository()
            >>> aliases = repo.get_all_aliases_by_game(10000147)
        """
        query = """
            SELECT pa.*, ep.param_name, ep.param_name_cn
            FROM parameter_aliases pa
            LEFT JOIN event_params ep ON pa.param_id = ep.id
            WHERE pa.game_gid = ?
            ORDER BY pa.param_id, pa.is_preferred DESC, pa.usage_count DESC
        """
        return fetch_all_as_dict(query, (game_gid,))
