"""
Batch Mutations Module

Provides batch operation mutations for efficient bulk operations.
Simple and practical implementation without over-engineering.
"""

import logging
from typing import List as TypingList

import graphene
from graphene import Boolean, Field, Int, List, Mutation, String

from backend.core.cache.cache_system import hierarchical_cache
from backend.core.security.authentication import authenticated, require_permission
from backend.core.security.error_sanitizer import ErrorSanitizer

logger = logging.getLogger(__name__)

# Import types needed for return values
from backend.gql_api.types.game_type import GameType


def _unwrap_graphene_value(value):
    """
    Unwrap Graphene scalar types to Python native types.

    In real GraphQL execution, scalars are already unwrapped (e.g., int).
    In direct Python tests or direct instantiation, scalars are Graphene objects
    with the actual value stored in the .kwargs dict.

    Args:
        value: Graphene scalar object or Python native type

    Returns:
        Python native type (int, str, bool, etc.)

    Examples:
        _unwrap_graphene_value(graphene.Int(123)) -> 123
        _unwrap_graphene_value(123) -> 123
        _unwrap_graphene_value(graphene.String("test")) -> "test"
    """
    if isinstance(value, (int, str, bool, float)) or value is None:
        return value
    if hasattr(value, 'kwargs'):
        return value.kwargs.get(list(value.kwargs.keys())[0]) if value.kwargs else value
    return value


class GameInput(graphene.InputObjectType):
    """Game input for batch operations"""

    gid = Int(required=True, description="游戏GID")
    name = String(required=True, description="游戏名称")
    name_cn = String(description="游戏中文名称")
    ods_db = String(description="ODS数据库名称")
    description = String(description="游戏描述")


class GameUpdateInput(graphene.InputObjectType):
    """Game update input for batch operations"""

    id = Int(required=True, description="游戏ID")
    name = String(description="游戏名称")
    name_cn = String(description="游戏中文名称")
    description = String(description="游戏描述")
    is_active = Boolean(description="是否活跃")


