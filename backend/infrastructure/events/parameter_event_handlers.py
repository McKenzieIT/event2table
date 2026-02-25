#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Event Handlers

Handles parameter-related domain events to trigger side effects:
- Cache invalidation
- Audit logging
- Analytics updates
- Common parameter recalculation
"""

import logging
from typing import Dict, Any

from backend.domain.events.parameter_events import (
    ParameterTypeChanged,
    ParameterCountChanged,
    CommonParametersRecalculated,
    ParameterActivated,
    ParameterDeactivated,
    ParameterValidationFailed,
    CommonParameterThresholdAdjusted
)
from backend.core.cache.cache_system import CacheInvalidator

logger = logging.getLogger(__name__)


class ParameterEventHandler:
    """
    Handles parameter-related domain events

    This class provides static handler methods for all parameter-related
    domain events. Handlers are responsible for triggering side effects
    like cache invalidation, logging, and updates.
    """

    def __init__(self, cache_invalidator: CacheInvalidator = None):
        """
        Initialize event handler

        Args:
            cache_invalidator: Optional cache invalidator instance
        """
        self.cache_invalidator = cache_invalidator or CacheInvalidator()

    @staticmethod
    def handle_parameter_type_changed(event: ParameterTypeChanged) -> None:
        """
        Handle ParameterTypeChanged event

        Side effects:
        1. Invalidate parameter cache
        2. Invalidate game parameter list cache
        3. Log audit trail
        4. Trigger dependent HQL invalidation (future)

        Args:
            event: ParameterTypeChanged event
        """
        try:
            # Invalidate specific parameter cache
            CacheInvalidator.invalidate_key(f'parameter:{event.parameter_id}')

            # Invalidate game-wide parameter caches
            CacheInvalidator.invalidate_pattern(f'parameters:game:{event.game_gid}:*')
            CacheInvalidator.invalidate_pattern(f'params:game:{event.game_gid}:*')

            # Invalidate event parameter list cache
            CacheInvalidator.invalidate_pattern(f'event:{event.game_gid}:*:params')

            logger.info(
                f"Parameter type changed: ID={event.parameter_id}, "
                f"{event.old_type}→{event.game_gid}, "
                f"game_gid={event.game_gid}, "
                f"changed_by={event.changed_by}"
            )

            # TODO: Write to audit log table
            # TODO: Invalidate dependent HQL configurations

        except Exception as e:
            logger.error(f"Error handling ParameterTypeChanged event: {e}", exc_info=True)

    @staticmethod
    def handle_parameter_count_changed(event: ParameterCountChanged) -> None:
        """
        Handle ParameterCountChanged event

        Side effects:
        1. Trigger common parameter recalculation if threshold crossed
        2. Invalidate parameter count cache
        3. Log metrics

        Args:
            event: ParameterCountChanged event
        """
        try:
            # Invalidate count caches
            CacheInvalidator.invalidate_pattern(f'params:game:{event.game_gid}:count:*')
            CacheInvalidator.invalidate_key(f'parameters:game:{event.game_gid}:stats')

            # Log parameter count change
            logger.info(
                f"Parameter count changed for game {event.game_gid}: "
                f"{event.previous_count}→{event.current_count} "
                f"({event.change_type})"
            )

            # TODO: Trigger common parameter recalculation if needed
            # TODO: Publish metrics to monitoring system

        except Exception as e:
            logger.error(f"Error handling ParameterCountChanged event: {e}", exc_info=True)

    @staticmethod
    def handle_common_parameters_recalculated(event: CommonParametersRecalculated) -> None:
        """
        Handle CommonParametersRecalculated event

        Side effects:
        1. Invalidate common parameter caches
        2. Update statistics
        3. Log recalculation metrics

        Args:
            event: CommonParametersRecalculated event
        """
        try:
            # Invalidate common parameter caches
            CacheInvalidator.invalidate_pattern(f'common_params:game:{event.game_gid}:*')
            CacheInvalidator.invalidate_key(f'parameters:game:{event.game_gid}:common')

            logger.info(
                f"Common parameters recalculated for game {event.game_gid}: "
                f"{event.common_params_count} params "
                f"(threshold={event.threshold_used}, "
                f"duration={event.calculation_duration_ms}ms)"
            )

            # TODO: Update analytics dashboard
            # TODO: Trigger dependent cache refreshes

        except Exception as e:
            logger.error(f"Error handling CommonParametersRecalculated event: {e}", exc_info=True)

    @staticmethod
    def handle_parameter_activated(event: ParameterActivated) -> None:
        """
        Handle ParameterActivated event

        Side effects:
        1. Invalidate parameter cache
        2. Reactivate dependent configurations

        Args:
            event: ParameterActivated event
        """
        try:
            CacheInvalidator.invalidate_key(f'parameter:{event.parameter_id}')
            CacheInvalidator.invalidate_pattern(f'params:game:{event.game_gid}:*')

            logger.info(
                f"Parameter activated: ID={event.parameter_id}, "
                f"name={event.param_name}, "
                f"game_gid={event.game_gid}, "
                f"activated_by={event.activated_by}"
            )

        except Exception as e:
            logger.error(f"Error handling ParameterActivated event: {e}", exc_info=True)

    @staticmethod
    def handle_parameter_deactivated(event: ParameterDeactivated) -> None:
        """
        Handle ParameterDeactivated event

        Side effects:
        1. Invalidate parameter cache
        2. Mark dependent configurations as inactive

        Args:
            event: ParameterDeactivated event
        """
        try:
            CacheInvalidator.invalidate_key(f'parameter:{event.parameter_id}')
            CacheInvalidator.invalidate_pattern(f'params:game:{event.game_gid}:*')

            logger.info(
                f"Parameter deactivated: ID={event.parameter_id}, "
                f"name={event.param_name}, "
                f"game_gid={event.game_gid}, "
                f"deactivated_by={event.deactivated_by}, "
                f"reason={event.reason}"
            )

        except Exception as e:
            logger.error(f"Error handling ParameterDeactivated event: {e}", exc_info=True)

    @staticmethod
    def handle_parameter_validation_failed(event: ParameterValidationFailed) -> None:
        """
        Handle ParameterValidationFailed event

        Side effects:
        1. Log validation failure for monitoring
        2. Trigger alert if critical
        3. Update failure metrics

        Args:
            event: ParameterValidationFailed event
        """
        try:
            logger.warning(
                f"Parameter validation failed: "
                f"param_name={event.param_name}, "
                f"rule={event.validation_rule}, "
                f"error={event.error_message}, "
                f"game_gid={event.game_gid}"
            )

            # TODO: Send alert if validation failures exceed threshold
            # TODO: Update validation metrics in monitoring system

        except Exception as e:
            logger.error(f"Error handling ParameterValidationFailed event: {e}", exc_info=True)

    @staticmethod
    def handle_common_parameter_threshold_adjusted(event: CommonParameterThresholdAdjusted) -> None:
        """
        Handle CommonParameterThresholdAdjusted event

        Side effects:
        1. Invalidate all common parameter caches
        2. Trigger recalculation for affected games

        Args:
            event: CommonParameterThresholdAdjusted event
        """
        try:
            if event.game_gid:
                # Game-specific threshold change
                CacheInvalidator.invalidate_pattern(f'common_params:game:{event.game_gid}:*')
                logger.info(
                    f"Common parameter threshold adjusted for game {event.game_gid}: "
                    f"{event.old_threshold}→{event.new_threshold}, "
                    f"adjusted_by={event.adjusted_by}, "
                    f"reason={event.reason}"
                )
            else:
                # Global threshold change - invalidate all common parameter caches
                CacheInvalidator.invalidate_pattern('common_params:*')
                logger.info(
                    f"Global common parameter threshold adjusted: "
                    f"{event.old_threshold}→{event.new_threshold}, "
                    f"adjusted_by={event.adjusted_by}, "
                    f"reason={event.reason}"
                )

            # TODO: Trigger recalculation for affected games
            # TODO: Send notification to affected users

        except Exception as e:
            logger.error(f"Error handling CommonParameterThresholdAdjusted event: {e}", exc_info=True)


class ParameterEventRouter:
    """
    Routes parameter events to appropriate handlers

    This class registers all parameter event handlers with the
    DomainEventPublisher during initialization.
    """

    def __init__(self, publisher=None):
        """
        Initialize event router

        Args:
            publisher: DomainEventPublisher instance (uses global if None)
        """
        from backend.infrastructure.events.domain_event_publisher import get_domain_event_publisher

        self.publisher = publisher or get_domain_event_publisher()
        self.handler = ParameterEventHandler()
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all parameter event handlers"""
        self.publisher.subscribe(ParameterTypeChanged, self.handler.handle_parameter_type_changed)
        self.publisher.subscribe(ParameterCountChanged, self.handler.handle_parameter_count_changed)
        self.publisher.subscribe(CommonParametersRecalculated, self.handler.handle_common_parameters_recalculated)
        self.publisher.subscribe(ParameterActivated, self.handler.handle_parameter_activated)
        self.publisher.subscribe(ParameterDeactivated, self.handler.handle_parameter_deactivated)
        self.publisher.subscribe(ParameterValidationFailed, self.handler.handle_parameter_validation_failed)
        self.publisher.subscribe(CommonParameterThresholdAdjusted, self.handler.handle_common_parameter_threshold_adjusted)

        logger.info("Parameter event handlers registered")


def register_parameter_event_handlers(publisher=None) -> ParameterEventRouter:
    """
    Register all parameter event handlers with the publisher

    This function should be called during application initialization
    to ensure all parameter events are properly handled.

    Args:
        publisher: Optional DomainEventPublisher instance

    Returns:
        ParameterEventRouter instance with registered handlers

    Example:
        # In application initialization
        register_parameter_event_handlers()
    """
    router = ParameterEventRouter(publisher)
    return router
