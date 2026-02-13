"""
AST Analyzer Utilities

Provides AST analysis utilities for code audit.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any


def analyze_file_ast(file_path: Path) -> Dict[str, Any]:
    """
    Analyze Python file using AST

    Args:
        file_path: Path to Python file

    Returns:
        Dictionary with analysis results
    """
    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity": 0
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    analysis["imports"].append(alias.name)

        return analysis

    except SyntaxError:
        return {"error": "Syntax error"}
    except Exception as e:
        return {"error": str(e)}
