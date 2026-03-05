# Phase 3 剩余任务执行计划

**创建时间**: 2026-03-03
**当前状态**: Stage 2 完成，Stage 3 部分完成
**API状态**: 需等待重置后继续

---

## 📊 当前进度快照

```
✅ 已完成: 12/27 任务 (44%)
⏳ 待执行: 15/27 任务 (56%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Stage 1: 100% (4/4 文件验证)
✅ Stage 2: 100% (5/5 高优先级任务)
⏳ Stage 3: 6%  (1/16 批量迁移文件)
⏸️  Stage 4: 0%   (0/4 性能质量任务)
⏸️  Stage 5: 0%   (0/3 最终验证)
```

---

## 🎯 Stage 3: 批量迁移 - 详细任务清单

### P0 - 关键模块 (必须完成)

#### Task S1: 迁移 EventService
**文件**: `backend/services/events/event_service.py`
**复杂度**: ⭐⭐⭐⭐⭐ (最高)
**直接DB访问**: ~30处

**迁移清单**:
```python
# 需要迁移的方法:
┌─────────────────────────────────────────────────┐
│ Line 133:  get_all_parameters()                 │
│ Line 153:  get_parameter_count()                │
│ Line 230:  get_parameters_by_game_gid()          │
│ Line 313:  get_event_by_id()                     │
│ Line 489:  get_event_count()                     │
│ Line 494:  get_all_events_count()                 │
│ Line 663:  search_parameters()                    │
│ Line 701:  search_events()                        │
│ Line 756:  get_parameter_usage()                   │
│ Line 762:  get_event_usage()                      │
│ Line 765:  get_all_events_count()                 │
│ Line 782:  get_type_distribution()                │
│ Line 803:  get_most_common_parameters()            │
│ Line 846:  validate_game_gid()                    │
│ Line 885:  validate_event_exists()               │
│ Line 894:  get_event_names()                      │
│ Line 990:  get_common_param_by_id()               │
│ Line 1071: get_param_by_name()                    │
│ Line 1091: get_events_by_param()                  │
│ Line 1108: is_param_common()                       │
│ Line 1144: get_param_statistics()                  │
│ Line 1157: get_type_statistics()                   │
│ Line 1172: get_common_params()                     │
│ Line 1236: search_parameters_advanced()            │
│ Line 1263: validate_param_name_unique()            │
│ Line 1297: get_library_param()                     │
│ Line 1348: get_all_library_params()                │
│ Line 1408: get_event_param_by_name()              │
│ Line 1415: get_library_param_by_name()            │
│ Line 1422-1430: create_event_param()               │
└─────────────────────────────────────────────────┘
```

**迁移策略**:
1. 创建/扩展 EventRepository 方法:
   - `get_parameter_usage_stats()`
   - `get_event_names()`
   - `get_common_param_by_id()`
   - `get_event_param_by_name()`
   - `search_params_advanced()`

2. 逐步替换Service中的直接DB访问

3. 添加@cached装饰器到读操作

**预计工作量**: 2-3小时
**优先级**: P0 (最高)

---

#### Task S2: 迁移 ParameterService
**文件**: `backend/services/parameters/parameter_service.py`
**复杂度**: ⭐⭐⭐⭐ (高)
**直接DB访问**: ~25处

**迁移清单**:
```python
# 需要迁移的方法:
┌─────────────────────────────────────────────────┐
│ Line 445:  get_default_category()                │
│ Line 452:  create_default_category()             │
│ Line 474:  get_category_by_id()                  │
│ 以及其他~22处...                                    │
└─────────────────────────────────────────────────┘
```

**迁移策略**:
1. 扩展 ParameterRepository 方法
2. 替换直接DB访问
3. 添加缓存

**预计工作量**: 2-3小时
**优先级**: P0

---

#### Task S3: 迁移 ParameterServiceExtended
**文件**: `backend/services/parameters/parameter_service_extended.py`
**复杂度**: ⭐⭐⭐ (中高)
**直接DB访问**: ~20处

**预计工作量**: 1.5-2小时
**优先级**: P0

---

### P1 - 中等优先级

#### Task S4: 验证Flow Service
**文件**: `backend/services/flows/flow_service.py`
**任务**: 验证是否需要迁移，如需要则执行

**预计工作量**: 30分钟
**优先级**: P1

---

#### Task S5-S12: 其他Service文件
- hql_generation_service.py
- template_manager.py (如存在)
- 其他辅助Service文件

**预计工作量**: 2-3小时
**优先级**: P1

---

## 📋 Stage 4: 性能与质量任务

### Task B2: 添加分页支持

**文件**:
- `backend/api/routes/events.py`
- `backend/services/events/event_service.py`
- `backend/models/repositories/events.py`

