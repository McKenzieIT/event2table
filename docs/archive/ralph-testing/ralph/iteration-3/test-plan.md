# Event2Table E2E 测试计划 - 迭代 3

**测试时间**: 2026-02-18 (迭代 3)
**测试环境**:
- 前端: http://localhost:5173
- 后端: http://127.0.0.1:5001
- 测试游戏 GID: 10000147 (STAR001)

**测试工具**: Chrome DevTools MCP

## 迭代 3 目标

**基于前两次迭代的结果**：
- 迭代 1: 测试了 13 个核心页面，全部通过 ✅
- 迭代 2: 发现并修复了 4 个严重问题 ✅
- **迭代 3**: 继续测试剩余页面，完成全面覆盖

## 待测试页面清单

### 剩余未测试页面 (约 10 个)

1. **Parameter Analysis** (参数分析) - `/parameter-analysis?game_gid=10000147`
2. **Parameter Compare** (参数对比) - `/parameters/compare?game_gid=10000147`
3. **Parameter Usage** (参数使用) - `/parameter-usage?game_gid=10000147`
4. **Parameter History** (参数历史) - `/parameter-history?game_gid=10000147`
5. **Parameter Dashboard** (参数仪表板) - `/parameter-dashboard?game_gid=10000147`
6. **Parameter Network** (参数网络) - `/parameter-network?game_gid=10000147`
7. **Parameters Enhanced** (增强参数) - `/parameters/enhanced?game_gid=10000147`
8. **Logs Create** (创建日志) - `/logs/create?game_gid=10000147`
9. **Alter SQL** (SQL修改) - `/alter-sql/:paramId`
10. **Flow Builder** (流程构建器) - `/flow-builder?game_gid=10000147`
11. **HQL Results** (HQL结果) - `/hql-results?game_gid=10000147`

### 深度交互测试

对已测试的核心页面进行按钮级测试：
- **Games**: 测试新增、编辑、删除功能
- **Events**: 测试筛选、搜索、排序功能
- **Canvas**: 测试添加节点、连接节点、生成HQL
- **Event Node Builder**: 测试选择事件、添加字段、配置WHERE条件

## 测试策略

### 策略 A: 快速覆盖优先（推荐）
1. 快速浏览所有剩余页面
2. 截图并记录加载状态
3. 识别有问题的页面
4. 对问题页面进行详细分析

### 策略 B: 深度测试优先
1. 逐个页面进行深度测试
2. 测试每个按钮和功能
3. 记录所有发现的问题
4. 生成详细的测试报告

### 策略 C: 混合策略
1. 先快速扫描所有页面（策略 A）
2. 对关键页面进行深度测试（策略 B）
3. 平衡覆盖率和深度

## 成功标准

- ✅ 所有页面都能正常加载
- ✅ 无阻塞性错误
- ⚠️ 非阻塞性问题需要记录
- ❌ 发现的新问题需要详细记录

## 测试开始时间
- 2026-02-18 迭代 3 开始

---

*此文档将在测试过程中持续更新*
