#!/usr/bin/env python3
"""
Deprecated Code Cleanup Script

Automatically identifies and removes deprecated code from the codebase.
Provides safe removal with backup and rollback capabilities.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeprecatedCodeCleaner:
    """
    Deprecated Code Cleaner
    
    Identifies and removes deprecated code safely.
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / 'archive' / 'deprecated_cleanup'
        self.deprecated_patterns = [
            r'@deprecated',
            r'DEPRECATED',
            r'deprecated',
            r'TODO.*remove',
            r'FIXME.*remove',
            r'# Legacy',
            r'# Old API',
            r'# Backward compatibility',
        ]
        
        # Files to skip
        self.skip_patterns = [
            r'__pycache__',
            r'\.pyc$',
            r'\.git',
            r'node_modules',
            r'venv',
            r'\.venv',
            r'archive',
        ]
    
    def scan_deprecated_code(self) -> Dict[str, List[Tuple[int, str]]]:
        """
        Scan for deprecated code in the project.
        
        Returns:
            Dict mapping file paths to list of (line_number, line_content) tuples
        """
        deprecated_files = {}
        
        for file_path in self._get_source_files():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                deprecated_lines = []
                for line_num, line in enumerate(lines, 1):
                    for pattern in self.deprecated_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            deprecated_lines.append((line_num, line.strip()))
                            break
                
                if deprecated_lines:
                    deprecated_files[str(file_path.relative_to(self.project_root))] = deprecated_lines
                    
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
        
        return deprecated_files
    
    def _get_source_files(self) -> List[Path]:
        """Get all source files to scan"""
        source_files = []
        
        for ext in ['*.py', '*.js', '*.jsx', '*.ts', '*.tsx']:
            for file_path in self.project_root.rglob(ext):
                # Skip certain directories
                if any(re.search(pattern, str(file_path)) for pattern in self.skip_patterns):
                    continue
                source_files.append(file_path)
        
        return source_files
    
    def create_backup(self, file_path: str):
        """Create backup of file before modification"""
        source = self.project_root / file_path
        if not source.exists():
            return
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{source.name}.backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(source, backup_path)
        logger.info(f"Created backup: {backup_path}")
    
    def remove_deprecated_functions(self, file_path: str, function_names: List[str]):
        """Remove deprecated functions from a file"""
        source = self.project_root / file_path
        if not source.exists():
            logger.warning(f"File not found: {file_path}")
            return
        
        # Create backup
        self.create_backup(file_path)
        
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove each deprecated function
        for func_name in function_names:
            # Pattern to match function definition
            pattern = rf'def {func_name}\([^)]*\):[^\n]*\n(.*?)(?=\ndef |\nclass |\Z)'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            logger.info(f"Removed function: {func_name} from {file_path}")
        
        # Write modified content
        with open(source, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def remove_deprecated_classes(self, file_path: str, class_names: List[str]):
        """Remove deprecated classes from a file"""
        source = self.project_root / file_path
        if not source.exists():
            logger.warning(f"File not found: {file_path}")
            return
        
        # Create backup
        self.create_backup(file_path)
        
        with open(source, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove each deprecated class
        for class_name in class_names:
            # Pattern to match class definition
            pattern = rf'class {class_name}[^:]*:[^\n]*\n(.*?)(?=\nclass |\ndef |\Z)'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            logger.info(f"Removed class: {class_name} from {file_path}")
        
        # Write modified content
        with open(source, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_cleanup_report(self) -> str:
        """Generate a cleanup report"""
        deprecated_files = self.scan_deprecated_code()
        
        report = []
        report.append("# Deprecated Code Cleanup Report")
        report.append(f"\n**Generated**: {datetime.now().isoformat()}")
        report.append(f"\n## Summary")
        report.append(f"- Total files with deprecated code: {len(deprecated_files)}")
        
        total_lines = sum(len(lines) for lines in deprecated_files.values())
        report.append(f"- Total deprecated lines: {total_lines}")
        
        report.append(f"\n## Details")
        for file_path, lines in deprecated_files.items():
            report.append(f"\n### {file_path}")
            for line_num, line_content in lines:
                report.append(f"- Line {line_num}: {line_content}")
        
        return '\n'.join(report)


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cleanup_deprecated_code.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    cleaner = DeprecatedCodeCleaner(project_root)
    
    # Scan for deprecated code
    print("🔍 Scanning for deprecated code...")
    deprecated_files = cleaner.scan_deprecated_code()
    
    print(f"\n📊 Found {len(deprecated_files)} files with deprecated code")
    
    # Generate report
    report = cleaner.generate_cleanup_report()
    print("\n" + report)
    
    # Save report
    report_path = Path(project_root) / 'DEPRECATED_CODE_CLEANUP_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_path}")


if __name__ == '__main__':
    main()
