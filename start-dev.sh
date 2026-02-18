#!/bin/bash

# Event2Table 开发环境启动脚本
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# 日志文件（使用绝对路径）
PROJECT_DIR="/Users/mckenzie/Documents/event2table"
FLASK_LOG="$PROJECT_DIR/logs/flask.log"
VITE_LOG="$PROJECT_DIR/logs/vite.log"

# 清理端口
cleanup_ports() {
    echo "清理端口和进程..."
    lsof -i :5001 -t 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -i :5173 -t 2>/dev/null | xargs kill -9 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    sleep 2
}

# 启动Flask后端
start_flask() {
    echo -e "${YELLOW}启动Flask后端...${NC}"
    cd /Users/mckenzie/Documents/event2table

    if [ -f "backend/venv/bin/python" ]; then
        echo "使用虚拟环境: backend/venv"
        backend/venv/bin/python web_app.py > "$FLASK_LOG" 2>&1 &
    else
        echo "使用系统python3"
        python3 web_app.py > "$FLASK_LOG" 2>&1 &
    fi
    FLASK_PID=$!

    sleep 5

    if ps -p $FLASK_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Flask已启动 (PID: $FLASK_PID, 端口5001)${NC}"
        return 0
    else
        echo -e "${RED}✗ Flask启动失败，查看日志: $FLASK_LOG${NC}"
        return 1
    fi
}

# 启动Vite前端
start_vite() {
    echo -e "${YELLOW}启动Vite前端...${NC}"
    cd /Users/mckenzie/Documents/event2table/frontend

    # 确保logs目录存在
    mkdir -p ../logs

    npm run dev > "$VITE_LOG" 2>&1 &
    VITE_PID=$!

    sleep 5

    if ps -p $VITE_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Vite已启动 (PID: $VITE_PID, 端口5173)${NC}"
        return 0
    else
        echo -e "${RED}✗ Vite启动失败，查看日志: $VITE_LOG${NC}"
        return 1
    fi
}

# 显示菜单
show_menu() {
    echo ""
    echo -e "${GREEN}═══════════════════${NC}"
    echo -e "${GREEN}Event2Table 开发环境启动脚本${NC}"
    echo ""
    echo "1) 启动开发环境 (Flask + Vite)"
    echo "2) 仅启动Flask后端"
    echo "3) 仅启动Vite前端"
    echo "0) 退出"
    echo ""
}

# 主函数
main() {
    # 确保logs目录存在
    mkdir -p logs

    # 显示菜单
    show_menu

    # 读取选择
    read -p "请选择 (1/2/3/0): " choice

    case $choice in
        1)
            cleanup_ports
            start_flask || exit 1
            start_vite || exit 1
            ;;
        2)
            cleanup_ports
            start_flask || exit 1
            echo -e "${YELLOW}仅Flask模式，按Ctrl+C退出${NC}"
            sleep infinity
            ;;
        3)
            cleanup_ports
            start_vite || exit 1
            echo -e "${YELLOW}仅Vite模式，按Ctrl+C退出${NC}"
            sleep infinity
            ;;
        0)
            echo "退出"
            exit 0
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac

    # 显示成功信息
    echo ""
    echo -e "${GREEN}═══════════════════${NC}"
    echo -e "${GREEN}✓ 服务器已启动${NC}"
    echo -e "${GREEN}  前端: http://localhost:5173${NC}"
    echo -e "${GREEN}  后端: http://127.0.0.1:5001${NC}"
    echo -e "${YELLOW}  (Ctrl+C 退出)${NC}"
    echo -e "${GREEN}═══════════════════${NC}"
    echo ""

    # 等待中断
    trap 'echo -e "${YELLOW}正在关闭服务器...${NC}"; kill $FLASK_PID $VITE_PID 2>/dev/null; exit 0' INT TERM

    while true; do
        sleep 10
    done
}

# 启动
main "$@"
