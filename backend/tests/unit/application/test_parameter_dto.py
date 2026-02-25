"""
Unit Tests for Parameter DTOs

Tests for Data Transfer Objects including:
- ParameterFilterDTO
- ParameterTypeChangeDTO
- ParameterCreateDTO
- CommonParameterSyncDTO
- FieldBatchAddDTO
- ParameterUpdateDTO
- ParameterBatchDeleteDTO
- FieldTypeEnum
"""

import pytest
from backend.application.dtos.parameter_dto import (
    FieldTypeEnum,
    ParameterFilterDTO,
    ParameterTypeChangeDTO,
    ParameterCreateDTO,
    CommonParameterSyncDTO,
    FieldBatchAddDTO,
    ParameterUpdateDTO,
    ParameterBatchDeleteDTO
)


class TestFieldTypeEnum:
    """Test FieldTypeEnum"""

    def test_field_type_enum_values(self):
        """Test all enum values are defined"""
        assert FieldTypeEnum.ALL.value == 'all'
        assert FieldTypeEnum.PARAMS.value == 'params'
        assert FieldTypeEnum.NON_COMMON.value == 'non-common'
        assert FieldTypeEnum.COMMON.value == 'common'
        assert FieldTypeEnum.BASE.value == 'base'

    def test_is_valid_valid_values(self):
        """Test is_valid returns True for valid values"""
        valid_values = ['all', 'params', 'non-common', 'common', 'base']

        for value in valid_values:
            assert FieldTypeEnum.is_valid(value), f"Should be valid: {value}"

    def test_is_valid_invalid_values(self):
        """Test is_valid returns False for invalid values"""
        invalid_values = ['invalid', 'ALL', 'Params', '']

        for value in invalid_values:
            assert not FieldTypeEnum.is_valid(value), f"Should be invalid: {value}"


class TestParameterFilterDTO:
    """Test ParameterFilterDTO"""

    def test_parameter_filter_dto_valid(self):
        """Test valid ParameterFilterDTO creation"""
        dto = ParameterFilterDTO(
            game_gid=90000001,
            mode='all',
            event_id=None
        )

        assert dto.game_gid == 90000001
        assert dto.mode == 'all'
        assert dto.event_id is None

    def test_parameter_filter_dto_with_event_id(self):
        """Test ParameterFilterDTO with event_id"""
        dto = ParameterFilterDTO(
            game_gid=90000001,
            mode='common',
            event_id=1
        )

        assert dto.game_gid == 90000001
        assert dto.mode == 'common'
        assert dto.event_id == 1

    def test_parameter_filter_dto_invalid_game_gid(self):
        """Test invalid game_gid raises error"""
        with pytest.raises(ValueError, match="Invalid game_gid"):
            ParameterFilterDTO(game_gid=-1, mode='all')

        with pytest.raises(ValueError, match="Invalid game_gid"):
            ParameterFilterDTO(game_gid=0, mode='all')

    def test_parameter_filter_dto_invalid_mode(self):
        """Test invalid mode raises error"""
        with pytest.raises(ValueError, match="Invalid mode"):
            ParameterFilterDTO(game_gid=90000001, mode='invalid')

    def test_parameter_filter_dto_invalid_event_id(self):
        """Test invalid event_id raises error"""
        with pytest.raises(ValueError, match="Invalid event_id"):
            ParameterFilterDTO(
                game_gid=90000001,
                mode='all',
                event_id=-1
            )

    def test_parameter_filter_dto_frozen(self):
        """Test DTO is immutable (frozen)"""
        dto = ParameterFilterDTO(game_gid=90000001, mode='all')

        with pytest.raises(Exception):  # FrozenInstanceError
            dto.game_gid = 90000002


