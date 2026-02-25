#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Unit of Work Pattern Implementation

This module provides a production-ready Unit of Work implementation with:
- Automatic transaction management (BEGIN/COMMIT/ROLLBACK)
- Domain event publishing after successful commit
- Operation tracking for audit logs
- Repository lazy loading for performance
- Context manager support for clean resource handling
- Integration with existing Repository implementations

Architecture:
    UnitOfWork manages transaction boundaries
    → Repositories handle data access
    → Domain events published after commit
    → Cache invalidation triggered by events
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps

from backend.core.database.database import get_db_connection
from backend.core.config.config import get_db_path

logger = logging.getLogger(__name__)


@dataclass
class TransactionContext:
    """Transaction context for tracking operations and metadata"""
    transaction_id: str
    started_at: datetime
    operations: List[Dict[str, Any]] = field(default_factory=list)
    is_committed: bool = False
    is_rolled_back: bool = False

    def add_operation(self, operation: str, metadata: Optional[Dict] = None):
        """Track an operation within this transaction"""
        self.operations.append({
            'operation': operation,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        })


class UnitOfWork:
    """
    Enhanced Unit of Work for Transaction and Domain Event Management

    This implementation provides:
    1. **Transaction Safety**: Automatic BEGIN/COMMIT/ROLLBACK
    2. **Domain Events**: Events published only after successful commit
    3. **Repository Lazy Loading**: Repositories created on-demand
    4. **Operation Tracking**: Audit log for all operations
    5. **Context Manager**: Clean resource handling with automatic cleanup

    Usage Examples:

        **As Context Manager (Recommended)**:
        ```python
        with UnitOfWork() as uow:
            param = uow.parameters.find_by_id(123)
            param.change_type('int')
            uow.parameters.save(param)

            # Register domain event
            uow.register_event(ParameterTypeChanged(...))

            # Track operation
            uow.add_operation("Updated parameter type")

            # Auto-commit on success, auto-rollback on exception
        ```

        **Manual Mode**:
        ```python
        uow = UnitOfWork()
        try:
            uow.begin()
            # ... operations ...
            uow.commit()
        except Exception:
            uow.rollback()
            raise
        finally:
            uow.close()
        ```

        **Decorator Mode**:
        ```python
        @unit_of_work()
        def update_parameter(uow: UnitOfWork, param_id: int, new_type: str):
            param = uow.parameters.find_by_id(param_id)
            param.change_type(new_type)
            uow.parameters.save(param)
            return param
        ```
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Unit of Work

        Args:
            db_path: Optional database path. Uses default from config if not provided.
        """
        self._db_path = db_path or str(get_db_path())
        self._connection: Optional[sqlite3.Connection] = None
        self._repositories: Dict[str, Any] = {}
        self._events: List[Any] = []
        self._transaction_context: Optional[TransactionContext] = None
        self._is_active = False

    @property
    def connection(self) -> sqlite3.Connection:
        """
        Get the database connection

        Raises:
            RuntimeError: If connection not initialized (call begin() first)
        """
        if self._connection is None:
            raise RuntimeError(
                "No active connection. Call begin() first or use as context manager."
            )
        return self._connection

    @property
    def is_active(self) -> bool:
        """Check if transaction is currently active"""
        return self._is_active

    @property
    def parameters(self):
        """
        Get or create Parameter Repository

        Lazy loading pattern - repository created only when first accessed.

        Returns:
            ParameterRepositoryImpl instance with current connection
        """
        if 'parameters' not in self._repositories:
            from backend.infrastructure.persistence.repositories.parameter_repository_impl import ParameterRepositoryImpl
            repo = ParameterRepositoryImpl()
            # Inject connection for transaction consistency
            repo._connection = self.connection
            self._repositories['parameters'] = repo
            logger.debug("Parameter repository initialized")
        return self._repositories['parameters']

    @property
    def common_params(self):
        """
        Get or create Common Parameter Repository

        Returns:
            CommonParameterRepositoryImpl instance with current connection
        """
        if 'common_params' not in self._repositories:
            from backend.infrastructure.persistence.repositories.common_parameter_repository_impl import CommonParameterRepositoryImpl
            repo = CommonParameterRepositoryImpl()
            repo._connection = self.connection
            self._repositories['common_params'] = repo
            logger.debug("Common parameter repository initialized")
        return self._repositories['common_params']

    @property
    def games(self):
        """
        Get or create Game Repository

        Returns:
            GameRepositoryImpl instance with current connection
        """
        if 'games' not in self._repositories:
            from backend.infrastructure.persistence.repositories.game_repository_impl import GameRepositoryImpl
            repo = GameRepositoryImpl()
            repo._connection = self.connection
            self._repositories['games'] = repo
            logger.debug("Game repository initialized")
        return self._repositories['games']

    @property
    def events(self):
        """
        Get or create Event Repository

        Returns:
            EventRepositoryImpl instance with current connection
        """
        if 'events' not in self._repositories:
            from backend.infrastructure.persistence.repositories.event_repository_impl import EventRepositoryImpl
            repo = EventRepositoryImpl()
            repo._connection = self.connection
            self._repositories['events'] = repo
            logger.debug("Event repository initialized")
        return self._repositories['events']

    def begin(self) -> 'UnitOfWork':
        """
        Begin a new transaction

        Starts a database transaction with BEGIN IMMEDIATE for write operations.
        Creates a transaction context for tracking operations.

        Returns:
            Self for method chaining

        Raises:
            RuntimeError: If transaction already active
        """
        if self._is_active:
            raise RuntimeError("Transaction already active")

        self._connection = get_db_connection(self._db_path)
        self._connection.execute("BEGIN IMMEDIATE")
        self._is_active = True

        # Create transaction context
        import uuid
        self._transaction_context = TransactionContext(
            transaction_id=str(uuid.uuid4())[:8],
            started_at=datetime.now()
        )

        logger.debug(f"Transaction {self._transaction_context.transaction_id} started")
        return self

    def commit(self) -> None:
        """
        Commit the transaction and publish domain events

        This method:
        1. Commits database changes
        2. Publishes all registered domain events
        3. Marks transaction as committed
        4. Cleans up resources

        Raises:
            RuntimeError: If no active transaction
            Exception: If commit fails (transaction rolled back)
        """
        if not self._is_active:
            raise RuntimeError("No active transaction to commit")

        try:
            # Commit database transaction
            self._connection.commit()
            self._transaction_context.is_committed = True

            # Publish domain events after successful commit
            self._publish_events()

            logger.debug(
                f"Transaction {self._transaction_context.transaction_id} committed "
                f"({len(self._transaction_context.operations)} operations, "
                f"{len(self._events)} events published)"
            )
        except Exception as e:
            # Rollback on any error
            logger.error(f"Commit failed, rolling back: {e}")
            self._connection.rollback()
            self._transaction_context.is_rolled_back = True
            self._events.clear()  # Discard events on rollback
            raise
        finally:
            self._cleanup()

    def rollback(self) -> None:
        """
        Rollback the transaction and discard domain events

        This method:
        1. Rolls back database changes
        2. Clears all pending domain events
        3. Marks transaction as rolled back
        4. Cleans up resources

        Raises:
            RuntimeError: If no active transaction
        """
        if not self._is_active:
            raise RuntimeError("No active transaction to rollback")

        try:
            self._connection.rollback()
            self._transaction_context.is_rolled_back = True

            # Clear pending events on rollback
            self._events.clear()

            logger.debug(
                f"Transaction {self._transaction_context.transaction_id} rolled back "
                f"({len(self._transaction_context.operations)} operations discarded)"
            )
        finally:
            self._cleanup()

    def close(self) -> None:
        """
        Close the database connection

        Should be called after commit/rollback when not using context manager.
        """
        if self._connection:
            try:
                self._connection.close()
                logger.debug("Database connection closed")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self._connection = None
                self._is_active = False

    def _cleanup(self) -> None:
        """Cleanup after commit/rollback"""
        self._is_active = False
        # Don't clear repositories - they can be reused
        # But clear their connections
        for repo in self._repositories.values():
            if hasattr(repo, '_connection'):
                repo._connection = None

    def register_event(self, event: Any) -> None:
        """
        Register a domain event to be published after commit

        Events are published only after successful commit.
        If transaction is rolled back, all events are discarded.

        Args:
            event: Domain event instance (must inherit from DomainEvent)

        Example:
            uow.register_event(ParameterTypeChanged(
                parameter_id=123,
                old_type='string',
                new_type='int',
                game_gid=10000147
            ))
        """
        self._events.append(event)
        logger.debug(f"Event registered: {type(event).__name__}")

    def add_operation(self, operation_description: str, metadata: Optional[Dict] = None) -> None:
        """
        Track an operation for audit log

        Args:
            operation_description: Human-readable description of the operation
            metadata: Optional metadata dictionary

        Example:
            uow.add_operation("Changed parameter type", {
                'parameter_id': 123,
                'old_type': 'string',
                'new_type': 'int'
            })
        """
        if self._transaction_context:
            self._transaction_context.add_operation(operation_description, metadata)

    def get_operations(self) -> List[Dict[str, Any]]:
        """
        Get all operations tracked in this transaction

        Returns:
            List of operation dictionaries
        """
        if self._transaction_context:
            return self._transaction_context.operations
        return []

    def _publish_events(self) -> None:
        """
        Publish all registered domain events after successful commit

        Events are published to DomainEventPublisher which dispatches
        them to registered handlers (cache invalidation, logging, etc.)
        """
        if not self._events:
            return

        from backend.infrastructure.events.domain_event_publisher import DomainEventPublisher

        publisher = DomainEventPublisher()
        published_count = 0
        failed_count = 0

        for event in self._events:
            try:
                publisher.publish(event)
                published_count += 1
                logger.debug(f"Event published: {type(event).__name__}")
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to publish event {type(event).__name__}: {e}")

        logger.info(
            f"Published {published_count}/{len(self._events)} events "
            f"({failed_count} failed)"
        )

        self._events.clear()

    def __enter__(self) -> 'UnitOfWork':
        """Context manager entry - begin transaction"""
        return self.begin()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit - commit or rollback

        Auto-commit on success, auto-rollback on exception.
        Always closes connection.
        """
        if exc_type is not None:
            # Exception occurred, rollback
            logger.debug(f"Exception {exc_type.__name__} occurred, rolling back")
            self.rollback()
        else:
            # No exception, commit
            self.commit()

        self.close()


class UnitOfWorkDecorator:
    """
    Decorator-based Unit of Work for automatic transaction management

    Usage:
        @unit_of_work()
        def update_parameter(param_id: int, new_type: str):
            # First argument is always UnitOfWork instance
            param = uow.parameters.find_by_id(param_id)
            param.change_type(new_type)
            uow.parameters.save(param)
            return param

        # Call without UnitOfWork parameter
        result = update_parameter(123, 'int')
    """

    @staticmethod
    def unit_of_work(db_path: Optional[str] = None):
        """
        Create a Unit of Work decorator

        Args:
            db_path: Optional database path

        Returns:
            Decorator function

        Example:
            @unit_of_work()
            def create_game(uow: UnitOfWork, gid: int, name: str):
                game = Game(gid=gid, name=name)
                uow.games.save(game)
                return game
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create Unit of Work
                uow = UnitOfWork(db_path)

                try:
                    # Begin transaction
                    uow.begin()

                    # Inject Unit of Work as first argument
                    result = func(uow, *args, **kwargs)

                    # Commit on success
                    uow.commit()
                    return result

                except Exception:
                    # Rollback on error
                    uow.rollback()
                    raise

                finally:
                    # Always close connection
                    uow.close()

            return wrapper
        return decorator


# Convenience decorator function
def unit_of_work(db_path: Optional[str] = None):
    """
    Decorator for automatic Unit of Work transaction management

    Usage:
        @unit_of_work()
        def my_service_method(uow: UnitOfWork, arg1, arg2):
            # uow is automatically injected
            param = uow.parameters.find_by_id(arg1)
            return param

    Args:
        db_path: Optional database path

    Returns:
        Decorated function with automatic transaction management
    """
    return UnitOfWorkDecorator.unit_of_work(db_path)


@contextmanager
def unit_of_work_context(db_path: Optional[str] = None):
    """
    Context manager for Unit of Work (alternative to using UnitOfWork class directly)

    Usage:
        with unit_of_work_context() as uow:
            param = uow.parameters.find_by_id(123)
            param.change_type('int')
            uow.parameters.save(param)
            # Auto-commit on success, auto-rollback on exception

    Args:
        db_path: Optional database path

    Yields:
        UnitOfWork instance
    """
    uow = UnitOfWork(db_path)
    try:
        uow.begin()
        yield uow
        uow.commit()
    except Exception:
        uow.rollback()
        raise
    finally:
        uow.close()
