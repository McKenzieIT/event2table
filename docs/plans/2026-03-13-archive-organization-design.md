# 归档文档深度组织 - 设计文档

**日期**: 2026-03-13
**方案**: 方案B - 混合组织（日期 + 主题标签）
**目标**: 为829个归档文档添加主题索引，支持快速查找

---

## 一、背景

### 问题
- docs/archive/ 下有829个归档文档
- 按日期组织，但不适合按主题查找
- 偶尔需要浏览历史文档时，难以快速定位

### 用户需求
- **使用频率**: 很少使用（D）
- **使用场景**: 偶尔浏览（C）
- **核心痛点**: 想找特定主题的历史报告时，不知道是哪个月份

---

## 二、方案选择

### 为什么选择方案B（混合组织）

**对比三个方案**:

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **A. 纯日期** | 简单、易维护 | 难以按主题查找 | 主要按日期查找 |
| **B. 混合** ⭐ | 两维查找、维护成本低 | 需要维护索引 | 偶尔按主题浏览 |
| **C. 纯主题** | 最适合主题查找 | 高工作量、失去时间线 | 频繁按主题浏览 |

**选择方案B的理由**：
1. ✅ 保留日期结构（历史追溯）
2. ✅ 添加主题查找（快速定位）
3. ✅ 工作量适中（4-6小时）
4. ✅ 维护成本低（只需维护索引）

---

## 三、核心设计

### 目录结构

**保持现有结构不变**，只添加主题索引：

```
docs/archive/
├── TOPIC_INDEX.md        ← 新增：主题索引（跨月份）
├── README.md             ← 更新：添加主题索引链接
└── 2026/
    └── 03-march/
        └── reports/      ← 文件不动
            ├── CACHE-*.md
            ├── GRAPHQL-*.md
            └── ...
```

### 主题分类

**6大主题类别**：

1. **GraphQL迁移** (12个文档)
   - 迁移总结、完成报告
   - 性能监控、DataLoader优化
   - 批量操作、订阅功能

2. **E2E测试** (9个文档)
   - 测试报告
   - Chrome MCP相关
   - 修复验证

3. **缓存失效修复** (5个文档)
   - 修复报告、设计文档
   - 最终报告

4. **测试覆盖率** (5个文档)
   - 覆盖率报告
   - 测试分类

5. **Chrome MCP** (3个文档)
   - Modal修复
   - 快速总结

6. **TDD实践** (2个文档)
   - Red/Green阶段
   - 完成报告

7. **其他** (19个文档)
   - 配置管理、滚动修复等

---

## 四、实施步骤

### 步骤1：分析归档文档（30分钟）

```bash
# 扫描所有归档文档
find docs/archive/ -name "*.md" -type f | sort

# 统计各月份文档数量
find docs/archive/2026/03-march/reports/ -name "*.md" | wc -l
# 输出：55个（已知）

# 分析文件名模式
ls docs/archive/2026/03-march/reports/ | grep -i "graphql\|cache\|test\|e2e"
```

### 步骤2：创建主题分类（1-2小时）

**使用Python脚本自动分类**：

```python
# scripts/tools/generate_topic_index.py
import os
import re
from pathlib import Path
from collections import defaultdict

ARCHIVE_DIR = Path("docs/archive/2026/03-march/reports")
OUTPUT_FILE = Path("docs/archive/TOPIC_INDEX.md")

TOPIC_KEYWORDS = {
    "GraphQL迁移": ["GRAPHQL", "graphql"],
    "E2E测试": ["E2E", "e2e", "TEST"],
    "缓存失效修复": ["CACHE", "cache"],
    "测试覆盖率": ["COVERAGE", "coverage"],
    "Chrome MCP": ["CHROME.*MCP", "chrome"],
    "TDD实践": ["TDD", "tdd"],
    "配置管理": ["CONFIG", "config"],
    "滚动修复": ["SCROLL.*FIX", "scroll"],
}

def classify_document(filename):
    """根据文件名分类文档"""
    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if re.search(keyword, filename, re.IGNORECASE):
                return topic
    return "其他"

def generate_index():
    """生成主题索引"""
    documents = [f.name for f in ARCHIVE_DIR.glob("*.md")]
    topics = defaultdict(list)

    for doc in sorted(documents):
        topic = classify_document(doc)
        topics[topic].append(doc)

    # 生成Markdown
    output = ["# 归档文档主题索引\n", "> 按主题快速查找历史文档\n\n"]

    for topic, docs in sorted(topics.items()):
        output.append(f"## {topic} ({len(docs)}个文档)\n")

        # 关联经验文档
        if "GraphQL" in topic:
            output.append("**经验文档**：[api-design-patterns.md](../lessons-learned/api-design-patterns.md)\n")
        elif "E2E" in topic or "测试" in topic:
            output.append("**经验文档**：[testing-guide.md](../lessons-learned/testing-guide.md)\n")
        elif "缓存" in topic:
            output.append("**经验文档**：[performance-patterns.md](../lessons-learned/performance-patterns.md)\n")

        output.append("\n")

        for doc in docs:
            output.append(f"- [{doc}](2026/03-march/reports/{doc})\n")

        output.append("\n---\n")

    OUTPUT_FILE.write_text("".join(output), encoding="utf-8")
    print(f"✅ 主题索引已生成: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_index()
```

