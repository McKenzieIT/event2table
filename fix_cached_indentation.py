#!/usr/bin/env python3
"""
自动修复@cached装饰器缩进错误

Worker 4添加的@cached装饰器缩进不正确。
这个脚本自动修复所有backend/目录下的缩进问题。
"""

import re
from pathlib import Path

def fix_cached_indentation(file_path: Path) -> bool:
    """
    修复文件中的@cached缩进错误

    模式1:
    @cached(ttl=...)
        def function(...)

    应该改为:
        @cached(ttl=...)
        def function(...)

    Returns:
        bool: 是否进行了修复
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        new_lines = []
        modified = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # 检测模式：@cached在行首（无缩进），下一行是缩进的def
            if re.match(r'^@cached\(ttl=\d+\)', line.strip()):
                next_line = lines[i + 1] if i + 1 < len(lines) else ""

                # 检查下一行是否是缩进的def
                if next_line.strip().startswith('def ') and next_line.startswith('    '):
                    # 需要修复：给@cached添加缩进
                    indent = re.match(r'^(\s+)', next_line)
                    if indent:
                        new_indent = indent.group(1)
                        new_lines.append(new_indent + line.strip())
                        modified = True
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

            i += 1

        if modified:
            file_path.write_text('\n'.join(new_lines), encoding='utf-8')
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """主函数"""
    backend_dir = Path('/Users/mckenzie/Documents/event2table/backend')

    # 查找所有包含@cached的Python文件
    py_files = list(backend_dir.rglob('*.py'))

    fixed_count = 0
    for py_file in py_files:
        content = py_file.read_text(encoding='utf-8')
        if '@cached' in content:
            if fix_cached_indentation(py_file):
                fixed_count += 1

    print(f"\n🎉 总共修复了 {fixed_count} 个文件")

if __name__ == '__main__':
    main()