class TestParameterTypeChangeDTO:
    """Test ParameterTypeChangeDTO"""

    def test_parameter_type_change_dto_valid(self):
        """Test valid ParameterTypeChangeDTO creation"""
        dto = ParameterTypeChangeDTO(
            parameter_id=1,
            new_type='base'
        )

        assert dto.parameter_id == 1
        assert dto.new_type == 'base'

    def test_parameter_type_change_dto_all_valid_types(self):
        """Test all valid new_type values"""
        valid_types = ['base', 'common', 'params']

        for new_type in valid_types:
            dto = ParameterTypeChangeDTO(parameter_id=1, new_type=new_type)
            assert dto.new_type == new_type

    def test_parameter_type_change_dto_invalid_parameter_id(self):
        """Test invalid parameter_id raises error"""
        with pytest.raises(ValueError, match="Invalid parameter_id"):
            ParameterTypeChangeDTO(parameter_id=0, new_type='base')

        with pytest.raises(ValueError, match="Invalid parameter_id"):
            ParameterTypeChangeDTO(parameter_id=-1, new_type='base')

    def test_parameter_type_change_dto_invalid_new_type_empty(self):
        """Test empty new_type raises error"""
        with pytest.raises(ValueError, match="Invalid new_type"):
            ParameterTypeChangeDTO(parameter_id=1, new_type='')

    def test_parameter_type_change_dto_invalid_new_type_value(self):
        """Test invalid new_type value raises error"""
        with pytest.raises(ValueError, match="Invalid new_type"):
            ParameterTypeChangeDTO(parameter_id=1, new_type='invalid')


class TestParameterCreateDTO:
    """Test ParameterCreateDTO"""

    def test_parameter_create_dto_valid(self):
        """Test valid ParameterCreateDTO creation"""
        dto = ParameterCreateDTO(
            param_name='guild_id',
            param_type='base',
            json_path='$.guildId',
            event_id=1,
            game_gid=90000001,
            param_name_cn='公会ID'
        )

        assert dto.param_name == 'guild_id'
        assert dto.param_type == 'base'
        assert dto.json_path == '$.guildId'
        assert dto.event_id == 1
        assert dto.game_gid == 90000001
        assert dto.param_name_cn == '公会ID'

    def test_parameter_create_dto_minimal(self):
        """Test ParameterCreateDTO with minimal fields"""
        dto = ParameterCreateDTO(
            param_name='zone_id',
            param_type='params',
            json_path='$.zoneId',
            event_id=1,
            game_gid=90000001
        )

        assert dto.param_name == 'zone_id'
        assert dto.param_name_cn is None

    def test_parameter_create_dto_sanitizes_names(self):
        """Test DTO sanitizes param_name and param_name_cn"""
        dto = ParameterCreateDTO(
            param_name='  guild_id  ',
            param_type='base',
            json_path='$.guildId',
            event_id=1,
            game_gid=90000001,
            param_name_cn='  公会ID  '
        )

        assert dto.param_name == 'guild_id'
        assert dto.param_name_cn == '公会ID'

    def test_parameter_create_dto_empty_param_name(self):
        """Test empty param_name raises error"""
        with pytest.raises(ValueError, match="Invalid param_name"):
            ParameterCreateDTO(
                param_name='',
                param_type='base',
                json_path='$.guildId',
                event_id=1,
                game_gid=90000001
            )

    def test_parameter_create_dto_invalid_param_type(self):
        """Test invalid param_type raises error"""
        with pytest.raises(ValueError, match="Invalid param_type"):
            ParameterCreateDTO(
                param_name='test',
                param_type='invalid',
                json_path='$.test',
                event_id=1,
                game_gid=90000001
            )

    def test_parameter_create_dto_invalid_json_path_format(self):
        """Test invalid json_path format raises error"""
        with pytest.raises(ValueError, match="Invalid json_path format"):
            ParameterCreateDTO(
                param_name='test',
                param_type='base',
                json_path='invalid',
                event_id=1,
                game_gid=90000001
            )

    def test_parameter_create_dto_invalid_event_id(self):
        """Test invalid event_id raises error"""
        with pytest.raises(ValueError, match="Invalid event_id"):
            ParameterCreateDTO(
                param_name='test',
                param_type='base',
                json_path='$.test',
                event_id=0,
                game_gid=90000001
            )

    def test_parameter_create_dto_invalid_game_gid(self):
        """Test invalid game_gid raises error"""
        with pytest.raises(ValueError, match="Invalid game_gid"):
            ParameterCreateDTO(
                param_name='test',
                param_type='base',
                json_path='$.test',
                event_id=1,
                game_gid=0
            )


