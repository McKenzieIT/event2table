"""
Parameter App Service Enhanced

Application service layer for parameter management.
This service provides enhanced parameter operations with filtering,
auto-sync, and business logic that goes beyond basic CRUD.

It wraps the core ParameterService and provides application-specific features
for GraphQL resolvers and other high-level operations.

Author: Event2Table Development Team
Date: 2026-03-08
"""

import logging
from typing import Any, Dict, List, Optional

from backend.services.parameters.parameter_service import ParameterService

logger = logging.getLogger(__name__)


class ParameterAppServiceEnhanced:
    """
    Enhanced Parameter Application Service

    Provides application-level parameter operations including filtering,
    common parameter management, and auto-sync features.

    This service wraps the core ParameterService and adds business logic
    specific to the application layer.
    """

    def __init__(self):
        """Initialize the enhanced service with core dependencies."""
        self._param_service = ParameterService()

    def get_filtered_parameters(
        self, game_gid: int, mode: str = 'all', event_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get filtered parameters based on mode and event.

        Args:
            game_gid: Game GID
            mode: Filter mode ('all', 'common', 'non_common')
            event_id: Optional event ID filter

        Returns:
            List of parameter dictionaries

        Raises:
            ValueError: If mode is invalid
        """
        # Validate mode
        valid_modes = ['all', 'common', 'non_common']
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of: {', '.join(valid_modes)}")

        # ⚡ PERFORMANCE: Use paginated query instead of loading all 36K+ parameters
        # Get parameters for the game with pagination (max 10000 to prevent memory issues)
        all_params = []
        offset = 0
        limit = 1000
        max_total = 10000  # Safety limit

        while offset < max_total:
            batch = self._param_service.get_all_parameters_uncached(limit=limit, offset=offset)
            if not batch:
                break
            all_params.extend(batch)
            offset += limit
            if len(batch) < limit:  # Last batch
                break

        # Filter by game_gid
        game_params = [p for p in all_params if p.game_gid == game_gid]

        # Filter by event_id if specified
        if event_id:
            game_params = [p for p in game_params if p.event_id == event_id]

        # Apply mode filter
        if mode == 'all':
            return [self._to_dict(p) for p in game_params]
        elif mode == 'common':
            common_params = [p for p in game_params if p.is_common]
            return [self._to_dict(p) for p in common_params]
        elif mode == 'non_common':
            non_common_params = [p for p in game_params if not p.is_common]
            return [self._to_dict(p) for p in non_common_params]
        else:
            return []

    def get_parameter_by_id(self, parameter_id: int) -> Optional[Dict[str, Any]]:
        """
        Get parameter by ID with detailed information.

        Args:
            parameter_id: Parameter ID

        Returns:
            Parameter dictionary or None if not found

        Raises:
            ValueError: If parameter_id is invalid
        """
        if not parameter_id or parameter_id < 1:
            raise ValueError(f"Invalid parameter_id: {parameter_id}. Must be a positive integer")

        param = self._param_service.get_parameter_by_id(parameter_id)
        if param:
            return self._to_dict(param)
        return None

    def update_parameter_type(self, parameter_id: int, new_type: str) -> Dict[str, Any]:
        """
        Update parameter type with validation and cache invalidation.

        Args:
            parameter_id: Parameter ID
            new_type: New data type ('int', 'string', 'array', 'boolean', 'map')

        Returns:
            Updated parameter dictionary

        Raises:
            ValueError: If validation fails
        """
        # Validate parameter_id
        if not parameter_id or parameter_id < 1:
            raise ValueError(f"Invalid parameter_id: {parameter_id}. Must be a positive integer")

        # Validate new_type
        valid_types = ['int', 'string', 'array', 'boolean', 'map']
        if new_type not in valid_types:
            raise ValueError(
                f"Invalid new_type: {new_type}. Must be one of: {', '.join(valid_types)}"
            )

        # Get current parameter
        param = self._param_service.get_parameter_by_id(parameter_id)
        if not param:
            raise ValueError(f"Parameter not found: {parameter_id}")

        # Update using ParameterService
        updated_param = self._param_service.update_parameter(parameter_id, {'data_type': new_type})

        logger.info(f"Parameter type updated: id={parameter_id}, new_type={new_type}")

        return self._to_dict(updated_param)

    def auto_sync_common_parameters(self, game_gid: int, threshold: float = 0.8) -> Dict[str, Any]:
        """
        Automatically sync common parameters based on usage frequency.

        Parameters with usage frequency >= threshold across all events
        will be marked as common.

        Args:
            game_gid: Game GID
            threshold: Usage frequency threshold (0.0 to 1.0)

        Returns:
            Sync result dictionary with statistics

        Raises:
            ValueError: If validation fails
        """
        # Validate game_gid
        if not game_gid or game_gid < 1:
            raise ValueError(f"Invalid game_gid: {game_gid}. Must be a positive integer")

        # Validate threshold
        if not 0 <= threshold <= 1:
            raise ValueError(f"Invalid threshold: {threshold}. Must be between 0 and 1")

        # ⚡ PERFORMANCE: Use paginated query instead of loading all 36K+ parameters
        # Get parameters for this game with pagination
        all_params = []
        offset = 0
        limit = 1000
        max_total = 10000  # Safety limit

        while offset < max_total:
            batch = self._param_service.get_all_parameters_uncached(limit=limit, offset=offset)
            if not batch:
                break
            all_params.extend(batch)
            offset += limit
            if len(batch) < limit:  # Last batch
                break

        game_params = [p for p in all_params if p.game_gid == game_gid]

        # Calculate usage statistics
        param_usage = {}
        total_events = len(set(p.event_id for p in game_params))

        for param in game_params:
            param_name = param.name
            if param_name not in param_usage:
                # Count how many events use this parameter
                usage_count = sum(1 for p in game_params if p.name == param_name)
                param_usage[param_name] = usage_count / total_events if total_events > 0 else 0

        # Determine which parameters should be common
        new_common_params = [
            param_name for param_name, usage_freq in param_usage.items() if usage_freq >= threshold
        ]

        # Update common parameter status
        synced_count = 0
        for param in game_params:
            should_be_common = param.name in new_common_params
            if param.is_common != should_be_common:
                self._param_service.update_parameter(param.id, {'is_common': should_be_common})
                synced_count += 1

        logger.info(
            f"Auto-sync common parameters: game_gid={game_gid}, "
            f"threshold={threshold}, synced_count={synced_count}"
        )

        return {
            'success': True,
            'message': f'Successfully synced {synced_count} parameters',
            'game_gid': game_gid,
            'threshold': threshold,
            'total_parameters': len(game_params),
            'common_parameters': len(new_common_params),
            'synced_count': synced_count,
        }

    def _to_dict(self, param) -> Dict[str, Any]:
        """Convert ParameterEntity to dictionary."""
        return {
            'id': param.id,
            'name': param.name,
            'param_name': param.param_name,
            'param_name_cn': param.param_name_cn,
            'description': param.description,
            'event_id': param.event_id,
            'game_gid': param.game_gid,
            'param_type': param.param_type,
            'data_type': param.data_type,
            'json_path': param.json_path,
            'is_common': param.is_common,
            'is_base_field': getattr(param, 'is_base_field', False),
            'hql_config': param.hql_config,
        }


def get_parameter_app_service() -> ParameterAppServiceEnhanced:
    """
    Factory function to get ParameterAppServiceEnhanced instance.

    Returns:
        ParameterAppServiceEnhanced instance
    """
    return ParameterAppServiceEnhanced()
