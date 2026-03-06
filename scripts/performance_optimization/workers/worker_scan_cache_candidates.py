#!/usr/bin/env python3
"""
扫描backend/目录，查找需要添加@cached装饰器的查询函数

目标：找到所有fetch_、get_开头的查询函数，添加@cached(ttl=1800)装饰器
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def is_already_cached(file_path: str, content: str) -> bool:
    """检查文件是否已经有@cached装饰器"""
    return '@cached' in content or '@cache_invalidate' in content

def has_import(content: str) -> bool:
    """检查文件是否已经导入了cached装饰器"""
    return 'from backend.core.cache.decorators import' in content or \
           'from backend.core.cache import' in content

def find_query_functions(content: str, file_path: str) -> List[Dict]:
    """
    查找文件中所有需要缓存的查询函数

    返回: [
        {
            'name': 'function_name',
            'line': line_number,
            'is_fetch': True/False,
            'is_get': True/False,
            'has_select': True/False,
            'has_fetch_call': True/False,
            'is_nested': True/False  # 是否是嵌套函数
        },
        ...
    ]
    """
    functions = []
    lines = content.split('\n')

    # 匹配函数定义
    function_pattern = re.compile(r'^(\s*)(def|async def)\s+(fetch_\w+|get_\w+)\s*\(')

    for i, line in enumerate(lines, start=1):
        match = function_pattern.match(line)
        if match:
            indent = match.group(1)
            func_name = match.group(3)

            # 检查是否是嵌套函数（缩进>4个空格）
            is_nested = len(indent) > 4

            # 检查函数体（向下扫描20行）
            function_body = '\n'.join(lines[i:min(i+20, len(lines))])

            # 检查是否包含数据库查询
            has_select = 'SELECT' in function_body.upper()
            has_fetch_call = 'fetch_' in function_body
            has_execute = 'execute_' in function_body

            # 检查是否已有旧缓存装饰器
            has_old_cache = '@cache_result' in lines[i-1] if i > 0 else False

            # 如果是查询函数且不是嵌套函数，添加到列表
            if (has_select or has_fetch_call) and not is_nested and not has_old_cache:
                functions.append({
                    'name': func_name,
                    'line': i,
                    'is_fetch': func_name.startswith('fetch_'),
                    'is_get': func_name.startswith('get_'),
                    'has_select': has_select,
                    'has_fetch_call': has_fetch_call,
                    'has_execute': has_execute,
                    'is_nested': is_nested,
                    'has_old_cache': has_old_cache
                })

    return functions

def scan_backend_directory(backend_dir: str) -> Dict:
    """
    扫描backend目录，查找需要添加缓存的文件

    返回: {
        'total_files': int,
        'scanned_files': int,
        'already_cached_files': int,
        'files_needing_cache': int,
        'total_functions': int,
        'files': [
            {
                'path': 'file_path',
                'functions': [function_info, ...],
                'needs_import': True/False
            },
            ...
        ]
    }
    """
    backend_path = Path(backend_dir)

    result = {
        'total_files': 0,
        'scanned_files': 0,
        'already_cached_files': 0,
        'files_needing_cache': 0,
        'total_functions': 0,
        'files': []
    }

    # 遍历所有Python文件
    for py_file in backend_path.rglob('*.py'):
        # 跳过测试文件、虚拟环境、缓存
        if 'test' in str(py_file) or '__pycache__' in str(py_file) or 'venv' in str(py_file):
            continue

        result['total_files'] += 1

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            result['scanned_files'] += 1

            # 检查是否已经有缓存装饰器
            if is_already_cached(str(py_file), content):
                result['already_cached_files'] += 1
                continue

            # 查找查询函数
            functions = find_query_functions(content, str(py_file))

            if functions:
                result['files_needing_cache'] += 1
                result['total_functions'] += len(functions)

                result['files'].append({
                    'path': str(py_file),
                    'relative_path': str(py_file.relative_to(backend_path)),
                    'functions': functions,
                    'needs_import': not has_import(content)
                })

        except Exception as e:
            print(f"⚠️  扫描文件失败: {py_file} - {e}")
            continue

    return result

def generate_report(result: Dict) -> str:
    """生成扫描报告"""
    report = []
    report.append("=" * 80)
    report.append("缓存装饰器扫描报告")
    report.append("=" * 80)
    report.append("")
    report.append(f"📊 扫描统计:")
    report.append(f"  - 总文件数: {result['total_files']}")
    report.append(f"  - 已扫描文件: {result['scanned_files']}")
    report.append(f"  - 已有缓存文件: {result['already_cached_files']}")
    report.append(f"  - 需要添加缓存文件: {result['files_needing_cache']}")
    report.append(f"  - 需要添加缓存的函数: {result['total_functions']}")
    report.append("")

    if result['files']:
        report.append("📁 需要添加缓存的文件列表:")
        report.append("")

        for file_info in result['files']:
            report.append(f"文件: {file_info['relative_path']}")
            report.append(f"  函数数: {len(file_info['functions'])}")
            report.append(f"  需要导入: {'是' if file_info['needs_import'] else '否'}")
            report.append("  函数列表:")

            for func in file_info['functions']:
                report.append(f"    - {func['name']} (行{func['line']})")
                if func['has_select']:
                    report.append(f"      ✓ 包含SELECT查询")
                if func['has_fetch_call']:
                    report.append(f"      ✓ 包含fetch调用")
                if func['is_nested']:
                    report.append(f"      ⚠️  嵌套函数（跳过）")
                if func['has_old_cache']:
                    report.append(f"      ⚠️  已有旧缓存装饰器")
            report.append("")

    report.append("=" * 80)

    return '\n'.join(report)

if __name__ == '__main__':
    # 设置backend目录路径
    backend_dir = '/Users/mckenzie/Documents/event2table/backend'

    print("🔍 开始扫描backend目录...")
    result = scan_backend_directory(backend_dir)

    # 生成报告
    report = generate_report(result)
    print(report)

    # 保存报告到文件
    report_path = '/Users/mckenzie/Documents/event2table/docs/reports/2026-03-06/CACHE-SCAN-REPORT.md'
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ 报告已保存到: {report_path}")
