# TypeScript CI/CD Type Checking Guide

> **版本**: 1.0.0 | **创建日期**: 2026-03-08
>
> **目的**: 在CI/CD流水线中添加严格的TypeScript类型检查，防止类型不匹配问题进入生产环境

---

## 概述

项目已配置GitHub Actions工作流，在每次push和pull request时自动运行以下检查：

1. **TypeScript Type Check** - 严格类型检查
2. **ESLint** - 代码规范检查
3. **Unit Tests** - 单元测试

---

## 配置文件

### 1. TypeScript配置 (`frontend/tsconfig.json`)

已启用的严格检查选项：

```json
{
  "compilerOptions": {
    "strict": true,                      // ✅ 启用完整严格模式
    "noImplicitAny": true,               // 禁止隐式any类型
    "strictNullChecks": true,            // 严格空值检查
    "strictFunctionTypes": true,         // 严格函数类型检查
    "strictBindCallApply": true,         // 严格的bind/call/apply检查
    "strictPropertyInitialization": true, // 严格的类属性初始化检查
    "noImplicitThis": true,              // 禁止隐式this类型
    "alwaysStrict": true,                // 始终使用严格模式
    "noFallthroughCasesInSwitch": true   // switch语句的fallthrough检查
  }
}
```

### 2. Package.json脚本 (`frontend/package.json`)

```json
{
  "scripts": {
    "type-check": "tsc --noEmit --pretty"
  }
}
```

### 3. GitHub Actions配置 (`.github/workflows/frontend-ci.yml`)

工作流包含三个独立的任务：

- **type-check**: 运行TypeScript类型检查
- **lint**: 运行ESLint检查
- **test**: 运行单元测试

---

## 本地使用

### 运行类型检查

在提交代码前，建议先在本地运行类型检查：

```bash
cd frontend
npm run type-check
```

### 运行完整CI检查

运行所有CI检查（类型检查 + ESLint + 单元测试）：

```bash
cd frontend
npm run type-check && npm run lint && npm run test:unit
```

---

## CI/CD触发条件

工作流在以下情况下自动运行：

### Push事件
- 推送到`main`分支
- 推送到`develop`分支
- 修改`frontend/`目录下的文件
- 修改`.github/workflows/frontend-ci.yml`文件

### Pull Request事件
- 目标分支为`main`或`develop`
- 修改`frontend/`目录下的文件

---

## 处理类型错误

### 常见类型错误

#### 1. 隐式any类型

```typescript
// ❌ 错误：参数类型隐式为any
function processData(data) {
  return data.map(item => item.value);
}

// ✅ 正确：显式指定类型
interface DataItem {
  value: number;
}

function processData(data: DataItem[]) {
  return data.map(item => item.value);
}
```

#### 2. 空值检查

```typescript
// ❌ 错误：可能为null的对象
function getName(user: User | null) {
  return user.name.toLowerCase(); // 可能在null上调用
}

// ✅ 正确：添加空值检查
function getName(user: User | null) {
  if (!user) return '';
  return user.name.toLowerCase();
}

// 或使用可选链
function getName(user: User | null) {
  return user?.name?.toLowerCase() ?? '';
}
```

#### 3. 函数类型不匹配

```typescript
// ❌ 错误：回调函数参数类型不匹配
function processItems(items: Item[], callback: (item: Item) => string) {
  items.forEach(callback);
}

processItems(items, (item: number) => item.toString()); // 类型错误

// ✅ 正确：匹配回调函数签名
processItems(items, (item: Item) => item.name);
```

### 修复类型错误的步骤

1. **查看CI日志**: GitHub Actions会显示具体的类型错误位置
2. **本地复现**: 运行`npm run type-check`在本地查看错误
3. **修复类型问题**:
   - 添加缺失的类型注解
   - 修复类型不匹配
   - 添加必要的空值检查
4. **验证修复**: 再次运行`npm run type-check`
5. **提交修复**: 推送代码，CI会自动重新运行

---

## 类型断言谨慎使用

### ⚠️ 避免过度使用类型断言

```typescript
// ❌ 不推荐：过度使用as
const data = response as any;

// ✅ 推荐：正确定义类型
interface ApiResponse {
  data: UserData;
}

const data = response as ApiResponse;
```

### 何时使用类型断言

仅在以下情况下使用`as`：

1. 从非类型化的API解析数据
2. 处理DOM元素（TypeScript无法推断类型）
3. 集成第三方库缺少类型定义

```typescript
// ✅ 合理使用场景1：API响应
const user = apiResponse.data as User;

// ✅ 合理使用场景2：DOM元素
const input = document.getElementById('my-input') as HTMLInputElement;

// ✅ 合理使用场景3：联合类型缩小
const value = get Value() as string | number;
```

---

## 类型定义最佳实践

### 1. 使用interface定义对象类型

```typescript
// ✅ 推荐：使用interface
interface User {
  id: number;
  name: string;
  email: string;
}

// ❌ 不推荐：使用type（除非需要联合类型）
type User = {
  id: number;
  name: string;
  email: string;
};
```

### 2. 导出类型定义

```typescript
// ✅ 在types目录统一管理类型
// src/types/user.ts
export interface User {
  id: number;
  name: string;
}

// 在其他文件中导入
import { User } from '@types/user';
```

### 3. 使用泛型增强类型复用

```typescript
// ✅ 使用泛型
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

const userResponse: ApiResponse<User> = await fetchUser();
const eventResponse: ApiResponse<Event> = await fetchEvent();
```

---

## 故障排除

### 问题1: CI通过但本地类型检查失败

**原因**: TypeScript版本不一致

**解决方案**:
```bash
cd frontend
npm install
npm run type-check
```

### 问题2: 第三方库类型错误

**原因**: 缺少类型定义或类型定义错误

**解决方案**:
```bash
# 安装类型定义包
npm install --save-dev @types/package-name

# 或使用declare module临时绕过
// src/types/global.d.ts
declare module 'some-untyped-package';
```

### 问题3: 路径别名解析错误

**原因**: `tsconfig.json`的paths配置与实际不匹配

**解决方案**: 确保`tsconfig.json`中的paths与`vite.config.ts`中的resolve.alias一致

```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@shared/*": ["./src/shared/*"]
    }
  }
}
```

---

## 监控和报告

### GitHub Actions状态

检查workflow运行状态：

1. 访问GitHub仓库
2. 点击"Actions"标签
3. 选择"Frontend CI"工作流
4. 查看最近的运行结果

### 类型检查报告

如果类型检查失败：

1. 点击失败的job
2. 展开"Run TypeScript type check"步骤
3. 查看详细的类型错误信息

### 修复后的验证

修复类型错误后：

1. 推送修复到分支
2. GitHub Actions会自动重新运行
3. 确认所有job都通过

---

## 相关文档

- [TypeScript官方文档](https://www.typescriptlang.org/docs/)
- [GitHub Actions文档](https://docs.github.com/en/actions)
- [项目开发规范](/Users/mckenzie/Documents/event2table/CLAUDE.md)
- [前端开发指南](/Users/mckenzie/Documents/event2table/docs/development/frontend-development.md)

---

## 变更历史

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-03-08 | 1.0.0 | 初始版本 - 添加TypeScript CI/CD配置 |
