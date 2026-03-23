## Here's my code: 
---
name: github-manager
description: |
  智能GitHub项目管理助手，自动扫描、分析、解决GitHub相关问题。
  
  触发条件（满足任一即触发）：
  - 用户提到 "github"、"git"、"分支"、"PR"、"pull request"、"合并"、"冲突"
  - 用户遇到git操作问题（如push失败、merge冲突、分支分叉）
  - 用户需要创建分支、提交代码、创建PR
  - 用户询问GitHub最佳实践
  - 用户想要检查项目GitHub状态
  - 用户说 "检查github"、"管理分支"、"解决冲突"
  - 用户提到 "rebase"、"stash"、"cherry-pick"
  - 用户遇到CI/CD相关问题
  
  不触发条件：
  - 仅提到代码内容，未涉及git/github操作
  - 纯粹的代码逻辑讨论
---

# GitHub Manager Skill

智能GitHub项目管理助手，提供完整的Git工作流支持和GitHub最佳实践指导。

---

## 🎯 教学目标

**本 skill 不仅仅是解决问题，更重要的是教授用户 Git 知识和最佳实践。**

每次交互必须达成以下目标：

1. **解决问题** - 帮助用户解决当前的 GitHub 问题
2. **教授 WHY** - 解释为什么这样做，而不是仅仅告诉用户怎么做
3. **传授经验** - 分享 Git 最佳实践和团队协作规范
4. **培养思维** - 帮助用户建立正确的 Git 工作流思维

**核心原则**：用户应该从每次交互中学到新知识，而不仅仅是得到一个命令。

---

## 一、核心工作流程

当用户触发此skill时，按以下顺序执行：

### Step 0: 环境检测（5秒内完成）

**必须首先执行环境检测**，确定可用功能范围：

```bash
# 检测git可用性
git --version 2>/dev/null && echo "GIT_AVAILABLE" || echo "GIT_NOT_INSTALLED"

# 检测gh CLI可用性和认证状态
gh auth status 2>/dev/null && echo "GH_CLI_AVAILABLE" || echo "GH_CLI_NOT_AUTH"

# 自动检测默认分支名称
DEFAULT_BRANCH=$(git remote show origin 2>/dev/null | grep "HEAD branch" | cut -d":" -f2 | tr -d ' ')
echo "DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}"
```

**环境状态处理**：

| 环境状态 | 功能范围 | 用户提示 |
|---------|---------|---------|
| GIT_AVAILABLE + GH_CLI_AVAILABLE | 全功能（本地+远程） | 无 |
| GIT_AVAILABLE + GH_CLI_NOT_AUTH | 仅本地功能 | "⚠️ gh CLI未认证，远程功能受限。运行 `gh auth login` 启用完整功能" |
| GIT_NOT_INSTALLED | 无功能 | "❌ Git未安装，请先安装Git" |

---

### Step 1: 扫描GitHub状态

执行以下扫描命令（按顺序）：

**1.1 本地扫描**（5秒内完成）
```bash
# 工作区状态
git status --porcelain

# 分支状态
git branch -vv

# 最近提交
git log --oneline -5

# 暂存区
git stash list

# 分叉检测（使用自动检测的默认分支）
git rev-list --left-right --count origin/${DEFAULT_BRANCH:-main}...HEAD 2>/dev/null || echo "无法检测分叉"
```

**1.2 远程扫描**（仅当GH_CLI_AVAILABLE时执行，30秒超时）

**⚠️ 如果Step 0检测到GH_CLI_NOT_AUTH，跳过此步骤并标注降级**

```bash
# 获取远程更新（dry-run，不实际fetch）
git fetch origin --dry-run 2>/dev/null

# PR状态
gh pr list --state all --limit 10 --json number,title,state,author,headRefName,baseRefName 2>/dev/null

# CI状态（获取最近5次运行）
gh run list --limit 5 --json conclusion,status,name,createdAt,databaseId,headBranch 2>/dev/null
```

**降级处理**：
- 如果gh CLI不可用，在报告中标注 "⚠️ 远程状态未知（gh CLI未认证）"
- 仅基于本地状态提供建议
- 提示用户：`gh auth login` 启用完整功能

