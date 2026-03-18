#!/bin/bash

###############################################################################
# Performance Monitoring Script for Event2Table
#
# Features:
# - Cache hit rate monitoring
# - API response time monitoring
# - Database query performance monitoring
# - Resource usage tracking
# - Performance report generation
#
# Usage:
#   ./scripts/monitoring/performance_monitor.sh              # Run all checks
#   ./scripts/monitoring/performance_monitor.sh --cache      # Cache monitoring only
#   ./scripts/monitoring/performance_monitor.sh --api        # API monitoring only
#   ./scripts/monitoring/performance_monitor.sh --database   # Database monitoring only
#   ./scripts/monitoring/performance_monitor.sh --report     # Generate report
#
# Author: Subagent 6 (CI/CD Automation)
# Date: 2026-03-18
###############################################################################

set -euo pipefail

###############################################################################
# Configuration
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/monitoring"
REPORT_DIR="${PROJECT_ROOT}/reports/monitoring"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/performance_${TIMESTAMP}.log"
REPORT_FILE="${REPORT_DIR}/performance_report_${TIMESTAMP}.md"

# Monitoring thresholds
CACHE_HIT_RATE_THRESHOLD=80  # Minimum 80% cache hit rate
API_RESPONSE_TIME_THRESHOLD=1000  # Maximum 1s average response time
DB_QUERY_TIME_THRESHOLD=500  # Maximum 500ms average query time
MEMORY_USAGE_THRESHOLD=80  # Maximum 80% memory usage
CPU_USAGE_THRESHOLD=80  # Maximum 80% CPU usage

# API endpoints to monitor
API_ENDPOINTS=(
    "http://127.0.0.1:5001/api/health"
    "http://127.0.0.1:5001/api/games"
    "http://127.0.0.1:5001/api/events"
)

# Database to monitor
DATABASE_PATH="${PROJECT_ROOT}/data/dwd_generator.db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

###############################################################################
# Logging Functions
###############################################################################

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "${LOG_FILE}"
}

init_directories() {
    mkdir -p "${LOG_DIR}"
    mkdir -p "${REPORT_DIR}"
    mkdir -p "${PROJECT_ROOT}/logs"
}

###############################################################################
# Cache Monitoring
###############################################################################

monitor_cache() {
    log "Monitoring cache performance..."

    init_directories

    # Check if cache monitoring endpoint exists
    CACHE_STATS_URL="http://127.0.0.1:5001/api/cache/stats"

    if curl -f -s "${CACHE_STATS_URL}" > /dev/null 2>&1; then
        # Fetch cache statistics from API
        CACHE_STATS=$(curl -s "${CACHE_STATS_URL}")

        # Parse cache statistics
        CACHE_HITS=$(echo "${CACHE_STATS}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('hits', 0))" 2>/dev/null || echo "0")
        CACHE_MISSES=$(echo "${CACHE_STATS}" | python3 -c "import sys, json; print(json.load(sys.stdin).get('misses', 0))" 2>/dev/null || echo "0")
        CACHE_TOTAL=$((CACHE_HITS + CACHE_MISSES))

        if [ ${CACHE_TOTAL} -gt 0 ]; then
            CACHE_HIT_RATE=$((CACHE_HITS * 100 / CACHE_TOTAL))

            log "Cache Hits: ${CACHE_HITS}"
            log "Cache Misses: ${CACHE_MISSES}"
            log "Cache Hit Rate: ${CACHE_HIT_RATE}%"

            if [ ${CACHE_HIT_RATE} -ge ${CACHE_HIT_RATE_THRESHOLD} ]; then
                log_success "Cache hit rate is good (${CACHE_HIT_RATE}% >= ${CACHE_HIT_RATE_THRESHOLD}%)"
                return 0
            else
                log_warning "Cache hit rate is below threshold (${CACHE_HIT_RATE}% < ${CACHE_HIT_RATE_THRESHOLD}%)"
                return 1
            fi
        else
            log_warning "No cache statistics available"
            return 0
        fi
    else
        # Fallback: Check cache logs
        log "Cache API not available, checking logs..."

        if [ -f "${PROJECT_ROOT}/logs/cache.log" ]; then
            # Parse cache logs
            CACHE_HITS=$(grep -c "Cache hit" "${PROJECT_ROOT}/logs/cache.log" 2>/dev/null || echo "0")
            CACHE_MISSES=$(grep -c "Cache miss" "${PROJECT_ROOT}/logs/cache.log" 2>/dev/null || echo "0")
            CACHE_TOTAL=$((CACHE_HITS + CACHE_MISSES))

            if [ ${CACHE_TOTAL} -gt 0 ]; then
                CACHE_HIT_RATE=$((CACHE_HITS * 100 / CACHE_TOTAL))
                log "Cache Hit Rate (from logs): ${CACHE_HIT_RATE}%"
            else
                log_warning "No cache data found in logs"
            fi
        else
            log_warning "Cache log file not found"
        fi

        return 0
    fi
}

