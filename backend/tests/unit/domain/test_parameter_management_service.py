"""
Unit Tests for ParameterManagementService

Tests for the domain service including:
- Common parameter calculation
- Parameter type change validation
- Parameter change detection
- Parameter usage statistics
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from backend.domain.services.parameter_management_service import (
    ParameterManagementService,
    ParameterUsageStats
)
from backend.domain.models.parameter import Parameter, ParameterType, ValidationResult
from backend.domain.models.common_parameter import CommonParameter


class TestParameterManagementServiceCreation:
    """Test service initialization"""

    def test_service_creation(self, mock_parameter_repository, mock_common_param_repository):
        """Test service creation with repositories"""
        service = ParameterManagementService(
            mock_parameter_repository,
            mock_common_param_repository
        )

        assert service.parameter_repo == mock_parameter_repository
        assert service.common_param_repo == mock_common_param_repository


class TestCalculateCommonParameters:
    """Test common parameter calculation"""

    def test_calculate_common_parameters_80_percent_threshold(self):
        """Test calculation with 80% threshold"""
        # Setup mock
        param_repo = Mock()
        common_param_repo = Mock()

        param_repo.count_events_by_game.return_value = 5
        param_repo.get_parameter_usage_stats.return_value = [
            {
                'param_name': 'zone_id',
                'param_name_cn': None,
                'param_type': 'int',
                'event_count': 5,  # 5/5 = 100% >= 80%
                'usage_count': 10,
                'is_active': True,
                'id': 1
            },
            {
                'param_name': 'guild_id',
                'param_name_cn': '公会ID',
                'param_type': 'string',
                'event_count': 4,  # 4/5 = 80% >= 80%
                'usage_count': 8,
                'is_active': True,
                'id': 2
            },
            {
                'param_name': 'role_id',
                'param_name_cn': None,
                'param_type': 'int',
                'event_count': 3,  # 3/5 = 60% < 80%
                'usage_count': 6,
                'is_active': True,
                'id': 3
            }
        ]

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.calculate_common_parameters(90000001, threshold=0.8)

        # Verify result
        assert result.game_gid == 90000001
        assert result.total_events == 5
        assert result.total_parameters == 3
        assert result.threshold_used == 0.8
        assert len(result.common_parameters) == 2  # zone_id, guild_id

        # Verify common parameters
        common_param_names = [cp.param_name for cp in result.common_parameters]
        assert 'zone_id' in common_param_names
        assert 'guild_id' in common_param_names
        assert 'role_id' not in common_param_names

    def test_calculate_common_parameters_minimum_2_events(self):
        """Test calculation enforces minimum 2 events rule"""
        param_repo = Mock()
        common_param_repo = Mock()

        param_repo.count_events_by_game.return_value = 10
        param_repo.get_parameter_usage_stats.return_value = [
            {
                'param_name': 'single_use_param',
                'param_name_cn': None,
                'param_type': 'string',
                'event_count': 1,  # Only 1 event - should not qualify
                'usage_count': 1,
                'is_active': True,
                'id': 1
            },
            {
                'param_name': 'double_use_param',
                'param_name_cn': None,
                'param_type': 'int',
                'event_count': 2,  # 2 events - should qualify if >= 80%
                'usage_count': 4,
                'is_active': True,
                'id': 2
            }
        ]

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.calculate_common_parameters(90000001, threshold=0.8)

        # Only double_use_param qualifies
        assert len(result.common_parameters) == 1
        assert result.common_parameters[0].param_name == 'double_use_param'

    def test_calculate_common_parameters_no_events(self):
        """Test calculation with zero events"""
        param_repo = Mock()
        common_param_repo = Mock()

        param_repo.count_events_by_game.return_value = 0
        param_repo.get_parameter_usage_stats.return_value = []

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.calculate_common_parameters(90000001)

        assert result.total_events == 0
        assert result.total_parameters == 0
        assert len(result.common_parameters) == 0

    def test_calculate_common_parameters_invalid_type_skipped(self):
        """Test calculation skips invalid parameter types"""
        param_repo = Mock()
        common_param_repo = Mock()

        param_repo.count_events_by_game.return_value = 5
        param_repo.get_parameter_usage_stats.return_value = [
            {
                'param_name': 'valid_param',
                'param_name_cn': None,
                'param_type': 'string',
                'event_count': 5,
                'usage_count': 10,
                'is_active': True,
                'id': 1
            },
            {
                'param_name': 'invalid_param',
                'param_name_cn': None,
                'param_type': 'invalid_type',  # Invalid type
                'event_count': 5,
                'usage_count': 10,
                'is_active': True,
                'id': 2
            }
        ]

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.calculate_common_parameters(90000001)

        # Only valid_param included
        assert len(result.common_parameters) == 1
        assert result.common_parameters[0].param_name == 'valid_param'

    def test_calculate_common_parameters_custom_threshold(self):
        """Test calculation with custom threshold"""
        param_repo = Mock()
        common_param_repo = Mock()

        param_repo.count_events_by_game.return_value = 10
        param_repo.get_parameter_usage_stats.return_value = [
            {
                'param_name': 'param_70_percent',
                'param_name_cn': None,
                'param_type': 'string',
                'event_count': 7,  # 7/10 = 70% >= 70%
                'usage_count': 14,
                'is_active': True,
                'id': 1
            },
            {
                'param_name': 'param_60_percent',
                'param_name_cn': None,
                'param_type': 'int',
                'event_count': 6,  # 6/10 = 60% < 70%
                'usage_count': 12,
                'is_active': True,
                'id': 2
            }
        ]

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.calculate_common_parameters(90000001, threshold=0.7)

        # Only param_70_percent qualifies
        assert len(result.common_parameters) == 1
        assert result.common_parameters[0].param_name == 'param_70_percent'


class TestValidateParameterTypeChange:
    """Test parameter type change validation"""

    def test_validate_type_change_valid_simple_to_simple(self):
        """Test validation of valid simple to simple type change"""
        param_repo = Mock()
        common_param_repo = Mock()

        param = Parameter(
            id=1,
            param_name='test',
            param_type='string',
            is_active=True
        )

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.validate_parameter_type_change(
            param,
            ParameterType.INT
        )

        assert result.is_valid is True
        assert result.errors == []

    def test_validate_type_change_invalid_complex_to_simple(self):
        """Test validation fails for complex to simple type change"""
        param_repo = Mock()
        common_param_repo = Mock()

        param = Parameter(
            id=1,
            param_name='test',
            param_type='array',
            is_active=True
        )

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.validate_parameter_type_change(
            param,
            ParameterType.STRING
        )

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert '类型' in result.errors[0] and '不能转换为' in result.errors[0]

    def test_validate_type_change_inactive_parameter(self):
        """Test validation fails for inactive parameter"""
        param_repo = Mock()
        common_param_repo = Mock()

        param = Parameter(
            id=1,
            param_name='test',
            param_type='string',
            is_active=False  # Inactive
        )

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.validate_parameter_type_change(
            param,
            ParameterType.INT
        )

        assert result.is_valid is False
        assert '参数未激活' in result.errors

    def test_validate_type_change_multiple_errors(self):
        """Test validation accumulates multiple errors"""
        param_repo = Mock()
        common_param_repo = Mock()

        param = Parameter(
            id=1,
            param_name='test',
            param_type='array',  # Complex type
            is_active=False  # Inactive
        )

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.validate_parameter_type_change(
            param,
            ParameterType.STRING
        )

        assert result.is_valid is False
        assert len(result.errors) == 2  # Both type and active errors


class TestDetectParameterChanges:
    """Test parameter count change detection"""

    def test_detect_parameter_changes_first_time(self):
        """Test first-time detection initializes cache"""
        from backend.core.cache import cache

        param_repo = Mock()
        common_param_repo = Mock()

        param_repo.count_by_game.return_value = 10

        # Clear cache
        cache_key = f'params_count:90000001'
        cache.delete(cache_key)

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.detect_parameter_changes(90000001)

        # First time - no event
        assert result is None

        # Cache initialized
        cached_count = cache.get(cache_key)
        assert cached_count == 10

    def test_detect_parameter_changes_increased(self):
        """Test detection of increased parameter count"""
        from backend.core.cache import cache

        param_repo = Mock()
        common_param_repo = Mock()

        cache_key = f'params_count:90000001'

        # Set initial cache
        cache.set(cache_key, 10, timeout=3600)

        # Current count is higher
        param_repo.count_by_game.return_value = 15

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.detect_parameter_changes(90000001)

        assert result is not None
        assert result.game_gid == 90000001
        assert result.previous_count == 10
        assert result.current_count == 15
        assert result.change_type == 'increased'

    def test_detect_parameter_changes_decreased(self):
        """Test detection of decreased parameter count"""
        from backend.core.cache import cache

        param_repo = Mock()
        common_param_repo = Mock()

        cache_key = f'params_count:90000001'

        # Set initial cache
        cache.set(cache_key, 15, timeout=3600)

        # Current count is lower
        param_repo.count_by_game.return_value = 10

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.detect_parameter_changes(90000001)

        assert result is not None
        assert result.previous_count == 15
        assert result.current_count == 10
        assert result.change_type == 'decreased'

    def test_detect_parameter_changes_no_change(self):
        """Test no change detected"""
        from backend.core.cache import cache

        param_repo = Mock()
        common_param_repo = Mock()

        cache_key = f'params_count:90000001'

        # Set initial cache
        cache.set(cache_key, 10, timeout=3600)

        # Current count is same
        param_repo.count_by_game.return_value = 10

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.detect_parameter_changes(90000001)

        # No change
        assert result is None


class TestGetParameterUsageStats:
    """Test parameter usage statistics retrieval"""

    def test_get_parameter_usage_stats(self):
        """Test getting parameter usage statistics"""
        param_repo = Mock()
        common_param_repo = Mock()

        param_repo.get_parameter_usage_stats.return_value = [
            {
                'param_name': 'guild_id',
                'param_name_cn': '公会ID',
                'param_type': 'string',
                'event_count': 4,
                'usage_count': 8,
                'is_active': True,
                'id': 1
            },
            {
                'param_name': 'zone_id',
                'param_name_cn': None,
                'param_type': 'int',
                'event_count': 5,
                'usage_count': 10,
                'is_active': True,
                'id': 2
            }
        ]

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.get_parameter_usage_stats(90000001)

        assert len(result) == 2
        assert isinstance(result[0], ParameterUsageStats)
        assert result[0].param_name == 'guild_id'
        assert result[0].param_id == 1
        assert result[0].param_name_cn == '公会ID'
        assert result[0].param_type == 'string'
        assert result[0].event_count == 4
        assert result[0].usage_count == 8
        assert result[0].is_active is True


class TestShouldRecalculateCommonParams:
    """Test common parameter recalculation decision logic"""

    def test_should_recalculate_force_true(self):
        """Test force recalculate returns True"""
        param_repo = Mock()
        common_param_repo = Mock()

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.should_recalculate_common_params(90000001, force=True)

        assert result is True

    def test_should_recalculate_with_changes(self):
        """Test recalculation when changes detected"""
        param_repo = Mock()
        common_param_repo = Mock()

        from backend.core.cache import cache
        cache_key = f'params_count:90000001'
        cache.set(cache_key, 10, timeout=3600)

        param_repo.count_by_game.return_value = 15  # Changed

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.should_recalculate_common_params(90000001, force=False)

        assert result is True

    def test_should_recalculate_no_changes(self):
        """Test no recalculation when no changes"""
        param_repo = Mock()
        common_param_repo = Mock()

        from backend.core.cache import cache
        cache_key = f'params_count:90000001'
        cache.set(cache_key, 10, timeout=3600)

        param_repo.count_by_game.return_value = 10  # No change

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.should_recalculate_common_params(90000001, force=False)

        assert result is False


class TestValidateParameterName:
    """Test parameter name validation"""

    def test_validate_parameter_name_valid(self):
        """Test validation of valid parameter names"""
        param_repo = Mock()
        common_param_repo = Mock()

        service = ParameterManagementService(param_repo, common_param_repo)

        # Valid names
        valid_names = [
            'guild_id',
            'zoneId',
            '_private_param',
            'param123',
            'a',
            '_',
            'Param_Name_123'
        ]

        for name in valid_names:
            result = service.validate_parameter_name(name)
            assert result.is_valid is True, f"Failed for: {name}"
            assert result.errors == []

    def test_validate_parameter_name_empty(self):
        """Test validation fails for empty name"""
        param_repo = Mock()
        common_param_repo = Mock()

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.validate_parameter_name('')

        assert result.is_valid is False
        assert '参数名称不能为空' in result.errors

    def test_validate_parameter_name_invalid_start(self):
        """Test validation fails for name starting with number"""
        param_repo = Mock()
        common_param_repo = Mock()

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.validate_parameter_name('123param')

        assert result.is_valid is False
        assert '必须以字母或下划线开头' in result.errors

    def test_validate_parameter_name_invalid_characters(self):
        """Test validation fails for invalid characters"""
        param_repo = Mock()
        common_param_repo = Mock()

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.validate_parameter_name('param-name')

        assert result.is_valid is False
        assert '只能包含字母、数字和下划线' in result.errors

    def test_validate_parameter_name_multiple_errors(self):
        """Test validation accumulates errors"""
        param_repo = Mock()
        common_param_repo = Mock()

        service = ParameterManagementService(param_repo, common_param_repo)
        result = service.validate_parameter_name('123-param')

        assert result.is_valid is False
        assert len(result.errors) == 2  # Start + character errors