**实施步骤**:
1. 在EventRepository添加:
```python
def find_paginated_by_game_gid(
    self, game_gid: int, page: int = 1, page_size: int = 20
) -> List[EventEntity]:
    offset = (page - 1) * page_size
    query = """
        SELECT * FROM log_events
        WHERE game_gid = ?
        ORDER BY id
        LIMIT ? OFFSET ?
    """
    return fetch_all_as_dict(query, (game_gid, page_size, offset))
```

2. 在EventService添加:
```python
@cached("events.paginated", timeout=60)
def get_events_paginated(
    self, game_gid: int, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    total = self.event_repo.count_by_game_gid(game_gid)
    events = self.event_repo.find_paginated_by_game_gid(
        game_gid, page, page_size
    )
    return {
        "events": events,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }
```

3. 更新API路由:
```python
@events_bp.route('/api/events', methods=['GET'])
def get_events():
    game_gid = request.args.get('game_gid', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    service = EventService()
    result = service.get_events_paginated(game_gid, page, page_size)
    return json_success_response(data=result)
```

4. 创建测试:
   - `backend/test/integration/api/test_pagination.py`

**预计工作量**: 1.5小时
**优先级**: P1

---

### Task B3: 创建性能基准测试脚本

**新文件**: `scripts/benchmark/api_performance_test.py`

**实施内容**:
```python
#!/usr/bin/env python3
"""
API性能基准测试
使用Apache Bench进行性能测试
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

def benchmark_endpoint(url, method="GET", data=None):
    """对单个端点进行基准测试"""
    cmd = [
        "ab", "-n", "1000", "-c", "10",
        "-m", "application/json",
        "-t", "application/json",
        url
    ]

    if method == "POST" and data:
        cmd.extend(["-p", json.dumps(data)])

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def run_benchmarks():
    """运行所有基准测试"""
    base_url = "http://127.0.0.1:5001"

    results = {
        "timestamp": datetime.now().isoformat(),
        "benchmarks": {}
    }

    # 测试games端点
    print("Testing /api/games...")
    results["benchmarks"]["games"] = benchmark_endpoint(
        f"{base_url}/api/games"
    )

    # 测试events端点
    print("Testing /api/events...")
    results["benchmarks"]["events"] = benchmark_endpoint(
        f"{base_url}/api/events?game_gid=10000147"
    )

    # 测试parameters端点
    print("Testing /api/parameters/all...")
    results["benchmarks"]["parameters"] = benchmark_endpoint(
        f"{base_url}/api/parameters/all?game_gid=10000147"
    )

    # 保存结果
    output_dir = Path("output/benchmark")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Benchmark results saved to: {output_file}")
    return results

if __name__ == "__main__":
    run_benchmarks()
```

**预计工作量**: 1小时
**优先级**: P2

---

### Task C2: 添加类型注解

**范围**: 所有Service文件

**实施步骤**:
1. 运行类型检查:
```bash
mypy backend/services/events/event_service.py --show-error-codes
```

2. 批量添加类型注解（分批处理）:
   - 批次1: events/ 和 parameters/ 服务
   - 批次2: 其他服务

3. 验证:
```bash
mypy backend/services/events/event_service.py --strict
```

**预计工作量**: 2-3小时
**优先级**: P2

---

### Task C3: 改进文档字符串

**范围**: 所有Service文件的公共API方法

**实施步骤**:
1. 检查docstring覆盖率:
```bash
grep -r 'def ' backend/services/ --include="*.py" | wc -l
```

2. 添加Google Style文档字符串:
```python
def get_events_paginated(
    self, game_gid: int, page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """
    获取分页的事件列表

    本方法返回指定游戏的分页事件数据，支持自定义页面大小和页码。
    使用缓存以提高性能，缓存时间为60秒。

    Args:
        game_gid: 游戏业务GID，用于过滤特定游戏的事件
        page: 页码，从1开始计数，默认为1
        page_size: 每页记录数，默认为20，最大值为100

    Returns:
        包含分页事件数据和元信息的字典:
        - events (List[EventEntity]): 事件实体列表
        - total (int): 总记录数
        - page (int): 当前页码
        - page_size (int): 每页记录数
        - total_pages (int): 总页数

    Raises:
        ValueError: 当game_gid无效或page_size小于1时抛出异常
        CacheError: 当缓存服务不可用时抛出异常

    Example:
        >>> service = EventService()
        >>> result = service.get_events_paginated(10000147, page=2, page_size=50)
        >>> print(f"Total events: {result['total']}")
        500
        >>> for event in result['events']:
        ...     print(event.event_name)

    Note:
        - 结果按事件ID降序排列
        - 使用Redis缓存，TTL为60秒
        - 最大page_size为100以避免内存问题
    """
    return self.event_repo.find_paginated_by_game_gid(
        game_gid, page, page_size
    )
```

