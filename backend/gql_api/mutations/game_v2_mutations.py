"""
Game V2 Mutations

Implements GraphQL mutation resolvers for Game V2 API with batch operations.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging

logger = logging.getLogger(__name__)


class GameV2Mutations:
    """Game V2-related GraphQL mutations"""
    
    class CreateGameV2(graphene.Mutation):
        """Create a new game (V2 API)"""
        
        class Arguments:
            input = graphene.Argument(
                lambda: __import__('backend.gql_api.types.game_v2_type', fromlist=['GameV2CreateInput']).GameV2CreateInput,
                required=True,
                description="创建游戏输入"
            )
        
        Output = lambda: __import__('backend.gql_api.types.game_v2_type', fromlist=['GameV2Result']).GameV2Result
        
        def mutate(self, info, input):
            """Execute the mutation"""
            try:
                from backend.services.games.game_service import GameService
                from backend.models.entities import GameEntity
                from backend.gql_api.types.game_v2_type import GameV2Type, GameV2Result

                # Validate ods_db
                if input.ods_db not in ['ieu_ods', 'overseas_ods']:
                    return GameV2Result.error_result(
                        errors=[f"Invalid ods_db: {input.ods_db}. Must be 'ieu_ods' or 'overseas_ods'"],
                        message="验证失败"
                    )

                # Get service
                service = GameService()

                # Create Entity (Pydantic will validate)
                game_entity = GameEntity(
                    gid=input.gid,
                    name=input.name,
                    ods_db=input.ods_db
                )

                # Call service
                result = service.create_game(game_entity)

                logger.info(f"Game created via GraphQL V2 (new architecture): {input.name} (GID: {input.gid})")

                # Convert to GameV2Type
                game_dict = result.model_dump()
                game = GameV2Type.from_dict(game_dict)

                return GameV2Result.success_result(game, "游戏创建成功")
            
            except ValueError as e:
                # Game already exists
                logger.warning(f"Game creation failed: {e}")
                return GameV2Result.error_result(errors=[str(e)], message="游戏已存在")
            
            except DomainException as e:
                logger.error(f"Domain error creating game: {e}")
                return GameV2Result.error_result(errors=[str(e)], message="创建失败")
            
            except Exception as e:
                logger.error(f"Error creating game: {e}", exc_info=True)
                return GameV2Result.error_result(errors=[str(e)], message="创建失败")
    
    class UpdateGameV2(graphene.Mutation):
        """Update an existing game (V2 API)"""
        
        class Arguments:
            gid = Int(required=True, description="游戏GID")
            input = graphene.Argument(
                lambda: __import__('backend.gql_api.types.game_v2_type', fromlist=['GameV2UpdateInput']).GameV2UpdateInput,
                required=True,
                description="更新游戏输入"
            )
        
        Output = lambda: __import__('backend.gql_api.types.game_v2_type', fromlist=['GameV2Result']).GameV2Result
        
        def mutate(self, info, gid: int, input):
            """Execute the mutation"""
            try:
                from backend.services.games.game_service import GameService
                from backend.gql_api.types.game_v2_type import GameV2Type, GameV2Result

                # Validate ods_db if provided
                if input.ods_db and input.ods_db not in ['ieu_ods', 'overseas_ods']:
                    return GameV2Result.error_result(
                        errors=[f"Invalid ods_db: {input.ods_db}. Must be 'ieu_ods' or 'overseas_ods'"],
                        message="验证失败"
                    )

                # Check if at least one field is provided
                if not any([input.name, input.ods_db, input.description, input.is_active is not None]):
                    return GameV2Result.error_result(
                        errors=["At least one field must be provided for update"],
                        message="验证失败"
                    )

                # Get service
                service = GameService()

                # Build updates dict
                update_data = {}
                if input.name:
                    update_data['name'] = input.name
                if input.ods_db:
                    update_data['ods_db'] = input.ods_db

                # Call service
                result = service.update_game(gid, update_data)

                logger.info(f"Game updated via GraphQL V2 (new architecture): GID {gid}")

                # Convert to GameV2Type
                game_dict = result.model_dump()
                game = GameV2Type.from_dict(game_dict)

                return GameV2Result.success_result(game, "游戏更新成功")
            
            except GameNotFound as e:
                logger.warning(f"Game not found: {e}")
                return GameV2Result.error_result(errors=["Game not found"], message="游戏不存在")
            
            except DomainException as e:
                logger.error(f"Domain error updating game: {e}")
                return GameV2Result.error_result(errors=[str(e)], message="更新失败")
            
            except Exception as e:
                logger.error(f"Error updating game: {e}", exc_info=True)
                return GameV2Result.error_result(errors=[str(e)], message="更新失败")
    
    class DeleteGameV2(graphene.Mutation):
        """Delete a game (V2 API)"""
        
        class Arguments:
            gid = Int(required=True, description="游戏GID")
        
        Output = lambda: __import__('backend.gql_api.types.game_v2_type', fromlist=['OperationResult']).OperationResult
        
        def mutate(self, info, gid: int):
            """Execute the mutation"""
            try:
                from backend.services.games.game_service import GameService
                from backend.gql_api.types.game_v2_type import OperationResult
                from backend.core.utils.converters import fetch_one_as_dict

                # Get service
                service = GameService()

                # Check if game has events
                event_count_result = fetch_one_as_dict(
                    "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
                    (gid,)
                )
                event_count = event_count_result['count'] if event_count_result else 0

                if event_count > 0:
                    return OperationResult.error_result(
                        errors=["Cannot delete game with events. Delete events first."],
                        message="无法删除"
                    )

                # Call service
                service.delete_game(gid)

                logger.info(f"Game deleted via GraphQL V2 (new architecture): GID {gid}")

                return OperationResult.success_result("游戏删除成功")
            
            except GameNotFound as e:
                logger.warning(f"Game not found: {e}")
                return OperationResult.error_result(errors=["Game not found"], message="游戏不存在")
            
            except CannotDeleteGameWithEvents as e:
                logger.warning(f"Cannot delete game with events: {e}")
                return OperationResult.error_result(
                    errors=["Cannot delete game with events. Delete events first."],
                    message="无法删除"
                )
            
            except Exception as e:
                logger.error(f"Error deleting game: {e}", exc_info=True)
                return OperationResult.error_result(errors=[str(e)], message="删除失败")
    
    class BatchDeleteGamesV2(graphene.Mutation):
        """Batch delete games (V2 API)"""
        
        class Arguments:
            gids = List(Int, required=True, description="游戏GID列表")
        
        Output = lambda: __import__('backend.gql_api.types.game_v2_type', fromlist=['BatchOperationResult']).BatchOperationResult
        
        def mutate(self, info, gids: list):
            """Execute the mutation"""
            try:
                from backend.services.games.game_service import GameService
                from backend.gql_api.types.game_v2_type import BatchOperationResult
                from backend.core.utils.converters import fetch_one_as_dict

                if not gids:
                    return BatchOperationResult.error_result(
                        errors=["GIDs list cannot be empty"],
                        message="验证失败"
                    )

                # Get service
                service = GameService()

                deleted_count = 0
                errors = []

                for gid in gids:
                    try:
                        # Check if game has events
                        event_count_result = fetch_one_as_dict(
                            "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
                            (gid,)
                        )
                        event_count = event_count_result['count'] if event_count_result else 0

                        if event_count > 0:
                            errors.append(f"Game {gid} has events and cannot be deleted")
                            continue

                        service.delete_game(gid)
                        deleted_count += 1
                    except ValueError as e:
                        errors.append(f"Game {gid}: {str(e)}")
                    except Exception as e:
                        errors.append(f"Failed to delete game {gid}: {str(e)}")

                logger.info(f"Batch delete games via GraphQL V2 (new architecture): {deleted_count}/{len(gids)} deleted")

                if deleted_count == len(gids):
                    return BatchOperationResult.success_result(
                        deleted_count=deleted_count,
                        message=f"成功删除 {deleted_count} 个游戏"
                    )
                else:
                    return BatchOperationResult(
                        success=False,
                        message=f"部分删除成功: {deleted_count}/{len(gids)}",
                        deleted_count=deleted_count,
                        failed_count=len(gids) - deleted_count,
                        errors=errors
                    )
            
            except Exception as e:
                logger.error(f"Error batch deleting games: {e}", exc_info=True)
                return BatchOperationResult.error_result(errors=[str(e)], message="批量删除失败")
    
    # Expose mutations as fields
    create_game_v2 = CreateGameV2.Field()
    update_game_v2 = UpdateGameV2.Field()
    delete_game_v2 = DeleteGameV2.Field()
    batch_delete_games_v2 = BatchDeleteGamesV2.Field()
