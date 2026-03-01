"""
Integration Tests for Parameter Management GraphQL Resolvers

This module provides comprehensive integration tests for parameter management
GraphQL queries and mutations.

Test Database: data/test_database.db
Test GID Range: 90000000+

Author: Event2Table Development Team
Date: 2026-02-23
"""

import pytest
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from backend.gql_api.schema import schema
from backend.core.config.config import TEST_DB_PATH, get_db_path
from backend.core.database.database import get_db_connection


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="module")
def test_game_gid():
    """Provide test game GID (90000000+ range to avoid STAR001 conflict)"""
    return 90000001


@pytest.fixture(scope="module")
def test_event_id():
    """Provide test event ID"""
    return 1


@pytest.fixture(scope="module")
def test_parameter_id():
    """Provide test parameter ID"""
    return 1


@pytest.fixture(scope="function")
def setup_test_data(test_game_gid):
    """
    Setup test data in database before each test

    Creates:
    - Test game (GID: 90000001)
    - Test events
    - Test parameters
    """
    conn = get_db_connection(TEST_DB_PATH)
    cursor = conn.cursor()

    try:
        # Create test game
        cursor.execute("""
            INSERT OR IGNORE INTO games (gid, name, ods_db, description)
            VALUES (?, ?, ?, ?)
        """, (test_game_gid, "Test Game", "ieu_ods", "Test game for GraphQL integration"))

        # Create test events
        cursor.execute("""
            INSERT OR IGNORE INTO log_events
            (game_gid, event_code, event_name, event_name_cn, category)
            VALUES (?, ?, ?, ?, ?)
        """, (test_game_gid, "test_event", "Test Event", "测试事件", "test"))

        # Create test parameters
        cursor.execute("""
            INSERT OR IGNORE INTO event_params
            (event_id, param_name, param_name_cn, param_type, json_path, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (1, "role_id", "角色ID", "int", "$.roleId", 1))

        cursor.execute("""
            INSERT OR IGNORE INTO event_params
            (event_id, param_name, param_name_cn, param_type, json_path, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (1, "zone_id", "区域ID", "int", "$.zoneId", 1))

        conn.commit()
        print(f"✅ Test data setup complete: game_gid={test_game_gid}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Test data setup failed: {e}")
        raise
    finally:
        conn.close()


@pytest.fixture(scope="function")
def cleanup_test_data(test_game_gid):
    """Cleanup test data after each test"""
    yield
    conn = get_db_connection(TEST_DB_PATH)
    try:
        # Delete test data
        conn.execute(f"DELETE FROM event_params WHERE event_id IN (SELECT id FROM log_events WHERE game_gid = {test_game_gid})")
        conn.execute(f"DELETE FROM log_events WHERE game_gid = {test_game_gid}")
        conn.execute(f"DELETE FROM games WHERE gid = {test_game_gid}")
        conn.commit()
        print(f"✅ Test data cleanup complete: game_gid={test_game_gid}")
    except Exception as e:
        print(f"⚠️  Test data cleanup failed: {e}")
    finally:
        conn.close()


# ============================================================================
# QUERY RESOLVER TESTS
# ============================================================================

class TestParameterManagementQueries:
    """Test parameter management query resolvers"""

    def test_parameters_management_all_mode(
        self, setup_test_data, cleanup_test_data, test_game_gid
    ):
        """Test parameters_management query with mode='all'"""
        query = '''
            query {
                parametersManagement(gameGid: %d, mode: ALL) {
                    id
                    paramName
                    paramType
                    isCommon
                    gameGid
                }
            }
        ''' % test_game_gid

        result = schema.execute(query)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        parameters = result.data['parametersManagement']
        assert isinstance(parameters, list), "Should return a list"
        print(f"✅ parameters_management (ALL) returned {len(parameters)} parameters")

    def test_parameters_management_common_mode(
        self, setup_test_data, cleanup_test_data, test_game_gid
    ):
        """Test parameters_management query with mode='common'"""
        query = '''
            query {
                parametersManagement(gameGid: %d, mode: COMMON) {
                    id
                    paramName
                    paramType
                    isCommon
                }
            }
        ''' % test_game_gid

        result = schema.execute(query)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        parameters = result.data['parametersManagement']
        assert isinstance(parameters, list), "Should return a list"
        # All returned parameters should be common
        for param in parameters:
            assert param['isCommon'] is True, f"Parameter {param['paramName']} should be common"
        print(f"✅ parameters_management (COMMON) returned {len(parameters)} common parameters")

    def test_parameters_management_non_common_mode(
        self, setup_test_data, cleanup_test_data, test_game_gid
    ):
        """Test parameters_management query with mode='non_common'"""
        query = '''
            query {
                parametersManagement(gameGid: %d, mode: NON_COMMON) {
                    id
                    paramName
                    paramType
                    isCommon
                }
            }
        ''' % test_game_gid

        result = schema.execute(query)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        parameters = result.data['parametersManagement']
        assert isinstance(parameters, list), "Should return a list"
        # All returned parameters should be non-common
        for param in parameters:
            assert param['isCommon'] is False, f"Parameter {param['paramName']} should be non-common"
        print(f"✅ parameters_management (NON_COMMON) returned {len(parameters)} non-common parameters")

    def test_parameters_management_invalid_mode(
        self, setup_test_data, cleanup_test_data, test_game_gid
    ):
        """Test parameters_management query with invalid mode (should return error)"""
        query = '''
            query {
                parametersManagement(gameGid: %d, mode: INVALID) {
                    id
                    paramName
                }
            }
        ''' % test_game_gid

        result = schema.execute(query)

        # Should have an error for invalid mode
        assert result.errors is not None, "Should return error for invalid mode"
        print(f"✅ parameters_management (INVALID mode) correctly returned error")

    def test_common_parameters(
        self, setup_test_data, cleanup_test_data, test_game_gid
    ):
        """Test common_parameters query"""
        query = '''
            query {
                commonParameters(gameGid: %d, threshold: 0.5) {
                    paramName
                    paramType
                    occurrenceCount
                    totalEvents
                    isCommon
                    commonalityScore
                }
            }
        ''' % test_game_gid

        result = schema.execute(query)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        parameters = result.data['commonParameters']
        assert isinstance(parameters, list), "Should return a list"
        print(f"✅ common_parameters returned {len(parameters)} common parameters")

    def test_common_parameters_invalid_threshold(
        self, setup_test_data, cleanup_test_data, test_game_gid
    ):
        """Test common_parameters query with invalid threshold (should return error)"""
        query = '''
            query {
                commonParameters(gameGid: %d, threshold: 1.5) {
                    paramName
                }
            }
        ''' % test_game_gid

        result = schema.execute(query)

        # Should have an error for invalid threshold
        assert result.errors is not None, "Should return error for invalid threshold"
        print(f"✅ common_parameters (invalid threshold) correctly returned error")

    def test_parameter_changes(
        self, setup_test_data, cleanup_test_data, test_game_gid
    ):
        """Test parameter_changes query"""
        query = '''
            query {
                parameterChanges(gameGid: %d, limit: 10) {
                    id
                    paramName
                    changeType
                    changedAt
                }
            }
        ''' % test_game_gid

        result = schema.execute(query)

        # Note: parameter_changes table doesn't exist yet, so this returns empty list
        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        changes = result.data['parameterChanges']
        assert isinstance(changes, list), "Should return a list"
        print(f"✅ parameter_changes returned {len(changes)} changes (expected 0 - table not implemented)")

    def test_event_fields_all(
        self, setup_test_data, cleanup_test_data, test_event_id
    ):
        """Test event_fields query with field_type='all'"""
        query = '''
            query {
                eventFields(eventId: %d, fieldType: ALL) {
                    name
                    displayName
                    type
                    category
                    isCommon
                    dataType
                }
            }
        ''' % test_event_id

        result = schema.execute(query)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        fields = result.data['eventFields']
        assert isinstance(fields, list), "Should return a list"
        assert len(fields) > 0, "Should return at least base fields"

        # Check that base fields are included
        field_names = [f['name'] for f in fields]
        assert 'ds' in field_names, "Should include ds field"
        assert 'role_id' in field_names, "Should include role_id field"
        print(f"✅ event_fields (ALL) returned {len(fields)} fields")

    def test_event_fields_base(
        self, setup_test_data, cleanup_test_data, test_event_id
    ):
        """Test event_fields query with field_type='base'"""
        query = '''
            query {
                eventFields(eventId: %d, fieldType: BASE) {
                    name
                    displayName
                    type
                    category
                }
            }
        ''' % test_event_id

        result = schema.execute(query)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        fields = result.data['eventFields']
        assert isinstance(fields, list), "Should return a list"

        # All fields should be base type
        for field in fields:
            assert field['type'] == 'base', f"Field {field['name']} should be base type"
        print(f"✅ event_fields (BASE) returned {len(fields)} base fields")

    def test_event_fields_invalid_type(
        self, setup_test_data, cleanup_test_data, test_event_id
    ):
        """Test event_fields query with invalid field_type (should return error)"""
        query = '''
            query {
                eventFields(eventId: %d, fieldType: INVALID) {
                    name
                }
            }
        ''' % test_event_id

        result = schema.execute(query)

        # Should have an error for invalid field_type
        assert result.errors is not None, "Should return error for invalid field_type"
        print(f"✅ event_fields (invalid type) correctly returned error")


# ============================================================================
# MUTATION RESOLVER TESTS
# ============================================================================

class TestParameterManagementMutations:
    """Test parameter management mutation resolvers"""

    def test_change_parameter_type(
        self, setup_test_data, cleanup_test_data, test_parameter_id
    ):
        """Test change_parameter_type mutation"""
        mutation = '''
            mutation {
                changeParameterType(parameterId: %d, newType: STRING) {
                    success
                    message
                    parameter {
                        id
                        paramType
                    }
                }
            }
        ''' % test_parameter_id

        result = schema.execute(mutation)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        mutation_result = result.data['changeParameterType']
        assert mutation_result['success'] is True, "Mutation should succeed"
        assert mutation_result['parameter'] is not None, "Should return updated parameter"
        assert mutation_result['parameter']['paramType'] == 'string', "Type should be updated to string"
        print(f"✅ change_parameter_type succeeded")

    def test_change_parameter_type_invalid_parameter_id(
        self, setup_test_data, cleanup_test_data
    ):
        """Test change_parameter_type with invalid parameter_id (should return error)"""
        mutation = '''
            mutation {
                changeParameterType(parameterId: 999999, newType: STRING) {
                    success
                    message
                }
            }
        '''

        result = schema.execute(mutation)

        # Should succeed but with error message
        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        mutation_result = result.data['changeParameterType']
        assert mutation_result['success'] is False, "Mutation should fail for non-existent parameter"
        print(f"✅ change_parameter_type (invalid ID) correctly failed")

    def test_change_parameter_type_invalid_type(
        self, setup_test_data, cleanup_test_data, test_parameter_id
    ):
        """Test change_parameter_type with invalid type (should return error)"""
        mutation = '''
            mutation {
                changeParameterType(parameterId: %d, newType: INVALID_TYPE) {
                    success
                    message
                }
            }
        ''' % test_parameter_id

        result = schema.execute(mutation)

        # Should have an error for invalid type
        assert result.errors is not None, "Should return error for invalid type"
        print(f"✅ change_parameter_type (invalid type) correctly returned error")

    def test_auto_sync_common_parameters(
        self, setup_test_data, cleanup_test_data, test_game_gid
    ):
        """Test auto_sync_common_parameters mutation"""
        mutation = '''
            mutation {
                autoSyncCommonParameters(gameGid: %d, forceRecalculate: false) {
                    success
                    message
                    result {
                        gameGid
                        totalParameters
                        commonParametersCount
                        parametersAdded
                        parametersRemoved
                    }
                }
            }
        ''' % test_game_gid

        result = schema.execute(mutation)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        mutation_result = result.data['autoSyncCommonParameters']
        assert mutation_result['success'] is True, "Mutation should succeed"
        assert mutation_result['result'] is not None, "Should return sync result"
        print(f"✅ auto_sync_common_parameters succeeded")

    def test_auto_sync_common_parameters_invalid_game_gid(
        self, setup_test_data, cleanup_test_data
    ):
        """Test auto_sync_common_parameters with invalid game_gid (should return error)"""
        mutation = '''
            mutation {
                autoSyncCommonParameters(gameGid: -1, forceRecalculate: false) {
                    success
                    message
                }
            }
        '''

        result = schema.execute(mutation)

        # Should have an error for invalid game_gid
        assert result.errors is not None, "Should return error for invalid game_gid"
        print(f"✅ auto_sync_common_parameters (invalid GID) correctly returned error")

    def test_batch_add_fields_to_canvas(
        self, setup_test_data, cleanup_test_data, test_event_id
    ):
        """Test batch_add_fields_to_canvas mutation"""
        mutation = '''
            mutation {
                batchAddFieldsToCanvas(eventId: %d, fieldType: ALL) {
                    success
                    message
                    result {
                        totalCount
                        successCount
                        failedCount
                    }
                }
            }
        ''' % test_event_id

        result = schema.execute(mutation)

        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data is not None, "No data returned"

        mutation_result = result.data['batchAddFieldsToCanvas']
        assert mutation_result['success'] is True, "Mutation should succeed"
        assert mutation_result['result'] is not None, "Should return batch result"
        print(f"✅ batch_add_fields_to_canvas succeeded")

    def test_batch_add_fields_to_canvas_invalid_event_id(
        self, setup_test_data, cleanup_test_data
    ):
        """Test batch_add_fields_to_canvas with invalid event_id (should return error)"""
        mutation = '''
            mutation {
                batchAddFieldsToCanvas(eventId: -1, fieldType: ALL) {
                    success
                    message
                }
            }
        '''

        result = schema.execute(mutation)

        # Should have an error for invalid event_id
        assert result.errors is not None, "Should return error for invalid event_id"
        print(f"✅ batch_add_fields_to_canvas (invalid event_id) correctly returned error")


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
