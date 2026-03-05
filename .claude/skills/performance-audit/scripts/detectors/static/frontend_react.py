"""
Frontend React Performance Detector

Detects React performance anti-patterns:
- Missing React.memo on components
- Missing useMemo on expensive computations
- Missing useCallback on callbacks
"""

import ast
from pathlib import Path
from typing import List, Dict, Any


def detect(source_dir: Path) -> List[Dict[str, Any]]:
    """Detect React performance issues"""
    issues = []
    
    if not source_dir.exists():
        print(f"  ⚠️  Source directory not found: {source_dir}")
        return issues
    
    # Find all React component files
    jsx_files = list(source_dir.rglob("*.jsx"))
    tsx_files = list(source_dir.rglob("*.tsx"))
    
    print(f"  📁 Analyzing {len(jsx_files) + len(tsx_files)} React files...")
    
    for file_path in jsx_files + tsx_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Simple pattern-based detection (can be enhanced with AST)
            issues.extend(_detect_patterns(file_path, source_code))
            
        except Exception as e:
            pass
    
    return issues


def _detect_patterns(file_path: Path, source_code: str) -> List[Dict[str, Any]]:
    """Detect common React performance patterns"""
    issues = []
    
    # Pattern 1: Large components without React.memo
    if len(source_code) > 500 and 'React.memo' not in source_code:
        if 'export' in source_code and 'function' in source_code:
            issues.append({
                'type': 'missing_react_memo',
                'severity': 'MEDIUM',
                'category': 'frontend',
                'file_path': str(file_path),
                'line': 1,
                'message': f'Large component file ({len(source_code)} chars) without React.memo',
                'suggestion': 'Consider wrapping with React.memo to prevent unnecessary re-renders'
            })
    
    # Pattern 2: Array methods without useMemo
    if '.map(' in source_code and 'useMemo' not in source_code:
        issues.append({
            'type': 'potential_missing_usememo',
            'severity': 'LOW',
            'category': 'frontend',
            'file_path': str(file_path),
            'line': 1,
            'message': 'Array.map() found without useMemo',
            'suggestion': 'If mapping large datasets, wrap computation in useMemo'
        })
    
    # Pattern 3: useEffect with dependencies that might cause re-renders
    if 'useEffect' in source_code and 'useCallback' not in source_code:
        if 'function' in source_code or '=>' in source_code:
            issues.append({
                'type': 'potential_missing_usecallback',
                'severity': 'LOW',
                'category': 'frontend',
                'file_path': str(file_path),
                'line': 1,
                'message': 'useEffect found without useCallback for dependencies',
                'suggestion': 'Use useCallback for functions passed to useEffect dependencies'
            })
    
    return issues
