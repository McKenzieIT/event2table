"""
Batch Mutations Module

Provides batch operation mutations for efficient bulk operations.
Simple and practical implementation without over-engineering.
"""

import graphene
from graphene import Mutation, List, Int, String, Boolean, Field
import logging
from typing import List as TypingList

logger = logging.getLogger(__name__)


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

    Creates multiple games in a single operation.
    Simple implementation with basic error handling.
    """

    class Arguments:
        games = List(GameInput, required=True, description="游戏列表")

    ok = Boolean(description="操作是否成功")
    games = List(lambda: graphene.Field('backend.gql_api.types.game_type.GameType'), description="创建的游戏列表")
    created_count = Int(description="创建数量")
    errors = List(String, description="错误信息")

    def mutate(root, info, games):
        """Execute batch create games"""
        from backend.core.data_access import Repositories
        from backend.gql_api.types.game_type import GameType

        created_games = []
        errors = []

        try:
            game_repo = Repositories.games()

            for game_input in games:
                try:
                    # Create game in database
                    game_data = {
                        'gid': game_input.gid,
                        'name': game_input.name,
                        'name_cn': game_input.name_cn,
                        'ods_db': game_input.ods_db or f"ods_game_{game_input.gid}",
                        'description': game_input.description,
                    }

                    game_id = game_repo.create(game_data)
                    game_data['id'] = game_id

                    created_games.append(GameType.from_dict(game_data))

                except Exception as e:
                    errors.append(f"Failed to create game {game_input.gid}: {str(e)}")
                    logger.error(f"Batch create game error: {e}")

            return BatchCreateGames(
                ok=len(errors) == 0,
                games=created_games,
                created_count=len(created_games),
                errors=errors if errors else None
            )

        except Exception as e:
            logger.error(f"Batch create games failed: {e}")
            return BatchCreateGames(
                ok=False,
                games=[],
                created_count=0,
                errors=[str(e)]
            )


class BatchUpdateGames(Mutation):
    """
    Batch Update Games Mutation

    Updates multiple games in a single operation.
    Simple implementation with basic error handling.
    """

    class Arguments:
        updates = List(GameUpdateInput, required=True, description="更新列表")

    ok = Boolean(description="操作是否成功")
    updated_count = Int(description="更新数量")
    errors = List(String, description="错误信息")

    def mutate(root, info, updates):
        """Execute batch update games"""
        from backend.core.data_access import Repositories

        updated_count = 0
        errors = []

        try:
            game_repo = Repositories.games()

            for update_input in updates:
                try:
                    # Prepare update data
                    update_data = {}
                    if update_input.name is not None:
                        update_data['name'] = update_input.name
                    if update_input.name_cn is not None:
                        update_data['name_cn'] = update_input.name_cn
                    if update_input.description is not None:
                        update_data['description'] = update_input.description
                    if update_input.is_active is not None:
                        update_data['is_active'] = update_input.is_active

                    # Update game in database
                    if update_data:
                        game_repo.update(update_input.id, update_data)
                        updated_count += 1

                except Exception as e:
                    errors.append(f"Failed to update game {update_input.id}: {str(e)}")
                    logger.error(f"Batch update game error: {e}")

            return BatchUpdateGames(
                ok=len(errors) == 0,
                updated_count=updated_count,
                errors=errors if errors else None
            )

        except Exception as e:
            logger.error(f"Batch update games failed: {e}")
            return BatchUpdateGames(
                ok=False,
                updated_count=0,
                errors=[str(e)]
            )


class BatchDeleteGames(Mutation):
    """
    Batch Delete Games Mutation

    Deletes multiple games in a single operation.
    Simple implementation with basic error handling.
    """

    class Arguments:
        ids = List(Int, required=True, description="游戏ID列表")

    ok = Boolean(description="操作是否成功")
    deleted_count = Int(description="删除数量")
    errors = List(String, description="错误信息")

    def mutate(root, info, ids):
        """Execute batch delete games"""
        from backend.core.data_access import Repositories

        deleted_count = 0
        errors = []

        try:
            game_repo = Repositories.games()

            for game_id in ids:
                try:
                    game_repo.delete(game_id)
                    deleted_count += 1

                except Exception as e:
                    errors.append(f"Failed to delete game {game_id}: {str(e)}")
                    logger.error(f"Batch delete game error: {e}")

            return BatchDeleteGames(
                ok=len(errors) == 0,
                deleted_count=deleted_count,
                errors=errors if errors else None
            )

        except Exception as e:
            logger.error(f"Batch delete games failed: {e}")
            return BatchDeleteGames(
                ok=False,
                deleted_count=0,
                errors=[str(e)]
            )


class BatchMutations(graphene.ObjectType):
    """
    Batch Mutations Root Type

    Groups all batch operation mutations.
    """

    batch_create_games = BatchCreateGames.Field()
    batch_update_games = BatchUpdateGames.Field()
    batch_delete_games = BatchDeleteGames.Field()
