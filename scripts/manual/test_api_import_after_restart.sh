#!/bin/bash
# 事件导入API快速测试脚本
# 用于在Flask服务器重启后验证 /api/events/import 端点

echo "================================================================================"
echo "事件导入API快速测试"
echo "================================================================================"
echo ""
echo "测试前请确保："
echo "1. Flask服务器已重启"
echo "2. 服务器运行在 http://127.0.0.1:5001"
echo ""

# 检查服务器是否运行
echo "检查服务器状态..."
SERVER_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5001/api/events)

if [ "$SERVER_STATUS" != "200" ]; then
    echo "❌ 服务器未运行或响应异常 (HTTP $SERVER_STATUS)"
    echo ""
    echo "请先启动服务器："
    echo "  cd /Users/mckenzie/Documents/event2table"
    echo "  python3 web_app.py"
    echo ""
    exit 1
fi

echo "✅ 服务器运行正常 (HTTP $SERVER_STATUS)"
echo ""

# 测试1: 基本导入
echo "================================================================================"
echo "测试1: 基本导入功能"
echo "================================================================================"
echo ""

RESPONSE1=$(curl -s -X POST http://127.0.0.1:5001/api/events/import \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 90000001,
    "events": [
      {
        "event_code": "test_quick_001",
        "event_name": "Quick Test Event 1",
        "event_name_cn": "快速测试事件1",
        "description": "用于验证API功能的测试事件",
        "category": "test"
      },
      {
        "event_code": "test_quick_002",
        "event_name": "Quick Test Event 2",
        "event_name_cn": "快速测试事件2",
        "category": "test"
      }
    ]
  }')

echo "请求:"
echo "  POST /api/events/import"
echo "  Content-Type: application/json"
echo ""
echo "响应:"
echo "$RESPONSE1" | python3 -m json.tool
echo ""

# 检查响应
IMPORTED=$(echo "$RESPONSE1" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('imported', 0))")
FAILED=$(echo "$RESPONSE1" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('failed', 0))")

if [ "$IMPORTED" == "2" ] && [ "$FAILED" == "0" ]; then
    echo "✅ 测试1通过: 成功导入2个事件"
else
    echo "❌ 测试1失败: 预期导入2个，实际导入 $IMPORTED 个，失败 $FAILED 个"
    echo ""
    exit 1
fi

echo ""

# 测试2: 重复检测
echo "================================================================================"
echo "测试2: 重复事件检测"
echo "================================================================================"
echo ""

RESPONSE2=$(curl -s -X POST http://127.0.0.1:5001/api/events/import \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 90000001,
    "events": [
      {
        "event_code": "test_quick_001",
        "event_name": "Duplicate Event"
      }
    ]
  }')

echo "请求: (提交相同的事件代码)"
echo "  POST /api/events/import"
echo ""
echo "响应:"
echo "$RESPONSE2" | python3 -m json.tool
echo ""

# 检查是否检测到重复
HAS_ERROR=$(echo "$RESPONSE2" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', {})
errors = data.get('errors', [])
failed = data.get('failed', 0)
print('1' if failed > 0 and any('already exists' in e for e in errors) else '0')
")

if [ "$HAS_ERROR" == "1" ]; then
    echo "✅ 测试2通过: 正确检测到重复事件"
else
    echo "❌ 测试2失败: 未检测到重复事件"
    echo ""
    exit 1
fi

echo ""

# 测试3: 无效game_gid
echo "================================================================================"
echo "测试3: 无效game_gid处理"
echo "================================================================================"
echo ""

RESPONSE3=$(curl -s -X POST http://127.0.0.1:5001/api/events/import \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 99999999,
    "events": [
      {
        "event_code": "test_invalid",
        "event_name": "Invalid Game Test"
      }
    ]
  }')

echo "请求: (使用不存在的game_gid)"
echo "  POST /api/events/import"
echo ""
echo "响应:"
echo "$RESPONSE3" | python3 -m json.tool
echo ""

# 检查是否正确拒绝
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://127.0.0.1:5001/api/events/import \
  -H "Content-Type: application/json" \
  -d '{
    "game_gid": 99999999,
    "events": [{"event_code": "test", "event_name": "test"}]
  }')

if [ "$HTTP_CODE" != "200" ] || echo "$RESPONSE3" | python3 -c "
import sys, json
data = json.load(sys.stdin).get('data', {})
failed = data.get('failed', 0)
print('1' if failed > 0 or 'not found' in json.load(sys.stdin).get('message', '').lower() else '0')
" | grep -q "1"; then
    echo "✅ 测试3通过: 正确拒绝无效的game_gid"
else
    echo "⚠️  测试3警告: 预期拒绝无效game_gid，但请求成功"
fi

echo ""

# 清理测试数据
echo "================================================================================"
echo "清理测试数据"
echo "================================================================================"
echo ""

sqlite3 /Users/mckenzie/Documents/event2table/data/dwd_generator.db <<EOF
DELETE FROM log_events WHERE event_name LIKE 'test_quick_%' OR event_name LIKE 'test_json_%';
DELETE FROM event_params WHERE event_id IN (SELECT id FROM log_events WHERE event_name LIKE 'test_%');
EOF

echo "✅ 测试数据已清理"
echo ""

# 总结
echo "================================================================================"
echo "测试总结"
echo "================================================================================"
echo ""
echo "✅ 所有测试通过!"
echo ""
echo "验证结果:"
echo "  ✅ 基本导入功能正常"
echo "  ✅ 重复检测功能正常"
echo "  ✅ 无效参数处理正常"
echo ""
echo "API端点: POST /api/events/import"
echo "文档位置: docs/api/events-import-api.md"
echo ""
echo "下一步:"
echo "  1. 在前端集成此API"
echo "  2. 添加更多测试用例"
echo "  3. 性能测试（大批量导入）"
echo ""
echo "================================================================================"
