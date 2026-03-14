"""
HQL V2 - 抽象模型定义

这些模型完全脱离业务逻辑, 可以独立使用
"""

from .event import Condition, Event, Field, JoinConfig

__all__ = ["Event", "Field", "Condition", "JoinConfig"]
