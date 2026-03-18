#!/usr/bin/env python3
"""
Python调度器 - 定时执行文档整合任务
绕过macOS TCC对bash脚本的限制
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import schedule
import time

# 项目路径
PROJECT_DIR = Path("/Users/mckenzie/Documents/event2table")
LOG_FILE = PROJECT_DIR / "logs" / "update-docs-scheduler.log"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}\n"
    print(log_msg, end="")

    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg)

def run_doc_consolidation():
    """执行文档整合任务"""
    log("=" * 50)
    log("🚀 开始执行文档整合任务")
    log("=" * 50)

    try:
        # 直接导入并执行Python脚本
        sys.path.insert(0, str(PROJECT_DIR))
        from scripts.scheduled.run_claude_api_exec import main as run_consolidation

        exit_code = run_consolidation()

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

def main():
    """主函数"""
    log("Python调度器启动")
    log(f"工作目录: {os.getcwd()}")

    # 设置环境变量
    os.environ["PATH"] = "/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:/usr/local/bin:/usr/bin:/bin"
    os.environ["HOME"] = "/Users/mckenzie"

    # 立即执行一次（用于测试）
    log("执行一次性任务...")
    run_doc_consolidation()

    # 如果是调度模式
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        log("调度模式：每天06:30执行")
        schedule.every().day.at("06:30").do(run_doc_consolidation)

        log("调度器已启动，等待下次执行...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    main()
