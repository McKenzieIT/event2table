# 性能优化实施计划

**生成时间**: 2026-03-09 13:55:00
**优先级**: P0（关键性能问题）
**预计工作量**: 2-3 天
**预期提升**: 10-100倍性能改进

---

## 🎯 优化目标

| 指标 | 当前 | 目标 | 提升倍数 |
|------|------|------|----------|
| 核心查询响应时间 | 10-50ms | 0.1-0.5ms | **100x** |
| API P95 延迟 | 2000ms | 200ms | **10x** |
| 缓存命中率 | 20% | 85% | **4.25x** |
| 前端渲染时间 | 500ms | 200ms | **2.5x** |

---

## 📋 第一阶段：后端缓存优化（Day 1）

### 目标
将核心查询函数的缓存命中率从 20% 提升到 85%

### 任务清单

#### ✅ 任务 1.1: 识别需要缓存的核心查询函数

**方法**:
1. 查找所有 `def get_*` 和 `def fetch_*` 函数
2. 排除工具函数（如 `fetch_one_as_dict`, `fetch_all_as_dict`）
3. 优先处理频繁调用的业务查询

**关键文件**:
- `backend/services/games/game_service.py`
- `backend/services/events/event_service.py`
- `backend/services/parameters/parameter_service.py`
- `backend/models/repositories/*.py`

#### ✅ 任务 1.2: 添加 @cached 装饰器

**修复示例 1: GameService**
```python
# 文件: backend/services/games/game_service.py

from backend.core.cache.decorators import cached, cache_invalidate

class GameService:
    @cached(ttl=1800)  # ✅ 添加缓存 - 30分钟
    def get_game_by_gid(self, game_gid: int) -> Optional[GameEntity]:
        """
        根据GID获取游戏

        缓存策略: 30分钟（游戏信息很少变化）
        预期命中率: >95%
        """
        return self.game_repo.find_by_gid(game_gid)

    @cached(ttl=1800)  # ✅ 添加缓存
    def get_all_games(self) -> List[GameEntity]:
        """
        获取所有游戏

        缓存策略: 30分钟
        预期命中率: >90%
        """
        return self.game_repo.get_all()

    @cache_invalidate  # ✅ 创建游戏时清理缓存
    def create_game(self, game_data: GameEntity) -> GameEntity:
        """创建游戏（写操作 - 清理缓存）"""
        return self.game_repo.create(game_data.model_dump())
```

**修复示例 2: EventService**
```python
# 文件: backend/services/events/event_service.py

class EventService:
    @cached(ttl=600)  # ✅ 添加缓存 - 10分钟（事件信息中等变化频率）
    def get_events_by_game(self, game_gid: int) -> List[EventEntity]:
        """
        获取游戏的所有事件

        缓存策略: 10分钟
        预期命中率: >80%
        """
        return self.event_repo.find_by_game_gid(game_gid)

    @cached(ttl=300)  # ✅ 添加缓存 - 5分钟
    def get_event_by_id(self, event_id: int) -> Optional[EventEntity]:
        """
        根据ID获取事件

        缓存策略: 5分钟
        预期命中率: >85%
        """
        return self.event_repo.find_by_id(event_id)
```

**修复示例 3: ParameterService**
```python
# 文件: backend/services/parameters/parameter_service.py

class ParameterService:
    @cached(ttl=300)  # ✅ 添加缓存 - 5分钟
    def get_parameters_by_event(self, event_id: int) -> List[ParameterEntity]:
        """
        获取事件的所有参数

        缓存策略: 5分钟
        预期命中率: >75%
        """
        return self.param_repo.find_by_event_id(event_id)

    @cached(ttl=1800)  # ✅ 添加缓存 - 30分钟（公共参数很少变化）
    def get_common_parameters(self) -> List[ParameterEntity]:
        """
        获取所有公共参数

        缓存策略: 30分钟
        预期命中率: >95%
        """
        return self.param_repo.find_common_params()
```

#### ✅ 任务 1.3: 验证缓存生效

**测试脚本**:
```python
# backend/tests/performance/test_cache_verification.py

import time
from backend.services.games.game_service import GameService

def test_cache_hit_rate():
    """测试缓存命中率"""
    service = GameService()

    # 第一次调用 - 缓存未命中
    start = time.time()
    game1 = service.get_game_by_gid(10000147)
    time1 = time.time() - start

    # 第二次调用 - 应该命中缓存
    start = time.time()
    game2 = service.get_game_by_gid(10000147)
    time2 = time.time() - start

    print(f"第一次调用（未命中缓存）: {time1*1000:.2f} ms")
    print(f"第二次调用（命中缓存）: {time2*1000:.2f} ms")
    print(f"性能提升: {time1/time2:.1f}x")

    assert time2 < time1 / 10, "缓存应该至少快10倍"
```

