#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pydantic Data Models (Schema Layer)

定义所有数据传输对象（DTO）和验证模型
提供输入验证、序列化和文档化功能
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
import html

# ============================================================================
# Game 相关 Schema
# ============================================================================


class GameBase(BaseModel):
    """游戏基础模型"""

    gid: int = Field(..., ge=0, description="游戏业务ID (INTEGER)")
    name: str = Field(..., min_length=1, max_length=100, description="游戏名称")
    ods_db: Literal["ieu_ods", "overseas_ods"] = Field(..., description="ODS数据库名称")

    @validator("name")
    def sanitize_name(cls, v):
        """防止XSS攻击：转义HTML字符"""
        if v:
            return html.escape(v.strip())
        return v

    @validator("gid")
    def validate_gid(cls, v):
        """验证gid格式 - 必须是正整数"""
        if not isinstance(v, int):
            raise ValueError("gid必须是整数类型")
        if v < 0:
            raise ValueError("gid必须是正整数")
        return v


class GameCreate(GameBase):
    """游戏创建模型"""

    pass


class GameUpdate(BaseModel):
    """游戏更新模型"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    ods_db: Optional[Literal["ieu_ods", "overseas_ods"]] = None

    @validator("name")
    def sanitize_name(cls, v):
        """防止XSS攻击：转义HTML字符"""
        if v:
            return html.escape(v.strip())
        return v


class GameResponse(GameBase):
    """游戏响应模型"""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Event Parameter 相关 Schema
# ============================================================================


class EventParameterBase(BaseModel):
    """事件参数基础模型"""

    param_name: str = Field(..., min_length=1, max_length=100, description="参数英文名")
    param_name_cn: Optional[str] = Field(None, max_length=100, description="参数中文名")
    template_id: int = Field(default=1, description="参数模板ID")
    param_description: Optional[str] = Field(None, max_length=500, description="参数描述")
    json_path: Optional[str] = Field(None, max_length=200, description="JSON路径，用于从事件JSON中提取参数值")

    @validator("param_name")
    def sanitize_param_name(cls, v):
        """验证并清理参数名（snake_case）"""
        v = v.strip()
        if not v:
            raise ValueError("param_name不能为空")
        if " " in v:
            raise ValueError("param_name不能包含空格，请使用snake_case格式")
        return v

    @validator("param_name_cn")
    def sanitize_param_name_cn(cls, v):
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v

    @validator("param_description")
    def sanitize_description(cls, v):
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v

    @validator("json_path")
    def validate_json_path(cls, v):
        """验证JSON路径格式"""
        if v:
            v = v.strip()
            # JSON路径应该以$.开头
            if not v.startswith("$."):
                raise ValueError("json_path必须以'$.'开头（例如：'$.zoneId'）")
        return v


class EventParameterCreate(EventParameterBase):
    """事件参数创建模型"""

    pass


class EventParameterResponse(EventParameterBase):
    """事件参数响应模型"""

    id: int
    event_id: int
    is_active: bool = True
    version: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Event 相关 Schema
# ============================================================================


class EventBase(BaseModel):
    """事件基础模型"""

    game_gid: int = Field(..., description="游戏GID")
    event_name: str = Field(..., min_length=1, max_length=100, description="事件英文名")
    event_name_cn: str = Field(..., min_length=1, max_length=100, description="事件中文名")
    category_id: int = Field(..., description="事件分类ID")
    source_table: Optional[str] = Field(None, max_length=200, description="源表名")
    target_table: Optional[str] = Field(None, max_length=200, description="目标表名")
    include_in_common_params: bool = False

    @validator("event_name")
    def sanitize_event_name(cls, v):
        """验证并清理事件名"""
        v = v.strip()
        if not v:
            raise ValueError("event_name不能为空")
        if " " in v:
            raise ValueError("event_name不能包含空格")
        return v

    @validator("event_name_cn")
    def sanitize_event_name_cn(cls, v):
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v


class EventCreate(EventBase):
    """事件创建模型"""

    parameters: List[EventParameterCreate] = Field(default_factory=list, description="事件参数列表")

    @validator("parameters")
    def validate_parameters(cls, v):
        """验证至少有一个参数"""
        if not v or len(v) == 0:
            raise ValueError("至少需要一个参数")
        return v


class EventUpdate(BaseModel):
    """事件更新模型"""

    event_name_cn: Optional[str] = Field(None, min_length=1, max_length=100)
    category_id: Optional[int] = None
    include_in_common_params: Optional[bool] = None

    @validator("event_name_cn")
    def sanitize_event_name_cn(cls, v):
        """防止XSS攻击"""
        if v:
            return html.escape(v.strip())
        return v


class EventResponse(EventBase):
    """事件响应模型"""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # 关联数据
    game_name: Optional[str] = None
    category_name: Optional[str] = None
    param_count: Optional[int] = 0

    class Config:
        from_attributes = True


class EventDetailResponse(EventResponse):
    """事件详情响应模型（包含参数列表）"""

    parameters: List[EventParameterResponse] = Field(default_factory=list)


# ============================================================================
# HQL 生成相关 Schema
# ============================================================================


class FieldDefinition(BaseModel):
    """字段定义模型"""

    field_name: str = Field(..., description="字段名称")
    field_alias: Optional[str] = Field(None, description="字段别名")
    aggregation: Optional[Literal["COUNT", "SUM", "AVG", "MAX", "MIN", "GROUP_CONCAT"]] = Field(
        None, description="聚合函数"
    )

    @validator("field_name")
    def sanitize_field_name(cls, v):
        """验证字段名"""
        v = v.strip()
        if not v:
            raise ValueError("field_name不能为空")
        return v


class ConditionDefinition(BaseModel):
    """条件定义模型"""

    field: str = Field(..., description="条件字段")
    operator: Literal["=", "!=", ">", "<", ">=", "<=", "IN", "NOT IN", "LIKE", "BETWEEN"] = Field(
        ..., description="操作符"
    )
    value: Any = Field(..., description="条件值")
    logical_op: Literal["AND", "OR"] = Field("AND", description="逻辑操作符")


class HQLGenerationRequest(BaseModel):
    """HQL生成请求模型"""

    event_ids: List[int] = Field(..., min_length=1, description="事件ID列表")
    fields: List[FieldDefinition] = Field(..., min_length=1, description="字段定义列表")
    conditions: List[ConditionDefinition] = Field(default_factory=list, description="条件列表")
    group_by: Optional[List[str]] = Field(None, description="分组字段")
    order_by: Optional[Dict[str, Literal["ASC", "DESC"]]] = Field(None, description="排序字段")
    limit: Optional[int] = Field(None, ge=1, le=10000, description="限制数量")

    @validator("event_ids")
    def validate_event_ids(cls, v):
        """验证事件ID列表"""
        if not v or len(v) == 0:
            raise ValueError("至少需要一个事件ID")
        return v


class HQLGenerationResponse(BaseModel):
    """HQL生成响应模型"""

    hql: str = Field(..., description="生成的HQL语句")
    estimated_rows: Optional[int] = Field(None, description="预估行数")
    execution_time_ms: Optional[float] = Field(None, description="执行时间（毫秒）")
    tables_used: List[str] = Field(default_factory=list, description="使用的表")
    warnings: Optional[List[str]] = Field(None, description="警告信息")


# ============================================================================
# 通用 Schema
# ============================================================================


class PaginationParams(BaseModel):
    """分页参数模型"""

    page: int = Field(default=1, ge=1, description="页码（从1开始）")
    per_page: int = Field(default=20, ge=1, le=100, description="每页数量")


class ApiResponse(BaseModel):
    """通用API响应模型"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    meta: Optional[Dict[str, Any]] = Field(None, description="元数据（如分页信息）")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    success: bool = Field(default=False, description="是否成功")
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    path: Optional[str] = Field(None, description="请求路径")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


