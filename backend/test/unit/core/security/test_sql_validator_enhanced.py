#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLValidator增强功能单元测试
"""

import pytest
from backend.core.security.sql_validator import SQLValidator


class TestSQLValidatorEnhanced:
    """测试SQLValidator的增强HQL验证功能"""

    def test_validate_hql_expression_safe(self):
        """测试安全的HQL表达式验证"""
        # 安全的get_json_object表达式
        safe_expr = "get_json_object(params, '$.zoneId') AS zone_id"
        result = SQLValidator.validate_hql_expression(safe_expr)
        assert result == safe_expr

    def test_validate_hql_expression_sql_injection(self):
        """测试SQL注入攻击检测"""
        # 尝试SQL注入
        dangerous_expr = "get_json_object(params, '$.zoneId'); DROP TABLE games--"
        with pytest.raises(ValueError, match="Dangerous keyword"):
            SQLValidator.validate_hql_expression(dangerous_expr)

    def test_validate_hql_expression_disallowed_function(self):
        """测试不允许的函数"""
        # 尝试使用不允许的函数
        disallowed_expr = "eval('malicious_code')"
        with pytest.raises(ValueError, match="Disallowed function"):
            SQLValidator.validate_hql_expression(disallowed_expr)

    def test_validate_hql_expression_invalid_json_path(self):
        """测试无效的JSON路径"""
        # 包含特殊字符的JSON路径
        invalid_json_path = "get_json_object(params, '$.zone@Id')"
        with pytest.raises(ValueError, match="Invalid JSON path"):
            SQLValidator.validate_hql_expression(invalid_json_path)

    def test_validate_join_condition_valid(self):
        """测试有效的JOIN条件"""
        valid_condition = "t1.role_id = t2.role_id"
        result = SQLValidator.validate_join_condition(valid_condition)
        assert result == valid_condition

    def test_validate_join_condition_invalid_format(self):
        """测试无效的JOIN条件格式"""
        # 不是table.column = table.column格式
        invalid_condition = "role_id LIKE '%test%'"
        with pytest.raises(ValueError, match="Invalid JOIN condition format"):
            SQLValidator.validate_join_condition(invalid_condition)

    def test_validate_join_condition_sql_injection(self):
        """测试JOIN条件的SQL注入检测"""
        dangerous_condition = "t1.id = t2.id; DROP TABLE games--"
        with pytest.raises(ValueError, match="Dangerous keyword"):
            SQLValidator.validate_join_condition(dangerous_condition)

    def test_validate_join_type_valid(self):
        """测试有效的JOIN类型"""
        valid_types = ['LEFT_JOIN', 'RIGHT_JOIN', 'INNER_JOIN', 'FULL_JOIN']
        for join_type in valid_types:
            result = SQLValidator.validate_join_type(join_type)
            assert result == join_type.upper()

    def test_validate_join_type_invalid(self):
        """测试无效的JOIN类型"""
        invalid_join_type = "CROSS_JOIN_INVALID"
        with pytest.raises(ValueError, match="Invalid JOIN type"):
            SQLValidator.validate_join_type(invalid_join_type)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
