"""
Query Depth Limit Middleware

Limits the depth of GraphQL queries to prevent malicious queries.
"""

from graphql import GraphQLError
import logging

logger = logging.getLogger(__name__)


class DepthLimitMiddleware:
    """
    Query Depth Limit Middleware
    
    Prevents malicious deep queries that could cause performance issues.
    """
    
    def __init__(self, max_depth: int = 10):
        """
        Initialize middleware.
        
        Args:
            max_depth: Maximum allowed query depth
        """
        self.max_depth = max_depth
    
    def resolve(self, next, root, info, **args):
        """
        Check query depth before resolving.
        
        Args:
            next: Next resolver in chain
            root: Root object
            info: GraphQL resolve info
            **args: Resolver arguments
            
        Returns:
            Result from next resolver
            
        Raises:
            GraphQLError: If depth exceeds limit
        """
        depth = self._get_depth(info.path)
        
        if depth > self.max_depth:
            logger.warning(f"Query depth {depth} exceeds maximum {self.max_depth}")
            raise GraphQLError(
                f"Query depth {depth} exceeds maximum allowed depth of {self.max_depth}"
            )
        
        return next(root, info, **args)
    
    def _get_depth(self, path) -> int:
        """
        Calculate query depth from path.
        
        Args:
            path: GraphQL path object
            
        Returns:
            Depth as integer
        """
        depth = 0
        while path:
            depth += 1
            path = path.prev
        return depth
