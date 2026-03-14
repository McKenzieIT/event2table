# Event2Table 文档导航指南

> **最后更新**: 2026-03-05
> **版本**: 1.0

---

## 快速导航

### 新用户快速开始

1. **5分钟上手项目**: [快速开始指南](development/QUICKSTART.md)
2. **理解项目架构**: [架构设计文档](development/architecture.md)
3. **开发规范检查**: [CLAUDE.md](../CLAUDE.md) - 项目开发规范
4. **查找解决方案**: [经验文档索引](lessons-learned/README.md)

### 常见任务快速查找

| 我想... | 查看文档 |
|---------|---------|
| 🚀 快速上手 | [快速开始](development/QUICKSTART.md) |
| 📖 学习架构 | [架构设计](development/architecture.md) |
| 🐛 修复Bug | [调试技能](lessons-learned/debugging-skills.md) |
| ✅ 编写测试 | [测试指南](lessons-learned/testing-guide.md) |
| ⚡ 优化性能 | [性能模式](lessons-learned/performance-patterns.md) |
| 🔒 安全加固 | [安全要点](lessons-learned/security-essentials.md) |
| 📝 API开发 | [API设计模式](lessons-learned/api-design-patterns.md) |
| 🎨 前端开发 | [React最佳实践](lessons-learned/react-best-practices.md) |
| 🧪 E2E测试 | [测试指南](lessons-learned/testing-guide.md) |

---

## 文档分类导航

### 核心文档（必读）

#### 开发规范
- **[CLAUDE.md](../CLAUDE.md)** - 项目开发规范（最重要）
  - 环境设置和快速开始
  - Critical Rules（关键规则）
  - 编码规范（Python、TypeScript、SQL）
  - 问题修复记录
  - 经验文档快速查找

- **[README.md](README.md)** - 文档中心索引
  - 所有文档的导航中心
  - 快速查找各类文档

#### 经验文档系统
- **[经验文档索引](lessons-learned/README.md)** - 446个文档的精华经验 ⭐
  - P0核心经验（必须掌握）
  - P1重要经验（推荐学习）
  - 快速查找场景
  - 经验贡献指南

### 开发指南

#### 快速开始
- **[5分钟快速开始](development/QUICKSTART.md)** - 新用户必读
- **[环境搭建](development/getting-started.md)** - 开发环境配置
- **[贡献指南](development/contributing.md)** - 如何贡献代码

#### 架构设计
- **[架构设计文档](development/architecture.md)** - 分层架构设计 ⭐
  - API层、Service层、Repository层、Entity层
  - HQL生成器架构
  - Canvas系统设计

#### 开发规范
- **[API设计模式](lessons-learned/api-design-patterns.md)** - API开发规范
- **[React最佳实践](lessons-learned/react-best-practices.md)** - 前端开发规范
- **[游戏GID迁移指南](development/GAME_GID_MIGRATION_GUIDE.md)** - game_gid迁移经验

### 经验文档（按主题）

#### P0核心经验 ⚠️ **必须掌握**
- **[React最佳实践](lessons-learned/react-best-practices.md)**
  - React Hooks规则（避免Hooks顺序错误）
  - Lazy Loading最佳实践（避免加载超时）
  - Input组件CSS布局规范
  - Vite与Apollo Client兼容性

- **[测试指南](lessons-learned/testing-guide.md)**
  - E2E测试完整流程（Chrome DevTools MCP 6步流程）
  - TDD实践（Red-Green-Refactor循环）
  - 测试失败诊断方法
  - API契约测试

- **[安全要点](lessons-learned/security-essentials.md)**
  - SQL注入防护（参数化查询、SQLValidator）
  - XSS防护（HTML转义、React自动转义）
  - 输入验证（Pydantic Schema验证）
  - 异常信息脱敏

