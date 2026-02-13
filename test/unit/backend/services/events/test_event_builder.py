#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Builder 单元测试

测试EventBuilder使用建造者模式创建事件
"""

import pytest
from backend.models.events import EventBuilder, EventData


class TestEventBuilder:
    """测试EventBuilder建造者模式"""

    def test_builder_exists(self):
        """测试EventBuilder类存在"""
        builder = EventBuilder()
        assert builder is not None
        assert hasattr(builder, 'set_game')
        assert hasattr(builder, 'set_names')
        assert hasattr(builder, 'set_category')
        assert hasattr(builder, 'set_parameters')
        assert hasattr(builder, 'build')

    def test_builder_set_game(self):
        """测试设置游戏信息"""
        builder = EventBuilder()
        result = builder.set_game(10000147, "ieu_ods")

        assert result is builder  # Fluent interface
        assert builder.game_gid == 10000147
        assert builder.ods_db == "ieu_ods"

    def test_builder_set_names(self):
        """测试设置事件名称"""
        builder = EventBuilder()
        result = builder.set_names("login", "登录")

        assert result is builder  # Fluent interface
        assert builder.event_name == "login"
        assert builder.event_name_cn == "登录"

    def test_builder_set_category(self):
        """测试设置分类"""
        builder = EventBuilder()
        result = builder.set_category(1)

        assert result is builder  # Fluent interface
        assert builder.category_id == 1

    def test_builder_set_parameters(self):
        """测试设置参数"""
        builder = EventBuilder()
        params = [
            {"name": "role_id", "name_cn": "角色ID", "type": 1, "description": "角色ID"},
            {"name": "account_id", "name_cn": "账号ID", "type": 1, "description": "账号ID"},
        ]
        result = builder.set_parameters(params)

        assert result is builder  # Fluent interface
        assert len(builder.parameters) == 2

    def test_builder_builds_event_data(self):
        """测试构建事件数据"""
        event_data = (
            EventBuilder()
            .set_game(10000147, "ieu_ods")
            .set_names("login", "登录")
            .set_category(1)
            .set_parameters([
                {"name": "role_id", "name_cn": "角色ID", "type": 1, "description": "角色ID"}
            ])
            .build()
        )

        assert event_data.game_gid == 10000147
        assert event_data.event_name == "login"
        assert event_data.event_name_cn == "登录"
        assert event_data.category_id == 1
        assert event_data.source_table == "ieu_ods.ods_10000147_all_view"
        assert event_data.target_table == "ieu_cdm.v_dwd_10000147_login_di"
        assert event_data.include_in_common_params == 0  # Default

    def test_builder_calculates_source_table(self):
        """测试计算源表名"""
        event_data = (
            EventBuilder()
            .set_game(10000147, "ieu_ods")
            .set_names("test", "测试")
            .set_category(1)
            .build()
        )

        assert event_data.source_table == "ieu_ods.ods_10000147_all_view"

    def test_builder_calculates_target_table_domestic(self):
        """测试计算目标表名（国内游戏）"""
        event_data = (
            EventBuilder()
            .set_game(10000147, "ieu_ods")
            .set_names("login", "登录")
            .set_category(1)
            .build()
        )

        assert event_data.target_table == "ieu_cdm.v_dwd_10000147_login_di"

    def test_builder_calculates_target_table_overseas(self):
        """测试计算目标表名（海外游戏）"""
        event_data = (
            EventBuilder()
            .set_game(99999999, "overseas_ods")
            .set_names("logout", "登出")
            .set_category(1)
            .build()
        )

        assert event_data.target_table == "overseas_ods.v_dwd_99999999_logout_di"

    def test_builder_sanitizes_event_name(self):
        """测试清理事件名中的特殊字符"""
        event_data = (
            EventBuilder()
            .set_game(10000147, "ieu_ods")
            .set_names("user.login", "用户登录")
            .set_category(1)
            .build()
        )

        # 点号应该被替换为下划线
        assert event_data.target_table == "ieu_cdm.v_dwd_10000147_user_login_di"

    def test_builder_sets_include_flag(self):
        """测试设置是否包含在公共参数中"""
        event_data = (
            EventBuilder()
            .set_game(10000147, "ieu_ods")
            .set_names("login", "登录")
            .set_category(1)
            .set_include_in_common(True)
            .build()
        )

        assert event_data.include_in_common_params == 1


class TestEventData:
    """测试EventData数据类"""

    def test_event_data_attributes(self):
        """测试EventData包含所有必需属性"""
        event_data = EventData(
            game_gid=10000147,
            event_name="login",
            event_name_cn="登录",
            category_id=1,
            source_table="ieu_ods.ods_10000147_all_view",
            target_table="ieu_cdm.v_dwd_10000147_login_di",
            include_in_common_params=0,
            parameters=[]
        )

        assert event_data.game_gid == 10000147
        assert event_data.event_name == "login"
        assert event_data.event_name_cn == "登录"
        assert event_data.category_id == 1
        assert event_data.source_table == "ieu_ods.ods_10000147_all_view"
        assert event_data.target_table == "ieu_cdm.v_dwd_10000147_login_di"
        assert event_data.include_in_common_params == 0
        assert event_data.parameters == []

    def test_event_data_with_parameters(self):
        """测试EventData包含参数"""
        params = [
            {"name": "role_id", "name_cn": "角色ID", "type": 1, "description": "角色ID"},
        ]

        event_data = EventData(
            game_gid=10000147,
            event_name="login",
            event_name_cn="登录",
            category_id=1,
            source_table="ieu_ods.ods_10000147_all_view",
            target_table="ieu_cdm.v_dwd_10000147_login_di",
            include_in_common_params=1,
            parameters=params
        )

        assert len(event_data.parameters) == 1
        assert event_data.parameters[0]["name"] == "role_id"


class TestEventBuilderValidation:
    """测试EventBuilder验证逻辑"""

    def test_builder_validates_required_fields(self):
        """测试建造者验证必需字段"""
        builder = EventBuilder()

        # 不设置任何字段，构建应该失败
        with pytest.raises(ValueError, match="game_gid"):
            builder.build()

    def test_builder_validates_game_required(self):
        """测试必须设置游戏"""
        builder = EventBuilder()
        builder.set_names("login", "登录")

        with pytest.raises(ValueError, match="game_gid"):
            builder.build()

    def test_builder_validates_names_required(self):
        """测试必须设置事件名"""
        builder = EventBuilder()
        builder.set_game(10000147, "ieu_ods")

        with pytest.raises(ValueError, match="event_name"):
            builder.build()

    def test_builder_validates_category_required(self):
        """测试必须设置分类"""
        builder = EventBuilder()
        builder.set_game(10000147, "ieu_ods")
        builder.set_names("login", "登录")

        with pytest.raises(ValueError, match="category_id"):
            builder.build()


class TestEventBuilderIntegration:
    """集成测试"""

    def test_complete_builder_flow(self):
        """测试完整的建造者流程"""
        params = [
            {"name": "role_id", "name_cn": "角色ID", "type": 1, "description": "角色ID"},
            {"name": "account_id", "name_cn": "账号ID", "type": 1, "description": "账号ID"},
            {"name": "level", "name_cn": "等级", "type": 2, "description": "等级"},
        ]

        event_data = (
            EventBuilder()
            .set_game(10000147, "ieu_ods")
            .set_names("login", "登录")
            .set_category(1)
            .set_parameters(params)
            .set_include_in_common(True)
            .build()
        )

        # 验证所有字段
        assert event_data.game_gid == 10000147
        assert event_data.event_name == "login"
        assert event_data.event_name_cn == "登录"
        assert event_data.category_id == 1
        assert event_data.include_in_common_params == 1
        assert len(event_data.parameters) == 3

        # 验证表名计算
        assert event_data.source_table == "ieu_ods.ods_10000147_all_view"
        assert event_data.target_table == "ieu_cdm.v_dwd_10000147_login_di"
