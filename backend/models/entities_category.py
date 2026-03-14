#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Category Entity Module

事件类别相关的Entity定义
"""

import html
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator('name', 'name_cn')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """防止XSS攻击"""
        import html

        if v:
            return html.escape(v.strip())
        return v

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