- **[性能模式](lessons-learned/performance-patterns.md)**
  - 缓存策略（Redis缓存TTL 5-10分钟）
  - N+1查询优化（使用JOIN、合并统计查询）
  - 并行优化策略
  - 分页支持（LIMIT/OFFSET分页）

- **[数据库模式](lessons-learned/database-patterns.md)**
  - game_gid迁移经验（game_gid vs game_id区别）
  - 数据库事务使用原则
  - 数据隔离规范（三环境隔离、STAR001保护）

- **[API设计模式](lessons-learned/api-design-patterns.md)**
  - 分层架构（API → Service → Repository → Schema）
  - 错误处理（具体可操作的错误消息）
  - 路由参数设计规范（game_gid vs game_id）
  - API契约一致性验证

#### P1重要经验 ⭐ **推荐学习**
- **[调试技能](lessons-learned/debugging-skills.md)**
  - Chrome DevTools MCP调试法（标准调试流程）
  - Subagent并行分析法（根因分析策略）
  - Canvas组件调试
  - 错误检测模式

- **[重构检查清单](lessons-learned/refactoring-checklist.md)**
  - TDD重构流程
  - 代码审查清单
  - Brainstorming系统化设计
  - 技术债务管理

- **[项目管理](lessons-learned/project-management.md)**
  - 并行开发策略
  - 分阶段重构策略
  - 零破坏性变更保证
  - 文档驱动开发

- **[部署与运维](lessons-learned/deployment-operations.md)**
  - 部署流程规范
  - 环境配置管理
  - 监控与告警
  - 日志管理

### 测试文档

- **[测试指南](lessons-learned/testing-guide.md)** - E2E测试规范 ⭐
  - 测试方法论
  - Chrome DevTools MCP测试流程
  - 测试报告模板

- **[测试报告归档](archive/2026/03-march/reports/)** - 历史测试报告

### API文档

- **[API文档中心](api/README.md)** - API文档索引 ⭐

### 架构决策记录

- **Note**: ADR文档待补充

### 缓存系统文档

- **[缓存系统文档中心](cache/README.md)** - 完整的缓存系统文档 ⭐
  - [5分钟快速开始](cache/quickstart/5-minute-guide.md) - 新用户5分钟上手
  - [常见问题FAQ](cache/quickstart/faq.md) - 10个最常见问题
  - [开发者指南](cache/development/developer-guide.md) - 深入了解架构
  - [故障排除手册](cache/operations/troubleshooting.md) - 解决80%常见问题
  - [部署运维文档](cache/operations/deployment.md) - 生产环境配置

### HQL生成器文档

- **[HQL文档中心](hql/)** - HQL生成器文档
  - [HQL安全开发指南](hql/hql-security-guide.md) - HQL安全规范 ⭐
  - [HQL注入防护示例](hql/hql-injection-prevention.md) - 实际漏洞案例 ⭐

### Canvas模块文档

- **[Canvas文档中心](canvas/)** - Canvas系统文档

### 归档文档

- **[归档文档索引](archive/README.md)** - 历史文档索引
- **[2026年3月归档](archive/2026/03-march/README.md)** - 2026-03文档归档

---

## 文档生命周期管理

### 活跃文档（docs/）
- 经常更新
- 反映当前最佳实践
- 包括：开发指南、测试文档、API文档、经验文档

### 归档文档（docs/archive/）
- 按主题分类
- 历史参考价值
- 组织结构：`archive/{主题}/{日期}/`

### 临时文档
- 短期使用
- 完成后删除或归档

---

## 文档更新流程

### 每次代码变更后
1. 更新API文档（如果修改了API）
2. 更新架构文档（如果修改了架构）
3. 更新经验文档（如果学到了新经验）
4. 提交文档和代码

### 完成阶段时
1. 整理重复文档
2. 归档过时文档
3. 更新文档索引
4. 更新CLAUDE.md

### 经验贡献
**如何贡献经验**:
1. 修复问题后，提取经验
2. 使用统一的经验模板
3. 在CLAUDE.md中添加简短记录
4. 更新对应经验文档

