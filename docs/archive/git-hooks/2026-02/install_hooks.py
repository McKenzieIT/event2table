#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Install Git Hooks

安装项目的 Git hooks 到 .git/hooks/ 目录

使用方法：
    python scripts/git-hooks/install_hooks.py
"""

import os
import shutil
import sys
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'
BOLD = '\033[1m'

def main():
    """安装 Git hooks"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    hooks_source_dir = script_dir
    hooks_target_dir = project_root / '.git' / 'hooks'

    print(f"{YELLOW}📦 Installing Git hooks...{RESET}\n")

    # 检查 .git 目录是否存在
    if not hooks_target_dir.exists():
        print(f"{YELLOW}⚠️  Warning: .git/hooks/ directory not found.{RESET}")
        print(f"{YELLOW}   If this is a fresh clone, run 'git init' first.{RESET}\n")
        # 创建目录
        hooks_target_dir.mkdir(parents=True, exist_ok=True)
        print(f"{GREEN}✅ Created .git/hooks/ directory{RESET}\n")

    # 安装 pre-commit hook
    pre_commit_source = hooks_source_dir / 'pre-commit'
    pre_commit_target = hooks_target_dir / 'pre-commit'

    if pre_commit_source.exists():
        # 复制文件
        shutil.copy2(pre_commit_source, pre_commit_target)

        # 赋予执行权限
        os.chmod(pre_commit_target, 0o755)

        print(f"{GREEN}✅ Installed pre-commit hook{RESET}")
        print(f"   {GREEN}→ {pre_commit_target}{RESET}\n")

        # 验证安装
        print(f"{YELLOW}🔍 Verifying installation...{RESET}")
        result = os.system(f"cd {project_root} && .git/hooks/pre-commit")
        if result == 0:
            print(f"{GREEN}✅ Hook verification passed!{RESET}\n")
        else:
            print(f"{YELLOW}⚠️  Hook verification had non-zero exit code (may be expected){RESET}\n")

        print(f"{GREEN}✅ Git hooks installed successfully!{RESET}\n")
        print(f"{YELLOW}📋 What this does:{RESET}")
        print(f"   Pre-commit hook will check for misplaced database files")
        print(f"   before each commit, blocking commits if found outside data/ directory.\n")

        return 0
    else:
        print(f"{YELLOW}⚠️  Warning: pre-commit hook not found:{RESET}")
        print(f"   {pre_commit_source}\n")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