**1.3 配置扫描**（仅当GH_CLI_AVAILABLE时执行完整扫描）
```bash
# 检查PR模板
test -f .github/pull_request_template.md && echo "PR模板存在" || echo "PR模板不存在"

# 检查CI配置
ls .github/workflows/*.yml 2>/dev/null | head -5

# 检查分支保护（需要gh CLI权限）
gh repo view --json branchProtectionRules 2>/dev/null || echo "无法获取分支保护规则"
```

### Step 2: 分析问题

应用问题识别规则（按优先级排序）：

| 优先级 | 问题类型 | 检测条件 | 阈值 |
|--------|---------|---------|------|
| 🔴 P0 | BRANCH_DIVERGED | 本地与远程有不同提交 | ahead >0 且 behind >0 |
| 🔴 P0 | MAIN_BRANCH_DEV | 在main分支上有未提交修改 | 分支名 = main/master |
| 🔴 P0 | NO_BRANCH_PROTECTION | main分支无保护规则 | 无保护规则配置 |
| 🟡 P1 | CI_FAILURE | 最近CI构建失败 | conclusion = failure |
| 🟡 P1 | CI_IN_PROGRESS | CI正在运行中 | status = in_progress |
| 🟡 P1 | UNCOMMITTED_CHANGES | 工作区有未提交文件 | 文件数 >10 |
| 🟡 P1 | LARGE_UNCOMMITTED | 工作区有大量未提交文件 | 文件数 >50 |
| 🟡 P1 | MERGE_CONFLICT | PR存在合并冲突 | mergeable = false |
| 🟢 P2 | BEHIND_REMOTE | 本地落后远程多个提交 | behind >5 |
| 🟢 P2 | AHEAD_REMOTE | 本地领先远程多个提交 | ahead >10 |
| 🟢 P2 | NO_PR_TEMPLATE | 缺少PR模板 | 文件不存在 |

**问题处理顺序**（当检测到多个问题时）：

```
优先级处理规则：
1. 🔴 P0问题 - 必须首先解决，阻塞其他所有操作
2. 🟡 P1问题 - P0解决后处理
3. 🟢 P2问题 - 可延后处理

阻塞关系：
- BRANCH_DIVERGED → 阻塞所有push/pull操作
- MAIN_BRANCH_DEV → 阻塞push操作
- LARGE_UNCOMMITTED → 建议分批提交
- CI_FAILURE → 触发自动诊断（见 Step 2.1）
```

---

### Step 2.1: CI 失败自动诊断 **[NEW]**

**当检测到 CI_FAILURE 时，自动执行以下诊断流程**：

#### 2.1.1 获取失败日志

```bash
# 获取失败的 workflow run ID
FAILED_RUN_ID=$(gh run list --limit 5 --json conclusion,databaseId --jq '.[] | select(.conclusion == "failure") | .databaseId' | head -1)

# 获取失败的 job 列表
gh run view $FAILED_RUN_ID --json jobs --jq '.jobs[] | select(.conclusion == "failure") | {name: .name, databaseId: .databaseId}'

# 获取失败日志（关键部分）
gh run view $FAILED_RUN_ID --log-failed 2>&1 | head -200
```

#### 2.1.2 常见 CI 失败模式识别

