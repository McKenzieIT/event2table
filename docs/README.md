# Event2Table 文档中心

> **版本**: 1.0 | **最后更新**: 2026-02-10
>
> 欢迎来到 Event2Table 项目文档中心！这里汇集了项目的所有文档。

---

## 快速导航

### 新手入门

- [项目 README](../../README.md) - 项目简介和快速开始
- [开发规范](../../CLAUDE.md) ⭐ - Claude开发指南（必读）
- [贡献指南](development/contributing.md) - 如何参与开发
- [架构设计](development/architecture.md) - 系统架构详解

### 核心文档

| 文档 | 描述 | 适用人群 |
|------|------|----------|
| [CLAUDE.md](../../CLAUDE.md) | Claude开发指南，包含所有关键规则 | AI助手、开发者 |
| [架构设计](development/architecture.md) | 分层架构、模块职责、数据流向 | 所有开发者 |
| [贡献指南](development/contributing.md) | 开发环境、代码规范、测试规范 | 贡献者 |

### 开发指南

#### 快速开始
- [环境搭建](development/getting-started.md) - 开发环境配置
- [项目结构](development/project-structure.md) - 目录结构说明

#### 后端开发
- [API开发指南](development/api-development.md) - API开发规范
- [数据库操作](development/database-operations.md) - 数据库访问
- [HQL生成器](development/hql-generator.md) - HQL生成原理

#### 前端开发
- [React开发指南](development/react-development.md) - 组件开发
- [Canvas系统](development/canvas-system.md) - Canvas系统设计
- [状态管理](development/state-management.md) - 状态管理最佳实践

#### 测试
- [测试指南](development/testing-guide.md) - 测试规范
- [TDD实践](development/tdd-practices.md) - 测试驱动开发
- [E2E测试](development/e2e-testing.md) - 端到端测试

### 架构文档

#### 设计文档
- [系统架构](development/architecture.md) ⭐ - 分层架构设计
- [数据库设计](development/database-design.md) - 数据库Schema
- [API设计](development/api-design.md) - RESTful API设计

#### 架构决策
- [架构决策记录](../adr/README.md) - 重要技术决策
- [技术选型](development/technology-choices.md) - 技术栈说明

### API文档

- [API参考](../api/README.md) - 完整API文档
- [游戏管理API](../api/games.md) - 游戏相关接口
- [事件管理API](../api/events.md) - 事件相关接口
- [参数管理API](../api/parameters.md) - 参数相关接口
- [Canvas API](../api/canvas.md) - Canvas系统接口
- [HQL生成API](../api/hql.md) - HQL生成接口

### 项目文档

#### 产品文档
- [产品需求文档(PRD)](../requirements/PRD.md) - 功能需求和变更记录
- [用户手册](../user-guide/README.md) - 用户使用指南
- [部署指南](development/deployment.md) - 生产环境部署

#### 技术文档
- [性能优化](development/performance-optimization.md) - 性能优化指南
- [安全指南](development/security-guide.md) - 安全最佳实践
- [监控和日志](development/monitoring.md) - 监控和日志管理

---

## 文档分类

### 按角色分类

**AI助手（Claude）**
- [CLAUDE.md](../../CLAUDE.md) ⭐ - 必读
- [架构设计](development/architecture.md)
- [贡献指南](development/contributing.md)

**后端开发者**
- [快速开始](development/getting-started.md)
- [架构设计](development/architecture.md)
- [API开发指南](development/api-development.md)
- [数据库操作](development/database-operations.md)
- [HQL生成器](development/hql-generator.md)
- [测试指南](development/testing-guide.md)

**前端开发者**
- [快速开始](development/getting-started.md)
- [React开发指南](development/react-development.md)
- [Canvas系统](development/canvas-system.md)
- [状态管理](development/state-management.md)
- [API文档](../api/README.md)
- [E2E测试](development/e2e-testing.md)

