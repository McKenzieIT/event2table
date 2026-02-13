"""
智能字段推荐服务

基于业务规则和历史数据推荐字段

推荐策略：
1. 历史频率统计 - 从hql_history表统计字段使用频率
2. 事件特定推荐 - 基于事件类型的业务规则
3. 协同过滤 - 相似事件组合的字段推荐
4. 模糊匹配 - 部分字段名匹配
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from datetime import datetime, timedelta


class FieldRecommender:
    """
    字段推荐器

    基于多种策略推荐常用字段
    """

    # 常用字段库（按类型分类）
    COMMON_FIELDS = {
        "identity": [
            {"name": "ds", "type": "base", "description": "Partition field (日期分区)"},
            {"name": "role_id", "type": "base", "description": "Role ID (角色ID)"},
            {"name": "account_id", "type": "base", "description": "Account ID (账号ID)"},
            {"name": "utdid", "type": "base", "description": "Device ID (设备ID)"},
        ],
        "params": [
            {
                "name": "zone_id",
                "type": "param",
                "json_path": "$.zone_id",
                "description": "Zone ID (分区ID)",
            },
            {
                "name": "level",
                "type": "param",
                "json_path": "$.level",
                "description": "Player level (玩家等级)",
            },
            {
                "name": "vip_level",
                "type": "param",
                "json_path": "$.vipLevel",
                "description": "VIP level (VIP等级)",
            },
            {
                "name": "coin",
                "type": "param",
                "json_path": "$.coin",
                "description": "Coin amount (金币数量)",
            },
            {
                "name": "diamond",
                "type": "param",
                "json_path": "$.diamond",
                "description": "Diamond amount (钻石数量)",
            },
        ],
        "timestamp": [
            {"name": "tm", "type": "base", "description": "Timestamp (时间戳)"},
            {"name": "ts", "type": "base", "description": "Timestamp (时间戳)"},
        ],
        "environment": [
            {"name": "envinfo", "type": "base", "description": "Environment info (环境信息)"},
            {
                "name": "ip",
                "type": "param",
                "json_path": "$.ip",
                "description": "IP address (IP地址)",
            },
            {
                "name": "device_model",
                "type": "param",
                "json_path": "$.deviceModel",
                "description": "Device model (设备型号)",
            },
        ],
    }

    # 事件特定推荐（业务规则）
    EVENT_SPECIFIC_FIELDS = {
        "login": {
            "recommended": ["role_id", "account_id", "zone_id", "level", "ip"],
            "description": "Login event commonly uses account and device fields",
        },
        "logout": {
            "recommended": ["role_id", "account_id", "online_time"],
            "description": "Logout event commonly uses account and duration fields",
        },
        "purchase": {
            "recommended": ["role_id", "account_id", "coin", "diamond", "item_id"],
            "description": "Purchase event commonly uses transaction fields",
        },
        "level_up": {
            "recommended": ["role_id", "account_id", "level", "zone_id"],
            "description": "Level up event commonly uses character fields",
        },
        "battle": {
            "recommended": ["role_id", "account_id", "level", "battle_result", "zone_id"],
            "description": "Battle event commonly uses result and location fields",
        },
    }

    def __init__(self, db_path: Optional[str] = None):
        """
        初始化推荐器

        Args:
            db_path: 数据库路径（用于历史统计）
        """
        self.db_path = db_path

    def recommend_fields(
        self,
        event_name: Optional[str] = None,
        partial: Optional[str] = None,
        limit: int = 10,
        use_history: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        推荐字段（增强版）

        Args:
            event_name: 事件名称（用于事件特定推荐）
            partial: 部分字段名（用于模糊匹配）
            limit: 返回数量限制
            use_history: 是否使用历史统计数据

        Returns:
            List[Dict]: 推荐字段列表
        """
        recommendations = []
        weights = []

        # 策略1: 历史统计（权重最高）
        if use_history:
            history_recs = self._get_history_based_recommendations(event_name)
            for rec in history_recs:
                recommendations.append(rec)
                weights.append(5.0)  # 历史数据权重5.0

        # 策略2: 事件特定推荐
        if event_name:
            event_recs = self._get_event_specific_recommendations(event_name)
            for rec in event_recs:
                if rec["name"] not in [r["name"] for r in recommendations]:
                    recommendations.append(rec)
                    weights.append(3.0)  # 事件特定权重3.0

        # 策略3: 协同过滤（相似事件组合）
        if event_name and use_history:
            collaborative_recs = self._get_collaborative_recommendations(event_name)
            for rec in collaborative_recs:
                if rec["name"] not in [r["name"] for r in recommendations]:
                    recommendations.append(rec)
                    weights.append(2.0)  # 协同过滤权重2.0

        # 策略4: 模糊匹配
        if partial:
            fuzzy_matches = self._fuzzy_match_fields(partial)
            for rec in fuzzy_matches:
                if rec["name"] not in [r["name"] for r in recommendations]:
                    recommendations.append(rec)
                    weights.append(1.5)  # 模糊匹配权重1.5

        # 策略5: 常用字段（兜底）
        if not recommendations:
            recommendations = self._get_common_fields()
            weights = [1.0] * len(recommendations)

        # 按权重排序并去重
        scored_recs = list(zip(recommendations, weights))
        scored_recs.sort(key=lambda x: x[1], reverse=True)

        # 去重并限制数量
        seen = set()
        unique_recommendations = []
        for rec, weight in scored_recs:
            if rec["name"] not in seen:
                seen.add(rec["name"])
                rec["score"] = weight
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= limit:
                    break

        return unique_recommendations

    def _get_history_based_recommendations(
        self, event_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        从历史数据获取推荐（基于hql_history表）

        Args:
            event_name: 事件名称（可选）

        Returns:
            List[Dict]: 推荐字段列表
        """
        if not self.db_path:
            return []

        try:
            from backend.core.database import fetch_all_as_dict

            # 查询最近30天的历史记录
            sql = """
                SELECT fields_json, events_json, mode
                FROM hql_history
                WHERE created_at >= datetime('now', '-30 days')
                ORDER BY created_at DESC
                LIMIT 1000
            """

            history_records = fetch_all_as_dict(sql, db_path=self.db_path)

            if not history_records:
                return []

            # 统计字段使用频率
            field_counter = Counter()
            field_type_map = {}

            for record in history_records:
                # 解析字段
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

        except Exception as e:
            # 数据库查询失败，返回空列表
            print(f"Warning: Failed to fetch history data: {e}")
            return []

    def _get_collaborative_recommendations(self, event_name: str) -> List[Dict[str, Any]]:
        """
        协同过滤推荐（基于相似事件组合）

        Args:
            event_name: 事件名称

        Returns:
            List[Dict]: 推荐字段列表
        """
        if not self.db_path:
            return []

        try:
            from backend.core.database import fetch_all_as_dict

            # 查询包含类似事件的历史记录
            sql = """
                SELECT fields_json, events_json
                FROM hql_history
                WHERE events_json LIKE ?
                ORDER BY created_at DESC
                LIMIT 100
            """

            history_records = fetch_all_as_dict(sql, (f"%{event_name}%",), db_path=self.db_path)

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

            # 获取最常用字段（排除已知的常用字段）
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

        except Exception as e:
            print(f"Warning: Failed to fetch collaborative data: {e}")
            return []

    def _get_event_specific_recommendations(self, event_name: str) -> List[Dict[str, Any]]:
        """获取事件特定推荐"""
        event_name_lower = event_name.lower()

        if event_name_lower not in self.EVENT_SPECIFIC_FIELDS:
            return []

        field_names = self.EVENT_SPECIFIC_FIELDS[event_name_lower]["recommended"]
        return self._build_field_recommendations(field_names)

    def _fuzzy_match_fields(self, partial: str) -> List[Dict[str, Any]]:
        """模糊匹配字段"""
        partial_lower = partial.lower()
        matches = []

        # 从所有常用字段中搜索
        all_fields = []
        for category_fields in self.COMMON_FIELDS.values():
            all_fields.extend(category_fields)

        for field in all_fields:
            if partial_lower in field["name"].lower():
                matches.append(field)

        return matches

    def _get_common_fields(self) -> List[Dict[str, Any]]:
        """获取常用字段"""
        # 返回所有identity字段（最常用）
        return self.COMMON_FIELDS["identity"] + self.COMMON_FIELDS["params"][:3]

    def _build_field_recommendations(self, field_names: List[str]) -> List[Dict[str, Any]]:
        """构建字段推荐列表"""
        recommendations = []

        for field_name in field_names:
            # 在常用字段库中查找
            found = False
            for category_fields in self.COMMON_FIELDS.values():
                for field in category_fields:
                    if field["name"] == field_name:
                        recommendations.append(field)
                        found = True
                        break
                if found:
                    break

            # 如果没找到，创建基础推荐
            if not found:
                recommendations.append(
                    {"name": field_name, "type": "base", "description": f"{field_name} field"}
                )

        return recommendations

    def get_field_usage_statistics(self, days: int = 30) -> Dict[str, int]:
        """
        获取字段使用统计（从hql_history表）

        Args:
            days: 统计天数

        Returns:
            Dict: 字段使用频率统计
        """
        if not self.db_path:
            # 返回默认统计
            return Counter(["role_id", "account_id", "zone_id", "level", "ds"])

        try:
            from backend.core.database import fetch_all_as_dict

            sql = """
                SELECT fields_json
                FROM hql_history
                WHERE created_at >= datetime('now', '-' || ? || ' days')
                ORDER BY created_at DESC
            """

            history_records = fetch_all_as_dict(sql, (days,), db_path=self.db_path)

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

        except Exception as e:
            print(f"Warning: Failed to calculate field statistics: {e}")
            return {}


# 便捷函数
def recommend_fields(
    event_name: Optional[str] = None,
    partial: Optional[str] = None,
    limit: int = 10,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    推荐字段（便捷函数）

    Args:
        event_name: 事件名称
        partial: 部分字段名
        limit: 返回数量限制
        db_path: 数据库路径

    Returns:
        List[Dict]: 推荐字段列表
    """
    recommender = FieldRecommender(db_path=db_path)
    return recommender.recommend_fields(event_name, partial, limit)


# 导出
__all__ = ["FieldRecommender", "recommend_fields"]
