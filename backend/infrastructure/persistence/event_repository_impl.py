"""事件仓储实现"""
from typing import Optional, List
import logging
from backend.domain.models.event import Event
from backend.domain.models.parameter import Parameter
from backend.domain.repositories.event_repository import IEventRepository
from backend.core.cache.cache_system import CacheInvalidator

logger = logging.getLogger(__name__)


class EventRepositoryImpl(IEventRepository):
    """事件仓储实现"""
    
    def __init__(self):
        # 使用现有的数据访问层
        from backend.core.data_access import Repositories
        self.event_repo = Repositories.events
        self.param_repo = Repositories.parameters
        self.game_repo = Repositories.games
    
    def find_by_id(self, event_id: int) -> Optional[Event]:
        """根据ID查找事件"""
        try:
            from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict
            
            event_dict = fetch_one_as_dict(
                "SELECT * FROM log_events WHERE id = ?",
                (event_id,)
            )
            
            if not event_dict:
                return None
            
            # 获取参数列表
            params_dict = fetch_all_as_dict(
                "SELECT * FROM event_params WHERE event_id = ? AND is_active = 1",
                (event_id,)
            )
            
            return self._to_domain_model(event_dict, params_dict)
        except Exception as e:
            logger.error(f"查找事件失败: {e}")
            return None
    
    def find_by_name(self, event_name: str, game_gid: int) -> Optional[Event]:
        """根据名称和游戏GID查找事件"""
        try:
            from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict
            
            event_dict = fetch_one_as_dict(
                "SELECT * FROM log_events WHERE event_name = ? AND game_gid = ?",
                (event_name, game_gid)
            )
            
            if not event_dict:
                return None
            
            # 获取参数列表
            params_dict = fetch_all_as_dict(
                "SELECT * FROM event_params WHERE event_id = ? AND is_active = 1",
                (event_dict['id'],)
            )
            
            return self._to_domain_model(event_dict, params_dict)
        except Exception as e:
            logger.error(f"根据名称查找事件失败: {e}")
            return None
    
    def find_by_game_gid(
        self,
        game_gid: int,
        category: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[Event]:
        """根据游戏GID查找事件列表"""
        try:
            from backend.core.utils import fetch_all_as_dict
            
            offset = (page - 1) * per_page
            
            if category:
                events_dict = fetch_all_as_dict(
                    """
                    SELECT * FROM log_events 
                    WHERE game_gid = ? AND category_id = (SELECT id FROM event_categories WHERE name = ?)
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (game_gid, category, per_page, offset)
                )
            else:
                events_dict = fetch_all_as_dict(
                    """
                    SELECT * FROM log_events 
                    WHERE game_gid = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (game_gid, per_page, offset)
                )
            
            return [self._to_domain_model(e, []) for e in events_dict]
        except Exception as e:
            logger.error(f"查找游戏事件列表失败: {e}")
            return []
    
    def count_by_game_gid(self, game_gid: int, category: Optional[str] = None) -> int:
        """统计游戏的事件数量"""
        try:
            from backend.core.utils import fetch_one_as_dict
            
            if category:
                result = fetch_one_as_dict(
                    """
                    SELECT COUNT(*) as count FROM log_events 
                    WHERE game_gid = ? AND category_id = (SELECT id FROM event_categories WHERE name = ?)
                    """,
                    (game_gid, category)
                )
            else:
                result = fetch_one_as_dict(
                    "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
                    (game_gid,)
                )
            
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"统计事件数量失败: {e}")
            return 0
    
    def save(self, event: Event) -> Event:
        """保存事件"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            
            if event.id is None:
                # 创建新事件
                event_id = execute_write(
                    """
                    INSERT INTO log_events (event_name, event_name_cn, game_gid, category_id)
                    VALUES (?, ?, ?, (SELECT id FROM event_categories WHERE name = ?))
                    """,
                    (event.name, event.description, event.game_gid, event.category),
                    return_last_id=True
                )
            else:
                # 更新事件
                execute_write(
                    """
                    UPDATE log_events 
                    SET event_name_cn = ?, 
                        category_id = (SELECT id FROM event_categories WHERE name = ?)
                    WHERE id = ?
                    """,
                    (event.description, event.category, event.id)
                )
                event_id = event.id
            
            # 失效缓存
            CacheInvalidator.invalidate_event(event_id, event.game_gid)
            
            # 返回更新后的事件
            return self.find_by_id(event_id)
        except Exception as e:
            logger.error(f"保存事件失败: {e}")
            raise
    
    def delete(self, event_id: int) -> None:
        """删除事件"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            
            # 获取事件信息用于缓存失效
            event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))
            
            # 软删除
            execute_write("UPDATE log_events SET is_active = 0 WHERE id = ?", (event_id,))
            
            # 失效缓存
            if event:
                CacheInvalidator.invalidate_event(event_id, event['game_gid'])
        except Exception as e:
            logger.error(f"删除事件失败: {e}")
            raise
    
    def search_events(self, keyword: str, game_gid: Optional[int] = None) -> List[Event]:
        """搜索事件"""
        try:
            from backend.core.utils import fetch_all_as_dict
            
            search_pattern = f"%{keyword}%"
            
            if game_gid:
                events_dict = fetch_all_as_dict(
                    """
                    SELECT * FROM log_events 
                    WHERE game_gid = ? AND (event_name LIKE ? OR event_name_cn LIKE ?)
                    ORDER BY created_at DESC
                    LIMIT 50
                    """,
                    (game_gid, search_pattern, search_pattern)
                )
            else:
                events_dict = fetch_all_as_dict(
                    """
                    SELECT * FROM log_events 
                    WHERE event_name LIKE ? OR event_name_cn LIKE ?
                    ORDER BY created_at DESC
                    LIMIT 50
                    """,
                    (search_pattern, search_pattern)
                )
            
            return [self._to_domain_model(e, []) for e in events_dict]
        except Exception as e:
            logger.error(f"搜索事件失败: {e}")
            return []
    
    def get_game_by_gid(self, game_gid: int) -> Optional[dict]:
        """根据GID获取游戏"""
        try:
            from backend.core.utils import fetch_one_as_dict
            
            return fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
        except Exception as e:
            logger.error(f"获取游戏失败: {e}")
            return None
    
    def _to_domain_model(self, event_dict: dict, params_dict: list = None) -> Event:
        """转换为领域模型"""
        # 转换参数
        parameters = []
        if params_dict:
            for param_dict in params_dict:
                parameters.append(Parameter(
                    name=param_dict['param_name'],
                    type=param_dict.get('param_type', 'string'),
                    json_path=param_dict.get('json_path', '$.'),
                    description=param_dict.get('param_name_cn') or param_dict.get('param_description')
                ))
        
        # 获取分类名称
        category_name = event_dict.get('category', '')
        if event_dict.get('category_id'):
            from backend.core.utils import fetch_one_as_dict
            cat = fetch_one_as_dict(
                "SELECT name FROM event_categories WHERE id = ?",
                (event_dict['category_id'],)
            )
            if cat:
                category_name = cat['name']
        
        return Event(
            id=event_dict['id'],
            name=event_dict['event_name'],
            category=category_name,
            game_gid=event_dict['game_gid'],
            description=event_dict.get('event_name_cn'),
            parameters=parameters,
            created_at=event_dict.get('created_at'),
            updated_at=event_dict.get('updated_at')
        )
