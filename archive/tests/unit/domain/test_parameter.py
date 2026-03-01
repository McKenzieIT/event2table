#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter值对象单元测试
"""

import pytest
from backend.domain.models.parameter import Parameter


class TestParameter:
    """Parameter值对象测试"""

    def test_create_parameter(self):
        """测试创建参数"""
        param = Parameter(
            name="user_id",
            type="int",
            json_path="$.user_id",
            description="用户ID"
        )
        
        assert param.name == "user_id"
        assert param.type == "int"
        assert param.json_path == "$.user_id"
        assert param.description == "用户ID"

    def test_create_parameter_without_description(self):
        """测试创建无描述的参数"""
        param = Parameter(
            name="user_id",
            type="int",
            json_path="$.user_id"
        )
        
        assert param.name == "user_id"
        assert param.description is None

    def test_create_parameter_with_empty_name_raises_error(self):
        """测试空名称参数抛出异常"""
        with pytest.raises(ValueError):
            Parameter(name="", type="int", json_path="$.user_id")

    def test_create_parameter_with_invalid_type_raises_error(self):
        """测试无效类型参数抛出异常"""
        with pytest.raises(ValueError):
            Parameter(name="user_id", type="invalid", json_path="$.user_id")

    def test_valid_parameter_types(self):
        """测试有效参数类型"""
        valid_types = ["string", "int", "float", "boolean", "array"]
        
        for param_type in valid_types:
            param = Parameter(
                name="test_param",
                type=param_type,
                json_path="$.test"
            )
            assert param.type == param_type

    def test_parameter_is_immutable(self):
        """测试参数不可变性"""
        param = Parameter(
            name="user_id",
            type="int",
            json_path="$.user_id"
        )
        
        # 尝试修改应该失败
        with pytest.raises(Exception):  # frozen=True 抛出异常
            param.name = "new_name"
