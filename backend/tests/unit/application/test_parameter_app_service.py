"""
Unit Tests for ParameterAppServiceEnhanced

Tests for the application service including:
- Get filtered parameters (all/common/non-common)
- Change parameter type
- Auto-sync common parameters
- Get parameter usage stats
- Detect parameter changes
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from backend.application.services.parameter_app_service_enhanced_v2 import (
    ParameterAppServiceEnhanced
)
from backend.application.dtos.parameter_dto import (
    ParameterFilterDTO,
    ParameterTypeChangeDTO,
    CommonParameterSyncDTO
)
from backend.domain.models.parameter import Parameter, ParameterType
from backend.domain.models.common_parameter import CommonParameter


class TestGetFilteredParameters:
    """Test get_filtered_parameters use case"""

    def test_get_filtered_parameters_all(self, mock_uow):
        """Test getting all parameters"""
        # Setup mock
        mock_params = [
            Parameter(
                id=1,
                param_name='guild_id',
                param_type='string',
                event_id=1,
                game_gid=90000001,
                is_common=True
            ),
            Parameter(
                id=2,
                param_name='role_id',
                param_type='int',
                event_id=1,
                game_gid=90000001,
                is_common=False
            )
        ]
        mock_uow.parameters.find_by_game.return_value = mock_params

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterFilterDTO(game_gid=90000001, mode='all')

        result = service.get_filtered_parameters(dto)

        assert len(result) == 2
        assert result[0]['param_name'] == 'guild_id'
        assert result[1]['param_name'] == 'role_id'
        mock_uow.parameters.find_by_game.assert_called_once_with(90000001)

    def test_get_filtered_parameters_common_only(self, mock_uow):
        """Test getting only common parameters"""
        mock_params = [
            Parameter(
                id=1,
                param_name='guild_id',
                param_type='string',
                event_id=1,
                game_gid=90000001,
                is_common=True
            )
        ]
        mock_uow.parameters.find_common_by_game.return_value = mock_params

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterFilterDTO(game_gid=90000001, mode='common')

        result = service.get_filtered_parameters(dto)

        assert len(result) == 1
        assert result[0]['param_name'] == 'guild_id'
        assert result[0]['is_common'] is True
        mock_uow.parameters.find_common_by_game.assert_called_once_with(90000001)

    def test_get_filtered_parameters_non_common_only(self, mock_uow):
        """Test getting only non-common parameters"""
        mock_params = [
            Parameter(
                id=2,
                param_name='role_id',
                param_type='int',
                event_id=1,
                game_gid=90000001,
                is_common=False
            )
        ]
        mock_uow.parameters.find_non_common_by_game.return_value = mock_params

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterFilterDTO(game_gid=90000001, mode='non-common')

        result = service.get_filtered_parameters(dto)

        assert len(result) == 1
        assert result[0]['param_name'] == 'role_id'
        assert result[0]['is_common'] is False
        mock_uow.parameters.find_non_common_by_game.assert_called_once_with(90000001)

    def test_get_filtered_parameters_with_event_filter(self, mock_uow):
        """Test filtering by event_id"""
        mock_params = [
            Parameter(
                id=1,
                param_name='guild_id',
                param_type='string',
                event_id=1,
                game_gid=90000001,
                is_common=True
            ),
            Parameter(
                id=2,
                param_name='zone_id',
                param_type='int',
                event_id=2,
                game_gid=90000001,
                is_common=True
            )
        ]
        mock_uow.parameters.find_by_game.return_value = mock_params

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterFilterDTO(game_gid=90000001, mode='all', event_id=1)

        result = service.get_filtered_parameters(dto)

        # Only event_id=1 parameter returned
        assert len(result) == 1
        assert result[0]['param_name'] == 'guild_id'
        assert result[0]['event_id'] == 1

    def test_get_filtered_parameters_invalid_mode(self, mock_uow):
        """Test invalid mode raises error"""
        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterFilterDTO(game_gid=90000001, mode='invalid')

        with pytest.raises(ValueError, match="Invalid filter mode"):
            service.get_filtered_parameters(dto)

    def test_get_filtered_parameters_enriches_usage_stats(self, mock_uow):
        """Test parameters are enriched with usage statistics"""
        mock_param = Parameter(
            id=1,
            param_name='guild_id',
            param_type='string',
            event_id=1,
            game_gid=90000001,
            is_common=True
        )
        mock_uow.parameters.find_by_game.return_value = [mock_param]

        service = ParameterAppServiceEnhanced(mock_uow)

        # Mock helper methods
        service._get_usage_count = Mock(return_value=5)
        service._get_event_count = Mock(return_value=2)

        dto = ParameterFilterDTO(game_gid=90000001, mode='all')
        result = service.get_filtered_parameters(dto)

        assert 'usage_count' in result[0]
        assert 'events_count' in result[0]
        assert result[0]['usage_count'] == 5
        assert result[0]['events_count'] == 2


class TestChangeParameterType:
    """Test change_parameter_type use case"""

    def test_change_parameter_type_valid(self, mock_uow):
        """Test valid parameter type change"""
        # Setup mock
        original_param = Parameter(
            id=1,
            param_name='test_param',
            param_type='string',
            event_id=1,
            game_gid=90000001,
            is_active=True
        )

        updated_param = Parameter(
            id=1,
            param_name='test_param',
            param_type='int',
            json_path='$.',
            event_id=1,
            game_gid=90000001,
            is_active=True,
            version=2
        )

        mock_uow.parameters.find_by_id.return_value = original_param
        mock_uow.parameters.save.return_value = updated_param

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterTypeChangeDTO(parameter_id=1, new_type='int')

        result = service.change_parameter_type(dto)

        assert result['param_type'] == 'int'
        assert result['version'] == 2
        mock_uow.parameters.save.assert_called_once()
        mock_uow.register_event.assert_called_once()

    def test_change_parameter_type_not_found(self, mock_uow):
        """Test changing non-existent parameter raises error"""
        mock_uow.parameters.find_by_id.return_value = None

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterTypeChangeDTO(parameter_id=999, new_type='int')

        with pytest.raises(ValueError, match="Parameter not found"):
            service.change_parameter_type(dto)

    def test_change_parameter_type_invalid_change(self, mock_uow):
        """Test invalid type change raises error"""
        param = Parameter(
            id=1,
            param_name='test',
            param_type='array',  # Complex type
            is_active=True
        )
        mock_uow.parameters.find_by_id.return_value = param

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterTypeChangeDTO(parameter_id=1, new_type='string')

        with pytest.raises(ValueError, match="Type change validation failed"):
            service.change_parameter_type(dto)

    def test_change_parameter_type_inactive_parameter(self, mock_uow):
        """Test changing inactive parameter type raises error"""
        param = Parameter(
            id=1,
            param_name='test',
            param_type='string',
            is_active=False  # Inactive
        )
        mock_uow.parameters.find_by_id.return_value = param

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterTypeChangeDTO(parameter_id=1, new_type='int')

        with pytest.raises(ValueError, match="Type change validation failed"):
            service.change_parameter_type(dto)


class TestAutoSyncCommonParameters:
    """Test auto_sync_common_parameters use case"""

    def test_auto_sync_with_force_recalculate(self, mock_uow):
        """Test forced recalculation of common parameters"""
        # Setup mock
        mock_uow.parameters.count_events_by_game.return_value = 5
        mock_uow.parameters.get_parameter_usage_stats.return_value = [
            {
                'param_name': 'guild_id',
                'param_name_cn': '公会ID',
                'param_type': 'string',
                'event_count': 4,  # 80%
                'usage_count': 8,
                'is_active': True,
                'id': 1
            }
        ]
        mock_uow.common_params.delete_by_game.return_value = 0

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = CommonParameterSyncDTO(game_gid=90000001, force_recalculate=True)

        service.auto_sync_common_parameters(dto)

        # Verify calculation was performed
        mock_uow.parameters.count_events_by_game.assert_called_once_with(90000001)
        mock_uow.common_params.delete_by_game.assert_called_once_with(90000001)
        mock_uow.register_event.assert_called_once()

    def test_auto_sync_with_parameter_changes(self, mock_uow):
        """Test sync when parameters changed"""
        from backend.core.cache import cache

        # Setup cache
        cache_key = f'params_count:90000001'
        cache.set(cache_key, 10, timeout=3600)

        mock_uow.parameters.count_by_game.return_value = 15  # Changed
        mock_uow.parameters.count_events_by_game.return_value = 5
        mock_uow.parameters.get_parameter_usage_stats.return_value = []

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = CommonParameterSyncDTO(game_gid=90000001, force_recalculate=False)

        service.auto_sync_common_parameters(dto)

        # Should detect changes and recalculate
        mock_uow.parameters.count_events_by_game.assert_called_once()

    def test_auto_sync_no_changes(self, mock_uow):
        """Test sync skipped when no changes"""
        from backend.core.cache import cache

        # Setup cache
        cache_key = f'params_count:90000001'
        cache.set(cache_key, 10, timeout=3600)

        mock_uow.parameters.count_by_game.return_value = 10  # No change

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = CommonParameterSyncDTO(game_gid=90000001, force_recalculate=False)

        service.auto_sync_common_parameters(dto)

        # Should skip calculation
        mock_uow.parameters.count_events_by_game.assert_not_called()

    def test_auto_sync_updates_common_params_table(self, mock_uow):
        """Test sync updates common_params table"""
        mock_uow.parameters.count_events_by_game.return_value = 5
        mock_uow.parameters.get_parameter_usage_stats.return_value = [
            {
                'param_name': 'guild_id',
                'param_name_cn': '公会ID',
                'param_type': 'string',
                'event_count': 4,
                'usage_count': 8,
                'is_active': True,
                'id': 1
            }
        ]
        mock_uow.common_params.delete_by_game.return_value = 0

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = CommonParameterSyncDTO(game_gid=90000001, force_recalculate=True)

        service.auto_sync_common_parameters(dto)

        # Verify delete and save
        mock_uow.common_params.delete_by_game.assert_called_once_with(90000001)
        assert mock_uow.common_params.save.call_count == 1

        # Verify saved parameter is CommonParameter
        saved_param = mock_uow.common_params.save.call_args[0][0]
        assert isinstance(saved_param, CommonParameter)
        assert saved_param.param_name == 'guild_id'

    def test_auto_sync_publishes_domain_event(self, mock_uow):
        """Test sync publishes domain event"""
        mock_uow.parameters.count_events_by_game.return_value = 5
        mock_uow.parameters.get_parameter_usage_stats.return_value = [
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
        mock_uow.common_params.delete_by_game.return_value = 0

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = CommonParameterSyncDTO(game_gid=90000001, force_recalculate=True)

        service.auto_sync_common_parameters(dto)

        # Verify domain event published
        assert mock_uow.register_event.call_count == 1
        event = mock_uow.register_event.call_args[0][0]
        assert event.game_gid == 90000001
        assert event.common_params_count == 2


class TestGetParameterUsageStats:
    """Test get_parameter_usage_stats use case"""

    def test_get_parameter_usage_stats(self, mock_uow):
        """Test getting parameter usage statistics"""
        mock_uow.parameters.get_parameter_usage_stats.return_value = [
            {
                'param_name': 'guild_id',
                'param_name_cn': '公会ID',
                'param_type': 'string',
                'event_count': 4,
                'usage_count': 8,
                'is_active': True,
                'id': 1
            }
        ]

        service = ParameterAppServiceEnhanced(mock_uow)
        result = service.get_parameter_usage_stats(90000001)

        assert len(result) == 1
        assert result[0]['param_name'] == 'guild_id'
        assert result[0]['event_count'] == 4
        assert result[0]['usage_count'] == 8


class TestDetectParameterChanges:
    """Test detect_parameter_changes use case"""

    def test_detect_parameter_changes_with_changes(self, mock_uow):
        """Test detecting parameter changes"""
        from backend.core.cache import cache

        # Setup cache
        cache_key = f'params_count:90000001'
        cache.set(cache_key, 10, timeout=3600)

        mock_uow.parameters.count_by_game.return_value = 15  # Changed

        service = ParameterAppServiceEnhanced(mock_uow)
        result = service.detect_parameter_changes(90000001)

        assert result is not None
        assert result['game_gid'] == 90000001
        assert result['previous_count'] == 10
        assert result['current_count'] == 15
        assert result['change_type'] == 'increased'

    def test_detect_parameter_changes_no_changes(self, mock_uow):
        """Test detecting no changes returns None"""
        from backend.core.cache import cache

        # Setup cache
        cache_key = f'params_count:90000001'
        cache.set(cache_key, 10, timeout=3600)

        mock_uow.parameters.count_by_game.return_value = 10  # No change

        service = ParameterAppServiceEnhanced(mock_uow)
        result = service.detect_parameter_changes(90000001)

        assert result is None


class TestErrorHandling:
    """Test error handling in application service"""

    def test_get_filtered_parameters_handles_exception(self, mock_uow):
        """Test get_filtered_parameters handles exceptions"""
        mock_uow.parameters.find_by_game.side_effect = Exception("Database error")

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterFilterDTO(game_gid=90000001, mode='all')

        with pytest.raises(Exception, match="Database error"):
            service.get_filtered_parameters(dto)

    def test_change_parameter_type_handles_exception(self, mock_uow):
        """Test change_parameter_type handles exceptions"""
        mock_uow.parameters.find_by_id.side_effect = Exception("Not found")

        service = ParameterAppServiceEnhanced(mock_uow)
        dto = ParameterTypeChangeDTO(parameter_id=1, new_type='int')

        with pytest.raises(Exception, match="Not found"):
            service.change_parameter_type(dto)
