#!/bin/bash

# Event2Table 开发环境一键启动脚本（改进版）
# 同时启动Flask后端和Vite前端服务器

set -e  # 遇到错误立即退出
NC='\033[0m'  # 无色
GREEN='\033[0;32m'  # 绿色
YELLOW='\033[0;33m'  # 黄色
RED='\033[0;31m'  # 红色

# 日志文件
LOG_DIR="logs"
FLASK_LOG="$LOG_DIR/flask.log"
VITE_LOG="$LOG_DIR/vite.log"

# 清空日志函数
clear_logs() {
    echo -e "${NC}清空旧日志...${NC}"
    > "$FLASK_LOG"
    > "$VITE_LOG"
    echo ""
}

# 启动Flask后端
start_flask() {
    echo -e "${YELLOW}正在启动Flask后端...${NC}"
    cd /Users/mckenzie/Documents/event2table

    # 🔧 强制清理：确保端口可用，缓存清理
    echo -e "${YELLOW}🧹 清理端口和缓存...${NC}"

    # 杀掉占用5001端口的所有进程
    lsof -i :5001 2>/dev/null | awk '{print $2}' | xargs kill -9 2>/dev/null

    # 清理Python缓存
    find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find backend/core -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

    sleep 2
    echo -e "${GREEN}✅ 清理完成${NC}"

    # 使用后台运行，让脚本可以继续
    if [[ "$1" == "--no-flask" ]]; then
        echo -e "${YELLOW}跳过Flask启动${NC}"
        FLASK_PID=""
    else
        # 使用虚拟环境启动Flask
        if [ -d "backend/venv" ]; then
            source backend/venv/bin/activate && python web_app.py > "$FLASK_LOG" 2>&1 &
        else
            python web_app.py > "$FLASK_LOG" 2>&1 &
        fi
        FLASK_PID=$!
        sleep 2

        # 等待Flask启动完成（内联版本）
        for i in {1..30}; do
            if ps -p $FLASK_PID > /dev/null; then
                echo -e "${GREEN}✓ Flask后端启动成功 (PID: $FLASK_PID)${NC}"
                break
            fi
        done

        if ps -p $FLASK_PID > /dev/null; then
            echo -e "${GREEN}═════════════════${NC}"
            echo -e "${GREEN}Flask后端已就绪！${NC}"
            echo -e " 端口: ${RED}5001${NC}"
            echo -e " 状态: ${GREEN}运行中${NC}"
            echo ""
            break
        else
            echo -e "${RED}✗ Flask后端启动失败${NC}"
            exit 1
        fi
}

# 启动Vite前端服务器
start_vite() {
    echo -e "${YELLOW}正在启动Vite前端服务器...${NC}"
    cd /Users/mckenzie/Documents/event2table/frontend

    # 优先使用直接node路径（更可靠）
    local VITE_CMD="/usr/local/bin/node node_modules/vite/bin/vite.js"

    echo -e "${YELLOW}执行: $VITE_CMD${NC}"
    echo -e "参数: --host 0.0.0.0 --port 5173"
    echo ""

    # 使用后台运行，让脚本可以继续
    $VITE_CMD > "$VITE_LOG" 2>&1 &
    VITE_PID=$!

    # 等待Vite启动完成（内联版本）
    echo -e "${YELLOW}等待Vite服务器初始化...${NC}"
    for i in {1..20}; do
        # 检查进程是否还在运行
        if ps -p $VITE_PID > /dev/null; then
            echo -e "${GREEN}✓ Vite服务器运行中 (PID: $VITE_PID)${NC}"
            break
        fi
        sleep 1
    done

    # 验证Vite是否正常响应
    if ps -p $VITE_PID > /dev/null; then
        echo -e "${GREEN}✓ Vite启动成功${NC}"
        echo -e "${GREEN}═══════════════════${NC}"
        echo -e "${GREEN}前端地址: http://localhost:5173${NC}"
        echo -e "${GREEN}后端地址: http://127.0.0.1:5001${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Vite启动失败${NC}"
        return 1
    fi
}

# 主启动逻辑
main() {
    # 清空日志
    clear_logs

    # 检查端口
    echo -e "${YELLOW}═══════════════════${NC}"
    echo -e "${GREEN}Event2Table 开发环境启动脚本${NC}"
    echo -e ""

    # 显示菜单
    echo -e "${GREEN}1) 启动开发环境${NC}"
    echo -e "${GREEN}2) 仅启动Flask后端${NC}"
    echo -e "${GREEN}3) 仅启动Vite前端${NC}"
    echo -e "${GREEN}4) 启动并测试（推荐）${NC}"
    echo -e "${YELLOW}0) 退出${NC}"
    echo ""
    echo -e "${YELLOW}正在执行启动流程...${NC}"

    # 读取用户选择
    read -p "请选择操作 (1/2/3/4/0): " choice

    case $choice in
        1)
            main
            ;;
        2)
            start_flask
            ;;
        3)
            start_vite
            ;;
        4)
            start_flask
            start_vite
            ;;
        0)
            echo -e "${RED}无效选择，退出${NC}"
            exit 1
            ;;
        esac
    echo -e "${YELLOW}正在执行启动流程...${NC}"
}

# 信号处理
trap 'echo -e "${RED}收到中断信号，正在关闭所有服务器...${NC}"; kill $FLASK_PID $VITE_PID 2>/dev/null; exit' INT TERM
