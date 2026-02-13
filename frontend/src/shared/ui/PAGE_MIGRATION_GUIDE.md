# Page Migration Guide - 页面迁移统一设计规范

> **版本**: 1.0
> **创建日期**: 2026-02-11
> **设计主题**: Cyberpunk Lab

---

## 🎨 设计系统规范

### 核心设计原则

1. **一致性优先** - 所有页面使用统一的组件库 `@shared/ui`
2. **Cyberpunk Lab 主题** - 黑色背景 + 青色强调 (#06B6D4)
3. **Glassmorphism 效果** - 玻璃态卡片 + 背景模糊
4. **性能优先** - 使用 React.memo、useCallback、useMemo 优化
5. **无障碍访问** - ARIA 标签 + 键盘导航支持

---

## 📦 组件使用映射表

### 旧组件 → 新组件替换规则

| 旧组件/HTML | 新组件 | 导入路径 | 说明 |
|------------|--------|---------|------|
| `<button className="btn">` | `<Button>` | `@shared/ui` | 必须替换 |
| `<div className="card">` | `<Card>` | `@shared/ui` | 玻璃态卡片 |
| `<input>` | `<Input>` | `@shared/ui` | 带focus glow |
| `<textarea>` | `<TextArea>` | `@shared/ui` | 多行输入 |
| `<table>` | `<Table>` | `@shared/ui` | 数据表格 |
| `<select>` | `<Select>` | `@shared/ui` | 下拉选择器 |
| `<input type="checkbox">` | `<Checkbox>` | `@shared/ui` | 三态复选框 |
| `<input type="radio">` | `<Radio>` | `@shared/ui` | 单选按钮组 |
| Bootstrap Modal | `<Modal>` | `@shared/ui` | 玻璃态模态框 |
| `<span className="badge">` | `<Badge>` | `@shared/ui` | 状态徽章 |
| `Toast.tsx` (旧) | `<ToastProvider> + useToast()` | `@shared/ui` | 通知系统 |
| 自定义 Spinner | `<Spinner>` | `@shared/ui` | 加载指示器 |
| 自定义 Switch | `<Switch>` | `@shared/ui` | 切换开关 |

---

## 🏗️ 标准页面布局模式

### 模式 1: 列表页面（GamesList, EventsList, ParametersList）

```jsx
import { Button, Input, Card, Badge, Spinner } from '@shared/ui';

function PageList() {
  return (
    <div className="page-container">
      {/* 1. 页面头部 */}
      <div className="page-header">
        <div className="header-title">
          <h1>页面标题</h1>
          <p className="text-secondary">副标题/描述</p>
        </div>
        <div className="header-actions">
          <Button variant="primary">主要操作</Button>
          <Button variant="secondary">次要操作</Button>
        </div>
      </div>

      {/* 2. 统计卡片（可选） */}
      <div className="stats-grid">
        <Card className="stat-card">
          <Card.Body>
            <div className="stat-value">42</div>
            <div className="stat-label">统计项</div>
          </Card.Body>
        </Card>
      </div>

      {/* 3. 搜索和筛选 */}
      <Card>
        <Card.Body>
          <Input
            placeholder="搜索..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </Card.Body>
      </Card>

      {/* 4. 数据表格/列表 */}
      {isLoading ? (
        <Spinner size="lg" label="加载中..." />
      ) : (
        <Table data={data} columns={columns} />
      )}

      {/* 5. 分页（可选） */}
      <div className="pagination">
        {/* 分页组件 */}
      </div>
    </div>
  );
}
```

### 模式 2: 表单页面（GameForm, EventForm, ParameterForm）

```jsx
import { Button, Input, TextArea, Card, useToast } from '@shared/ui';

function PageForm() {
  const { success, error } = useToast();

  const handleSubmit = () => {
    try {
      // 提交逻辑
      success('保存成功');
    } catch (err) {
      error('保存失败');
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>创建/编辑</h1>
      </div>

      <Card>
        <Card.Body>
          <form onSubmit={handleSubmit}>
            <Input
              label="字段名"
              required
              error={errors.field}
              {...getFieldProps('field')}
            />

            <TextArea
              label="描述"
              rows={4}
              helperText="选填"
            />

            <div className="form-actions">
              <Button variant="ghost" onClick={handleCancel}>
                取消
              </Button>
              <Button variant="primary" type="submit">
                保存
              </Button>
            </div>
          </form>
        </Card.Body>
      </Card>
    </div>
  );
}
```

### 模式 3: 详情页面（EventDetail, GameDetail）

```jsx
import { Card, Badge, Button } from '@shared/ui';

function PageDetail() {
  return (
    <div className="page-container">
      {/* 头部 */}
      <div className="page-header">
        <h1>{data.name}</h1>
        <div className="header-actions">
          <Button variant="secondary">编辑</Button>
          <Button variant="danger">删除</Button>
        </div>
      </div>

      {/* 详情卡片 */}
      <Card>
        <Card.Header>
          <Card.Title>基本信息</Card.Title>
        </Card.Header>
        <Card.Body>
          {/* 详情内容 */}
        </Card.Body>
      </Card>

      {/* 关联数据 */}
      <Card>
        <Card.Header>
          <Card.Title>关联数据</Card.Title>
        </Card.Header>
        <Card.Body>
          {/* 关联列表 */}
        </Card.Body>
      </Card>
    </div>
  );
}
```

### 模式 4: Dashboard 页面

```jsx
import { Card, Button } from '@shared/ui';

function Dashboard() {
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Event2Table</h1>
        <p className="text-secondary">欢迎使用Event2Table</p>
      </div>

      {/* 统计卡片 */}
      <div className="stats-grid">
        {stats.map(stat => (
          <Card key={stat.label} className="stat-card">
            <Card.Body>
              <div className="stat-icon">
                <i className={`bi bi-${stat.icon}`}></i>
              </div>
              <div className="stat-content">
                <h3>{stat.value}</h3>
                <p>{stat.label}</p>
              </div>
            </Card.Body>
          </Card>
        ))}
      </div>

      {/* 快速操作 */}
      <div className="quick-actions">
        <h2>快速操作</h2>
        <div className="actions-grid">
          {actions.map(action => (
            <Card
              key={action.label}
              as={Link}
              to={action.to}
              className="action-card"
            >
              <Card.Body>
                <i className={`bi bi-${action.icon}`}></i>
                <h3>{action.label}</h3>
                <p>{action.description}</p>
              </Card.Body>
            </Card>
          ))}
        </div>
      </div>

      {/* 最近活动 */}
      <Card>
        <Card.Header>
          <Card.Title>最近活动</Card.Title>
        </Card.Header>
        <Card.Body>
          {/* 活动列表 */}
        </Card.Body>
      </Card>
    </div>
  );
}
```

---

## 🚫 必须移除的旧代码模式

### 1. Bootstrap 类名（全部替换）

```jsx
// ❌ 错误 - 不要使用 Bootstrap 类名
<div className="btn btn-primary">
<button className="btn btn-secondary">
<div className="card">
<div className="badge badge-info">

// ✅ 正确 - 使用新组件
<Button variant="primary">
<Button variant="secondary">
<Card>
<Badge variant="info">
```

### 2. 原生 HTML 表单元素（全部替换）

```jsx
// ❌ 错误
<input type="text" className="form-control">
<textarea className="form-control"></textarea>
<select className="form-select"></select>
<input type="checkbox">
<input type="radio">

// ✅ 正确
<Input label="字段名">
<TextArea label="描述">
<Select options={options}>
<Checkbox label="同意">
<Radio label="选项">
```

### 3. 旧的 Toast 导入（必须替换）

```jsx
// ❌ 错误
import { Toast } from '../../shared/ui/Toast';
import { ToastNotification } from './ToastNotification';

// ✅ 正确 - 使用新的 Context API
import { useToast } from '@shared/ui';

const { success, error, warning, info } = useToast();
```

### 4. 旧的 Spinner 实现（必须替换）

```jsx
// ❌ 错误
<div className="spinner-border" role="status">
  <span className="visually-hidden">加载中...</span>
</div>

// ✅ 正确
<Spinner size="md" label="加载中..." />
```

### 5. 原生 alert/confirm（建议替换）

```jsx
// ❌ 不推荐 - 阻塞式对话框
if (confirm('确定删除？')) {
  // ...
}

// ✅ 推荐 - 使用 Modal 组件
const [showConfirm, setShowConfirm] = useState(false);
<Modal isOpen={showConfirm} onClose={() => setShowConfirm(false)}>
  {/* 确认对话框内容 */}
</Modal>
```

---

## ✅ 性能优化清单

每个迁移的页面必须包含以下优化：

### React 性能优化

- [ ] 使用 `React.memo` 包装页面组件（如果 props 变化不频繁）
- [ ] 使用 `useCallback` 包装事件处理函数
- [ ] 使用 `useMemo` 优化计算密集型操作
- [ ] 使用 `@shared/ui` 的已优化组件（已包含 React.memo）

### 代码示例

```jsx
import React, { useState, useCallback, useMemo } from 'react';
import { Button, Input } from '@shared/ui';

function MyPage() {
  const [data, setData] = useState([]);

  // ✅ 使用 useCallback 优化事件处理
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  // ✅ 使用 useMemo 优化计算
  const filteredData = useMemo(() => {
    return data.filter(item => item.active);
  }, [data]);

  return (
    <div>
      <Button onClick={handleClick}>Click</Button>
    </div>
  );
}

// ✅ 使用 React.memo 包装
export default React.memo(MyPage);
```

---

## 🔍 旧代码残留检查清单

迁移完成后，必须检查以下项：

### Import 语句检查

```bash
# 搜索旧的组件导入
grep -r "from.*shared/ui/Button" frontend/src/analytics  # 应该改为 @shared/ui
grep -r "from.*Toast\.tsx" frontend/src/  # 应该改为 @shared/ui
grep -r "from.*ToastNotification" frontend/src/  # 应该删除
```

### CSS 类名检查

```bash
# 搜索 Bootstrap 类名
grep -r "className=\"btn " frontend/src/analytics  # 应该删除
grep -r "className=\"card\"" frontend/src/analytics  # 应该改为 Card 组件
grep -r "className=\"badge " frontend/src/analytics  # 应该改为 Badge 组件
```

### 组件使用检查

```bash
# 搜索原生表单元素
grep -r "<input " frontend/src/analytics  # 应该改为 Input 组件
grep -r "<textarea" frontend/src/analytics  # 应该改为 TextArea 组件
grep -r "<select " frontend/src/analytics  # 应该改为 Select 组件
```

---

## 📋 测试清单

每个页面迁移完成后，必须测试：

### 功能测试

- [ ] 页面可以正常加载
- [ ] 所有按钮点击有响应
- [ ] 表单提交正常工作
- [ ] 搜索/筛选功能正常
- [ ] 分页功能正常（如果有）
- [ ] 创建/编辑/删除操作正常
- [ ] Toast 通知正常显示

### 视觉测试

- [ ] Cyberpunk Lab 主题一致
- [ ] 玻璃态效果正常显示
- [ ] Focus glow 效果可见
- [ ] Hover 效果流畅
- [ ] 响应式布局正常（移动端）

### 性能测试

- [ ] 页面加载时间 < 2s
- [ ] 无控制台错误或警告
- [ ] React DevTools 显示组件重渲染合理

---

## 🎯 Button Variant 使用规范

| 操作类型 | 推荐 Variant | 说明 |
|---------|-------------|------|
| **主要操作** | `primary` | 创建、保存、提交 |
| **次要操作** | `secondary` | 取消、返回 |
| **危险操作** | `danger` | 删除、移除 |
| **成功操作** | `success` | 导入、下载 |
| **信息操作** | `outline-primary` | 查看、详情 |
| **编辑操作** | `outline-info` | 编辑、修改 |
| **取消选择** | `outline-secondary` | 清除、重置 |

---

## 📝 迁移步骤

1. **分析旧页面** - 识别使用的旧组件
2. **创建新版本** - 使用 `@shared/ui` 组件重写
3. **应用性能优化** - React.memo、useCallback、useMemo
4. **替换 Toast** - 使用 `useToast` Hook
5. **更新 CSS** - 移除 Bootstrap 类名依赖
6. **功能测试** - 验证所有功能正常
7. **旧代码检查** - 使用 grep 搜索残留
8. **视觉验证** - 确保主题一致性

---

**设计规范版本**: 1.0
**最后更新**: 2026-02-11
**维护者**: Event2Table Frontend Team
