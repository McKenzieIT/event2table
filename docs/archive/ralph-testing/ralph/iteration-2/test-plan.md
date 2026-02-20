# Event2Table E2E 测试计划 - 迭代 2

**测试时间**: 2026-02-18 (迭代 2)
**测试环境**:
- 前端: http://localhost:5173
- 后端: http://127.0.0.1:5001
- 测试游戏 GID: 10000147 (STAR001)

**测试工具**: Chrome DevTools MCP

## 迭代 2 目标

1. 测试迭代 1 中未测试的页面
2. 对已测试页面进行深度交互测试（每个按钮和功能）
3. 记录所有发现的问题
4. 验证表单提交和数据修改功能

## 迭代 2 测试范围

### 新页面测试 (剩余 10 个页面)

1. **Common Params** (通用参数) - `/common-params?game_gid=10000147`
2. **HQL Manage** (HQL管理) - `/hql-manage?game_gid=10000147`
3. **API Docs** (API文档) - `/api-docs`
4. **Validation Rules** (验证规则) - `/validation-rules?game_gid=10000147`
5. **Parameter Analysis** (参数分析) - `/parameter-analysis?game_gid=10000147`
6. **Parameter Compare** (参数对比) - `/parameters/compare?game_gid=10000147`
7. **Parameter Usage** (参数使用) - `/parameter-usage?game_gid=10000147`
8. **Parameter History** (参数历史) - `/parameter-history?game_gid=10000147`
9. **Parameter Dashboard** (参数仪表板) - `/parameter-dashboard?game_gid=10000147`
10. **Parameter Network** (参数网络) - `/parameter-network?game_gid=10000147`
11. **Logs Create** (创建日志) - `/logs/create?game_gid=10000147`
12. **Alter SQL** (SQL修改) - `/alter-sql/:paramId`
13. **Flow Builder** (流程构建器) - `/flow-builder?game_gid=10000147`

### 深度交互测试

对以下页面进行按钮级测试：
- Dashboard: 测试所有链接和按钮
- Games: 测试新增、编辑、删除、搜索功能
- Events: 测试筛选、搜索、排序功能
- Canvas: 测试添加节点、连接节点、生成HQL
- Event Node Builder: 测试选择事件、添加字段、配置WHERE条件

## 测试步骤

对于每个页面：
1. 导航到页面
2. 获取页面快照
3. **测试每个可点击元素**（按钮、链接、复选框等）
4. **测试表单填写**（输入框、下拉选择等）
5. 记录控制台错误
6. 截图记录关键步骤
7. 记录测试结果（✅ 成功 / ❌ 失败 / ⚠️ 警告）

## 测试结果记录

- ✅ 成功：功能正常工作
- ❌ 失败：功能不工作或有错误
- ⚠️ 警告：功能工作但有非阻塞性问题

## 测试开始时间
- 2026-02-18 迭代 2 开始

---

*此文档将在测试过程中持续更新*
