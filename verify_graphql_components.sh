#!/bin/bash
# GraphQL组件验证脚本

echo "🔍 验证GraphQL组件文件..."

COMPONENTS=(
  "frontend/src/analytics/pages/DashboardGraphQL.jsx"
  "frontend/src/analytics/pages/EventsListGraphQL.jsx"
  "frontend/src/analytics/pages/EventDetailGraphQL.jsx"
  "frontend/src/analytics/pages/CategoriesListGraphQL.jsx"
  "frontend/src/analytics/pages/ParametersEnhancedGraphQL.jsx"
)

all_ok=true

for component in "${COMPONENTS[@]}"; do
  if [ -f "$component" ]; then
    size=$(wc -c < "$component")
    echo "✅ $component (${size} bytes)"
  else
    echo "❌ $component - 文件不存在"
    all_ok=false
  fi
done

echo ""
echo "🔍 验证GraphQL hooks和queries..."

if [ -f "frontend/src/graphql/hooks.ts" ]; then
  hooks_count=$(grep -c "export function use" frontend/src/graphql/hooks.ts)
  echo "✅ hooks.ts - 包含 $hooks_count 个hooks"
else
  echo "❌ hooks.ts - 文件不存在"
  all_ok=false
fi

if [ -f "frontend/src/graphql/queries.ts" ]; then
  queries_count=$(grep -c "export const GET_" frontend/src/graphql/queries.ts)
  echo "✅ queries.ts - 包含 $queries_count 个查询"
else
  echo "❌ queries.ts - 文件不存在"
  all_ok=false
fi

echo ""
if [ "$all_ok" = true ]; then
  echo "🎉 所有GraphQL组件验证通过!"
  exit 0
else
  echo "⚠️  部分组件验证失败"
  exit 1
fi
