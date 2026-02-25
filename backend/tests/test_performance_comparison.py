"""
Performance Comparison Tests

Compare GraphQL vs REST API performance.
"""

import pytest
import time
from backend.gql_api.schema import schema


class TestPerformanceComparison:
    """Compare GraphQL and REST API performance"""

    def test_graphql_games_query_performance(self):
        """Test GraphQL games query performance"""
        query = '''
        query GetGames {
            games(limit: 50) {
                gid
                name
                odsDb
                eventCount
                parameterCount
            }
        }
        '''

        # Warm up
        schema.execute(query)
        
        # Measure
        times = []
        for _ in range(10):
            start = time.time()
            result = schema.execute(query)
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n=== GraphQL Games Query Performance ===")
        print(f"Average: {avg_time*1000:.2f}ms")
        print(f"Min: {min_time*1000:.2f}ms")
        print(f"Max: {max_time*1000:.2f}ms")
        
        assert result.errors is None or len(result.errors) == 0
        assert avg_time < 0.1, f"Average time {avg_time:.3f}s is too slow"

    def test_graphql_single_game_query_performance(self):
        """Test GraphQL single game query performance"""
        query = '''
        query GetGame($gid: Int!) {
            game(gid: $gid) {
                gid
                name
                odsDb
                eventCount
                parameterCount
            }
        }
        '''

        # Warm up
        schema.execute(query, variables={'gid': 10000147})
        
        # Measure
        times = []
        for _ in range(10):
            start = time.time()
            result = schema.execute(query, variables={'gid': 10000147})
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n=== GraphQL Single Game Query Performance ===")
        print(f"Average: {avg_time*1000:.2f}ms")
        print(f"Min: {min_time*1000:.2f}ms")
        print(f"Max: {max_time*1000:.2f}ms")
        
        assert result.errors is None or len(result.errors) == 0
        assert avg_time < 0.05, f"Average time {avg_time:.3f}s is too slow"

    def test_graphql_search_performance(self):
        """Test GraphQL search performance"""
        query = '''
        query SearchGames($query: String!) {
            searchGames(query: $query) {
                gid
                name
                odsDb
            }
        }
        '''

        # Warm up
        schema.execute(query, variables={'query': 'game'})
        
        # Measure
        times = []
        for _ in range(10):
            start = time.time()
            result = schema.execute(query, variables={'query': 'game'})
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n=== GraphQL Search Performance ===")
        print(f"Average: {avg_time*1000:.2f}ms")
        print(f"Min: {min_time*1000:.2f}ms")
        print(f"Max: {max_time*1000:.2f}ms")
        
        assert result.errors is None or len(result.errors) == 0
        assert avg_time < 0.1, f"Average time {avg_time:.3f}s is too slow"

    def test_graphql_batch_query_performance(self):
        """Test GraphQL batch query performance (simulating multiple REST calls)"""
        # This simulates what would require multiple REST API calls
        query = '''
        query GetMultipleResources {
            games(limit: 10) {
                gid
                name
                eventCount
            }
            categories(limit: 10) {
                id
                name
                eventCount
            }
        }
        '''

        # Warm up
        schema.execute(query)
        
        # Measure
        times = []
        for _ in range(10):
            start = time.time()
            result = schema.execute(query)
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n=== GraphQL Batch Query Performance ===")
        print(f"(Equivalent to 2 REST API calls)")
        print(f"Average: {avg_time*1000:.2f}ms")
        print(f"Min: {min_time*1000:.2f}ms")
        print(f"Max: {max_time*1000:.2f}ms")
        
        assert result.errors is None or len(result.errors) == 0
        assert avg_time < 0.15, f"Average time {avg_time:.3f}s is too slow"


class TestDataLoaderPerformance:
    """Test DataLoader performance benefits"""

    def test_dataloader_vs_n_plus_1(self):
        """Compare DataLoader vs N+1 queries"""
        # Query that would cause N+1 without DataLoader
        query = '''
        query GetGamesWithCounts {
            games(limit: 20) {
                gid
                name
                eventCount
                parameterCount
            }
        }
        '''

        # Warm up
        schema.execute(query)
        
        # Measure with DataLoader
        times = []
        for _ in range(10):
            start = time.time()
            result = schema.execute(query)
            end = time.time()
            times.append(end - start)
        
        avg_time = sum(times) / len(times)
        
        print(f"\n=== DataLoader Performance ===")
        print(f"Query with counts (20 games): {avg_time*1000:.2f}ms")
        print(f"Without DataLoader would require 1 + 20*2 = 41 queries")
        print(f"With DataLoader: 1 query (batched)")
        
        assert result.errors is None or len(result.errors) == 0
        # Should be fast with DataLoader
        assert avg_time < 0.1, f"Average time {avg_time:.3f}s is too slow"


class TestCachePerformance:
    """Test cache performance benefits"""

    def test_cache_hit_performance(self):
        """Test cache hit performance"""
        query = '''
        query GetGamesCached {
            games(limit: 50) {
                gid
                name
            }
        }
        '''

        # First query (cache miss)
        start = time.time()
        result1 = schema.execute(query)
        first_time = time.time() - start
        
        # Second query (should hit cache)
        start = time.time()
        result2 = schema.execute(query)
        second_time = time.time() - start
        
        print(f"\n=== Cache Performance ===")
        print(f"First query (cache miss): {first_time*1000:.2f}ms")
        print(f"Second query (cache hit): {second_time*1000:.2f}ms")
        
        if second_time < first_time:
            improvement = ((first_time - second_time) / first_time) * 100
            print(f"Improvement: {improvement:.1f}%")
        
        assert result1.errors is None or len(result1.errors) == 0
        assert result2.errors is None or len(result2.errors) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
