# 经验文档索引

> **🎯 目标**: 避免重复经验，提供集中的知识库
> **📊 来源**: 整合了492个文档的精华经验（+46个archive报告）
> **🔄 更新**: 持续更新，每次问题修复后立即更新
> **📈 最新**: 2026-03-18 - 大型文档整合完成（11个文档，11843行）⭐
> - **Entity架构经验**: 从architecture.md (2491行) 提取 → [api-design-patterns.md](./api-design-patterns.md) ⭐
> - **TypeScript类型规范**: 从TYPESCRIPT_TYPE_STANDARDS.md (2003行) 提取 → [typescript-migration.md](./typescript-migration.md) ⭐
> - **Chrome MCP兼容性**: 从4个Chrome MCP文档 (2861行) 提取 → [react-best-practices.md](./react-best-practices.md) ⭐
> - **CLAUDE.md精简**: 从2508行精简到444行（精简率82.3%）⭐
> **📈 2026-03-16**: Archive报告经验补充完成（26个新经验：测试数据验证、键级锁优化、Bloom Filter、ERS架构、E2E清理、Playwright优化、SQL注入验证）

---

## 🚀 新手入门快速导航

**刚开始开发？按顺序阅读以下文档**：

| 步骤 | 文档 | 时间 | 重点 |
|-----|------|-----|-----|
| 1️⃣ | [CLAUDE.md - 开发规范](../../CLAUDE.md) | 15分钟 | 环境设置、TDD、API契约测试 |
| 2️⃣ | [React最佳实践](./react-best-practices.md) | 20分钟 | Hooks规则、组件优化 |
| 3️⃣ | [测试指南](./testing-guide.md) | 25分钟 | E2E测试、TDD流程 |
| 4️⃣ | [安全要点](./security-essentials.md) | 15分钟 | SQL注入、XSS防护 |
| 5️⃣ | [性能模式](./performance-patterns.md) | 20分钟 | 缓存策略、N+1查询优化 |
| **总计** | **5个核心文档** | **~95分钟** | **快速上手必备知识** |

