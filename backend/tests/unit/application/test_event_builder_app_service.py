"""
Unit Tests for EventBuilderAppService

Tests for the EventBuilder application service including:
- Get fields by type (all/params/non-common/common/base)
- Batch add fields
- Base field constants
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from backend.application.services.parameter_app_service_enhanced_v2 import EventBuilderAppService


class TestBaseFieldsConstants:
    """Test BASE_FIELDS constant"""

    def test_base_fields_constant_exists(self):
        """Test BASE_FIELDS is defined correctly"""
        assert hasattr(EventBuilderAppService, 'BASE_FIELDS')
        assert isinstance(EventBuilderAppService.BASE_FIELDS, list)

    def test_base_fields_count(self):
        """Test BASE_FIELDS contains exactly 7 fields"""
        assert len(EventBuilderAppService.BASE_FIELDS) == 7

    def test_base_fields_content(self):
        """Test BASE_FIELDS contains required fields"""
        field_names = [f['name'] for f in EventBuilderAppService.BASE_FIELDS]

        required_fields = ['ds', 'role_id', 'account_id', 'utdid', 'envinfo', 'tm', 'ts']

        for field in required_fields:
            assert field in field_names, f"Missing required field: {field}"

    def test_base_fields_structure(self):
        """Test BASE_FIELDS have correct structure"""
        for field in EventBuilderAppService.BASE_FIELDS:
            assert 'name' in field
            assert 'type' in field
            assert field['category'] == 'base'


class TestGetFieldsByType:
    """Test get_fields_by_type use case"""

    def test_get_fields_by_type_all(self, mock_uow):
        """Test getting all fields (base + params)"""
        # Setup mock
        mock_params = [
            {
                'name': 'guild_id',
                'type': 'string',
                'category': 'param',
                'is_common': True
            },
            {
                'name': 'zone_id',
                'type': 'int',
                'category': 'param',
                'is_common': False
            }
        ]
        mock_uow.parameters.find_by_event_id.return_value = mock_params

        service = EventBuilderAppService(mock_uow)
        result = service.get_fields_by_type(event_id=1, field_type='all')

        # Should return base fields + params
        assert len(result) == 9  # 7 base + 2 params

        # Verify base fields present
        base_field_names = [f['name'] for f in result[:7]]
        assert 'ds' in base_field_names
        assert 'role_id' in base_field_names

        # Verify param fields present
        param_field_names = [f['name'] for f in result[7:]]
        assert 'guild_id' in param_field_names
        assert 'zone_id' in param_field_names

    def test_get_fields_by_type_params_only(self, mock_uow):
        """Test getting only param fields"""
        mock_params = [
            {
                'name': 'guild_id',
                'type': 'string',
                'category': 'param',
                'is_common': True
            }
        ]
        mock_uow.parameters.find_by_event_id.return_value = mock_params

        service = EventBuilderAppService(mock_uow)
        result = service.get_fields_by_type(event_id=1, field_type='params')

        # Should return only params
        assert len(result) == 1
        assert result[0]['name'] == 'guild_id'
        assert result[0]['category'] == 'param'

    def test_get_fields_by_type_common_only(self, mock_uow):
        """Test getting only common param fields"""
        mock_params = [
            {
                'name': 'guild_id',
                'type': 'string',
                'category': 'param',
                'is_common': True
            },
            {
                'name': 'zone_id',
                'type': 'int',
                'category': 'param',
                'is_common': False
            }
        ]
        mock_uow.parameters.find_by_event_id.return_value = mock_params

        service = EventBuilderAppService(mock_uow)
        result = service.get_fields_by_type(event_id=1, field_type='common')

        # Should return only common params
        assert len(result) == 1
        assert result[0]['name'] == 'guild_id'
        assert result[0]['is_common'] is True

    def test_get_fields_by_type_non_common_only(self, mock_uow):
        """Test getting only non-common param fields"""
        mock_params = [
            {
                'name': 'guild_id',
                'type': 'string',
                'category': 'param',
                'is_common': True
            },
            {
                'name': 'zone_id',
                'type': 'int',
                'category': 'param',
                'is_common': False
            }
        ]
        mock_uow.parameters.find_by_event_id.return_value = mock_params

        service = EventBuilderAppService(mock_uow)
        result = service.get_fields_by_type(event_id=1, field_type='non-common')

        # Should return only non-common params
        assert len(result) == 1
        assert result[0]['name'] == 'zone_id'
        assert result[0]['is_common'] is False

    def test_get_fields_by_type_base_only(self, mock_uow):
        """Test getting only base fields"""
        service = EventBuilderAppService(mock_uow)
        result = service.get_fields_by_type(event_id=1, field_type='base')

        # Should return only base fields
        assert len(result) == 7
        field_names = [f['name'] for f in result]

        assert 'ds' in field_names
        assert 'role_id' in field_names
        assert 'account_id' in field_names
        assert 'utdid' in field_names
        assert 'envinfo' in field_names
        assert 'tm' in field_names
        assert 'ts' in field_names

        # All should be base category
        for field in result:
            assert field['category'] == 'base'

    def test_get_fields_by_type_invalid_field_type(self, mock_uow):
        """Test invalid field_type raises error"""
        service = EventBuilderAppService(mock_uow)

        with pytest.raises(ValueError, match="Invalid field_type"):
            service.get_fields_by_type(event_id=1, field_type='invalid')

    def test_get_fields_by_type_empty_params(self, mock_uow):
        """Test with no param fields"""
        mock_uow.parameters.find_by_event_id.return_value = []

        service = EventBuilderAppService(mock_uow)
        result = service.get_fields_by_type(event_id=1, field_type='all')

        # Should return only base fields
        assert len(result) == 7
        field_names = [f['name'] for f in result]
        assert 'ds' in field_names

    def test_get_fields_by_type_calls_repository(self, mock_uow):
        """Test method calls correct repository method"""
        mock_uow.parameters.find_by_event_id.return_value = []

        service = EventBuilderAppService(mock_uow)
        service.get_fields_by_type(event_id=123, field_type='params')

        # Verify repository called
        mock_uow.parameters.find_by_event_id.assert_called_once_with(123)


class TestBatchAddFields:
    """Test batch_add_fields use case"""

    def test_batch_add_fields_all(self, mock_uow):
        """Test batch adding all fields"""
        # Setup mocks
        mock_config = {
            'id': 1,
            'event_id': 1,
            'base_fields': []
        }
        mock_uow.canvas_configs.find_by_event_id.return_value = mock_config
        mock_uow.canvas_configs.save.return_value = mock_config

        mock_params = [
            {'name': 'guild_id', 'type': 'string', 'category': 'param', 'is_common': True}
        ]
        mock_uow.parameters.find_by_event_id.return_value = mock_params

        service = EventBuilderAppService(mock_uow)
        result = service.batch_add_fields(event_id=1, field_type='all')

        # Verify save was called
        mock_uow.canvas_configs.save.assert_called_once()
        saved_config = mock_uow.canvas_configs.save.call_args[0][0]

        # Should have 7 base + params fields
        assert len(saved_config['base_fields']) == 8  # 7 base + 1 param

    def test_batch_add_fields_base_only(self, mock_uow):
        """Test batch adding only base fields"""
        mock_config = {'id': 1, 'event_id': 1, 'base_fields': []}
        mock_uow.canvas_configs.find_by_event_id.return_value = mock_config
        mock_uow.canvas_configs.save.return_value = mock_config

        service = EventBuilderAppService(mock_uow)
        result = service.batch_add_fields(event_id=1, field_type='base')

        # Verify save was called
        mock_uow.canvas_configs.save.assert_called_once()
        saved_config = mock_uow.canvas_configs.save.call_args[0][0]

        # Should have exactly 7 base fields
        assert len(saved_config['base_fields']) == 7

    def test_batch_add_fields_creates_config_if_not_exists(self, mock_uow):
        """Test batch add creates new config if not exists"""
        mock_uow.canvas_configs.find_by_event_id.return_value = None

        new_config = {'id': 1, 'event_id': 1, 'base_fields': []}
        mock_uow.canvas_configs.create.return_value = new_config
        mock_uow.canvas_configs.save.return_value = new_config

        service = EventBuilderAppService(mock_uow)
        result = service.batch_add_fields(event_id=1, field_type='base')

        # Verify create was called
        mock_uow.canvas_configs.create.assert_called_once()

    def test_batch_add_fields_invalid_field_type(self, mock_uow):
        """Test batch add with invalid field_type raises error"""
        service = EventBuilderAppService(mock_uow)

        with pytest.raises(ValueError, match="Invalid field_type"):
            service.batch_add_fields(event_id=1, field_type='invalid')

    def test_batch_add_fields_invalidates_cache(self, mock_uow):
        """Test batch add invalidates cache"""
        mock_config = {'id': 1, 'event_id': 1, 'base_fields': []}
        mock_uow.canvas_configs.find_by_event_id.return_value = mock_config
        mock_uow.canvas_configs.save.return_value = mock_config

        with patch('backend.application.services.parameter_app_service_enhanced_v2.CacheInvalidator') as mock_cache:
            service = EventBuilderAppService(mock_uow)
            service.batch_add_fields(event_id=1, field_type='base')

            # Verify cache invalidated
            mock_cache.invalidate_pattern.assert_called()


class TestErrorHandling:
    """Test error handling in EventBuilderAppService"""

    def test_get_fields_by_type_handles_exception(self, mock_uow):
        """Test get_fields_by_type handles exceptions"""
        mock_uow.parameters.find_by_event_id.side_effect = Exception("Database error")

        service = EventBuilderAppService(mock_uow)

        with pytest.raises(Exception, match="Database error"):
            service.get_fields_by_type(event_id=1, field_type='all')

    def test_batch_add_fields_handles_exception(self, mock_uow):
        """Test batch_add_fields handles exceptions"""
        mock_uow.canvas_configs.find_by_event_id.side_effect = Exception("Not found")

        service = EventBuilderAppService(mock_uow)

        with pytest.raises(Exception, match="Not found"):
            service.batch_add_fields(event_id=1, field_type='base')


class TestFieldMetadata:
    """Test field metadata structure"""

    def test_field_metadata_structure(self, mock_uow):
        """Test all fields have correct metadata structure"""
        mock_params = [
            {'name': 'guild_id', 'type': 'string', 'category': 'param', 'is_common': True}
        ]
        mock_uow.parameters.find_by_event_id.return_value = mock_params

        service = EventBuilderAppService(mock_uow)
        result = service.get_fields_by_type(event_id=1, field_type='all')

        for field in result:
            # Required fields
            assert 'name' in field
            assert 'type' in field
            assert 'category' in field

            # Valid values
            assert isinstance(field['name'], str)
            assert isinstance(field['type'], str)
            assert field['category'] in ['base', 'param']

    def test_base_field_types(self, mock_uow):
        """Test base fields have correct types"""
        service = EventBuilderAppService(mock_uow)
        result = service.get_fields_by_type(event_id=1, field_type='base')

        # Check type mappings
        field_types = {f['name']: f['type'] for f in result}

        assert field_types['ds'] == 'string'
        assert field_types['role_id'] == 'int'
        assert field_types['account_id'] == 'string'
        assert field_types['utdid'] == 'string'
        assert field_types['envinfo'] == 'string'
        assert field_types['tm'] == 'int'
        assert field_types['ts'] == 'int'
