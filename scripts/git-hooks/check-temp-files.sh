#!/bin/bash
# Pre-commit检查：防止临时文件提交
# 版本: 1.0
# 创建日期: 2026-03-20

set -e

echo "🔍 检查临时文件..."

ERRORS_FOUND=0

# 检查根目录的截图文件
SCREENSHOTS=$(git diff --cached --name-only | grep -E '\.(png|jpg|jpeg|gif)$' | grep -v '^output/screenshots/' || true)
if [ -n "$SCREENSHOTS" ]; then
    echo "❌ 错误：检测到根目录的截图文件"
    echo "请将截图移动到 output/screenshots/ 目录："
    echo "$SCREENSHOTS"
    echo ""
    echo "💡 快速修复："
    echo "  mkdir -p output/screenshots/manual"
    echo "  mv $SCREENSHOTS output/screenshots/manual/"
    ERRORS_FOUND=1
fi

# 检查根目录的临时报告
REPORTS=$(git diff --cached --name-only | grep -E 'REPORT\.md$|IMPLEMENTATION-REPORT\.md$|PROGRESS.*\.md$|SUMMARY\.md$' | grep -v '^output/reports/' || true)
if [ -n "$REPORTS" ]; then
    echo "❌ 错误：检测到根目录的临时报告文件"
    echo "请将报告移动到 output/reports/ 目录："
    echo "$REPORTS"
    echo ""
    echo "💡 快速修复："
    echo "  mkdir -p output/reports/analysis"
    echo "  mv $REPORTS output/reports/analysis/"
    ERRORS_FOUND=1
fi

# 检查日志文件
LOGS=$(git diff --cached --name-only | grep -E '::log_file$|\.log$' || true)
if [ -n "$LOGS" ]; then
    echo "❌ 错误：检测到日志文件"
    echo "日志文件不应提交到git："
    echo "$LOGS"
    echo ""
    echo "💡 快速修复："
    echo "  git rm --cached $LOGS"
    echo "  echo '*.log' >> .gitignore"
    ERRORS_FOUND=1
fi

# 检查临时文件
TEMP_FILES=$(git diff --cached --name-only | grep -E '\.tmp$|\.temp$|\.cache$|\.DS_Store$|::log_file$' || true)
if [ -n "$TEMP_FILES" ]; then
    echo "❌ 错误：检测到临时文件"
    echo "临时文件不应提交到git："
    echo "$TEMP_FILES"
    echo ""
    echo "💡 快速修复："
    echo "  git rm --cached $TEMP_FILES"
    ERRORS_FOUND=1
fi

if [ $ERRORS_FOUND -eq 1 ]; then
    echo ""
    echo "❌ Pre-commit检查失败，请修复后重新提交"
    echo "💡 提示：使用 'git commit --no-verify' 跳过检查（不推荐）"
    exit 1
fi

echo "✅ 临时文件检查通过"
exit 0
