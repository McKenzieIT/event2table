#!/bin/bash

###############################################################################
# Cache System Performance Test Runner
#
# This script runs Locust performance tests against the cache system.
# It tests three load scenarios: normal, high, and extreme.
#
# Usage:
#   bash run_performance_test.sh
#
# Requirements:
#   - Backend server running on port 5001
#   - Locust installed (pip install locust)
#   - Test data available (games, events, parameters)
#
# Author: Event2Table Development Team
# Date: 2026-02-24
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/mckenzie/Documents/event2table"
BACKEND_DIR="$PROJECT_ROOT/backend"
TEST_DIR="$BACKEND_DIR/test/performance"
HOST="http://127.0.0.1:5001"
BACKEND_PID=""

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_backend_running() {
    log_info "Checking if backend server is running..."
    if curl -s "$HOST/api/cache/stats" > /dev/null 2>&1; then
        log_success "Backend server is running on $HOST"
        return 0
    else
        log_warning "Backend server is not running"
        return 1
    fi
}

start_backend() {
    log_info "Starting backend server..."
    cd "$PROJECT_ROOT"
    source backend/venv/bin/activate
    python3 web_app.py > /tmp/backend_performance_test.log 2>&1 &
    BACKEND_PID=$!
    log_success "Backend started with PID: $BACKEND_PID"

    # Wait for backend to be ready
    log_info "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s "$HOST/api/cache/stats" > /dev/null 2>&1; then
            log_success "Backend is ready!"
            return 0
        fi
        sleep 1
    done

    log_error "Backend failed to start within 30 seconds"
    return 1
}

stop_backend() {
    if [ -n "$BACKEND_PID" ]; then
        log_info "Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
        log_success "Backend stopped"
    fi
}

run_test() {
    local test_name=$1
    local users=$2
    local spawn_rate=$3
    local run_time=$4
    local csv_prefix=$5

    log_info "=========================================="
    log_info "Running: $test_name"
    log_info "Users: $users"
    log_info "Spawn Rate: $spawn_rate"
    log_info "Run Time: $run_time"
    log_info "=========================================="

    cd "$TEST_DIR"

    locust -f test_cache_performance.py \
        --headless \
        --host "$HOST" \
        --users "$users" \
        --spawn-rate "$spawn_rate" \
        --run-time "$run_time" \
        --csv "$csv_prefix" \
        --html "$csv_prefix.html"

    if [ $? -eq 0 ]; then
        log_success "$test_name completed successfully"
    else
        log_error "$test_name failed"
        return 1
    fi
}

generate_report() {
    local output_file="$TEST_DIR/PERFORMANCE_REPORT.md"

    log_info "Generating performance report..."

    cat > "$output_file" << 'EOF'
# 缓存系统性能测试报告

**测试日期**: 2026-02-24
**测试工具**: Locust 2.34.0
**测试主机**: http://127.0.0.1:5001

---

## 测试环境

- **CPU**: $(sysctl -n hw.ncpu) cores
- **Memory**: $(sysctl -n hw.memsize | awk '{printf "%.2f GB", $1/1024/1024/1024}')
- **Python Version**: $(python3 --version)
- **操作系统**: $(sw_vers -productName) $(sw_vers -productVersion)
- **Locust Version**: $(locust --version | cut -d' ' -f3)

---

## 测试场景

### 场景1: 正常负载 (100 users)

**配置**:
- 并发用户: 100
- 启动速率: 10 users/s
- 运行时长: 30s

**结果**:
EOF

    # Add test results
    if [ -f "$TEST_DIR/normal_load_stats.csv" ]; then
        echo '```csv' >> "$output_file"
        cat "$TEST_DIR/normal_load_stats.csv" >> "$output_file"
        echo '```' >> "$output_file"
    fi

    cat >> "$output_file" << 'EOF'

### 场景2: 高峰负载 (500 users)

**配置**:
- 并发用户: 500
- 启动速率: 50 users/s
- 运行时长: 30s

**结果**:
EOF

    if [ -f "$TEST_DIR/high_load_stats.csv" ]; then
        echo '```csv' >> "$output_file"
        cat "$TEST_DIR/high_load_stats.csv" >> "$output_file"
        echo '```' >> "$output_file"
    fi

    cat >> "$output_file" << 'EOF'

### 场景3: 极限负载 (1000 users)

**配置**:
- 并发用户: 1000
- 启动速率: 100 users/s
- 运行时长: 30s

**结果**:
EOF

    if [ -f "$TEST_DIR/extreme_load_stats.csv" ]; then
        echo '```csv' >> "$output_file"
        cat "$TEST_DIR/extreme_load_stats.csv" >> "$output_file"
        echo '```' >> "$output_file"
    fi

    cat >> "$output_file" << 'EOF'

---

## 性能指标对比

| 场景 | 并发用户 | 平均响应时间 | P95响应时间 | P99响应时间 | 错误率 | RPS |
|------|---------|-------------|------------|------------|--------|-----|
| 正常负载 | 100 | TBD | TBD | TBD | TBD | TBD |
| 高峰负载 | 500 | TBD | TBD | TBD | TBD | TBD |
| 极限负载 | 1000 | TBD | TBD | TBD | TBD | TBD |

---

## 结论

### 性能标准

- ✅ P99响应时间 < 100ms
- ✅ 错误率 < 0.1%
- ✅ 系统稳定，无崩溃

### 测试结果

[测试完成后更新此部分]

### 性能瓶颈分析

[分析后更新此部分]

### 优化建议

[评估后更新此部分]

---

## 附录

### 测试数据

- 游戏GID列表: 10000147, 90000001, 90000002
- 测试端点: /api/cache/stats, /api/events, /api/games, /api/parameters/all
- 缓存策略: L1 (内存) + L2 (Redis)

### 详细日志

- Normal Load: `normal_load_stats.csv`, `normal_load.html`
- High Load: `high_load_stats.csv`, `high_load.html`
- Extreme Load: `extreme_load_stats.csv`, `extreme_load.html`

---

**报告生成时间**: $(date)
**测试执行者**: $(whoami)
EOF

    log_success "Performance report generated: $output_file"
}

cleanup() {
    log_info "Cleaning up..."
    stop_backend
}

# Main execution
main() {
    log_info "Starting cache system performance test..."
    echo ""

    # Check if backend is running
    if ! check_backend_running; then
        if ! start_backend; then
            log_error "Failed to start backend server"
            exit 1
        fi
    fi

    # Trap cleanup on exit
    trap cleanup EXIT

    # Run tests
    echo ""
    run_test "Normal Load Test" 100 10 "30s" "normal_load" || exit 1
    echo ""

    run_test "High Load Test" 500 50 "30s" "high_load" || exit 1
    echo ""

    run_test "Extreme Load Test" 1000 100 "30s" "extreme_load" || exit 1
    echo ""

    # Generate report
    generate_report

    log_success "Performance tests completed successfully!"
    echo ""

    # List generated files
    log_info "Generated files:"
    ls -lh "$TEST_DIR"/*.csv "$TEST_DIR"/*.html 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
}

# Run main
main "$@"
