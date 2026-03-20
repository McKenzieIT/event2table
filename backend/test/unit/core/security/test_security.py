#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for backend.core.security module

Provides security utilities including SQL injection prevention,
path validation, and cache security.
"""

import pytest

from backend.core.security import SQLValidator

# PathValidator is conditionally imported
try:
    from backend.core.security import PathValidator

    PATH_VALIDATOR_AVAILABLE = True
except ImportError:
    PATH_VALIDATOR_AVAILABLE = False


class TestSQLValidator:
    """Test SQLValidator functionality"""

    def test_import(self):
        """Test module can be imported"""
        assert SQLValidator is not None

    def test_validate_table_name(self):
        """Test table name validation"""
        # Valid table names
        assert SQLValidator.validate_table_name("games") == "games"
        assert SQLValidator.validate_table_name("log_events") == "log_events"
        assert SQLValidator.validate_table_name("test_table") == "test_table"

        # Invalid table names
        with pytest.raises(ValueError):
            SQLValidator.validate_table_name("games; DROP TABLE users--")
        with pytest.raises(ValueError):
            SQLValidator.validate_table_name("games' OR '1'='1")
        with pytest.raises(ValueError):
            SQLValidator.validate_table_name("")
            # Empty string

    def test_validate_column_name(self):
        """Test column name validation"""
        # Valid column names
        assert SQLValidator.validate_column_name("id") == "id"
        assert SQLValidator.validate_column_name("game_gid") == "game_gid"
        assert SQLValidator.validate_column_name("created_at") == "created_at"

        # Invalid column names
        with pytest.raises(ValueError):
            SQLValidator.validate_column_name("id; DROP TABLE users--")
        with pytest.raises(ValueError):
            SQLValidator.validate_column_name("id' OR '1'='1")
        with pytest.raises(ValueError):
            SQLValidator.validate_column_name("")
            # Empty string

    def test_validate_field_whitelist(self):
        """Test field whitelist validation"""
        allowed_fields = {"id", "name", "gid", "created_at"}

        # Valid fields
        SQLValidator.validate_field_whitelist("id", allowed_fields)
        SQLValidator.validate_field_whitelist("name", allowed_fields)
        SQLValidator.validate_field_whitelist("gid", allowed_fields)

        # Invalid fields
        with pytest.raises(ValueError):
            SQLValidator.validate_field_whitelist("invalid_field", allowed_fields)
        with pytest.raises(ValueError):
            SQLValidator.validate_field_whitelist("id; DROP TABLE--", allowed_fields)


@pytest.mark.skipif(not PATH_VALIDATOR_AVAILABLE, reason="PathValidator not available")
class TestPathValidator:
    """Test PathValidator functionality"""

    def test_import(self):
        """Test module can be imported"""
        assert PathValidator is not None

    def test_validate_path_safe(self):
        """Test safe path validation"""
        # Safe paths
        assert PathValidator.is_safe_path("/tmp/test.txt")
        assert PathValidator.is_safe_path("/var/log/app.log")
        assert PathValidator.is_safe_path("data/test.db")

        # Unsafe paths (path traversal)
        assert not PathValidator.is_safe_path("/etc/passwd")
        assert not PathValidator.is_safe_path("../../../etc/passwd")
        assert not PathValidator.is_safe_path("/tmp/../../../etc/shadow")


class TestCacheSecurity:
    """Test cache security features"""

    def test_import_cache_security(self):
        """Test cache security modules can be imported"""
        try:
            from backend.core.security import CacheKeyValidator, SensitiveDataFilter

            assert CacheKeyValidator is not None
            assert SensitiveDataFilter is not None
        except ImportError:
            pytest.skip("Cache security modules not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
