#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parameter Repository Implementation

Implements the IParameterRepository interface using SQLite.
"""

import logging
from typing import List, Optional

from backend.domain.models.parameter import Parameter
from backend.domain.repositories.parameter_repository import IParameterRepository
from backend.core.database import get_db_connection

logger = logging.getLogger(__name__)


class ParameterRepositoryImpl(IParameterRepository):
    """Parameter repository implementation using SQLite"""

    def find_by_id(self, param_id: int) -> Optional[Parameter]:
        """Find parameter by ID"""
        try:
            conn = get_db_connection()
            cursor = conn.execute(
                """
                SELECT ep.*, pt.template_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id = ?
                """,
                (param_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_parameter(row)
            return None

        except Exception as e:
            logger.error(f"Error finding parameter by id: {e}", exc_info=True)
            raise

    def find_by_event_id(self, event_id: int) -> List[Parameter]:
        """Find all parameters for an event"""
        try:
            conn = get_db_connection()
            cursor = conn.execute(
                """
                SELECT ep.*, pt.template_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.event_id = ?
                ORDER BY ep.id
                """,
                (event_id,)
            )
            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_parameter(row) for row in rows]

        except Exception as e:
            logger.error(f"Error finding parameters by event: {e}", exc_info=True)
            raise

    def find_common_parameters(self, game_gid: int) -> List[Parameter]:
        """Find all common parameters for a game"""
        try:
            conn = get_db_connection()
            cursor = conn.execute(
                """
                SELECT ep.*, pt.template_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                JOIN log_events le ON ep.event_id = le.id
                WHERE le.game_gid = ? AND ep.is_common = 1 AND ep.is_active = 1
                ORDER BY ep.param_name
                """,
                (game_gid,)
            )
            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_parameter(row) for row in rows]

        except Exception as e:
            logger.error(f"Error finding common parameters: {e}", exc_info=True)
            raise

    def find_by_name(self, param_name: str, event_id: int) -> Optional[Parameter]:
        """Find parameter by name within an event"""
        try:
            conn = get_db_connection()
            cursor = conn.execute(
                """
                SELECT ep.*, pt.template_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.param_name = ? AND ep.event_id = ?
                """,
                (param_name, event_id)
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_parameter(row)
            return None

        except Exception as e:
            logger.error(f"Error finding parameter by name: {e}", exc_info=True)
            raise

    def save(self, parameter: Parameter) -> Parameter:
        """Save parameter"""
        try:
            conn = get_db_connection()

            if parameter.id is None:
                # Insert new parameter
                cursor = conn.execute(
                    """
                    INSERT INTO event_params
                    (event_id, param_name, param_name_cn, template_id, param_description, 
                     json_path, is_common, is_active, version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        parameter.event_id,
                        parameter.param_name,
                        parameter.param_name,  # Use param_name as default for param_name_cn
                        self._get_template_id(parameter.param_type),
                        parameter.description,
                        parameter.json_path,
                        1 if parameter.is_common else 0,
                        1 if parameter.is_active else 0,
                        parameter.version
                    )
                )
                param_id = cursor.lastrowid
                conn.commit()
                conn.close()

                return Parameter(
                    id=param_id,
                    param_name=parameter.param_name,
                    param_type=parameter.param_type,
                    json_path=parameter.json_path,
                    description=parameter.description,
                    event_id=parameter.event_id,
                    is_common=parameter.is_common,
                    is_active=parameter.is_active,
                    version=parameter.version
                )
            else:
                # Update existing parameter
                conn.execute(
                    """
                    UPDATE event_params
                    SET param_name = ?, param_name_cn = ?, template_id = ?,
                        param_description = ?, json_path = ?, is_common = ?,
                        is_active = ?, version = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        parameter.param_name,
                        parameter.param_name,
                        self._get_template_id(parameter.param_type),
                        parameter.description,
                        parameter.json_path,
                        1 if parameter.is_common else 0,
                        1 if parameter.is_active else 0,
                        parameter.version,
                        parameter.id
                    )
                )
                conn.commit()
                conn.close()

                return parameter

        except Exception as e:
            logger.error(f"Error saving parameter: {e}", exc_info=True)
            raise

    def delete(self, param_id: int) -> None:
        """Delete parameter (soft delete)"""
        try:
            conn = get_db_connection()
            conn.execute(
                "UPDATE event_params SET is_active = 0 WHERE id = ?",
                (param_id,)
            )
            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error deleting parameter: {e}", exc_info=True)
            raise

    def search_parameters(
        self,
        keyword: str,
        game_gid: Optional[int] = None
    ) -> List[Parameter]:
        """Search parameters by keyword"""
        try:
            conn = get_db_connection()

            if game_gid:
                cursor = conn.execute(
                    """
                    SELECT ep.*, pt.template_name
                    FROM event_params ep
                    LEFT JOIN param_templates pt ON ep.template_id = pt.id
                    JOIN log_events le ON ep.event_id = le.id
                    WHERE le.game_gid = ? 
                    AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)
                    ORDER BY ep.param_name
                    """,
                    (game_gid, f"%{keyword}%", f"%{keyword}%")
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT ep.*, pt.template_name
                    FROM event_params ep
                    LEFT JOIN param_templates pt ON ep.template_id = pt.id
                    WHERE ep.param_name LIKE ? OR ep.param_name_cn LIKE ?
                    ORDER BY ep.param_name
                    """,
                    (f"%{keyword}%", f"%{keyword}%")
                )

            rows = cursor.fetchall()
            conn.close()

            return [self._row_to_parameter(row) for row in rows]

        except Exception as e:
            logger.error(f"Error searching parameters: {e}", exc_info=True)
            raise

    def _row_to_parameter(self, row) -> Parameter:
        """Convert database row to Parameter object"""
        return Parameter(
            id=row['id'],
            param_name=row['param_name'],
            param_type=row.get('template_name', 'string'),
            json_path=row.get('json_path', '$.'),
            description=row.get('param_description'),
            event_id=row.get('event_id'),
            is_common=bool(row.get('is_common', 0)),
            is_active=bool(row.get('is_active', 1)),
            version=row.get('version', 1)
        )

    def _get_template_id(self, param_type: str) -> int:
        """Get template ID for parameter type"""
        type_mapping = {
            'string': 1,
            'int': 2,
            'float': 3,
            'boolean': 4,
            'array': 5,
            'map': 6
        }
        return type_mapping.get(param_type, 1)
