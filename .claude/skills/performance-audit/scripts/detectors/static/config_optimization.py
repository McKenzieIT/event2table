"""
Configuration Performance Detector

Detects build and configuration performance issues:
- Missing code splitting
- Missing compression
- Missing optimization settings
"""

import re
from pathlib import Path
from typing import List, Dict, Any


def detect(config_path: Path) -> List[Dict[str, Any]]:
    """Detect configuration performance issues"""
    issues = []
    
    if not config_path.exists():
        print(f"  ⚠️  Config file not found: {config_path}")
        return issues
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        print(f"  📁 Analyzing configuration: {config_path.name}")
        issues.extend(_detect_config_patterns(config_path, source_code))
        
    except Exception as e:
        pass
    
    return issues


def _detect_config_patterns(file_path: Path, source_code: str) -> List[Dict[str, Any]]:
    """Detect build configuration issues"""
    issues = []
    
    # Pattern 1: Missing code splitting
    if 'build:' in source_code and 'splitChunks' not in source_code and 'manualChunks' not in source_code:
        if 'Vite' in source_code or 'vite' in source_code.lower():
            issues.append({
                'type': 'missing_code_splitting',
                'severity': 'MEDIUM',
                'category': 'config',
                'file_path': str(file_path),
                'line': 1,
                'message': 'Build config missing code splitting',
                'suggestion': 'Enable manualChunks in build.rollupOptions to reduce bundle size'
            })
    
    # Pattern 2: Missing compression
    if 'compress' not in source_code.lower() and 'gzip' not in source_code.lower():
        issues.append({
            'type': 'missing_compression',
            'severity': 'MEDIUM',
            'category': 'config',
            'file_path': str(file_path),
            'line': 1,
            'message': 'Build config missing compression (gzip/brotli)',
            'suggestion': 'Enable compression to reduce transfer size by 60-80%'
        })
    
    return issues
