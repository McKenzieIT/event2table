#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Field Recommendation Service (智能字段推荐服务)

提供智能字段推荐功能:
- 分析历史事件参数，提取常用字段模式
- 基于字段名称相似度推荐
- 基于游戏分类推荐特定字段
- 支持字段类型推断

架构: Service Layer (四层架构: API → Service → Repository → Entity)
"""

import logging
from typing import Any, Dict, List, Optional

from backend.core.cache.cache_system import cached
from backend.models.repositories.field_pattern_repository import FieldPatternRepository
from backend.services.base_service import BaseService

logger = logging.getLogger(__name__)


class FieldRecommendationService(BaseService):
    """
    智能字段推荐服务类

    职责:
    - 提供智能字段推荐功能
    - 分析历史数据提取字段模式
    - 基于相似度和游戏分类推荐字段
    - 推断字段类型
    """

    def __init__(self):
        """初始化智能字段推荐服务"""
        super().__init__()
        self.field_pattern_repo = FieldPatternRepository()
        logger.info("✅ FieldRecommendationService initialized")

    @cached("field_recommendations.recommend", timeout=300)
    def get_recommendations(
        self,
        game_gid: Optional[int] = None,
        event_name: Optional[str] = None,
        field_name_hint: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        获取字段推荐

        Args:
            game_gid: 可选的游戏GID
            event_name: 可选的事件名称(用于事件类型推荐)
            field_name_hint: 可选的字段名称提示(用于相似度推荐)
            limit: 返回数量限制

        Returns:
            List[Dict]: 推荐字段列表,格式:
                {
                    "param_name": str,
                    "param_name_cn": str,
                    "param_type": str,
                    "inferred_type": str,
                    "usage_count": int,
                    "event_count": int,
                    "is_common": bool,
                    "similarity_score": Optional[float],
                    "recommendation_reason": str
                }

        Raises:
            ValueError: 参数无效

        Example:
            >>> service = FieldRecommendationService()
            >>> recs = service.get_recommendations(game_gid=10000147, limit=10)
            >>> for rec in recs:
            ...     print(f"{rec['param_name']}: {rec['recommendation_reason']}")
        """
        recommendations = []

        # 策略1: 基于字段名称提示的相似度推荐
        if field_name_hint:
            similar_fields = self.field_pattern_repo.find_similar_fields(
                field_name_hint, game_gid=game_gid, limit=limit
            )
            for field in similar_fields:
                field[
                    "recommendation_reason"
                ] = f"与'{field_name_hint}'相似 (相似度: {field['similarity_score']:.2f})"
                recommendations.append(field)

        # 策略2: 基于事件类型的推荐
        if event_name and not field_name_hint:
            event_fields = self.field_pattern_repo.get_field_patterns_by_event_type(
                event_name, game_gid=game_gid, limit=limit
            )
            for field in event_fields:
                field["recommendation_reason"] = f"在'{event_name}'类型事件中常用"
                recommendations.append(field)

        # 策略3: 基于游戏的全局常用字段推荐
        if not field_name_hint and not event_name:
            common_fields = self.field_pattern_repo.get_common_field_patterns(
                game_gid=game_gid, limit=limit
            )
            for field in common_fields:
                if field["is_common"]:
                    field["recommendation_reason"] = "全局常用字段"
                else:
                    field["recommendation_reason"] = f"使用频率高 ({field['usage_count']}次)"
                recommendations.append(field)

        # 去重并限制数量
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec["param_name"] not in seen:
                seen.add(rec["param_name"])
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= limit:
                    break

        logger.info(
            f"Generated {len(unique_recommendations)} recommendations for game_gid={game_gid}"
        )
        return unique_recommendations

    @cached("field_recommendations.patterns", timeout=600)
    def get_common_patterns(
        self, game_gid: Optional[int] = None, limit: int = 50
    ) -> Dict[str, Any]:
        """
        获取常用字段模式

        Args:
            game_gid: 可选的游戏GID
            limit: 返回数量限制

        Returns:
            Dict[str, Any]: 常用字段模式信息
                {
                    "patterns": List[Dict],
                    "statistics": Dict[str, Any]
                }

        Raises:
            ValueError: 参数无效

        Example:
            >>> service = FieldRecommendationService()
            >>> patterns = service.get_common_patterns(game_gid=10000147)
            >>> print(patterns["statistics"])
        """
        # 获取常用字段模式
        patterns = self.field_pattern_repo.get_common_field_patterns(game_gid=game_gid, limit=limit)

        # 获取统计信息
        statistics = self.field_pattern_repo.get_field_usage_statistics(game_gid=game_gid)

        return {
            "patterns": patterns,
            "statistics": statistics,
        }

    @cached("field_recommendations.types", timeout=600)
    def infer_field_type(self, field_name: str) -> Dict[str, Any]:
        """
        推断字段类型

        Args:
            field_name: 字段名称

        Returns:
            Dict[str, Any]: 字段类型推断结果
                {
                    "field_name": str,
                    "inferred_type": str,
                    "confidence": float,
                    "suggested_hive_type": str,
                    "reasoning": str
                }

        Raises:
            ValueError: field_name为空

        Example:
            >>> service = FieldRecommendationService()
            >>> result = service.infer_field_type("role_id")
            >>> print(result["inferred_type"])  # "base"
            >>> print(result["suggested_hive_type"])  # "BIGINT"
        """
        if not field_name or len(field_name.strip()) == 0:
            raise ValueError("field_name cannot be empty")

        field_name = field_name.strip()

        # 推断字段类型
        inferred_type = self.field_pattern_repo._infer_field_type(field_name)

        # 根据推断类型建议Hive类型
        suggested_hive_type = self._suggest_hive_type(field_name, inferred_type)

        # 计算置信度
        confidence = self._calculate_type_confidence(field_name, inferred_type)

        # 生成推理说明
        reasoning = self._generate_type_reasoning(field_name, inferred_type, confidence)

        logger.info(
            f"Inferred type for '{field_name}': {inferred_type} (confidence: {confidence:.2f})"
        )

        return {
            "field_name": field_name,
            "inferred_type": inferred_type,
            "confidence": confidence,
            "suggested_hive_type": suggested_hive_type,
            "reasoning": reasoning,
        }

    def _suggest_hive_type(self, field_name: str, inferred_type: str) -> str:
        """
        根据字段名称和推断类型建议Hive类型

        Args:
            field_name: 字段名称
            inferred_type: 推断的字段类型

        Returns:
            建议的Hive类型

        Example:
            >>> service = FieldRecommendationService()
            >>> service._suggest_hive_type("role_id", "base")  # "BIGINT"
            >>> service._suggest_hive_type("zone_name", "param")  # "STRING"
        """
        field_name_lower = field_name.lower()

        # 基于字段名称的模式匹配
        if any(pattern in field_name_lower for pattern in ["id", "uid", "gid"]):
            return "BIGINT"
        elif any(pattern in field_name_lower for pattern in ["count", "num", "amount", "level"]):
            return "INT"
        elif any(pattern in field_name_lower for pattern in ["price", "cost", "value", "rate"]):
            return "DOUBLE"
        elif any(pattern in field_name_lower for pattern in ["time", "date", "ts", "timestamp"]):
            return "STRING"  # Hive中时间通常用STRING表示
        elif any(pattern in field_name_lower for pattern in ["is_", "has_", "can_", "flag"]):
            return "BOOLEAN"
        elif any(pattern in field_name_lower for pattern in ["name", "title", "desc", "content"]):
            return "STRING"
        else:
            # 默认根据类型推断
            if inferred_type == "base":
                return "BIGINT"
            elif inferred_type == "calculate":
                return "DOUBLE"
            else:
                return "STRING"

    def _calculate_type_confidence(self, field_name: str, inferred_type: str) -> float:
        """
        计算类型推断的置信度

        Args:
            field_name: 字段名称
            inferred_type: 推断的字段类型

        Returns:
            置信度 (0-1)

        Example:
            >>> service = FieldRecommendationService()
            >>> service._calculate_type_confidence("role_id", "base")  # 0.95
        """
        field_name_lower = field_name.lower()

        # 高置信度模式
        high_confidence_patterns = [
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
        ]

        # 中等置信度模式
        medium_confidence_patterns = ["zone_id", "item_id", "skill_id", "level", "count", "num"]

        # 检查是否匹配高置信度模式
        for pattern in high_confidence_patterns:
            if pattern in field_name_lower:
                return 0.95

        # 检查是否匹配中等置信度模式
        for pattern in medium_confidence_patterns:
            if pattern in field_name_lower:
                return 0.80

        # 检查是否包含_id后缀
        if field_name_lower.endswith("_id"):
            return 0.75

        # 默认置信度
        return 0.60

    def _generate_type_reasoning(
        self, field_name: str, inferred_type: str, confidence: float
    ) -> str:
        """
        生成类型推断的推理说明

        Args:
            field_name: 字段名称
            inferred_type: 推断的字段类型
            confidence: 置信度

        Returns:
            推理说明字符串

        Example:
            >>> service = FieldRecommendationService()
            >>> service._generate_type_reasoning("role_id", "base", 0.95)
            >>> # "字段名包含'role_id'，匹配基础字段模式，置信度高"
        """
        field_name_lower = field_name.lower()

        if inferred_type == "base":
            return f"字段名'{field_name}'匹配基础字段模式，通常为全局标识符"
        elif inferred_type == "param":
            return f"字段名'{field_name}'包含'_id'后缀，推断为参数字段"
        elif inferred_type == "calculate":
            return f"字段名'{field_name}'以计算关键词开头，推断为计算字段"
        else:
            return f"字段名'{field_name}'未匹配已知模式，默认为参数字段"

    def invalidate_recommendations_cache(self, game_gid: Optional[int] = None):
        """
        失效推荐缓存

        Args:
            game_gid: 可选的游戏GID

        Example:
            >>> service = FieldRecommendationService()
            >>> service.invalidate_recommendations_cache(game_gid=10000147)
        """
        if game_gid:
            self.invalidator.invalidate_pattern(
                "field_recommendations.recommend", game_gid=game_gid
            )
            self.invalidator.invalidate_pattern("field_recommendations.patterns", game_gid=game_gid)
            logger.info(f"Invalidated recommendations cache for game_gid={game_gid}")
        else:
            self.invalidator.invalidate_pattern("field_recommendations.recommend")
            self.invalidator.invalidate_pattern("field_recommendations.patterns")
            self.invalidator.invalidate_pattern("field_recommendations.types")
            logger.info("Invalidated all recommendations cache")
