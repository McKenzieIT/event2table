"""
领域事件处理器

实现具体的领域事件处理逻辑
"""

from typing import Dict, Any
import logging
from backend.domain.events.game_events import (
    GameCreated,
    GameUpdated,
    GameDeleted,
    EventAddedToGame,
)
from backend.domain.events.parameter_events import (
    ParameterTypeChanged,
    ParameterCountChanged,
    CommonParametersRecalculated,
    ParameterActivated,
    ParameterDeactivated,
)
from backend.infrastructure.events.domain_event_publisher import DomainEventPublisher
from backend.core.cache.cache_system import CacheInvalidator

logger = logging.getLogger(__name__)


class GameEventHandler:
    """游戏事件处理器"""

    @staticmethod
    def handle_game_created(event: GameCreated):
        """
        处理游戏创建事件

        Args:
            event: 游戏创建事件
        """
        logger.info(f"处理游戏创建事件: GID={event.gid}, 名称={event.name}")

        # 1. 失效游戏列表缓存
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_game(event.gid)

        # 2. 发送通知(示例)
        # NotificationService.send_game_created_notification(event)

        # 3. 记录审计日志
        logger.info(
            f"游戏创建审计: GID={event.gid}, "
            f"创建者={event.created_by}, "
            f"时间={event.created_at}"
        )

    @staticmethod
    def handle_game_updated(event: GameUpdated):
        """
        处理游戏更新事件

        Args:
            event: 游戏更新事件
        """
        logger.info(f"处理游戏更新事件: GID={event.gid}")

        # 1. 失效游戏缓存
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_game(event.gid)

        # 2. 记录变更历史
        logger.info(
            f"游戏更新审计: GID={event.gid}, "
            f"变更字段={event.changed_fields}, "
            f"更新者={event.updated_by}"
        )

    @staticmethod
    def handle_game_deleted(event: GameDeleted):
        """
        处理游戏删除事件

        Args:
            event: 游戏删除事件
        """
        logger.info(f"处理游戏删除事件: GID={event.gid}")

        # 1. 失效所有相关缓存
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_game(event.gid)

        # 2. 清理关联数据(如果有)
        # CleanupService.cleanup_game_data(event.gid)

        # 3. 记录审计日志
        logger.info(f"游戏删除审计: GID={event.gid}, 删除者={event.deleted_by}")

    @staticmethod
    def handle_event_added_to_game(event: EventAddedToGame):
        """
        处理事件添加到游戏事件

        Args:
            event: 事件添加事件
        """
        logger.info(
            f"处理事件添加事件: 游戏GID={event.game_gid}, "
            f"事件ID={event.event_id}, 事件名称={event.event_name}"
        )

        # 1. 失效游戏缓存(事件数量变化)
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_game(event.game_gid)

        # 2. 失效事件列表缓存
        invalidator.invalidate_by_event(event.event_id)

        # 3. 记录审计日志
        logger.info(
            f"事件添加审计: 游戏GID={event.game_gid}, "
            f"事件={event.event_name}, "
            f"添加者={event.added_by}"
        )


