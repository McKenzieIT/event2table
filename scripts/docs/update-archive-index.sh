#!/bin/bash
# update-archive-index.sh - 归档索引自动更新脚本
#
# 用途：
#   1. 每月初自动运行，更新归档主题索引
#   2. 手动运行：新增归档文档后更新索引
#
# 使用方法：
#   bash scripts/docs/update-archive-index.sh
#
# 作者：Event2Table Development Team
# 日期：2026-03-13

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  归档索引自动更新工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查虚拟环境
if [ -f "backend/venv/bin/activate" ]; then
    echo -e "${GREEN}✓${NC} 虚拟环境已找到"
else
    echo -e "${YELLOW}⚠${NC} 虚拟环境未激活，某些Python脚本可能无法运行"
fi

echo ""
echo -e "${BLUE}[步骤 1/3]${NC} 扫描归档文档..."
echo "----------------------------------------"

# 统计归档文档数量
ARCHIVE_COUNT=$(find docs/archive/ -name "*.md" -type f | wc -l | tr -d ' ')
echo -e "归档文档总数: ${GREEN}${ARCHIVE_COUNT}${NC} 个"

# 按月份统计
echo ""
echo "按月份分布:"
for year_month in $(find docs/archive/ -type d -name "20*" -o -name "202*" | sort -u); do
    if [ -d "$year_month" ]; then
        count=$(find "$year_month" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [ "$count" -gt 0 ]; then
            echo -e "  $(basename $year_month): ${GREEN}${count}${NC} 个"
        fi
    fi
done

echo ""
echo -e "${BLUE}[步骤 2/3]${NC} 生成主题索引..."
echo "----------------------------------------"

# 运行Python脚本生成索引
if [ -f "scripts/tools/generate_topic_index.py" ]; then
    python3 scripts/tools/generate_topic_index.py

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} 主题索引生成成功"
    else
        echo -e "${RED}✗${NC} 主题索引生成失败"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} 未找到索引生成脚本: scripts/tools/generate_topic_index.py"
    exit 1
fi

echo ""
echo -e "${BLUE}[步骤 3/3]${NC} 验证索引质量..."
echo "----------------------------------------"

# 验证索引文件是否存在
if [ ! -f "docs/archive/TOPIC_INDEX.md" ]; then
    echo -e "${RED}✗${NC} 主题索引文件不存在: docs/archive/TOPIC_INDEX.md"
    exit 1
fi

# 检查索引中的文档数量
INDEXED_COUNT=$(grep -c "^- \[" docs/archive/TOPIC_INDEX.md 2>/dev/null || echo "0")
echo -e "索引中的文档数量: ${GREEN}${INDEXED_COUNT}${NC} 个"

# 检查是否有死链接（简单的链接格式检查）
echo ""
echo "检查链接格式..."
LINK_COUNT=$(grep -c "\](.*\.md)" docs/archive/TOPIC_INDEX.md 2>/dev/null || echo "0")
echo -e "索引中的链接数量: ${GREEN}${LINK_COUNT}${NC} 个"

# 检查README是否已更新
if grep -q "TOPIC_INDEX" docs/archive/README.md; then
    echo -e "${GREEN}✓${NC} 主索引README已更新"
else
    echo -e "${YELLOW}⚠${NC} 主索引README可能需要更新（未找到TOPIC_INDEX链接）"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  归档索引更新完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📋 查看主题索引:"
echo "   docs/archive/TOPIC_INDEX.md"
echo ""
echo "📋 查看主索引:"
echo "   docs/archive/README.md"
echo ""
echo "🔍 测试查找:"
echo "   打开 docs/archive/TOPIC_INDEX.md"
echo "   按主题查找历史文档"
echo ""
