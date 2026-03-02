# Field Builder API

**字段构建器API**

**版本**: 8.0.0 (Phase 5新增)
**文件**: `backend/api/routes/field_builder.py`
**架构**: FieldBuilderService → JoinConfigRepository → FieldBuilderConfigEntity

---

## 概述

字段构建器API提供字段配置管理、HQL预览和视图配置功能。

**核心特性**:
- ✅ 字段配置管理
- ✅ HQL预览生成
- ✅ 基础字段管理
- ✅ 自定义字段管理
- ✅ 配置版本控制

**架构变更**:
- Phase 5: 全新API模块

---

## 端点列表

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/field-builder/configs` | 列出配置 |
| GET | `/api/field-builder/configs/<id>` | 获取配置 |
| POST | `/api/field-builder/configs` | 创建配置 |
| PUT/PATCH | `/api/field-builder/configs/<id>` | 更新配置 |
| DELETE | `/api/field-builder/configs/<id>` | 删除配置 |
| POST | `/api/field-builder/preview` | 预览HQL |

---

## 端点详情

### GET /api/field-builder/configs

列出字段构建器配置。

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| limit | int | ❌ | 50 | 返回数量限制 |
| search | string | ❌ | - | 搜索关键词 |

**请求示例**:
```bash
GET /api/field-builder/configs?limit=100&search=login
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "view_name": "v_dwd_login_view",
      "display_name": "登录视图",
      "config": {
        "view_config": {...},
        "base_fields": [...],
        "custom_fields": {...}
      },
      "created_at": "2026-03-01T10:00:00",
      "updated_at": "2026-03-01T10:00:00"
    }
  ]
}
```

**Service层**: `FieldBuilderService.list_configs(limit, search)`

---

### GET /api/field-builder/configs/<id>

获取单个配置。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 配置ID |

**请求示例**:
```bash
GET /api/field-builder/configs/1
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "view_name": "v_dwd_login_view",
    "display_name": "登录视图",
    "config": {
      "view_config": {
        "source_events": [1, 2],
        "output_table": "dwd.v_dwd_login_view"
      },
      "base_fields": [
        "ds",
        "role_id",
        "account_id",
        "utdid",
        "envinfo",
        "tm",
        "ts"
      ],
      "custom_fields": {
        "zone_id": {
          "type": "param",
          "json_path": "$.zoneId",
          "event_id": 1
        }
      }
    },
    "created_at": "2026-03-01T10:00:00",
    "updated_at": "2026-03-01T10:00:00"
  }
}
```

**Service层**: `FieldBuilderService.get_config_by_id(id)`

---

### POST /api/field-builder/configs

创建新配置。

**请求体**:
```json
{
  "config": {
    "view_config": {...},
    "base_fields": [...],
    "custom_fields": {...}
  },
  "view_name": "v_dwd_custom_view",
  "display_name": "自定义视图",
  "id": 1
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| config | object | ✅ | 配置对象 |
| config.view_config | object | ✅ | 视图配置 |
| config.base_fields | array | ✅ | 基础字段列表 |
| config.custom_fields | object | ❌ | 自定义字段映射 |
| view_name | string | ✅ | 视图名称 |
| display_name | string | ✅ | 显示名称 |
| id | int | ❌ | 配置ID（更新时提供） |

**请求示例**:
```bash
POST /api/field-builder/configs
Content-Type: application/json

{
  "config": {
    "view_config": {
      "source_events": [1, 2],
      "output_table": "dwd.v_dwd_login_view"
    },
    "base_fields": [
      "ds",
      "role_id",
      "account_id",
      "utdid",
      "envinfo",
      "tm",
      "ts"
    ],
    "custom_fields": {
      "zone_id": {
        "type": "param",
        "json_path": "$.zoneId",
        "event_id": 1
      }
    }
  },
  "view_name": "v_dwd_login_view",
  "display_name": "登录视图"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Field builder configuration saved successfully",
  "data": {
    "id": 2,
    "view_name": "v_dwd_login_view",
    "display_name": "登录视图",
    "created_at": "2026-03-01T10:30:00"
  }
}
```

**Service层**: `FieldBuilderService.save_config(config, view_name, display_name, config_id)`

---

### PUT/PATCH /api/field-builder/configs/<id>

更新配置。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 配置ID |

**请求体**: 同POST

**请求示例**:
```bash
PUT /api/field-builder/configs/1
Content-Type: application/json

{
  "config": {
    "view_config": {...},
    "base_fields": [...],
    "custom_fields": {...}
  },
  "view_name": "v_dwd_login_view_v2",
  "display_name": "登录视图V2",
  "id": 1
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "Field builder configuration saved successfully",
  "data": {
    "id": 1,
    "view_name": "v_dwd_login_view_v2",
    "updated_at": "2026-03-01T11:00:00"
  }
}
```

**Service层**: `FieldBuilderService.save_config(config, view_name, display_name, config_id=1)`

---

### DELETE /api/field-builder/configs/<id>

删除配置。

**路径参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| id | int | 配置ID |

**请求示例**:
```bash
DELETE /api/field-builder/configs/1
```

**响应示例**:
```json
{
  "success": true,
  "message": "Configuration deleted successfully"
}
```

**错误响应**:
| 状态码 | 描述 |
|--------|------|
| 404 | 配置不存在 |

**Service层**: `FieldBuilderService.delete_config(id)`

---

### POST /api/field-builder/preview

预览HQL生成结果。

**请求体**:
```json
{
  "config": {
    "view_config": {...},
    "base_fields": [...],
    "custom_fields": {...}
  },
  "source_events": [1, 2, 3],
  "view_name": "v_dwd_preview",
  "date_var": "${bizdate}"
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| config | object | ✅ | - | 配置对象 |
| source_events | array | ❌ | [] | 源事件ID列表 |
| view_name | string | ❌ | "v_dwd_preview" | 视图名称 |
| date_var | string | ❌ | "${bizdate}" | 日期变量 |

**请求示例**:
```bash
POST /api/field-builder/preview
Content-Type: application/json

{
  "config": {
    "view_config": {
      "source_events": [1, 2],
      "output_table": "dwd.v_dwd_login_view"
    },
    "base_fields": [
      "ds",
      "role_id",
      "account_id"
    ],
    "custom_fields": {
      "zone_id": {
        "type": "param",
        "json_path": "$.zoneId",
        "event_id": 1
      }
    }
  },
  "source_events": [1, 2],
  "view_name": "v_dwd_preview",
  "date_var": "${bizdate}"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "hql": "-- Auto-generated HQL\nCREATE OR REPLACE VIEW dwd.v_dwd_preview AS\nSELECT\n  ds,\n  role_id,\n  account_id,\n  get_json_object(params, '$.zoneId') AS zone_id\nFROM ieu_ods.ods_10000147_all_view\nWHERE ds = '${bizdate}';"
  }
}
```

**Service层**: `FieldBuilderService.preview_hql(config, source_events, view_name, date_var)`

---

## 配置结构

### config对象

```javascript
{
  "view_config": {
    "source_events": [1, 2, 3],      // 源事件ID列表
    "output_table": "dwd.v_dwd_view"  // 输出表名
  },
  "base_fields": [                     // 基础字段列表
    "ds",
    "role_id",
    "account_id",
    "utdid",
    "envinfo",
    "tm",
    "ts"
  ],
  "custom_fields": {                   // 自定义字段映射
    "zone_id": {
      "type": "param",                 // 字段类型: param/base
      "json_path": "$.zoneId",        // JSON路径（type=param时）
      "event_id": 1                   // 源事件ID（type=param时）
    },
    "level": {
      "type": "base",                 // 基础字段类型
      "field_name": "level"           // 字段名称
    }
  }
}
```

---

## 使用场景

### 1. 创建字段配置

```javascript
const config = {
  view_config: {
    source_events: [1, 2],
    output_table: 'dwd.v_dwd_login_view'
  },
  base_fields: [
    'ds', 'role_id', 'account_id', 'utdid', 'envinfo', 'tm', 'ts'
  ],
  custom_fields: {
    zone_id: {
      type: 'param',
      json_path: '$.zoneId',
      event_id: 1
    }
  }
};

const result = await fetch('/api/field-builder/configs', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    config: config,
    view_name: 'v_dwd_login_view',
    display_name: '登录视图'
  })
}).then(r => r.json());

console.log(`Config created with ID: ${result.data.id}`);
```

### 2. 预览HQL

```javascript
const preview = await fetch('/api/field-builder/preview', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    config: config,
    source_events: [1, 2],
    view_name: 'v_dwd_preview',
    date_var: '${bizdate}'
  })
}).then(r => r.json());

console.log('Generated HQL:');
console.log(preview.data.hql);
```

---

## 相关文档

- [Events API](EVENTS-API.md) - 事件管理
- [Join Configs API](JOIN-CONFIGS-API.md) - JOIN配置
- [HQL生成器](../hql/README.md) - HQL生成详解
