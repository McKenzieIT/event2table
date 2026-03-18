#!/usr/bin/env python3
"""
Python调度器 - 定时执行文档整合任务
简化版本，不依赖外部库
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 切换到项目目录
PROJECT_DIR = Path("/Users/mckenzie/Documents/event2table")
os.chdir(PROJECT_DIR)

LOG_FILE = PROJECT_DIR / "logs" / "update-docs-scheduler.log"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}\n"
    print(log_msg, end="")

    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg)

def main():
    """主函数"""
    log("=" * 50)
    log("🚀 开始执行文档整合任务")
    log("=" * 50)

    try:
        # 执行文档整合脚本 (使用skill逻辑)
        script_path = PROJECT_DIR / "scripts" / "scheduled" / "doc_consolidation_by_skill.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=PROJECT_DIR
        )

        log("脚本输出:")
        log(result.stdout)

        if result.stderr:
            log("错误输出:")
            log(result.stderr)

        exit_code = result.returncode

        if exit_code == 0:
            log("✅ 文档整合任务成功完成")
        else:
            log(f"⚠️  文档整合任务完成，退出码: {exit_code}")

        return exit_code

    except Exception as e:
        log(f"❌ 执行失败: {e}")
        import traceback
        log(traceback.format_exc())
        return 1

if __name__ == "__main__":
    main()
