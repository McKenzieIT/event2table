# 重构检查清单

> **来源**: 整合了多个重构项目的经验
> **最后更新**: 2026-02-24
> **维护**: 每次重构项目后立即更新

---

## TDD重构流程 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CLAUDE.md](../../CLAUDE.md#tdd开发模式), [TESTING_LESSONS_LEARNED.md](../archive/2026-02/testing-reports/TESTING_LESSONS_LEARNED.md)

### TDD铁律

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

**Red-Green-Refactor循环**:
1. **Red** - 先写测试，看测试失败
2. **Green** - 编写最小代码使测试通过
3. **Refactor** - 重构优化，保持测试通过

### 重构前的准备

**1. 确保有测试覆盖**:
```bash
# 检查测试覆盖率
pytest backend/test/ --cov=backend --cov-report=html
npm run test:coverage
```

**2. 添加失败测试**:
```python
# 先写测试（应该失败）
def test_new_feature():
    result = calculate_something()
    assert result == expected_value  # ❌ 测试失败（功能未实现）

# 然后实现功能（测试通过）
def calculate_something():
    return expected_value  # ✅ 测试通过
```

### 重构步骤

**1. 小步重构**:
- ✅ 每次只重构一小部分
- ✅ 每次重构后运行测试
- ✅ 确保测试始终通过

**2. 提取方法**:
```python
# 重构前
def process_event(event):
    # 复杂逻辑
    if event['type'] == 'login':
        # ... 100行代码 ...
    elif event['type'] == 'logout':
        # ... 100行代码 ...

# 重构后
def process_event(event):
    if event['type'] == 'login':
        return process_login(event)
    elif event['type'] == 'logout':
        return process_logout(event)

def process_login(event):
    # 登录逻辑

def process_logout(event):
    # 登出逻辑
```

**3. 引入参数对象**:
```python
# 重构前
def create_event(name, game_gid, table_name, fields, conditions, mode):
    # 太多参数

# 重构后
@dataclass
class EventConfig:
    name: str
    game_gid: int
    table_name: str
    fields: List[Field]
    conditions: List[Condition]
    mode: str

def create_event(config: EventConfig):
    # 清晰的参数
```

### 重构验证

**验证清单**:
- [ ] 所有测试是否通过？
- [ ] 测试覆盖率是否保持？
- [ ] 功能是否等效？
- [ ] 性能是否改善或保持？

### 相关经验

