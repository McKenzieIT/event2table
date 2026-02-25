"""
Subscription Error Handler Middleware

Enhanced error handling for GraphQL subscriptions.
Provides automatic reconnection, error logging, and graceful degradation.
"""

import logging
from typing import Any, Callable, Dict
from promise import Promise
from graphql import GraphQLError
from graphql.execution import ExecutionResult

logger = logging.getLogger(__name__)


class SubscriptionErrorHandler:
    """
    Subscription Error Handler
    
    Handles errors in GraphQL subscriptions with:
    - Automatic reconnection logic
    - Error logging and monitoring
    - Graceful error messages
    - Connection state management
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Initialize error handler.
        
        Args:
            max_retries: Maximum number of reconnection attempts
            retry_delay: Delay between retry attempts in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._connection_states = {}
        self._error_counts = {}
    
    def handle_subscription_error(
        self,
        error: Exception,
        subscription_id: str,
        operation_name: str = None
    ) -> Dict[str, Any]:
        """
        Handle a subscription error.
        
        Args:
            error: The exception that occurred
            subscription_id: Unique identifier for the subscription
            operation_name: Name of the GraphQL operation
            
        Returns:
            Error response dict with retry information
        """
        # Log the error
        logger.error(
            f"Subscription error in {operation_name or 'unknown'}: {error}",
            extra={
                'subscription_id': subscription_id,
                'operation_name': operation_name,
                'error_type': type(error).__name__,
            }
        )
        
        # Track error count
        if subscription_id not in self._error_counts:
            self._error_counts[subscription_id] = 0
        self._error_counts[subscription_id] += 1
        
        # Determine if we should retry
        should_retry = self._error_counts[subscription_id] < self.max_retries
        
        # Prepare error response
        error_response = {
            'error': True,
            'message': self._get_user_friendly_message(error),
            'should_retry': should_retry,
            'retry_after': self.retry_delay if should_retry else None,
            'retry_count': self._error_counts[subscription_id],
            'max_retries': self.max_retries,
        }
        
        return error_response
    
    def handle_connection_error(
        self,
        error: Exception,
        connection_id: str
    ) -> Dict[str, Any]:
        """
        Handle a WebSocket connection error.
        
        Args:
            error: The connection exception
            connection_id: Unique identifier for the connection
            
        Returns:
            Connection error response
        """
        logger.error(
            f"WebSocket connection error: {error}",
            extra={
                'connection_id': connection_id,
                'error_type': type(error).__name__,
            }
        )
        
        # Update connection state
        self._connection_states[connection_id] = {
            'status': 'error',
            'error': str(error),
            'retry_count': self._connection_states.get(connection_id, {}).get('retry_count', 0) + 1,
        }
        
        return {
            'error': True,
            'type': 'connection_error',
            'message': 'Connection lost. Attempting to reconnect...',
            'should_reconnect': True,
        }
    
    def _get_user_friendly_message(self, error: Exception) -> str:
        """
        Convert technical error to user-friendly message.
        
        Args:
            error: The exception
            
        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        
        if 'Timeout' in error_type:
            return "Request timed out. Please try again."
        elif 'Connection' in error_type:
            return "Connection lost. Reconnecting..."
        elif 'Permission' in error_type or 'Auth' in error_type:
            return "Authentication required. Please log in."
        elif 'NotFound' in error_type:
            return "The requested resource was not found."
        elif 'Validation' in error_type:
            return "Invalid request. Please check your input."
        else:
            return "An unexpected error occurred. Please try again."
    
    def reset_error_count(self, subscription_id: str):
        """Reset error count for a subscription"""
        if subscription_id in self._error_counts:
            del self._error_counts[subscription_id]
    
    def get_connection_state(self, connection_id: str) -> Dict[str, Any]:
        """Get current state of a connection"""
        return self._connection_states.get(connection_id, {
            'status': 'unknown',
            'error': None,
            'retry_count': 0,
        })


# Global error handler instance
_subscription_error_handler = None


def get_subscription_error_handler() -> SubscriptionErrorHandler:
    """Get or create subscription error handler instance"""
    global _subscription_error_handler
    if _subscription_error_handler is None:
        _subscription_error_handler = SubscriptionErrorHandler()
    return _subscription_error_handler
