"""
GraphQL DataLoader优化实现

解决N+1查询问题,提升GraphQL性能
"""

from promise.dataloader import DataLoader
from promise import Promise
from typing import List, Dict, Any, Optional
import logging
from backend.core.database import get_db_connection
from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator

logger = logging.getLogger(__name__)


class CachedDataLoader:
    """
    带缓存的DataLoader基类
    
    结合DataLoader的批量加载和缓存系统的性能优势
    """
    
    def __init__(self, cache_prefix: str):
        self.cache = HierarchicalCache()
        self.cache_prefix = cache_prefix
    
    def _get_cache_key(self, key: Any) -> str:
        """生成缓存键"""
        return f"{self.cache_prefix}:{key}"
    
    def _batch_load_with_cache(
        self,
        keys: List[Any],
        batch_load_fn: callable,
        ttl_l1: int = 60,
        ttl_l2: int = 300
    ) -> Promise:
        """
        带缓存的批量加载
        
        Args:
            keys: 键列表
            batch_load_fn: 批量加载函数
            ttl_l1: L1缓存TTL
            ttl_l2: L2缓存TTL
        
        Returns:
            Promise<List<Any>>
        """
        results = []
        uncached_keys = []
        uncached_indices = []
        
        # 1. 先从缓存获取
        for i, key in enumerate(keys):
            cache_key = self._get_cache_key(key)
            cached_value = self.cache.get(cache_key)
            
            if cached_value is not None:
                results.append(cached_value)
                logger.debug(f"DataLoader缓存命中: {cache_key}")
            else:
                results.append(None)
                uncached_keys.append(key)
                uncached_indices.append(i)
        
        # 2. 批量加载未缓存的数据
        if uncached_keys:
            logger.debug(f"DataLoader批量加载: {len(uncached_keys)}个键")
            loaded_values = batch_load_fn(uncached_keys)
            
            # 3. 填充结果并写入缓存
            for idx, key, value in zip(uncached_indices, uncached_keys, loaded_values):
                results[idx] = value
                
                # 写入缓存
                cache_key = self._get_cache_key(key)
                self.cache.set(cache_key, value, ttl_l1=ttl_l1, ttl_l2=ttl_l2)
        
        return Promise.resolve(results)


class EventLoader(DataLoader):
    """
    事件批量加载器
    
    解决查询游戏事件时的N+1问题
    
    Example:
        # 优化前: 10个游戏 = 11次查询(1次游戏 + 10次事件)
        query {
            games {
                events { id name }
            }
        }
        
        # 优化后: 10个游戏 = 2次查询(1次游戏 + 1次批量事件)
    """
    
    def __init__(self):
        super().__init__(load_fn=self._batch_load_events)
        self.cache_loader = CachedDataLoader('events')
    
    def _batch_load_events(self, game_gids: List[int]) -> Promise:
        """
        批量加载事件
        
        Args:
            game_gids: 游戏GID列表
        
        Returns:
            Promise<List<List[Event]>>: 每个游戏的事件列表
        """
        def load_from_db(gids: List[int]) -> List[List[Dict]]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 一次性查询所有游戏的事件
            placeholders = ','.join('?' * len(gids))
            cursor.execute(f"""
                SELECT * FROM log_events
                WHERE game_gid IN ({placeholders})
                ORDER BY game_gid, id
            """, gids)
            
            rows = cursor.fetchall()
            conn.close()
            
            # 按游戏GID分组
            events_by_game = {gid: [] for gid in gids}
            for row in rows:
                event = dict(row)
                game_gid = event['game_gid']
                events_by_game[game_gid].append(event)
            
            # 按请求顺序返回
            return [events_by_game.get(gid, []) for gid in gids]
        
        return self.cache_loader._batch_load_with_cache(
            game_gids,
            load_from_db,
            ttl_l1=60,
            ttl_l2=300
        )


class ParameterLoader(DataLoader):
    """
    参数批量加载器
    
    解决查询事件参数时的N+1问题
    """
    
    def __init__(self):
        super().__init__(load_fn=self._batch_load_parameters)
        self.cache_loader = CachedDataLoader('parameters')
    
    def _batch_load_parameters(self, event_ids: List[int]) -> Promise:
        """
        批量加载参数
        
        Args:
            event_ids: 事件ID列表
        
        Returns:
            Promise<List<List[Parameter]>>: 每个事件的参数列表
        """
        def load_from_db(ids: List[int]) -> List[List[Dict]]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 一次性查询所有事件的参数
            placeholders = ','.join('?' * len(ids))
            cursor.execute(f"""
                SELECT * FROM event_params
                WHERE event_id IN ({placeholders})
                AND is_active = 1
                ORDER BY event_id, id
            """, ids)
            
            rows = cursor.fetchall()
            conn.close()
            
            # 按事件ID分组
            params_by_event = {eid: [] for eid in ids}
            for row in rows:
                param = dict(row)
                event_id = param['event_id']
                params_by_event[event_id].append(param)
            
            # 按请求顺序返回
            return [params_by_event.get(eid, []) for eid in ids]
        
        return self.cache_loader._batch_load_with_cache(
            event_ids,
            load_from_db,
            ttl_l1=60,
            ttl_l2=300
        )


class GameLoader(DataLoader):
    """
    游戏批量加载器
    
    解决查询事件所属游戏时的N+1问题
    """
    
    def __init__(self):
        super().__init__(load_fn=self._batch_load_games)
        self.cache_loader = CachedDataLoader('games')
    
    def _batch_load_games(self, game_gids: List[int]) -> Promise:
        """
        批量加载游戏
        
        Args:
            game_gids: 游戏GID列表
        
        Returns:
            Promise<List<Game>>: 游戏列表
        """
        def load_from_db(gids: List[int]) -> List[Dict]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 一次性查询所有游戏
            placeholders = ','.join('?' * len(gids))
            cursor.execute(f"""
                SELECT * FROM games
                WHERE gid IN ({placeholders})
            """, gids)
            
            rows = cursor.fetchall()
            conn.close()
            
            # 构建游戏字典
            games_dict = {row['gid']: dict(row) for row in rows}
            
            # 按请求顺序返回
            return [games_dict.get(gid) for gid in gids]
        
        return self.cache_loader._batch_load_with_cache(
            game_gids,
            load_from_db,
            ttl_l1=120,
            ttl_l2=600
        )


# 全局DataLoader实例
_event_loader = None
_parameter_loader = None
_game_loader = None


def get_event_loader() -> EventLoader:
    """获取事件加载器实例"""
    global _event_loader
    if _event_loader is None:
        _event_loader = EventLoader()
    return _event_loader


def get_parameter_loader() -> ParameterLoader:
    """获取参数加载器实例"""
    global _parameter_loader
    if _parameter_loader is None:
        _parameter_loader = ParameterLoader()
    return _parameter_loader


def get_game_loader() -> GameLoader:
    """获取游戏加载器实例"""
    global _game_loader
    if _game_loader is None:
        _game_loader = GameLoader()
    return _game_loader


def clear_dataloader_cache():
    """清除DataLoader缓存"""
    global _event_loader, _parameter_loader, _game_loader
    _event_loader = None
    _parameter_loader = None
    _game_loader = None
    logger.info("DataLoader缓存已清除")
