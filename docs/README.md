# Event2Table 文档中心

**版本**: 8.0.0
**最后更新**: 2026-03-19

---

## 📚 快速导航

### 新用户入门
- [项目 README](../README.md) - 项目概述和快速开始
- [开发快速开始](development/QUICKSTART.md) ⭐ - 5分钟上手指南
- [环境搭建指南](development/getting-started.md) - 详细环境配置

### 核心开发文档
- [架构设计](development/architecture.md) ⭐ - 分层架构设计
- [贡献指南](development/contributing.md) - 开发规范
- [API开发指南](development/api-development.md) - API开发规范
- [前端开发指南](development/frontend-development.md) - 前端开发规范

### 经验文档系统 ⭐
- [经验文档索引](lessons-learned/README.md) ⭐ - 所有经验文档的导航中心

---

## 📖 文档目录

### 开发指南 (`development/`)

核心开发文档和规范。

**入门指南**:
- [QUICKSTART.md](development/QUICKSTART.md) - 快速开始
- [getting-started.md](development/getting-started.md) - 环境搭建
- [contributing.md](development/contributing.md) - 贡献指南

**架构设计**:
- [architecture.md](development/architecture.md) ⭐ - 系统架构设计
- [sql-validator-guidelines.md](development/sql-validator-guidelines.md) - SQL验证器规范
- [graphql-development-guide.md](development/graphql-development-guide.md) - GraphQL开发指南

**开发规范**:
- [github-setup-guide.md](development/github-setup-guide.md) - GitHub和PR工作流设置
- [API-CONTRACT-TEST-GUIDE.md](development/API-CONTRACT-TEST-GUIDE.md) - API契约测试
- [GAME_GID_MIGRATION_GUIDE.md](development/GAME_GID_MIGRATION_GUIDE.md) - game_gid迁移指南

**TypeScript**:
- [TYPESCRIPT-CI-GUIDE.md](development/TYPESCRIPT-CI-GUIDE.md) - TypeScript CI配置
- [TYPESCRIPT-QUICK-REF.md](development/TYPESCRIPT-QUICK-REF.md) - TypeScript快速参考
- [TYPESCRIPT-MIGRATION-CHECKLIST.md](development/TYPESCRIPT-MIGRATION-CHECKLIST.md) - TypeScript迁移清单

**React**:
- [react-performance-optimization-guide.md](development/react-performance-optimization-guide.md) - React性能优化
- [COMPONENT_PROPS_PATTERNS.md](development/COMPONENT_PROPS_PATTERNS.md) - 组件Props模式
- [HASHROUTER-QPARAMS-GUIDE.md](development/HASHROUTER-QPARAMS-GUIDE.md) - HashRouter Q参数指南

**安全**:
- [fix-sensitive-data-leakage-2026-02-24.md](security/fix-sensitive-data-leakage-2026-02-24.md) - 敏感数据泄漏修复
- [cache-key-injection-fix-2026-02-24.md](security/cache-key-injection-fix-2026-02-24.md) - 缓存键注入修复

### API 文档 (`api/`)

RESTful API 和 GraphQL API 文档。

**核心API**:
- [README.md](api/README.md) ⭐ - API索引和概述
- [GAMES-API.md](api/GAMES-API.md) - 游戏管理API
- [EVENTS-API.md](api/EVENTS-API.md) - 事件管理API
- [PARAMETERS-API.md](api/PARAMETERS-API.md) - 参数管理API

**Canvas API**:
- [EVENT-NODES-API.md](api/EVENT-NODES-API.md) - 事件节点API
- [FLOWS-API.md](api/FLOWS-API.md) - 流程管理API
- [JOIN-CONFIGS-API.md](api/JOIN-CONFIGS-API.md) - JOIN配置API

### 缓存系统 (`cache/`)

缓存系统架构和使用指南。

**快速开始**:
- [5分钟快速开始](cache/quickstart/5-minute-guide.md) ⭐ - 新用户快速上手
- [常见问题FAQ](cache/quickstart/faq.md) - 10个最常见问题

