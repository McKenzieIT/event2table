#!/bin/bash
# 使用tmux在后台会话中运行Claude skill

SESSION_NAME="claude-doc-update"
PROJECT_DIR="/Users/mckenzie/Documents/event2table"
LOG_FILE="$PROJECT_DIR/logs/update-docs-scheduled.log"
ERROR_LOG="$PROJECT_DIR/logs/update-docs-scheduled-error.log"

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

# 检查tmux是否安装
if ! command -v tmux &> /dev/null; then
    echo "错误: tmux未安装" >> "$ERROR_LOG"
    exit 1
fi

# 清理可能存在的旧会话
tmux has-session -t $SESSION_NAME 2>/dev/null
if [ $? -eq 0 ]; then
    echo "清理旧会话..." >> "$LOG_FILE"
    tmux kill-session -t $SESSION_NAME 2>/dev/null
    sleep 1
fi

# 创建新的tmux会话并执行命令
echo "创建tmux会话..." >> "$LOG_FILE"
tmux new-session -d -s $SESSION_NAME

# 在tmux会话中执行命令
tmux send-keys -t $SESSION_NAME "cd $PROJECT_DIR" C-m
sleep 1
tmux send-keys -t $SESSION_NAME "export PATH=/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:\$PATH" C-m
sleep 1

# 记录执行的命令
echo "执行命令: $FULL_PROMPT" >> "$LOG_FILE"

# 发送claude命令
tmux send-keys -t $SESSION_NAME "claude" C-m
sleep 3

# 等待Claude启动
echo "等待Claude启动..." >> "$LOG_FILE"
sleep 5

# 发送skill命令
tmux send-keys -t $SESSION_NAME "$FULL_PROMPT" C-m

# 等待命令执行（最多10分钟）
echo "等待Claude处理文档（最多10分钟）..." >> "$LOG_FILE"
for i in {1..60}; do
    # 检查会话是否还存在
    if ! tmux has-session -t $SESSION_NAME 2>/dev/null; then
        echo "会话已结束" >> "$LOG_FILE"
        break
    fi

    # 每分钟记录一次进度
    if [ $((i % 10)) -eq 0 ]; then
        echo "进度: $i/60 次（已运行 $((i/10)) 分钟）" >> "$LOG_FILE"
    fi

    sleep 10
done

# 发送exit命令（如果会话还在）
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "发送退出命令..." >> "$LOG_FILE"
    tmux send-keys -t $SESSION_NAME "exit" C-m
    sleep 2
fi

# 结束会话
tmux kill-session -t $SESSION_NAME 2>/dev/null

# 记录完成
echo "=========================================" >> "$LOG_FILE"
echo "任务完成时间: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "✅ 文档整合任务已调度完成"
exit 0
