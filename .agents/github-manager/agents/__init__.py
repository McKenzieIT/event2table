"""
GitHub Manager Agents Package

智能代理系统，支持多代理协作。
"""

from .state_machine import StateMachine, ManagerState, StateRecord, StateTransition
from .decision_engine import DecisionEngine, DecisionRule, Decision, DecisionOutcome

__all__ = [
    "StateMachine",
    "ManagerState",
    "StateRecord",
    "StateTransition",
    "DecisionEngine",
    "DecisionRule",
    "Decision",
    "DecisionOutcome",
]

__version__ = "1.0.0"
