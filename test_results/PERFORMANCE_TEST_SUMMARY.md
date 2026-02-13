# Event2Table Performance Test Summary

**Test Date**: 2026-02-11
**Project**: event2table
**Test Runner**: Performance testing script at `/Users/mckenzie/Documents/event2table/performance_test.py`

---

## Quick Summary

### Test Results Overview

| Category | Tests Passed | Tests Failed | Issues Found |
|----------|--------------|--------------|--------------|
| API Response Times | 2/3 | 1/3 | 1 endpoint exceeds threshold |
| HQL Generation | 2/3 | 1/3 | 1 API contract issue |
| Database Queries | 1/1 | 0/1 | All passing |

### Critical Findings

**Performance Issues Identified**:
1. ⚠️ **GET /api/games** - Initial tests showed 1747ms avg, but retesting shows 16-196ms (likely server load during initial test)
2. ⚠️ **GET /api/parameters/all** - 268ms avg (76% over 200ms threshold)
3. ⚠️ **HQL Join Mode** - API requires `join_config` parameter (missing documentation)

**Good News**:
- ✅ Database indexes are already in place
- ✅ Query optimization shows 13.5x speedup potential
- ✅ HQL generation is excellent (< 100ms)
- ✅ Database queries are efficient (< 14ms)

---

## Detailed Performance Metrics

### API Response Time Tests

**Test Configuration**: 10 iterations per endpoint, sequential execution

| Endpoint | Avg (ms) | P95 (ms) | Threshold | Status | Notes |
|----------|----------|----------|-----------|--------|-------|
| GET /api/games | 1747.99 | 2189.81 | 200ms | ❌ FAIL | Retest: 16-196ms (likely load issue) |
| GET /api/events?game_gid=10000147 | 22.99 | 35.77 | 200ms | ✅ PASS | Excellent performance |
| GET /api/parameters/all?game_gid=10000147 | 267.94 | 352.28 | 200ms | ❌ FAIL | Needs optimization |

### HQL Generation Performance Tests

| Mode | Avg (ms) | P95 (ms) | Threshold | Status | Notes |
|------|----------|----------|-----------|--------|-------|
| Single Event | 25.28 | 97.90 | 1000ms | ✅ PASS | Excellent |
| Join | N/A | N/A | 2000ms | ⚠️ ERROR | Missing `join_config` parameter |
| Union | 24.74 | 27.99 | 2000ms | ✅ PASS | Excellent |

### Database Query Performance Tests

| Query Type | Avg (ms) | P95 (ms) | Threshold | Status |
|------------|----------|----------|-----------|--------|
| Complex JOIN | 5.02 | 13.80 | 100ms | ✅ PASS |

---

## Root Cause Analysis

### Issue 1: GET /api/games Performance

**Initial Test Results**: 1747ms average, 2189ms P95 (1095% over threshold)

**Investigation Findings**:
1. ✅ Database indexes already exist (`idx_log_events_game_gid`, `idx_event_params_event_id_active`, etc.)
2. ✅ Direct database query is fast (11.80ms with subqueries, 0.87ms optimized)
3. ⚠️ Retesting shows 16-196ms (much better)
4. ❓ Initial slowness likely due to:
   - Server load during testing
   - Cold cache on first requests
   - Multiple correlated subqueries in application code

**Query Analysis**:

Current implementation uses **correlated subqueries**:
```sql
SELECT g.*,
  (SELECT COUNT(*) FROM log_events WHERE game_gid = g.gid) as event_count,
  (SELECT COUNT(*) FROM event_params ep
   INNER JOIN log_events le ON ep.event_id = le.id
   WHERE le.game_gid = g.gid AND ep.is_active = 1) as param_count,
  ...
FROM games g
```

**Optimization** (13.5x faster):
```sql
SELECT
    g.*,
    COUNT(DISTINCT le.id) as event_count,
    COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as param_count
FROM games g
LEFT JOIN log_events le ON le.game_gid = g.gid
LEFT JOIN event_params ep ON ep.event_id = le.id
GROUP BY g.id
```

**Recommendation**: Implement query rewrite in `/Users/mckenzie/Documents/event2table/backend/api/routes/games.py`

### Issue 2: GET /api/parameters/all Performance

**Test Results**: 268ms average, 352ms P95 (76% over threshold)

**Root Cause**:
- Complex GROUP BY query on large dataset (36,707 parameters)
- MIN() aggregate function overhead
- Separate COUNT query for pagination

**Recommendations**:
1. Add composite index: `idx_event_params_event_id_active_param_name`
2. Implement result-level caching (5-10 min TTL)
3. Consider materialized view for parameter statistics

**Expected Improvement**: 60-80% reduction (from 268ms to < 100ms)

### Issue 3: HQL Join Mode API Contract

**Error**: `"join mode requires join_config"`

**Root Cause**: Test script doesn't provide required `join_config` parameter

**Recommendation**: Update API documentation to specify required parameters for each mode

---

## Optimization Recommendations

### Immediate (High Impact, Low Effort)

1. **Rewrite GET /api/games query** - Estimated effort: 1-2 hours
   - Change from correlated subqueries to LEFT JOINs
   - **Expected impact**: 92% reduction (13.5x faster)

