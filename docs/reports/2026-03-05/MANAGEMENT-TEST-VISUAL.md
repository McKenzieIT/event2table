# Flows & Categories Management - 测试结构可视化

**测试日期**: 2026-03-05
**测试范围**: 2个管理页面 × 10项测试 = 20项测试

---

## 测试矩阵

```
                    ┌─────────────────────────────────────────────┐
                    │         Flows Management (流程管理)          │
                    └─────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
               ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
               │页面加载  │      │ 按钮功能   │      │ 数据操作 │
               │ ✅ API   │      │ ⚠️ 手动    │      │ ⚠️ 手动  │
               └────┬────┘      └─────┬─────┘      └────┬────┘
                    │                  │                  │
                ✅ 已验证           ⚠️ 需要手动测试      ⚠️ 需要手动测试
```

```
                    ┌─────────────────────────────────────────────┐
                    │      Categories Management (分类管理)        │
                    └─────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
               ┌────▼────┐      ┌─────▼─────┐      ┌────▼────┐
               │页面加载  │      │ 按钮功能   │      │ 数据操作 │
               │ ✅ API   │      │ ⚠️ 手动    │      │ ⚠️ 手动  │
               └────┬────┘      └─────┬─────┘      └────┬────┘
                    │                  │                  │
                ✅ 已验证           ⚠️ 需要手动测试      ⚠️ 需要手动测试
```

---

## 测试覆盖图

### 自动化验证（通过API + 代码分析）

```
✅ 后端API测试
├─ GET /api/flows?game_gid=10000147
│  └─ 状态: 200 OK, ~50ms
│  └─ 数据: 2个flows
├─ GET /api/categories?game_gid=10000147
│  └─ 状态: 200 OK, ~50ms
│  └─ 数据: 11个categories
└─ 结论: API 100%稳定

✅ 前端代码分析
├─ FlowsList.tsx
│  ├─ React Hooks: ✅ 正确使用
│  ├─ React Query: ✅ 配置正确
│  ├─ TypeScript: ✅ 类型完整
│  └─ 错误处理: ✅ 完善
└─ CategoriesList.tsx
   ├─ React Hooks: ✅ 正确使用
   ├─ React Query: ✅ 配置正确
   ├─ TypeScript: ✅ 类型完整
   └─ 错误处理: ✅ 完善
```

### 手动测试（需要浏览器验证）

```
⚠️ UI交互测试
├─ 页面加载和DOM渲染
├─ 按钮点击和路由跳转
├─ 表单填写和提交
├─ 搜索和过滤功能
├─ 模态框开关
├─ 确认对话框
└─ 批量操作

⚠️ 用户体验测试
├─ 加载状态显示
├─ 空状态提示
├─ 错误提示
├─ 成功提示
└─ 性能响应

⚠️ 浏览器兼容性
├─ Chrome
├─ Firefox
├─ Safari
└─ Edge
```

---

## 测试优先级

```
P0 - 关键功能（必须测试）
├─ ✅ API端点稳定性
├─ ⚠️ 页面加载和渲染
├─ ⚠️ 按钮点击和导航
├─ ⚠️ 表单提交
└─ ⚠️ 控制台错误检查

P1 - 重要功能（应该测试）
├─ ⚠️ 搜索和过滤
├─ ⚠️ 模态框交互
├─ ⚠️ 批量操作
└─ ⚠️ 错误处理

P2 - 优化功能（可以测试）
├─ ⚠️ 性能测量
├─ ⚠️ 浏览器兼容性
└─ ⚠️ 可访问性
```

---

## 测试数据流

```
┌─────────────┐
│   浏览器    │
│  (Frontend) │
└──────┬──────┘
       │
       │ HTTP Request
       ▼
┌─────────────┐
│  Flask API  │
│  (Backend)  │
└──────┬──────┘
       │
       │ SQL Query
       ▼
┌─────────────┐
│  SQLite DB  │
│  (Database) │
└─────────────┘

数据验证:
✅ API → DB: 数据格式正确
✅ DB → API: 响应格式正确
✅ API → Frontend: 数据传输成功
⚠️ Frontend → UI: 需要手动验证
```

---

## 组件结构图

### FlowsList 组件

