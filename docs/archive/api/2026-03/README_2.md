# API 文档索引

**版本**: 9.0.0
**最后更新**: 2026-03-19
**架构**: ERS (Entity-Repository-Service)

---

## 概述

Event2Table 提供了一套完整的 RESTful API，支持游戏管理、事件配置、Canvas 流程、参数管理和 HQL 生成。

### 架构特点

- **Entity层**: 统一数据模型（Pydantic）
- **Repository层**: 数据访问封装
- **Service层**: 业务逻辑实现
- **API层**: HTTP 端点（REST + GraphQL）

---

## 核心 API 模块

### 游戏管理 API

**文档**: [GAMES-API.md](GAMES-API.md)

**端点**:
- `GET /api/games` - 列出游戏
- `GET /api/games/<gid>` - 获取游戏详情
- `POST /api/games` - 创建游戏
- `PUT /api/games/<gid>` - 更新游戏
- `DELETE /api/games/<gid>` - 删除游戏

**特性**:
- ✅ 游戏CRUD操作
- ✅ GID业务标识符
- ✅ ODS数据库配置
- ✅ 事件统计

---

### 事件管理 API

**文档**: [EVENTS-API.md](EVENTS-API.md)

**端点**:
- `GET /api/events` - 列出事件
- `GET /api/events/<id>` - 获取事件详情
- `POST /api/events` - 创建事件
- `PUT /api/events/<id>` - 更新事件
- `DELETE /api/events/<id>` - 删除事件

**特性**:
- ✅ 事件配置管理
- ✅ 表名自动生成
- ✅ 事件类型分类
- ✅ 参数字段管理

---

### 参数管理 API

**文档**: [PARAMETERS-API.md](PARAMETERS-API.md)

**端点**:
- `GET /api/parameters` - 列出参数
- `GET /api/parameters/all` - 获取所有参数（批量）
- `POST /api/parameters` - 创建参数
- `PUT /api/parameters/<id>` - 更新参数
- `DELETE /api/parameters/<id>` - 删除参数
- `POST /api/parameters/batch` - 批量操作

**特性**:
- ✅ 参数CRUD操作
- ✅ JSON路径解析
- ✅ 批量导入导出
- ✅ 参数使用统计

---

### Canvas 和流程 API

#### Event Nodes API

**文档**: [EVENT-NODES-API.md](EVENT-NODES-API.md)

**端点**:
- `GET /api/event-nodes` - 列出事件节点
- `GET /api/event-nodes/<id>` - 获取节点详情
- `POST /api/event-nodes` - 创建事件节点
- `PUT /api/event-nodes/<id>` - 更新事件节点
- `DELETE /api/event-nodes/<id>` - 删除事件节点

**特性**:
- ✅ 单事件节点配置
- ✅ WHERE条件构建
- ✅ 实时HQL预览
- ✅ 节点版本管理

#### Flows/Canvas API

**文档**: [FLOWS-API.md](FLOWS-API.md)

**端点**:
- `GET /api/flows` - 列出流程
- `GET /api/flows/<flow_id>` - 获取流程详情
- `POST /api/flows` - 创建流程
- `PUT /api/flows/<flow_id>` - 更新流程
- `DELETE /api/flows/<flow_id>` - 删除流程
- `POST /api/flows/generate` - 生成HQL

**Canvas别名端点**:
- `POST /canvas/api/flows/save` - 保存流程
- `GET /canvas/api/flows/<flowId>` - 获取流程
- `POST /canvas/api/execute` - 执行流程
- `GET /canvas/api/canvas/health` - 健康检查
- `POST /canvas/api/preview-results` - 预览结果

**特性**:
- ✅ 可视化流程配置
- ✅ 多节点组合
- ✅ Single/Join/Union模式
- ✅ 批量操作支持

#### Join Configs API

**文档**: [JOIN-CONFIGS-API.md](JOIN-CONFIGS-API.md)

