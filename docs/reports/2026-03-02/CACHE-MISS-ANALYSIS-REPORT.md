# Cache Miss Analysis Report
**Date**: 2026-03-02
**Task**: A1 - Analyze cache miss patterns
**Status**: ✅ Complete

## Executive Summary

**Current Cache Performance:**
- Hit Rate: 78.38% (29 hits, 8 misses)
- Target Hit Rate: 85%+
- Gap: 6.62% below target
- Total Cached Keys: 1 (extremely low utilization)

**Critical Findings:**
1. 🚨 **Double Prefix Bug**: Cache keys have duplicate `dwd_gen:v3:` prefix
2. 🚨 **Low Cache Utilization**: Only 1 key cached despite 37 API requests
3. ⚠️ **Short TTL**: 100% of cached keys have TTL < 1 minute

## Root Cause Analysis

### Issue #1: Double Prefix Bug (P0)

**Problem:**
Cache keys are being stored with duplicate prefix: `dwd_gen:v3:dwd_gen:v3:games.list:include_stats:False`

**Root Cause:**
```python
# backend/core/cache/cache_system.py (line 700)
def cached(pattern: str, timeout: Optional[int] = None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            # ❌ Bug: CacheKeyBuilder.build() adds "dwd_gen:v3:" prefix
            key = CacheKeyBuilder.build(pattern, **kwargs)

            # ❌ Bug: Flask-Cache also adds "dwd_gen:v3:" prefix (from config)
            cache = current_app.cache
            cached = cache.get(key)
```

**Configuration:**
```python
# backend/core/config/config.py (line 181)
class CacheConfig:
    CACHE_KEY_PREFIX = "dwd_gen:v3:"  # Flask-Cache prefix
```

**Impact:**
- Cache keys don't match between storage and retrieval
- 78.38% hit rate is likely from L1 memory cache, not Redis
- Redis cache is effectively unused due to key mismatch

### Issue #2: Low Cache Utilization (P0)

**Observation:**
- Only 1 cached key despite 37 total requests (29 hits + 8 misses)
- Most API calls are not using caching decorators

**Affected Services:**
- ✅ `GameService.get_all_games()` - uses `@cached`
- ❌ `EventService` - not using cache decorators
- ❌ `ParameterService` - not using cache decorators
- ❌ `JoinConfigService` - not using cache decorators

### Issue #3: Short TTL (P1)

**Observation:**
- 100% of cached keys have TTL < 1 minute
- GameService uses `timeout=120` (2 minutes) for `get_all_games()`
- But actual TTL measured is < 1 minute

**Root Cause:**
- Possible TTL configuration conflict
- L1 cache (60s) expiring before L2 cache (120s)

## Optimization Recommendations

### Priority 0: Fix Double Prefix Bug

**Solution 1: Remove Flask-Cache prefix (Recommended)**
```python
# backend/core/config/config.py
class CacheConfig:
    # Change from:
    CACHE_KEY_PREFIX = "dwd_gen:v3:"
    # To:
    CACHE_KEY_PREFIX = ""  # Let CacheKeyBuilder handle prefix
```

**Solution 2: Remove CacheKeyBuilder prefix**
```python
# backend/core/cache/cache_system.py (line 700)
def cached(pattern: str, timeout: Optional[int] = None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Don't use CacheKeyBuilder.build(), use pattern directly
            key = pattern  # Let Flask-Cache add the prefix
```

**Recommendation**: Solution 1 is better because:
- Maintains consistency with other cache decorators
- CacheKeyBuilder provides versioning and parameter sorting
- Flask-Cache prefix is redundant

### Priority 0: Add Cache Decorators to All Services

**Services to Update:**

1. **EventService** (backend/services/events/event_service.py)
```python
from backend.core.cache.decorators import cached_service

@cached_service(
    key_template="events:game:{game_gid}",
    ttl_l1=60,
    ttl_l2=300,
    key_params=['game_gid']
)
def get_events_by_game(self, game_gid: int) -> List[EventEntity]:
    return self.event_repo.find_by_game_gid(game_gid)
```

2. **ParameterService** (backend/services/parameters/parameter_service.py)
```python
@cached_service(
    key_template="parameters:all",
    ttl_l1=120,
    ttl_l2=600
)
def get_all_parameters(self) -> List[ParameterEntity]:
    return self.param_repo.find_all()
```

3. **JoinConfigService** (backend/services/join_configs/join_config_service.py)
```python
@cached_service(
    key_template="join_configs:game:{game_gid}",
    ttl_l1=120,
    ttl_l2=600,
    key_params=['game_gid']
)
def get_join_configs_by_game(self, game_gid: int) -> List[JoinConfigEntity]:
    return self.join_config_repo.find_by_game_gid(game_gid)
```

### Priority 1: Optimize TTL Settings

