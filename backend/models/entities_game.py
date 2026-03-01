#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Entity Module

游戏相关的Entity定义
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
import html


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
    ods_db: str = Field(..., pattern=r'^(ieu_ods|overseas_ods)$', description="ODS数据库名称")
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

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
