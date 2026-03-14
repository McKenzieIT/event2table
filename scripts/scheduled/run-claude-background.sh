#!/bin/bash
# 使用后台进程运行Claude skill（无需expect/tmux）

PROJECT_DIR="/Users/mckenzie/Documents/event2table"
LOG_FILE="$PROJECT_DIR/logs/update-docs-scheduled.log"
ERROR_LOG="$PROJECT_DIR/logs/update-docs-scheduled-error.log"
PROMPT_FILE="$PROJECT_DIR/scripts/scheduled/claude-prompt.txt"

# 完整的prompt
FULL_PROMPT="/update-docs 更新文档，并整合docs/目录下的文档，将重复的文档提取经验到新或已有经验文档中，过程中不能因为token和时间去忽略重要的经验，完成后将旧的文档进行归档，并在开发文档中更新经验和索引"

# 记录开始
echo "=========================================" >> "$LOG_FILE"
echo "启动Claude Code文档整合任务" >> "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"

# 切换到项目目录
cd "$PROJECT_DIR" || exit 1

# 设置环境
export PATH="/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:$PATH"

# 将prompt写入文件
echo "$FULL_PROMPT" > "$PROMPT_FILE"

# 使用nohup在后台运行Claude
echo "启动Claude CLI..." >> "$LOG_FILE"

# 使用here-document传递输入给Claude
(
    cat "$PROMPT_FILE"
    sleep 2
    echo "exit"
) | timeout 600 claude >> "$LOG_FILE" 2>> "$ERROR_LOG"

EXIT_CODE=$?

# 清理
rm -f "$PROMPT_FILE"

# 记录完成
echo "=========================================" >> "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 任务成功完成" >> "$LOG_FILE"
else
    echo "⚠️  任务完成（退出码: $EXIT_CODE）" >> "$LOG_FILE"
fi
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $EXIT_CODE