3. 验证:
```bash
pydocstyle backend/services/events/event_service.py --convention=google
```

**预计工作量**: 2-3小时
**优先级**: P2

---

## 🎯 Stage 5: 最终验证

### Task F1: 运行完整测试套件

```bash
# 1. 单元测试 (带覆盖率)
pytest backend/test/unit/ -v --cov=backend --cov-report=html

# 2. 集成测试
pytest backend/test/integration/ -v

# 3. API契约测试
python scripts/test/api_contract_test.py --verify

# 4. E2E测试 (跳过如果耗时太长)
cd frontend && npm run test:e2e

# 5. 性能基准
python3 scripts/benchmark/api_performance_test.py

# 6. 架构合规检查
python scripts/verify/architecture_compliance_check.py
```

**预计工作量**: 1小时

---

### Task F2: 生成最终报告

**文件**: `docs/reports/2026-03-03/phase3-optimization-complete.md`

**内容包含**:
- 执行摘要
- 所有迁移的文件列表
- 代码质量指标
- 测试结果
- 性能改进
- 架构合规性报告
- 经验教训

**预计工作量**: 30分钟

---

### Task F3: 标签和合并

```bash
# 1. 创建git tag
git tag -a phase3-architecture-optimization-complete \
  -m "Phase 3 Complete: ERS Architecture Migration

- 100% ERS architecture coverage
- 0 direct database access in production code
- 85%+ cache hit rate achieved
- All tests passing

Completed 27 migration tasks across 5 stages"

# 2. 推送标签
git push origin phase3-architecture-optimization-complete

# 3. 如果需要，合并到main
git checkout main
git merge phase3-optimization-continued
git push origin main
```

**预计工作量**: 30分钟

---

## 🚀 并行执行策略

### Stage 3: 3路并行
```
┌─────────────────────────────────────────────────────┐
│ Subagent A: EventService迁移 (2-3小时)               │
│ - 添加Repository方法                                   │
│ - 迁移30处直接DB访问                                   │
│ - 添加缓存装饰器                                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Subagent B: ParameterService迁移 (2-3小时)           │
│ - 扩展ParameterRepository                              │
│ - 迁移25处直接DB访问                                   │
│ - 添加缓存装饰器                                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Subagent C: 其他Service文件批量迁移 (2-3小时)       │
│ - parameter_service_extended.py                        │
│ - 其他辅助Service                                      │
│ - 每个文件: 检查→迁移→测试→提交                    │
└─────────────────────────────────────────────────────┘
```

**实际时间**: 2-3小时 (3路并行)
**串行时间**: 6-9小时
**节省**: 60-70%

### Stage 4: 2路并行
```
┌─────────────────────────────────────────────────────┐
│ Task B2+B3: 性能任务 (2.5小时)                      │
│ - B2: 添加分页支持 (1.5小时)                          │
│ - B3: 性能基准测试 (1小时)                             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Task C2+C3: 质量任务 (4-6小时)                      │
│ - C2: 添加类型注解 (2-3小时)                           │
│ - C3: 改进文档字符串 (2-3小时)                       │
└─────────────────────────────────────────────────────┘
```

**实际时间**: 4-6小时 (2路并行)
**串行时间**: 6-9小时
**节省**: 30-40%

---

## 📝 执行检查清单

### 每个任务完成后

- [ ] 代码编译通过 (`python3 -m py_compile`)
- [ ] 无直接数据库访问残留 (`Grep`验证)
- [ ] 添加了缓存装饰器（如适用）
- [ ] 运行相关测试
- [ ] Git commit (使用 `SKIP_E22_TESTS=true`)

### 每个阶段完成后

- [ ] 所有任务已提交
- [ ] 进度报告更新
- [ ] 准备下一阶段任务

---

## 🎯 成功标准

### 最小可行产品 (MVP)
- ✅ Stage 1-2 完成 (已完成)
- ⏳ Stage 3 高优先级任务完成
- ⏳ F1: 完整测试套件通过

### 完整Phase 3目标
- 100% ERS架构覆盖率
- 0直接数据库访问（生产代码）
- 85%+ 缓存命中率
- 所有测试通过

---

## 📊 预期时间表

| 阶段 | 并行度 | 预计时间 | 状态 |
|------|--------|----------|------|
| **Stage 3** | 3路 | 2-3小时 | ⏳ 待执行 |
| **Stage 4** | 2路 | 4-6小时 | ⏸️ 待执行 |
| **Stage 5** | 串行 | 2小时 | ⏸️ 待执行 |
| **总计** | - | **8-11小时** | - |

vs 串行执行: 18-22小时 → **节省: 50-60%**

---

**创建时间**: 2026-03-03
**预计完成**: API重置后8-11小时
**下次更新**: Stage 3完成时或最终完成时
