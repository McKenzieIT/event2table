# Cache System Performance Tests

Performance testing suite for the Event2Table cache system using Locust.

## Overview

This test suite validates the cache system performance under various load conditions:
- **Normal Load**: 100 concurrent users
- **High Load**: 500 concurrent users
- **Extreme Load**: 1000 concurrent users

## Prerequisites

### 1. Install Dependencies

```bash
source backend/venv/bin/activate
pip install locust
```

### 2. Ensure Backend is Running

```bash
# Option 1: Start backend manually
python3 web_app.py

# Option 2: Let the test script start it automatically
bash backend/test/performance/run_performance_test.sh
```

### 3. Verify Test Data

Ensure you have test data in the database:
- Games with GIDs: 10000147, 90000001, 90000002
- Events for these games
- Parameters for these games

## Test Scenarios

### CacheUser - Normal User Behavior

Simulates typical user behavior with realistic wait times (100-500ms between requests).

**Task Weights**:
- Cache Stats (weight 3): Most frequent operation
- Events List (weight 2): High-frequency read
- Game Detail (weight 2): High-frequency read
- Parameters List (weight 1): Lower-frequency read
- Monitoring Metrics: Admin operations
- L1 Capacity: Cache management

### PerformanceTestUser - High Load

Simulates extreme load with minimal wait times (10-50ms).

**Tasks**:
- High frequency reads: Stresses cache layer
- Cache stats burst: Tests monitoring endpoints

### WriteLoadUser - Write Operations

Tests cache invalidation and write-through performance.

## Running Tests

### Quick Test (Recommended)

```bash
bash backend/test/performance/run_performance_test.sh
```

This will:
1. Check if backend is running (start it if needed)
2. Run all three test scenarios
3. Generate performance report
4. Display results

### Manual Test Execution

```bash
cd backend/test/performance

# Normal load
locust -f test_cache_performance.py \
  --headless \
  --host http://127.0.0.1:5001 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 30s \
  --csv normal_load

# High load
locust -f test_cache_performance.py \
  --headless \
  --host http://127.0.0.1:5001 \
  --users 500 \
  --spawn-rate 50 \
  --run-time 30s \
  --csv high_load

# Extreme load
locust -f test_cache_performance.py \
  --headless \
  --host http://127.0.0.1:5001 \
  --users 1000 \
  --spawn-rate 100 \
  --run-time 30s \
  --csv extreme_load
```

### Interactive Mode (Web UI)

```bash
locust -f test_cache_performance.py \
  --host http://127.0.0.1:5001
```

Then open: http://localhost:8089

## Performance Criteria

The cache system must meet these criteria:

| Metric | Threshold | Status |
|--------|-----------|--------|
| P99 Response Time | < 100ms | ⚠️ Critical |
| P95 Response Time | < 50ms | ✅ Target |
| Average Response Time | < 30ms | ✅ Target |
| Error Rate | < 0.1% | ⚠️ Critical |
| Throughput | > 1000 RPS | ✅ Target |
| System Stability | No crashes | ⚠️ Critical |

## Output Files

After running tests, you'll find:

```
backend/test/performance/
├── normal_load_stats.csv          # Normal load statistics
├── normal_load_requests.csv       # Normal load per-request data
├── normal_load.html               # Normal load HTML report
├── high_load_stats.csv            # High load statistics
├── high_load_requests.csv         # High load per-request data
├── high_load.html                 # High load HTML report
├── extreme_load_stats.csv         # Extreme load statistics
├── extreme_load_requests.csv      # Extreme load per-request data
├── extreme_load.html              # Extreme load HTML report
└── PERFORMANCE_REPORT.md          # Combined performance report
```

## Interpreting Results

### CSV Files

**Stats File** (`*_stats.csv`):
- Aggregate statistics per endpoint
- Columns: Type, Name, Request Count, Failure Count, Median, Average, Min, Max, Average Size, RPS, Failures/Sec

**Requests File** (`*_requests.csv`):
- Individual request data
- Columns: Time, Elapsed, Name, Request Type, Response Time, Success, Exception, Size

### HTML Reports

