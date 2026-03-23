#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一Entity模型

单一真相来源(Single Source of Truth):
- 所有模块(API/Service/Repository)使用相同的Entity定义
- Pydantic自动验证输入和序列化输出
- 彻底解决模型不一致问题

替换旧的DDD模型和Schema:
- backend/domain/models/ (DDD领域模型) → 合并到此文件
- backend/models/schemas.py (Pydantic Schema) → 合并到此文件

优势:
1. 模型一致性: 单一定义,不可能不一致
2. 自动验证: Pydantic自动验证所有输入
3. 类型安全: IDE自动补全和错误检测
4. 减少转换: 直接使用Entity,无需中间转换
5. 自动文档: 可导出JSON Schema用于API文档
"""

from typing import Optional, List, Dict, Any, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict, field_serializer
import html
import os

# ============================================================================
# Game Entity
# ============================================================================


class GameEntity(BaseModel):
    """
    游戏实体 - 全局唯一的游戏模型定义

    用途:
    - API层: 请求验证和响应序列化
    - Service层: 业务逻辑传参
    - Repository层: 数据库读写

    验证规则:
    - gid: 必须是正整数
    - name: 1-100字符,自动XSS防护
    - ods_db: 生产环境只能是ieu_ods或overseas_ods,测试环境允许任意值

    测试模式:
    - 设置 FLASK_ENV=testing 或 ENVIRONMENT=test 允许任意 ods_db 值
    - 用于E2E测试和单元测试的测试数据创建
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    gid: int = Field(..., ge=0, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: str = Field(..., description="ODS数据库名称 (生产: ieu_ods/overseas_ods, 测试: 任意值)")
    description: Optional[str] = Field(None, description="游戏描述")
    dwd_prefix: str = Field("dwd", description="DWD表前缀")
    icon_path: Optional[str] = Field(None, description="图标路径")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    # 关联数据 (统计信息,不持久化到数据库)
    event_count: Optional[int] = Field(default=0, description="事件数量统计", exclude=True)

    @field_validator("ods_db")
    @classmethod
    def validate_ods_db(cls, v: str) -> str:
        """
            验证ODS数据库名称

            生产环境: 只允许 ieu_ods 或 overseas_ods
        测试环境: 允许任意值 (用于测试数据创建)

            Args:
                v: ODS数据库名称

            Returns:
                验证后的数据库名称

            Raises:
                ValueError: 生产环境下使用无效的数据库名称
        """
        # 检查是否在测试环境 (仅当明确设置FLASK_ENV=testing时)
        # 注意: 不自动检测PYTEST_CURRENT_TEST,以允许测试验证功能
        is_testing = (
            os.environ.get("FLASK_ENV", "").lower() == "testing"
            or os.environ.get("ENVIRONMENT", "").lower() == "test"
        )

        # 测试环境: 允许任意值
        if is_testing:
            return v

        # 生产环境: 严格验证
        allowed_values = ["ieu_ods", "overseas_ods"]
        if v not in allowed_values:
            raise ValueError(
                f"ods_db必须是以下值之一: {', '.join(allowed_values)}. "
                f"当前值: '{v}'. "
                f"提示: 如需在测试中使用其他值,请设置 FLASK_ENV=testing 环境变量."
            )

        return v

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """
        防止XSS攻击: 转义HTML字符

        Args:
            v: 原始名称

        Returns:
            转义后的安全名称
        """
        if v:
            return html.escape(v.strip())
        return v

    @field_validator("gid", mode="before")
    @classmethod
    def validate_gid(cls, v: Union[int, str]) -> int:
        """
        验证gid格式 - 必须是正整数
        支持从字符串转换(数据库存储为TEXT)

        Args:
            v: GID值 (int或str)

        Returns:
            验证后的GID (int)

        Raises:
            ValueError: GID格式不正确
        """
        # 如果是字符串,先转换为整数
        if isinstance(v, str):
            try:
                v = int(v)
            except ValueError:
                raise ValueError(f"gid必须是整数,得到: {v}")

        # 验证业务规则
        if v < 0:
            raise ValueError("gid必须是正整数")
        return v

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        return dt.isoformat() if dt else None

    model_config = ConfigDict(
        from_attributes=True,  # 支持ORM模式
        json_schema_extra={
            "example": {
                "id": 1,
                "gid": 10000147,
                "name": "STAR001",
                "ods_db": "ieu_ods",
                "description": "测试游戏",
                "dwd_prefix": "dwd",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "event_count": 10,
            }
        },
    )


# ============================================================================
# Event Entity
# ============================================================================


class EventEntity(BaseModel):
    """
    事件实体 - 全局唯一的事件模型定义

    用途:
    - API层: 请求验证和响应序列化
    - Service层: 业务逻辑传参
    - Repository层: 数据库读写

    验证规则:
    - game_gid: 必须关联有效游戏
    - name: 1-100字符

    字段映射:
    - name (Entity) <-> event_name (Database)
    - name_cn (Entity) <-> event_name_cn (Database)
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段 (使用数据库列名作为字段名, 同时接受Entity字段名作为别名)
    game_gid: int = Field(..., ge=0, description="游戏GID")

    # 使用alias同时接受name和event_name
    event_name: str = Field(..., alias="name", min_length=1, max_length=100, description="事件名称")
    event_name_cn: Optional[str] = Field(None, alias="name_cn", max_length=100, description="事件中文名")

    # 数据库字段 (从log_events表)
    category_id: Optional[int] = Field(None, description="分类ID")
    source_table: str = Field(..., description="ODS源表")
    target_table: str = Field(..., description="DWD目标表")
    include_in_common_params: int = Field(1, description="是否包含在公共参数中")

    # 关联数据 (从JOIN查询获取)
    game_name: Optional[str] = Field(None, description="游戏名称 (JOIN games)")
    ods_db: Optional[str] = Field(None, description="ODS数据库 (JOIN games)")
    category_name: Optional[str] = Field(None, description="分类名称 (JOIN event_categories)")

    # 计算字段 (不持久化)
    table_name: Optional[str] = Field(None, description="ODS表名", exclude=True)
    description: Optional[str] = Field(None, description="事件描述", exclude=True)

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    # 关联数据 (统计信息,不持久化到数据库)
    param_count: Optional[int] = Field(default=0, description="参数数量统计", exclude=True)

    # 兼容旧代码的属性访问 (name -> event_name)
    @property
    def name(self) -> str:
        """兼容旧代码: name属性映射到event_name"""
        return self.event_name

    @name.setter
    def name(self, value: str):
        """兼容旧代码: 设置name属性时映射到event_name"""
        self.event_name = value

    @property
    def name_cn(self) -> Optional[str]:
        """兼容旧代码: name_cn属性映射到event_name_cn"""
        return self.event_name_cn

    @name_cn.setter
    def name_cn(self, value: Optional[str]):
        """兼容旧代码: 设置name_cn属性时映射到event_name_cn"""
        self.event_name_cn = value

    @field_validator("event_name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        return dt.isoformat() if dt else None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # 允许使用alias或field name
        json_schema_extra={
            "example": {
                "id": 1,
                "game_gid": 10000147,
                "event_name": "login",
                "event_name_cn": "登录",
                "table_name": "ieu_ods.ods_10000147_login",
                "description": "用户登录事件",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "param_count": 5,
            }
        },
    )


# ============================================================================
# Parameter Entity
# ============================================================================


class ParameterEntity(BaseModel):
    """
    参数实体 - 全局唯一的参数模型定义

    用途:
    - API层: 请求验证和响应序列化
    - Service层: 业务逻辑传参
    - Repository层: 数据库读写

    验证规则:
    - event_id: 必须关联有效事件
    - game_gid: 必须关联有效游戏
    - param_type: 只能是base/param/common/calculate
    - json_path: 可选,用于JSON提取
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    event_id: int = Field(..., gt=0, description="事件ID")
    game_gid: int = Field(..., ge=0, description="游戏GID")
    name: str = Field(..., min_length=1, max_length=100, description="参数名称")
    param_type: Literal["base", "param", "common", "calculate"] = Field("base", description="参数类型")
    json_path: Optional[str] = Field(None, description="JSON提取路径 (如 $.zoneId)")
    hive_type: str = Field("STRING", description="Hive数据类型")
    description: Optional[str] = Field(None, description="参数描述")
    is_common: bool = Field(False, description="是否为公共参数")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v

    @field_validator("json_path")
    @classmethod
    def validate_json_path(cls, v: Optional[str]) -> Optional[str]:
        """
        验证JSON路径格式

        Args:
            v: JSON路径 (如 $.zoneId)

        Returns:
            验证后的JSON路径

        Raises:
            ValueError: JSON路径格式不正确
        """
        if v is None:
            return v
        if not v.startswith("$."):
            raise ValueError(f"JSON路径必须以'$.开头', 当前: {v}")
        return v

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        return dt.isoformat() if dt else None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "event_id": 1,
                "game_gid": 10000147,
                "name": "zone_id",
                "param_type": "param",
                "json_path": "$.zoneId",
                "hive_type": "INT",
                "description": "区域ID",
                "is_common": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        },
    )


