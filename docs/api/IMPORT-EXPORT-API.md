# Import/Export API 文档

**版本**: 9.0.0
**最后更新**: 2026-03-05
**架构**: ERS (Entity-Repository-Service)

---

## 概述

Import/Export API提供事件导入、HQL导出、批量操作等功能，用于数据的批量导入导出和管理。

### 特性

- **Excel导入**: 从Excel文件导入事件和参数配置
- **数据验证**: 导入前验证数据格式和完整性
- **HQL导出**: 导出单个或批量事件的HQL语句
- **批量导出**: 批量导出多个事件的HQL
- **进度跟踪**: 导入导出进度实时反馈

---

## 端点列表

### Import Events

**POST /api/import/events**

从Excel文件导入事件和参数配置。

**Content-Type**: `multipart/form-data`

**请求参数**:
- `file` (file, required): Excel文件（.xlsx格式）
- `game_gid` (int, required): 游戏GID
- `overwrite` (bool, optional): 是否覆盖已存在的事件，默认false
- `dry_run` (bool, optional): 验证模式，不实际导入，默认false

**请求示例**:
```bash
curl -X POST "http://127.0.0.1:5001/api/import/events" \
  -F "file=@events.xlsx" \
  -F "game_gid=10000147" \
  -F "overwrite=false" \
  -F "dry_run=false"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "imported": 10,
    "updated": 5,
    "skipped": 2,
    "failed": 0,
    "details": [
      {
        "event_name": "login",
        "status": "imported",
        "event_id": 1
      },
      {
        "event_name": "logout",
        "status": "updated",
        "event_id": 2
      }
    ],
    "warnings": [
      "Event 'test_event' already exists, skipped"
    ]
  },
  "message": "Import completed: 10 imported, 5 updated, 2 skipped"
}
```

**错误码**:
- 400: 文件格式错误或参数验证失败
- 404: 游戏不存在
- 500: 导入失败

**Excel文件格式要求**:

| 列名 | 类型 | 必填 | 说明 |
|------|------|------|------|
| event_name | string | ✅ | 事件名称 |
| table_name | string | ✅ | 表名 |
| category | string | ❌ | 分类名称 |
| param_name | string | ❌ | 参数名称 |
| param_type | string | ❌ | 参数类型（base/param） |
| json_path | string | ❌ | JSON路径 |
| is_active | boolean | ❌ | 是否激活，默认true |

**Excel示例**:
```
event_name | table_name                          | category  | param_name | param_type | json_path
login      | dwd.v_dwd_10000147_login_di         | 登录/认证 | role_id    | base       |
login      | dwd.v_dwd_10000147_login_di         | 登录/认证 | zone_id    | param      | $.zoneId
logout     | dwd.v_dwd_10000147_logout_di        | 登录/认证 | role_id    | base       |
```

---

### Validate Import Data

**POST /api/import/validate**

验证导入数据但不实际导入（dry-run模式）。

**Content-Type**: `multipart/form-data`

**请求参数**:
- `file` (file, required): Excel文件（.xlsx格式）
- `game_gid` (int, required): 游戏GID

**请求示例**:
```bash
curl -X POST "http://127.0.0.1:5001/api/import/validate" \
  -F "file=@events.xlsx" \
  -F "game_gid=10000147"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "total_rows": 15,
    "valid_rows": 13,
    "invalid_rows": 2,
    "errors": [
      {
        "row": 5,
        "error": "Missing required field: event_name"
      },
      {
        "row": 10,
        "error": "Invalid param_type: invalid_type"
      }
    ],
    "warnings": [
      "Row 3: Event 'login' already exists, will be updated"
    ]
  },
  "message": "Validation completed: 13 valid rows, 2 invalid rows"
}
```

**错误码**:
- 400: 文件格式错误
- 500: 验证失败

---

### Export HQL (Single Event)

**GET /api/export/hql/<event_id>**

导出单个事件的HQL语句。

**路径参数**:
- `event_id` (int, required): 事件ID

**查询参数**:
- `bizdate` (string, optional): 业务日期，格式YYYYMMDD，默认当前日期
- `include_drop` (bool, optional): 是否包含DROP TABLE语句，默认true
- `mode` (string, optional): HQL生成模式，可选值: `single`, `join`, `union`，默认`single`

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5001/api/export/hql/1?bizdate=20260305&include_drop=true" \
  -o login_event.sql
