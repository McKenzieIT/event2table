"""
Batch Operations GraphQL Integration Tests

Tests for batch operation mutations (Games, Events, Flows).
"""

import pytest
from backend.gql_api.schema import schema


class TestBatchGamesOperations:
    """Test Games batch operations"""

    def test_batch_delete_games_mutation_structure(self):
        """Test batch delete games mutation structure"""
        query = '''
        mutation BatchDeleteGames($ids: [Int!]!) {
            batchDeleteGames(ids: $ids) {
                ok
                deletedCount
                errors
            }
        }
        '''

        # Use non-existent IDs for structure testing
        result = schema.execute(
            query,
            variables={'ids': [99999990, 99999991, 99999992]}
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'batchDeleteGames' in result.data
        assert 'ok' in result.data['batchDeleteGames']
        assert 'deletedCount' in result.data['batchDeleteGames']
        assert 'errors' in result.data['batchDeleteGames']

    def test_batch_update_games_mutation_structure(self):
        """Test batch update games mutation structure"""
        query = '''
        mutation BatchUpdateGames($updates: [GameUpdateInput!]!) {
            batchUpdateGames(updates: $updates) {
                ok
                updatedCount
                errors
            }
        }
        '''

        # Use non-existent IDs for structure testing
        result = schema.execute(
            query,
            variables={
                'updates': [
                    {'id': 99999990, 'name': 'Updated Game 1'},
                    {'id': 99999991, 'name': 'Updated Game 2'}
                ]
            }
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'batchUpdateGames' in result.data
        assert 'ok' in result.data['batchUpdateGames']
        assert 'updatedCount' in result.data['batchUpdateGames']
        assert 'errors' in result.data['batchUpdateGames']

    def test_batch_create_games_mutation_structure(self):
        """Test batch create games mutation structure"""
        query = '''
        mutation BatchCreateGames($games: [GameInput!]!) {
            batchCreateGames(games: $games) {
                ok
                games {
                    gid
                    name
                    odsDb
                }
                createdCount
                errors
            }
        }
        '''

        result = schema.execute(
            query,
            variables={
                'games': [
                    {'gid': 99999990, 'name': 'Test Game 1', 'odsDb': 'test_db_1'},
                    {'gid': 99999991, 'name': 'Test Game 2', 'odsDb': 'test_db_2'}
                ]
            }
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'batchCreateGames' in result.data
        assert 'ok' in result.data['batchCreateGames']
        assert 'createdCount' in result.data['batchCreateGames']


class TestBatchEventsOperations:
    """Test Events batch operations"""

    def test_batch_delete_events_mutation_structure(self):
        """Test batch delete events mutation structure"""
        query = '''
        mutation BatchDeleteEvents($ids: [Int!]!) {
            batchDeleteEvents(ids: $ids) {
                ok
                deletedCount
                errors
            }
        }
        '''

        # Use non-existent IDs for structure testing
        result = schema.execute(
            query,
            variables={'ids': [99999990, 99999991, 99999992]}
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'batchDeleteEvents' in result.data
        assert 'ok' in result.data['batchDeleteEvents']
        assert 'deletedCount' in result.data['batchDeleteEvents']
        assert 'errors' in result.data['batchDeleteEvents']

    def test_batch_update_events_mutation_structure(self):
        """Test batch update events mutation structure"""
        query = '''
        mutation BatchUpdateEvents($ids: [Int!]!, $updates: EventUpdateInput!) {
            batchUpdateEvents(ids: $ids, updates: $updates) {
                ok
                updatedCount
                errors
            }
        }
        '''

        # Use non-existent IDs for structure testing
        result = schema.execute(
            query,
            variables={
                'ids': [99999990, 99999991],
                'updates': {
                    'eventName': 'Updated Event Name',
                    'eventNameCn': '更新的事件名称'
                }
            }
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'batchUpdateEvents' in result.data
        assert 'ok' in result.data['batchUpdateEvents']
        assert 'updatedCount' in result.data['batchUpdateEvents']
        assert 'errors' in result.data['batchUpdateEvents']

    def test_batch_update_events_with_category(self):
        """Test batch update events with category_id"""
        query = '''
        mutation BatchUpdateEvents($ids: [Int!]!, $updates: EventUpdateInput!) {
            batchUpdateEvents(ids: $ids, updates: $updates) {
                ok
                updatedCount
                errors
            }
        }
        '''

        result = schema.execute(
            query,
            variables={
                'ids': [99999990],
                'updates': {
                    'categoryId': 1,
                    'includeInCommonParams': 1
                }
            }
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None


class TestBatchFlowsOperations:
    """Test Flows batch operations"""

    def test_batch_delete_flows_mutation_structure(self):
        """Test batch delete flows mutation structure"""
        query = '''
        mutation BatchDeleteFlows($ids: [Int!]!) {
            batchDeleteFlows(ids: $ids) {
                ok
                deletedCount
                errors
            }
        }
        '''

        # Use non-existent IDs for structure testing
        result = schema.execute(
            query,
            variables={'ids': [99999990, 99999991, 99999992]}
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'batchDeleteFlows' in result.data
        assert 'ok' in result.data['batchDeleteFlows']
        assert 'deletedCount' in result.data['batchDeleteFlows']
        assert 'errors' in result.data['batchDeleteFlows']

    def test_batch_update_flows_mutation_structure(self):
        """Test batch update flows mutation structure"""
        query = '''
        mutation BatchUpdateFlows($ids: [Int!]!, $updates: FlowUpdateInput!) {
            batchUpdateFlows(ids: $ids, updates: $updates) {
                ok
                updatedCount
                errors
            }
        }
        '''

        # Use non-existent IDs for structure testing
        result = schema.execute(
            query,
            variables={
                'ids': [99999990, 99999991],
                'updates': {
                    'name': 'Updated Flow Name',
                    'description': 'Updated flow description',
                    'isActive': 1
                }
            }
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'batchUpdateFlows' in result.data
        assert 'ok' in result.data['batchUpdateFlows']
        assert 'updatedCount' in result.data['batchUpdateFlows']
        assert 'errors' in result.data['batchUpdateFlows']


class TestBatchOperationsValidation:
    """Test batch operations input validation"""

    def test_batch_update_events_empty_name_validation(self):
        """Test that empty event_name is rejected"""
        query = '''
        mutation BatchUpdateEvents($ids: [Int!]!, $updates: EventUpdateInput!) {
            batchUpdateEvents(ids: $ids, updates: $updates) {
                ok
                updatedCount
                errors
            }
        }
        '''

        result = schema.execute(
            query,
            variables={
                'ids': [1],
                'updates': {
                    'eventName': ''  # Empty name should be rejected
                }
            }
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        # Should fail validation
        assert result.data['batchUpdateEvents']['ok'] is False
        assert result.data['batchUpdateEvents']['updatedCount'] == 0
        assert result.data['batchUpdateEvents']['errors'] is not None

    def test_batch_update_events_long_name_validation(self):
        """Test that event_name exceeding max length is rejected"""
        query = '''
        mutation BatchUpdateEvents($ids: [Int!]!, $updates: EventUpdateInput!) {
            batchUpdateEvents(ids: $ids, updates: $updates) {
                ok
                updatedCount
                errors
            }
        }
        '''

        result = schema.execute(
            query,
            variables={
                'ids': [1],
                'updates': {
                    'eventName': 'a' * 201  # Exceeds 200 character limit
                }
            }
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        # Should fail validation
        assert result.data['batchUpdateEvents']['ok'] is False
        assert result.data['batchUpdateEvents']['updatedCount'] == 0
        assert result.data['batchUpdateEvents']['errors'] is not None

    def test_batch_update_flows_empty_name_validation(self):
        """Test that empty flow name is rejected"""
        query = '''
        mutation BatchUpdateFlows($ids: [Int!]!, $updates: FlowUpdateInput!) {
            batchUpdateFlows(ids: $ids, updates: $updates) {
                ok
                updatedCount
                errors
            }
        }
        '''

        result = schema.execute(
            query,
            variables={
                'ids': [1],
                'updates': {
                    'name': ''  # Empty name should be rejected
                }
            }
        )

        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        # Should fail validation
        assert result.data['batchUpdateFlows']['ok'] is False
        assert result.data['batchUpdateFlows']['updatedCount'] == 0
        assert result.data['batchUpdateFlows']['errors'] is not None


class TestBatchOperationTypes:
    """Test batch operation type definitions"""

    def test_batch_operation_error_type_exists(self):
        """Test that BatchOperationErrorType is defined"""
        from backend.gql_api.types.batch_operation_type import BatchOperationErrorType
        
        error = BatchOperationErrorType(id=1, error="Test error")
        assert error.id == 1
        assert error.error == "Test error"

    def test_batch_operation_result_type_exists(self):
        """Test that BatchOperationResultType is defined"""
        from backend.gql_api.types.batch_operation_type import BatchOperationResultType
        
        result = BatchOperationResultType.success_result(affected_count=5)
        assert result.success is True
        assert result.affected_count == 5
        assert result.failed_count == 0
        assert result.errors == []

    def test_batch_operation_result_partial_success(self):
        """Test BatchOperationResultType partial success"""
        from backend.gql_api.types.batch_operation_type import BatchOperationResultType
        
        errors = [{'id': 1, 'error': 'Failed to delete'}]
        result = BatchOperationResultType.partial_success_result(
            affected_count=3,
            failed_count=1,
            errors=errors
        )
        assert result.success is False
        assert result.affected_count == 3
        assert result.failed_count == 1
        assert len(result.errors) == 1
