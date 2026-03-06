"""
性能修复Agent

Phase 3使用的Agent，负责修复531个性能问题：
- N+1查询（添加@cached装饰器）
- React优化（添加React.memo）
- 其他性能问题
"""

import re
from pathlib import Path
from typing import Dict, Any

from agent_worker import AgentWorker


class PerformanceFixerAgent(AgentWorker):
    """性能问题修复Agent (Phase 3, 所有Agent)"""

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        修复性能问题

        Args:
            task: 任务字典，包含：
                - type: 问题类型
                - file_path: 文件路径
                - line: 行号

        Returns:
            修复结果
        """
        issue_type = task.get("type", "")
        file_path = task.get("file_path", "")
        line_number = task.get("line", 0)

        if not file_path:
            return {"status": "skipped", "reason": "No file_path"}

        if issue_type == "n_plus_1_query":
            return self.fix_n_plus_1(file_path, line_number)

        elif issue_type == "missing_react_memo":
            return self.add_react_memo(file_path)

        elif issue_type == "missing_cached":
            return self.add_cached_decorator(file_path)

        else:
            return {"status": "skipped", "reason": f"Unknown type: {issue_type}"}

    def fix_n_plus_1(self, file_path: str, line_number: int) -> Dict[str, Any]:
        """
        修复N+1查询（添加@cached装饰器）

        Args:
            file_path: 文件路径
            line_number: 行号

        Returns:
            修复结果
        """
        try:
            content = Path(file_path).read_text()
            lines = content.split('\n')

            # 检查是否已有@cached
            if '@cached' in content:
                return {"status": "skipped", "reason": "Already has @cached"}

            # 查找函数定义
            for i, line in enumerate(lines):
                # 查找查询函数（fetch_ 或 get_）
                if i == line_number - 1 and ('def fetch_' in line or 'def get_' in line):
                    # 检查前一行是否已有装饰器
                    if i > 0 and lines[i-1].strip().startswith('@'):
                        return {"status": "skipped", "reason": "Already has decorator"}

                    # 添加@cached装饰器
                    indent = len(line) - len(line.lstrip())
                    lines.insert(i, ' ' * indent + '@cached(ttl=1800)')

                    # 写回文件
                    Path(file_path).write_text('\n'.join(lines))

                    print(f"   [PerfAgent] 添加@cached: {Path(file_path).name}:{line_number}")

                    return {
                        "status": "fixed",
                        "fix": "Added @cached(ttl=1800) decorator",
                        "file": file_path,
                        "line": line_number
                    }

            return {"status": "skipped", "reason": "No matching function found"}

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "file": file_path
            }

    def add_react_memo(self, file_path: str) -> Dict[str, Any]:
        """
        添加React.memo（TSX/JSX文件）

        Args:
            file_path: 文件路径

        Returns:
            修复结果
        """
        try:
            if not (file_path.endswith('.tsx') or file_path.endswith('.jsx')):
                return {"status": "skipped", "reason": "Not a React component"}

            content = Path(file_path).read_text()

            # 检查是否已有React.memo
            if 'React.memo' in content:
                return {"status": "skipped", "reason": "Already has React.memo"}

            # 检测export default
            if 'export default' in content:
                # 替换为 export default React.memo(...)
                new_content = re.sub(
                    r'export default (\w+)',
                    r'export default React.memo(\1)',
                    content
                )

                # 添加React导入（如果缺少）
                if 'import React' not in content:
                    # 找到第一个import
                    lines = content.split('\n')
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.strip().startswith('import'):
                            insert_pos = i + 1
                            break

                    lines.insert(insert_pos, "import React from 'react';")
                    new_content = '\n'.join(lines)

                Path(file_path).write_text(new_content)

                print(f"   [PerfAgent] 添加React.memo: {Path(file_path).name}")

                return {
                    "status": "fixed",
                    "fix": "Added React.memo wrapper",
                    "file": file_path
                }

            return {"status": "skipped", "reason": "No export default found"}

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "file": file_path
            }

    def add_cached_decorator(self, file_path: str) -> Dict[str, Any]:
        """
        添加@cached装饰器（Python文件）

        Args:
            file_path: 文件路径

        Returns:
            修复结果
        """
        try:
            if not file_path.endswith('.py'):
                return {"status": "skipped", "reason": "Not a Python file"}

            content = Path(file_path).read_text()

            # 检查是否已有@cached
            if '@cached' in content:
                return {"status": "skipped", "reason": "Already has @cached"}

            lines = content.split('\n')

            # 查找所有查询函数
            fixed_count = 0
            for i, line in enumerate(lines):
                # 查找查询函数
                if 'def fetch_' in line or 'def get_' in line:
                    # 检查前一行是否已有装饰器
                    if i > 0 and lines[i-1].strip().startswith('@'):
                        continue

                    # 添加@cached装饰器
                    indent = len(line) - len(line.lstrip())
                    lines.insert(i, ' ' * indent + '@cached(ttl=1800)')
                    fixed_count += 1

            if fixed_count > 0:
                Path(file_path).write_text('\n'.join(lines))

                print(f"   [PerfAgent] 添加{fixed_count}个@cached: {Path(file_path).name}")

                return {
                    "status": "fixed",
                    "fix": f"Added {fixed_count} @cached decorators",
                    "file": file_path,
                    "count": fixed_count
                }

            return {"status": "skipped", "reason": "No matching functions found"}

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "file": file_path
            }
