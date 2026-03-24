# 经验文档索引 (Lessons Learned)

> **Welcome**: Event2Table项目经验知识库 - 从实践中提取的可复用经验
> **Total Documents**: 23 experience documents
> **Last Updated**: 2026-03-24
> **Maintained By**: `/update-docs` skill (automatic extraction + manual curation)

---

## 📊 Experience Statistics

- **Total Experience Documents**: 23
- **Total Experience Points**: ~150+ (estimated)
- **P0 (Critical)**: ~10 experiences
- **P1 (Important)**: ~21 experiences
- **P2 (Useful)**: ~120+ experiences
- **Recent Updates** (2026-03-24):
  - ✅ 新增: 避免过度工程化 (P0)
  - ✅ 新增: TDD驱动的Prompt工程 (P1)
  - ✅ 新增: 示例驱动Prompt验证方法 (P1) 🆕
  - ✅ 新增: 对话式测试方法 (P1)

---

## 🎯 Quick Finder

**按问题类型快速查找经验**:

| 问题类型 | 推荐文档 | 优先级 |
|---------|---------|--------|
| **React应用挂载** | [testing-guide](testing-guide.md) | P0 |
| **Chrome DevTools调试** | [testing-guide](testing-guide.md) | P0 |
| **mypy类型错误** | [python-development](python-development.md) | P0 |
| **React Hooks错误** | [react-best-practices](react-best-practices.md) | P0 |
| **Vite-Apollo兼容性** | [react-best-practices](react-best-practices.md) | P1 |
| **Lazy Loading问题** | [react-best-practices](react-best-practices.md) | P0 |
| **缓存失效分析** | [performance-patterns](performance-patterns.md) | P0 |
| **DataLoader批量查询** | [api-design-patterns](api-design-patterns.md) | P0 |
| **GraphQL 400错误** | [api-design-patterns](api-design-patterns.md) | P0 |
| **SQL注入风险** | [security-essentials](security-essentials.md) | P0 |
| **XSS防护实施** | [security-essentials](security-essentials.md) | P0 |
| **E2E测试失败** | [testing-guide](testing-guide.md) | P0 |
| **TDD Red阶段** | [testing-guide](testing-guide.md) | P0 |
| **N+1查询优化** | [performance-patterns](performance-patterns.md) | P0 |
| **game_gid迁移** | [database-patterns](database-patterns.md) | P0 |
| **并行开发任务** | [project-management](project-management.md) | P0 |
| **大规模重构** | [project-management](project-management.md) | P0 |
| **TypeScript迁移** | [typescript-migration](typescript-migration.md) | P0 |
| **Security Integration测试** | [security-integration-testing](security-integration-testing.md) | P0 |
| **Mutation业务逻辑** | [mutation-business-logic](mutation-business-logic.md) | P0 |
| **Test-Fix迭代** | [test-fix-iteration](test-fix-iteration.md) | P0 |
| **过度工程化** 🆕 | [project-management](project-management.md) | P0 |
| **TDD Prompt工程** 🆕 | [project-management](project-management.md) | P1 |
| **Prompt验证测试** 🆕 | [project-management](project-management.md) | P1 |
| **对话式测试** 🆕 | [testing-guide](testing-guide.md) | P1 |

---

## 📚 Experience Documents by Category

### Project Management (项目管理)

**[project-management.md](project-management.md)** ⭐
- 并行开发策略 (P0)
- 大规模重构管理 (P0)
- 分阶段重构策略 (P0)
- 零破坏性变更保证 (P1)
- 文档驱动开发 (P1)
- **避免过度工程化** (P0) 🆕
- **TDD驱动的Prompt工程** (P1) 🆕
- **示例驱动Prompt验证** (P1) 🆕
- Subagent-Driven Development (P1)
- 技术债务管理 (P2)

**Experience Count**: ~18 points
**Last Updated**: 2026-03-24

---

### Development (开发规范)

**[python-development.md](python-development.md)**
- mypy类型安全 (P0)
- GenericRepository模式 (P0)
- Pydantic validator最佳实践 (P1) 🆕
- 代码审查检查项 (P1)
- AST语义分析 (P2)