get_cache_size() {
    # Estimate cache size from Redis or memory cache
    if command -v redis-cli &> /dev/null; then
        redis-cli INFO memory | grep used_memory_human | awk '{print $2}'
    else
        # Check memory usage of Python process
        ps aux | grep "[p]ython.*web_app.py" | awk '{sum+=$4} END {print sum"%"}'
    fi
}

###############################################################################
# API Response Time Monitoring
###############################################################################

monitor_api_response_time() {
    log "Monitoring API response times..."

    init_directories

    local total_time=0
    local endpoint_count=0

    for endpoint in "${API_ENDPOINTS[@]}"; do
        log "Testing endpoint: ${endpoint}"

        # Measure response time
        RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_starttransfer}\n' "${endpoint}" 2>/dev/null || echo "0")

        if [ "${RESPONSE_TIME}" != "0" ]; then
            # Convert to milliseconds
            RESPONSE_TIME_MS=$(echo "${RESPONSE_TIME} * 1000" | bc)
            total_time=$(echo "${total_time} + ${RESPONSE_TIME_MS}" | bc)
            endpoint_count=$((endpoint_count + 1))

            log "Response time: ${RESPONSE_TIME_MS}ms"

            # Check against threshold
            RESPONSE_TIME_INT=$(printf "%.0f" "${RESPONSE_TIME_MS}")
            if [ ${RESPONSE_TIME_INT} -gt ${API_RESPONSE_TIME_THRESHOLD} ]; then
                log_warning "Response time exceeds threshold (${RESPONSE_TIME_MS}ms > ${API_RESPONSE_TIME_THRESHOLD}ms)"
            else
                log_success "Response time is acceptable (${RESPONSE_TIME_MS}ms)"
            fi
        else
            log_warning "Failed to connect to ${endpoint}"
        fi
    done

    if [ ${endpoint_count} -gt 0 ]; then
        AVG_TIME=$(echo "scale=2; ${total_time} / ${endpoint_count}" | bc)
        log "Average response time: ${AVG_TIME}ms"

        # Check average against threshold
        AVG_INT=$(printf "%.0f" "${AVG_TIME}")
        if [ ${AVG_INT} -gt ${API_RESPONSE_TIME_THRESHOLD} ]; then
            log_warning "Average response time exceeds threshold (${AVG_TIME}ms > ${API_RESPONSE_TIME_THRESHOLD}ms)"
            return 1
        else
            log_success "Average response time is good (${AVG_TIME}ms)"
            return 0
        fi
    else
        log_error "No API endpoints could be tested"
        return 1
    fi
}

monitor_api_errors() {
    log "Monitoring API error rates..."

    local ERROR_LOG="${PROJECT_ROOT}/logs/backend.log"
    local ACCESS_LOG="${PROJECT_ROOT}/logs/access.log"

    if [ -f "${ERROR_LOG}" ]; then
        # Count errors in last hour
        ERROR_COUNT=$(grep -c "$(date +'%Y-%m-%d %H')" "${ERROR_LOG}" 2>/dev/null || echo "0")
        log "Errors in last hour: ${ERROR_COUNT}"
    fi

    if [ -f "${ACCESS_LOG}" ]; then
        # Count HTTP 4xx and 5xx errors
        ERROR_COUNT=$(grep "$(date +'%Y-%m-%d %H')" "${ACCESS_LOG}" | grep -cE " [45][0-9]{2} " || echo "0")
        log "HTTP errors in last hour: ${ERROR_COUNT}"
    fi
}

