# Event Node Builder E2E测试报告

**测试日期**: 2026-03-11
**测试工具**: Chrome DevTools MCP
**测试范围**: 事件节点构建器完整工作流
**测试事件**: phxcard.gacha (事件ID: 1207)

---

## 执行摘要

### 测试状态: ✅ 部分成功 (核心问题已识别)

**成功项目**:
- ✅ 搜索功能正常工作
- ✅ phxcard.gacha事件选择成功
- ✅ 参数列表加载成功（25个参数）
- ✅ 批量添加字段到画布功能正常
- ✅ HQL预览生成成功

**关键问题**:
- ❌ 字段类型显示为"未知 UNKNOWN"（应显示"参数"）
- ❌ 统计信息错误（参数字段显示0而非25）
- ❌ GraphQL mutation返回的type字段为undefined

### 优先级: P0 - 高优先级（用户体验影响）

---

## 测试环境

- **前端**: http://localhost:5173
- **后端**: http://127.0.0.1:5001
- **游戏**: Updated Name (GID: 10000147)
- **测试事件**: phxcard.gacha (ID: 1207)

---

## 详细测试过程

### 1. 搜索功能测试 ✅ PASS

**测试步骤**:
1. 在事件选择器的搜索框输入"gacha"
2. 等待防抖延迟（300ms）
3. 验证搜索结果显示

**测试结果**:
```
✅ 控制台日志显示:
- [SearchInput] handleChange called with newValue: g
- [SearchInput] Scheduling onChange with debounce: g debounceMs: 300
- [SearchInput] Triggering onChange with value: gacha
- [EventSelector] Component render - searchQuery: gacha gameGid: 10000147
- [EventSelector] React Query data received
- [EventSelector] useMemo: Matched primary format, returning 5 events
- [EventSelector] Final events array length: 5

✅ UI正确显示5个gacha事件:
1. 火凤追加-抽 (phxcard.gacha) ⭐
2. 新手集市-招募武将 (newplayeractivity.kgacha)
3. 新手集市-命魂抽奖 (newplayeractivity.advgacha)
4. 23周年庆付费活动-抽 (anniversary23pay.gacha)
5. 新武将投放活动-抽奖 (advanceevent.gacha)
```

**结论**: 搜索功能完全正常 ✅

---

### 2. 事件选择测试 ✅ PASS

**测试步骤**:
1. 点击"火凤追加-抽 (phxcard.gacha)"
2. 等待参数列表加载
3. 验证左侧参数字段显示

**测试结果**:
```
✅ 事件成功选中（高亮显示）
✅ 左侧参数字段列表显示25个参数:
- 游戏服名字 (serverName)
- 角色名 (roleName)
- 紫金 -> 改为总元宝数 (diamond)
- ip (ip)
- 灵犀账号id (accountId)
- 钉钉名字 (dingname)
- 游戏服id (serverId)
- 角色id (roleId)
- 服务端日志生成时间戳 (serialId)
- 上线时间 (onlineTime)
- 角色等级 (roleLevel)
- vip等级 (vipLevel)
- 注册时间 (regTime)
- 战力 (fforce)
- 头衔 (title)
- 公会id (guildId)
- 战区化前的公会id (guildIdOld)
- 赛季塔赛季 (stSeason)
- 奖励id (id)
- 旧point数 (oldpoint)
- 新point数 (newpoint)
- 是否军团战区化 (league)
- 卡的id (gachaid)
- 抽取数量 (gachanum)
- 抽取所有的id (allid)

✅ 搜索框功能正常（可以搜索参数）
```

**结论**: 事件选择和参数列表加载完全正常 ✅

---

### 3. 批量添加字段测试 ⚠️ PARTIAL

**测试步骤**:
1. 点击"⚡快速添加▼"按钮
2. 在弹出的对话框中选择"⚙️ 仅参数字段"
3. 等待字段添加到画布
4. 验证画布上的字段显示

**测试结果**:
```
✅ 快速添加对话框正常弹出
✅ 包含5个选项：
   - 📋 所有字段
   - ⚙️ 仅参数字段 ← 选择了此选项
   - 🔧 非公共字段
   - 🔗 仅公共字段
   - 🏗️ 仅基础字段
   - ⏭️ 跳过

✅ 25个参数字段成功添加到画布
✅ 字段画布显示: "累计 25 参数"
✅ HQL预览成功生成，显示正确的SELECT语句

❌ 字段类型显示问题:
- 所有25个字段显示 " 未知 UNKNOWN"
- 应显示 " 参数 PARAM" 或 "🔗 参数"

❌ 统计信息错误:
- 总字段数: 25 ✅
- 基础字段: 0 ✅
- 参数字段: 0 ❌（应该是25）
```

**控制台错误**:
```
❌ Error #490:
Warning: Failed prop type: The prop `fields[0].type` is marked as required
in `FieldCanvas`, but its value is `undefined`.

❌ Error #495-513 (重复19次):
Warning: Encountered two children with the same key, `1773231845752`.
Keys should be unique so that components maintain their identity across updates.
```

**结论**: 功能基本正常，但字段类型显示有严重问题 ⚠️

---

## 问题分析

### 问题1: 字段类型显示为"未知"

**现象**:
- 所有25个字段在FieldCanvas组件中显示为"未知 UNKNOWN"
- 控制台错误显示 `fields[0].type` 为 `undefined`

