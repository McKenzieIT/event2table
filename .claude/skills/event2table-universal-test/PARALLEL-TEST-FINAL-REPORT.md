# 并行测试优化最终报告

> **日期**: 2026-03-19
> **任务**: 并行修复超时问题并增加超时时间；使用agent-browser的并行功能加速测试
> **结论**: agent-browser 架构不支持真正的并行执行

---

## 📊 执行结果对比

| 执行方式 | 通过率 | 执行时间 | 资源冲突 | 结论 |
|---------|--------|----------|----------|------|
| **串行执行** | **74.4% (29/39)** | ~8分钟 | 无 | ✅ **推荐** |
| **完全并行 (4 workers)** | 7.7% (3/39) | 8.5分钟 | 严重 | ❌ 不可用 |
| **Session并行 (2 workers)** | 5.1% (2/39) | 11.4分钟 | 严重 | ❌ 不可用 |
| **混合策略 (批次5×并行3)** | 56.4% (22/39) | 8.5分钟 | 中等 | ⚠️ 可用但不理想 |

---

## 🔍 根本原因分析

### agent-browser 的架构限制

**设计理念**：
- agent-browser 使用**单一 daemon 进程**管理**单个浏览器实例**
- daemon 通过固定的 WebSocket 端口（默认9222）与浏览器通信
- 所有命令都通过同一个 daemon 串行执行

**并行执行的问题**：
1. **端口冲突**：多个并行进程尝试连接同一个 daemon 端口
2. **资源竞争**：多个测试同时向 daemon 发送命令，造成命令混乱
3. **状态污染**：多个测试共享同一个浏览器实例，状态互相干扰
4. **进程泄漏**：异常退出时，daemon 和浏览器进程没有正确清理

**尝试的解决方案**：

**方案1：完全并行（ThreadPoolExecutor + subprocess）**
```python
with ThreadPoolExecutor(max_workers=4) as executor:
    future = executor.submit(execute_single_test, test_file)
```
- ❌ **结果**：92.3% 失败率
- **原因**：多个 subprocess 同时调用 agent-browser CLI，全部竞争同一个 daemon

**方案2：Session隔离（每个测试独立session）**
```python
session_id = f"test_{test_id}_{uuid.uuid4().hex[:8]}"
cmd = f'agent-browser --session {session_id} open {url}'
```
- ❌ **结果**：94.9% 失败率，更慢
- **原因**：每个 session 创建独立的浏览器实例，消耗大量资源，反而加剧冲突

**方案3：混合策略（批次并行 + 批次内串行）**
```python
# 将39个测试分成8个批次（每批5个）
# 最多3个批次并行执行
# 每批内串行执行
```
- ⚠️ **结果**：56.4% 失败率，可用但不理想
- **原因**：批次之间仍然存在资源竞争，但比完全并行好很多

---

## 💡 最终建议

### 推荐方案：**串行执行**

**理由**：
1. ✅ **稳定性最高**：74.4% 通过率
2. ✅ **无资源冲突**：每个测试独立执行
3. ✅ **调试友好**：失败时容易定位问题
4. ✅ **执行时间可接受**：~8分钟（不是瓶颈）

**使用方式**：
```bash
# 使用原始的串行脚本
python3 /Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/scripts/run-all-tests.py

# 或使用 skill
/event2table-universal-test
```

### 备选方案：混合策略（仅在CI/CD环境）

**适用场景**：
- CI/CD 环境需要快速反馈
- 可以接受较低的通过率
- 有专门的测试服务器

**配置建议**：
```python
BATCH_SIZE = 8  # 增加批次大小减少批次数量
MAX_PARALLEL_BATCHES = 2  # 减少并行批次降低资源冲突
```

**使用方式**：
```bash
python3 /Users/mckenzie/Documents/event2table/scripts/run-all-tests-hybrid.py
```

---

## 🛠️ 已完成的优化

### ✅ 1. URL修复（相对→绝对）

**问题**：5个测试使用相对URL导致超时
**解决**：自动转换 `"/"` → `"http://localhost:5173/"`
**脚本**：`fix-test-urls.py`
**结果**：5个测试文件全部修复

