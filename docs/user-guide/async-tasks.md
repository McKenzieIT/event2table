# 异步任务用户手册

## 概述

异步任务功能允许您在后台执行耗时操作（如HQL生成、数据导入导出等），无需等待操作完成即可继续其他工作。任务完成后，您可以随时查询结果。

## 适用场景

异步任务适用于以下场景：

- **HQL生成**: 复杂的HQL查询生成（预计1-10秒）
- **数据导入**: 大量数据导入（预计10-60秒）
- **数据导出**: 大量数据导出（预计10-60秒）
- **批量操作**: 批量删除或更新（预计5-30秒）
- **缓存预热**: 系统缓存预热（预计30-120秒）

## 快速开始

### 步骤1: 提交任务

通过API提交异步任务：

```bash
POST /api/async-tasks
Content-Type: application/json

{
  "task_type": "hql_generation",
  "params": {
    "event_id": 123,
    "mode": "join"
  }
}
```

响应示例：

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "pending",
    "created_at": "2026-03-20T01:00:00Z"
  }
}
```

保存返回的 `task_id`，用于后续查询。

### 步骤2: 查询任务状态

使用 `task_id` 查询任务状态：

```bash
GET /api/async-tasks/task_abc123def456
```

响应示例：

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "running",
    "progress": 45,
    "estimated_remaining": 3000
  }
}
```

### 步骤3: 获取任务结果

任务状态为 `completed` 时，获取结果：

```bash
GET /api/async-tasks/task_abc123def456/result
```

响应示例：

```json
{
  "success": true,
  "data": {
    "task_id": "task_abc123def456",
    "status": "completed",
    "result": {
      "hql": "SELECT ...",
      "execution_time": 5234
    }
  }
}
```

## 任务类型详解

### 1. HQL生成任务

生成HQL查询语句。

**参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `event_id` | integer | 是 | 事件ID |
| `mode` | string | 是 | 生成模式（join/union/single） |
| `parameters` | object | 否 | 参数配置 |

**示例**:

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

### 2. 数据导入任务

导入数据到系统。

**参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `source` | string | 是 | 数据源（file/url） |
| `file_path` | string | 是 | 文件路径或URL |
| `game_gid` | integer | 是 | 游戏GID |
| `format` | string | 是 | 文件格式（csv/json/excel） |
| `options` | object | 否 | 导入选项 |

**示例**:

