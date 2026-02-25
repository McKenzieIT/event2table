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
    - ods_db: 只能是ieu_ods或overseas_ods
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    gid: int = Field(..., ge=0, description="游戏业务GID")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: Literal["ieu_ods", "overseas_ods"] = Field(
        ..., description="ODS数据库名称"
    )
    description: Optional[str] = Field(None, description="游戏描述")
    dwd_prefix: str = Field("dwd", description="DWD表前缀")
    icon_path: Optional[str] = Field(None, description="图标路径")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    # 关联数据 (统计信息,不持久化到数据库)
    event_count: Optional[int] = Field(default=0, description="事件数量统计", exclude=True)

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
    - name (Entity) ↔ event_name (Database)
    - name_cn (Entity) ↔ event_name_cn (Database)
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段 (使用数据库列名作为字段名，同时接受Entity字段名作为别名)
    game_gid: int = Field(..., ge=0, description="游戏GID")

    # 使用alias同时接受name和event_name
    event_name: str = Field(..., alias="name", min_length=1, max_length=100, description="事件名称")
    event_name_cn: Optional[str] = Field(None, alias="name_cn", max_length=100, description="事件中文名")

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
    param_type: Literal["base", "param", "common", "calculate"] = Field(
        "base", description="参数类型"
    )
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
    param_type: Literal["base", "param", "calculate"] = Field(
        "param", description="参数类型"
    )
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
