"""
HQL服务抽象接口

定义HQL生成服务的统一接口，支持多版本实现
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IHQLGenerationService(ABC):
    """
    HQL生成服务接口

    定义了HQL生成服务的标准接口，所有版本实现必须遵循此接口
    """

    @abstractmethod
    def generate_hql(
        self, events: List[Any], fields: List[Any], conditions: List[Any], **options
    ) -> str:
        """
        生成HQL语句

        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            **options: 额外选项
                - mode: 生成模式（single/join/union）
                - sql_mode: SQL模式（VIEW/PROCEDURE/CUSTOM）
                - include_comments: 是否包含注释（默认True）
                - join_config: JOIN配置（join模式必需）

        Returns:
            str: 生成的HQL语句

        Raises:
            ValueError: 参数不合法时
        """
        pass

    @abstractmethod
    def validate_hql(self, hql: str) -> Dict[str, Any]:
        """
        验证HQL语法

        Args:
            hql: HQL语句

        Returns:
            Dict[str, Any]: 验证结果
                - is_valid: bool 是否有效
                - errors: List[Dict] 错误列表
                - warnings: List[Dict] 警告列表
        """
        pass

    @abstractmethod
    def get_supported_modes(self) -> List[str]:
        """
        获取支持的生成模式

        Returns:
            List[str]: 支持的模式列表
                例如: ['single', 'join', 'union']
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        获取服务版本

        Returns:
            str: 版本号，例如: '2.0.0'
        """
        pass


class HQLGenerationServiceV2(IHQLGenerationService):
    """
    HQL生成服务 V2实现

    基于 hql_v2 模块的完整实现
    支持单事件、JOIN、UNION三种生成模式
    """

    def __init__(self):
        """初始化V2服务"""
        from .core.generator import HQLGenerator
        from .validators.syntax_validator import SyntaxValidator

        self.generator = HQLGenerator()
        self.validator = SyntaxValidator()
        self._version = "2.0.0"

    def generate_hql(
        self, events: List[Any], fields: List[Any], conditions: List[Any], **options
    ) -> str:
        """
        生成HQL语句（V2实现）

        Args:
            events: Event模型列表
            fields: Field模型列表
            conditions: Condition模型列表
            **options: 额外选项

        Returns:
            str: 完整的HQL语句

        Examples:
            >>> service = HQLGenerationServiceV2()
            >>> from . Event, Field
            >>> event = Event(name="login", table_name="ods.table")
            >>> field = Field(name="role_id", type="base")
            >>> hql = service.generate_hql([event], [field], [])
        """
        # 转换为内部模型（如果不是Event/Field/Condition对象）
        from .models.event import Event, Field, Condition

        # 转换events
        internal_events = []
        for event in events:
            if isinstance(event, Event):
                internal_events.append(event)
            elif isinstance(event, dict):
                internal_events.append(Event(**event))
            else:
                raise ValueError(f"Unsupported event type: {type(event)}")

        # 转换fields
        internal_fields = []
        for field in fields:
            if isinstance(field, Field):
                internal_fields.append(field)
            elif isinstance(field, dict):
                internal_fields.append(Field(**field))
            else:
                raise ValueError(f"Unsupported field type: {type(field)}")

        # 转换conditions
        internal_conditions = []
        for condition in conditions:
            if isinstance(condition, Condition):
                internal_conditions.append(condition)
            elif isinstance(condition, dict):
                internal_conditions.append(Condition(**condition))
            elif condition:  # 简单转换
                internal_conditions.append(condition)
            else:
                raise ValueError(f"Unsupported condition type: {type(condition)}")

        # 调用生成器
        return self.generator.generate(
            events=internal_events,
            fields=internal_fields,
            conditions=internal_conditions,
            **options,
        )

    def validate_hql(self, hql: str) -> Dict[str, Any]:
        """
        验证HQL语法（V2实现）

        Args:
            hql: HQL语句

        Returns:
            Dict[str, Any]: 验证结果
        """
        result = self.validator.validate(hql)

        return {
            "is_valid": result.is_valid,
            "errors": [
                {
                    "line": err.line,
                    "column": err.column,
                    "message": err.message,
                    "error_type": err.error_type,
                    "suggestion": err.suggestion,
                }
                for err in result.errors
            ],
            "warnings": [
                {
                    "line": warn.line,
                    "column": warn.column,
                    "message": warn.message,
                    "error_type": warn.error_type,
                    "suggestion": warn.suggestion,
                }
                for warn in result.warnings
            ],
        }

    def get_supported_modes(self) -> List[str]:
        """
        获取支持的生成模式（V2实现）

        Returns:
            List[str]: ['single', 'join', 'union']
        """
        return ["single", "join", "union"]

    def get_version(self) -> str:
        """
        获取服务版本

        Returns:
            str: '2.0.0'
        """
        return self._version


class HQLServiceFactory:
    """
    HQL服务工厂

    根据版本创建对应的HQL服务实例

    Examples:
        >>> # 创建V2服务（默认）
        >>> service = HQLServiceFactory.create()
        >>>
        >>> # 明确指定V2
        >>> service = HQLServiceFactory.create(version='v2')
        >>>
        >>> # 生成HQL
        >>> hql = service.generate_hql(events, fields, conditions)
    """

    @staticmethod
    def create(version: str = "v2") -> IHQLGenerationService:
        """
        创建HQL服务实例

        Args:
            version: 服务版本（'v1' | 'v2'）
                - v1: 仅支持单事件（已废弃）
                - v2: 支持single/join/union（默认）

        Returns:
            IHQLGenerationService: 服务实例

        Raises:
            ValueError: 不支持的版本

        Examples:
            >>> factory = HQLServiceFactory()
            >>> service = factory.create('v2')
            >>> hql = service.generate_hql(events, fields, conditions)
        """
        version = version.lower().replace(".", "")

        if version == "v2" or version == "2":
            return HQLGenerationServiceV2()
        elif version == "v1" or version == "1":
            raise ValueError(
                "HQL V1 has been deprecated. "
                "Please use V2 which supports all V1 features plus JOIN and UNION modes."
            )
        else:
            raise ValueError(f"Unsupported version: {version}. Available: v2")


# 导出
__all__ = ["IHQLGenerationService", "HQLGenerationServiceV2", "HQLServiceFactory"]
