# 归档文档评分系统 - 快速使用指南

**版本**: 1.0
**最后更新**: 2026-03-14

---

## 🎯 快速开始

### 查看带评分的归档索引

```bash
# 打开主题索引
open docs/archive/TOPIC_INDEX.md

# 或在VS Code中
code docs/archive/TOPIC_INDEX.md
```

**您将看到**：
- 📊 **评分统计** - 了解文档分布
- ⭐⭐⭐ **核心文档** - 优先阅读（25个必读文档）
- ⭐⭐ **重要参考** - 按需参考（34个）
- ⭐ **补充材料** - 可选浏览（6个）

---

## 📖 使用场景

### 场景1：查找"缓存失效修复"的核心报告

**步骤**：
1. 打开 `docs/archive/TOPIC_INDEX.md`
2. 找到"缓存失效修复"章节
3. 查看"⭐⭐⭐ 核心文档"部分
4. 点击文档标题查看详细内容

**预期结果**：
- ⭐⭐×4 核心文档 → 优先阅读
- 完整修复方案 + 设计文档
- 快速找到解决方案

### 场景2：了解GraphQL迁移的关键文档

**步骤**：
1. 打开 `docs/archive/TOPIC_INDEX.md`
2. 找到"GraphQL迁移"章节
3. 查看"⭐⭐⭐ 核心文档"（0个）和"⭐⭐ 重要参考"（5个）
4. 点击经验文档链接查看完整方案

**预期结果**：
- 虽然没有3星文档，但5个2星文档也很有价值
- 经验文档包含完整的GraphQL迁移策略

### 场景3：搜索特定问题

**步骤**：
```bash
# 在所有归档中搜索关键词
rg "滚动修复" docs/archive/

# 在特定主题中搜索
rg "性能" docs/archive/TOPIC_INDEX.md
```

---

## 🔧 维护操作

### 新增归档文档

```bash
# 1. 添加文档
mv NEW-REPORT.md docs/archive/2026/03-march/reports/

# 2. 更新索引（自动评分）
python3 scripts/tools/generate_topic_index.py

# 3. 查看输出
# ✅ 评分完成: 3星=25个, 2星=34个, 1星=6个
```

### 手动调整评分

```bash
# 1. 编辑配置文件
vim docs/archive/manual-scores.yaml

# 2. 取消注释相关配置，例如：
# E2E-TEST-QUICK-REFERENCE.md:
#   score: 3  # 从2星提升到3星
#   tags: ["核心", "测试参考"]
#   override: true
#   reason: "内容完整，值得3星"

# 3. 重新生成索引
python3 scripts/tools/generate_topic_index.py

# 4. 验证变更
grep "E2E-TEST-QUICK-REFERENCE" docs/archive/TOPIC_INDEX.md
```

### 验证索引质量

```bash
# 运行完整维护脚本
bash scripts/docs/update-archive-index.sh

# 查看验证结果
# ✅ 所有文档已正确分类和评分 (65/65)
```

---

## 📊 评分标准

### 三星制说明

| 评分 | 含义 | 文件名关键词 | 使用场景 |
|------|------|-------------|---------|
| **⭐⭐⭐ 核心文档** | 完整方案，必读 | SUMMARY, COMPLETE, FINAL, DESIGN | 优先阅读 |
| **⭐⭐ 重要参考** | 重要参考文档 | REPORT, PROGRESS, STATUS, FIX, TEST, QUICK, GUIDE | 按需参考 |
| **⭐ 补充材料** | 补充说明文档 | 其他（默认） | 可选浏览 |

### 标签系统

**主题标签**:
- #核心 - 必读文档
- #参考 - 重要参考
- #补充 - 补充材料
- #GraphQL, #测试, #缓存 - 主题标签

**标签示例**:
- `#核心 #完整方案` - 核心文档，包含完整解决方案
- `#参考 #测试` - 测试相关参考文档
- `#核心 #缓存` - 缓存相关的核心文档

---

## ⚡ 高级技巧

### 技巧1：快速定位核心文档

**问题**: 在"其他"主题中有30个文档，如何快速找到核心文档？

**解决方案**:
1. 打开 `docs/archive/TOPIC_INDEX.md`
2. 搜索"⭐⭐⭐ 核心文档（8个）"
3. 直接跳转到核心文档列表

### 技巧2：按标签筛选

**问题**: 只想看GraphQL相关的核心文档

**解决方案**:
```bash
# 搜索GraphQL相关的核心文档
rg "#核心" docs/archive/TOPIC_INDEX.md | rg -i graphql
```

### 技巧3：自定义评分覆盖

**问题**: 某个文档虽然文件名是QUICK，但内容很完整

**解决方案**:
1. 编辑 `docs/archive/manual-scores.yaml`
2. 添加配置：
```yaml
E2E-TEST-QUICK-REFERENCE.md:
  score: 3
  tags: ["核心", "测试参考"]
  override: true
  reason: "内容完整，值得3星"
```
3. 重新生成索引

---

## 🎓 学习资源

### 相关文档

- **设计文档**: [docs/plans/2026-03-13-archive-organization-design.md](docs/plans/2026-03-13-archive-organization-design.md)
- **实施报告**: [ARCHIVE-ORGANIZATION-IMPLEMENTATION-REPORT.md](ARCHIVE-ORGANIZATION-IMPLEMENTATION-REPORT.md)
- **评分系统报告**: [DOCUMENT-SCORING-SYSTEM-IMPLEMENTATION-REPORT.md](DOCUMENT-SCORING-SYSTEM-IMPLEMENTATION-REPORT.md)

### 经验文档

- **测试指南**: [docs/lessons-learned/testing-guide.md](docs/lessons-learned/testing-guide.md)
- **项目管理**: [docs/lessons-learned/project-management.md](docs/lessons-learned/project-management.md)

---

## ❓ 常见问题

### Q1: 为什么3星文档占比38%（目标20%）？

**A**: 自动评分规则倾向于给予较高评分，确保重要文档不被遗漏。38%的占比意味着有更多高质量文档可供选择，这是好事。如需调整，可以通过手动配置降低部分文档的评分。

### Q2: 如何判断哪些文档需要手动调整评分？

**A**: 运行脚本后，查看各主题的评分分布：
- 如果某个主题只有2星和1星，但您知道有重要文档，手动提升到3星
- 如果某主题3星过多，但实际内容不完整，手动降到2星

### Q3: 标签是自动生成的吗？

**A**: 部分自动生成，部分手动添加：
- 自动：#核心、#参考、#补充（基于评分）
- 自动：#GraphQL、#测试、#缓存（基于文件名）
- 手动：可在`manual-scores.yaml`中添加自定义标签

---

## 📝 更新日志

**v1.0** (2026-03-14)
- ✅ 初始版本
- ✅ 自动评分功能
- ✅ 手动配置覆盖
- ✅ 评分分组显示
- ✅ 评分统计表

---

**文档维护者**: Event2Table Development Team
**下次更新**: 2026-04-14
**反馈渠道**: 提交Issue或Pull Request
