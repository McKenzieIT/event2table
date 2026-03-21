# GitHub Manager Skill 完整设计规范

**创建时间**: 2026-03-22
**设计者**: Qoder + 用户协作
**版本**: 1.0.0
**状态**: 待审核

---

## 一、概述

### 1.1 背景

当前项目（Event2Table）已发展到一定规模，但用户的GitHub知识储备已不足以支撑当前项目的开发需求。需要一个专门针对当前项目的GitHub管理skill，能够：

1. 自动分析和管理项目当前的GitHub状态
2. 识别项目中存在的GitHub相关问题
3. 在使用过程中传授GitHub最佳实践
4. 具备自我学习和改进能力
5. 集成项目特定的GitHub工作流和规范

### 1.2 目标

创建一个智能GitHub管理助手（github-manager skill），实现：

- **自动化**：运行后自动发现并解决问题
- **教育性**：说明解决了什么、为什么要解决、怎么解决
- **规范性**：输出内容有规范格式，每次一致
- **学习性**：随着使用次数增加而提升适配度和效果

### 1.3 用户需求确认

| 需求项 | 用户选择 |
|--------|---------|
| 使用场景 | A+B+C+D（日常开发+问题诊断+最佳实践教育+状态监控） |
| 自动化程度 | B（半自动执行，确认后自动执行，高风险额外确认） |
| 输出格式 | D（Markdown用户阅读 + JSON机器学习） |
| 工作流规范 | C（重新设计规范，选用最佳实践并说明原因） |
| 学习机制 | D（综合方案：JSON存储+Markdown文档+动态优化+定期报告） |

---

## 二、架构设计

### 2.1 方案选择

采用**方案B：模块化设计**，平衡功能完整度和开发成本。

### 2.2 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Manager Skill                          │
│                      (SKILL.md 主控制器)                          │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Scanner     │     │   Analyzer    │     │    Solver     │
│   扫描器      │────▶│   分析器      │────▶│   解决器      │
└───────────────┘     └───────────────┘     └───────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Executor    │     │   Reporter    │     │   Learner     │
│   执行器      │◀────│   报告器      │◀────│   学习器      │
└───────────────┘     └───────────────┘     └───────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   学习数据存储         │
                    │  .github/skill-data/   │
                    └───────────────────────┘
```

### 2.3 核心工作流程

```
用户触发 → 扫描GitHub状态 → 分析问题 → 设计解决方案 
    → 用户确认方案 → 自动执行（低/中风险） 
    → 高风险操作确认 → 生成报告 → 学习优化
```

### 2.4 文件结构

```
github-manager/
├── SKILL.md                    # 主技能文件（~300行）
├── references/
│   ├── scanner.md              # 状态扫描模块
│   ├── analyzer.md             # 问题分析模块
│   ├── solver.md               # 解决方案模块
│   ├── executor.md             # 执行器模块
│   ├── reporter.md             # 报告生成模块
│   └── learner.md              # 学习优化模块
├── scripts/
│   ├── scan_github_state.py    # GitHub状态扫描脚本
│   ├── analyze_problems.py     # 问题分析脚本
│   └── generate_report.py      # 报告生成脚本
└── templates/
    ├── report-template.md      # Markdown报告模板
    └── report-schema.json      # JSON数据结构
