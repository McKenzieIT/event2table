"""
AST Analyzer.

Analyzes Python code using AST.
"""
import ast
from typing import List, Dict, Any


class ASTAnalyzer:
    """Analyzes Python AST."""

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            tree = ast.parse(content)

            return {
                "api_endpoints": self._extract_api_endpoints(tree),
                "services": self._extract_classes(tree, "Service"),
                "repositories": self._extract_classes(tree, "Repository"),
                "schemas": self._extract_classes(tree, "Schema"),
            }
        except Exception as e:
            return {"error": str(e)}

    def _extract_api_endpoints(self, tree: ast.AST) -> List[str]:
        """Extract Flask API endpoints."""
        endpoints = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if self._is_route_decorator(decorator):
                        endpoints.append(node.name)

        return endpoints

    def _is_route_decorator(self, decorator) -> bool:
        """Check if decorator is a Flask route."""
        if isinstance(decorator, ast.Call):
            if hasattr(decorator.func, 'attr'):
                return decorator.func.attr == 'route'
        return False

    def _extract_classes(self, tree: ast.AST, suffix: str) -> List[str]:
        """Extract classes with specific suffix."""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith(suffix):
                classes.append(node.name)

        return classes
