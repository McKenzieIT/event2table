#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Field Recommendation Service

测试智能字段推荐服务的功能
"""

import pytest
from unittest.mock import MagicMock, patch

from backend.services.field_recommendation_service import FieldRecommendationService


class TestFieldRecommendationService:
    """测试FieldRecommendationService类"""

    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return FieldRecommendationService()

    @pytest.fixture
    def mock_patterns(self):
        """模拟字段模式数据"""
        return [
            {
                "param_name": "role_id",
                "param_name_cn": "角色ID",
                "param_type": "base",
                "usage_count": 150,
                "event_count": 10,
                "is_common": True,
                "inferred_type": "base"
            },
            {
                "param_name": "zone_id",
                "param_name_cn": "区域ID",
                "param_type": "param",
                "usage_count": 120,
                "event_count": 8,
                "is_common": True,
                "inferred_type": "param"
            }
        ]

    @pytest.fixture
    def mock_statistics(self):
        """模拟统计数据"""
        return {
            "total_unique_fields": 50,
            "total_field_usage": 500,
            "most_common_fields": [
                {"param_name": "role_id", "count": 150},
                {"param_name": "account_id", "count": 142}
            ],
            "type_distribution": {
                "base": 20,
                "param": 25,
                "calculate": 5
            }
        }

    def test_get_recommendations_with_game_gid(self, service, mock_patterns):
        """测试基于游戏GID获取推荐"""
        with patch.object(
            service.field_pattern_repo,
            'get_common_field_patterns',
            return_value=mock_patterns
        ):
            recommendations = service.get_recommendations(game_gid=10000147, limit=10)

            assert len(recommendations) == 2
            assert recommendations[0]["param_name"] == "role_id"
            assert recommendations[0]["is_common"] is True
            assert "recommendation_reason" in recommendations[0]

    def test_get_recommendations_with_field_hint(self, service, mock_patterns):
        """测试基于字段名称提示获取推荐"""
        with patch.object(
            service.field_pattern_repo,
            'find_similar_fields',
            return_value=mock_patterns
        ):
            recommendations = service.get_recommendations(
                field_name_hint="role",
                limit=10
            )

            assert len(recommendations) == 2
            assert "similarity_score" in recommendations[0]
            assert "recommendation_reason" in recommendations[0]

    def test_get_recommendations_with_event_name(self, service, mock_patterns):
        """测试基于事件名称获取推荐"""
        with patch.object(
            service.field_pattern_repo,
            'get_field_patterns_by_event_type',
            return_value=mock_patterns
        ):
            recommendations = service.get_recommendations(
                event_name="login",
                limit=10
            )

            assert len(recommendations) == 2
            assert "recommendation_reason" in recommendations[0]
            assert "login" in recommendations[0]["recommendation_reason"]

    def test_get_recommendations_deduplication(self, service):
        """测试推荐结果去重"""
        mock_patterns = [
            {
                "param_name": "role_id",
                "param_name_cn": "角色ID",
                "param_type": "base",
                "usage_count": 150,
                "event_count": 10,
                "is_common": True,
                "inferred_type": "base"
            },
            {
                "param_name": "role_id",  # 重复
                "param_name_cn": "角色ID",
                "param_type": "base",
                "usage_count": 150,
                "event_count": 10,
                "is_common": True,
                "inferred_type": "base"
            }
        ]

        with patch.object(
            service.field_pattern_repo,
            'get_common_field_patterns',
            return_value=mock_patterns
        ):
            recommendations = service.get_recommendations(game_gid=10000147, limit=10)

            # 应该去重
            assert len(recommendations) == 1
            assert recommendations[0]["param_name"] == "role_id"

    def test_get_common_patterns(self, service, mock_patterns, mock_statistics):
        """测试获取常用字段模式"""
        with patch.object(
            service.field_pattern_repo,
            'get_common_field_patterns',
            return_value=mock_patterns
        ), patch.object(
            service.field_pattern_repo,
            'get_field_usage_statistics',
            return_value=mock_statistics
        ):
            result = service.get_common_patterns(game_gid=10000147, limit=10)

            assert "patterns" in result
            assert "statistics" in result
            assert len(result["patterns"]) == 2
            assert result["statistics"]["total_unique_fields"] == 50

    def test_infer_field_type_base(self, service):
        """测试推断基础字段类型"""
        result = service.infer_field_type("role_id")

        assert result["field_name"] == "role_id"
        assert result["inferred_type"] == "base"
        assert result["suggested_hive_type"] == "BIGINT"
        assert result["confidence"] > 0.9
        assert "reasoning" in result

    def test_infer_field_type_param(self, service):
        """测试推断参数字段类型"""
        result = service.infer_field_type("zone_id")

        assert result["field_name"] == "zone_id"
        assert result["inferred_type"] == "param"
        assert result["suggested_hive_type"] == "BIGINT"
        assert "reasoning" in result

    def test_infer_field_type_calculate(self, service):
        """测试推断计算字段类型"""
        result = service.infer_field_type("count_total")

        assert result["field_name"] == "count_total"
        assert result["inferred_type"] == "calculate"
        assert result["suggested_hive_type"] == "DOUBLE"
        assert "reasoning" in result

    def test_infer_field_type_empty_name(self, service):
        """测试空字段名称"""
        with pytest.raises(ValueError, match="field_name cannot be empty"):
            service.infer_field_type("")

    def test_infer_field_type_whitespace_name(self, service):
        """测试空白字段名称"""
        with pytest.raises(ValueError, match="field_name cannot be empty"):
            service.infer_field_type("   ")

    def test_suggest_hive_type_for_id_fields(self, service):
        """测试ID字段的Hive类型建议"""
        assert service._suggest_hive_type("role_id", "base") == "BIGINT"
        assert service._suggest_hive_type("user_id", "base") == "BIGINT"
        assert service._suggest_hive_type("uid", "base") == "BIGINT"

    def test_suggest_hive_type_for_count_fields(self, service):
        """测试计数字段的Hive类型建议"""
        assert service._suggest_hive_type("count", "param") == "INT"
        assert service._suggest_hive_type("num", "param") == "INT"
        assert service._suggest_hive_type("amount", "param") == "INT"

    def test_suggest_hive_type_for_price_fields(self, service):
        """测试价格字段的Hive类型建议"""
        assert service._suggest_hive_type("price", "param") == "DOUBLE"
        assert service._suggest_hive_type("cost", "param") == "DOUBLE"
        assert service._suggest_hive_type("value", "param") == "DOUBLE"

    def test_suggest_hive_type_for_boolean_fields(self, service):
        """测试布尔字段的Hive类型建议"""
        assert service._suggest_hive_type("is_active", "param") == "BOOLEAN"
        assert service._suggest_hive_type("has_permission", "param") == "BOOLEAN"
        assert service._suggest_hive_type("can_edit", "param") == "BOOLEAN"

    def test_suggest_hive_type_for_string_fields(self, service):
        """测试字符串字段的Hive类型建议"""
        assert service._suggest_hive_type("name", "param") == "STRING"
        assert service._suggest_hive_type("title", "param") == "STRING"
        assert service._suggest_hive_type("description", "param") == "STRING"

    def test_calculate_type_confidence_high(self, service):
        """测试高置信度计算"""
        confidence = service._calculate_type_confidence("role_id", "base")
        assert confidence == 0.95

    def test_calculate_type_confidence_medium(self, service):
        """测试中等置信度计算"""
        confidence = service._calculate_type_confidence("zone_id", "param")
        assert confidence == 0.80

    def test_calculate_type_confidence_default(self, service):
        """测试默认置信度计算"""
        confidence = service._calculate_type_confidence("custom_field", "param")
        assert confidence == 0.60

    def test_generate_type_reasoning_base(self, service):
        """测试生成基础字段推理说明"""
        reasoning = service._generate_type_reasoning("role_id", "base", 0.95)
        assert "基础字段" in reasoning
        assert "role_id" in reasoning

    def test_generate_type_reasoning_param(self, service):
        """测试生成参数字段推理说明"""
        reasoning = service._generate_type_reasoning("zone_id", "param", 0.75)
        assert "参数字段" in reasoning
        assert "zone_id" in reasoning

    def test_generate_type_reasoning_calculate(self, service):
        """测试生成计算字段推理说明"""
        reasoning = service._generate_type_reasoning("count_total", "calculate", 0.70)
        assert "计算字段" in reasoning
        assert "count_total" in reasoning

    def test_invalidate_recommendations_cache_with_game_gid(self, service):
        """测试失效特定游戏的推荐缓存"""
        with patch.object(service.invalidator, 'invalidate_pattern') as mock_invalidate:
            service.invalidate_recommendations_cache(game_gid=10000147)

            assert mock_invalidate.call_count == 2

    def test_invalidate_recommendations_cache_all(self, service):
        """测试失效所有推荐缓存"""
        with patch.object(service.invalidator, 'invalidate_pattern') as mock_invalidate:
            service.invalidate_recommendations_cache()

            assert mock_invalidate.call_count == 3


class TestFieldPatternRepository:
    """测试FieldPatternRepository类"""

    @pytest.fixture
    def repository(self):
        """创建仓储实例"""
        from backend.models.repositories.field_pattern_repository import FieldPatternRepository
        return FieldPatternRepository()

    def test_infer_field_type_base_patterns(self, repository):
        """测试基础字段类型推断"""
        assert repository._infer_field_type("role_id") == "base"
        assert repository._infer_field_type("account_id") == "base"
        assert repository._infer_field_type("user_id") == "base"
        assert repository._infer_field_type("uid") == "base"
        assert repository._infer_field_type("game_id") == "base"
        assert repository._infer_field_type("gid") == "base"
        assert repository._infer_field_type("server_id") == "base"
        assert repository._infer_field_type("channel_id") == "base"
        assert repository._infer_field_type("platform") == "base"
        assert repository._infer_field_type("device_id") == "base"
        assert repository._infer_field_type("utdid") == "base"
        assert repository._infer_field_type("ds") == "base"
        assert repository._infer_field_type("dt") == "base"
        assert repository._infer_field_type("hour") == "base"

    def test_infer_field_type_param_patterns(self, repository):
        """测试参数字段类型推断"""
        assert repository._infer_field_type("zone_id") == "param"
        assert repository._infer_field_type("item_id") == "param"
        assert repository._infer_field_type("skill_id") == "param"
        assert repository._infer_field_type("monster_id") == "param"

    def test_infer_field_type_calculate_patterns(self, repository):
        """测试计算字段类型推断"""
        assert repository._infer_field_type("count_total") == "calculate"
        assert repository._infer_field_type("sum_amount") == "calculate"
        assert repository._infer_field_type("avg_level") == "calculate"
        assert repository._infer_field_type("max_score") == "calculate"
        assert repository._infer_field_type("min_value") == "calculate"
        assert repository._infer_field_type("total_users") == "calculate"

    def test_calculate_similarity_identical(self, repository):
        """测试相同字符串的相似度"""
        similarity = repository._calculate_similarity("role_id", "role_id")
        assert similarity == 1.0

    def test_calculate_similarity_similar(self, repository):
        """测试相似字符串的相似度"""
        similarity = repository._calculate_similarity("user_id", "userid")
        assert similarity > 0.8

    def test_calculate_similarity_different(self, repository):
        """测试不同字符串的相似度"""
        similarity = repository._calculate_similarity("role_id", "zone_id")
        assert similarity < 1.0
        assert similarity > 0.0

    def test_calculate_similarity_empty(self, repository):
        """测试空字符串的相似度"""
        similarity = repository._calculate_similarity("", "role_id")
        assert similarity == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
