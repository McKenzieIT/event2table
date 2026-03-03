# 批量操作GraphQL Schema设计文档

**项目**: Event2Table GraphQL迁移
**创建日期**: 2026-02-26
**状态**: 设计阶段

---

## 📋 文档概述

本文档定义了批量操作端点迁移到GraphQL的Schema设计。

### 迁移的批量操作端点

根据分析,需要迁移的批量操作端点包括:

1. **Games批量操作** (2个端点)
   - `DELETE /api/games/batch` - 批量删除游戏
   - `PUT /api/games/batch-update` - 批量更新游戏

2. **Events批量操作** (2个端点)
   - `DELETE /api/events/batch` - 批量删除事件
   - `PUT /api/events/batch-update` - 批量更新事件

3. **Flows批量操作** (2个端点)
   - `DELETE /api/flows/batch` - 批量删除流程
   - `PUT /api/flows/batch-update` - 批量更新流程

4. **Categories批量操作** (需要确认)
   - 可能存在批量删除分类

---

## 🏗️ GraphQL Schema设计

### 1. 通用批量操作类型

```graphql
# 批量操作结果
type BatchOperationResult {
  success: Boolean!
  message: String!
  affectedCount: Int!
  failedCount: Int!
  errors: [BatchOperationError!]
}

# 批量操作错误
type BatchOperationError {
  id: Int!
  error: String!
}

# 批量更新输入
input BatchUpdateInput {
  ids: [Int!]!
  updates: UpdateFields!
}

# 更新字段 (通用)
input UpdateFields {
  # Games字段
  name: String
  ods_db: String
  is_active: Boolean
  
  # Events字段
  event_name: String
  event_name_cn: String
  description: String
  category_id: Int
  
  # Flows字段
  flow_name: String
  flow_description: String
  status: String
}
```

### 2. Games批量操作

```graphql
# 批量删除游戏
mutation batchDeleteGames($ids: [Int!]!) {
  batchDeleteGames(ids: $ids) {
    success
    message
    affectedCount
    failedCount
    errors {
      id
      error
    }
  }
}

# 批量更新游戏
mutation batchUpdateGames($input: BatchUpdateInput!) {
  batchUpdateGames(input: $input) {
    success
    message
    affectedCount
    failedCount
    errors {
      id
      error
    }
  }
}
```

### 3. Events批量操作

```graphql
# 批量删除事件
mutation batchDeleteEvents($ids: [Int!]!) {
  batchDeleteEvents(ids: $ids) {
    success
    message
    affectedCount
    failedCount
    errors {
      id
      error
    }
  }
}

# 批量更新事件
mutation batchUpdateEvents($input: BatchUpdateInput!) {
  batchUpdateEvents(input: $input) {
    success
    message
    affectedCount
    failedCount
    errors {
      id
      error
    }
  }
}
```

### 4. Flows批量操作

```graphql
# 批量删除流程
mutation batchDeleteFlows($ids: [Int!]!) {
  batchDeleteFlows(ids: $ids) {
    success
    message
    affectedCount
    failedCount
    errors {
      id
      error
    }
  }
}

# 批量更新流程
mutation batchUpdateFlows($input: BatchUpdateInput!) {
  batchUpdateFlows(input: $input) {
    success
    message
    affectedCount
    failedCount
    errors {
      id
      error
    }
  }
}
```

---

## 🔧 类型定义实现

### BatchOperationErrorType

```python
class BatchOperationErrorType(graphene.ObjectType):
    """批量操作错误类型"""
    
    class Meta:
        description = "批量操作错误信息"
    
    id = Int(required=True, description="失败的ID")
    error = String(required=True, description="错误消息")
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BatchOperationErrorType':
        """Create BatchOperationErrorType instance from dictionary."""
        return cls(
            id=data.get('id'),
            error=data.get('error'),
        )
```

### BatchOperationResultType

