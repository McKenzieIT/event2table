# GitHub Manager Skill & Agent 实施计划

**创建时间**: 2026-03-22
**基于设计**: 
- Plan B (模块化设计) → Skill实现
- Plan C (智能代理设计) → Agent实现
**状态**: 待执行

---

## 一、实施概述

### 1.1 双轨并行策略

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Manager 系统                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────┐  ┌─────────────────────────┐   │
│  │   Skill Layer (方案B)       │  │   Agent Layer (方案C)   │   │
│  │   github-manager skill      │  │   智能代理系统           │   │
│  │   ─────────────────────    │  │   ───────────────────    │   │
│  │   • 单文件SKILL.md          │  │   • 多代理协作           │   │
│  │   • references/模块         │  │   • 状态机驱动           │   │
│  │   • 规则驱动                │  │   • 决策引擎             │   │
│  │   • 快速响应                │  │   • 深度学习             │   │
│  │   • 适合日常操作            │  │   • 适合复杂场景         │   │
│  └─────────────────────────────┘  └─────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 实施优先级

| 优先级 | 目标 | 原因 |
|--------|------|------|
| **P0** | Skill (方案B) | 快速上线，覆盖80%日常场景 |
| **P1** | Agent (方案C) | 深度智能，处理复杂场景 |

### 1.3 实施阶段

```
Phase 1: Skill核心模块 (P0)
    ├── 1.1 Scanner模块
    ├── 1.2 Analyzer模块
    ├── 1.3 Solver模块
    └── 1.4 Executor模块

Phase 2: Skill辅助系统 (P0)
    ├── 2.1 Reporter模块
    └── 2.2 Learner模块

Phase 3: Agent智能代理 (P1)
    ├── 3.1 状态机框架
    ├── 3.2 决策引擎
    ├── 3.3 多代理协作
    └── 3.4 共享知识库

Phase 4: 集成与优化 (P1)
    ├── 4.1 Skill-Agent协同
    ├── 4.2 测试覆盖
    └── 4.3 文档完善
```

---

## 二、Phase 1: Skill核心模块实施

### 2.1 文件结构规划

```
.claude/skills/github-manager/
├── SKILL.md                    # 主技能文件 (~500行)
└── references/
    ├── scanner.md              # 扫描器模块 (~200行)
    ├── analyzer.md             # 分析器模块 (~300行)
    ├── solver.md               # 解决器模块 (~400行)
    ├── executor.md             # 执行器模块 (~300行)
    ├── reporter.md             # 报告器模块 (~150行)
    └── learner.md              # 学习器模块 (~200行)
```

### 2.2 SKILL.md 主文件设计

#### 2.2.1 Prompt设计反思

**问题1: 如何让Skill准确触发？**

❌ **差的prompt**:
```yaml
description: GitHub管理工具，帮助用户管理GitHub项目
```
问题：太笼统，容易误触发或漏触发

✅ **优化后的prompt**:
```yaml
description: |
  智能GitHub项目管理助手，自动扫描、分析、解决GitHub相关问题。
  
  触发条件（满足任一即触发）：
  - 用户提到 "github"、"git"、"分支"、"PR"、"pull request"、"合并"、"冲突"
  - 用户遇到git操作问题（如push失败、merge冲突、分支分叉）
  - 用户需要创建分支、提交代码、创建PR
  - 用户询问GitHub最佳实践
  - 用户想要检查项目GitHub状态
  - 用户说 "检查github"、"管理分支"、"解决冲突"
  
  不触发条件：
  - 仅提到代码内容，未涉及git/github操作
  - 纯粹的代码逻辑讨论
```

**优化点**:
1. 明确的触发条件列表
2. 包含中英文关键词
3. 明确不触发场景，避免误触发

---

**问题2: 如何让Skill输出规范化？**

❌ **差的prompt**:
```markdown
## 输出格式

请按照以下格式输出：
1. 扫描结果
2. 发现的问题
3. 解决方案
```
问题：格式描述太模糊，LLM输出不一致

✅ **优化后的prompt**:
```markdown
## 输出格式规范

### 必须输出的章节（按顺序）

**1. GitHub状态扫描** （必须包含表格）
```markdown
| 项目 | 状态 | 详情 |
|------|------|------|
| 当前分支 | `{branch_name}` | {status} |
| 工作区状态 | {clean/dirty} | {file_count} 个未提交文件 |
| 远程同步 | {ahead/behind/uptodate} | {commit_count} 个提交差异 |
```

**2. 发现的问题** （使用emoji标识严重性）
```markdown
### 问题 #1: {problem_title} {🔴/🟡/🟢}

**问题描述**: {description}
**根本原因**: {root_cause}
**影响范围**: {impact}
```

**3. 解决方案** （包含步骤表格）
```markdown
### 方案: {solution_title}

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `git stash` | 备份当前工作 | 🟢 低 | 否 |
```

**4. 最佳实践说明** （必须解释WHY）
```markdown
**为什么是最佳实践**:
1. {reason_1}
2. {reason_2}
```
```

**优化点**:
1. 提供具体的Markdown模板
2. 明确每个章节的必需元素
3. 使用表格格式强制结构化

---

#### 2.2.2 SKILL.md 完整结构

```markdown
# GitHub Manager Skill

name: github-manager
description: |
  [见2.2.1优化后的prompt]

---

## 一、核心工作流程

当用户触发此skill时，按以下顺序执行：

### Step 1: 扫描GitHub状态

调用references/scanner.md中的扫描流程：

1. **本地扫描**（5秒内完成）
   - `git status --porcelain` → 工作区状态
   - `git branch -vv` → 分支状态
   - `git log --oneline -5` → 最近提交
   - `git stash list` → 暂存区

2. **远程扫描**（30秒内完成）
   - `git fetch origin --dry-run` → 远程更新
   - `gh pr list --state all --limit 10` → PR状态
   - `gh run list --limit 3` → CI状态

3. **配置扫描**（5秒内完成）
   - 检查 `.github/pull_request_template.md`
   - 检查 `.github/workflows/` CI配置
   - 检查 `.github/CODEOWNERS`

### Step 2: 分析问题

调用references/analyzer.md中的问题规则：

应用问题识别规则（按优先级排序）：
1. 🔴 HIGH: BRANCH_DIVERGED, MAIN_BRANCH_DEV, NO_BRANCH_PROTECTION
2. 🟡 MEDIUM: UNCOMMITTED_CHANGES, CI_FAILURE, MERGE_CONFLICT
3. 🟢 LOW: NO_PR_TEMPLATE, BEHIND_REMOTE

### Step 3: 设计解决方案

调用references/solver.md中的解决方案模板：

为每个问题匹配最佳解决方案：
- 优先选择符合GitHub最佳实践的方案
- 评估风险等级
- 准备回滚计划

### Step 4: 用户确认与执行

调用references/executor.md中的执行策略：

风险分级执行：
- 🟢 低风险：自动执行（只读操作）
- 🟡 中风险：方案确认后自动执行
- 🔴 高风险：每步确认

---

## 二、输出规范

[见2.2.2优化后的输出格式]

---

## 三、学习机制

每次执行后：
1. 记录执行历史到 `.github/skill-data/github-manager/history/`
2. 更新模式识别到 `.github/skill-data/github-manager/patterns/`
3. 优化后续建议

---

## 四、参考模块

- [扫描器模块](references/scanner.md)
- [分析器模块](references/analyzer.md)
- [解决器模块](references/solver.md)
- [执行器模块](references/executor.md)
- [报告器模块](references/reporter.md)
- [学习器模块](references/learner.md)
```

---

### 2.3 Scanner模块实施

#### 2.3.1 Prompt设计反思

**问题: 如何确保扫描结果结构化？**

