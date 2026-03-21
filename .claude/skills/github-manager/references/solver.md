# Solver 解决器模块

解决方案模板库，为每个问题类型提供最佳实践解决方案。

---

## 一、解决方案匹配流程

### Step 1: 问题类型匹配

根据问题类型，选择对应的解决方案模板：

| 问题类型 | 首选方案 | 备选方案 |
|---------|---------|---------|
| BRANCH_DIVERGED | git_rebase | git_merge |
| MAIN_BRANCH_DEV | create_feature_branch | - |
| NO_BRANCH_PROTECTION | setup_branch_protection | - |
| UNCOMMITTED_CHANGES | batch_commit | - |
| CI_FAILURE | fix_ci_failure | - |
| MERGE_CONFLICT | resolve_conflicts | - |
| BEHIND_REMOTE | pull_with_rebase | - |
| NO_PR_TEMPLATE | create_pr_template | - |
| LARGE_PR | split_pr | - |
| STALE_PR | review_stale_pr | close_stale_pr |

### Step 2: 用户偏好检查

```python
# 检查用户偏好
if user_preferences.preferred_solutions.get(problem_type):
    solution = user_preferences.preferred_solutions[problem_type]
else:
    solution = DEFAULT_SOLUTIONS[problem_type]
```

### Step 3: 前提条件检查

每个方案执行前必须检查前提条件：

| 方案 | 前提条件 | 不满足时的处理 |
|------|---------|---------------|
| git_rebase | 工作区干净或已暂存 | 先执行 `git stash` |
| git_merge | 工作区干净或已暂存 | 先执行 `git stash` |
| create_feature_branch | 在main分支上有修改 | 直接执行 |
| setup_branch_protection | 有GitHub管理员权限 | 提示用户联系管理员 |
| fix_ci_failure | 有CI访问权限 | 提示用户检查CI配置 |

---

## 二、解决方案模板

### 2.1 git_rebase（解决分支分叉）

**方案标题**: 使用 git rebase 变基合并

**执行步骤**（按顺序）:

| 步骤 | 命令 | 描述 | 风险 | 需确认 | 回滚 |
|------|------|------|------|--------|------|
| 1 | `git stash push -m 'backup before rebase'` | 备份当前未提交的工作 | 🟢 低 | 否 | `git stash pop` |
| 2 | `git fetch origin` | 获取远程最新更新 | 🟢 低 | 否 | - |
| 3 | `git rebase origin/{branch}` | 变基到远程分支 | 🟡 中 | 是 | `git rebase --abort` |
| 4 | `git stash pop` | 恢复之前暂存的工作 | 🟢 低 | 否 | - |

**最佳实践说明**（必须解释WHY）:

1. **保持线性历史** 
   - rebase不会产生额外的merge commit
   - 历史更清晰易读
   - 便于代码审查

2. **便于冲突定位**
   - 变基时逐个提交应用
   - 冲突更容易定位和解决
   - 不会因为一次合并引入多个冲突

3. **符合GitHub Flow**
   - 主分支应始终保持可部署状态
   - 功能分支在合并前应该变基
   - 避免不必要的merge commit

**风险因素**:
- 重写本地提交历史
- 可能遇到冲突需要手动解决
- 如果已推送到远程，需要force push（谨慎使用）

**详细回滚方案**:

**场景1: rebase过程中发现冲突，想放弃**
```bash
git rebase --abort
```

**场景2: rebase完成但想撤销**
```bash
# 方法1: 使用ORIG_HEAD（推荐）
git reset --hard ORIG_HEAD

# 方法2: 使用reflog查找rebase前的提交
git reflog
git reset --hard HEAD@{N}
```

**场景3: 已push但想撤销（危险）**
```bash
# ⚠️ 警告：这会重写远程历史
git reset --hard ORIG_HEAD
git push --force-with-lease origin {branch}
```

---

### 2.2 create_feature_branch（解决main分支开发）

**方案标题**: 创建功能分支迁移修改

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `git stash push -m 'backup before branch'` | 备份当前修改 | 🟢 低 | 否 |
| 2 | `git checkout main` | 切换到main分支 | 🟢 低 | 否 |
| 3 | `git pull origin main` | 同步远程main | 🟢 低 | 否 |
| 4 | `git checkout -b feature/{name}` | 创建功能分支 | 🟢 低 | 是 |
| 5 | `git stash pop` | 恢复修改到新分支 | 🟢 低 | 否 |

**最佳实践说明**:

1. **隔离开发**
   - 功能分支隔离修改
   - 不影响main分支稳定性
   - 便于代码审查

2. **便于回滚**
   - 如果功能有问题，直接删除分支
   - main分支保持干净
   - 降低风险

**分支命名建议**:
- `feature/{功能名称}` - 新功能
- `fix/{问题描述}` - bug修复
- `refactor/{重构内容}` - 代码重构
- `docs/{文档内容}` - 文档更新

