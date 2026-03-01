#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event实体单元测试
"""

import pytest
from backend.domain.models.event import Event
from backend.domain.models.parameter import Parameter
from backend.domain.exceptions.domain_exceptions import ParameterAlreadyExists


class TestEvent:
    """Event实体测试"""

    def test_create_event(self):
        """测试创建事件"""
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001,
            description="用户登录"
        )
        
        assert event.id == 1
        assert event.name == "登录事件"
        assert event.category == "user"
        assert event.game_gid == 1001
        assert event.description == "用户登录"
        assert len(event.parameters) == 0

    def test_add_parameter(self):
        """测试添加参数"""
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        param = Parameter(
            name="user_id",
            type="int",
            json_path="$.user_id",
            description="用户ID"
        )
        
        event.add_parameter(param)
        
        assert len(event.parameters) == 1
        assert event.parameters[0].name == "user_id"

    def test_add_duplicate_parameter_raises_error(self):
        """测试添加重复参数抛出异常"""
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        param1 = Parameter(name="user_id", type="int", json_path="$.user_id")
        param2 = Parameter(name="user_id", type="int", json_path="$.user_id")
        
        event.add_parameter(param1)
        
        with pytest.raises(ParameterAlreadyExists):
            event.add_parameter(param2)

    def test_has_parameter(self):
        """测试检查参数是否存在"""
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        param = Parameter(name="user_id", type="int", json_path="$.user_id")
        
        assert not event.has_parameter("user_id")
        event.add_parameter(param)
        assert event.has_parameter("user_id")

    def test_get_parameter(self):
        """测试获取参数"""
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        param = Parameter(name="user_id", type="int", json_path="$.user_id")
        event.add_parameter(param)
        
        retrieved_param = event.get_parameter("user_id")
        assert retrieved_param is not None
        assert retrieved_param.name == "user_id"

    def test_get_parameter_not_found(self):
        """测试获取不存在的参数"""
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        param = event.get_parameter("nonexistent")
        assert param is None

    def test_update_event(self):
        """测试更新事件"""
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        event.update(name="新登录事件", description="新的描述")
        
        assert event.name == "新登录事件"
        assert event.description == "新的描述"

    def test_remove_parameter(self):
        """测试删除参数"""
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        param = Parameter(name="user_id", type="int", json_path="$.user_id")
        event.add_parameter(param)
        
        event.remove_parameter("user_id")
        
        assert len(event.parameters) == 0
        assert not event.has_parameter("user_id")