class TestCommonParameterSyncDTO:
    """Test CommonParameterSyncDTO"""

    def test_common_parameter_sync_dto_valid(self):
        """Test valid CommonParameterSyncDTO creation"""
        dto = CommonParameterSyncDTO(
            game_gid=90000001,
            force_recalculate=True
        )

        assert dto.game_gid == 90000001
        assert dto.force_recalculate is True

    def test_common_parameter_sync_dto_defaults(self):
        """Test CommonParameterSyncDTO default values"""
        dto = CommonParameterSyncDTO(game_gid=90000001)

        assert dto.game_gid == 90000001
        assert dto.force_recalculate is False

    def test_common_parameter_sync_dto_invalid_game_gid(self):
        """Test invalid game_gid raises error"""
        with pytest.raises(ValueError, match="Invalid game_gid"):
            CommonParameterSyncDTO(game_gid=-1)

    def test_common_parameter_sync_dto_invalid_force_recalculate(self):
        """Test invalid force_recalculate raises error"""
        with pytest.raises(ValueError, match="Invalid force_recalculate"):
            CommonParameterSyncDTO(
                game_gid=90000001,
                force_recalculate='yes'  # Should be bool
            )


class TestFieldBatchAddDTO:
    """Test FieldBatchAddDTO"""

    def test_field_batch_add_dto_valid(self):
        """Test valid FieldBatchAddDTO creation"""
        dto = FieldBatchAddDTO(
            event_id=1,
            field_type='all'
        )

        assert dto.event_id == 1
        assert dto.field_type == 'all'

    def test_field_batch_add_dto_all_valid_types(self):
        """Test all valid field_type values"""
        valid_types = ['all', 'params', 'non-common', 'common', 'base']

        for field_type in valid_types:
            dto = FieldBatchAddDTO(event_id=1, field_type=field_type)
            assert dto.field_type == field_type

    def test_field_batch_add_dto_invalid_event_id(self):
        """Test invalid event_id raises error"""
        with pytest.raises(ValueError, match="Invalid event_id"):
            FieldBatchAddDTO(event_id=0, field_type='all')

    def test_field_batch_add_dto_invalid_field_type(self):
        """Test invalid field_type raises error"""
        with pytest.raises(ValueError, match="Invalid field_type"):
            FieldBatchAddDTO(event_id=1, field_type='invalid')


class TestParameterUpdateDTO:
    """Test ParameterUpdateDTO"""

    def test_parameter_update_dto_valid_single_field(self):
        """Test valid ParameterUpdateDTO with one field"""
        dto = ParameterUpdateDTO(
            parameter_id=1,
            param_name='new_name'
        )

        assert dto.parameter_id == 1
        assert dto.param_name == 'new_name'
        assert dto.param_name_cn is None
        assert dto.param_type is None
        assert dto.json_path is None

    def test_parameter_update_dto_valid_multiple_fields(self):
        """Test valid ParameterUpdateDTO with multiple fields"""
        dto = ParameterUpdateDTO(
            parameter_id=1,
            param_name='new_name',
            param_name_cn='新名称',
            json_path='$.newPath'
        )

        assert dto.param_name == 'new_name'
        assert dto.param_name_cn == '新名称'
        assert dto.json_path == '$.newPath'

    def test_parameter_update_dto_no_fields_raises_error(self):
        """Test DTO with no fields to update raises error"""
        with pytest.raises(ValueError, match="At least one field must be provided"):
            ParameterUpdateDTO(parameter_id=1)

    def test_parameter_update_dto_invalid_parameter_id(self):
        """Test invalid parameter_id raises error"""
        with pytest.raises(ValueError, match="Invalid parameter_id"):
            ParameterUpdateDTO(
                parameter_id=0,
                param_name='test'
            )

    def test_parameter_update_dto_sanitizes_strings(self):
        """Test DTO sanitizes string fields"""
        dto = ParameterUpdateDTO(
            parameter_id=1,
            param_name='  test_name  ',
            param_name_cn='  测试名称  '
        )

        assert dto.param_name == 'test_name'
        assert dto.param_name_cn == '测试名称'

    def test_parameter_update_dto_empty_param_name(self):
        """Test empty param_name raises error"""
        with pytest.raises(ValueError, match="Invalid param_name"):
            ParameterUpdateDTO(
                parameter_id=1,
                param_name=''
            )

    def test_parameter_update_dto_invalid_param_type(self):
        """Test invalid param_type raises error"""
        with pytest.raises(ValueError, match="Invalid param_type"):
            ParameterUpdateDTO(
                parameter_id=1,
                param_type='invalid'
            )

    def test_parameter_update_dto_invalid_json_path_format(self):
        """Test invalid json_path format raises error"""
        with pytest.raises(ValueError, match="Invalid json_path format"):
            ParameterUpdateDTO(
                parameter_id=1,
                json_path='invalid'
            )