```

**响应示例** (Content-Type: text/plain):
```sql
-- Auto-generated HQL for event: login
-- Generated at: 2026-03-05 12:00:00
-- Game: STAR001 (GID: 10000147)

DROP TABLE IF EXISTS dwd.v_dwd_10000147_login_di;

CREATE TABLE IF NOT EXISTS dwd.v_dwd_10000147_login_di AS
SELECT
  ds,
  role_id,
  account_id,
  utdid,
  get_json_object(params, '$.zoneId') AS zone_id,
  get_json_object(params, '$.level') AS level,
  envinfo,
  tm,
  ts
FROM ieu_ods.ods_10000147_all_view
WHERE ds = '${bizdate}'
  AND event_name = 'login'
  AND get_json_object(params, '$.zoneId') IS NOT NULL;
```

**错误码**:
- 404: 事件不存在
- 500: HQL生成失败

---

### Batch Export HQL

**POST /api/export/batch**

批量导出多个事件的HQL语句。

**请求体**:
```json
{
  "event_ids": [1, 2, 3, 5, 8],
  "bizdate": "20260305",
  "include_drop": true,
  "format": "single_file"
}
```

**参数说明**:
- `event_ids` (array[int], required): 事件ID列表
- `bizdate` (string, optional): 业务日期，格式YYYYMMDD，默认当前日期
- `include_drop` (bool, optional): 是否包含DROP TABLE语句，默认true
- `format` (string, optional): 导出格式，可选值:
  - `single_file`: 所有HQL合并到一个文件（默认）
  - `separate_files`: 每个事件一个文件（返回ZIP）

**请求示例**:
```bash
curl -X POST "http://127.0.0.1:5001/api/export/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "event_ids": [1, 2, 3, 5, 8],
    "bizdate": "20260305",
    "include_drop": true,
    "format": "single_file"
  }' \
  -o batch_export.sql
```

**响应示例 (single_file)**:
```json
{
  "success": true,
  "data": {
    "format": "single_file",
    "total_events": 5,
    "hql": "-- Batch HQL Export\n-- Generated at: 2026-03-05 12:00:00\n-- Total events: 5\n\n-- Event 1: login\nDROP TABLE IF EXISTS dwd.v_dwd_10000147_login_di;\nCREATE TABLE ...\n\n-- Event 2: logout\nDROP TABLE IF EXISTS dwd.v_dwd_10000147_logout_di;\nCREATE TABLE ...\n\n...",
    "file_name": "batch_export_20260305.sql"
  },
  "message": "Batch export completed: 5 events"
}
```

**响应示例 (separate_files)**:
```json
{
  "success": true,
  "data": {
    "format": "separate_files",
    "total_events": 5,
    "file_type": "zip",
    "file_name": "batch_export_20260305.zip",
    "files": [
      "login_event.sql",
      "logout_event.sql",
      "pay_event.sql",
      "level_up_event.sql",
      "item_use_event.sql"
    ]
  },
  "message": "Batch export completed: 5 files in ZIP archive"
}
```

**错误码**:
- 400: 参数验证失败
- 404: 一个或多个事件不存在
- 500: HQL生成失败

---

## 数据模型

### Import Result

```json
{
  "imported": 10,
  "updated": 5,
  "skipped": 2,
  "failed": 0,
  "details": [
    {
      "event_name": "login",
      "status": "imported|updated|skipped|failed",
      "event_id": 1,
      "error": "错误消息（仅失败时）"
    }
  ],
  "warnings": [
    "警告消息"
  ]
}
```

### Validation Result

```json
{
  "valid": true,
  "total_rows": 15,
  "valid_rows": 13,
  "invalid_rows": 2,
  "errors": [
    {
      "row": 5,
      "error": "错误描述"
    }
  ],
  "warnings": [
    "警告消息"
  ]
}
```

### Export Result

```json
{
  "format": "single_file|separate_files",
  "total_events": 5,
  "hql": "HQL语句（仅single_file格式）",
  "file_name": "文件名",
  "files": [
    "文件列表（仅separate_files格式）"
  ]
}
```

---

## 使用示例

### 导入事件配置

```javascript
// 1. 验证Excel文件
const validateImport = async (file, gameGid) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('game_gid', gameGid);

  const response = await fetch('/api/import/validate', {
    method: 'POST',
    body: formData
  });
  return response.json();
};

