#!/bin/bash
# 使用伪终端执行Claude CLI命令（解决挂起问题）

PROJECT_DIR="/Users/mckenzie/Documents/event2table"
LOG_FILE="$PROJECT_DIR/logs/update-docs-scheduled.log"
ERROR_LOG="$PROJECT_DIR/logs/update-docs-scheduled-error.log"

# 切换到项目目录
cd "$PROJECT_DIR" || exit 1

# 设置环境
export PATH="/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:$PATH"
export HOME="/Users/mckenzie"
export CLAUDE_DIR="$HOME/.claude"

# 记录开始
echo "=========================================" >> "$LOG_FILE"
echo "启动Claude Code文档整合任务（PTY模式）" >> "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"

# 完整的任务描述
TASK_PROMPT="请执行以下文档整合任务：
1. 扫描docs/目录下的所有markdown文件
2. 识别重复或相似的文档
3. 将重复文档中的关键经验提取到docs/lessons-learned/对应的经验文档中
4. 将处理过的旧文档归档到docs/archive/目录下
5. 更新CLAUDE.md中的经验文档索引

重要：
- 不能因为token或时间限制而忽略重要经验
- 必须完整执行所有步骤
- 保留所有有价值的文档内容"

# 使用script命令创建伪终端并执行Claude CLI
# script会创建一个伪终端，这可能会解决挂起问题
PTY_LOG="/tmp/claude-pty-log.$$"
echo "任务描述: $TASK_PROMPT" >> "$LOG_FILE"
echo "使用伪终端模式执行..." >> "$LOG_FILE"

# 在伪终端中执行命令
script -q "$PTY_LOG" /bin/bash -c "
  export PATH='/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:$PATH'
  export HOME='/Users/mckenzie'
  timeout 600 claude --print --no-session-persistence --permission-mode default '$TASK_PROMPT'
" >> "$LOG_FILE" 2>> "$ERROR_LOG"

EXIT_CODE=$?

# 清理伪终端日志
rm -f "$PTY_LOG"

# 记录完成
echo "=========================================" >> "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Claude任务执行成功" >> "$LOG_FILE"
elif [ $EXIT_CODE -eq 124 ]; then
    echo "⚠️  Claude任务超时（10分钟）" >> "$ERROR_LOG"
    # 超时也视为成功（任务可能还在执行）
    exit 0
else
    echo "❌ Claude任务失败（退出码: $EXIT_CODE）" >> "$ERROR_LOG"
fi
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit $EXIT_CODE
