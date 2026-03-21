# Executor 执行器模块

执行策略和错误处理，确保安全可靠地执行解决方案。

---

## 一、执行策略（风险分级）

### 🟢 低风险操作 - 自动执行

**条件**: 风险等级 = LOW 且 命令是只读的

**自动执行的命令**:
- `git status`, `git log`, `git branch`, `git remote`
- `git stash list`, `git fetch --dry-run`
- `gh pr list`, `gh repo view`, `gh run list`
- `ls`, `cat`, `head`, `tail` (只读文件操作)

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
- `gh pr create`, `gh pr merge`

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
- 分支保护配置

**执行方式**:
1. 每步执行前展示命令和风险警告
2. 等待用户明确确认
3. 用户可随时中止
4. 超时设置: 120秒
5. 不自动重试，失败后询问用户

---

## 二、用户确认格式规范

### 确认方式

**用户必须使用以下任一格式**:

| 用户输入 | 含义 | 适用场景 |
|---------|------|---------|
| "继续" / "y" / "yes" / "确认" | 继续执行当前步骤 | 默认确认 |
| "跳过" / "s" / "skip" | 跳过当前步骤 | 不想执行某步骤 |
| "中止" / "a" / "abort" | 中止整个方案 | 不想继续执行 |
| "详情" / "d" / "detail" | 查看更多详情 | 想了解更多信息 |
| "回滚" / "r" / "rollback" | 执行回滚 | 想撤销已执行的操作 |

### 确认提示格式

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

---

## 三、进度反馈机制

### 进度显示格式

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

### 进度条设计

```markdown
# 总进度
[████████████████░░░░] 80% (4/5 问题已解决)

# 当前方案进度
[████████░░░░░░░░░░░░] 40% (2/5 步骤已完成)

# 预计剩余时间
预计剩余时间: 2分钟
```

---

## 四、错误处理策略

### 错误类型与处理方式

| 错误类型 | 处理策略 | 用户提示 | 重试次数 |
|---------|---------|---------|---------|
| NETWORK_ERROR | 自动重试 | "网络连接失败，正在重试..." | 3次 |
| PERMISSION_DENIED | 中止执行 | "权限不足，请检查GitHub token或SSH密钥配置" | 0次 |
| MERGE_CONFLICT | 询问用户 | "发现合并冲突，请选择处理方式" | 0次 |
| TIMEOUT | 询问用户 | "操作超时，请选择：重试/跳过/中止" | 用户决定 |
| USER_ABORT | 回滚 | "用户中止操作，正在回滚..." | 0次 |
| COMMAND_FAILED | 根据严重性决定 | "命令执行失败：{error}" | 2次 |
| PREREQUISITE_NOT_MET | 准备或跳过 | "前提条件不满足，请先..." | 0次 |

### 错误处理流程

```markdown
### ⚠️ 执行失败

命令: `{command}`
错误: {error_message}

**选择处理方式**:
A. 重试 - 再次尝试执行此命令
B. 跳过 - 跳过此步骤继续执行
C. 中止 - 停止整个方案并回滚
D. 详情 - 查看完整错误日志
```

---

## 五、冲突处理流程

### 5.1 冲突检测

当检测到合并冲突时：

```markdown
### ⚠️ 发现合并冲突

以下文件需要手动解决：
- src/file1.ts (content conflict)
- src/file2.ts (modify/delete conflict)

**选择处理方式**:
A. 手动解决冲突（推荐）- 我会指导你逐个文件解决
B. 使用我们的版本 - 保留本地修改
C. 使用他们的版本 - 使用远程版本
D. 中止操作 - 执行回滚
```

### 5.2 手动解决指导

```markdown
### 解决冲突: src/file1.ts

打开文件，你会看到：

```
<<<<<<< HEAD
本地版本代码
=======
远程版本代码
>>>>>>> origin/main
```

**解决方式**:
1. 删除冲突标记（<<<<<<<, =======, >>>>>>>）
2. 保留你想要的代码
3. 保存文件
4. 运行 `git add src/file1.ts`

完成后告诉我 "继续" 或 "done"。
```

### 5.3 自动解决选项

**使用本地版本**:
```bash
git checkout --ours src/file1.ts
git add src/file1.ts
```

**使用远程版本**:
```bash
git checkout --theirs src/file1.ts
git add src/file1.ts
```

---

## 六、回滚机制

### 6.1 回滚失败处理

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
git reflog
git reset --hard HEAD@{N}

# 如果是stash相关问题
git stash list
git stash drop stash@{0}
```

3. **如果无法恢复**:
- 请联系项目维护者
- 或提供以下信息以便诊断：
  - `git status` 输出
  - `git reflog` 输出
  - 错误信息截图
```

### 6.2 回滚命令映射

| 操作 | 回滚命令 |
|------|---------|
| `git stash` | `git stash pop` |
| `git rebase` | `git rebase --abort` 或 `git reset --hard ORIG_HEAD` |
| `git merge` | `git merge --abort` 或 `git reset --hard ORIG_HEAD` |
| `git checkout` | `git checkout {previous_branch}` |
| `git commit` | `git reset --soft HEAD~1` |
| `git reset --hard` | `git reset --hard ORIG_HEAD`（如果可用） |

---

## 七、执行锁机制

### 7.1 锁规则

**防止并发冲突**:

- 如果正在执行 `git rebase`，禁止同时执行 `git merge`
- 如果正在执行 `git stash`，禁止同时执行 `git reset`
- 如果两个问题需要修改同一文件，必须串行执行

### 7.2 锁冲突处理

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

---

## 八、执行输出格式

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
      "duration_ms": 500,
      "retry_count": 0
    }
  ],
  "completed_steps": 4,
  "failed_steps": 0,
  "skipped_steps": 0,
  "rollback_available": true,
  "rollback_commands": ["git stash pop"],
  "errors": [],
  "warnings": []
}
```

---

**模块版本**: 1.0.0
