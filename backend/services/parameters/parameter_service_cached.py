"""
参数服务缓存增强版

为ParameterService添加多级缓存支持,提升性能
"""

from typing import List, Dict, Any, Optional
import json
import hashlib
from backend.services.parameters.event_param_manager import EventParameterManager
from backend.services.parameters.param_type_manager import ParameterTypeManager
from backend.services.parameters.common_params import CommonParameterCalculator
from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator
import logging

logger = logging.getLogger(__name__)


class ParameterServiceCached:
    """
    参数服务缓存增强版
    
    特点:
    - 使用多级缓存存储参数查询结果
    - 自动缓存失效
    - 支持参数列表缓存
    - 支持公共参数缓存
    """
    
    def __init__(self):
        self.event_param_manager = EventParameterManager()
        self.type_manager = ParameterTypeManager()
        self.common_calculator = CommonParameterCalculator()
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)
    
    def get_parameters_by_event(
        self,
        event_id: int,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取事件的参数列表(带缓存)
        
        Args:
            event_id: 事件ID
            use_cache: 是否使用缓存
            
        Returns:
            List[Dict]: 参数列表
        """
        cache_key = f"parameters:event:{event_id}"
        
        if use_cache:
            # 尝试从缓存获取
            cached_params = self.cache.get(cache_key)
            if cached_params:
                logger.debug(f"参数列表缓存命中: {cache_key}")
                return cached_params
        
        # 从数据库查询
        params = self.event_param_manager.get_parameters_by_event(event_id)
        
        if use_cache:
            # 写入缓存
            self.cache.set(cache_key, params, ttl_l2=1800)  # 30分钟缓存
            logger.debug(f"参数列表已缓存: {cache_key}")
        
        return params
    
    def get_parameter_by_id(
        self,
        parameter_id: int,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        根据ID获取参数(带缓存)
        
        Args:
            parameter_id: 参数ID
            use_cache: 是否使用缓存
            
        Returns:
            Optional[Dict]: 参数信息
        """
        cache_key = f"parameter:id:{parameter_id}"
        
        if use_cache:
            # 尝试从缓存获取
            cached_param = self.cache.get(cache_key)
            if cached_param:
                logger.debug(f"参数缓存命中: {cache_key}")
                return cached_param
        
        # 从数据库查询
        param = self.event_param_manager.get_parameter_by_id(parameter_id)
        
        if use_cache and param:
            # 写入缓存
            self.cache.set(cache_key, param, ttl_l2=1800)
            logger.debug(f"参数已缓存: {cache_key}")
        
        return param
    
    def get_parameters_by_game(
        self,
        game_gid: int,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取游戏的所有参数(带缓存)
        
        Args:
            game_gid: 游戏GID
            use_cache: 是否使用缓存
            
        Returns:
            List[Dict]: 参数列表
        """
        cache_key = f"parameters:game:{game_gid}"
        
        if use_cache:
            # 尝试从缓存获取
            cached_params = self.cache.get(cache_key)
            if cached_params:
                logger.debug(f"游戏参数缓存命中: {cache_key}")
                return cached_params
        
        # 从数据库查询
        params = self.event_param_manager.get_parameters_by_game(game_gid)
        
        if use_cache:
            # 写入缓存
            self.cache.set(cache_key, params, ttl_l2=1800)
            logger.debug(f"游戏参数已缓存: {cache_key}")
        
        return params
    
    def get_common_parameters(
        self,
        game_gid: int,
        threshold: float = 0.8,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取公共参数(带缓存)
        
        Args:
            game_gid: 游戏GID
            threshold: 公共参数阈值
            use_cache: 是否使用缓存
            
        Returns:
            List[Dict]: 公共参数列表
        """
        cache_key = f"parameters:common:{game_gid}:{threshold}"
        
        if use_cache:
            # 尝试从缓存获取
            cached_params = self.cache.get(cache_key)
            if cached_params:
                logger.debug(f"公共参数缓存命中: {cache_key}")
                return cached_params
        
        # 计算公共参数
        params = self.common_calculator.calculate_common_parameters(game_gid, threshold)
        
        if use_cache:
            # 写入缓存
            self.cache.set(cache_key, params, ttl_l2=3600)  # 1小时缓存
            logger.debug(f"公共参数已缓存: {cache_key}")
        
        return params
    
    def create_parameter(
        self,
        event_id: int,
        name: str,
        param_type: str,
        json_path: str,
        description: str = None
    ) -> Dict[str, Any]:
        """
        创建参数(自动失效缓存)
        
        Args:
            event_id: 事件ID
            name: 参数名称
            param_type: 参数类型
            json_path: JSON路径
            description: 描述
            
        Returns:
            Dict: 创建的参数
        """
        # 创建参数
        param = self.event_param_manager.create_parameter(
            event_id=event_id,
            name=name,
            param_type=param_type,
            json_path=json_path,
            description=description
        )
        
        # 失效相关缓存
        self._invalidate_parameter_cache(event_id, param.get('game_gid'))
        
        logger.info(f"参数创建成功: {name}, 已失效相关缓存")
        
        return param
    
    def update_parameter(
        self,
        parameter_id: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新参数(自动失效缓存)
        
        Args:
            parameter_id: 参数ID
            data: 更新数据
            
        Returns:
            Dict: 更新后的参数
        """
        # 更新参数
        param = self.event_param_manager.update_parameter(parameter_id, data)
        
        # 失效相关缓存
        self._invalidate_parameter_cache(
            param.get('event_id'),
            param.get('game_gid')
        )
        
        logger.info(f"参数更新成功: {parameter_id}, 已失效相关缓存")
        
        return param
    
    def delete_parameter(self, parameter_id: int) -> bool:
        """
        删除参数(自动失效缓存)
        
        Args:
            parameter_id: 参数ID
            
        Returns:
            bool: 是否成功
        """
        # 获取参数信息(用于失效缓存)
        param = self.event_param_manager.get_parameter_by_id(parameter_id)
        
        if not param:
            return False
        
        event_id = param.get('event_id')
        game_gid = param.get('game_gid')
        
        # 删除参数
        success = self.event_param_manager.delete_parameter(parameter_id)
        
        if success:
            # 失效相关缓存
            self._invalidate_parameter_cache(event_id, game_gid)
            logger.info(f"参数删除成功: {parameter_id}, 已失效相关缓存")
        
        return success
    
    def change_parameter_type(
        self,
        parameter_id: int,
        new_type: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        更改参数类型(带缓存验证)
        
        Args:
            parameter_id: 参数ID
            new_type: 新类型
            use_cache: 是否使用缓存
            
        Returns:
            Dict: 更改结果
        """
        # 获取参数信息
        param = self.get_parameter_by_id(parameter_id, use_cache=use_cache)
        
        if not param:
            return {'success': False, 'error': '参数不存在'}
        
        old_type = param.get('type')
        
        # 验证类型变更
        validation = self.type_manager.validate_type_change(old_type, new_type)
        
        if not validation['valid']:
            return {'success': False, 'error': validation['reason']}
        
        # 执行类型变更
        result = self.type_manager.change_type(parameter_id, new_type)
        
        if result['success']:
            # 失效缓存
            self._invalidate_parameter_cache(
                param.get('event_id'),
                param.get('game_gid')
            )
            logger.info(f"参数类型变更成功: {parameter_id} {old_type} -> {new_type}")
        
        return result
    
    def _invalidate_parameter_cache(self, event_id: int = None, game_gid: int = None):
        """
        失效参数相关缓存
        
        Args:
            event_id: 事件ID
            game_gid: 游戏GID
        """
        if event_id:
            # 失效事件的参数缓存
            self.cache.delete(f"parameters:event:{event_id}")
        
        if game_gid:
            # 失效游戏的参数缓存
            self.cache.delete(f"parameters:game:{game_gid}")
            # 失效公共参数缓存(使用通配符)
            self.invalidator.invalidate_by_game(game_gid)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 缓存统计
        """
        return self.cache.get_stats()
