#!/bin/bash

# 修复特定组件的扩展名映射
declare -A extensions_map=(
  ["@shared/ui/Toast"]=".tsx"
  ["@shared/ui/ErrorBoundary"]=".tsx"
  ["@event-builder/components/FieldCanvas"]=".tsx"
  ["@event-builder/components/FieldsListModal"]=".tsx"
  ["@event-builder/components/HQLViewModal"]=".tsx"
  ["@event-builder/components/AdvancedFilterPanel"]=".tsx"
  ["@event-builder/components/FieldEventSelector"]=".tsx"
  ["@event-builder/components/ParamSelector"]=".tsx"
  ["@event-builder/components/EventSelector"]=".tsx"
  ["@event-builder/components/NodeConfigForm"]=".tsx"
  ["@event-builder/components/PageHeader"]=".tsx"
  ["@event-builder/components/LeftSidebar"]=".tsx"
  ["@event-builder/components/RightSidebar"]=".tsx"
  ["@event-builder/components/StatsPanel"]=".tsx"
  ["@event-builder/components/BaseFieldsList"]=".jsx"
)

echo "🔧 Fixing component extensions..."

for component in "${!extensions_map[@]}"; do
  ext="${extensions_map[$component]}"
  echo "Fixing $component to $ext"
  find . -type f \( -name "*.jsx" -o -name "*.tsx" \) -exec sed -i '' \
    -e "s|from '$component'|from '$component$ext'|g" \
    {} \; 2>/dev/null
done

echo "✅ Fixed all component extensions"