```

---

## 三、Scanner（扫描器）

### 3.1 功能描述

全面扫描项目GitHub状态，收集诊断数据

### 3.2 扫描流程

```
┌─────────────────────────────────────────────────────────────┐
│                      Scanner 扫描流程                        │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  LocalScanner │     │ RemoteScanner │     │ ConfigScanner │
│  本地状态扫描  │     │  远程状态扫描  │     │  配置状态扫描  │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ - git status  │     │ - gh pr list  │     │ - .github/    │
│ - git branch  │     │ - gh repo view│     │ - workflows/  │
│ - git log     │     │ - CI status   │     │ - templates/  │
│ - git stash   │     │ - branch prot.│     │ - CODEOWNERS  │
└───────────────┘     └───────────────┘     └───────────────┘
```

### 3.3 扫描命令清单

| 类别 | 命令 | 用途 | 风险等级 | 超时设置 |
|------|------|------|---------|---------|
| 本地 | `git status --porcelain` | 检查未提交文件 | 🟢 低 | 5s |
| 本地 | `git branch -vv` | 检查分支状态 | 🟢 低 | 5s |
| 本地 | `git log --oneline -10` | 检查最近提交 | 🟢 低 | 5s |
| 本地 | `git stash list` | 检查暂存区 | 🟢 低 | 5s |
| 本地 | `git remote -v` | 检查远程配置 | 🟢 低 | 5s |
| 本地 | `git rev-list --left-right --count origin/main...HEAD` | 检查分叉状态 | 🟢 低 | 5s |
| 本地 | `git diff --stat` | 检查变更统计 | 🟢 低 | 10s |
| 远程 | `git fetch origin --dry-run` | 检查远程更新 | 🟢 低 | 30s |
| 远程 | `gh pr list --state all --limit 20` | 检查PR状态 | 🟢 低 | 30s |
| 远程 | `gh repo view --json branchProtectionRules,defaultBranchRef` | 检查分支保护 | 🟢 低 | 30s |
| 远程 | `gh run list --limit 5` | 检查CI运行状态 | 🟢 低 | 30s |
| 远程 | `gh issue list --state open --limit 10` | 检查Issue状态 | 🟢 低 | 30s |
| 配置 | 读取 `.github/pull_request_template.md` | 检查PR模板 | 🟢 低 | 2s |
| 配置 | 读取 `.github/ISSUE_TEMPLATE/` | 检查Issue模板 | 🟢 低 | 2s |
| 配置 | 读取 `.github/workflows/*.yml` | 检查CI/CD配置 | 🟢 低 | 5s |
| 配置 | 读取 `.github/CODEOWNERS` | 检查代码所有者 | 🟢 低 | 2s |
| 配置 | 读取 `.pre-commit-config.yaml` | 检查pre-commit | 🟢 低 | 2s |

### 3.4 数据结构

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class ScanResult:
    """扫描结果数据结构"""
    
    # 本地状态
    local_state: 'LocalState'
    
    # 远程状态  
    remote_state: 'RemoteState'
    
    # 项目配置
    project_config: 'ProjectConfig'
    
    # 扫描元数据
    scan_time: datetime
    scan_duration_ms: int
    errors: List['ScanError']
    
    def to_json(self) -> Dict:
        """转换为JSON格式"""
        pass
    
    def has_issues(self) -> bool:
        """是否存在问题"""
        return (
            not self.local_state.is_clean or
            self.local_state.diverged or
            self.remote_state.ci_status.status == 'failure' or
            not self.project_config.has_branch_protection
        )


class LocalState:
    """本地Git状态"""
    
    current_branch: str
    is_clean: bool  # 工作区是否干净
    uncommitted_files: List['UncommittedFile']
    unpushed_commits: int
    unpulled_commits: int
    diverged: bool  # 是否分叉
    stash_count: int
    local_branches: List[str]
    last_commit_hash: str
    last_commit_message: str
    last_commit_time: datetime
    
    def get_uncommitted_count(self) -> int:
        """获取未提交文件数量"""
        return len(self.uncommitted_files)
    
    def get_status_summary(self) -> str:
        """获取状态摘要"""
        if self.is_clean:
            return "工作区干净"
        return f"有 {self.get_uncommitted_count()} 个未提交文件"


class UncommittedFile:
    """未提交文件"""
    
    path: str
    status: str  # M/A/D/R/C (修改/新增/删除/重命名/复制)
    is_new: bool
    is_deleted: bool
    is_modified: bool


class RemoteState:
    """远程仓库状态"""
    
    remote_url: str
    default_branch: str
    active_prs: List['PRInfo']
    ci_status: 'CIStatus'
    branch_protection: 'BranchProtection'
    collaborators: List[str]
    open_issues: int
    last_push_time: datetime
    
    def has_active_prs(self) -> bool:
        """是否有活跃PR"""
        return len(self.active_prs) > 0
    
    def get_pr_needing_review(self) -> List['PRInfo']:
        """获取需要审查的PR"""
        return [pr for pr in self.active_prs if pr.needs_review]


class PRInfo:
    """PR信息"""
    
    number: int
    title: str
    state: str  # open/closed/merged
    author: str
    created_at: datetime
    updated_at: datetime
    head_branch: str
    base_branch: str
    mergeable: Optional[bool]
    merge_state_status: str
    review_decision: Optional[str]  # APPROVED/CHANGES_REQUESTED/REVIEW_REQUIRED
    ci_status: str
    additions: int
    deletions: int
    changed_files: int
    
    @property
    def needs_review(self) -> bool:
        """是否需要审查"""
        return self.review_decision == 'REVIEW_REQUIRED'
    
    @property
    def is_stale(self) -> bool:
        """是否过期（超过7天未更新）"""
        from datetime import timedelta
        return (datetime.now() - self.updated_at) > timedelta(days=7)


class CIStatus:
    """CI状态"""
    
    status: str  # success/failure/pending/none
    last_run_id: str
    last_run_time: datetime
    last_run_conclusion: str
    workflow_runs: List['WorkflowRun']
    
    def is_passing(self) -> bool:
        """是否通过"""
        return self.status == 'success'


class WorkflowRun:
    """工作流运行记录"""
    
    id: str
    name: str
    status: str
    conclusion: str
    created_at: datetime
    html_url: str


class BranchProtection:
    """分支保护规则"""
    
    enabled: bool
    required_approving_review_count: int
    requires_status_checks: bool
    requires_pull_request: bool
    enforce_admins: bool
    allows_force_pushes: bool
    allows_deletions: bool
    required_status_checks: List[str]
    
    def is_well_protected(self) -> bool:
        """是否保护完善"""
        return (
            self.enabled and
            self.requires_pull_request and
            self.required_approving_review_count >= 1 and
            not self.allows_force_pushes and
            not self.allows_deletions
        )


class ProjectConfig:
    """项目GitHub配置"""
    
    has_pr_template: bool
    has_issue_templates: bool
    has_codeowners: bool
    has_ci_cd: bool
    has_pre_commit: bool
    workflows: List['WorkflowInfo']
    pr_template_content: Optional[str]
    
    def get_missing_configs(self) -> List[str]:
        """获取缺失的配置"""
        missing = []
        if not self.has_pr_template:
            missing.append("PR模板")
        if not self.has_issue_templates:
            missing.append("Issue模板")
        if not self.has_codeowners:
            missing.append("CODEOWNERS")
        if not self.has_pre_commit:
            missing.append("pre-commit hooks")
        return missing


class WorkflowInfo:
    """工作流信息"""
    
    name: str
    path: str
    triggers: List[str]  # push/pull_request/schedule等
    jobs: List[str]
    has_test_job: bool
    has_deploy_job: bool


class ScanError:
    """扫描错误"""
    
    category: str  # local/remote/config
    command: str
    error_message: str
    is_critical: bool
```

---

## 四、Analyzer（分析器）

### 4.1 功能描述

分析扫描结果，识别问题并评估严重性

### 4.2 分析流程

```
┌─────────────────────────────────────────────────────────────┐
│                      Analyzer 分析流程                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   加载扫描结果     │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   应用问题规则     │
                    │  (ProblemRules)   │
                    └───────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ BranchAnalyzer│     │ CommitAnalyzer│     │ ConfigAnalyzer│
│ 分支问题分析   │     │ 提交问题分析   │     │ 配置问题分析   │
└───────────────┘     └───────────────┘     └───────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  问题严重性评估    │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   根因分析        │
                    └───────────────────┘
```

### 4.3 问题识别规则库

```python
class ProblemRule:
    """问题识别规则"""
    
    rule_id: str
    problem_type: 'ProblemType'
    condition: callable  # 判断条件
    severity: 'Severity'
    description_template: str
    root_cause_template: str
    impact_list: List[str]


# 规则定义
PROBLEM_RULES = [
    # 规则1: 分支分叉
    ProblemRule(
        rule_id="RULE-001",
        problem_type=ProblemType.BRANCH_DIVERGED,
        condition=lambda scan: scan.local_state.diverged,
        severity=Severity.HIGH,
        description_template="本地 {branch} 分支与远程分支已分叉，本地有 {local_commits} 个提交，远程有 {remote_commits} 个不同的提交",
        root_cause_template="直接在 {branch} 分支上开发，或其他协作者推送了新提交",
        impact_list=[
            "无法直接push到远程",
            "可能导致合并冲突",
            "违反分支保护最佳实践",
            "增加代码同步复杂度"
        ]
    ),
    
    # 规则2: 大量未提交文件
    ProblemRule(
        rule_id="RULE-002",
        problem_type=ProblemType.UNCOMMITTED_CHANGES,
        condition=lambda scan: len(scan.local_state.uncommitted_files) > 10,
        severity=Severity.MEDIUM,
        description_template="工作区有 {count} 个未提交的文件修改",
        root_cause_template="开发过程中未及时提交，或正在进行大规模重构",
        impact_list=[
            "代码变更难以追踪",
            "无法回滚到稳定状态",
            "增加代码丢失风险",
            "影响团队协作"
        ]
    ),
    
    # 规则3: 在main分支直接开发
    ProblemRule(
        rule_id="RULE-003",
        problem_type=ProblemType.MAIN_BRANCH_DEV,
        condition=lambda scan: (
            scan.local_state.current_branch == 'main' and 
            not scan.local_state.is_clean
        ),
        severity=Severity.HIGH,
        description_template="在 main 分支上直接开发，有 {count} 个未提交修改",
        root_cause_template="未遵循分支策略，直接在受保护分支上开发",
        impact_list=[
            "违反分支保护最佳实践",
            "main分支可能变得不稳定",
            "无法进行代码审查",
            "增加部署风险"
        ]
    ),
    
    # 规则4: 无分支保护
    ProblemRule(
        rule_id="RULE-004",
        problem_type=ProblemType.NO_BRANCH_PROTECTION,
        condition=lambda scan: not scan.remote_state.branch_protection.enabled,
        severity=Severity.HIGH,
        description_template="main 分支未配置保护规则",
        root_cause_template="项目初始化时未配置分支保护",
        impact_list=[
            "任何人可直接推送到main",
            "无法强制代码审查",
            "增加代码质量风险",
            "违反GitHub最佳实践"
        ]
    ),
    
    # 规则5: CI失败
    ProblemRule(
        rule_id="RULE-005",
        problem_type=ProblemType.CI_FAILURE,
        condition=lambda scan: scan.remote_state.ci_status.status == 'failure',
        severity=Severity.HIGH,
        description_template="最近一次CI构建失败",
        root_cause_template="代码存在测试失败、lint错误或构建问题",
        impact_list=[
            "无法部署到生产环境",
            "代码质量无法保证",
            "可能影响其他开发者"
        ]
    ),
    
    # 规则6: PR过期
    ProblemRule(
        rule_id="RULE-006",
        problem_type=ProblemType.PR_STALE,
        condition=lambda scan: any(pr.is_stale for pr in scan.remote_state.active_prs),
        severity=Severity.MEDIUM,
        description_template="有 {count} 个PR超过7天未更新",
        root_cause_template="审查流程阻塞或开发者忘记跟进",
        impact_list=[
            "代码变更延迟合并",
            "可能产生更多冲突",
            "影响项目进度"
        ]
    ),
    
    # 规则7: 落后远程
    ProblemRule(
        rule_id="RULE-007",
        problem_type=ProblemType.BEHIND_REMOTE,
        condition=lambda scan: scan.local_state.unpulled_commits > 5,
        severity=Severity.MEDIUM,
        description_template="本地落后远程 {count} 个提交",
        root_cause_template="未及时同步远程更新",
        impact_list=[
            "可能基于过时代码开发",
            "增加合并冲突风险",
            "可能重复已完成的工作"
        ]
    ),
    
    # 规则8: 缺少PR模板
    ProblemRule(
        rule_id="RULE-008",
        problem_type=ProblemType.NO_PR_TEMPLATE,
        condition=lambda scan: not scan.project_config.has_pr_template,
        severity=Severity.LOW,
        description_template="项目缺少PR模板",
        root_cause_template="项目初始化时未创建",
        impact_list=[
            "PR描述不规范",
            "可能遗漏重要检查项",
            "降低审查效率"
        ]
    ),
    
    # 规则9: 合并冲突
    ProblemRule(
        rule_id="RULE-009",
        problem_type=ProblemType.MERGE_CONFLICT,
        condition=lambda scan: any(
            pr.merge_state_status == 'DIRTY' 
            for pr in scan.remote_state.active_prs
        ),
        severity=Severity.HIGH,
        description_template="有 {count} 个PR存在合并冲突",
        root_cause_template="多个PR修改了同一文件",
        impact_list=[
            "无法自动合并",
            "需要手动解决冲突",
            "可能引入错误"
        ]
    ),
    
    # 规则10: 大型PR
    ProblemRule(
        rule_id="RULE-010",
        problem_type=ProblemType.LARGE_PR,
        condition=lambda scan: any(
            pr.changed_files > 20 or pr.additions + pr.deletions > 1000
            for pr in scan.remote_state.active_prs
        ),
        severity=Severity.MEDIUM,
        description_template="有 {count} 个PR变更过大（超过20个文件或1000行）",
        root_cause_template="一次PR包含过多功能或重构范围过大",
        impact_list=[
            "审查困难且耗时",
            "增加引入bug风险",
            "难以回滚"
        ]
    ),
]
```

### 4.4 数据结构

```python
class AnalysisResult:
    """分析结果数据结构"""
    
    analysis_id: str
    analysis_time: datetime
    analysis_duration_ms: int
    
    # 问题列表
    problems: List['Problem']
    
    # 统计信息
    total_issues: int
    by_severity: Dict[str, int]  # {"high": 2, "medium": 3, "low": 1}
    by_type: Dict[str, int]
    
    # 优先级排序
    sorted_problems: List['Problem']  # 按严重性和影响排序
    
    def get_high_priority_problems(self) -> List['Problem']:
        """获取高优先级问题"""
        return [p for p in self.problems if p.severity == Severity.HIGH]
    
    def to_json(self) -> Dict:
        """转换为JSON"""
        pass


class Problem:
    """识别出的问题"""
    
    id: str  # "prob-001"
    type: 'ProblemType'
    severity: 'Severity'
    
    # 描述
    title: str
    description: str
    root_cause: str
    impact: List[str]
    
    # 关联信息
    affected_files: List[str]
    related_commits: List[str]
    related_prs: List[int]
    
    # 元数据
    detected_at: datetime
    rule_id: str  # 匹配的规则ID
    
    # 解决建议（初步）
    suggested_solutions: List[str]
    
    def get_severity_emoji(self) -> str:
        """获取严重性图标"""
        return {
            Severity.HIGH: "🔴",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🟢"
        }[self.severity]


class ProblemType(Enum):
    """问题类型枚举"""
    
    # 分支相关
    BRANCH_DIVERGED = "branch_diverged"
    MAIN_BRANCH_DEV = "main_branch_dev"
    BEHIND_REMOTE = "behind_remote"
    AHEAD_REMOTE = "ahead_remote"
    
    # 提交相关
    UNCOMMITTED_CHANGES = "uncommitted_changes"
    LARGE_COMMIT = "large_commit"
    CONVENTIONAL_COMMIT_VIOLATION = "conventional_commit_violation"
    
    # PR相关
    PR_STALE = "pr_stale"
    PR_NEEDS_REVIEW = "pr_needs_review"
    MERGE_CONFLICT = "merge_conflict"
    LARGE_PR = "large_pr"
    
    # CI/CD相关
    CI_FAILURE = "ci_failure"
    CI_PENDING_TOO_LONG = "ci_pending_too_long"
    
    # 配置相关
    NO_BRANCH_PROTECTION = "no_branch_protection"
    NO_PR_TEMPLATE = "no_pr_template"
    NO_ISSUE_TEMPLATE = "no_issue_template"
    NO_CODEOWNERS = "no_codeowners"
    NO_PRE_COMMIT = "no_pre_commit"
    
    # 安全相关
    FORCE_PUSH_RISK = "force_push_risk"
    SENSITIVE_FILE_CHANGE = "sensitive_file_change"


class Severity(Enum):
    """严重性等级"""
    
    HIGH = "high"      # 阻塞性问题，必须立即解决
    MEDIUM = "medium"  # 重要问题，应尽快解决
    LOW = "low"        # 次要问题，可以延后解决
```

---

## 五、Solver（解决器）

### 5.1 功能描述

针对每个问题设计解决方案，基于GitHub最佳实践

### 5.2 解决流程

```
┌─────────────────────────────────────────────────────────────┐
│                      Solver 解决流程                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   加载分析结果     │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   匹配解决方案     │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  最佳实践验证      │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  风险等级评估      │
                    └───────────────────┘
```

### 5.3 解决方案库

```python
class SolutionTemplate:
    """解决方案模板"""
    
    template_id: str
    problem_type: ProblemType
    approach: str  # 解决方法名称
    title: str
    description: str
    
    # 步骤模板
    steps: List['SolutionStepTemplate']
    
    # 最佳实践说明
    best_practice_reason: str
    best_practice_references: List[str]
    
    # 风险评估
    risk_level: 'RiskLevel'
    risk_factors: List[str]
    rollback_plan: str
    
    # 执行控制
    requires_confirmation: bool
    prerequisites: List[str]


# 解决方案模板定义
SOLUTION_TEMPLATES = [
    # 方案1: 解决分支分叉 - Rebase方式
    SolutionTemplate(
        template_id="SOL-001",
        problem_type=ProblemType.BRANCH_DIVERGED,
        approach="git_rebase",
        title="使用 git rebase 变基合并",
        description="将本地提交变基到远程提交之上，保持线性历史",
        steps=[
            SolutionStepTemplate(
                order=1,
                command="git stash push -m 'backup before rebase'",
                description="备份当前未提交的工作",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=2,
                command="git fetch origin",
                description="获取远程最新更新",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=3,
                command="git rebase origin/{branch}",
                description="变基到远程分支",
                risk_level=RiskLevel.MEDIUM,
                requires_confirmation=True,
                conflict_handling="manual"
            ),
            SolutionStepTemplate(
                order=4,
                command="git stash pop",
                description="恢复之前暂存的工作",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
        ],
        best_practice_reason="""
1. **保持线性历史** - rebase不会产生额外的merge commit，历史更清晰易读
2. **便于代码审查** - 每个提交都是独立的，更容易理解变更内容
3. **减少冲突复杂度** - 变基时逐个提交应用，冲突更容易定位和解决
4. **符合GitHub Flow** - 主分支应始终保持可部署状态
5. **bisect友好** - 线性历史便于使用git bisect定位问题
        """.strip(),
        best_practice_references=[
            "https://git-scm.com/book/en/v2/Git-Branching-Rebasing",
            "https://www.atlassian.com/git/tutorials/merging-vs-rebasing"
        ],
        risk_level=RiskLevel.MEDIUM,
        risk_factors=[
            "重写本地提交历史",
            "可能遇到冲突需要手动解决",
            "如果已推送到远程，需要force push"
        ],
        rollback_plan="git rebase --abort 取消变基操作",
        requires_confirmation=True,
        prerequisites=["工作区干净或已暂存", "有网络连接"]
    ),
    
    # 方案2: 解决分支分叉 - Merge方式
    SolutionTemplate(
        template_id="SOL-002",
        problem_type=ProblemType.BRANCH_DIVERGED,
        approach="git_merge",
        title="使用 git merge 合并",
        description="创建一个merge commit，保留完整历史",
        steps=[
            SolutionStepTemplate(
                order=1,
                command="git stash push -m 'backup before merge'",
                description="备份当前未提交的工作",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=2,
                command="git fetch origin",
                description="获取远程最新更新",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=3,
                command="git merge origin/{branch}",
                description="合并远程分支",
                risk_level=RiskLevel.MEDIUM,
                requires_confirmation=True,
                conflict_handling="manual"
            ),
            SolutionStepTemplate(
                order=4,
                command="git stash pop",
                description="恢复之前暂存的工作",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
        ],
        best_practice_reason="""
1. **保留完整历史** - 所有提交和分支历史都被保留
2. **团队协作友好** - 不改变已推送的提交，不影响他人
3. **可追溯性强** - 可以清楚看到何时何地进行了合并
4. **适合公共分支** - 已推送的分支不应rebase，merge是安全选择
        """.strip(),
        best_practice_references=[
            "https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging"
        ],
        risk_level=RiskLevel.MEDIUM,
        risk_factors=[
            "会产生额外的merge commit",
            "可能遇到冲突需要手动解决",
            "历史可能变得复杂"
        ],
        rollback_plan="git merge --abort 取消合并操作",
        requires_confirmation=True,
        prerequisites=["工作区干净或已暂存", "有网络连接"]
    ),
    
    # 方案3: 解决未提交文件
    SolutionTemplate(
        template_id="SOL-003",
        problem_type=ProblemType.UNCOMMITTED_CHANGES,
        approach="batch_commit",
        title="分批提交 + 语义化提交信息",
        description="按功能模块分批提交，使用语义化提交信息",
        steps=[
            SolutionStepTemplate(
                order=1,
                command="git status --short",
                description="查看文件变更分类",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=2,
                command="git add <files_by_category>",
                description="按功能分类暂存文件",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=3,
                command='git commit -m "<type>(<scope>): <subject>"',
                description="使用语义化信息提交",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
        ],
        best_practice_reason="""
1. **原子提交** - 每个提交只包含一个逻辑变更，便于理解和回滚
2. **语义化信息** - 便于自动化生成changelog，提高可读性
3. **便于审查** - 小提交更容易审查，减少遗漏bug的可能
4. **符合约定式提交** - 业界标准，工具友好
5. **便于回滚** - 如果某个功能有问题，可以精确回滚
        """.strip(),
        best_practice_references=[
            "https://www.conventionalcommits.org/",
            "https://chris.beams.io/posts/git-commit/"
        ],
        risk_level=RiskLevel.LOW,
        risk_factors=["需要手动分类文件"],
        rollback_plan="git reset HEAD~ 撤销最近一次提交",
        requires_confirmation=False,
        prerequisites=["文件已修改"]
    ),
    
    # 方案4: 解决main分支开发问题
    SolutionTemplate(
        template_id="SOL-004",
        problem_type=ProblemType.MAIN_BRANCH_DEV,
        approach="create_feature_branch",
        title="创建功能分支并迁移修改",
        description="创建新的功能分支，将当前修改迁移到功能分支",
        steps=[
            SolutionStepTemplate(
                order=1,
                command="git stash push -m 'migrate to feature branch'",
                description="暂存当前修改",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=2,
                command="git checkout -b feature/<feature-name>",
                description="创建并切换到功能分支",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=3,
                command="git stash pop",
                description="恢复修改到功能分支",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
        ],
        best_practice_reason="""
1. **隔离变更** - 功能分支隔离开发中的代码，不影响主分支
2. **便于审查** - 通过PR进行代码审查，提高代码质量
3. **支持并行开发** - 多人可同时开发不同功能，互不影响
4. **符合GitHub Flow** - 业界标准的分支策略
5. **易于回滚** - 功能分支可以随时删除，不影响主分支
        """.strip(),
        best_practice_references=[
            "https://docs.github.com/en/get-started/quickstart/github-flow",
            "https://nvie.com/posts/a-successful-git-branching-model/"
        ],
        risk_level=RiskLevel.LOW,
        risk_factors=["需要为功能分支命名"],
        rollback_plan="git checkout main && git branch -D feature/<name>",
        requires_confirmation=False,
        prerequisites=["在main分支上有未提交修改"]
    ),
    
    # 方案5: 配置分支保护
    SolutionTemplate(
        template_id="SOL-005",
        problem_type=ProblemType.NO_BRANCH_PROTECTION,
        approach="setup_branch_protection",
        title="配置分支保护规则",
        description="通过GitHub API配置main分支保护规则",
        steps=[
            SolutionStepTemplate(
                order=1,
                command="gh api -X PUT repos/{owner}/{repo}/branches/main/protection -f ...",
                description="配置分支保护规则",
                risk_level=RiskLevel.LOW,
                requires_confirmation=True
            ),
        ],
        best_practice_reason="""
1. **防止意外** - 禁止直接推送，避免意外破坏主分支
2. **强制审查** - 所有变更必须通过PR和代码审查
3. **保护历史** - 禁止force push，保护提交历史
4. **质量保证** - 可以要求CI通过才能合并
5. **符合最佳实践** - 业界标准的分支保护策略
        """.strip(),
        best_practice_references=[
            "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branch-protection-rules"
        ],
        risk_level=RiskLevel.LOW,
        risk_factors=["需要管理员权限"],
        rollback_plan="通过GitHub网页或API删除保护规则",
        requires_confirmation=True,
        prerequisites=["有GitHub管理员权限"]
    ),
    
    # 方案6: 解决CI失败
    SolutionTemplate(
        template_id="SOL-006",
        problem_type=ProblemType.CI_FAILURE,
        approach="fix_ci_failure",
        title="分析并修复CI失败",
        description="分析CI日志，定位问题并修复",
        steps=[
            SolutionStepTemplate(
                order=1,
                command="gh run view <run-id> --log",
                description="查看CI失败日志",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=2,
                command="# 根据日志分析问题类型",
                description="分析失败原因（测试/lint/构建）",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=3,
                command="# 修复代码问题",
                description="修复导致CI失败的代码",
                risk_level=RiskLevel.MEDIUM,
                requires_confirmation=True
            ),
            SolutionStepTemplate(
                order=4,
                command="git push",
                description="推送修复后重新触发CI",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
        ],
        best_practice_reason="""
1. **快速反馈** - CI失败应立即修复，避免影响他人
2. **质量保证** - CI是代码质量的最后一道防线
3. **可追溯** - 修复记录会被保存，便于回顾
4. **自动化** - 修复后CI自动重新运行，无需手动干预
        """.strip(),
        best_practice_references=[
            "https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/troubleshooting-workflows"
        ],
        risk_level=RiskLevel.MEDIUM,
        risk_factors=["可能需要修改代码", "可能影响其他功能"],
        rollback_plan="git revert 撤销修复提交",
        requires_confirmation=True,
        prerequisites=["有CI访问权限"]
    ),
    
    # 方案7: 解决合并冲突
    SolutionTemplate(
        template_id="SOL-007",
        problem_type=ProblemType.MERGE_CONFLICT,
        approach="resolve_conflicts",
        title="手动解决合并冲突",
        description="逐个文件解决冲突，确保合并正确性",
        steps=[
            SolutionStepTemplate(
                order=1,
                command="git status",
                description="查看冲突文件列表",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=2,
                command="# 打开冲突文件，手动编辑解决",
                description="逐个文件解决冲突",
                risk_level=RiskLevel.HIGH,
                requires_confirmation=True,
                conflict_handling="manual"
            ),
            SolutionStepTemplate(
                order=3,
                command="git add <resolved-files>",
                description="标记冲突已解决",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=4,
                command="git rebase --continue 或 git commit",
                description="继续变基或提交合并",
                risk_level=RiskLevel.MEDIUM,
                requires_confirmation=True
            ),
        ],
        best_practice_reason="""
1. **确保正确性** - 手动解决冲突可以确保合并结果正确
2. **理解变更** - 解决冲突的过程有助于理解双方变更
3. **避免错误** - 自动合并可能引入难以发现的错误
4. **团队沟通** - 冲突解决可能需要与原作者沟通
        """.strip(),
        best_practice_references=[
            "https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging"
        ],
        risk_level=RiskLevel.HIGH,
        risk_factors=[
            "可能引入错误",
            "需要理解双方代码",
            "可能需要与原作者沟通"
        ],
        rollback_plan="git rebase --abort 或 git merge --abort",
        requires_confirmation=True,
        prerequisites=["存在冲突文件"]
    ),
    
    # 方案8: 同步远程更新
    SolutionTemplate(
        template_id="SOL-008",
        problem_type=ProblemType.BEHIND_REMOTE,
        approach="pull_with_rebase",
        title="使用 rebase 方式拉取远程更新",
        description="拉取远程更新并变基本地提交",
        steps=[
            SolutionStepTemplate(
                order=1,
                command="git stash",
                description="暂存本地修改",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=2,
                command="git pull --rebase origin {branch}",
                description="拉取并变基",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
            SolutionStepTemplate(
                order=3,
                command="git stash pop",
                description="恢复本地修改",
                risk_level=RiskLevel.LOW,
                requires_confirmation=False
            ),
        ],
        best_practice_reason="""
1. **避免merge commit** - pull --rebase不会产生额外的merge commit
2. **保持历史整洁** - 线性历史更易读
3. **减少冲突** - 变基方式更容易处理冲突
4. **符合最佳实践** - 推荐的同步方式
        """.strip(),
        best_practice_references=[
            "https://git-scm.com/docs/git-pull#Documentation/git-pull.txt---rebasefalsemergetrue"
        ],
        risk_level=RiskLevel.LOW,
        risk_factors=["可能遇到冲突"],
        rollback_plan="git rebase --abort",
        requires_confirmation=False,
        prerequisites=["有网络连接"]
    ),
]
```

### 5.4 数据结构

```python
class SolutionPlan:
    """解决方案计划"""
    
    plan_id: str
    plan_time: datetime
    
    # 解决方案列表
    solutions: List['Solution']
    
    # 执行顺序（依赖关系）
    execution_order: List[str]  # solution_id列表
    
    # 统计信息
    total_steps: int
    estimated_duration_seconds: int
    total_risk: RiskLevel
    
    # 确认状态
    user_confirmed: bool
    confirmed_at: Optional[datetime]
    
    def get_solutions_by_risk(self, risk: RiskLevel) -> List['Solution']:
        """按风险等级获取解决方案"""
        return [s for s in self.solutions if s.risk_level == risk]
    
    def get_high_risk_steps(self) -> List['SolutionStep']:
        """获取所有高风险步骤"""
        steps = []
        for solution in self.solutions:
            steps.extend([s for s in solution.steps if s.risk_level == RiskLevel.HIGH])
        return steps


class Solution:
    """单个解决方案"""
    
    id: str  # "sol-001"
    problem_id: str  # 关联的问题ID
    template_id: str  # 使用的模板ID
    
    # 基本信息
    approach: str
    title: str
    description: str
    
    # 执行步骤
    steps: List['SolutionStep']
    
    # 最佳实践说明
    best_practice_reason: str
    best_practice_references: List[str]
    
    # 风险评估
    risk_level: RiskLevel
    risk_factors: List[str]
    rollback_plan: str
    
    # 执行控制
    requires_confirmation: bool
    can_auto_execute: bool
    prerequisites: List[str]
    
    # 执行状态
    status: 'SolutionStatus'
    executed_at: Optional[datetime]


class SolutionStep:
    """解决方案步骤"""
    
    step_id: str
    solution_id: str
    order: int
    
    # 命令信息
    command: str
    description: str
    expected_output: str
    
    # 风险控制
    risk_level: RiskLevel
    requires_confirmation: bool
    conflict_handling: str  # auto/manual/abort
    
    # 错误处理
    error_handling: str
    retry_count: int
    retry_delay_seconds: int
    
    # 执行状态
    status: 'StepStatus'
    executed_at: Optional[datetime]
    output: Optional[str]
    error: Optional[str]


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"        # 只读或安全操作
    MEDIUM = "medium"  # 常规操作
    HIGH = "high"      # 破坏性操作


class SolutionStatus(Enum):
    """解决方案状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    WAITING_CONFIRMATION = "waiting_confirmation"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CONFLICT = "conflict"
```

---

## 六、Executor（执行器）

### 6.1 功能描述

安全执行解决方案，处理确认流程和错误恢复

### 6.2 执行流程

```
┌─────────────────────────────────────────────────────────────┐
│                      Executor 执行流程                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   加载解决方案     │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   风险等级分类     │
                    └───────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   🟢 低风险   │     │   🟡 中风险   │     │   🔴 高风险   │
│   自动执行    │     │ 方案确认后执行 │     │   逐个确认    │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  错误处理/回滚    │
                    └───────────────────┘
```

### 6.3 执行策略

```python
class ExecutionStrategy:
    """执行策略配置"""
    
    # 🟢 低风险：自动执行（只读操作）
    LOW_RISK_AUTO = {
        "risk_level": RiskLevel.LOW,
        "auto_execute": True,
        "requires_confirmation": False,
        "timeout_seconds": 30,
        "retry_on_failure": True,
        "max_retries": 3,
        "commands": [
            "git status",
            "git log",
            "git branch",
            "git remote",
            "git stash list",
            "git fetch --dry-run",
            "gh pr list",
            "gh repo view",
            "gh run list",
            "gh issue list",
        ]
    }
    
    # 🟡 中风险：方案确认后自动执行（常规操作）
    MEDIUM_RISK_SEMI_AUTO = {
        "risk_level": RiskLevel.MEDIUM,
        "auto_execute": False,
        "requires_plan_confirmation": True,  # 需要确认整个方案
        "auto_proceed_after_confirm": True,  # 确认后自动执行所有步骤
        "timeout_seconds": 60,
        "retry_on_failure": True,
        "max_retries": 2,
        "commands": [
            "git stash",
            "git stash pop",
            "git pull",
            "git pull --rebase",
            "git push",
            "git checkout",
            "git checkout -b",
            "git add",
            "git commit",
            "git rebase",
            "git merge",
            "git branch",
        ]
    }
    
    # 🔴 高风险：逐个确认（破坏性操作）
    HIGH_RISK_MANUAL = {
        "risk_level": RiskLevel.HIGH,
        "auto_execute": False,
        "requires_step_confirmation": True,  # 每步都需确认
        "show_warning": True,
        "warning_message": "⚠️ 此操作具有破坏性，请确认后继续",
        "provide_rollback": True,
        "timeout_seconds": 120,
        "retry_on_failure": False,
        "commands": [
            "git push --force",
            "git push --force-with-lease",
            "git reset --hard",
            "git reset --soft",
            "git branch -D",
            "git clean -fd",
            "merge conflict resolution",
        ]
    }
```

### 6.4 错误处理器

```python
class ErrorHandler:
    """错误处理器"""
    
    def handle_error(self, error: 'ExecutionError') -> 'ErrorAction':
        """
        根据错误类型决定处理方式
        
        Args:
            error: 执行错误对象
            
        Returns:
            ErrorAction: 错误处理动作
        """
        
        # 网络错误：重试
        if error.error_type == ErrorType.NETWORK_ERROR:
            return ErrorAction(
                strategy=ErrorHandlingStrategy.RETRY,
                max_attempts=3,
                delay_seconds=5,
                message="网络连接失败，正在重试..."
            )
        
        # 权限错误：中止并提示
        elif error.error_type == ErrorType.PERMISSION_DENIED:
            return ErrorAction(
                strategy=ErrorHandlingStrategy.ABORT,
                message="权限不足，请检查GitHub token或SSH密钥配置",
                help_url="https://docs.github.com/en/authentication"
            )
        
        # 合并冲突：询问用户
        elif error.error_type in [ErrorType.MERGE_CONFLICT, ErrorType.REBASE_CONFLICT]:
            return ErrorAction(
                strategy=ErrorHandlingStrategy.ASK_USER,
                message="发现合并冲突，请选择处理方式",
                options=[
                    "手动解决冲突",
                    "中止操作",
                    "使用我们的版本",
                    "使用他们的版本"
                ],
                show_conflict_details=True
            )
        
        # 超时：重试或跳过
        elif error.error_type == ErrorType.TIMEOUT:
            return ErrorAction(
                strategy=ErrorHandlingStrategy.ASK_USER,
                message="操作超时，请选择处理方式",
                options=[
                    "重试",
                    "跳过此步骤",
                    "中止操作"
                ]
            )
        
        # 用户中止：回滚
        elif error.error_type == ErrorType.USER_ABORT:
            return ErrorAction(
                strategy=ErrorHandlingStrategy.ROLLBACK,
                message="用户中止操作，正在回滚..."
            )
        
        # 命令失败：根据严重性决定
        elif error.error_type == ErrorType.COMMAND_FAILED:
            if error.exit_code == 1:  # 轻微错误
                return ErrorAction(
                    strategy=ErrorHandlingStrategy.SKIP,
                    message="命令执行失败，跳过此步骤"
                )
            else:  # 严重错误
                return ErrorAction(
                    strategy=ErrorHandlingStrategy.ROLLBACK,
                    message="命令执行失败，正在回滚..."
                )
        
        # 未知错误：询问用户
        else:
            return ErrorAction(
                strategy=ErrorHandlingStrategy.ASK_USER,
                message=f"发生未知错误: {error.error_message}",
                options=[
                    "重试",
                    "跳过此步骤",
                    "中止操作",
                    "查看详细错误信息"
                ]
            )


class ErrorType(Enum):
    """错误类型"""
    NETWORK_ERROR = "network_error"           # 网络错误
    PERMISSION_DENIED = "permission_denied"   # 权限不足
    COMMAND_NOT_FOUND = "command_not_found"   # 命令不存在
    COMMAND_FAILED = "command_failed"         # 命令执行失败
    MERGE_CONFLICT = "merge_conflict"         # 合并冲突
    REBASE_CONFLICT = "rebase_conflict"       # 变基冲突
    TIMEOUT = "timeout"                       # 超时
    USER_ABORT = "user_abort"                 # 用户中止
    UNKNOWN = "unknown"                       # 未知错误


class ErrorHandlingStrategy(Enum):
    """错误处理策略"""
    RETRY = "retry"           # 重试
    SKIP = "skip"             # 跳过
    ROLLBACK = "rollback"     # 回滚
    ABORT = "abort"           # 中止
    ASK_USER = "ask_user"     # 询问用户
```

### 6.5 数据结构

```python
class ExecutionResult:
    """执行结果"""
    
    execution_id: str
    plan_id: str
    
    # 时间信息
    start_time: datetime
    end_time: datetime
    total_duration_ms: int
    
    # 步骤结果
    step_results: List['StepResult']
    
    # 整体状态
    status: 'ExecutionStatus'
    completed_steps: int
    failed_steps: int
    skipped_steps: int
    
    # 错误信息
    errors: List['ExecutionError']
    
    # 回滚信息
    rollback_available: bool
    rollback_commands: List[str]
    rollback_performed: bool
    
    # 冲突信息
    has_conflicts: bool
    conflicts: List['ConflictInfo']
    
    def is_success(self) -> bool:
        """是否成功"""
        return self.status == ExecutionStatus.SUCCESS


class StepResult:
    """单个步骤执行结果"""
    
    step_id: str
    solution_id: str
    order: int
    
    # 命令信息
    command: str
    description: str
    
    # 执行状态
    status: StepStatus
    
    # 输出
    stdout: str
    stderr: str
    exit_code: int
    
    # 时间
    start_time: datetime
    end_time: datetime
    duration_ms: int
    
    # 确认信息
    confirmation_requested: bool
    confirmation_response: Optional[str]
    confirmed_by: Optional[str]  # user/agent
    
    # 冲突信息
    has_conflict: bool
    conflicts: List['ConflictInfo']


class ConflictInfo:
    """冲突信息"""
    
    file_path: str
    conflict_type: str  # content/rename/delete/modify-delete
    
    # 冲突内容
    ours_version: str      # 我们的版本
    theirs_version: str    # 他们的版本
    base_version: str      # 共同祖先版本
    
    # 解决建议
    suggested_resolution: str
    resolution_options: List[str]
    
    # 解决状态
    resolved: bool
    resolution: Optional[str]
    resolved_by: Optional[str]


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    PARTIAL = "partial"      # 部分成功
    FAILED = "failed"
    ABORTED = "aborted"      # 用户中止
    ROLLED_BACK = "rolled_back"
```

---

## 七、学习系统设计

### 7.1 数据存储结构

```
.github/skill-data/github-manager/
├── history/                          # 历史记录
│   ├── 2026-03/
│   │   ├── 2026-03-22-001.json      # 每次执行记录
│   │   ├── 2026-03-22-002.json
│   │   └── ...
│   └── summary.json                  # 月度汇总
│
├── patterns/                         # 模式识别
│   ├── project-patterns.json         # 项目特定模式
│   ├── common-problems.json          # 常见问题库
│   ├── solution-effectiveness.json   # 方案有效性
│   └── branch-naming-patterns.json   # 分支命名模式
│
├── preferences/                      # 用户偏好
│   ├── user-preferences.json         # 用户偏好设置
│   └── confirmation-history.json     # 确认历史
│
├── learnings/                        # 学习成果
│   ├── best-practices.json           # 最佳实践积累
│   ├── failure-patterns.json         # 失败模式
│   └── success-patterns.json         # 成功模式
│
└── reports/                          # 报告存档
    ├── 2026-03/
    │   ├── 2026-03-22-001.md
    │   └── ...
    └── index.json                    # 报告索引
```

### 7.2 学习引擎

```python
class LearningEngine:
    """学习引擎"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.history_recorder = HistoryRecorder(data_dir)
        self.pattern_analyzer = PatternAnalyzer(data_dir)
        self.preference_learner = PreferenceLearner(data_dir)
        self.strategy_optimizer = StrategyOptimizer(data_dir)
    
    def learn_from_execution(self, execution_result: ExecutionResult) -> 'LearningOutput':
        """
        从执行结果中学习
        
        Args:
            execution_result: 执行结果
            
        Returns:
            LearningOutput: 学习输出
        """
        
        # 1. 记录历史
        self.history_recorder.record(execution_result)
        
        # 2. 分析模式
        patterns = self.pattern_analyzer.analyze(execution_result)
        
        # 3. 更新偏好
        preferences = self.preference_learner.update(execution_result)
        
        # 4. 优化策略
        optimizations = self.strategy_optimizer.optimize(execution_result)
        
        return LearningOutput(
            patterns_discovered=patterns,
            preferences_updated=preferences,
            optimizations=optimizations
        )
    
    def get_recommendations(self, context: 'ExecutionContext') -> List['Recommendation']:
        """
        基于学习结果提供推荐
        """
        
        recommendations = []
        
        # 1. 基于历史推荐
        history_recs = self._get_history_based_recommendations(context)
        recommendations.extend(history_recs)
        
        # 2. 基于模式推荐
        pattern_recs = self._get_pattern_based_recommendations(context)
        recommendations.extend(pattern_recs)
        
        # 3. 基于偏好推荐
        preference_recs = self._get_preference_based_recommendations(context)
        recommendations.extend(preference_recs)
        
        return recommendations
```

### 7.3 学习维度

| 维度 | 学习内容 | 应用场景 |
|------|---------|---------|
| 项目模式 | 常用分支名、提交风格、工作流习惯 | 自动推荐分支名、提交信息 |
| 问题频率 | 哪些问题经常出现 | 主动预防常见问题 |
| 方案有效性 | 哪些解决方案效果最好 | 优先推荐高效方案 |
| 用户偏好 | 用户喜欢的操作方式 | 调整自动化程度 |

---

## 八、报告输出规范

### 8.1 Markdown报告模板

```markdown
# 📊 GitHub管理报告

**生成时间**: {generated_at}
**项目**: {project_name}
**执行ID**: {execution_id}

---

## 1️⃣ GitHub状态扫描

### 1.1 本地状态

| 项目 | 状态 | 详情 |
|------|------|------|
| 当前分支 | `{current_branch}` | {branch_status} |
| 工作区状态 | {workspace_status} | {uncommitted_count} 个未提交文件 |
| 未推送提交 | {unpushed_commits} | 领先远程 {unpushed_commits} 个提交 |
| 分支状态 | {diverged_status} | {diverged_detail} |

### 1.2 远程状态

| 项目 | 状态 | 详情 |
|------|------|------|
| 活跃PR | {active_prs} 个 | {pr_list} |
| CI状态 | {ci_status} | {ci_detail} |
| 分支保护 | {branch_protection_status} | {protection_detail} |

---

## 2️⃣ 发现的问题

**问题统计**: 共发现 {total_problems} 个问题
- 🔴 高优先级: {high_count} 个
- 🟡 中优先级: {medium_count} 个
- 🟢 低优先级: {low_count} 个

### 问题 #{problem_number}: {problem_title} {severity_emoji}

**问题描述**: {description}
**根本原因**: {root_cause}
**影响范围**: {impact}

---

## 3️⃣ 解决方案

### 方案 #{solution_number}: {solution_title}

**执行步骤**:

| 步骤 | 命令 | 描述 | 风险 | 需确认 |
|------|------|------|------|--------|
| 1 | `git stash` | 备份当前工作 | 🟢 低 | 否 |
| 2 | `git fetch origin` | 获取远程更新 | 🟢 低 | 否 |
| 3 | `git rebase origin/main` | 变基到远程分支 | 🟡 中 | 是 |

**为什么是最佳实践**: {best_practice_reason}

---

## 4️⃣ 执行结果

| 操作 | 状态 | 耗时 | 备注 |
|------|------|------|------|
| git stash | ✅ 成功 | 0.5s | 已暂存34个文件 |
| git fetch origin | ✅ 成功 | 1.2s | 获取远程更新 |
| git rebase origin/main | ⚠️ 冲突 | - | 发现3个冲突文件 |

---

## 5️⃣ 最佳实践学习

### 1. 分支管理最佳实践

**规则**: 永远不要直接在main分支上开发

**为什么重要**: main分支应始终保持稳定可部署状态

**正确做法**:
```bash
git checkout -b feature/your-feature
```

---

## 6️⃣ 下一步建议

- [ ] 解决合并冲突后继续rebase
- [ ] 创建功能分支提交当前变更
- [ ] 配置pre-commit hooks

---

**报告生成完成** ✅
```

### 8.2 JSON数据结构

报告同时生成JSON格式数据，包含：
- `report_meta`: 报告元数据
- `scan_results`: 扫描结果
- `problems_found`: 发现的问题
- `solutions_proposed`: 解决方案
- `execution_results`: 执行结果
- `learnings`: 学习成果

---

## 九、GitHub最佳实践规范

### 9.1 分支策略

```
main (受保护)
  │
  ├── develop (开发集成分支)
  │     │
  │     ├── feature/xxx (功能分支)
  │     ├── fix/xxx (修复分支)
  │     ├── refactor/xxx (重构分支)
  │     └── docs/xxx (文档分支)
  │
  └── release/x.x.x (发布分支)
```

**为什么是最佳实践**:
1. **main始终稳定** - 可随时部署到生产环境
2. **功能隔离** - 每个功能独立开发，互不影响
3. **便于审查** - PR范围明确，审查效率高
4. **支持并行开发** - 多人可同时开发不同功能

### 9.2 提交信息规范

```
<type>(<scope>): <subject>

类型：feat/fix/docs/refactor/test/chore
```

**为什么是最佳实践**:
1. **自动化changelog** - 工具可自动生成变更日志
2. **便于搜索** - 按类型/范围快速定位提交
3. **规范历史** - 历史记录清晰易读
4. **业界标准** - 被广泛采用

### 9.3 分支保护规则

| 规则 | 设置 | 原因 |
|------|------|------|
| Require PR | ✅ | 防止直接推送 |
| Required approvals | 1 | 确保代码审查 |
| Dismiss stale reviews | ✅ | 新提交需重新审查 |
| Require status checks | ✅ | CI必须通过 |
| Enforce admins | ✅ | 管理员也需遵守 |
| Allow force pushes | ❌ | 保护历史 |
| Allow deletions | ❌ | 保护分支 |

---

## 十、Skill触发条件

```yaml
name: github-manager
description: |
  智能GitHub项目管理助手，自动扫描、分析、解决GitHub相关问题。
  
  触发条件：
  - 用户提到 "github"、"git"、"分支"、"PR"、"pull request"、"合并"、"冲突"
  - 用户遇到git操作问题（如push失败、merge冲突）
  - 用户需要创建分支、提交代码、创建PR
  - 用户询问GitHub最佳实践
  - 用户想要检查项目GitHub状态
  
  功能：
  - 自动扫描GitHub状态（本地+远程+配置）
  - 智能分析问题并设计解决方案
  - 自动执行操作（低/中风险自动，高风险确认）
  - 生成规范化报告（Markdown+JSON）
  - 持续学习优化建议质量
  - 传授GitHub最佳实践
```

---

## 十一、实施计划

### Phase 1: 核心模块实现
- [ ] 创建SKILL.md主文件
- [ ] 实现Scanner模块（扫描命令+数据结构）
- [ ] 实现Analyzer模块（问题规则库+分析逻辑）
- [ ] 实现Solver模块（解决方案模板+最佳实践验证）
- [ ] 实现Executor模块（执行策略+错误处理+回滚）

### Phase 2: 报告和学习系统
- [ ] 实现Reporter模块（Markdown模板+JSON生成）
- [ ] 实现Learner模块（历史记录+模式分析+偏好学习）
- [ ] 创建报告模板文件
- [ ] 配置数据存储目录

### Phase 3: 测试和优化
- [ ] 编写测试用例（单元测试+集成测试）
- [ ] 运行评估（测试prompt+结果验证）
- [ ] 优化触发准确性（description优化）
- [ ] 文档完善（使用指南+最佳实践）

---

## 十二、附录

### A. 方案C：智能代理设计

完整的设计文档请参阅：
`docs/superpowers/specs/2026-03-22-github-manager-skill-design-plan-c.md`

方案C包含：
- 状态机设计（完整状态转换表）
- 决策引擎（规则匹配+权重学习）
- 多代理协作（6个独立代理）
- 共享知识库（订阅通知机制）

### B. 相关文档

- [GitHub设置指南](../../development/github-setup-guide.md)
- [分支保护配置](../../../scripts/github/branch-protection.json)
- [PR模板](../../../.github/pull_request_template.md)
- [CI/CD工作流](../../../.github/workflows/ci-cd.yml)

---

**文档版本**: 1.0.0
**最后更新**: 2026-03-22
**状态**: 待用户审核
