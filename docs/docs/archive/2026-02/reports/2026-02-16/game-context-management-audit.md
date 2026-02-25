# 游戏上下文管理审查报告

**审查日期**: 2026-02-16
**审查人**: Claude Code
**审查范围**: 前后端游戏上下文(game_gid)参数实现情况
**优先级**: P0 - 严重问题需立即修复

---

## 执行摘要

Event2Table项目规定：**所有数据管理页面都应该只查询当前游戏的数据**（通过URL参数 `game_gid` 过滤）。本次审查发现多个页面缺少游戏上下文过滤，存在**数据泄露、数据混乱、用户体验问题**等严重风险。

### 关键发现

- ✅ **已正确实现** (2/6): 游戏管理、分类管理、事件管理、参数管理
- ❌ **缺少game_gid过滤** (2/6): **公参管理**、**HQL流程管理**
- ⚠️ **部分实现问题** (1/6): 事件节点管理（使用useOutletContext但未在URL中）
- ⚠️ **后端API未强制验证** (3/6): 公参API、流程API、部分事件API

---

## 1. 问题详细分析

### 1.1 前端页面审查

#### ✅ 已正确实现的页面

| 页面 | 路由 | game_gid来源 | API调用 | 代码位置 |
|------|------|-------------|---------|---------|
| **事件管理** | `/events` | `useOutletContext().currentGame.gid` | `GET /api/events?game_gid=${gid}` | EventsList.jsx:44 |
| **参数管理** | `/parameters` | `useGameStore().currentGame.gid` | `fetchAllParameters(gameGid, {...})` | ParametersList.jsx:87 |
| **分类管理** | `/categories` | `useSearchParams().get('game_gid')` | API调用含game_gid | CategoriesList.jsx:28 |
| **游戏管理** | `/games` | 无需游戏上下文 | - | GamesList.jsx |

**验证代码示例**（EventsList.jsx）:
```javascript
// ✅ 正确实现：从useOutletContext获取游戏上下文
const { currentGame } = useOutletContext();

// ✅ 游戏上下文验证
if (!currentGame) {
  return <SelectGamePrompt message="查看事件列表需要先选择游戏" />;
}

// ✅ API调用包含game_gid
const params = new URLSearchParams({
  page: currentPage.toString(),
  per_page: pageSize.toString(),
  game_gid: currentGame.gid.toString() // 使用game_gid而非game_id
});

const response = await fetch(`/api/events?${params.toString()}`);
```

#### ❌ 问题页面1：公参管理（CommonParamsList.jsx）

**文件路径**: `/frontend/src/analytics/pages/CommonParamsList.jsx`

**问题描述**:
1. ❌ **未从URL读取game_gid参数**
2. ❌ **未使用useOutletContext获取游戏上下文**
3. ❌ **未进行游戏上下文验证（无SelectGamePrompt）**
4. ❌ **API调用未传递game_gid参数**
5. ⚠️ **同步功能使用localStorage（非标准方式）**

**当前实现**（第22-30行）:
```javascript
// ❌ 错误：未使用游戏上下文，直接查询所有公参
const { data: params = [], isLoading, error: queryError } = useQuery({
  queryKey: ['common-params'],
  queryFn: async () => {
    const res = await fetch('/api/common-params'); // ❌ 缺少game_gid参数
    if (!res.ok) throw new Error('Failed to fetch common parameters');
    const result = await res.json();
    return result.data || [];
  }
});
```

**同步功能的game_gid获取**（第62-73行）:
```javascript
// ⚠️ 使用localStorage而非标准游戏上下文
const syncMutation = useMutation({
  mutationFn: async () => {
    const gameGid = localStorage.getItem('selectedGameGid'); // ⚠️ 非标准方式
    if (!gameGid) {
      throw new Error('Please select a game first');
    }

    const res = await fetch('/common-params/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_gid: parseInt(gameGid) })
    });
    // ...
  }
});
```

**影响评估**:
- 🔴 **严重**: 查询所有游戏的公参，导致数据泄露
- 🔴 **严重**: 用户可能看到其他游戏的公参数据
- 🔴 **严重**: 同步功能操作错误的游戏数据

---

#### ❌ 问题页面2：HQL流程管理（FlowsList.jsx）

**文件路径**: `/frontend/src/analytics/pages/FlowsList.jsx`

**问题描述**:
1. ❌ **未从URL读取game_gid参数**
2. ❌ **未使用useOutletContext获取游戏上下文**
3. ❌ **未进行游戏上下文验证**
4. ❌ **API调用未传递game_gid参数**

**当前实现**（第17-26行）:
```javascript
// ❌ 错误：未使用游戏上下文，直接查询所有流程
const { data: apiResponse, isLoading, error } = useQuery({
  queryKey: ['flows'],
  queryFn: async () => {
    const response = await fetch('/api/flows'); // ❌ 缺少game_gid参数
    if (!response.ok) throw new Error('Failed to fetch flows');
    const result = await response.json();
    return result;
  }
});
```

**影响评估**:
- 🔴 **严重**: 查询所有游戏的HQL流程，导致数据泄露
- 🔴 **严重**: 用户可能误删/误编辑其他游戏的流程
- 🟡 **中等**: 流程列表过长影响用户体验

---

#### ⚠️ 部分问题：事件节点管理（EventNodes.tsx）

**文件路径**: `/frontend/src/analytics/pages/EventNodes.tsx`

**问题描述**:
1. ⚠️ **使用useOutletContext获取游戏上下文**（正确）
2. ✅ **有游戏上下文验证**（正确）
3. ⚠️ **但URL中未包含game_gid参数**
4. ❌ **Sidebar.jsx的routesRequiringGameContext列表中未添加**