**端点**:
- `GET /api/join-configs` - 列出JOIN配置
- `GET /api/join-configs/<id>` - 获取配置详情
- `POST /api/join-configs` - 创建JOIN配置
- `PUT /api/join-configs/<id>` - 更新JOIN配置
- `DELETE /api/join-configs/<id>` - 删除JOIN配置

**特性**:
- ✅ 多事件JOIN配置
- ✅ union_all、join、where_in类型
- ✅ JSON字段自动解析
- ✅ 输出字段管理

---

## GraphQL API

**端点**: `POST /api/graphql`

**文档**: [GraphQL Development Guide](../development/graphql-development-guide.md)

**特性**:
- ✅ 统一查询接口
- ✅ 类型安全
- ✅ 实时订阅（未来）
- ✅ 代码生成（GraphQL Code Generator）

---

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "data": {
    // 响应数据
  },
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

---

## HTTP 状态码

| 状态码 | 说明 | 示例场景 |
|--------|------|----------|
| 200 | OK | 成功获取资源 |
| 201 | Created | 成功创建资源 |
| 400 | Bad Request | 缺少必填参数、参数格式错误 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如GID已存在） |
| 500 | Internal Server Error | 服务器错误 |

---

## 认证和授权

> **注意**: 当前版本未实现认证系统。所有端点都是公开的。

**计划中的功能**:
- ✅ API Key认证
- ✅ JWT Token认证
- ✅ OAuth 2.0集成
- ✅ 权限管理（RBAC）

---

## 速率限制

> **注意**: 当前版本未实现速率限制。

**计划中的功能**:
- ✅ 每IP速率限制
- ✅ 每用户速率限制
- ✅ 分层速率限制（免费/付费）

---

## 错误处理

### 常见错误

#### 400 Bad Request

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "缺少必填参数: game_gid",
    "details": {
      "field": "game_gid",
      "constraint": "required"
    }
  }
}
```

#### 409 Conflict

```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_GID",
    "message": "游戏GID已存在: 10000147",
    "details": {
      "gid": 10000147,
      "existing_game_id": 1
    }
  }
}
```

#### 500 Internal Server Error

```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "服务器内部错误，请稍后重试",
    "details": {
      "request_id": "req_123456"
    }
  }
}
```

---

## 开发指南

### API 契约测试

确保前后端API一致性：

```bash
# 运行API契约测试
python scripts/test/api_contract_test.py

# 自动修复API契约问题
python scripts/test/api_contract_test.py --fix
```

**详见**: [API Contract Test Guide](../development/API-CONTRACT-TEST-GUIDE.md)

### 安全规范

**输入验证**:
- ✅ 使用Pydantic Schema验证
- ✅ SQL注入防护（参数化查询）
- ✅ XSS防护（HTML转义）
- ✅ SQLValidator验证动态标识符

**详见**: [SQL Validator Guidelines](../development/sql-validator-guidelines.md)

### game_gid vs game_id

**重要**: 所有数据关联必须使用 `game_gid`（业务GID），而非 `game_id`（数据库自增ID）。

**详见**: [GAME_GID Migration Guide](../development/GAME_GID_MIGRATION_GUIDE.md)

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 9.0.0 | 2026-03-05 | ERS架构迁移完成，GraphQL类型同步 |
| 8.0.0 | 2026-02-26 | Canvas API重构，Join Configs API新增 |
| 7.0.0 | 2026-02-18 | Event Nodes API新增 |
| 6.0.0 | 2026-02-10 | Parameters API批量操作 |

---

## 相关文档

- [开发指南](../development/)
- [API开发规范](../development/api-development.md)
- [GraphQL开发指南](../development/graphql-development-guide.md)
- [安全规范](../development/sql-validator-guidelines.md)

---

## 贡献指南

修改API时：
1. ✅ 更新对应的API文档
2. ✅ 运行API契约测试
3. ✅ 更新本索引文档
4. ✅ 提交Pull Request

---

**维护者**: Event2Table Development Team
**最后更新**: 2026-03-19
