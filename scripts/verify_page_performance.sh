#!/bin/bash
# 页面加载性能快速验证脚本
# 使用方法: ./scripts/verify_page_performance.sh

set -e

echo "🚀 Event2Table 页面加载性能验证"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查服务器是否运行
echo "📡 检查开发服务器..."
if ! curl -s http://localhost:5173 > /dev/null; then
  echo -e "${RED}❌ 开发服务器未运行${NC}"
  echo "请先启动: cd frontend && npm run dev"
  exit 1
fi
echo -e "${GREEN}✅ 服务器运行正常${NC}"
echo ""

# 测试1: 基本加载时间
echo "🔍 测试1: 基本加载性能"
TIME_TOTAL=$(curl -w "%{time_total}" -o /dev/null -s http://localhost:5173/)
TTFB=$(curl -w "%{time_starttransfer}" -o /dev/null -s http://localhost:5173/)

echo "总加载时间: ${TIME_TOTAL}s"
echo "首字节时间(TTFB): ${TTFB}s"

if (( $(echo "$TIME_TOTAL < 1.0" | bc -l) )); then
  echo -e "${GREEN}✅ 加载时间良好 (<1s)${NC}"
elif (( $(echo "$TIME_TOTAL < 2.0" | bc -l) )); then
  echo -e "${YELLOW}⚠️  加载时间可接受 (<2s)${NC}"
else
  echo -e "${RED}❌ 加载时间过长 (>2s)${NC}"
fi
echo ""

# 测试2: FOUC检查
echo "🔍 测试2: FOUC（样式闪烁）检查"
HTML=$(curl -s http://localhost:5173/)

if echo "$HTML" | grep -q "style"; then
  echo -e "${GREEN}✅ 内联样式存在（防止FOUC）${NC}"
else
  echo -e "${RED}❌ 缺少内联样式（FOUC风险）${NC}"
fi

if echo "$HTML" | grep -q "initial-loader"; then
  echo -e "${GREEN}✅ 加载指示器存在${NC}"
else
  echo -e "${YELLOW}⚠️  无加载指示器${NC}"
fi
echo ""

# 测试3: Bundle大小
echo "🔍 测试3: Bundle大小分析"
if [ -d "frontend/dist/assets/js" ]; then
  echo "生产Bundle:"
  ls -lh frontend/dist/assets/js/*.js | awk '{print $5, $9}'
  TOTAL=$(du -sh frontend/dist/assets/js | awk '{print $1}')
  echo "总计: $TOTAL"
else
  echo -e "${YELLOW}⚠️  生产构建不存在（运行 npm run build）${NC}"
fi
echo ""

# 测试4: Suspense使用情况
echo "🔍 测试4: Suspense架构检查"
SUSPENSE_COUNT=$(grep -r "Suspense" frontend/src/ --include="*.tsx" --include="*.jsx" 2>/dev/null | grep -v node_modules | wc -l)
echo "Suspense引用数: $SUSPENSE_COUNT"

if grep -q "Suspense" frontend/src/App.tsx; then
  if grep "import.*Suspense" frontend/src/App.tsx > /dev/null; then
    echo -e "${YELLOW}⚠️  App.tsx导入并使用Suspense${NC}"
  else
    echo -e "${GREEN}✅ App.tsx仅注释提到Suspense（未使用）${NC}"
  fi
else
  echo -e "${GREEN}✅ App.tsx不使用Suspense${NC}"
fi

LAZY_COUNT=$(grep -r "lazy(()" frontend/src/ --include="*.tsx" --include="*.jsx" 2>/dev/null | wc -l)
echo "Lazy loading使用: $LAZY_COUNT处"
echo ""

# 测试5: CSS加载顺序
echo "🔍 测试5: CSS加载顺序检查"
if grep -q "design-tokens.css" frontend/src/main.tsx; then
  echo -e "${GREEN}✅ design-tokens.css (设计变量)${NC}"
fi
if grep -q "components.css" frontend/src/main.tsx; then
  echo -e "${GREEN}✅ components.css (组件样式)${NC}"
fi
if grep -q "index.css" frontend/src/main.tsx; then
  echo -e "${GREEN}✅ index.css (基础样式)${NC}"
fi
echo ""

# 总结
echo "=================================="
echo "📊 诊断总结"
echo "=================================="
echo ""
echo "✅ 完成的检查:"
echo "  - 服务器响应性能"
echo "  - FOUC风险分析"
echo "  - Bundle大小"
echo "  - Suspense架构"
echo "  - CSS加载顺序"
echo ""
echo "📋 下一步行动:"
echo "  1. 在真实浏览器打开性能测试页面:"
echo "     open http://localhost:5173/performance-test.html"
echo ""
echo "  2. 查看完整诊断报告:"
echo "     cat docs/reports/2026-03-06/PAGE-LOAD-PERFORMANCE-DIAGNOSIS.md"
echo ""
echo "  3. 如需优化，参考报告中的建议措施"
echo ""
