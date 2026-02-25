"""HQL仓储实现"""
from typing import Optional, List, Dict, Any
import logging
import json
from backend.domain.repositories.hql_repository import IHQLRepository
from backend.core.cache.cache_system import CacheInvalidator

logger = logging.getLogger(__name__)


class HQLRepositoryImpl(IHQLRepository):
    """HQL仓储实现"""
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取事件"""
        try:
            from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict
            
            event = fetch_one_as_dict(
                """
                SELECT le.*, ec.name as category_name
                FROM log_events le
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE le.id = ?
                """,
                (event_id,)
            )
            
            if not event:
                return None
            
            # 获取参数
            params = fetch_all_as_dict(
                """
                SELECT ep.*, pt.name as template_name
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.event_id = ? AND ep.is_active = 1
                """,
                (event_id,)
            )
            
            event['parameters'] = params
            return event
        except Exception as e:
            logger.error(f"获取事件失败: {e}")
            return None
    
    def save_history(self, history: Dict[str, Any]) -> None:
        """保存HQL历史"""
        try:
            from backend.core.utils import execute_write
            
            execute_write(
                """
                INSERT INTO hql_history (game_gid, event_ids, hql_content, mode, options, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    history.get('game_gid'),
                    json.dumps(history.get('event_ids', [])),
                    history.get('hql_content'),
                    history.get('mode', 'single'),
                    json.dumps(history.get('options', {})),
                    history.get('created_by', 'system')
                )
            )
            
            # 失效缓存
            if history.get('game_gid'):
                CacheInvalidator.invalidate_game(history['game_gid'])
        except Exception as e:
            logger.error(f"保存HQL历史失败: {e}")
            raise
    
    def get_history(
        self,
        game_gid: Optional[int] = None,
        page: int = 1,
        per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """获取HQL历史"""
        try:
            from backend.core.utils import fetch_all_as_dict
            
            offset = (page - 1) * per_page
            
            if game_gid:
                history = fetch_all_as_dict(
                    """
                    SELECT * FROM hql_history
                    WHERE game_gid = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (game_gid, per_page, offset)
                )
            else:
                history = fetch_all_as_dict(
                    """
                    SELECT * FROM hql_history
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                    """,
                    (per_page, offset)
                )
            
            # 解析JSON字段
            for h in history:
                if h.get('event_ids'):
                    try:
                        h['event_ids'] = json.loads(h['event_ids'])
                    except:
                        h['event_ids'] = []
                if h.get('options'):
                    try:
                        h['options'] = json.loads(h['options'])
                    except:
                        h['options'] = {}
            
            return history
        except Exception as e:
            logger.error(f"获取HQL历史失败: {e}")
            return []
    
    def count_history(self, game_gid: Optional[int] = None) -> int:
        """统计HQL历史数量"""
        try:
            from backend.core.utils import fetch_one_as_dict
            
            if game_gid:
                result = fetch_one_as_dict(
                    "SELECT COUNT(*) as count FROM hql_history WHERE game_gid = ?",
                    (game_gid,)
                )
            else:
                result = fetch_one_as_dict("SELECT COUNT(*) as count FROM hql_history")
            
            return result['count'] if result else 0
        except Exception as e:
            logger.error(f"统计HQL历史数量失败: {e}")
            return 0
    
    def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取HQL模板"""
        try:
            from backend.core.utils import fetch_all_as_dict
            
            if category:
                templates = fetch_all_as_dict(
                    """
                    SELECT * FROM hql_templates
                    WHERE category = ? AND is_active = 1
                    ORDER BY created_at DESC
                    """,
                    (category,)
                )
            else:
                templates = fetch_all_as_dict(
                    """
                    SELECT * FROM hql_templates
                    WHERE is_active = 1
                    ORDER BY created_at DESC
                    """
                )
            
            return templates
        except Exception as e:
            logger.error(f"获取HQL模板失败: {e}")
            return []
    
    def save_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """保存HQL模板"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            
            if template.get('id'):
                # 更新
                execute_write(
                    """
                    UPDATE hql_templates
                    SET name = ?, content = ?, category = ?, description = ?
                    WHERE id = ?
                    """,
                    (
                        template['name'],
                        template['content'],
                        template.get('category'),
                        template.get('description'),
                        template['id']
                    )
                )
                template_id = template['id']
            else:
                # 创建
                template_id = execute_write(
                    """
                    INSERT INTO hql_templates (name, content, category, description)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        template['name'],
                        template['content'],
                        template.get('category'),
                        template.get('description')
                    ),
                    return_last_id=True
                )
            
            # 返回保存的模板
            return fetch_one_as_dict(
                "SELECT * FROM hql_templates WHERE id = ?",
                (template_id,)
            )
        except Exception as e:
            logger.error(f"保存HQL模板失败: {e}")
            raise
    
    def delete_template(self, template_id: int) -> None:
        """删除HQL模板"""
        try:
            from backend.core.utils import execute_write
            
            # 软删除
            execute_write(
                "UPDATE hql_templates SET is_active = 0 WHERE id = ?",
                (template_id,)
            )
        except Exception as e:
            logger.error(f"删除HQL模板失败: {e}")
            raise
