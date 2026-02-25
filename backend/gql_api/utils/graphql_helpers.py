"""
GraphQL Helper Utilities

Utility functions and helpers for GraphQL operations.
Provides common functionality for resolvers, mutations, and queries.
"""

import logging
from typing import Any, Dict, List, Optional, TypeVar, Callable
from functools import wraps
from promise import Promise

logger = logging.getLogger(__name__)

T = TypeVar('T')


def log_graphql_operation(operation_name: str):
    """
    Decorator to log GraphQL operations.
    
    Args:
        operation_name: Name of the GraphQL operation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(
                f"GraphQL operation started: {operation_name}",
                extra={'args': str(args)[:200], 'kwargs': str(kwargs)[:200]}
            )
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"GraphQL operation completed: {operation_name}")
                return result
            except Exception as e:
                logger.error(
                    f"GraphQL operation failed: {operation_name}",
                    extra={'error': str(e)}
                )
                raise
        
        return wrapper
    return decorator


def validate_input(data: Dict, required_fields: List[str]) -> Optional[str]:
    """
    Validate input data for required fields.
    
    Args:
        data: Input data dictionary
        required_fields: List of required field names
        
    Returns:
        Error message if validation fails, None otherwise
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            return f"Missing required field: {field}"
    return None


def paginate_results(
    items: List[T],
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        limit: Maximum number of items per page
        offset: Number of items to skip
        
    Returns:
        Dictionary with paginated results and metadata
    """
    total = len(items)
    paginated_items = items[offset:offset + limit]
    
    return {
        'items': paginated_items,
        'total': total,
        'limit': limit,
        'offset': offset,
        'has_more': offset + limit < total,
    }


def batch_load(loader_class, keys: List[Any]) -> Promise:
    """
    Generic batch loading function using DataLoader.
    
    Args:
        loader_class: DataLoader class to use
        keys: List of keys to load
        
    Returns:
        Promise resolving to list of results
    """
    loader = loader_class()
    return loader.load_many(keys)


def transform_to_camel_case(data: Dict) -> Dict:
    """
    Transform dictionary keys from snake_case to camelCase.
    
    Args:
        data: Dictionary with snake_case keys
        
    Returns:
        Dictionary with camelCase keys
    """
    def to_camel(snake_str: str) -> str:
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        camel_key = to_camel(key)
        
        if isinstance(value, dict):
            result[camel_key] = transform_to_camel_case(value)
        elif isinstance(value, list):
            result[camel_key] = [
                transform_to_camel_case(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[camel_key] = value
    
    return result


def transform_to_snake_case(data: Dict) -> Dict:
    """
    Transform dictionary keys from camelCase to snake_case.
    
    Args:
        data: Dictionary with camelCase keys
        
    Returns:
        Dictionary with snake_case keys
    """
    import re
    
    def to_snake(camel_str: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        snake_key = to_snake(key)
        
        if isinstance(value, dict):
            result[snake_key] = transform_to_snake_case(value)
        elif isinstance(value, list):
            result[snake_key] = [
                transform_to_snake_case(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[snake_key] = value
    
    return result


class GraphQLCache:
    """
    Simple in-memory cache for GraphQL operations.
    """
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        self._cache = {}
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        import time
        
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        
        # Check if expired
        if time.time() - timestamp > self._ttl:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        import time
        self._cache[key] = (value, time.time())
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()


# Global cache instance
_graphql_cache = GraphQLCache()


def get_graphql_cache() -> GraphQLCache:
    """Get global GraphQL cache instance"""
    return _graphql_cache