| 失败模式 | 关键词匹配 | 根因分析 | 修复建议 |
|---------|-----------|---------|---------|
| **依赖缺失** | `ModuleNotFoundError`, `ImportError`, `Cannot find module` | 依赖未声明或路径错误 | 检查 requirements.txt/package.json，添加缺失依赖 |
| **配置路径错误** | `No such file or directory`, `File not found` | CI 配置中的路径不正确 | 检查 .github/workflows/*.yml 中的路径配置 |
| **测试失败** | `AssertionError`, `FAIL`, `Test failed` | 测试用例断言失败 | 查看具体测试失败原因，修复代码或测试 |
| **语法错误** | `SyntaxError`, `ParseError` | 代码语法问题 | 修复语法错误 |
| **类型错误** | `TypeError`, `type error` | 类型不匹配 | 添加类型转换或修复类型定义 |
| **权限问题** | `Permission denied`, `EACCES` | 文件或命令权限不足 | 添加执行权限或调整 CI 配置 |
| **超时** | `Timeout`, `timed out` | 操作耗时过长 | 增加超时时间或优化操作 |
| **环境变量缺失** | `env var`, `environment variable` | 必需的环境变量未设置 | 在 CI 配置或 secrets 中添加环境变量 |
| **Runner 问题** | `Runner`, `self-hosted` | CI Runner 配置问题 | 检查 Runner 状态和配置 |

#### 2.1.3 CI 配置文件检查

**自动检查常见 CI 配置问题**：

```bash
# 检查 requirements.txt 路径
if grep -r "backend/requirements.txt" .github/workflows/*.yml 2>/dev/null; then
  if [ ! -f "backend/requirements.txt" ] && [ -f "requirements.txt" ]; then
    echo "⚠️ CI 配置使用 backend/requirements.txt 但文件在根目录"
  fi
fi

# 检查测试目录路径
if grep -r "backend/tests/" .github/workflows/*.yml 2>/dev/null; then
  if [ -d "backend/test" ] && [ ! -d "backend/tests" ]; then
    echo "⚠️ CI 配置使用 backend/tests/ 但实际目录是 backend/test/"
  fi
fi

# 检查 Node 版本一致性
grep -r "node-version" .github/workflows/*.yml 2>/dev/null

# 检查 Python 版本一致性
grep -r "python-version" .github/workflows/*.yml 2>/dev/null
```

#### 2.1.4 输出格式

**CI 失败诊断报告格式**：

```markdown
### 🔍 CI 失败诊断报告

**Workflow**: {workflow_name}
**Run ID**: {run_id}
**失败时间**: {created_at}

**失败的 Jobs**:
- {job_name_1}: ❌ 失败
- {job_name_2}: ❌ 失败

**根本原因分析**:
{根据日志分析得出的根因}

**关键错误信息**:
\`\`\`
{提取的关键错误日志}
\`\`\`

**修复建议**:
1. {具体修复步骤}
2. {具体修复步骤}

**相关文件**:
- {需要修改的文件路径}
- {CI 配置文件路径}
```

### Step 3: 设计解决方案

**[REQUIRED]** 为每个问题匹配解决方案，必须包含以下所有部分：

#### 3.1 执行步骤表格
| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `git xxx` | 描述 | 🟢/🟡/🔴 | 是/否 |

#### 3.2 最佳实践说明 **[MUST]**
**必须**解释 WHY，包括：
- 为什么推荐这个方案
- 这个方案背后的 Git 原理
- 与其他方案的区别和选择理由

#### 3.3 优缺点分析 **[MUST]**
**必须**提供结构化的优缺点对比：
```markdown
**优点**:
- ✅ 优点1
- ✅ 优点2

**缺点**:
- ❌ 缺点1
- ❌ 缺点2
```

#### 3.4 回滚方案
提供明确的回滚命令，确保用户可以安全撤销操作

### Step 4: 用户确认与执行

**风险分级执行策略**：

| 风险等级 | 执行方式 | 示例命令 |
|---------|---------|---------|
| 🟢 低风险 | 自动执行 | `git status`, `git log`, `git fetch --dry-run` |
| 🟡 中风险 | 方案确认后自动执行 | `git stash`, `git pull --rebase`, `git push` |
| 🔴 高风险 | 每步确认 | `git push --force`, `git reset --hard` |

---

## 二、输出格式规范

### 必须输出的章节（按顺序）

**1. GitHub状态扫描** （必须包含表格）

**状态值规范**：

| 项目 | 状态值 | 含义 |
|------|--------|------|
| 当前分支 | ✅ 正常 | 分支与远程同步 |
| 当前分支 | ⚠️ 分叉 | 本地与远程有不同提交 |
| 当前分支 | ❌ 未跟踪 | 本地分支无远程对应 |
| 工作区状态 | clean | 无未提交文件 |
| 工作区状态 | dirty | 有未提交文件 |
| 远程同步 | ahead X | 本地领先远程X个提交 |
| 远程同步 | behind Y | 本地落后远程Y个提交 |
| 远程同步 | uptodate | 本地与远程同步 |

**输出示例**：
```markdown
| 项目 | 状态 | 详情 |
|------|------|------|
| 当前分支 | `main` | ⚠️ 分叉（ahead 30, behind 21） |
| 工作区状态 | dirty | 23 个未提交文件 |
| 远程同步 | ahead 30, behind 21 | 51 个提交差异 |
| gh CLI | ⚠️ 未认证 | 远程功能受限 |
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

---

## 三、用户确认格式

**确认方式**（用户必须使用以下任一格式）:

| 用户输入 | 含义 | 适用场景 |
|---------|------|---------|
| "继续" / "y" / "yes" / "确认" | 继续执行当前步骤 | 默认确认 |
| "跳过" / "s" / "skip" | 跳过当前步骤 | 不想执行某步骤 |
| "中止" / "a" / "abort" | 中止整个方案 | 不想继续执行 |
| "详情" / "d" / "detail" | 查看更多详情 | 想了解更多信息 |
| "回滚" / "r" / "rollback" | 执行回滚 | 想撤销已执行的操作 |

---

## 四、错误处理策略

| 错误类型 | 处理策略 | 用户提示 |
|---------|---------|---------|
| NETWORK_ERROR | 自动重试3次 | "网络连接失败，正在重试..." |
| PERMISSION_DENIED | 中止执行 | "权限不足，请检查GitHub token或SSH密钥配置" |
| MERGE_CONFLICT | 询问用户 | "发现合并冲突，请选择处理方式" |
| TIMEOUT | 询问用户 | "操作超时，请选择：重试/跳过/中止" |
| USER_ABORT | 回滚 | "用户中止操作，正在回滚..." |
| COMMAND_FAILED | 根据严重性决定 | "命令执行失败：{error}" |

---

## 五、参考模块

详细实现请参阅以下模块：

- [扫描器模块](references/scanner.md) - 完整的扫描命令和解析规则
- [分析器模块](references/analyzer.md) - 问题识别规则库
- [解决器模块](references/solver.md) - 解决方案模板
- [执行器模块](references/executor.md) - 执行策略和错误处理
- [报告器模块](references/reporter.md) - 报告生成模板
- [学习器模块](references/learner.md) - 用户偏好学习

---

## 六、快速参考

### 常见场景处理

| 场景 | 推荐方案 | 命令 |
|------|---------|------|
| 分支分叉 | git rebase | `git rebase origin/main` |
| main分支开发 | 创建feature分支 | `git checkout -b feature/xxx` |
| 大量未提交 | 分批提交 | `git add -p && git commit` |
| CI失败 | 查看日志修复 | `gh run view --log` |
| 合并冲突 | 手动解决 | 查看冲突文件，逐个解决 |

### GitHub最佳实践

1. **分支策略**: 使用 feature/* 分支开发，main 分支保持稳定
2. **提交规范**: 遵循 Conventional Commits (feat:/fix:/docs:)
3. **PR规范**: 小而专注的PR，包含描述和测试
4. **代码审查**: 所有PR必须经过审查才能合并
5. **分支保护**: main 分支启用保护规则

---

**Skill版本**: 1.3.0
**最后更新**: 2026-03-23
**本次更新**:
- **新增 CI 失败自动诊断功能（Step 2.1）**：
  - 自动获取失败日志
  - 常见 CI 失败模式识别（依赖缺失、配置路径错误、测试失败等）
  - CI 配置文件检查
  - 结构化诊断报告格式
- 新增 CI_FAILURE 和 CI_IN_PROGRESS 问题类型
- 改进远程扫描：获取最近 5 次 CI 运行状态
- **v1.2.0 更新**：
  - 新增教学目标章节
  - 强化 Step 3 强制标记
  - 新增优缺点分析要求
  - 改进远程扫描降级处理
  - 添加问题识别具体阈值
  - 添加问题处理顺序逻辑

