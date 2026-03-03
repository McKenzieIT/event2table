# Event2Table 文档中心

> **🆕 更新 (2026-03-02)**: 完善归档文档系统，建立文档生命周期管理
> **🆕 更新 (2026-02-24)**: 建立经验文档系统，整合399个文档精华

---

## 🚀 快速开始（推荐阅读顺序）

1. **新人入门**: [快速开始](development/QUICKSTART.md)
2. **核心规范**: [CLAUDE.md](../CLAUDE.md)（开发规范）
3. **经验文档**: [经验文档索引](lessons-learned/README.md) ⭐ **重要**
4. **架构设计**: [架构文档](development/architecture.md)

---

## 📚 经验文档 ⭐ **必读**

> 所有项目经验已整合到经验文档系统，避免重复，持续更新
> **P0完成度**: 100% ✅ | **P1完成度**: 100% ✅

### 按主题

- **[React最佳实践](lessons-learned/react-best-practices.md)** - Hooks规则、Lazy Loading、性能优化
  - React Hooks规则 ⚠️ P0极其重要 - 避免Hooks顺序错误导致组件崩溃
  - Lazy Loading最佳实践 ⚠️ P0极其重要 - 避免双重Suspense嵌套导致加载超时
  - Input组件CSS布局规范 ⚠️ P0极其重要 - 始终使用label prop，Grid架构说明
  - React性能优化 ⭐ P1重要 - React.memo、useCallback
  - React子组件定义顺序 ⭐ P1重要 - 组件定义顺序
  - useEffect依赖数组最佳实践 ⭐ P1重要 - 避免useCallback+useEffect组合
  - 组件导出规范 ⭐ P1重要 - 导出原始组件名和别名
  - API响应数据结构处理 ⭐ P1重要 - 处理嵌套数据结构

- **[测试指南](lessons-learned/testing-guide.md)** - E2E测试、TDD、自动化测试
  - E2E测试方法论 ⚠️ P0极其重要 - Chrome DevTools MCP测试流程
  - TDD实践 ⚠️ P0极其重要 - Red-Green-Refactor循环
  - 错误消息质量 ⭐ P1重要 - 用户友好错误消息
  - 测试自动化 ⭐ P1重要 - Pre-commit Hook强制测试
  - 避免重复工作 ⭐ P1重要 - 调查优先于实现
  - 测试方法论演进 ⭐ P1重要 - Phase 1 vs Phase 2测试方法

- **[安全要点](lessons-learned/security-essentials.md)** - XSS防护、SQL注入、输入验证
  - SQL注入防护 ⚠️ P0极其重要 - 参数化查询、SQLValidator
  - XSS防护 ⚠️ P0极其重要 - HTML转义、React自动转义
  - 输入验证 ⚠️ P0极其重要 - Pydantic Schema验证
  - 异常信息脱敏 ⚠️ P0极其重要 - 错误响应不暴露敏感信息
  - Legacy API废弃管理 ⭐ P1重要 - DeprecationDecorator
  - GenericRepository安全验证 ⭐ P1重要 - 表名/字段名验证
  - 批量删除验证 ⭐ P1重要 - 输入验证和系统保护

- **[性能模式](lessons-learned/performance-patterns.md)** - 缓存、N+1查询、优化技巧
  - 缓存策略 ⚠️ P0极其重要 - Redis缓存TTL 5-10分钟、缓存清理、一致性验证
  - N+1查询优化 ⚠️ P0极其重要 - 使用JOIN、合并统计查询
  - 分页支持 ⚠️ P0极其重要 - LIMIT/OFFSET分页
  - 数据库索引 ⭐ P1重要 - 索引设计和优化
  - game_gid转换缓存 ⭐ P1重要 - LRU缓存优化
  - Dashboard统计查询合并 ⭐ P1重要 - 合并统计查询
  - 多级缓存架构 ⭐ P1重要 - L1+L2+L3缓存层级
  - Cache Tags系统 ⭐ P1重要 - 按标签批量失效缓存
  - 性能监控装饰器 ⭐ P1重要 - 函数执行时间监控

- **[数据库模式](lessons-learned/database-patterns.md)** - game_gid使用、事务、迁移
  - game_gid迁移经验 ⚠️ P0极其重要 - game_gid vs game_id区别、表名生成规范
  - 数据库事务 ⭐ P1重要 - 事务使用原则
  - 数据隔离规范 ⚠️ P0极其重要 - 三环境隔离、STAR001保护
  - 数据库文件位置规范 ⚠️ P0极其重要 - 所有DB文件必须在data/目录