# ============================================================================
# Common Parameter Entity
# ============================================================================


class CommonParameterEntity(BaseModel):
    """
    公共参数实体 - 全局唯一的公共参数模型定义

    用途:
    - 管理跨事件共享的参数
    - 参数模板定义

    验证规则:
    - game_gid: 必须关联有效游戏
    - name: 全局唯一
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    game_gid: int = Field(..., ge=0, description="游戏GID")
    name: str = Field(..., min_length=1, max_length=100, description="参数名称")
    param_type: Literal["base", "param", "calculate"] = Field("param", description="参数类型")
    json_path: Optional[str] = Field(None, description="JSON提取路径")
    hive_type: str = Field("STRING", description="Hive数据类型")
    description: Optional[str] = Field(None, description="参数描述")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        return dt.isoformat() if dt else None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "game_gid": 10000147,
                "name": "role_id",
                "param_type": "base",
                "json_path": None,
                "hive_type": "BIGINT",
                "description": "角色ID",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        },
    )


# ============================================================================
# Field Builder Config Entity
# ============================================================================


class FieldBuilderConfigEntity(BaseModel):
    """
    Field Builder配置实体 - 全局唯一的Field Builder配置模型定义

    用途:
    - API层: Field Builder配置CRUD请求验证
    - Service层: Field Builder业务逻辑处理
    - Repository层: Field Builder配置数据访问

    验证规则:
    - name: 必填, 1-200字符
    - output_table: 必填, 1-200字符 (视图/表名)
    - field_mapping_v2: JSON格式的字段映射配置

    字段说明:
    - field_mapping_v2: 包含view_config, base_fields, param_fields等
    - source_events: JSON数组,源事件ID列表
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    name: str = Field(..., min_length=1, max_length=200, description="配置名称")
    display_name: str = Field(..., min_length=1, max_length=200, description="显示名称")
    output_table: str = Field(
        ..., alias="view_name", min_length=1, max_length=200, description="输出表/视图名称"
    )

    # 配置数据 (JSON格式)
    source_events: Optional[str] = Field(None, description="源事件列表(JSON)")
    field_mapping_v2: Optional[Dict[str, Any]] = Field(None, description="字段映射配置v2(JSON)")

    # 旧字段 (兼容性)
    join_conditions: Optional[str] = Field(None, description="JOIN条件(JSON)")
    output_fields: Optional[str] = Field(None, description="输出字段(JSON)")
    join_type: Optional[str] = Field("join", description="连接类型")
    where_conditions: Optional[str] = Field(None, description="WHERE条件(JSON)")
    field_mappings: Optional[str] = Field(None, description="字段映射(JSON)")
    description: Optional[str] = Field(None, description="描述")

    # 游戏关联
    game_id: Optional[int] = Field(None, description="游戏ID(旧)")
    game_gid: Optional[int] = Field(None, description="游戏GID(新)")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @field_validator("name", "display_name", "output_table")
    @classmethod
    def sanitize_string(cls, v: str) -> str:
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """序列化datetime为ISO格式字符串"""
        return dt.isoformat() if dt else None

    @property
    def view_name(self) -> str:
        """兼容旧代码: view_name属性映射到output_table"""
        return self.output_table

    @view_name.setter
    def view_name(self, value: str):
        """兼容旧代码: 设置view_name属性时映射到output_table"""
        self.output_table = value

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,  # 允许使用alias或field name
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Custom View",
                "display_name": "自定义视图",
                "view_name": "v_dwd_custom_view",
                "output_table": "v_dwd_custom_view",
                "field_mapping_v2": {
                    "view_config": {"game_gid": 10000147, "date_var": "${bizdate}"},
                    "base_fields": [
                        {
                            "event_id": 1,
                            "event_name": "login",
                            "field_name": "role_id",
                            "alias": "role_id",
                        }
                    ],
                },
                "source_events": "[1, 2, 3]",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        },
    )


