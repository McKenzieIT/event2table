---
name: update-docs
description: 文档管理工具 - 自动检测代码变更并更新文档（git status、修改文件后）；整合重复文档并提取经验到docs/lessons-learned/；分析文档相似度并归档过时内容；创建文档索引（API索引、文档中心）；批量更新多个受影响的文档；执行文档合规性审计。必须在使用git后、修改代码后、发现文档重复时、需要归档旧文档时、文档太多需要整理时使用此技能。当用户提到文档、更新、整合、归档、索引、重复、经验、git status时必须使用此技能。
---

# update-docs Skill - 智能文档管理系统

全面的文档管理工具，确保项目文档与代码保持同步、组织清晰、经验可复用。

## 核心功能

### 1. 智能代码变更检测与文档更新

**变更检测方式**：
- Git Diff 分析未提交的代码变更
- AST 语义分析理解代码结构
- 提交信息和注释关键词匹配

**文档更新动作**：
- 自动识别变更影响的目标文档
- 生成文档更新内容（API端点、功能说明、架构变更等）
- 应用更新并记录变更日志

### 2. 文档整合与去重 ⭐

**检测重复内容**：
- 跨文档相似度分析
- 识别语义重复但表述不同的内容
- 检测过时或冲突的文档

**整合策略**：
- 合并重复文档到单一权威来源
- 提取共同经验到经验文档系统
- 建立文档引用关系而非重复内容
- 更新所有引用到新的权威位置

**经验提取**：
- 从整合过程中识别可复用的经验模式
- 自动提取到对应的经验文档（`docs/lessons-learned/`）
- 更新 CLAUDE.md 中的经验索引

### 3. 文档归档管理 ⭐

**归档触发条件**：
- 文档 6 个月未更新
- 功能已废弃或移除
- 临时性文档已完成使命
- 重复内容已整合

**归档流程**：
- 移动文档到 `docs/archive/{主题}/{日期}/`
- 添加归档说明和日期戳
- 更新文档索引和引用
- 清理断开的内部链接

**归档结构**：
```
docs/archive/
├── 2026/
│   ├── 03-march/
│   │   ├── reports/
│   │   ├── testing/
│   │   └── development/
│   └── ...
├── reports/
├── testing/
└── development/
```

### 4. 文档索引维护

**自动维护**：
- 更新 `docs/README.md` 主索引
- 维护 `docs/lessons-learned/README.md` 经验索引
- 更新 CLAUDE.md 中的文档引用

**链接验证**：
- 检测断开的内部链接
- 验证外部引用的可用性
- 生成链接健康报告

### 5. 文档合规性审计

**检查项目**：
- 文档命名规范（小写+连字符）
- 文档位置规范（正确的目录结构）
- 必需章节完整性（API文档需要示例等）
- Markdown 格式规范

**输出报告**：
```
.claude/skills/update-docs/output/
├── audits/
│   └── compliance-YYYY-MM-DD.md
├── updates/
│   └── update-log-YYYY-MM-DD.md
└── integration/
    └── integration-report-YYYY-MM-DD.md
```

## 使用方式

### 基本用法

```bash
# 完整流程：检测变更 → 更新文档 → 整合重复 → 归档过时
/update-docs

# 仅更新文档（不整合/归档）
/update-docs --update-only

# 仅整合重复文档
/update-docs --integrate

# 仅归档过时文档
/update-docs --archive

# 预览模式（不实际修改）
/update-docs --dry-run
```

### 高级用法

```bash
# 文档合规性审计
/update-docs --audit

# 手动指定要更新的文档
/update-docs --manual docs/api/README.md

# 强制整合特定目录
/update-docs --integrate --target docs/reports/

# 归档特定文档
/update-docs --archive --target docs/old-doc.md

# 详细模式（显示所有操作）
/update-docs --verbose
```

## 文档映射规则

### 代码 → 文档映射

| 代码位置 | 目标文档 | 更新动作 |
|---------|---------|---------|
| `backend/api/routes/` | `docs/api/` | 添加/更新 API 端点文档 |
| `backend/services/` | `docs/development/backend-development.md` | 更新 Service 架构文档 |
| `backend/models/repositories/` | `docs/development/backend-development.md` | 更新 Repository 模式文档 |
| `frontend/src/features/` | `docs/development/frontend-development.md` | 添加功能说明 |
| `backend/services/hql/` | `docs/hql/` | 更新 HQL 生成器文档 |
| `backend/core/cache/` | `docs/cache/` | 更新缓存系统文档 |
| `backend/core/security/` | `docs/development/security-guide.md` | 更新安全规范 |

