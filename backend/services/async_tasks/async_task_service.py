#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Task Service - 异步任务服务

提供异步任务管理功能:
- 创建任务
- 查询任务状态
- 更新任务进度
- 清理过期任务
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from backend.core.data_access import GenericRepository
from backend.core.logging import get_logger
from backend.services.base_service import BaseService

logger = get_logger(__name__)


class AsyncTaskService(BaseService):
    """
    异步任务服务类

    负责管理异步任务的创建、查询、更新和清理
    """

    def __init__(self):
        """初始化异步任务服务"""
        super().__init__()
        self.task_repo = GenericRepository("async_tasks", primary_key="id")
        logger.info("✅ AsyncTaskService initialized")

    def create_task(
        self,
        task_type: str,
        payload: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
    ) -> str:
        """
        创建新的异步任务

        Args:
            task_type: 任务类型 (如: 'batch_import', 'data_export', 'sql_optimization')
            payload: 任务负载数据 (JSON序列化)
            created_by: 创建者标识

        Returns:
            任务ID (UUID字符串)

        Raises:
            ValueError: 如果task_type为空
        """
        if not task_type:
            raise ValueError("task_type is required")

        task_id = str(uuid.uuid4())

        task_data = {
            "task_id": task_id,
            "task_type": task_type,
            "status": "pending",
            "progress": 0,
            "result": None,
            "error_message": None,
            "created_by": created_by,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
        }

        if payload:
            task_data["result"] = json.dumps({"payload": payload})

        created = self.task_repo.create(task_data)

        if created:
            logger.info(f"任务创建成功: task_id={task_id}, type={task_type}")
            return task_id
        else:
            raise RuntimeError("Failed to create task")

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        根据任务ID获取任务详情

        Args:
            task_id: 任务ID (UUID字符串)

        Returns:
            任务详情字典, 不存在返回None
        """
        task = self.task_repo.find_by_field("task_id", task_id)

        if task:
            # 解析result字段
            if task.get("result"):
                try:
                    task["result"] = json.loads(task["result"])
                except (json.JSONDecodeError, TypeError):
                    pass

        return task

    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: Optional[int] = None,
        result: Optional[Any] = None,
        error: Optional[str] = None,
    ) -> bool:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态 ('pending', 'running', 'completed', 'failed')
            progress: 进度百分比 (0-100)
            result: 任务结果数据
            error: 错误信息

        Returns:
            是否更新成功

        Raises:
            ValueError: 如果任务不存在
        """
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        updates = {"status": status}

        # 更新进度
        if progress is not None:
            updates["progress"] = max(0, min(100, progress))

        # 更新时间戳
        if status == "running" and not task.get("started_at"):
            updates["started_at"] = datetime.now().isoformat()

        if status in ["completed", "failed"] and not task.get("completed_at"):
            updates["completed_at"] = datetime.now().isoformat()

        # 更新结果或错误信息
        if result is not None:
            if isinstance(result, (dict, list)):
                updates["result"] = json.dumps(result)
            else:
                updates["result"] = str(result)

        if error is not None:
            updates["error_message"] = error

        # 执行更新
        updated = self.task_repo.update(task["id"], updates)

        if updated:
            logger.info(f"任务状态更新: task_id={task_id}, status={status}, progress={progress}")
            # 清理任务相关缓存
            self.invalidate_pattern(f"async_tasks:*")
            return True

        return False

    def list_tasks(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = 100,
    ) -> List[Dict[str, Any]]:
        """
        列出任务

        Args:
            filters: 过滤条件
                - task_type: 任务类型
                - status: 任务状态
                - created_by: 创建者
            limit: 返回数量限制

        Returns:
            任务列表
        """
        conditions = {}

        if filters:
            if "task_type" in filters:
                conditions["task_type"] = filters["task_type"]
            if "status" in filters:
                conditions["status"] = filters["status"]
            if "created_by" in filters:
                conditions["created_by"] = filters["created_by"]

        tasks = self.task_repo.find_where(
            conditions=conditions,
            order_by="created_at DESC",
            limit=limit,
        )

        # 解析result字段
        for task in tasks:
            if task.get("result"):
                try:
                    task["result"] = json.loads(task["result"])
                except (json.JSONDecodeError, TypeError):
                    pass

        return tasks

    def cleanup_old_tasks(self, days: int = 30) -> int:
        """
        清理旧任务

        Args:
            days: 保留天数, 删除早于此天数的已完成或失败的任务

        Returns:
            删除的任务数量
        """
        from backend.core.utils.converters import fetch_all_as_dict

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()

        # 查询符合条件的任务
        query = """
            SELECT id FROM async_tasks
            WHERE status IN ('completed', 'failed')
            AND completed_at IS NOT NULL
            AND completed_at < ?
        """

        old_tasks = fetch_all_as_dict(query, (cutoff_str,))

        if not old_tasks:
            return 0

        task_ids = [task["id"] for task in old_tasks]
        deleted_count = self.task_repo.delete_batch(task_ids)

        logger.info(f"清理旧任务: 删除了 {deleted_count} 个任务 (早于 {days} 天)")

        # 清理缓存
        if deleted_count > 0:
            self.invalidate_pattern("async_tasks:*")

        return deleted_count

    def get_task_statistics(self) -> Dict[str, Any]:
        """
        获取任务统计信息

        Returns:
            统计信息字典
        """
        from backend.core.utils.converters import fetch_one_as_dict

        # 总任务数
        total_query = "SELECT COUNT(*) as count FROM async_tasks"
        total_result = fetch_one_as_dict(total_query)
        total_count = total_result["count"] if total_result else 0

        # 按状态统计
        status_query = """
            SELECT status, COUNT(*) as count
            FROM async_tasks
            GROUP BY status
        """
        status_results = fetch_all_as_dict(status_query)
        status_counts = {row["status"]: row["count"] for row in status_results}

        # 按类型统计
        type_query = """
            SELECT task_type, COUNT(*) as count
            FROM async_tasks
            GROUP BY task_type
        """
        type_results = fetch_all_as_dict(type_query)
        type_counts = {row["task_type"]: row["count"] for row in type_results}

        return {
            "total_tasks": total_count,
            "by_status": status_counts,
            "by_type": type_counts,
        }
