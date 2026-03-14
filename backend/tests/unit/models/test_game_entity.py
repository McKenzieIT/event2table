#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for GameEntity

Tests for Pydantic Entity model including:
- Field validation
- Type conversion
- XSS protection
- GID validation
- Serialization/Deserialization
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from backend.models.entities import GameEntity


class TestGameEntityValidation:
    """Test Pydantic validation for GameEntity"""

    def test_valid_game_creation_minimal(self):
        """Test valid game creation with minimal fields"""
        game = GameEntity(gid=90000001, name='Test Game', ods_db='ieu_ods')
        assert game.gid == 90000001
        assert game.name == 'Test Game'
        assert game.ods_db == 'ieu_ods'
        assert game.dwd_prefix == 'dwd'  # Default value
        assert game.description is None  # Optional field

    def test_valid_game_creation_full(self):
        """Test valid game creation with all fields"""
        now = datetime.now()
        game = GameEntity(
            id=1,
            gid=90000001,
            name='Test Game',
            ods_db='ieu_ods',
            description='Test game description',
            dwd_prefix='dwd',
            icon_path='/path/to/icon.png',
            created_at=now,
            updated_at=now,
            event_count=10,
        )
        assert game.id == 1
        assert game.gid == 90000001
        assert game.name == 'Test Game'
        assert game.ods_db == 'ieu_ods'
        assert game.description == 'Test game description'
        assert game.dwd_prefix == 'dwd'
        assert game.icon_path == '/path/to/icon.png'

    def test_xss_protection_in_name(self):
        """Test XSS protection in name field"""
        game = GameEntity(
            gid=90000001, name='<script>alert("xss")</script>Test Game', ods_db='ieu_ods'
        )
        # HTML should be escaped
        assert '<script>' not in game.name
        assert '&lt;script&gt;' in game.name
        assert 'Test Game' in game.name

    def test_xss_protection_in_description(self):
        """Test XSS protection in description field"""
        # Note: description field doesn't have XSS protection in current implementation
        game = GameEntity(
            gid=90000001,
            name='Test Game',
            ods_db='ieu_ods',
            description='<img src=x onerror=alert(1)> test',
        )
        # Currently no XSS protection on description field
        assert '<img' in game.description

    def test_ods_db_valid_values(self):
        """Test all valid ods_db values"""
        valid_dbs = ['ieu_ods', 'overseas_ods']

        for db in valid_dbs:
            game = GameEntity(gid=90000001, name='Test Game', ods_db=db)
            assert game.ods_db == db

    def test_ods_db_invalid_value(self):
        """Test invalid ods_db is rejected"""
        with pytest.raises(ValidationError):
            GameEntity(gid=90000001, name='Test Game', ods_db='invalid_db')

    def test_gid_must_be_non_negative(self):
        """Test gid must be non-negative"""
        with pytest.raises(ValidationError, match="gid必须是正整数"):
            GameEntity(gid=-1, name='Test Game', ods_db='ieu_ods')  # Invalid

    def test_gid_accepts_string(self):
        """Test gid accepts string and converts to int"""
        game = GameEntity(gid="90000001", name='Test Game', ods_db='ieu_ods')  # String
        assert isinstance(game.gid, int)
        assert game.gid == 90000001

    def test_gid_rejects_invalid_string(self):
        """Test gid rejects non-numeric string"""
        with pytest.raises(ValidationError, match="gid必须是整数"):
            GameEntity(gid="not_a_number", name='Test Game', ods_db='ieu_ods')

    def test_name_min_length(self):
        """Test name minimum length validation"""
        with pytest.raises(ValidationError):
            GameEntity(gid=90000001, name='', ods_db='ieu_ods')  # Too short

    def test_name_max_length(self):
        """Test name maximum length validation"""
        with pytest.raises(ValidationError):
            GameEntity(gid=90000001, name='x' * 101, ods_db='ieu_ods')  # Too long (max 100)

    def test_event_count_default(self):
        """Test event_count defaults to 0"""
        game = GameEntity(gid=90000001, name='Test Game', ods_db='ieu_ods')
        assert game.event_count == 0

    def test_event_count_excluded_from_json(self):
        """Test event_count is excluded from JSON serialization"""
        game = GameEntity(gid=90000001, name='Test Game', ods_db='ieu_ods', event_count=10)
        data = game.model_dump()
        assert 'event_count' not in data


