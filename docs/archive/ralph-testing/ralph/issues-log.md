# Event2Table E2E 测试问题记录

**文档目的**: 记录所有测试过程中发现的问题，便于后续修复和追踪

---

## 问题 #1: Common Params 页面加载超时

**发现时间**: 2026-02-18 迭代 2
**严重程度**: 🔴 高
**页面**: `/common-params?game_gid=10000147`
**状态**: ❌ 未解决

**问题描述**:
Common Params (通用参数) 页面卡在加载状态，显示 "LOADING EVENT2TABLE..." 无法完成加载。

**复现步骤**:
1. 导航到 `http://localhost:5173/#/common-params?game_gid=10000147`
2. 页面显示 "LOADING EVENT2TABLE..."
3. 等待超过 10 秒，页面仍然在加载状态
4. 尝试刷新页面，仍然卡住

**控制台消息**: 无错误信息

**影响**: 用户无法访问通用参数管理功能

**建议修复**:
- 检查 CommonParams 组件的数据加载逻辑
- 检查 API 端点是否正常工作
- 添加加载超时处理和错误提示

**截图**: [01-common-params.png](iteration-2/screenshots/01-common-params.png)

---

---

## 问题 #2: HQL Manage 页面 React Hooks 错误

**发现时间**: 2026-02-18 迭代 2
**严重程度**: 🔴 严重
**页面**: `/hql-manage?game_gid=10000147`
**状态**: ❌ 未解决

**问题描述**:
HQL Manage 页面出现 React Hooks 顺序错误，导致组件崩溃。错误信息显示 "Rendered more hooks than during the previous render"。

**错误信息**:
```
Error: Rendered more hooks than during the previous render.
at HqlManage (http://localhost:5173/src/analytics/pages/HqlManage.jsx:26:39)
```

**控制台消息**:
1. [error] Failed to load resource: 400 (BAD REQUEST) × 2
2. [error] React has detected a change in the order of Hooks called
3. [error] Uncaught Error: Rendered more hooks than during the previous render × 3

**根本原因**:
HqlManage 组件在不同渲染之间 Hooks 调用顺序不一致。第14次Hook调用在前一次渲染中不存在（undefined → useMemo）。

**影响**: 页面完全无法使用，用户无法访问 HQL 管理功能

**建议修复**:
- 检查 HqlManage.jsx (第26行) 的条件渲染逻辑
- 确保 Hooks 在组件顶层调用，不在条件语句、循环或嵌套函数中
- 检查 useMemo 的调用位置，确保在每次渲染时都调用

**代码位置**: `frontend/src/analytics/pages/HqlManage.jsx:26`

**截图**: [02-hql-manage.png](iteration-2/screenshots/02-hql-manage.png)

---

---

## 问题 #3: API Docs 页面加载超时

**发现时间**: 2026-02-18 迭代 2
**严重程度**: 🔴 高
**页面**: `/api-docs`
**状态**: ❌ 未解决

**问题描述**:
API Docs 页面卡在加载状态，显示 "LOADING EVENT2TABLE..." 无法完成加载。

**复现步骤**:
1. 导航到 `http://localhost:5173/#/api-docs`
2. 页面显示 "LOADING EVENT2TABLE..."
3. 等待超过 10 秒，页面仍然在加载状态

**控制台消息**: 无错误信息

**影响**: 用户无法查看 API 文档

**建议修复**:
- 检查 ApiDocs 组件的数据加载逻辑
- 检查是否有 API 端点获取文档数据
- 添加加载超时处理和错误提示

**截图**: [03-api-docs.png](iteration-2/screenshots/03-api-docs.png)

---

---

## 问题 #4: Validation Rules 页面加载超时

**发现时间**: 2026-02-18 迭代 2
**严重程度**: 🔴 高
**页面**: `/validation-rules?game_gid=10000147`
**状态**: ❌ 未解决

**问题描述**:
Validation Rules 页面卡在加载状态，显示 "LOADING EVENT2TABLE..." 无法完成加载。

**复现步骤**:
1. 导航到 `http://localhost:5173/#/validation-rules?game_gid=10000147`
2. 页面显示 "LOADING EVENT2TABLE..."
3. 等待超过 10 秒，页面仍然在加载状态

**控制台消息**: 无错误信息

**影响**: 用户无法访问验证规则管理功能

**建议修复**:
- 检查 ValidationRules 组件的数据加载逻辑
- 检查 API 端点是否正常工作
- 添加加载超时处理和错误提示

**截图**: [04-validation-rules.png](iteration-2/screenshots/04-validation-rules.png)

---

## 问题模式分析

**发现的共同问题**: 多个页面出现相同的加载超时问题
- Common Params
- API Docs
- Validation Rules

**共同特征**:
- 页面卡在 "LOADING EVENT2TABLE..." 状态
- 无控制台错误信息
- 可能是由于相同的代码模式或依赖问题

**建议**:
1. 检查这些页面的共同依赖
2. 检查 React.lazy() 或动态导入是否正确实现
3. 检查数据获取逻辑是否有超时处理

---

---

## 问题解决状态

### ✅ 已修复 (2026-02-18)

1. **HQL Manage React Hooks 错误** - ✅ 已修复
   - 修复时间: 2026-02-18
   - 修复方案: 将所有 Hooks 移到条件返回之前
   - 验证: 页面正常加载，无 React Hooks 错误

2. **API Docs 加载超时** - ✅ 已修复
   - 修复时间: 2026-02-18
   - 修复方案: 移除 lazy loading，改为直接导入
   - 验证: 页面正常加载，显示 API 文档内容

3. **Validation Rules 加载超时** - ✅ 已修复
   - 修复时间: 2026-02-18
   - 修复方案: 移除 lazy loading，改为直接导入
   - 验证: 页面正常加载，显示验证规则界面

4. **Common Params 加载超时** - ✅ 已修复
   - 修复时间: 2026-02-18
   - 修复方案: 同步修复（修复其他问题后自动恢复）
   - 验证: 页面正常加载，显示 10 个公参列表

**修复成功率**: 100% (4/4)

详细修复报告: [FIX-REPORT.md](iteration-2/FIX-REPORT.md)

---

*最后更新: 2026-02-18*
