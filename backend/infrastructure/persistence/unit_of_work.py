#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit of Work Pattern Implementation

This module implements the Unit of Work pattern for managing database transactions
in a DDD architecture. It ensures that all changes within a business operation
are committed atomically or rolled back on failure.

Key Features:
- Transaction management with automatic commit/rollback
- Context manager support for clean resource handling
- Integration with domain event publishing
- Thread-safe connection management
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import Optional, Callable, List, Any, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime

from backend.core.database.database import get_db_connection
from backend.core.config import get_db_path

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class TransactionContext:
    """Transaction context for tracking operations"""
    transaction_id: str
    started_at: datetime
    operations: List[str] = field(default_factory=list)
    is_committed: bool = False
    is_rolled_back: bool = False


class UnitOfWork:
    """
    Unit of Work Pattern Implementation
    
    Manages database transactions and ensures atomic operations.
    All changes within a unit of work are committed together or rolled back.
    
    Usage:
        # As context manager (recommended)
        with UnitOfWork() as uow:
            game_repo.save(game)
            event_repo.save(event)
            # Auto-commit on success, auto-rollback on exception
        
        # Manual mode
        uow = UnitOfWork()
        try:
            uow.begin()
            game_repo.save(game)
            uow.commit()
        except Exception:
            uow.rollback()
            raise
        finally:
            uow.close()
    """
    
    _current: Optional['UnitOfWork'] = None
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Unit of Work
        
        Args:
            db_path: Optional database path. Uses default if not provided.
        """
        self._db_path = db_path or str(get_db_path())
        self._connection: Optional[sqlite3.Connection] = None
        self._is_active = False
        self._transaction_context: Optional[TransactionContext] = None
        self._event_handlers: List[Callable] = []
        self._pending_events: List[Any] = []
    
    @property
    def connection(self) -> sqlite3.Connection:
        """Get the database connection"""
        if self._connection is None:
            raise RuntimeError("No active connection. Call begin() first or use as context manager.")
        return self._connection
    
    @property
    def is_active(self) -> bool:
        """Check if transaction is active"""
        return self._is_active
    
    @property
    def cursor(self) -> sqlite3.Cursor:
        """Get a cursor from the connection"""
        return self.connection.cursor()
    
    def begin(self) -> 'UnitOfWork':
        """
        Begin a new transaction
        
        Returns:
            Self for method chaining
        """
        if self._is_active:
            raise RuntimeError("Transaction already active")
        
        self._connection = get_db_connection(self._db_path)
        self._connection.execute("BEGIN IMMEDIATE")  # Exclusive lock for write operations
        self._is_active = True
        
        # Create transaction context
        import uuid
        self._transaction_context = TransactionContext(
            transaction_id=str(uuid.uuid4())[:8],
            started_at=datetime.now()
        )
        
        # Set as current unit of work
        UnitOfWork._current = self
        
        logger.debug(f"Transaction {self._transaction_context.transaction_id} started")
        return self
    
    def commit(self) -> None:
        """
        Commit the transaction
        
        Raises:
            RuntimeError: If no active transaction
        """
        if not self._is_active:
            raise RuntimeError("No active transaction to commit")
        
        try:
            self._connection.commit()
            self._transaction_context.is_committed = True
            
            # Publish pending events after successful commit
            self._publish_pending_events()
            
            logger.debug(
                f"Transaction {self._transaction_context.transaction_id} committed "
                f"({len(self._transaction_context.operations)} operations)"
            )
        finally:
            self._cleanup()
    
    def rollback(self) -> None:
        """
        Rollback the transaction
        
        Raises:
            RuntimeError: If no active transaction
        """
        if not self._is_active:
            raise RuntimeError("No active transaction to rollback")
        
        try:
            self._connection.rollback()
            self._transaction_context.is_rolled_back = True
            
            # Clear pending events on rollback
            self._pending_events.clear()
            
            logger.debug(
                f"Transaction {self._transaction_context.transaction_id} rolled back"
            )
        finally:
            self._cleanup()
    
    def close(self) -> None:
        """Close the connection"""
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self._connection = None
                self._is_active = False
    
    def _cleanup(self) -> None:
        """Cleanup after commit/rollback"""
        self._is_active = False
        if UnitOfWork._current is self:
            UnitOfWork._current = None
    
    def add_operation(self, operation: str) -> None:
        """
        Track an operation within this unit of work
        
        Args:
            operation: Description of the operation
        """
        if self._transaction_context:
            self._transaction_context.operations.append(operation)
    
    def register_event(self, event: Any) -> None:
        """
        Register a domain event to be published after commit
        
        Args:
            event: Domain event to publish
        """
        self._pending_events.append(event)
    
    def register_event_handler(self, handler: Callable) -> None:
        """
        Register an event handler
        
        Args:
            handler: Function to handle events
        """
        self._event_handlers.append(handler)
    
    def _publish_pending_events(self) -> None:
        """Publish all pending events after successful commit"""
        for event in self._pending_events:
            for handler in self._event_handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error handling event {type(event).__name__}: {e}")
        self._pending_events.clear()
    
    def __enter__(self) -> 'UnitOfWork':
        """Context manager entry"""
        return self.begin()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit"""
        if exc_type is not None:
            # Exception occurred, rollback
            logger.debug(f"Exception {exc_type.__name__} occurred, rolling back")
            self.rollback()
        else:
            # No exception, commit
            self.commit()
        self.close()
    
    @classmethod
    def get_current(cls) -> Optional['UnitOfWork']:
        """Get the current unit of work"""
        return cls._current


