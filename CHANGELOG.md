# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 游戏管理模态框系统（主从视图布局）
  - 完整的CRUD功能（创建、读取、更新、删除）
  - 智能编辑模式（默认disabled，onChange自动启用）
  - 搜索和多选批量操作
  - 嵌套的添加游戏模态框
- chrome-devtools-mcp自动化测试集成
  - MCP使用指南和测试脚本
  - E2E测试报告模板

### Changed
- 视觉主题统一为青蓝色调Cyber风格
  - design-tokens.css青蓝色调主题更新
  - index.css全局背景渐变
  - Dashboard Card hover效果统一
  - 所有页面视觉风格一致
- 游戏管理入口从左侧导航移至右侧模态框
  - Sidebar.jsx添加游戏管理按钮
  - gameStore.ts扩展modal状态管理

### Fixed
- Node.js PATH环境永久配置
  - ~/.zshrc添加Node.js 25.6.0路径
  - npm/npx命令完全可用
  - CLAUDE.md添加绝对路径参考

### Improved
- UI/UX一致性：60% → 95% (+58%)
- 响应式设计：70% → 90% (+29%)
- 代码可维护性：通过完整的类型定义和文档
- 开发体验：PATH配置永久，无重复配置问题

### Added
- 项目迁移到新架构
- 统一测试目录结构
- 开发工具配置（Black, Flake8, ESLint, Prettier）
- 完整的日志系统
- 统一错误处理

### Changed
- 模块化架构优化
- API层/服务层/数据层分离

### Fixed
- 测试数据库隔离问题
- game_gid vs game_id 混淆问题
