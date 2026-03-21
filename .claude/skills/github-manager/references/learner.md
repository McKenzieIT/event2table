# Learner 学习器模块

用户偏好学习系统，持续优化建议质量。

---

## 一、学习数据存储结构

```
.github/skill-data/github-manager/
├── history/                          # 历史记录
│   ├── 2026-03/
│   │   ├── 2026-03-22-001.json      # 每次执行记录
│   │   ├── 2026-03-22-002.json
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

---

## 二、学习维度

### 2.1 项目模式学习

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
      "usage_count": {"feature": 15, "fix": 5, "refactor": 3},
      "last_updated": "2026-03-22T10:00:00Z"
    },
    "commit_style": {
      "style": "conventional_commits",
      "examples": ["feat: add new feature", "fix: resolve bug"],
      "confidence": 0.95,
      "last_updated": "2026-03-22T10:00:00Z"
    },
    "workflow_habits": {
      "avg_commits_before_pr": 5,
      "preferred_merge_method": "squash",
      "pr_review_preference": "self_review_first"
    }
  }
}
```

### 2.2 问题频率学习

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
      "related_problems": ["MERGE_CONFLICT"],
      "avg_resolution_time_seconds": 120,
      "last_occurred": "2026-03-22T10:00:00Z"
    },
    "UNCOMMITTED_CHANGES": {
      "frequency": 0.5,
      "conditions": ["active_development"],
      "avg_file_count": 15,
      "last_occurred": "2026-03-22T10:00:00Z"
    }
  }
}
```

### 2.3 方案有效性学习

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
      "common_issues": ["conflict_resolution_needed"],
      "total_uses": 20,
      "successful_uses": 17
    },
    "git_merge": {
      "success_rate": 0.95,
      "user_preference": 0.3,
      "avg_duration_seconds": 45,
      "common_issues": ["merge_commit_created"],
      "total_uses": 10,
      "successful_uses": 9
    },
    "batch_commit": {
      "success_rate": 0.90,
      "user_preference": 0.8,
      "avg_duration_seconds": 60,
      "common_issues": ["commit_message_format"],
      "total_uses": 15,
      "successful_uses": 13
    }
  }
}
```

### 2.4 用户偏好学习

**学习内容**:
- 自动化程度偏好
- 确认频率偏好
- 报告格式偏好
- 解决方案偏好

**应用场景**:
```json
{
  "user_preferences": {
    "automation_level": "semi_auto",
    "confirmation_frequency": "medium_risk_only",
    "report_format": "detailed",
    "report_mode": "summary",
    "preferred_solutions": {
      "BRANCH_DIVERGED": "git_rebase",
      "UNCOMMITTED_CHANGES": "batch_commit",
      "BEHIND_REMOTE": "pull_with_rebase"
    },
    "branch_naming_template": "feature/{issue-number}-{description}",
    "commit_message_template": "{type}: {description}",
    "last_updated": "2026-03-22T10:00:00Z"
  }
}
```

---

## 三、学习应用

### 3.1 每次执行后

**记录历史**:
1. 保存执行详情到 `history/YYYY-MM/YYYY-MM-DD-NNN.json`
2. 更新月度汇总 `summary.json`

**更新模式**:
1. 更新分支命名统计
2. 更新问题频率
3. 更新方案有效性

**优化建议**:
1. 基于历史推荐常用分支名
2. 基于有效性优先推荐高效方案
3. 基于偏好调整自动化程度

### 3.2 学习应用示例

**场景1: 推荐分支名**
```python
# 基于历史学习
if user_preferences.branch_naming_template:
    suggested_name = user_preferences.branch_naming_template.format(
        issue_number=issue_number,
        description=short_description
    )
else:
    # 基于最常用模式
    suggested_name = f"{most_used_pattern}/{short_description}"
```

**场景2: 选择解决方案**
```python
# 基于用户偏好
if problem.type in user_preferences.preferred_solutions:
    solution = user_preferences.preferred_solutions[problem.type]
else:
    # 基于有效性
    solution = max(
        SOLUTIONS[problem.type],
        key=lambda s: solution_effectiveness[s]['success_rate']
    )
```

**场景3: 调整自动化程度**
```python
# 基于用户偏好
if user_preferences.automation_level == "full_auto":
    auto_execute = True
elif user_preferences.automation_level == "semi_auto":
    auto_execute = risk_level in ["low", "medium"]
else:  # manual
    auto_execute = risk_level == "low"
```

---

## 四、数据过期机制

### 4.1 自动清理规则

| 数据类型 | 保留期限 | 清理策略 |
|---------|---------|---------|
| 历史记录 | 90天 | 自动删除超过90天的记录 |
| 模式数据 | 180天 | 权重衰减，不删除 |
| 偏好数据 | 永久 | 权重衰减，不删除 |
| 学习成果 | 永久 | 定期合并优化 |

### 4.2 权重衰减

```python
def apply_weight_decay(preferences: Dict) -> Dict:
    """应用权重衰减，使旧数据影响降低"""
    for key, value in preferences.items():
        if 'last_updated' in value:
            days_since_update = (datetime.now() - value['last_updated']).days
            decay_factor = 0.99 ** days_since_update  # 每天衰减1%
            value['weight'] *= decay_factor
            
            # 如果权重过低，移除
            if value['weight'] < 0.1:
                del preferences[key]
    
    return preferences
```

---

## 五、学习效果验证

### 5.1 A/B测试机制

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

### 5.2 效果追踪

```json
{
  "learning_effectiveness": {
    "period": "2026-03",
    "metrics": {
      "solution_success_rate": {
        "with_learning": 0.85,
        "without_learning": 0.70,
        "improvement": 0.15
      },
      "user_satisfaction": {
        "with_learning": 4.5,
        "without_learning": 3.8,
        "improvement": 0.7
      },
      "avg_resolution_time": {
        "with_learning": 180,
        "without_learning": 480,
        "improvement": 300
      }
    }
  }
}
```

---

## 六、隐私保护

### 6.1 数据脱敏规则

| 数据类型 | 脱敏方式 |
|---------|---------|
| 文件路径 | 仅保留文件名，移除完整路径 |
| 提交信息 | 仅保留类型（feat/fix），移除具体内容 |
| 分支名称 | 仅保留模式（feature/*），移除具体名称 |

### 6.2 脱敏示例

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

### 6.3 用户控制

- 用户可随时清除学习数据
- 用户可选择不参与学习
- 用户可导出/删除个人数据

---

## 七、学习输出示例

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

### 偏好更新
- 已记录您偏好使用 `git rebase` 解决分支分叉
- 已记录您偏好使用 `batch_commit` 处理大量未提交文件
- 已记录您偏好 `summary` 模式报告
```

---

**模块版本**: 1.0.0
