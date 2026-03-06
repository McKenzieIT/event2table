"""
并行优化状态管理模块

基于文件锁的Agent状态协调系统，支持：
- Agent状态读写（带文件锁）
- Phase锁管理
- 完成标志（.flag文件）管理
"""

import json
from pathlib import Path
from datetime import datetime
import fcntl  # Unix文件锁
from typing import Dict, Optional

class StateManager:
    """Agent状态管理器 - 基于文件锁的协调机制"""

    def __init__(self, base_dir: Path = Path("status")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_agent_status(self, agent_id: str, status: dict) -> None:
        """
        写入Agent状态（原子操作，使用文件锁）

        Args:
            agent_id: Agent标识（如 "agent_1"）
            status: 状态字典，包含：
                - agent_id: str
                - phase: int
                - status: str ("working", "idle", "completed", "error")
                - current_task: str
                - progress: int
                - total: int
                - errors: list
                - last_heartbeat: str (ISO格式时间戳)
        """
        phase = status.get("phase", 1)
        phase_dir = self.base_dir / f"phase_{phase}_agents"
        phase_dir.mkdir(parents=True, exist_ok=True)

        status_file = phase_dir / f"{agent_id}_status.json"
        status["last_heartbeat"] = datetime.now().isoformat()

        # 使用文件锁确保原子写入
        with open(status_file, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # 排他锁
            json.dump(status, f, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def read_agent_status(self, agent_id: str, phase: int) -> Optional[Dict]:
        """
        读取Agent状态

        Args:
            agent_id: Agent标识
            phase: Phase编号

        Returns:
            状态字典，如果文件不存在则返回None
        """
        status_file = self.base_dir / f"phase_{phase}_agents" / f"{agent_id}_status.json"
        if not status_file.exists():
            return None

        with open(status_file, 'r') as f:
            return json.load(f)

    def read_all_agent_statuses(self, phase: int) -> Dict[str, Dict]:
        """
        读取指定Phase的所有Agent状态

        Args:
            phase: Phase编号

        Returns:
            {agent_id: status_dict} 字典
        """
        phase_dir = self.base_dir / f"phase_{phase}_agents"
        if not phase_dir.exists():
            return {}

        statuses = {}
        for status_file in phase_dir.glob("*_status.json"):
            agent_id = status_file.stem.replace("_status", "")
            with open(status_file, 'r') as f:
                statuses[agent_id] = json.load(f)

        return statuses

    def create_lock(self, phase_name: str) -> None:
        """
        创建Phase锁（原子操作）

        Args:
            phase_name: Phase名称（如 "phase_1"）
        """
        lock_file = self.base_dir / f"{phase_name}_lock.json"
        with open(lock_file, 'w') as f:
            json.dump({
                "locked_at": datetime.now().isoformat(),
                "phase": phase_name
            }, f)

    def check_lock(self, phase_name: str) -> bool:
        """
        检查Phase锁是否存在

        Args:
            phase_name: Phase名称

        Returns:
            True if lock exists, False otherwise
        """
        lock_file = self.base_dir / f"{phase_name}_lock.json"
        return lock_file.exists()

    def remove_lock(self, phase_name: str) -> None:
        """
        移除Phase锁

        Args:
            phase_name: Phase名称
        """
        lock_file = self.base_dir / f"{phase_name}_lock.json"
        if lock_file.exists():
            lock_file.unlink()

    def create_flag(self, flag_name: str) -> None:
        """
        创建完成标志（原子操作，使用空文件）

        Args:
            flag_name: 标志名称（如 "phase_1_complete"）
        """
        flag_file = self.base_dir / f"{flag_name}.flag"
        flag_file.touch()  # 创建空文件

    def check_flag(self, flag_name: str) -> bool:
        """
        检查完成标志是否存在

        Args:
            flag_name: 标志名称

        Returns:
            True if flag exists, False otherwise
        """
        flag_file = self.base_dir / f"{flag_name}.flag"
        return flag_file.exists()

    def save_checkpoint(self, phase: int, checkpoint_data: dict) -> None:
        """
        保存Phase检查点

        Args:
            phase: Phase编号
            checkpoint_data: 检查点数据
        """
        import subprocess

        checkpoint_dir = Path("checkpoints")
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        checkpoint_file = checkpoint_dir / f"phase_{phase}_complete.json"

        # 添加Git commit信息
        try:
            git_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            git_commit = "unknown"

        checkpoint_data["git_commit"] = git_commit
        checkpoint_data["timestamp"] = datetime.now().isoformat()

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

    def load_checkpoint(self, phase: int) -> Optional[Dict]:
        """
        加载Phase检查点

        Args:
            phase: Phase编号

        Returns:
            检查点数据，如果不存在则返回None
        """
        checkpoint_file = Path("checkpoints") / f"phase_{phase}_complete.json"
        if not checkpoint_file.exists():
            return None

        with open(checkpoint_file, 'r') as f:
            return json.load(f)