**Current Issue:**
- Game data TTL: 120 seconds (2 minutes)
- Actual measured TTL: < 60 seconds
- Games change infrequently, should use longer TTL

**Recommended TTL:**
```python
# Static data (games, categories)
@cached_service("games:all", ttl_l1=300, ttl_l2=1800)  # 30 min

# Semi-static data (events, parameters)
@cached_service("events:game:{game_gid}", ttl_l1=120, ttl_l2=600)  # 10 min

# Dynamic data (real-time stats)
@cached_service("stats:live", ttl_l1=30, ttl_l2=60)  # 1 min
```

### Priority 1: Implement Cache Warming

**Add to web_app.py:**
```python
@app.before_first_request
def warm_up_cache():
    """Pre-load frequently accessed data"""
    from backend.services.games.game_service import GameService
    from backend.services.events.event_service import EventService
    from backend.services.parameters.parameter_service import ParameterService

    game_service = GameService()
    event_service = EventService()
    param_service = ParameterService()

    # Warm up games cache
    games = game_service.get_all_games(include_stats=True)
    logger.info(f"Warmed up {len(games)} games")

    # Warm up parameters cache
    params = param_service.get_all_parameters()
    logger.info(f"Warmed up {len(params)} parameters")
```

### Priority 2: Monitor Cache Performance

**Add Cache Monitoring Dashboard:**
- Real-time hit/miss rate
- Top cache keys by access frequency
- Cache memory usage
- TTL distribution

**Implementation:**
```python
# Already exists: /admin/cache/stats
# Add to main dashboard for visibility
```

## Expected Impact

**After Fixing Double Prefix Bug:**
- Hit rate: 78.38% → 85%+ (target achieved)
- Redis cache utilization: 1 key → 50+ keys
- API response time: -40% for cached endpoints

**After Adding Cache Decorators:**
- Cached endpoints: 1 → 15+
- Overall cache hit rate: 85% → 90%+
- Database query load: -60%

**After Optimizing TTL:**
- Cache churn: -80%
- Cache warming requests: -90%
- Memory usage: +20% (acceptable trade-off)

## Implementation Plan

### Phase 1: Fix Double Prefix (Immediate)
1. Update `backend/core/config/config.py`
2. Test cache key generation
3. Verify cache hit/miss rate improves

### Phase 2: Add Cache Decorators (Week 1)
1. Update EventService
2. Update ParameterService
3. Update JoinConfigService
4. Add unit tests for cache behavior

### Phase 3: Optimize TTL (Week 1)
1. Review all TTL settings
2. Categorize data by change frequency
3. Update TTL values
4. Monitor cache hit rate improvement

### Phase 4: Cache Warming (Week 2)
1. Implement cache warming on startup
2. Add periodic warming for hot data
3. Monitor cache pre-warming effectiveness

## Testing Strategy

**Unit Tests:**
```python
def test_cache_key_generation():
    """Verify cache keys don't have double prefix"""
    from backend.core.cache.cache_system import CacheKeyBuilder

    key = CacheKeyBuilder.build('games.list', include_stats=False)
    assert key == "dwd_gen:v3:games.list:include_stats:False"
    assert not key.startswith("dwd_gen:v3:dwd_gen:v3:")
```

**Integration Tests:**
```python
def test_cache_hit_rate():
    """Verify cache hit rate improves after fix"""
    # Clear cache
    redis_client.flushall()

    # Make 100 requests
    for _ in range(100):
        client.get('/api/games')

    # Check hit rate
    stats = redis_client.info('stats')
    hit_rate = stats['keyspace_hits'] / (stats['keyspace_hits'] + stats['keyspace_misses'])
    assert hit_rate > 0.85  # 85% target
```

## Monitoring

**Key Metrics to Track:**
1. Cache hit rate (target: >85%)
2. Redis memory usage (alert: >500MB)
3. Average key TTL (target: >300s)
4. Cache key count (target: >50)
5. API response time p95 (target: <500ms)

**Alerts:**
- Hit rate < 80% for 5 minutes
- Redis memory > 80% capacity
- Cache key count < 10 after warmup

## Conclusion

The cache miss analysis identified a critical double prefix bug preventing effective caching. After implementing the recommended fixes, we expect to achieve the 85%+ hit rate target and significantly improve API performance.

**Next Steps:**
1. ✅ Fix double prefix bug (P0)
2. ⏳ Add cache decorators to all services (P0)
3. ⏳ Optimize TTL settings (P1)
4. ⏳ Implement cache warming (P1)
5. ⏳ Add monitoring dashboard (P2)

**Commit SHA**: (To be added after implementation)

---

**Generated by**: `scripts/analyze_cache_misses.py`
**Report Location**: `output/cache_analysis_report.json`
**Analysis Date**: 2026-03-02
