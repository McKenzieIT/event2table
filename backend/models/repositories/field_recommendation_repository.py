from backend.core.cache.decorators import cached

# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor
# TODO: Replace loop queries with single JOIN query
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Field Recommendation Repository (字段推荐数据访问层)

提供字段推荐相关的数据访问方法
- 从hql_history表查询字段使用历史
- 统计字段使用频率
- 协同过滤推荐
"""

import json
from collections import Counter
from typing import Any, Dict, List

from backend.core.data_access import GenericRepository
from backend.core.utils.converters import fetch_all_as_dict


class FieldRecommendationRepository(GenericRepository):
    """
    字段推荐仓储类

    继承 GenericRepository 并添加字段推荐特定的查询方法
    注意: 此Repository不返回Entity,因为推荐结果是动态计算的数据
    """

    def __init__(self):
        """
        初始化字段推荐仓储

        启用缓存以提高查询性能
        """
        super().__init__(
            table_name="hql_history",
            primary_key="id",
            enable_cache=True,
            cache_timeout=600,  # 10分钟缓存 (推荐数据变化不频繁)
        )

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_history_recommendations(
        self, days: int = 30, limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        基于历史数据的字段推荐

        Args:
            days: 查询最近N天的历史记录
            limit: 返回数量限制

        Returns:
            List[Dict]: 推荐字段列表,格式: {"name": str, "type": str, "description": str, "frequency": int}

        Example:
            >>> repo = FieldRecommendationRepository()
            >>> recs = repo.get_history_recommendations(days=30, limit=1000)
            >>> for rec in recs:
            ...     print(f"{rec['name']}: {rec['frequency']}次")
        """
        query = f'''
            SELECT fields_json
            FROM "{self.table_name}"
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY created_at DESC
            LIMIT ?
        '''

        history_records = fetch_all_as_dict(query, (days, limit))

        if not history_records:
            return []

        # 统计字段使用频率
        field_counter = Counter()
        field_type_map = {}

        for record in history_records:
            try:
                fields = json.loads(record["fields_json"])
                for field in fields:
                    field_name = field.get("fieldName") or field.get("name")
                    if field_name:
                        field_counter[field_name] += 1
                        # 保存字段类型
                        if field_name not in field_type_map:
                            field_type_map[field_name] = (
                                field.get("fieldType") or field.get("type") or "base"
                            )
            except (json.JSONDecodeError, KeyError):
                continue

        # 获取最常用字段
        top_fields = field_counter.most_common(20)

        recommendations = []
        for field_name, count in top_fields:
            field_type = field_type_map.get(field_name, "base")
            recommendations.append(
                {
                    "name": field_name,
                    "type": field_type,
                    "description": f"使用频率: {count}次",
                    "frequency": count,
                }
            )

        return recommendations

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_collaborative_recommendations(
        self, event_name: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        基于协同过滤的字段推荐

        Args:
            event_name: 事件名称
            limit: 返回数量限制

        Returns:
            List[Dict]: 推荐字段列表

        Example:
            >>> repo = FieldRecommendationRepository()
            >>> recs = repo.get_collaborative_recommendations("login")
            >>> for rec in recs:
            ...     print(f"{rec['name']}: {rec['description']}")
        """
        query = f'''
            SELECT fields_json, events_json
            FROM "{self.table_name}"
            WHERE events_json LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        '''

        history_records = fetch_all_as_dict(query, (f"%{event_name}%", limit))

        if not history_records:
            return []

        # 统计字段使用频率
        field_counter = Counter()

        for record in history_records:
            try:
                fields = json.loads(record["fields_json"])
                for field in fields:
                    field_name = field.get("fieldName") or field.get("name")
                    if field_name:
                        field_counter[field_name] += 1
            except (json.JSONDecodeError, KeyError):
                continue

        # 获取最常用字段(排除已知的常用字段)
        top_fields = field_counter.most_common(10)

        recommendations = []
        for field_name, count in top_fields:
            # 跳过已在常用字段库中的字段
            if field_name in ["ds", "role_id", "account_id", "utdid"]:
                continue

            recommendations.append(
                {
                    "name": field_name,
                    "type": "base",
                    "description": f"相似事件常用 ({count}次)",
                    "frequency": count,
                }
            )

        return recommendations

    @cached(ttl=1800)  # Cache for 30 minutes
    def get_field_usage_statistics(self, days: int = 30) -> Dict[str, int]:
        """
        获取字段使用统计

        Args:
            days: 统计天数

        Returns:
            Dict[str, int]: 字段使用频率统计

        Example:
            >>> repo = FieldRecommendationRepository()
            >>> stats = repo.get_field_usage_statistics(days=30)
            >>> print(stats)  # {"role_id": 150, "account_id": 142, ...}
        """
        query = f'''
            SELECT fields_json
            FROM "{self.table_name}"
            WHERE created_at >= datetime('now', '-' || ? || ' days')
            ORDER BY created_at DESC
        '''

        history_records = fetch_all_as_dict(query, (days,))

        if not history_records:
            return {}

        # 统计字段使用频率
        field_counter = Counter()

        for record in history_records:
            try:
                fields = json.loads(record["fields_json"])
                for field in fields:
                    field_name = field.get("fieldName") or field.get("name")
                    if field_name:
                        field_counter[field_name] += 1
            except (json.JSONDecodeError, KeyError):
                continue

        return dict(field_counter.most_common(20))