```python
class BatchOperationResultType(graphene.ObjectType):
    """批量操作结果类型"""
    
    class Meta:
        description = "批量操作结果"
    
    success = Boolean(required=True, description="操作是否成功")
    message = String(description="操作消息")
    affected_count = Int(required=True, description="影响的数量")
    failed_count = Int(required=True, description="失败的数量")
    errors = List(lambda: BatchOperationErrorType, description="错误列表")
    
    @classmethod
    def success_result(cls, affected_count: int, message: str = "批量操作成功") -> 'BatchOperationResultType':
        """Create a successful result."""
        return cls(
            success=True,
            message=message,
            affected_count=affected_count,
            failed_count=0,
            errors=[]
        )
    
    @classmethod
    def partial_success_result(cls, affected_count: int, failed_count: int, errors: list, message: str = "部分成功") -> 'BatchOperationResultType':
        """Create a partial success result."""
        return cls(
            success=False,
            message=message,
            affected_count=affected_count,
            failed_count=failed_count,
            errors=errors
        )
```

---

## 📊 实现计划

### 第一阶段: 创建通用类型 (预计1-2小时)

1. 创建 `BatchOperationErrorType`
2. 创建 `BatchOperationResultType`
3. 创建 `BatchUpdateInput` 输入类型

### 第二阶段: 实现Games批量操作 (预计3-4小时)

1. 实现 `batchDeleteGames` mutation
2. 实现 `batchUpdateGames` mutation
3. 添加验证和错误处理
4. 集成缓存失效

### 第三阶段: 实现Events批量操作 (预计3-4小时)

1. 实现 `batchDeleteEvents` mutation
2. 实现 `batchUpdateEvents` mutation
3. 添加验证和错误处理
4. 处理级联删除

### 第四阶段: 实现Flows批量操作 (预计3-4小时)

1. 实现 `batchDeleteFlows` mutation
2. 实现 `batchUpdateFlows` mutation
3. 添加验证和错误处理

### 第五阶段: 测试和验证 (预计2-3小时)

1. 创建单元测试
2. 创建集成测试
3. 性能测试
4. 错误处理测试

---

## 🔒 安全性考虑

### 输入验证

1. **ID列表验证**
   - 必须是非空列表
   - 所有ID必须是正整数
   - 限制最大批量数量 (建议100)

2. **更新字段验证**
   - 字段名必须在白名单中
   - 字段值必须通过验证规则
   - 防止SQL注入

3. **权限检查**
   - 检查用户是否有权限操作这些资源
   - 检查资源是否存在

### 错误处理

1. **部分成功处理**
   - 记录每个失败的操作
   - 返回详细的错误信息
   - 不影响成功的操作

2. **事务处理**
   - 考虑使用事务保证数据一致性
   - 失败时回滚已执行的操作

---

## 📈 性能优化

### 批量操作优化

1. **使用批量SQL**
   - 使用 `IN` 子句批量查询
   - 使用批量UPDATE语句
   - 避免循环执行单条SQL

2. **缓存失效**
   - 批量操作后统一清理缓存
   - 使用模式匹配清理相关缓存

3. **限制批量大小**
   - 限制单次批量操作的最大数量
   - 建议最大100个ID

---

## 📝 注意事项

### 向后兼容性

1. 保留现有的REST API批量操作端点
2. GraphQL批量操作应与REST API行为一致
3. 错误消息应保持一致

### 测试策略

1. **单元测试**
   - 测试每个mutation的基本功能
   - 测试错误处理
   - 测试边界条件

2. **集成测试**
   - 测试批量操作与其他功能的关系
   - 测试缓存失效
   - 测试事务处理

3. **性能测试**
   - 测试不同批量大小的性能
   - 测试并发批量操作
   - 测试内存使用

---

## 📚 参考资料

- [GraphQL Complete Documentation](./GRAPHQL_COMPLETE_DOCUMENTATION.md)
- [V2 API Migration Execution Summary](./V2_API_MIGRATION_EXECUTION_SUMMARY.md)
- [Games API Routes](../../backend/api/routes/games.py)
- [Events API Routes](../../backend/api/routes/events.py)
- [Flows API Routes](../../backend/api/routes/flows.py)

---

**文档版本**: 1.0
**最后更新**: 2026-02-26
**维护者**: Event2Table开发团队