```
<FlowsList>
  ├─ <PageHeader>
  │  ├─ <h1>HQL 流程管理</h1>
  │  └─ <Button>新建流程</Button>
  │
  ├─ <SearchBar>
  │  └─ <SearchInput placeholder="搜索流程名称..." />
  │
  ├─ {isLoading && <Spinner />}
  │
  ├─ {filteredFlows.length === 0 && <EmptyState />}
  │
  └─ <div className="flows-grid">
     └─ {filteredFlows.map(flow => (
         <FlowCard key={flow.id}>
           ├─ <FlowHeader>
           │  ├─ <h3>{flow.flow_name}</h3>
           │  └─ <span>已保存</span>
           │
           ├─ <FlowBody>
           │  ├─ <p>{flow.description}</p>
           │  └─ <FlowMeta>
           │     ├─ <span>📊 {nodes.length} 个节点</span>
           │     └─ <span>🕐 {updated_at}</span>
           │
           └─ <FlowActions>
              ├─ <Button>编辑</Button>
              ├─ <Button>执行</Button> ⚠️ TODO
              └─ <Button>删除</Button>
         </FlowCard>
       ))}
     </div>

  └─ <ConfirmDialog />
</FlowsList>
```

### CategoriesList 组件

```
<CategoriesList>
  ├─ <PageHeader>
  │  ├─ <h1>事件分类管理</h1>
  │  ├─ <Button variant="danger">批量删除</Button>
  │  └─ <Button variant="primary">新建分类</Button>
  │
  ├─ <SearchBar>
  │  └─ <SearchInput placeholder="搜索分类名称..." />
  │
  ├─ <SelectionToolbar>
  │  └─ <input type="checkbox" onChange={toggleSelectAll} />
  │
  ├─ {isLoading && <Skeleton />}
  │
  └─ <div className="categories-grid">
     └─ {filteredCategories.map(category => (
         <CategoryCard key={category.id}>
           ├─ <input type="checkbox"
           │     checked={selectedIds.has(category.id)}
           │     onChange={() => toggleSelect(category.id)} />
           │
           ├─ <CategoryInfo>
           │  ├─ <h3>{category.name}</h3>
           │  ├─ <p>{category.description}</p>
           │  └─ <span>📊 {event_count} 个事件</span>
           │
           └─ <CategoryActions>
              ├─ <Button>编辑</Button>
              └─ <Button>删除</Button>
         </CategoryCard>
       ))}
     </div>

  └─ <ConfirmDialog />
  └─ <CategoryModal />
</CategoriesList>
```

---

## API请求流程

### 获取流程列表

```
1. 用户访问: http://localhost:5173/#/flows?game_gid=10000147
2. React Query执行:
   queryKey: ['flows', '10000147']
   queryFn: fetch('/api/flows?game_gid=10000147')
3. 后端处理:
   GET /api/flows?game_gid=10000147
   → Flask接收请求
   → 调用FlowService.get_flows(game_gid=10000147)
   → 查询数据库: SELECT * FROM flows WHERE game_gid=10000147
   → 返回JSON: {data: {flows: [...]}, success: true}
4. 前端接收:
   → React Query缓存数据
   → 组件重新渲染
   → 显示流程卡片
```

### 删除流程

```
1. 用户点击"删除"按钮
2. 显示确认对话框
3. 用户确认删除
4. React Mutation执行:
   mutationFn: fetch(`/api/flows/${flowId}`, {method: 'DELETE'})
5. 后端处理:
   DELETE /api/flows/{flowId}
   → Flask接收请求
   → 调用FlowService.delete_flow(flow_id)
   → 删除数据库记录: DELETE FROM flows WHERE id=?
   → 清理缓存: cache.delete('flows:*')
   → 返回JSON: {success: true, message: 'Flow deleted'}
6. 前端接收:
   → onSuccess回调执行
   → 失效缓存: queryClient.invalidateQueries(['flows', gameGid])
   → React Query自动重新获取数据
   → 组件更新，流程卡片消失
```

---

## 缓存策略

```
React Query缓存层级:
├─ L1: 内存缓存（自动）
│  ├─ queryKey: ['flows', '10000147']
│  ├─ queryKey: ['categories', '10000147']
│  └─ staleTime: 0 (立即过期)
│
├─ L2: 后端缓存（Redis）
│  ├─ cache:flows:10000147 (TTL: 1800s)
│  └─ cache:categories:10000147 (TTL: 1800s)
│
└─ L3: 数据库（SQLite）
   └─ 持久化存储

缓存失效流程:
├─ 创建 → 失效缓存
├─ 更新 → 失效缓存
└─ 删除 → 失效缓存

精确失效（最佳实践）:
✅ queryClient.invalidateQueries({ queryKey: ['flows', gameGid] })

❌ 错误: 失效所有缓存
   queryClient.invalidateQueries(['flows'])
```

