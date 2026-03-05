"""
Backend Query Performance Detector

Detects backend performance issues:
- N+1 query patterns
- Missing @cached decorators
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any


def detect(source_dir: Path) -> List[Dict[str, Any]]:
    """Detect backend query performance issues"""
    issues = []
    
    if not source_dir.exists():
        print(f"  ⚠️  Backend directory not found: {source_dir}")
        return issues
    
    py_files = list(source_dir.rglob("*.py"))
    print(f"  📁 Analyzing {len(py_files)} Python files...")
    
    for file_path in py_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            issues.extend(_detect_query_patterns(file_path, source_code))
            
        except Exception as e:
            pass
    
    return issues


def _detect_query_patterns(file_path: Path, source_code: str) -> List[Dict[str, Any]]:
    """Detect N+1 query patterns"""
    issues = []
    
    # Pattern 1: for loop with database query (N+1)
    for_loop_pattern = r'for\s+\w+\s+in\s+[\w\[\]]+:.*?(fetch_|execute_|select|query)'
    if re.search(for_loop_pattern, source_code, re.DOTALL | re.IGNORECASE):
        issues.append({
            'type': 'potential_n_plus_1_query',
            'severity': 'HIGH',
            'category': 'backend',
            'file_path': str(file_path),
            'line': 1,
            'message': 'Possible N+1 query detected: database query inside loop',
            'suggestion': 'Use eager loading (JOIN) or prefetch to avoid N+1 queries'
        })
    
    # Pattern 2: Query function without @cached decorator
    if 'def get_' in source_code or 'def fetch_' in source_code:
        if '@cached' not in source_code and '@cache' not in source_code:
            if 'SELECT' in source_code or 'fetch_' in source_code:
                issues.append({
                    'type': 'missing_cache_decorator',
                    'severity': 'MEDIUM',
                    'category': 'backend',
                    'file_path': str(file_path),
                    'line': 1,
                    'message': 'Query function without @cached decorator',
                    'suggestion': 'Add @cached decorator to improve performance'
                })
    
    return issues