# ============================================================================
# Helper Functions
# ============================================================================


def entity_to_dict(entity: BaseModel) -> Dict[str, Any]:
    """
    将Entity转换为字典 (兼容旧代码)

    Args:
        entity: Entity实例

    Returns:
        字典表示
    """
    return entity.model_dump()


def dict_to_entity(entity_class: type, data: Dict[str, Any]) -> BaseModel:
    """
    将字典转换为Entity (兼容旧代码)

    Args:
        entity_class: Entity类
        data: 字典数据

    Returns:
        Entity实例
    """
    return entity_class(**data)


# ============================================================================
# Flow Entity
# ============================================================================


class FlowEntity(BaseModel):
    """
    流程模板实体 - 全局唯一的流程模型定义

    用途:
    - API层: Flow模板CRUD请求验证
    - Service层: Flow业务逻辑处理
    - Repository层: Flow数据访问

    验证规则:
    - flow_name: 必填, 1-200字符
    - flow_graph: JSON对象,存储流程图结构
    - variables: JSON对象,存储流程变量
    - game_gid: 可选,关联到游戏

    JSON字段自动序列化/反序列化:
    - flow_graph: Dict[str, Any] <-> JSON字符串
    - variables: Dict[str, Any] <-> JSON字符串
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    flow_name: str = Field(..., min_length=1, max_length=200, description="流程名称")
    name: Optional[str] = Field(None, max_length=200, description="流程名称别名")

    # JSON字段 - 自动序列化/反序列化
    flow_graph: Dict[str, Any] = Field(default_factory=dict, description="流程图结构（节点和边）")
    variables: Dict[str, Any] = Field(default_factory=dict, description="流程变量")

    # 关联
    game_gid: Optional[int] = Field(None, description="关联游戏GID")

    # 元数据
    description: Optional[str] = Field(None, description="流程描述")
    created_by: Optional[str] = Field(None, description="创建者")
    is_active: bool = Field(True, description="是否激活")
    version: int = Field(1, description="版本号")

    # 时间戳
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @field_validator('flow_name')
    @classmethod
    def sanitize_flow_name(cls, v: str) -> str:
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v

    @field_validator('flow_graph', 'variables', mode='before')
    @classmethod
    def deserialize_json_fields(cls, v):
        """从数据库读取时反序列化JSON字段"""
        from backend.core.utils.json_helpers import deserialize_json_field

        return deserialize_json_field(v)

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        # exclude为None的字段
        exclude_none=False,
    )


# ============================================================================
# Join Config Entity
# ============================================================================


class JoinConfigEntity(BaseModel):
    """
    Join配置实体 - 全局唯一的Join配置模型定义

    支持JSON字段自动序列化:
    - source_events: List[int] → JSON字符串 (存储到source_events列)
    - join_config: Dict → JSON字符串 (存储到join_conditions列)

    字段映射说明:
    - Entity字段名 join_config → 数据库列名 join_conditions
    - Repository会自动处理字段映射
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    game_gid: int = Field(..., ge=0, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="配置名称")
    display_name: str = Field(..., min_length=1, max_length=100, description="显示名称")

    # Join配置
    join_type: Literal["join", "union_all"] = Field("join", description="Join类型: join, union_all")
    source_events: List[int] = Field(default_factory=list, description="源事件ID列表")
    join_config: Dict[str, Any] = Field(default_factory=dict, description="JOIN条件配置")
    output_fields: List[str] = Field(default_factory=list, description="输出字段列表")
    output_table: str = Field(..., description="输出表名")

    # 可选配置
    where_conditions: Optional[Dict[str, Any]] = Field(None, description="WHERE条件")
    field_mappings: Optional[Dict[str, Any]] = Field(None, description="字段映射")
    description: Optional[str] = Field(None, description="配置描述")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @field_validator('name', 'display_name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        import html

        if v:
            return html.escape(v.strip())
        return v

    @field_validator('source_events', 'output_fields', mode='before')
    @classmethod
    def deserialize_list_fields(cls, v):
        """从数据库读取时反序列化list字段"""
        from backend.core.utils.json_helpers import deserialize_json_field

        return deserialize_json_field(v)

    @field_validator('join_config', 'where_conditions', 'field_mappings', mode='before')
    @classmethod
    def deserialize_dict_fields(cls, v):
        """从数据库读取时反序列化dict字段"""
        from backend.core.utils.json_helpers import deserialize_json_field

        return deserialize_json_field(v)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, exclude_none=False)


