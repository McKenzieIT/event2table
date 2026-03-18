#!/bin/bash
# 诊断脚本 - 测试定时任务的所有组件

PROJECT_DIR="/Users/mckenzie/Documents/event2table"
cd "$PROJECT_DIR" || exit 1

echo "========================================="
echo "开始诊断测试"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="

# 1. 测试项目目录
echo ""
echo "1. 测试项目目录"
echo "当前目录: $(pwd)"
echo "目录存在: $([ -d "$PROJECT_DIR" ] && echo "✅" || echo "❌")"

# 2. 测试Python虚拟环境
echo ""
echo "2. 测试Python虚拟环境"
VENV_PATH="backend/venv/bin/activate"
echo "虚拟环境路径: $VENV_PATH"
echo "虚拟环境存在: $([ -f "$VENV_PATH" ] && echo "✅" || echo "❌")"
if [ -f "$VENV_PATH" ]; then
    echo "尝试激活虚拟环境..."
    source "$VENV_PATH" && echo "✅ 虚拟环境激活成功" || echo "❌ 虚拟环境激活失败"
    echo "Python路径: $(which python3)"
fi

# 3. 测试Node.js和npm
echo ""
echo "3. 测试Node.js环境"
export PATH="/Users/mckenzie/.nvm/versions/node/v20.20.0/bin:$PATH"
echo "PATH中包含Node.js: $([ -f "/Users/mckenzie/.nvm/versions/node/v20.20.0/bin/node" ] && echo "✅" || echo "❌")"
which node && echo "✅ Node.js: $(node --version)" || echo "❌ Node.js未找到"
which npm && echo "✅ npm: $(npm --version)" || echo "❌ npm未找到"

# 4. 测试Claude CLI
echo ""
echo "4. 测试Claude CLI"
which claude && echo "✅ Claude CLI路径: $(which claude)" || echo "❌ Claude CLI未找到"
claude --version && echo "✅ Claude CLI版本: $(claude --version)" || echo "❌ 无法获取Claude CLI版本"

# 5. 测试日志文件
echo ""
echo "5. 测试日志文件"
LOG_DIR="logs"
echo "日志目录: $LOG_DIR"
echo "日志目录存在: $([ -d "$LOG_DIR" ] && echo "✅" || echo "❌")"
if [ ! -d "$LOG_DIR" ]; then
    echo "创建日志目录..."
    mkdir -p "$LOG_DIR" && echo "✅ 日志目录创建成功" || echo "❌ 无法创建日志目录"
fi

# 6. 测试简单Claude命令（快速测试）
echo ""
echo "6. 测试Claude CLI快速响应"
echo "发送简单测试命令..."
timeout 5 claude --print "echo hello" 2>&1 | head -c 100 || echo "命令超时或失败（预期行为）"

# 7. 测试脚本权限
echo ""
echo "7. 测试脚本权限"
echo "update-docs-scheduled.sh: $(ls -l scripts/scheduled/update-docs-scheduled.sh | awk '{print $1}')"
echo "run-claude-direct.sh: $(ls -l scripts/scheduled/run-claude-direct.sh | awk '{print $1}')"

# 8. 测试Cron服务
echo ""
echo "8. 测试Cron服务"
ps aux | grep -i cron | grep -v grep | head -1 > /dev/null && echo "✅ Cron服务运行中" || echo "❌ Cron服务未运行"

# 9. 显示当前crontab配置
echo ""
echo "9. 当前Crontab配置"
crontab -l | grep -v "^#" | grep -v "^$"

echo ""
echo "========================================="
echo "诊断完成"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
