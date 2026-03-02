#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST API 阶段1移除脚本

移除无前端使用的REST API模块:
- dashboard.py
- templates.py
- nodes.py

使用方法:
    python scripts/remove_rest_api_stage1.py --dry-run  # 预览移除内容
    python scripts/remove_rest_api_stage1.py --execute  # 执行移除
"""

import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path


class RESTAPIRemover:
    """REST API移除工具"""

    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.api_routes_dir = self.project_root / "backend" / "api" / "routes"
        self.archive_dir = self.project_root / "archive" / "backend" / "api" / "removed_stage1"

        # 阶段1要移除的API模块
        self.stage1_apis = [
            "dashboard.py",
            "templates.py",
            "nodes.py"
        ]

        # 创建归档目录
        if not self.dry_run:
            self.archive_dir.mkdir(parents=True, exist_ok=True)

    def analyze_dependencies(self):
        """分析API依赖关系"""
        print("\n" + "="*60)
        print("依赖关系分析")
        print("="*60)

        for api_file in self.stage1_apis:
            api_path = self.api_routes_dir / api_file
            if not api_path.exists():
                print(f"⚠️  {api_file} 不存在,跳过")
                continue

            # 检查是否有其他文件导入此API
            print(f"\n检查 {api_file} 的依赖关系:")

            # 检查backend/api/__init__.py
            init_file = self.project_root / "backend" / "api" / "__init__.py"
            if init_file.exists():
                with open(init_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    module_name = api_file.replace('.py', '')
                    if module_name in content:
                        print(f"  ✅ 在 backend/api/__init__.py 中注册")
                    else:
                        print(f"  ⚠️  未在 backend/api/__init__.py 中注册")

            # 检查前端使用
            frontend_dir = self.project_root / "frontend" / "src"
            if frontend_dir.exists():
                found_usage = False
                for root, dirs, files in os.walk(frontend_dir):
                    for file in files:
                        if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                            filepath = os.path.join(root, file)
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                # 检查API路径
                                api_paths = self._extract_api_paths(api_file)
                                for path in api_paths:
                                    if path in content:
                                        print(f"  ⚠️  前端使用: {filepath} -> {path}")
                                        found_usage = True

                if not found_usage:
                    print(f"  ✅ 无前端使用")

    def _extract_api_paths(self, api_file):
        """从API文件提取API路径"""
        api_paths = []
        api_path = self.api_routes_dir / api_file

        if api_path.exists():
            with open(api_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单提取@api_bp.route装饰器中的路径
                import re
                matches = re.findall(r'@api_bp\.route\(["\']([^"\']+)["\']', content)
                api_paths.extend(matches)

        return api_paths

    def preview_removal(self):
        """预览移除内容"""
        print("\n" + "="*60)
        print("阶段1 REST API移除预览")
        print("="*60)

        print(f"\n移除模式: {'预览模式 (dry-run)' if self.dry_run else '执行模式'}")
        print(f"移除时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"\n将要移除的API模块 ({len(self.stage1_apis)}个):")
        for i, api_file in enumerate(self.stage1_apis, 1):
            api_path = self.api_routes_dir / api_file
            if api_path.exists():
                size = api_path.stat().st_size
                print(f"  {i}. {api_file} ({size} bytes)")
            else:
                print(f"  {i}. {api_file} (不存在)")

        print(f"\n归档位置: {self.archive_dir}")

        # 分析依赖
        self.analyze_dependencies()

        # 统计信息
        total_size = sum(
            (self.api_routes_dir / api).stat().st_size
            for api in self.stage1_apis
            if (self.api_routes_dir / api).exists()
        )

        print("\n" + "-"*60)
        print("统计信息:")
        print("-"*60)
        print(f"移除文件数: {len(self.stage1_apis)}")
        print(f"释放空间: {total_size} bytes ({total_size/1024:.2f} KB)")
        print(f"REST API路由减少: ~30个")

    def execute_removal(self):
        """执行移除操作"""
        if self.dry_run:
            print("\n⚠️  预览模式,不会实际移除文件")
            print("使用 --execute 参数执行实际移除")
            return

        print("\n" + "="*60)
        print("执行阶段1 REST API移除")
        print("="*60)

        # 1. 备份文件到归档目录
        print("\n步骤1: 备份文件到归档目录")
        for api_file in self.stage1_apis:
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
            for api_file in self.stage1_apis:
                module_name = api_file.replace('.py', '')
                import_line = f"from .routes import {module_name}\n"
                if import_line in content:
                    content = content.replace(import_line, "")
                    print(f"  ✅ 移除导入: {module_name}")

            # 写回文件
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(content)

        # 3. 删除原文件
        print("\n步骤3: 删除原API文件")
        for api_file in self.stage1_apis:
            api_path = self.api_routes_dir / api_file
            if api_path.exists():
                api_path.unlink()
                print(f"  ✅ 删除: {api_file}")

        # 4. 创建移除日志
        print("\n步骤4: 创建移除日志")
        log_file = self.archive_dir / "REMOVAL_LOG.md"
        log_content = f"""# REST API 阶段1移除日志

## 移除时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 移除原因
无前端使用,已完全迁移到GraphQL API

## 移除的API模块
"""
        for api_file in self.stage1_apis:
            log_content += f"- {api_file}\n"

        log_content += f"""
## GraphQL替代方案
- dashboard.py → dashboardStats, gameStats, allGameStats queries
- templates.py → template, templates, searchTemplates queries
- nodes.py → node, nodes queries

## 影响范围
- 前端: 无影响 (无前端使用)
- 后端: 减少维护负担
- 性能: 无影响

## 回滚方法
如需回滚,执行以下步骤:
1. 从归档目录恢复API文件
2. 在backend/api/__init__.py中重新导入
3. 重启服务

## 验证
- [ ] 服务正常启动
- [ ] GraphQL API正常工作
- [ ] 无API调用错误
"""
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
        print(f"  ✅ 创建移除日志: {log_file}")

        print("\n" + "="*60)
        print("✅ 阶段1 REST API移除完成!")
        print("="*60)

    def run(self):
        """运行移除流程"""
        self.preview_removal()
        self.execute_removal()


def main():
    parser = argparse.ArgumentParser(description='REST API 阶段1移除工具')
    parser.add_argument('--dry-run', action='store_true', help='预览模式,不实际移除')
    parser.add_argument('--execute', action='store_true', help='执行实际移除')

    args = parser.parse_args()

    # 默认为dry-run模式
    dry_run = not args.execute

    remover = RESTAPIRemover(dry_run=dry_run)
    remover.run()


if __name__ == '__main__':
    main()
