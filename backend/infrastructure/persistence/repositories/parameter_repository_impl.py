#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Repository Implementation

Concrete implementation of IParameterRepository for parameter data access.
This repository handles all database operations for the event_params table.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from backend.domain.repositories.parameter_repository import IParameterRepository
from backend.domain.models.parameter import Parameter
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.core.database.database import get_db_connection


logger = logging.getLogger(__name__)


class ParameterRepositoryImpl(IParameterRepository):
    """
    Concrete implementation of IParameterRepository

    Provides data access methods for event parameters using the event_params table.
    All SQL queries use parameterized statements to prevent SQL injection.
    """

    def __init__(self):
        """Initialize the repository"""
        self.table_name = "event_params"
        logger.debug("ParameterRepositoryImpl initialized")

    def find_by_id(self, param_id: int) -> Optional[Parameter]:
        """
        Find parameter by ID

        Args:
            param_id: Parameter ID

        Returns:
            Parameter object or None if not found
        """
        if not param_id:
            return None

        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                ep.json_path,
                ep.param_description as description,
                ep.event_id,
                ep.is_active,
                ep.version,
                ep.created_at,
                ep.updated_at,
                le.game_gid,
                pt.template_name as param_type
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.id = ?
        """

        try:
            result = fetch_one_as_dict(query, (param_id,))
            if not result:
                return None

            return self._dict_to_parameter(result)
        except Exception as e:
            logger.error(f"Error finding parameter by ID {param_id}: {e}")
            raise

    def find_by_game(self, game_gid: int) -> List[Parameter]:
        """
        Find all parameters for a game

        Args:
            game_gid: Game GID

        Returns:
            List of parameters
        """
        if not game_gid:
            return []

        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                ep.json_path,
                ep.param_description as description,
                ep.event_id,
                ep.is_active,
                ep.version,
                ep.created_at,
                ep.updated_at,
                le.game_gid,
                pt.template_name as param_type
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ?
            ORDER BY ep.event_id, ep.id
        """

        try:
            results = fetch_all_as_dict(query, (game_gid,))
            return [self._dict_to_parameter(row) for row in results]
        except Exception as e:
            logger.error(f"Error finding parameters for game {game_gid}: {e}")
            raise

    def find_common_by_game(self, game_gid: int) -> List[Parameter]:
        """
        Find all common parameters for a game

        Args:
            game_gid: Game GID

        Returns:
            List of common parameters
        """
        if not game_gid:
            return []

        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                ep.json_path,
                ep.param_description as description,
                ep.event_id,
                ep.is_active,
                ep.version,
                ep.created_at,
                ep.updated_at,
                le.game_gid,
                pt.template_name as param_type
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ?
            AND le.include_in_common_params = 1
            AND ep.is_active = 1
            ORDER BY ep.param_name
        """

        try:
            results = fetch_all_as_dict(query, (game_gid,))
            return [self._dict_to_parameter(row) for row in results]
        except Exception as e:
            logger.error(f"Error finding common parameters for game {game_gid}: {e}")
            raise

    def find_non_common_by_game(self, game_gid: int) -> List[Parameter]:
        """
        Find all non-common parameters for a game

        Args:
            game_gid: Game GID

        Returns:
            List of non-common parameters
        """
        if not game_gid:
            return []

        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                ep.json_path,
                ep.param_description as description,
                ep.event_id,
                ep.is_active,
                ep.version,
                ep.created_at,
                ep.updated_at,
                le.game_gid,
                pt.template_name as param_type
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ?
            AND (le.include_in_common_params = 0 OR le.include_in_common_params IS NULL)
            AND ep.is_active = 1
            ORDER BY ep.event_id, ep.id
        """

        try:
            results = fetch_all_as_dict(query, (game_gid,))
            return [self._dict_to_parameter(row) for row in results]
        except Exception as e:
            logger.error(f"Error finding non-common parameters for game {game_gid}: {e}")
            raise

    def find_by_event_id(self, event_id: int) -> List[Parameter]:
        """
        Find all parameters for an event

        Args:
            event_id: Event ID

        Returns:
            List of parameters
        """
        if not event_id:
            return []

        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                ep.json_path,
                ep.param_description as description,
                ep.event_id,
                ep.is_active,
                ep.version,
                ep.created_at,
                ep.updated_at,
                le.game_gid,
                pt.template_name as param_type
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.event_id = ?
            AND ep.is_active = 1
            ORDER BY ep.id
        """

        try:
            results = fetch_all_as_dict(query, (event_id,))
            return [self._dict_to_parameter(row) for row in results]
        except Exception as e:
            logger.error(f"Error finding parameters for event {event_id}: {e}")
            raise

    def count_by_game(self, game_gid: int) -> int:
        """
        Count parameters for a game

        Args:
            game_gid: Game GID

        Returns:
            Number of parameters
        """
        if not game_gid:
            return 0

        query = """
            SELECT COUNT(*) as total
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = ?
            AND ep.is_active = 1
        """

        try:
            result = fetch_one_as_dict(query, (game_gid,))
            return result['total'] if result else 0
        except Exception as e:
            logger.error(f"Error counting parameters for game {game_gid}: {e}")
            raise

    def count_events_by_game(self, game_gid: int) -> int:
        """
        Count events with parameters for a game

        Args:
            game_gid: Game GID

        Returns:
            Number of events with parameters
        """
        if not game_gid:
            return 0

        query = """
            SELECT COUNT(DISTINCT ep.event_id) as total
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = ?
            AND ep.is_active = 1
        """

        try:
            result = fetch_one_as_dict(query, (game_gid,))
            return result['total'] if result else 0
        except Exception as e:
            logger.error(f"Error counting events for game {game_gid}: {e}")
            raise

    def get_parameter_usage_stats(self, game_gid: int) -> List[Dict]:
        """
        Get parameter usage statistics for a game

        Args:
            game_gid: Game GID

        Returns:
            List of parameter usage statistics
        """
        if not game_gid:
            return []

        query = """
            SELECT
                ep.param_name,
                ep.param_name_cn,
                COUNT(DISTINCT ep.event_id) as event_count,
                COUNT(*) as total_count,
                pt.template_name as param_type
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = ?
            AND ep.is_active = 1
            GROUP BY ep.param_name, ep.param_name_cn, pt.template_name
            ORDER BY event_count DESC, total_count DESC
        """

        try:
            return fetch_all_as_dict(query, (game_gid,))
        except Exception as e:
            logger.error(f"Error getting parameter usage stats for game {game_gid}: {e}")
            raise

    def find_common_parameters(self, game_gid: int) -> List[Parameter]:
        """
        Find all common parameters for a game (legacy method)

        Args:
            game_gid: Game GID

        Returns:
            List of common parameters
        """
        # This method is equivalent to find_common_by_game
        return self.find_common_by_game(game_gid)

    def find_by_name(self, param_name: str, event_id: int) -> Optional[Parameter]:
        """
        Find parameter by name within an event

        Args:
            param_name: Parameter name
            event_id: Event ID

        Returns:
            Parameter object or None if not found
        """
        if not param_name or not event_id:
            return None

        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_name_cn,
                ep.json_path,
                ep.param_description as description,
                ep.event_id,
                ep.is_active,
                ep.version,
                ep.created_at,
                ep.updated_at,
                le.game_gid,
                pt.template_name as param_type
            FROM event_params ep
            LEFT JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE ep.param_name = ?
            AND ep.event_id = ?
            AND ep.is_active = 1
        """

        try:
            result = fetch_one_as_dict(query, (param_name, event_id))
            if not result:
                return None

            return self._dict_to_parameter(result)
        except Exception as e:
            logger.error(f"Error finding parameter by name {param_name} in event {event_id}: {e}")
            raise

    def save(self, parameter: Parameter) -> Parameter:
        """
        Save parameter (create or update)

        Args:
            parameter: Parameter object

        Returns:
            Saved parameter object
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if parameter.id:
                # Update existing parameter
                cursor.execute(
                    """
                    UPDATE event_params
                    SET param_name = ?,
                        param_name_cn = ?,
                        json_path = ?,
                        param_description = ?,
                        is_active = ?,
                        version = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        parameter.param_name,
                        getattr(parameter, 'param_name_cn', ''),
                        parameter.json_path,
                        parameter.description,
                        1 if parameter.is_active else 0,
                        parameter.version,
                        parameter.id
                    )
                )
            else:
                # Map parameter type to template_id
                template_id = 1  # default: string
                if parameter.param_type == 'int':
                    template_id = 2
                elif parameter.param_type == 'bigint':
                    template_id = 3
                elif parameter.param_type == 'array':
                    template_id = 4
                elif parameter.param_type == 'boolean':
                    template_id = 5
                elif parameter.param_type == 'map':
                    template_id = 6

                # Create new parameter
                cursor.execute(
                    """
                    INSERT INTO event_params (
                        event_id, param_name, param_name_cn,
                        json_path, param_description, is_active, version, template_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        parameter.event_id,
                        parameter.param_name,
                        getattr(parameter, 'param_name_cn', ''),
                        parameter.json_path,
                        parameter.description,
                        1 if parameter.is_active else 0,
                        parameter.version,
                        template_id
                    )
                )
                parameter = Parameter(
                    id=cursor.lastrowid,
                    **{k: v for k, v in parameter.__dict__.items() if k != 'id'}
                )

            conn.commit()
            conn.close()

            logger.info(f"Saved parameter {parameter.id}: {parameter.param_name}")
            return parameter

        except Exception as e:
            logger.error(f"Error saving parameter: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise

    def delete(self, param_id: int) -> None:
        """
        Delete parameter (soft delete by setting is_active to False)

        Args:
            param_id: Parameter ID
        """
        if not param_id:
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE event_params SET is_active = 0 WHERE id = ?",
                (param_id,)
            )

            conn.commit()
            conn.close()

            logger.info(f"Soft deleted parameter {param_id}")

        except Exception as e:
            logger.error(f"Error deleting parameter {param_id}: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise

    def search_parameters(
        self,
        keyword: str,
        game_gid: Optional[int] = None
    ) -> List[Parameter]:
        """
        Search parameters by keyword

        Args:
            keyword: Search keyword
            game_gid: Filter by game GID (optional)

        Returns:
            List of matching parameters
        """
        if not keyword:
            return []

        keyword_pattern = f"%{keyword}%"

        if game_gid:
            query = """
                SELECT
                    ep.id,
                    ep.param_name,
                    ep.param_name_cn,
                    ep.json_path,
                    ep.param_description as description,
                    ep.event_id,
                    ep.is_active,
                    ep.version,
                    ep.created_at,
                    ep.updated_at,
                    le.game_gid,
                    pt.template_name as param_type
                FROM event_params ep
                LEFT JOIN log_events le ON ep.event_id = le.id
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE le.game_gid = ?
                AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)
                AND ep.is_active = 1
                ORDER BY ep.param_name
            """
            params = (game_gid, keyword_pattern, keyword_pattern)
        else:
            query = """
                SELECT
                    ep.id,
                    ep.param_name,
                    ep.param_name_cn,
                    ep.json_path,
                    ep.param_description as description,
                    ep.event_id,
                    ep.is_active,
                    ep.version,
                    ep.created_at,
                    ep.updated_at,
                    le.game_gid,
                    pt.template_name as param_type
                FROM event_params ep
                LEFT JOIN log_events le ON ep.event_id = le.id
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)
                AND ep.is_active = 1
                ORDER BY ep.param_name
            """
            params = (keyword_pattern, keyword_pattern)

        try:
            results = fetch_all_as_dict(query, params)
            return [self._dict_to_parameter(row) for row in results]
        except Exception as e:
            logger.error(f"Error searching parameters with keyword '{keyword}': {e}")
            raise

    def _dict_to_parameter(self, data: Dict[str, Any]) -> Parameter:
        """
        Convert database dictionary to Parameter domain model

        Args:
            data: Dictionary from database

        Returns:
            Parameter domain model
        """
        # Extract template name and map to parameter type
        param_type = 'string'  # default
        if data.get('param_type'):
            template_name = data['param_type'].lower()
            if 'int' in template_name or 'integer' in template_name:
                param_type = 'int'
            elif 'string' in template_name:
                param_type = 'string'
            elif 'array' in template_name:
                param_type = 'array'
            elif 'map' in template_name:
                param_type = 'map'
            elif 'bool' in template_name:
                param_type = 'boolean'

        return Parameter(
            id=data.get('id'),
            param_name=data.get('param_name', ''),
            param_type=param_type,
            json_path=data.get('json_path', '$.'),
            description=data.get('description'),
            event_id=data.get('event_id'),
            game_gid=data.get('game_gid'),
            is_active=bool(data.get('is_active', 1)),
            version=data.get('version', 1),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now()
        )