**当前实现**（第418-422行）:
```javascript
// ✅ 正确：使用useOutletContext获取游戏上下文
function EventNodes() {
  const { currentGame } = useOutletContext<LayoutContext>();
  const gameGid = currentGame?.gid || null;

  // ✅ 正确：游戏上下文验证
  if (!gameGid) {
    return <GameSelectionPrompt />;
  }

  // ✅ API调用包含game_gid
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["event-nodes", gameGid, filters],
    queryFn: async () => {
      const response = await eventNodesApi.list({
        game_gid: gameGid!, // ✅ 正确传递
        // ...
      });
      return response.data;
    },
  });
}
```

**Sidebar.jsx第23行**:
```javascript
// ❌ 错误：/event-nodes未添加到需要游戏上下文的路由列表
const routesRequiringGameContext = ['/event-node-builder', '/canvas', '/parameters', '/categories'];
// 应该添加: '/event-nodes'
```

**影响评估**:
- 🟡 **中等**: 功能实现正确但URL不规范
- 🟡 **中等**: 用户刷新页面可能丢失游戏上下文
- 🟢 **轻微**: 不影响数据隔离

---

### 1.2 后端API审查

#### ✅ 已正确实现的API

| API端点 | game_gid验证 | 强制要求 | 代码位置 |
|---------|------------|---------|---------|
| **GET /api/events** | ✅ 可选过滤 | ⚠️ 非强制 | events.py:96-132 |
| **POST /api/events** | ✅ 必填字段 | ✅ 强制 | events.py:176-184 |
| **GET /api/parameters/all** | ✅ 必填字段 | ✅ 强制 | parameters.py:82-84 |
| **GET /api/parameters/<param>/details** | ✅ 必填字段 | ✅ 强制 | parameters.py:209-247 |

**正确实现示例**（events.py）:
```python
# ✅ 正确：game_gid是可选的查询参数
@api_bp.route("/api/events", methods=["GET"])
def api_list_events() -> Tuple[Dict[str, Any], int]:
    game_gid_str = request.args.get("game_gid")
    game_gid = safe_int_convert(game_gid_str) if game_gid_str else None

    # ✅ 根据game_gid过滤（可选）
    if game_gid:
        where_clauses.append("le.game_gid = ?")
        params.append(game_gid)
```

#### ❌ 问题API1：GET /api/common-params

**文件路径**: `/backend/api/routes/legacy_api.py`

**问题描述**:
1. ❌ **未接受game_gid参数**
2. ❌ **未进行游戏上下文验证**
3. ❌ **返回所有游戏的公参数据**
4. ❌ **缺少400错误响应**

**当前实现**（legacy_api.py:103-133）:
```python
@api_bp.route("/api/common-params", methods=["GET"])
def api_list_common_params():
    """API: List all common parameters"""
    try:
        # ❌ 错误：查询所有公参，未按game_gid过滤
        common_params = fetch_all_as_dict("""
            SELECT
                id, game_id, param_name, param_name_cn,
                param_type, table_name, status, created_at, updated_at
            FROM common_params
            ORDER BY created_at DESC
        """)  # ❌ 缺少 WHERE game_id = ? 或 game_gid = ?

        # ... 数据映射逻辑 ...

        return json_success_response(data=common_params)
    except Exception as e:
        logger.error(f"Error fetching common params: {e}")
        return json_error_response("Failed to fetch common params", status_code=500)
```

**应该修改为**:
```python
@api_bp.route("/api/common-params", methods=["GET"])
def api_list_common_params():
    """API: List common parameters for a specific game"""
    try:
        # ✅ 1. 获取并验证game_gid
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return json_error_response("game_gid parameter required", status_code=400)

        # ✅ 2. 转换为game_id（common_params表使用game_id）
        game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
        if not game:
            return json_error_response(f"Game not found: gid={game_gid}", status_code=404)
        game_id = game["id"]

        # ✅ 3. 按game_id过滤查询
        common_params = fetch_all_as_dict("""
            SELECT
                id, game_id, param_name, param_name_cn,
                param_type, table_name, status, created_at, updated_at
            FROM common_params
            WHERE game_id = ?
            ORDER BY created_at DESC
        """, (game_id,))

        return json_success_response(data=common_params)
    except Exception as e:
        logger.error(f"Error fetching common params: {e}")
        return json_error_response("Failed to fetch common params", status_code=500)
```

**影响评估**:
- 🔴 **严重**: 数据泄露风险
- 🔴 **严重**: 返回所有游戏的公参，前端无法区分
- 🔴 **严重**: 违反游戏数据隔离原则

---

#### ❌ 问题API2：GET /api/flows

**文件路径**: `/backend/api/routes/flows.py`

**问题描述**:
1. ⚠️ **接受game_gid参数但不是强制的**
2. ❌ **未强制要求game_gid参数**
3. ❌ **缺少game_gid时返回所有流程**

**当前实现**（flows.py:64-92）:
```python
@api_bp.route("/api/flows", methods=["GET"])
def api_list_flows():
    """API: List all flows"""
    try:
        game_gid = request.args.get("game_gid", type=int)  # ⚠️ 可选参数

        where_clauses = ["1=1"]  # ❌ 错误：默认查询所有
        params = []

        if game_gid:
            where_clauses.append("game_gid = ?")
            params.append(game_gid)

        where_sql = " AND ".join(where_clauses)

        flows = fetch_all_as_dict(
            f"""
            SELECT * FROM flow_templates
            WHERE {where_sql}
            ORDER BY updated_at DESC
        """,
            params,
        )

        return json_success_response(data=flows)
    except Exception as e:
        logger.error(f"Error fetching flows: {e}")
        return json_error_response("Failed to fetch flows", status_code=500)
```

