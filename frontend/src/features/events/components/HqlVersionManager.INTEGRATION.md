/**
 * HQL版本管理功能 - 集成指南
 *
 * 本文档说明如何将HQL版本管理功能集成到事件编辑页面中
 */

## 功能概述

HQL版本管理功能提供以下能力：
- 保存HQL版本快照
- 查看版本历史（列表视图和时间线视图）
- 对比两个版本的差异
- 回滚到指定版本
- 实时版本变更追踪

## 集成步骤

### 1. 导入组件

```tsx
import { HqlVersionManager } from '@features/events/components';
```

### 2. 在事件编辑页面中使用

```tsx
function EventEditPage() {
  const [hql, setHql] = useState<string>('');
  const eventId = 123; // 从路由或状态获取

  return (
    <div className="event-edit-page">
      {/* HQL编辑器 */}
      <HqlEditor 
        value={hql}
        onChange={setHql}
      />

      {/* HQL版本管理 */}
      <HqlVersionManager
        eventId={eventId}
        currentHql={hql}
        onVersionChange={setHql}
      />
    </div>
  );
}
```

### 3. 组件Props说明

#### HqlVersionManager Props

| 属性 | 类型 | 必需 | 说明 |
|------|------|------|------|
| eventId | number | 是 | 事件ID |
| currentHql | string | 是 | 当前HQL内容 |
| onVersionChange | (hql: string) => void | 否 | 版本变更回调，用于回滚时更新编辑器内容 |

### 4. 功能说明

#### 保存版本
- 点击"保存版本"按钮
- 可选输入版本描述
- 系统自动保存当前HQL内容为快照

#### 查看历史
- 支持列表视图和时间线视图切换
- 显示版本号、创建时间、描述等信息
- 可展开查看完整HQL内容

#### 对比版本
- 在历史列表中选择一个版本
- 选择另一个版本进行对比
- 显示差异对比（diff格式）

#### 回滚版本
- 选择要回滚的版本
- 点击"回滚到此版本"按钮
- 编辑器内容更新为选定版本的HQL

## 文件结构

```
frontend/src/features/events/
├── api/
│   ├── hqlVersionApi.ts          # API客户端
│   └── index.ts                  # API导出
├── hooks/
│   ├── useHqlVersionHistory.ts   # 版本历史查询hook
│   ├── useHqlVersionCompare.ts   # 版本对比hook
│   ├── useSaveHqlVersion.ts      # 保存版本hook
│   ├── useRollbackHqlVersion.ts  # 回滚版本hook
│   └── index.ts                  # Hooks导出
└── components/
    ├── HqlVersionHistory.tsx     # 版本历史列表
    ├── HqlVersionHistory.css
    ├── HqlVersionCompare.tsx     # 版本对比组件
    ├── HqlVersionCompare.css
    ├── HqlVersionTimeline.tsx    # 版本时间线
    ├── HqlVersionTimeline.css
    ├── HqlVersionActions.tsx     # 版本操作按钮
    ├── HqlVersionActions.css
    ├── HqlVersionManager.tsx     # 版本管理容器
    ├── HqlVersionManager.css
    └── index.ts                  # 组件导出
```

## API端点

- POST /api/hql-versions/save - 保存HQL版本
- POST /api/hql-versions/compare - 对比两个版本
- GET /api/hql-versions/history/:event_id - 获取版本历史
- POST /api/hql-versions/rollback - 回滚到指定版本
- GET /api/hql-versions/latest/:event_id - 获取最新版本
- GET /api/hql-versions/:version_id - 获取特定版本

## 注意事项

1. **事件ID**: 确保传入正确的eventId，否则无法加载版本历史
2. **HQL内容**: 只有非空的HQL内容才能保存版本
3. **回滚确认**: 回滚操作会覆盖当前编辑器内容，请谨慎操作
4. **版本对比**: 需要选择两个不同的版本才能进行对比

## 样式定制

所有组件都使用独立的CSS文件，可以根据项目主题进行定制：

- 使用CSS变量控制颜色
- 支持响应式布局
- 遵循项目现有的设计规范

## 性能优化

- 使用React.memo优化组件渲染
- 使用React Query缓存API响应
- 懒加载版本详情内容
- 虚拟滚动支持大量版本历史

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

需要以下浏览器API支持：
- fetch API
- ES6+语法
- CSS Grid和Flexbox