###############################################################################
# Database Query Performance Monitoring
###############################################################################

monitor_database_queries() {
    log "Monitoring database query performance..."

    init_directories

    if [ ! -f "${DATABASE_PATH}" ]; then
        log_warning "Database file not found: ${DATABASE_PATH}"
        return 1
    fi

    # Check database size
    DB_SIZE=$(du -h "${DATABASE_PATH}" | cut -f1)
    log "Database size: ${DB_SIZE}"

    # Check database integrity
    python3 << EOF
import sqlite3
import time
import sys

try:
    conn = sqlite3.connect('${DATABASE_PATH}')
    cursor = conn.cursor()

    # Test common queries
    queries = [
        ("SELECT COUNT(*) FROM games", "Count games"),
        ("SELECT COUNT(*) FROM events", "Count events"),
        ("SELECT * FROM games LIMIT 10", "Fetch games"),
    ]

    total_time = 0
    for query, desc in queries:
        start = time.time()
        try:
            cursor.execute(query)
            cursor.fetchall()
            elapsed = (time.time() - start) * 1000
            total_time += elapsed
            print(f"{desc}: {elapsed:.2f}ms")
        except Exception as e:
            print(f"{desc}: Error - {e}")

    avg_time = total_time / len(queries)
    print(f"Average query time: {avg_time:.2f}ms")

    conn.close()

    if avg_time > ${DB_QUERY_TIME_THRESHOLD}:
        sys.exit(1)
    else:
        sys.exit(0)

except Exception as e:
    print(f"Database monitoring error: {e}")
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        log_success "Database query performance is good"
        return 0
    else
        log_warning "Database query performance needs optimization"
        return 1
    fi
}

check_database_connections() {
    log "Checking database connections..."

    python3 << EOF
import sqlite3

try:
    # Check for open connections
    conn = sqlite3.connect('${DATABASE_PATH}')
    cursor = conn.cursor()

    # Get database stats
    cursor.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]

    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]

    size_mb = (page_count * page_size) / (1024 * 1024)
    print(f"Database size: {size_mb:.2f} MB")
    print(f"Pages: {page_count}")
    print(f"Page size: {page_size} bytes")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
EOF
}

###############################################################################
# Resource Usage Monitoring
###############################################################################

monitor_system_resources() {
    log "Monitoring system resources..."

    # Memory usage
    if command -v free &> /dev/null; then
        MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
        log "Memory usage: ${MEMORY_USAGE}%"

        if [ ${MEMORY_USAGE} -gt ${MEMORY_USAGE_THRESHOLD} ]; then
            log_warning "Memory usage is high (${MEMORY_USAGE}% > ${MEMORY_USAGE_THRESHOLD}%)"
        else
            log_success "Memory usage is normal (${MEMORY_USAGE}%)"
        fi
    fi

    # CPU usage
    if command -v top &> /dev/null; then
        CPU_USAGE=$(top -l 1 -n 0 | grep "CPU usage" | awk '{print $3}' | sed 's/%//' || echo "0")
        log "CPU usage: ${CPU_USAGE}%"

        if command -v bc &> /dev/null; then
            CPU_INT=$(printf "%.0f" "${CPU_USAGE}")
            if [ ${CPU_INT} -gt ${CPU_USAGE_THRESHOLD} ]; then
                log_warning "CPU usage is high (${CPU_USAGE}% > ${CPU_USAGE_THRESHOLD}%)"
            else
                log_success "CPU usage is normal (${CPU_USAGE}%)"
            fi
        fi
    fi

    # Disk usage
    DISK_USAGE=$(df "${PROJECT_ROOT}" | tail -1 | awk '{print $5}' | sed 's/%//')
    log "Disk usage: ${DISK_USAGE}%"

    if [ ${DISK_USAGE} -gt 80 ]; then
        log_warning "Disk usage is high (${DISK_USAGE}%)"
    else
        log_success "Disk usage is normal (${DISK_USAGE}%)"
    fi
}

