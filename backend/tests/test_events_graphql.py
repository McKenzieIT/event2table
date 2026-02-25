"""
Events GraphQL Integration Tests

Tests for Events module GraphQL operations.
"""

import pytest
from backend.gql_api.schema import schema


class TestEventsQueries:
    """Test Events GraphQL queries"""

    def test_events_list_query(self):
        """Test events list query with game filter"""
        query = '''
        query GetEvents($gameGid: Int!, $limit: Int, $offset: Int) {
            events(gameGid: $gameGid, limit: $limit, offset: $offset) {
                id
                eventName
                eventNameCn
                categoryName
                paramCount
            }
        }
        '''

        result = schema.execute(query, variables={'gameGid': 10000147, 'limit': 10, 'offset': 0})
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'events' in result.data
        assert isinstance(result.data['events'], list)

    def test_single_event_query(self):
        """Test single event query"""
        query = '''
        query GetEvent($id: Int!) {
            event(id: $id) {
                id
                gameGid
                eventName
                eventNameCn
                categoryId
                categoryName
                sourceTable
                targetTable
                paramCount
            }
        }
        '''

        # First get an event ID from the list
        list_query = '''
        query GetEvents($gameGid: Int!) {
            events(gameGid: $gameGid, limit: 1) {
                id
            }
        }
        '''
        list_result = schema.execute(list_query, variables={'gameGid': 10000147})
        
        if list_result.data and list_result.data['events'] and len(list_result.data['events']) > 0:
            event_id = list_result.data['events'][0]['id']
            result = schema.execute(query, variables={'id': event_id})
            
            assert result.errors is None or len(result.errors) == 0
            assert result.data is not None
            assert 'event' in result.data

    def test_search_events_query(self):
        """Test events search query"""
        query = '''
        query SearchEvents($query: String!, $gameGid: Int) {
            searchEvents(query: $query, gameGid: $gameGid) {
                id
                eventName
                eventNameCn
                gameGid
            }
        }
        '''

        result = schema.execute(query, variables={'query': 'event', 'gameGid': 10000147})
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'searchEvents' in result.data
        assert isinstance(result.data['searchEvents'], list)

    def test_events_with_category_filter(self):
        """Test events query with category filter"""
        query = '''
        query GetEventsWithCategory($gameGid: Int!, $category: String) {
            events(gameGid: $gameGid, category: $category, limit: 10) {
                id
                eventName
                categoryName
            }
        }
        '''

        result = schema.execute(query, variables={'gameGid': 10000147, 'category': '埋点'})
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'events' in result.data


class TestEventsMutations:
    """Test Events GraphQL mutations"""

    def test_create_event_mutation_structure(self):
        """Test create event mutation structure"""
        query = '''
        mutation CreateEvent($gameGid: Int!, $eventName: String!, $eventNameCn: String!, 
                            $categoryId: Int!, $includeInCommonParams: Boolean) {
            createEvent(gameGid: $gameGid, eventName: $eventName, eventNameCn: $eventNameCn,
                       categoryId: $categoryId, includeInCommonParams: $includeInCommonParams) {
                ok
                event {
                    id
                    eventName
                    eventNameCn
                }
                errors
            }
        }
        '''

        # This will create a test event
        result = schema.execute(
            query,
            variables={
                'gameGid': 10000147,
                'eventName': 'test_event_graphql',
                'eventNameCn': '测试事件GraphQL',
                'categoryId': 1,
                'includeInCommonParams': False
            }
        )
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'createEvent' in result.data
        assert 'ok' in result.data['createEvent']

    def test_update_event_mutation_structure(self):
        """Test update event mutation structure"""
        query = '''
        mutation UpdateEvent($id: Int!, $eventNameCn: String, $categoryId: Int) {
            updateEvent(id: $id, eventNameCn: $eventNameCn, categoryId: $categoryId) {
                ok
                event {
                    id
                    eventNameCn
                }
                errors
            }
        }
        '''

        # Get an existing event first
        list_query = '''
        query GetEvents($gameGid: Int!) {
            events(gameGid: $gameGid, limit: 1) {
                id
            }
        }
        '''
        list_result = schema.execute(list_query, variables={'gameGid': 10000147})
        
        if list_result.data and list_result.data['events'] and len(list_result.data['events']) > 0:
            event_id = list_result.data['events'][0]['id']
            result = schema.execute(
                query,
                variables={
                    'id': event_id,
                    'eventNameCn': 'Updated Event Name'
                }
            )
            
            assert result.errors is None or len(result.errors) == 0
            assert result.data is not None
            assert 'updateEvent' in result.data

    def test_delete_event_mutation_structure(self):
        """Test delete event mutation structure"""
        query = '''
        mutation DeleteEvent($id: Int!) {
            deleteEvent(id: $id) {
                ok
                message
                errors
            }
        }
        '''

        # Test with a non-existent event
        result = schema.execute(query, variables={'id': 99999999})
        
        assert result.errors is None or len(result.errors) == 0
        assert result.data is not None
        assert 'deleteEvent' in result.data


class TestEventsPerformance:
    """Test Events query performance"""

    def test_events_query_performance(self):
        """Test events query performance"""
        import time

        query = '''
        query GetEvents($gameGid: Int!) {
            events(gameGid: $gameGid, limit: 50) {
                id
                eventName
                eventNameCn
                categoryName
                paramCount
            }
        }
        '''

        start = time.time()
        result = schema.execute(query, variables={'gameGid': 10000147})
        end = time.time()
        
        execution_time = end - start
        
        assert result.errors is None or len(result.errors) == 0
        # Should complete within 1 second
        assert execution_time < 1.0, f"Query took {execution_time:.2f}s"
        
        print(f"\nEvents query execution time: {execution_time:.3f}s")

    def test_event_search_performance(self):
        """Test event search performance"""
        import time

        query = '''
        query SearchEvents($query: String!) {
            searchEvents(query: $query) {
                id
                eventName
                eventNameCn
            }
        }
        '''

        start = time.time()
        result = schema.execute(query, variables={'query': 'event'})
        end = time.time()
        
        execution_time = end - start
        
        assert result.errors is None or len(result.errors) == 0
        # Should complete within 0.5 seconds
        assert execution_time < 0.5, f"Query took {execution_time:.2f}s"
        
        print(f"\nEvent search execution time: {execution_time:.3f}s")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
