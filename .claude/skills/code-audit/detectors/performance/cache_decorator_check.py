"""
Cache Decorator Compliance Detector

Checks for proper use of caching decorators in Service layer methods.
Ensures @cached and @cache_invalidate decorators are used correctly.

Based on Event2Table caching standards:
- Read operations (SELECT) should use @cached(ttl=300-1800)
- Write operations (INSERT/UPDATE/DELETE) should use @cache_invalidate
"""

import ast
import re
from pathlib import Path
from typing import List, Optional
from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class CacheDecoratorDetector(BaseDetector):
    """
    Detects missing or improper cache decorators in Service layer

    Rules:
    1. Service methods that query database should use @cached decorator
    2. Service methods that modify data should use @cache_invalidate decorator
    3. Cache TTL should be in reasonable range (300-1800 seconds)
    4. Cache key should include function parameters to avoid shared cache
    """

    # Database query functions that indicate need for caching
    DB_QUERY_FUNCTIONS = {
        'fetch_all_as_dict',
        'fetch_one_as_dict',
        'execute_query',
        'execute_select',
    }

    # Write operation patterns
    WRITE_PATTERNS = {
        r'INSERT\s+INTO',
        r'UPDATE\s+\w+\s+SET',
        r'DELETE\s+FROM',
        r'create_',
        r'update_',
        r'delete_',
        r'add_',
        r'remove_',
    }

    def __init__(self, min_ttl: int = 300, max_ttl: int = 1800):
        super().__init__()
        self.rule_id = "PERF_CACHE_001"
        self.min_ttl = min_ttl
        self.max_ttl = max_ttl

    def is_applicable(self, file_path: str) -> bool:
        """
        Check if detector applies to this file

        Only analyze Python files in backend/services/ directory
        """
        path = Path(file_path)
        return (
            path.suffix == '.py' and
            'services' in str(path) and
            'test' not in str(path).lower()
        )

    def detect(self, file_path: str) -> List[Issue]:
        """Detect cache decorator issues"""
        issues = []

        try:
            content = Path(file_path).read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if this is a Service class
                    if self._is_service_class(node):
                        # Check all methods in this service class
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                issues.extend(self._check_method_decorators(
                                    file_path, node.name, item
                                ))
                            elif isinstance(item, ast.AsyncFunctionDef):
                                # Handle async functions similarly
                                issues.extend(self._check_method_decorators(
                                    file_path, node.name, item
                                ))

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _is_service_class(self, node: ast.ClassDef) -> bool:
        """Check if class is a Service class"""
        return node.name.endswith('Service')

    def _check_method_decorators(
        self,
        file_path: str,
        class_name: str,
        method: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> List[Issue]:
        """Check if method has appropriate cache decorators"""
        issues = []

        # Check if method has database queries
        has_db_query = self._has_database_query(method)
        if not has_db_query:
            return issues

        # Check if method is a write operation
        is_write_operation = self._is_write_operation(method)

        # Get decorator names
        decorators = self._get_decorator_names(method)

        if is_write_operation:
            # Write operations should use @cache_invalidate
            if 'cache_invalidate' not in decorators:
                issues.append(Issue(
                    file_path=file_path,
                    line_number=method.lineno,
                    severity=Severity.HIGH,
                    category=IssueCategory.QUALITY,
                    message=f"Write operation missing @cache_invalidate decorator: {class_name}.{method.name}",
                    suggestion="Add @cache_invalidate decorator to this method to clear cached data after modification",
                    code_snippet=self._extract_code_snippet(method),
                    rule_id=self.rule_id
                ))
        else:
            # Read operations should use @cached decorator
            if 'cached' not in decorators:
                issues.append(Issue(
                    file_path=file_path,
                    line_number=method.lineno,
                    severity=Severity.HIGH,
                    category=IssueCategory.QUALITY,
                    message=f"Query method missing @cached decorator: {class_name}.{method.name}",
                    suggestion="Add @cached(ttl=300-1800) decorator to cache query results and reduce database load",
                    code_snippet=self._extract_code_snippet(method),
                    rule_id=self.rule_id
                ))
            else:
                # Check TTL value
                for decorator in method.decorator_list:
                    if isinstance(decorator, ast.Call):
                        decorator_name = self._get_decorator_name(decorator)
                        if decorator_name == 'cached':
                            ttl_value = self._extract_ttl_value(decorator)
                            if ttl_value is not None:
                                if ttl_value < self.min_ttl or ttl_value > self.max_ttl:
                                    issues.append(Issue(
                                        file_path=file_path,
                                        line_number=method.lineno,
                                        severity=Severity.MEDIUM,
                                        category=IssueCategory.QUALITY,
                                        message=f"Cache TTL out of recommended range: {ttl_value}s (recommended: {self.min_ttl}-{self.max_ttl}s)",
                                        suggestion=f"Adjust TTL to between {self.min_ttl} and {self.max_ttl} seconds for optimal balance between performance and data freshness",
                                        code_snippet=self._extract_code_snippet(method),
                                        rule_id=self.rule_id,
                                        metadata={'ttl': ttl_value}
                                    ))

        return issues

    def _has_database_query(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method contains database query calls"""
        for node in ast.walk(method):
            if isinstance(node, ast.Call):
                func_name = self._get_call_function_name(node)
                if func_name in self.DB_QUERY_FUNCTIONS:
                    return True
        return False

    def _is_write_operation(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method performs write operations"""
        # Check method name
        method_name = method.name.lower()
        for pattern in ['create', 'update', 'delete', 'add', 'remove', 'insert']:
            if pattern in method_name:
                return True

        # Check for SQL write operations in strings
        for node in ast.walk(method):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for pattern in self.WRITE_PATTERNS:
                    if re.search(pattern, node.value, re.IGNORECASE):
                        return True

        return False

    def _get_decorator_names(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
        """Get list of decorator names"""
        decorators = []
        for decorator in method.decorator_list:
            decorators.append(self._get_decorator_name(decorator))
        return [d for d in decorators if d]

    def _get_decorator_name(self, decorator: ast.AST) -> Optional[str]:
        """Get decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        return None

    def _get_call_function_name(self, call: ast.Call) -> Optional[str]:
        """Get function name from Call node"""
        if isinstance(call.func, ast.Name):
            return call.func.id
        elif isinstance(call.func, ast.Attribute):
            return call.func.attr
        return None

    def _extract_ttl_value(self, decorator: ast.Call) -> Optional[int]:
        """Extract TTL value from @cached decorator"""
        if len(decorator.args) >= 1:
            arg = decorator.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                return int(arg.value)
        elif decorator.keywords:
            for keyword in decorator.keywords:
                if keyword.arg == 'ttl':
                    if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, (int, float)):
                        return int(keyword.value.value)
        return None

    def _extract_code_snippet(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract code snippet for issue report (method signature only)"""
        # Return method signature as snippet
        async_prefix = "async " if isinstance(method, ast.AsyncFunctionDef) else ""
        return f"{async_prefix}def {method.name}(...):"
