# Event2Table E2E 测试计划 - 迭代 1

**测试时间**: 2026-02-18
**测试环境**:
- 前端: http://localhost:5173
- 后端: http://127.0.0.1:5001
- 测试游戏 GID: 10000147 (STAR001)

**测试工具**: Chrome DevTools MCP

## 测试范围

### 核心页面清单（共 20+ 个页面）

1. **Dashboard** (首页) - `/`
2. **Canvas** (画布) - `/canvas`
3. **Event Node Builder** (事件节点构建器) - `/event-node-builder`
4. **Games** (游戏管理) - `/games`
5. **Events** (事件管理) - `/events`
6. **Categories** (分类管理) - `/categories`
7. **Parameters** (参数管理) - `/parameters`
8. **Common Params** (通用参数) - `/common-params`
9. **HQL Manage** (HQL管理) - `/hql-manage`
10. **Flows** (流程) - `/flows`
11. **Import Events** (导入事件) - `/import-events`
12. **API Docs** (API文档) - `/api-docs`
13. **Batch Operations** (批量操作) - `/batch-operations`
14. **Validation Rules** (验证规则) - `/validation-rules`
15. **Parameter Analysis** (参数分析) - `/parameter-analysis`
16. **Parameter Compare** (参数对比) - `/parameters/compare`
17. **Parameter Usage** (参数使用) - `/parameter-usage`
18. **Parameter History** (参数历史) - `/parameter-history`
19. **Parameter Dashboard** (参数仪表板) - `/parameter-dashboard`
20. **Parameter Network** (参数网络) - `/parameter-network`
21. **Parameters Enhanced** (增强参数) - `/parameters/enhanced`
22. **Log Form** (日志创建) - `/logs/create`
23. **Log Detail** (日志详情) - `/log-detail`
24. **Generate** (生成器) - `/generate`
25. **Generate Result** (生成结果) - `/generate/result`
26. **Field Builder** (字段构建器) - `/field-builder`
27. **Event Nodes** (事件节点) - `/event-nodes`
28. **Alter SQL** (SQL修改) - `/alter-sql/:paramId`
29. **HQL Edit** (HQL编辑) - `/hql/:id/edit`
30. **Flow Builder** (流程构建器) - `/flow-builder`
31. **HQL Results** (HQL结果) - `/hql-results`

## 测试步骤

对于每个页面，执行以下操作：
1. 导航到页面
2. 获取页面快照
3. 检查控制台错误
4. 测试所有按钮和交互元素
5. 测试表单填写（如果有）
6. 截图记录关键步骤
7. 记录测试结果

## 测试结果记录

- ✅ 成功
- ❌ 失败（记录详细信息）
- ⚠️ 警告（部分功能正常）

## 测试开始时间
- 2026-02-18 开始

---

*此文档将在测试过程中持续更新*
