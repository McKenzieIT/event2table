#!/bin/bash
# Chrome MCP兼容性修复验证脚本

echo "=========================================="
echo "Chrome MCP兼容性修复验证"
echo "=========================================="
echo ""

# 检查文件是否存在
FILES=(
  "src/event-builder/components/modals/NodeConfigModal.tsx"
  "src/features/events/EventManagementModalGraphQL.tsx"
  "src/features/events/AddEventModalGraphQL.tsx"
)

echo "1. 检查文件是否存在..."
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (不存在)"
  fi
done

echo ""
echo "2. 检查Chrome MCP兼容性代码移除情况..."

# 检查是否还包含手动Chrome MCP兼容性代码
echo "  检查手动useEffect + ref模式..."
if grep -q "Chrome MCP兼容性: 监听DOM值变化" src/event-builder/components/modals/NodeConfigModal.tsx 2>/dev/null; then
  echo "    ❌ NodeConfigModal.tsx - 仍包含手动Chrome MCP代码"
else
  echo "    ✅ NodeConfigModal.tsx - 已移除手动Chrome MCP代码"
fi

if grep -q "Chrome MCP兼容性: 监听DOM值变化" src/features/events/EventManagementModalGraphQL.tsx 2>/dev/null; then
  echo "    ❌ EventManagementModalGraphQL.tsx - 仍包含手动Chrome MCP代码"
else
  echo "    ✅ EventManagementModalGraphQL.tsx - 已移除手动Chrome MCP代码"
fi

if grep -q "Chrome MCP兼容性: 监听DOM值变化" src/features/events/AddEventModalGraphQL.tsx 2>/dev/null; then
  echo "    ❌ AddEventModalGraphQL.tsx - 仍包含手动Chrome MCP代码"
else
  echo "    ✅ AddEventModalGraphQL.tsx - 已移除手动Chrome MCP代码"
fi

echo ""
echo "3. 检查useChromeMCPCompatibleInput hook导入..."
for file in "${FILES[@]}"; do
  if grep -q "useChromeMCPCompatibleInput" "$file" 2>/dev/null; then
    echo "  ✅ $file - 已导入hook"
  else
    echo "  ❌ $file - 未导入hook"
  fi
done

echo ""
echo "4. 统计代码行数变化..."
echo "  NodeConfigModal.tsx:"
  wc -l src/event-builder/components/modals/NodeConfigModal.tsx | awk '{print "    当前: " $1 " 行"}'
  wc -l src/event-builder/components/modals/NodeConfigModal.tsx.backup | awk '{print "    备份: " $1 " 行"}' 2>/dev/null || echo "    备份: 不存在"

echo ""
echo "  EventManagementModalGraphQL.tsx:"
  wc -l src/features/events/EventManagementModalGraphQL.tsx | awk '{print "    当前: " $1 " 行"}'
  wc -l src/features/events/EventManagementModalGraphQL.tsx.backup | awk '{print "    备份: " $1 " 行"}' 2>/dev/null || echo "    备份: 不存在"

echo ""
echo "  AddEventModalGraphQL.tsx:"
  wc -l src/features/events/AddEventModalGraphQL.tsx | awk '{print "    当前: " $1 " 行"}'
  wc -l src/features/events/AddEventModalGraphQL.tsx.backup | awk '{print "    备份: " $1 " 行"}' 2>/dev/null || echo "    备份: 不存在"

echo ""
echo "=========================================="
echo "验证完成"
echo "=========================================="
