#!/bin/bash
set -euo pipefail

# 切换到项目目录（必须在最前面）
PROJECT_DIR="/Users/mckenzie/Documents/event2table"
cd "$PROJECT_DIR" || {
    echo "错误：无法切换到项目目录: $PROJECT_DIR" >&2
    exit 1
}

# 日志文件配置（现在使用相对路径是安全的）
LOG_FILE="logs/update-docs-scheduled.log"
ERROR_LOG="logs/update-docs-scheduled-error.log"

# 记录开始时间
echo "=========================================" >> "$LOG_FILE"
echo "开始执行: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "工作目录: $(pwd)" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"

# 验证Python虚拟环境存在
if [ ! -f "backend/venv/bin/activate" ]; then
    echo "错误: Python虚拟环境不存在" >> "$ERROR_LOG"
    echo "预期的位置: backend/venv/bin/activate" >> "$ERROR_LOG"
    exit 1
fi

# 激活Python虚拟环境
echo "激活虚拟环境..." >> "$LOG_FILE"
source backend/venv/bin/activate

# 设置PATH确保Claude CLI可用
export PATH="/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:$PATH"

# 验证Claude CLI可用
if ! command -v claude &> /dev/null; then
    echo "错误: Claude CLI未找到" >> "$ERROR_LOG"
    echo "当前PATH: $PATH" >> "$ERROR_LOG"
    exit 1
fi

# 执行文档整合任务
echo "执行文档整合任务..." >> "$LOG_FILE"
echo "任务: 通过Claude Code CLI调用/update-docs skill" >> "$LOG_FILE"
echo "完整任务: 整合docs/目录，提取经验，归档旧文档，更新索引" >> "$LOG_FILE"
./scripts/scheduled/run-claude-direct.sh \
  >> "$LOG_FILE" 2>> "$ERROR_LOG"

# 检查执行结果
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 任务成功完成" >> "$LOG_FILE"
else
    echo "❌ 任务执行失败，退出码: $EXIT_CODE" >> "$ERROR_LOG"
fi

# 记录结束时间
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $EXIT_CODE
