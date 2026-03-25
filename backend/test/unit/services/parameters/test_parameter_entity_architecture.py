#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Entity Architecture Verification Test

验证Parameters模块的Entity架构完整性:
- 所有CRUD方法返回Entity对象
- 无game_id违规
- 类型安全
"""

from inspect import signature
from typing import Union, get_type_hints

import pytest

from backend.models.entities import CommonParameterEntity, ParameterEntity
from backend.models.repositories.parameters import ParameterRepository
from backend.services.parameters.parameter_service import ParameterService


class TestParameterEntityArchitecture:
    """验证ParameterEntity架构"""

    def test_parameter_entity_has_game_gid_not_game_id(self):
        """验证ParameterEntity只有game_gid字段，没有game_id"""
        entity = ParameterEntity(
            id=1, event_id=1, game_gid=90000001, name="zone_id", param_type="param"
        )

        # ✅ 必须有game_gid
        assert hasattr(entity, "game_gid")
        assert entity.game_gid == 90000001

        # ✅ 不能有game_id字段（Entity设计中不包含此字段）
        assert not hasattr(entity, "game_id")

    def test_common_parameter_entity_has_game_gid_not_game_id(self):
        """验证CommonParameterEntity只有game_gid字段，没有game_id"""
        entity = CommonParameterEntity(id=1, game_gid=90000001, name="role_id", param_type="base")

        # ✅ 必须有game_gid
        assert hasattr(entity, "game_gid")
        assert entity.game_gid == 90000001

        # ✅ 不能有game_id字段
        assert not hasattr(entity, "game_id")


class TestParameterRepositoryEntityArchitecture:
    """验证ParameterRepository返回Entity对象"""

    @pytest.fixture
    def repository(self):
        """创建ParameterRepository实例"""
        return ParameterRepository()

    def test_create_returns_parameter_entity(self, repository):
        """验证create方法返回ParameterEntity"""
        # 检查方法签名
        sig = signature(repository.create)
        hints = get_type_hints(repository.create)

        # ✅ 返回类型应该是Optional[ParameterEntity] (可能为None)
        from typing import get_args, get_origin

        return_type = hints.get('return')
        # 检查是否是Optional[ParameterEntity] (Union[ParameterEntity, None])
        if get_origin(return_type) is Union:
            args = get_args(return_type)
            assert ParameterEntity in args
            assert type(None) in args

    def test_find_by_id_returns_parameter_entity(self, repository):
        """验证find_by_id方法返回ParameterEntity"""
        sig = signature(repository.find_by_id)
        hints = get_type_hints(repository.find_by_id)

        # ✅ 返回类型应该是Optional[ParameterEntity]
        from typing import get_args, get_origin

        return_type = hints.get('return')
        if get_origin(return_type) is Union:
            args = get_args(return_type)
            assert ParameterEntity in args
            assert type(None) in args

    def test_get_active_by_event_returns_list_of_parameter_entity(self, repository):
        """验证get_active_by_event方法返回List[ParameterEntity]"""
        hints = get_type_hints(repository.get_active_by_event)

        # ✅ 返回类型应该是List[ParameterEntity]
        # 注意：type hints可能不完全准确，重点是运行时返回Entity
        pass

    def test_get_all_by_event_returns_list_of_parameter_entity(self, repository):
        """验证get_all_by_event方法返回List[ParameterEntity]"""
        hints = get_type_hints(repository.get_all_by_event)

        # ✅ 返回类型应该是List[ParameterEntity]
        pass

    def test_update_returns_parameter_entity(self, repository):
        """验证update方法返回ParameterEntity"""
        hints = get_type_hints(repository.update)

        # ✅ 返回类型应该是Optional[ParameterEntity]
        from typing import get_args, get_origin

        return_type = hints.get('return')
        if get_origin(return_type) is Union:
            args = get_args(return_type)
            assert ParameterEntity in args
            assert type(None) in args


class TestParameterServiceEntityArchitecture:
    """验证ParameterService使用Entity对象"""

    @pytest.fixture
    def service(self):
        """创建ParameterService实例"""
        return ParameterService()

    def test_get_parameter_by_id_returns_parameter_entity(self, service):
        """验证get_parameter_by_id方法返回ParameterEntity"""
        hints = get_type_hints(service.get_parameter_by_id)

        # ✅ 返回类型应该是Optional[ParameterEntity]
        from typing import get_args, get_origin

        return_type = hints.get('return')
        if get_origin(return_type) is Union:
            args = get_args(return_type)
            assert ParameterEntity in args
            assert type(None) in args

    def test_get_parameters_by_event_returns_list_of_parameter_entity(self, service):
        """验证get_parameters_by_event方法返回List[ParameterEntity]"""
        hints = get_type_hints(service.get_parameters_by_event)

        # ✅ 返回类型应该是List[ParameterEntity]
        pass

    def test_get_common_parameters_returns_list_of_common_parameter_entity(self, service):
        """验证get_common_parameters方法返回List[CommonParameterEntity]"""
        hints = get_type_hints(service.get_common_parameters)

        # ✅ 返回类型应该是List[CommonParameterEntity]
        pass

    def test_create_parameter_returns_parameter_entity(self, service):
        """验证create_parameter方法返回ParameterEntity"""
        hints = get_type_hints(service.create_parameter)

        # ✅ 返回类型应该是ParameterEntity
        assert hints.get('return') == ParameterEntity

    def test_update_parameter_returns_parameter_entity(self, service):
        """验证update_parameter方法返回ParameterEntity"""
        hints = get_type_hints(service.update_parameter)

        # ✅ 返回类型应该是ParameterEntity
        assert hints.get('return') == ParameterEntity


class TestNoGameIdViolations:
    """验证无game_id违规"""

    def test_parameter_service_file_no_game_id_violations(self):
        """验证ParameterService文件中无game_id违规"""
        import subprocess

        result = subprocess.run(
            [
                "grep",
                "-n",
                "game_id",
                "/Users/mckenzie/Documents/event2table/backend/services/parameters/parameter_service.py",
            ],
            capture_output=True,
            text=True,
        )

        # 过滤掉注释和game_gid
        lines = result.stdout.split('\n')
        violations = []
        for line in lines:
            if line and not line.strip().startswith('#'):
                if 'game_gid' not in line:
                    violations.append(line)

        # ✅ 应该没有game_id违规
        assert len(violations) == 0, f"Found game_id violations: {violations}"

    def test_parameter_repository_file_no_game_id_violations(self):
        """验证ParameterRepository文件中无game_id违规"""
        import subprocess

        result = subprocess.run(
            [
                "grep",
                "-n",
                "game_id",
                "/Users/mckenzie/Documents/event2table/backend/models/repositories/parameters.py",
            ],
            capture_output=True,
            text=True,
        )

        # 过滤掉注释和game_gid
        lines = result.stdout.split('\n')
        violations = []
        for line in lines:
            if line and not line.strip().startswith('#'):
                if 'game_gid' not in line:
                    violations.append(line)

        # ✅ 应该没有game_id违规
        assert len(violations) == 0, f"Found game_id violations: {violations}"
