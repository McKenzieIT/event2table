# Analyzer 分析器模块

问题识别规则库，用于分析GitHub状态并识别问题。

---

## 一、问题识别规则库

按优先级顺序应用以下规则，**发现第一个匹配即停止该类型检查**：

### P0 - 高优先级问题（阻塞流程）

**RULE-001: 分支分叉 (BRANCH_DIVERGED)**
```yaml
条件: local_state.diverged == True
严重性: 🔴 HIGH
描述模板: "本地 {branch} 分支与远程分支已分叉，本地有 {local_commits} 个提交，远程有 {remote_commits} 个不同的提交"
根因模板: "直接在 {branch} 分支上开发，或其他协作者推送了新提交"
影响:
  - 无法直接push到远程
  - 可能导致合并冲突
  - 违反分支保护最佳实践
```

**RULE-002: 在main分支直接开发 (MAIN_BRANCH_DEV)**
```yaml
条件: local_state.current_branch == "main" AND local_state.is_clean == False
严重性: 🔴 HIGH
描述模板: "在 main 分支上直接开发，有 {count} 个未提交修改"
根因模板: "未遵循分支策略，直接在受保护分支上开发"
影响:
  - 违反分支保护最佳实践
  - main分支可能变得不稳定
  - 无法进行代码审查
```

**RULE-003: 无分支保护 (NO_BRANCH_PROTECTION)**
```yaml
条件: remote_state.branch_protection.enabled == False
严重性: 🔴 HIGH
描述模板: "main 分支未配置保护规则"
根因模板: "项目初始化时未配置分支保护"
影响:
  - 任何人可直接推送到main
  - 无法强制代码审查
  - 增加代码质量风险
```

### P1 - 中优先级问题（影响效率）

**RULE-004: 大量未提交文件 (UNCOMMITTED_CHANGES)**
```yaml
条件: len(local_state.uncommitted_files) > 10
严重性: 🟡 MEDIUM
描述模板: "工作区有 {count} 个未提交的文件修改"
根因模板: "开发过程中未及时提交，或正在进行大规模重构"
影响:
  - 代码变更难以追踪
  - 无法回滚到稳定状态
  - 增加代码丢失风险
```

**RULE-005: CI失败 (CI_FAILURE)**
```yaml
条件: remote_state.ci_status.status == "failure"
严重性: 🟡 MEDIUM
描述模板: "最近一次CI构建失败"
根因模板: "代码存在测试失败、lint错误或构建问题"
影响:
  - 无法部署到生产环境
  - 代码质量无法保证
```

**RULE-006: 合并冲突 (MERGE_CONFLICT)**
```yaml
条件: any(pr.merge_state_status == "DIRTY" for pr in remote_state.active_prs)
严重性: 🔴 HIGH
描述模板: "有 {count} 个PR存在合并冲突"
根因模板: "多个PR修改了同一文件"
影响:
  - 无法自动合并
  - 需要手动解决冲突
```

### P2 - 低优先级问题（最佳实践）

**RULE-007: 落后远程 (BEHIND_REMOTE)**
```yaml
条件: local_state.unpulled_commits > 5
严重性: 🟢 LOW
描述模板: "本地落后远程 {count} 个提交"
根因模板: "未及时同步远程更新"
影响:
  - 可能基于过时代码开发
  - 增加合并冲突风险
```

**RULE-008: 缺少PR模板 (NO_PR_TEMPLATE)**
```yaml
条件: project_config.has_pr_template == False
严重性: 🟢 LOW
描述模板: "项目缺少PR模板"
根因模板: "项目初始化时未创建"
影响:
  - PR描述不规范
  - 可能遗漏重要检查项
```

**RULE-009: 大型PR (LARGE_PR)**
```yaml
条件: any(pr.changed_files > 20 for pr in remote_state.active_prs)
严重性: 🟡 MEDIUM
描述模板: "有 {count} 个PR修改超过20个文件"
根因模板: "PR范围过大，应该拆分"
影响:
  - 代码审查困难
  - 增加引入bug风险
```

**RULE-010: 过期PR (STALE_PR)**
```yaml
条件: any(pr.last_updated > 30_days for pr in remote_state.active_prs)
严重性: 🟢 LOW
描述模板: "有 {count} 个PR超过30天未更新"
根因模板: "PR被遗忘或阻塞"
影响:
  - 代码可能过时
  - 阻塞其他开发工作
```

---

## 二、规则应用策略

### 2.1 互斥规则处理

以下规则互斥，优先应用更严重的：

| 规则A | 规则B | 优先 |
|-------|-------|------|
| RULE-001 (BRANCH_DIVERGED) | RULE-007 (BEHIND_REMOTE) | RULE-001 |
| RULE-002 (MAIN_BRANCH_DEV) | RULE-004 (UNCOMMITTED_CHANGES) | RULE-002 |

### 2.2 组合条件支持

```python
# 支持AND/OR组合
条件: (local_state.diverged == True) OR (local_state.unpushed_commits > 10)

# 支持嵌套条件
条件: {
  "AND": [
    {"field": "current_branch", "operator": "eq", "value": "main"},
    {"field": "is_clean", "operator": "eq", "value": False}
  ]
}
```

### 2.3 项目上下文参数

| 参数 | 用途 |
|------|------|
| `project.is_team_project` | 是否多人协作（影响严重性判断） |
| `project.has_ci` | 是否有CI配置（影响CI_FAILURE判断） |
| `project.branch_protection_enforced` | 是否强制分支保护 |

**上下文应用示例**:
```python
# 如果是团队项目，BEHIND_REMOTE严重性提升
if project.is_team_project and problem.type == "BEHIND_REMOTE":
    problem.severity = Severity.MEDIUM  # 从LOW提升到MEDIUM
```

---

## 三、分析输出格式

分析完成后，必须输出：

```json
{
  "analysis_time": "2026-03-22T10:30:05Z",
  "problems": [
    {
      "id": "prob-001",
      "rule_id": "RULE-001",
      "type": "BRANCH_DIVERGED",
      "severity": "high",
      "title": "分支分叉",
      "description": "本地 feature/auth 分支与远程分支已分叉...",
      "root_cause": "直接在 feature/auth 分支上开发...",
      "impact": ["无法直接push到远程", "可能导致合并冲突"]
    }
  ],
  "total_issues": 3,
  "by_severity": {"high": 1, "medium": 1, "low": 1},
  "analysis_errors": []
}
```

---

## 四、严重性评估

| 严重性 | 标识 | 处理优先级 | 用户提示 |
|--------|------|-----------|---------|
| HIGH | 🔴 | 立即处理 | "⚠️ 高优先级问题，建议立即处理" |
| MEDIUM | 🟡 | 尽快处理 | "📋 中优先级问题，建议今天处理" |
| LOW | 🟢 | 可延后 | "💡 低优先级问题，可稍后优化" |

---

**模块版本**: 1.0.0