**预期结果**:
- 第一次调用: ~10-50ms（数据库查询）
- 第二次调用: ~0.1-0.5ms（缓存）
- 性能提升: **20-100倍**

---

## 📋 第二阶段：React 组件优化（Day 2）

### 目标
减少不必要的组件重渲染，提升前端响应速度

### 任务清单

#### ✅ 任务 2.1: 识别需要优化的 React 组件

**优先级标准**:
1. 大型组件（>1000 行）
2. 频繁渲染的组件（列表、表格）
3. 复杂计算组件（.map(), .filter()）

**关键文件**:
- `frontend/src/analytics/pages/*.tsx`
- `frontend/src/shared/ui/*.tsx`
- `frontend/src/event-builder/components/*.tsx`

#### ✅ 任务 2.2: 添加 React.memo 和 useMemo

**修复示例 1: 大型列表组件**
```tsx
// 文件: frontend/src/analytics/pages/EventsListGraphQL.tsx

import React, { useMemo, useCallback } from 'react';

// ❌ 修复前
export default function EventsList({ gameGid }) {
  const { data, loading, error } = useFetchEvents(gameGid);

  const filtered = data.filter(event => event.active);  // 每次渲染都重新计算
  const sorted = filtered.sort((a, b) => a.name.localeCompare(b.name));  // 每次都重新排序

  return (
    <div>
      {sorted.map(event => (
        <EventCard key={event.id} {...event} />
      ))}
    </div>
  );
}

// ✅ 修复后
export default React.memo(function EventsList({ gameGid }) {
  const { data, loading, error } = useFetchEvents(gameGid);

  const filtered = useMemo(() =>
    data.filter(event => event.active),  // 只在 data 变化时重新计算
    [data]
  );

  const sorted = useMemo(() =>
    [...filtered].sort((a, b) => a.name.localeCompare(b.name)),  // 只在 filtered 变化时重新排序
    [filtered]
  );

  const handleEventClick = useCallback((eventId) => {
    // 事件处理函数也用 useCallback 包装
    navigate(`/events/${eventId}`);
  }, [navigate]);

  return (
    <div>
      {sorted.map(event => (
        <EventCard key={event.id} {...event} onClick={handleEventClick} />
      ))}
    </div>
  );
});
```

**修复示例 2: 共享 UI 组件**
```tsx
// 文件: frontend/src/shared/ui/Table/Table.tsx

import React, { useMemo } from 'react';

// ❌ 修复前
export default function Table({ data, columns }) {
  const filteredData = data.filter(row => row.visible);  // 每次都重新计算
  const sortedData = filteredData.sort((a, b) => a.id - b.id);  // 每次都重新排序

  return (
    <table>
      <thead>
        <tr>
          {columns.map(col => <th key={col.key}>{col.label}</th>)}
        </tr>
      </thead>
      <tbody>
        {sortedData.map(row => (
          <tr key={row.id}>
            {columns.map(col => <td key={col.key}>{row[col.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ✅ 修复后
export default React.memo(function Table({ data, columns }) {
  const filteredData = useMemo(() =>
    data.filter(row => row.visible),
    [data]
  );

  const sortedData = useMemo(() =>
    [...filteredData].sort((a, b) => a.id - b.id),
    [filteredData]
  );

  return (
    <table>
      <thead>
        <tr>
          {columns.map(col => <th key={col.key}>{col.label}</th>)}
        </tr>
      </thead>
      <tbody>
        {sortedData.map(row => (
          <tr key={row.id}>
            {columns.map(col => <td key={col.key}>{row[col.key]}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
});
```

#### ✅ 任务 2.3: 验证前端性能改进

**Chrome DevTools 测试**:
```javascript
// 在浏览器控制台运行

// 1. 测量渲染时间
performance.mark('render-start');
// ... 触发组件渲染 ...
performance.mark('render-end');
performance.measure('render-time', 'render-start', 'render-end');

const measure = performance.getEntriesByName('render-time')[0];
console.log(`渲染时间: ${measure.duration.toFixed(2)} ms`);

// 2. 检查重渲染次数
// 安装 React DevTools 并使用 "Profiler" 标签
```

---

## 📋 第三阶段：性能验证与监控（Day 3）

### 目标
确保优化有效，无回归问题

### 任务清单

#### ✅ 任务 3.1: 运行 E2E 测试

