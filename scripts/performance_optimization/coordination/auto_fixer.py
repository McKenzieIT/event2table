"""
自动修复器

智能分诊Gate的核心组件，负责自动修复简单问题：
- IndentationError（缩进错误）
- ImportError（导入错误）
- SyntaxError（语法错误）
"""

import re
from pathlib import Path
from typing import Dict, Any


class AutoFixer:
    """简单问题自动修复器"""

    def __init__(self):
        self.fix_history = []

    def attempt_auto_fix(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """
        尝试自动修复失败

        Args:
            failure: 失败信息字典，包含：
                - error_type: 错误类型
                - file_path: 文件路径
                - line_number: 行号
                - error_message: 错误消息

        Returns:
            修复结果 {"status": "fixed" | "cannot_auto_fix", "fix": "..."}
        """
        error_type = failure.get("error_type", "")
        file_path = failure.get("file_path", "")

        if not file_path:
            return {"status": "cannot_auto_fix", "reason": "No file_path"}

        if error_type == "IndentationError":
            return self.fix_indentation_error(
                file_path,
                failure.get("line_number", 0)
            )

        elif error_type == "ImportError":
            return self.fix_import_error(
                file_path,
                failure.get("missing_import", {})
            )

        elif error_type == "SyntaxError":
            return self.fix_syntax_error(
                file_path,
                failure.get("line_number", 0),
                failure.get("error_message", "")
            )

        return {"status": "cannot_auto_fix", "reason": f"Unknown error_type: {error_type}"}

    def fix_indentation_error(self, file_path: str, line_number: int) -> Dict[str, Any]:
        """
        修复缩进错误

        Args:
            file_path: 文件路径
            line_number: 错误行号

        Returns:
            修复结果
        """
        try:
            content = Path(file_path).read_text()
            lines = content.split('\n')

            if line_number <= 0 or line_number > len(lines):
                return {"status": "cannot_auto_fix", "reason": "Invalid line_number"}

            error_line = lines[line_number - 1]

            # 分析前一行获取正确缩进
            if line_number > 1:
                prev_line = lines[line_number - 2]
                indent = len(prev_line) - len(prev_line.lstrip())

                # 修复当前行缩进
                lines[line_number - 1] = ' ' * indent + error_line.strip()

                # 写回文件
                Path(file_path).write_text('\n'.join(lines))

                self.fix_history.append({
                    "file": file_path,
                    "type": "indentation",
                    "line": line_number
                })

                return {
                    "status": "fixed",
                    "fix": f"Fixed indentation at line {line_number}"
                }

        except Exception as e:
            return {
                "status": "cannot_auto_fix",
                "reason": str(e)
            }

        return {"status": "cannot_auto_fix", "reason": "No previous line to detect indent"}

    def fix_import_error(self, file_path: str, missing_import: Dict[str, str]) -> Dict[str, Any]:
        """
        修复导入错误

        Args:
            file_path: 文件路径
            missing_import: 缺失导入信息 {"module": "...", "name": "..."}

        Returns:
            修复结果
        """
        try:
            content = Path(file_path).read_text()

            module = missing_import.get("module", "")
            name = missing_import.get("name", "")

            if not module or not name:
                return {"status": "cannot_auto_fix", "reason": "Missing import info"}

            # 构建导入语句
            import_statement = f"from {module} import {name}\n"

            # 检查是否已存在
            if name in content and module in content:
                return {"status": "skipped", "reason": "Import already exists"}

            # 在文件开头添加（在docstring之后）
            lines = content.split('\n')

            # 找到第一个非注释、非docstring行
            insert_pos = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
                    insert_pos = i
                    break

            lines.insert(insert_pos, import_statement.strip())

            Path(file_path).write_text('\n'.join(lines))

            self.fix_history.append({
                "file": file_path,
                "type": "import",
                "import": f"from {module} import {name}"
            })

            return {
                "status": "fixed",
                "fix": f"Added import: from {module} import {name}"
            }

        except Exception as e:
            return {
                "status": "cannot_auto_fix",
                "reason": str(e)
            }

    def fix_syntax_error(self, file_path: str, line_number: int, error_message: str) -> Dict[str, Any]:
        """
        修复语法错误

        Args:
            file_path: 文件路径
            line_number: 错误行号
            error_message: 错误消息

        Returns:
            修复结果
        """
        try:
            content = Path(file_path).read_text()
            lines = content.split('\n')

            if line_number <= 0 or line_number > len(lines):
                return {"status": "cannot_auto_fix", "reason": "Invalid line_number"}

            error_line = lines[line_number - 1]

            # 常见语法错误修复
            fixed_line = error_line

            # 修复: 缺少冒号
            if 'unexpected EOF' in error_message or ':' in error_message:
                if any(keyword in fixed_line for keyword in ['if', 'else', 'elif', 'for', 'while', 'def', 'class', 'try', 'except', 'finally', 'with']):
                    if not fixed_line.rstrip().endswith(':'):
                        fixed_line = fixed_line.rstrip() + ':'

            # 修复: 缺少闭合括号
            if 'unexpected EOF' in error_message or 'parenthesis' in error_message.lower():
                open_parens = fixed_line.count('(')
                close_parens = fixed_line.count(')')
                if open_parens > close_parens:
                    fixed_line += ')' * (open_parens - close_parens)

            # 修复: 缺少闭合引号
            if 'EOF' in error_message and ('"' in fixed_line or "'" in fixed_line):
                if '"' in fixed_line and fixed_line.count('"') % 2 != 0:
                    fixed_line += '"'
                elif "'" in fixed_line and fixed_line.count("'") % 2 != 0:
                    fixed_line += "'"

            if fixed_line != error_line:
                lines[line_number - 1] = fixed_line
                Path(file_path).write_text('\n'.join(lines))

                self.fix_history.append({
                    "file": file_path,
                    "type": "syntax",
                    "line": line_number
                })

                return {
                    "status": "fixed",
                    "fix": f"Fixed syntax at line {line_number}"
                }

        except Exception as e:
            return {
                "status": "cannot_auto_fix",
                "reason": str(e)
            }

        return {"status": "cannot_auto_fix", "reason": "Could not auto-fix syntax error"}

    def get_fix_summary(self) -> Dict[str, int]:
        """
        获取修复总结

        Returns:
            {"indentation": count, "import": count, "syntax": count}
        """
        summary = {
            "indentation": 0,
            "import": 0,
            "syntax": 0
        }

        for fix in self.fix_history:
            fix_type = fix.get("type", "")
            if fix_type in summary:
                summary[fix_type] += 1

        return summary


if __name__ == "__main__":
    # 测试自动修复器
    fixer = AutoFixer()

    # 测试缩进修复
    test_failure = {
        "error_type": "IndentationError",
        "file_path": "test_file.py",
        "line_number": 10
    }

    result = fixer.attempt_auto_fix(test_failure)
    print(f"Fix result: {result}")
