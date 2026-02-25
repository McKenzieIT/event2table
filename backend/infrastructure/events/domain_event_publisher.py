#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Domain Event Publisher

Publishes domain events to registered handlers.
Implements observer pattern for loose coupling between domain logic and side effects.
"""

import logging
from typing import Dict, List, Callable, Any, Type
from dataclasses import is_dataclass

logger = logging.getLogger(__name__)


class DomainEventPublisher:
    """
    Publisher for domain events using observer pattern
    """

    def __init__(self):
        """Initialize event publisher with empty handler registry"""
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: Type, handler: Callable[[Any], None]) -> None:
        """
        Subscribe a handler to an event type

        Args:
            event_type: Event class (e.g., ParameterTypeChanged)
            handler: Callable that accepts event instance
        """
        if not is_dataclass(event_type):
            raise TypeError(f"Event type {event_type.__name__} must be a dataclass")

        event_name = event_type.__name__

        if event_name not in self._handlers:
            self._handlers[event_name] = []

        self._handlers[event_name].append(handler)
        logger.debug(f"Handler subscribed to {event_name}: {handler.__name__}")

    def publish(self, event: Any) -> None:
        """
        Publish event to all registered handlers

        Args:
            event: Domain event instance (must be dataclass)
        """
        if not is_dataclass(event):
            raise TypeError(f"Event must be a dataclass, got {type(event)}")

        event_name = type(event).__name__

        if event_name not in self._handlers:
            logger.debug(f"No handlers registered for event {event_name}")
            return

        logger.info(f"Publishing {event_name} to {len(self._handlers[event_name])} handlers")

        failed_handlers = 0

        for handler in self._handlers[event_name]:
            try:
                handler(event)
                logger.debug(f"Handler {handler.__name__} processed {event_name}")
            except Exception as e:
                failed_handlers += 1
                logger.error(
                    f"Handler {handler.__name__} failed for {event_name}: {e}",
                    exc_info=True
                )

        if failed_handlers > 0:
            logger.warning(
                f"{failed_handlers}/{len(self._handlers[event_name])} "
                f"handlers failed for {event_name}"
            )

    def unsubscribe(self, event_type: Type, handler: Callable) -> bool:
        """
        Unsubscribe a handler from an event type

        Args:
            event_type: Event class
            handler: Handler to remove

        Returns:
            True if handler was removed, False if not found
        """
        event_name = event_type.__name__

        if event_name not in self._handlers:
            return False

        try:
            self._handlers[event_name].remove(handler)
            logger.debug(f"Handler unsubscribed from {event_name}: {handler.__name__}")
            return True
        except ValueError:
            return False

    def get_handler_count(self, event_type: Type) -> int:
        """
        Get number of handlers for an event type

        Args:
            event_type: Event class

        Returns:
            Number of registered handlers
        """
        event_name = event_type.__name__
        return len(self._handlers.get(event_name, []))

    def clear_handlers(self, event_type: Type = None) -> None:
        """
        Clear all handlers for an event type or all events

        Args:
            event_type: Optional event type. If None, clears all handlers.
        """
        if event_type is None:
            self._handlers.clear()
            logger.debug("Cleared all event handlers")
        else:
            event_name = event_type.__name__
            if event_name in self._handlers:
                del self._handlers[event_name]
                logger.debug(f"Cleared handlers for {event_name}")


# Global singleton instance
_global_publisher = None


def get_domain_event_publisher() -> DomainEventPublisher:
    """Get global domain event publisher instance"""
    global _global_publisher
    if _global_publisher is None:
        _global_publisher = DomainEventPublisher()
    return _global_publisher


def reset_domain_event_publisher():
    """Reset global publisher (useful for testing)"""
    global _global_publisher
    _global_publisher = None
