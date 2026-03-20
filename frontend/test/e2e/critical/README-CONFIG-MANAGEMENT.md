# Event Node Builder - Config Management E2E Tests

## 快速开始

### 前置条件
1. ✅ 后端服务运行在 `http://127.0.0.1:5001`
2. ✅ 前端开发服务器运行在 `http://localhost:5173`
3. ✅ 测试数据库包含游戏数据 (Game GID: 10000147)

### 运行测试

```bash
cd /Users/mckenzie/Documents/event2table/frontend

# 运行所有配置管理测试
npm run test:e2e -- config-management.spec.ts

# 运行特定测试
npm run test:e2e -- config-management.spec.ts -g "Test 1"

# 调试模式（显示浏览器）
npm run test:e2e -- config-management.spec.ts --headed

# 调试模式（暂停执行）
npm run test:e2e -- config-management.spec.ts --debug
```

## 测试文件

**文件路径**: `frontend/test/e2e/critical/config-management.spec.ts`

**测试数量**: 3个核心测试

**测试类别**: Critical Path E2E Tests

## 测试描述

### Test 1: 完整工作流 (Complete Workflow)
测试从选择事件到保存配置的完整流程。

**步骤**:
1. 打开Event Node Builder页面
2. 选择事件
3. 添加字段到Canvas
4. 编辑字段别名
5. 预览HQL
6. 保存配置
7. 验证保存成功

**预期结果**: 配置成功保存，显示成功消息

### Test 2: 通过URL加载配置 (Load Config via URL)
测试使用URL参数加载现有配置。

**步骤**:
1. 直接访问带`config_id`参数的URL
2. 验证配置自动加载
3. 验证字段显示正确
4. 验证别名保留
5. 验证HQL预览正确

**预期结果**: 配置正确加载，所有字段和别名显示

**依赖**: Test 1必须成功保存配置

### Test 3: 编辑并保存配置 (Edit and Save Config)
测试修改现有配置并保存。

**步骤**:
1. 加载现有配置
2. 添加新字段
3. 修改字段别名
4. 删除字段
5. 保存修改
6. 重新加载验证

**预期结果**: 修改成功保存并持久化

**依赖**: Test 1必须成功保存配置

## 测试数据管理

### 自动创建测试数据
测试会自动创建测试配置，无需手动准备：

```typescript
// 自动生成唯一的配置名称
const TEST_CONFIG_NAME = 'E2E Test Config ' + Date.now();
```

### 自动清理测试数据
测试完成后自动删除测试配置：

```typescript
test.afterAll(async ({ request }) => {
  if (testConfigId) {
    await deleteTestConfig(request, testConfigId);
  }
});
```

### 动态获取事件ID
测试不依赖硬编码的事件ID：

```typescript
// 自动获取第一个可用事件
const testEvent = eventsData.data.find(e =>
  e.event_name === 'phxcard.gacha'
) || eventsData.data[0];
```

## 技术实现

### 错误处理策略
测试使用优雅的错误处理，避免因为UI元素不存在而失败：

```typescript
const isAliasVisible = await aliasInput.isVisible().catch(() => false);
if (isAliasVisible) {
  await aliasInput.fill('test_alias');
}
```

### 多选择器策略
提高测试稳定性，使用多种选择器：

```typescript
const saveButton = page.locator(
  'button:has-text("保存"), ' +
  'button[type="submit"], ' +
  '[data-testid="save-button"]'
);
```

### 测试依赖管理
使用`test.skip()`处理测试间的依赖：

```typescript
test.skip(!testConfigId, 'No config ID available from test 1');
```

## API端点

### REST API
- `GET /api/events?game_gid={gid}` - 获取事件列表
- `POST /event_node_builder/api/save` - 保存配置
- `GET /event_node_builder/api/load/{config_id}` - 加载配置
- `DELETE /event_node_builder/api/delete/{config_id}` - 删除配置

### URL参数
- `game_gid` - 游戏GID
- `config_id` - 配置ID（可选，用于加载现有配置）

## 故障排除

### 问题1: 测试超时
**症状**: 测试运行时间过长

**解决方案**:
1. 检查网络连接
2. 检查后端API是否正常运行
3. 增加timeout值：
   ```typescript
   await page.goto(url, { timeout: 120000 });
   ```

### 问题2: 元素找不到
**症状**: `TimeoutError: Element not found`

**解决方案**:
1. 确认前端服务正常运行
2. 检查URL是否正确
3. 增加等待时间：
   ```typescript
   await page.waitForTimeout(3000);
   ```

### 问题3: 配置保存失败
**症状**: 保存后没有成功消息

**解决方案**:
1. 检查后端日志
2. 验证API端点是否正确
3. 检查请求数据格式

### 问题4: Test 2和Test 3被跳过
**症状**: "Skipped: No config ID available from test 1"

**解决方案**:
1. 确保Test 1成功执行
2. 检查是否有网络错误
3. 查看Test 1的控制台输出

## 维护指南

### 更新UI选择器
如果UI变化，更新以下选择器：

```typescript
// 事件选择器
'[data-testid="event-selector"]'

// Canvas字段
'[data-testid="canvas-field"]'

// 保存按钮
'button:has-text("保存配置")'

// 成功提示
'.toast-success, .alert-success'
```

### 更新测试数据
如果游戏数据变化：

```typescript
// 更新游戏GID
const GAME_GID = 10000147;

// 更新事件选择逻辑
const testEvent = eventsData.data.find(e =>
  e.event_name === 'your_event_name'
);
```

## 测试覆盖率

| 功能 | Test 1 | Test 2 | Test 3 |
|------|--------|--------|--------|
| 选择事件 | ✅ | ❌ | ❌ |
| 添加字段 | ✅ | ❌ | ✅ |
| 编辑别名 | ✅ | ❌ | ✅ |
| 删除字段 | ❌ | ❌ | ✅ |
| HQL预览 | ✅ | ✅ | ❌ |
| 保存配置 | ✅ | ❌ | ✅ |
| 加载配置 | ❌ | ✅ | ✅ |
| 更新配置 | ❌ | ❌ | ✅ |

## 已知限制

1. **测试依赖**: Test 2和Test 3依赖Test 1的执行结果
2. **固定等待**: 使用`page.waitForTimeout()`可能导致测试慢
3. **UI依赖**: 选择器依赖UI结构，UI变化需要更新测试
4. **Toast验证**: 如果Toast不显示，无法验证成功消息

## 未来改进

1. **并行执行**: 移除测试依赖，支持并行执行
2. **性能测试**: 添加保存/加载时间测试
3. **错误场景**: 测试保存失败、加载失败等场景
4. **可视化对比**: 截图对比验证UI正确性
5. **API契约**: 验证前后端API一致性

## 相关文档

- [E2E测试指南](../../../../../../docs/testing/e2e-testing-guide.md)
- [Event Node Builder API文档](../../../../../../docs/development/event-node-builder-api.md)
- [测试最佳实践](../../../../../../docs/lessons-learned/testing-guide.md)

---

**创建时间**: 2026-03-12
**最后更新**: 2026-03-12
**维护者**: Event2Table Development Team
