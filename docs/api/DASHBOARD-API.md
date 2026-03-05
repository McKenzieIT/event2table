# Dashboard API 文档

**版本**: 9.0.0
**最后更新**: 2026-03-05
**架构**: ERS (Entity-Repository-Service)

---

## 概述

Dashboard API提供系统统计数据、最近事件和系统健康检查功能，用于前端Dashboard展示和系统监控。

### 特性

- **实时统计**: 游戏数量、事件数量、参数数量等核心指标
- **最近活动**: 最近创建/更新的事件和参数
- **系统健康**: 系统状态、缓存状态、数据库连接状态
- **分类统计**: 按分类统计事件数量
- **性能监控**: API性能指标、缓存命中率

---

## 端点列表

### Get Dashboard Statistics

**GET /api/dashboard/stats**

获取Dashboard统计数据，包括游戏、事件、参数、分类等核心指标。

**查询参数**:
- `game_gid` (int, optional): 游戏GID（过滤特定游戏的统计）

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5001/api/dashboard/stats"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "games": {
      "total": 1,
      "active": 1
    },
    "events": {
      "total": 57,
      "active": 57
    },
    "parameters": {
      "total": 345,
      "active": 320
    },
    "categories": {
      "total": 8,
      "active": 8
    },
    "flows": {
      "total": 12,
      "active": 10
    },
    "join_configs": {
      "total": 5,
      "active": 5
    },
    "by_category": [
      {
        "category": "登录/认证",
        "count": 1903
      },
      {
        "category": "充值/付费",
        "count": 856
      },
      {
        "category": "未分类",
        "count": 234
      }
    ],
    "recent_activity": {
      "last_event_created": "2026-03-05T10:30:00Z",
      "last_parameter_updated": "2026-03-05T11:00:00Z"
    }
  },
  "message": "Dashboard statistics retrieved successfully"
}
```

**错误码**:
- 500: 服务器错误

---

### Get Recent Events

**GET /api/dashboard/recent-events**

获取最近创建或更新的事件列表。

**查询参数**:
- `game_gid` (int, optional): 游戏GID
- `limit` (int, optional): 返回数量，默认10，最大50

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5001/api/dashboard/recent-events?limit=10"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "id": 57,
        "name": "login",
        "table_name": "dwd.v_dwd_10000147_login_di",
        "category": "登录/认证",
        "updated_at": "2026-03-05T11:00:00Z",
        "action": "created"
      },
      {
        "id": 56,
        "name": "logout",
        "table_name": "dwd.v_dwd_10000147_logout_di",
        "category": "登录/认证",
        "updated_at": "2026-03-05T10:30:00Z",
        "action": "updated"
      }
    ]
  },
  "message": "Recent events retrieved successfully"
}
```

**错误码**:
- 500: 服务器错误

---

### Get System Health

**GET /api/dashboard/system-health**

获取系统健康状态，包括数据库连接、缓存状态、服务状态等。

**请求示例**:
```bash
curl -X GET "http://127.0.0.1:5001/api/dashboard/system-health"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "components": {
      "database": {
        "status": "healthy",
        "connection_time_ms": 5,
        "size_mb": 9.3
      },
      "cache": {
        "status": "healthy",
        "type": "redis",
        "hit_rate": 85.5,
        "memory_used_mb": 128,
        "ttl_seconds": 1800
      },
      "api": {
        "status": "healthy",
        "uptime_seconds": 86400,
        "version": "9.0.0"
      },
      "canvas": {
        "status": "healthy",
        "active_flows": 10
      }
    },
    "checks": {
      "database_connection": "pass",
      "cache_connection": "pass",
      "disk_space": "pass",
      "memory_usage": "pass"
    },
    "timestamp": "2026-03-05T12:00:00Z"
  },
  "message": "System health check completed"
}
```

**健康状态说明**:
- `healthy`: 所有组件正常
- `degraded`: 部分组件性能下降但仍可用
- `unhealthy`: 一个或多个组件不可用

**错误码**:
- 500: 健康检查失败

---

## 性能监控端点

### Get Cache Statistics

**GET /api/cache/stats**

