# update-docs Skill

智能文档更新工具，自动检测代码变更并更新相关文档。

## 快速开始

```bash
# 基本使用
/update-docs

# 预览模式（不实际修改）
/update-docs --dry-run

# 审计模式
/update-docs --audit
```

## 功能特性

### 1. 智能变更检测
- **Git Diff分析**: 检测未提交的代码变更
- **AST语义分析**: 理解代码结构和语义
- **关键词匹配**: 分析提交信息和注释

### 2. 多维度文档映射
- **基于路径映射**: 根据文件路径映射到目标文档
- **基于类型映射**: 根据变更类型（API/Service/Repository等）
- **语义映射**: 根据代码语义智能映射

### 3. 自动文档生成
- **API文档**: 自动生成API端点文档
- **功能文档**: 自动生成功能说明文档
- **PRD更新**: 自动更新产品需求文档

## 工作流程

```
代码变更
    ↓
变更检测 (Git Diff + AST + 关键词)
    ↓
文档映射 (路径 + 类型 + 语义)
    ↓
更新计划 (优先级排序)
    ↓
文档更新 (应用模板)
    ↓
生成报告 (JSON + Markdown)
```

## 映射规则

| 代码位置 | 目标文档 | 更新动作 |
|---------|---------|---------|
| `backend/api/routes/` | `docs/api/` | 添加API端点文档 |
| `backend/services/` | `docs/development/backend-development.md` | 更新Service文档 |
| `backend/models/repositories/` | `docs/development/backend-development.md` | 更新Repository文档 |
| `frontend/src/features/` | `docs/development/frontend-development.md` | 添加功能说明 |
| `backend/services/hql/` | `docs/hql/` | 更新HQL文档 |
