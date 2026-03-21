"""
GitHub Manager Decision Engine

决策引擎，支持规则匹配和权重学习。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class ConditionOperator(Enum):
    """条件操作符"""
    EQ = "eq"           # 等于
    NE = "ne"           # 不等于
    GT = "gt"           # 大于
    LT = "lt"           # 小于
    GTE = "gte"         # 大于等于
    LTE = "lte"         # 小于等于
    IN = "in"           # 在列表中
    NOT_IN = "not_in"   # 不在列表中
    CONTAINS = "contains"  # 包含
    MATCHES = "matches"    # 正则匹配


@dataclass
class Condition:
    """条件"""
    field: str
    operator: str
    value: Any
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """评估条件"""
        # 支持嵌套字段访问
        field_value = self._get_nested_value(context, self.field)
        if field_value is None:
            return False
        
        # 根据操作符比较
        if self.operator == "eq":
            return field_value == self.value
        elif self.operator == "ne":
            return field_value != self.value
        elif self.operator == "gt":
            return field_value > self.value
        elif self.operator == "lt":
            return field_value < self.value
        elif self.operator == "gte":
            return field_value >= self.value
        elif self.operator == "lte":
            return field_value <= self.value
        elif self.operator == "in":
            return field_value in self.value
        elif self.operator == "not_in":
            return field_value not in self.value
        elif self.operator == "contains":
            return self.value in field_value
        elif self.operator == "matches":
            import re
            return bool(re.match(self.value, str(field_value)))
        
        return False
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """获取嵌套字段值"""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value


@dataclass
class DecisionRule:
    """决策规则"""
    rule_id: str
    name: str
    description: str
    priority: int  # 优先级，越高越优先
    weight: float  # 权重，学习后调整
    conditions: List[Condition]
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def matches(self, context: Dict[str, Any]) -> bool:
        """检查规则是否适用"""
        return all(condition.evaluate(context) for condition in self.conditions)
    
    def increase_weight(self, delta: float = 0.1):
        """增加权重"""
        self.weight = min(1.0, self.weight + delta)
        self.updated_at = datetime.now()
    
    def decrease_weight(self, delta: float = 0.1):
        """减少权重"""
        self.weight = max(0.0, self.weight - delta)
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "weight": self.weight,
            "conditions": [
                {"field": c.field, "operator": c.operator, "value": c.value}
                for c in self.conditions
            ],
            "action": self.action,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Decision:
    """决策"""
    decision_id: str
    action: str
    parameters: Dict[str, Any]
    confidence: float
    rules_applied: List[str]
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "decision_id": self.decision_id,
            "action": self.action,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "rules_applied": self.rules_applied,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class DecisionOutcome:
    """决策结果"""
    decision_id: str
    is_positive: bool
    feedback: str
    timestamp: datetime = field(default_factory=datetime.now)


# 默认决策规则
DEFAULT_RULES: List[DecisionRule] = [
    # 高优先级规则
    DecisionRule(
        rule_id="RULE-H001",
        name="分支分叉处理",
        description="检测到本地分支与远程分支分叉",
        priority=10,
        weight=0.85,
        conditions=[
            Condition("local_state.diverged", "eq", True)
        ],
        action="git_rebase",
        parameters={"strategy": "rebase"}
    ),
    DecisionRule(
        rule_id="RULE-H002",
        name="main分支开发处理",
        description="检测到在main分支上直接开发",
        priority=10,
        weight=0.90,
        conditions=[
            Condition("local_state.current_branch", "eq", "main"),
            Condition("local_state.is_clean", "eq", False)
        ],
        action="create_feature_branch",
        parameters={"strategy": "feature_branch"}
    ),
    DecisionRule(
        rule_id="RULE-H003",
        name="无分支保护处理",
        description="检测到main分支无保护规则",
        priority=10,
        weight=0.80,
        conditions=[
            Condition("remote_state.branch_protection.enabled", "eq", False)
        ],
        action="setup_branch_protection",
        parameters={"strategy": "protection"}
    ),
    
    # 中优先级规则
    DecisionRule(
        rule_id="RULE-M001",
        name="大量未提交处理",
        description="检测到大量未提交文件",
        priority=5,
        weight=0.75,
        conditions=[
            Condition("local_state.uncommitted_files_count", "gt", 10)
        ],
        action="batch_commit",
        parameters={"strategy": "batch"}
    ),
    DecisionRule(
        rule_id="RULE-M002",
        name="CI失败处理",
        description="检测到CI构建失败",
        priority=5,
        weight=0.70,
        conditions=[
            Condition("remote_state.ci_status.status", "eq", "failure")
        ],
        action="fix_ci_failure",
        parameters={"strategy": "ci_fix"}
    ),
    DecisionRule(
        rule_id="RULE-M003",
        name="合并冲突处理",
        description="检测到PR存在合并冲突",
        priority=5,
        weight=0.75,
        conditions=[
            Condition("has_merge_conflict", "eq", True)
        ],
        action="resolve_conflicts",
        parameters={"strategy": "conflict_resolution"}
    ),
    
    # 低优先级规则
    DecisionRule(
        rule_id="RULE-L001",
        name="落后远程处理",
        description="检测到本地落后远程多个提交",
        priority=1,
        weight=0.60,
        conditions=[
            Condition("local_state.unpulled_commits", "gt", 5)
        ],
        action="pull_with_rebase",
        parameters={"strategy": "pull_rebase"}
    ),
    DecisionRule(
        rule_id="RULE-L002",
        name="缺少PR模板处理",
        description="检测到项目缺少PR模板",
        priority=1,
        weight=0.50,
        conditions=[
            Condition("project_config.has_pr_template", "eq", False)
        ],
        action="create_pr_template",
        parameters={"strategy": "template"}
    ),
]


class DecisionEngine:
    """决策引擎"""
    
    def __init__(self, rules: Optional[List[DecisionRule]] = None):
        self.rules = rules or DEFAULT_RULES.copy()
        self.decision_history: List[Decision] = []
        self.outcome_history: List[DecisionOutcome] = []
        self._decision_counter = 0
    
    def make_decision(self, context: Dict[str, Any]) -> Decision:
        """
        基于上下文做出决策
        
        Args:
            context: 决策上下文
            
        Returns:
            决策结果
        """
        # 1. 收集所有适用的规则
        applicable_rules = [
            rule for rule in self.rules 
            if rule.matches(context)
        ]
        
        # 2. 按优先级和权重排序
        applicable_rules.sort(
            key=lambda r: (r.priority, r.weight), 
            reverse=True
        )
        
        # 3. 应用最高优先级规则
        if applicable_rules:
            rule = applicable_rules[0]
            decision = Decision(
                decision_id=self._generate_decision_id(),
                action=rule.action,
                parameters=rule.parameters,
                confidence=rule.weight,
                rules_applied=[rule.rule_id],
                reason=f"应用规则: {rule.name} (优先级={rule.priority}, 权重={rule.weight:.2f})"
            )
        else:
            # 4. 如果没有规则适用，使用默认决策
            decision = Decision(
                decision_id=self._generate_decision_id(),
                action="ask_user",
                parameters={},
                confidence=0.0,
                rules_applied=[],
                reason="无法自动决策，需要用户确认"
            )
        
        # 5. 记录决策历史
        self.decision_history.append(decision)
        
        return decision
    
    def _generate_decision_id(self) -> str:
        """生成决策ID"""
        self._decision_counter += 1
        return f"decision-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._decision_counter}"
    
    def learn_from_outcome(self, decision_id: str, outcome: DecisionOutcome):
        """
        从决策结果中学习
        
        Args:
            decision_id: 决策ID
            outcome: 决策结果
        """
        # 记录结果
        self.outcome_history.append(outcome)
        
        # 查找决策
        decision = next(
            (d for d in self.decision_history if d.decision_id == decision_id), 
            None
        )
        if not decision:
            return
        
        # 更新规则权重
        for rule_id in decision.rules_applied:
            rule = next((r for r in self.rules if r.rule_id == rule_id), None)
            if rule:
                if outcome.is_positive:
                    rule.increase_weight()
                else:
                    rule.decrease_weight()
    
    def add_rule(self, rule: DecisionRule):
        """添加规则"""
        self.rules.append(rule)
        # 按优先级排序
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        for i, rule in enumerate(self.rules):
            if rule.rule_id == rule_id:
                self.rules.pop(i)
                return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[DecisionRule]:
        """获取规则"""
        return next((r for r in self.rules if r.rule_id == rule_id), None)
    
    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """获取决策"""
        return next((d for d in self.decision_history if d.decision_id == decision_id), None)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self.decision_history:
            return {
                "total_decisions": 0,
                "total_outcomes": 0,
                "success_rate": 0.0,
                "rules_used": {}
            }
        
        # 计算成功率
        positive_outcomes = sum(1 for o in self.outcome_history if o.is_positive)
        success_rate = positive_outcomes / len(self.outcome_history) if self.outcome_history else 0.0
        
        # 统计规则使用情况
        rules_used: Dict[str, int] = {}
        for decision in self.decision_history:
            for rule_id in decision.rules_applied:
                rules_used[rule_id] = rules_used.get(rule_id, 0) + 1
        
        return {
            "total_decisions": len(self.decision_history),
            "total_outcomes": len(self.outcome_history),
            "success_rate": success_rate,
            "rules_used": rules_used,
            "rules_count": len(self.rules)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rules": [r.to_dict() for r in self.rules],
            "decision_history": [d.to_dict() for d in self.decision_history],
            "statistics": self.get_statistics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DecisionEngine':
        """从字典创建"""
        rules = []
        for rule_data in data.get("rules", []):
            conditions = [
                Condition(
                    field=c["field"],
                    operator=c["operator"],
                    value=c["value"]
                )
                for c in rule_data.get("conditions", [])
            ]
            rule = DecisionRule(
                rule_id=rule_data["rule_id"],
                name=rule_data["name"],
                description=rule_data["description"],
                priority=rule_data["priority"],
                weight=rule_data["weight"],
                conditions=conditions,
                action=rule_data["action"],
                parameters=rule_data.get("parameters", {})
            )
            rules.append(rule)
        
        return cls(rules=rules)