---

### 2.3 batch_commit（解决大量未提交）

**方案标题**: 分批提交修改

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `git status` | 查看所有修改 | 🟢 低 | 否 |
| 2 | `git add -p {file}` | 交互式添加修改 | 🟢 低 | 是 |
| 3 | `git commit -m "{message}"` | 提交 | 🟢 低 | 是 |

**最佳实践说明**:

1. **原子提交**
   - 每个提交只做一件事
   - 便于代码审查
   - 便于回滚

2. **提交信息规范**
   - 使用 Conventional Commits
   - `feat:` 新功能
   - `fix:` bug修复
   - `refactor:` 重构
   - `docs:` 文档
   - `test:` 测试
   - `chore:` 构建/工具

**提交分组建议**:
```
第一组: 核心功能修改
  git add src/core/
  git commit -m "feat(core): add authentication"

第二组: 测试文件
  git add tests/
  git commit -m "test: add auth tests"

第三组: 文档更新
  git add docs/
  git commit -m "docs: update auth guide"
```

---

### 2.4 setup_branch_protection（解决无分支保护）

**方案标题**: 配置分支保护规则

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `gh api repos/{owner}/{repo}/branches/main/protection` | 设置保护规则 | 🟡 中 | 是 |

**推荐的保护规则**:
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci/test", "ci/lint"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "restrictions": null
}
```

**最佳实践说明**:

1. **强制代码审查**
   - 所有修改必须经过审查
   - 提高代码质量
   - 知识共享

2. **CI检查**
   - 测试必须通过
   - Lint必须通过
   - 防止引入明显问题

---

### 2.5 fix_ci_failure（解决CI失败）

**方案标题**: 修复CI失败

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `gh run view --log` | 查看CI日志 | 🟢 低 | 否 |
| 2 | `gh run view --log-failed` | 查看失败日志 | 🟢 低 | 否 |

**常见CI问题及修复**:

| 问题 | 原因 | 修复方式 |
|------|------|---------|
| 测试失败 | 代码逻辑错误 | 修复测试或代码 |
| Lint失败 | 代码风格问题 | 运行 `npm run lint --fix` |
| 构建失败 | 依赖或配置问题 | 检查依赖安装 |
| 超时 | 测试太慢 | 优化测试或增加超时 |

---

### 2.6 resolve_conflicts（解决合并冲突）

**方案标题**: 解决合并冲突

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `git status` | 查看冲突文件 | 🟢 低 | 否 |
| 2 | 手动编辑 | 解决冲突 | 🟡 中 | 是 |
| 3 | `git add {file}` | 标记已解决 | 🟢 低 | 否 |
| 4 | `git rebase --continue` 或 `git commit` | 继续操作 | 🟢 低 | 否 |

**冲突解决指导**:
```markdown
打开冲突文件，你会看到：

```
<<<<<<< HEAD
本地版本代码
=======
远程版本代码
>>>>>>> origin/main
```

解决方式：
1. 删除冲突标记（<<<<<<<, =======, >>>>>>>）
2. 保留你想要的代码（可以是本地、远程或合并两者）
3. 保存文件
4. 运行 `git add {file}`
```

---

### 2.7 pull_with_rebase（解决落后远程）

**方案标题**: 使用 rebase 拉取远程更新

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `git stash` | 备份当前工作 | 🟢 低 | 否 |
| 2 | `git pull --rebase origin main` | 变基拉取 | 🟡 中 | 是 |
| 3 | `git stash pop` | 恢复工作 | 🟢 低 | 否 |

---

### 2.8 create_pr_template（解决缺少PR模板）

**方案标题**: 创建PR模板

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `mkdir -p .github` | 创建目录 | 🟢 低 | 否 |
| 2 | 创建文件 | 写入模板 | 🟢 低 | 是 |

**推荐PR模板**:
```markdown
## 变更描述
<!-- 描述这个PR做了什么 -->

## 变更类型
- [ ] 新功能 (feat)
- [ ] Bug修复 (fix)
- [ ] 重构 (refactor)
- [ ] 文档 (docs)
- [ ] 测试 (test)

## 测试
- [ ] 已添加单元测试
- [ ] 已添加集成测试
- [ ] 手动测试通过

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 已更新相关文档
- [ ] 无新的警告或错误
```

---

## 三、方案输出格式

```json
{
  "solutions": [
    {
      "id": "sol-001",
      "problem_id": "prob-001",
      "template_id": "git_rebase",
      "title": "使用 git rebase 变基合并",
      "steps": [...],
      "best_practice_reason": "...",
      "risk_level": "medium",
      "risk_factors": [...],
      "rollback_plan": "...",
      "prerequisites": [...],
      "prerequisites_met": true
    }
  ],
  "execution_order": ["sol-001", "sol-002"],
  "total_steps": 8,
  "estimated_duration": "2-5 minutes"
}
```

---

**模块版本**: 1.0.0