获取缓存统计信息（详见Cache API文档）。

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_keys": 1250,
    "hit_rate": 85.5,
    "memory_used_mb": 128,
    "keys_by_type": {
      "games": 10,
      "events": 570,
      "parameters": 3450,
      "categories": 80
    }
  }
}
```

---

### Get Performance Metrics

**GET /api/monitoring/metrics**

获取API性能指标（详见Monitoring API文档）。

**响应示例**:
```json
{
  "success": true,
  "data": {
    "api_calls": {
      "/api/games": 1250,
      "/api/events": 3450,
      "/api/parameters": 8900
    },
    "avg_response_time_ms": 45,
    "cache_hit_rate": 85.5,
    "error_rate": 0.01
  }
}
```

---

## 数据模型

### Dashboard Statistics

```json
{
  "games": {
    "total": 1,
    "active": 1
  },
  "events": {
    "total": 57,
    "active": 57
  },
  "parameters": {
    "total": 345,
    "active": 320
  },
  "categories": {
    "total": 8,
    "active": 8
  },
  "flows": {
    "total": 12,
    "active": 10
  },
  "join_configs": {
    "total": 5,
    "active": 5
  },
  "by_category": [
    {
      "category": "分类名称",
      "count": 100
    }
  ],
  "recent_activity": {
    "last_event_created": "2026-03-05T10:30:00Z",
    "last_parameter_updated": "2026-03-05T11:00:00Z"
  }
}
```

### System Health

```json
{
  "status": "healthy|degraded|unhealthy",
  "components": {
    "database": {
      "status": "healthy|degraded|unhealthy",
      "connection_time_ms": 5,
      "size_mb": 9.3
    },
    "cache": {
      "status": "healthy|degraded|unhealthy",
      "type": "redis",
      "hit_rate": 85.5,
      "memory_used_mb": 128,
      "ttl_seconds": 1800
    },
    "api": {
      "status": "healthy|degraded|unhealthy",
      "uptime_seconds": 86400,
      "version": "9.0.0"
    },
    "canvas": {
      "status": "healthy|degraded|unhealthy",
      "active_flows": 10
    }
  },
  "checks": {
    "database_connection": "pass|fail",
    "cache_connection": "pass|fail",
    "disk_space": "pass|fail",
    "memory_usage": "pass|fail"
  },
  "timestamp": "2026-03-05T12:00:00Z"
}
```

---

## 使用示例

### 获取Dashboard数据

```javascript
// 1. 获取统计数据
const getDashboardStats = async () => {
  const response = await fetch('/api/dashboard/stats');
  return response.json();
};

// 2. 获取最近事件
const getRecentEvents = async (limit = 10) => {
  const response = await fetch(
    `/api/dashboard/recent-events?limit=${limit}`
  );
  return response.json();
};

// 3. 获取系统健康状态
const getSystemHealth = async () => {
  const response = await fetch('/api/dashboard/system-health');
  return response.json();
};

// 使用示例
Promise.all([
  getDashboardStats(),
  getRecentEvents(10),
  getSystemHealth()
]).then(([stats, events, health]) => {
  console.log('Dashboard Stats:', stats.data);
  console.log('Recent Events:', events.data.events);
  console.log('System Health:', health.data);

  // 渲染Dashboard
  renderDashboard({
    stats: stats.data,
    events: events.data.events,
    health: health.data
  });
});
```

### 实时更新Dashboard

```javascript
// 定期刷新Dashboard数据（每30秒）
useEffect(() => {
  const refreshDashboard = async () => {
    const [stats, health] = await Promise.all([
      fetch('/api/dashboard/stats').then(r => r.json()),
      fetch('/api/dashboard/system-health').then(r => r.json())
    ]);

    setDashboardData({
      stats: stats.data,
      health: health.data,
      timestamp: new Date()
    });
  };

  // 初始加载
  refreshDashboard();

  // 定期刷新
  const interval = setInterval(refreshDashboard, 30000);

  return () => clearInterval(interval);
}, []);
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

**500 Internal Server Error - 数据库查询失败**:
```json
{
  "success": false,
  "error": "Failed to fetch dashboard statistics",
  "message": "Unable to retrieve dashboard statistics. Please try again later."
}
```

**503 Service Unavailable - 系统降级**:
```json
{
  "success": false,
  "error": "System degraded",
  "message": "One or more components are experiencing issues. Some data may be unavailable."
}
```

---

## 性能优化

### 缓存策略

**Dashboard统计数据缓存**:
- TTL: 120秒 (2分钟)
- 失效条件: 创建/更新/删除操作

**系统健康检查缓存**:
- TTL: 60秒 (1分钟)
- 失效条件: 定期刷新

### 数据预聚合

**统计数据预计算**:
- 游戏数量、事件数量等核心指标预计算
- 分类统计数据定期更新（每5分钟）

---

## 相关文档

- **[Cache API文档](CACHE-API.md)** - 缓存系统详细文档
- **[Monitoring API文档](../backend/api/routes/monitoring.py)** - 性能监控API
- **[经验文档 - 性能模式](../lessons-learned/performance-patterns.md)** - 性能优化经验

---

## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-02-20 | Dashboard API初始版本 |
| 2.0.0 | 2026-02-25 | 添加系统健康检查 |
| 3.0.0 | 2026-03-01 | 添加分类统计 |
| 4.0.0 | 2026-03-05 | 性能优化和缓存增强 |
