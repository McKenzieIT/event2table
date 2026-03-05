# 分支保护规则配置指南

**仓库**：https://github.com/McKenzieIT/event2table
**分支**：main

---

## 🎯 配置目标

为main分支配置以下保护规则：
- ✅ 需要Pull Request才能合并
- ✅ 至少1个审查批准
- ✅ 自动驳回过期的审查
- ✅ 管理员也必须遵守规则
- ✅ 禁止强制推送
- ✅ 禁止删除分支

---

## 📋 手动配置步骤

### 方法1：通过GitHub网页配置（推荐）

1. **访问仓库设置**
   - 打开：https://github.com/McKenzieIT/event2table/settings/branches

2. **点击"Add rule"**
   - 分支名称模式：`main`

3. **配置"Branch name pattern"**
   - ✅ 勾选 "Require a pull request before merging"

4. **配置"Require pull request reviews"**
   - ✅ Required approving reviews: **1**
   - ✅ Dismiss stale reviews when new commits are pushed: **勾选**
   - ❌ Require review from CODEOWNERS: **不勾选**
   - ❌ Require review from a code owner: **不勾选**

5. **配置"Do not allow bypassing the above settings"**
   - ✅ 勾选此选项（管理员也必须遵守）

6. **点击"Create"保存**

### 方法2：使用GitHub CLI（高级用户）

如果`gh` CLI支持API调用，可以使用以下命令：

```bash
# 方法1：直接API调用
gh api \
  --method PUT \
  --header "Accept: application/vnd.github.v3+json" \
  repos/McKenzieIT/event2table/branches/main/protection \
  --input - << 'JSON'
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "bypass_pull_request_allowances": {
      "apps": {},
      "users": []
    }
  },
  "required_status_checks": {
    "strict": false,
    "contexts": [],
    "checks": []
  },
  "enforce_admins": true,
  "allow_deletions": false,
  "allow_force_pushes": false
}
JSON

# 方法2：使用gh extension (如果安装了)
# gh branch-protection protect --repo McKenzieIT/event2table --branch main \
#   --require-approval 1 --dismiss-stale --enforce-admins \
#   --no-allow-force-pushes --no-allow-deletions
```

---

## ✅ 配置验证

配置完成后，验证规则是否生效：

1. **尝试直接推送**
   ```bash
   git push origin main
   ```
   应该被拒绝（需要PR）

2. **创建测试PR**
   - 创建新分支
   - 提交更改
   - 创建PR
   - 应该需要批准才能合并

---

## 🔒 配置说明

### 为什么需要这些规则？

1. **代码质量保证**
   - 所有变更需要审查
   - 避免低质量代码合并

2. **防止意外**
   - 禁止强制推送（保护历史）
   - 禁止删除分支（保护main）
   - 管理员也遵守规则（避免特权滥用）

3. **自动化**
   - 自动驳回过期审查（保持流程更新）

---

## 📝 可选：配置必需的状态检查

如果配置了CI/CD（如GitHub Actions），可以添加：

1. 在分支保护设置中
2. 找到"Require status checks to pass before merging"
3. 添加以下检查：
   - `pre-commit`
   - `tests`
   - `ci/ci`

---

## 🔄 如何临时绕过（紧急情况）

**不推荐！**仅在紧急情况下使用：

1. 临时修改分支保护规则
2. 合并紧急修复
3. 立即恢复保护规则

---

## 📚 相关资源

- [GitHub Docs: About branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-merge-behavior-of-your-repository/about-protected-branches)
- [GitHub Docs: Configuring protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-protected-branches)
- [贡献指南](./contributing.md)

---

**配置完成后**，请通知团队成员，确保大家都了解新的工作流程。