### 经验文档映射

| 问题类型 | 目标经验文档 | 提取内容 |
|---------|-------------|---------|
| API 错误/400 错误 | `docs/lessons-learned/api-design-patterns.md` | API 设计模式、错误处理 |
| SQL 注入/XSS | `docs/lessons-learned/security-essentials.md` | 安全防护经验 |
| React Hooks 错误 | `docs/lessons-learned/react-best-practices.md` | React 最佳实践 |
| 性能问题 | `docs/lessons-learned/performance-patterns.md` | 性能优化模式 |
| 测试失败 | `docs/lessons-learned/testing-guide.md` | 测试技巧和调试方法 |
| 数据库问题 | `docs/lessons-learned/database-patterns.md` | 数据库设计模式 |
| 部署问题 | `docs/lessons-learned/deployment-operations.md` | 部署运维经验 |
| 架构决策 | `docs/adr/README.md` | 架构决策记录 |

## 工作流程

### 阶段 1: 检测与分析

1. **分析代码变更**
   - 运行 `git diff` 检测未提交变更
   - 识别修改的文件和变更类型
   - 分析 AST 提取语义信息

2. **识别影响范围**
   - 确定变更影响的文档
   - 检测可能的重复内容
   - 识别需要归档的过时文档

### 阶段 2: 文档更新

3. **生成更新内容**
   - 为 API 变更生成端点文档
   - 为功能变更生成使用说明
   - 为架构变更生成设计文档

4. **应用更新**
   - 更新目标文档
   - 添加变更记录到 CHANGELOG.md
   - 更新相关索引

### 阶段 3: 整合与提取

5. **整合重复内容**
   - 检测相似度 >70% 的文档片段
   - 合并到权威来源
   - 更新所有引用

6. **提取经验**
   - 从更新/整合过程中识别经验模式
   - 提取到经验文档系统
   - 更新 CLAUDE.md 经验索引

### 阶段 4: 归档与清理

7. **归档过时文档**
   - 移动 6 个月未更新的文档到 archive/
   - 添加归档说明
   - 更新索引和引用

8. **清理断开链接**
   - 检测并修复断开的内部链接
   - 验证外部引用
   - 生成链接健康报告

### 阶段 5: 审计与报告

9. **执行合规性审计**
   - 检查文档命名规范
   - 验证文档位置正确性
   - 检查必需章节完整性

10. **生成报告**
    - 创建更新日志
    - 生成整合报告
    - 输出审计结果

## 输出报告

### 更新日志示例

```markdown
# 文档更新日志 - 2026-03-19

## 本次更新概览
- 更新文档: 12 个
- 整合重复文档: 5 个
- 归档过时文档: 3 个
- 提取经验条目: 8 条

## 详细变更

### API 文档更新
- `docs/api/README.md`: 添加新端点 `/api/events/batch`
- `docs/api/endpoints/events.md`: 更新事件查询参数

### 经验文档更新
- `docs/lessons-learned/api-design-patterns.md`: 添加批量API设计经验
- `docs/lessons-learned/performance-patterns.md`: 添加缓存优化经验

### 归档文档
- `docs/archive/2026/03-march/reports/old-test-report.md`

## 链接健康检查
- 断开链接: 2 个（已修复）
- 外部引用失效: 0 个
```

### 整合报告示例

```markdown
# 文档整合报告 - 2026-03-19

## 重复内容分析
- 检测文档: 156 个
- 发现重复: 23 处
- 整合完成: 18 处
- 需要人工审核: 5 处

## 整合详情

### 合并: React Hooks 规则（4 处重复）
- 权威来源: `docs/lessons-learned/react-best-practices.md`
- 已移除重复:
  - `docs/reports/react-hooks-error.md`
  - `docs/testing/e2e-testing-guide.md` (重复章节)
  - `frontend/docs/react-rules.md`
  - `CLAUDE.md` (重复内容，改为引用)

### 经验提取: GraphQL 类型同步（3 处重复）
- 新增经验: `docs/lessons-learned/graphql-type-synchronization.md`
- 提取来源:
  - `docs/reports/graphql-fix-2026-03-08.md`
  - `CHANGELOG.md` (v8.1.0 变更记录)
  - `docs/development/graphql-development-guide.md`
```