❌ **差的prompt**:
```markdown
扫描GitHub状态，返回本地和远程信息。
```

✅ **优化后的prompt**:
```markdown
# Scanner 扫描器模块

## 扫描流程

### 1. 本地扫描（必须按顺序执行）

**命令1**: `git status --porcelain`
- 用途: 检查未提交文件
- 输出解析: 每行格式为 `{XY} {path}`
  - `M` = 修改, `A` = 新增, `D` = 删除, `??` = 未跟踪
- 存储到: `local_state.uncommitted_files`

**命令2**: `git branch -vv`
- 用途: 检查分支状态
- 输出解析: 
  - `*` 标记当前分支
  - `[origin/xxx]` 显示远程跟踪
  - `ahead N` / `behind N` 显示提交差异
- 存储到: `local_state.current_branch`, `local_state.diverged`

**命令3**: `git rev-list --left-right --count origin/main...HEAD`
- 用途: 精确计算分叉状态
- 输出解析: 返回 `N M` 格式
  - N = 本地领先提交数
  - M = 远程领先提交数
- 存储到: `local_state.unpushed_commits`, `local_state.unpulled_commits`

### 2. 远程扫描（必须有网络）

**命令1**: `gh pr list --state all --limit 10 --json number,title,state,author,headRefName,baseRefName`
- 用途: 获取PR列表
- 输出解析: JSON格式，直接解析
- 存储到: `remote_state.active_prs`

**命令2**: `gh run list --limit 3 --json conclusion,status,name,createdAt`
- 用途: 获取CI状态
- 输出解析: 检查 `conclusion` 字段
- 存储到: `remote_state.ci_status`

### 3. 扫描结果数据结构

扫描完成后，必须输出以下JSON结构：

```json
{
  "scan_time": "2026-03-22T10:30:00Z",
  "local_state": {
    "current_branch": "feature/xxx",
    "is_clean": false,
    "uncommitted_files": [
      {"path": "src/file.ts", "status": "M"}
    ],
    "unpushed_commits": 2,
    "unpulled_commits": 0,
    "diverged": false
  },
  "remote_state": {
    "active_prs": [...],
    "ci_status": {
      "status": "success",
      "last_run": "2026-03-22T10:00:00Z"
    },
    "branch_protection": {
      "enabled": true
    }
  },
  "has_issues": true
}
```
```

**优化点**:
1. 明确每个命令的用途和输出解析方式
2. 定义数据结构，确保后续模块可以依赖
3. 按优先级排序，先本地后远程

---

### 2.4 Analyzer模块实施

#### 2.4.1 Prompt设计反思

**问题: 如何让问题识别准确且不遗漏？**

❌ **差的prompt**:
```markdown
分析扫描结果，识别问题。
```

✅ **优化后的prompt**:
```markdown
# Analyzer 分析器模块

## 问题识别规则库

按优先级顺序应用以下规则，**发现第一个匹配即停止该类型检查**：

### P0 - 高优先级问题（阻塞流程）

**RULE-001: 分支分叉**
```python
条件: local_state.diverged == True
严重性: 🔴 HIGH
描述模板: "本地 {branch} 分支与远程分支已分叉，本地有 {local_commits} 个提交，远程有 {remote_commits} 个不同的提交"
根因模板: "直接在 {branch} 分支上开发，或其他协作者推送了新提交"
影响: ["无法直接push到远程", "可能导致合并冲突", "违反分支保护最佳实践"]
```

**RULE-002: 在main分支直接开发**
```python
条件: local_state.current_branch == "main" AND local_state.is_clean == False
严重性: 🔴 HIGH
描述模板: "在 main 分支上直接开发，有 {count} 个未提交修改"
根因模板: "未遵循分支策略，直接在受保护分支上开发"
影响: ["违反分支保护最佳实践", "main分支可能变得不稳定", "无法进行代码审查"]
```

**RULE-003: 无分支保护**
```python
条件: remote_state.branch_protection.enabled == False
严重性: 🔴 HIGH
描述模板: "main 分支未配置保护规则"
根因模板: "项目初始化时未配置分支保护"
影响: ["任何人可直接推送到main", "无法强制代码审查", "增加代码质量风险"]
```

### P1 - 中优先级问题（影响效率）

**RULE-004: 大量未提交文件**
```python
条件: len(local_state.uncommitted_files) > 10
严重性: 🟡 MEDIUM
描述模板: "工作区有 {count} 个未提交的文件修改"
根因模板: "开发过程中未及时提交，或正在进行大规模重构"
影响: ["代码变更难以追踪", "无法回滚到稳定状态", "增加代码丢失风险"]
```

**RULE-005: CI失败**
```python
条件: remote_state.ci_status.status == "failure"
严重性: 🟡 MEDIUM
描述模板: "最近一次CI构建失败"
根因模板: "代码存在测试失败、lint错误或构建问题"
影响: ["无法部署到生产环境", "代码质量无法保证"]
```

**RULE-006: 合并冲突**
```python
条件: any(pr.merge_state_status == "DIRTY" for pr in remote_state.active_prs)
严重性: 🔴 HIGH
描述模板: "有 {count} 个PR存在合并冲突"
根因模板: "多个PR修改了同一文件"
影响: ["无法自动合并", "需要手动解决冲突"]
```

### P2 - 低优先级问题（最佳实践）

**RULE-007: 落后远程**
```python
条件: local_state.unpulled_commits > 5
严重性: 🟢 LOW
描述模板: "本地落后远程 {count} 个提交"
根因模板: "未及时同步远程更新"
影响: ["可能基于过时代码开发", "增加合并冲突风险"]
```

**RULE-008: 缺少PR模板**
```python
条件: project_config.has_pr_template == False
严重性: 🟢 LOW
描述模板: "项目缺少PR模板"
根因模板: "项目初始化时未创建"
影响: ["PR描述不规范", "可能遗漏重要检查项"]
```

## 分析输出格式

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
      "description": "...",
      "root_cause": "...",
      "impact": [...]
    }
  ],
  "total_issues": 3,
  "by_severity": {"high": 1, "medium": 1, "low": 1}
}
```
```

**优化点**:
1. 规则按优先级排序，高优先级先检查
2. 每个规则有明确的条件、模板、影响
3. 输出结构化，便于后续模块处理

---

### 2.5 Solver模块实施

#### 2.5.1 Prompt设计反思

**问题: 如何让解决方案符合最佳实践且易于理解？**

❌ **差的prompt**:
```markdown
为每个问题提供解决方案。
```

✅ **优化后的prompt**:
```markdown
# Solver 解决器模块

## 解决方案匹配流程

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

### Step 2: 方案详细设计

每个解决方案必须包含以下部分：

#### 模板示例：git_rebase（解决分支分叉）

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

**回滚计划**:
```bash
# 如果rebase过程中出现问题
git rebase --abort  # 取消变基操作，恢复到rebase前状态

# 如果rebase完成但想撤销
git reset --hard ORIG_HEAD  # 回到rebase前的HEAD
```

### Step 3: 方案输出格式

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
      "rollback_plan": "..."
    }
  ],
  "execution_order": ["sol-001", "sol-002"],
  "total_steps": 8,
  "estimated_duration": "2-5 minutes"
}
```
```

**优化点**:
1. 问题类型与解决方案的明确映射
2. 每个步骤有风险等级、确认需求、回滚方案
3. 最佳实践说明解释WHY，而不仅仅是WHAT
4. 提供具体的回滚命令

---

### 2.6 Executor模块实施

#### 2.6.1 Prompt设计反思

**问题: 如何确保执行安全且用户可控？**

❌ **差的prompt**:
```markdown
执行解决方案，处理错误。
```