# ============================================================================
# 批量操作 Schema
# ============================================================================


class BatchDeleteRequest(BaseModel):
    """批量删除请求模型"""

    ids: List[int] = Field(..., min_length=1, description="要删除的ID列表")


class BatchUpdateRequest(BaseModel):
    """批量更新请求模型"""

    ids: List[int] = Field(..., min_length=1, description="要更新的ID列表")
    updates: Dict[str, Any] = Field(..., description="要更新的字段字典")


class BatchOperationResponse(BaseModel):
    """批量操作响应模型"""

    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    errors: Optional[List[str]] = Field(None, description="错误列表")


# ============================================================================
# 统计相关 Schema
# ============================================================================


class GameStatsResponse(BaseModel):
    """游戏统计响应模型"""

    game_id: int
    game_name: str
    total_events: int
    total_parameters: int
    latest_event_update: Optional[datetime] = None


class ParameterUsageStats(BaseModel):
    """参数使用统计模型"""

    param_name: str
    usage_count: int
    event_names: List[str]
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


# ============================================================================
# 导出相关 Schema
# ============================================================================


class ExportRequest(BaseModel):
    """导出请求模型"""

    game_gid: Optional[int] = Field(None, description="游戏GID（可选）")
    category_id: Optional[int] = Field(None, description="分类ID（可选）")
    format: Literal["xlsx", "csv", "json"] = Field("xlsx", description="导出格式")
    include_parameters: bool = Field(True, description="是否包含参数")
    include_inactive: bool = Field(False, description="是否包含非活跃参数")


class ExportResponse(BaseModel):
    """导出响应模型"""

    file_path: str = Field(..., description="文件路径")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    record_count: int = Field(..., description="记录数")
    download_url: str = Field(..., description="下载链接")
