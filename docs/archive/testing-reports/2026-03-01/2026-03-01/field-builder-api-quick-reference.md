# Field Builder API 快速参考

## 现状

✅ **Field Builder API 已正确注册并正常工作**

无需修改 `web_app.py`，蓝图已通过 `api_bp` 正确注册。

---

## 可用的API端点

### 1. 列出所有配置
```bash
GET /api/field-builder/configs?limit=10&search=keyword
```

**示例**:
```bash
curl -s "http://127.0.0.1:5001/api/field-builder/configs?limit=10" | python3 -m json.tool
```

**响应**:
```json
{
    "success": true,
    "data": [
        {
            "id": 6,
            "name": "Api Test",
            "display_name": "API Test View",
            "view_name": "v_dwd_api_test",
            "created_at": "2026-03-01 07:45:04"
        }
    ]
}
```

### 2. 获取特定配置
```bash
GET /api/field-builder/configs/<id>
```

**示例**:
```bash
curl -s "http://127.0.0.1:5001/api/field-builder/configs/6" | python3 -m json.tool
```

### 3. 保存配置
```bash
POST /api/field-builder/configs
Content-Type: application/json

{
    "config": {
        "view_config": {...},
        "base_fields": [...],
        "custom_fields": {...}
    },
    "view_name": "v_dwd_custom_view",
    "display_name": "Custom View Display Name"
}
```

**示例**:
```bash
curl -s -X POST "http://127.0.0.1:5001/api/field-builder/configs" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "view_config": {},
      "base_fields": [],
      "custom_fields": {}
    },
    "view_name": "v_test",
    "display_name": "Test View"
  }' | python3 -m json.tool
```

### 4. 预览HQL
```bash
POST /api/field-builder/preview
Content-Type: application/json

{
    "config": {...},
    "source_events": [1, 2, 3],
    "view_name": "v_dwd_preview",
    "date_var": "${bizdate}"
}
```

**示例**:
```bash
curl -s -X POST "http://127.0.0.1:5001/api/field-builder/preview" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "view_config": {},
      "base_fields": ["role_id", "account_id"],
      "custom_fields": {}
    },
    "source_events": [1],
    "view_name": "v_test"
  }' | python3 -m json.tool
```

### 5. 删除配置
```bash
DELETE /api/field-builder/config/<id>
```

**示例**:
```bash
curl -s -X DELETE "http://127.0.0.1:5001/api/field-builder/config/6" | python3 -m json.tool
```

---

## 不存在的端点

以下端点**不存在**，会返回404：

- ❌ `/api/field-builder/base-fields`
- ❌ `/api/field-builder/custom-fields`
- ❌ `/api/field-builder/fields`

如需这些端点，请在 `backend/api/routes/field_builder.py` 中添加。

---

## 快速测试

### 1. 启动服务器
```bash
cd /Users/mckenzie/Documents/event2table
source backend/venv/bin/activate
python3 web_app.py
```

### 2. 测试端点
```bash
# 列出配置
curl -s "http://127.0.0.1:5001/api/field-builder/configs" | python3 -m json.tool

# 预览HQL
curl -s -X POST "http://127.0.0.1:5001/api/field-builder/preview" \
  -H "Content-Type: application/json" \
  -d '{"config":{"view_config":{},"base_fields":[],"custom_fields":{}},"source_events":[],"view_name":"test"}' \
  | python3 -m json.tool
```

### 3. 查看日志
```bash
tail -f /tmp/flask_server.log
```

---

## 前端集成

前端已正确使用这些端点：

```typescript
// frontend/src/shared/api/fieldBuilder.ts

// 保存配置
await fetch('/api/field-builder/configs', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(config)
});

// 加载配置
await fetch(`/api/field-builder/configs/${configId}`);

// 预览HQL
await fetch('/api/field-builder/preview', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ config, source_events, view_name })
});
```

---

## 文件位置

- **API路由**: `/Users/mckenzie/Documents/event2table/backend/api/routes/field_builder.py`
- **Service层**: `/Users/mckenzie/Documents/event2table/backend/services/field_builder/field_builder_service.py`
- **前端API**: `/Users/mckenzie/Documents/event2table/frontend/src/shared/api/fieldBuilder.ts`