class ParameterEventHandler:
    """参数事件处理器"""

    @staticmethod
    def handle_parameter_type_changed(event: ParameterTypeChanged):
        """
        处理参数类型变更事件

        Args:
            event: 参数类型变更事件
        """
        logger.info(
            f"处理参数类型变更事件: 参数ID={event.parameter_id}, "
            f"旧类型={event.old_type}, 新类型={event.new_type}"
        )

        # 1. 失效参数缓存
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_parameter(event.parameter_id)

        # 2. 失效事件缓存(参数变化)
        invalidator.invalidate_by_event(event.event_id)

        # 3. 记录审计日志
        logger.info(
            f"参数类型变更审计: 参数ID={event.parameter_id}, "
            f"类型变更={event.old_type} -> {event.new_type}, "
            f"操作者={event.changed_by}"
        )

    @staticmethod
    def handle_parameter_count_changed(event: ParameterCountChanged):
        """
        处理参数数量变更事件

        Args:
            event: 参数数量变更事件
        """
        logger.info(
            f"处理参数数量变更事件: 事件ID={event.event_id}, "
            f"旧数量={event.old_count}, 新数量={event.new_count}"
        )

        # 1. 失效事件缓存
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_event(event.event_id)

        # 2. 记录审计日志
        logger.info(
            f"参数数量变更审计: 事件ID={event.event_id}, "
            f"数量变更={event.old_count} -> {event.new_count}"
        )

    @staticmethod
    def handle_common_parameters_recalculated(event: CommonParametersRecalculated):
        """
        处理公共参数重新计算事件

        Args:
            event: 公共参数重新计算事件
        """
        logger.info(
            f"处理公共参数重新计算事件: 游戏GID={event.game_gid}, "
            f"公共参数数量={event.common_count}"
        )

        # 1. 失效公共参数缓存
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_game(event.game_gid)

        # 2. 记录审计日志
        logger.info(
            f"公共参数重新计算审计: 游戏GID={event.game_gid}, "
            f"公共参数数量={event.common_count}, "
            f"阈值={event.threshold}"
        )

    @staticmethod
    def handle_parameter_activated(event: ParameterActivated):
        """
        处理参数激活事件

        Args:
            event: 参数激活事件
        """
        logger.info(f"处理参数激活事件: 参数ID={event.parameter_id}")

        # 1. 失效参数缓存
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_parameter(event.parameter_id)

        # 2. 记录审计日志
        logger.info(
            f"参数激活审计: 参数ID={event.parameter_id}, 激活者={event.activated_by}"
        )

    @staticmethod
    def handle_parameter_deactivated(event: ParameterDeactivated):
        """
        处理参数停用事件

        Args:
            event: 参数停用事件
        """
        logger.info(f"处理参数停用事件: 参数ID={event.parameter_id}")

        # 1. 失效参数缓存
        invalidator = CacheInvalidator()
        invalidator.invalidate_by_parameter(event.parameter_id)

        # 2. 记录审计日志
        logger.info(
            f"参数停用审计: 参数ID={event.parameter_id}, 停用者={event.deactivated_by}"
        )


def register_event_handlers():
    """
    注册所有事件处理器

    在应用启动时调用,建立事件与处理器的绑定关系
    """
    from backend.infrastructure.events.domain_event_publisher import (
        get_domain_event_publisher,
    )

    logger.info("开始注册领域事件处理器...")
    publisher = get_domain_event_publisher()

    # 注册游戏事件处理器
    publisher.subscribe(GameCreated, GameEventHandler.handle_game_created)
    publisher.subscribe(GameUpdated, GameEventHandler.handle_game_updated)
    publisher.subscribe(GameDeleted, GameEventHandler.handle_game_deleted)
    publisher.subscribe(EventAddedToGame, GameEventHandler.handle_event_added_to_game)

    # 注册参数事件处理器
    publisher.subscribe(
        ParameterTypeChanged, ParameterEventHandler.handle_parameter_type_changed
    )
    publisher.subscribe(
        ParameterCountChanged, ParameterEventHandler.handle_parameter_count_changed
    )
    publisher.subscribe(
        CommonParametersRecalculated,
        ParameterEventHandler.handle_common_parameters_recalculated,
    )
    publisher.subscribe(
        ParameterActivated, ParameterEventHandler.handle_parameter_activated
    )
    publisher.subscribe(
        ParameterDeactivated, ParameterEventHandler.handle_parameter_deactivated
    )

    logger.info("领域事件处理器注册完成")


def unregister_event_handlers():
    """
    注销所有事件处理器

    在应用关闭时调用,清理资源
    """
    logger.info("注销领域事件处理器...")
    DomainEventPublisher.clear_handlers()
    logger.info("领域事件处理器已注销")
