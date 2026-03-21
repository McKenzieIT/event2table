# 异步任务 API 文档

## 概述

异步任务API允许客户端提交耗时操作（如HQL生成、数据导入导出等）到后台处理，避免长时间阻塞HTTP请求。

## 基础信息

- **API版本**: v2.1.0
- **基础路径**: `/api/async-tasks`
- **认证方式**: 可选

## 任务类型

| 任务类型 | 描述 | 预计耗时 |
|---------|------|---------|
| `hql_generation` | HQL生成 | 1-10秒 |
| `data_import` | 数据导入 | 10-60秒 |
| `data_export` | 数据导出 | 10-60秒 |
| `batch_operation` | 批量操作 | 5-30秒 |
| `cache_warmup` | 缓存预热 | 30-120秒 |

## 任务状态

| 状态 | 描述 |
|------|------|
| `pending` | 任务已提交，等待处理 |
| `running` | 任务正在执行 |
| `completed` | 任务完成 |
| `failed` | 任务失败 |
| `cancelled` | 任务已取消 |

## API端点

### 1. 提交异步任务

提交一个新的异步任务。

**端点**: `POST /api/async-tasks`

**请求参数**:

```json
{
  "task_type": "hql_generation",
  "params": {
    "event_id": 123,
    "mode": "join",
    "parameters": {
      "start_time": "2026-01-01",
      "end_time": "2026-01-31"
    }
  },
  "callback_url": "https://example.com/callback",
  "priority": "normal"
}
```

**参数说明**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `task_type` | string | 是 | 任务类型（见任务类型表） |
| `params` | object | 是 | 任务参数，根据任务类型不同而不同 |
| `callback_url` | string | 否 | 任务完成后的回调URL |
| `priority` | string | 否 | 优先级（low/normal/high），默认normal |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "pending",
    "task_type": "hql_generation",
    "created_at": "2026-03-20T01:00:00Z",
    "estimated_duration": 5000
  }
}
```

**错误响应**:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_TASK_TYPE",
    "message": "不支持的任务类型"
  }
}
```

---

### 2. 查询任务状态

查询指定任务的执行状态。

**端点**: `GET /api/async-tasks/<task_id>`

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `task_id` | string | 是 | 任务ID |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "running",
    "progress": 45,
    "task_type": "hql_generation",
    "created_at": "2026-03-20T01:00:00Z",
    "updated_at": "2026-03-20T01:00:02Z",
    "started_at": "2026-03-20T01:00:01Z",
    "estimated_remaining": 3000,
    "worker_id": "worker_001"
  }
}
```

**状态说明**:

- `progress`: 进度百分比（0-100）
- `estimated_remaining`: 预计剩余时间（毫秒）
- `worker_id`: 处理任务的worker ID

---

### 3. 获取任务结果

获取已完成任务的结果。

**端点**: `GET /api/async-tasks/<task_id>/result`

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `task_id` | string | 是 | 任务ID |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "completed",
    "result": {
      "hql": "SELECT\n  event_id,\n  COUNT(*) as event_count\nFROM ods_game_events\nWHERE dt >= '2026-01-01'\n  AND dt <= '2026-01-31'\nGROUP BY event_id",
      "execution_time": 5234,
      "row_count": 1234
    },
    "completed_at": "2026-03-20T01:00:05Z"
  }
}
```

**错误响应**（任务未完成）:

```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_COMPLETED",
    "message": "任务尚未完成，无法获取结果"
  }
}
```

---

### 4. 获取任务列表

获取所有任务或特定任务的列表。

**端点**: `GET /api/async-tasks`

**查询参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `status` | string | 否 | 按状态过滤（pending/running/completed/failed/cancelled） |
| `task_type` | string | 否 | 按任务类型过滤 |
| `page` | integer | 否 | 页码（默认1） |
| `page_size` | integer | 否 | 每页数量（默认20，最大100） |
| `sort_by` | string | 否 | 排序字段（created_at/updated_at） |
| `order` | string | 否 | 排序方向（asc/desc） |

**请求示例**:

```
GET /api/async-tasks?status=completed&task_type=hql_generation&page=1&page_size=20
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "task_id": "task_abc123def456",
        "status": "completed",
        "task_type": "hql_generation",
        "created_at": "2026-03-20T01:00:00Z",
        "completed_at": "2026-03-20T01:00:05Z",
        "execution_time": 5234
      },
      {
        "task_id": "task_xyz789uvw012",
        "status": "completed",
        "task_type": "hql_generation",
        "created_at": "2026-03-19T23:00:00Z",
        "completed_at": "2026-03-19T23:00:03Z",
        "execution_time": 3120
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

---

### 5. 取消任务

取消一个待处理或正在运行的任务。

**端点**: `DELETE /api/async-tasks/<task_id>`

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `task_id` | string | 是 | 任务ID |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "cancelled",
    "cancelled_at": "2026-03-20T01:00:03Z"
  }
}
```

**错误响应**（任务已完成）:

```json
{
  "success": false,
  "error": {
    "code": "TASK_CANNOT_BE_CANCELLED",
    "message": "任务已完成，无法取消"
  }
}
```

---

### 6. 删除任务

