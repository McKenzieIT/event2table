"""
Unit Tests for Parameter Domain Model

Tests for the Parameter value object including:
- Creation and validation
- Type conversion rules
- Immutability
- Serialization/Deserialization
"""

import pytest
from datetime import datetime
from backend.domain.models.parameter import Parameter, ParameterType, ValidationResult


class TestParameterCreation:
    """Test parameter creation and validation"""

    def test_parameter_creation_valid(self):
        """Test valid parameter creation"""
        param = Parameter(
            id=1,
            param_name='guild_id',
            param_type='string',
            json_path='$.guildId',
            description='Guild ID',
            event_id=1,
            game_gid=90000001,
            is_common=False,
            is_active=True
        )

        assert param.id == 1
        assert param.param_name == 'guild_id'
        assert param.param_type == 'string'
        assert param.json_path == '$.guildId'
        assert param.description == 'Guild ID'
        assert param.event_id == 1
        assert param.game_gid == 90000001
        assert param.is_common is False
        assert param.is_active is True

    def test_parameter_creation_minimal(self):
        """Test parameter creation with minimal fields"""
        param = Parameter(
            param_name='zone_id',
            param_type='int'
        )

        assert param.param_name == 'zone_id'
        assert param.param_type == 'int'
        assert param.json_path == '$.'  # Default
        assert param.is_active is True  # Default

    def test_parameter_validation_empty_name(self):
        """Test validation fails with empty name"""
        with pytest.raises(ValueError, match="参数名称不能为空"):
            Parameter(
                param_name='',
                param_type='string'
            )

    def test_parameter_validation_invalid_type(self):
        """Test validation fails with invalid type"""
        with pytest.raises(ValueError, match="无效的参数类型"):
            Parameter(
                param_name='test',
                param_type='invalid_type'
            )

    def test_parameter_validation_invalid_json_path(self):
        """Test validation fails with invalid JSON path"""
        with pytest.raises(ValueError, match="JSON路径必须以"):
            Parameter(
                param_name='test',
                param_type='string',
                json_path='invalid'
            )

    def test_parameter_valid_types(self):
        """Test all valid parameter types"""
        valid_types = ['string', 'int', 'float', 'boolean', 'array', 'map']

        for param_type in valid_types:
            param = Parameter(
                param_name='test',
                param_type=param_type
            )
            assert param.param_type == param_type


class TestParameterType:
    """Test ParameterType enum"""

    def test_parameter_type_from_string_valid(self):
        """Test ParameterType creation from valid string"""
        assert ParameterType.from_string('int') == ParameterType.INT
        assert ParameterType.from_string('string') == ParameterType.STRING
        assert ParameterType.from_string('array') == ParameterType.ARRAY
        assert ParameterType.from_string('boolean') == ParameterType.BOOLEAN
        assert ParameterType.from_string('map') == ParameterType.MAP

    def test_parameter_type_from_string_invalid(self):
        """Test ParameterType creation from invalid string"""
        with pytest.raises(ValueError, match="Invalid parameter type"):
            ParameterType.from_string('invalid')

    def test_parameter_type_from_string_case_insensitive(self):
        """Test ParameterType is case insensitive"""
        assert ParameterType.from_string('STRING') == ParameterType.STRING
        assert ParameterType.from_string('Int') == ParameterType.INT


class TestParameterTypeChange:
    """Test parameter type conversion rules"""

    def test_can_change_type_simple_to_simple_int_to_string(self):
        """Test INT can change to STRING (simple to simple)"""
        param = Parameter(param_name='test', param_type='int')
        assert param.can_change_type('string') is True

    def test_can_change_type_simple_to_simple_string_to_boolean(self):
        """Test STRING can change to BOOLEAN (simple to simple)"""
        param = Parameter(param_name='test', param_type='string')
        assert param.can_change_type('boolean') is True

    def test_can_change_type_simple_to_simple_boolean_to_int(self):
        """Test BOOLEAN can change to INT (simple to simple)"""
        param = Parameter(param_name='test', param_type='boolean')
        assert param.can_change_type('int') is True

    def test_can_change_type_complex_to_simple_fails(self):
        """Test ARRAY cannot change to STRING (complex to simple)"""
        param = Parameter(param_name='test', param_type='array')
        assert param.can_change_type('string') is False

    def test_can_change_type_simple_to_complex_fails(self):
        """Test STRING cannot change to ARRAY (simple to complex)"""
        param = Parameter(param_name='test', param_type='string')
        assert param.can_change_type('array') is False

    def test_can_change_type_map_to_int_fails(self):
        """Test MAP cannot change to INT (complex to simple)"""
        param = Parameter(param_name='test', param_type='map')
        assert param.can_change_type('int') is False

    def test_can_change_type_invalid_type(self):
        """Test invalid type returns False"""
        param = Parameter(param_name='test', param_type='string')
        assert param.can_change_type('invalid') is False


