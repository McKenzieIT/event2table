"""
扩展的GraphQL DataLoader实现

为更多查询场景添加DataLoader，进一步优化性能
"""

from promise.dataloader import DataLoader
from promise import Promise
from typing import List, Dict, Any, Optional
import logging
from backend.core.database import get_db_connection
from backend.gql_api.dataloaders.optimized_loaders import CachedDataLoader

logger = logging.getLogger(__name__)


class CategoryLoader(DataLoader):
    """
    分类批量加载器

    解决查询事件分类时的N+1问题

    Example:
        # 优化前: 100个事件 = 101次查询(1次事件 + 100次分类)
        query {
            events {
                categoryName
            }
        }

        # 优化后: 100个事件 = 2次查询(1次事件 + 1次批量分类)
    """

    def __init__(self):
        super().__init__(load_fn=self._batch_load_categories)
        self.cache_loader = CachedDataLoader('categories')

    def _batch_load_categories(self, category_ids: List[int]) -> Promise:
        """
        批量加载分类

        Args:
            category_ids: 分类ID列表

        Returns:
            Promise<List[Category>>: 分类列表
        """
        def load_from_db(ids: List[int]) -> List[Dict]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()

            # 一次性查询所有分类
            placeholders = ','.join('?' * len(ids))
            cursor.execute(f"""
                SELECT id, name
                FROM event_categories
                WHERE id IN ({placeholders})
            """, ids)

            rows = cursor.fetchall()
            conn.close()

            # 转换为字典并按ID索引
            categories_by_id = {row['id']: dict(row) for row in rows}

            # 按请求顺序返回（未找到的返回None）
            return [categories_by_id.get(cid) for cid in ids]

        return self.cache_loader._batch_load_with_cache(
            category_ids,
            load_from_db,
            ttl_l1=300,  # 分类变化较少，缓存时间更长
            ttl_l2=1800
        )


class TemplateLoader(DataLoader):
    """
    模板批量加载器

    解决查询HQL模板时的N+1问题
    """

    def __init__(self):
        super().__init__(load_fn=self._batch_load_templates)
        self.cache_loader = CachedDataLoader('templates')

    def _batch_load_templates(self, template_ids: List[int]) -> Promise:
        """
        批量加载模板

        Args:
            template_ids: 模板ID列表

        Returns:
            Promise<List[Template>>: 模板列表
        """
        def load_from_db(ids: List[int]) -> List[Dict]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(ids))
            cursor.execute(f"""
                SELECT id, name, content, category, description, created_at, updated_at
                FROM hql_templates
                WHERE id IN ({placeholders})
            """, ids)

            rows = cursor.fetchall()
            conn.close()

            templates_by_id = {row['id']: dict(row) for row in rows}
            return [templates_by_id.get(tid) for tid in ids]

        return self.cache_loader._batch_load_with_cache(
            template_ids,
            load_from_db,
            ttl_l1=120,
            ttl_l2=600
        )


class NodeLoader(DataLoader):
    """
    节点批量加载器

    解决查询事件节点时的N+1问题
    """

    def __init__(self):
        super().__init__(load_fn=self._batch_load_nodes)
        self.cache_loader = CachedDataLoader('nodes')

    def _batch_load_nodes(self, node_ids: List[int]) -> Promise:
        """
        批量加载节点

        Args:
            node_ids: 节点ID列表

        Returns:
            Promise<List[Node>>: 节点列表
        """
        def load_from_db(ids: List[int]) -> List[Dict]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(ids))
            cursor.execute(f"""
                SELECT id, game_gid, node_type, node_name, config, created_at, updated_at
                FROM event_nodes
                WHERE id IN ({placeholders})
            """, ids)

            rows = cursor.fetchall()
            conn.close()

            nodes_by_id = {row['id']: dict(row) for row in rows}
            return [nodes_by_id.get(nid) for nid in ids]

        return self.cache_loader._batch_load_with_cache(
            node_ids,
            load_from_db,
            ttl_l1=60,
            ttl_l2=300
        )


class FlowLoader(DataLoader):
    """
    流程批量加载器

    解决查询HQL流程时的N+1问题
    """

    def __init__(self):
        super().__init__(load_fn=self._batch_load_flows)
        self.cache_loader = CachedDataLoader('flows')

    def _batch_load_flows(self, flow_ids: List[int]) -> Promise:
        """
        批量加载流程

        Args:
            flow_ids: 流程ID列表

        Returns:
            Promise<List[Flow>>: 流程列表
        """
        def load_from_db(ids: List[int]) -> List[Dict]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(ids))
            cursor.execute(f"""
                SELECT id, game_gid, flow_name, flow_type, config, created_at, updated_at
                FROM hql_flows
                WHERE id IN ({placeholders})
            """, ids)

            rows = cursor.fetchall()
            conn.close()

            flows_by_id = {row['id']: dict(row) for row in rows}
            return [flows_by_id.get(fid) for fid in ids]

        return self.cache_loader._batch_load_with_cache(
            flow_ids,
            load_from_db,
            ttl_l1=60,
            ttl_l2=300
        )


