#!/usr/bin/env python3
"""
将旧的@cache_result装饰器迁移到新的@cached装饰器

目标：
1. 替换 @cache_result 装饰器为 @cached(ttl=1800)
2. 更新导入语句
3. 移除手动缓存键生成
"""
import os
import re
from pathlib import Path

def migrate_cache_decorators(file_path: str) -> bool:
    """
    迁移文件中的缓存装饰器

    返回: True如果文件被修改，False否则
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 1. 替换导入语句
        # 旧: from backend.core.cache.cache_system import cache_result
        # 新: from backend.core.cache.decorators import cached
        content = re.sub(
            r'from backend\.core\.cache\.cache_system import \([^)]*cache_result[^)]*\)',
            'from backend.core.cache.decorators import cached',
            content
        )

        # 2. 替换 @cache_result 装饰器
        # 旧模式1: @cache_result("pattern", timeout=xxx)
        # 新: @cached(ttl=1800)
        content = re.sub(
            r'@cache_result\(\s*"[^"]*",\s*timeout=[^)]*\)',
            '@cached(ttl=1800)',
            content
        )

        # 旧模式2: @cache_result("pattern", timeout=xxx)
        # 多行模式
        content = re.sub(
            r'@cache_result\(\s*"[^"]*",\s*timeout=\d+\s*\)',
            '@cached(ttl=1800)',
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        # 3. 如果内容被修改，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 迁移文件失败: {file_path} - {e}")
        return False

def migrate_specific_file(file_path: str) -> bool:
    """
    迁移特定文件（models/events.py）

    这个文件使用旧的多行@cache_result装饰器，需要特殊处理
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 1. 替换导入
        old_import = """from backend.core.cache.cache_system import (
    clear_event_cache,
    clear_game_cache,
    cache_result,
)"""

        new_import = """from backend.core.cache.cache_system import (
    clear_event_cache,
    clear_game_cache,
)
from backend.core.cache.decorators import cached"""

        content = content.replace(old_import, new_import)

        # 2. 替换特定的@cache_result装饰器
        # 模式1: get_events_paginated_cached
        old_pattern1 = """@cache_result(
    "events:list_by_game:{game_gid}:{page}:{per_page}",
    timeout=CacheConfig.CACHE_TIMEOUT_EVENTS,
)
def get_events_paginated_cached("""

        new_pattern1 = """@cached(ttl=1800)
def get_events_paginated_cached("""

        content = content.replace(old_pattern1, new_pattern1)

        # 模式2: get_active_parameters_cached
        old_pattern2 = """@cache_result(
    "params:active_by_event:{event_id}", timeout=CacheConfig.CACHE_TIMEOUT_PARAMS
)
def get_active_parameters_cached("""

        new_pattern2 = """@cached(ttl=1800)
def get_active_parameters_cached("""

        content = content.replace(old_pattern2, new_pattern2)

        # 模式3: get_events_count_cached
        old_pattern3 = """@cache_result(
    "events:count_by_game:{game_gid}", timeout=CacheConfig.CACHE_TIMEOUT_EVENTS
)
def get_events_count_cached("""

        new_pattern3 = """@cached(ttl=1800)
def get_events_count_cached("""

        content = content.replace(old_pattern3, new_pattern3)

        # 3. 如果内容被修改，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"❌ 迁移文件失败: {file_path} - {e}")
        return False

if __name__ == '__main__':
    # 迁移 models/events.py
    file_path = '/Users/mckenzie/Documents/event2table/backend/models/events.py'

    print("🔄 迁移缓存装饰器...")
    print(f"📁 文件: {file_path}")

    if migrate_specific_file(file_path):
        print("✅ 迁移成功！")

        # 显示修改后的函数
        print("\n📝 修改后的函数:")
        print("=" * 80)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 显示前3个迁移后的函数
        for i, line in enumerate(lines):
            if '@cached(ttl=1800)' in line:
                print(f"\n行 {i+1}:")
                for j in range(max(0, i-1), min(len(lines), i+5)):
                    print(f"  {j+1}: {lines[j]}", end='')

        print("\n" + "=" * 80)
    else:
        print("ℹ️  文件无需修改")
