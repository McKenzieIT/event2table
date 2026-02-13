# 组件问题记录

本文档记录Event2Table项目中发现的组件问题和修复方案。

---

## Card组件 - as属性支持

**发现时间**: 2026-02-11
**状态**: ✅ 已修复

### 问题描述

**问题**:
- Card组件不支持`as`属性
- 导致`Card as={Link}`语法无法正常工作
- 影响Dashboard页面的快速操作卡片和最近游戏列表点击导航

**根本原因**:
- Card组件硬编码渲染为`div`元素
- 缺少多态渲染（Polymorphic Rendering）能力
- 无法将Card渲染为Link、button等其他HTML元素

**影响范围**:
- Dashboard快速操作卡片（4个卡片）
- Dashboard最近游戏列表
- 其他可能使用`Card as={Link}`的页面

### 修复方案

**实现方式**: 添加`as`属性支持多态渲染

```jsx
// 修复前
export const Card = React.forwardRef(({
  variant = 'default',
  padding = 'md',
  hover = false,
  className = '',
  children,
  ...props
}, ref) => {
  return (
    <div  // ❌ 硬编码为div
      ref={ref}
      className={`card card-${variant} card-padding-${padding} ${hover ? 'card-hover' : ''} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});

// 修复后
export const Card = React.forwardRef(({
  as: Component = 'div',  // ✅ 支持as属性，默认div
  variant = 'default',
  padding = 'md',
  hover = false,
  className = '',
  children,
  ...props
}, ref) => {
  return (
    <Component  // ✅ 动态渲染为指定元素
      ref={ref}
      className={`card card-${variant} card-padding-${padding} ${hover ? 'card-hover' : ''} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
});
```

### 使用示例

```jsx
// 渲染为Link（Dashboard使用场景）
import { Link } from 'react-router-dom';
import { Card } from '@shared/ui';

<Card as={Link} to="/games" variant="glass" hover>
  <h3>管理游戏</h3>
  <p>创建和管理游戏项目</p>
</Card>

// 渲染为button
<Card as="button" onClick={handleClick} variant="elevated">
  <span>点击我</span>
</Card>

// 默认渲染为div（向后兼容）
<Card variant="outlined">
  <h4>默认行为</h4>
  <p>仍然是div元素</p>
</Card>
```

### 技术细节

**类型定义**:
```typescript
type CardProps = {
  as?: React.ElementType;  // 支持的HTML元素类型
  variant?: 'default' | 'elevated' | 'outlined' | 'glass' | 'glass-dark';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  className?: string;
  children?: React.ReactNode;
  [key: string]: any;  // 其他HTML属性
}
```

**关键特性**:
- ✅ 向后兼容：默认行为不变（渲染为div）
- ✅ 灵活性：支持任意React元素类型
- ✅ 类型安全：所有HTML属性正确传递
- ✅ 样式保留：所有CSS类名正常应用

### 验证清单

- [x] Card组件支持as属性
- [x] JSDoc注释已更新
- [x] 向后兼容性保持
- [x] Dashboard快速操作卡片可点击
- [x] Dashboard最近游戏列表可点击

### 相关文件

- **组件文件**: `/frontend/src/shared/ui/Card.jsx`
- **样式文件**: `/frontend/src/shared/ui/Card.css`
- **使用页面**: `/frontend/src/analytics/pages/Dashboard.jsx`

---

## 记录维护

**规范**:
- 发现组件问题后及时记录
- 修复完成后更新状态
- 保留修复历史用于参考

**更新日志**:
- 2026-02-11: 初始创建，Card组件as属性问题
- 待更新：修复验证结果
