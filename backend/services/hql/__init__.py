"""
HQL 服务模块

统一的HQL生成服务, 支持多种生成模式（single/join/union）

此模块是完全独立, 无业务依赖的HQL生成器, 可以作为独立Python包使用

Examples:
    >>> from . HQLServiceFactory, Event, Field
    >>>
    >>> # 创建服务实例
    >>> service = HQLServiceFactory.create(version='v2')
    >>>
    >>> # 定义事件和字段
    >>> event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")
    >>> fields = [
    ...     Field(name="role_id", type="base"),
    ...     Field(name="zone_id", type="param", json_path="$.zone_id")
    ... ]
    >>>
    >>> # 生成HQL
    >>> hql = service.generate_hql(events=[event], fields=fields, conditions=[])
    >>> print(hql)

Service Interface:
    - IHQLGenerationService: 抽象接口
    - HQLGenerationServiceV2: V2实现（支持single/join/union）
    - HQLServiceFactory: 服务工厂

Core Components:
    - HQLGenerator: 核心HQL生成器
    - FieldBuilder: 字段构建器
    - WhereBuilder: WHERE条件构建器
    - JoinBuilder: JOIN构建器
    - UnionBuilder: UNION构建器
    - SyntaxValidator: 语法校验器

Models:
    - Event: 事件模型
    - Field: 字段模型
    - Condition: 条件模型
    - JoinConfig: JOIN配置模型
"""

__version__ = "2.0.0"

# 导出构建器
from .builders.field_builder import FieldBuilder
from .builders.join_builder import JoinBuilder
from .builders.union_builder import UnionBuilder
from .builders.where_builder import WhereBuilder

# 导出核心生成器
from .core.generator import DebuggableHQLGenerator, HQLGenerator

# 导出核心Facade
from .hql_facade import HQLFacade

# 导出带缓存的服务
from .hql_service_cached import HQLServiceCached

# 导出核心模型
from .models.event import (
    AggregateFunction,
    Condition,
    Event,
    Field,
    FieldType,
    HQLContext,
    JoinConfig,
    JoinType,
    LogicalOperator,
    Operator,
)

# 导出验证器
from .validators.syntax_validator import (
    SyntaxError,
    SyntaxValidator,
    ValidationResult,
    quick_validate_hql,
    validate_hql,
)

# 导出适配器(可选, 因为依赖项目业务逻辑)
try:
    pass

    _project_adapter_available = True
except ImportError:
    _project_adapter_available = False

# 公共API
__all__ = [
    # 版本
    "__version__",
    # 服务
    "HQLFacade",
    "HQLServiceCached",
    # 核心模型
    "Event",
    "Field",
    "Condition",
    "JoinConfig",
    "HQLContext",
    "FieldType",
    "AggregateFunction",
    "Operator",
    "LogicalOperator",
    "JoinType",
    # 生成器
    "HQLGenerator",
    "DebuggableHQLGenerator",
    # 构建器
    "FieldBuilder",
    "WhereBuilder",
    "JoinBuilder",
    "UnionBuilder",
    # 验证器
    "SyntaxValidator",
    "SyntaxError",
    "ValidationResult",
    "validate_hql",
    "quick_validate_hql",
]

# 如果适配器可用, 添加到导出列表
if _project_adapter_available:
    __all__.append("ProjectAdapter")
