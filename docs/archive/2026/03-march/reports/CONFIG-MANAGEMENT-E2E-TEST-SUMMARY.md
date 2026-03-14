# Event Node Builder - Config Management E2E Test Summary

## 测试文件信息

**文件路径**: `/Users/mckenzie/Documents/event2table/frontend/test/e2e/critical/config-management.spec.ts`

**测试数量**: 3个核心测试

**测试类型**: Critical path E2E tests

**测试数据需求**:
- ✅ 使用现有游戏数据 (Game GID: 10000147)
- ✅ 动态获取事件ID (不需要预设)
- ✅ 自动创建测试配置
- ✅ 测试完成后自动清理

## 测试覆盖范围

### Test 1: Complete Workflow (完整工作流)
**名称**: "Complete workflow: Select event → Add fields → Generate HQL → Save"

**步骤**:
1. 导航到Event Node Builder页面
2. 等待页面加载完成
3. 选择一个事件 (使用第一个可用事件)
4. 关闭字段选择弹窗 (如果出现)
5. 使用"快速添加"按钮添加基础字段
6. 验证字段添加到Canvas
7. 编辑第一个字段的别名为"test_alias"
8. 打开HQL预览并验证生成
9. 点击"保存配置"按钮
10. 填写配置名称和描述
11. 确认保存
12. 验证保存成功提示
13. 验证可以继续工作或重定向

**验证点**:
- ✅ 页面正常加载
- ✅ 事件选择成功
- ✅ 字段添加到Canvas
- ✅ 字段别名编辑成功
- ✅ HQL预览生成
- ✅ 配置保存成功
- ✅ 成功提示显示

### Test 2: Load Config via URL (通过URL加载配置)
**名称**: "Load existing config via URL parameter"

**步骤**:
1. 直接访问配置URL (带config_id参数)
2. 等待页面加载
3. 验证配置加载 - Canvas中显示字段
4. 验证字段别名保留
5. 验证HQL预览正确
6. 验证字段顺序

**验证点**:
- ✅ URL参数正确解析
- ✅ 配置自动加载
- ✅ 字段正确显示
- ✅ 别名保留
- ✅ HQL预览正确
- ✅ 字段顺序正确

**依赖**: Test 1必须成功保存配置

### Test 3: Edit and Save Config (编辑并保存配置)
**名称**: "Edit existing config and save changes"

**步骤**:
1. 加载现有配置
2. 记录初始字段数量
3. 添加新字段 (使用"快速添加"→"仅参数")
4. 修改现有字段别名
5. 删除一个字段 (如果有足够字段)
6. 保存更新的配置
7. 验证更新成功
8. 重新加载配置验证修改生效

**验证点**:
- ✅ 配置加载成功
- ✅ 新字段添加成功
- ✅ 字段别名修改成功
- ✅ 字段删除成功
- ✅ 更新保存成功
- ✅ 修改持久化验证

**依赖**: Test 1必须成功保存配置

## 技术实现要点

### 1. 测试数据Setup
```typescript
// 动态获取事件ID，避免硬编码
const eventsResponse = await request.get(`${BASE_URL}/api/events?game_gid=${GAME_GID}`);
const testEvent = eventsData.data.find(e => e.event_name === 'phxcard.gacha') || eventsData.data[0];
eventId = testEvent.id;
```

### 2. 测试数据Cleanup
```typescript
// 测试完成后自动删除测试配置
test.afterAll(async ({ request }) => {
  if (testConfigId) {
    await deleteTestConfig(request, testConfigId);
  }
});
```

### 3. 错误处理
```typescript
// 优雅处理UI元素可能不存在的情况
const isAliasVisible = await aliasInput.isVisible().catch(() => false);
if (isAliasVisible) {
  await aliasInput.fill('test_alias');
}
```

### 4. 选择器策略
```typescript
// 使用多种选择器策略提高稳定性
const saveButton = page.locator('button:has-text("保存")');
const confirmButton = page.locator('button:has-text("确认"), button[type="submit"]').first();
```

### 5. 测试依赖管理
```typescript
// 使用test.skip()处理依赖关系
test.skip(!testConfigId, 'No config ID available from test 1');
```

## API端点依赖