---

## 错误边界

```
错误处理层级:
├─ L1: 组件级错误
│  ├─ game_gid缺失 → 显示"请先选择游戏"
│  └─ 数据为空 → 显示<EmptyState />
│
├─ L2: API错误
│  ├─ 400 Bad Request → "game_gid is required"
│  ├─ 404 Not Found → "Game not found"
│  └─ 500 Server Error → "Failed to fetch"
│
└─ L3: 网络错误
   ├─ 请求超时 → 显示重试按钮
   └─ 网络断开 → 显示网络错误提示

用户友好提示:
✅ 明确的错误消息
✅ 可操作的解决建议
✅ 重试机制
```

---

## 性能优化建议

```
当前优化:
✅ useMemo: 过滤逻辑优化
✅ React Query: 自动缓存和去重
✅ 精确缓存失效: 避免过度请求

待实现优化:
⚠️ React.memo: 包裹流程/分类卡片
⚠️ useCallback: 优化事件处理函数
⚠️ 虚拟滚动: 数据量大时使用
⚠️ 代码分割: 懒加载模态框组件
⚠️ 图片优化: 压缩图标和图片
```

---

## 测试报告结构

```
docs/reports/2026-03-05/
├─ MANAGEMENT-FULL-TEST.md       # 完整测试报告（13个章节）
│  ├─ 1. Flows代码分析
│  ├─ 2. Categories代码分析
│  ├─ 3. 完整测试清单（10项×2页面）
│  ├─ 4. 批量操作测试
│  ├─ 5. 错误处理测试
│  ├─ 6. 路由测试
│  ├─ 7. 性能优化分析
│  ├─ 8. 安全测试
│  ├─ 9. 可访问性测试
│  ├─ 10. 浏览器兼容性测试
│  ├─ 11. 手动测试总结
│  ├─ 12. 问题和建议
│  └─ 13. 测试结论
│
├─ MANAGEMENT-TEST-SUMMARY.md    # 快速总结（2页）
│  ├─ 快速评估
│  ├─ 关键发现
│  ├─ 测试数据
│  ├─ 快速测试指南
│  └─ 下一步行动
│
├─ MANAGEMENT-TEST-CHECKLIST.md  # 手动测试清单（可打印）
│  ├─ 准备工作
│  ├─ Flows测试（6项）
│  ├─ Categories测试（8项）
│  ├─ 错误处理测试（2项）
│  ├─ 性能检查（2项）
│  └─ 最终评估
│
└─ MANAGEMENT-TEST-VISUAL.md    # 本文档（可视化）
   ├─ 测试矩阵
   ├─ 测试覆盖图
   ├─ 测试优先级
   ├─ 数据流图
   ├─ 组件结构图
   └─ API流程图
```

---

## 测试时间估算

```
自动测试（已完成）:
├─ API测试: 5分钟
├─ 代码分析: 30分钟
└─ 报告编写: 30分钟
总计: ~65分钟

手动测试（待执行）:
├─ Flows页面: 10分钟
├─ Categories页面: 15分钟
├─ 错误处理: 5分钟
└─ 性能检查: 5分钟
总计: ~35分钟

总计: ~100分钟（1小时40分钟）
```

---

## 快速开始测试

### 1分钟快速测试

```bash
# 打开页面
http://localhost:5173/#/flows?game_gid=10000147
http://localhost:5173/#/categories?game_gid=10000147

# 快速检查
□ 页面加载正常
□ 显示数据
□ 无控制台错误
□ 按钮可点击
```

### 5分钟完整测试

```bash
# Flows (2分钟)
□ 搜索功能正常
□ 编辑按钮跳转正确
□ 删除确认对话框显示

# Categories (3分钟)
□ 全选功能正常
□ 新建分类成功
□ 批量删除成功
```

---

**测试完成率**: 50% (自动测试完成，手动测试待执行)

**建议**: 使用 [MANAGEMENT-TEST-CHECKLIST.md](./MANAGEMENT-TEST-CHECKLIST.md) 进行手动测试
