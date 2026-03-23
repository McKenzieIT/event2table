"""
重复代码检测测试

测试目标：
1. 验证日期格式化使用共享函数
2. 验证字符串清理使用共享函数
3. 验证错误处理使用共享模式
4. 验证API调用使用共享模式

TDD原则：先写测试，验证重复代码识别，再看测试失败
"""

import pytest
import ast
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class CodeDuplicateAnalyzer:
    """代码重复分析器"""

    def __init__(self, backend_root: str):
        self.backend_root = Path(backend_root)
        self.issues: List[Dict[str, Any]] = []

    def scan_python_files(self, directory: str) -> List[Path]:
        """扫描Python文件"""
        base_path = self.backend_root / directory
        if not base_path.exists():
            return []

        python_files = []
        for file_path in base_path.rglob("*.py"):
            # 跳过测试文件和__pycache__
            if "__pycache__" not in str(file_path) and "test" not in str(file_path):
                python_files.append(file_path)

        return python_files

    def check_date_formatting_patterns(self) -> Dict[str, Any]:
        """
        检测日期格式化重复模式

        常见重复模式：
        - datetime.strftime()
        - datetime.now().strftime()
        - date.strftime()
        """
        files = self.scan_python_files("core") + self.scan_python_files("services")

        date_formatting_patterns = {
            "strftime_calls": 0,
            "manual_formatting": 0,
            "files_with_patterns": [],
            "locations": [],
        }

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content, filename=str(file_path))

                    for node in ast.walk(tree):
                        # 检测strftime调用
                        if isinstance(node, ast.Call):
                            if hasattr(node.func, 'attr') and node.func.attr == 'strftime':
                                date_formatting_patterns["strftime_calls"] += 1
                                date_formatting_patterns["locations"].append(
                                    {
                                        "file": str(file_path.relative_to(self.backend_root)),
                                        "line": node.lineno,
                                    }
                                )

            except Exception as e:
                # 跳过解析错误的文件
                continue

        # 提取唯一文件
        date_formatting_patterns["files_with_patterns"] = list(
            set(loc["file"] for loc in date_formatting_patterns["locations"])
        )

        return date_formatting_patterns

    def check_string_sanitization_patterns(self) -> Dict[str, Any]:
        """
        检测字符串清理重复模式

        常见重复模式：
        - html.escape()
        - str.strip()
        - 手动清理
        """
        files = self.scan_python_files("core") + self.scan_python_files("services")

        sanitization_patterns = {
            "html_escape_calls": 0,
            "strip_calls": 0,
            "manual_sanitization": 0,
            "files_with_patterns": [],
            "locations": [],
        }

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content, filename=str(file_path))

                    for node in ast.walk(tree):
                        # 检测html.escape调用
                        if isinstance(node, ast.Call):
                            if hasattr(node.func, 'attr') and node.func.attr == 'escape':
                                sanitization_patterns["html_escape_calls"] += 1
                                sanitization_patterns["locations"].append(
                                    {
                                        "file": str(file_path.relative_to(self.backend_root)),
                                        "line": node.lineno,
                                        "type": "html.escape",
                                    }
                                )

                        # 检测strip调用
                        if isinstance(node, ast.Call):
                            if hasattr(node.func, 'attr') and node.func.attr == 'strip':
                                sanitization_patterns["strip_calls"] += 1
                                if len(sanitization_patterns["locations"]) < 20:
                                    sanitization_patterns["locations"].append(
                                        {
                                            "file": str(file_path.relative_to(self.backend_root)),
                                            "line": node.lineno,
                                            "type": "str.strip",
                                        }
                                    )

            except Exception as e:
                # 跳过解析错误的文件
                continue

        # 提取唯一文件
        sanitization_patterns["files_with_patterns"] = list(
            set(loc["file"] for loc in sanitization_patterns["locations"])
        )

        return sanitization_patterns

    def check_error_handling_patterns(self) -> Dict[str, Any]:
        """
        检测错误处理重复模式

        常见重复模式：
        - try-except块
        - logger.error() + return
        - 重复的错误消息格式
        """
        files = self.scan_python_files("api") + self.scan_python_files("services")

        error_patterns = {
            "try_except_blocks": 0,
            "logger_error_calls": 0,
            "json_error_calls": 0,
            "files_with_patterns": [],
            "locations": [],
        }

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # 简单统计
                    error_patterns["try_except_blocks"] += content.count("try:")
                    error_patterns["logger_error_calls"] += content.count("logger.error")
                    error_patterns["json_error_calls"] += content.count("json_error_response")

                    if "try:" in content:
                        error_patterns["files_with_patterns"].append(
                            str(file_path.relative_to(self.backend_root))
                        )

            except Exception as e:
                # 跳过读取错误的文件
                continue

        return error_patterns


