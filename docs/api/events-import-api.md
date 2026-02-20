# 事件导入API文档

## 概述

Event2Table提供两种事件导入方式：
1. **JSON格式批量导入** - `/api/events/import`（推荐用于小批量）
2. **Excel文件导入** - `/events/import`（适合大批量）

---

## JSON格式批量导入 ⭐

### 端点
```
POST /api/events/import
```

### 请求格式

**Headers**:
```http
Content-Type: application/json
```

**Body**:
```json
{
    "game_gid": 10000147,
    "events": [
        {
            "event_code": "test_event_001",
            "event_name": "测试事件",
            "event_name_cn": "测试事件",
            "description": "事件描述",
            "category": "login"
        },
        {
            "event_code": "test_event_002",
            "event_name": "Another Event",
            "event_name_cn": "另一个事件",
            "description": "另一个描述",
            "category": "battle"
        }
    ]
}
```

### 请求参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| game_gid | int | ✅ | 游戏GID |
| events | array | ✅ | 事件列表（最多100个） |
| events[].event_code | string | ✅ | 事件代码（字母、数字、下划线，不含空格） |
| events[].event_name | string | ✅ | 事件英文名称 |
| events[].event_name_cn | string | ❌ | 事件中文名称 |
| events[].description | string | ❌ | 事件描述（最长500字符） |
| events[].category | string | ❌ | 事件分类（默认: "other"） |

### 响应格式

**成功响应**（HTTP 200）:
```json
{
    "success": true,
    "data": {
        "imported": 5,
        "failed": 1,
        "errors": [
            "Row 3: Event test_event_003 already exists"
        ]
    },
    "message": "Import completed: 5 imported, 1 failed"
}
```

**错误响应**（HTTP 400/404/500）:
```json
{
    "success": false,
    "error": "Validation error",
    "message": "game_gid must be a positive integer"
}
```

### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 是否成功 |
| data.imported | int | 成功导入数量 |
| data.failed | int | 失败数量 |
| data.errors | array | 错误信息列表（每个错误对应一行） |
| message | string | 操作结果摘要 |

### 限制和验证

- ✅ **XSS防护**: 所有文本字段自动转义HTML字符
- ✅ **SQL注入防护**: 使用参数化查询
- ✅ **唯一性检查**: event_code在同一game_gid下必须唯一
- ✅ **批量限制**: 最多一次导入100个事件
- ✅ **格式验证**: event_code只允许字母、数字、下划线

### 错误码

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 成功（部分成功也返回200） |
| 400 | 请求参数验证失败 |
| 404 | 游戏不存在 |
| 500 | 服务器内部错误 |

### 使用场景

**推荐使用JSON API的场景**:
- ✅ 小批量导入（< 100个事件）
- ✅ 前端表单直接提交
- ✅ 自动化脚本集成
- ✅ 需要实时反馈的场景

**不推荐使用JSON API的场景**:
- ❌ 大批量导入（> 100个事件）→ 使用Excel文件导入
- ❌ 复杂的数据转换逻辑
- ❌ 需要离线准备数据的场景

---

## Excel文件导入（旧版）📊

### 端点
```
POST /events/import
```

### 请求格式

**Content-Type**:
```http
Content-Type: multipart/form-data
```

**Body**:
```http
file: [Excel文件]
game_gid: 10000147
```

### 说明

此端点用于上传Excel文件，服务器端解析后导入数据库。

**与JSON API的区别**:
| 特性 | JSON API | Excel文件导入 |
|------|----------|--------------|
| Content-Type | application/json | multipart/form-data |
| 数据格式 | JSON | Excel (.xlsx, .xls) |
| 解析位置 | 前端 | 后端 |
| 批量限制 | 100个事件 | 无限制 |
| 适用场景 | 小批量、实时 | 大批量、离线 |

### 推荐使用

- **小批量（<100）**: 使用 `/api/events/import` JSON格式
- **大批量（>100）**: 使用 `/events/import` Excel文件
- **前端集成**: 优先使用JSON API
- **手动导入**: 使用Excel文件

---

## 完整示例

### 前端JavaScript示例

