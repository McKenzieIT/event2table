#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game聚合根单元测试
"""

import pytest
from backend.domain.models.game import Game
from backend.domain.models.event import Event
from backend.domain.models.parameter import Parameter
from backend.domain.exceptions.domain_exceptions import (
    EventAlreadyExists,
    CannotDeleteGameWithEvents
)


class TestGame:
    """Game聚合根测试"""

    def test_create_game(self):
        """测试创建游戏"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        
        assert game.gid == 1001
        assert game.name == "测试游戏"
        assert game.ods_db == "test_db"
        assert len(game.events) == 0
        assert len(game._domain_events) == 1
        assert game._domain_events[0].__class__.__name__ == "GameCreated"

    def test_add_event(self):
        """测试添加事件"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001,
            description="用户登录"
        )
        
        game.add_event(event)
        
        assert len(game.events) == 1
        assert game.events[0].name == "登录事件"
        assert len(game._domain_events) == 2

    def test_add_duplicate_event_raises_error(self):
        """测试添加重复事件抛出异常"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        event1 = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        event2 = Event(
            id=2,
            name="登录事件",  # 相同名称
            category="user",
            game_gid=1001
        )
        
        game.add_event(event1)
        
        with pytest.raises(EventAlreadyExists):
            game.add_event(event2)

    def test_has_event(self):
        """测试检查事件是否存在"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        
        assert not game.has_event("登录事件")
        game.add_event(event)
        assert game.has_event("登录事件")

    def test_can_delete_with_no_events(self):
        """测试无事件时可以删除"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        assert game.can_delete() is True

    def test_can_delete_with_events(self):
        """测试有事件时不能删除"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        game.add_event(event)
        assert game.can_delete() is False

    def test_delete_with_no_events(self):
        """测试删除无事件的游戏"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        game.delete()
        assert len(game._domain_events) == 2  # GameCreated + GameDeleted

    def test_delete_with_events_raises_error(self):
        """测试删除有事件的游戏抛出异常"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        event = Event(
            id=1,
            name="登录事件",
            category="user",
            game_gid=1001
        )
        game.add_event(event)
        
        with pytest.raises(CannotDeleteGameWithEvents):
            game.delete()

    def test_update_game(self):
        """测试更新游戏"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        game.update(name="新游戏名称", ods_db="new_db")
        
        assert game.name == "新游戏名称"
        assert game.ods_db == "new_db"

    def test_get_domain_events(self):
        """测试获取领域事件"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        event = Event(id=1, name="登录事件", category="user", game_gid=1001)
        game.add_event(event)
        
        domain_events = game.get_domain_events()
        assert len(domain_events) == 2
        assert domain_events[0].__class__.__name__ == "GameCreated"
        assert domain_events[1].__class__.__name__ == "EventAddedToGame"

    def test_clear_domain_events(self):
        """测试清除领域事件"""
        game = Game.create(gid=1001, name="测试游戏", ods_db="test_db")
        game.clear_domain_events()
        
        assert len(game.get_domain_events()) == 0