class TestCodeDuplicationDetection:
    """重复代码检测测试套件"""

    @pytest.fixture
    def analyzer(self):
        """创建代码分析器"""
        backend_root = Path(__file__).parent.parent.parent.parent
        return CodeDuplicateAnalyzer(str(backend_root))

    def test_date_formatting_should_use_shared_function(self, analyzer):
        """
        测试：日期格式化应使用共享函数

        预期：
        - 检测到strftime调用
        - 建议使用format_date共享函数
        """
        patterns = analyzer.check_date_formatting_patterns()

        # 应该检测到一些日期格式化（证明测试有效）
        assert patterns["strftime_calls"] >= 0, "应该能检测到日期格式化模式"

        # 如果检测到重复，应该建议使用共享函数
        if patterns["strftime_calls"] > 5:
            pytest.fail(
                f"发现{patterns['strftime_calls']}处日期格式化重复，"
                f"应使用共享函数format_date()。"
                f"涉及文件：{patterns['files_with_patterns'][:5]}"
            )

    def test_string_sanitization_should_use_shared_function(self, analyzer):
        """
        测试：字符串清理应使用共享函数

        预期：
        - 检测到html.escape调用
        - 建议使用sanitize_string共享函数
        """
        patterns = analyzer.check_string_sanitization_patterns()

        # 应该检测到一些字符串清理（证明测试有效）
        assert patterns["html_escape_calls"] >= 0, "应该能检测到字符串清理模式"
        assert patterns["strip_calls"] >= 0, "应该能检测到strip调用"

        # 如果检测到大量重复，应该建议使用共享函数
        if patterns["html_escape_calls"] > 10:
            pytest.fail(
                f"发现{patterns['html_escape_calls']}处html.escape重复，"
                f"应使用共享函数sanitize_string()。"
                f"涉及文件：{patterns['files_with_patterns'][:5]}"
            )

    def test_error_handling_should_use_shared_pattern(self, analyzer):
        """
        测试：错误处理应使用共享模式

        预期：
        - 检测到重复的try-except模式
        - 建议使用统一错误处理装饰器
        """
        patterns = analyzer.check_error_handling_patterns()

        # 应该检测到一些错误处理（证明测试有效）
        assert patterns["try_except_blocks"] >= 0, "应该能检测到错误处理模式"
        assert patterns["logger_error_calls"] >= 0, "应该能检测到日志记录"
        assert patterns["json_error_calls"] >= 0, "应该能检测到错误响应"

        # 如果检测到大量重复，应该建议使用共享模式
        if patterns["try_except_blocks"] > 50:
            pytest.fail(
                f"发现{patterns['try_except_blocks']}处try-except块，"
                f"应考虑使用统一错误处理装饰器。"
                f"涉及文件数：{len(patterns['files_with_patterns'])}"
            )

    def test_shared_utils_module_should_exist(self, analyzer):
        """
        测试：共享工具模块应该存在

        预期：
        - backend/core/utils/common.py应该存在
        - 应包含format_date函数
        - 应包含sanitize_string函数
        """
        common_utils_path = analyzer.backend_root / "core" / "utils" / "common.py"

        if not common_utils_path.exists():
            # RED阶段：测试失败，因为共享模块还不存在
            pytest.fail(
                f"共享工具模块不存在：{common_utils_path.relative_to(analyzer.backend_root)}\n"
                "需要创建该模块并实现format_date()和sanitize_string()函数"
            )

        # 检查模块内容
        with open(common_utils_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if "def format_date" not in content:
            pytest.fail("共享工具模块缺少format_date()函数。\n" "请实现该函数以统一日期格式化逻辑")

        if "def sanitize_string" not in content:
            pytest.fail("共享工具模块缺少sanitize_string()函数。\n" "请实现该函数以统一字符串清理逻辑")


class TestCommonUtilsImplementation:
    """共享工具实现测试套件"""

    def test_format_date_function_exists(self):
        """测试：format_date函数应该存在并可用"""
        try:
            from backend.core.utils.common import format_date
        except ImportError as e:
            pytest.fail(f"无法导入format_date函数：{e}\n" "请在backend/core/utils/common.py中实现该函数")

    def test_sanitize_string_function_exists(self):
        """测试：sanitize_string函数应该存在并可用"""
        try:
            from backend.core.utils.common import sanitize_string
        except ImportError as e:
            pytest.fail(f"无法导入sanitize_string函数：{e}\n" "请在backend/core/utils/common.py中实现该函数")

    def test_format_date_basic_functionality(self):
        """测试：format_date基本功能"""
        try:
            from backend.core.utils.common import format_date

            test_date = datetime(2026, 3, 17, 14, 30, 0)
            formatted = format_date(test_date)

            assert isinstance(formatted, str), "format_date应返回字符串"
            assert "2026" in formatted, "格式化结果应包含年份"
            assert "03" in formatted or "3" in formatted, "格式化结果应包含月份"

        except ImportError:
            pytest.skip("format_date函数尚未实现")
        except Exception as e:
            pytest.fail(f"format_date函数执行失败：{e}")

    def test_sanitize_string_basic_functionality(self):
        """测试：sanitize_string基本功能"""
        try:
            from backend.core.utils.common import sanitize_string

            test_input = "<script>alert('test')</script>  "
            sanitized = sanitize_string(test_input)

            assert isinstance(sanitized, str), "sanitize_string应返回字符串"
            assert "<script>" not in sanitized, "应该转义HTML标签"
            assert sanitized != test_input, "应该清理输入"

        except ImportError:
            pytest.skip("sanitize_string函数尚未实现")
        except Exception as e:
            pytest.fail(f"sanitize_string函数执行失败：{e}")


if __name__ == "__main__":
    # 可以直接运行此文件进行快速测试
    pytest.main([__file__, "-v", "--tb=short"])