- **[API设计模式](lessons-learned/api-design-patterns.md)** - 分层架构、错误处理
  - 分层架构 ⚠️ P0极其重要 - API → Service → Repository → Schema
  - 错误处理 ⚠️ P0极其重要 - 具体可操作的错误消息
  - GraphQL实施经验 ⭐ P1重要 - Schema设计、DataLoader优化
  - Service层缓存集成 ⭐ P1重要 - @cached装饰器使用
  - API缓存失效策略 ⭐ P1重要 - CacheInvalidator使用
  - DDD架构实施 ⭐ P1重要 - 领域驱动设计
  - Canvas系统设计模式 ⭐ P1重要 - Builder、Facade、Strategy模式
  - HQL生成器重构经验 ⭐ P1重要 - 模块化V2架构

- **[调试技能](lessons-learned/debugging-skills.md)** - Chrome DevTools MCP、Subagent分析
  - Chrome DevTools MCP调试法 ⚠️ P0极其重要 - 标准调试流程
  - Subagent并行分析法 ⭐ P1重要 - 根因分析策略

- **[重构检查清单](lessons-learned/refactoring-checklist.md)** - TDD、代码审查、技术债务
  - TDD重构流程 ⚠️ P0极其重要 - Red-Green-Refactor循环
  - 代码审查清单 ⚠️ P0极其重要 - React、Python、安全、性能、测试
  - Brainstorming系统化设计 ⭐ P1重要 - 系统化设计流程
  - 技术债务管理 ⭐ P1重要 - 技术债务识别和偿还

### 按优先级

#### P0 核心经验 ⚠️ **必须掌握**