删除已完成的任务记录。

**端点**: `DELETE /api/async-tasks/<task_id>/cleanup`

**路径参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `task_id` | string | 是 | 任务ID |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "message": "任务记录已删除"
  }
}
```

---

## 任务类型详细说明

### HQL生成任务

**任务类型**: `hql_generation`

**参数**:

```json
{
  "event_id": 123,
  "mode": "join",
  "parameters": {
    "start_time": "2026-01-01",
    "end_time": "2026-01-31",
    "filters": {...}
  }
}
```

**结果**:

```json
{
  "hql": "SELECT ...",
  "execution_time": 5234,
  "row_count": 1234
}
```

---

### 数据导入任务

**任务类型**: `data_import`

**参数**:

```json
{
  "source": "file",
  "file_path": "/path/to/file.csv",
  "game_gid": 100001,
  "format": "csv",
  "options": {
    "skip_duplicates": true,
    "update_existing": false
  }
}
```

**结果**:

```json
{
  "imported_count": 100,
  "skipped_count": 5,
  "error_count": 0,
  "errors": []
}
```

---

### 数据导出任务

**任务类型**: `data_export`

**参数**:

```json
{
  "event_ids": [1, 2, 3],
  "format": "json",
  "include_parameters": true
}
```

**结果**:

```json
{
  "file_path": "/exports/export_20260320.json",
  "file_size": 1024000,
  "record_count": 100
}
```

---

### 批量操作任务

**任务类型**: `batch_operation`

**参数**:

```json
{
  "operation": "delete",
  "target_type": "events",
  "target_ids": [1, 2, 3, 4, 5]
}
```

**结果**:

```json
{
  "success_count": 5,
  "failed_count": 0,
  "errors": []
}
```

---

### 缓存预热任务

**任务类型**: `cache_warmup`

**参数**:

```json
{
  "cache_type": "games",
  "limit": 100
}
```

**结果**:

```json
{
  "warmed_count": 100,
  "execution_time": 45000
}
```

---

## 回调机制

任务完成后，系统会向指定的`callback_url`发送POST请求。

**回调请求格式**:

```json
{
  "task_id": "task_abc123def456",
  "status": "completed",
  "result": {...},
  "completed_at": "2026-03-20T01:00:05Z"
}
```

**回调响应**:

服务端应返回 `200 OK` 确认收到回调。

---

## 错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| `TASK_NOT_FOUND` | 404 | 任务不存在 |
| `INVALID_TASK_TYPE` | 400 | 不支持的任务类型 |
| `INVALID_PARAMS` | 400 | 任务参数无效 |
| `TASK_NOT_COMPLETED` | 400 | 任务尚未完成 |
| `TASK_CANNOT_BE_CANCELLED` | 400 | 任务无法取消 |
| `TASK_EXECUTION_FAILED` | 500 | 任务执行失败 |
| `WORKER_UNAVAILABLE` | 503 | Worker不可用 |

---

## 性能指标

- **任务提交延迟**: < 100ms
- **状态查询延迟**: < 50ms
- **结果获取延迟**: < 100ms
- **任务队列容量**: 1000个并发任务
- **任务保留时间**: 7天

---

## 最佳实践

1. **合理使用优先级**: 重要任务使用高优先级
2. **设置回调**: 避免轮询，使用回调机制
3. **定期清理**: 及时删除已完成的任务记录
4. **错误处理**: 妥善处理任务失败情况
5. **超时设置**: 客户端应设置合理的超时时间

---

## 示例代码

### Python

```python
import requests
import time

# 提交任务
response = requests.post('http://localhost:5000/api/async-tasks', json={
    'task_type': 'hql_generation',
    'params': {
        'event_id': 123,
        'mode': 'join'
    }
})
task_id = response.json()['data']['task_id']

# 轮询状态
while True:
    response = requests.get(f'http://localhost:5000/api/async-tasks/{task_id}')
    status = response.json()['data']['status']
    
    if status == 'completed':
        # 获取结果
        result_response = requests.get(f'http://localhost:5000/api/async-tasks/{task_id}/result')
        result = result_response.json()['data']['result']
        print(f"任务完成: {result}")
        break
    elif status == 'failed':
        print("任务失败")
        break
    
    time.sleep(1)
```

### JavaScript

```javascript
// 提交任务
const response = await fetch('/api/async-tasks', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    task_type: 'hql_generation',
    params: { event_id: 123, mode: 'join' }
  })
});
const { task_id } = (await response.json()).data;

// 轮询状态
const pollStatus = async () => {
  const response = await fetch(`/api/async-tasks/${task_id}`);
  const { status } = (await response.json()).data;
  
  if (status === 'completed') {
    const resultResponse = await fetch(`/api/async-tasks/${task_id}/result`);
    const result = (await resultResponse.json()).data.result;
    console.log('任务完成:', result);
  } else if (status === 'failed') {
    console.log('任务失败');
  } else {
    setTimeout(pollStatus, 1000);
  }
};

pollStatus();
```

---

## 相关文档

- [用户手册: 异步任务](../user-guide/async-tasks.md)
- [架构文档: 异步任务模块](../development/architecture.md#异步任务模块)
- [API总览](./README.md)
