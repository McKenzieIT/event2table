#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Entity Module

事件相关的Entity定义
"""

import html
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


class EventEntity(BaseModel):
    """
    事件实体 - 全局唯一的事件模型定义

    用途:
    - API层: 请求验证和响应序列化
    - Service层: 业务逻辑传参
    - Repository层: 数据库读写
    """

    # 主键
    id: Optional[int] = Field(None, description="数据库自增ID")

    # 业务字段
    game_gid: int = Field(..., description="游戏业务GID（关联games.gid）")
    name: str = Field(..., min_length=1, max_length=100, description="事件名称（唯一）")
    name_cn: Optional[str] = Field(None, max_length=100, description="中文名称")
    description: Optional[str] = Field(None, description="事件描述")
    table_name: Optional[str] = Field(None, max_length=200, description="数据表名")
    event_name: Optional[str] = Field(None, alias="name", description="事件名称（兼容字段）")
    event_name_cn: Optional[str] = Field(None, alias="name_cn", description="中文名称（兼容字段）")

    # 关联字段
    category_id: Optional[int] = Field(None, description="事件类别ID（外键）")
    source_table: Optional[str] = Field(None, max_length=200, description="数据源表")
    target_table: Optional[str] = Field(None, max_length=200, description="目标表")

    # DWD配置
    include_in_common_params: bool = Field(False, description="是否包含在公共参数中")

    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    # 统计字段(不持久化)
    param_count: Optional[int] = Field(default=0, description="参数数量", exclude=True)

    @field_validator("name", "name_cn")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