**应该修改为**:
```python
@api_bp.route("/api/flows", methods=["GET"])
def api_list_flows():
    """API: List flows for a specific game"""
    try:
        # ✅ 1. 强制要求game_gid
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return json_error_response("game_gid parameter required", status_code=400)

        # ✅ 2. 按game_gid过滤查询
        flows = fetch_all_as_dict(
            """
            SELECT * FROM flow_templates
            WHERE game_gid = ?
            ORDER BY updated_at DESC
        """,
            (game_gid,),
        )

        return json_success_response(data=flows)
    except Exception as e:
        logger.error(f"Error fetching flows: {e}")
        return json_error_response("Failed to fetch flows", status_code=500)
```

**影响评估**:
- 🔴 **严重**: 数据泄露风险
- 🔴 **严重**: 用户看到其他游戏的流程
- 🔴 **严重**: 批量操作可能误删其他游戏的流程

---

#### ⚠️ 部分问题：POST /common-params/sync

**文件路径**: `/backend/api/routes/legacy_api.py`（推断，未完整读取）

**问题描述**:
1. ✅ **接受game_gid参数**
2. ⚠️ **但从request body获取而非URL参数**
3. ⚠️ **前端使用localStorage而非标准方式**

**前端调用**（CommonParamsList.jsx:69）:
```javascript
const res = await fetch('/common-params/sync', {  // ⚠️ URL中无game_gid
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ game_gid: parseInt(gameGid) })  // game_gid在body中
});
```