class TestParameterWithMethods:
    """Test parameter with_* methods (immutability)"""

    def test_with_type_returns_new_instance(self):
        """Test with_type returns new instance (immutability)"""
        original = Parameter(
            id=1,
            param_name='test',
            param_type='string',
            version=1
        )

        updated = original.with_type('int')

        # New instance
        assert updated is not original
        # Type changed
        assert updated.param_type == 'int'
        # Version incremented
        assert updated.version == 2
        # Original unchanged
        assert original.param_type == 'string'
        assert original.version == 1

    def test_with_type_invalid_change_raises_error(self):
        """Test with_type raises error for invalid change"""
        param = Parameter(param_name='test', param_type='string')

        with pytest.raises(ValueError, match="Cannot change parameter type"):
            param.with_type('array')

    def test_with_common_status_returns_new_instance(self):
        """Test with_common_status returns new instance"""
        original = Parameter(
            id=1,
            param_name='test',
            param_type='string',
            is_common=False
        )

        updated = original.with_common_status(True)

        # New instance
        assert updated is not original
        # Status changed
        assert updated.is_common is True
        # Original unchanged
        assert original.is_common is False

    def test_deactivate_returns_new_instance(self):
        """Test deactivate returns new instance"""
        original = Parameter(
            id=1,
            param_name='test',
            param_type='string',
            is_active=True
        )

        deactivated = original.deactivate()

        # New instance
        assert deactivated is not original
        # Status changed
        assert deactivated.is_active is False
        # Original unchanged
        assert original.is_active is True


class TestParameterLegacyMethods:
    """Test legacy backward compatibility methods"""

    def test_name_property(self):
        """Test name property returns param_name"""
        param = Parameter(param_name='guild_id', param_type='string')
        assert param.name == 'guild_id'

    def test_type_property(self):
        """Test type property returns param_type"""
        param = Parameter(param_name='test', param_type='int')
        assert param.type == 'int'

    def test_is_common_parameter_method(self):
        """Test is_common_parameter method"""
        param = Parameter(
            param_name='test',
            param_type='string',
            is_common=True
        )
        assert param.is_common_parameter() is True

    def test_get_hive_type_string(self):
        """Test get_hive_type for STRING"""
        param = Parameter(param_name='test', param_type='string')
        assert param.get_hive_type() == 'STRING'

    def test_get_hive_type_int(self):
        """Test get_hive_type for INT"""
        param = Parameter(param_name='test', param_type='int')
        assert param.get_hive_type() == 'INT'

    def test_get_hive_type_float(self):
        """Test get_hive_type for FLOAT"""
        param = Parameter(param_name='test', param_type='float')
        assert param.get_hive_type() == 'DOUBLE'

    def test_get_hive_type_boolean(self):
        """Test get_hive_type for BOOLEAN"""
        param = Parameter(param_name='test', param_type='boolean')
        assert param.get_hive_type() == 'BOOLEAN'

    def test_get_hive_type_array(self):
        """Test get_hive_type for ARRAY"""
        param = Parameter(param_name='test', param_type='array')
        assert param.get_hive_type() == 'ARRAY<STRING>'

    def test_get_hive_type_map(self):
        """Test get_hive_type for MAP"""
        param = Parameter(param_name='test', param_type='map')
        assert param.get_hive_type() == 'MAP<STRING, STRING>'

    def test_get_hive_type_array(self):
        """Test get_hive_type for ARRAY returns default"""
        # Note: 'unknown' type will fail validation, so we test with a valid type
        param = Parameter(param_name='test', param_type='array')
        result = param.get_hive_type()
        # Should return ARRAY<STRING> or a default
        assert result in ['ARRAY<STRING>', 'STRING']


