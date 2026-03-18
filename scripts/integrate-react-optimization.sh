#!/bin/bash
# React优化工具集成指南
# 创建日期: 2026-03-18

set -e

echo "🚀 React优化工具集成"
echo "==================="
echo ""

# 检查OptimizedVirtualList是否存在
if [ -f "frontend/src/shared/components/VirtualList/OptimizedVirtualList.tsx" ]; then
    echo "✅ OptimizedVirtualList 组件已存在"
else
    echo "❌ OptimizedVirtualList 组件不存在"
    echo "   请先创建: frontend/src/shared/components/VirtualList/OptimizedVirtualList.tsx"
    exit 1
fi

# 检查performanceMonitor是否存在
if [ -f "frontend/src/shared/utils/performanceMonitor.ts" ]; then
    echo "✅ performanceMonitor hook已存在"
else
    echo "❌ performanceMonitor hook不存在"
    exit 1
fi

# 检查lazyModals是否存在
if [ -f "frontend/src/shared/utils/lazyModals.tsx" ]; then
    echo "✅ lazyModals工具已存在"
else
    echo "❌ lazyModals工具不存在"
    exit 1
fi

echo ""
echo "📋 可以优化的组件："
echo "==================="
echo ""

# 查找列表组件
echo "🔍 列表组件 (使用OptimizedVirtualList):"
echo "----------------------------------------"
find frontend/src -name "*List*.tsx" -not -path "*/node_modules/*" -not -path "*/__tests__/*" -not -path "*/test/*" | while read file; do
    if grep -q "\.map(" "$file" 2>/dev/null; then
        echo "  📝 $file"
        # 统计行数
        lines=$(wc -l < "$file")
        echo "     ($lines 行)"
    fi
done

echo ""
echo "🔍 Modal组件 (使用lazyModals):"
echo "-------------------------------"
find frontend/src -name "*Modal*.tsx" -not -path "*/node_modules/*" -not -path "*/__tests__/*" -not -path "*/test/*" | while read file; do
    echo "  📝 $file"
done

echo ""
echo "📚 优化指南："
echo "==========="
echo ""
echo "1️⃣ 优化列表组件 (使用OptimizedVirtualList):"
echo ""
cat << 'EOF'
// 优化前
{items.map(item => (
  <Item key={item.id} data={item} />
))}

// 优化后
import { OptimizedVirtualList } from '@/shared/components/VirtualList/OptimizedVirtualList';

<OptimizedVirtualList
  items={items}
  renderItem={(item) => <Item data={item} />}
  itemHeight={50}  // 根据实际情况调整
  height={600}     // 根据实际情况调整
/>
EOF

echo ""
echo "2️⃣ 优化Modal组件 (使用lazyModals):"
echo ""
cat << 'EOF'
// 优化前
import { GameManagementModal } from '@/features/games/modals/GameManagementModal';

// 优化后
import { LazyGameManagementModal } from '@/shared/utils/lazyModals';

<Suspense fallback={<Spinner />}>
  <LazyGameManagementModal isOpen={isOpen} onClose={handleClose} />
</Suspense>
EOF

echo ""
echo "3️⃣ 添加性能监控 (使用performanceMonitor):"
echo ""
cat << 'EOF'
import { usePerformanceMonitor } from '@/shared/utils/performanceMonitor';

function MyComponent() {
  usePerformanceMonitor('MyComponent', 16.67); // 60fps
  // ... 组件代码
}
EOF

echo ""
echo "✅ 优化工具检查完成！"
echo ""
echo "📖 详细文档:"
echo "   - frontend/src/shared/components/VirtualList/README.md"
echo "   - docs/performance/react-optimization-guide.md"
