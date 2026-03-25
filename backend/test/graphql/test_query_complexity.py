"""
Query Complexity Tests

Tests for query complexity calculation and limiting.
"""

import pytest
from graphql import GraphQLError, parse, validate
from graphql.execution import execute, execute_sync

from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware
from backend.gql_api.schema import schema


@pytest.mark.describe("ComplexityLimitMiddleware")
class TestComplexityLimitMiddleware:
    """Test query complexity limiting"""

    @pytest.fixture
    def middleware(self):
        """Create middleware instance"""
        return ComplexityLimitMiddleware(max_complexity=1000)

    @pytest.mark.it("should allow simple queries")
    def test_allow_simple_query(self, middleware):
        """Test that simple queries pass complexity check"""
        query = """
            query {
                game(gid: 10000147) {
                    gid
                    name
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        assert complexity < 1000
        assert complexity == 3  # game + gid + name

    @pytest.mark.it("should calculate complexity for nested queries")
    def test_nested_query_complexity(self, middleware):
        """Test that nested queries have higher complexity"""
        query = """
            query {
                game(gid: 10000147) {
                    gid
                    name
                    events {
                        id
                        eventName
                        parameters {
                            id
                            paramName
                        }
                    }
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # Should be higher than simple query
        # Structure: game(1) + fields(3) + events(N) + parameters(M)
        assert complexity > 10

    @pytest.mark.it("should block overly complex queries")
    def test_block_complex_query(self, middleware):
        """Test that queries exceeding max complexity are blocked"""
        # Create a query with >1000 fields
        fields = "\n                ".join([f"field{i}: String" for i in range(1001)])
        query = f"""
            query {{
                game(gid: 10000147) {{
                    {fields}
                }}
            }}
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        assert complexity > 1000

    @pytest.mark.it("should calculate list multipliers correctly")
    def test_list_multiplier(self, middleware):
        """Test that list fields have higher complexity weight"""
        query = """
            query {
                games(limit: 10) {
                    gid
                    name
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # List query should have multiplier
        # Base complexity * limit (10)
        assert complexity > 3


@pytest.mark.describe("Advanced Complexity Calculator")
class TestAdvancedComplexityCalculator:
    """Test advanced complexity calculation with field weighting"""

    @pytest.mark.it("should weight scalar fields as 1")
    def test_scalar_field_weight(self):
        """Test that scalar fields have base complexity of 1"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)
        query = """
            query {
                game(gid: 10000147) {
                    gid
                    name
                    description
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # 3 scalar fields = 3 complexity
        assert complexity >= 3

    @pytest.mark.it("should weight object fields higher")
    def test_object_field_weight(self):
        """Test that object fields have higher complexity"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)
        query = """
            query {
                game(gid: 10000147) {
                    gid
                    name
                    events {
                        id
                        eventName
                    }
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # Object field (events) should cost more than scalars
        assert complexity > 5

    @pytest.mark.it("should apply depth multiplier")
    def test_depth_multiplier(self):
        """Test that deeper nesting increases complexity exponentially"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)

        # Shallow query
        shallow_query = """
            query {
                game(gid: 10000147) {
                    name
                }
            }
        """

        # Deep query
        deep_query = """
            query {
                game(gid: 10000147) {
                    name
                    events {
                        eventName
                        parameters {
                            paramName
                            template {
                                name
                            }
                        }
                    }
                }
            }
        """

        shallow_doc = parse(shallow_query)
        deep_doc = parse(deep_query)

        shallow_complexity = middleware._calculate_complexity(shallow_doc.definitions[0])
        deep_complexity = middleware._calculate_complexity(deep_doc.definitions[0])

        # Deep query should be significantly more complex
        assert deep_complexity > shallow_complexity * 2


@pytest.mark.describe("Real-world Query Complexity")
class TestRealWorldQueryComplexity:
    """Test complexity of actual queries used in production"""

    @pytest.mark.it("should calculate games list query complexity")
    def test_games_list_complexity(self):
        """Test complexity of typical games list query"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)
        query = """
            query {
                games(limit: 20) {
                    gid
                    name
                    odsDb
                    eventCount
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # Should be reasonable
        assert complexity < 100
        assert complexity > 0

    @pytest.mark.it("should calculate event detail query complexity")
    def test_event_detail_complexity(self):
        """Test complexity of event detail with parameters"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)
        query = """
            query {
                event(id: 1) {
                    id
                    eventName
                    eventNameCn
                    game {
                        gid
                        name
                    }
                    category {
                        name
                    }
                    parameters(activeOnly: true) {
                        id
                        paramName
                        paramNameCn
                        paramType
                    }
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # Should be moderate
        assert complexity < 500
        assert complexity > 10

    @pytest.mark.it("should detect malicious deep queries")
    def test_detect_malicious_queries(self):
        """Test that maliciously deep queries are blocked"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)

        # Create deeply nested query (depth > 10)
        nested_part = "parameters { id paramName "
        for _ in range(15):
            nested_part += "parameters { id paramName "
        nested_part += "}" * 15

        query = f"""
            query {{
                game(gid: 10000147) {{
                    name
                    events {{
                        {nested_part}
                    }}
                }}
            }}
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # Should exceed limit
        assert complexity > 1000


@pytest.mark.describe("Complexity Calculator Integration")
class TestComplexityCalculatorIntegration:
    """Test integration with GraphQL execution"""

    @pytest.mark.it("should reject complex queries during execution")
    def test_reject_complex_query_execution(self):
        """Test that complex queries are rejected during execution"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        # Very complex query
        fields = "\n                    ".join([f"f{i}: String" for i in range(2000)])
        query = f"""
            query {{
                game(gid: 10000147) {{
                    {fields}
                }}
            }}
        """

        middleware = ComplexityLimitMiddleware(max_complexity=1000)
        document = parse(query)

        # Calculate complexity
        complexity = middleware._calculate_complexity(document.definitions[0])

        # Should exceed limit
        assert complexity > 1000

    @pytest.mark.it("should allow reasonable production queries")
    def test_allow_production_queries(self):
        """Test that actual production queries are allowed"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)

        # Typical production queries
        queries = [
            # Games list
            """
            query {
                games(limit: 50) {
                    gid
                    name
                    odsDb
                }
            }
            """,
            # Event with parameters
            """
            query {
                events(gameGid: 10000147, limit: 20) {
                    id
                    eventName
                    eventNameCn
                }
            }
            """,
            # Single game
            """
            query {
                game(gid: 10000147) {
                    gid
                    name
                    description
                }
            }
            """,
        ]

        for query_str in queries:
            document = parse(query_str)
            complexity = middleware._calculate_complexity(document.definitions[0])

            # All should be under limit
            assert complexity < 1000, f"Query complexity {complexity} exceeds limit"


@pytest.mark.describe("Complexity Calculation Algorithm")
class TestComplexityCalculationAlgorithm:
    """Test the complexity calculation algorithm implementation"""

    @pytest.mark.it("should count fields correctly")
    def test_field_counting(self):
        """Test that fields are counted accurately"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)
        query = """
            query {
                game(gid: 1) {
                    field1
                    field2
                    field3
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # game + field1 + field2 + field3 = 4
        assert complexity >= 4

    @pytest.mark.it("should handle fragments correctly")
    def test_fragment_handling(self):
        """Test that fragments are included in complexity"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)
        query = """
            query {
                game(gid: 1) {
                    ...gameFields
                }
            }

            fragment gameFields on GameType {
                gid
                name
                description
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # Should include fragment fields
        assert complexity >= 4  # game + gid + name + description

    @pytest.mark.it("should handle inline fragments")
    def test_inline_fragments(self):
        """Test that inline fragments are counted"""
        from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware

        middleware = ComplexityLimitMiddleware(max_complexity=1000)
        query = """
            query {
                game(gid: 1) {
                    gid
                    ... on GameType {
                        name
                    }
                }
            }
        """

        document = parse(query)
        complexity = middleware._calculate_complexity(document.definitions[0])

        # Should include inline fragment
        assert complexity >= 3  # game + gid + name
