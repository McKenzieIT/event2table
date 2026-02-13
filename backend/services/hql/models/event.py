"""
抽象数据模型

完全脱离项目业务逻辑的核心模型
"""

from dataclasses import dataclass, field
from typing import Any, Optional, List
from enum import Enum


class FieldType(str, Enum):
    """字段类型枚举"""

    BASE = "base"  # 基础字段（直接从表查询）
    PARAM = "param"  # 参数字段（从JSON params提取）
    CUSTOM = "custom"  # 自定义字段（自定义表达式）
    FIXED = "fixed"  # 固定值字段（常量）


class AggregateFunction(str, Enum):
    """聚合函数枚举"""

    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MAX = "MAX"
    MIN = "MIN"


class Operator(str, Enum):
    """操作符枚举"""

    EQ = "="
    NE = "!="
    GT = ">"
    LT = "<"
    GTE = ">="
    LTE = "<="
    LIKE = "LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"


class LogicalOperator(str, Enum):
    """逻辑操作符枚举"""

    AND = "AND"
    OR = "OR"


class JoinType(str, Enum):
    """JOIN类型枚举"""

    INNER = "INNER"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    FULL = "FULL"


@dataclass
class Event:
    """
    抽象事件模型

    完全脱离项目业务，只包含HQL生成所需的最少信息

    Attributes:
        name: 事件名称（如: login, purchase）
        table_name: 完整表名（如: ieu_ods.ods_10000147_all_view）
        alias: 表别名（可选，用于JOIN/UNION操作）
        partition_field: 分区字段名（默认: ds）
    """

    name: str
    table_name: str
    alias: Optional[str] = None
    partition_field: str = "ds"

    def __post_init__(self):
        """初始化后验证"""
        if not self.name:
            raise ValueError("Event name cannot be empty")
        if not self.table_name:
            raise ValueError("Event table_name cannot be empty")


@dataclass
class Field:
    """
    抽象字段模型

    支持4种字段类型：
    - base: 直接从表查询的基础字段（role_id, account_id等）
    - param: 从JSON params字段提取的参数（get_json_object(params, '$.zone_id')）
    - custom: 自定义HQL表达式
    - fixed: 固定常量值

    Attributes:
        name: 字段名
        type: 字段类型（base/param/custom/fixed）
        alias: 字段别名（可选）
        aggregate_func: 聚合函数（可选）
        json_path: JSON路径（用于param类型）
        custom_expression: 自定义表达式（用于custom类型）
        fixed_value: 固定值（用于fixed类型）
    """

    name: str
    type: str
    alias: Optional[str] = None
    aggregate_func: Optional[str] = None
    json_path: Optional[str] = None
    custom_expression: Optional[str] = None
    fixed_value: Any = None

    def __post_init__(self):
        """初始化后验证"""
        if not self.name:
            raise ValueError("Field name cannot be empty")
        if self.type not in [t.value for t in FieldType]:
            raise ValueError(f"Invalid field type: {self.type}")

        # 验证param类型必须有json_path
        if self.type == FieldType.PARAM.value and not self.json_path:
            raise ValueError("param type field must have json_path")

        # 验证custom类型必须有custom_expression
        if self.type == FieldType.CUSTOM.value and not self.custom_expression:
            raise ValueError("custom type field must have custom_expression")

        # 验证fixed类型必须有fixed_value
        if self.type == FieldType.FIXED.value and self.fixed_value is None:
            raise ValueError("fixed type field must have fixed_value")


@dataclass
class Condition:
    """
    抽象条件模型

    支持WHERE条件构建，支持AND/OR逻辑组合

    Attributes:
        field: 字段名
        operator: 操作符（=, !=, >, <, LIKE, IN等）
        value: 条件值（可选，IS NULL等操作符不需要值）
        logical_op: 逻辑操作符（AND/OR，默认AND）
    """

    field: str
    operator: str
    value: Optional[Any] = None
    logical_op: str = LogicalOperator.AND.value

    def __post_init__(self):
        """初始化后验证"""
        if not self.field:
            raise ValueError("Condition field cannot be empty")
        if self.operator not in [o.value for o in Operator]:
            raise ValueError(f"Invalid operator: {self.operator}")

    def is_null_operator(self) -> bool:
        """判断是否为NULL相关操作符"""
        return self.operator in [Operator.IS_NULL.value, Operator.IS_NOT_NULL.value]


@dataclass
class JoinConfig:
    """
    JOIN配置模型

    用于多事件JOIN场景

    Attributes:
        join_type: JOIN类型（INNER/LEFT/RIGHT/FULL）
        join_keys: JOIN键字段列表
        left_event: 左侧事件
        right_event: 右侧事件
    """

    join_type: str
    join_keys: List[str]
    left_event: Optional[Event] = None
    right_event: Optional[Event] = None

    def __post_init__(self):
        """初始化后验证"""
        if self.join_type not in [t.value for t in JoinType]:
            raise ValueError(f"Invalid join type: {self.join_type}")
        if not self.join_keys:
            raise ValueError("join_keys cannot be empty")


@dataclass
class HQLContext:
    """
    HQL生成上下文

    包含生成HQL所需的所有配置信息

    Attributes:
        events: 事件列表
        fields: 字段列表
        conditions: 条件列表
        mode: 生成模式（single/join/union）
        sql_mode: SQL模式（VIEW/PROCEDURE/CUSTOM）
        join_config: JOIN配置（可选）
    """

    events: List[Event]
    fields: List[Field]
    conditions: List[Condition] = field(default_factory=list)
    mode: str = "single"
    sql_mode: str = "VIEW"
    join_config: Optional[JoinConfig] = None

    def __post_init__(self):
        """初始化后验证"""
        if not self.events:
            raise ValueError("events cannot be empty")
        if not self.fields:
            raise ValueError("fields cannot be empty")

        # 验证模式
        valid_modes = ["single", "join", "union"]
        if self.mode not in valid_modes:
            raise ValueError(f"Invalid mode: {self.mode}")

        # JOIN模式必须有join_config
        if self.mode == "join" and not self.join_config:
            raise ValueError("join mode requires join_config")
