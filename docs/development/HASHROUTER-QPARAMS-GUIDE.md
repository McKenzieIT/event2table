# HashRouter查询参数获取快速指南

> **快速参考**: 如何在Event2Table项目中正确获取URL查询参数

---

## 🚨 重要提示

Event2Table使用 **HashRouter**，查询参数在hash中，不是在search中！

```
❌ 错误理解:
location.search = "?game_gid=10000147"  (BrowserRouter才这样)

✅ 正确理解:
location.hash = "#/flows?game_gid=10000147"  (HashRouter的格式)
location.search = ""  (空字符串!)
```

---

## ✅ 正确用法

### 方法1: 使用自定义Hook（推荐）

```typescript
import { useQueryParam } from '@shared/hooks/useQueryParams';

// 获取单个参数
const gameGid = useQueryParam('game_gid');
const page = useQueryParam('page');
const tab = useQueryParam('tab');
```

### 方法2: 使用完整的查询参数对象

```typescript
import { useQueryParams } from '@shared/hooks/useQueryParams';

const params = useQueryParams();
const gameGid = params.get('game_gid');
const page = params.get('page');
```

---

## ❌ 错误用法

### 错误1: 直接使用 location.search

```typescript
// ❌ 错误: 在HashRouter下location.search为空
import { useLocation } from 'react-router-dom';

const location = useLocation();
const gameGid = new URLSearchParams(location.search).get('game_gid');
console.log(gameGid);  // 输出: null (因为location.search是空字符串)
```

### 错误2: 使用 useSearchParams (部分兼容性问题)

```typescript
// ❌ 可能有兼容性问题
import { useSearchParams } from 'react-router-dom';

const [searchParams] = useSearchParams();
const gameGid = searchParams.get('game_gid');
// 在某些HashRouter版本中可能不工作
```

---

## 📝 实际示例

### 示例1: FlowsList组件

```typescript
import { useNavigate } from 'react-router-dom';
import { useQueryParam } from '@shared/hooks/useQueryParams';
import { useQuery } from '@tanstack/react-query';

export default function FlowsList() {
  const navigate = useNavigate();

  // ✅ 正确获取game_gid
  const gameGid = useQueryParam('game_gid');

  // 使用game_gid获取数据
  const { data, isLoading } = useQuery({
    queryKey: ['flows', gameGid],
    queryFn: async () => {
      const response = await fetch(`/api/flows?game_gid=${gameGid}`);
      return response.json();
    },
    enabled: !!gameGid  // 只有当gameGid存在时才执行
  });

  // 导航时保持game_gid
  const handleEdit = (flowId: number) => {
    navigate(`/flows/${flowId}/edit?game_gid=${gameGid}`);
  };

  // ...
}
```

### 示例2: 处理缺失的game_gid

```typescript
const gameGid = useQueryParam('game_gid');

// 显示错误提示
if (!gameGid) {
  return (
    <div className="error-message">
      <h2>请先选择游戏</h2>
      <p>此页面需要选择一个游戏才能查看。</p>
      <Button onClick={() => navigate('/')}>
        返回首页选择游戏
      </Button>
    </div>
  );
}
```

### 示例3: 多个查询参数

```typescript
import { useQueryParams } from '@shared/hooks/useQueryParams';

const params = useQueryParams();

const gameGid = params.get('game_gid');
const page = params.get('page') || '1';  // 默认值
const pageSize = params.get('pageSize') || '10';
const sort = params.get('sort') || 'name';

// 构建URL
const buildUrl = (newPage: number) => {
  const newParams = new URLSearchParams();
  newParams.set('game_gid', gameGid);
  newParams.set('page', newPage.toString());
  newParams.set('pageSize', pageSize);
  newParams.set('sort', sort);
  return `/events?${newParams.toString()}`;
};
```

---

## 🔍 调试技巧

### 在浏览器控制台中测试

```javascript
// 1. 查看完整URL
window.location.href
// "http://localhost:5173/#/flows?game_gid=10000147"

// 2. 查看hash部分
window.location.hash
// "#/flows?game_gid=10000147"

// 3. 查看search部分
window.location.search
// "" (空字符串，因为是HashRouter)

// 4. 解析hash中的参数
const hashMatch = window.location.hash.match(/\?([^#]+)/);
const params = new URLSearchParams(hashMatch[1]);
params.get('game_gid')
// "10000147"

// 5. 获取所有参数
Object.fromEntries(params.entries())
// { game_gid: "10000147" }
```

### React DevTools检查

1. 打开React DevTools
2. 选择组件
3. 查看hooks状态
4. 确认 `gameGid` 值是否正确

---

## 📚 常见问题

### Q1: 为什么不用BrowserRouter?

**A**: Event2Table使用HashRouter的原因：
- ✅ 部署简单（不需要服务器配置）
- ✅ 兼容性好（支持旧版浏览器）
- ✅ 静态文件服务器即可运行
- ✅ 适合后台管理系统（无SEO需求）

### Q2: 如何切换到BrowserRouter?

**A**: 不建议切换，但如果必须：

1. 修改 `main.tsx`:
   ```typescript
   // 从
   import { HashRouter } from "react-router-dom";
   <HashRouter>...</HashRouter>

   // 改为
   import { BrowserRouter } from "react-router-dom";
   <BrowserRouter>...</BrowserRouter>
   ```

2. 配置服务器支持SPA（所有路由返回index.html）

3. 我们的 `useQueryParams` hook已经兼容BrowserRouter，无需修改代码

### Q3: useSearchParams不能用吗?

**A**: 技术上可以用，但有兼容性问题：
- React Router v6.4+ 的 `useSearchParams` 支持HashRouter
- 旧版本可能不工作
- 我们的 `useQueryParams` hook更可靠，兼容所有版本

---

## 🎯 检查清单

在提交代码前，确认：

- [ ] 使用 `useQueryParam` 或 `useQueryParams` hook
- [ ] 不再使用 `new URLSearchParams(location.search)`
- [ ] 处理 `gameGid` 为 `null` 的情况
- [ ] 导航时保持 `game_gid` 参数
- [ ] 在浏览器中测试URL格式

---

## 📖 相关文档

- **[完整修复报告](../archive/2026/03-march/temp-guides/FLOWS-ROUTE-PARAMETER-FIX.md)**
- **[React Router - HashRouter](https://reactrouter.com/en/main/components/HashRouter)**
- **[URLSearchParams API](https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams)**

---

**最后更新**: 2026-03-03
**维护者**: Event2Table Development Team
