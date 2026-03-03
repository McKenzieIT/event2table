# API Legacy Documentation Archive

**Archived Date**: 2026-03-03
**Reason**: API Documentation Consolidation

---

## Archived Files

### API-INDEX.md
- **原用途**: API端点完整列表
- **归档原因**: 内容已合并到 [../../api/README.md](../../api/README.md)
- **替代方案**: 参见主README.md的"API端点索引"部分

### API-ENDPOINT-QUICK-REFERENCE.md
- **原用途**: API快速参考指南
- **归档原因**: 内容已合并到 [../../api/README.md](../../api/README.md)
- **替代方案**: 参见主README.md的"快速开始"和"Critical Rules"部分

---

## 新文档结构

**主文档**: [docs/api/README.md](../../api/README.md)

**包含部分**:
1. 快速开始（基础信息、响应格式、Critical Rules）
2. 架构概述（ERS架构、双API架构）
3. API端点索引（完整的84个REST端点）
4. GraphQL API（78个操作）
5. 错误处理
6. 性能优化（缓存、DataLoader、分页）
7. 相关文档链接

---

## 迁移理由

**问题**:
- 三个文件内容重复
- 维护成本高（需要同步更新）
- 用户困惑（不知道查看哪个文件）

**解决方案**:
- 合并为单一权威文档
- 清晰的章节划分
- 完整的端点索引 + 快速参考代码示例

---

## 如需查询历史文档

这些文档保留了API演进的历史记录，仅用于参考。所有最新信息请查看主文档。