### ✅ 2. 超时时间增加

**问题**：10秒超时太短
**解决**：增加到30秒（测试级）+ 15秒（步骤级）
**结果**：超时问题大幅减少

### ✅ 3. 混合策略实现

**问题**：完全并行不可用
**解决**：批次并行 + 批次内串行
**脚本**：`run-all-tests-hybrid.py`
**结果**：56.4% 通过率（比完全并行好7倍）

---

## 📝 agent-browser 的正确使用方式

### ✅ 推荐用法

**1. 串行执行测试**
```bash
for test in tests; do
    agent-browser open $url
    agent-browser wait --load networkidle
    agent-browser eval "document.title"
    agent-browser screenshot result.png
done
```

**2. 使用 batch 批量命令**
```bash
echo '[
    ["open", "https://example.com"],
    ["wait", "--load", "networkidle"],
    ["eval", "document.title"]
]' | agent-browser batch --json
```

**3. Session管理（手动切换）**
```bash
# Session 1
agent-browser --session site1 open https://site-a.com
agent-browser --session site1 snapshot

# Session 2（手动切换，不是并行）
agent-browser --session site2 open https://site-b.com
agent-browser --session site2 snapshot
```

### ❌ 避免的用法

**1. 多进程并行调用 agent-browser**
```python
# ❌ 错误：会导致 daemon 冲突
with ThreadPoolExecutor(max_workers=4) as executor:
    executor.submit(lambda: subprocess.run("agent-browser open url1"))
    executor.submit(lambda: subprocess.run("agent-browser open url2"))
```

**2. 同时操作多个 session**
```python
# ❌ 错误：session 不是为并行设计的
for i in range(4):
    session = f"test{i}"
    subprocess.run(f"agent-browser --session {session} open url")
```

**3. 频繁创建和销毁 session**
```bash
# ❌ 错误：会导致资源泄漏
for i in {1..100}; do
    agent-browser --session test$i open url
    agent-browser --session test$i close
done
```

---

## 🔧 故障排除

### 清理遗留进程

```bash
# 查看进程数量
ps aux | grep agent-browser | grep -v grep | wc -l

# 清理所有 agent-browser 进程
pkill -f "agent-browser"

# 验证清理结果
ps aux | grep agent-browser | grep -v grep
```

### 检查 daemon 状态

```bash
# 查看 agent-browser session 列表
agent-browser session list

# 关闭所有 session
agent-browser close
```

### 调试并行问题

```bash
# 监控进程数量
watch -n 1 'ps aux | grep agent-browser | grep -v grep | wc -l'

# 监控端口占用
lsof -i :9222
```

---

## 📚 经验总结

### 关键学习点

1. **架构理解优先**：在尝试并行化之前，必须理解工具的架构设计
2. **串行 > 并行**：如果工具不支持并行，串行执行往往比强行并行更可靠
3. **资源清理重要**：并行测试必须确保进程正确清理，否则会累积资源冲突
4. **渐进式优化**：从串行 → 混合 → 完全并行，逐步测试可行性

### agent-browser 的定位

**适合的场景**：
- ✅ 单个浏览器自动化
- ✅ 串行执行多个任务
- ✅ 批量命令执行（batch）
- ✅ 手动切换 session（非并行）

**不适合的场景**：
- ❌ 真正的并行执行
- ❌ 多个独立浏览器实例
- ❌ 高并发测试场景

---

## 🎯 最终结论

**agent-browser 不适合真正的并行测试执行**。虽然我们实现了混合策略（56.4% 通过率），但串行执行仍然是最可靠的选择（74.4% 通过率）。

**推荐工作流**：
1. **本地开发**：使用串行执行（`run-all-tests.py`）
2. **CI/CD**：考虑混合策略（`run-all-tests-hybrid.py`），但需要接受较低的通过率
3. **未来改进**：考虑迁移到支持并行的测试框架（如 Playwright）

---

**报告生成时间**: 2026-03-19 00:20:00
**报告版本**: 1.0
**作者**: Claude Code (Event2Table Team)
