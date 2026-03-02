# Join Configs API

**JOIN配置管理API**

**版本**: 8.0.0 (Phase 3)
**文件**: `backend/api/routes/join_configs.py`

---

## 概述

Join Configs API提供多事件JOIN配置管理功能。

**核心特性**:
- ✅ JOIN配置CRUD
- ✅ 支持union_all、join、where_in类型
- ✅ JSON字段自动解析

---

## 端点列表

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/join-configs` | 列出JOIN配置 |
| GET | `/api/join-configs/<id>` | 获取配置 |
| POST | `/api/join-configs` | 创建配置 |
| PUT/PATCH | `/api/join-configs/<id>` | 更新配置 |
| DELETE | `/api/join-configs/<id>` | 删除配置 |

---

## 核心端点

### POST /api/join-configs

创建JOIN配置。

**请求体**:
```json
{
  "name": "config_name",
  "display_name": "Display Name",
  "source_events": [1, 2, 3],
  "join_config": {},
  "output_fields": [],
  "output_table": "dwd_output_view",
  "join_type": "union_all",
  "game_gid": 10000147
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Join configuration created successfully",
  "data": {
    "config_id": 10
  }
}
```

---

## 相关文档

- [Events API](EVENTS-API.md) - 事件管理
- [Flows API](FLOWS-API.md) - 流程管理