Open `*.html` files in a browser to see:
- Response time distribution charts
- RPS over time
- Failure rates
- Percentile graphs

### Key Metrics

**Response Times**:
- **Average**: Overall performance
- **Median**: Typical user experience
- **P95**: 95% of users see this time or better
- **P99**: Worst-case scenario (critical for SLA)

**Throughput**:
- **RPS (Requests Per Second)**: System capacity
- **Users**: Concurrent load

**Reliability**:
- **Failure Rate**: Percentage of failed requests
- **Exceptions**: Error types and counts

## Performance Warnings

The test script will warn you if:

- ⚠️ **HIGH FAILURE RATE**: > 0.1% (threshold: 0.1%)
- ⚠️ **HIGH AVG RESPONSE TIME**: > 50ms (threshold: 50ms)
- ⚠️ **HIGH P99 RESPONSE TIME**: > 100ms (threshold: 100ms)
- ⚠️ **LOW THROUGHPUT**: < 1000 RPS (expected: >1000 RPS)

## Troubleshooting

### Backend Not Running

```bash
# Start backend
python3 web_app.py

# Or use the test script (will auto-start)
bash backend/test/performance/run_performance_test.sh
```

### Locust Not Installed

```bash
source backend/venv/bin/activate
pip install locust
```

### Connection Refused

Ensure backend is running on port 5001:
```bash
curl http://127.0.0.1:5001/api/cache/stats
```

### High Failure Rate

Check backend logs:
```bash
tail -f /tmp/backend_performance_test.log
```

Common issues:
- Database connection problems
- Redis connection issues
- Memory limits
- Too many open files

### Slow Response Times

Check system resources:
```bash
# CPU usage
top -o cpu

# Memory usage
top -o mem

# Disk I/O
iostat 1

# Network connections
netstat -an | grep 5001
```

## Performance Optimization Tips

### If P99 > 100ms

1. **Check cache hit rate**:
   ```python
   # View cache statistics
   curl http://127.0.0.1:5001/api/cache/stats
   ```

2. **Increase L1 cache size**:
   ```python
   # backend/core/cache/cache_manager.py
   L1_MAX_SIZE = 10000  # Increase from default
   ```

3. **Optimize queries**:
   - Add database indexes
   - Use SELECT specific columns instead of SELECT *
   - Implement pagination

### If Throughput < 1000 RPS

1. **Increase worker processes**:
   ```bash
   # Use Gunicorn with multiple workers
   gunicorn -w 4 -b 0.0.0.0:5001 web_app:app
   ```

2. **Enable connection pooling**:
   ```python
   # backend/core/database/connection.py
   pool_size = 20  # Increase connection pool
   ```

3. **Optimize Redis connection**:
   ```python
   # Use connection pooling
   redis_pool = redis.ConnectionPool(max_connections=50)
   ```

### If Error Rate > 0.1%

1. **Add retry logic**:
   ```python
   from tenacity import retry, stop_after_attempt

   @retry(stop=stop_after_attempt(3))
   def get_with_retry(key):
       return cache.get(key)
   ```

2. **Implement circuit breaker**:
   ```python
   from circuitbreaker import circuit

   @circuit(failure_threshold=5, recovery_timeout=60)
   def external_api_call():
       pass
   ```

3. **Add timeouts**:
   ```python
   redis_client.get(key, timeout=0.1)  # 100ms timeout
   ```

## Continuous Integration

Add to CI/CD pipeline:

```yaml
# .github/workflows/performance-test.yml
name: Performance Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install locust
      - name: Start backend
        run: python3 web_app.py &
      - name: Run performance tests
        run: bash backend/test/performance/run_performance_test.sh
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: performance-results
          path: backend/test/performance/*.csv
```

## References

- [Locust Documentation](https://docs.locust.io/)
- [Cache System Architecture](../../docs/development/architecture.md)
- [Performance Optimization Guide](../../docs/optimization/CORE_OPTIMIZATION_GUIDE.md)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Locust logs in console output
3. Check backend logs in `/tmp/backend_performance_test.log`
4. Consult project documentation in `docs/`

---

**Author**: Event2Table Development Team
**Last Updated**: 2026-02-24
**Version**: 1.0.0
