# Reporter 报告器模块

报告生成模板，提供结构化和教育性的输出。

---

## 一、报告生成原则

1. **结构化** - 使用表格、列表、代码块，便于阅读
2. **可视化** - 使用emoji标识状态和严重性
3. **教育性** - 解释WHY，而不仅仅是WHAT
4. **可操作** - 提供具体的命令和步骤

---

## 二、报告模式

### 2.1 摘要模式（默认）

仅显示问题列表和关键建议，适合快速查看。

**长度**: ~50行

```markdown
# GitHub管理报告

**生成时间**: 2026-03-22 10:30
**项目**: event2table

## 状态概览

| 项目 | 状态 |
|------|------|
| 当前分支 | `feature/auth` ✅ |
| 工作区 | 8个未提交文件 ⚠️ |
| 远程同步 | 领先2个提交 |
| CI状态 | ✅ 通过 |

## 发现的问题 (2)

### 🔴 问题1: 分支分叉
本地feature/auth分支与远程已分叉

**建议**: 执行 `git rebase origin/feature/auth`

### 🟡 问题2: 大量未提交文件
工作区有8个未提交文件

**建议**: 分批提交修改

## 下一步

1. [ ] 解决分支分叉
2. [ ] 提交未提交文件
```

### 2.2 详细模式

包含完整的扫描结果、分析过程、解决方案。

**长度**: ~200行

### 2.3 教育模式

包含最佳实践解释和学习内容。

**长度**: ~300行

---

## 三、Markdown报告模板

```markdown
# GitHub管理报告

**生成时间**: {generated_at}
**项目**: {project_name}
**执行ID**: {execution_id}

---

## 1️⃣ GitHub状态扫描

### 1.1 本地状态

| 项目 | 状态 | 详情 |
|------|------|------|
| 当前分支 | `{current_branch}` | {branch_status} |
| 工作区状态 | {workspace_status_emoji} | {uncommitted_count} 个未提交文件 |
| 未推送提交 | {unpushed_commits} | 领先远程 {unpushed_commits} 个提交 |
| 分支状态 | {diverged_status_emoji} | {diverged_detail} |
| 暂存区 | {stash_count} 个暂存 | {stash_list} |

### 1.2 远程状态

| 项目 | 状态 | 详情 |
|------|------|------|
| 活跃PR | {active_prs} 个 | {pr_list} |
| CI状态 | {ci_status_emoji} | {ci_detail} |
| 分支保护 | {branch_protection_status_emoji} | {protection_detail} |

### 1.3 项目配置

| 项目 | 状态 |
|------|------|
| PR模板 | {has_pr_template} |
| CI配置 | {ci_configs} |
| CODEOWNERS | {has_codeowners} |

---

## 2️⃣ 发现的问题

**问题统计**: 共发现 {total_problems} 个问题
- 🔴 高优先级: {high_count} 个
- 🟡 中优先级: {medium_count} 个
- 🟢 低优先级: {low_count} 个

### 问题 #{problem_number}: {problem_title} {severity_emoji}

**问题描述**: {description}

**根本原因**: {root_cause}

**影响范围**: 
- {impact_1}
- {impact_2}

**建议优先级**: {priority}

---

## 3️⃣ 解决方案

### 方案 #{solution_number}: {solution_title}

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `git stash` | 备份当前工作 | 🟢 低 | 否 |
| 2 | `git fetch origin` | 获取远程更新 | 🟢 低 | 否 |
| 3 | `git rebase origin/main` | 变基到远程分支 | 🟡 中 | 是 |

**为什么是最佳实践**: 
{best_practice_reason}

**风险提示**: 
{risk_factors}

**回滚方案**: 
```bash
{rollback_commands}
```

**前提条件**:
- [ ] {prerequisite_1}
- [ ] {prerequisite_2}

---

## 4️⃣ 执行结果

| 操作 | 状态 | 耗时 | 备注 |
|------|------|------|------|
| git stash | ✅ 成功 | 0.5s | 已暂存8个文件 |
| git fetch origin | ✅ 成功 | 1.2s | 获取远程更新 |
| git rebase origin/main | ⚠️ 冲突 | - | 发现3个冲突文件 |

**执行统计**:
- 完成步骤: {completed_steps}/{total_steps}
- 失败步骤: {failed_steps}
- 总耗时: {total_duration}

---

## 5️⃣ 最佳实践学习

### {practice_title}

**规则**: {rule}

**为什么重要**: {importance}

**正确做法**:
```bash
{correct_approach}
```

**错误做法**:
```bash
{wrong_approach}
```

**相关资源**:
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 6️⃣ 下一步建议

- [ ] {next_step_1}
- [ ] {next_step_2}
- [ ] {next_step_3}

---

## 7️⃣ 历史对比

### 问题趋势

| 问题类型 | 上次 | 本次 | 变化 |
|---------|------|------|------|
| 分支分叉 | 2次 | 0次 | ✅ 改善 |
| 未提交文件 | 15个 | 8个 | ✅ 改善 |
| CI失败 | 1次 | 1次 | ➡️ 持平 |

### 持续改进

- 🎯 已连续{streak}次执行无高优先级问题
- 📈 问题总数从{prev_total}个减少到{curr_total}个
- ⏱️ 平均解决时间从{prev_time}减少到{curr_time}

---

**报告生成完成** ✅

**导出选项**:
- Markdown: `github-manager export --format md`
- JSON: `github-manager export --format json`
- HTML: `github-manager export --format html`
```

---

## 四、JSON数据结构

同时生成JSON格式数据，用于学习系统：

```json
{
  "report_meta": {
    "generated_at": "2026-03-22T10:40:00Z",
    "project_name": "event2table",
    "execution_id": "exec-001",
    "mode": "detailed"
  },
  "scan_results": {
    "local_state": {...},
    "remote_state": {...},
    "project_config": {...}
  },
  "problems_found": [
    {
      "id": "prob-001",
      "type": "BRANCH_DIVERGED",
      "severity": "high",
      "title": "分支分叉",
      "description": "...",
      "root_cause": "...",
      "impact": [...]
    }
  ],
  "solutions_proposed": [
    {
      "id": "sol-001",
      "template_id": "git_rebase",
      "title": "使用 git rebase 变基合并",
      "steps": [...],
      "best_practice_reason": "...",
      "risk_level": "medium"
    }
  ],
  "execution_results": {
    "status": "partial_success",
    "completed_steps": 4,
    "failed_steps": 1,
    "total_duration_ms": 45000
  },
  "learnings": {
    "patterns_discovered": [
      "用户偏好使用rebase解决分支分叉"
    ],
    "preferences_updated": {
      "preferred_solutions": {
        "BRANCH_DIVERGED": "git_rebase"
      }
    }
  },
  "history_comparison": {
    "previous_problems": 5,
    "current_problems": 2,
    "improvement": "60%"
  }
}
```

---

## 五、导出选项

### 5.1 Markdown导出

```bash
github-manager export --format md --output report.md
```

适合GitHub PR/Issue。

### 5.2 JSON导出

```bash
github-manager export --format json --output report.json
```

适合机器学习/自动化。

### 5.3 HTML导出

```bash
github-manager export --format html --output report.html
```

适合网页展示。

---

**模块版本**: 1.0.0
