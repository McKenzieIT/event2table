# update-docs Skill

智能文档更新工具，自动检测代码变更并更新相关文档。

## 功能特性

### 1. 智能变更检测
- **Git Diff分析**: 检测未提交的代码变更
- **AST语义分析**: 理解代码结构和语义
- **关键词匹配**: 分析提交信息和注释

### 2. 多维度文档映射
- **基于路径映射**: 根据文件路径映射到目标文档
- **基于类型映射**: 根据变更类型映射（API/Service/Repository等）
- **语义映射**: 根据代码语义智能映射

### 3. 自动文档生成
- **API文档**: 自动生成API端点文档
- **功能文档**: 自动生成功能说明文档
- **PRD更新**: 自动更新产品需求文档

### 4. 文档审计
- **合规性检查**: 检查文档是否符合规范
- **完整性验证**: 检查文档是否完整
- **冲突检测**: 检测文档合并冲突

## 使用方式

```bash
# 自动检测并更新文档
/update-docs

# 预览将要更新的文档（不实际修改）
/update-docs --dry-run

# 文档合规性审计
/update-docs --audit

# 手动指定要更新的文档
/update-docs --manual docs/api/README.md
```

## 输出位置

```
.claude/skills/update-docs/output/
├── updates/           # 更新记录（JSON + Markdown）
└── audits/            # 审计报告
```

## 映射规则

| 代码位置 | 目标文档 | 更新动作 |
|---------|---------|---------|
| `backend/api/routes/` | `docs/api/` | 添加API端点文档 |
| `backend/services/` | `docs/development/backend-development.md` | 更新Service文档 |
| `backend/models/repositories/` | `docs/development/backend-development.md` | 更新Repository文档 |
| `frontend/src/features/` | `docs/development/frontend-development.md` | 添加功能说明 |
| `backend/services/hql/` | `docs/hql/` | 更新HQL文档 |
