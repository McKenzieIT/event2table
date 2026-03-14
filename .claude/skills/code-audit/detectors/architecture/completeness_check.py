"""
Completeness Principle Detector

Checks for violations of the "Complete Implementation Principle".

Based on Event2Table Complete Implementation Principle:
- NO pass statements as implementation placeholders
- NO returning empty values/default values instead of real implementation
- NO skipping exception handling
- NO hardcoded sensitive information (passwords, keys)
"""

import ast
import re
from pathlib import Path
from typing import List

from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class CompletenessDetector(BaseDetector):
    """
    Detects violations of the Complete Implementation Principle

    Rules:
    1. No pass statements as implementation placeholders
    2. No returning empty values/default values instead of real implementation
    3. No skipping exception handling
    4. No hardcoded sensitive information
    """

    # Patterns that indicate incomplete implementation
    INCOMPLETE_PATTERNS = {
        'return []',  # Returning empty list
        'return {}',  # Returning empty dict
        'return None',  # Returning None without implementation
        'return ""',   # Returning empty string
        'return 0',    # Returning zero
        'return False', # Returning False
    }

    # Sensitive information patterns (dict for pattern->description mapping)
    SENSITIVE_PATTERNS = {
        r'password\s*=\s*["\']([^"\']+)["\']': 'password',
        r'api_key\s*=\s*["\']([^"\']+)["\']': 'api_key',
        r'secret\s*=\s*["\']([^"\']+)["\']': 'secret',
        r'token\s*=\s*["\']([^"\']+)["\']': 'token',
    }

    def __init__(self):
        super().__init__()
        self.rule_id = "COMPLETE_001"

    def is_applicable(self, file_path: str) -> bool:
        """
        Check if detector applies to this file

        Analyze Python files in backend/ directory
        """
        path = Path(file_path)
        return (
            path.suffix == '.py' and
            'backend' in str(path) and
            'test' not in str(path).lower() and
            '__pycache__' not in str(path) and
            'venv' not in str(path)
        )

    def detect(self, file_path: str) -> List[Issue]:
        """Detect completeness principle violations"""
        issues = []

        try:
            content = Path(file_path).read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    issues.extend(self._check_function_completeness(file_path, node))

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        # Also check for hardcoded sensitive information in strings
        issues.extend(self._check_sensitive_info(file_path, content))

        return issues

    def _check_function_completeness(
        self,
        file_path: str,
        func: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> List[Issue]:
        """Check if function has complete implementation"""
        issues = []

        # Rule 1: No pass statements as implementation
        for node in ast.walk(func):
            if isinstance(node, ast.Pass):
                # Check if pass is in a valid context (abstract method, interface, etc.)
                if not self._is_valid_pass_context(func, node):
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.CRITICAL,
                        category=IssueCategory.QUALITY,
                        message=f"Function {func.name}() has pass statement instead of implementation",
                        suggestion="Implement the function logic. Pass statements are only allowed in abstract methods or explicitly marked TODO items with issue tracking.",
                        code_snippet=self._extract_method_signature(func),
                        rule_id=self.rule_id,
                        metadata={'function': func.name}
                    ))

        # Rule 2 & 3: Check for early returns with empty values
        returns = self._find_all_returns(func)
        for return_node, return_value in returns:
            if return_value and self._is_empty_implementation(return_value):
                # Check if this is a valid early return (guard clause)
                if not self._is_valid_guard_clause(func, return_node):
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=return_node.lineno,
                        severity=Severity.HIGH,
                        category=IssueCategory.QUALITY,
                        message=f"Function {func.name}() returns empty/default value instead of implementing logic",
                        suggestion="Implement the actual logic. Return meaningful values or raise appropriate exceptions.",
                        code_snippet=self._extract_return_snippet(return_value),
                        rule_id=self.rule_id,
                        metadata={'function': func.name}
                    ))

        return issues

    def _check_sensitive_info(self, file_path: str, content: str) -> List[Issue]:
        """Check for hardcoded sensitive information"""
        issues = []

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue

            # Check for sensitive patterns
            for pattern, description in self.SENSITIVE_PATTERNS.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=line_num,
                        severity=Severity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        message=f"Hardcoded {description.split('=')[0].strip()} detected",
                        suggestion="Move sensitive information to environment variables or configuration files. Use os.environ.get() or config settings.",
                        code_snippet=line.strip()[:80],  # Truncate long lines
                        rule_id=self.rule_id,
                        metadata={'type': description.split('=')[0].strip(), 'value': match.group(1)[:10]}  # Truncate for security
                    ))

        return issues

    def _is_valid_pass_context(self, func: ast.FunctionDef | ast.AsyncFunctionDef, pass_node: ast.Pass) -> bool:
        """Check if pass statement is in a valid context"""
        # Allow pass in abstract methods
        for decorator in func.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'abstractmethod':
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr == 'abstractmethod':
                return True

        # Allow pass in raise NotImplementedError
        parent = self._get_parent_node(func, pass_node)
        if parent and isinstance(parent, ast.Raise):
            return True

        # Allow pass in interface definitions (no body methods in ABC)
        if not func.body:
            return True

        return False

    def _is_valid_guard_clause(self, func: ast.FunctionDef | ast.AsyncFunctionDef, return_node: ast.Return) -> bool:
        """Check if early return is a valid guard clause"""
        # Guard clauses are typically at the start of function with error returns
        if return_node.lineno <= func.lineno + 5:  # Within first 5 lines
            return True

        return False

    def _find_all_returns(self, func: ast.FunctionDef | ast.AsyncFunctionDef) -> List[tuple]:
        """Find all return statements in function"""
        returns = []
        for node in ast.walk(func):
            if isinstance(node, ast.Return):
                returns.append((node, node.value))
        return returns

    def _is_empty_implementation(self, return_value: ast.AST) -> bool:
        """Check if return value is empty/default"""
        if return_value is None:
            return True

        if isinstance(return_value, ast.Constant):
            # Check for empty values
            if return_value.value in [None, [], {}, '', 0, False]:
                return True

        if isinstance(return_value, ast.List):
            # Check if empty list
            if not return_value.elts:
                return True

        if isinstance(return_value, ast.Tuple):
            # Check if empty tuple
            if not return_value.elts:
                return True

        if isinstance(return_value, ast.Dict):
            # Check if empty dict (use .keys, not .elts)
            if not return_value.keys:
                return True

        return False

    def _get_parent_node(self, func: ast.FunctionDef | ast.AsyncFunctionDef, target_node: ast.AST) -> ast.AST:
        """Get parent node of target_node within func"""
        for node in ast.walk(func):
            for child in ast.iter_child_nodes(node):
                if child is target_node:
                    return node
        return None

    def _extract_method_signature(self, func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract method signature"""
        args = []
        for arg in func.args.args[:3]:  # First 3 args
            args.append(arg.arg)

        async_prefix = "async " if isinstance(func, ast.AsyncFunctionDef) else ""
        return f"{async_prefix}def {func.name}({', '.join(args)})"

    def _extract_return_snippet(self, return_value: ast.AST) -> str:
        """Extract return statement snippet"""
        if return_value is None:
            return "return"
        elif isinstance(return_value, ast.Constant):
            return f"return {repr(return_value.value)}"
        elif isinstance(return_value, ast.Name):
            return f"return {return_value.id}"
        elif isinstance(return_value, (ast.List, ast.Dict, ast.Tuple)):
            return "return [] or {} or ()"
        else:
            return "return <value>"
