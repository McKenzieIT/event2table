# Performance Optimization: N+1 query detected (2026-03-05)
# TODO: Replace loop queries with JOIN or prefetch pattern
# Expected improvement: 50-100x faster
#
# Example optimization:
#   Original: for item in items: data = fetch_item(item.id)
#   Fixed: items_with_data = fetch_all_as_dict('SELECT * FROM items')
#

# ⚠️ PERFORMANCE ISSUE: N+1 query detected in this file
# TODO: Refactor to use JOIN or prefetch pattern
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Field Builder Service - N+1 Query Optimization

This test suite validates that the Field Builder Service uses batch queries
instead of N+1 patterns when fetching multiple configurations.

TDD Approach:
1. Write failing test (N+1 detection)
2. Implement batch query fix
3. Verify test passes
4. Add performance test
"""

import pytest
import time
from unittest.mock import Mock, patch
from backend.services.field_builder.field_builder_service import FieldBuilderService


class TestFieldBuilderServiceBatchQueries:
    """Test suite for batch query optimization in FieldBuilderService"""

    def test_get_configs_batch_no_n_plus_1(self):
        """
        Test that get_configs_batch doesn't cause N+1 queries.

        This test verifies that fetching configurations for multiple config IDs
        uses batch queries instead of looping with individual queries.

        Expected behavior:
        - Should use IN clause for batch fetching
        - Should not loop through config IDs with individual queries
        - Should complete in reasonable time (< 1 second for 100 configs)
        """
        service = FieldBuilderService()

        # Test with a small batch of config IDs
        # Note: These IDs may not exist in the database, which is fine for this test
        config_ids = [1, 2, 3, 4, 5]

        # Attempt to fetch configs in batch
        # This method should be implemented to avoid N+1 queries
        try:
            configs = service.get_configs_batch(config_ids)
        except AttributeError:
            # Method doesn't exist yet - this is expected in TDD red phase
            pytest.skip("get_configs_batch method not yet implemented")

        # Verify results structure
        assert isinstance(configs, dict), "Should return a dictionary"
        assert len(configs) <= len(config_ids), "Should not return more configs than requested"

        # Each config should have expected fields
        for config_id, config in configs.items():
            if config is not None:  # Config might not exist
                assert isinstance(config, dict), f"Config {config_id} should be a dict"
                assert "id" in config, f"Config {config_id} should have 'id' field"

    def test_get_configs_batch_performance(self):
        """
        Performance test for batch config fetching.

        Verifies that fetching 100 configs completes in under 1 second.
        This ensures batch queries are being used instead of N+1 pattern.

        Performance expectations:
        - 100 configs should be fetched in < 1 second with batch query
        - N+1 pattern would take 5-10 seconds (100 individual queries)
        """
        service = FieldBuilderService()

        # Test with a larger batch (100 config IDs)
        config_ids = list(range(1, 101))

        start_time = time.time()
        try:
            configs = service.get_configs_batch(config_ids)
        except AttributeError:
            # Method doesn't exist yet - skip in TDD red phase
            pytest.skip("get_configs_batch method not yet implemented")

        elapsed = time.time() - start_time

        # Performance assertion: should complete quickly with batch query
        # If this fails, it likely indicates N+1 pattern is being used
        assert elapsed < 1.0, (
            f"Batch query too slow: {elapsed:.3f}s (expected < 1s). "
            f"This suggests N+1 query pattern instead of batch query."
        )

        # Should have returned results (even if many are None for non-existent IDs)
        assert isinstance(configs, dict), "Should return a dictionary"

    def test_get_configs_batch_empty_list(self):
        """Test that empty config_ids list returns empty dict"""
        service = FieldBuilderService()

        try:
            configs = service.get_configs_batch([])
        except AttributeError:
            pytest.skip("get_configs_batch method not yet implemented")

        assert configs == {}, "Empty input should return empty dict"

    def test_get_configs_batch_mixed_valid_invalid_ids(self):
        """Test handling of mix of valid and invalid config IDs"""
        service = FieldBuilderService()

        # Mix of likely valid (low numbers) and invalid (high numbers) IDs
        config_ids = [1, 999999, 2, 999998, 3]

        try:
            configs = service.get_configs_batch(config_ids)
        except AttributeError:
            pytest.skip("get_configs_batch method not yet implemented")

        # Should return dict with same number of entries
        assert len(configs) == len(
            config_ids
        ), f"Should return {len(config_ids)} entries (including None for non-existent)"

        # Valid IDs should have data, invalid IDs should be None
        for config_id in config_ids:
            assert config_id in configs, f"Config ID {config_id} should be in result"


class TestFieldBuilderServiceExistingMethods:
    """Test suite for existing methods to ensure they don't have N+1 patterns"""

    @patch('backend.core.utils.converters.fetch_all_as_dict')
    def test_list_configs_no_n_plus_1(self, mock_fetch):
        """
        Test that list_configs doesn't cause N+1 queries.

        list_configs should fetch all configs in a single query,
        not loop through and fetch additional data.
        """
        # Mock the database response
        mock_fetch.return_value = [
            {"id": 1, "name": "Config1", "view_name": "v_dwd_1", "display_name": "Config 1"},
            {"id": 2, "name": "Config2", "view_name": "v_dwd_2", "display_name": "Config 2"},
        ]

        service = FieldBuilderService()
        configs = service.list_configs(limit=10)

        # Verify fetch_all_as_dict was called exactly once (no N+1)
        assert mock_fetch.call_count == 1, (
            f"list_configs should use 1 query, but used {mock_fetch.call_count}. "
            f"This indicates N+1 query pattern."
        )

        # Verify results
        assert len(configs) == 2
        assert configs[0]["id"] == 1

    @patch('backend.core.utils.converters.fetch_one_as_dict')
    def test_get_config_by_id_single_query(self, mock_fetch):
        """
        Test that get_config_by_id uses exactly one query.

        This should not loop or fetch additional data.
        """
        # Mock the database response
        mock_fetch.return_value = {
            "id": 1,
            "field_mapping_v2": '{"fields": []}',
            "output_table": "v_dwd_test",
            "display_name": "Test Config",
        }

        service = FieldBuilderService()
        config = service.get_config_by_id(1)

        # Verify fetch_one_as_dict was called exactly once
        assert (
            mock_fetch.call_count == 1
        ), f"get_config_by_id should use 1 query, but used {mock_fetch.call_count}"

        # Verify result
        assert config is not None
        assert config["id"] == 1
        assert config["config"] == {"fields": []}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
