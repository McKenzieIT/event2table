# 经验文档索引

> **🎯 目标**: 避免重复经验，提供集中的知识库
> **📊 来源**: 整合了399个文档的精华经验
> **🔄 更新**: 持续更新，每次问题修复后立即更新

---

## P0 核心经验 ⚠️ **必须掌握**

### React最佳实践
- [React Hooks规则](./react-best-practices.md#react-hooks-规则) - 避免Hooks顺序错误
- [Lazy Loading最佳实践](./react-best-practices.md#lazy-loading最佳实践) - 避免加载超时
- [Input组件CSS布局规范](./react-best-practices.md#input组件css布局规范) - 始终使用label prop

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

---

## 快速查找场景

| 场景 | 经验文档 | 章节 |
|-----|---------|-----|
| 🚨 React Hooks错误 | [React最佳实践](./react-best-practices.md) | Hooks规则 |
| 🐌 页面加载超时 | [React最佳实践](./react-best-practices.md) | Lazy Loading |
| 🔒 SQL注入风险 | [安全要点](./security-essentials.md) | SQL注入防护 |
| 🧪 E2E测试失败 | [测试指南](./testing-guide.md) | E2E测试方法论 |
| ⚡ 查询性能差 | [性能模式](./performance-patterns.md) | N+1查询优化 |
| 🗄️ 数据库迁移 | [数据库模式](./database-patterns.md) | game_gid迁移 |
| 🔧 API错误处理 | [API设计模式](./api-design-patterns.md) | 错误处理模式 |
| 🐛 Bug调试方法 | [调试技能](./debugging-skills.md) | Chrome DevTools MCP |

---

## 经验贡献

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

- **经验文档总数**: 9个
- **P0核心经验**: 7个主题（22个经验点）
- **P1重要经验**: 8个主题（32个经验点）
- **P0完成度**: 100% ✅
- **P1完成度**: 100% ✅
- **整合文档数**: 399个
- **归档报告数**: 269个
- **文档减少率**: 87.5% (399 → 50)

---

## 相关文档

- [CLAUDE.md](../../CLAUDE.md) - 项目开发规范（包含经验文档链接）
- [docs/README.md](../README.md) - 文档中心索引
- [archive/README.md](../archive/README.md) - 归档报告索引
