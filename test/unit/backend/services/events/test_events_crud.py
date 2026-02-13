#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Event CRUD Operations
Tests for backend/models/events.py module

Following TDD principle: Write tests first, watch them fail, then implement.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.models.events import (
    EventData,
    EventBuilder,
    _parse_event_parameters,
    _build_event_from_form,
)


class TestEventData:
    """Test EventData dataclass"""

    def test_event_data_creation(self):
        """Test creating EventData with all fields"""
        event = EventData(
            game_gid=10000147,
            event_name="login",
            event_name_cn="登录",
            category_id=1,
            source_table="ieu_ods.ods_10000147_all_view",
            target_table="ieu_cdm.v_dwd_10000147_login_di",
            include_in_common_params=1,
            parameters=[{"name": "role_id", "type": 1}]
        )

        assert event.game_gid == 10000147
        assert event.event_name == "login"
        assert event.event_name_cn == "登录"
        assert event.category_id == 1
        assert event.include_in_common_params == 1
        assert len(event.parameters) == 1


class TestEventBuilder:
    """Test EventBuilder class"""

    def test_event_builder_initial_state(self):
        """Test EventBuilder initialization with default values"""
        builder = EventBuilder()

        assert builder.game_gid is None
        assert builder.ods_db is None
        assert builder.event_name is None
        assert builder.event_name_cn is None
        assert builder.category_id is None
        assert builder.include_in_common_params == 0
        assert builder.parameters == []

    def test_set_game(self):
        """Test setting game information"""
        builder = EventBuilder()
        result = builder.set_game(10000147, "ieu_ods")

        assert result is builder  # Fluent interface
        assert builder.game_gid == 10000147
        assert builder.ods_db == "ieu_ods"

    def test_set_names(self):
        """Test setting event names"""
        builder = EventBuilder()
        result = builder.set_names("login", "登录")

        assert result is builder  # Fluent interface
        assert builder.event_name == "login"
        assert builder.event_name_cn == "登录"

    def test_set_category(self):
        """Test setting category"""
        builder = EventBuilder()
        result = builder.set_category(1)

        assert result is builder  # Fluent interface
        assert builder.category_id == 1

    def test_set_parameters(self):
        """Test setting parameters"""
        builder = EventBuilder()
        params = [{"name": "role_id", "type": 1}]
        result = builder.set_parameters(params)

        assert result is builder  # Fluent interface
        assert builder.parameters == params

    def test_set_include_in_common_true(self):
        """Test setting include_in_common_params to True"""
        builder = EventBuilder()
        result = builder.set_include_in_common(True)

        assert result is builder  # Fluent interface
        assert builder.include_in_common_params == 1

    def test_set_include_in_common_false(self):
        """Test setting include_in_common_params to False"""
        builder = EventBuilder()
        result = builder.set_include_in_common(False)

        assert result is builder  # Fluent interface
        assert builder.include_in_common_params == 0

    def test_build_success(self):
        """Test successful build with all required fields"""
        builder = (EventBuilder()
                   .set_game(10000147, "ieu_ods")
                   .set_names("login", "登录")
                   .set_category(1)
                   .set_parameters([{"name": "role_id", "type": 1}]
                                   ))

        event = builder.build()

        assert isinstance(event, EventData)
        assert event.game_gid == 10000147
        assert event.event_name == "login"
        assert event.event_name_cn == "登录"
        assert event.category_id == 1
        assert event.source_table == "ieu_ods.ods_10000147_all_view"
        assert event.target_table == "ieu_cdm.v_dwd_10000147_login_di"
        assert event.include_in_common_params == 0
        assert event.parameters == [{"name": "role_id", "type": 1}]

    def test_build_missing_game_gid(self):
        """Test build raises ValueError when game_gid is missing"""
        builder = (EventBuilder()
                   .set_names("login", "登录")
                   .set_category(1))

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "game_gid is required" in str(exc_info.value)

    def test_build_missing_event_name(self):
        """Test build raises ValueError when event_name is missing"""
        builder = (EventBuilder()
                   .set_game(10000147, "ieu_ods")
                   .set_category(1))

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "event_name is required" in str(exc_info.value)

    def test_build_missing_event_name_cn(self):
        """Test build raises ValueError when event_name_cn is missing"""
        builder = (EventBuilder()
                   .set_game(10000147, "ieu_ods")
                   .set_names("login", None)
                   .set_category(1))

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "event_name_cn is required" in str(exc_info.value)

    def test_build_missing_category_id(self):
        """Test build raises ValueError when category_id is missing"""
        builder = (EventBuilder()
                   .set_game(10000147, "ieu_ods")
                   .set_names("login", "登录"))

        with pytest.raises(ValueError) as exc_info:
            builder.build()

        assert "category_id is required" in str(exc_info.value)

    def test_build_table_names_with_ieu_ods(self):
        """Test table name generation with ieu_ods database"""
        builder = (EventBuilder()
                   .set_game(10000147, "ieu_ods")
                   .set_names("login", "登录")
                   .set_category(1))

        event = builder.build()

        assert event.source_table == "ieu_ods.ods_10000147_all_view"
        assert event.target_table == "ieu_cdm.v_dwd_10000147_login_di"

    def test_build_table_names_with_custom_ods(self):
        """Test table name generation with custom ODS database"""
        builder = (EventBuilder()
                   .set_game(10000147, "custom_ods")
                   .set_names("login", "登录")
                   .set_category(1))

        event = builder.build()

        assert event.source_table == "custom_ods.ods_10000147_all_view"
        assert event.target_table == "custom_ods.v_dwd_10000147_login_di"

    def test_build_sanitizes_event_name(self):
        """Test that event name dots are replaced with underscores"""
        builder = (EventBuilder()
                   .set_game(10000147, "ieu_ods")
                   .set_names("user.login", "用户登录")
                   .set_category(1))

        event = builder.build()

        assert event.target_table == "ieu_cdm.v_dwd_10000147_user_login_di"