monitor_application_resources() {
    log "Monitoring application resource usage..."

    # Check Python process (backend)
    PYTHON_PID=$(pgrep -f "python.*web_app.py" | head -n 1)

    if [ -n "${PYTHON_PID}" ]; then
        PYTHON_MEM=$(ps -p "${PYTHON_PID}" -o %mem | tail -1 | xargs)
        PYTHON_CPU=$(ps -p "${PYTHON_PID}" -o %cpu | tail -1 | xargs)

        log "Backend (PID: ${PYTHON_PID}) - Memory: ${PYTHON_MEM}%, CPU: ${PYTHON_CPU}%"
    else
        log_warning "Backend process not found"
    fi

    # Check Node process (frontend dev server)
    NODE_PID=$(pgrep -f "vite" | head -n 1)

    if [ -n "${NODE_PID}" ]; then
        NODE_MEM=$(ps -p "${NODE_PID}" -o %mem | tail -1 | xargs)
        NODE_CPU=$(ps -p "${NODE_PID}" -o %cpu | tail -1 | xargs)

        log "Frontend (PID: ${NODE_PID}) - Memory: ${NODE_MEM}%, CPU: ${NODE_CPU}%"
    else
        log "Frontend dev server not running (normal in production)"
    fi
}

###############################################################################
# Report Generation
###############################################################################

generate_report() {
    log "Generating performance report..."

    init_directories

    cat > "${REPORT_FILE}" << EOF
# Performance Monitoring Report

**Generated:** $(date +'%Y-%m-%d %H:%M:%S')
**Server:** $(hostname)
**Version:** $(cd "${PROJECT_ROOT}" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")

## Executive Summary

EOF

    # Run all monitoring checks and append to report
    {
        echo "### Cache Performance"
        if monitor_cache 2>&1 | tee -a "${LOG_FILE}"; then
            echo "Status: ✅ PASS"
        else
            echo "Status: ❌ FAIL"
        fi
        echo ""

        echo "### API Response Times"
        if monitor_api_response_time 2>&1 | tee -a "${LOG_FILE}"; then
            echo "Status: ✅ PASS"
        else
            echo "Status: ❌ FAIL"
        fi
        echo ""

        echo "### Database Query Performance"
        if monitor_database_queries 2>&1 | tee -a "${LOG_FILE}"; then
            echo "Status: ✅ PASS"
        else
            echo "Status: ❌ FAIL"
        fi
        echo ""

        echo "### System Resources"
        monitor_system_resources 2>&1 | tee -a "${LOG_FILE}"
        echo ""

        echo "### Application Resources"
        monitor_application_resources 2>&1 | tee -a "${LOG_FILE}"
        echo ""

    } | tee -a "${REPORT_FILE}"

    log_success "Performance report generated: ${REPORT_FILE}"

    # Also output to stdout for easy viewing
    cat "${REPORT_FILE}"
}

###############################################################################
# Main
###############################################################################

print_usage() {
    cat << EOF
Usage: $0 [option]

Options:
  (no args)     Run all monitoring checks
  --cache       Monitor cache performance only
  --api         Monitor API response times only
  --database    Monitor database queries only
  --resources   Monitor system resources only
  --report      Generate performance report
  --help        Show this help message

Examples:
  $0                    # Run all checks
  $0 --cache            # Cache monitoring only
  $0 --report           # Generate report

EOF
}

main() {
    local option=${1:-}

    case ${option} in
        --cache)
            monitor_cache
            ;;
        --api)
            monitor_api_response_time
            monitor_api_errors
            ;;
        --database)
            monitor_database_queries
            check_database_connections
            ;;
        --resources)
            monitor_system_resources
            monitor_application_resources
            ;;
        --report)
            generate_report
            ;;
        --help|-h)
            print_usage
            ;;
        "")
            # Run all checks
            init_directories
            log "Starting comprehensive performance monitoring..."

            monitor_cache
            monitor_api_response_time
            monitor_database_queries
            monitor_system_resources
            monitor_application_resources

            log_success "Performance monitoring completed"
            ;;
        *)
            echo "Unknown option: ${option}"
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
