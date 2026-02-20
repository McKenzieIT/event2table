# 事件导入API快速参考

## 端点信息

- **URL**: `/api/events/import`
- **方法**: `POST`
- **Content-Type**: `application/json`

---

## 请求格式

### 最小请求

```json
{
    "game_gid": 10000147,
    "events": [
        {
            "event_code": "login",
            "event_name": "Login Event"
        }
    ]
}
```

### 完整请求

```json
{
    "game_gid": 10000147,
    "events": [
        {
            "event_code": "login",
            "event_name": "Login Event",
            "event_name_cn": "登录事件",
            "description": "User login event",
            "category": "authentication"
        },
        {
            "event_code": "logout",
            "event_name": "Logout Event",
            "event_name_cn": "登出事件",
            "description": "User logout event",
            "category": "authentication"
        }
    ]
}
```

---

## 响应格式

### 成功响应（200）

```json
{
    "success": true,
    "data": {
        "imported": 2,
        "failed": 0,
        "errors": []
    },
    "message": "Import completed: 2 imported, 0 failed"
}
```

### 部分成功（200）

```json
{
    "success": true,
    "data": {
        "imported": 1,
        "failed": 1,
        "errors": [
            "Row 2: Event login already exists"
        ]
    },
    "message": "Import completed: 1 imported, 1 failed"
}
```

### 失败响应（400/500）

```json
{
    "success": false,
    "error": "Validation error",
    "message": "game_gid必须是正整数"
}
```

---

## 字段说明

### 请求字段

| 字段 | 类型 | 必填 | 说明 | 限制 |
|------|------|------|------|------|
| `game_gid` | int | ✅ | 游戏GID | > 0 |
| `events` | array | ✅ | 事件列表 | 1-100个 |
| `event_code` | string | ✅ | 事件代码 | 1-50字符，无空格 |
| `event_name` | string | ✅ | 事件名称 | 1-100字符，无空格 |
| `event_name_cn` | string | ❌ | 事件中文名 | 0-100字符 |
| `description` | string | ❌ | 事件描述 | 0-500字符 |
| `category` | string | ❌ | 事件分类 | 默认"other" |

### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `imported` | int | 成功导入数量 |
| `failed` | int | 失败数量 |
| `errors` | array | 错误信息列表 |

---

## cURL示例

```bash
# 基本导入
curl -X POST http://127.0.0.1:5001/api/events/import \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 10000147,
    "events": [
      {
        "event_code": "test_login",
        "event_name": "Test Login",
        "category": "authentication"
      }
    ]
  }'

# 批量导入
curl -X POST http://127.0.0.1:5001/api/events/import \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 10000147,
    "events": [
      {"event_code": "login", "event_name": "Login"},
      {"event_code": "logout", "event_name": "Logout"},
      {"event_code": "register", "event_name": "Register"}
    ]
  }'
```

---

## Python示例

```python
import requests

url = "http://127.0.0.1:5001/api/events/import"
data = {
    "game_gid": 10000147,
    "events": [
        {
            "event_code": "login",
            "event_name": "Login Event",
            "event_name_cn": "登录事件",
            "category": "authentication"
        }
    ]
}

response = requests.post(url, json=data)
result = response.json()

if result["success"]:
    print(f"导入成功: {result['data']['imported']} 个")
    if result['data']['failed'] > 0:
        print(f"导入失败: {result['data']['failed']} 个")
        print(f"错误: {result['data']['errors']}")
else:
    print(f"导入失败: {result['message']}")
```

---

## JavaScript示例

```javascript
async function importEvents(gameGid, events) {
  const response = await fetch('/api/events/import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      game_gid: gameGid,
      events: events
    })
  });

  const result = await response.json();

  if (result.success) {
    console.log(`✅ 导入成功: ${result.data.imported} 个`);
    if (result.data.failed > 0) {
      console.warn(`⚠️ 导入失败: ${result.data.failed} 个`);
      console.error('错误:', result.data.errors);
    }
  } else {
    console.error(`❌ 导入失败: ${result.message}`);
  }

  return result;
}

// 使用示例
importEvents(10000147, [
  {
    event_code: 'login',
    event_name: 'Login Event',
    category: 'authentication'
  }
]);
```

---

## 常见错误

### 1. 游戏不存在

```json
{
    "success": true,
    "data": {
        "imported": 0,
        "failed": 1,
        "errors": ["Game with gid 99999999 not found"]
    }
}
```

**解决方案**: 使用有效的`game_gid`

### 2. 事件重复

```json
{
    "success": true,
    "data": {
        "imported": 0,
        "failed": 1,
        "errors": ["Row 1: Event login already exists"]
    }
}
```

**解决方案**: 使用不同的`event_code`或删除已存在的事件

### 3. 验证错误

```json
{
    "success": false,
    "error": "Validation error",
    "message": "event_code不能包含空格"
}
```

**解决方案**: 确保所有字段符合验证规则

---

## 测试数据示例

### 测试游戏GID: 10000147 (STAR001)

```json
{
    "game_gid": 10000147,
    "events": [
        {
            "event_code": "test_login_001",
            "event_name": "测试登录事件",
            "description": "这是一个测试导入的登录事件",
            "category": "login"
        },
        {
            "event_code": "test_logout_001",
            "event_name": "测试登出事件",
            "description": "这是一个测试导入的登出事件",
            "category": "logout"
        },
        {
            "event_code": "test_payment_001",
            "event_name": "测试支付事件",
            "description": "这是一个测试导入的支付事件",
            "category": "payment"
        }
    ]
}
```

---

## 注意事项

1. **重复检测**: 按`event_code`检测，同一游戏下不能重复
2. **自动分类**: 如果指定的`category`不存在，会自动创建
3. **独立处理**: 单个事件失败不影响其他事件
4. **批量限制**: 最多100个事件/请求
5. **XSS防护**: 所有字符串字段自动HTML转义
