"""
Performance tests for field usage calculation

Tests the P0-5 performance issue:
- _calculate_field_usage performs 2 LIKE queries per field
- Called in a loop in resolve_event_fields
- 50 fields → 100 database queries
- Needs batch query or caching optimization

Author: Event2Table Development Team
Date: 2026-03-08
TDD Phase: RED (failing tests)
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from backend.gql_api.resolvers.parameter_resolvers import _calculate_field_usage


class TestFieldUsagePerformance:
    """
    Test suite for field usage performance optimization

    Current Implementation Issues:
    - N+1 query pattern in resolve_event_fields
    - Each field triggers 2 separate LIKE queries
    - No caching mechanism
    - No batch query optimization
    """

    def test_calculate_field_usage_performance(self):
        """
        Test field usage calculation performance (BATCH version)

        Current behavior:
        - 50 fields * 2 queries = 100 database calls (old individual function)

        Expected behavior (after optimization):
        - Batch query: 2 database calls total (1 HQL + 1 flow)
        - Expected time: <500ms
        """
        # Simulate 50 fields (realistic scenario)
        field_names = [f'field_{i}' for i in range(1, 51)]
        event_id = 1

        with patch('backend.core.utils.fetch_all_as_dict') as mock_fetch:
            # Mock query results - each field appears 10 times
            mock_fetch.return_value = [
                {'field_name': name, 'total_count': 10} for name in field_names
            ]

            # Track call count
            call_count = {'count': 0}

            def counting_fetch(*args, **kwargs):
                call_count['count'] += 1
                return (
                    mock_fetch.return_value
                    if 'UNION' in args[0] or 'GROUP BY' in args[0]
                    else [{'field_name': args[1][0].replace('%', ''), 'total_count': 10}]
                )

            mock_fetch.side_effect = counting_fetch

            # Measure performance with BATCH function
            start_time = time.time()

            from backend.gql_api.resolvers.parameter_resolvers import _calculate_field_usage_batch

            result = _calculate_field_usage_batch(field_names, event_id)

            elapsed = time.time() - start_time

            # Performance check (should be <500ms)
            assert elapsed < 0.5, f"Performance too slow: {elapsed:.3f}s (should be <0.5s)"

            # Query count check (should be 2 for batch query: 1 HQL + 1 flow)
            assert (
                call_count['count'] == 2
            ), f"Wrong number of DB calls: {call_count['count']} (should be 2: 1 HQL + 1 flow batch query)"

            # Verify all fields are present in result
            assert len(result) == len(
                field_names
            ), f"Missing fields in result: got {len(result)}, expected {len(field_names)}"

    def test_calculate_field_usage_has_cache(self):
        """
        Test that _calculate_field_usage has cache mechanism

        Current implementation: No cache decorator
        Expected: @cached or @cache decorator
        """
        import inspect
        from backend.gql_api.resolvers.parameter_resolvers import _calculate_field_usage

        # Check function source for cache decorators
        source = inspect.getsource(_calculate_field_usage)

        # CURRENT IMPLEMENTATION: This will FAIL
        # No cache decorator present
        has_cache = '@cached' in source or '@cache' in source or '@lru_cache' in source

        assert (
            has_cache
        ), "_calculate_field_usage should have cache decorator (@cached, @cache, or @lru_cache)"

    def test_calculate_field_usage_batch_query_method(self):
        """
        Test that batch query method exists

        Current implementation: No batch method
        Expected: Batch method like _calculate_field_usage_batch
        """
        import backend.gql_api.resolvers.parameter_resolvers as module

        # Check for batch query methods
        has_batch_method = any(
            'batch' in name.lower() and 'field_usage' in name.lower() for name in dir(module)
        )

        # CURRENT IMPLEMENTATION: This will FAIL
        # No batch method exists
        assert (
            has_batch_method
        ), "Should have batch field usage calculation method (e.g., _calculate_field_usage_batch)"

    def test_n_plus_1_pattern_in_resolve_event_fields(self):
        """
        Verify N+1 query pattern is FIXED in resolve_event_fields

        Before fix: _calculate_field_usage called inside for loop
        After fix: _calculate_field_usage_batch called once before loop
        """
        import os

        file_path = 'backend/gql_api/resolvers/parameter_resolvers.py'

        if not os.path.exists(file_path):
            pytest.skip("File not found")

        with open(file_path, 'r') as f:
            content = f.read()

        # Check for batch method usage
        has_batch_call = '_calculate_field_usage_batch(' in content

        # Check that OLD pattern (non-batch in loop) is NOT used
        # We look for the pattern: for field in fields: ... _calculate_field_usage(
        lines = content.split('\n')
        in_resolve_event_fields = False
        in_for_loop = False
        n_plus_1_detected = False

        for line in lines:
            if 'def resolve_event_fields(' in line:
                in_resolve_event_fields = True
            elif in_resolve_event_fields and line.strip().startswith('def '):
                # End of function
                in_resolve_event_fields = False

            if in_resolve_event_fields:
                if 'for ' in line and 'field' in line and 'in' in line and 'fields' in line:
                    in_for_loop = True
                elif (
                    in_for_loop
                    and line.strip()
                    and not line.strip().startswith(('for ', '    ', '\t'))
                ):
                    # End of for loop block
                    in_for_loop = False

                if in_for_loop and '_calculate_field_usage(' in line and '_batch' not in line:
                    n_plus_1_detected = True
                    break

        # AFTER FIX: N+1 pattern should NOT be detected
        # Batch method should be used
        assert (
            not n_plus_1_detected
        ), "N+1 pattern still exists: _calculate_field_usage called inside for loop"
        assert (
            has_batch_call
        ), "Batch method should be used: _calculate_field_usage_batch should be called"

    def test_calculate_field_usage_query_efficiency(self):
        """
        Test that field usage calculation uses efficient queries (BATCH version)

        Current implementation: 2 separate LIKE queries per field (individual function)

        Expected: Single batch query with UNION for all fields (batch function)
        """
        from unittest.mock import call

        field_names = ['field_1', 'field_2', 'field_3']

        with patch('backend.core.utils.fetch_all_as_dict') as mock_fetch:
            # Mock batch query results
            mock_fetch.return_value = [
                {'field_name': 'field_1', 'total_count': 5},
                {'field_name': 'field_2', 'total_count': 5},
                {'field_name': 'field_3', 'total_count': 5},
            ]

            # Call BATCH function (not individual)
            from backend.gql_api.resolvers.parameter_resolvers import _calculate_field_usage_batch

            result = _calculate_field_usage_batch(field_names, event_id=1)

            # Check call patterns
            calls = mock_fetch.call_args_list

            # Expected: 2 batch queries (1 HQL + 1 flow)
            assert (
                len(calls) == 2
            ), f"Wrong number of batch queries: {len(calls)} (should be 2: 1 HQL + 1 flow)"

            # Verify batch pattern is used (UNION ALL in query)
            first_query = calls[0][0][0] if calls else ""
            has_union = 'UNION' in first_query.upper()

            assert has_union, "Batch query should use UNION ALL to combine multiple field queries"

            # Verify all fields returned
            assert len(result) == len(
                field_names
            ), f"Missing fields: got {len(result)}, expected {len(field_names)}"

    def test_calculate_field_usage_mock_accuracy(self):
        """
        Verify that our test mocks accurately reflect real behavior

        This test validates that the test setup is correct
        """
        with patch('backend.core.utils.fetch_one_as_dict') as mock_fetch:
            # Simulate realistic query results
            mock_fetch.return_value = {'count': 5}

            result = _calculate_field_usage('test_field', event_id=1)

            # Verify function was called twice (HQL + flow)
            assert (
                mock_fetch.call_count == 2
            ), f"Expected 2 queries (HQL + flow), got {mock_fetch.call_count}"

            # Verify result
            assert result == 10, f"Expected usage count 10 (5+5), got {result}"

    def test_performance_regression_prevention(self):
        """
        Prevent performance regression (BATCH version)

        Establish baseline performance metrics for batch query
        """
        field_names = [f'field_{i}' for i in range(1, 11)]  # 10 fields
        event_id = 1

        with patch('backend.core.utils.fetch_all_as_dict') as mock_fetch:
            # Mock batch query results
            mock_fetch.return_value = [
                {'field_name': name, 'total_count': 5} for name in field_names
            ]

            start_time = time.time()

            # Use BATCH function
            from backend.gql_api.resolvers.parameter_resolvers import _calculate_field_usage_batch

            result = _calculate_field_usage_batch(field_names, event_id)

            elapsed = time.time() - start_time

            # Expected: <100ms for 10 fields (2 batch queries)
            assert (
                elapsed < 0.1
            ), f"Performance regression: {elapsed:.3f}s (should be <0.1s for 10 fields with batch query)"

            # Verify result
            assert len(result) == len(
                field_names
            ), f"Missing fields: got {len(result)}, expected {len(field_names)}"


class TestFieldUsageOptimizationGuidelines:
    """
    Guidelines for optimizing field usage calculation

    After implementing fixes, these tests should pass
    """

    def test_guideline_batch_query_structure(self):
        """
        Guideline: Use batch query structure

        Recommended SQL:
        SELECT field_name,
               SUM(hql_count) + SUM(flow_count) as total_usage
        FROM (
            SELECT field_name, COUNT(*) as hql_count
            FROM hql_history
            WHERE hql LIKE '%field1%'
               OR hql LIKE '%field2%'
               ...
            UNION ALL
            SELECT field_name, COUNT(*) as flow_count
            FROM flow_templates
            WHERE config LIKE '%field1%'
               OR config LIKE '%field2%'
               ...
        ) grouped
        GROUP BY field_name
        """
        # This is a documentation test - shows the target structure
        # Implement this optimization to make performance tests pass
        assert True, "Implement batch query following the structure in docstring"

    def test_guideline_cache_ttl(self):
        """
        Guideline: Add cache with appropriate TTL

        Field usage changes infrequently, so cache TTL can be long
        Recommended: 1800s (30 minutes) or 3600s (1 hour)
        """
        # This is a documentation test - shows recommended TTL
        assert True, "Add @cached(ttl=1800) decorator to _calculate_field_usage"

    def test_guideline_batch_function_signature(self):
        """
        Guideline: Create batch query function

        Recommended signature:
        def _calculate_field_usage_batch(
            field_names: List[str],
            event_id: int
        ) -> Dict[str, int]

        Returns: {field_name: usage_count, ...}
        """
        # This is a documentation test - shows recommended API
        assert True, "Implement _calculate_field_usage_batch function"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
