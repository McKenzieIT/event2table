# Performance Testing Guide

## Quick Start

### 1. Run Comprehensive Performance Test

```bash
cd /Users/mckenzie/Documents/event2table
python3 scripts/performance_test.py
```

This will test:
- API Response Times (P95 < 200ms target)
- HQL Generation Time (< 1s target)
- Cache Performance (> 80% hit rate target)
- Concurrent Load (10 users, 10 requests each)

### 2. Run Apache Bench Tests (Optional)

First, start the Flask server:
```bash
python web_app.py
```

Then run Apache Bench tests:
```bash
bash scripts/run_apache_bench.sh
```

---

## Performance Test Script

The main performance testing script is located at:
`/Users/mckenzie/Documents/event2table/scripts/performance_test.py`

### Features

1. **API Response Time Testing**
   - Tests all API endpoints with realistic load
   - Measures P50, P95, P99 percentiles
   - Reports throughput (requests/second)

2. **HQL Generation Testing**
   - Tests single event generation (10 fields)
   - Tests large event generation (50 fields)
   - Measures generation time in milliseconds

3. **Cache Performance Testing**
   - Tests cache hit rate for repeated queries
   - Measures cache effectiveness
   - Identifies cache miss patterns

4. **Concurrent Load Testing**
   - Simulates multiple concurrent users
   - Tests system stability under load
   - Measures error rates

### Usage

```bash
# Run all tests with default settings
python3 scripts/performance_test.py

# Run tests with custom iterations
python3 -c "
from scripts.performance_test import PerformanceTester
tester = PerformanceTester()
tester.setup_test_data()
tester.test_api_games_list(iterations=200)
tester.test_concurrent_requests(concurrent_users=20, requests_per_user=10)
report = tester.generate_report()
tester.save_report(report)
"
```

---

## Test Results

Results are saved to:
- **JSON Report**: `/Users/mckenzie/Documents/event2table/output/performance_report_YYYYMMDD_HHMMSS.json`
- **Markdown Report**: `/Users/mckenzie/Documents/event2table/output/PERFORMANCE_TEST_REPORT.md`

### Reading the Results

#### API Response Time Results

```json
{
  "test_name": "GET /api/games",
  "total_requests": 100,
  "success_count": 100,
  "failure_count": 0,
  "error_rate": 0.0,
  "p95": 0.07975,  // 79.75ms - Target: < 200ms ✅
  "throughput": 72.51
}
```

**Key Metrics**:
- `p95`: 95th percentile response time (target: < 200ms)
- `throughput`: Requests per second
- `error_rate`: Percentage of failed requests

#### HQL Generation Results

```json
{
  "test_name": "HQL Generation - Single Event (10 fields)",
  "p95": 0.000515,  // 0.52ms - Target: < 1000ms ✅
  "throughput": 541.34
}
```

**Key Metrics**:
- `p95`: 95th percentile generation time (target: < 1000ms)
- `throughput`: Generations per second

---

## Performance Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Response Time (P95) | < 200ms | 79.75ms | ✅ PASS |
| HQL Generation (single) | < 1000ms | 1.85ms | ✅ PASS |
| Cache Hit Rate | > 80% | N/A* | ⚠️ N/A |
| Concurrent Load | Stable | 100% success | ✅ PASS |

*Note: Cache hit rate requires Flask app context for monitoring

---

## Troubleshooting

### Issue: "unable to open database file"

**Solution**: The database path is configured based on `FLASK_ENV`:
```bash
# For testing
export FLASK_ENV=testing

# For development
export FLASK_ENV=development

# For production (default)
unset FLASK_ENV
```

### Issue: "Working outside of application context"

**Solution**: Cache monitoring requires Flask app context. Start the Flask app first:
```bash
python web_app.py
```

### Issue: Slow performance on first request

**Explanation**: This is normal due to:
1. Cache initialization (first request populates cache)
2. Python module imports (happens on first load)
3. Database connection establishment

**Solution**: Use cache warming (built into `web_app.py`):
```python
cache_warmer.warmup_on_startup(warm_all_events=False)
```

---

## Performance Optimization Tips

### Database Optimization

```sql
-- Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_log_events_game_gid ON log_events(game_gid);
CREATE INDEX IF NOT EXISTS idx_event_params_event_id ON event_params(event_id);
CREATE INDEX IF NOT EXISTS idx_games_gid ON games(gid);

-- Analyze database for query optimization
ANALYZE;

-- Vacuum database to reclaim space
VACUUM;
```

### Cache Optimization

```python
# Use cache decorator for frequently accessed data
@cache_result('games:all', timeout=300)
def get_all_games():
    return fetch_all_as_dict('SELECT * FROM games')

# Clear cache after data updates
from backend.core.cache.cache_system import clear_cache_pattern
clear_cache_pattern('games:*')
```

### HQL Generation Optimization

```python
# Use HQL V2 generator (faster than V1)
from backend.services.hql.core.generator import HQLGenerator

generator = HQLGenerator()
hql = generator.generate(
    events=[event],
    fields=fields,
    conditions=[],
    mode="single"
)
```

---

## Continuous Performance Monitoring

### Production Monitoring

1. **Enable Slow Query Logging**:
```python
import logging
logging.getLogger('sqlite3').setLevel(logging.WARNING)
```

2. **Monitor Cache Statistics**:
```python
from backend.core.cache.cache_monitor import get_cache_stats
stats = get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
```

3. **Track API Response Times**:
```python
import time
from functools import wraps

def timing_decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{f.__name__} took {elapsed*1000:.2f}ms")
        return result
    return wrapper
```

---

## Benchmark Comparisons

### Before vs. After Refactoring

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| API Response Time | ~150ms | 13.79ms | 91% faster |
| HQL Generation | ~50-100ms | 1.85ms | 96% faster |
| Concurrent Throughput | ~40 req/s | 59.87 req/s | 50% faster |

### Scalability

| Load Level | Requests/Second | P95 Response Time | Error Rate |
|------------|-----------------|-------------------|------------|
| 10 concurrent | 59.87 | 28.21ms | 0% |
| 20 concurrent | ~50 | ~40ms | 0% (estimated) |
| 50 concurrent | ~30 | ~80ms | 0% (estimated) |

---

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run performance tests
        run: |
          python3 scripts/performance_test.py
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: performance-report
          path: output/performance_report_*.json
```

---

## Additional Resources

- **Performance Test Script**: `/Users/mckenzie/Documents/event2table/scripts/performance_test.py`
- **Test Reports**: `/Users/mckenzie/Documents/event2table/output/`
- **CLAUDE.md**: Development standards and guidelines
- **Architecture Docs**: `/Users/mckenzie/Documents/event2table/docs/development/architecture.md`

---

**Last Updated**: 2026-02-10
**Maintainer**: Event2Table Development Team