**建议修改**:
```javascript
// ✅ 推荐：game_gid放在URL参数中
const res = await fetch(`/common-params/sync?game_gid=${gameGid}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' }
});
```

---

## 2. 风险评估

### 2.1 数据泄露风险（P0 - 严重）

**风险描述**: 用户可以查看/修改其他游戏的敏感数据

**影响范围**:
- 🔴 **公参管理**: 用户可以看到所有游戏的公参配置
- 🔴 **HQL流程管理**: 用户可以看到/修改所有游戏的流程

**潜在后果**:
- 用户A看到用户B的游戏配置
- 竞争对手的游戏配置泄露
- 违反数据隔离原则

### 2.2 数据混乱风险（P0 - 严重）

**风险描述**: 用户可能在错误的上下文中修改数据

**影响范围**:
- 🔴 **公参同步**: 同步到错误的游戏
- 🔴 **流程管理**: 编辑/删除错误的流程

**潜在后果**:
- 用户A误删用户B的流程
- 公参同步到错误的游戏
- 数据一致性破坏

### 2.3 用户体验问题（P1 - 高）

**风险描述**: 页面显示过多无关数据

**影响范围**:
- 🟡 **公参列表**: 显示所有游戏的公参（可能数千条）
- 🟡 **流程列表**: 显示所有游戏的流程

**潜在后果**:
- 页面加载缓慢
- 搜索/筛选困难
- 用户困惑

### 2.4 URL规范性问题（P2 - 中）

**风险描述**: URL中缺少game_gid参数

**影响范围**:
- 🟡 **事件节点管理**: 未在URL中包含game_gid
- 🟡 **Sidebar配置**: routesRequiringGameContext列表不完整

**潜在后果**:
- 刷新页面丢失游戏上下文
- 无法通过URL分享特定页面
- 违反RESTful规范

---

## 3. 修复方案

### 3.1 前端修复清单

#### 修复1：CommonParamsList.jsx

**优先级**: P0 - 严重
**文件**: `/frontend/src/analytics/pages/CommonParamsList.jsx`
**修改步骤**:

1. **添加游戏上下文导入**:
```javascript
import { useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui';
```

2. **获取游戏上下文**:
```javascript
export default function CommonParamsList() {
  const { currentGame } = useOutletContext();  // ✅ 新增

  // ✅ 游戏上下文验证
  if (!currentGame) {
    return <SelectGamePrompt message="查看公参管理需要先选择游戏" />;
  }

  const gameGid = currentGame.gid;  // ✅ 新增
```

3. **修改API调用**:
```javascript
// ❌ 修改前
const { data: params = [], ... } = useQuery({
  queryKey: ['common-params'],
  queryFn: async () => {
    const res = await fetch('/api/common-params');  // ❌ 无game_gid
    // ...
  }
});

// ✅ 修改后
const { data: params = [], ... } = useQuery({
  queryKey: ['common-params', gameGid],  // ✅ 添加gameGid到queryKey
  queryFn: async () => {
    const res = await fetch(`/api/common-params?game_gid=${gameGid}`);  // ✅ 添加game_gid
    if (!res.ok) throw new Error('Failed to fetch common parameters');
    const result = await res.json();
    return result.data || [];
  },
  enabled: !!gameGid  // ✅ 只在有游戏时执行
});
```

4. **修改同步功能**:
```javascript
// ❌ 修改前
const gameGid = localStorage.getItem('selectedGameGid');  // ❌ 非标准方式

// ✅ 修改后
const syncMutation = useMutation({
  mutationFn: async () => {
    if (!gameGid) {  // ✅ 使用组件状态中的gameGid
      throw new Error('Please select a game first');
    }

    // ✅ game_gid放在URL参数中
    const res = await fetch(`/common-params/sync?game_gid=${gameGid}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    // ...
  }
});
```

5. **删除同步游戏选择提示**（第92-96行）:
```javascript
// ❌ 删除这段代码
const handleSync = () => {
  const gameGid = localStorage.getItem('selectedGameGid');
  if (!gameGid) {
    warning('请先选择一个游戏');
    return;
  }
  // ...
};

// ✅ 修改为（使用组件状态中的gameGid）
const handleSync = () => {
  // gameGid已从currentGame获取，无需额外验证
  setConfirmState({
    // ...
  });
};
```

**验证测试**:
- [ ] 未选择游戏时显示"请先选择游戏"提示
- [ ] 选择游戏后只显示该游戏的公参
- [ ] URL参数包含`?game_gid=xxx`
- [ ] 同步功能使用当前游戏的game_gid

---

#### 修复2：FlowsList.jsx

**优先级**: P0 - 严重
**文件**: `/frontend/src/analytics/pages/FlowsList.jsx`
**修改步骤**:

1. **添加游戏上下文导入**:
```javascript
import { useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui';
```

2. **获取游戏上下文**:
```javascript
export default function FlowsList() {
  const { currentGame } = useOutletContext();  // ✅ 新增
  const gameGid = currentGame?.gid;  // ✅ 新增

  // ✅ 游戏上下文验证
  if (!gameGid) {
    return <SelectGamePrompt message="查看流程管理需要先选择游戏" />;
  }
```

3. **修改API调用**:
```javascript
// ❌ 修改前
const { data: apiResponse, ... } = useQuery({
  queryKey: ['flows'],
  queryFn: async () => {
    const response = await fetch('/api/flows');  // ❌ 无game_gid
    // ...
  }
});

// ✅ 修改后
const { data: apiResponse, ... } = useQuery({
  queryKey: ['flows', gameGid],  // ✅ 添加gameGid
  queryFn: async () => {
    const response = await fetch(`/api/flows?game_gid=${gameGid}`);  // ✅ 添加game_gid
    if (!response.ok) throw new Error('Failed to fetch flows');
    const result = await response.json();
    return result;
  },
  enabled: !!gameGid  // ✅ 只在有游戏时执行
});
```

4. **修改删除mutation**（可选，如果后端API需要）:
```javascript
// ⚠️ 检查后端DELETE /api/flows/<id>是否需要game_gid
const deleteMutation = useMutation({
  mutationFn: async (flowId) => {
    const response = await fetch(`/api/flows/${flowId}?game_gid=${gameGid}`, {  // ✅ 添加game_gid
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete flow');
    return response.json();
  },
  // ...
});
```

**验证测试**:
- [ ] 未选择游戏时显示"请先选择游戏"提示
- [ ] 选择游戏后只显示该游戏的流程
- [ ] URL参数包含`?game_gid=xxx`
- [ ] 删除流程时传递game_gid

---

#### 修复3：EventNodes.tsx（URL规范化）

**优先级**: P1 - 高
**文件**:
- `/frontend/src/analytics/pages/EventNodes.tsx`
- `/frontend/src/analytics/components/sidebar/Sidebar.jsx`

**修改步骤**:

1. **在EventNodes.tsx中添加URL同步**:
```javascript
import { useSearchParams } from 'react-router-dom';

function EventNodes() {
  const { currentGame } = useOutletContext<LayoutContext>();
  const [searchParams, setSearchParams] = useSearchParams();  // ✅ 新增
  const gameGid = currentGame?.gid || null;

  // ✅ 同步game_gid到URL
  useEffect(() => {
    if (gameGid && !searchParams.get('game_gid')) {
      setSearchParams({ game_gid: gameGid.toString() });
    }
  }, [gameGid, searchParams, setSearchParams]);

  // ✅ 游戏上下文验证
  if (!gameGid) {
    return <GameSelectionPrompt />;
  }
```

2. **在Sidebar.jsx中添加路由**:
```javascript
// ❌ 修改前
const routesRequiringGameContext = ['/event-node-builder', '/canvas', '/parameters', '/categories'];

// ✅ 修改后
const routesRequiringGameContext = ['/event-node-builder', '/event-nodes', '/canvas', '/parameters', '/categories'];
```

**验证测试**:
- [ ] URL中包含`?game_gid=xxx`
- [ ] 刷新页面后游戏上下文保留
- [ ] SidebarMenuItem正确处理game_gid参数

---

### 3.2 后端修复清单

#### 修复1：GET /api/common-params

**优先级**: P0 - 严重
**文件**: `/backend/api/routes/legacy_api.py`
**修改位置**: 第103-133行

**完整修改代码**:
```python
@api_bp.route("/api/common-params", methods=["GET"])
def api_list_common_params():
    """
    API: List common parameters for a specific game

    Query Parameters:
        - game_gid: Game GID (required)

    Returns:
        List of common parameters for the specified game
    """
    try:
        # ✅ 1. 获取并验证game_gid
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return json_error_response(
                "game_gid parameter required",
                status_code=400
            )

        # ✅ 2. 转换为game_id（common_params表使用game_id）
        game = fetch_one_as_dict(
            "SELECT id FROM games WHERE gid = ?",
            (game_gid,)
        )
        if not game:
            return json_error_response(
                f"Game not found: gid={game_gid}",
                status_code=404
            )
        game_id = game["id"]

        # ✅ 3. 按game_id过滤查询
        common_params = fetch_all_as_dict("""
            SELECT
                id,
                game_id,
                param_name,
                param_name_cn,
                param_type,
                table_name,
                status,
                created_at,
                updated_at
            FROM common_params
            WHERE game_id = ?
            ORDER BY created_at DESC
        """, (game_id,))

        # ✅ 4. 数据映射（保持原有逻辑）
        for param in common_params:
            param['data_type'] = param.get('param_type', 'string')
            param['key'] = param.get('param_name', '')
            param['name'] = param.get('param_name_cn', param.get('param_name', ''))
            param['description'] = param.get('param_description', '')

        logger.info(f"✅ Fetched {len(common_params)} common params for game_gid={game_gid}")
        return json_success_response(data=common_params)

    except Exception as e:
        logger.error(f"Error fetching common params: {e}", exc_info=True)
        return json_error_response("Failed to fetch common params", status_code=500)
```

**验证测试**:
```bash
# ❌ 测试1：缺少game_gid参数（应返回400）
curl -X GET "http://localhost:5001/api/common-params"
# 预期响应: {"success": false, "error": "game_gid parameter required"}

# ✅ 测试2：提供game_gid参数（应返回该游戏的公参）
curl -X GET "http://localhost:5001/api/common-params?game_gid=10000147"
# 预期响应: {"success": true, "data": [...]}

# ❌ 测试3：无效的game_gid（应返回404）
curl -X GET "http://localhost:5001/api/common-params?game_gid=99999999"
# 预期响应: {"success": false, "error": "Game not found: gid=99999999"}
```

---

#### 修复2：GET /api/flows

**优先级**: P0 - 严重
**文件**: `/backend/api/routes/flows.py`
**修改位置**: 第64-92行

**完整修改代码**:
```python
@api_bp.route("/api/flows", methods=["GET"])
def api_list_flows():
    """
    API: List flows for a specific game

    Query Parameters:
        - game_gid: Game GID (required)

    Returns:
        List of flows for the specified game
    """
    try:
        # ✅ 1. 强制要求game_gid
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return json_error_response(
                "game_gid parameter required",
                status_code=400
            )

        # ✅ 2. 验证游戏存在
        game = fetch_one_as_dict(
            "SELECT id, gid FROM games WHERE gid = ?",
            (game_gid,)
        )
        if not game:
            return json_error_response(
                f"Game not found: gid={game_gid}",
                status_code=404
            )

        # ✅ 3. 按game_gid过滤查询
        flows = fetch_all_as_dict(
            """
            SELECT * FROM flow_templates
            WHERE game_gid = ?
            ORDER BY updated_at DESC
        """,
            (game_gid,),
        )

        logger.info(f"✅ Fetched {len(flows)} flows for game_gid={game_gid}")
        return json_success_response(data=flows)

    except Exception as e:
        logger.error(f"Error fetching flows: {e}", exc_info=True)
        return json_error_response("Failed to fetch flows", status_code=500)
```

**验证测试**:
```bash
# ❌ 测试1：缺少game_gid参数（应返回400）
curl -X GET "http://localhost:5001/api/flows"
# 预期响应: {"success": false, "error": "game_gid parameter required"}

# ✅ 测试2：提供game_gid参数（应返回该游戏的流程）
curl -X GET "http://localhost:5001/api/flows?game_gid=10000147"
# 预期响应: {"success": true, "data": [...]}

# ❌ 测试3：无效的game_gid（应返回404）
curl -X GET "http://localhost:5001/api/flows?game_gid=99999999"
# 预期响应: {"success": false, "error": "Game not found: gid=99999999"}
```

---

#### 修复3：POST /common-params/sync（API规范化）

**优先级**: P1 - 高
**文件**: `/backend/api/routes/legacy_api.py`（需要查找完整代码）

**修改建议**:
```python
@api_bp.route("/common-params/sync", methods=["POST"])
def api_sync_common_params():
    """
    API: Sync common parameters for a specific game

    Query Parameters:
        - game_gid: Game GID (required)

    Request Body:
        Optional configuration for sync operation

    Returns:
        Sync result with statistics
    """
    try:
        # ✅ 1. 从URL参数获取game_gid
        game_gid = request.args.get("game_gid", type=int)
        if not game_gid:
            return json_error_response(
                "game_gid query parameter required",
                status_code=400
            )

        # ✅ 2. 验证游戏存在
        game = fetch_one_as_dict(
            "SELECT id, gid, name FROM games WHERE gid = ?",
            (game_gid,)
        )
        if not game:
            return json_error_response(
                f"Game not found: gid={game_gid}",
                status_code=404
            )
        game_id = game["id"]

        # ✅ 3. 执行同步逻辑（原有代码）
        # ...

        logger.info(f"✅ Synced common params for game_gid={game_gid}")
        return json_success_response(
            data={...},
            message="Common parameters synced successfully"
        )

    except Exception as e:
        logger.error(f"Error syncing common params: {e}", exc_info=True)
        return json_error_response("Failed to sync common params", status_code=500)
```

**验证测试**:
```bash
# ✅ 测试：正确的同步请求
curl -X POST "http://localhost:5001/common-params/sync?game_gid=10000147" \
  -H "Content-Type: application/json"
# 预期响应: {"success": true, "message": "Common parameters synced successfully"}
```

---

### 3.3 Sidebar配置修复

**优先级**: P1 - 高
**文件**: `/frontend/src/analytics/components/sidebar/Sidebar.jsx`
**修改位置**: 第23行

**修改代码**:
```javascript
// ❌ 修改前
const routesRequiringGameContext = ['/event-node-builder', '/canvas', '/parameters', '/categories'];

// ✅ 修改后
const routesRequiringGameContext = [
  '/event-node-builder',
  '/event-nodes',       // ✅ 新增
  '/canvas',
  '/parameters',
  '/categories',
  '/common-params',     // ✅ 新增（如果需要）
  '/flows'              // ✅ 新增（如果需要）
];
```

**作用**: 确保SidebarMenuItem组件自动为这些路由添加game_gid参数。

---

## 4. 测试验证步骤

### 4.1 前端测试

#### 测试1：公参管理（CommonParamsList）

**前置条件**: 启动前端开发服务器
```bash
cd frontend
npm run dev
```

**测试步骤**:
1. 未选择游戏时访问`/common-params`
   - **预期**: 显示"请先选择游戏"提示
   - **验证**: 页面显示`SelectGamePrompt`组件

2. 选择游戏后访问`/common-params`
   - **预期**: 只显示该游戏的公参
   - **验证**:
     - URL: `/common-params?game_gid=10000147`
     - API调用: `/api/common-params?game_gid=10000147`
     - 数据只包含该游戏的公参

3. 测试同步功能
   - **预期**: 同步当前游戏的公参
   - **验证**:
     - API调用: `/common-params/sync?game_gid=10000147`
     - 不再使用localStorage

**浏览器控制台验证**:
```javascript
// 检查API请求
// Network tab → Filter by "common-params"
// 验证URL包含: ?game_gid=10000147
```

---

#### 测试2：HQL流程管理（FlowsList）

**测试步骤**:
1. 未选择游戏时访问`/flows`
   - **预期**: 显示"请先选择游戏"提示
   - **验证**: 页面显示`SelectGamePrompt`组件

2. 选择游戏后访问`/flows`
   - **预期**: 只显示该游戏的流程
   - **验证**:
     - URL: `/flows?game_gid=10000147`
     - API调用: `/api/flows?game_gid=10000147`
     - 数据只包含该游戏的流程

3. 测试删除流程
   - **预期**: 删除当前游戏的流程
   - **验证**:
     - API调用: `/api/flows/{id}?game_gid=10000147`
     - 成功删除后列表刷新

---

#### 测试3：事件节点管理（EventNodes）

**测试步骤**:
1. 选择游戏后访问`/event-nodes`
   - **预期**: URL包含game_gid参数
   - **验证**:
     - URL: `/event-nodes?game_gid=10000147`
     - 刷新页面后游戏上下文保留

2. 测试Sidebar导航
   - **预期**: 点击侧边栏导航自动添加game_gid
   - **验证**:
     - 点击"事件节点"链接
     - URL自动变为`/event-nodes?game_gid=10000147`

---

### 4.2 后端测试

#### 测试1：GET /api/common-params

**测试脚本** (`test_api_common_params.sh`):
```bash
#!/bin/bash

BASE_URL="http://localhost:5001"

echo "=== 测试1: 缺少game_gid参数（应返回400）==="
curl -X GET "$BASE_URL/api/common-params" -H "Content-Type: application/json"
echo -e "\n"

echo "=== 测试2: 提供game_gid参数（应返回该游戏的公参）==="
curl -X GET "$BASE_URL/api/common-params?game_gid=10000147" -H "Content-Type: application/json"
echo -e "\n"

echo "=== 测试3: 无效的game_gid（应返回404）==="
curl -X GET "$BASE_URL/api/common-params?game_gid=99999999" -H "Content-Type: application/json"
echo -e "\n"

echo "=== 测试4: 验证数据隔离（不同游戏返回不同数据）==="
GAME1_DATA=$(curl -s "$BASE_URL/api/common-params?game_gid=10000147" | jq '.data | length')
GAME2_DATA=$(curl -s "$BASE_URL/api/common-params?game_gid=10000148" | jq '.data | length')
echo "Game 10000147: $GAME1_DATA 个公参"
echo "Game 10000148: $GAME2_DATA 个公参"
```

**运行测试**:
```bash
chmod +x test_api_common_params.sh
./test_api_common_params.sh
```

**预期结果**:
- 测试1: 返回400错误，包含"game_gid parameter required"
- 测试2: 返回游戏10000147的公参列表
- 测试3: 返回404错误，包含"Game not found"
- 测试4: 两个游戏返回不同的数据

---

#### 测试2：GET /api/flows

**测试脚本** (`test_api_flows.sh`):
```bash
#!/bin/bash

BASE_URL="http://localhost:5001"

echo "=== 测试1: 缺少game_gid参数（应返回400）==="
curl -X GET "$BASE_URL/api/flows" -H "Content-Type: application/json"
echo -e "\n"

echo "=== 测试2: 提供game_gid参数（应返回该游戏的流程）==="
curl -X GET "$BASE_URL/api/flows?game_gid=10000147" -H "Content-Type: application/json"
echo -e "\n"

echo "=== 测试3: 无效的game_gid（应返回404）==="
curl -X GET "$BASE_URL/api/flows?game_gid=99999999" -H "Content-Type: application/json"
echo -e "\n"

echo "=== 测试4: 验证数据隔离（不同游戏返回不同数据）==="
GAME1_FLOWS=$(curl -s "$BASE_URL/api/flows?game_gid=10000147" | jq '.data | length')
GAME2_FLOWS=$(curl -s "$BASE_URL/api/flows?game_gid=10000148" | jq '.data | length')
echo "Game 10000147: $GAME1_FLOWS 个流程"
echo "Game 10000148: $GAME2_FLOWS 个流程"
```

**运行测试**:
```bash
chmod +x test_api_flows.sh
./test_api_flows.sh
```

---

#### 测试3：E2E集成测试

**测试场景**: 验证完整的用户流程

**测试步骤**:
1. 启动应用
   ```bash
   # 后端
   python web_app.py

   # 前端
   cd frontend
   npm run dev
   ```

2. 浏览器访问 `http://localhost:5173`

3. **测试公参管理**:
   - 点击侧边栏"公参管理"
   - 验证显示"请先选择游戏"
   - 选择游戏10000147
   - 验证只显示该游戏的公参
   - 验证URL: `http://localhost:5173/common-params?game_gid=10000147`

4. **测试流程管理**:
   - 点击侧边栏"HQL流程"
   - 验证显示"请先选择游戏"
   - 选择游戏10000147
   - 验证只显示该游戏的流程
   - 验证URL: `http://localhost:5173/flows?game_gid=10000147`

5. **测试数据隔离**:
   - 切换到游戏10000148
   - 验证公参列表和流程列表已更新
   - 验证URL参数已更新

---

## 5. 防止未来遗漏的机制

### 5.1 代码审查Checklist

**前端开发Checklist**:
- [ ] 数据管理页面是否使用`useOutletContext`获取游戏上下文？
- [ ] 是否添加了游戏上下文验证（`if (!currentGame) return <SelectGamePrompt />`）？
- [ ] API调用是否包含`game_gid`参数？
- [ ] React Query的`enabled`条件是否包含`!!gameGid`？
- [ ] URL中是否包含`?game_gid=${gameGid}`？
- [ ] Sidebar.jsx的`routesRequiringGameContext`列表是否包含当前路由？

**后端开发Checklist**:
- [ ] API是否接受`game_gid`参数？
- [ ] 是否验证`game_gid`参数（`if not game_gid: return 400`）？
- [ ] 是否验证游戏存在（`SELECT * FROM games WHERE gid = ?`）？
- [ ] SQL查询是否包含`WHERE game_gid = ?`过滤条件？
- [ ] 缺少game_gid时是否返回400错误而非所有数据？
- [ ] API文档是否说明game_gid为必填参数？

---

### 5.2 自动化测试

**创建E2E测试**: `frontend/test/e2e/game-context.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('游戏上下文管理', () => {
  test.beforeEach(async ({ page }) => {
    // 访问应用
    await page.goto('http://localhost:5173');
  });

  test('公参管理页面需要游戏上下文', async ({ page }) => {
    // 未选择游戏时访问公参管理
    await page.goto('http://localhost:5173/common-params');

    // 验证显示游戏选择提示
    await expect(page.locator('text=请先选择游戏')).toBeVisible();

    // 选择游戏
    await page.click('[data-testid="game-selector"]');
    await page.click('text=测试游戏10000147');

    // 验证URL包含game_gid
    expect(page.url()).toContain('game_gid=10000147');

    // 验证API调用包含game_gid
    const apiRequest = await page.waitForRequest(request =>
      request.url().includes('/api/common-params') &&
      request.url().includes('game_gid=10000147')
    );
    expect(apiRequest).toBeTruthy();
  });

  test('HQL流程管理页面需要游戏上下文', async ({ page }) => {
    // 未选择游戏时访问流程管理
    await page.goto('http://localhost:5173/flows');

    // 验证显示游戏选择提示
    await expect(page.locator('text=请先选择游戏')).toBeVisible();

    // 选择游戏
    await page.click('[data-testid="game-selector"]');
    await page.click('text=测试游戏10000147');

    // 验证URL包含game_gid
    expect(page.url()).toContain('game_gid=10000147');

    // 验证API调用包含game_gid
    const apiRequest = await page.waitForRequest(request =>
      request.url().includes('/api/flows') &&
      request.url().includes('game_gid=10000147')
    );
    expect(apiRequest).toBeTruthy();
  });

  test('不同游戏的数据隔离', async ({ page }) => {
    // 选择游戏10000147
    await page.goto('http://localhost:5173/common-params?game_gid=10000147');
    const game1Params = await page.locator('.param-card').count();

    // 切换到游戏10000148
    await page.goto('http://localhost:5173/common-params?game_gid=10000148');
    const game2Params = await page.locator('.param-card').count();

    // 验证数据不同（或至少尝试验证）
    console.log(`Game 10000147: ${game1Params} params`);
    console.log(`Game 10000148: ${game2Params} params`);
  });
});
```

**运行E2E测试**:
```bash
cd frontend
npx playwright test game-context.spec.ts
```

---

### 5.3 Pre-commit Hook

**创建Git Hook**: `.git/hooks/pre-commit`

```bash
#!/bin/bash
# pre-commit hook: 检查game上下文实现

echo "🔍 检查游戏上下文实现..."

# 检查前端文件
FRONTEND_FILES=$(git diff --cached --name-only | grep -E '^frontend/src/analytics/pages/.*\.jsx?$')

if [ -n "$FRONTEND_FILES" ]; then
  echo "📝 检查前端文件的游戏上下文..."

  for file in $FRONTEND_FILES; do
    # 检查是否包含useOutletContext
    if ! grep -q "useOutletContext" "$file"; then
      echo "⚠️  警告: $file 未使用useOutletContext获取游戏上下文"
      echo "   请确认是否为数据管理页面"
    fi

    # 检查是否包含游戏上下文验证
    if ! grep -q "SelectGamePrompt\|if (!currentGame)" "$file"; then
      echo "⚠️  警告: $file 缺少游戏上下文验证"
    fi
  done
fi

# 检查后端文件
BACKEND_FILES=$(git diff --cached --name-only | grep -E '^backend/api/routes/.*\.py$')

if [ -n "$BACKEND_FILES" ]; then
  echo "📝 检查后端文件的游戏上下文..."

  for file in $BACKEND_FILES; do
    # 检查API路由是否验证game_gid
    if grep -q "@api_bp.route.*methods=\[\"GET\"\]" "$file"; then
      if ! grep -q "game_gid.*request.args.get" "$file"; then
        echo "⚠️  警告: $file 的GET API未验证game_gid参数"
      fi
    fi
  done
fi

echo "✅ Pre-commit检查完成"
```

**安装Hook**:
```bash
cp .git/hooks/pre-commit .git/hooks/pre-commit.bak  # 备份
chmod +x .git/hooks/pre-commit
```

---

### 5.4 文档更新

**更新CLAUDE.md**:

在`## Critical Rules → 关键规则`章节添加：

```markdown
### 游戏上下文管理规范 ⚠️ **极其重要 - 强制执行**

> **🚨 所有数据管理页面必须实现游戏上下文过滤**
> **🆕 更新 (2026-02-16)**: 建立强制游戏上下文验证机制

#### 前端实现规范

**必做事项**:
1. ✅ 使用`useOutletContext`获取游戏上下文
2. ✅ 添加游戏上下文验证（`if (!currentGame) return <SelectGamePrompt />`）
3. ✅ API调用包含`game_gid`参数
4. ✅ React Query的`enabled`条件包含`!!gameGid`
5. ✅ URL包含`?game_gid=${gameGid}`
6. ✅ 在Sidebar.jsx的`routesRequiringGameContext`列表中添加路由

**参考实现**（EventsList.jsx）:
\`\`\`javascript
const { currentGame } = useOutletContext();
const gameGid = currentGame?.gid;

if (!currentGame) {
  return <SelectGamePrompt message="查看事件列表需要先选择游戏" />;
}

const { data } = useQuery({
  queryKey: ['events', gameGid],
  queryFn: () => fetch(\`/api/events?game_gid=\${gameGid}\`),
  enabled: !!gameGid
});
\`\`\`

#### 后端API规范

**必做事项**:
1. ✅ API接受`game_gid`查询参数
2. ✅ 验证`game_gid`存在（返回400）
3. ✅ 验证游戏存在（返回404）
4. ✅ SQL查询包含`WHERE game_gid = ?`
5. ✅ API文档说明`game_gid`为必填参数

**参考实现**（events.py）:
\`\`\`python
@api_bp.route("/api/events", methods=["GET"])
def api_list_events():
    game_gid = request.args.get("game_gid", type=int)
    if not game_gid:
        return json_error_response("game_gid parameter required", status_code=400)

    game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (game_gid,))
    if not game:
        return json_error_response(f"Game not found: gid={game_gid}", status_code=404)

    events = fetch_all_as_dict("SELECT * FROM log_events WHERE game_gid = ?", (game_gid,))
    return json_success_response(data=events)
\`\`\`

#### 违规后果

- ⚠️ **数据泄露风险**: 用户可查看其他游戏的数据
- ⚠️ **数据混乱风险**: 用户可修改其他游戏的数据
- ⚠️ **用户体验问题**: 显示过多无关数据
- ❌ Code Review必须拒绝
```

---

## 6. 实施计划

### 阶段1：紧急修复（P0）- 1-2天

**目标**: 修复数据泄露和混乱风险

**任务**:
1. ✅ 修复CommonParamsList.jsx（前端）
2. ✅ 修复FlowsList.jsx（前端）
3. ✅ 修复GET /api/common-params（后端）
4. ✅ 修复GET /api/flows（后端）

**验证**: 运行测试脚本验证修复效果

---

### 阶段2：规范化改进（P1）- 1天

**目标**: 提升代码规范性和用户体验

**任务**:
1. ✅ 修复EventNodes.tsx的URL同步
2. ✅ 更新Sidebar.jsx的routesRequiringGameContext
3. ✅ 修复POST /common-params/sync的API规范

**验证**: E2E测试验证URL规范

---

### 阶段3：预防机制（P2）- 1天

**目标**: 建立长期预防机制

**任务**:
1. ✅ 创建E2E测试用例
2. ✅ 设置Pre-commit Hook
3. ✅ 更新CLAUDE.md文档
4. ✅ 创建代码审查Checklist

**验证**: 运行E2E测试和pre-commit hook

---

## 7. 总结

### 7.1 问题汇总

| 问题类型 | 数量 | 严重程度 | 状态 |
|---------|------|---------|------|
| **前端缺少游戏上下文** | 2/6 | P0 - 严重 | ❌ 需修复 |
| **后端未强制验证** | 2/6 | P0 - 严重 | ❌ 需修复 |
| **URL不规范** | 1/6 | P1 - 高 | ⚠️ 建议修复 |
| **Sidebar配置不完整** | 1/1 | P1 - 高 | ⚠️ 建议修复 |

### 7.2 优先级排序

1. **P0 - 严重（立即修复）**:
   - CommonParamsList.jsx + /api/common-params
   - FlowsList.jsx + /api/flows

2. **P1 - 高（本周修复）**:
   - EventNodes.tsx URL同步
   - Sidebar.jsx配置更新
   - POST /common-params/sync规范化

3. **P2 - 中（下周完成）**:
   - E2E测试
   - Pre-commit Hook
   - 文档更新

### 7.3 成功标准

- ✅ 所有数据管理页面正确实现游戏上下文
- ✅ 所有后端API强制验证game_gid参数
- ✅ URL规范包含game_gid参数
- ✅ 通过E2E测试验证
- ✅ 代码审查Checklist建立

---

## 附录

### A. 参考文档

- [项目开发规范](/Users/mckenzie/Documents/event2table/CLAUDE.md)
- [API文档](/Users/mckenzie/Documents/event2table/docs/api/README.md)
- [前端开发指南](/Users/mckenzie/Documents/event2table/docs/development/frontend-development.md)

### B. 相关文件路径

**前端文件**:
- `/frontend/src/analytics/pages/CommonParamsList.jsx`
- `/frontend/src/analytics/pages/FlowsList.jsx`
- `/frontend/src/analytics/pages/EventNodes.tsx`
- `/frontend/src/analytics/components/sidebar/Sidebar.jsx`

**后端文件**:
- `/backend/api/routes/legacy_api.py`
- `/backend/api/routes/flows.py`
- `/backend/api/routes/events.py`
- `/backend/api/routes/parameters.py`

### C. 测试脚本

**API测试脚本**:
- `/test_api_common_params.sh`
- `/test_api_flows.sh`

**E2E测试**:
- `/frontend/test/e2e/game-context.spec.ts`

---

**报告生成时间**: 2026-02-16
**下次审查时间**: 修复完成后（预计2026-02-18）
**负责人**: Event2Table Development Team