### 步骤3：更新主索引（30分钟）

在 `docs/archive/README.md` 中添加：

```markdown
## 快速查找 🔍

### 按主题查找 ⭐ **推荐**
- 📋 **[主题索引](TOPIC_INDEX.md)** - 按主题快速查找所有归档文档

### 按日期查找
- 2026年3月 (55个报告) → [2026/03-march/README.md](2026/03-march/README.md)
```

### 步骤4：验证和测试（30分钟）

```bash
# 1. 检查主题索引是否存在
ls -lh docs/archive/TOPIC_INDEX.md

# 2. 验证文档数量
echo "主题索引中的文档数量:"
grep -c "^- \[" docs/archive/TOPIC_INDEX.md

echo "实际归档的文档数量:"
find docs/archive/2026/03-march/reports/ -name "*.md" | wc -l
```

---

## 五、维护策略

### 自动化维护

**月度维护脚本**：`scripts/docs/update-archive-index.sh`

```bash
#!/bin/bash
# 每月初自动更新归档索引

echo "🔄 开始更新归档索引..."

# 重新生成主题索引
python3 scripts/tools/generate_topic_index.py

echo "✅ 归档索引更新完成！"
```

### 手动维护流程

**新增归档文档时**：
1. 移动文档到归档目录
2. 运行 `python3 scripts/tools/generate_topic_index.py`
3. 验证链接

---

## 六、成功标准

实施完成后，应该能够：

1. ✅ **在30秒内找到任何主题的归档文档**
   - 打开 `docs/archive/TOPIC_INDEX.md`
   - 浏览到对应主题章节
   - 点击链接打开文档

2. ✅ **了解所有归档文档的主题分布**
   - 查看主题索引的章节列表
   - 了解每个主题的文档数量

3. ✅ **发现相关历史经验**
   - 通过主题关联发现相关文档
   - 通过经验文档链接找到完整方案

4. ✅ **维护索引成本低**
   - 新增文档后运行一个脚本
   - 自动更新主题索引

---

## 七、后续优化

### 短期（1-2个月）
- 添加文档评分系统（⭐⭐⭐标记重要文档）
- 添加文档关联（相关文档链接）

### 中期（3-6个月）
- 全文搜索集成（ripgrep）
- 文档标签系统（YAML元数据）

### 长期（6个月+）
- 知识图谱构建（可视化文档关系）
- 智能推荐系统（基于上下文推荐）
- 文档版本管理（git历史）

---

## 八、实施时间表

| 阶段 | 任务 | 预计时间 | 优先级 |
|------|------|---------|--------|
| **Phase 1** | 步骤1-2：分析和分类 | 1.5小时 | P0 |
| **Phase 2** | 步骤3-4：生成索引 | 1.5小时 | P0 |
| **Phase 3** | 步骤5：验证测试 | 0.5小时 | P0 |
| **Phase 4** | 自动化脚本 | 1小时 | P1 |
| **Phase 5** | 质量保证 | 0.5小时 | P1 |
| **总计** | | **5-6小时** | |

---

**设计文档版本**: 1.0
**最后更新**: 2026-03-13
**状态**: ✅ 已批准，准备执行
