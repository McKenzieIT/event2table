# 归档文档索引自动化 - 用户指南

**版本**: 1.0
**最后更新**: 2026-03-14

---

## 🎯 自动化概述

归档文档索引系统提供了**三种自动化方式**，确保索引始终与文档保持同步：

### 三种自动化方式

| 方式 | 触发时机 | 适用场景 | 性能影响 |
|------|---------|---------|---------|
| **Git Pre-commit Hook** | 提交代码时自动触发 | ✅ 日常开发（推荐） | 无影响 |
| **文件监控后台服务** | 文件保存时实时触发 | ✅ 长时间开发会话 | 极低 |
| **手动触发命令** | 需要时手动执行 | ✅ 批量更新、CI/CD | 无影响 |

---

## 方式1: Git Pre-commit Hook ⭐ 推荐

### 工作原理

每次执行 `git commit` 时，pre-commit hook会自动：
1. 检测是否有归档文档变更
2. 自动运行索引生成脚本
3. 将更新后的索引添加到本次提交

### 使用方法

**无需任何配置！** Hook已自动安装到 `.git/hooks/pre-commit`

**正常提交即可**：
```bash
# 添加归档文档
git add docs/archive/2026/03-march/reports/NEW-REPORT.md

# 提交（Hook会自动更新索引）
git commit -m "Add new report"

# 查看提交内容（索引已自动包含）
git show --stat
```

### 输出示例

```
📚 Check 5/5: Archive document index update...
检测到归档文档变更，自动更新索引...
  📄 docs/archive/2026/03-march/reports/NEW-REPORT.md
🔍 开始扫描归档文档...
✅ 找到 66 个归档文档
✅ 分类完成，共 11 个主题
✅ 评分完成: ⭐⭐⭐×25 ⭐⭐×35 ⭐×6
✅ Archive index updated and staged!
```

### 跳过Hook检查

如果需要跳过索引更新（不推荐）：
```bash
git commit --no-verify -m "Add report without index update"
```

---

## 方式2: 文件监控后台服务

### 工作原理

后台监控服务会实时监测 `docs/archive/` 目录：
- 使用 **fswatch** 实时监控（推荐）
- 或使用 **polling模式** 每5秒检查一次（备选）

### 安装fswatch（推荐）

```bash
# macOS
brew install fswatch

# Linux
sudo apt-get install fswatch  # Ubuntu/Debian
sudo yum install fswatch      # CentOS/RHEL
```

### 启动监控服务

**终端1** - 启动监控：
```bash
cd /Users/mckenzie/Documents/event2table

# 启动后台监控
bash scripts/docs/monitor-archive-index.sh &

# 或使用nohup（关闭终端后继续运行）
nohup bash scripts/docs/monitor-archive-index.sh > logs/archive-monitor.log 2>&1 &
```

**终端2** - 正常开发：
```bash
# 编辑归档文档
vim docs/archive/2026/03-march/reports/NEW-REPORT.md

# 保存后，监控服务会自动更新索引
# 无需手动操作！
```

### 监控服务输出

```
📚 Archive Index Monitor
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
监控目录: docs/archive/
使用方法:
  后台运行: bash scripts/docs/monitor-archive-index.sh &
  停止监控: pkill -f monitor-archive-index.sh
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 使用fswatch监控（实时响应）
监控中... (Ctrl+C停止)

[2026-03-14 10:30:15] 检测到归档文档变更
原因: 文件系统变化检测
🔍 开始扫描归档文档...
✅ 找到 66 个归档文档
✅ 评分完成: ⭐⭐⭐×25 ⭐⭐×35 ⭐×6
✅ 索引已更新
```

### 停止监控服务

```bash
# 查找监控进程
ps aux | grep monitor-archive-index

# 停止监控
pkill -f monitor-archive-index.sh

# 或使用Ctrl+C（如果在前台运行）
```

### 适用场景

- ✅ **长时间开发会话**：一天内多次修改归档文档
- ✅ **团队协作**：多人同时修改归档文档
- ✅ **CI/CD集成**：需要实时更新索引

---

## 方式3: 手动触发命令

### 工作原理

使用Python脚本直接生成索引，无需任何自动化工具。

### 使用方法

```bash
# 进入项目目录
cd /Users/mckenzie/Documents/event2table

# 运行索引生成脚本
python3 scripts/tools/generate_topic_index.py
```

### 输出示例

