"""
GitHub Manager State Machine

状态机驱动的工作流管理，确保流程可控、可追溯。
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import json


class ManagerState(Enum):
    """管理器状态"""
    # 初始状态
    IDLE = "idle"
    
    # 扫描阶段
    SCANNING = "scanning"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    
    # 分析阶段
    ANALYZING = "analyzing"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_FAILED = "analysis_failed"
    
    # 解决阶段
    RESOLVING = "resolving"
    RESOLUTION_COMPLETED = "resolution_completed"
    RESOLUTION_FAILED = "resolution_failed"
    
    # 确认阶段
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    
    # 执行阶段
    EXECUTING = "executing"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_ABORTED = "execution_aborted"
    
    # 报告阶段
    REPORTING = "reporting"
    REPORT_COMPLETED = "report_completed"
    
    # 学习阶段
    LEARNING = "learning"
    LEARNING_COMPLETED = "learning_completed"
    
    # 终态
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StateRecord:
    """状态记录"""
    from_state: ManagerState
    to_state: ManagerState
    trigger: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateTransition:
    """状态转换"""
    from_state: ManagerState
    to_state: ManagerState
    trigger: str
    action: Optional[str] = None
    guard: Optional[str] = None  # 转换条件


# 状态转换表
STATE_TRANSITIONS: List[StateTransition] = [
    # 扫描阶段
    StateTransition(ManagerState.IDLE, ManagerState.SCANNING, "start_scan"),
    StateTransition(ManagerState.SCANNING, ManagerState.SCAN_COMPLETED, "scan_success"),
    StateTransition(ManagerState.SCANNING, ManagerState.SCAN_FAILED, "scan_failure"),
    
    # 分析阶段
    StateTransition(ManagerState.SCAN_COMPLETED, ManagerState.ANALYZING, "start_analysis"),
    StateTransition(ManagerState.ANALYZING, ManagerState.ANALYSIS_COMPLETED, "analysis_success"),
    StateTransition(ManagerState.ANALYZING, ManagerState.ANALYSIS_FAILED, "analysis_failure"),
    
    # 解决阶段
    StateTransition(ManagerState.ANALYSIS_COMPLETED, ManagerState.RESOLVING, "start_resolution"),
    StateTransition(ManagerState.RESOLVING, ManagerState.RESOLUTION_COMPLETED, "resolution_success"),
    StateTransition(ManagerState.RESOLVING, ManagerState.RESOLUTION_FAILED, "resolution_failure"),
    
    # 确认阶段
    StateTransition(ManagerState.RESOLUTION_COMPLETED, ManagerState.AWAITING_CONFIRMATION, "request_confirmation"),
    StateTransition(ManagerState.AWAITING_CONFIRMATION, ManagerState.CONFIRMED, "user_confirmed"),
    StateTransition(ManagerState.AWAITING_CONFIRMATION, ManagerState.REJECTED, "user_rejected"),
    
    # 执行阶段
    StateTransition(ManagerState.CONFIRMED, ManagerState.EXECUTING, "start_execution"),
    StateTransition(ManagerState.EXECUTING, ManagerState.EXECUTION_COMPLETED, "execution_success"),
    StateTransition(ManagerState.EXECUTING, ManagerState.EXECUTION_FAILED, "execution_failure"),
    StateTransition(ManagerState.EXECUTING, ManagerState.EXECUTION_ABORTED, "execution_abort"),
    
    # 报告阶段
    StateTransition(ManagerState.EXECUTION_COMPLETED, ManagerState.REPORTING, "start_report"),
    StateTransition(ManagerState.REPORTING, ManagerState.REPORT_COMPLETED, "report_success"),
    
    # 学习阶段
    StateTransition(ManagerState.REPORT_COMPLETED, ManagerState.LEARNING, "start_learning"),
    StateTransition(ManagerState.LEARNING, ManagerState.LEARNING_COMPLETED, "learning_success"),
    
    # 终态
    StateTransition(ManagerState.LEARNING_COMPLETED, ManagerState.COMPLETED, "finish"),
    StateTransition(ManagerState.SCAN_FAILED, ManagerState.FAILED, "abort"),
    StateTransition(ManagerState.ANALYSIS_FAILED, ManagerState.FAILED, "abort"),
    StateTransition(ManagerState.RESOLUTION_FAILED, ManagerState.FAILED, "abort"),
    StateTransition(ManagerState.REJECTED, ManagerState.IDLE, "restart"),
    StateTransition(ManagerState.EXECUTION_FAILED, ManagerState.FAILED, "abort"),
    StateTransition(ManagerState.EXECUTION_ABORTED, ManagerState.FAILED, "abort"),
]


class StateMachine:
    """状态机"""
    
    def __init__(self):
        self.current_state = ManagerState.IDLE
        self.history: List[StateRecord] = []
        self.context: Dict[str, Any] = {}
    
    def transition(self, trigger: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        执行状态转换
        
        Args:
            trigger: 触发器名称
            context: 上下文参数
            
        Returns:
            是否转换成功
        """
        # 查找匹配的转换
        transition = self._find_transition(trigger)
        if not transition:
            return False
        
        # 检查转换条件
        if transition.guard and not self._check_guard(transition.guard):
            return False
        
        # 记录历史
        record = StateRecord(
            from_state=self.current_state,
            to_state=transition.to_state,
            trigger=trigger,
            context=context or {}
        )
        self.history.append(record)
        
        # 更新上下文
        if context:
            self.context.update(context)
        
        # 更新状态
        self.current_state = transition.to_state
        
        return True
    
    def _find_transition(self, trigger: str) -> Optional[StateTransition]:
        """查找匹配的转换"""
        for transition in STATE_TRANSITIONS:
            if (transition.from_state == self.current_state and 
                transition.trigger == trigger):
                return transition
        return None
    
    def _check_guard(self, guard: str) -> bool:
        """检查转换条件"""
        # 简化实现，实际应根据guard表达式评估
        return True
    
    def can_transition(self, trigger: str) -> bool:
        """检查是否可以转换"""
        transition = self._find_transition(trigger)
        return transition is not None
    
    def get_available_triggers(self) -> List[str]:
        """获取当前可用的触发器"""
        return [
            t.trigger for t in STATE_TRANSITIONS 
            if t.from_state == self.current_state
        ]
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """获取状态历史"""
        return [
            {
                "from_state": record.from_state.value,
                "to_state": record.to_state.value,
                "trigger": record.trigger,
                "timestamp": record.timestamp.isoformat()
            }
            for record in self.history
        ]
    
    def reset(self):
        """重置状态机"""
        self.current_state = ManagerState.IDLE
        self.history = []
        self.context = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "current_state": self.current_state.value,
            "history": self.get_state_history(),
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateMachine':
        """从字典创建"""
        sm = cls()
        sm.current_state = ManagerState(data["current_state"])
        sm.context = data.get("context", {})
        return sm


