# Performance Benchmark Suite

This directory contains performance benchmarking tools for the Event2Table project.

## Overview

The benchmark suite is designed to:
- Establish performance baselines before optimization
- Measure improvements after optimization
- Compare performance between versions
- Detect performance regressions

## Files

- `performance_baseline.py` - Main baseline testing script
- `README.md` - This file

## Usage

### Prerequisites

1. **Flask server must be running**:
   ```bash
   python web_app.py
   ```

2. **Virtual environment activated**:
   ```bash
   source backend/venv/bin/activate
   ```

3. **Optional dependencies** (for full functionality):
   ```bash
   pip install psutil redis
   ```

### Running the Baseline Test

```bash
python scripts/benchmark/performance_baseline.py
```

### Output

Results are saved to: `output/performance_baseline_v8.json`

Example output format:
```json
{
  "version": "V8.0.0",
  "timestamp": "2026-03-02 10:30:00",
  "tests": {
    "api__api_games": {
      "description": "Get all games",
      "endpoint": "/api/games",
      "requests": 10,
      "errors": 0,
      "avg_ms": 45.23,
      "min_ms": 42.15,
      "max_ms": 51.87
    },
    "cache": {
      "hits": 1234,
      "misses": 398,
      "total_requests": 1632,
      "hit_rate_percent": 75.61
    },
    "db_n1_query_simulation": {
      "query_name": "N+1 query simulation",
      "time_ms": 12.45
    },
    "memory": {
      "rss_mb": 146.32,
      "vms_mb": 892.15
    }
  }
}
```

## Test Categories

### 1. API Response Times
- Tests 3 key endpoints (10 requests each)
- Measures average, min, and max response times
- Endpoints:
  - `/api/games` - Get all games
  - `/api/events?game_gid=10000147` - Get events
  - `/api/parameters/all?game_gid=10000147` - Get parameters

### 2. Cache Hit Rate
- Measures Redis cache effectiveness
- Tracks keyspace hits and misses
- Calculates hit rate percentage

### 3. Database Query Performance
- Tests common query patterns
- Measures execution time in milliseconds
- Queries:
  - N+1 query simulation
  - Count query
  - Join query

### 4. Memory Usage
- Measures Resident Set Size (RSS)
- Measures Virtual Memory Size (VMS)
- Requires `psutil` package

## Comparing Baselines

To compare performance between versions:

```bash
# Run baseline for V8.0.0
python scripts/benchmark/performance_baseline.py
# Output: output/performance_baseline_v8.json

# After optimization, run again
python scripts/benchmark/performance_baseline.py
# Output: output/performance_baseline_v9.json

# Compare manually or use a diff tool
diff output/performance_baseline_v8.json output/performance_baseline_v9.json
```

## Requirements

- Python 3.9+
- Flask server running on port 5001
- SQLite database (`data/dwd_generator.db`)
- Optional: Redis server (for cache tests)
- Optional: psutil (for memory tests)

## Troubleshooting

### "Connection failed - Is Flask server running?"
Start the Flask server:
```bash
python web_app.py
```

### "Database not found"
Initialize the database:
```bash
python scripts/setup/init_db.py
```

### "Redis not installed"
Install Redis (optional):
```bash
pip install redis
```

### "psutil not installed"
Install psutil (optional):
```bash
pip install psutil
```

## Best Practices

1. **Run baselines in consistent environments**
   - Same hardware
   - Same database size
   - Same server load

2. **Run multiple times**
   - Take the average of 3-5 runs
   - Discard outliers

3. **Document the environment**
   - CPU/RAM specifications
   - Database size
   - Concurrent users

4. **Compare apples to apples**
   - Same queries
   - Same endpoints
   - Same test data

## Performance Targets

Based on V8.0.0 baseline:

| Metric | V8.0.0 | V9.0.0 Target | Status |
|--------|--------|---------------|--------|
| API avg response | 45-235ms | <100ms | ⏳ |
| Cache hit rate | 75.6% | >85% | ⏳ |
| Query performance | 5-12ms | <10ms | ⏳ |
| Memory usage | 146MB | <150MB | ⏳ |

## Version History

- **V8.0.0** (2026-03-02) - Initial baseline established
- **V9.0.0** (TBD) - Performance optimization target

## Contributing

When adding new benchmarks:
1. Add test method to `PerformanceBaseline` class
2. Update this README with test description
3. Ensure test is idempotent (can be run multiple times)
4. Handle errors gracefully
5. Print progress messages

## License

MIT License - See LICENSE file for details
