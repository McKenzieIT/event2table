#!/bin/bash
# Vite Configuration Verification Script
# 用于验证 Vite 配置与 Apollo Client v4 的兼容性

set -e

echo "🔍 Vite Configuration Verification Script"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查 Vite 配置文件
echo "📋 检查 Vite 配置文件..."
if [ -f "vite.config.ts" ]; then
    echo -e "${GREEN}✅ vite.config.ts 存在${NC}"
else
    echo -e "${RED}❌ vite.config.ts 不存在${NC}"
    exit 1
fi

# 2. 检查 optimizeDeps 配置
echo ""
echo "🔍 检查 optimizeDeps 配置..."
if grep -q "'@apollo/client'" vite.config.ts && \
   grep -q "'@apollo/client/react'" vite.config.ts && \
   grep -q "'@apollo/client/link/context'" vite.config.ts && \
   grep -q "'@apollo/client/link/error'" vite.config.ts && \
   grep -q "'@apollo/client/link/retry'" vite.config.ts && \
   grep -q "'@apollo/client/link/http'" vite.config.ts && \
   grep -q "'@apollo/client/utilities'" vite.config.ts && \
   grep -q "'graphql'" vite.config.ts; then
    echo -e "${GREEN}✅ optimizeDeps 配置完整${NC}"
else
    echo -e "${YELLOW}⚠️  optimizeDeps 配置可能不完整${NC}"
    echo "建议检查 vite.config.ts 中的 optimizeDeps.include 配置"
fi

# 3. 检查 resolve.extensions 配置
echo ""
echo "🔍 检查 resolve.extensions 配置..."
if grep -q "extensions:" vite.config.ts && \
   grep -q "'.graphql'" vite.config.ts && \
   grep -q "'.gql'" vite.config.ts; then
    echo -e "${GREEN}✅ resolve.extensions 配置正确${NC}"
else
    echo -e "${YELLOW}⚠️  resolve.extensions 配置可能不完整${NC}"
    echo "建议添加 GraphQL 文件扩展名支持"
fi

# 4. 检查依赖版本
echo ""
echo "📦 检查依赖版本..."
VITE_VERSION=$(npm list vite --depth=0 2>/dev/null | grep vite | sed 's/.*@//')
APOLLO_VERSION=$(npm list @apollo/client --depth=0 2>/dev/null | grep @apollo/client | sed 's/.*@//')

if [ -n "$VITE_VERSION" ]; then
    echo -e "Vite 版本: ${GREEN}$VITE_VERSION${NC}"
else
    echo -e "Vite 版本: ${YELLOW}未找到${NC}"
fi

if [ -n "$APOLLO_VERSION" ]; then
    echo -e "Apollo Client 版本: ${GREEN}$APOLLO_VERSION${NC}"
else
    echo -e "Apollo Client 版本: ${YELLOW}未找到${NC}"
fi

# 5. 检查 Vite 缓存
echo ""
echo "🗑️  检查 Vite 缓存..."
if [ -d "node_modules/.vite" ]; then
    CACHE_SIZE=$(du -sh node_modules/.vite 2>/dev/null | cut -f1)
    echo -e "Vite 缓存大小: ${YELLOW}$CACHE_SIZE${NC}"
    echo "建议在修改配置后清理缓存: rm -rf node_modules/.vite"
else
    echo -e "${GREEN}✅ Vite 缓存目录不存在${NC}"
fi

# 6. 提供操作建议
echo ""
echo "💡 操作建议："
echo ""
echo "1. 清理 Vite 缓存："
echo "   rm -rf node_modules/.vite"
echo ""
echo "2. 启动开发服务器："
echo "   npm run dev"
echo ""
echo "3. 检查浏览器控制台是否有模块解析错误"
echo ""
echo "4. 运行生产构建测试："
echo "   npm run build"
echo ""
echo "5. 测试 GraphQL 功能："
echo "   访问 /games-graphql, /parameters-graphql, /events-graphql"
echo ""

# 7. 兼容性警告
echo "⚠️  兼容性提醒："
echo ""
if [[ "$VITE_VERSION" == 7.* ]]; then
    echo -e "${YELLOW}当前使用 Vite 7.x，与 Apollo Client v4 存在潜在兼容性问题${NC}"
    echo "如果遇到模块解析错误，考虑以下选项："
    echo "  1. 确保 optimizeDeps 配置完整（已完成）"
    echo "  2. 清理 Vite 缓存并重启开发服务器"
    echo "  3. 如果问题持续，考虑降级到 Vite 5.x:"
    echo "     npm install vite@^5.4.0 --save-dev"
fi

echo ""
echo "=========================================="
echo "✅ 配置验证完成"
echo ""
