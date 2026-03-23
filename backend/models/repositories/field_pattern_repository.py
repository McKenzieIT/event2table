#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Field Pattern Repository (字段模式数据访问层)

提供字段模式相关的数据访问方法:
- 从event_params表提取常用字段模式
- 统计字段使用频率
- 基于游戏和事件类型的字段分析
"""

import logging
from collections import Counter
from typing import Any, Dict, List, Optional

from backend.core.cache.decorators import cached
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_all_as_dict, fetch_one_as_dict

logger = logging.getLogger(__name__)


class FieldPatternRepository(GenericRepository):
    """
    字段模式仓储类

    继承 GenericRepository 并添加字段模式特定的查询方法
    用于存储和查询字段模式,统计字段使用频率
    """

    def __init__(self):
        """
        初始化字段模式仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="event_params",
            primary_key="id",
            enable_cache=True,
            cache_timeout=600,  # 10分钟缓存 (字段模式变化不频繁)
        )

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_common_field_patterns(
        self, game_gid: Optional[int] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取常用字段模式

        Args:
            game_gid: 可选的游戏GID过滤
            limit: 返回数量限制

        Returns:
            List[Dict]: 常用字段模式列表,格式:
                {
                    "param_name": str,
                    "param_name_cn": str,
                    "param_type": str,
                    "usage_count": int,
                    "event_count": int,
                    "is_common": bool
                }

        Example:
            >>> repo = FieldPatternRepository()
            >>> patterns = repo.get_common_field_patterns(game_gid=10000147, limit=20)
            >>> for pattern in patterns:
            ...     print(f"{pattern['param_name']}: {pattern['usage_count']}次")
        """
        # 构建查询
        query = """
            SELECT
                ep.param_name,
                MIN(ep.param_name_cn) as param_name_cn,
                MIN(ep.param_type) as param_type,
                COUNT(DISTINCT ep.event_id) as event_count,
                COUNT(*) as usage_count,
                CASE WHEN COUNT(DISTINCT ep.event_id) >= 3 THEN 1 ELSE 0 END as is_common
            FROM event_params ep
        """
        params = []

        if game_gid:
            query += """
                JOIN log_events le ON ep.event_id = le.id
                WHERE le.game_gid = ?
            """
            params.append(game_gid)

        query += """
            GROUP BY ep.param_name
            ORDER BY usage_count DESC
            LIMIT ?
        """
        params.append(limit)

        patterns = fetch_all_as_dict(query, tuple(params))

        # 添加字段类型推断
        for pattern in patterns:
            pattern["inferred_type"] = self._infer_field_type(pattern["param_name"])

        return patterns

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_field_patterns_by_event_type(
        self, event_name_pattern: str, game_gid: Optional[int] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        基于事件类型获取字段模式

        Args:
            event_name_pattern: 事件名称模式(如 "login", "purchase")
            game_gid: 可选的游戏GID过滤
            limit: 返回数量限制

        Returns:
            List[Dict]: 字段模式列表

        Example:
            >>> repo = FieldPatternRepository()
            >>> patterns = repo.get_field_patterns_by_event_type("login", game_gid=10000147)
        """
        query = """
            SELECT
                ep.param_name,
                MIN(ep.param_name_cn) as param_name_cn,
                MIN(ep.param_type) as param_type,
                COUNT(DISTINCT ep.event_id) as event_count,
                COUNT(*) as usage_count
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            WHERE le.event_name LIKE ?
        """
        params = [f"%{event_name_pattern}%"]

        if game_gid:
            query += " AND le.game_gid = ?"
            params.append(game_gid)

        query += """
            GROUP BY ep.param_name
            ORDER BY usage_count DESC
            LIMIT ?
        """
        params.append(limit)

        patterns = fetch_all_as_dict(query, tuple(params))

        # 添加字段类型推断
        for pattern in patterns:
            pattern["inferred_type"] = self._infer_field_type(pattern["param_name"])

        return patterns

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_field_usage_statistics(
        self, game_gid: Optional[int] = None, days: int = 30
    ) -> Dict[str, Any]:
        """
        获取字段使用统计

        Args:
            game_gid: 可选的游戏GID过滤
            days: 统计天数

        Returns:
            Dict[str, Any]: 统计信息
                {
                    "total_unique_fields": int,
                    "total_field_usage": int,
                    "most_common_fields": List[Dict],
                    "type_distribution": Dict[str, int]
                }

        Example:
            >>> repo = FieldPatternRepository()
            >>> stats = repo.get_field_usage_statistics(game_gid=10000147)
            >>> print(stats["most_common_fields"])
        """
        # 获取总统计
        query = """
            SELECT
                COUNT(DISTINCT ep.param_name) as total_unique_fields,
                COUNT(*) as total_field_usage
            FROM event_params ep
        """
        params = []

        if game_gid:
            query += """
                JOIN log_events le ON ep.event_id = le.id
                WHERE le.game_gid = ?
            """
            params.append(game_gid)

        total_stats = fetch_one_as_dict(query, tuple(params))

        # 获取最常用字段
        common_query = """
            SELECT
                ep.param_name,
                COUNT(*) as count
            FROM event_params ep
        """
        common_params = []

        if game_gid:
            common_query += """
                JOIN log_events le ON ep.event_id = le.id
                WHERE le.game_gid = ?
            """
            common_params.append(game_gid)

        common_query += """
            GROUP BY ep.param_name
            ORDER BY count DESC
            LIMIT 10
        """

        most_common = fetch_all_as_dict(common_query, tuple(common_params))

        # 获取类型分布
        type_query = """
            SELECT
                ep.param_type,
                COUNT(DISTINCT ep.param_name) as count
            FROM event_params ep
        """
        type_params = []

        if game_gid:
            type_query += """
                JOIN log_events le ON ep.event_id = le.id
                WHERE le.game_gid = ?
            """
            type_params.append(game_gid)

        type_query += """
            GROUP BY ep.param_type
        """

        type_distribution_raw = fetch_all_as_dict(type_query, tuple(type_params))
        type_distribution = {item["param_type"]: item["count"] for item in type_distribution_raw}

        return {
            "total_unique_fields": total_stats["total_unique_fields"] if total_stats else 0,
            "total_field_usage": total_stats["total_field_usage"] if total_stats else 0,
            "most_common_fields": most_common,
            "type_distribution": type_distribution,
        }

    @cached(ttl=1800)  # Cache for 30 minutes
    def find_similar_fields(
        self, field_name: str, game_gid: Optional[int] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        基于字段名称相似度查找相似字段

        Args:
            field_name: 字段名称
            game_gid: 可选的游戏GID过滤
            limit: 返回数量限制

        Returns:
            List[Dict]: 相似字段列表

        Example:
            >>> repo = FieldPatternRepository()
            >>> similar = repo.find_similar_fields("user_id", game_gid=10000147)
        """
        # 使用LIKE进行模糊匹配
        query = """
            SELECT DISTINCT
                ep.param_name,
                MIN(ep.param_name_cn) as param_name_cn,
                MIN(ep.param_type) as param_type,
                COUNT(*) as usage_count
            FROM event_params ep
        """
        params = []

        if game_gid:
            query += """
                JOIN log_events le ON ep.event_id = le.id
                WHERE le.game_gid = ?
            """
            params.append(game_gid)

        # 添加相似度条件
        if params:
            query += " AND ep.param_name LIKE ?"
        else:
            query += " WHERE ep.param_name LIKE ?"

        params.append(f"%{field_name}%")

        query += """
            GROUP BY ep.param_name
            ORDER BY usage_count DESC
            LIMIT ?
        """
        params.append(limit)

        similar_fields = fetch_all_as_dict(query, tuple(params))

        # 计算相似度分数
        for field in similar_fields:
            field["similarity_score"] = self._calculate_similarity(field_name, field["param_name"])
            field["inferred_type"] = self._infer_field_type(field["param_name"])

        # 按相似度排序
        similar_fields.sort(key=lambda x: x["similarity_score"], reverse=True)

        return similar_fields

    def _infer_field_type(self, field_name: str) -> str:
        """
        基于字段名称推断字段类型

        Args:
            field_name: 字段名称

        Returns:
            推断的字段类型 (base/param/calculate)

        Example:
            >>> repo = FieldPatternRepository()
            >>> repo._infer_field_type("role_id")  # "base"
            >>> repo._infer_field_type("zone_id")  # "param"
        """
        field_name_lower = field_name.lower()

        # 基础字段模式
        base_patterns = [
            "role_id",
            "account_id",
            "user_id",
            "uid",
            "game_id",
            "gid",
            "server_id",
            "channel_id",
            "platform",
            "device_id",
            "utdid",
            "ds",
            "dt",
            "hour",
        ]

        # 检查是否匹配基础字段模式
        for pattern in base_patterns:
            if pattern in field_name_lower:
                return "base"

        # 参数字段模式 (包含 _id 但不是基础字段)
        if "_id" in field_name_lower:
            return "param"

        # 计算字段模式
        calc_patterns = ["count", "sum", "avg", "max", "min", "total"]
        for pattern in calc_patterns:
            if field_name_lower.startswith(pattern):
                return "calculate"

        # 默认返回param
        return "param"

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        计算两个字符串的相似度 (简单的编辑距离算法)

        Args:
            str1: 字符串1
            str2: 字符串2

        Returns:
            相似度分数 (0-1)

        Example:
            >>> repo = FieldPatternRepository()
            >>> repo._calculate_similarity("user_id", "userid")  # 0.8
        """
        if str1 == str2:
            return 1.0

        len1, len2 = len(str1), len(str2)

        if len1 == 0:
            return 0.0 if len2 == 0 else 0.0

        if len2 == 0:
            return 0.0

        # 创建距离矩阵
        matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        # 初始化
        for i in range(len1 + 1):
            matrix[i][0] = i
        for j in range(len2 + 1):
            matrix[0][j] = j

        # 填充矩阵
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if str1[i - 1] == str2[j - 1]:
                    cost = 0
                else:
                    cost = 1

                matrix[i][j] = min(
                    matrix[i - 1][j] + 1,  # 删除
                    matrix[i][j - 1] + 1,  # 插入
                    matrix[i - 1][j - 1] + cost,  # 替换
                )

        # 计算相似度
        max_len = max(len1, len2)
        distance = matrix[len1][len2]
        similarity = 1.0 - (distance / max_len)

        return similarity
