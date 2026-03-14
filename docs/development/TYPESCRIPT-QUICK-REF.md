# TypeScript Type Check Quick Reference

> **快速参考**: 本地运行类型检查，避免CI失败

---

## 本地命令

```bash
# 进入前端目录
cd frontend

# 运行类型检查
npm run type-check

# 运行所有CI检查（推荐在提交前运行）
npm run type-check && npm run lint && npm run test:unit
```

---

## 常见类型错误速查

### 错误1: Parameter 'xxx' implicitly has an 'any' type

```typescript
// ❌ 错误
function processData(data) {  // data隐式为any
  return data.map(item => item.value);
}

// ✅ 修复：添加类型
interface DataItem { value: number; }
function processData(data: DataItem[]) {
  return data.map(item => item.value);
}
```

### 错误2: Object is possibly 'null'

```typescript
// ❌ 错误
function getName(user: User | null) {
  return user.name.toLowerCase();  // user可能为null
}

// ✅ 修复1：可选链
function getName(user: User | null) {
  return user?.name?.toLowerCase() ?? '';
}

// ✅ 修复2：类型守卫
function getName(user: User | null) {
  if (!user) return '';
  return user.name.toLowerCase();
}
```

### 错误3: Property 'xxx' does not exist on type 'XXX'

```typescript
// ❌ 错误
const user = response.data;
console.log(user.name);  // TypeScript不知道response.data的类型

// ✅ 修复：定义接口
interface User { name: string; }
interface ApiResponse { data: User; }
const user = (response as ApiResponse).data;
console.log(user.name);
```

### 错误4: Type 'X' is not assignable to type 'Y'

```typescript
// ❌ 错误
function processItem(item: Item) { }
processItem(eventData);  // eventData不是Item类型

// ✅ 修复1：类型断言（如果确定类型兼容）
processItem(eventData as Item);

// ✅ 修复2：转换类型
function convertToItem(event: Event): Item {
  return { id: event.id, name: event.title };
}
processItem(convertToItem(eventData));
```

---

## 提交前检查清单

- [ ] 运行`npm run type-check`无错误
- [ ] 运行`npm run lint`无警告
- [ ] 运行`npm run test:unit`全部通过
- [ ] 新增代码有完整的类型定义
- [ ] 避免使用`any`类型
- [ ] 为复杂类型创建interface定义
- [ ] 正确处理null/undefined情况

---

## CI失败处理流程

1. **查看失败日志** → GitHub Actions → Frontend CI → type-check
2. **本地复现** → `npm run type-check`
3. **修复类型错误**
4. **验证修复** → `npm run type-check`
5. **推送代码** → CI自动重新运行

---

## 有用的TypeScript编译选项

```json
{
  "compilerOptions": {
    "strict": true,                    // 启用所有严格类型检查
    "noImplicitAny": true,             // 禁止隐式any
    "strictNullChecks": true,          // 严格null检查
    "noUnusedLocals": false,           // 未使用的局部变量（当前禁用）
    "noUnusedParameters": false,       // 未使用的参数（当前禁用）
    "noImplicitReturns": true,         // 函数所有路径必须有返回
    "noFallthroughCasesInSwitch": true // switch的fallthrough检查
  }
}
```

---

## 相关文档

- [完整TypeScript CI指南](./TYPESCRIPT-CI-GUIDE.md)
- [TypeScript官方文档](https://www.typescriptlang.org/docs/)
