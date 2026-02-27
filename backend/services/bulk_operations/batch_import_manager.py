"""
Batch Import Manager - 占位实现

注意：此模块在DDD清理中被移除，保留占位以满足测试导入。
批量导入功能应通过Service层实现，而非单独的Manager类。
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BatchImportManager:
    """
    批量导入管理器 (占位实现)

    注意：完整的批量导入功能已迁移到各模块的Service层
    """

    def __init__(self):
        """初始化批量导入管理器"""
        logger.warning("BatchImportManager is deprecated, use Service layer instead")

    def _prepare_event_record(
        self,
        event_data: Dict[str, Any],
        game_gid: int,
        category_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        准备事件记录 (占位实现)

        Args:
            event_data: 事件数据
            game_gid: 游戏GID
            category_id: 类别ID

        Returns:
            准备好的事件记录
        """
        # 占位实现 - 返回原始数据
        logger.warning("_prepare_event_record is deprecated, use EventService instead")
        return event_data

    def import_events(
        self,
        events_data: List[Dict[str, Any]],
        game_gid: int
    ) -> List[Dict[str, Any]]:
        """
        批量导入事件 (占位实现)

        Args:
            events_data: 事件数据列表
            game_gid: 游戏GID

        Returns:
            导入结果列表
        """
        logger.warning("import_events is deprecated, use EventService.create_batch instead")
        return []

    def import_parameters(
        self,
        parameters_data: List[Dict[str, Any]],
        event_id: int
    ) -> List[Dict[str, Any]]:
        """
        批量导入参数 (占位实现)

        Args:
            parameters_data: 参数数据列表
            event_id: 事件ID

        Returns:
            导入结果列表
        """
        logger.warning("import_parameters is deprecated, use ParameterService.create_batch instead")
        return []


# 全局单例实例
batch_import_manager = BatchImportManager()
