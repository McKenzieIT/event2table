#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL History Module Integration Tests

测试HQLHistoryEntity, HQLHistoryRepository, HQLHistoryService的集成
"""

import pytest

from backend.models.entities import HQLHistoryEntity
from backend.models.repositories.hql_history_repository import HQLHistoryRepository
from backend.services.hql.hql_history_service import HQLHistoryService


@pytest.mark.integration
class TestHQLHistoryModuleIntegration:
    """HQL History模块集成测试"""

    def test_entity_serialization(self):
        """测试HQLHistoryEntity序列化/反序列化"""
        history = HQLHistoryEntity(
            user_id=1,
            session_id="test-session-123",
            events_json=[{"event_name": "login", "table_name": "ods_login"}],
            fields_json=[{"name": "role_id", "type": "base"}],
            conditions_json=[{"field": "zone_id", "operator": ">", "value": "1"}],
            mode="single",
            hql="SELECT role_id FROM table WHERE ds = '${bizdate}'",
            hql_type="select",
            game_gid=90000101,
            name_en="Login Event",
            name_cn="登录事件",
        )
        history_dict = history.model_dump()

        assert history_dict["user_id"] == 1
        assert history_dict["session_id"] == "test-session-123"
        assert history_dict["events_json"][0]["event_name"] == "login"
        assert history_dict["fields_json"][0]["name"] == "role_id"
        assert history_dict["mode"] == "single"

    def test_repository_returns_entities(self):
        """测试HQLHistoryRepository返回Entity对象"""
        repo = HQLHistoryRepository()

        # 创建测试HQL历史记录
        history = HQLHistoryEntity(
            user_id=1,
            session_id="test-repo-123",
            events_json=[{"event_name": "login"}],
            fields_json=[{"name": "role_id"}],
            conditions_json=[],
            mode="single",
            hql="SELECT role_id FROM table",
            hql_type="select",
        )
        history_id = repo.create(history)

        # 查询并验证返回Entity
        retrieved_history = repo.find_by_id(history_id)
        assert isinstance(retrieved_history, HQLHistoryEntity)
        assert retrieved_history.mode == "single"
        assert retrieved_history.events_json[0]["event_name"] == "login"
        assert retrieved_history.hql_type == "select"

        # 清理
        repo.delete(history_id)

    def test_service_returns_entities(self):
        """测试HQLHistoryService返回Entity对象"""
        service = HQLHistoryService()

        # 创建测试HQL历史记录
        events = [{"event_name": "login"}]
        fields = [{"name": "role_id"}]
        conditions = []

        history_id = service.save_history(
            events=events,
            fields=fields,
            conditions=conditions,
            mode="single",
            hql="SELECT role_id FROM table",
            user_id=1,
            session_id="test-service-123",
            hql_type="select",
        )

        # 验证返回Entity
        retrieved_history = service.get_history_by_id(history_id)
        assert isinstance(retrieved_history, HQLHistoryEntity)
        assert retrieved_history.mode == "single"
        assert retrieved_history.events_json[0]["event_name"] == "login"

        # 清理
        service.delete_history(history_id)

    def test_json_field_serialization(self):
        """测试JSON字段的自动序列化"""
        repo = HQLHistoryRepository()

        # 创建包含复杂JSON的HQL历史记录
        history = HQLHistoryEntity(
            user_id=1,
            session_id="test-json-123",
            events_json=[
                {
                    "event_name": "login",
                    "table_name": "ods_login",
                    "game_gid": 10000147,
                }
            ],
            fields_json=[
                {"name": "role_id", "type": "base", "hive_type": "BIGINT"},
                {"name": "zone_id", "type": "param", "json_path": "$.zoneId"},
            ],
            conditions_json=[
                {"field": "zone_id", "operator": ">", "value": "1"},
                {"field": "level", "operator": ">=", "value": "10"},
            ],
            mode="where",
            hql="SELECT * FROM table WHERE zone_id > 1 AND level >= 10",
            hql_type="select",
            metadata_json={"performance_score": 85, "execution_time": 1.2},
        )
        history_id = repo.create(history)

        # 验证JSON正确序列化和反序列化
        retrieved = repo.find_by_id(history_id)
        assert isinstance(retrieved.events_json, list)
        assert len(retrieved.events_json) == 1
        assert retrieved.events_json[0]["event_name"] == "login"

        assert isinstance(retrieved.fields_json, list)
        assert len(retrieved.fields_json) == 2
        assert retrieved.fields_json[1]["json_path"] == "$.zoneId"

        assert isinstance(retrieved.conditions_json, list)
        assert len(retrieved.conditions_json) == 2
        assert retrieved.conditions_json[0]["field"] == "zone_id"

        assert isinstance(retrieved.metadata_json, dict)
        assert retrieved.metadata_json["performance_score"] == 85

        # 清理
        repo.delete(history_id)

    def test_save_history(self):
        """测试保存HQL历史记录"""
        service = HQLHistoryService()

        events = [{"event_name": "login"}]
        fields = [{"name": "role_id"}]
        conditions = []

        history_id = service.save_history(
            events=events,
            fields=fields,
            conditions=conditions,
            mode="single",
            hql="SELECT role_id FROM table",
            user_id=1,
            session_id="test-save-123",
            hql_type="select",
            game_gid=90000102,
            name_en="Test History",
            name_cn="测试历史",
        )

        assert history_id is not None
        assert history_id > 0

        # 验证保存成功
        history = service.get_history_by_id(history_id)
        assert history is not None
        assert history.game_gid == 90000102
        assert history.name_en == "Test History"
        assert history.name_cn == "测试历史"

        # 清理
        service.delete_history(history_id)

    def test_restore_history(self):
        """测试恢复历史版本"""
        service = HQLHistoryService()

        events = [{"event_name": "login", "table_name": "ods_login"}]
        fields = [{"name": "role_id", "type": "base"}]
        conditions = [{"field": "zone_id", "operator": ">", "value": "1"}]

        history_id = service.save_history(
            events=events,
            fields=fields,
            conditions=conditions,
            mode="where",
            hql="SELECT * FROM table WHERE zone_id > 1",
            user_id=1,
            session_id="test-restore-123",
            hql_type="select",
        )

        # 恢复历史版本
        restored = service.restore_history(history_id)
        assert restored is not None
        assert restored["events"][0]["event_name"] == "login"
        assert restored["fields"][0]["name"] == "role_id"
        assert restored["conditions"][0]["field"] == "zone_id"
        assert restored["mode"] == "where"

        # 清理
        service.delete_history(history_id)

    def test_delete_history(self):
        """测试删除HQL历史记录"""
        service = HQLHistoryService()

        history_id = service.save_history(
            events=[{"event_name": "login"}],
            fields=[{"name": "role_id"}],
            conditions=[],
            mode="single",
            hql="SELECT role_id FROM table",
            user_id=1,
            session_id="test-delete-123",
            hql_type="select",
        )

        # 删除记录
        success = service.delete_history(history_id)
        assert success is True

        # 验证已删除
        deleted_history = service.get_history_by_id(history_id)
        assert deleted_history is None

    def test_search_history(self):
        """测试搜索HQL历史记录"""
        service = HQLHistoryService()

        # 创建多个测试记录
        service.save_history(
            events=[{"event_name": "login"}],
            fields=[{"name": "role_id"}],
            conditions=[],
            mode="single",
            hql="SELECT role_id FROM login_table",
            user_id=1,
            session_id="test-search-123",
            hql_type="select",
            game_gid=90000103,
            name_en="Login Query",
            name_cn="登录查询",
        )

        service.save_history(
            events=[{"event_name": "logout"}],
            fields=[{"name": "account_id"}],
            conditions=[],
            mode="single",
            hql="SELECT account_id FROM logout_table",
            user_id=1,
            session_id="test-search-123",
            hql_type="select",
            game_gid=90000103,
            name_en="Logout Query",
            name_cn="登出查询",
        )

        # 搜索关键词
        results = service.search_history(keyword="Login", user_id=1)
        assert len(results) >= 1
        assert any("Login" in (h.name_en or "") for h in results)

        # 按游戏GID搜索
        results = service.search_history(game_gid=90000103, user_id=1)
        assert len(results) >= 2

    def test_canvas_hql_type(self):
        """测试canvas类型的HQL(JSON对象)"""
        service = HQLHistoryService()

        canvas_hql = {
            "create_table": "CREATE TABLE test...",
            "insert_overwrite": "INSERT OVERWRITE...",
            "select": "SELECT * FROM...",
        }

        history_id = service.save_history(
            events=[{"event_name": "login"}],
            fields=[{"name": "role_id"}],
            conditions=[],
            mode="union",
            hql=canvas_hql,
            hql_type="canvas",
            user_id=1,
            session_id="test-canvas-123",
        )

        # 验证保存成功
        history = service.get_history_by_id(history_id)
        assert history is not None
        assert history.hql_type == "canvas"
        # canvas类型的hql应该是JSON字符串
        assert isinstance(history.hql, str)

        # 清理
        service.delete_history(history_id)

    def test_get_history_by_user(self):
        """测试获取指定用户的HQL历史记录"""
        repo = HQLHistoryRepository()

        # 创建多个用户的历史记录
        repo.create(
            HQLHistoryEntity(
                user_id=100,
                session_id="test-user-100",
                events_json=[{"event_name": "login"}],
                fields_json=[{"name": "role_id"}],
                conditions_json=[],
                mode="single",
                hql="SELECT role_id FROM table",
                hql_type="select",
            )
        )

        repo.create(
            HQLHistoryEntity(
                user_id=100,
                session_id="test-user-100-2",
                events_json=[{"event_name": "logout"}],
                fields_json=[{"name": "account_id"}],
                conditions_json=[],
                mode="single",
                hql="SELECT account_id FROM table",
                hql_type="select",
            )
        )

        repo.create(
            HQLHistoryEntity(
                user_id=200,
                session_id="test-user-200",
                events_json=[{"event_name": "login"}],
                fields_json=[{"name": "role_id"}],
                conditions_json=[],
                mode="single",
                hql="SELECT role_id FROM table",
                hql_type="select",
            )
        )

        # 查询用户100的历史记录
        histories = repo.find_by_user_id(100)
        assert len(histories) >= 2
        user_events = [h.events_json[0]["event_name"] for h in histories]
        assert "login" in user_events
        assert "logout" in user_events

        # 清理(通过删除所有测试创建的记录)
        for h in histories:
            repo.delete(h.id)

    def test_count_by_user(self):
        """测试统计用户的HQL历史记录数量"""
        repo = HQLHistoryRepository()

        # 创建测试记录
        repo.create(
            HQLHistoryEntity(
                user_id=300,
                session_id="test-count-1",
                events_json=[{"event_name": "login"}],
                fields_json=[{"name": "role_id"}],
                conditions_json=[],
                mode="single",
                hql="SELECT 1",
                hql_type="select",
            )
        )

        repo.create(
            HQLHistoryEntity(
                user_id=300,
                session_id="test-count-2",
                events_json=[{"event_name": "logout"}],
                fields_json=[{"name": "account_id"}],
                conditions_json=[],
                mode="single",
                hql="SELECT 2",
                hql_type="select",
            )
        )

        repo.create(
            HQLHistoryEntity(
                user_id=300,
                session_id="test-count-3",
                events_json=[{"event_name": "level_up"}],
                fields_json=[{"name": "level"}],
                conditions_json=[],
                mode="single",
                hql="SELECT 3",
                hql_type="select",
            )
        )

        # 统计数量
        count = repo.count_by_user_id(300)
        assert count == 3

        # 清理
        histories = repo.find_by_user_id(300)
        for h in histories:
            repo.delete(h.id)
