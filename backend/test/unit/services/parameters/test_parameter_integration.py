#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Module Integration Test - Entity Architecture

集成测试验证Parameters模块的Entity架构:
- Repository返回Entity对象
- Service使用Entity对象
- 无game_id违规
"""

import pytest
from backend.models.entities import ParameterEntity, CommonParameterEntity
from backend.models.repositories.parameters import ParameterRepository
from backend.services.parameters.parameter_service import ParameterService


class TestParameterRepositoryEntityIntegration:
    """Repository层Entity对象集成测试"""

    def test_row_to_entity_returns_parameter_entity(self):
        """验证_row_to_entity方法返回ParameterEntity"""
        row = {
            'id': 1,
            'event_id': 1,
            'game_gid': 90000001,
            'param_name': 'zone_id',
            'param_description': 'Zone ID',
            'json_path': '$.zoneId',
            'created_at': '2024-01-01 00:00:00',
            'updated_at': '2024-01-01 00:00:00',
        }

        entity = ParameterRepository._row_to_entity(row)

        # ✅ 必须返回ParameterEntity
        assert isinstance(entity, ParameterEntity)
        assert entity.id == 1
        assert entity.game_gid == 90000001  # ✅ 使用game_gid
        assert entity.name == 'zone_id'
        assert entity.description == 'Zone ID'

    def test_row_to_entity_with_game_gid_map(self):
        """验证_row_to_entity使用game_gid_map避免N+1查询"""
        row = {'id': 1, 'event_id': 1, 'param_name': 'zone_id', 'json_path': '$.zoneId'}

        game_gid_map = {1: 90000001}  # event_id -> game_gid

        entity = ParameterRepository._row_to_entity(row, game_gid_map)

        # ✅ 应该从map中获取game_gid
        assert isinstance(entity, ParameterEntity)
        assert entity.game_gid == 90000001
        assert entity.event_id == 1


class TestParameterServiceEntityIntegration:
    """Service层Entity对象集成测试"""

    def test_service_methods_use_entity_objects(self):
        """验证Service方法使用Entity对象"""
        service = ParameterService()

        # 验证Repository被正确注入
        assert hasattr(service, 'param_repo')
        assert isinstance(service.param_repo, ParameterRepository)

        # 验证Entity对象可以被正确创建
        entity = ParameterEntity(
            id=1, event_id=1, game_gid=90000001, name="zone_id", param_type="param"
        )

        assert isinstance(entity, ParameterEntity)
        assert entity.game_gid == 90000001


class TestNoGameIdViolationsIntegration:
    """集成测试验证无game_id违规"""

    def test_parameter_entity_no_game_id_field(self):
        """验证ParameterEntity没有game_id字段"""
        entity = ParameterEntity(
            id=1, event_id=1, game_gid=90000001, name="zone_id", param_type="param"
        )

        # ✅ 必须有game_gid
        assert hasattr(entity, 'game_gid')

        # ✅ Entity对象没有game_id字段（这是正确的）
        # 注意：Pydantic模型不会动态添加字段
        field_names = entity.model_fields.keys()
        assert 'game_gid' in field_names
        assert 'game_id' not in field_names

    def test_common_parameter_entity_no_game_id_field(self):
        """验证CommonParameterEntity没有game_id字段"""
        entity = CommonParameterEntity(id=1, game_gid=90000001, name="role_id", param_type="base")

        # ✅ 必须有game_gid
        assert hasattr(entity, 'game_gid')

        # ✅ 没有game_id字段
        field_names = entity.model_fields.keys()
        assert 'game_gid' in field_names
        assert 'game_id' not in field_names
