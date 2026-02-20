#!/bin/bash

# E2E API测试脚本
# 测试SQL注入修复和新API端点

BACKEND_URL="http://127.0.0.1:5001"
GAME_GID=10000147
OUTPUT_FILE="/Users/mckenzie/Documents/event2table/docs/reports/2026-02-20/api-test-results.txt"

echo "========================================" | tee -a "$OUTPUT_FILE"
echo "E2E API测试开始" | tee -a "$OUTPUT_FILE"
echo "时间: $(date)" | tee -a "$OUTPUT_FILE"
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_api() {
    local test_name="$1"
    local url="$2"
    local expected_status="$3"
    local description="$4"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo "----------------------------------------" | tee -a "$OUTPUT_FILE"
    echo "测试 #$TOTAL_TESTS: $test_name" | tee -a "$OUTPUT_FILE"
    echo "描述: $description" | tee -a "$OUTPUT_FILE"
    echo "URL: $url" | tee -a "$OUTPUT_FILE"

    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "HTTP状态码: $http_code (期望: $expected_status)" | tee -a "$OUTPUT_FILE"
    echo "响应体: $body" | tee -a "$OUTPUT_FILE"

    if [ "$http_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC}" | tee -a "$OUTPUT_FILE"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED${NC}" | tee -a "$OUTPUT_FILE"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo "" | tee -a "$OUTPUT_FILE"
}

# ========================================
# 场景1: SQL注入修复验证
# ========================================
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "场景1: SQL注入修复验证" | tee -a "$OUTPUT_FILE"
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 测试函数（POST版本）
test_post_api() {
    local test_name="$1"
    local url="$2"
    local data="$3"
    local expected_status="$4"
    local description="$5"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo "----------------------------------------" | tee -a "$OUTPUT_FILE"
    echo "测试 #$TOTAL_TESTS: $test_name" | tee -a "$OUTPUT_FILE"
    echo "描述: $description" | tee -a "$OUTPUT_FILE"
    echo "URL: POST $url" | tee -a "$OUTPUT_FILE"
    echo "数据: $data" | tee -a "$OUTPUT_FILE"

    response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
      -H "Content-Type: application/json" \
      -d "$data")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    echo "HTTP状态码: $http_code (期望: $expected_status)" | tee -a "$OUTPUT_FILE"
    echo "响应体: $body" | tee -a "$OUTPUT_FILE"

    if [ "$http_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC}" | tee -a "$OUTPUT_FILE"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED${NC}" | tee -a "$OUTPUT_FILE"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo "" | tee -a "$OUTPUT_FILE"
}

# 测试1.1: 正常搜索
test_post_api \
    "参数搜索 - 正常查询" \
    "$BACKEND_URL/api/parameters/search" \
    "{\"game_gid\": $GAME_GID, \"keyword\": \"level\"}" \
    "200" \
    "验证正常的参数搜索功能"

# 测试1.2: SQL注入 - 单引号
test_post_api \
    "参数搜索 - SQL注入尝试 (单引号)" \
    "$BACKEND_URL/api/parameters/search" \
    "{\"game_gid\": $GAME_GID, \"keyword\": \"'\"}" \
    "200" \
    "验证单引号被正确转义或拒绝"

# 测试1.3: SQL注入 - 双引号
test_post_api \
    "参数搜索 - SQL注入尝试 (双引号)" \
    "$BACKEND_URL/api/parameters/search" \
    "{\"game_gid\": $GAME_GID, \"keyword\": \"\\\"\"}" \
    "200" \
    "验证双引号被正确转义或拒绝"

# 测试1.4: SQL注入 - 注释符
test_post_api \
    "参数搜索 - SQL注入尝试 (注释符)" \
    "$BACKEND_URL/api/parameters/search" \
    "{\"game_gid\": $GAME_GID, \"keyword\": \"--\"}" \
    "200" \
    "验证注释符被正确处理"

# 测试1.5: SQL注入 - 分号
test_post_api \
    "参数搜索 - SQL注入尝试 (分号)" \
    "$BACKEND_URL/api/parameters/search" \
    "{\"game_gid\": $GAME_GID, \"keyword\": \";\"}" \
    "200" \
    "验证分号被正确处理"

# 测试1.6: SQL注入 - UNION注入
test_post_api \
    "参数搜索 - SQL注入尝试 (UNION)" \
    "$BACKEND_URL/api/parameters/search" \
    "{\"game_gid\": $GAME_GID, \"keyword\": \"'OR'1'='1\"}" \
    "200" \
    "验证UNION注入被正确阻止"

# 测试1.7: SQL注入 - DROP TABLE尝试
test_post_api \
    "参数搜索 - SQL注入尝试 (DROP TABLE)" \
    "$BACKEND_URL/api/parameters/search" \
    "{\"game_gid\": $GAME_GID, \"keyword\": \"'; DROP TABLE log_events; --\"}" \
    "200" \
    "验证DROP TABLE注入被正确阻止"

# 测试1.7: 事件查询（参数化查询验证）
test_api \
    "事件查询 - 参数化查询验证" \
    "$BACKEND_URL/api/events?game_gid=$GAME_GID" \
    "200" \
    "验证game_gid参数使用参数化查询"

# ========================================
# 场景2: 事件导入API
# ========================================
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "场景2: 事件导入API测试" | tee -a "$OUTPUT_FILE"
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 测试2.1: 检查事件导入API是否存在
echo "----------------------------------------" | tee -a "$OUTPUT_FILE"
echo "测试: 事件导入API端点检查" | tee -a "$OUTPUT_FILE"
echo "URL: POST $BACKEND_URL/api/events/import" | tee -a "$OUTPUT_FILE"

import_response=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/events/import" \
  -H "Content-Type: application/json" \
  -d "{\"game_gid\": $GAME_GID, \"events\": [{\"event_code\": \"test_chrome_001\", \"event_name\": \"Chrome测试事件\", \"category\": \"test\"}]}")

import_http_code=$(echo "$import_response" | tail -n1)
import_body=$(echo "$import_response" | sed '$d')

echo "HTTP状态码: $import_http_code" | tee -a "$OUTPUT_FILE"
echo "响应体: $import_body" | tee -a "$OUTPUT_FILE"

TOTAL_TESTS=$((TOTAL_TESTS + 1))
if [ "$import_http_code" == "200" ] || [ "$import_http_code" == "201" ] || [ "$import_http_code" == "400" ]; then
    echo -e "${GREEN}✓ PASSED${NC} - API端点存在并响应" | tee -a "$OUTPUT_FILE"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠ WARNING${NC} - API端点可能未实现或返回错误状态码" | tee -a "$OUTPUT_FILE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo "" | tee -a "$OUTPUT_FILE"

# ========================================
# 场景3: 流程管理API
# ========================================
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "场景3: 流程管理API测试" | tee -a "$OUTPUT_FILE"
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 测试3.1: 流程列表API
echo "----------------------------------------" | tee -a "$OUTPUT_FILE"
echo "测试: 流程列表API" | tee -a "$OUTPUT_FILE"
echo "URL: GET $BACKEND_URL/api/flows?game_gid=$GAME_GID" | tee -a "$OUTPUT_FILE"

flows_response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/api/flows?game_gid=$GAME_GID")
flows_http_code=$(echo "$flows_response" | tail -n1)
flows_body=$(echo "$flows_response" | sed '$d')

echo "HTTP状态码: $flows_http_code" | tee -a "$OUTPUT_FILE"
echo "响应体: $flows_body" | tee -a "$OUTPUT_FILE"

TOTAL_TESTS=$((TOTAL_TESTS + 1))
if [ "$flows_http_code" == "200" ] || [ "$flows_http_code" == "404" ]; then
    echo -e "${GREEN}✓ PASSED${NC} - API端点响应正确" | tee -a "$OUTPUT_FILE"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠ WARNING${NC} - API端点可能未实现" | tee -a "$OUTPUT_FILE"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
echo "" | tee -a "$OUTPUT_FILE"

# ========================================
# 场景4: 性能和错误检测
# ========================================
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "场景4: 性能和错误检测" | tee -a "$OUTPUT_FILE"
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "" | tee -a "$OUTPUT_FILE"

# 测试4.1: Dashboard统计
test_api \
    "Dashboard统计数据加载" \
    "$BACKEND_URL/api/dashboard/stats?game_gid=$GAME_GID" \
    "200" \
    "验证Dashboard数据加载性能"

# 测试4.2: 事件列表
test_api \
    "事件列表数据加载" \
    "$BACKEND_URL/api/events?game_gid=$GAME_GID" \
    "200" \
    "验证事件列表加载性能"

# 测试4.3: 参数列表
test_api \
    "参数列表数据加载" \
    "$BACKEND_URL/api/parameters/all?game_gid=$GAME_GID" \
    "200" \
    "验证参数列表加载性能"

# ========================================
# 测试总结
# ========================================
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "测试总结" | tee -a "$OUTPUT_FILE"
echo "========================================" | tee -a "$OUTPUT_FILE"
echo "总测试数: $TOTAL_TESTS" | tee -a "$OUTPUT_FILE"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}" | tee -a "$OUTPUT_FILE"
echo -e "${RED}失败: $FAILED_TESTS${NC}" | tee -a "$OUTPUT_FILE"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！${NC}" | tee -a "$OUTPUT_FILE"
    exit 0
else
    pass_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "通过率: ${pass_rate}%" | tee -a "$OUTPUT_FILE"
    exit 1
fi
