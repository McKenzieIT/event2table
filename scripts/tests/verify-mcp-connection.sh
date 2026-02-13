#!/bin/bash
# MCP 连接验证脚本

echo "🔍 验证 chrome-devtools-mcp 安装..."

# 测试 1：检查 Claude MCP 配置
echo "1️⃣  检查 Claude MCP 配置..."
if [ -f "$HOME/.config/claude/mcp-servers.json" ]; then
    echo "   ✅ MCP 配置文件存在"
    # 检查是否包含 chrome-devtools
    if grep -q "chrome-devtools" "$HOME/.config/claude/mcp-servers.json"; then
        echo "   ✅ chrome-devtools 已配置"
    else
        echo "   ❌ chrome-devtools 未找到"
        exit 1
    fi
else
    echo "   ❌ MCP 配置文件不存在"
    exit 1
fi

# 测试 2：验证 npx 可以访问 chrome-devtools-mcp
echo "2️⃣  检查 chrome-devtools-mcp 可访问性..."
if export PATH="/usr/local/Cellar/node/25.6.0/bin:$PATH" && npx chrome-devtools-mcp@latest --version &> /dev/null; then
    echo "   ✅ chrome-devtools-mcp 可访问"
    VERSION=$(export PATH="/usr/local/Cellar/node/25.6.0/bin:$PATH" && npx chrome-devtools-mcp@latest --version 2>&1)
    echo "   📦 版本: $VERSION"
else
    echo "   ❌ chrome-devtools-mcp 不可访问"
    exit 1
fi

# 测试 3：检查 Chrome 浏览器
echo "3️⃣  检查 Chrome 浏览器..."
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    echo "   ✅ Chrome 浏览器已安装"
else
    echo "   ⚠️  Chrome 浏览器未找到（将使用默认浏览器）"
fi

# 测试 4：检查项目权限配置
echo "4️⃣  检查项目权限配置..."
if grep -q "chrome-devtools-mcp" .claude/settings.local.json; then
    echo "   ✅ 项目权限已配置"
else
    echo "   ⚠️  项目权限可能需要更新"
    echo "   💡 请在 .claude/settings.local.json 中添加："
    echo '      "Bash(npx chrome-devtools-mcp@latest:*)"'
fi

echo ""
echo "✅ MCP 连接验证通过！"