class JoinConfigLoader(DataLoader):
    """
    Join配置批量加载器

    解决查询Join配置时的N+1问题
    """

    def __init__(self):
        super().__init__(load_fn=self._batch_load_join_configs)
        self.cache_loader = CachedDataLoader('join_configs')

    def _batch_load_join_configs(self, config_ids: List[int]) -> Promise:
        """
        批量加载Join配置

        Args:
            config_ids: 配置ID列表

        Returns:
            Promise<List[JoinConfig>>: Join配置列表
        """
        def load_from_db(ids: List[int]) -> List[Dict]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(ids))
            cursor.execute(f"""
                SELECT id, game_id, join_type, left_table, right_table,
                       join_condition, created_at, updated_at
                FROM join_configs
                WHERE id IN ({placeholders})
            """, ids)

            rows = cursor.fetchall()
            conn.close()

            configs_by_id = {row['id']: dict(row) for row in rows}
            return [configs_by_id.get(cid) for cid in ids]

        return self.cache_loader._batch_load_with_cache(
            config_ids,
            load_from_db,
            ttl_l1=120,
            ttl_l2=600
        )


class GameStatsLoader(DataLoader):
    """
    游戏统计批量加载器

    解决查询游戏统计信息时的N+1问题
    """

    def __init__(self):
        super().__init__(load_fn=self._batch_load_game_stats)
        self.cache_loader = CachedDataLoader('game_stats')

    def _batch_load_game_stats(self, game_gids: List[int]) -> Promise:
        """
        批量加载游戏统计

        Args:
            game_gids: 游戏GID列表

        Returns:
            Promise<List[GameStats>>: 游戏统计列表
        """
        def load_from_db(gids: List[int]) -> List[Dict]:
            """从数据库批量加载统计信息"""
            conn = get_db_connection()
            cursor = conn.cursor()

            # 批量查询事件数量
            placeholders = ','.join('?' * len(gids))
            cursor.execute(f"""
                SELECT game_gid, COUNT(*) as event_count
                FROM log_events
                WHERE game_gid IN ({placeholders})
                GROUP BY game_gid
            """, gids)

            event_counts = {row['game_gid']: row['event_count'] for row in cursor.fetchall()}

            # 批量查询参数数量
            cursor.execute(f"""
                SELECT e.game_gid, COUNT(p.id) as param_count
                FROM log_events e
                LEFT JOIN event_params p ON e.id = p.event_id
                WHERE e.game_gid IN ({placeholders})
                GROUP BY e.game_gid
            """, gids)

            param_counts = {row['game_gid']: row['param_count'] for row in cursor.fetchall()}

            # 批量查询分类数量
            cursor.execute(f"""
                SELECT e.game_gid, COUNT(DISTINCT e.category_id) as category_count
                FROM log_events e
                WHERE e.game_gid IN ({placeholders})
                AND e.category_id IS NOT NULL
                GROUP BY e.game_gid
            """, gids)

            category_counts = {row['game_gid']: row['category_count'] for row in cursor.fetchall()}

            conn.close()

            # 组装结果
            stats = []
            for gid in gids:
                stats.append({
                    'gameGid': gid,
                    'eventCount': event_counts.get(gid, 0),
                    'parameterCount': param_counts.get(gid, 0),
                    'categoryCount': category_counts.get(gid, 0)
                })

            return stats

        return self.cache_loader._batch_load_with_cache(
            game_gids,
            load_from_db,
            ttl_l1=30,  # 统计信息变化较频繁
            ttl_l2=120
        )


# 全局实例管理
_category_loader = None
_template_loader = None
_node_loader = None
_flow_loader = None
_join_config_loader = None
_game_stats_loader = None


def get_category_loader() -> CategoryLoader:
    """获取分类加载器实例"""
    global _category_loader
    if _category_loader is None:
        _category_loader = CategoryLoader()
    return _category_loader


def get_template_loader() -> TemplateLoader:
    """获取模板加载器实例"""
    global _template_loader
    if _template_loader is None:
        _template_loader = TemplateLoader()
    return _template_loader


def get_node_loader() -> NodeLoader:
    """获取节点加载器实例"""
    global _node_loader
    if _node_loader is None:
        _node_loader = NodeLoader()
    return _node_loader


def get_flow_loader() -> FlowLoader:
    """获取流程加载器实例"""
    global _flow_loader
    if _flow_loader is None:
        _flow_loader = FlowLoader()
    return _flow_loader


def get_join_config_loader() -> JoinConfigLoader:
    """获取Join配置加载器实例"""
    global _join_config_loader
    if _join_config_loader is None:
        _join_config_loader = JoinConfigLoader()
    return _join_config_loader


def get_game_stats_loader() -> GameStatsLoader:
    """获取游戏统计加载器实例"""
    global _game_stats_loader
    if _game_stats_loader is None:
        _game_stats_loader = GameStatsLoader()
    return _game_stats_loader


def clear_all_loaders():
    """清除所有DataLoader缓存"""
    global _category_loader, _template_loader, _node_loader
    global _flow_loader, _join_config_loader, _game_stats_loader

    _category_loader = None
    _template_loader = None
    _node_loader = None
    _flow_loader = None
    _join_config_loader = None
    _game_stats_loader = None