**[react-best-practices.md](react-best-practices.md)**
- React Hooks规则 (P0)
- Lazy Loading最佳实践 (P0)
- Vite与Apollo Client兼容性 (P1)
- 组件设计模式 (P1)
- 性能优化技巧 (P2)

**[typescript-migration.md](typescript-migration.md)** 🆕
- Apollo Client 3.x兼容性 (P0)
- 类型重复定义解决方案 (P0)
- Template Literal语法错误修复 (P1)
- 迁移最佳实践 (P1)

**Experience Count**: ~15 points per document

---

### Architecture (架构设计)

**[service-architecture.md](service-architecture.md)**
- Service层职责划分 (P0)
- Repository层依赖 (P1)
- Entity架构设计 (P1)
- 缓存集成策略 (P1)
- 依赖注入模式 (P2)

**[repository-migration.md](repository-migration.md)** 🆕
- Repository模式迁移 (P0)
- 数据访问层重构 (P1)
- 测试策略 (P2)

**Experience Count**: ~10 points per document

---

### API & Data (API与数据)

**[api-design-patterns.md](api-design-patterns.md)** ⭐
- GraphQL DataLoader实施 (P0)
- 批量查询优化 (P0)
- 缓存键设计规范 (P0)
- GraphQL 400错误诊断 (P0) 🆕
- API错误处理 (P1)
- HQL生成器安全 (P1)

**[database-patterns.md](database-patterns.md)**
- game_gid使用规范 (P0)
- 事务管理 (P1)
- 数据库迁移 (P1)
- 连接池优化 (P2)

**Experience Count**: ~12 points per document

---

### Performance (性能优化)

**[performance-patterns.md](performance-patterns.md)** ⭐
- DataLoader批量查询优化 (P0) 🆕
- 批量操作优化 (P0) 🆕
- TTL分层设置策略 (P0) 🆕
- 并行优化策略 (P0) 🆕
- N+1查询优化 (P0)
- 缓存失效分析 (P0)
- Entity架构下的性能优化 (P1)

**Experience Count**: ~15 points

---

### Testing (测试与质量)

**[testing-guide.md](testing-guide.md)** ⭐
- E2E测试方法论 (P0)
- TDD Red阶段经验 (P0) 🆕
- 控制台错误检测 (P0) 🆕
- Dashboard实时优化 (P1) 🆕
- 缓存失效装饰器 (P1) 🆕
- E2E测试中的代码修复验证 (P0) 🆕
- **对话式测试方法** (P1) 🆕
- 修复验证流程 (P0)
- Chrome DevTools MCP测试流程 (P1)

**[test-fix-iteration.md](test-fix-iteration.md)** 🆕
- 4轮迭代模式 (P0)
- TDD + 并行执行 (P0)
- 自动化验证 (P1)
- 从20%到100%提升 (P1)

**[security-integration-testing.md](security-integration-testing.md)** 🆕
- SQL注入防护测试 (P0)
- XSS攻击检测 (P0)
- 白名单验证策略 (P0)
- 85%测试通过率 (P1)

**Experience Count**: ~20 points per document

---

### Security (安全与合规)

**[security-essentials.md](security-essentials.md)** ⭐
- SQL注入防护 (P0)
- XSS防护实施 (P0) 🆕
- 权限检查完整性 (P0) 🆕
- 输入验证 (P1)
- 输出编码 (P1)

**[mutation-business-logic.md](mutation-business-logic.md)** 🆕
- 5层验证架构 (P0)
- 完整实现原则 (P0)
- 安全加固 (P1)
- 缓存失效策略 (P1)

**Experience Count**: ~10 points per document

---

### Quality & Refactoring (质量与重构)

**[refactoring-checklist.md](refactoring-checklist.md)**
- TDD检查清单 (P0)
- 代码审查检查项 (P1)
- 技术债务识别 (P1)
- 重构策略 (P2)

**[debugging-skills.md](debugging-skills.md)**
- Chrome DevTools MCP调试 (P0)
- Subagent分析方法 (P1)
- 根因分析技巧 (P2)

**Experience Count**: ~8 points per document

---

### Specialized Topics (专业主题)

**[agent-browser-testing.md](agent-browser-testing.md)** 🆕
- Agent-Browser使用技巧 (P0)
- 故障排除 (P0)
- 替代测试方案 (P1)