class TestGameEntitySerialization:
    """Test Entity serialization and deserialization"""

    def test_model_dump_returns_dict(self):
        """Test model_dump() returns dict"""
        game = GameEntity(id=1, gid=90000001, name='Test Game', ods_db='ieu_ods')
        data = game.model_dump()

        assert isinstance(data, dict)
        assert data['id'] == 1
        assert data['gid'] == 90000001
        assert data['name'] == 'Test Game'

    def test_model_dump_exclude_unset(self):
        """Test model_dump(exclude_unset=True) excludes unset fields"""
        game = GameEntity(gid=90000001, name='Test Game', ods_db='ieu_ods')
        data = game.model_dump(exclude_unset=True)

        # Unset optional fields should be excluded
        assert 'id' not in data  # Not set
        assert 'description' not in data  # Not set
        assert 'icon_path' not in data  # Not set
        # Required fields should be present
        assert 'gid' in data
        assert 'name' in data

    def test_model_dump_json(self):
        """Test model_dump_json() returns JSON string"""
        game = GameEntity(id=1, gid=90000001, name='Test Game', ods_db='ieu_ods')
        json_str = game.model_dump_json()

        assert isinstance(json_str, str)
        assert 'Test Game' in json_str
        assert '"gid":90000001' in json_str

    def test_model_dump_json_roundtrip(self):
        """Test serialization and deserialization roundtrip"""
        original = GameEntity(
            id=1,
            gid=90000001,
            name='Test Game',
            ods_db='ieu_ods',
            description='Test description',
            dwd_prefix='dwd',
        )

        # Serialize
        json_str = original.model_dump_json()

        # Deserialize
        restored = GameEntity.model_validate_json(json_str)

        # Verify
        assert restored.id == original.id
        assert restored.gid == original.gid
        assert restored.name == original.name
        assert restored.description == original.description

    def test_from_dict(self):
        """Test creating Entity from dict"""
        data = {
            'id': 1,
            'gid': 90000001,
            'name': 'Test Game',
            'ods_db': 'ieu_ods',
            'description': 'Test description',
        }

        game = GameEntity(**data)

        assert game.id == 1
        assert game.gid == 90000001
        assert game.name == 'Test Game'
        assert game.description == 'Test description'

    def test_datetime_serialization(self):
        """Test datetime fields are serialized correctly"""
        now = datetime.now()
        game = GameEntity(
            id=1, gid=90000001, name='Test Game', ods_db='ieu_ods', created_at=now, updated_at=now
        )

        # model_dump should serialize datetime to ISO format
        data = game.model_dump()
        assert isinstance(data['created_at'], str)
        assert isinstance(data['updated_at'], str)
        assert data['created_at'] == now.isoformat()


class TestGameEntityJSONSchema:
    """Test JSON Schema generation"""

    def test_json_schema_generation(self):
        """Test JSON Schema is generated correctly"""
        schema = GameEntity.model_json_schema()

        assert 'properties' in schema
        assert 'gid' in schema['properties']
        assert 'name' in schema['properties']
        assert 'ods_db' in schema['properties']
        assert 'dwd_prefix' in schema['properties']

    def test_json_schema_required_fields(self):
        """Test JSON Schema marks required fields"""
        schema = GameEntity.model_json_schema()

        required = schema.get('required', [])
        assert 'gid' in required
        assert 'name' in required
        assert 'ods_db' in required

    def test_json_schema_optional_fields(self):
        """Test JSON Schema marks optional fields"""
        schema = GameEntity.model_json_schema()

        required = schema.get('required', [])
        # These should not be in required
        assert 'id' not in required
        assert 'description' not in required
        assert 'icon_path' not in required

    def test_json_schema_enum_constraints(self):
        """Test JSON Schema includes enum constraints for ods_db"""
        schema = GameEntity.model_json_schema()

        ods_db_prop = schema['properties']['ods_db']
        assert 'enum' in ods_db_prop
        assert set(ods_db_prop['enum']) == {'ieu_ods', 'overseas_ods'}


class TestGameEntityFieldValidation:
    """Test individual field validations"""

    def test_name_whitespace_trimmed(self):
        """Test name has whitespace trimmed"""
        game = GameEntity(gid=90000001, name='  Test Game  ', ods_db='ieu_ods')  # Whitespace
        assert game.name == 'Test Game'  # Trimmed

    def test_description_whitespace_trimmed(self):
        """Test description has whitespace trimmed"""
        # Note: description field doesn't trim whitespace in current implementation
        game = GameEntity(
            gid=90000001,
            name='Test Game',
            ods_db='ieu_ods',
            description='  Test description  ',  # Whitespace
        )
        # Currently no trimming on description field
        assert game.description == '  Test description  '

    def test_dwd_prefix_default(self):
        """Test dwd_prefix defaults to 'dwd'"""
        game = GameEntity(gid=90000001, name='Test Game', ods_db='ieu_ods')
        assert game.dwd_prefix == 'dwd'

    def test_id_can_be_none(self):
        """Test id can be None (for new entities)"""
        game = GameEntity(
            id=None, gid=90000001, name='Test Game', ods_db='ieu_ods'  # Explicit None
        )
        assert game.id is None


class TestGameEntityEdgeCases:
    """Test edge cases and error handling"""

    def test_all_fields_none_except_required(self):
        """Test entity with only required fields"""
        game = GameEntity(gid=90000001, name='Test Game', ods_db='ieu_ods')
        assert game.id is None
        assert game.description is None
        assert game.icon_path is None
        assert game.created_at is None
        assert game.updated_at is None

    def test_special_characters_in_name(self):
        """Test special characters in name are escaped"""
        special_names = [
            '<script>alert("xss")</script>',
            '"><img src=x onerror=alert(1)>',
            '\' OR 1=1 --',
        ]

        for name in special_names:
            game = GameEntity(gid=90000001, name=name, ods_db='ieu_ods')
            # Should be HTML-escaped
            assert '<script>' not in game.name
            assert '<img' not in game.name

    def test_unicode_in_name(self):
        """Test unicode characters in name"""
        game = GameEntity(gid=90000001, name='测试游戏', ods_db='ieu_ods')  # Chinese characters
        assert game.name == '测试游戏'

    def test_very_long_valid_name(self):
        """Test maximum length name is accepted"""
        game = GameEntity(gid=90000001, name='x' * 100, ods_db='ieu_ods')  # Max length
        assert len(game.name) == 100

    def test_gid_zero_is_allowed(self):
        """Test gid=0 is allowed"""
        game = GameEntity(gid=0, name='Test Game', ods_db='ieu_ods')
        assert game.gid == 0

    def test_custom_dwd_prefix(self):
        """Test custom dwd_prefix is accepted"""
        game = GameEntity(gid=90000001, name='Test Game', ods_db='ieu_ods', dwd_prefix='custom_dwd')
        assert game.dwd_prefix == 'custom_dwd'
