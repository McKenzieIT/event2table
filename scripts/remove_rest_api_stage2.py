#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST API 阶段2移除脚本

移除前端迁移完成后不再使用的REST API模块:
- games.py
- events.py
- parameters.py
- categories.py
- flows.py

使用方法:
    python scripts/remove_rest_api_stage2.py --dry-run  # 预览
    python scripts/remove_rest_api_stage2.py --execute  # 执行
"""

import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path


class RESTAPIStage2Remover:
    """REST API阶段2移除工具"""

    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.api_routes_dir = self.project_root / "backend" / "api" / "routes"
        self.archive_dir = self.project_root / "archive" / "backend" / "api" / "removed_stage2"

        # 阶段2要移除的API模块
        self.stage2_apis = [
            "games.py",
            "events.py",
            "parameters.py",
            "categories.py",
            "flows.py"
        ]

        # 创建归档目录
        if not self.dry_run:
            self.archive_dir.mkdir(parents=True, exist_ok=True)

    def check_frontend_migration(self):
        """检查前端迁移状态"""
        print("\n" + "="*60)
        print("前端迁移状态检查")
        print("="*60)

        # 运行迁移检查工具
        check_script = self.project_root / "scripts" / "check_migration_progress.py"
        if check_script.exists():
            print("\n运行迁移进度检查...")
            import subprocess
            result = subprocess.run(
                ['python3', str(check_script)],
                capture_output=True,
                text=True
            )
            
            # 检查是否还有REST API调用
            if "REST API: 0" in result.stdout or "✅ 无REST API使用" in result.stdout:
                print("✅ 前端迁移完成,可以安全移除REST API")
                return True
            else:
                print("⚠️  前端仍有REST API调用,建议先完成前端迁移")
                print("\n迁移进度:")
                print(result.stdout)
                return False
        else:
            print("⚠️  迁移检查工具不存在,跳过检查")
            return True

    def preview_removal(self):
        """预览移除内容"""
        print("\n" + "="*60)
        print("阶段2 REST API移除预览")
        print("="*60)

        print(f"\n移除模式: {'预览模式 (dry-run)' if self.dry_run else '执行模式'}")
        print(f"移除时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"\n将要移除的API模块 ({len(self.stage2_apis)}个):")
        for i, api_file in enumerate(self.stage2_apis, 1):
            api_path = self.api_routes_dir / api_file
            if api_path.exists():
                size = api_path.stat().st_size
                print(f"  {i}. {api_file} ({size} bytes)")
            else:
                print(f"  {i}. {api_file} (不存在)")

        print(f"\n归档位置: {self.archive_dir}")

        # 统计信息
        total_size = sum(
            (self.api_routes_dir / api).stat().st_size
            for api in self.stage2_apis
            if (self.api_routes_dir / api).exists()
        )

        print("\n" + "-"*60)
        print("统计信息:")
        print("-"*60)
        print(f"移除文件数: {len(self.stage2_apis)}")
        print(f"释放空间: {total_size} bytes ({total_size/1024:.2f} KB)")
        print(f"REST API路由减少: ~90个")

        # GraphQL替代方案
        print("\n" + "-"*60)
        print("GraphQL替代方案:")
        print("-"*60)
        print("games.py → games, game, searchGames, createGame, updateGame, deleteGame")
        print("events.py → events, event, searchEvents, createEvent, updateEvent, deleteEvent")
        print("parameters.py → parameters, parameter, createParameter, updateParameter, deleteParameter")
        print("categories.py → categories, category, searchCategories, createCategory, updateCategory, deleteCategory")
        print("flows.py → flows, flow, createFlow, updateFlow, deleteFlow")

    def execute_removal(self):
        """执行移除操作"""
        if self.dry_run:
            print("\n⚠️  预览模式,不会实际移除文件")
            print("使用 --execute 参数执行实际移除")
            return

        # 检查前端迁移状态
        if not self.check_frontend_migration():
            print("\n❌ 前端迁移未完成,无法移除REST API")
            print("请先完成前端迁移,然后再执行此脚本")
            return

        print("\n" + "="*60)
        print("执行阶段2 REST API移除")
        print("="*60)

        # 1. 备份文件到归档目录
        print("\n步骤1: 备份文件到归档目录")
        for api_file in self.stage2_apis:
            api_path = self.api_routes_dir / api_file
            if api_path.exists():
                archive_path = self.archive_dir / api_file
                shutil.copy2(api_path, archive_path)
                print(f"  ✅ 备份: {api_file} -> {archive_path}")

        # 2. 从backend/api/__init__.py移除导入
        print("\n步骤2: 从backend/api/__init__.py移除导入")
        init_file = self.project_root / "backend" / "api" / "__init__.py"
        if init_file.exists():
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 移除导入语句
            for api_file in self.stage2_apis:
                module_name = api_file.replace('.py', '')
                # 移除各种可能的导入格式
                import_patterns = [
                    f"from .routes import {module_name}\n",
                    f"    {module_name},\n",
                    f"    {module_name}\n",
                ]
                for pattern in import_patterns:
                    if pattern in content:
                        content = content.replace(pattern, "")
                        print(f"  ✅ 移除导入: {module_name}")

            # 写回文件
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(content)

        # 3. 删除原文件
        print("\n步骤3: 删除原API文件")
        for api_file in self.stage2_apis:
            api_path = self.api_routes_dir / api_file
            if api_path.exists():
                api_path.unlink()
                print(f"  ✅ 删除: {api_file}")

        # 4. 创建移除日志
        print("\n步骤4: 创建移除日志")
        log_file = self.archive_dir / "REMOVAL_LOG.md"
        log_content = f"""# REST API 阶段2移除日志