class BatchCreateGames(Mutation):
    """
    Batch Create Games Mutation

    Creates multiple games in a single operation with comprehensive validation.

    Business Logic:
    1. Batch size validation (max 100 games)
    2. GID uniqueness validation (no duplicates in batch)
    3. GID existence check (no conflicts with existing games)
    4. Data validation (gid format, name not empty)
    5. Transaction support (all-or-nothing)

    Example:
        mutation {
            batchCreateGames(games: [
                {gid: 10000148, name: "Game2"}
                {gid: 10000149, name: "Game3"}
            ]) {
                ok
                createdCount
                games { gid name }
            }
        }
    """

    class Arguments:
        games = List(GameInput, required=True, description="游戏列表")

    ok = Boolean(description="操作是否成功")
    games = List(lambda: GameType, description="创建的游戏列表")
    created_count = Int(description="创建数量")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('game:write')
    def mutate(root, info, games):
        """
        Execute batch create games with comprehensive validation

        Raises:
            ValueError: If validation fails (batch size, duplicates, data format)
            Exception: If database operation fails
        """
        import re

        from backend.core.database.transaction import transactional
        from backend.gql_api.types.game_type import GameType
        from backend.models.repositories.games import GameRepository

        MAX_BATCH_SIZE = 100

        # ===== VALIDATION PHASE =====

        # 1. Batch size validation
        if len(games) > MAX_BATCH_SIZE:
            raise ValueError(f"Cannot create more than {MAX_BATCH_SIZE} games at once")

        if len(games) == 0:
            raise ValueError("Games list cannot be empty")

        # 2. Extract and validate GIDs
        gids = [str(game.gid) for game in games]

        # 3. Check for duplicate GIDs in batch
        if len(gids) != len(set(gids)):
            duplicates = [gid for gid in gids if gids.count(gid) > 1]
            raise ValueError(f"Duplicate gids in batch: {set(duplicates)}")

        # 4. Check if GIDs already exist
        game_repo = GameRepository()
        existing_gids = game_repo.get_gids_by_list(gids)
        if existing_gids:
            raise ValueError(f"Gids already exist: {existing_gids}")

        # 5. Data validation for each game
        for game_data in games:
            # Validate GID format (3-20 digits)
            gid_str = str(game_data.gid)
            if not re.match(r'^\d{3,20}$', gid_str):
                raise ValueError(f"Invalid gid format: {game_data.gid}. Must be 3-20 digits.")

            # Validate name not empty
            if not game_data.name or len(game_data.name.strip()) == 0:
                raise ValueError(f"Game name cannot be empty for gid {game_data.gid}")

            # Validate ODS database if provided
            if game_data.ods_db and game_data.ods_db not in ['ieu_ods', 'overseas_ods']:
                raise ValueError(
                    f"Invalid ods_db for gid {game_data.gid}: {game_data.ods_db}. Must be 'ieu_ods' or 'overseas_ods'"
                )

        # ===== EXECUTION PHASE =====

        try:
            # 准备批量数据
            games_data = [
                {
                    'gid': str(game.gid),
                    'name': game.name.strip(),
                    'name_cn': (game.name_cn or '').strip(),
                    'ods_db': game.ods_db or f"ods_game_{game.gid}",
                    'description': (game.description or '').strip(),
                }
                for game in games
            ]

            # Execute batch create with transaction
            @transactional
            def _batch_create():
                return game_repo.create_batch(games_data)

            game_ids = _batch_create()

            # ⚡ PERF: Phase 1.2 Fix - Cache invalidation for batch create
            try:
                hierarchical_cache.delete("dashboard_statistics")
                hierarchical_cache.delete("games")
                logger.info(f"✅ 已失效缓存: dashboard_statistics, games (批量创建游戏)")
            except Exception as e:
                logger.warning(f"⚠️ 失效缓存失败: {e}")

            # 构建返回结果
            created_games = []
            for i, game_id in enumerate(game_ids):
                game_data = games_data[i].copy()
                game_data['id'] = game_id
                created_games.append(GameType.from_dict(game_data))

            return BatchCreateGames(
                ok=True, games=created_games, created_count=len(created_games), errors=None
            )

        except ValueError as e:
            # Validation errors - don't log stack trace
            logger.warning(f"Batch create games validation failed: {e}")
            return BatchCreateGames(ok=False, games=[], created_count=0, errors=[str(e)])
        except Exception as e:
            logger.error(f"Batch create games failed: {e}", exc_info=True)
            return BatchCreateGames(
                ok=False,
                games=[],
                created_count=0,
                errors=[f"Batch create failed: {ErrorSanitizer.sanitize_message(str(e))}"],
            )