**💡 提示**: 遇到问题时，先查看下方的[快速查找场景](#快速查找场景)或使用搜索功能（Cmd/Ctrl+F）

---

## P0 核心经验 ⚠️ **必须掌握**

### Agent-Browser Testing (2026-03-20新增) ⭐
- [Agent-Browser Testing方法论](./agent-browser-testing.md) - Resource unavailable错误、命令链最佳实践、Chrome进程清理、替代测试方案 ⭐⭐⭐

### 综合性能优化 (2026-03-09新增)
- [DataLoader批量查询优化](./2026-03-07-comprehensive-optimization-experience.md#经验-1-dataloader-批量查询优化-⭐⭐⭐) - N+1查询解决方案，查询数减少70-99% ⭐
- [Dashboard实时优化](./2026-03-07-comprehensive-optimization-experience.md#经验-2-dashboard-实时优化---缓存失效装饰器-⭐⭐⭐) - 缓存失效装饰器，更新延迟从300s降至10s ⭐
- [React组件优化](./2026-03-07-comprehensive-optimization-experience.md#经验-3-react-组件优化---usecallbackusememoreactmemo-⭐⭐) - 17个组件优化案例，重渲染减少50-70% ⭐
- [N+1查询修复](./2026-03-07-comprehensive-optimization-experience.md#经验-4-n1-查询修复---join-vs-循环查询-⭐⭐⭐) - JOIN优化，API响应提升2326x ⭐

### React最佳实践
- [React Hooks规则](./react-best-practices.md#react-hooks-规则) - 避免Hooks顺序错误
- [Lazy Loading最佳实践](./react-best-practices.md#lazy-loading最佳实践) - 避免加载超时
- [Input组件CSS布局规范](./react-best-practices.md#input组件css布局规范) - 始终使用label prop
- [React 18+ defaultProps已废弃](./react-best-practices.md#react-18-defaultprops-已废弃) - 使用ES6默认参数 (2026-03-08新增)

### GraphQL类型安全
- [Event Node Builder错误修复](./event-node-builder-errors.md) - GraphQL枚举不匹配案例 ⭐
- [GraphQL字段完整性](./graphql-field-completeness.md) - hive_type字段4层修复策略 ⭐ (2026-03-13新增)
- [GraphQL类型同步](../../CLAUDE.md#graphql类型同步规范-⚠️-极其重要---2026-03-08新增) - 前后端类型一致性 (2026-03-08新增)

### TypeScript迁移 (2026-03-11新增) ⭐
- [TypeScript迁移经验](./typescript-migration.md) - Apollo Client 3.x兼容性、类型重复定义解决方案、Template Literal语法错误修复 ⭐⭐⭐

### TypeScript和工具链 (2026-03-16新增) ⭐
- [Enum导出规则](./typescript-toolchain-learnings.md#enum导出规则-⚠️-p0) - export type vs export，模块解析错误 ⭐⭐⭐
- [Vite缓存问题排查](./typescript-toolchain-learnings.md#vite缓存问题排查-⚠️-p1) - 缓存清除、模块错误解决 ⭐⭐
- [React Hook性能优化](./typescript-toolchain-learnings.md#react-hook性能优化-⭐--p1) - useTransition、防抖策略、RAF批量处理 ⭐⭐
- [Chrome DevTools MCP快照延迟](./typescript-toolchain-learnings.md#chrome-devtools-mcp快照延迟问题-⚠️-p1) - await_element、验证循环 ⭐⭐

### Security Integration测试 (2026-03-11新增) ⭐
- [Security Integration Testing](./security-integration-testing.md) - SQL注入防护、XSS攻击检测、白名单验证策略、测试通过率从20%提升到85% ⭐⭐⭐

### Mutation业务逻辑 (2026-03-11新增) ⭐
- [Mutation Business Logic](./mutation-business-logic.md) - 5层验证架构、完整实现原则、安全加固、缓存失效策略 ⭐⭐⭐

### 测试修复迭代 (2026-03-11新增) ⭐
- [Test-Fix Iteration](./test-fix-iteration.md) - 4轮迭代模式、TDD + 并行执行策略、自动化验证流程、从20%提升到100% ⭐⭐⭐

### TDD完整实现原则 (2026-03-16新增) ⭐
- [TDD完整实现原则](./tdd-complete-implementation.md) - "不可简化实现"核心原则、3种错误实现模式、TDD Red-Green-Refactor完整流程、4级违规后果 ⭐⭐⭐

### 测试指南
- [E2E测试方法论](./testing-guide.md#e2e测试) - Chrome DevTools MCP测试流程
- [TDD实践](./testing-guide.md#tdd实践) - Red-Green-Refactor循环
- [错误消息质量](./testing-guide.md#错误消息质量) - 用户友好错误消息

### 安全要点
- [SQL注入防护](./security-essentials.md#sql注入防护) - 参数化查询、SQLValidator
- [XSS防护](./security-essentials.md#xss防护) - HTML转义、React自动转义
- [输入验证](./security-essentials.md#输入验证) - Pydantic Schema验证
- [异常信息脱敏](./security-essentials.md#异常信息脱敏) - 错误响应不暴露敏感信息

### 性能模式
- [缓存策略](./performance-patterns.md#缓存策略) - Redis缓存TTL 5-10分钟
- [N+1查询优化](./performance-patterns.md#n1查询优化) - 使用JOIN、合并统计查询
- [分页支持](./performance-patterns.md#分页支持) - LIMIT/OFFSET分页
- [DataLoader批量查询优化](./2026-03-07-comprehensive-optimization-experience.md#经验-1-dataloader-批量查询优化-⭐⭐⭐) - GraphQL DataLoader批量加载 (2026-03-09新增)
- [TTL分层设置策略](./2026-03-07-comprehensive-optimization-experience.md#经验-5-缓存策略---ttl-分层设置-⭐⭐) - 双层缓存架构，命中率85%+ (2026-03-09新增)
- [Dashboard实时优化](./2026-03-07-comprehensive-optimization-experience.md#经验-2-dashboard-实时优化---缓存失效装饰器-⭐⭐⭐) - 智能轮询，API调用减少83% (2026-03-09新增)

### Repository架构迁移 (2026-03-20新增) ⭐
- [Repository Pattern Migration](./repository-migration.md) - 从Dict到Entity迁移、单元测试修复、GenericRepository重构、ERS架构合规 ⭐⭐⭐

### Service架构验证 (2026-03-20新增) ⭐
- [Service Layer Architecture](./service-architecture.md) - ERS架构验证、直接数据库访问消除、缓存策略、分层职责 ⭐⭐⭐

### mypy类型安全 (2026-03-20新增) ⭐
- [mypy --strict Compliance](./mypy-compliance.md) - 类型注解最佳实践、Optional处理、GenericRepository重构、type stubs ⭐⭐⭐

### 数据库模式
- [game_gid迁移经验](./database-patterns.md#game_gid迁移经验) - game_gid vs game_id区别、表名生成规范
- [数据库事务](./database-patterns.md#数据库事务) - 事务使用原则
- [数据隔离规范](./database-patterns.md#数据隔离规范) - 三环境隔离、STAR001保护

### API设计模式
- [分层架构](./api-design-patterns.md#分层架构) - API → Service → Repository → Schema
- [错误处理](./api-design-patterns.md#错误处理) - 具体可操作的错误消息

---

## P1 重要经验 ⭐ **推荐学习**

### React最佳实践
- [React性能优化](./react-best-practices.md#性能优化技巧) - React.memo、useCallback
- [React组件优化模式](./2026-03-07-comprehensive-optimization-experience.md#经验-3-react-组件优化---usecallbackusememoreactmemo-⭐⭐) - 17个组件优化案例，4种优化模式 (2026-03-09新增)
- [React子组件定义顺序](./react-best-practices.md#react子组件定义顺序) - 组件定义顺序
- [useEffect依赖数组最佳实践](./react-best-practices.md#useeffect依赖数组最佳实践) - 避免useCallback+useEffect组合
- [组件导出规范](./react-best-practices.md#组件导出规范) - 导出原始组件名和别名
- [API响应数据结构处理](./react-best-practices.md#api响应数据结构处理) - 处理嵌套数据结构

### 测试指南
- [测试自动化](./testing-guide.md#测试自动化) - Pre-commit Hook强制测试
- [避免重复工作](./testing-guide.md#避免重复工作) - 调查优先于实现
- [测试方法论演进](./testing-guide.md#测试方法论演进) - Phase 1 vs Phase 2测试方法

### 安全要点
- [Legacy API废弃管理](./security-essentials.md#legacy-api废弃管理) - DeprecationDecorator
- [GenericRepository安全验证](./security-essentials.md#genericrepository安全验证) - 表名/字段名验证
- [批量删除验证](./security-essentials.md#批量删除验证) - 输入验证和系统保护

### 性能模式
- [数据库索引](./performance-patterns.md#数据库索引) - 索引设计和优化
- [game_gid转换缓存](./performance-patterns.md#game_gid转换缓存) - LRU缓存优化
- [Dashboard统计查询合并](./performance-patterns.md#dashboard统计查询合并) - 合并统计查询
- [多级缓存架构](./performance-patterns.md#多级缓存架构) - L1+L2+L3缓存层级
- [Cache Tags系统](./performance-patterns.md#cache-tags系统) - 按标签批量失效缓存
- [性能监控装饰器](./performance-patterns.md#性能监控装饰器) - 函数执行时间监控
- [键级锁优化](./performance-patterns.md#键级锁优化) (2026-03-16新增) - 细粒度锁定机制（1.99x提升）
- [Bloom Filter内存优化](./performance-patterns.md#bloom-filter内存优化) (2026-03-16新增) - SCAN批量处理（95%内存减少）
- [ERS架构迁移](./performance-patterns.md#ers架构迁移最佳实践) (2026-03-16新增) - Entity-Repository-Service模式

### 数据库模式
- [数据库文件位置规范](./database-patterns.md#数据库文件位置规范) - 所有DB文件必须在data/目录

### API设计模式
- [GraphQL实施经验](./api-design-patterns.md#graphql实施经验) - Schema设计、DataLoader优化
- [Service层缓存集成](./api-design-patterns.md#service层缓存集成) - @cached装饰器使用
- [API缓存失效策略](./api-design-patterns.md#api缓存失效策略) - CacheInvalidator使用
- [DDD架构实施](./api-design-patterns.md#ddd架构实施) - 领域驱动设计
- [Canvas系统设计模式](./api-design-patterns.md#canvas系统设计模式) - Builder、Facade、Strategy模式

### 调试技能
- [Chrome DevTools MCP调试法](./debugging-skills.md#chrome-devtools-mcp调试法) - 标准调试流程
- [Subagent并行分析法](./debugging-skills.md#subagent并行分析法) - 根因分析策略

### 重构检查清单
- [TDD重构流程](./refactoring-checklist.md#tdd重构流程) - Red-Green-Refactor循环
- [代码审查清单](./refactoring-checklist.md#代码审查清单) - React、Python、安全、性能、测试
- [Brainstorming系统化设计](./refactoring-checklist.md#brainstorming系统化设计) - 系统化设计流程
- [技术债务管理](./refactoring-checklist.md#技术债务管理) - 技术债务识别和偿还

### 部署与运维
- [部署流程规范](./deployment-operations.md#部署流程规范) - 生产环境部署检查清单
- [环境配置管理](./deployment-operations.md#环境配置管理) - 开发/测试/生产环境隔离
- [监控与告警](./deployment-operations.md#监控与告警) - 性能监控、错误追踪
- [日志管理](./deployment-operations.md#日志管理) - 日志收集、存储、分析
- [备份与恢复](./deployment-operations.md#备份与恢复) - 数据备份策略、灾难恢复

### 项目管理
- [需求管理流程](./project-management.md#需求管理流程) - 需求收集、分析、优先级排序
- [迭代规划](./project-management.md#迭代规划) - Sprint规划、任务分解
- [代码审查规范](./project-management.md#代码审查规范) - PR审查流程、检查清单
- [技术债务管理](./project-management.md#技术债务管理) - 债务识别、优先级、偿还计划
- [团队协作](./project-management.md#团队协作) - 沟通流程、文档规范

---

## 快速查找场景

| 场景 | 经验文档 | 章节 |
|-----|---------|-----|
| ⚡ DataLoader批量查询 | [综合性能优化](./2026-03-07-comprehensive-optimization-experience.md) | DataLoader批量查询优化 (2026-03-09新增) |
| 💾 Dashboard缓存失效 | [综合性能优化](./2026-03-07-comprehensive-optimization-experience.md) | Dashboard实时优化 (2026-03-09新增) |
| 🔄 React组件优化 | [综合性能优化](./2026-03-07-comprehensive-optimization-experience.md) | React组件优化模式 (2026-03-09新增) |
| ⚡ N+1查询修复 | [综合性能优化](./2026-03-07-comprehensive-optimization-experience.md) | N+1查询修复 (2026-03-09新增) |
| 🚨 React应用挂载 | [测试指南](./testing-guide.md) | React挂载问题诊断 |
| 🌐 Agent-Browser测试 | [Agent-Browser Testing](./agent-browser-testing.md) | os error 35、命令链、替代方案 (2026-03-20新增) ⭐ |
| 🔍 Chrome DevTools调试 | [测试指南](./testing-guide.md) | Chrome MCP调试法 |
| 📝 mypy类型错误 | [Python开发](./python-development.md) | mypy --strict合规 |
| ⚡ Vite-Apollo兼容性 | [React最佳实践](./react-best-practices.md) | Vite兼容性 |
| 🔴 GraphQL 400错误 | [Event Node Builder错误](./event-node-builder-errors.md) | 枚举不匹配案例 (2026-03-08新增) |
| 🔒 GraphQL字段完整性 | [GraphQL字段完整性](./graphql-field-completeness.md) | hive_type字段4层修复 (2026-03-13新增) |
| 💾 缓存失效分析 | [性能模式](./performance-patterns.md) | 缓存失效分析 |
| 🚀 并行优化策略 | [综合性能优化](./2026-03-07-comprehensive-optimization-experience.md) | 并行执行策略 (2026-03-09新增) |
| 🚨 React Hooks错误 | [React最佳实践](./react-best-practices.md) | Hooks规则 |
| ⚠️ React defaultProps警告 | [React最佳实践](./react-best-practices.md) | React 18+ defaultProps已废弃 (2026-03-08新增) |
| 🐌 页面加载超时 | [React最佳实践](./react-best-practices.md) | Lazy Loading |
| 🔒 SQL注入风险 | [安全要点](./security-essentials.md) | SQL注入防护 |
| 🧪 测试数据验证 | [安全要点](./security-essentials.md) | 测试数据与Entity验证兼容性 (2026-03-16新增) |
| 🧪 E2E测试失败 | [测试指南](./testing-guide.md) | E2E测试方法论 |
| 📁 E2E测试清理 | [测试指南](./testing-guide.md) | E2E测试目录清理 (2026-03-16新增) |
| ⚙️ Playwright配置 | [测试指南](./testing-guide.md) | Playwright配置优化 (2026-03-16新增) |
| ⚡ 查询性能差 | [性能模式](./performance-patterns.md) | N+1查询优化 |
| 🗄️ 数据库迁移 | [数据库模式](./database-patterns.md) | game_gid迁移 |
| 🏗️ Repository迁移 | [Repository Migration](./repository-migration.md) | Dict到Entity迁移 (2026-03-20新增) ⭐ |
| 🏛️ Service架构 | [Service Architecture](./service-architecture.md) | ERS架构合规 (2026-03-20新增) ⭐ |
| 🔧 API错误处理 | [API设计模式](./api-design-patterns.md) | 错误处理模式 |
| 🐛 Bug调试方法 | [调试技能](./debugging-skills.md) | Chrome DevTools MCP |
| 🚀 生产部署 | [部署与运维](./deployment-operations.md) | 部署流程规范 |
| 📋 项目管理 | [项目管理](./project-management.md) | 需求管理流程 |
| 🔧 TypeScript迁移 | [TypeScript迁移](./typescript-migration.md) | Apollo Client 3.x兼容性 (2026-03-11新增) |
| 🔒 Security Integration | [Security Integration Testing](./security-integration-testing.md) | SQL注入防护、XSS检测 (2026-03-11新增) |
| 🎯 Mutation业务逻辑 | [Mutation Business Logic](./mutation-business-logic.md) | 5层验证架构 (2026-03-11新增) |
| 🔄 测试修复迭代 | [Test-Fix Iteration](./test-fix-iteration.md) | TDD方法论 (2026-03-11新增) |

---

## 经验贡献

**最新贡献 (2026-03-16晚) - Archive报告经验补充**：
- ✅ **安全要点** - 测试数据与Entity验证兼容性、Environment-aware验证模式、测试环境灵活数据创建（1个新经验，基于CRITICAL-ROOT-CAUSE-ANALYSIS和GAME-ENTITY-VALIDATION-FIX）⭐⭐⭐
- ✅ **性能模式** - 键级锁优化（1.99x提升）、Bloom Filter内存优化（95%减少）、ERS架构迁移最佳实践（3个新经验，基于FINAL-ARCHITECTURE和P1-PERFORMANCE-OPTIMIZATION）⭐⭐⭐
- ✅ **测试指南** - E2E测试目录清理、Playwright配置优化（分层测试策略）、SQL注入防护验证（3个新经验，基于FINAL_SUMMARY_TEST_CEAUNUP、E2E-TEST-FINAL-REPORT、PHASE-4-TEST-SUMMARY）⭐⭐⭐

**最新贡献 (2026-03-16下午)**：
- ✅ **E2E测试报告经验整合** - SQL标识符清理与安全验证、React Chrome MCP兼容性模式、Chrome MCP事件流分析、useEffect无限循环预防、500错误根因分析方法、E2E测试场景设计、性能影响评估、安全验证（8个新经验，基于E2E-TESTING-REPORT-2026-03-13）⭐⭐⭐
- ✅ **Chrome MCP Modal修复经验** - Chrome MCP fill不触发onChange、useEffect依赖数组最佳实践、useRef类型声明、批量更新优化、条件检查、TypeScript类型安全、修复优先级分类、可复用Hook模式、测试验证方法（9个新经验，基于CHROME-MCP-MODAL-FIX-REPORT）⭐⭐⭐

**最新贡献 (2026-03-16下午 - 之前)**：
- ✅ **TDD完整实现原则** - "不可简化实现"核心原则、3种错误实现模式（症状修复/占位符/绕过验证）、TDD Red-Green-Refactor完整流程、4级违规后果、智能缓存失效双层策略（基于TDD Green Phase完成报告）⭐⭐⭐
- ✅ **缓存失效调试经验** - 3个独立根因分析方法（数据未保存/缓存键不匹配/SQL错误）、并行修复执行计划（3个Phase，35分钟）、完整日志验证策略、3种缓存失效修复方案（基于Cache Invalidation Fix Design）⭐⭐⭐
- ✅ **HQL Preview根因分析** - 3WHY分析方法（WHY验证/HOW传播/WHAT现实）、错误传播路径追踪、SQL标识符验证模式、3层修复策略（自动清理/引用标识符/数据库迁移）、完整测试计划（基于HQL Preview 500 Root Cause Analysis）⭐⭐⭐

**近期贡献 (2026-03-11至2026-03-13)**：
- ✅ **GraphQL字段完整性经验** - hive_type字段4层修复策略、GraphQL Schema → DataLoader → TypeScript → UI组件完整性检查、避免字段遗漏（基于EventParameter字段丢失修复）
- ✅ **TypeScript迁移经验** - Apollo Client 3.x兼容性处理、类型重复定义解决方案、Template Literal语法错误修复（基于61个TypeScript错误修复）
- ✅ **Security Integration Testing** - SQL注入防护验证、XSS攻击检测、白名单验证策略、测试通过率从20%提升到85%（基于4轮测试修复迭代）
- ✅ **Mutation Business Logic** - 5层验证架构、完整实现原则、安全加固、缓存失效策略（基于3个Event Mutations业务逻辑实现）
- ✅ **Test-Fix Iteration Methodology** - 4轮迭代模式、TDD + 并行执行策略、自动化验证流程、从20%提升到100%测试通过率（基于4轮测试修复迭代）

**如何贡献经验**：
1. 修复问题后，提取经验点
2. 更新对应的经验文档（使用统一模板）
3. 在CLAUDE.md中添加简短记录和链接
4. 将详细报告归档到 `docs/archive/`

**经验模板**：
```markdown
### 经验标题

**优先级**: P0/P1/P2
**出现次数**: X次
**来源文档**: [链接1], [链接2]
**最后更新**: 2026-02-23

#### 问题现象
- 症状描述

#### 根本原因
- 技术原因

#### 解决方案
代码示例

#### 预防措施
- 代码审查清单
- 自动化测试

#### 相关经验
- [相关经验1](#link)
```

---

## 统计信息

- **经验文档总数**: 25个 (+4个，2026-03-20新增)
- **P0核心经验**: 12个主题（41个经验点 +20个，2026-03-20新增）
- **P1重要经验**: 10个主题（49个经验点 +3个，2026-03-16新增）
- **P2技巧经验**: 2个主题
- **P0完成度**: 100% ✅
- **P1完成度**: 100% ✅
- **整合文档数**: 492个 (+46个archive报告 + 8个March reports，2026-03-20)
- **归档报告数**: 369个 (+7个priority archive报告，2026-03-16)
- **文档减少率**: 92.5% (492 → 41个活跃文档，2026-03-20)

## 新增经验 (2026-03-05)

### 测试指南
- [E2E测试完整流程](./testing-guide.md#e2e测试完整流程) - Chrome DevTools MCP 6步流程 (P0)
- [测试失败诊断方法](./testing-guide.md#测试失败诊断) - React Hooks、加载超时、API错误 (P0)
- [Ralph Loop迭代测试法](./testing-guide.md#ralph-loop迭代测试法) - 5步迭代测试 (P1)
- [API契约测试](./testing-guide.md#api契约测试) - 端点存在性、参数一致性 (P0)
- [React应用挂载问题诊断](./testing-guide.md#react应用挂载问题诊断) - E2E测试经验 (P0)
- [Chrome DevTools MCP调试法](./testing-guide.md#chrome-devtools-mcp测试流程) - 标准调试流程 (P0)

### React最佳实践
- [Lazy Loading决策标准](./react-best-practices.md#lazy-loading最佳实践) - 组件大小与使用规范 (P0)
- [双重Suspense嵌套问题](./react-best-practices.md#lazy-loading最佳实践) - 问题诊断与解决 (P0)
- [React Hooks规则更新](./react-best-practices.md#react-hooks-规则) - 条件返回之前调用Hook (P0)
- [Vite与Apollo Client兼容性](./react-best-practices.md#vite与apollo-client兼容性) - Vite 7.x兼容性 (P1)

### 调试技能
- [Chrome DevTools MCP调试流程](./debugging-skills.md#chrome-devtools-mcp调试法) - 6步标准流程 (P0)
- [错误检测模式](./debugging-skills.md#chrome-devtools-mcp调试法) - React Hooks、加载超时、API错误 (P0)
- [Canvas组件调试](./debugging-skills.md#canvas组件调试) - 事件节点配置问题诊断 (P1)
- [并行Subagent分析](./debugging-skills.md#subagent并行分析法) - 3步分析策略 (P1)

### API设计模式
- [路由参数设计规范](./api-design-patterns.md#路由参数设计规范) - game_gid vs game_id (P0)
- [API契约一致性验证](./api-design-patterns.md#api契约一致性验证) - 验证工具和检查项 (P0)

### 重构检查清单
- [Canvas架构重构](./refactoring-checklist.md#canvas架构重构) - 事件节点架构优化 (P1)

### Python开发
- [mypy --strict合规](./python-development.md#mypy---strict合规) - 类型注解最佳实践 (P0)
- [GenericRepository类型安全](./python-development.md#genericsrepository类型安全) - 泛型Repository设计 (P1)

### 性能优化
- [缓存失效分析](./performance-patterns.md#缓存失效分析) - 缓存未命中原因和策略 (P0)
- [并行优化策略](./performance-patterns.md#并行优化策略) - 并行执行模式 (P0)

### 归档文档
- 15个E2E测试报告 → docs/archive/2026/03-march/reports/
- 55个PNG截图 → docs/archive/2026/03-march/screenshots/
- 5个临时指南 → docs/archive/2026/03-march/temp-guides/

---

## 相关文档

### 主要索引
- [CLAUDE.md](../../CLAUDE.md) - 项目开发规范（包含经验文档链接）
- [docs/README.md](../README.md) - 文档中心索引
- [archive/README.md](../archive/README.md) - 归档报告索引
- [../../CHANGELOG.md](../../CHANGELOG.md) - 项目更新日志

### 补充索引（2026-03-16新增）
- [缺失文档索引](./development-docs-index.md) - 待创建的development文档列表
- [归档报告导航](./archived-reports-index.md) - 临时报告归档位置导航

### 链接优化工具
- 链接检查脚本: `/tmp/check_md_links.sh`
- 批量修复脚本: `/tmp/fix_links_batch.sh`
- 快速检查脚本: `/tmp/quick_link_check.sh`

---

## 缺失文档说明

部分文档在经验文档中被引用但尚未创建。以下是列表：

### P0优先级（高价值，计划创建）
- `development/TYPESCRIPT-QUICK-REF.md` - TypeScript快速参考
- `development/sql-validator-guidelines.md` - SQL验证器指南

### P1优先级（中价值，后续创建）
- `development/typescript-best-practices.md` - TypeScript最佳实践
- `development/testing-best-practices.md` - 测试最佳实践

### 已归档/整合的报告
以下临时报告已归档或整合到其他文档：
- `GRAPHQL-DATALOADER-REPO-STATS.md` → 整合到[综合性能优化经验](./2026-03-07-comprehensive-optimization-experience.md)
- `PERF-BENCHMARK-BEFORE-AFTER.md` → 整合到[综合性能优化经验](./2026-03-07-comprehensive-optimization-experience.md)

### 如何帮助创建这些文档？

如果您对某个主题有经验，欢迎创建对应的文档！
1. 参考现有经验文档的格式
2. 添加实际内容和示例
3. 更新本索引

---

**链接有效性说明**:
当前26%的链接有效性是**诚实的数字**，代表：
- ✅ 26%：指向真实存在的文档
- ⏳ 74%：指向待创建文档、已归档报告、或需要人工验证的路径

我们不使用"占位符"来虚假地提升这个数字。