```
🔍 开始扫描归档文档...
✅ 找到 66 个归档文档
✅ 分类完成，共 11 个主题
✅ 评分完成: ⭐⭐⭐×25 ⭐⭐×35 ⭐×6

📊 文档分类统计:
   Canvas相关: 4 个 (⭐⭐⭐×2 ⭐⭐×1 ⭐×1)
   Chrome MCP: 3 个 (⭐⭐⭐×2 ⭐×1)
   E2E测试: 10 个 (⭐⭐⭐×2 ⭐⭐×8)
   ...

📝 生成主题索引...
✅ 主题索引已生成: docs/archive/TOPIC_INDEX.md
   总文档数: 66 个
   主题数量: 11 个
   手动调整: 0 个

🔍 验证索引质量...
✅ 所有文档已正确分类和评分 (66/66)
```

### 适用场景

- ✅ **批量更新**：一次性添加多个文档
- ✅ **CI/CD集成**：在部署时生成索引
- ✅ **手动验证**：检查索引是否正确

---

## 🔄 三种方式对比

| 特性 | Git Hook | 文件监控 | 手动触发 |
|------|----------|---------|---------|
| **自动程度** | 提交时自动 | 实时自动 | 需手动执行 |
| **性能影响** | 无 | 极低 | 无 |
| **实时性** | 提交时 | 保存时 | 需要时 |
| **配置复杂度** | 无（已预装） | 需安装fswatch | 无需配置 |
| **适用场景** | 日常开发 | 长时会话 | 批量更新 |

---

## 🎓 最佳实践

### 日常开发

**推荐：使用 Git Pre-commit Hook**

```bash
# 1. 正常编辑归档文档
vim docs/archive/2026/03-march/reports/NEW-REPORT.md

# 2. 添加到Git
git add docs/archive/2026/03-march/reports/NEW-REPORT.md

# 3. 提交（Hook自动更新索引）
git commit -m "Add new report"
```

**优势**：
- ✅ 无需额外配置
- ✅ 零性能影响
- ✅ 索引自动包含在提交中

### 长时会话开发

**推荐：使用文件监控后台服务**

```bash
# 终端1：启动监控
bash scripts/docs/monitor-archive-index.sh &

# 终端2：正常开发
# 编辑文档后自动更新索引，无需任何操作
```

**优势**：
- ✅ 实时更新（保存即更新）
- ✅ 无需手动操作
- ✅ 适合长时间开发

### 批量更新

**推荐：使用手动触发命令**

```bash
# 1. 添加多个文档到归档
mv report1.md docs/archive/2026/03-march/reports/
mv report2.md docs/archive/2026/03-march/reports/

# 2. 手动生成索引
python3 scripts/tools/generate_topic_index.py

# 3. 提交
git add docs/archive/
git commit -m "Add multiple reports"
```

**优势**：
- ✅ 一次性更新多个文档
- ✅ 完全可控
- ✅ 适合CI/CD集成

---

## ❓ 常见问题

### Q1: Git Hook失败怎么办？

**问题**: 提交时Hook执行失败，阻止提交

**解决方案**:
```bash
# 1. 查看详细错误信息
git commit -m "Test"

# 2. 如果是索引生成失败，手动运行
python3 scripts/tools/generate_topic_index.py

# 3. 添加生成的索引
git add docs/archive/TOPIC_INDEX.md

# 4. 重新提交
git commit -m "Add report"
```

### Q2: 文件监控不工作？

**问题**: 保存文档后索引未更新

**解决方案**:
```bash
# 1. 检查fswatch是否安装
fswatch --version

# 2. 如果未安装，安装fswatch
brew install fswatch  # macOS
sudo apt-get install fswatch  # Linux

# 3. 重启监控服务
pkill -f monitor-archive-index.sh
bash scripts/docs/monitor-archive-index.sh &
```

### Q3: 如何禁用自动化？

**问题**: 想要手动控制索引更新

**解决方案**:
```bash
# 方式1: 跳过Git Hook
git commit --no-verify -m "Add report without index update"

# 方式2: 停止文件监控
pkill -f monitor-archive-index.sh

# 方式3: 手动更新索引
python3 scripts/tools/generate_topic_index.py
```

### Q4: 索引更新后如何验证？

**验证方法**:
```bash
# 1. 查看索引文件
cat docs/archive/TOPIC_INDEX.md

# 2. 检查评分统计
grep "评分统计" docs/archive/TOPIC_INDEX.md -A 5

# 3. 验证文档数量
grep "文档总数" docs/archive/TOPIC_INDEX.md
```

---

## 📝 相关文档

- **[评分系统用户指南](SCORING-SYSTEM-USER-GUIDE.md)** - 如何使用文档评分系统
- **[实施完成报告](../../DOCUMENT-SCORING-SYSTEM-IMPLEMENTATION-REPORT.md)** - 评分系统实施详情
- **[设计文档](../../plans/2026-03-13-archive-organization-design.md)** - 归档组织设计

---

**文档维护者**: Event2Table Development Team
**下次更新**: 2026-04-14
**反馈渠道**: 提交Issue或Pull Request