```json
{
  "task_type": "data_import",
  "params": {
    "source": "file",
    "file_path": "/path/to/file.csv",
    "game_gid": 100001,
    "format": "csv",
    "options": {
      "skip_duplicates": true,
      "update_existing": false
    }
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

### 3. 数据导出任务

导出系统数据。

**参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `event_ids` | array | 是 | 事件ID列表 |
| `format` | string | 是 | 导出格式（json/csv/excel） |
| `include_parameters` | boolean | 否 | 是否包含参数 |

**示例**:

```json
{
  "task_type": "data_export",
  "params": {
    "event_ids": [1, 2, 3],
    "format": "json",
    "include_parameters": true
  }
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

### 4. 批量操作任务

批量执行操作。

**参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `operation` | string | 是 | 操作类型（delete/update） |
| `target_type` | string | 是 | 目标类型（events/parameters） |
| `target_ids` | array | 是 | 目标ID列表 |

**示例**:

```json
{
  "task_type": "batch_operation",
  "params": {
    "operation": "delete",
    "target_type": "events",
    "target_ids": [1, 2, 3, 4, 5]
  }
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

### 5. 缓存预热任务

预热系统缓存。

**参数**:

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `cache_type` | string | 是 | 缓存类型（games/events/parameters） |
| `limit` | integer | 否 | 预热数量（默认100） |

**示例**:

```json
{
  "task_type": "cache_warmup",
  "params": {
    "cache_type": "games",
    "limit": 100
  }
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

## 任务状态说明

| 状态 | 描述 | 可执行操作 |
|------|------|-----------|
| `pending` | 任务已提交，等待处理 | 查询状态、取消任务 |
| `running` | 任务正在执行 | 查询状态、取消任务 |
| `completed` | 任务完成 | 获取结果、删除记录 |
| `failed` | 任务失败 | 查询错误信息、删除记录 |
| `cancelled` | 任务已取消 | 查询取消信息、删除记录 |

## 高级功能

### 回调机制

设置 `callback_url` 参数，任务完成后系统会自动通知您。

**示例**:

```json
{
  "task_type": "hql_generation",
  "params": {...},
  "callback_url": "https://your-server.com/callback"
}
```

**回调请求**:

```json
{
  "task_id": "task_abc123def456",
  "status": "completed",
  "result": {...},
  "completed_at": "2026-03-20T01:00:05Z"
}
```

您的服务器应返回 `200 OK` 确认收到回调。

---

### 任务优先级

设置 `priority` 参数控制任务执行顺序。

**优先级选项**:

- `low`: 低优先级，空闲时执行
- `normal`: 正常优先级（默认）
- `high`: 高优先级，优先执行

**示例**:

```json
{
  "task_type": "hql_generation",
  "params": {...},
  "priority": "high"
}
```

---

### 任务列表查询

查询所有任务或特定条件的任务列表。

**示例**:

```
GET /api/async-tasks?status=completed&task_type=hql_generation&page=1&page_size=20
```

**参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| `status` | string | 按状态过滤 |
| `task_type` | string | 按任务类型过滤 |
| `page` | integer | 页码 |
| `page_size` | integer | 每页数量 |
| `sort_by` | string | 排序字段 |
| `order` | string | 排序方向（asc/desc） |

---

## 使用示例

### Python示例

```python
import requests
import time

# 配置
API_BASE = "http://localhost:5000/api"

def submit_hql_generation_task(event_id, mode):
    """提交HQL生成任务"""
    response = requests.post(f"{API_BASE}/async-tasks", json={
        "task_type": "hql_generation",
        "params": {
            "event_id": event_id,
            "mode": mode
        }
    })
    return response.json()['data']['task_id']

def wait_for_task_completion(task_id, timeout=300):
    """等待任务完成"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(f"{API_BASE}/async-tasks/{task_id}")
        data = response.json()['data']
        status = data['status']
        
        if status == 'completed':
            return get_task_result(task_id)
        elif status == 'failed':
            raise Exception(f"任务失败: {data.get('error')}")
        elif status in ['pending', 'running']:
            progress = data.get('progress', 0)
            print(f"任务进度: {progress}%")
            time.sleep(2)
        else:
            raise Exception(f"未知状态: {status}")
    
    raise TimeoutError("任务超时")

def get_task_result(task_id):
    """获取任务结果"""
    response = requests.get(f"{API_BASE}/async-tasks/{task_id}/result")
    return response.json()['data']['result']

# 使用示例
task_id = submit_hql_generation_task(123, 'join')
print(f"任务已提交: {task_id}")

result = wait_for_task_completion(task_id)
print(f"任务完成: {result}")
```

---

### JavaScript示例

```javascript
const API_BASE = '/api/async-tasks';

async function submitTask(taskType, params) {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_type: taskType, params })
  });
  const data = await response.json();
  return data.data.task_id;
}

async function pollTaskStatus(taskId) {
  const response = await fetch(`${API_BASE}/${taskId}`);
  const data = await response.json();
  return data.data;
}

async function getTaskResult(taskId) {
  const response = await fetch(`${API_BASE}/${taskId}/result`);
  const data = await response.json();
  return data.data.result;
}

async function waitForTask(taskId, timeout = 300000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const task = await pollTaskStatus(taskId);
    
    if (task.status === 'completed') {
      return await getTaskResult(taskId);
    } else if (task.status === 'failed') {
      throw new Error(`任务失败: ${task.error}`);
    } else if (task.status === 'running') {
      console.log(`任务进度: ${task.progress || 0}%`);
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  throw new Error('任务超时');
}

// 使用示例
(async () => {
  const taskId = await submitTask('hql_generation', {
    event_id: 123,
    mode: 'join'
  });
  
  console.log(`任务已提交: ${taskId}`);
  
  const result = await waitForTask(taskId);
  console.log('任务完成:', result);
})();
```

---

## 常见问题

### Q1: 如何知道任务是否完成？

**A**: 有两种方式：

1. **轮询查询**: 定期调用 `GET /api/async-tasks/<task_id>` 查询状态
2. **回调通知**: 提交任务时设置 `callback_url`，系统会自动通知

推荐使用回调机制，减少不必要的轮询。

---

### Q2: 任务执行时间过长怎么办？

**A**: 

1. 检查任务状态是否为 `running`
2. 查看任务的 `progress` 字段确认进度
3. 如果长时间无响应，可以取消任务：`DELETE /api/async-tasks/<task_id>`
4. 联系管理员检查系统状态

---

### Q3: 任务失败后如何重试？

**A**: 

1. 查询任务失败原因：`GET /api/async-tasks/<task_id>`
2. 根据错误信息修正参数
3. 重新提交任务

---

### Q4: 如何取消正在运行的任务？

**A**: 调用取消接口：

```bash
DELETE /api/async-tasks/<task_id>
```

注意：已完成的任务无法取消。

---

### Q5: 任务结果保留多久？

**A**: 任务结果保留 **7天**。建议及时获取并保存结果。

---

### Q6: 可以同时提交多个任务吗？

**A**: 可以。系统支持最多 **1000个** 并发任务。

---

### Q7: 如何查看历史任务？

**A**: 使用任务列表接口：

```bash
GET /api/async-tasks?page=1&page_size=20
```

可以按状态、任务类型等条件过滤。

---

### Q8: 回调URL有什么要求？

**A**: 

1. 必须是可访问的HTTP(S) URL
2. 必须支持POST请求
3. 应返回 `200 OK` 确认收到回调
4. 建议使用HTTPS确保安全

---

### Q9: 任务优先级如何影响执行顺序？

**A**: 

- `high` 优先级任务会优先执行
- `normal` 优先级任务按提交顺序执行
- `low` 优先级任务在系统空闲时执行

---

### Q10: 如何删除已完成的任务记录？

**A**: 调用清理接口：

```bash
DELETE /api/async-tasks/<task_id>/cleanup
```

建议定期清理已完成的任务记录，释放存储空间。

---

## 最佳实践

### 1. 合理使用回调机制

对于长时间运行的任务，设置回调URL比轮询更高效：

```json
{
  "callback_url": "https://your-server.com/callback"
}
```

### 2. 设置合理的超时时间

客户端应设置合理的超时时间，避免无限等待：

```python
try:
    result = wait_for_task_completion(task_id, timeout=300)
except TimeoutError:
    print("任务超时")
```

### 3. 错误处理

妥善处理任务失败情况，记录错误信息：

```python
if status == 'failed':
    error = task.get('error', {})
    print(f"任务失败: {error.get('message')}")
    # 记录错误日志
```

### 4. 定期清理

定期清理已完成的任务记录，释放存储空间：

```python
# 清理7天前的已完成任务
def cleanup_old_tasks():
    response = requests.get(f"{API_BASE}/async-tasks?status=completed")
    tasks = response.json()['data']['tasks']
    
    for task in tasks:
        task_time = datetime.fromisoformat(task['completed_at'])
        if (datetime.now() - task_time).days > 7:
            requests.delete(f"{API_BASE}/async-tasks/{task['task_id']}/cleanup")
```

### 5. 监控任务状态

对于重要的任务，建议实现状态监控：

```python
def monitor_task(task_id):
    while True:
        task = get_task_status(task_id)
        status = task['status']
        
        if status == 'completed':
            print("任务完成")
            break
        elif status == 'failed':
            print(f"任务失败: {task.get('error')}")
            break
        elif status == 'running':
            print(f"进度: {task.get('progress', 0)}%")
        
        time.sleep(5)
```

---

## 性能指标

| 指标 | 值 |
|------|-----|
| 任务提交延迟 | < 100ms |
| 状态查询延迟 | < 50ms |
| 结果获取延迟 | < 100ms |
| 最大并发任务数 | 1000 |
| 任务保留时间 | 7天 |

---

## 相关文档

- [API文档: 异步任务](../api/ASYNC-TASKS-API.md)
- [架构文档: 异步任务模块](../development/architecture.md#异步任务模块)
- [API总览](../api/README.md)

---

## 技术支持

如有问题，请联系：

- GitHub Issues: [Event2Table/issues](https://github.com/your-org/event2table/issues)
- 文档: [Event2Table Documentation](https://docs.event2table.com)
