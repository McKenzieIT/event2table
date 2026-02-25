"""
Query Complexity Limit Middleware

Limits the complexity of GraphQL queries to prevent resource exhaustion.
"""

from graphql import GraphQLError
import logging

logger = logging.getLogger(__name__)


class ComplexityLimitMiddleware:
    """
    Query Complexity Limit Middleware
    
    Prevents complex queries that could exhaust server resources.
    """
    
    def __init__(self, max_complexity: int = 1000):
        """
        Initialize middleware.
        
        Args:
            max_complexity: Maximum allowed query complexity
        """
        self.max_complexity = max_complexity
    
    def resolve(self, next, root, info, **args):
        """
        Check query complexity before resolving.
        
        Args:
            next: Next resolver in chain
            root: Root object
            info: GraphQL resolve info
            **args: Resolver arguments
            
        Returns:
            Result from next resolver
            
        Raises:
            GraphQLError: If complexity exceeds limit
        """
        # Calculate complexity (simplified version)
        complexity = self._calculate_complexity(info.operation)
        
        if complexity > self.max_complexity:
            logger.warning(f"Query complexity {complexity} exceeds maximum {self.max_complexity}")
            raise GraphQLError(
                f"Query complexity {complexity} exceeds maximum allowed complexity of {self.max_complexity}"
            )
        
        return next(root, info, **args)
    
    def _calculate_complexity(self, operation) -> int:
        """
        Calculate query complexity.
        
        This is a simplified calculation that counts fields.
        A more sophisticated implementation would consider:
        - Field types (scalars vs objects)
        - List fields (higher cost)
        - Database operations
        
        Args:
            operation: GraphQL operation node
            
        Returns:
            Complexity score as integer
        """
        if not operation:
            return 0
        
        complexity = 0
        
        # Count fields in selection set
        if hasattr(operation, 'selection_set') and operation.selection_set:
            for selection in operation.selection_set.selections:
                complexity += self._count_fields(selection)
        
        return complexity
    
    def _count_fields(self, node) -> int:
        """
        Recursively count fields in a node.
        
        Args:
            node: GraphQL AST node
            
        Returns:
            Field count
        """
        count = 1  # Count this field
        
        if hasattr(node, 'selection_set') and node.selection_set:
            for selection in node.selection_set.selections:
                count += self._count_fields(selection)
        
        return count