---

## 文档查找策略

### 按问题类型查找

| 问题类型 | 首选文档 | 备选文档 |
|---------|---------|---------|
| React应用挂载 | [测试指南](lessons-learned/testing-guide.md) | [React最佳实践](lessons-learned/react-best-practices.md) |
| 页面加载超时 | [React最佳实践](lessons-learned/react-best-practices.md) | [调试技能](lessons-learned/debugging-skills.md) |
| mypy类型错误 | [Python开发](lessons-learned/python-development.md) | [重构检查清单](lessons-learned/refactoring-checklist.md) |
| SQL注入风险 | [安全要点](lessons-learned/security-essentials.md) | [API设计模式](lessons-learned/api-design-patterns.md) |
| 缓存失效 | [性能模式](lessons-learned/performance-patterns.md) | [缓存系统](cache/README.md) |
| E2E测试失败 | [测试指南](lessons-learned/testing-guide.md) | [调试技能](lessons-learned/debugging-skills.md) |
| N+1查询 | [性能模式](lessons-learned/performance-patterns.md) | [数据库模式](lessons-learned/database-patterns.md) |

### 按开发阶段查找

| 开发阶段 | 推荐文档 |
|---------|---------|
| 项目启动 | [快速开始](development/QUICKSTART.md) + [架构设计](development/architecture.md) |
| 功能开发 | [TDD实践](lessons-learned/testing-guide.md) + [API设计模式](lessons-learned/api-design-patterns.md) |
| Bug修复 | [调试技能](lessons-learned/debugging-skills.md) + [经验文档索引](lessons-learned/README.md) |
| 性能优化 | [性能模式](lessons-learned/performance-patterns.md) + [缓存系统](cache/README.md) |
| 代码审查 | [重构检查清单](lessons-learned/refactoring-checklist.md) + [CLAUDE.md](../CLAUDE.md) |
| 部署上线 | [部署与运维](lessons-learned/deployment-operations.md) |

### 按文档类型查找

| 文档类型 | 路径 |
|---------|------|
| 开发指南 | docs/development/ |
| 经验文档 | docs/lessons-learned/ |
| 测试文档 | docs/testing/ |
| API文档 | docs/api/ |
| 架构文档 | docs/adr/ |
| 缓存文档 | docs/cache/ |
| 归档文档 | docs/archive/ |

---

## 文档质量检查清单

### 创建新文档前
- [ ] 确认文档类型（指南/报告/需求）
- [ ] 确认目标目录
- [ ] 使用标准命名格式（小写+连字符）
- [ ] 检查是否已有类似文档（避免重复）

### 归档文档前
- [ ] 确认文档已过时或不再活跃
- [ ] 更新相关引用
- [ ] 添加归档日期说明
- [ ] 移动到正确归档目录

### 删除文档前
- [ ] 确认无参考价值
- [ ] 检查是否有其他文档引用
- [ ] 确认可以安全删除

---

## 相关资源

### 项目文档
- **[CLAUDE.md](../CLAUDE.md)** - 项目开发规范
- **[README.md](../README.md)** - 项目说明
- **[CHANGELOG.md](../CHANGELOG.md)** - 更新日志

### 外部资源
- **[Flask官方文档](https://flask.palletsprojects.com/)**
- **[React官方文档](https://react.dev/)**
- **[Vite官方文档](https://vitejs.dev/)**
- **[Playwright官方文档](https://playwright.dev/)**

---

## 文档统计（2026-03-05）

- **活跃文档**: 110个
- **归档文档**: 612个
- **经验文档**: 12个
- **P0核心经验**: 8个主题（34个经验点）
- **P1重要经验**: 10个主题（46个经验点）
- **文档覆盖率**: 100%
- **经验整合率**: 92.5% (493个文档 → 12个经验文档)

---

**文档版本**: 1.0
**最后更新**: 2026-03-05
**维护者**: Event2Table Development Team
