"""游戏仓储实现"""
from typing import Optional, List
import logging
from backend.domain.models.game import Game
from backend.domain.models.event import Event
from backend.domain.models.parameter import Parameter
from backend.domain.repositories.game_repository import IGameRepository
from backend.core.cache.cache_system import CacheInvalidator

logger = logging.getLogger(__name__)


class GameRepositoryImpl(IGameRepository):
    """游戏仓储实现"""
    
    def __init__(self):
        # 使用现有的数据访问层
        from backend.models.repositories.games import GameRepository as GameDataRepository
        from backend.models.repositories.events import EventRepository as EventDataRepository
        self.game_data_repo = GameDataRepository()
        self.event_data_repo = EventDataRepository()
    
    def find_by_gid(self, gid: int) -> Optional[Game]:
        """根据GID查找游戏"""
        try:
            game_dict = self.game_data_repo.find_by_gid(gid)
            if not game_dict:
                return None
            
            # 获取事件列表
            events_dict = self.event_data_repo.find_by_game_gid(gid)
            
            # 转换为领域模型
            return self._to_domain_model(game_dict, events_dict)
        except Exception as e:
            logger.error(f"查找游戏失败: {e}")
            return None
    
    def find_all(self) -> List[Game]:
        """查找所有游戏"""
        try:
            games_dict = self.game_data_repo.find_all()
            return [self._to_domain_model(g, []) for g in games_dict]
        except Exception as e:
            logger.error(f"查找所有游戏失败: {e}")
            return []
    
    def save(self, game: Game) -> Game:
        """保存游戏"""
        try:
            if game._deleted:
                # 删除游戏
                self.game_data_repo.delete(game.gid)
                CacheInvalidator.invalidate_game(game.gid)
                return game
            
            # 检查是否是新游戏
            existing = self.game_data_repo.find_by_gid(game.gid)
            
            if existing:
                # 更新游戏
                self.game_data_repo.update(game.gid, {
                    'name': game.name,
                    'ods_db': game.ods_db
                })
            else:
                # 创建新游戏
                self.game_data_repo.create({
                    'gid': game.gid,
                    'name': game.name,
                    'ods_db': game.ods_db
                })
            
            # 失效缓存
            CacheInvalidator.invalidate_game(game.gid)
            
            # 返回更新后的游戏
            return self.find_by_gid(game.gid)
        except Exception as e:
            logger.error(f"保存游戏失败: {e}")
            raise
    
    def delete(self, game: Game) -> None:
        """删除游戏"""
        try:
            self.game_data_repo.delete(game.gid)
            CacheInvalidator.invalidate_game(game.gid)
        except Exception as e:
            logger.error(f"删除游戏失败: {e}")
            raise
    
    def find_by_name(self, name: str) -> List[Game]:
        """根据名称查找游戏"""
        try:
            games_dict = self.game_data_repo.search_by_name(f"%{name}%")
            return [self._to_domain_model(g, []) for g in games_dict]
        except Exception as e:
            logger.error(f"根据名称查找游戏失败: {e}")
            return []
    
    def _to_domain_model(self, game_dict: dict, events_dict: list = None) -> Game:
        """转换为领域模型"""
        events = []
        if events_dict:
            for event_dict in events_dict:
                # 转换参数
                parameters = []
                if event_dict.get('parameters'):
                    for param_dict in event_dict['parameters']:
                        parameters.append(Parameter(
                            name=param_dict['param_name'],
                            type=param_dict.get('param_type', 'string'),
                            json_path=param_dict.get('json_path', '$.'),
                            description=param_dict.get('param_description')
                        ))
                
                events.append(Event(
                    id=event_dict['id'],
                    name=event_dict['event_name'],
                    category=event_dict.get('category', ''),
                    game_gid=event_dict['game_gid'],
                    description=event_dict.get('event_name_cn'),
                    parameters=parameters,
                    created_at=event_dict.get('created_at'),
                    updated_at=event_dict.get('updated_at')
                ))
        
        return Game(
            gid=game_dict['gid'],
            name=game_dict['name'],
            ods_db=game_dict['ods_db'],
            events=events,
            created_at=game_dict.get('created_at'),
            updated_at=game_dict.get('updated_at')
        )
