#!/usr/bin/env python3
"""
REST API归档状态检查脚本
检查旧的REST API是否已归档
"""

import os
import re
from pathlib import Path
from datetime import datetime

def check_deprecated_status(file_path):
    """检查文件中的deprecated标记"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    deprecated_patterns = [
        r'@deprecated',
        r'DEPRECATED',
        r'deprecated',
        r'TODO.*remove',
        r'FIXME.*remove',
        r'legacy',
        r'Legacy',
    ]
    
    found_patterns = []
    for pattern in deprecated_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            found_patterns.extend(matches)
    
    return found_patterns

def check_archive_directory():
    """检查archive目录"""
    archive_path = Path('/Users/mckenzie/Documents/event2table/archive')
    
    if not archive_path.exists():
        return None
    
    archived_files = []
    for file_path in archive_path.rglob('*'):
        if file_path.is_file() and file_path.suffix in ['.py', '.js', '.jsx', '.ts', '.tsx']:
            archived_files.append(str(file_path.relative_to(archive_path)))
    
    return archived_files

def main():
    """主函数"""
    print("🔍 检查REST API归档状态...\n")
    
    backend_path = Path('/Users/mckenzie/Documents/event2table/backend/api/routes')
    
    # 检查deprecated标记
    print("📋 Deprecated标记检查:")
    deprecated_files = []
    
    for file_path in backend_path.glob('*.py'):
        if file_path.name.startswith('__') or file_path.name == 'graphql.py':
            continue
        
        patterns = check_deprecated_status(file_path)
        if patterns:
            deprecated_files.append({
                'file': file_path.name,
                'patterns': patterns[:3]  # 只显示前3个
            })
    
    if deprecated_files:
        print(f"  找到 {len(deprecated_files)} 个文件包含deprecated标记:")
        for item in deprecated_files:
            print(f"  - {item['file']}: {', '.join(item['patterns'][:2])}")
    else:
        print("  ❌ 未找到deprecated标记")
    
    # 检查archive目录
    print(f"\n📁 Archive目录检查:")
    archived_files = check_archive_directory()
    
    if archived_files:
        print(f"  找到 {len(archived_files)} 个已归档文件:")
        for file in archived_files[:10]:
            print(f"  - {file}")
        if len(archived_files) > 10:
            print(f"  ... 还有 {len(archived_files) - 10} 个文件")
    else:
        print("  ❌ Archive目录不存在或为空")
    
    # 检查legacy_api.py
    legacy_file = backend_path / 'legacy_api.py'
    if legacy_file.exists():
        print(f"\n⚠️  发现legacy_api.py文件:")
        print(f"  文件大小: {legacy_file.stat().st_size} bytes")
        print(f"  修改时间: {datetime.fromtimestamp(legacy_file.stat().st_mtime)}")
    
    return {
        'deprecated_files': deprecated_files,
        'archived_files': archived_files or [],
        'has_legacy': legacy_file.exists()
    }

if __name__ == '__main__':
    main()
