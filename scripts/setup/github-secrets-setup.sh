#!/bin/bash
# GitHub Secrets配置辅助脚本

echo "🚀 GitHub Secrets配置助手"
echo "========================="
echo ""

# 检查gh CLI是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) 未安装"
    echo "   安装: brew install gh"
    echo "   认证: gh auth login"
    exit 1
fi

# 检查认证状态
if ! gh auth status &> /dev/null; then
    echo "❌ 未登录GitHub"
    echo "   请先运行: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI已安装并认证"
echo ""

# 配置LHCI_GITHUB_APP_TOKEN
echo "📝 配置LHCI_GITHUB_APP_TOKEN"
echo "----------------------------"
read -p "请输入LHCI token (格式: username:token): " lhci_token

if [ -n "$lhci_token" ]; then
    echo "$lhci_token" | gh secret set LHCI_GITHUB_APP_TOKEN
    echo "✅ LHCI_GITHUB_APP_TOKEN已设置"
fi

echo ""

# 配置DEPLOY_KEY
echo "📝 配置DEPLOY_KEY (SSH私钥)"
echo "----------------------------"
read -p "请输入SSH私钥文件路径 (默认: ~/.ssh/github_actions_deploy): " key_path
key_path=${key_path:-~/.ssh/github_actions_deploy}

if [ -f "$key_path" ]; then
    gh secret set DEPLOY_KEY < "$key_path"
    echo "✅ DEPLOY_KEY已设置"
else
    echo "❌ 文件不存在: $key_path"
fi

echo ""

# 配置DATABASE_URL（可选）
echo "📝 配置DATABASE_URL (可选)"
echo "----------------------------"
read -p "请输入DATABASE_URL (留空跳过): " db_url

if [ -n "$db_url" ]; then
    echo "$db_url" | gh secret set DATABASE_URL
    echo "✅ DATABASE_URL已设置"
else
    echo "⏭️  跳过DATABASE_URL配置"
fi

echo ""

# 配置API_TOKEN（可选）
echo "📝 配置API_TOKEN (可选)"
echo "----------------------------"
read -p "请输入API_TOKEN (留空跳过，或自动生成): " api_token

if [ -n "$api_token" ]; then
    echo "$api_token" | gh secret set API_TOKEN
    echo "✅ API_TOKEN已设置"
elif command -v openssl &> /dev/null; then
    # 自动生成token
    api_token=$(openssl rand -hex 32)
    echo "$api_token" | gh secret set API_TOKEN
    echo "✅ API_TOKEN已自动生成并设置"
    echo "   Token: $api_token"
else
    echo "⏭️  跳过API_TOKEN配置"
fi

echo ""
echo "✅ GitHub Secrets配置完成！"
echo ""
echo "🔍 验证配置:"
gh secret list

echo ""
echo "🚀 测试CI/CD:"
echo "   gh workflow run ci-cd.yml"
