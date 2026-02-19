# GitHub和Pull Request工作流设置指南

**创建时间**: 2026-02-19
**项目**: Event2Table
**目的**: 建立规范的Git工作流和代码审查流程

---

## 📋 前置条件

1. ✅ 已有GitHub账号
2. ✅ 已安装git
3. ⚠️ 需要创建GitHub远程仓库

---

## 第一步：创建GitHub远程仓库

### 选项A: 使用GitHub CLI（推荐）

```bash
# 安装gh CLI（如果未安装）
brew install gh  # macOS
# 或
sudo apt install gh  # Ubuntu/Debian

# 登录GitHub
gh auth login

# 创建新仓库
gh repo create event2table --public --source=. --remote=origin --push
```

### 选项B: 手动创建

1. 访问 https://github.com/new
2. 创建新仓库：`event2table`
3. **不要**初始化README、.gitignore或license（已有）
4. 创建后，按照GitHub的提示添加远程仓库：

```bash
git remote add origin https://github.com/你的用户名/event2table.git
git branch -M main
git push -u origin main
```

---

## 第二步：配置分支保护规则

### 保护main分支

1. 访问仓库设置：https://github.com/你的用户名/event2table/settings/branches
2. 点击 "Add rule"
3. 分支名称模式：`main`
4. 启用以下选项：
   - ✅ Require a pull request before merging
     - Required approvals: 1
   - ✅ Require status checks to pass before merging
     - Require branches to be up to date before merging
   - ✅ Do not allow bypassing the above settings
   - ❌ Restrict who can push to matching branches（暂时不启用）

### 配置必需的状态检查

在分支保护规则中，添加以下必需的检查：
- `pre-commit`（如果有CI）
- `tests`（如果有测试套件）

---

## 第三步：配置Pull Request模板

### 创建PR模板

创建文件 `.github/pull_request_template.md`：

```markdown
## 📝 变更描述

<!-- 简要描述这个PR的变更内容 -->

## 🔗 相关Issue

Closes #(issue编号)

## 🎯 变更类型

- [ ] 🐛 Bug修复
- [ ] ✨ 新功能
- [ ] 📝 文档更新
- [ ] ♻️ 代码重构
- [ ] ⚡ 性能优化
- [ ] ✅ 测试
- [ ] 🔧 配置

## 📸 截图（如果适用）

<!-- 添加截图或GIF展示UI变更 -->

## ✅ 检查清单

- [ ] 我的代码遵循了项目的代码规范
- [ ] 我已阅读 [CLAUDE.md](../CLAUDE.md) 并遵守相关规范
- [ ] 我已进行自我审查
- [ ] 我已为代码添加了注释（特别是难以理解的区域）
- [ ] 我已更新了相关文档
- [ ] 我的变更没有产生新的警告
- [ ] 我已通过本地测试验证变更
- [ ] 我已添加了能证明修复有效或特性可用的测试

## 🧪 测试

<!-- 描述你运行的测试以及如何重现它们 -->

## 📋 审查要点

<!-- 请审查者特别关注的区域 -->

## 📚 额外信息

<!-- 任何其他信息 -->
```

---

## 第四步：配置CI/CD（可选）

### 使用GitHub Actions

创建文件 `.github/workflows/ci.yml`：

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run backend tests
      run: |
        pytest backend/test/ -v

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '25'

    - name: Install dependencies
      run: |
        cd frontend
        npm install

    - name: Run frontend tests
      run: |
        cd frontend
        npm run test

  code-quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run API contract tests
      run: |
        python scripts/test/api_contract_test.py
```

---

## 第五步：配置代码审查自动化

### 使用Alexa或类似工具

创建文件 `.github/CODEOWNERS`：

```
# 默认代码审查者
* @你的用户名

# 特定路径的代码审查者
/backend/ @你的用户名
/frontend/ @你的用户名
/docs/ @你的用户名
```

---

## 第六步：建立开发工作流

### 推荐的Git工作流

```
1. 创建功能分支
   git checkout -b feature/功能名称