✅ **优化后的prompt**:
```markdown
# Executor 执行器模块

## 执行策略（风险分级）

### 🟢 低风险操作 - 自动执行

**条件**: 风险等级 = LOW 且 命令是只读的

**自动执行的命令**:
- `git status`, `git log`, `git branch`, `git remote`
- `git stash list`, `git fetch --dry-run`
- `gh pr list`, `gh repo view`, `gh run list`

**执行方式**:
1. 直接执行，无需用户确认
2. 超时设置: 30秒
3. 失败重试: 最多3次，间隔5秒

### 🟡 中风险操作 - 方案确认后自动执行

**条件**: 风险等级 = MEDIUM 且 用户已确认整个方案

**需要方案确认的命令**:
- `git stash`, `git stash pop`
- `git pull`, `git pull --rebase`, `git push`
- `git checkout`, `git checkout -b`
- `git add`, `git commit`
- `git rebase`, `git merge`

**执行方式**:
1. 展示完整方案，请求用户确认
2. 用户确认后，自动执行所有步骤
3. 每步执行后显示结果
4. 超时设置: 60秒
5. 失败重试: 最多2次

### 🔴 高风险操作 - 每步确认

**条件**: 风险等级 = HIGH 或 涉及破坏性操作

**需要每步确认的命令**:
- `git push --force`, `git push --force-with-lease`
- `git reset --hard`, `git reset --soft`
- `git branch -D`
- `git clean -fd`
- 合并冲突解决

**执行方式**:
1. 每步执行前展示命令和风险警告
2. 等待用户明确确认（"继续"/"y"/"yes"）
3. 用户可随时中止
4. 超时设置: 120秒
5. 不自动重试，失败后询问用户

## 错误处理策略

### 错误类型与处理方式

| 错误类型 | 处理策略 | 用户提示 |
|---------|---------|---------|
| NETWORK_ERROR | 自动重试3次 | "网络连接失败，正在重试..." |
| PERMISSION_DENIED | 中止执行 | "权限不足，请检查GitHub token或SSH密钥配置" |
| MERGE_CONFLICT | 询问用户 | "发现合并冲突，请选择处理方式" |
| TIMEOUT | 询问用户 | "操作超时，请选择：重试/跳过/中止" |
| USER_ABORT | 回滚 | "用户中止操作，正在回滚..." |
| COMMAND_FAILED | 根据严重性决定 | "命令执行失败：{error}" |

### 冲突处理流程

当检测到合并冲突时：

1. **显示冲突文件列表**
```markdown
发现合并冲突，以下文件需要手动解决：
- src/file1.ts (content conflict)
- src/file2.ts (modify/delete conflict)
```

2. **提供处理选项**
```markdown
请选择处理方式：
A. 手动解决冲突（推荐）- 我会指导你逐个文件解决
B. 使用我们的版本 - 保留本地修改
C. 使用他们的版本 - 使用远程版本
D. 中止操作 - 执行回滚
```

3. **手动解决指导**
```markdown
打开冲突文件 `src/file1.ts`，你会看到：

```
<<<<<<< HEAD
本地版本代码
=======
远程版本代码
>>>>>>> origin/main
```

解决方式：
1. 删除冲突标记（<<<<<<<, =======, >>>>>>>）
2. 保留你想要的代码
3. 保存文件
4. 运行 `git add src/file1.ts`
```

## 执行输出格式

```json
{
  "execution_id": "exec-001",
  "plan_id": "plan-001",
  "start_time": "2026-03-22T10:35:00Z",
  "end_time": "2026-03-22T10:36:30Z",
  "status": "success",
  "step_results": [
    {
      "step_id": "step-001",
      "command": "git stash",
      "status": "success",
      "output": "Saved working directory and index state...",
      "duration_ms": 500
    }
  ],
  "completed_steps": 4,
  "failed_steps": 0,
  "rollback_available": true,
  "rollback_commands": ["git stash pop"]
}
```
```

**优化点**:
1. 明确的风险分级执行策略
2. 每种错误类型有对应的处理方式
3. 冲突处理提供多种选项
4. 输出格式包含回滚信息

---

## 三、Phase 2: Skill辅助系统实施

### 3.1 Reporter模块实施

#### 3.1.1 Prompt设计反思

**问题: 如何让报告既规范又有教育意义？**

❌ **差的prompt**:
```markdown
生成报告，包含扫描结果和解决方案。
```

✅ **优化后的prompt**:
```markdown
# Reporter 报告器模块

## 报告生成原则

1. **结构化** - 使用表格、列表、代码块，便于阅读
2. **可视化** - 使用emoji标识状态和严重性
3. **教育性** - 解释WHY，而不仅仅是WHAT
4. **可操作** - 提供具体的命令和步骤

## Markdown报告模板

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

### 1.2 远程状态

| 项目 | 状态 | 详情 |
|------|------|------|
| 活跃PR | {active_prs} 个 | {pr_list} |
| CI状态 | {ci_status_emoji} | {ci_detail} |
| 分支保护 | {branch_protection_status_emoji} | {protection_detail} |

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

---

## 4️⃣ 执行结果

| 操作 | 状态 | 耗时 | 备注 |
|------|------|------|------|
| git stash | ✅ 成功 | 0.5s | 已暂存34个文件 |
| git fetch origin | ✅ 成功 | 1.2s | 获取远程更新 |
| git rebase origin/main | ⚠️ 冲突 | - | 发现3个冲突文件 |

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

---

## 6️⃣ 下一步建议

- [ ] {next_step_1}
- [ ] {next_step_2}
- [ ] {next_step_3}

---

**报告生成完成** ✅
```

## JSON数据结构（用于学习系统）

同时生成JSON格式数据：

```json
{
  "report_meta": {
    "generated_at": "2026-03-22T10:40:00Z",
    "project_name": "event2table",
    "execution_id": "exec-001"
  },
  "scan_results": {...},
  "problems_found": [...],
  "solutions_proposed": [...],
  "execution_results": {...},
  "learnings": {
    "patterns_discovered": [...],
    "preferences_updated": {...}
  }
}
```
```

**优化点**:
1. 提供完整的Markdown模板
2. 同时生成JSON用于机器学习
3. 包含教育性的最佳实践章节

---

### 3.2 Learner模块实施

#### 3.2.1 Prompt设计反思

**问题: 如何让学习系统真正有效？**

❌ **差的prompt**:
```markdown
记录执行历史，学习用户偏好。
```

✅ **优化后的prompt**:
```markdown
# Learner 学习器模块

## 学习数据存储结构

```
.github/skill-data/github-manager/
├── history/                          # 历史记录
│   ├── 2026-03/
│   │   ├── 2026-03-22-001.json      # 每次执行记录
│   │   └── summary.json              # 月度汇总
│
├── patterns/                         # 模式识别
│   ├── project-patterns.json         # 项目特定模式
│   ├── common-problems.json          # 常见问题库
│   └── solution-effectiveness.json   # 方案有效性
│
├── preferences/                      # 用户偏好
│   ├── user-preferences.json         # 用户偏好设置
│   └── confirmation-history.json     # 确认历史
│
└── learnings/                        # 学习成果
    ├── best-practices.json           # 最佳实践积累
    └── failure-patterns.json         # 失败模式
```

## 学习维度

### 1. 项目模式学习

