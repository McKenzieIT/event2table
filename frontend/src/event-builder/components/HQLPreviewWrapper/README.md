# HQLPreviewWrapper - 使用指南

## 概述

`HQLPreviewWrapper` 是一个集成组件，提供V1和V2版本的无缝切换功能。

## 功能特性

- ✅ **V1/V2切换**: 一键切换旧版和新版HQL生成器
- ✅ **向后兼容**: 完全兼容现有V1接口
- ✅ **V2新功能**: 支持多事件JOIN/UNION、调试模式、性能分析
- ✅ **历史版本**: V2版本支持历史记录查看和恢复
- ✅ **独立可复用**: 可复制到其他React项目使用

## 快速开始

### 基础使用

```tsx
import React, { useState } from 'react';
import { HQLPreviewWrapper } from './components/HQLPreviewWrapper';

function EventBuilder() {
  const [events, setEvents] = useState([
    { game_gid: 10000147, event_id: 1, event_name: 'login' }
  ]);

  const [fields, setFields] = useState([
    { fieldName: 'role_id', fieldType: 'base' },
    { fieldName: 'zone_id', fieldType: 'param', jsonPath: '$.zoneId' }
  ]);

  const [conditions, setConditions] = useState([
    { field: 'role_id', operator: '=', value: 123, logicalOp: 'AND' }
  ]);

  const handleHQLGenerated = (hql: string, version: 'v1' | 'v2') => {
    console.log(`HQL Generated (${version}):`, hql);
  };

  const handleError = (error: string, version: 'v1' | 'v2') => {
    console.error(`Error (${version}):`, error);
  };

  return (
    <HQLPreviewWrapper
      events={events}
      fields={fields}
      conditions={conditions}
      defaultVersion="v2"
      showVersionSwitcher={true}
      onHQLGenerated={handleHQLGenerated}
      onError={handleError}
    />
  );
}
```

### V2多事件JOIN示例

```tsx
function MultiEventJoinExample() {
  const [events, setEvents] = useState([
    { game_gid: 10000147, event_id: 1, event_name: 'login' },
    { game_gid: 10000147, event_id: 2, event_name: 'logout' }
  ]);

  const [fields, setFields] = useState([
    { fieldName: 'role_id', fieldType: 'base' },
    { fieldName: 'account_id', fieldType: 'base' }
  ]);

  const [joinConditions, setJoinConditions] = useState([
    {
      leftEvent: 'login',
      leftField: 'role_id',
      rightEvent: 'logout',
      rightField: 'role_id',
      operator: '='
    }
  ]);

  return (
    <HQLPreviewWrapper
      events={events}
      fields={fields}
      mode="join"
      joinConditions={joinConditions}
      defaultVersion="v2"
      onHQLGenerated={(hql) => console.log('JOIN HQL:', hql)}
    />
  );
}
```

### V2调试模式

```tsx
function DebugModeExample() {
  return (
    <HQLPreviewPanelV2
      events={events}
      fields={fields}
      conditions={conditions}
      debugMode={true}
      onHQLGenerated={(hql) => console.log(hql)}
    />
  );
}
```

## API文档

### HQLPreviewWrapper Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `events` | `Event[]` | **必填** | 事件列表 |
| `fields` | `Field[]` | **必填** | 字段列表 |
| `conditions` | `Condition[]` | `[]` | WHERE条件 |
| `defaultVersion` | `'v1' \| 'v2'` | `'v2'` | 默认版本 |
| `showVersionSwitcher` | `boolean` | `true` | 显示版本切换器 |
| `availableEvents` | `any[]` | `[]` | 可选事件列表（多事件配置用） |
| `onHQLGenerated` | `function` | - | HQL生成回调 |
| `onError` | `function` | - | 错误回调 |

### Event类型

```typescript
interface Event {
  game_gid: number;        // 游戏GID
  event_id: number;        // 事件ID
  event_name?: string;     // 事件名称
  fields?: any[];          // 事件字段列表
}
```

### Field类型

```typescript
interface Field {
  fieldName: string;                       // 字段名
  fieldType: 'base' | 'param' | 'custom' | 'fixed';  // 字段类型
  alias?: string;                           // 别名
  jsonPath?: string;                        // JSON路径（param类型）
  customExpression?: string;               // 自定义表达式（custom类型）
  fixedValue?: any;                         // 固定值（fixed类型）
  aggregateFunc?: string;                   // 聚合函数
}
```

