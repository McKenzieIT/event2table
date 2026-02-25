"""
Game Mutations

Implements GraphQL mutation resolvers for Game entity.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging

logger = logging.getLogger(__name__)


class CreateGame(graphene.Mutation):
    """Create a new game"""
    
    class Arguments:
        gid = Int(required=True, description="游戏GID")
        name = String(required=True, description="游戏名称")
        ods_db = String(required=True, description="ODS数据库名称")
    
    ok = Boolean(description="操作是否成功")
    game = Field(lambda: __import__('backend.gql_api.types.game_type', fromlist=['GameType']).GameType, description="创建的游戏")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, gid: int, name: str, ods_db: str):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.gql_api.types.game_type import GameType
            
            # Validate ods_db
            if ods_db not in ['ieu_ods', 'overseas_ods']:
                return CreateGame(ok=False, errors=[f"Invalid ods_db: {ods_db}"])
            
            # Create game
            execute_write(
                "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                (gid, name, ods_db)
            )
            
            # Clear cache using enhanced invalidator
            cache_invalidator_enhanced.invalidate_key('games.list')
            cache_invalidator_enhanced.invalidate_key('dashboard_statistics')
            
            logger.info(f"Game created via GraphQL: {name} (GID: {gid})")
            
            # Return created game
            from backend.core.data_access import Repositories
            game = Repositories.GAMES.find_by_field("gid", gid)
            
            return CreateGame(ok=True, game=GameType.from_dict(game) if game else None)
            
        except Exception as e:
            logger.error(f"Error creating game: {e}", exc_info=True)
            return CreateGame(ok=False, errors=[str(e)])


class UpdateGame(graphene.Mutation):
    """Update an existing game"""
    
    class Arguments:
        gid = Int(required=True, description="游戏GID")
        name = String(description="游戏名称")
        ods_db = String(description="ODS数据库名称")
    
    ok = Boolean(description="操作是否成功")
    game = Field(lambda: __import__('backend.gql_api.types.game_type', fromlist=['GameType']).GameType, description="更新的游戏")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, gid: int, name: str = None, ods_db: str = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            from backend.gql_api.types.game_type import GameType
            
            # Build update query
            updates = []
            params = []
            
            if name:
                updates.append("name = ?")
                params.append(name)
            
            if ods_db:
                if ods_db not in ['ieu_ods', 'overseas_ods']:
                    return UpdateGame(ok=False, errors=[f"Invalid ods_db: {ods_db}"])
                updates.append("ods_db = ?")
                params.append(ods_db)
            
            if not updates:
                return UpdateGame(ok=False, errors=["No fields to update"])
            
            params.append(gid)
            query = f"UPDATE games SET {', '.join(updates)} WHERE gid = ?"
            
            execute_write(query, tuple(params))
            
            # Clear cache using enhanced invalidator
            cache_invalidator_enhanced.invalidate_game_related(gid)
            
            logger.info(f"Game updated via GraphQL: GID {gid}")
            
            # Return updated game
            from backend.core.data_access import Repositories
            game = Repositories.GAMES.find_by_field("gid", gid)
            
            return UpdateGame(ok=True, game=GameType.from_dict(game) if game else None)
            
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
    
    def mutate(self, info, gid: int, confirm: bool = False):
        """Execute the mutation"""
        try:
            from backend.core.utils import fetch_one_as_dict, execute_write
            from backend.core.cache.invalidator import cache_invalidator_enhanced
            
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
                    errors=[f"Game has {event_count['count']} events. Set confirm=true to force delete."]
                )
            
            # Delete game (cascade delete handled by database or manually)
            if confirm and event_count['count'] > 0:
                # Delete associated data first
                execute_write(
                    "DELETE FROM event_params WHERE event_id IN "
                    "(SELECT id FROM log_events WHERE game_gid = ?)",
                    (gid,)
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
