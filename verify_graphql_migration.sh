#!/bin/bash
# GraphQL迁移验证脚本

echo "🔍 验证GraphQL迁移完成情况..."
echo ""

# 验证路由配置
echo "1️⃣ 验证路由配置..."
if grep -q "DashboardGraphQL" /Users/mckenzie/Documents/event2table/frontend/src/routes/routes.jsx; then
  echo "✅ 路由配置已更新为GraphQL版本"
else
  echo "❌ 路由配置未更新"
fi

# 验证性能监控工具
echo ""
echo "2️⃣ 验证性能监控工具..."
if [ -f "/Users/mckenzie/Documents/event2table/frontend/src/shared/utils/graphqlPerformanceMonitor.js" ]; then
  size=$(wc -c < /Users/mckenzie/Documents/event2table/frontend/src/shared/utils/graphqlPerformanceMonitor.js)
  echo "✅ 性能监控工具已创建 ($size bytes)"
else
  echo "❌ 性能监控工具未创建"
fi

# 验证批量操作
echo ""
echo "3️⃣ 验证批量操作mutations..."
if [ -f "/Users/mckenzie/Documents/event2table/frontend/src/graphql/batchMutations.ts" ]; then
  mutations=$(grep -c "export const BATCH_" /Users/mckenzie/Documents/event2table/frontend/src/graphql/batchMutations.ts)
  echo "✅ 批量操作mutations已创建 ($mutations 个)"
else
  echo "❌ 批量操作mutations未创建"
fi

# 验证查询优化工具
echo ""
echo "4️⃣ 验证查询优化工具..."
if [ -f "/Users/mckenzie/Documents/event2table/frontend/src/shared/utils/graphqlQueryOptimizer.js" ]; then
  size=$(wc -c < /Users/mckenzie/Documents/event2table/frontend/src/shared/utils/graphqlQueryOptimizer.js)
  echo "✅ 查询优化工具已创建 ($size bytes)"
else
  echo "❌ 查询优化工具未创建"
fi

# 验证订阅功能
echo ""
echo "5️⃣ 验证订阅功能..."
if [ -f "/Users/mckenzie/Documents/event2table/frontend/src/graphql/subscriptions.ts" ]; then
  subscriptions=$(grep -c "export const ON_" /Users/mckenzie/Documents/event2table/frontend/src/graphql/subscriptions.ts)
  echo "✅ 订阅定义已创建 ($subscriptions 个)"
else
  echo "❌ 订阅定义未创建"
fi

if [ -f "/Users/mckenzie/Documents/event2table/frontend/src/graphql/subscriptionHooks.ts" ]; then
  hooks=$(grep -c "export function use" /Users/mckenzie/Documents/event2table/frontend/src/graphql/subscriptionHooks.ts)
  echo "✅ 订阅hooks已创建 ($hooks 个)"
else
  echo "❌ 订阅hooks未创建"
fi

# 验证文档
echo ""
echo "6️⃣ 验证文档..."
docs=(
  "docs/GRAPHQL_API_DOCUMENTATION.md"
  "GRAPHQL_MIGRATION_PROGRESS_REPORT.md"
  "GRAPHQL_MIGRATION_FINAL_SUMMARY.md"
)

for doc in "${docs[@]}"; do
  if [ -f "/Users/mckenzie/Documents/event2table/$doc" ]; then
    size=$(wc -c < "/Users/mckenzie/Documents/event2table/$doc")
    echo "✅ $doc ($size bytes)"
  else
    echo "❌ $doc 未创建"
  fi
done

echo ""
echo "🎉 GraphQL迁移验证完成!"
