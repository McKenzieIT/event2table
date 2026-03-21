# Scanner 扫描器模块

完整的GitHub状态扫描命令和解析规则。

---

## 一、扫描流程

### 1.1 本地扫描（必须按顺序执行）

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

**命令4**: `git log --oneline -5`
- 用途: 获取最近提交历史
- 输出解析: 每行格式为 `{hash} {message}`
- 存储到: `local_state.recent_commits`

**命令5**: `git stash list`
- 用途: 检查暂存区
- 输出解析: 每行格式为 `stash@{N}: {message}`
- 存储到: `local_state.stashes`

### 1.2 远程扫描（必须有网络，超时30秒）

**降级策略**: 如果网络不可用或超时：
1. 跳过远程扫描
2. 在报告中标注"远程状态未知"
3. 仅基于本地状态提供建议

**命令执行规则**:
- 每个命令最多等待30秒
- 失败后不重试，继续下一个
- 记录失败原因到 `scan_errors`

**命令1**: `git fetch origin --dry-run`
- 用途: 检测远程更新（不实际fetch）
- 输出解析: 有输出表示有更新
- 存储到: `remote_state.has_updates`

**命令2**: `gh pr list --state all --limit 10 --json number,title,state,author,headRefName,baseRefName`
- 用途: 获取PR列表
- 输出解析: JSON格式，直接解析
- 存储到: `remote_state.active_prs`

**命令3**: `gh run list --limit 3 --json conclusion,status,name,createdAt`
- 用途: 获取CI状态
- 输出解析: 检查 `conclusion` 字段
- 存储到: `remote_state.ci_status`

**命令4**: `gh repo view --json branchProtectionRules`
- 用途: 检查分支保护规则
- 输出解析: JSON格式，检查rules数组
- 存储到: `remote_state.branch_protection`

### 1.3 配置扫描（5秒内完成）

**命令1**: `test -f .github/pull_request_template.md`
- 用途: 检查PR模板
- 存储到: `project_config.has_pr_template`

**命令2**: `ls .github/workflows/*.yml`
- 用途: 检查CI配置
- 存储到: `project_config.ci_configs`

**命令3**: `test -f .github/CODEOWNERS`
- 用途: 检查CODEOWNERS
- 存储到: `project_config.has_codeowners`

---

## 二、扫描结果数据结构

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
    "diverged": false,
    "recent_commits": [
      {"hash": "abc123", "message": "feat: add feature"}
    ],
    "stashes": []
  },
  "remote_state": {
    "has_updates": true,
    "active_prs": [
      {
        "number": 42,
        "title": "Add feature",
        "state": "open",
        "author": "user",
        "headRefName": "feature/xxx",
        "baseRefName": "main"
      }
    ],
    "ci_status": {
      "status": "success",
      "last_run": "2026-03-22T10:00:00Z"
    },
    "branch_protection": {
      "enabled": true,
      "rules": ["require_pull_request", "require_status_checks"]
    }
  },
  "project_config": {
    "has_pr_template": true,
    "ci_configs": ["ci.yml", "deploy.yml"],
    "has_codeowners": true
  },
  "has_issues": true,
  "scan_errors": []
}
```

---

## 三、大仓库优化

如果检测到仓库文件数 > 1000：

**优化策略**:
```bash
# 跳过未跟踪文件
git status --porcelain --untracked-files=no

# 加速提交历史
git log --oneline -5 --no-walk

# 限制diff输出
git diff --stat HEAD~1
```

**提示用户**:
```markdown
⚠️ 检测到大仓库（{file_count} 个文件），扫描可能需要较长时间。
建议使用 `--untracked-files=no` 参数加速。
```

---

## 四、错误处理

| 错误 | 处理方式 |
|------|---------|
| `git: command not found` | 提示用户安装git |
| `not a git repository` | 提示用户初始化git |
| `gh: command not found` | 跳过GitHub CLI相关扫描 |
| `network timeout` | 降级为本地扫描 |
| `permission denied` | 提示用户检查权限 |

---

**模块版本**: 1.0.0