**开发者指南**:
- [开发者指南](cache/development/developer-guide.md) ⭐ - 深入了解架构
- [API参考](cache/development/api-reference.md) - 完整API文档
- [代码片段](cache/quickstart/code-snippets.md) - 实用代码示例

**运维文档**:
- [性能调优](cache/operations/performance-tuning.md) - 性能优化
- [监控](cache/operations/monitoring.md) - 监控和告警
- [故障排除](cache/operations/troubleshooting.md) - 问题排查

**架构**:
- [系统设计](cache/architecture/system-design.md) - 架构设计文档

### 测试文档 (`testing/`)

测试指南和测试报告。

**测试指南**:
- [E2E测试指南](testing/e2e-testing-guide.md) ⭐ - E2E测试规范
- [快速测试指南](testing/quick-test-guide.md) - PATH问题排查

**测试报告**:
- [test-reports/](testing/test-reports/) - 测试报告存档

### 经验文档 (`lessons-learned/`)

项目经验总结，避免重复错误。

**核心经验** ⭐:
- [README.md](lessons-learned/README.md) ⭐ - 经验文档索引
- [项目管理](lessons-learned/project-management.md) ⭐ - 并行开发、大规模重构、文档整合
- [重构检查清单](lessons-learned/refactoring-checklist.md) - 重构最佳实践
- [调试技能](lessons-learned/debugging-skills.md) - 调试技巧

**领域经验**:
- [API设计模式](lessons-learned/api-design-patterns.md) - API设计经验
- [数据库模式](lessons-learned/database-patterns.md) - 数据库设计
- [性能模式](lessons-learned/performance-patterns.md) - 性能优化
- [安全要点](lessons-learned/security-essentials.md) - 安全防护
- [Python开发](lessons-learned/python-development.md) - Python最佳实践
- [React最佳实践](lessons-learned/react-best-practices.md) - React优化
- [测试指南](lessons-learned/testing-guide.md) - 测试技巧

### 计划文档 (`plans/`)

设计和实施计划。

**最近计划**:
- [2026-03-18: Universal Test系统设计](plans/2026-03-18-universal-test-system-design.md)
- [2026-03-14: 代码审计问题修复](plans/2026-03-14-code-audit-issues-fix.md)
- [2026-03-08: 完整实现原则设计](plans/2026-03-08-complete-implementation-principle-design.md)
- [2026-03-05: 性能优化自动化](plans/2026-03-05-performance-optimization-automation.md)

### 归档文档 (`archive/`)

历史文档和过时报告。

**归档结构**:
```
archive/
├── 2026/
│   ├── 03-march/       # 2026年3月文档
│   │   ├── integration/   # 整合报告
│   │   ├── reports/       # 测试报告
│   │   └── development/   # 开发文档
│   └── 02-february/    # 2026年2月文档
└── ...
```

---

## 🔍 文档查找

### 按主题查找

**我想了解...**

| 主题 | 查看文档 |
|------|----------|
| **项目架构** | [architecture.md](development/architecture.md) |
| **API使用** | [API索引](api/README.md) |
| **缓存系统** | [5分钟指南](cache/quickstart/5-minute-guide.md) |
| **React开发** | [React最佳实践](lessons-learned/react-best-practices.md) |
| **性能优化** | [性能模式](lessons-learned/performance-patterns.md) |
| **测试** | [E2E测试指南](testing/e2e-testing-guide.md) |
| **安全** | [安全要点](lessons-learned/security-essentials.md) |
| **调试** | [调试技能](lessons-learned/debugging-skills.md) |
| **项目管理** | [项目管理经验](lessons-learned/project-management.md) |

### 按问题查找

**遇到问题时...**

