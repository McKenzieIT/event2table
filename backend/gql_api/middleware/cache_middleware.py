"""
Cache Middleware for GraphQL

Integrates with the existing three-tier cache system.
"""

from graphql import GraphQLError
from typing import Any, Callable
import logging
import json
import hashlib

logger = logging.getLogger(__name__)


class CacheMiddleware:
    """
    GraphQL Cache Middleware

    Integrates with the existing three-tier cache system:
    - L1: In-memory hot cache
    - L2: Redis shared cache
    - L3: Database queries

    This middleware caches GraphQL query results at the resolver level.
    """

    def __init__(self, cache_timeout: int = 300):
        """
        Initialize cache middleware.

        Args:
            cache_timeout: Default cache timeout in seconds
        """
        self.cache_timeout = cache_timeout
        self._cache_enabled = True

    def resolve(self, next: Callable, root: Any, info, **args) -> Any:
        """
        Resolve with caching.

        Args:
            next: Next resolver in chain
            root: Root object
            info: GraphQL resolve info
            **args: Resolver arguments

        Returns:
            Result from cache or next resolver
        """
        # Only cache queries, not mutations
        operation_type = info.operation.operation.value if info.operation else 'query'

        if operation_type != 'query':
            return next(root, info, **args)

        # Get field name and parent type
        field_name = info.field_name
        parent_type = info.parent_type.name if info.parent_type else 'Query'

        # Build cache key
        cache_key = self._build_cache_key(parent_type, field_name, args)

        # Try to get from cache
        if self._cache_enabled:
            try:
                cached_result = self._get_from_cache(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {parent_type}.{field_name}")
                    return cached_result
            except Exception as e:
                logger.warning(f"Cache read error: {e}")

        # Execute resolver
        result = next(root, info, **args)

        # Cache the result
        if self._cache_enabled and result is not None:
            try:
                timeout = self._get_cache_timeout(parent_type, field_name)
                self._set_cache(cache_key, result, timeout)
                logger.debug(f"Cached {parent_type}.{field_name} for {timeout}s")
            except Exception as e:
                logger.warning(f"Cache write error: {e}")

        return result

    def _build_cache_key(self, parent_type: str, field_name: str, args: dict) -> str:
        """
        Build cache key from query info.

        Args:
            parent_type: Parent type name
            field_name: Field name
            args: Resolver arguments

        Returns:
            Cache key string
        """
        # Serialize args for cache key
        args_str = json.dumps(args, sort_keys=True, default=str)
        args_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]

        return f"gql:{parent_type}:{field_name}:{args_hash}"

    def _get_cache_timeout(self, parent_type: str, field_name: str) -> int:
        """
        Get cache timeout for a specific field.

        Args:
            parent_type: Parent type name
            field_name: Field name

        Returns:
            Cache timeout in seconds
        """
        # Different timeouts for different data types
        # Static data: longer cache
        static_fields = ['game', 'games', 'categories']
        if field_name in static_fields:
            return 3600  # 1 hour

        # Dynamic data: shorter cache
        dynamic_fields = ['events', 'parameters', 'searchGames', 'searchEvents']
        if field_name in dynamic_fields:
            return 300  # 5 minutes

        # Default cache
        return self.cache_timeout

    def _get_from_cache(self, key: str) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        try:
            from flask import current_app
            cache = getattr(current_app, 'cache', None)
            if cache:
                return cache.get(key)
        except Exception as e:
            logger.debug(f"Cache get error: {e}")

        return None

    def _set_cache(self, key: str, value: Any, timeout: int):
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds
        """
        try:
            from flask import current_app
            cache = getattr(current_app, 'cache', None)
            if cache:
                cache.set(key, value, timeout=timeout)
        except Exception as e:
            logger.debug(f"Cache set error: {e}")

    def invalidate(self, pattern: str = None):
        """
        Invalidate cache entries.

        Args:
            pattern: Cache key pattern to invalidate (optional)
        """
        try:
            from flask import current_app
            from backend.core.cache.cache_system import CacheInvalidator

            if pattern:
                # Invalidate specific pattern
                CacheInvalidator.invalidate_pattern(f"gql:{pattern}")
            else:
                # Invalidate all GraphQL cache
                CacheInvalidator.invalidate_pattern("gql:*")

            logger.info(f"Invalidated GraphQL cache: {pattern or 'all'}")

        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")


class CacheInvalidationMiddleware:
    """
    Cache Invalidation Middleware

    Automatically invalidates cache on mutations.
    """

    def resolve(self, next: Callable, root: Any, info, **args) -> Any:
        """
        Resolve and invalidate cache on mutations.

        Args:
            next: Next resolver in chain
            root: Root object
            info: GraphQL resolve info
            **args: Resolver arguments

        Returns:
            Result from next resolver
        """
        # Execute mutation
        result = next(root, info, **args)

        # Check if this is a mutation
        operation_type = info.operation.operation.value if info.operation else 'query'

        if operation_type == 'mutation':
            field_name = info.field_name

            # Invalidate relevant cache
            self._invalidate_for_mutation(field_name, args)

        return result

    def _invalidate_for_mutation(self, mutation_name: str, args: dict):
        """
        Invalidate cache based on mutation type.

        Args:
            mutation_name: Mutation field name
            args: Mutation arguments
        """
        try:
            from backend.core.cache.cache_system import CacheInvalidator

            # Game mutations
            if 'Game' in mutation_name:
                CacheInvalidator.invalidate_games_list()
                logger.debug(f"Invalidated games cache after {mutation_name}")

            # Event mutations
            elif 'Event' in mutation_name:
                game_gid = args.get('gameGid') or args.get('input', {}).get('gameGid')
                if game_gid:
                    CacheInvalidator.invalidate_events_list(game_gid)
                else:
                    CacheInvalidator.invalidate_pattern("events:*")
                logger.debug(f"Invalidated events cache after {mutation_name}")

            # Parameter mutations
            elif 'Parameter' in mutation_name:
                event_id = args.get('eventId') or args.get('input', {}).get('eventId')
                if event_id:
                    CacheInvalidator.invalidate_parameters(event_id)
                else:
                    CacheInvalidator.invalidate_pattern("parameters:*")
                logger.debug(f"Invalidated parameters cache after {mutation_name}")

        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")


# Global instances
cache_middleware = CacheMiddleware()
cache_invalidation_middleware = CacheInvalidationMiddleware()
