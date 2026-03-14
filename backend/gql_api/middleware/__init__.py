"""
GraphQL Middleware

Middleware for GraphQL operations including:
- Query complexity limiting
- Query depth limiting
- Error handling
- Cache integration
"""

from .cache_middleware import (
    CacheInvalidationMiddleware,
    CacheMiddleware,
    cache_invalidation_middleware,
    cache_middleware,
)
from .complexity_limit import ComplexityLimitMiddleware
from .depth_limit import DepthLimitMiddleware
from .error_handling import ErrorHandlingMiddleware

__all__ = [
    'ComplexityLimitMiddleware',
    'DepthLimitMiddleware',
    'ErrorHandlingMiddleware',
    'CacheMiddleware',
    'CacheInvalidationMiddleware',
    'cache_middleware',
    'cache_invalidation_middleware',
]

__version__ = "1.0.0"
