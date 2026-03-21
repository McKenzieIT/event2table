"""
GitHub Manager Agent System

智能代理系统，处理复杂的GitHub管理场景。
"""

from .agents import StateMachine, DecisionEngine, ManagerState

__all__ = [
    "StateMachine",
    "DecisionEngine",
    "ManagerState",
]

__version__ = "1.0.0"