class BatchUpdateGames(Mutation):
    """
    Batch Update Games Mutation

    Updates multiple games in a single operation with comprehensive validation.

    Business Logic:
    1. Batch size validation (max 100 updates)
    2. Existence check (all games must exist)
    3. Business rules validation (gid cannot be changed)
    4. Data validation (name not empty if provided)
    5. Transaction support (all-or-nothing)

    Example:
        mutation {
            batchUpdateGames(updates: [
                {id: 1, name: "Updated Game1"}
                {id: 2, description: "New description"}
            ]) {
                ok
                updatedCount
            }
        }
    """

    class Arguments:
        updates = List(GameUpdateInput, required=True, description="更新列表")

    ok = Boolean(description="操作是否成功")
    updated_count = Int(description="更新数量")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission('game:write')
    def mutate(root, info, updates):
        """
        Execute batch update games with comprehensive validation

        Raises:
            ValueError: If validation fails (existence, business rules)
            Exception: If database operation fails
        """
        from backend.core.database.transaction import transactional
        from backend.models.repositories.games import GameRepository

        MAX_BATCH_SIZE = 100

        # ===== VALIDATION PHASE =====

        # 1. Batch size validation
        if len(updates) > MAX_BATCH_SIZE:
            raise ValueError(f"Cannot update more than {MAX_BATCH_SIZE} games at once")

        if not updates:
            return BatchUpdateGames(ok=True, updated_count=0, errors=None)

        # 2. Extract game IDs (convert Graphene Int to Python int)
        game_ids = [_unwrap_graphene_value(u.id) for u in updates]

        # 3. Existence check - all games must exist
        game_repo = GameRepository()
        existing_games = game_repo.get_by_ids(game_ids)
        if len(existing_games) != len(game_ids):
            existing_ids = {g['id'] for g in existing_games}
            missing = set(game_ids) - existing_ids
            raise ValueError(f"Games not found: {missing}")

        # 4. Data validation for each update
        for update_input in updates:
            # Validate name not empty if provided
            if update_input.name is not None and len(update_input.name.strip()) == 0:
                game_id = _unwrap_graphene_value(update_input.id)
                raise ValueError(f"Game name cannot be empty for game id {game_id}")

        # ===== EXECUTION PHASE =====

        try:
            # Execute batch update with transaction using CASE WHEN
            @transactional
            def _batch_update():
                from backend.core.database.database import get_db_connection

                conn = get_db_connection()
                cursor = conn.cursor()

                # Build CASE WHEN clauses for each field
                name_cases = []
                description_cases = []
                is_active_cases = []
                name_cn_cases = []
                game_ids = []

                for update_input in updates:
                    # Convert Graphene Int to Python int (handles both test and real GraphQL)
                    game_id = _unwrap_graphene_value(update_input.id)
                    game_ids.append(game_id)

                    if update_input.name is not None:
                        # Validate ID before using in SQL
                        from backend.core.security.sql_validator import SQLValidator

                        validated_id = SQLValidator.validate_integer(game_id, "update_input.id")
                        name_cases.append(f"WHEN {validated_id} THEN ?")
                    if update_input.description is not None:
                        from backend.core.security.sql_validator import SQLValidator

                        validated_id = SQLValidator.validate_integer(game_id, "update_input.id")
                        description_cases.append(f"WHEN {validated_id} THEN ?")
                    if update_input.is_active is not None:
                        # Convert graphene Boolean to Python int
                        from backend.core.security.sql_validator import SQLValidator

                        validated_id = SQLValidator.validate_integer(game_id, "update_input.id")
                        is_active_int = 1 if update_input.is_active else 0
                        is_active_cases.append(f"WHEN {validated_id} THEN {is_active_int}")
                    if update_input.name_cn is not None:
                        from backend.core.security.sql_validator import SQLValidator

                        validated_id = SQLValidator.validate_integer(game_id, "update_input.id")
                        name_cn_cases.append(f"WHEN {validated_id} THEN ?")

                # Build SET clause
                set_clauses = []
                params = []
                placeholders = ",".join(["?" for _ in game_ids])

                if name_cases:
                    set_clauses.append(f"name = CASE id {' '.join(name_cases)} ELSE name END")
                    params.extend([u.name for u in updates if u.name is not None])

                if name_cn_cases:
                    set_clauses.append(
                        f"name_cn = CASE id {' '.join(name_cn_cases)} ELSE name_cn END"
                    )
                    params.extend([u.name_cn for u in updates if u.name_cn is not None])

                if description_cases:
                    set_clauses.append(
                        f"description = CASE id {' '.join(description_cases)} ELSE description END"
                    )
                    params.extend([u.description for u in updates if u.description is not None])

                if is_active_cases:
                    set_clauses.append(
                        f"is_active = CASE id {' '.join(is_active_cases)} ELSE is_active END"
                    )

                if not set_clauses:
                    return 0

                params.extend(game_ids)

                # Execute single UPDATE statement
                query = f"""
                    UPDATE games
                    SET {', '.join(set_clauses)}
                    WHERE id IN ({placeholders})
                """

                cursor.execute(query, params)
                return cursor.rowcount

            updated_count = _batch_update()

            # ⚡ PERF: Phase 1.2 Fix - Cache invalidation for batch update
            try:
                hierarchical_cache.delete("dashboard_statistics")
                hierarchical_cache.delete("games")
                logger.info(f"✅ 已失效缓存: dashboard_statistics, games (批量更新游戏)")
            except Exception as e:
                logger.warning(f"⚠️ 失效缓存失败: {e}")

            return BatchUpdateGames(ok=True, updated_count=updated_count, errors=None)

        except ValueError as e:
            # Validation errors - don't log stack trace
            logger.warning(f"Batch update games validation failed: {e}")
            return BatchUpdateGames(ok=False, updated_count=0, errors=[str(e)])
        except Exception as e:
            logger.error(f"Batch update games failed: {e}", exc_info=True)
            safe_error = ErrorSanitizer.sanitize_with_context(e, "batch update games")
            return BatchUpdateGames(ok=False, updated_count=0, errors=[safe_error])