class TestParseEventParameters:
    """Test _parse_event_parameters function"""

    def test_parse_single_parameter(self):
        """Test parsing a single parameter"""
        request_data = Mock()
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['role_id'],
            'param_name_cn[]': ['角色ID'],
            'param_type[]': ['1'],
            'param_description[]': ['Role identifier']
        }[x]

        params = _parse_event_parameters(request_data)

        assert len(params) == 1
        assert params[0]['name'] == 'role_id'
        assert params[0]['name_cn'] == '角色ID'
        assert params[0]['type'] == 1
        assert params[0]['description'] == 'Role identifier'

    def test_parse_multiple_parameters(self):
        """Test parsing multiple parameters"""
        request_data = Mock()
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['role_id', 'account_id'],
            'param_name_cn[]': ['角色ID', '账号ID'],
            'param_type[]': ['1', '1'],
            'param_description[]': ['Role ID', 'Account ID']
        }[x]

        params = _parse_event_parameters(request_data)

        assert len(params) == 2
        assert params[0]['name'] == 'role_id'
        assert params[1]['name'] == 'account_id'

    def test_parse_ignores_empty_names(self):
        """Test that parameters with empty names are ignored"""
        request_data = Mock()
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['role_id', '', 'account_id'],
            'param_name_cn[]': ['角色ID', '', '账号ID'],
            'param_type[]': ['1', '1', '1'],
            'param_description[]': ['', '', '']
        }[x]

        params = _parse_event_parameters(request_data)

        assert len(params) == 2
        assert params[0]['name'] == 'role_id'
        assert params[1]['name'] == 'account_id'

    def test_parse_handles_missing_arrays(self):
        """Test parsing when arrays have different lengths"""
        request_data = Mock()
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['role_id', 'account_id'],
            'param_name_cn[]': ['角色ID'],
            'param_type[]': ['1'],
            'param_description[]': []
        }[x]

        params = _parse_event_parameters(request_data)

        assert len(params) == 2
        assert params[0]['name_cn'] == '角色ID'
        assert params[1]['name_cn'] == ''
        assert params[0]['type'] == 1
        assert params[1]['type'] == 1

    def test_parse_handles_invalid_type(self):
        """Test parsing when type is not a valid integer"""
        request_data = Mock()
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['role_id'],
            'param_name_cn[]': ['角色ID'],
            'param_type[]': ['invalid'],
            'param_description[]': ['']
        }[x]

        params = _parse_event_parameters(request_data)

        assert len(params) == 1
        assert params[0]['type'] == 1  # Should default to 1

    def test_parse_trims_whitespace_from_name_only(self):
        """Test that only parameter names are trimmed (not name_cn based on current implementation)"""
        request_data = Mock()
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['  role_id  '],
            'param_name_cn[]': ['  角色ID  '],
            'param_type[]': ['1'],
            'param_description[]': ['']
        }[x]

        params = _parse_event_parameters(request_data)

        # Only name is trimmed in current implementation
        assert params[0]['name'] == 'role_id'
        assert params[0]['name_cn'] == '  角色ID  '  # Not trimmed in current implementation