**学习内容**:
- 常用分支命名模式（feature/*, fix/*, refactor/*）
- 提交信息风格（conventional commits）
- 工作流习惯（何时创建PR，何时合并）

**应用场景**:
```json
{
  "project_patterns": {
    "branch_naming": {
      "patterns": ["feature/*", "fix/*", "refactor/*"],
      "most_used": "feature/*",
      "usage_count": {"feature": 15, "fix": 5, "refactor": 3}
    },
    "commit_style": {
      "style": "conventional_commits",
      "examples": ["feat: add new feature", "fix: resolve bug"],
      "confidence": 0.95
    }
  }
}
```

### 2. 问题频率学习

**学习内容**:
- 哪些问题经常出现
- 问题出现的条件
- 问题的关联性

**应用场景**:
```json
{
  "common_problems": {
    "BRANCH_DIVERGED": {
      "frequency": 0.3,
      "conditions": ["working_on_feature_branch", "multiple_contributors"],
      "related_problems": ["MERGE_CONFLICT"]
    },
    "UNCOMMITTED_CHANGES": {
      "frequency": 0.5,
      "conditions": ["active_development"],
      "avg_file_count": 15
    }
  }
}
```

### 3. 方案有效性学习

**学习内容**:
- 哪些解决方案效果最好
- 用户偏好哪种方案
- 方案的成功率

**应用场景**:
```json
{
  "solution_effectiveness": {
    "git_rebase": {
      "success_rate": 0.85,
      "user_preference": 0.7,
      "avg_duration_seconds": 30,
      "common_issues": ["conflict_resolution_needed"]
    },
    "git_merge": {
      "success_rate": 0.95,
      "user_preference": 0.3,
      "avg_duration_seconds": 45,
      "common_issues": ["merge_commit_created"]
    }
  }
}
```

### 4. 用户偏好学习

**学习内容**:
- 自动化程度偏好
- 确认频率偏好
- 报告格式偏好

**应用场景**:
```json
{
  "user_preferences": {
    "automation_level": "semi_auto",
    "confirmation_frequency": "medium_risk_only",
    "report_format": "detailed",
    "preferred_solutions": {
      "BRANCH_DIVERGED": "git_rebase",
      "UNCOMMITTED_CHANGES": "batch_commit"
    }
  }
}
```

## 学习应用

### 每次执行后

1. **记录历史**
   - 保存执行详情到 `history/YYYY-MM/YYYY-MM-DD-NNN.json`
   - 更新月度汇总 `summary.json`

2. **更新模式**
   - 更新分支命名统计
   - 更新问题频率
   - 更新方案有效性

3. **优化建议**
   - 基于历史推荐常用分支名
   - 基于有效性优先推荐高效方案
   - 基于偏好调整自动化程度

### 学习输出示例

```markdown
## 学习成果

### 发现的模式
- 您经常使用 `feature/*` 分支命名（15次）
- 您偏好使用 rebase 方式解决分支分叉（成功率85%）
- 您的提交信息遵循 Conventional Commits 规范（置信度95%）

### 优化建议
- 建议配置 git alias: `git config alias.rb 'rebase origin/main'`
- 建议添加 pre-commit hook 确保提交信息格式
- 建议配置分支保护规则避免直接推送到main

### 下次改进
- 自动推荐分支名: `feature/{issue-number}-{short-description}`
- 自动生成符合规范的提交信息
- 主动检测并预防常见问题
```
```

**优化点**:
1. 明确的学习维度和数据结构
2. 具体的学习应用场景
3. 可操作的优化建议

---

## 四、Phase 3: Agent智能代理实施

### 4.1 Agent与Skill的关系

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户请求                                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   路由决策             │
                    │   判断复杂度           │
                    └───────────────────────┘
                                │
            ┌───────────────────┴───────────────────┐
            │                                       │
            ▼                                       ▼
    ┌───────────────┐                     ┌───────────────┐
    │   简单场景     │                     │   复杂场景     │
    │   日常操作     │                     │   多问题交织   │
    │   单一问题     │                     │   需要深度分析 │
    └───────────────┘                     └───────────────┘
            │                                       │
            ▼                                       ▼
    ┌───────────────┐                     ┌───────────────┐
    │ github-manager│                     │ GitHub Agent  │
    │    Skill      │                     │  (方案C)      │
    │   (方案B)     │                     │               │
    │               │                     │ • 状态机驱动  │
    │ • 快速响应    │                     │ • 决策引擎    │
    │ • 规则匹配    │                     │ • 多代理协作  │
    │ • 自动执行    │                     │ • 深度学习    │
    └───────────────┘                     └───────────────┘
```

### 4.2 Agent实施计划

#### 4.2.1 状态机框架

**文件**: `.agents/github-manager/agents/orchestrator.py`

```python
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

class ManagerState(Enum):
    """管理器状态"""
    IDLE = "idle"
    SCANNING = "scanning"
    SCAN_COMPLETED = "scan_completed"
    ANALYZING = "analyzing"
    ANALYSIS_COMPLETED = "analysis_completed"
    RESOLVING = "resolving"
    RESOLUTION_COMPLETED = "resolution_completed"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONFIRMED = "confirmed"
    EXECUTING = "executing"
    EXECUTION_COMPLETED = "execution_completed"
    REPORTING = "reporting"
    LEARNING = "learning"
    COMPLETED = "completed"
    FAILED = "failed"


class StateMachine:
    """状态机"""
    
    def __init__(self):
        self.current_state = ManagerState.IDLE
        self.history: List[StateRecord] = []
        self.context: Dict[str, Any] = {}
    
    def transition(self, trigger: str, **kwargs) -> bool:
        """执行状态转换"""
        transition = self._find_transition(trigger)
        if not transition:
            return False
        
        # 记录历史
        self.history.append(StateRecord(
            from_state=self.current_state,
            to_state=transition['to_state'],
            trigger=trigger,
            timestamp=datetime.now()
        ))
        
        # 执行动作
        if transition.get('action'):
            result = transition['action'](**kwargs)
            self.context.update(result or {})
        
        # 更新状态
        self.current_state = transition['to_state']
        return True
    
    def _find_transition(self, trigger: str) -> Optional[Dict]:
        """查找匹配的转换"""
        TRANSITIONS = [
            {'from': ManagerState.IDLE, 'to': ManagerState.SCANNING, 'trigger': 'start_scan'},
            {'from': ManagerState.SCANNING, 'to': ManagerState.SCAN_COMPLETED, 'trigger': 'scan_success'},
            {'from': ManagerState.SCAN_COMPLETED, 'to': ManagerState.ANALYZING, 'trigger': 'start_analysis'},
            # ... 更多转换
        ]
        
        for t in TRANSITIONS:
            if t['from'] == self.current_state and t['trigger'] == trigger:
                return t
        return None
```

#### 4.2.2 决策引擎

**文件**: `.agents/github-manager/agents/decision_engine.py`

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DecisionRule:
    """决策规则"""
    rule_id: str
    name: str
    priority: int
    weight: float
    conditions: List[Dict]
    action: str
    parameters: Dict[str, Any]
    
    def matches(self, context: Dict) -> bool:
        """检查规则是否适用"""
        for condition in self.conditions:
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            field_value = context.get(field)
            if field_value is None:
                return False
            
            if operator == 'eq' and field_value != value:
                return False
            elif operator == 'gt' and field_value <= value:
                return False
            # ... 更多操作符
        
        return True


class DecisionEngine:
    """决策引擎"""
    
    def __init__(self):
        self.rules: List[DecisionRule] = []
        self.decision_history: List[Dict] = []
    
    def make_decision(self, context: Dict) -> Dict:
        """基于上下文做出决策"""
        # 收集适用的规则
        applicable_rules = [r for r in self.rules if r.matches(context)]
        
        # 按优先级和权重排序
        applicable_rules.sort(key=lambda r: (r.priority, r.weight), reverse=True)
        
        # 应用最高优先级规则
        if applicable_rules:
            rule = applicable_rules[0]
            return {
                'action': rule.action,
                'parameters': rule.parameters,
                'confidence': rule.weight,
                'rule_id': rule.rule_id
            }
        
        # 默认决策
        return {'action': 'ask_user', 'confidence': 0.0}
    
    def learn_from_outcome(self, decision_id: str, outcome: Dict):
        """从决策结果中学习"""
        # 找到决策
        decision = next((d for d in self.decision_history if d['id'] == decision_id), None)
        if not decision:
            return
        
        # 更新规则权重
        rule = next((r for r in self.rules if r.rule_id == decision['rule_id']), None)
        if rule:
            if outcome.get('is_positive'):
                rule.weight = min(1.0, rule.weight + 0.1)
            else:
                rule.weight = max(0.0, rule.weight - 0.1)
```

#### 4.2.3 多代理协作

**文件**: `.agents/github-manager/agents/base_agent.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    """代理基类"""
    
    def __init__(self, agent_id: str, knowledge_base: 'KnowledgeBase'):
        self.agent_id = agent_id
        self.knowledge_base = knowledge_base
        self.state: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, task: Dict) -> Dict:
        """执行任务"""
        pass
    
    def communicate(self, target_agent: str, message: Dict) -> Dict:
        """与其他代理通信"""
        return self.knowledge_base.route_message(self.agent_id, target_agent, message)
    
    def get_shared_knowledge(self, key: str) -> Any:
        """获取共享知识"""
        return self.knowledge_base.get(key)
```

**文件**: `.agents/github-manager/agents/scanner_agent.py`

```python
class ScannerAgent(BaseAgent):
    """扫描代理"""
    
    def execute(self, task: Dict) -> Dict:
        """执行扫描任务"""
        # 1. 本地扫描
        local_result = self._scan_local()
        
        # 2. 远程扫描
        remote_result = self._scan_remote()
        
        # 3. 配置扫描
        config_result = self._scan_config()
        
        # 4. 更新共享知识
        self.knowledge_base.set('scan_result', {
            'local': local_result,
            'remote': remote_result,
            'config': config_result
        })
        
        # 5. 通知分析代理
        self.communicate('analyzer', {'type': 'scan_completed'})
        
        return {'success': True, 'data': {...}}
```

#### 4.2.4 共享知识库

**文件**: `.agents/github-manager/agents/knowledge_base.py`

```python
from typing import Dict, Any, List
from datetime import datetime

class KnowledgeBase:
    """共享知识库"""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.message_queue: Dict[str, List[Dict]] = {}
        self.subscriptions: Dict[str, List[str]] = {}
    
    def set(self, key: str, value: Any):
        """设置知识"""
        self.data[key] = value
        self._notify_subscribers(key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取知识"""
        return self.data.get(key, default)
    
    def subscribe(self, agent_id: str, topic: str):
        """订阅主题"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(agent_id)
    
    def _notify_subscribers(self, topic: str, data: Any):
        """通知订阅者"""
        if topic not in self.subscriptions:
            return
        
        for agent_id in self.subscriptions[topic]:
            if agent_id not in self.message_queue:
                self.message_queue[agent_id] = []
            
            self.message_queue[agent_id].append({
                'type': 'knowledge_update',
                'topic': topic,
                'data': data,
                'timestamp': datetime.now()
            })
    
    def route_message(self, from_agent: str, to_agent: str, message: Dict) -> Dict:
        """路由消息"""
        if to_agent not in self.message_queue:
            self.message_queue[to_agent] = []
        
        message['from_agent'] = from_agent
        message['timestamp'] = datetime.now()
        
        self.message_queue[to_agent].append(message)
        return message
```

---

## 五、Phase 4: 集成与优化

### 5.1 Skill-Agent协同机制

```python
# .agents/github-manager/router.py

class RequestRouter:
    """请求路由器 - 决定使用Skill还是Agent"""
    
    def route(self, user_request: str) -> str:
        """
        根据请求复杂度决定处理方式
        
        Returns:
            'skill' - 使用github-manager skill
            'agent' - 使用GitHub Agent
        """
        complexity_score = self._calculate_complexity(user_request)
        
        if complexity_score < 0.3:
            return 'skill'  # 简单场景
        elif complexity_score > 0.7:
            return 'agent'  # 复杂场景
        else:
            return 'skill'  # 默认使用skill，更快响应
    
    def _calculate_complexity(self, request: str) -> float:
        """计算请求复杂度"""
        score = 0.0
        
        # 多问题关键词
        problem_keywords = ['冲突', '分叉', '失败', '落后', '保护']
        problem_count = sum(1 for kw in problem_keywords if kw in request)
        score += problem_count * 0.2
        
        # 需要深度分析的关键词
        deep_keywords = ['为什么', '最佳实践', '优化', '改进', '学习']
        if any(kw in request for kw in deep_keywords):
            score += 0.3
        
        # 需要多步骤的关键词
        multi_step_keywords = ['同时', '并且', '然后', '之后']
        if any(kw in request for kw in multi_step_keywords):
            score += 0.2
        
        return min(1.0, score)
```

### 5.2 测试计划

#### 5.2.1 Skill测试用例

| 测试场景 | 触发输入 | 预期行为 |
|---------|---------|---------|
| 分支分叉 | "我的分支分叉了" | 扫描→分析→建议rebase/merge |
| main分支开发 | "我在main上改了代码" | 警告→建议创建feature分支 |
| CI失败 | "CI失败了" | 查看日志→分析原因→建议修复 |
| 合并冲突 | "有冲突" | 列出冲突文件→提供解决选项 |

#### 5.2.2 Agent测试用例

| 测试场景 | 复杂度 | 预期代理协作 |
|---------|--------|-------------|
| 多问题交织 | 高 | Scanner→Analyzer→Resolver→Executor |
| 需要学习优化 | 高 | Executor→Reporter→Learner |
| 用户偏好学习 | 中 | 多次执行后更新preferences |

### 5.3 文档完善

| 文档 | 位置 | 内容 |
|------|------|------|
| Skill使用指南 | `docs/skills/github-manager-guide.md` | 触发方式、输出格式、最佳实践 |
| Agent架构文档 | `docs/agents/github-manager-architecture.md` | 状态机、决策引擎、多代理协作 |
| 开发者文档 | `docs/developers/github-manager-dev.md` | 如何扩展规则、添加解决方案 |

---

## 六、实施时间表

### 6.1 Phase 1: Skill核心模块

| 任务 | 预计时间 | 依赖 |
|------|---------|------|
| 创建SKILL.md主文件 | 2小时 | - |
| 实现Scanner模块 | 2小时 | SKILL.md |
| 实现Analyzer模块 | 3小时 | Scanner |
| 实现Solver模块 | 3小时 | Analyzer |
| 实现Executor模块 | 2小时 | Solver |
| **Phase 1 总计** | **12小时** | |

### 6.2 Phase 2: Skill辅助系统

| 任务 | 预计时间 | 依赖 |
|------|---------|------|
| 实现Reporter模块 | 2小时 | Phase 1 |
| 实现Learner模块 | 3小时 | Reporter |
| 创建数据存储结构 | 1小时 | - |
| **Phase 2 总计** | **6小时** | |

### 6.3 Phase 3: Agent智能代理

| 任务 | 预计时间 | 依赖 |
|------|---------|------|
| 实现状态机框架 | 3小时 | Phase 2 |
| 实现决策引擎 | 4小时 | 状态机 |
| 实现多代理协作 | 6小时 | 决策引擎 |
| 实现共享知识库 | 2小时 | 多代理 |
| **Phase 3 总计** | **15小时** | |

### 6.4 Phase 4: 集成与优化

| 任务 | 预计时间 | 依赖 |
|------|---------|------|
| Skill-Agent协同 | 2小时 | Phase 3 |
| 测试用例编写 | 4小时 | 协同机制 |
| 文档完善 | 3小时 | 测试完成 |
| **Phase 4 总计** | **9小时** | |

### 6.5 总计

| Phase | 时间 |
|-------|------|
| Phase 1: Skill核心 | 12小时 |
| Phase 2: Skill辅助 | 6小时 |
| Phase 3: Agent智能 | 15小时 |
| Phase 4: 集成优化 | 9小时 |
| **总计** | **42小时** |

---

## 七、验收标准

### 7.1 Skill验收标准

- [ ] 能准确识别10种问题类型
- [ ] 能提供符合最佳实践的解决方案
- [ ] 低风险操作自动执行，中/高风险需确认
- [ ] 输出格式规范，包含教育性内容
- [ ] 学习系统能记录历史并优化建议

### 7.2 Agent验收标准

- [ ] 状态机能正确处理所有状态转换
- [ ] 决策引擎能根据上下文做出合理决策
- [ ] 多代理能正确协作，共享知识
- [ ] 能处理复杂场景（多问题交织）
- [ ] 学习系统能持续优化

### 7.3 集成验收标准

- [ ] 路由器能正确区分简单/复杂场景
- [ ] Skill和Agent能共享学习数据
- [ ] 用户无感知切换Skill/Agent
- [ ] 整体响应时间<30秒

---

## 八、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Prompt不够准确 | 误触发或漏触发 | 多轮测试优化，添加更多触发条件 |
| 执行命令失败 | 用户体验差 | 完善错误处理，提供回滚方案 |
| 学习数据不准确 | 优化效果差 | 增加数据验证，定期清理无效数据 |
| Agent过于复杂 | 维护成本高 | 保持Skill为主，Agent仅处理复杂场景 |

---

## 九、Prompt质量深度反思

### 9.1 反思维度总览

| 维度 | 检查项 | Scanner | Analyzer | Solver | Executor | Reporter | Learner |
|------|--------|---------|----------|--------|----------|----------|---------|
| **触发准确性** | 是否能准确识别触发场景？ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **输出规范性** | 输出格式是否一致？ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **教育价值** | 是否解释WHY而非仅WHAT？ | ⚠️ | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| **错误处理** | 是否覆盖所有错误场景？ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ⚠️ |
| **可扩展性** | 是否易于添加新规则？ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ |

---

### 9.2 Scanner模块 - 深度反思

#### 当前设计的优点

- ✅ 明确的命令列表和输出解析方式
- ✅ 定义了数据结构
- ✅ 按优先级排序（本地→远程）

#### 潜在问题与改进

| 问题 | 影响 | 改进方案 |
|------|------|---------|
| **网络超时未处理** | 远程扫描可能卡住 | 添加超时设置和降级策略 |
| **大仓库扫描慢** | `git status`在大型仓库可能慢 | 添加性能优化提示 |
| **命令失败未降级** | 单个命令失败影响整体 | 添加部分成功处理 |

#### 改进后的Prompt片段

```markdown
### 远程扫描（必须有网络，超时30秒）

**降级策略**: 如果网络不可用或超时：
1. 跳过远程扫描
2. 在报告中标注"远程状态未知"
3. 仅基于本地状态提供建议

**命令执行规则**:
- 每个命令最多等待30秒
- 失败后不重试，继续下一个
- 记录失败原因到 `scan_errors`

**大仓库优化**:
- 使用 `git status --porcelain --untracked-files=no` 跳过未跟踪文件
- 使用 `git log --oneline -5 --no-walk` 加速提交历史
- 如果文件数>1000，提示用户可能需要等待
```

---

### 9.3 Analyzer模块 - 深度反思

#### 当前设计的优点

- ✅ 规则按优先级排序
- ✅ 每个规则有明确的条件、模板、影响
- ✅ 输出结构化

#### 潜在问题与改进

| 问题 | 影响 | 改进方案 |
|------|------|---------|
| **规则冲突未处理** | 多个规则可能同时匹配 | 添加规则互斥逻辑 |
| **条件过于简单** | 无法表达复杂条件 | 支持组合条件 |
| **缺少上下文** | 未考虑项目特定情况 | 添加项目上下文参数 |

#### 改进后的Prompt片段

```markdown
### 规则应用策略

**互斥规则处理**:
- RULE-001 (BRANCH_DIVERGED) 和 RULE-007 (BEHIND_REMOTE) 互斥
- 如果同时匹配，优先应用RULE-001（更严重）
- 规则优先级: HIGH > MEDIUM > LOW

**组合条件支持**:
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

**项目上下文参数**:
- `project.is_team_project`: 是否多人协作（影响问题严重性判断）
- `project.has_ci`: 是否有CI配置（影响CI_FAILURE判断）
- `project.branch_protection_enforced`: 是否强制分支保护（影响建议方式）

**上下文应用示例**:
```python
# 如果是团队项目，BEHIND_REMOTE严重性提升
if project.is_team_project and problem.type == "BEHIND_REMOTE":
    problem.severity = Severity.MEDIUM  # 从LOW提升到MEDIUM
```
```

---

### 9.4 Solver模块 - 深度反思

#### 当前设计的优点

- ✅ 问题类型与解决方案明确映射
- ✅ 每个步骤有风险等级、确认需求、回滚方案
- ✅ 最佳实践说明解释WHY

#### 潜在问题与改进

| 问题 | 影响 | 改进方案 |
|------|------|---------|
| **方案选择过于简单** | 未考虑用户偏好 | 添加方案选择逻辑 |
| **缺少前置检查** | 方案可能不适用 | 添加前提条件检查 |
| **回滚方案不够详细** | 用户可能不知道如何回滚 | 提供详细回滚步骤 |

#### 改进后的Prompt片段

```markdown
### 方案选择逻辑

**基于用户偏好选择**:
1. 检查 `user_preferences.preferred_solutions[problem_type]`
2. 如果用户有偏好，优先使用偏好方案
3. 否则使用默认首选方案

**偏好学习示例**:
```json
{
  "user_preferences": {
    "preferred_solutions": {
      "BRANCH_DIVERGED": "git_rebase",  // 用户偏好rebase
      "UNCOMMITTED_CHANGES": "batch_commit"  // 用户偏好分批提交
    }
  }
}
```

### 前提条件检查

每个方案执行前必须检查：

| 方案 | 前提条件 | 不满足时的处理 |
|------|---------|---------------|
| git_rebase | 工作区干净或已暂存 | 先执行 `git stash` |
| git_merge | 工作区干净或已暂存 | 先执行 `git stash` |
| create_feature_branch | 在main分支上有修改 | 直接执行 |
| setup_branch_protection | 有GitHub管理员权限 | 提示用户联系管理员 |
| fix_ci_failure | 有CI访问权限 | 提示用户检查CI配置 |

**前提条件检查流程**:
```python
def check_prerequisites(solution: Solution) -> CheckResult:
    """检查方案前提条件"""
    missing = []
    
    for prereq in solution.prerequisites:
        if not check_condition(prereq):
            missing.append(prereq)
    
    if missing:
        return CheckResult(
            can_proceed=False,
            missing_prerequisites=missing,
            suggested_actions=generate_preparation_steps(missing)
        )
    
    return CheckResult(can_proceed=True)
```

**或提示用户手动准备**:
```markdown
### 前提条件不满足

方案 "{solution_title}" 需要以下前提条件：

❌ {missing_prerequisite_1}
   → 请先执行: {preparation_command_1}

❌ {missing_prerequisite_2}
   → 请先执行: {preparation_command_2}

**选择处理方式**:
A. 自动准备 - 我会帮你执行上述准备步骤
B. 手动准备 - 请你手动执行后告诉我继续
C. 选择其他方案 - 使用备选方案
D. 跳过此问题 - 暂不处理
```

### 详细回滚方案

**每个方案必须包含详细回滚步骤**:

```markdown
### 回滚方案：git rebase

**场景1: rebase过程中发现冲突，想放弃**
```bash
# 立即中止rebase，恢复到rebase前状态
git rebase --abort
```

**场景2: rebase完成但想撤销**
```bash
# 方法1: 使用ORIG_HEAD（推荐）
git reset --hard ORIG_HEAD

# 方法2: 使用reflog查找rebase前的提交
git reflog  # 找到rebase前的HEAD
git reset --hard HEAD@{N}  # N是reflog中的序号
```

**场景3: 已push但想撤销（危险）**
```bash
# ⚠️ 警告：这会重写远程历史，可能影响其他协作者
git push --force-with-lease origin {branch}

# 如果想完全撤销远程的rebase
git reset --hard ORIG_HEAD
git push --force-with-lease origin {branch}
```

**回滚验证**:
```bash
# 确认回滚成功
git log --oneline -5  # 检查提交历史
git status  # 检查工作区状态
```
```

---

### 9.5 Executor模块 - 深度反思

#### 当前设计的优点

- ✅ 明确的风险分级执行策略
- ✅ 每种错误类型有对应的处理方式
- ✅ 冲突处理提供多种选项

#### 潜在问题与改进

| 问题 | 影响 | 改进方案 |
|------|------|---------|
| **确认方式不明确** | 用户可能不知道如何确认 | 明确确认格式 |
| **回滚可能失败** | 回滚命令也可能失败 | 添加回滚失败处理 |
| **缺少进度反馈** | 用户不知道执行进度 | 添加进度显示 |
| **并发执行风险** | 多步骤可能冲突 | 添加执行锁机制 |

#### 改进后的Prompt片段

```markdown
### 用户确认格式规范

**确认方式**（用户必须使用以下任一格式）:

| 用户输入 | 含义 | 适用场景 |
|---------|------|---------|
| "继续" / "y" / "yes" / "确认" | 继续执行当前步骤 | 默认确认 |
| "跳过" / "s" / "skip" | 跳过当前步骤 | 不想执行某步骤 |
| "中止" / "a" / "abort" | 中止整个方案 | 不想继续执行 |
| "详情" / "d" / "detail" | 查看更多详情 | 想了解更多信息 |
| "回滚" / "r" / "rollback" | 执行回滚 | 想撤销已执行的操作 |

**确认提示格式**:
```markdown
⚠️ 需要确认

即将执行: `git rebase origin/main`
风险等级: 🟡 中等
影响: 将本地提交变基到远程提交之上

确认方式:
- 输入 "y" 或 "继续" 执行此步骤
- 输入 "s" 或 "跳过" 跳过此步骤
- 输入 "a" 或 "中止" 停止整个方案
- 输入 "d" 或 "详情" 查看更多信息

请确认:
```

### 进度反馈机制

**每步执行后显示**:
```markdown
┌─────────────────────────────────────────────────────────────┐
│ 执行进度: [████████░░░░░░░░░░░░] 3/8 步骤                   │
├─────────────────────────────────────────────────────────────┤
│ [3/8] 执行: git rebase origin/main                          │
│ 状态: ⏳ 执行中...                                           │
│ 耗时: 1.2s                                                   │
│ 结果: ✅ 成功                                                │
│ 输出: Successfully rebased and updated refs/heads/feature   │
└─────────────────────────────────────────────────────────────┘

下一步: [4/8] git stash pop（恢复之前暂存的工作）
```

**进度条设计**:
```markdown
# 总进度
[████████████████░░░░] 80% (4/5 问题已解决)

# 当前方案进度
[████████░░░░░░░░░░░░] 40% (2/5 步骤已完成)

# 预计剩余时间
预计剩余时间: 2分钟
```

### 回滚失败处理

**回滚失败场景与处理**:

| 场景 | 原因 | 处理方式 |
|------|------|---------|
| `git rebase --abort` 失败 | rebase已完成后无法abort | 使用 `git reset --hard ORIG_HEAD` |
| `git reset --hard` 失败 | 工作区有未跟踪文件冲突 | 使用 `git clean -fd` 清理 |
| `git stash pop` 失败 | stash与当前状态冲突 | 手动解决冲突或放弃stash |
| `git push --force` 失败 | 无权限或网络问题 | 提示用户检查权限和网络 |

**回滚失败处理流程**:
```markdown
### ⚠️ 回滚失败

回滚命令 `{rollback_command}` 执行失败：
```
{error_output}
```

**手动恢复步骤**:

1. **检查当前状态**:
```bash
git status
git log --oneline -5
```

2. **尝试替代回滚方案**:
```bash
# 如果是rebase相关问题
git reflog  # 查找rebase前的提交
git reset --hard HEAD@{N}  # N是rebase前的位置

# 如果是stash相关问题
git stash list  # 查看所有stash
git stash drop stash@{0}  # 放弃最新的stash
```

3. **如果无法恢复**:
- 请联系项目维护者
- 或提供以下信息以便诊断：
  - `git status` 输出
  - `git reflog` 输出
  - 错误信息截图
```

### 执行锁机制

**防止并发冲突**:

```markdown
### 执行锁规则

**场景1: 同一分支多个操作**
- 如果正在执行 `git rebase`，禁止同时执行 `git merge`
- 如果正在执行 `git stash`，禁止同时执行 `git reset`

**场景2: 多个问题并行解决**
- 如果两个问题需要修改同一文件，必须串行执行
- 如果两个问题相互依赖，按依赖顺序执行

**锁检测**:
```python
def acquire_execution_lock(operation: str) -> bool:
    """获取执行锁"""
    lock_file = f".git/github-manager-{operation}.lock"
    
    if os.path.exists(lock_file):
        # 检查锁是否过期（超过5分钟）
        if is_lock_expired(lock_file, timeout=300):
            release_execution_lock(operation)
        else:
            return False  # 锁被占用
    
    # 创建锁文件
    create_lock_file(lock_file, operation)
    return True

def release_execution_lock(operation: str):
    """释放执行锁"""
    lock_file = f".git/github-manager-{operation}.lock"
    if os.path.exists(lock_file):
        os.remove(lock_file)
```

**锁冲突处理**:
```markdown
### ⚠️ 操作冲突

检测到另一个GitHub管理操作正在进行中：
- 操作类型: {locked_operation}
- 开始时间: {lock_time}
- 当前步骤: {current_step}

**选择处理方式**:
A. 等待完成 - 等待当前操作完成后继续
B. 强制取消 - 取消当前操作，开始新操作（可能丢失数据）
C. 稍后重试 - 稍后再执行此操作
```
```

---

### 9.6 Reporter模块 - 深度反思

#### 当前设计的优点

- ✅ 提供完整的Markdown模板
- ✅ 同时生成JSON用于机器学习
- ✅ 包含教育性的最佳实践章节

#### 潜在问题与改进

| 问题 | 影响 | 改进方案 |
|------|------|---------|
| **报告过长** | 用户可能不想看长报告 | 提供摘要和详细两种模式 |
| **缺少历史对比** | 无法看到改进趋势 | 添加历史对比章节 |
| **无导出选项** | 用户可能想保存报告 | 提供多种导出格式 |

#### 改进后的Prompt片段

```markdown
### 报告模式选择

**模式1: 摘要模式（默认）**
- 仅显示问题列表和关键建议
- 适合快速查看
- 长度: ~50行

**模式2: 详细模式**
- 包含完整的扫描结果、分析过程、解决方案
- 适合深度理解
- 长度: ~200行

**模式3: 教育模式**
- 包含最佳实践解释和学习内容
- 适合学习GitHub最佳实践
- 长度: ~300行

**用户选择方式**:
```markdown
报告已生成。选择查看模式：
A. 摘要 - 快速查看问题和建议
B. 详细 - 完整的扫描和解决方案
C. 教育 - 包含最佳实践解释
```

### 历史对比章节

```markdown
## 📊 历史对比

### 问题趋势

| 问题类型 | 上次 | 本次 | 变化 |
|---------|------|------|------|
| 分支分叉 | 2次 | 0次 | ✅ 改善 |
| 未提交文件 | 15个 | 8个 | ✅ 改善 |
| CI失败 | 1次 | 1次 | ➡️ 持平 |

### 改进建议效果

- 上次建议: "使用rebase解决分支分叉"
- 执行结果: ✅ 成功
- 效果: 分支历史更清晰

### 持续改进

- 🎯 已连续3次执行无高优先级问题
- 📈 问题总数从5个减少到2个
- ⏱️ 平均解决时间从15分钟减少到5分钟
```

### 导出选项

```markdown
### 报告导出

**支持格式**:
- Markdown (.md) - 适合GitHub PR/Issue
- JSON (.json) - 适合机器学习/自动化
- HTML (.html) - 适合网页展示
- PDF (.pdf) - 适合归档

**导出命令**:
```bash
# 导出为Markdown
github-manager export --format md --output report.md

# 导出为JSON（用于学习系统）
github-manager export --format json --output report.json

# 导出为HTML
github-manager export --format html --output report.html
```
```

---

### 9.7 Learner模块 - 深度反思

#### 当前设计的优点

- ✅ 明确的学习维度和数据结构
- ✅ 具体的学习应用场景
- ✅ 可操作的优化建议

#### 潜在问题与改进

| 问题 | 影响 | 改进方案 |
|------|------|---------|
| **学习数据可能过时** | 偏好可能变化 | 添加数据过期机制 |
| **缺少学习效果验证** | 学习可能无效 | 添加A/B测试 |
| **隐私问题** | 数据可能敏感 | 添加数据脱敏 |

#### 改进后的Prompt片段

```markdown
### 数据过期机制

**自动清理规则**:
- 历史记录: 保留最近90天
- 模式数据: 保留最近180天
- 偏好数据: 永久保留（但权重会衰减）

**权重衰减**:
```python
def apply_weight_decay(preferences: Dict) -> Dict:
    """应用权重衰减，使旧数据影响降低"""
    for key, value in preferences.items():
        if 'last_updated' in value:
            days_since_update = (datetime.now() - value['last_updated']).days
            decay_factor = 0.99 ** days_since_update  # 每天衰减1%
            value['weight'] *= decay_factor
    
    return preferences
```

### 学习效果验证

**A/B测试机制**:
```markdown
### 学习效果验证

**测试组A（使用学习优化）**:
- 应用用户偏好方案
- 使用历史有效方案

**测试组B（不使用学习）**:
- 使用默认方案
- 不考虑用户偏好

**对比指标**:
- 成功率: A=85% vs B=70%
- 用户满意度: A=4.5/5 vs B=3.8/5
- 平均解决时间: A=3分钟 vs B=8分钟

**结论**: 学习优化有效，继续应用
```

### 数据脱敏

```markdown
### 隐私保护

**脱敏规则**:
- 文件路径: 仅保留文件名，移除完整路径
- 提交信息: 仅保留类型（feat/fix），移除具体内容
- 分支名称: 仅保留模式（feature/*），移除具体名称

**脱敏示例**:
```json
// 原始数据
{
  "branch_name": "feature/user-authentication",
  "commit_message": "feat: add OAuth login",
  "file_path": "/Users/xxx/project/src/auth/login.ts"
}

// 脱敏后
{
  "branch_pattern": "feature/*",
  "commit_type": "feat",
  "file_type": "*.ts"
}
```

**用户控制**:
- 用户可随时清除学习数据
- 用户可选择不参与学习
- 用户可导出/删除个人数据
```
```

---

## 十、总结与行动建议

### 10.1 Prompt优化优先级

| 优先级 | 模块 | 优化项 | 预期效果 |
|--------|------|--------|---------|
| **P0** | Executor | 明确确认格式 | 用户不困惑 |
| **P0** | Scanner | 添加超时降级 | 防止卡住 |
| **P0** | Solver | 详细回滚方案 | 安全可逆 |
| **P1** | Executor | 进度反馈 | 用户体验提升 |
| **P1** | Analyzer | 规则互斥处理 | 避免冲突建议 |
| **P1** | Solver | 前提条件检查 | 避免无效执行 |
| **P2** | Reporter | 报告模式选择 | 满足不同需求 |
| **P2** | Learner | 数据脱敏 | 隐私保护 |

### 10.2 关键设计决策

| 决策 | 选择 | 原因 |
|------|------|------|
| **Skill vs Agent** | 两者并行 | Skill覆盖80%日常，Agent处理20%复杂 |
| **风险分级** | 三级（低/中/高） | 平衡自动化和安全性 |
| **学习机制** | JSON存储 + 权重衰减 | 可持久化且不过时 |
| **错误处理** | 多策略（重试/跳过/回滚/询问） | 覆盖所有场景 |
| **输出格式** | Markdown + JSON | 人类可读 + 机器可处理 |

### 10.3 实施建议

**Phase 1 (Skill核心) 实施建议**:
1. 先实现Scanner和Analyzer，确保问题识别准确
2. 再实现Solver和Executor，确保解决方案有效
3. 每个模块完成后进行单元测试

**Phase 2 (Skill辅助) 实施建议**:
1. Reporter先实现摘要模式，快速验证
2. Learner先实现历史记录，后续添加智能学习

**Phase 3 (Agent智能) 实施建议**:
1. 先实现状态机，确保流程可控
2. 再实现决策引擎，支持复杂决策
3. 最后实现多代理协作，处理复杂场景

**Phase 4 (集成优化) 实施建议**:
1. 先实现路由器，区分简单/复杂场景
2. 再优化Skill-Agent协同
3. 最后完善文档和测试

### 10.4 验收清单

**Skill验收**:
- [ ] 触发准确率 > 95%
- [ ] 问题识别准确率 > 90%
- [ ] 解决方案有效率 > 85%
- [ ] 用户满意度 > 4.0/5.0
- [ ] 平均响应时间 < 30秒

**Agent验收**:
- [ ] 状态转换正确率 100%
- [ ] 决策准确率 > 80%
- [ ] 多代理协作成功率 > 90%
- [ ] 学习优化效果显著（A/B测试通过）
- [ ] 复杂场景处理成功率 > 75%

**集成验收**:
- [ ] 路由准确率 > 90%
- [ ] Skill-Agent切换无感知
- [ ] 数据共享正确率 100%
- [ ] 整体系统稳定性 > 99%

---

## 十一、附录

### A. 参考文档

- [GitHub Manager Skill 设计文档 (Plan B)](../specs/2026-03-22-github-manager-skill-design.md)
- [GitHub Manager Agent 设计文档 (Plan C)](../specs/2026-03-22-github-manager-skill-design-plan-c.md)
- [GitHub Flow 最佳实践](https://docs.github.com/en/get-started/quickstart/github-flow)
- [Conventional Commits 规范](https://www.conventionalcommits.org/)

### B. 相关Skills

- `writing-skills` - 用于创建和优化skill
- `systematic-debugging` - 用于调试执行问题
- `test-driven-development` - 用于测试驱动开发

### C. 变更历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-03-22 | 初始版本，包含完整实施计划和Prompt反思 |

---

**文档版本**: 1.0.0
**最后更新**: 2026-03-22
**状态**: ✅ 已完成