```bash
# 1. 启动开发服务器
cd frontend && npm run dev &

# 2. 启动后端服务器
source backend/venv/bin/activate
python web_app.py &

# 3. 运行 E2E 测试
cd frontend/test/e2e
npx playwright test

# 4. 检查测试结果
# 所有测试应该通过
```

#### ✅ 任务 3.2: 性能基准测试

**API 响应时间测试**:
```python
# backend/tests/performance/benchmark_api.py

import time
import requests
import statistics

def benchmark_api(endpoint: str, iterations: int = 100):
    """API 性能基准测试"""
    times = []

    for i in range(iterations):
        start = time.time()
        response = requests.get(f"http://127.0.0.1:5001{endpoint}")
        end = time.time()

        assert response.status_code == 200
        times.append((end - start) * 1000)  # 转换为毫秒

    return {
        "min": min(times),
        "max": max(times),
        "avg": statistics.mean(times),
        "p50": statistics.median(times),
        "p95": statistics.quantiles(times, n=20)[18],  # 95th percentile
        "p99": statistics.quantiles(times, n=100)[98],  # 99th percentile
    }

if __name__ == "__main__":
    print("🔬 API 性能基准测试")
    print("=" * 60)

    # 测试关键 API
    apis = [
        "/api/games",
        "/api/events?game_gid=10000147",
        "/api/parameters/all?game_gid=10000147",
    ]

    for api in apis:
        print(f"\n📊 测试: {api}")
        results = benchmark_api(api)
        print(f"  平均: {results['avg']:.2f} ms")
        print(f"  P50:  {results['p50']:.2f} ms")
        print(f"  P95:  {results['p95']:.2f} ms")
        print(f"  P99:  {results['p99']:.2f} ms")
```

#### ✅ 任务 3.3: 监控缓存命中率

**缓存统计 API**:
```bash
# 访问缓存统计页面
curl http://127.0.0.1:5001/api/cache/stats

# 预期输出:
# {
#   "l1_hits": 8500,
#   "l2_hits": 1200,
#   "misses": 300,
#   "hit_rate": "97.0%",
#   "total_requests": 10000
# }
```

**目标缓存命中率**: ≥ 85%

---

## 📊 成功标准

### 后端
- ✅ 所有 `get_*` 和 `fetch_*` 函数都有 `@cached` 装饰器
- ✅ 所有写操作都有 `@cache_invalidate` 装饰器
- ✅ 缓存命中率 ≥ 85%
- ✅ API P95 响应时间 < 500ms

### 前端
- ✅ 所有大型组件（>1000 行）都使用 `React.memo`
- ✅ 所有数组操作（.map(), .filter(), .reduce()）都使用 `useMemo`
- ✅ 所有事件处理函数都使用 `useCallback`
- ✅ 组件重渲染次数减少 ≥ 50%

### 测试
- ✅ 所有 E2E 测试通过
- ✅ 无性能回归
- ✅ 无新的控制台错误

---

## 🚀 实施步骤

### Day 1 上午（3-4 小时）
1. ✅ 识别需要缓存的核心查询函数
2. ✅ 添加 @cached 装饰器到 GameService
3. ✅ 添加 @cached 装饰器到 EventService
4. ✅ 添加 @cached 装饰器到 ParameterService

### Day 1 下午（2-3 小时）
5. ✅ 验证缓存生效（运行测试脚本）
6. ✅ 监控缓存命中率
7. ✅ 调整 TTL 参数以优化命中率

### Day 2 全天（6-8 小时）
8. ✅ 识别需要优化的 React 组件
9. ✅ 添加 React.memo 到大型组件
10. ✅ 添加 useMemo 到数组操作
11. ✅ 添加 useCallback 到事件处理函数
12. ✅ 验证前端性能改进

### Day 3 全天（6-8 小时）
13. ✅ 运行完整的 E2E 测试套件
14. ✅ 执行 API 性能基准测试
15. ✅ 监控缓存命中率
16. ✅ 生成修复后对比报告

---

## 📈 预期成果

修复完成后，重新运行性能审计：

```bash
python .claude/skills/performance-audit/scripts/run_audit.py --mode quick
```

**预期结果**:
- ✅ 总问题数: 599 → **<50** (减少 92%)
- ✅ HIGH 严重问题: 538 → **<10** (减少 98%)
- ✅ MEDIUM 严重问题: 34 → **<5** (减少 85%)
- ✅ LOW 严重问题: 27 → **<5** (减少 82%)

---

**报告生成**: 2026-03-09 13:55:00
**执行团队**: Performance Optimization Team
**审核人**: TBD
**下次审查**: 完成后 3 天