// 2. 导入事件
const importEvents = async (file, gameGid, overwrite = false) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('game_gid', gameGid);
  formData.append('overwrite', overwrite);

  const response = await fetch('/api/import/events', {
    method: 'POST',
    body: formData
  });
  return response.json();
};

// 使用示例
const fileInput = document.getElementById('excel-file');
const gameGid = 10000147;

fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];

  // 先验证
  const validation = await validateImport(file, gameGid);
  console.log('Validation result:', validation.data);

  if (validation.data.valid) {
    // 确认后导入
    const result = await importEvents(file, gameGid);
    console.log('Import result:', result.data);
    alert(`导入完成: ${result.data.imported}个新增, ${result.data.updated}个更新`);
  } else {
    alert(`验证失败: ${validation.data.invalid_rows}行有错误`);
  }
});
```

### 导出HQL

```javascript
// 导出单个事件HQL
const exportSingleHQL = async (eventId, bizdate) => {
  const response = await fetch(
    `/api/export/hql/${eventId}?bizdate=${bizdate}&include_drop=true`
  );

  if (response.ok) {
    const hql = await response.text();
    return hql;
  }
  throw new Error('Failed to export HQL');
};

// 批量导出HQL
const exportBatchHQL = async (eventIds, bizdate) => {
  const response = await fetch('/api/export/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_ids: eventIds,
      bizdate: bizdate,
      include_drop: true,
      format: 'single_file'
    })
  });

  const result = await response.json();
  return result.data.hql;
};

// 下载HQL文件
const downloadHQL = (hql, filename) => {
  const blob = new Blob([hql], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

// 使用示例
exportSingleHQL(1, '20260305').then(hql => {
  downloadHQL(hql, 'login_event.sql');
});

exportBatchHQL([1, 2, 3], '20260305').then(hql => {
  downloadHQL(hql, 'batch_export.sql');
});
```

---

## 错误处理

### 统一错误响应格式

```json
{
  "success": false,
  "error": "具体错误消息",
  "message": "用户友好的错误描述"
}
```

### 常见错误场景

**400 Bad Request - 文件格式错误**:
```json
{
  "success": false,
  "error": "Invalid file format: expected .xlsx",
  "message": "Please upload a valid Excel file (.xlsx format)."
}
```

**400 Bad Request - 数据验证失败**:
```json
{
  "success": false,
  "error": "Validation failed: 5 rows have errors",
  "message": "Please fix the errors in the Excel file and try again.",
  "data": {
    "errors": [
      {
        "row": 5,
        "error": "Missing required field: event_name"
      }
    ]
  }
}
```

**404 Not Found - 事件不存在**:
```json
{
  "success": false,
  "error": "Event 999 not found",
  "message": "Event 999 not found. Check the event_id or create the event first."
}
```

**500 Internal Server Error - 导入失败**:
```json
{
  "success": false,
  "error": "Failed to import events: database error",
  "message": "Import failed due to a server error. Please try again later."
}
```

---

## 性能优化

### 批量导入优化

**批量插入**:
- 使用批量插入而非逐条插入
- 事务处理确保数据一致性

**内存管理**:
- 流式读取大文件
- 分批处理（每1000行一批）

### 导出优化

**HQL缓存**:
- 缓存生成的HQL（TTL: 300秒）
- 避免重复生成相同配置的HQL

**文件压缩**:
- separate_files格式使用ZIP压缩
- 减少传输数据量

---

## 相关文档

- **[Events API文档](EVENTS-API.md)** - 事件管理API
- **[HQL生成器文档](../hql/)** - HQL生成器详细说明
- **[经验文档 - 数据导入最佳实践](../lessons-learned/data-import-best-practices.md)** - 数据导入经验

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-02-15 | Import/Export API初始版本 |
| 2.0.0 | 2026-02-20 | 添加批量导出功能 |
| 3.0.0 | 2026-03-01 | 添加数据验证功能 |
| 4.0.0 | 2026-03-05 | 性能优化和错误处理增强 |