2. 进行开发和提交
   git add .
   git commit -m "feat: 添加功能描述"

3. 推送到远程
   git push origin feature/功能名称

4. 创建Pull Request
   gh pr create --title "添加功能描述" --body "填写PR描述"

5. 代码审查和修改
   - 根据反馈修改代码
   - 推送更新到功能分支

6. 合并PR
   - 使用 "Squash and merge" 保持历史清洁
   - 或使用 "Merge commit" 保留完整历史

7. 删除功能分支
   git branch -d feature/功能名称
   gh pr edit --delete-branch
```

---

## 第七步：配置pre-commit hooks

### 自动化代码质量检查

创建文件 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: local
    hooks:
      - id: database-location
        name: Check database file location
        entry: python scripts/git-hooks/pre-commit
        language: system
        pass_filenames: false

      - id: api-contract
        name: API contract test
        entry: python scripts/test/api_contract_test.py
        language: system
        pass_filenames: false

      - id: frontend-lint
        name: Frontend lint
        entry: cd frontend && npm run lint
        language: system
        pass_filenames: false
```

安装pre-commit：

```bash
pip install pre-commit
pre-commit install
```

---

## 第八步：配置GitHub模板

### Issue模板

创建文件 `.github/ISSUE_TEMPLATE/bug_report.md`：

```markdown
---
name: Bug报告
about: 报告一个bug帮助我们改进
title: '[BUG] '
---

## 🐛 Bug描述

<!-- 清晰简洁地描述bug是什么 -->

## 📍 复现步骤

1. 前往 '...'
2. 点击 '....'
3. 滚动到 '....'
4. 看到错误

## 🤔 期望行为

<!-- 描述你期望发生什么 -->

## 📸 截图

<!-- 如果适用，添加截图帮助解释问题 -->

## 💻 环境信息

- 操作系统: [例如 macOS 14.0]
- 浏览器: [例如 Chrome 121]
- Node版本: [例如 25.6.0]
- Python版本: [例如 3.9]

## 📋 额外信息

<!-- 添加任何其他有助于解决问题的信息 -->
```

---

## 第九步：配置项目Wiki

### 创建Wiki页面

1. 访问仓库的Wiki
2. 创建以下页面：
   - Home（项目概述）
   - Getting-Started（快速开始）
   - Development-Workflow（开发工作流）
   - Code-Review-Guidelines（代码审查指南）
   - Deployment-Guide（部署指南）

---

## 第十步：建立社区指南

### 创建CONTRIBUTING.md

创建文件 `CONTRIBUTING.md`：

```markdown
# 贡献指南

感谢你对Event2Table项目的关注！

## 如何贡献

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 代码规范

- 遵守 [CLAUDE.md](CLAUDE.md) 中的开发规范
- 使用语义化提交信息
- 添加单元测试
- 更新相关文档

## 代码审查流程

1. 提交Pull Request
2. 至少一名维护者审查
3. 修复审查意见
4. 通过CI测试
5. 合并到main分支

## 行为准则

- 尊重不同观点
- 欢迎建设性批评
- 关注对社区最有利的事情

## 联系方式

- 项目维护者：[你的名字]
- Email：[你的邮箱]
```

---

## ✅ 验证清单

完成以上步骤后，验证：

- [ ] GitHub远程仓库已配置
- [ ] main分支已启用保护规则
- [ ] PR模板已创建
- [ ] CI/CD已配置（如果需要）
- [ ] CODEOWNERS已配置
- [ ] pre-commit hooks已安装
- [ ] Issue模板已创建
- [ ] CONTRIBUTING.md已创建
- [ ] Wiki页面已创建

---

## 🎯 下一步行动

1. **立即执行**：创建GitHub远程仓库并推送代码
2. **本周完成**：配置分支保护和PR模板
3. **本月完成**：配置CI/CD和pre-commit hooks

---

**文档版本**: 1.0
**最后更新**: 2026-02-19
**维护者**: Event2Table Team
