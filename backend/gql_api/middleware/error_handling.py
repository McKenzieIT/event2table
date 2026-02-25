"""
Error Handling Middleware

Provides unified error handling for GraphQL operations.
"""

from graphql import GraphQLError
import logging
import traceback

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware:
    """
    Error Handling Middleware
    
    Catches exceptions and returns user-friendly error messages.
    Logs detailed error information for debugging.
    """
    
    def resolve(self, next, root, info, **args):
        """
        Wrap resolver with error handling.
        
        Args:
            next: Next resolver in chain
            root: Root object
            info: GraphQL resolve info
            **args: Resolver arguments
            
        Returns:
            Result from next resolver or error
        """
        try:
            return next(root, info, **args)
        
        except GraphQLError:
            # Re-raise GraphQL errors as-is
            raise
        
        except ValueError as e:
            # Validation errors
            logger.warning(f"Validation error in {info.field_name}: {e}")
            raise GraphQLError(str(e))
        
        except Exception as e:
            # Unexpected errors
            logger.error(
                f"Unexpected error in {info.field_name}: {e}\n"
                f"Traceback: {traceback.format_exc()}",
                exc_info=True
            )
            
            # Return generic error message to client
            # (Don't expose internal details)
            raise GraphQLError(
                "An unexpected error occurred. Please try again later."
            )
