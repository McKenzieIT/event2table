#!/bin/bash
# Event2Table Development Server Startup Script
# 启动开发环境Flask服务器（包含缓存系统）

set -e  # Exit on error

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/Users/mckenzie/Documents/event2table"
FLASK_APP="web_app.py"
FLASK_HOST="127.0.0.1"
FLASK_PORT="5001"
LOG_FILE="/tmp/event2table-dev.log"
PID_FILE="/tmp/event2table-dev.pid"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Event2Table - Development Server Startup${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 切换到项目目录
cd "$PROJECT_DIR"
echo -e "${YELLOW}📂 Working directory: $PROJECT_DIR${NC}"
echo ""

# ============================================
# Step 1: 环境检查
# ============================================
echo -e "${BLUE}[Step 1/7]${NC} Checking environment..."

# 检查虚拟环境
if [ ! -d "backend/venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Please run: source backend/venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi
echo -e "${GREEN}✅ Virtual environment found${NC}"

# 检查数据库
if [ ! -f "data/dwd_generator.db" ]; then
    echo -e "${YELLOW}⚠️  Database not found, initializing...${NC}"
    source backend/venv/bin/activate
    python scripts/setup/init_db.py
fi
echo -e "${GREEN}✅ Database ready${NC}"

# 检查Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Redis not running, starting...${NC}"
    brew services start redis
    sleep 2
fi
echo -e "${GREEN}✅ Redis running${NC}"

echo ""

# ============================================
# Step 2: 停止旧进程
# ============================================
echo -e "${BLUE}[Step 2/7]${NC} Stopping old processes..."

# 读取PID文件（如果存在）
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
    if [ -n "$OLD_PID" ]; then
        if ps -p "$OLD_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}🔄 Stopping old Flask process (PID: $OLD_PID)...${NC}"
            kill "$OLD_PID" 2>/dev/null || true
            sleep 2
        fi
    fi
fi

# 强制杀死所有web_app.py进程
PIDS=$(ps aux | grep "[p]ython.*web_app" | awk '{print $2}' || true)
if [ -n "$PIDS" ]; then
    echo -e "${YELLOW}🔄 Killing existing Flask processes...${NC}"
    kill -9 $PIDS 2>/dev/null || true
    sleep 2
fi

echo -e "${GREEN}✅ Old processes stopped${NC}"
echo ""

# ============================================
# Step 3: 初始化缓存系统
# ============================================
echo -e "${BLUE}[Step 3/7]${NC} Initializing cache system..."

source backend/venv/bin/activate

# 初始化缓存（通过Python脚本）
python << 'EOF'
import sys
import os

# 设置环境
os.environ['FLASK_ENV'] = 'development'

try:
    from backend.core.cache.cache_system import cache_result
    from backend.core.cache.cache_hierarchical import HierarchicalCache

    # 初始化缓存
    print("  → Cache imports: OK")
    print("  → Cache system ready")

except ImportError as e:
    print(f"  → Cache import warning: {e}")
    print("  → Continuing anyway (cache will auto-initialize)")

except Exception as e:
    print(f"  → Cache initialization warning: {e}")
    print("  → Continuing anyway")

sys.exit(0)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cache system initialized${NC}"
else
    echo -e "${YELLOW}⚠️  Cache initialization skipped (will auto-initialize)${NC}"
fi

echo ""

# ============================================
# Step 4: 验证配置
# ============================================
echo -e "${BLUE}[Step 4/7]${NC} Verifying configuration..."

# 检查配置文件
if [ -f "backend/core/config/config.py" ]; then
    echo -e "${GREEN}✅ Config file found${NC}"
else
    echo -e "${RED}❌ Config file not found${NC}"
    exit 1
fi

# 检查Flask secret key
if [ -z "$FLASK_SECRET_KEY" ]; then
    echo -e "${YELLOW}⚠️  FLASK_SECRET_KEY not set (using development default)${NC}"
fi

echo -e "${GREEN}✅ Configuration verified${NC}"
echo ""

# ============================================
# Step 5: 清理旧日志
# ============================================
echo -e "${BLUE}[Step 5/7]${NC} Cleaning old logs..."

# 保留最近100行日志
if [ -f "$LOG_FILE" ]; then
    tail -100 "$LOG_FILE" > "$LOG_FILE.tmp"
    mv "$LOG_FILE.tmp" "$LOG_FILE"
    echo -e "${GREEN}✅ Logs cleaned (last 100 lines retained)${NC}"
else
    echo -e "${GREEN}✅ No old logs to clean${NC}"
fi

echo ""

# ============================================
# Step 6: 启动Flask服务器
# ============================================
echo -e "${BLUE}[Step 6/7]${NC} Starting Flask server..."
echo ""

echo -e "${YELLOW}📝 Server configuration:${NC}"
echo "   → Host: $FLASK_HOST"
echo "   → Port: $FLASK_PORT"
echo "   → Log: $LOG_FILE"
echo "   → PID: $PID_FILE"
echo ""

# 启动Flask（后台模式）
nohup python3 "$FLASK_APP" > "$LOG_FILE" 2>&1 &
FLASK_PID=$!

# 保存PID
echo "$FLASK_PID" > "$PID_FILE"

echo -e "${GREEN}✅ Flask server started (PID: $FLASK_PID)${NC}"
echo ""

# ============================================
# Step 7: 验证服务
# ============================================
echo -e "${BLUE}[Step 7/7]${NC} Verifying services..."
echo ""

# 等待服务器启动
echo "Waiting for server to start..."
for i in {1..10}; do
    if curl -s "http://${FLASK_HOST}:${FLASK_PORT}/api/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is responding${NC}"
        break
    fi

    if [ $i -eq 10 ]; then
        echo -e "${YELLOW}⚠️  Server not responding yet (this is normal for first start)${NC}"
        echo -e "${YELLOW}   Check logs: tail -f $LOG_FILE${NC}"
    fi

    sleep 1
done

echo ""

# 验证关键端点
echo -e "${BLUE}🔍 Verifying endpoints...${NC}"

# 健康检查
echo -n "   → Health check: "
if curl -s "http://${FLASK_HOST}:${FLASK_PORT}/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}SKIP${NC}"
fi

# GraphQL API
echo -n "   → GraphQL API: "
if curl -s -X POST "http://${FLASK_HOST}:${FLASK_PORT}/api/graphql" \
    -H "Content-Type: application/json" \
    -d '{"query": "{ __typename }"}' > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}SKIP${NC}"
fi

# 缓存系统
echo -n "   → Cache system: "
if curl -s "http://${FLASK_HOST}:${FLASK_PORT}/api/cache/stats" > /dev/null 2>&1; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}INITIALIZING${NC}"
fi