- [测试指南 - TDD实践](./testing-guide.md#tdd实践) - TDD详细流程
- [API设计模式 - 分层架构](./api-design-patterns.md#分层架构) - 架构重构

---

## 代码审查清单 ⚠️ **P0极其重要**

**优先级**: P0 | **出现次数**: 多次 | **来源**: [CLAUDE.md](../../CLAUDE.md), [多个审查报告](../archive/2026-02/)

### React组件审查

- [ ] 所有Hooks都在组件最顶层调用？
- [ ] 没有任何Hook在条件语句、循环或嵌套函数中？
- [ ] 没有在Hooks调用之间进行条件返回？
- [ ] 每次渲染时Hooks的调用顺序相同？
- [ ] ESLint React Hooks规则已启用？
- [ ] 组件是否使用TypeScript类型注解？
- [ ] 是否有适当的性能优化（React.memo、useCallback）？

### Python代码审查

- [ ] 所有SQL查询是否使用 `game_gid` 而非 `game_id`？
- [ ] 所有SQL查询是否使用参数化查询？
- [ ] 所有动态SQL标识符是否使用SQLValidator验证？
- [ ] 是否使用Pydantic Schema验证输入？
- [ ] 错误处理是否适当（400/404/409/500）？
- [ ] 是否有完整的类型注解？
- [ ] 是否有完整的docstring？

### 安全审查

- [ ] 输入验证（必填字段、数据类型、长度限制）
- [ ] XSS防护（HTML转义用户输入）
- [ ] SQL注入防护（参数化查询）
- [ ] SQLValidator验证（动态标识符）
- [ ] 输出编码（JSON响应，不暴露内部信息）
- [ ] 错误处理（适当的HTTP状态码：400/404/409/500）

### 性能审查

- [ ] 是否有N+1查询？
- [ ] 是否可以使用JOIN合并多次查询？
- [ ] 是否可以合并统计查询？
- [ ] 缓存TTL是否合理（5-10分钟）？
- [ ] 修改数据的API是否清理缓存？
- [ ] 是否使用EXPLAIN QUERY PLAN分析慢查询？

### 测试审查

- [ ] 是否有单元测试？
- [ ] 是否有集成测试？
- [ ] 是否有E2E测试（关键路径）？
- [ ] 测试覆盖率是否达标（>80%）？
- [ ] 测试是否先于代码编写（TDD）？

### 违规后果

**必须拒绝的Code Review**:
- ❌ 使用game_id而非game_gid
- ❌ SQL注入风险（字符串拼接）
- ❌ XSS风险（未转义用户输入）
- ❌ 暴露堆栈跟踪
- ❌ React Hooks规则违反
- ❌ 缺少测试

### 相关经验

- [数据库模式 - game_gid迁移](./database-patterns.md#game_gid迁移) - game_gid使用规范
- [安全要点 - SQL注入防护](./security-essentials.md#sql注入防护) - SQL安全
- [React最佳实践 - Hooks规则](./react-best-practices.md#react-hooks-规则) - React规范

---

## Brainstorming系统化设计 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [E2E测试修复报告](../archive/2026-02/e2e-test-reports/iteration-2/)

### 何时使用Brainstorming

**适用场景**:
- ✅ 需要设计复杂功能的实现方案
- ✅ 需要探索多种解决方案
- ✅ 需要系统化地分析问题
- ❌ 简单显而易见的实现

### Brainstorming流程

**1. 理解问题**:
- 问题的本质是什么？
- 有哪些约束条件？
- 有哪些成功标准？

**2. 探索方案**:
- 列出2-3种可能的解决方案
- 分析每种方案的优缺点
- 评估每种方案的风险

**3. 选择最佳**:
- 基于分析结果选择方案
- 考虑长期维护性
- 考虑团队技能和经验

**4. 分段验证**:
- 先验证核心概念
- 再实现完整功能
- 最后优化性能

**5. 记录经验**:
- 记录为什么选择这个方案
- 记录遇到的问题和解决方法
- 更新相关文档

### 相关经验

- [调试技能 - Subagent并行分析法](./debugging-skills.md#subagent并行分析法) - 并行分析策略
- [API设计模式 - 分层架构](./api-design-patterns.md#分层架构) - 架构设计

---

## 技术债务管理 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [技术债务管理文档](../development/technical_debt_management.md)

### 识别技术债务

**常见技术债务**:
- ❌ 缺少测试
- ❌ 违反编码规范
- ❌ 过时的依赖
- ❌ 性能问题
- ❌ 安全漏洞
- ❌ 架构问题

### 优先级评估

**P0 - 立即处理**:
- 安全漏洞（SQL注入、XSS等）
- 数据损坏风险
- 严重的性能问题

**P1 - 尽快处理**:
- 缺少关键测试
- 违反核心规范（game_gid等）
- 架构问题

**P2 - 计划处理**:
- 代码风格不一致
- 过时的注释
- 小的优化机会

### 偿还技术债务

**策略**:
1. **记录债务** - 在代码中添加TODO注释
2. **评估影响** - 分析债务的影响范围
3. **制定计划** - 安排偿还优先级
4. **分步偿还** - 每次迭代偿还一部分
5. **验证清理** - 确保债务已完全偿还

---

## 技术债务管理流程 ⭐ **P1重要**

**优先级**: P1 | **出现次数**: 1次 | **来源**: [cache-cleanup-report.md](../../reports/2026-03-01/cache-cleanup-report.md)

### 核心原则

**系统化技术债务清理策略**

### 定期审计

**审计频率**: 每月

**审计内容**:
```bash
# 1. 检测未使用代码
vulture backend/ --min-confidence 70

# 2. 检测重复代码
jscpd backend/

# 3. 检测代码复杂度
radon cc backend/ -a

# 4. 检测类型问题
mypy backend/
```

### 债务分类

**按严重程度分类**:
- **P0** - 影响功能的债务（立即处理）
- **P1** - 影响性能的债务（本周处理）
- **P2** - 代码质量问题（本月处理）
- **P3** - 优化建议（有空处理）

### 清理优先级

**1. 先清理影响功能的债务**:
```python
# ❌ 错误：导入错误导致崩溃
from backend.services.events import EventService  # 文件不存在

# ✅ 正确：修复导入
from backend.services.events.event_service import EventService
```

**2. 再清理影响性能的债务**:
```python
# ❌ N+1查询
events = fetch_all_as_dict("SELECT * FROM log_events")
for event in events:
    game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (event['game_gid'],))

# ✅ 使用JOIN
events = fetch_all_as_dict('''
    SELECT le.*, g.name as game_name
    FROM log_events le
    INNER JOIN games g ON le.game_gid = g.gid
''')
```

**3. 最后清理代码质量问题**:
```python
# ❌ 未使用的导入
import os
import sys
from datetime import datetime  # 未使用

# ✅ 删除未使用的导入
from datetime import datetime
```

### 自动化清理

**使用工具自动清理**:
```bash
# 1. 自动删除未使用的导入
autoflake --remove-all-unused-imports --recursive backend/

# 2. 自动排序导入
isort backend/

# 3. 自动格式化代码
black backend/
```

### 代码审查清单

- [ ] 是否定期进行代码审计？
- [ ] 技术债务是否按优先级分类？
- [ ] 是否优先清理影响功能的债务？
- [ ] 是否使用自动化工具辅助清理？

### 案例文档

- [缓存清理报告](../../reports/2026-03-01/cache-cleanup-report.md)

---

## Canvas组件重构步骤（分离关注点） ⭐ (2026-03-04新增)

**优先级**: P0 | **出现次数**: 1次 | **来源**: [CANVAS-EVENT-NODES-FIX-GUIDE.md](../../reports/2026-03-03/CANVAS-EVENT-NODES-FIX-GUIDE.md)

### 分离关注点的重构策略

**问题背景**: Canvas和Event Nodes模块存在以下架构问题
- 路由配置混乱，URL直接访问失败
- API连接管理分散，错误处理不统一
- 组件职责不清，UI逻辑与业务逻辑混合
- 缺少统一的错误边界和加载状态

### 重构步骤

#### 第1步：路由层重构（URL访问基础）

**目标**: 确保所有Canvas相关页面可以通过URL直接访问

**重构前问题**:
```typescript
// ❌ 路由配置不完整
<Routes>
  <Route path="/event-node-builder" element={<EventNodeBuilder />} />
</Routes>

// ❌ 缺少Suspense包装
<Route path="/canvas" element={<Canvas />} />
```

**重构后方案**:
```typescript
// ✅ 完整的路由配置
const routes = (
  <BrowserRouter>
    <Routes>
      <Route
        path="/event-node-builder"
        element={
          <Suspense fallback={<GlobalLoading />}>
            <EventNodeBuilder />
          </Suspense>
        }
      />
      <Route
        path="/event-nodes"
        element={
          <Suspense fallback={<GlobalLoading />}>
            <EventNodesManagement />
          </Suspense>
        }
      />
      <Route
        path="/canvas"
        element={
          <Suspense fallback={<GlobalLoading />}>
            <Canvas />
          </Suspense>
        }
      />
    </Routes>
  </BrowserRouter>
)
```

#### 第2步：API层重构（数据访问层）

**目标**: 统一API调用管理，分离数据获取逻辑

**重构前问题**:
```typescript
// ❌ 组件内直接调用API
function EventNodeBuilder() {
  const [params, setParams] = useState([]);

  useEffect(() => {
    fetch(`/api/parameters?game_gid=${gameGid}`)
      .then(res => res.json())
      .then(data => setParams(data))
      .catch(error => console.error(error));
  }, []);
}
```

**重构后方案**:
```typescript
// ✅ 创建专门的API Service
import { apiService } from '@/shared/services/apiService';

class EventNodeService {
  async getParameters(gameGid) {
    return apiService.get('/api/parameters', { game_gid: gameGid });
  }

  async createNode(gameGid, nodeData) {
    return apiService.post('/api/event-nodes', { ...nodeData, game_gid: gameGid });
  }
}

// ✅ 组件使用Service
function EventNodeBuilder() {
  const [params, setParams] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadParameters = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await eventNodeService.getParameters(gameGid);
      setParams(data);
    } catch (err) {
      setError('加载参数失败');
    } finally {
      setLoading(false);
    }
  };
}
```

#### 第3步：组件层重构（UI组件分离）

**目标**: 分离可复用组件，提高代码复用性

**重构前问题**:
```typescript
// ❌ 所有逻辑都在一个组件中
function Canvas() {
  // 复杂的状态管理
  // 复杂的渲染逻辑
  // 复杂的事件处理
  // 硬编码的面包屑
  // 重复的错误处理
}
```

**重构后方案**:
```typescript
// ✅ 分离可复用组件
// 1. 面包屑组件
export function DynamicBreadcrumb({ path }) {
  const breadcrumbs = breadcrumbMap[path] || [];
  // ...
}

// 2. 游戏上下文组件
export function GameContextBar() {
  const gameGid = useGameGid();
  const gameInfo = useGameInfo(gameGid);
  // ...
}

// 3. 加载状态组件
export function CanvasLoading({ message }) {
  return (
    <div className="canvas-loading">
      <Spinner />
      <p>{message || '正在加载...'}</p>
    </div>
  );
}

// 4. 空状态组件
export function EmptyCanvasState() {
  return (
    <div className="empty-state">
      <div className="empty-icon">🎨</div>
      <h2>暂无画布配置</h2>
      <p>开始创建您的第一个事件节点</p>
      <button onClick={onCreateFirstNode}>
        创建事件节点
      </button>
    </div>
  );
}

// ✅ 简化的主组件
function Canvas() {
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);

  if (loading) return <CanvasLoading />;
  if (nodes.length === 0) return <EmptyCanvasState />;

  return (
    <div className="canvas">
      <DynamicBreadcrumb path="/canvas" />
      <GameContextBar />
      <CanvasNodes nodes={nodes} />
    </div>
  );
}
```

#### 第4步：错误处理重构（统一的错误边界）

**目标**: 建立统一的错误处理机制

**重构前问题**:
```typescript
// ❌ 分散的错误处理
try {
  // API调用
} catch (error) {
  console.error(error);
  alert('Error');
}
```

**重构后方案**:
```typescript
// ✅ 全局错误边界
export class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Canvas Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>出现错误</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            重新加载页面
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// ✅ 组件使用错误边界
function CanvasWithErrorBoundary() {
  return (
    <ErrorBoundary>
      <Canvas />
    </ErrorBoundary>
  );
}
```

### 前后端集成验证（4步验证）

**验证目标**: 确保重构后的系统正常工作

#### 步骤1：路由访问验证
```bash
# ✅ 所有Canvas相关URL必须可访问
curl -I http://localhost:5173/event-node-builder?game_gid=10000147
curl -I http://localhost:5173/event-nodes?game_gid=10000147
curl -I http://localhost:5173/canvas?game_gid=10000147

# 预期响应: HTTP 200
```

#### 步骤2：API连接验证
```bash
# ✅ 所有API端点正常响应
curl -s "http://127.0.0.1:5001/api/parameters?game_gid=10000147" | jq .
curl -s "http://127.0.0.1:5001/api/events?game_gid=10000147" | jq .
curl -s "http://127.0.0.1:5001/api/event-nodes?game_gid=10000147" | jq .

# 预期响应: 正常JSON数据
```

#### 步骤3：组件功能验证
```typescript
// ✅ 验证关键组件功能
describe('Canvas Components', () => {
  test('EventNodeBuilder loads parameters', async () => {
    render(<EventNodeBuilder />);
    expect(screen.getByText('正在加载...')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText('参数列表')).toBeInTheDocument();
    });
  });

  test('Canvas shows game context', () => {
    render(<Canvas />);
    expect(screen.getByText('当前游戏:')).toBeInTheDocument();
    expect(screen.getByText('10000147')).toBeInTheDocument();
  });
});
```

#### 步骤4：用户体验验证
```typescript
// ✅ 验证用户体验改进
test('Breadcrumbs show correct navigation', () => {
  render(<DynamicBreadcrumb path="/canvas" />);
  expect(screen.getByText('首页')).toBeInTheDocument();
  expect(screen.getByText('HQL画布')).toBeInTheDocument();
});

test('Game context bar shows game info', () => {
  render(<GameContextBar gameGid="10000147" />);
  expect(screen.getByText('GID: 10000147')).toBeInTheDocument();
});
```

### 重构收益

**架构改进**:
- ✅ **关注点分离**: 路由、API、UI、错误处理各司其职
- ✅ **代码复用**: 提取了4个可复用组件
- ✅ **错误统一**: 全局错误边界处理
- ✅ **类型安全**: TypeScript类型覆盖

**开发体验**:
- ✅ **组件化**: 组件职责明确，易于维护
- ✅ **可测试性**: 每个组件可独立测试
- ✅ **可扩展性**: 新功能可快速集成

**用户体验**:
- ✅ **响应式**: 加载状态和错误提示清晰
- ✅ **导航清晰**: 动态面包屑指引
- ✅ **上下文明确**: 游戏信息始终可见

### 重构检查清单

- [ ] 路由配置是否完整且支持参数？
- [ ] API服务是否抽象为独立层？
- [ ] 组件是否按功能分离？
- [ ] 错误处理是否统一？
- [ ] TypeScript类型是否完整？
- [ ] 所有功能是否正常工作？
- [ ] 性能是否得到优化？
- [ ] 是否更新了相关文档？

### 相关经验

- [测试指南 - TDD实践](./testing-guide.md#tdd实践) - 避免测试债务
- [代码审查清单](#代码审查清单) - 防止新债务产生