## 最佳实践

### 何时使用此技能

**必须使用**（强制）：
- ✅ 代码修改后（无论大小）
- ✅ API 变更后
- ✅ 功能添加/删除后
- ✅ 架构重构后

**建议使用**：
- 文档组织混乱时
- 发现重复文档时
- 需要整理归档时
- 定期维护（每周/每月）

### 文档命名规范

**正确示例**：
- `api-development-guide.md` ✅
- `e2e-testing-guide.md` ✅
- `performance-report-2026-03-19.md` ✅

**错误示例**：
- `API_Development_Guide.md` ❌（大写和下划线）
- `e2eTestingGuide.md` ❌（驼峰命名）
- `FINAL_REPORT.md` ❌（全大写）

### 文档位置规范

```
docs/
├── development/      # 开发指南
│   ├── architecture.md
│   ├── contributing.md
│   └── getting-started.md
├── testing/          # 测试文档
│   ├── e2e-testing-guide.md
│   └── quick-test-guide.md
├── reports/          # 开发报告
│   └── (临时报告，完成后归档)
├── lessons-learned/  # 经验文档（长期维护）
│   ├── react-best-practices.md
│   └── api-design-patterns.md
├── archive/          # 归档文档
│   └── 2026/03-march/
└── README.md         # 主索引
```

### 避免重复内容

**❌ 错误：在多个文档中重复相同内容**
```markdown
# docs/reports/react-error.md
## React Hooks 规则
1. 只在顶层调用 Hooks
2. 不在条件语句中使用 Hooks
...

# docs/testing/e2e-guide.md
## React Hooks 规则
1. 只在顶层调用 Hooks
2. 不在条件语句中使用 Hooks
...
```

**✅ 正确：引用权威来源**
```markdown
# docs/reports/react-error.md
## React Hooks 规则
详见：[React 最佳实践](docs/lessons-learned/react-best-practices.md#react-hooks-规则)

# docs/testing/e2e-guide.md
## React Hooks 规则
详见：[React 最佳实践](docs/lessons-learned/react-best-practices.md#react-hooks-规则)
```

## 配置选项

### 自定义映射规则

创建 `.claude/skills/update-docs/config.json`:

```json
{
  "custom_mappings": [
    {
      "source_pattern": "backend/services/custom/*",
      "target_doc": "docs/custom/service-guide.md",
      "update_action": "append_section"
    }
  ],
  "archive_rules": {
    "age_threshold_days": 180,
    "exclude_patterns": ["README.md", "CLAUDE.md"]
  },
  "integration_rules": {
    "similarity_threshold": 0.7,
    "auto_merge": true,
    "require_review": ["docs/lessons-learned/*", "CLAUDE.md"]
  }
}
```

## 常见问题

**Q: 会自动删除文档吗？**
A: 不会。整合和归档操作都会生成报告，需要您审核后确认才执行。

**Q: 如何跳过某些文档？**
A: 使用 `--exclude` 参数或在配置文件中添加 `exclude_patterns`。

**Q: 整合后如何找到原来的内容？**
A: 所有被整合的文档都会移动到 `docs/archive/` 原位置保留引用。

**Q: 经验提取准确吗？**
A: 系统会识别经验模式，但建议您审核提取的内容，确保质量。

## 技术实现

### 相似度检测算法

使用 TF-IDF + Cosine Similarity 检测文档相似度：

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def detect_similarity(doc1, doc2):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([doc1, doc2])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return similarity
```

### AST 语义分析

使用 Python `ast` 模块分析代码结构：

```python
import ast

def analyze_code_structure(code):
    tree = ast.parse(code)
    # 提取类、函数、导入等信息
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    return {"classes": classes, "functions": functions}
```

## 贡献指南

如果您发现技能有任何问题或改进建议，请：

1. 检查现有 issues
2. 提交新的 issue 或 PR
3. 更新测试用例
4. 确保通过所有测试

## 许可证

MIT License - 详见项目根目录 LICENSE 文件
