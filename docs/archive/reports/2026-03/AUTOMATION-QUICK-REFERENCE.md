# update-docs Automation - Quick Reference Guide

> **Version**: 2.0.0
> **Date**: 2026-03-23
> **Status**: Active

---

## 🎯 Overview

The update-docs skill now provides **full automation** for the complete document lifecycle:

1. **Code Change Detection** → **Document Updates** → **Duplicate Detection** → **Experience Extraction** → **Auto-Archiving** → **Index Regeneration** → **Knowledge Graph Updates**

**Total Time**: 25-64 seconds (average 35 seconds)

---

## 🚀 Quick Start

### Basic Usage

```bash
# Full automation (all 7 phases)
/update-docs

# Selective execution
/update-docs --update-only        # Phase 1-2 only
/update-docs --integrate          # Phase 3-4 only
/update-docs --archive            # Phase 5 only
/update-docs --update-indexes     # Phase 6 only
/update-docs --kg-only            # Phase 7 only

# Dry-run mode (preview changes)
/update-docs --dry-run
```

### Index Management

```bash
# Force regenerate docs/README.md
/update-docs --regenerate-main-index

# Update lessons-learned/README.md
/update-docs --update-lessons-index
```

### Experience Extraction

```bash
# Extract experiences from reports
/update-docs --extract-experience

# Extract from specific document
/update-docs --extract --target docs/reports/fix-report.md
```

### Auto-Archiving

```bash
# Auto-archive all candidates (6+ months old)
/update-docs --archive --auto

# Archive specific document
/update-docs --archive --target docs/old-doc.md

# Preview archiving (dry-run)
/update-docs --archive --dry-run
```

---

## 📊 7-Phase Workflow Details

### Phase 1: 变更检测 (2-3秒)

**Detection Methods**:
- Git diff analysis
- AST semantic analysis
- Commit message keyword matching

**Output**: List of changed files and affected documents

### Phase 2: 文档更新 (3-5秒)

**Update Actions**:
- API endpoint changes → `docs/api/`
- Architecture changes → `docs/development/`
- Feature changes → Feature-specific docs
- Metadata updates (date, version)

**Smart Mapping**:
```
backend/api/routes/       → docs/api/
backend/services/         → docs/development/
frontend/src/features/    → docs/development/
backend/services/hql/     → docs/hql/
backend/core/cache/       → docs/cache/
```

### Phase 3: 重复检测 (5-10秒)

**Detection**:
- Cross-document similarity analysis (TF-IDF + cosine similarity)
- Threshold: 0.7 similarity

**Actions**:
- Identify semantic duplicates
- Detect outdated/conflicting documents
- Generate integration report

### Phase 4: 经验提取 (5-8秒)

**Extraction Patterns**:
```python
# Problem-Solution Pair Detection
problem_pattern = r"##?\s*[问题|Problem|Issue]\s*\n+(.+?)(?=##?\s*[解决|Solution|Fix])"
solution_pattern = r"##?\s*[解决|Solution|Fix]\s*\n+(.+?)(?=##|\Z)"
```

**Category Mapping**:
```python
{
    "React": "react-best-practices.md",
    "GraphQL": "api-design-patterns.md",
    "Testing": "testing-guide.md",
    "Security": "security-essentials.md",
    "Performance": "performance-patterns.md",
    # ... etc
}
```

### Phase 5: 自动归档 (2-3秒)

**Archive Conditions**:
- Documents 6+ months stale
- Temporary reports completed
- Duplicate content integrated

**Archive Structure**:
```
archive/
├── reports/{date}/
├── implementation-reports/{date}/
├── performance/{date}/
├── testing/{date}/
└── general/{date}/
```

**Archive Stamp**:
```markdown
---

> **Archived**: 2026-03-23
> **Reason**: Older than 6 months
> **Original Location**: docs/reports/old-report.md

---
```

**Whitelist Protection**:
- README.md (never archived)
- CLAUDE.md (never archived)
- CHANGELOG.md (never archived)

### Phase 6: 索引更新 (3-5秒)

**Updated Indexes**:
- `docs/README.md` - Main documentation index
- `docs/lessons-learned/README.md` - Experience documentation index

**Statistics**:
- Total subdirectories: 26
- Total documents: 1107
- Active documents: 737 (66.5%)
- Archived documents: 370 (33.5%)

### Phase 7: 知识图谱更新 (5-30秒)

**Update Modes**:
- **Incremental** (normal): <5 seconds
  - Only updates changed documents
  - Increments counter (+1/+2/...)

- **Full Detection** (every 10 updates): <30 seconds
  - Node integrity check
  - Recalculate document similarity
  - Detect orphan nodes
  - Fix broken links
  - Reset counter

**Knowledge Graph Stats**:
- Nodes: 1045 (6 types)
- Edges: 6385 (9 relationship types)
- Incremental counter: 0-10/10

