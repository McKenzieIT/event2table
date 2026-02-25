#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CommonParameter Repository Implementation

Concrete implementation of ICommonParameterRepository for common parameter data access.
This repository handles all database operations for the common_params table.
"""

from typing import Optional, List
from datetime import datetime
import logging

from backend.domain.repositories.common_parameter_repository import ICommonParameterRepository
from backend.domain.models.common_parameter import CommonParameter, ParameterType
from backend.domain.models.parameter import Parameter
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.core.database.database import get_db_connection


logger = logging.getLogger(__name__)


class CommonParameterRepositoryImpl(ICommonParameterRepository):
    """
    Concrete implementation of ICommonParameterRepository

    Provides data access methods for common parameters using the common_params table.
    All SQL queries use parameterized statements to prevent SQL injection.
    """

    def __init__(self):
        """Initialize the repository"""
        self.table_name = "common_params"
        logger.debug("CommonParameterRepositoryImpl initialized")

    def find_by_game(self, game_gid: int) -> List[CommonParameter]:
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
                id,
                game_gid,
                param_name,
                param_name_cn,
                param_type,
                param_description,
                table_name,
                status,
                created_at,
                updated_at,
                display_name
            FROM common_params
            WHERE game_gid = ?
            ORDER BY param_name
        """

        try:
            results = fetch_all_as_dict(query, (game_gid,))
            return [self._dict_to_common_parameter(row) for row in results]
        except Exception as e:
            logger.error(f"Error finding common parameters for game {game_gid}: {e}")
            raise

    def save(self, common_param: CommonParameter) -> CommonParameter:
        """
        Save common parameter

        Args:
            common_param: CommonParameter object

        Returns:
            Saved common parameter object
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get game_id from game_gid
            cursor.execute("SELECT id FROM games WHERE gid = ?", (common_param.game_gid,))
            game_row = cursor.fetchone()
            game_id = game_row[0] if game_row else None

            if not game_id:
                raise ValueError(f"Game with GID {common_param.game_gid} not found")

            # Map ParameterType enum to string
            param_type_str = common_param.param_type.value if isinstance(common_param.param_type, ParameterType) else str(common_param.param_type)

            if common_param.id:
                # Update existing common parameter
                cursor.execute(
                    """
                    UPDATE common_params
                    SET param_name = ?,
                        param_name_cn = ?,
                        param_type = ?,
                        param_description = ?,
                        table_name = ?,
                        status = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        common_param.param_name,
                        common_param.param_name_cn,
                        param_type_str,
                        getattr(common_param, 'param_description', ''),
                        getattr(common_param, 'table_name', 'common'),
                        getattr(common_param, 'status', 'new'),
                        common_param.id
                    )
                )
            else:
                # Create new common parameter
                cursor.execute(
                    """
                    INSERT INTO common_params (
                        game_id, game_gid, param_name, param_name_cn,
                        param_type, param_description, table_name, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        game_id,
                        common_param.game_gid,
                        common_param.param_name,
                        common_param.param_name_cn,
                        param_type_str,
                        getattr(common_param, 'param_description', ''),
                        getattr(common_param, 'table_name', 'common'),
                        getattr(common_param, 'status', 'new')
                    )
                )
                common_param = CommonParameter(
                    id=cursor.lastrowid,
                    **{k: v for k, v in common_param.__dict__.items() if k != 'id'}
                )

            conn.commit()
            conn.close()

            logger.info(f"Saved common parameter {common_param.id}: {common_param.param_name}")
            return common_param

        except Exception as e:
            logger.error(f"Error saving common parameter: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise

    def delete_by_game(self, game_gid: int) -> None:
        """
        Delete all common parameters for a game

        Args:
            game_gid: Game GID
        """
        if not game_gid:
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM common_params WHERE game_gid = ?",
                (game_gid,)
            )

            conn.commit()
            conn.close()

            logger.info(f"Deleted all common parameters for game {game_gid}")

        except Exception as e:
            logger.error(f"Error deleting common parameters for game {game_gid}: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise

    def delete(self, common_param_id: int) -> None:
        """
        Delete common parameter by ID

        Args:
            common_param_id: Common parameter ID
        """
        if not common_param_id:
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM common_params WHERE id = ?",
                (common_param_id,)
            )

            conn.commit()
            conn.close()

            logger.info(f"Deleted common parameter {common_param_id}")

        except Exception as e:
            logger.error(f"Error deleting common parameter {common_param_id}: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            raise

    def find_by_param_name(self, game_gid: int, param_name: str) -> Optional[CommonParameter]:
        """
        Find common parameter by game and parameter name

        Args:
            game_gid: Game GID
            param_name: Parameter name

        Returns:
            CommonParameter object or None
        """
        if not game_gid or not param_name:
            return None

        query = """
            SELECT
                id,
                game_gid,
                param_name,
                param_name_cn,
                param_type,
                param_description,
                table_name,
                status,
                created_at,
                updated_at,
                display_name
            FROM common_params
            WHERE game_gid = ?
            AND param_name = ?
        """

        try:
            result = fetch_one_as_dict(query, (game_gid, param_name))
            if not result:
                return None

            return self._dict_to_common_parameter(result)
        except Exception as e:
            logger.error(f"Error finding common parameter by name {param_name} for game {game_gid}: {e}")
            raise

    def count_by_game(self, game_gid: int) -> int:
        """
        Count common parameters for a game

        Args:
            game_gid: Game GID

        Returns:
            Number of common parameters
        """
        if not game_gid:
            return 0

        query = "SELECT COUNT(*) as total FROM common_params WHERE game_gid = ?"

        try:
            result = fetch_one_as_dict(query, (game_gid,))
            return result['total'] if result else 0
        except Exception as e:
            logger.error(f"Error counting common parameters for game {game_gid}: {e}")
            raise

    def recalculate_for_game(
        self,
        game_gid: int,
        threshold: float = 0.8
    ) -> List[CommonParameter]:
        """
        Recalculate common parameters for a game

        Args:
            game_gid: Game GID
            threshold: Threshold ratio (default 0.8 = 80%)

        Returns:
            List of newly calculated common parameters
        """
        if not game_gid:
            return []

        try:
            # Get total event count for the game
            total_events_query = """
                SELECT COUNT(DISTINCT le.id) as total
                FROM log_events le
                WHERE le.game_gid = ?
            """
            total_result = fetch_one_as_dict(total_events_query, (game_gid,))
            total_events = total_result['total'] if total_result else 0

            if total_events == 0:
                return []

            # Find parameters that meet the threshold criteria
            params_query = """
                SELECT
                    ep.param_name,
                    ep.param_name_cn,
                    pt.template_name as param_type,
                    COUNT(DISTINCT ep.event_id) as occurrence_count,
                    ? as total_events,
                    ? as threshold
                FROM event_params ep
                LEFT JOIN log_events le ON ep.event_id = le.id
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE le.game_gid = ?
                AND ep.is_active = 1
                AND le.include_in_common_params = 1
                GROUP BY ep.param_name, ep.param_name_cn, pt.template_name
                HAVING (CAST(COUNT(DISTINCT ep.event_id) AS FLOAT) / ?) >= ?
                ORDER BY occurrence_count DESC
            """

            results = fetch_all_as_dict(
                params_query,
                (total_events, threshold, game_gid, total_events, threshold)
            )

            common_params = []
            for row in results:
                # Map template_name to ParameterType
                param_type_str = row.get('param_type', 'string')
                if 'int' in param_type_str.lower():
                    param_type = ParameterType.INT
                elif 'string' in param_type_str.lower():
                    param_type = ParameterType.STRING
                elif 'array' in param_type_str.lower():
                    param_type = ParameterType.ARRAY
                elif 'map' in param_type_str.lower():
                    param_type = ParameterType.MAP
                elif 'bool' in param_type_str.lower():
                    param_type = ParameterType.BOOLEAN
                else:
                    param_type = ParameterType.STRING

                common_param = CommonParameter(
                    id=None,
                    game_gid=game_gid,
                    param_name=row['param_name'],
                    param_name_cn=row.get('param_name_cn'),
                    param_type=param_type,
                    occurrence_count=row['occurrence_count'],
                    total_events=row['total_events'],
                    threshold=row['threshold'],
                    calculated_at=datetime.now()
                )
                common_params.append(common_param)

            # Save calculated common parameters to database
            for cp in common_params:
                self.save(cp)

            logger.info(
                f"Recalculated {len(common_params)} common parameters "
                f"for game {game_gid} with threshold {threshold}"
            )

            return common_params

        except Exception as e:
            logger.error(f"Error recalculating common parameters for game {game_gid}: {e}")
            raise

    def _dict_to_common_parameter(self, data: dict) -> CommonParameter:
        """
        Convert database dictionary to CommonParameter domain model

        Args:
            data: Dictionary from database

        Returns:
            CommonParameter domain model
        """
        # Map database param_type string to ParameterType enum
        param_type_str = data.get('param_type', 'string')
        try:
            param_type = ParameterType.from_string(param_type_str)
        except ValueError:
            param_type = ParameterType.STRING

        # For existing common parameters from database, we need to provide
        # occurrence_count and total_evenets (set to 0 as they're not stored)
        return CommonParameter(
            id=data.get('id'),
            game_gid=data.get('game_gid'),
            param_name=data.get('param_name', ''),
            param_name_cn=data.get('param_name_cn'),
            param_type=param_type,
            occurrence_count=0,  # Not stored in DB
            total_events=0,  # Not stored in DB
            calculated_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now()
        )
