"""
N+1 Query Problem Detector

Detects N+1 query performance issues where database queries are executed inside loops.

Based on Event2Table performance standards:
- Forbidden: Database queries in loops (N+1 queries)
- Required: JOIN or prefetch patterns for related data
- Required: Batch queries with IN (...) instead of loop queries
"""

import ast
from pathlib import Path
from typing import List, Set
from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class NPlusOneQueryDetector(BaseDetector):
    """
    Detects N+1 query problems in code

    Rules:
    1. Database queries should not be inside for/while loops
    2. Related data should use JOIN instead of multiple queries
    3. Batch operations should use IN (...) instead of loop queries
    """

    # Database query functions that trigger N+1 problems in loops
    DB_QUERY_FUNCTIONS = {
        'fetch_all_as_dict',
        'fetch_one_as_dict',
        'execute_query',
        'execute_select',
        'fetchone',
        'fetchall',
    }

    def __init__(self):
        super().__init__()
        self.rule_id = "PERF_N_PLUS_ONE_001"

    def is_applicable(self, file_path: str) -> bool:
        """
        Check if detector applies to this file

        Analyze Python files in backend/ directory
        """
        file_path = Path(file_path)
        return (
            file_path.suffix == '.py' and
            'backend' in file_path.parts and
            'test' not in str(file_path).lower() and
            '__pycache__' not in str(file_path)
        )

    def detect(self, file_path: str) -> List[Issue]:
        """Detect N+1 query issues"""
        issues = []

        try:
            content = Path(file_path).read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Check for loops
                if isinstance(node, (ast.For, ast.While)):
                    issues.extend(self._check_loop_for_queries(file_path, node))

                # Check for function calls that might indicate N+1
                if isinstance(node, ast.FunctionDef):
                    issues.extend(self._check_function_for_patterns(file_path, node))

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _check_loop_for_queries(
        self,
        file_path: str,
        loop: ast.For
    ) -> List[Issue]:
        """Check if loop contains database queries"""
        issues = []

        # Find all function calls in loop body
        for node in ast.walk(loop):
            if isinstance(node, ast.Call):
                func_name = self._get_call_function_name(node)
                if func_name in self.DB_QUERY_FUNCTIONS:
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.CRITICAL,
                        category=IssueCategory.QUALITY,
                        message=f"N+1 query problem: Database query '{func_name}' inside loop",
                        suggestion="Refactor to use JOIN or batch query with IN (...) to avoid N+1 performance issue",
                        code_snippet=f"for item in items:\n    {func_name}(...)  # ← N+1 query",
                        rule_id=self.rule_id,
                        metadata={'query_function': func_name}
                    ))

        return issues

    def _check_function_for_patterns(
        self,
        file_path: str,
        func: ast.FunctionDef
    ) -> List[Issue]:
        """Check function for N+1 query patterns"""
        issues = []

        # Pattern 1: Multiple similar queries in a function
        # Pattern 2: Query followed by loop that uses results for more queries

        # Collect all query calls
        query_calls = []
        for node in ast.walk(func):
            if isinstance(node, ast.Call):
                func_name = self._get_call_function_name(node)
                if func_name in self.DB_QUERY_FUNCTIONS:
                    query_calls.append((node.lineno, func_name))

        # If we have multiple queries with same pattern, flag it
        if len(query_calls) > 2:
            # Group by function name
            query_names = [name for _, name in query_calls]
            unique_names = set(query_names)

            # If same query function called multiple times
            for query_name in unique_names:
                count = query_names.count(query_name)
                if count >= 3:
                    # Find first occurrence
                    first_line = next(line for line, name in query_calls if name == query_name)
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=first_line,
                        severity=Severity.HIGH,
                        category=IssueCategory.QUALITY,
                        message=f"Potential N+1 pattern: {query_name}() called {count} times in function",
                        suggestion=f"Consider refactoring to use a single JOIN query or batch operation with IN (...)",
                        code_snippet=f"# {query_name}() called {count} times",
                        rule_id=self.rule_id,
                        metadata={'query_function': query_name, 'call_count': count}
                    ))

        return issues

    def _get_call_function_name(self, call: ast.Call) -> str:
        """Get function name from Call node"""
        if isinstance(call.func, ast.Name):
            return call.func.id
        elif isinstance(call.func, ast.Attribute):
            return call.func.attr
        return ""
