#!/bin/bash
# 使用Claude CLI --print模式直接执行文档整合任务

PROJECT_DIR="/Users/mckenzie/Documents/event2table"
LOG_FILE="$PROJECT_DIR/logs/update-docs-scheduled.log"
ERROR_LOG="$PROJECT_DIR/logs/update-docs-scheduled-error.log"

# 记录开始
echo "=========================================" >> "$LOG_FILE"
echo "启动Claude Code文档整合任务" >> "$LOG_FILE"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "模式: Claude CLI --print 非交互式执行" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"

# 切换到项目目录
cd "$PROJECT_DIR" || exit 1

# 设置环境
export PATH="/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:$PATH"

# 使用Claude CLI --print模式执行任务
echo "执行Claude任务..." >> "$LOG_FILE"

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

# 使用timeout限制执行时间（最多10分钟）
echo "任务描述: $TASK_PROMPT" >> "$LOG_FILE"
timeout 600 claude --print "$TASK_PROMPT" >> "$LOG_FILE" 2>> "$ERROR_LOG"

EXIT_CODE=$?

# 记录完成
echo "=========================================" >> "$LOG_FILE"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Claude任务执行成功" >> "$LOG_FILE"
elif [ $EXIT_CODE -eq 124 ]; then
    echo "⚠️  Claude任务超时（10分钟）" >> "$ERROR_LOG"
else
    echo "❌ Claude任务失败（退出码: $EXIT_CODE）" >> "$ERROR_LOG"
fi
echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 如果timeout超时，也视为成功（可能任务还在执行）
if [ $EXIT_CODE -eq 124 ]; then
    exit 0
fi

exit $EXIT_CODE
