# GitHub Secrets 配置指南

**创建日期**: 2026-03-18
**用途**: 为Event2Table CI/CD自动化配置GitHub Secrets

---

## 🎯 配置目标

为了启用`.github/workflows/ci-cd.yml`中的CI/CD自动化，需要在GitHub仓库中配置以下Secrets：

### 必需的Secrets（4个）

1. **LHCI_GITHUB_APP_TOKEN** - Lighthouse CI性能测试
2. **DEPLOY_KEY** - SSH部署密钥
3. **DATABASE_URL** - 数据库连接URL（可选）
4. **API_TOKEN** - API认证令牌（可选）

---

## 📋 分步配置指南

### 第1步：访问GitHub仓库设置

1. 打开GitHub仓库页面
2. 点击 **Settings** 标签
3. 在左侧菜单中找到 **Secrets and variables** → **Actions**
4. 点击 **New repository secret** 按钮

### 第2步：配置LHCI_GITHUB_APP_TOKEN

**用途**: Lighthouse CI性能测试结果上传到GitHub

**获取方式**:

```bash
# 1. 安装Lighthouse CI CLI
npm install -g @lhci/cli

# 2. 初始化Lighthouse CI（会引导你创建token）
lhci wizard

# 或者使用GitHub App安装:
# 访问: https://github.com/apps/lighthouse-ci
# 点击"Install"，选择你的仓库
```

**配置步骤**:
1. 在GitHub Actions设置中，点击 **New repository secret**
2. Name: `LHCI_GITHUB_APP_TOKEN`
3. Secret: 粘贴你的token（格式：`<GitHub username>:<LHCI token>`）
4. 点击 **Add secret**

**验证**:
```bash
# 验证token是否有效
lhci autorize --token <your-token>
```

---

### 第3步：配置DEPLOY_KEY（SSH部署密钥）

**用途**: 允许GitHub Actions通过SSH部署到服务器

**生成SSH密钥对**:

```bash
# 1. 生成新的SSH密钥对（如果还没有）
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# 2. 显示公钥内容
cat ~/.ssh/github_actions_deploy.pub

# 3. 显示私钥内容（复制时注意不要包含换行符）
cat ~/.ssh/github_actions_deploy
```

**配置步骤**:

**A. 在目标服务器上添加公钥**:
```bash
# 将公钥添加到服务器的authorized_keys
cat ~/.ssh/github_actions_deploy.pub >> ~/.ssh/authorized_keys

# 或者复制公钥内容，手动添加到服务器
```

**B. 在GitHub上添加私钥Secret**:
1. 在GitHub Actions设置中，点击 **New repository secret**
2. Name: `DEPLOY_KEY`
3. Secret: 粘贴私钥内容（整个文件内容，包括`-----BEGIN`和`-----END`行）
4. 点击 **Add secret**

**验证**:
```bash
# 测试SSH连接（使用生成的密钥）
ssh -i ~/.ssh/github_actions_deploy user@your-server.com

# 如果成功连接，说明配置正确
```

---

### 第4步：配置DATABASE_URL（可选）

**用途**: 数据库连接URL，用于测试或部署

**格式**: `sqlite:///path/to/database.db` 或其他数据库连接字符串

**配置步骤**:
1. 在GitHub Actions设置中，点击 **New repository secret**
2. Name: `DATABASE_URL`
3. Secret: `sqlite:///data/dwd_generator.db`
4. 点击 **Add secret**

**注意**: 如果数据库文件在仓库中，可以跳过此配置。

---

### 第5步：配置API_TOKEN（可选）

**用途**: API认证令牌，用于部署后验证API功能

**生成方式**:
```bash
# 生成随机token
openssl rand -hex 32

# 或使用Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**配置步骤**:
1. 在GitHub Actions设置中，点击 **New repository secret**
2. Name: `API_TOKEN`
3. Secret: 粘贴生成的token
4. 点击 **Add secret**

**应用端配置**（后端）:
```python
# backend/core/config/config.py
import os

API_TOKEN = os.environ.get('API_TOKEN', 'default-dev-token')
```

---

## ✅ 验证配置

### 验证Secrets是否添加成功

1. 在GitHub仓库中，进入 **Settings** → **Secrets and variables** → **Actions**
2. 确认以下Secrets都已添加：
   - ✅ `LHCI_GITHUB_APP_TOKEN`
   - ✅ `DEPLOY_KEY`
   - ✅ `DATABASE_URL` (可选)
   - ✅ `API_TOKEN` (可选)

### 手动触发CI/CD workflow测试

```bash
# 使用GitHub CLI触发workflow
gh workflow run ci-cd.yml

# 或在GitHub网页上:
# 1. 进入Actions标签
# 2. 选择"CI/CD Pipeline" workflow
# 3. 点击"Run workflow"按钮
# 4. 选择分支（main或opt/ci-cd）
# 5. 点击"Run workflow"
```

### 检查workflow运行状态

```bash
# 使用GitHub CLI检查最近的工作流运行
gh run list --workflow=ci-cd.yml --limit 5

# 查看特定运行的日志
gh run view <run-id> --log

# 或在GitHub网页上查看:
# Actions → 选择运行 → 查看各个job的日志
```

---

## 🔧 故障排除

### 问题1: LHCI测试失败

**错误信息**: `Error: Not authorized to upload to Lighthouse CI`

**解决方案**:
1. 检查`LHCI_GITHUB_APP_TOKEN`格式是否正确
2. 确认token有权限访问仓库
3. 重新生成token并更新Secret

### 问题2: SSH部署失败

**错误信息**: `Permission denied (publickey)`

**解决方案**:
1. 确认私钥内容完整（包含BEGIN和END行）
2. 检查服务器上`authorized_keys`文件权限：
   ```bash
   chmod 600 ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   ```
3. 测试SSH连接：
   ```bash
   ssh -i ~/.ssh/github_actions_deploy -T user@server
   ```

### 问题3: Secret未生效

**解决方案**:
1. 确认Secret名称拼写正确（区分大小写）
2. 删除并重新添加Secret
3. 检查workflow文件中引用Secret的语法：
   ```yaml
   env:
     TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}
   ```

---

## 📊 配置完成后的功能

配置完成后，CI/CD workflow将自动执行：

### 自动运行（每次push/PR）
- ✅ 后端单元测试 (pytest)
- ✅ 前端单元测试 (Vitest)
- ✅ E2E测试 (Playwright)
- ✅ Lighthouse性能测试
- ✅ 代码质量检查 (ESLint, mypy)

### 手动触发（部署）
- ✅ 自动部署到生产服务器
- ✅ 数据库迁移
- ✅ 性能监控
- ✅ 自动回滚（失败时<2分钟）

---

## 🎁 配置脚本（自动化）

为了简化配置过程，我创建了一个辅助脚本：

### 自动配置脚本

创建文件: `scripts/setup/github-secrets-setup.sh`

```bash
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
```

**使用方法**:
```bash
# 1. 创建脚本目录
mkdir -p scripts/setup

# 2. 创建脚本文件（将上面的脚本内容保存）

# 3. 添加执行权限
chmod +x scripts/setup/github-secrets-setup.sh

# 4. 运行脚本
bash scripts/setup/github-secrets-setup.sh
```

---

## 📖 参考文档

- [GitHub Actions Secrets文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Lighthouse CI文档](https://github.com/GoogleChrome/lighthouse-ci)
- [GitHub CLI文档](https://cli.github.com/manual/)

---

**配置完成后，Event2Table的CI/CD自动化将完全生效！** 🚀
