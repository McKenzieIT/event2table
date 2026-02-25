# Legacy API 归档说明

**归档日期**: 2026-02-24  
**原文件**: `backend/api/routes/legacy_api.py`  
**归档原因**: 已迁移到GraphQL,REST API不再需要

---

## 归档内容

### legacy_api.py
- **文件大小**: 15,046 bytes
- **最后修改**: 2026-02-20
- **状态**: DEPRECATED
- **替代方案**: GraphQL API

---

## 迁移说明

### 已迁移功能
- ✅ 游戏管理 → GraphQL mutations
- ✅ 事件管理 → GraphQL mutations
- ✅ 参数管理 → GraphQL mutations
- ✅ 分类管理 → GraphQL mutations

### GraphQL替代方案
```graphql
# 替代 legacy game API
mutation CreateGame {
  createGame(gid: 123, name: "新游戏", odsDb: "game_db") {
    ok
    game { gid name }
    errors
  }
}

# 替代 legacy event API
mutation CreateEvent {
  createEvent(gameGid: 123, eventName: "event", eventNameCn: "事件", categoryId: 1) {
    ok
    event { id eventName }
    errors
  }
}
```

---

## 注意事项

1. **兼容性**: 旧客户端可能仍依赖此API
2. **迁移期**: 建议保留1-2个月的过渡期
3. **监控**: 监控旧API的调用频率
4. **清理**: 确认无调用后可完全删除

---

## 联系方式

如有问题,请联系GraphQL迁移团队。