### Condition类型

```typescript
interface Condition {
  field: string;           // 字段名
  operator: string;        // 操作符（=, >, <, IN, LIKE等）
  value?: any;             // 值
  logicalOp?: 'AND' | 'OR'; // 逻辑操作符
}
```

## V2新功能

### 1. 多事件JOIN

```tsx
<HQLPreviewWrapper
  events={[event1, event2, event3]}
  mode="join"
  joinConditions={[
    { leftEvent: 'e1', leftField: 'id', rightEvent: 'e2', rightField: 'id', operator: '=' },
    { leftEvent: 'e2', leftField: 'user_id', rightEvent: 'e3', rightField: 'user_id', operator: '=' }
  ]}
/>
```

支持的JOIN类型：
- INNER JOIN
- LEFT JOIN
- RIGHT JOIN
- CROSS JOIN

### 2. 多事件UNION

```tsx
<HQLPreviewWrapper
  events={[event1, event2, event3]}
  mode="union"
  fields={fields}  // 所有事件必须使用相同字段
/>
```

### 3. 调试模式

```tsx
<HQLPreviewPanelV2
  debugMode={true}
  events={events}
  fields={fields}
/>
```

调试模式会显示：
- 字段构建步骤
- WHERE条件构建步骤
- HQL组装步骤
- 每步的中间结果

### 4. 性能分析

```tsx
<HQLPreviewPanelV2
  events={events}
  fields={fields}
  onHQLGenerated={(hql) => {
    // 自动分析性能
  }}
/>
```

性能指标包括：
- 分区过滤检测
- SELECT *检测
- JOIN计数
- 复杂度评分
- 优化建议

### 5. 历史版本

V2版本自动保存最近50条历史记录，支持：
- 查看历史HQL
- 一键恢复版本
- 版本对比

## 迁移指南

### 从V1迁移到V2

**步骤1**: 安装wrapper组件
```bash
# 无需安装，组件已集成
```

**步骤2**: 替换组件导入
```tsx
// 之前
import HQLPreview from './HQLPreview';
<HQLPreview {...props} />

// 之后
import { HQLPreviewWrapper } from './HQLPreviewWrapper';
<HQLPreviewWrapper {...props} defaultVersion="v2" />
```

**步骤3**: 更新字段格式
```tsx
// V1格式
{ name: 'role_id', type: 'base' }

// V2格式
{ fieldName: 'role_id', fieldType: 'base' }
```

**步骤4**: 测试功能
1. 生成单事件HQL
2. 生成多事件JOIN HQL
3. 生成多事件UNION HQL
4. 测试调试模式
5. 查看历史版本

## 故障排除

### 问题：V2组件无法加载

**解决方案**：
1. 检查API是否可访问：`GET /hql-preview-v2/api/status`
2. 检查控制台错误
3. 确认CORS配置正确

### 问题：字段格式错误

**解决方案**：
```tsx
// ❌ 错误
{ name: 'role_id' }

// ✅ 正确
{ fieldName: 'role_id', fieldType: 'base' }
```

### 问题：JOIN条件不生效

**解决方案**：
1. 确保至少有2个事件
2. JOIN条件中的事件名必须与events中的event_name一致
3. 左右字段名必须正确

## 最佳实践

1. **使用V2作为默认版本**
   ```tsx
   <HQLPreviewWrapper defaultVersion="v2" />
   ```

2. **启用历史版本**
   ```tsx
   <HQLPreviewWrapper enableHistory={true} />
   ```

3. **处理错误**
   ```tsx
   <HQLPreviewWrapper
     onError={(error, version) => {
       if (version === 'v2') {
         // 回退到V1
         setVersion('v1');
       }
       console.error(error);
     }}
   />
   ```

4. **性能优化**
   ```tsx
   // 启用缓存
   <HQLPreviewWrapper enableCache={true} />

   // 防抖自动生成（V2默认支持）
   ```

## 相关文档

- [HQL V2 API文档](../../../../../backend/api/routes/hql_preview_v2.py)
- [前端组件开发指南](../../../../../docs/development/frontend-guide.md)
- [HQL生成规范](../../../../../docs/specifications/hql-generation-guide.md)

## 支持

如有问题，请查看：
- [故障排除](#故障排除)
- [API文档](#api文档)
- [迁移指南](#迁移指南)
