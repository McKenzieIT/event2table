"""
GraphQL API Route

Provides GraphQL endpoint for the Event2Table application.
"""

from flask import Blueprint
from flask_graphql import GraphQLView
import logging

logger = logging.getLogger(__name__)

# Import schema
from backend.gql_api.schema import schema

# Import middleware
from backend.gql_api.middleware.depth_limit import DepthLimitMiddleware
from backend.gql_api.middleware.complexity_limit import ComplexityLimitMiddleware
from backend.gql_api.middleware.error_handling import ErrorHandlingMiddleware
from backend.gql_api.middleware.cache_middleware import cache_middleware, cache_invalidation_middleware

# Create blueprint
graphql_bp = Blueprint('graphql', __name__)

# GraphQL endpoint with middleware
graphql_bp.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True,  # Enable GraphiQL IDE
        middleware=[
            DepthLimitMiddleware(max_depth=10),
            ComplexityLimitMiddleware(max_complexity=1000),
            ErrorHandlingMiddleware(),
            cache_middleware,
            cache_invalidation_middleware,
        ]
    )
)

# Separate GraphiQL endpoint (optional)
graphql_bp.add_url_rule(
    '/graphiql',
    view_func=GraphQLView.as_view(
        'graphiql',
        schema=schema,
        graphiql=True
    )
)

logger.info("GraphQL API routes registered with cache middleware")