class TestBuildEventFromForm:
    """Test _build_event_from_form function"""

    @patch('backend.models.events.fetch_one_as_dict')
    def test_build_event_from_form_success(self, mock_fetch):
        """Test successful event building from form data"""
        # Mock game data
        mock_fetch.return_value = {
            'id': 1,
            'gid': 10000147,
            'name': 'Test Game',
            'ods_db': 'ieu_ods'
        }

        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': {
            'game_gid': '1',
            'event_name': 'login',
            'event_name_cn': '登录',
            'category_id': '1'
        }.get(x, d)
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['role_id'],
            'param_name_cn[]': ['角色ID'],
            'param_type[]': ['1'],
            'param_description[]': ['Role ID']
        }[x]

        event = _build_event_from_form(request_data)

        assert isinstance(event, EventData)
        assert event.game_gid == 10000147
        assert event.event_name == 'login'
        assert event.event_name_cn == '登录'
        assert event.category_id == 1
        assert len(event.parameters) == 1

    @patch('backend.models.events.fetch_one_as_dict')
    def test_build_event_missing_game_gid(self, mock_fetch):
        """Test error when game_gid is missing"""
        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': d

        with pytest.raises(ValueError) as exc_info:
            _build_event_from_form(request_data)

        assert "请选择游戏" in str(exc_info.value)

    @patch('backend.models.events.fetch_one_as_dict')
    def test_build_event_missing_event_name(self, mock_fetch):
        """Test error when event_name is missing"""
        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': {
            'game_gid': '1',
            'event_name': '',
            'event_name_cn': '登录',
            'category_id': '1'
        }.get(x, d)

        with pytest.raises(ValueError) as exc_info:
            _build_event_from_form(request_data)

        assert "请输入事件英文名" in str(exc_info.value)

    @patch('backend.models.events.fetch_one_as_dict')
    def test_build_event_missing_event_name_cn(self, mock_fetch):
        """Test error when event_name_cn is missing"""
        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': {
            'game_gid': '1',
            'event_name': 'login',
            'event_name_cn': '',
            'category_id': '1'
        }.get(x, d)

        with pytest.raises(ValueError) as exc_info:
            _build_event_from_form(request_data)

        assert "请输入事件中文名" in str(exc_info.value)

    @patch('backend.models.events.fetch_one_as_dict')
    def test_build_event_missing_category_id(self, mock_fetch):
        """Test error when category_id is missing"""
        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': {
            'game_gid': '1',
            'event_name': 'login',
            'event_name_cn': '登录',
            'category_id': ''
        }.get(x, d)

        with pytest.raises(ValueError) as exc_info:
            _build_event_from_form(request_data)

        assert "请选择事件分类" in str(exc_info.value)

    @patch('backend.models.events.fetch_one_as_dict')
    def test_build_event_game_not_found(self, mock_fetch):
        """Test error when game doesn't exist"""
        mock_fetch.return_value = None

        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': {
            'game_gid': '999',
            'event_name': 'login',
            'event_name_cn': '登录',
            'category_id': '1'
        }.get(x, d)
        request_data.getlist.return_value = ['role_id']

        with pytest.raises(ValueError) as exc_info:
            _build_event_from_form(request_data)

        assert "游戏不存在" in str(exc_info.value)

    @patch('backend.models.events.fetch_one_as_dict')
    def test_build_event_missing_parameters(self, mock_fetch):
        """Test error when no parameters are provided"""
        mock_fetch.return_value = {
            'id': 1,
            'gid': 10000147,
            'name': 'Test Game',
            'ods_db': 'ieu_ods'
        }

        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': {
            'game_gid': '1',
            'event_name': 'login',
            'event_name_cn': '登录',
            'category_id': '1'
        }.get(x, d)
        request_data.getlist.return_value = []

        with pytest.raises(ValueError) as exc_info:
            _build_event_from_form(request_data)

        assert "请至少添加一个参数" in str(exc_info.value)

    @patch('backend.models.events.fetch_one_as_dict')
    def test_build_event_with_include_in_common(self, mock_fetch):
        """Test building event with include_in_common_params flag"""
        mock_fetch.return_value = {
            'id': 1,
            'gid': 10000147,
            'name': 'Test Game',
            'ods_db': 'ieu_ods'
        }

        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': {
            'game_gid': '1',
            'event_name': 'login',
            'event_name_cn': '登录',
            'category_id': '1',
            'include_in_common_params': 'yes'
        }.get(x, d)
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['role_id'],
            'param_name_cn[]': ['角色ID'],
            'param_type[]': ['1'],
            'param_description[]': ['']
        }[x]

        event = _build_event_from_form(request_data)

        assert event.include_in_common_params == 1


