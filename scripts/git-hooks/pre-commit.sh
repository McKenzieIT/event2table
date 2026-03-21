#!/bin/bash
# Pre-commit Hook Template
#
# 安装方法:
#   cp scripts/git-hooks/pre-commit.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit

set -e

echo "🧪 Running pre-commit tests..."

# 激活虚拟环境
if [ -f "backend/venv/bin/activate" ]; then
    source backend/venv/bin/activate
fi

# 运行Backend单元测试
echo "📦 Backend单元测试..."
pytest backend/test/unit/ -q --tb=short || {
    echo "❌ Backend单元测试失败"
    exit 1
}

echo "✅ Pre-commit检查通过"
exit 0