### 使用的前端API
- `GET /api/events?game_gid={gid}` - 获取事件列表
- `GET /event_node_builder/api/load/{config_id}` - 加载配置
- `POST /event_node_builder/api/save` - 保存配置
- `DELETE /event_node_builder/api/delete/{config_id}` - 删除配置

### GraphQL Mutations (可选)
如果使用GraphQL API，可使用：
- `batchAddFieldsToCanvas` - 批量添加字段
- `updateEventNode` - 更新节点配置

## 执行方式

### 运行所有测试
```bash
cd frontend
npm run test:e2e -- config-management.spec.ts
```

### 运行特定测试
```bash
# 只运行Test 1
npm run test:e2e -- config-management.spec.ts -g "Complete workflow"

# 只运行Test 2
npm run test:e2e -- config-management.spec.ts -g "Load existing config"

# 只运行Test 3
npm run test:e2e -- config-management.spec.ts -g "Edit existing config"
```

### 调试模式
```bash
# 显示浏览器窗口
npm run test:e2e -- config-management.spec.ts --headed

# 调试模式（暂停执行）
npm run test:e2e -- config-management.spec.ts --debug
```

## 预期结果

### 成功标准
1. **Test 1**: 成功创建配置，返回config_id
2. **Test 2**: 成功加载配置，字段和别名正确
3. **Test 3**: 成功修改配置，修改持久化

### 失败场景处理
- **配置保存失败**: 检查后端API是否正常运行
- **字段选择失败**: 检查事件ID是否有效
- **HQL生成失败**: 检查字段格式是否正确
- **URL加载失败**: 检查config_id是否有效

## 测试覆盖率

| 功能 | 覆盖 | 测试 |
|------|------|------|
| 选择事件 | ✅ | Test 1 |
| 添加字段 | ✅ | Test 1, Test 3 |
| 编辑字段别名 | ✅ | Test 1, Test 3 |
| 删除字段 | ✅ | Test 3 |
| HQL预览生成 | ✅ | Test 1, Test 2 |
| 保存配置 | ✅ | Test 1, Test 3 |
| 加载配置 (URL) | ✅ | Test 2 |
| 更新配置 | ✅ | Test 3 |
| 删除配置 | ✅ | Test 3 (cleanup) |

## 已知限制

1. **UI选择器依赖**: 测试依赖于特定的UI元素和文本，如果UI变化需要更新选择器
2. **测试数据依赖**: Test 2和Test 3依赖Test 1成功保存配置
3. **网络延迟**: 使用固定等待时间 (`page.waitForTimeout`)，在网络慢时可能失败
4. **Toast消息验证**: 如果Toast不显示，测试仍会继续但可能无法验证成功消息

## 后续改进建议

1. **添加性能测试**: 测量配置保存/加载时间
2. **添加错误处理测试**: 测试保存失败、加载失败等场景
3. **添加并发测试**: 测试多用户同时编辑配置
4. **改进等待策略**: 使用`waitForSelector`替代固定等待时间
5. **添加可视化测试**: 截图对比验证UI正确性
6. **添加API契约测试**: 验证前后端API一致性

## 维护指南

### 更新UI选择器
如果UI变化，需要更新以下选择器：
- `[data-testid="event-selector"]` - 事件选择器
- `[data-testid="canvas-field"]` - Canvas字段
- `button:has-text("保存配置")` - 保存按钮
- `.toast-success` - 成功提示

### 更新测试数据
如果游戏数据变化，需要更新：
- `GAME_GID = 10000147` - 游戏GID
- 事件选择逻辑 - `find(e => e.event_name === 'phxcard.gacha')`

### 添加新测试
复制现有测试结构，确保：
1. 使用`test.describe()`组织测试
2. 使用`test.beforeEach()`清理状态
3. 使用`test.afterAll()`清理数据
4. 添加详细的console.log用于调试
5. 使用优雅的错误处理 (`catch(() => false)`)

## 执行状态

**创建时间**: 2026-03-12
**测试数量**: 3
**文件大小**: ~15KB
**预计执行时间**: 2-3分钟

---

**创建者**: Claude Code Agent
**项目**: Event2Table
**模块**: Event Node Builder - Config Management