class TestParameterBatchDeleteDTO:
    """Test ParameterBatchDeleteDTO"""

    def test_parameter_batch_delete_dto_valid(self):
        """Test valid ParameterBatchDeleteDTO creation"""
        dto = ParameterBatchDeleteDTO(
            parameter_ids=[1, 2, 3],
            game_gid=90000001
        )

        assert dto.parameter_ids == (1, 2, 3)  # Converted to tuple
        assert dto.game_gid == 90000001

    def test_parameter_batch_delete_dto_converts_list_to_tuple(self):
        """Test DTO converts list to tuple for immutability"""
        dto = ParameterBatchDeleteDTO(
            parameter_ids=[1, 2, 3],
            game_gid=90000001
        )

        assert isinstance(dto.parameter_ids, tuple)
        assert len(dto.parameter_ids) == 3

    def test_parameter_batch_delete_dto_empty_list_raises_error(self):
        """Test empty parameter_ids list raises error"""
        with pytest.raises(ValueError, match="Invalid parameter_ids"):
            ParameterBatchDeleteDTO(
                parameter_ids=[],
                game_gid=90000001
            )

    def test_parameter_batch_delete_dto_invalid_ids_in_list(self):
        """Test invalid IDs in list raise error"""
        with pytest.raises(ValueError, match="Invalid parameter_id in list"):
            ParameterBatchDeleteDTO(
                parameter_ids=[1, 2, 0],  # 0 is invalid
                game_gid=90000001
            )

        with pytest.raises(ValueError, match="Invalid parameter_id in list"):
            ParameterBatchDeleteDTO(
                parameter_ids=[1, 2, -1],  # -1 is invalid
                game_gid=90000001
            )

    def test_parameter_batch_delete_dto_invalid_game_gid(self):
        """Test invalid game_gid raises error"""
        with pytest.raises(ValueError, match="Invalid game_gid"):
            ParameterBatchDeleteDTO(
                parameter_ids=[1, 2, 3],
                game_gid=0
            )


class TestDTOImmutability:
    """Test DTO immutability across all DTOs"""

    def test_all_dtos_are_frozen(self):
        """Test all DTOs are frozen (immutable)"""
        dtos = [
            ParameterFilterDTO(game_gid=90000001, mode='all'),
            ParameterTypeChangeDTO(parameter_id=1, new_type='base'),
            ParameterCreateDTO(
                param_name='test',
                param_type='base',
                json_path='$.test',
                event_id=1,
                game_gid=90000001
            ),
            CommonParameterSyncDTO(game_gid=90000001),
            FieldBatchAddDTO(event_id=1, field_type='all'),
            ParameterUpdateDTO(parameter_id=1, param_name='test'),
            ParameterBatchDeleteDTO(parameter_ids=[1], game_gid=90000001)
        ]

        for dto in dtos:
            with pytest.raises(Exception):  # FrozenInstanceError
                # Try to modify any attribute
                if hasattr(dto, 'game_gid'):
                    dto.game_gid = 999999
                elif hasattr(dto, 'parameter_id'):
                    dto.parameter_id = 999
                elif hasattr(dto, 'event_id'):
                    dto.event_id = 999