def get_state_diagram() -> str:
    """获取状态转换图（DOT格式）"""
    return """
digraph state_machine {
    rankdir=TB;
    node [shape=ellipse];
    
    IDLE [label="IDLE\\n(初始状态)"];
    SCANNING [label="SCANNING\\n(扫描中)"];
    SCAN_COMPLETED [label="SCAN_COMPLETED\\n(扫描完成)"];
    SCAN_FAILED [label="SCAN_FAILED\\n(扫描失败)"];
    ANALYZING [label="ANALYZING\\n(分析中)"];
    ANALYSIS_COMPLETED [label="ANALYSIS_COMPLETED\\n(分析完成)"];
    RESOLVING [label="RESOLVING\\n(解决中)"];
    RESOLUTION_COMPLETED [label="RESOLUTION_COMPLETED\\n(解决完成)"];
    AWAITING_CONFIRMATION [label="AWAITING_CONFIRMATION\\n(等待确认)"];
    CONFIRMED [label="CONFIRMED\\n(已确认)"];
    REJECTED [label="REJECTED\\n(已拒绝)"];
    EXECUTING [label="EXECUTING\\n(执行中)"];
    EXECUTION_COMPLETED [label="EXECUTION_COMPLETED\\n(执行完成)"];
    EXECUTION_FAILED [label="EXECUTION_FAILED\\n(执行失败)"];
    REPORTING [label="REPORTING\\n(报告生成中)"];
    REPORT_COMPLETED [label="REPORT_COMPLETED\\n(报告完成)"];
    LEARNING [label="LEARNING\\n(学习中)"];
    LEARNING_COMPLETED [label="LEARNING_COMPLETED\\n(学习完成)"];
    COMPLETED [label="COMPLETED\\n(完成)" shape=doublecircle];
    FAILED [label="FAILED\\n(失败)" shape=doublecircle];
    
    IDLE -> SCANNING [label="start_scan"];
    SCANNING -> SCAN_COMPLETED [label="scan_success"];
    SCANNING -> SCAN_FAILED [label="scan_failure"];
    SCAN_COMPLETED -> ANALYZING [label="start_analysis"];
    ANALYZING -> ANALYSIS_COMPLETED [label="analysis_success"];
    ANALYSIS_COMPLETED -> RESOLVING [label="start_resolution"];
    RESOLVING -> RESOLUTION_COMPLETED [label="resolution_success"];
    RESOLUTION_COMPLETED -> AWAITING_CONFIRMATION [label="request_confirmation"];
    AWAITING_CONFIRMATION -> CONFIRMED [label="user_confirmed"];
    AWAITING_CONFIRMATION -> REJECTED [label="user_rejected"];
    CONFIRMED -> EXECUTING [label="start_execution"];
    EXECUTING -> EXECUTION_COMPLETED [label="execution_success"];
    EXECUTING -> EXECUTION_FAILED [label="execution_failure"];
    EXECUTION_COMPLETED -> REPORTING [label="start_report"];
    REPORTING -> REPORT_COMPLETED [label="report_success"];
    REPORT_COMPLETED -> LEARNING [label="start_learning"];
    LEARNING -> LEARNING_COMPLETED [label="learning_success"];
    LEARNING_COMPLETED -> COMPLETED [label="finish"];
    SCAN_FAILED -> FAILED [label="abort"];
    EXECUTION_FAILED -> FAILED [label="abort"];
}
"""