**新贡献者**
- [贡献指南](development/contributing.md) ⭐ - 必读
- [快速开始](development/getting-started.md)
- [代码规范](development/contributing.md#代码规范)
- [测试规范](development/contributing.md#测试规范)
- [提交规范](development/contributing.md#提交规范)

### 按主题分类

**架构设计**
- [系统架构](development/architecture.md) ⭐
- [数据库设计](development/database-design.md)
- [API设计](development/api-design.md)
- [Canvas系统](development/canvas-system.md)
- [HQL生成器](development/hql-generator.md)

**开发指南**
- [环境搭建](development/getting-started.md)
- [代码规范](development/contributing.md#代码规范)
- [API开发](development/api-development.md)
- [React开发](development/react-development.md)
- [测试实践](development/testing-guide.md)

**最佳实践**
- [TDD实践](development/tdd-practices.md)
- [性能优化](development/performance-optimization.md)
- [安全指南](development/security-guide.md)
- [错误处理](development/error-handling.md)
- [日志记录](development/logging.md)

---

## 文档维护

### 文档规范

**创建新文档**：
1. 使用清晰的文件名（英文小写+连字符）
2. 添加文档头部元数据
3. 包含目录（TOC）
4. 添加代码示例
5. 更新本文档索引

**更新现有文档**：
1. 修改版本号
2. 更新最后修改日期
3. 在变更日志中记录

**文档模板**：

```markdown
# 文档标题

> **版本**: 1.0 | **最后更新**: 2026-02-10
>
> 简短描述文档内容。

---

## 目录

- [章节1](#章节1)
- [章节2](#章节2)

---

## 章节1

内容...

---

## 章节2

内容...

---

**文档版本**: 1.0
**最后更新**: 2026-02-10
**维护者**: Event2Table Development Team
```

### 文档审查

**审查清单**：
- [ ] 内容准确无误
- [ ] 代码示例可运行
- [ ] 链接有效
- [ ] 格式统一
- [ ] 术语一致

---

## 快速查找

### 常见问题

**Q: 如何快速上手开发？**
A: 阅读 [贡献指南](development/contributing.md) 和 [快速开始](development/getting-started.md)

**Q: 项目架构是怎样的？**
A: 阅读 [架构设计](development/architecture.md)

**Q: 如何编写测试？**
A: 阅读 [测试指南](development/testing-guide.md) 和 [TDD实践](development/tdd-practices.md)

**Q: API接口如何调用？**
A: 查看 [API文档](../api/README.md)

**Q: Canvas系统如何使用？**
A: 阅读 [Canvas系统](development/canvas-system.md)

**Q: HQL如何生成？**
A: 阅读 [HQL生成器](development/hql-generator.md)

### 关键概念

| 概念 | 文档链接 |
|------|----------|
| **分层架构** | [架构设计](development/architecture.md#分层架构说明) |
| **Schema层** | [架构设计](development/architecture.md#schema层数据验证层) |
| **Repository层** | [架构设计](development/architecture.md#repository层数据访问层) |
| **Service层** | [架构设计](development/architecture.md#service层业务逻辑层) |
| **API层** | [架构设计](development/architecture.md#api层http端点层) |
| **Canvas系统** | [Canvas系统](development/canvas-system.md) |
| **HQL生成器** | [HQL生成器](development/hql-generator.md) |
| **game_gid规范** | [CLAUDE.md](../../CLAUDE.md#游戏标识符规范-极其重要---强制执行) |
| **TDD开发** | [测试指南](development/testing-guide.md#tdd开发流程) |

---

## 获取帮助

**文档问题**：
- 发现文档错误？提交 Issue
- 文档不清晰？提交 Issue
- 想要贡献文档？查看 [贡献指南](development/contributing.md)

**技术问题**：
- 提交 GitHub Issue
- 参与 GitHub Discussions
- 查看代码注释

---

## 外部资源

**官方文档**：
- [Flask文档](https://flask.palletsprojects.com/)
- [React文档](https://react.dev/)
- [Pydantic文档](https://docs.pydantic.dev/)
- [Vite文档](https://vitejs.dev/)

**学习资源**：
- [Python最佳实践](https://docs.python-guide.org/)
- [React最佳实践](https://react.dev/learn)
- [测试驱动开发](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

---

**文档版本**: 1.0
**最后更新**: 2026-02-10
**维护者**: Event2Table Development Team