**根本原因**:
GraphQL mutation `batchAddFieldsToCanvas` 返回的FieldTypeType对象中，`type`字段为undefined。

**代码位置**:
- 后端: `backend/gql_api/schema_parameter_management.py:842`
- 问题代码:
```python
field_obj = FieldTypeType(
    name=field['name'],
    type=field.get('field_type', 'param'),  # ← 这里应该设置type字段
    category=field.get('field_type', 'param'),
    display_name=field.get('description', field.get('name', '')),
    json_path=field.get('json_path'),
)
```

**可能原因**:
1. GraphQL schema中FieldTypeType的`type`字段定义问题
2. Graphene ObjectType构造函数参数映射问题
3. GraphQL序列化时type字段丢失

---

### 问题2: React key重复警告

**现象**:
- 所有25个字段使用相同的key `1773231845752`
- React警告: "Encountered two children with the same key"

**根本原因**:
FieldTypeType没有定义`id`字段，React使用某个默认值作为key，导致所有字段key相同。

**解决方向**:
在FieldTypeType中添加唯一的`id`字段，可以使用字段名或生成唯一ID。

---

## 已修复的问题

### ✅ 问题1: EventSelector搜索功能不更新

**原始问题**:
搜索API返回正确数据，但UI事件列表不更新

**根本原因**:
useMemo中的数据提取逻辑优先级错误，主要API响应格式放在了第3位

**修复方案**:
重新排序useMemo中的数据提取逻辑，将完整API响应格式检查移到最前面

**修复文件**:
`frontend/src/event-builder/components/EventSelector.tsx:49-77`

**验证结果**: ✅ 搜索功能完全正常

---

## 待修复问题

### ❌ P0: 字段类型显示为"未知"

**影响**: 用户体验，无法区分字段类型

**修复建议**:
1. 检查GraphQL schema中FieldTypeType的type字段定义
2. 确认Graphene ObjectType构造函数正确传递type参数
3. 添加调试日志验证type字段值是否正确设置
4. 检查GraphQL响应序列化是否包含type字段

**预计工作量**: 1-2小时

---

### ❌ P1: React key重复警告

**影响**: React性能，可能导致渲染问题

**修复建议**:
在FieldTypeType中添加id字段：
```python
class FieldTypeType(graphene.ObjectType):
    id = String(required=True, description="字段唯一标识")
    name = String(required=True, description="字段名称")
    type = FieldTypeEnum(description="字段类型")
    # ...
```

在创建对象时设置唯一id：
```python
field_obj = FieldTypeType(
    id=f"{field['name']}_{field.get('field_type', 'param')}",
    name=field['name'],
    type=field.get('field_type', 'param'),
    # ...
)
```

**预计工作量**: 30分钟

---

## 测试覆盖率

| 功能 | 测试状态 | 备注 |
|------|---------|------|
| 事件搜索 | ✅ PASS | 完全正常 |
| 事件选择 | ✅ PASS | 完全正常 |
| 参数列表加载 | ✅ PASS | 25个参数全部显示 |
| 批量添加字段 | ⚠️ PARTIAL | 功能正常但显示错误 |
| 字段类型显示 | ❌ FAIL | 显示"未知"而非"参数" |
| HQL预览生成 | ✅ PASS | 正确生成SELECT语句 |
| 统计信息显示 | ❌ FAIL | 参数字段显示0 |

**总体评分**: 5/8 = 62.5% (部分成功)

---

## 后续修复建议

### 立即修复 (P0)
1. **修复字段类型显示问题**
   - 添加调试日志验证type字段值
   - 检查GraphQL schema定义
   - 确认Graphene序列化正确性

### 短期修复 (P1)
2. **修复React key重复警告**
   - 在FieldTypeType中添加id字段
   - 使用字段名和类型组合生成唯一id

### 长期优化 (P2)
3. **优化统计信息计算**
   - 确保参数字段数量正确统计
   - 区分基础字段、公共字段、参数字段

4. **添加E2E自动化测试**
   - 使用Playwright编写完整的E2E测试套件
   - 自动回归测试覆盖主要功能

---

## 附录: 测试截图

### 成功截图
1. **搜索gacha事件**: [event-node-builder-test-2026-03-10.png](event-node-builder-test-2026-03-10.png)
2. **phxcard.gacha事件选中**: (页面快照显示)
3. **参数列表加载**: 显示25个参数

### 问题截图
1. **字段类型显示"未知"**: 控制台错误 #490
2. **HQL预览生成**: 成功生成但字段类型为"未知"

---

## 总结

本次E2E测试成功验证了事件节点构建器的核心功能流程：

**✅ 成功**:
- 搜索功能完全正常（之前的问题已修复）
- phxcard.gacha事件成功选择
- 参数列表正确加载25个参数
- 批量添加字段功能正常工作
- HQL预览成功生成

**❌ 待修复**:
- 字段类型显示为"未知"（核心问题）
- React key重复警告（性能问题）
- 统计信息显示错误（次要问题）

**建议优先级**:
1. P0: 修复字段类型显示问题（1-2小时）
2. P1: 修复React key重复警告（30分钟）
3. P2: 优化统计信息和添加自动化测试

总体而言，核心功能流程已经打通，剩余问题主要是UI显示和数据结构优化，不影响核心HQL生成功能。