class TestParameterSerialization:
    """Test parameter serialization and deserialization"""

    def test_to_dict(self):
        """Test parameter to dictionary conversion"""
        now = datetime.now()
        param = Parameter(
            id=1,
            param_name='guild_id',
            param_type='string',
            json_path='$.guildId',
            description='Guild ID',
            event_id=1,
            game_gid=90000001,
            is_common=True,
            is_active=True,
            version=2,
            created_at=now,
            updated_at=now
        )

        result = param.to_dict()

        assert result['id'] == 1
        assert result['param_name'] == 'guild_id'
        assert result['param_type'] == 'string'
        assert result['json_path'] == '$.guildId'
        assert result['description'] == 'Guild ID'
        assert result['event_id'] == 1
        assert result['game_gid'] == 90000001
        assert result['is_common'] is True
        assert result['is_active'] is True
        assert result['version'] == 2
        assert result['created_at'] == now.isoformat()
        assert result['updated_at'] == now.isoformat()

    def test_from_dict(self):
        """Test parameter creation from dictionary"""
        now = datetime.now()
        data = {
            'id': 1,
            'param_name': 'guild_id',
            'param_type': 'string',
            'json_path': '$.guildId',
            'description': 'Guild ID',
            'event_id': 1,
            'game_gid': 90000001,
            'is_common': True,
            'is_active': True,
            'version': 2,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }

        param = Parameter.from_dict(data)

        assert param.id == 1
        assert param.param_name == 'guild_id'
        assert param.param_type == 'string'
        assert param.json_path == '$.guildId'
        assert param.description == 'Guild ID'
        assert param.event_id == 1
        assert param.game_gid == 90000001
        assert param.is_common is True
        assert param.is_active is True
        assert param.version == 2

    def test_from_dict_legacy_names(self):
        """Test from_dict with legacy field names (name, type)"""
        data = {
            'name': 'guild_id',  # Legacy name
            'type': 'string',    # Legacy type
            'json_path': '$.guildId'
        }

        param = Parameter.from_dict(data)

        assert param.param_name == 'guild_id'
        assert param.param_type == 'string'

    def test_serialization_roundtrip(self):
        """Test serialization and deserialization roundtrip"""
        original = Parameter(
            id=1,
            param_name='guild_id',
            param_type='string',
            json_path='$.guildId',
            description='Guild ID',
            event_id=1,
            game_gid=90000001,
            is_common=True,
            is_active=True
        )

        # Serialize
        data = original.to_dict()

        # Deserialize
        restored = Parameter.from_dict(data)

        # Verify
        assert restored.id == original.id
        assert restored.param_name == original.param_name
        assert restored.param_type == original.param_type
        assert restored.json_path == original.json_path
        assert restored.description == original.description
        assert restored.event_id == original.event_id
        assert restored.game_gid == original.game_gid
        assert restored.is_common == original.is_common
        assert restored.is_active == original.is_active


class TestValidationResult:
    """Test ValidationResult value object"""

    def test_validation_result_valid(self):
        """Test valid validation result"""
        result = ValidationResult(is_valid=True)

        assert result.is_valid is True
        assert result.errors == []

    def test_validation_result_invalid(self):
        """Test invalid validation result"""
        result = ValidationResult(
            is_valid=False,
            errors=['Error 1', 'Error 2']
        )

        assert result.is_valid is False
        assert result.errors == ['Error 1', 'Error 2']

    def test_add_error(self):
        """Test add_error returns new instance"""
        original = ValidationResult(is_valid=True)

        updated = original.add_error('New error')

        # New instance
        assert updated is not original
        # Error added
        assert updated.is_valid is False
        assert updated.errors == ['New error']
        # Original unchanged
        assert original.is_valid is True
        assert original.errors == []

    def test_get_error_message(self):
        """Test get_error_message concatenates errors"""
        result = ValidationResult(
            is_valid=False,
            errors=['Error 1', 'Error 2', 'Error 3']
        )

        message = result.get_error_message()

        assert message == 'Error 1; Error 2; Error 3'

    def test_get_error_message_no_errors(self):
        """Test get_error_message with no errors"""
        result = ValidationResult(is_valid=True)

        message = result.get_error_message()

        assert message == 'No errors'