class TestEventIntegration:
    """Integration tests for event building"""

    @patch('backend.models.events.fetch_one_as_dict')
    def test_full_event_building_workflow(self, mock_fetch):
        """Test complete workflow from form to EventData"""
        mock_fetch.return_value = {
            'id': 1,
            'gid': 10000147,
            'name': 'Test Game',
            'ods_db': 'ieu_ods'
        }

        request_data = Mock()
        request_data.get.side_effect = lambda x, d='': {
            'game_gid': '1',
            'event_name': 'user.login',
            'event_name_cn': '用户登录',
            'category_id': '2',
            'include_in_common_params': '1'
        }.get(x, d)
        request_data.getlist.side_effect = lambda x: {
            'param_name[]': ['role_id', 'account_id', 'zone_id'],
            'param_name_cn[]': ['角色ID', '账号ID', '分区ID'],
            'param_type[]': ['1', '1', '2'],
            'param_description[]': ['Role ID', 'Account ID', 'Zone ID']
        }[x]

        event = _build_event_from_form(request_data)

        # Verify all fields
        assert event.game_gid == 10000147
        assert event.event_name == 'user.login'
        assert event.event_name_cn == '用户登录'
        assert event.category_id == 2
        assert event.include_in_common_params == 1
        assert len(event.parameters) == 3

        # Verify table names
        assert event.source_table == 'ieu_ods.ods_10000147_all_view'
        assert event.target_table == 'ieu_cdm.v_dwd_10000147_user_login_di'

        # Verify parameters
        assert event.parameters[0]['name'] == 'role_id'
        assert event.parameters[1]['name'] == 'account_id'
        assert event.parameters[2]['name'] == 'zone_id'
        assert event.parameters[2]['type'] == 2