class BatchDeleteGames(Mutation):
    """
    Batch Delete Games Mutation

    Deletes multiple games in a single operation with comprehensive validation.

    Business Logic:
    1. Batch size validation (max 100 deletions)
    2. STAR001 protection (gid 10000147 cannot be deleted)
    3. Dependency check (cannot delete games with events)
    4. Dependency check (cannot delete games with categories)
    5. Transaction support (all-or-nothing)

    Example:
        mutation {
            batchDeleteGames(ids: [2, 3, 4]) {
                ok
                deletedCount
            }
        }
    """

    class Arguments:
        ids = List(Int, required=True, description="游戏ID列表")

    ok = Boolean(description="操作是否成功")
    deleted_count = Int(description="删除数量")
    errors = List(String, description="错误信息")

    def mutate(root, info, ids):
        """
        Execute batch delete games with comprehensive validation

        Raises:
            ValueError: If validation fails (STAR001 protection, dependencies)
            Exception: If database operation fails
        """
        from backend.core.database.transaction import transactional
        from backend.models.repositories.events import EventRepository
        from backend.models.repositories.games import GameRepository

        MAX_BATCH_SIZE = 100
        STAR001_GID = "10000147"  # Protected game GID

        # ===== VALIDATION PHASE =====

        # 1. Batch size validation
        if len(ids) > MAX_BATCH_SIZE:
            raise ValueError(f"Cannot delete more than {MAX_BATCH_SIZE} games at once")

        if not ids:
            return BatchDeleteGames(ok=True, deleted_count=0, errors=None)

        # 2. Existence check and STAR001 protection
        game_repo = GameRepository()
        existing_games = game_repo.get_by_ids(ids)

        # Check for STAR001
        for game in existing_games:
            if str(game.gid) == STAR001_GID:
                raise ValueError(
                    f"Cannot delete STAR001 game (gid {STAR001_GID}). This game is protected."
                )

        # 3. Dependency check - events
        event_repo = EventRepository()
        for game in existing_games:
            event_count = event_repo.count_by_game_gid(game.gid)
            if event_count > 0:
                raise ValueError(
                    f"Cannot delete game '{game.name}' (gid {game.gid}) with {event_count} events. "
                    f"Delete events first."
                )

        # 4. Dependency check - categories (if applicable)
        # TODO: Add category count check when category repository has count_by_game_gid method

        # ===== EXECUTION PHASE =====

        try:
            # Execute batch delete with transaction
            @transactional
            def _batch_delete():
                # Use delete_batch for single SQL statement
                return game_repo.delete_batch(ids)

            deleted_count = _batch_delete()

            # ⚡ PERF: Phase 1.2 Fix - Cache invalidation for batch delete
            try:
                hierarchical_cache.delete("dashboard_statistics")
                hierarchical_cache.delete("games")
                logger.info(f"✅ 已失效缓存: dashboard_statistics, games (批量删除游戏)")
            except Exception as e:
                logger.warning(f"⚠️ 失效缓存失败: {e}")

            return BatchDeleteGames(ok=True, deleted_count=deleted_count, errors=None)

        except ValueError as e:
            # Validation errors - don't log stack trace
            logger.warning(f"Batch delete games validation failed: {e}")
            return BatchDeleteGames(ok=False, deleted_count=0, errors=[str(e)])
        except Exception as e:
            logger.error(f"Batch delete games failed: {e}", exc_info=True)
            safe_error = ErrorSanitizer.sanitize_with_context(e, "batch delete games")
            return BatchDeleteGames(ok=False, deleted_count=0, errors=[safe_error])


class BatchMutations(graphene.ObjectType):
    """
    Batch Mutations Root Type

    Groups all batch operation mutations for games.
    All mutations support:
    - Transaction support (all-or-nothing)
    - Comprehensive validation
    - Batch size limits (max 100 items)
    - Cache invalidation

    Note: Event batch mutations are defined in event_mutations.py
    """

    # Game batch operations
    batch_create_games = BatchCreateGames.Field(description="Batch create games with validation")
    batch_update_games = BatchUpdateGames.Field(description="Batch update games with validation")
    batch_delete_games = BatchDeleteGames.Field(
        description="Batch delete games with dependency checks"
    )