## 移除时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 移除原因
前端已完成GraphQL迁移,REST API不再使用

## 移除的API模块
"""
        for api_file in self.stage2_apis:
            log_content += f"- {api_file}\n"

        log_content += f"""
## GraphQL替代方案
- games.py → games, game, searchGames, createGame, updateGame, deleteGame
- events.py → events, event, searchEvents, createEvent, updateEvent, deleteEvent
- parameters.py → parameters, parameter, createParameter, updateParameter, deleteParameter
- categories.py → categories, category, searchCategories, createCategory, updateCategory, deleteCategory
- flows.py → flows, flow, createFlow, updateFlow, deleteFlow

## 影响范围
- 前端: 无影响 (已迁移到GraphQL)
- 后端: 减少维护负担
- 性能: 无影响

## 回滚方法
如需回滚,执行以下步骤:
1. 从归档目录恢复API文件
2. 在backend/api/__init__.py中重新导入
3. 重启服务

## 验证
- [x] 前端迁移完成
- [ ] 服务正常启动
- [ ] GraphQL API正常工作
- [ ] 无API调用错误
"""
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
        print(f"  ✅ 创建移除日志: {log_file}")

        print("\n" + "="*60)
        print("✅ 阶段2 REST API移除完成!")
        print("="*60)
        print("\n下一步:")
        print("1. 重启后端服务")
        print("2. 验证GraphQL API功能")
        print("3. 执行回归测试")
        print("4. 更新API文档")

    def run(self):
        """运行移除流程"""
        self.preview_removal()
        self.execute_removal()


def main():
    parser = argparse.ArgumentParser(description='REST API 阶段2移除工具')
    parser.add_argument('--dry-run', action='store_true', help='预览模式,不实际移除')
    parser.add_argument('--execute', action='store_true', help='执行实际移除')

    args = parser.parse_args()

    # 默认为dry-run模式
    dry_run = not args.execute

    remover = RESTAPIStage2Remover(dry_run=dry_run)
    remover.run()


if __name__ == '__main__':
    main()