---

## 🔧 Configuration

### Configuration File

Location: `.claude/skills/update-docs/kg/storage/kg_update_config.json`

```json
{
  "automation": {
    "auto_archive": true,
    "archive_threshold_months": 6,
    "auto_extract_experience": true,
    "auto_update_indexes": true,
    "auto_update_kg": true
  },
  "index_generation": {
    "docs_readme": {
      "enabled": true,
      "template": "docs/README.md",
      "output": "docs/README.md"
    },
    "lessons_learned_readme": {
      "enabled": true,
      "output": "docs/lessons-learned/README.md"
    }
  },
  "duplicate_detection": {
    "similarity_threshold": 0.7,
    "auto_integrate": false,
    "require_confirmation": true
  }
}
```

---

## 📈 Automation Report Example

```markdown
# 文档自动化报告 - 2026-03-23

## 执行概览
- 总耗时: 35秒
- 执行阶段: 7/7 (100%)

## Phase 1: 变更检测
- 变更文件: 3 个
- 影响文档: 2 个

## Phase 2: 文档更新
- 更新文档: 2 个
- ✅ docs/api/README.md
- ✅ docs/development/architecture.md

## Phase 3: 重复检测
- 检测文档: 1107 个
- 发现重复: 0 个
- 相似度计算: 6153 对

## Phase 4: 经验提取
- 提取经验: 1 条
- 目标文档: docs/lessons-learned/react-best-practices.md
- 经验标题: React Hooks 规则最佳实践

## Phase 5: 自动归档
- 归档候选: 0 个
- 白名单保护: 3 个文档

## Phase 6: 索引更新
- ✅ docs/README.md 已更新
- ✅ docs/lessons-learned/README.md 已更新
- 内部链接验证: 全部有效

## Phase 7: 知识图谱更新
- 更新模式: 增量更新
- 节点变更: +1, ~2, -0
- 边变更: +5, -0
- 累积更新计数: 8/10
- 下次全面检测: 还需 2 次更新

## 总结
✅ 所有阶段完成
✅ 无错误
✅ 文档库已同步
```

---

## 🎯 Common Use Cases

### Use Case 1: After Code Changes

```bash
# Make code changes
git add .
git commit -m "feat: add new API endpoint"

# Run full automation
/update-docs
```

**Result**: All documentation updated automatically

### Use Case 2: Extract Experience from Bug Fix

```bash
# Create fix report
# docs/reports/2026-03-23/bug-fix-report.md

# Extract experience automatically
/update-docs --extract-experience
```

**Result**: Experience added to appropriate lessons-learned/ document

### Use Case 3: Clean Up Old Documents

```bash
# Auto-archive stale documents
/update-docs --archive --auto
```

**Result**: 6+ month old documents moved to archive/

### Use Case 4: Update Documentation Index

```bash
# After adding new documentation subdirectory
/update-docs --update-indexes
```

**Result**: docs/README.md regenerated with new subdirectory

---

## 🔍 Knowledge Graph Integration

### Query Commands

```bash
# Quick problem lookup
/kg:query "GraphQL 400错误"

# Find related documents
/kg:related doc:react-best-practices

# Visualize knowledge graph
/kg:visualize --output kg-vis.html
```

### Update Modes

- **Incremental**: Runs after each `/update-docs`
- **Full Detection**: Runs every 10th `/update-docs`

---

## ✅ Benefits

1. **Zero Manual Effort**: Complete document lifecycle automation
2. **Consistency**: All indexes and graphs stay synchronized
3. **Time Savings**: 35 seconds vs hours of manual work
4. **Quality**: Eliminates human error and omissions
5. **Self-Maintaining**: Auto-archives stale documents, keeps docs fresh

---

## 🚨 Important Notes

- **Whitelisted Files**: README.md, CLAUDE.md, CHANGELOG.md never archived
- **Dry-Run Mode**: Always preview changes first with `--dry-run`
- **Knowledge Graph**: Automatically updated, no manual sync needed
- **Index Updates**: Automatic, but can force with `--update-indexes`

---

## 📚 Related Documentation

- **[update-docs SKILL.md](../../.claude/skills/update-docs/SKILL.md)** - Full skill documentation
- **[docs/README.md](../../docs/README.md)** - Main documentation index
- **[lessons-learned/README.md](../../docs/lessons-learned/README.md)** - Experience documentation index
- **[Implementation Plan](../../../.claude/plans/typed-crunching-lake.md)** - Design and implementation details

---

**Maintained By**: update-docs skill v2.0
**Last Updated**: 2026-03-23

---

> **Archived**: 2026-03-24
> **Reason**: 临时报告，经验已提取到lessons-learned
> **Original Location**: docs/reports/2026-03-23/AUTOMATION-QUICK-REFERENCE.md

---