**[deployment-operations.md](deployment-operations.md)**
- 部署流程 (P1)
- 运维监控 (P1)
- 故障排查 (P2)

**[event-node-builder-errors.md](event-node-builder-errors.md)**
- GraphQL类型不匹配案例 (P0)
- 错误诊断方法 (P1)

**[graphql-field-completeness.md](graphql-field-completeness.md)**
- GraphQL字段完整性检查 (P0)
- Schema同步 (P1)

**[mypy-compliance.md](mypy-compliance.md)**
- mypy strict合规 (P0)
- 类型注解最佳实践 (P1)

**[zod-schema-validation-analysis.md](zod-schema-validation-analysis.md)**
- Zod schema验证 (P1)
- 运行时类型检查 (P2)

**[HIVE_TYPE_DOCUMENTATION_UPDATE_SUMMARY.md](HIVE_TYPE_DOCUMENTATION_UPDATE_SUMMARY.md)** 🆕
- Hive类型文档更新 (P1)
- 元数据管理 (P2)

**Experience Count**: ~5-8 points per document

---

## 🔄 Recently Updated (2026-03-24)

### New Experiences Added

1. **避免过度工程化** (P0) → [project-management.md](project-management.md)
   - 来源: update-docs-overengineering-audit.md
   - 核心原则: "简单 + Claude思考 = 高质量"
   - 代码量减少87.5% (400行→50行)

2. **TDD驱动的Prompt工程** (P1) → [project-management.md](project-management.md)
   - 来源: PROMPT-VALIDATION-TEST-FRAMEWORK.md
   - 核心方法: 黄金标准 + 质量评估 + 多轮迭代
   - 目标质量分数: >85分

3. **对话式测试方法** (P1) → [testing-guide.md](testing-guide.md)
   - 来源: CONVERSATION-TESTING-GUIDE.md
   - 核心方法: 4轮思考工作流
   - 成功标准: Quality Score >0.9, Duplication Rate <5%

### Documents Enhanced

- **project-management.md**: +200 lines, 2 new experiences
- **testing-guide.md**: +70 lines, 1 new experience

---

## 📖 How to Use This Index

### Searching by Problem

1. **快速查找表** - 使用上面的Quick Finder按问题类型查找
2. **按类别浏览** - 浏览各个类别下的文档
3. **全文搜索** - 使用IDE的搜索功能在所有经验文档中搜索关键词

### Contributing New Experiences

当遇到问题时：
1. 解决问题后，提取经验
2. 使用统一格式添加到对应文档
3. 在本索引中添加引用
4. 运行 `/update-docs` 自动更新索引

### Maintenance

- **自动更新**: 每次 `/update-docs` 执行时自动更新
- **手动更新**: 重大经验添加时手动更新
- **审查频率**: 每月审查一次

---

## 📊 Experience Distribution

| Category | Documents | Total Experiences | P0 | P1 | P2 |
|----------|-----------|-------------------|----|----|-----|
| Project Management | 1 | ~17 | 10 | 7 | ~0 |
| Development | 3 | ~45 | 15 | 20 | ~10 |
| Architecture | 2 | ~20 | 5 | 10 | ~5 |
| API & Data | 2 | ~24 | 8 | 12 | ~4 |
| Performance | 1 | ~15 | 8 | 5 | ~2 |
| Testing | 3 | ~40 | 15 | 15 | ~10 |
| Security | 2 | ~20 | 8 | 10 | ~2 |
| Quality & Refactoring | 2 | ~16 | 5 | 8 | ~3 |
| Specialized Topics | 7 | ~30 | 10 | 15 | ~5 |
| **Total** | **23** | **~227** | **~84** | **~102** | **~41** |

---

## 🔗 Related Documentation

- **[Main Documentation Index](../README.md)** - 项目文档总索引
- **[CLAUDE.md](../CLAUDE.md)** - 项目开发规范
- **[CHANGELOG.md](../CHANGELOG.md)** - 项目更新日志

---

**Index Version**: 1.0.0
**Last Updated**: 2026-03-24
**Next Review**: 2024-04-24
**Maintained By**: update-docs skill v2.0

---

**🎯 Quick Tip**: 使用 `Ctrl+F` 或 `Cmd+F` 在此页面搜索关键词，快速找到相关经验！