**React最佳实践**:
- [React Hooks规则](lessons-learned/react-best-practices.md#react-hooks-规则) - 避免Hooks顺序错误
- [Lazy Loading最佳实践](lessons-learned/react-best-practices.md#lazy-loading) - 避免加载超时

**测试指南**:
- [E2E测试方法论](lessons-learned/testing-guide.md#e2e测试) - Chrome DevTools MCP测试流程
- [TDD实践](lessons-learned/testing-guide.md#tdd实践) - 测试驱动开发

**安全要点**:
- [SQL注入防护](lessons-learned/security-essentials.md#sql注入防护) - 参数化查询
- [XSS防护](lessons-learned/security-essentials.md#xss防护) - HTML转义
- [异常信息脱敏](lessons-learned/security-essentials.md#异常信息脱敏) - 错误响应安全

**性能模式**:
- [缓存策略](lessons-learned/performance-patterns.md#缓存策略) - Redis缓存TTL 5-10分钟
- [N+1查询优化](lessons-learned/performance-patterns.md#n1查询优化) - 使用JOIN合并查询

**数据库模式**:
- [game_gid迁移经验](lessons-learned/database-patterns.md#game_gid迁移) - game_gid vs game_id
- [数据隔离规范](lessons-learned/database-patterns.md#数据隔离规范) - 测试数据库隔离

**API设计模式**:
- [分层架构](lessons-learned/api-design-patterns.md#分层架构) - 四层架构设计
- [错误处理](lessons-learned/api-design-patterns.md#错误处理) - 用户友好错误消息

#### P1 重要经验 ⭐ **推荐学习**

- [React性能优化](lessons-learned/react-best-practices.md#性能优化) - React.memo、useCallback
- [测试自动化](lessons-learned/testing-guide.md#测试自动化) - Pre-commit Hook
- [输入验证](lessons-learned/security-essentials.md#输入验证) - Pydantic Schema
- [数据库索引](lessons-learned/performance-patterns.md#数据库索引) - 索引设计
- [数据库事务](lessons-learned/database-patterns.md#数据库事务) - 事务使用
- [GraphQL实施经验](lessons-learned/api-design-patterns.md#graphql实施经验) - DataLoader
- [Chrome DevTools MCP调试法](lessons-learned/debugging-skills.md#chrome-devtools-mcp调试法) - 标准流程
- [代码审查清单](lessons-learned/refactoring-checklist.md#代码审查清单) - 完整检查项

### 快速查找场景

| 我想要... | 查看文档 | 章节 |
|---------|---------|-----|
| 🚨 解决React Hooks错误 | [React最佳实践](lessons-learned/react-best-practices.md) | Hooks规则 |
| 🐌 页面加载超时 | [React最佳实践](lessons-learned/react-best-practices.md) | Lazy Loading |
| 🔒 防止SQL注入 | [安全要点](lessons-learned/security-essentials.md) | SQL注入防护 |
| 🧪 编写E2E测试 | [测试指南](lessons-learned/testing-guide.md) | E2E测试 |
| ⚡ 优化查询性能 | [性能模式](lessons-learned/performance-patterns.md) | N+1查询 |
| 🗄️ 了解game_gid迁移 | [数据库模式](lessons-learned/database-patterns.md) | game_gid迁移 |
| 🔧 处理API错误 | [API设计模式](lessons-learned/api-design-patterns.md) | 错误处理 |
| 🐛 调试Bug | [调试技能](lessons-learned/debugging-skills.md) | Chrome DevTools MCP |
| 📝 代码审查 | [重构检查清单](lessons-learned/refactoring-checklist.md) | 代码审查清单 |

---

## 🏗️ 开发文档

### 架构与设计

- **[架构设计](development/architecture.md)** - 分层架构设计
  - 四层架构（API → Service → Repository → Entity）
  - 关注点分离原则
  - ERS架构（Entity-Repository-Service）

- **[Repository模式指南](development/repository-pattern-guide.md)** ⭐ **NEW**
  - GenericRepository使用方法
  - Entity架构集成
  - 缓存策略最佳实践
  - Service层集成示例
  - 完整的代码示例和常见问题

- **[game_gid迁移指南](development/GAME_GID_MIGRATION_GUIDE.md)** - game_gid迁移
  - game_gid vs game_id区别
  - 迁移前后对比
  - 验证清单

- **[STAR001游戏保护](development/STAR001-GAME-PROTECTION.md)** - 数据保护规则
  - 核心规则：禁止删除STAR001数据
  - 测试GID规范（90000000+范围）
  - 违规后果

### 快速开始

- **[快速开始](development/QUICKSTART.md)** - 快速上手指南
  - 环境设置
  - 依赖安装
  - 数据库初始化
  - 启动应用

### 其他开发文档

- **[贡献指南](development/contributing.md)** - 贡献指南
- **[Unit of Work指南](development/UNIT_OF_WORK_GUIDE.md)** - Unit of Work模式
- **[Apollo Client设置](development/APOLLO_CLIENT_SETUP_SUMMARY.md)** - GraphQL客户端设置
- **[分支保护设置](development/branch-protection-setup.md)** - Git分支保护

---

## 📊 归档文档

> 历史报告和文档已按主题归档，便于查找和参考

### 归档索引

- **[归档文档索引](archive/README.md)** - 完整的归档文档导航中心

### 归档内容（按主题分类）

#### 🔌 GraphQL 专题
- **[GraphQL 迁移文档](graphql-migration/)** - REST 到 GraphQL 迁移
  - GraphQL API 文档
  - 迁移计划和进度
  - 批量操作 GraphQL Schema
  - V2 API GraphQL 设计

#### 🚀 架构与性能优化
- **后端优化报告** - Phase 1-4全面优化（57+优化点）
  - 安全加固（SQL注入防护、XSS防护）
  - 性能优化（N+1查询修复、缓存优化）
  - 架构重构（Service层、Repository层、门面模式）
  - game_gid迁移（完全切换到game_gid）
- **缓存系统优化** - 缓存覆盖率从7.5%提升到60%
- **前端性能优化** - React组件优化、Lazy Loading最佳实践

#### 🧪 测试与验证
- **E2E测试报告** - Chrome DevTools MCP测试流程
- **单元测试报告** - 测试覆盖率达到85%+
- **测试基础设施** - 测试环境隔离、TDD实践
- **API契约测试** - 前后端API一致性验证

#### 📝 项目进度与里程碑
- **Entity架构迁移** - 6/8核心模块完成迁移（75%）
- **REST到GraphQL迁移** - API迁移进度跟踪
- **TypeScript迁移** - 前端代码完全TypeScript化
- **Phase 4完成报告** - 项目阶段性总结

#### 🔧 问题修复与改进
- **事件节点构建器修复** - 6大问题解决
- **Input组件架构重构** - CSS布局修复
- **Dashboard统计修复** - 数据准确性改进
- **各种Bug修复报告** - 具体问题分析和解决方案

#### 📚 专题报告
- **开发规范更新** - CLAUDE.md版本历史
- **文档重组报告** - 文档结构优化
- **技术债务清理** - DDD Legacy代码清理
- **最佳实践总结** - 各种开发经验汇总

---

## 🔍 文档统计

### 经验文档系统
- **经验文档总数**: 11个
- **P0核心经验**: 7个主题（22个经验点）✅ 100%完成
- **P1重要经验**: 8个主题（32个经验点）✅ 100%完成
- **整合文档数**: 399个
- **经验贡献者**: Event2Table Development Team

### 归档文档系统
- **归档报告总数**: 670+个
- **分类主题**: 6大主题（架构、测试、进度、修复、专题、GraphQL）
- **文档减少率**: 53% (676 → 317个活跃文档，含归档)

### 文档覆盖度
- **开发规范**: 95% ✅
- **架构文档**: 100% ✅
- **测试指南**: 100% ✅
- **经验文档**: 100% ✅

---

## 📖 使用指南

### 文档生命周期管理

Event2Table项目采用**三阶段文档生命周期管理**：

#### 1. 活跃文档（docs/）
- **位置**: `docs/development/`, `docs/lessons-learned/`, `docs/api/`等
- **特点**: 经常更新，反映当前最佳实践
- **更新频率**: 每次问题修复后立即更新
- **维护者**: 活跃开发团队

#### 2. 归档文档（docs/archive/）
- **位置**: `docs/archive/`
- **特点**: 按主题分类，历史参考价值
- **归档条件**:
  - 完成阶段性任务（如Phase 4完成）
  - 重大功能上线（如Entity架构迁移）
  - 月度总结报告（如2026-02总结）
- **保留期限**: 永久保留，供参考

#### 3. 临时文档（临时创建，及时清理）
- **位置**: 项目根目录（临时）
- **特点**: 短期使用，完成后删除或归档
- **生命周期**:
  - 创建: 开始调查问题时
  - 使用: 调查和修复期间
  - 归档: 修复完成后移到 `docs/archive/`
  - 删除: 无价值临时笔记直接删除

### 文档更新流程

**新增经验时**：
```bash
# 1. 修复问题后提取经验
# 2. 更新对应经验文档（docs/lessons-learned/）
# 3. 在CLAUDE.md中添加简短记录
# 4. 将详细报告归档（docs/archive/YYYY-MM/）
```

**完成阶段时**：
```bash
# 1. 创建总结报告（docs/reports/YYYY-MM-DD/）
# 2. 更新CLAUDE.md版本历史
# 3. 将相关报告归档（docs/archive/YYYY-MM/）
# 4. 更新文档统计（docs/README.md）
```

### 如何使用经验文档

1. **遇到问题** → 先查阅经验文档，看是否有类似问题
2. **修复问题后** → 提取经验，更新对应经验文档
3. **Code Review** → 检查是否违反经验文档中的规范
4. **定期回顾** → 每月回顾经验文档，提取共性模式

### 经验贡献指南

**如何贡献经验**：
1. 修复问题后，提取经验点
2. 更新对应的经验文档（使用统一模板）
3. 在CLAUDE.md中添加简短记录和链接
4. 将详细报告归档到 `docs/archive/YYYY-MM/`
5. 更新 `docs/README.md` 文档统计

**经验模板**：
```markdown
### 经验标题

**优先级**: P0/P1/P2
**出现次数**: X次
**来源文档**: [链接1], [链接2]
**最后更新**: 2026-03-02

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

#### 案例文档
- [详细案例](../archive/2026-03/case-report.md)
```

---

## 🔗 相关文档

- **[CLAUDE.md](../CLAUDE.md)** - 项目开发规范（包含经验文档链接）
- **[CHANGELOG.md](../CHANGELOG.md)** - 更新日志
- **[README.md](../README.md)** - 项目说明

---

**文档版本**: 2.2
**最后更新**: 2026-03-03
**维护者**: Event2Table Development Team

---

## 📋 更新日志

### v2.2 (2026-03-03)
- ✅ **文档整合完成**：移除 `docs/docs/` 重复嵌套结构（323个文档）
- ✅ **GraphQL 专题归档**：8个GraphQL文档集中到 `docs/graphql-migration/`
- ✅ **旧报告归档**：2月报告移至 `docs/archive/2026-02/reports/`
- ✅ **经验文档系统**：11个经验文档，64个经验点，整合676个文档精华
- ✅ **活跃文档优化**：从676个减少到核心文档，归档文档系统完善

### v2.1 (2026-03-02)
- ✅ 完善归档文档系统，添加按主题分类的索引
- ✅ 更新文档统计，经验文档从9个增加到11个
- ✅ 新增文档生命周期管理说明
- ✅ 新增经验贡献指南

### v2.0 (2026-02-24)
- ✅ 建立经验文档系统，整合399个文档精华
- ✅ 按主题和优先级组织经验文档
- ✅ 添加快速查找场景表