@contextmanager
def unit_of_work(db_path: Optional[str] = None):
    """
    Context manager for Unit of Work
    
    Usage:
        with unit_of_work() as uow:
            # Perform database operations
            pass
    
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


class RepositoryUnitOfWork(Generic[T]):
    """
    Repository-aware Unit of Work
    
    Provides a convenient way to work with repositories within a transaction.
    
    Usage:
        with RepositoryUnitOfWork() as ruow:
            game = ruow.games.find_by_gid(10000147)
            game.update_info(name="New Name")
            ruow.games.save(game)
            # Auto-commit on success
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self._uow = UnitOfWork(db_path)
        self._repositories = {}
    
    def __enter__(self) -> 'RepositoryUnitOfWork':
        self._uow.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self._uow.rollback()
        else:
            self._uow.commit()
        self._uow.close()
    
    @property
    def connection(self) -> sqlite3.Connection:
        return self._uow.connection
    
    @property
    def games(self):
        """Get game repository"""
        if 'games' not in self._repositories:
            from backend.infrastructure.persistence.game_repository_impl import GameRepositoryImpl
            self._repositories['games'] = GameRepositoryImpl()
            self._repositories['games']._connection = self._uow.connection
        return self._repositories['games']
    
    @property
    def events(self):
        """Get event repository"""
        if 'events' not in self._repositories:
            from backend.infrastructure.persistence.event_repository_impl import EventRepositoryImpl
            self._repositories['events'] = EventRepositoryImpl()
            self._repositories['events']._connection = self._uow.connection
        return self._repositories['events']
    
    @property
    def hql(self):
        """Get HQL repository"""
        if 'hql' not in self._repositories:
            from backend.infrastructure.persistence.hql_repository_impl import HQLRepositoryImpl
            self._repositories['hql'] = HQLRepositoryImpl()
            self._repositories['hql']._connection = self._uow.connection
        return self._repositories['hql']
    
    def register_event(self, event: Any) -> None:
        """Register a domain event"""
        self._uow.register_event(event)
    
    def add_operation(self, operation: str) -> None:
        """Track an operation"""
        self._uow.add_operation(operation)


# Decorator for automatic transaction management
def transactional(func: Callable) -> Callable:
    """
    Decorator to wrap a function in a transaction
    
    Usage:
        @transactional
        def create_game(gid: int, name: str):
            # Database operations are automatically wrapped in a transaction
            pass
    
    Args:
        func: Function to wrap
    
    Returns:
        Wrapped function
    """
    def wrapper(*args, **kwargs):
        with unit_of_work():
            return func(*args, **kwargs)
    return wrapper


# Async support (for future use)
class AsyncUnitOfWork:
    """
    Async Unit of Work for async database operations
    
    Note: SQLite doesn't support true async, but this provides
    a consistent interface for future database backends.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self._uow = UnitOfWork(db_path)
    
    async def __aenter__(self) -> 'AsyncUnitOfWork':
        self._uow.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self._uow.rollback()
        else:
            self._uow.commit()
        self._uow.close()
    
    @property
    def connection(self) -> sqlite3.Connection:
        return self._uow.connection