```javascript
// 使用fetch API
async function importEvents(gameGid, events) {
    const response = await fetch('/api/events/import', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            game_gid: gameGid,
            events: events
        })
    });

    const result = await response.json();

    if (result.success) {
        console.log(`✅ Imported ${result.data.imported} events`);
        if (result.data.failed > 0) {
            console.warn(`⚠️ ${result.data.failed} events failed:`, result.data.errors);
        }
    } else {
        console.error(`❌ Import failed: ${result.message}`);
    }

    return result;
}

// 使用示例
const events = [
    {
        event_code: 'login_success',
        event_name: 'Login Success',
        event_name_cn: '登录成功',
        description: 'User successfully logged in',
        category: 'login'
    },
    {
        event_code: 'battle_start',
        event_name: 'Battle Start',
        event_name_cn: '战斗开始',
        description: 'Battle started',
        category: 'battle'
    }
];

importEvents(10000147, events);
```

### Python示例（使用requests）

```python
import requests

API_URL = "http://127.0.0.1:5001/api/events/import"

data = {
    "game_gid": 10000147,
    "events": [
        {
            "event_code": "test_event_001",
            "event_name": "Test Event",
            "event_name_cn": "测试事件",
            "description": "This is a test event",
            "category": "test"
        }
    ]
}

response = requests.post(API_URL, json=data)
result = response.json()

if result['success']:
    print(f"✅ Imported {result['data']['imported']} events")
    if result['data']['failed'] > 0:
        print(f"⚠️ {result['data']['failed']} events failed:")
        for error in result['data']['errors']:
            print(f"   - {error}")
else:
    print(f"❌ Import failed: {result['message']}")
```

### cURL示例

```bash
curl -X POST http://127.0.0.1:5001/api/events/import \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 10000147,
    "events": [
      {
        "event_code": "test_event_001",
        "event_name": "Test Event",
        "event_name_cn": "测试事件",
        "description": "This is a test event",
        "category": "test"
      }
    ]
  }'
```

---

## 测试

### 运行测试脚本

```bash
# 确保Flask服务器正在运行
python web_app.py

# 在另一个终端运行测试
python scripts/manual/test_json_event_import.py
```

### 测试覆盖

测试脚本包含以下测试用例：
1. ✅ **基本导入测试** - 验证正常导入流程
2. ✅ **重复检测测试** - 验证重复事件代码被正确拒绝
3. ✅ **无效game_gid测试** - 验证不存在的游戏GID被正确拒绝

### 预期输出

```
================================================================================
Testing JSON Event Import API
================================================================================

URL: http://127.0.0.1:5001/api/events/import
Method: POST
Content-Type: application/json

Request Body:
{
  "game_gid": 90000001,
  "events": [
    {
      "event_code": "test_json_001",
      "event_name": "JSON测试事件1",
      ...
    }
  ]
}

--------------------------------------------------------------------------------
Sending request...

Status Code: 200
Response Time: 0.15s

Response Body:
{
  "success": true,
  "data": {
    "imported": 2,
    "failed": 0,
    "errors": []
  },
  "message": "Import completed: 2 imported, 0 failed"
}

================================================================================
Validation Results
================================================================================

✅ Import successful!
   Imported: 2
   Failed: 0
   Errors: None

✅ All events imported successfully!
```

---

## 常见问题 (FAQ)

### Q1: 导入时提示"Event already exists"

**原因**: event_code在同一game_gid下必须唯一

**解决方案**:
- 检查数据库中是否已存在该event_code
- 使用不同的event_code
- 或先删除旧事件再导入

### Q2: 导入数量限制是多少？

**限制**: 最多一次导入100个事件

**原因**: 防止请求超时和内存溢出

**解决方案**: 分批导入，每批不超过100个

### Q3: 如何处理特殊字符？

**处理**: 所有文本字段自动进行XSS防护（HTML转义）

**示例**:
```javascript
// 输入
event_name: "<script>alert('xss')</script>"

// 存储到数据库
event_name: "&lt;script&gt;alert('xss')&lt;/script&gt;"
```

### Q4: event_code有什么格式要求？

**要求**:
- 只允许字母、数字、下划线
- 不允许空格
- 不允许特殊字符

**示例**:
```
✅ login_success
✅ BattleStart
✅ event_001

❌ login-success
❌ login success
❌ login@success
```

### Q5: 如何验证导入是否成功？

**方法1**: 检查响应中的`data.imported`字段
```javascript
if (result.data.imported > 0) {
    console.log("导入成功");
}
```

**方法2**: 查询数据库
```sql
SELECT * FROM log_events
WHERE game_gid = 10000147
AND event_name IN ('test_json_001', 'test_json_002');
```

**方法3**: 在前端查看事件列表

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-20 | 初始版本：JSON格式批量导入API |