# ============================================================================
# HQL History Entity
# ============================================================================


class HQLHistoryEntity(BaseModel):
    """
    HQL历史记录实体 - 全局唯一的HQL历史模型定义

    支持JSON字段自动序列化:
    - events_json: List[Dict] → JSON字符串
    - fields_json: List[Dict] → JSON字符串
    - conditions_json: List[Dict] → JSON字符串 (条件配置列表)
    - metadata_json: Dict → JSON字符串
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    user_id: int = Field(0, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    game_gid: Optional[int] = Field(None, description="游戏GID")

    # HQL内容
    name_cn: Optional[str] = Field(None, description="中文名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    hql_type: str = Field("select", description="HQL类型: select, insert, create")
    hql: str = Field(..., description="生成的HQL语句")
    mode: str = Field("single", description="生成模式: single, join, union")

    # JSON字段 (存储为JSON字符串)
    events_json: List[Dict[str, Any]] = Field(default_factory=list, description="事件配置")
    fields_json: List[Dict[str, Any]] = Field(default_factory=list, description="字段配置")
    conditions_json: List[Dict[str, Any]] = Field(default_factory=list, description="条件配置列表")
    metadata_json: Optional[Dict[str, Any]] = Field(None, description="元数据")

    # 性能指标
    performance_score: Optional[int] = Field(None, ge=0, le=100, description="性能评分")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")

    @field_validator('name_cn', 'name_en', mode='before')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        import html

        if v:
            return html.escape(v.strip())
        return v

    @field_validator('events_json', 'fields_json', 'conditions_json', mode='before')
    @classmethod
    def deserialize_json_list(cls, v):
        """从数据库读取时反序列化JSON列表"""
        from backend.core.utils.json_helpers import deserialize_json_field

        return deserialize_json_field(v)

    @field_validator('metadata_json', mode='before')
    @classmethod
    def deserialize_json_dict(cls, v):
        """从数据库读取时反序列化JSON字典"""
        from backend.core.utils.json_helpers import deserialize_json_field

        return deserialize_json_field(v)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============================================================================
# Event Category Entity
# ============================================================================


class EventCategoryEntity(BaseModel):
    """
    事件类别实体 - 全局唯一的事件类别模型定义

    用于事件的分类管理, 如"充值/付费", "任务系统"等
    支持全局分类和游戏级别分类
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    name: str = Field(..., min_length=1, max_length=50, description="类别名称(唯一)")
    game_gid: Optional[int] = Field(None, description="游戏GID, 用于游戏级别的分类")
    name_cn: Optional[str] = Field(None, max_length=100, description="中文名称")
    description: Optional[str] = Field(None, description="类别描述")
    color: Optional[str] = Field(None, max_length=20, description="显示颜色")
    icon: Optional[str] = Field(None, max_length=50, description="图标名称")
    is_active: bool = Field(True, description="是否活跃")
    display_order: int = Field(0, description="显示顺序")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    # 统计信息(仅在查询时填充, 不写入数据库)
    event_count: Optional[int] = Field(default=0, description="该类别下的事件数量", exclude=True)

    @field_validator('name', 'name_cn', mode='before')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        import html

        if v:
            return html.escape(v.strip())
        return v

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ============================================================================
# Event Node Entity
# ============================================================================


class EventNodeEntity(BaseModel):
    """
    事件节点实体 - 全局唯一的事件节点模型定义

    用于Canvas系统中的事件节点配置
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    game_gid: int = Field(..., ge=0, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="节点名称")
    event_id: int = Field(..., ge=0, description="关联的事件ID")

    # 关联数据（仅用于显示，不存储）
    event_name: Optional[str] = Field(None, description="事件名称（仅显示用）")
    event_name_cn: Optional[str] = Field(None, description="事件中文名称（仅显示用）")

    # 配置
    config_json: Dict[str, Any] = Field(default_factory=dict, description="节点配置JSON")
    is_active: bool = Field(True, description="是否激活")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @field_validator('name', mode='before')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        import html

        return html.escape(v.strip())

    @field_validator('config_json', mode='before')
    @classmethod
    def deserialize_config(cls, v):
        """从数据库读取时反序列化配置"""
        from backend.core.utils.json_helpers import deserialize_json_field

        return deserialize_json_field(v)

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
