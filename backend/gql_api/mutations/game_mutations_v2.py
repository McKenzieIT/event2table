"""
Game Mutations (DDD Architecture)

Implements GraphQL mutation resolvers for Game entity using DDD architecture.
Uses the enhanced application service layer with Unit of Work.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging

logger = logging.getLogger(__name__)


class CreateGameV2(graphene.Mutation):
    """Create a new game using DDD architecture"""
    
    class Arguments:
        gid = Int(required=True, description="游戏GID")
        name = String(required=True, description="游戏名称")
        ods_db = String(required=True, description="ODS数据库名称")
    
    ok = Boolean(description="操作是否成功")
    game = Field(lambda: __import__('backend.gql_api.types.game_type', fromlist=['GameType']).GameType, description="创建的游戏")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, gid: int, name: str, ods_db: str):
        """Execute the mutation using DDD application service"""
        try:
            from backend.application.services.game_app_service_enhanced import (
                GameAppServiceEnhanced,
                GameCreateDTO,
                get_game_app_service
            )
            from backend.gql_api.types.game_type import GameType
            from backend.domain.exceptions import DomainException
            
            # Validate ods_db
            if ods_db not in ['ieu_ods', 'overseas_ods']:
                return CreateGameV2(ok=False, errors=[f"Invalid ods_db: {ods_db}. Must be 'ieu_ods' or 'overseas_ods'"])
            
            # Get application service
            service = get_game_app_service()
            
            # Create DTO
            dto = GameCreateDTO(gid=gid, name=name, ods_db=ods_db)
            
            # Call application service
            result = service.create_game(dto)
            
            logger.info(f"Game created via GraphQL (DDD): {name} (GID: {gid})")
            
            # Convert to GameType
            game_dict = result.to_dict()
            
            return CreateGameV2(ok=True, game=GameType.from_dict(game_dict) if game_dict else None)
        
        except ValueError as e:
            # Game already exists
            logger.warning(f"Game creation failed: {e}")
            return CreateGameV2(ok=False, errors=[str(e)])
        
        except DomainException as e:
            logger.error(f"Domain error creating game: {e}")
            return CreateGameV2(ok=False, errors=[str(e)])
        
        except Exception as e:
            logger.error(f"Error creating game: {e}", exc_info=True)
            return CreateGameV2(ok=False, errors=[str(e)])


class UpdateGameV2(graphene.Mutation):
    """Update an existing game using DDD architecture"""
    
    class Arguments:
        gid = Int(required=True, description="游戏GID")
        name = String(description="游戏名称")
        ods_db = String(description="ODS数据库名称")
    
    ok = Boolean(description="操作是否成功")
    game = Field(lambda: __import__('backend.gql_api.types.game_type', fromlist=['GameType']).GameType, description="更新的游戏")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, gid: int, name: str = None, ods_db: str = None):
        """Execute the mutation using DDD application service"""
        try:
            from backend.application.services.game_app_service_enhanced import (
                GameAppServiceEnhanced,
                GameUpdateDTO,
                get_game_app_service
            )
            from backend.gql_api.types.game_type import GameType
            from backend.domain.exceptions import DomainException, GameNotFound
            
            # Validate ods_db if provided
            if ods_db and ods_db not in ['ieu_ods', 'overseas_ods']:
                return UpdateGameV2(ok=False, errors=[f"Invalid ods_db: {ods_db}. Must be 'ieu_ods' or 'overseas_ods'"])
            
            # Check if at least one field is provided
            if name is None and ods_db is None:
                return UpdateGameV2(ok=False, errors=["No fields to update. Provide 'name' and/or 'ods_db'"])
            
            # Get application service
            service = get_game_app_service()
            
            # Create DTO
            dto = GameUpdateDTO(name=name, ods_db=ods_db)
            
            # Call application service
            result = service.update_game(gid, dto)
            
            logger.info(f"Game updated via GraphQL (DDD): GID {gid}")
            
            # Convert to GameType
            game_dict = result.to_dict()
            
            return UpdateGameV2(ok=True, game=GameType.from_dict(game_dict) if game_dict else None)
        
        except GameNotFound as e:
            return UpdateGameV2(ok=False, errors=[str(e)])
        
        except DomainException as e:
            logger.error(f"Domain error updating game: {e}")
            return UpdateGameV2(ok=False, errors=[str(e)])
        
        except Exception as e:
            logger.error(f"Error updating game: {e}", exc_info=True)
            return UpdateGameV2(ok=False, errors=[str(e)])


class DeleteGameV2(graphene.Mutation):
    """Delete a game using DDD architecture"""
    
    class Arguments:
        gid = Int(required=True, description="游戏GID")
        confirm = Boolean(default_value=False, description="确认删除（即使有关联数据）")
    
    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    deleted_event_count = Int(description="删除的事件数量")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, gid: int, confirm: bool = False):
        """Execute the mutation using DDD application service"""
        try:
            from backend.application.services.game_app_service_enhanced import get_game_app_service
            from backend.domain.exceptions import DomainException, GameNotFound, CannotDeleteGameWithEvents
            
            # Get application service
            service = get_game_app_service()
            
            # Check deletion impact first
            impact = service.check_deletion_impact(gid)
            
            # If no confirmation and has associated data, return impact
            if not confirm and impact['has_associated_data']:
                return DeleteGameV2(
                    ok=False,
                    errors=[f"Game has {impact['event_count']} events. Set confirm=true to force delete."],
                    deleted_event_count=0
                )
            
            # Delete the game
            result = service.delete_game(gid, force=confirm)
            
            logger.info(f"Game deleted via GraphQL (DDD): GID {gid}")
            
            return DeleteGameV2(
                ok=True,
                message="Game deleted successfully",
                deleted_event_count=result.get('deleted_event_count', 0)
            )
        
        except GameNotFound as e:
            return DeleteGameV2(ok=False, errors=[str(e)], deleted_event_count=0)
        
        except CannotDeleteGameWithEvents as e:
            return DeleteGameV2(ok=False, errors=[str(e)], deleted_event_count=0)
        
        except DomainException as e:
            logger.error(f"Domain error deleting game: {e}")
            return DeleteGameV2(ok=False, errors=[str(e)], deleted_event_count=0)
        
        except Exception as e:
            logger.error(f"Error deleting game: {e}", exc_info=True)
            return DeleteGameV2(ok=False, errors=[str(e)], deleted_event_count=0)


class CheckGameImpactV2(graphene.Mutation):
    """Check the impact of deleting a game"""
    
    class Arguments:
        gid = Int(required=True, description="游戏GID")
    
    ok = Boolean(description="操作是否成功")
    event_count = Int(description="事件数量")
    param_count = Int(description="参数数量")
    node_config_count = Int(description="节点配置数量")
    has_associated_data = Boolean(description="是否有关联数据")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, gid: int):
        """Execute the mutation using DDD application service"""
        try:
            from backend.application.services.game_app_service_enhanced import get_game_app_service
            from backend.domain.exceptions import GameNotFound
            
            # Get application service
            service = get_game_app_service()
            
            # Check impact
            impact = service.check_deletion_impact(gid)
            
            return CheckGameImpactV2(
                ok=True,
                event_count=impact['event_count'],
                param_count=impact['param_count'],
                node_config_count=impact['node_config_count'],
                has_associated_data=impact['has_associated_data']
            )
        
        except GameNotFound as e:
            return CheckGameImpactV2(ok=False, errors=[str(e)])
        
        except Exception as e:
            logger.error(f"Error checking game impact: {e}", exc_info=True)
            return CheckGameImpactV2(ok=False, errors=[str(e)])


class BatchDeleteGamesV2(graphene.Mutation):
    """Batch delete games using DDD architecture"""
    
    class Arguments:
        gids = List(Int, required=True, description="游戏GID列表")
        confirm = Boolean(default_value=False, description="确认删除（即使有关联数据）")
    
    ok = Boolean(description="操作是否成功")
    success_count = Int(description="成功删除数量")
    failed_count = Int(description="失败数量")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, gids: list, confirm: bool = False):
        """Execute the mutation using DDD application service"""
        try:
            from backend.application.services.game_app_service_enhanced import get_game_app_service
            
            if not gids:
                return BatchDeleteGamesV2(ok=False, errors=["No game GIDs provided"])
            
            # Get application service
            service = get_game_app_service()
            
            # Batch delete
            result = service.batch_delete_games(gids, force=confirm)
            
            logger.info(f"Batch deleted {result['success_count']} games via GraphQL (DDD)")
            
            return BatchDeleteGamesV2(
                ok=True,
                success_count=result['success_count'],
                failed_count=result['failed_count'],
                errors=result['errors']
            )
        
        except Exception as e:
            logger.error(f"Error batch deleting games: {e}", exc_info=True)
            return BatchDeleteGamesV2(ok=False, errors=[str(e)])


class GameMutationsV2:
    """Container for game mutations (DDD Architecture)"""
    CreateGame = CreateGameV2
    UpdateGame = UpdateGameV2
    DeleteGame = DeleteGameV2
    CheckGameImpact = CheckGameImpactV2
    BatchDeleteGames = BatchDeleteGamesV2
