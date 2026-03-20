#!/bin/bash
# 临时文件清理脚本
# 版本: 1.0
# 创建日期: 2026-03-20

set -e

echo "🧹 清理临时文件..."
echo ""

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p output/screenshots/ui
mkdir -p output/screenshots/e2e
mkdir -p output/screenshots/manual
mkdir -p output/reports/implementation
mkdir -p output/reports/testing
mkdir -p output/reports/analysis

# 统计移动前的文件数
SCREENSHOT_COUNT=$(find . -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" \) 2>/dev/null | wc -l | tr -d ' ')
REPORT_COUNT=$(find . -maxdepth 1 -type f \( -name "*REPORT*.md" -o -name "*PROGRESS*.md" -o -name "*SUMMARY.md" \) 2>/dev/null | wc -l | tr -d ' ')
LOG_COUNT=$(find . -maxdepth 1 -type f -name "::log_file" 2>/dev/null | wc -l | tr -d ' ')

# 移动根目录的截图到output/screenshots/
if [ "$SCREENSHOT_COUNT" -gt 0 ]; then
    echo "📸 移动 $SCREENSHOT_COUNT 个截图文件..."
    find . -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" \) -exec mv {} output/screenshots/manual/ \; 2>/dev/null || true
else
    echo "✓ 没有需要移动的截图文件"
fi

# 移动根目录的临时报告到output/reports/
if [ "$REPORT_COUNT" -gt 0 ]; then
    echo "📄 移动 $REPORT_COUNT 个临时报告文件..."
    find . -maxdepth 1 -type f -name "*REPORT*.md" -exec mv {} output/reports/analysis/ \; 2>/dev/null || true
    find . -maxdepth 1 -type f -name "*PROGRESS*.md" -exec mv {} output/reports/analysis/ \; 2>/dev/null || true
    find . -maxdepth 1 -type f -name "*SUMMARY.md" -exec mv {} output/reports/analysis/ \; 2>/dev/null || true
else
    echo "✓ 没有需要移动的报告文件"
fi

# 删除日志文件
if [ "$LOG_COUNT" -gt 0 ]; then
    echo "🗑️  删除 $LOG_COUNT 个日志文件..."
    find . -maxdepth 1 -type f -name "::log_file" -delete 2>/dev/null || true
    find . -maxdepth 1 -type f -name "*.log" -delete 2>/dev/null || true
else
    echo "✓ 没有需要删除的日志文件"
fi

echo ""
echo "✅ 清理完成"
echo ""
echo "📊 统计："
echo "  - output/screenshots/: $(find output/screenshots/ -type f 2>/dev/null | wc -l | tr -d ' ') 个文件"
echo "  - output/reports/: $(find output/reports/ -type f 2>/dev/null | wc -l | tr -d ' ') 个文件"
echo ""
echo "💡 提示：运行 'git status' 查看变更"
