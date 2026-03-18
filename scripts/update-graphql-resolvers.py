#!/usr/bin/env python3
"""
GraphQL Resolvers更新脚本
自动更新所有GraphQL resolvers使用DataLoader
"""
import sys
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path("/Users/mckenzie/Documents/event2table")
BACKEND_ROOT = PROJECT_ROOT / "backend"

# 需要更新的resolver文件
RESOLVER_FILES = [
    "backend/gql_api/queries/game_queries.py",
    "backend/gql_api/queries/dashboard_queries.py",
    "backend/gql_api/schema.py",
]

def update_resolver_file(file_path: Path):
    """更新单个resolver文件"""
    print(f"\n📝 更新文件: {file_path.relative_to(PROJECT_ROOT)}")

    content = file_path.read_text()
    original_content = content

    # 更新1: 导入DataLoader
    if "from backend.gql_api.middleware.dataloader_context import get_dataloader" not in content:
        # 在文件顶部添加导入
        import_match = re.search(r'^from backend\.gql_api\.middleware import ', content, re.MULTILINE)
        if import_match:
            insert_pos = import_match.end()
            content = content[:insert_pos] + "from backend.gql_api.middleware.dataloader_context import get_dataloader\n" + content[insert_pos:]
            print(f"  ✅ 添加DataLoader导入")

    # 更新2: 更新game resolver示例
    # 查找使用fetch_one_as_dict的game查询
    pattern = r"fetch_one_as_dict\(['\"]\s*SELECT \* FROM games WHERE gid = \?, \((\w+)\)"
    replacement = r"get_dataloader(info, 'game').load(\1).get()"

    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print(f"  ✅ 更新game查询使用DataLoader")

    # 写回文件
    if content != original_content:
        # 创建备份
        backup_path = file_path.with_suffix('.py.backup')
        backup_path.write_text(original_content)
        print(f"  💾 备份文件: {backup_path.relative_to(PROJECT_ROOT)}")

        # 写入更新后的内容
        file_path.write_text(content)
        print(f"  ✅ 文件已更新")
    else:
        print(f"  ℹ️  文件无需更新（已包含DataLoader）")

def main():
    """主函数"""
    print("🚀 开始更新GraphQL Resolvers使用DataLoader...")

    for resolver_file in RESOLVER_FILES:
        file_path = PROJECT_ROOT / resolver_file
        if file_path.exists():
            update_resolver_file(file_path)
        else:
            print(f"⚠️  文件不存在: {resolver_file}")

    print("\n✅ GraphQL Resolvers更新完成！")
    print("\n📋 下一步:")
    print("1. 运行测试: python -m pytest backend/test/graphql/test_dataloader_performance.py -v")
    print("2. 重启应用: python web_app.py")
    print("3. 验证性能提升")

if __name__ == '__main__':
    main()