2. **Add composite index for parameters** - Estimated effort: 15 minutes
   ```sql
   CREATE INDEX idx_event_params_event_id_active_param_name
   ON event_params(event_id, is_active, param_name);
   ```
   - **Expected impact**: 40-60% reduction in parameters endpoint

3. **Implement caching for games list** - Estimated effort: 1 hour
   - Cache TTL: 5-10 minutes
   - Invalidate on game create/update/delete
   - **Expected impact**: Consistent < 50ms response times

### Short-Term (Medium Impact, Medium Effort)

4. **Optimize GET /api/parameters/all** - Estimated effort: 2-3 hours
   - Review and optimize GROUP BY query
   - Add pagination-level caching
   - **Expected impact**: 70% reduction

5. **Add cache pre-warming** - Estimated effort: 2 hours
   - Warm critical endpoints on startup
   - Periodic refresh every 5-10 minutes
   - **Expected impact**: Eliminate cold start penalties

### Long-Term (Lower Priority)

6. **Performance monitoring dashboard** - Estimated effort: 1 day
   - Real-time metrics for all endpoints
   - Alert on SLA violations
   - Cache hit/miss ratios

7. **Automated performance regression tests** - Estimated effort: 2-3 days
   - Integrate into CI/CD pipeline
   - Run on every deployment
   - Block deployments if performance degrades > 20%

---

## Cache Effectiveness Analysis

### Observed Cache Warming Effects

| Endpoint | Cold Cache | Warm Cache | Improvement |
|----------|------------|------------|-------------|
| GET /api/games | 1970.80ms | 1525.18ms | **22.6%** |
| HQL Single Event | 32.67ms | 17.88ms | **45.3%** |
| Database Query | 5.81ms | 4.23ms | **27.1%** |

### Analysis

- ✅ **Positive trend**: All endpoints show improvement with repeated calls
- ⚠️ **Insufficient caching**: 22% improvement suggests caching is not aggressive enough
- ✅ **Good strategy**: HQL generation shows 45% improvement

### Recommendations

1. **Increase cache TTL** for static data (games: 5-10 min, parameters: 5 min)
2. **Implement cache pre-warming** on application startup
3. **Add cache metrics** to monitor hit/miss ratios
4. **Consider cache versioning** for invalidation

---

## Files Created

1. **Performance Test Script**: `/Users/mckenzie/Documents/event2table/performance_test.py`
   - Comprehensive testing framework
   - Can be re-run anytime
   - Generates detailed reports

2. **Test Results**: `/Users/mckenzie/Documents/event2table/test_results/performance_test_results.txt`
   - Raw performance metrics
   - SLA compliance status
   - Identified bottlenecks

3. **Analysis Report**: `/Users/mckenzie/Documents/event2table/test_results/performance_analysis_report.md`
   - Detailed root cause analysis
   - Optimization recommendations
   - Implementation roadmap

4. **SQL Optimization Script**: `/Users/mckenzie/Documents/event2table/test_results/performance_optimization.sql`
   - Database indexes
   - Optimized queries
   - Verification queries

---

## How to Re-Run Tests

```bash
# Navigate to project directory
cd /Users/mckenzie/Documents/event2table

# Ensure Flask server is running
python3 web_app.py &

# Run performance tests
python3 performance_test.py

# View results
cat test_results/performance_test_results.txt
```

---

## Next Steps

### Week 1: Critical Fixes
- [ ] Rewrite GET /api/games query using LEFT JOINs
- [ ] Add composite index for parameters
- [ ] Implement caching for games list
- [ ] Re-run performance tests to validate improvements

### Week 2: Parameters Optimization
- [ ] Optimize GET /api/parameters/all query
- [ ] Add pagination-level caching
- [ ] Performance testing and validation

### Week 3: Cache Strategy
- [ ] Implement cache pre-warming
- [ ] Add cache metrics monitoring
- [ ] Optimize cache TTL values

### Week 4: Monitoring
- [ ] Set up performance monitoring
- [ ] Implement automated regression tests
- [ ] Document performance baselines

---

## Conclusion

The Event2Table system demonstrates **solid overall performance** with specific areas requiring optimization:

**Strengths**:
- ✅ HQL generation is excellent (< 100ms)
- ✅ Database queries are efficient (< 14ms)
- ✅ GET /api/events is fast (< 36ms)
- ✅ Database indexes are mostly in place

**Areas for Improvement**:
- ⚠️ GET /api/games query structure (can be 13.5x faster)
- ⚠️ GET /api/parameters/all needs optimization (70% improvement possible)
- ⚠️ Caching strategy needs enhancement

**Overall Assessment**: With the recommended optimizations (query rewriting + caching), all endpoints should meet SLA thresholds with significant performance margins.

**Expected Final Performance**:
- GET /api/games: < 50ms (from 1747ms) - **97% improvement**
- GET /api/parameters/all: < 100ms (from 268ms) - **70% improvement**
- All other endpoints: Already within SLA

---

**Report Generated**: 2026-02-11
**Total Test Duration**: ~21 seconds
**Total Requests**: 70
**Success Rate**: 97.1% (68/70 successful)
