#!/bin/bash
# Archive Index File Monitor
#
# 后台监控docs/archive/目录变化，自动更新索引
# 使用方法：
#   bash scripts/docs/monitor-archive-index.sh &
#
# 停止监控：
#   pkill -f monitor-archive-index.sh

set -e

# 颜色定义
GREEN='\033[92m'
YELLOW='\033[93m'
BLUE='\033[96m'
RESET='\033[0m'

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}📚 Archive Index Monitor${RESET}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${YELLOW}监控目录: docs/archive/${RESET}"
echo -e "${YELLOW}使用方法:${RESET}"
echo -e "  后台运行: bash scripts/docs/monitor-archive-index.sh &"
echo -e "  停止监控: pkill -f monitor-archive-index.sh"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"

# 检查是否安装了fswatch（用于文件监控）
if ! command -v fswatch &> /dev/null; then
    echo -e "${YELLOW}⚠️  fswatch未安装，安装方法:${RESET}"
    echo -e "  brew install fswatch"
    echo -e "${YELLOW}将使用polling模式（每5秒检查一次）${RESET}\n"
    USE_FSWATCH=false
else
    USE_FSWATCH=true
fi

# 索引更新函数
update_index() {
    local reason="$1"

    echo -e "\n${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] 检测到归档文档变更${RESET}"
    echo -e "${YELLOW}原因: $reason${RESET}"

    # 运行索引生成脚本
    python3 scripts/tools/generate_topic_index.py

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 索引已更新${RESET}"
    else
        echo -e "${YELLOW}⚠️  索引更新失败${RESET}"
    fi
}

# 使用fswatch监控（推荐）
if [ "$USE_FSWATCH" = true ]; then
    echo -e "${GREEN}✅ 使用fswatch监控（实时响应）${RESET}"
    echo -e "${BLUE}监控中... (Ctrl+C停止)${RESET}\n"

    # 监控docs/archive/目录下的.md文件（排除TOPIC_INDEX.md）
    fswatch -o -e ".*" -r \
        --exclude="TOPIC_INDEX.md" \
        docs/archive/ \
        | while read -r f; do
            # 防抖：等待1秒后再更新（避免频繁更新）
            sleep 1
            update_index "文件系统变化检测"
        done

# 使用polling模式（备选）
else
    echo -e "${GREEN}✅ 使用polling模式（每5秒检查一次）${RESET}"
    echo -e "${BLUE}监控中... (Ctrl+C停止)${RESET}\n"

    # 记录上次检查的文件状态
    LAST_CHECKSUM=""

    while true; do
        # 计算当前归档文档的校验和（排除TOPIC_INDEX.md）
        CURRENT_CHECKSUM=$(find docs/archive/ -name "*.md" ! -name "TOPIC_INDEX.md" -type f -exec md5 {} \; | sort | md5)

        # 如果校验和变化，更新索引
        if [ "$CURRENT_CHECKSUM" != "$LAST_CHECKSUM" ]; then
            if [ -n "$LAST_CHECKSUM" ]; then
                update_index "文件变化检测"
            fi
            LAST_CHECKSUM="$CURRENT_CHECKSUM"
        fi

        # 等待5秒
        sleep 5
    done
fi