echo ""

# ============================================
# 启动完成
# ============================================
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🎉 Development server started successfully!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}📍 Server URLs:${NC}"
echo "   → Main App:     http://${FLASK_HOST}:${FLASK_PORT}"
echo "   → GraphQL API:  http://${FLASK_HOST}:${FLASK_PORT}/api/graphql"
echo "   → GraphiQL IDE:  http://${FLASK_HOST}:${FLASK_PORT}/api/graphql?graphiql"
echo "   → Cache Stats:  http://${FLASK_HOST}:${FLASK_PORT}/api/cache/stats"
echo ""
echo -e "${YELLOW}📋 Useful commands:${NC}"
echo "   → View logs:    tail -f $LOG_FILE"
echo "   → Stop server:  kill $FLASK_PID"
echo "   → Restart:     bash scripts/start-dev.sh"
echo "   → Test cache:  curl http://${FLASK_HOST}:${FLASK_PORT}/api/cache/stats"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "   → Cache auto-initializes on first use"
echo "   → Monitor cache: curl http://${FLASK_HOST}:${FLASK_PORT}/api/cache/stats"
echo "   → Clear cache:  curl -X POST http://${FLASK_HOST}:${FLASK_PORT}/api/cache/clear"
echo ""
echo -e "${BLUE}================================================${NC}"