| 问题 | 查看文档 |
|------|----------|
| **环境配置** | [getting-started.md](development/getting-started.md) |
| **PATH问题** | [快速测试指南](testing/quick-test-guide.md) |
| **React Hooks错误** | [React最佳实践 - Hooks规则](lessons-learned/react-best-practices.md) |
| **API 400错误** | [API设计模式 - 400诊断](lessons-learned/api-design-patterns.md) |
| **性能问题** | [性能模式 - N+1查询](lessons-learned/performance-patterns.md) |
| **SQL注入** | [安全要点 - SQL注入防护](lessons-learned/security-essentials.md) |
| **测试失败** | [测试指南 - E2E测试](lessons-learned/testing-guide.md) |

---

## 📝 文档规范

### 文档命名规范

**正确示例** ✅:
- `api-development-guide.md` (小写+连字符)
- `e2e-testing-guide.md` (小写+连字符)
- `performance-report-2026-03-19.md` (小写+连字符+日期)

**错误示例** ❌:
- `API_Development_Guide.md` (大写和下划线)
- `e2eTestingGuide.md` (驼峰命名)
- `FINAL_REPORT.md` (全大写)

### 文档位置规范

```
docs/
├── development/      # 开发指南
│   ├── architecture.md
│   ├── contributing.md
│   └── getting-started.md
├── api/             # API文档
│   ├── README.md
│   ├── GAMES-API.md
│   └── EVENTS-API.md
├── cache/           # 缓存系统
│   ├── quickstart/
│   ├── development/
│   └── operations/
├── testing/         # 测试文档
│   ├── e2e-testing-guide.md
│   └── test-reports/
├── lessons-learned/ # 经验文档（长期维护）
│   ├── README.md
│   ├── project-management.md
│   └── react-best-practices.md
├── plans/           # 计划文档
└── archive/         # 归档文档
    └── 2026/
        └── 03-march/
```

### 文档更新流程

**每次代码修改后**:
1. ✅ 更新API文档（如果修改了API）
2. ✅ 更新架构文档（如果修改了架构）
3. ✅ 提取经验到经验文档
4. ✅ 更新相关索引
5. ✅ 提交文档和代码

**详见**: [项目管理 - 文档整合管理](lessons-learned/project-management.md#文档整合管理)

---

## 🔧 文档工具

### 文档分析工具

**相似度检测**:
```bash
# 检测文档重复
python scripts/tools/doc_analyzer.py docs 0.65
```

**链接验证**:
```bash
# 验证内部链接
python scripts/tools/verify_links.py docs/
```

### 文档生成工具

**GraphQL类型生成**:
```bash
# 从GraphQL schema生成TypeScript类型
cd frontend
npm run generate:types
```

**API文档生成**:
```bash
# 从代码注释生成API文档
python scripts/tools/generate_api_docs.py
```

---

## 📊 文档统计

| 类别 | 文档数量 | 最后更新 |
|------|----------|----------|
| 开发指南 | 40+ | 2026-03-19 |
| API文档 | 10+ | 2026-03-19 |
| 缓存系统 | 7 | 2026-02-25 |
| 测试文档 | 5+ | 2026-02-18 |
| 经验文档 | 20+ | 2026-03-19 |
| 计划文档 | 10+ | 2026-03-18 |
| 归档文档 | 100+ | 2026-03-19 |

**总计**: 200+ 文档

---

## 🤝 贡献指南

### 更新文档

**发现文档问题时**:
1. 检查是否已有相关文档
2. 更新或创建新文档
3. 更新索引（本文件）
4. 提交Pull Request

**添加新经验**:
1. 提取经验模式
2. 使用统一模板更新经验文档
3. 在CLAUDE.md中添加简短记录
4. 更新经验文档索引

### 文档审查

**代码审查时检查**:
- [ ] 是否有对应的需求文档？
- [ ] 是否有API文档？
- [ ] 是否更新了架构文档？
- [ ] 是否提取了经验？
- [ ] 是否更新了相关索引？

---

## 📞 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/McKenzieIT/event2table/issues)
- **项目维护者**: Event2Table Development Team
- **文档反馈**: 在文档页面点击"编辑"按钮直接改进

---

**文档版本**: 8.0.0
**最后更新**: 2026-03-19
**维护者**: Event2Table Development Team
