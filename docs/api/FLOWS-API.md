# Flows/Canvas API

**流程管理和Canvas API**

**版本**: 8.0.0 (Phase 2-3)
**文件**: `backend/api/routes/flows.py`

---

## 概述

Flows API提供Canvas流程管理功能，支持流程创建、编辑、执行和预览。

**核心特性**:
- ✅ 流程CRUD操作
- ✅ 流程执行和HQL生成
- ✅ Canvas别名端点
- ✅ 批量操作支持

---

## 主要端点

### 流程管理

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/flows` | 列出流程（分页） |
| GET | `/api/flows/<flow_id>` | 获取流程详情 |
| POST | `/api/flows` | 创建流程 |
| PUT | `/api/flows/<flow_id>` | 更新流程 |
| DELETE | `/api/flows/<flow_id>` | 删除流程 |
| POST | `/api/flows/<flow_id>/load` | 加载流程数据 |
| POST | `/api/flows/generate` | 生成HQL |

### 批量操作

| 方法 | 端点 | 描述 |
|------|------|------|
| DELETE | `/api/flows/batch` | 批量删除流程 |
| PUT | `/api/flows/batch-update` | 批量更新流程 |

### Canvas别名端点

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/canvas/api/flows/save` | 保存流程 |
| GET | `/canvas/api/flows/<flowId>` | 获取流程 |
| POST | `/canvas/api/execute` | 执行流程 |
| GET | `/canvas/api/canvas/health` | 健康检查 |
| POST | `/canvas/api/preview-results` | 预览结果 |

---

## 核心端点详情

### POST /api/flows

创建新流程。

**请求体**:
```json
{
  "game_gid": 10000147,
  "flow_name": "登录流程",
  "category": "custom",
  "description": "用户登录数据分析流程",
  "flow_data": "{}"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Flow created successfully",
  "data": {
    "flow_id": 10
  }
}
```

---

### POST /api/flows/generate

生成流程HQL。

**请求体**:
```json
{
  "flow_id": 10,
  "options": {}
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Flow HQL generated successfully",
  "data": {
    "hql": "-- Generated HQL\n...",
    "stats": {...}
  }
}
```

---

## 相关文档

- [Events API](EVENTS-API.md) - 事件管理
- [Join Configs API](JOIN-CONFIGS-API.md) - JOIN配置
