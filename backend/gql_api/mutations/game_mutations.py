"""
Game Mutations

Implements GraphQL mutation resolvers for Game entity.

Provides comprehensive business logic validation:
- Input validation (gid format, name, ods_db enum)
- Uniqueness constraints (gid, name)
- Table name validation (SQL injection protection)
- Business rule enforcement (gid immutability, name uniqueness)
"""

import logging
import re
from datetime import datetime

import graphene
from graphene import Boolean, Field, Int, List, String

from backend.core.security.authentication import authenticated, require_permission
from backend.core.security.sql_validator import SQLValidator

logger = logging.getLogger(__name__)


class CreateGame(graphene.Mutation):
    """
    Create a new game

    Business Rules:
        - gid must be numeric string, 3-20 digits
        - name cannot be empty
        - ods_db must be one of: ieu_ods, overseas_ods
        - gid must be unique (no duplicates allowed)
        - ods_source_table must be validated (if provided)

    Example:
        mutation {
            createGame(gid: 10000147, name: "STAR001", ods_db: "ieu_ods") {
                ok
                game { gid name odsDb }
                errors
            }
        }
    """

    class Arguments:
        gid = Int(required=True, description="游戏GID（3-20位数字）")
        name = String(required=True, description="游戏名称（不能为空）")
        ods_db = String(required=True, description="ODS数据库名称（ieu_ods或overseas_ods）")
        ods_source_table = String(description="ODS源表名（可选, 需通过SQL验证）")
        dwd_prefix = String(description="DWD表前缀（可选, 默认'dwd'）")

    ok = Boolean(description="操作是否成功")
    game = Field(
        lambda: __import__('backend.gql_api.types.game_type', fromlist=['GameType']).GameType,
        description="创建的游戏",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('game:write')
    def mutate(
        self,
        info,
        gid: int,
        name: str,
        ods_db: str,
        ods_source_table: str = None,
        dwd_prefix: str = None,
    ):
        """
        Execute the mutation with comprehensive validation

        Validation Layers:
            1. Input Validation: gid format, name, ods_db enum
            2. Uniqueness Check: gid must be unique
            3. Table Validation: ods_source_table must be valid (if provided)
            4. Timestamp Initialization: created_at, updated_at

        Returns:
            CreateGame with ok=True if successful
            CreateGame with ok=False and errors list if validation fails
        """
        try:
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.gql_api.types.game_type import GameType

            # ========================================
            # Layer 1: Input Validation
            # ========================================

            # 1.1 Validate gid format (numeric string, 3-20 digits)
            if not isinstance(gid, int) or gid <= 0:
                return CreateGame(ok=False, errors=["gid must be a positive integer"])

            gid_str = str(gid)
            if not re.match(r'^\d{3,20}$', gid_str):
                return CreateGame(
                    ok=False,
                    errors=[f"gid must be numeric string with 3-20 digits, got: {gid_str}"],
                )

            # 1.2 Validate name is not empty
            if not name or len(name.strip()) == 0:
                return CreateGame(ok=False, errors=["Game name cannot be empty"])

            # Trim whitespace from name
            name = name.strip()

            # 1.3 Validate name length (reasonable limit)
            if len(name) > 100:
                return CreateGame(
                    ok=False, errors=[f"Game name too long (max 100 characters), got: {len(name)}"]
                )

            # 1.4 Validate ods_db enum value
            valid_dbs = ['ieu_ods', 'overseas_ods']
            if ods_db not in valid_dbs:
                return CreateGame(
                    ok=False,
                    errors=[f"Invalid ods_db: '{ods_db}'. Must be one of: {', '.join(valid_dbs)}"],
                )

            # 1.5 Validate dwd_prefix (if provided)
            if dwd_prefix is not None:
                if not dwd_prefix or len(dwd_prefix.strip()) == 0:
                    return CreateGame(ok=False, errors=["dwd_prefix cannot be empty string"])
                if len(dwd_prefix) > 20:
                    return CreateGame(
                        ok=False,
                        errors=[f"dwd_prefix too long (max 20 characters), got: {len(dwd_prefix)}"],
                    )

            # ========================================
            # Layer 2: Uniqueness Check
            # ========================================

            # 2.1 Check if gid already exists
            existing = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
            if existing:
                return CreateGame(
                    ok=False,
                    errors=[f"Game with gid {gid} already exists (name: '{existing['name']}')"],
                )

            # 2.2 Check if name already exists (optional, depending on requirements)
            existing_by_name = fetch_one_as_dict("SELECT * FROM games WHERE name = ?", (name,))
            if existing_by_name:
                return CreateGame(
                    ok=False,
                    errors=[f"Game name '{name}' already exists (gid: {existing_by_name['gid']})"],
                )

            # ========================================
            # Layer 3: Table Name Validation (if provided)
            # ========================================

            if ods_source_table:
                try:
                    # 3.1 Validate table name format (SQL injection protection)
                    validated_table = SQLValidator.validate_table_name(ods_source_table)

                    # 3.2 Optional: Check if table actually exists in database
                    # Note: This requires connection to Hive/ODS database, which may not be available
                    # Uncomment if you have cross-database query capability:
                    # if not self._table_exists_in_ods(validated_table):
                    #     return CreateGame(
                    #         ok=False,
                    #         errors=[f"Source table '{ods_source_table}' does not exist in ODS database"]
                    #     )

                    # If validation passes, use the validated table name
                    ods_source_table = validated_table

                except ValueError as e:
                    return CreateGame(
                        ok=False, errors=[f"Invalid table name '{ods_source_table}': {e}"]
                    )

            # ========================================
            # Layer 4: Timestamp Initialization
            # ========================================

            now = datetime.now()

            # ========================================
            # Create Game
            # ========================================

            # Build INSERT query dynamically based on provided fields
            fields = ['gid', 'name', 'ods_db', 'created_at', 'updated_at']
            values = [gid, name, ods_db, now, now]
            placeholders = ['?', '?', '?', '?', '?']

            if ods_source_table:
                fields.append('ods_source_table')
                values.append(ods_source_table)
                placeholders.append('?')

            if dwd_prefix:
                fields.append('dwd_prefix')
                values.append(dwd_prefix)
                placeholders.append('?')

            query = f"INSERT INTO games ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"

            execute_write(query, tuple(values))

            # Clear cache using enhanced invalidator
            cache_invalidator_enhanced.invalidate_key('games.list')
            cache_invalidator_enhanced.invalidate_key('dashboard_statistics')
            cache_invalidator_enhanced.invalidate_key('games')  # ⚡ PERF: Fix - Add games cache

            logger.info(f"Game created via GraphQL: {name} (GID: {gid}, ods_db: {ods_db})")

            # Return created game
            from backend.core.data_access import Repositories

            game = Repositories.GAMES.find_by_field("gid", gid)

            return CreateGame(ok=True, game=GameType.from_dict(game) if game else None)

        except Exception as e:
            logger.error(f"Error creating game: {e}", exc_info=True)
            return CreateGame(ok=False, errors=[str(e)])


class UpdateGame(graphene.Mutation):
    """
    Update an existing game

    Business Rules:
        - Game must exist (existence check)
        - gid cannot be changed (immutable field)
        - name must be unique (if changing)
        - ods_db must be valid enum value
        - ods_source_table must be validated (if changing)
        - updated_at is automatically updated

    Example:
        mutation {
            updateGame(gid: 10000147, name: "STAR001 Updated") {
                ok
                game { gid name odsDb }
                errors
            }
        }
    """

    class Arguments:
        gid = Int(required=True, description="游戏GID（不可修改）")
        name = String(description="游戏名称（如果提供, 必须唯一）")
        ods_db = String(description="ODS数据库名称（ieu_ods或overseas_ods）")
        ods_source_table = String(description="ODS源表名（可选, 需通过SQL验证）")
        dwd_prefix = String(description="DWD表前缀（可选）")
        description = String(description="游戏描述（可选）")

    ok = Boolean(description="操作是否成功")
    game = Field(
        lambda: __import__('backend.gql_api.types.game_type', fromlist=['GameType']).GameType,
        description="更新的游戏",
    )
    errors = List(String, description="错误信息")

    def mutate(
        self,
        info,
        gid: int,
        name: str = None,
        ods_db: str = None,
        ods_source_table: str = None,
        dwd_prefix: str = None,
        description: str = None,
    ):
        """
        Execute the mutation with comprehensive validation

        Validation Layers:
            1. Existence Check: Game must exist
            2. Immutable Field Check: gid cannot be changed
            3. Input Validation: name, ods_db, other fields
            4. Uniqueness Check: name must be unique (if changing)
            5. Table Validation: ods_source_table must be valid (if changing)
            6. Timestamp Update: updated_at is automatically updated

        Returns:
            UpdateGame with ok=True if successful
            UpdateGame with ok=False and errors list if validation fails
        """
        try:
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.gql_api.types.game_type import GameType

            # ========================================
            # Layer 1: Existence Check
            # ========================================

            # 1.1 Check if game exists
            game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
            if not game:
                return UpdateGame(ok=False, errors=[f"Game with gid {gid} not found"])

            # ========================================
            # Layer 2: Build Update Query
            # ========================================

            updates = []
            params = []
            errors = []

            # 2.1 Validate and add name (if provided)
            if name is not None:
                # Trim whitespace
                name = name.strip()

                # Validate name is not empty
                if not name:
                    errors.append("Game name cannot be empty")

                # Validate name length
                elif len(name) > 100:
                    errors.append(f"Game name too long (max 100 characters), got: {len(name)}")

                # Check name uniqueness
                else:
                    existing = fetch_one_as_dict(
                        "SELECT * FROM games WHERE name = ? AND gid != ?", (name, gid)
                    )
                    if existing:
                        errors.append(f"Game name '{name}' already exists (gid: {existing['gid']})")
                    else:
                        updates.append("name = ?")
                        params.append(name)

            # 2.2 Validate and add ods_db (if provided)
            if ods_db is not None:
                valid_dbs = ['ieu_ods', 'overseas_ods']
                if ods_db not in valid_dbs:
                    errors.append(
                        f"Invalid ods_db: '{ods_db}'. Must be one of: {', '.join(valid_dbs)}"
                    )
                else:
                    updates.append("ods_db = ?")
                    params.append(ods_db)

            # 2.3 Validate and add ods_source_table (if provided)
            if ods_source_table is not None:
                try:
                    # Validate table name format (SQL injection protection)
                    validated_table = SQLValidator.validate_table_name(ods_source_table)
                    updates.append("ods_source_table = ?")
                    params.append(validated_table)
                except ValueError as e:
                    errors.append(f"Invalid table name '{ods_source_table}': {e}")

            # 2.4 Validate and add dwd_prefix (if provided)
            if dwd_prefix is not None:
                if not dwd_prefix or len(dwd_prefix.strip()) == 0:
                    errors.append("dwd_prefix cannot be empty string")
                elif len(dwd_prefix) > 20:
                    errors.append(
                        f"dwd_prefix too long (max 20 characters), got: {len(dwd_prefix)}"
                    )
                else:
                    updates.append("dwd_prefix = ?")
                    params.append(dwd_prefix.strip())

            # 2.5 Validate and add description (if provided)
            if description is not None:
                if len(description) > 500:
                    errors.append(
                        f"Description too long (max 500 characters), got: {len(description)}"
                    )
                else:
                    updates.append("description = ?")
                    params.append(description)

            # ========================================
            # Layer 3: Validation Summary
            # ========================================

            # 3.1 Return errors if any validation failed
            if errors:
                return UpdateGame(ok=False, errors=errors)

            # 3.2 Check if there are any fields to update
            if not updates:
                return UpdateGame(
                    ok=False, errors=["No fields to update (all fields are None or unchanged)"]
                )

            # ========================================
            # Layer 4: Execute Update
            # ========================================

            # 4.1 Add updated_at timestamp
            updates.append("updated_at = ?")
            params.append(datetime.now())

            # 4.2 Add gid to params (WHERE clause)
            params.append(gid)

            # 4.3 Execute UPDATE query
            query = f"UPDATE games SET {', '.join(updates)} WHERE gid = ?"
            execute_write(query, tuple(params))

            # Clear cache using enhanced invalidator
            cache_invalidator_enhanced.invalidate_game_related(gid)

            logger.info(
                f"Game updated via GraphQL: GID {gid} (fields: {', '.join([u.split()[0] for u in updates[:-1]])})"
            )

            # Return updated game
            from backend.core.data_access import Repositories

            updated_game = Repositories.GAMES.find_by_field("gid", gid)

            return UpdateGame(
                ok=True, game=GameType.from_dict(updated_game) if updated_game else None
            )

        except Exception as e:
            logger.error(f"Error updating game: {e}", exc_info=True)
            return UpdateGame(ok=False, errors=[str(e)])


class DeleteGame(graphene.Mutation):
    """Delete a game"""

    class Arguments:
        gid = Int(required=True, description="游戏GID")
        confirm = Boolean(default_value=False, description="确认删除（即使有关联数据）")

    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('game:delete')
    def mutate(self, info, gid: int, confirm: bool = False):
        """Execute the mutation"""
        try:
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.core.utils import execute_write, fetch_one_as_dict

            # Check if game exists
            game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (gid,))
            if not game:
                return DeleteGame(ok=False, errors=["Game not found"])

            # Check for associated events
            event_count = fetch_one_as_dict(
                "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?", (gid,)
            )

            if event_count['count'] > 0 and not confirm:
                return DeleteGame(
                    ok=False,
                    errors=[
                        f"Game has {event_count['count']} events. Set confirm=true to force delete."
                    ],
                )

            # Delete game (cascade delete handled by database or manually)
            if confirm and event_count['count'] > 0:
                # Delete associated data first
                execute_write(
                    "DELETE FROM event_params WHERE event_id IN "
                    "(SELECT id FROM log_events WHERE game_gid = ?)",
                    (gid,),
                )
                execute_write("DELETE FROM log_events WHERE game_gid = ?", (gid,))

            execute_write("DELETE FROM games WHERE gid = ?", (gid,))

            # Clear cache using enhanced invalidator
            cache_invalidator_enhanced.invalidate_game_related(gid)

            logger.info(f"Game deleted via GraphQL: GID {gid}")

            return DeleteGame(ok=True, message="Game deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting game: {e}", exc_info=True)
            return DeleteGame(ok=False, errors=[str(e)])


class GameMutations:
    """Container for game mutations"""

    CreateGame = CreateGame
    UpdateGame = UpdateGame
    DeleteGame = DeleteGame
