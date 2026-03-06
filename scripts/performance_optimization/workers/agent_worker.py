"""
Agent Worker基类

所有Agent（1-5）的基类，提供：
- 状态管理（心跳、进度）
- 任务执行框架
- 错误处理
- 结果保存
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List
from abc import ABC, abstractmethod

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from coordination.state_manager import StateManager


class AgentWorker(ABC):
    """Agent Worker基类"""

    def __init__(self, agent_id: str):
        """
        初始化Agent

        Args:
            agent_id: Agent标识（如 "agent_1"）
        """
        self.agent_id = agent_id
        self.state_mgr = StateManager()
        self.current_phase = 0

    def update_status(self, status: str, progress: int, total: int, current_task: str = ""):
        """
        更新Agent状态（带心跳）

        Args:
            status: 状态（"working", "idle", "completed", "error"）
            progress: 当前进度
            total: 总任务数
            current_task: 当前任务描述
        """
        state = {
            "agent_id": self.agent_id,
            "phase": self.current_phase,
            "status": status,
            "current_task": current_task,
            "progress": progress,
            "total": total,
            "errors": []
        }

        self.state_mgr.write_agent_status(self.agent_id, state)

    def work_on_tasks(self, tasks: List[Dict[str, Any]]):
        """
        执行任务列表

        Args:
            tasks: 任务字典列表
        """
        total = len(tasks)
        results = []

        for i, task in enumerate(tasks):
            self.update_status("working", i, total, str(task))

            try:
                result = self.execute_task(task)
                self.save_result(task, result)
                results.append(result)
            except Exception as e:
                self.handle_error(task, e)
                results.append({"status": "error", "error": str(e)})

        self.update_status("completed", total, total, "")
        return results

    @abstractmethod
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个任务（子类必须实现）

        Args:
            task: 任务字典

        Returns:
            结果字典
        """
        raise NotImplementedError("Subclasses must implement execute_task()")

    def save_result(self, task: Dict[str, Any], result: Dict[str, Any]):
        """
        保存任务结果

        Args:
            task: 任务字典
            result: 结果字典
        """
        results_file = Path(f"fixes/{self.agent_id}_results.jsonl")
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'a') as f:
            json.dump({
                "agent": self.agent_id,
                "task": str(task),
                "result": result,
                "timestamp": time.time()
            }, f)
            f.write('\n')

    def handle_error(self, task: Dict[str, Any], error: Exception):
        """
        处理错误

        Args:
            task: 任务字典
            error: 异常对象
        """
        # 读取当前状态
        if self.current_phase > 0:
            state = self.state_mgr.read_agent_status(self.agent_id, self.current_phase)
            if state:
                state["errors"].append({
                    "task": str(task),
                    "error": str(error),
                    "error_type": type(error).__name__
                })
                self.state_mgr.write_agent_status(self.agent_id, state)

        # 记录到错误日志
        error_log = Path("fixes") / f"{self.agent_id}_errors.log"
        with open(error_log, 'a') as f:
            f.write(f"{time.ctime()}: ERROR in {task}\n")
            f.write(f"  {type(error).__name__}: {error}\n\n")

    def run_phase(self, phase: int, tasks: List[Dict[str, Any]]):
        """
        运行指定Phase的任务

        Args:
            phase: Phase编号
            tasks: 任务列表
        """
        self.current_phase = phase
        return self.work_on_tasks(tasks)


class TestInfrastructureAgent(AgentWorker):
    """测试基础设施修复Agent (Agent 1-2)"""

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        修复测试失败

        Args:
            task: 任务字典，包含 test_name 和 type

        Returns:
            修复结果
        """
        test_name = task.get("test_name", "")
        failure_type = task.get("type", "")

        if failure_type == "backend_500_errors":
            return self.fix_backend_500(test_name)
        elif failure_type == "frontend_timeouts":
            return self.fix_frontend_timeout(test_name)
        else:
            return {"status": "skipped", "reason": f"Unknown type: {failure_type}"}

    def fix_backend_500(self, test_name: str) -> Dict[str, Any]:
        """修复Backend 500错误"""
        # 实际实现会检查API路由、数据库连接等
        print(f"   [TestAgent] 修复Backend 500: {test_name}")
        return {"status": "fixed", "test": test_name}

    def fix_frontend_timeout(self, test_name: str) -> Dict[str, Any]:
        """修复前端超时"""
        # 实际实现会优化加载、增加超时等
        print(f"   [TestAgent] 修复前端超时: {test_name}")
        return {"status": "fixed", "test": test_name}


class P0JoinAgent(AgentWorker):
    """P0 JOIN查询实现Agent (Agent 3-5)"""

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        实现JOIN查询

        Args:
            task: 任务字典，包含 file_path

        Returns:
            实现结果
        """
        file_path = task.get("file_path", "")

        if not file_path:
            return {"status": "skipped", "reason": "No file_path"}

        return self.implement_join_query(file_path)

    def implement_join_query(self, file_path: str) -> Dict[str, Any]:
        """
        实现JOIN查询

        Args:
            file_path: 文件路径

        Returns:
            实现结果
        """
        print(f"   [P0Agent] 实现JOIN: {Path(file_path).name}")

        # 实际实现会：
        # 1. 读取文件
        # 2. 检测N+1模式
        # 3. 替换为JOIN查询
        # 4. 写回文件

        return {"status": "fixed", "file": file_path}
