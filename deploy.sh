#!/bin/bash

# Event2Table 自动化部署脚本
# 用于快速部署生产版本
# 使用方法: ./deploy.sh [环境]

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="event2table"
FRONTEND_DIR="/Users/mckenzie/Documents/event2table/frontend"
DEPLOY_DIR="/var/www/${PROJECT_NAME}/frontend/dist"
NGINX_CONF="/Users/mckenzie/Documents/event2table/frontend/nginx/event2table.conf"
NGINX_SITES="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
BACKUP_DIR="/var/backups/${PROJECT_NAME}"

# 环境参数
ENV=${1:-production}

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Event2Table 生产环境部署脚本${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${YELLOW}环境: ${ENV}${NC}"
echo ""

# 检查 root 权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}[1/7] 检查依赖...${NC}"
    
    # 检查 Nginx
    if ! command -v nginx &> /dev/null; then
        echo -e "${YELLOW}Nginx 未安装，正在安装...${NC}"
        if command -v apt-get &> /dev/null; then
            apt-get update && apt-get install -y nginx
        elif command -v yum &> /dev/null; then
            yum install -y nginx
        else
            echo -e "${RED}错误: 无法安装 Nginx，请手动安装${NC}"
            exit 1
        fi
    fi
    
    # 检查目录
    mkdir -p /var/www/${PROJECT_NAME}/frontend
    mkdir -p ${BACKUP_DIR}
    mkdir -p ${NGINX_SITES}
    
    echo -e "${GREEN}✓ 依赖检查完成${NC}"
}

# 备份当前版本
backup_current() {
    echo -e "${BLUE}[2/7] 备份当前版本...${NC}"
    
    if [ -d "${DEPLOY_DIR}" ]; then
        BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
        cp -r ${DEPLOY_DIR} ${BACKUP_DIR}/${BACKUP_NAME}
        echo -e "${GREEN}✓ 已备份到: ${BACKUP_DIR}/${BACKUP_NAME}${NC}"
    else
        echo -e "${YELLOW}⚠ 首次部署，无备份${NC}"
    fi
}

# 构建前端
build_frontend() {
    echo -e "${BLUE}[3/7] 构建前端...${NC}"
    
    cd ${FRONTEND_DIR}
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安装依赖...${NC}"
        npm install
    fi
    
    # 清理旧构建
    rm -rf dist
    
    # 执行构建
    echo -e "${YELLOW}执行生产构建...${NC}"
    npm run build
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 构建失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 构建完成${NC}"
    echo -e "${GREEN}  构建大小: $(du -sh dist | cut -f1)${NC}"
}

# 复制文件到部署目录
deploy_files() {
    echo -e "${BLUE}[4/7] 部署文件...${NC}"
    
    # 清空并复制新文件
    rm -rf ${DEPLOY_DIR}
    cp -r ${FRONTEND_DIR}/dist ${DEPLOY_DIR}
    
    # 设置权限
    chown -R www-data:www-data ${DEPLOY_DIR}
    chmod -R 755 ${DEPLOY_DIR}
    
    echo -e "${GREEN}✓ 文件已部署到: ${DEPLOY_DIR}${NC}"
}

# 配置 Nginx
configure_nginx() {
    echo -e "${BLUE}[5/7] 配置 Nginx...${NC}"
    
    # 复制配置文件
    cp ${NGINX_CONF} ${NGINX_SITES}/${PROJECT_NAME}.conf
    
    # 启用站点（如果是首次部署）
    if [ ! -L "${NGINX_ENABLED}/${PROJECT_NAME}.conf" ]; then
        ln -s ${NGINX_SITES}/${PROJECT_NAME}.conf ${NGINX_ENABLED}/${PROJECT_NAME}.conf
        echo -e "${GREEN}✓ 已启用 Nginx 站点${NC}"
    fi
    
    # 检查配置
    nginx -t
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: Nginx 配置测试失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Nginx 配置测试通过${NC}"
}

# 重启服务
restart_services() {
    echo -e "${BLUE}[6/7] 重启服务...${NC}"
    
    # 重启 Nginx
    systemctl restart nginx
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: Nginx 重启失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Nginx 已重启${NC}"
    
    # 检查后端服务
    if ! pgrep -f "python.*web_app.py" > /dev/null; then
        echo -e "${YELLOW}⚠ 后端服务未运行，请手动启动:${NC}"
        echo -e "${YELLOW}  cd /Users/mckenzie/Documents/event2table && python web_app.py${NC}"
    else
        echo -e "${GREEN}✓ 后端服务运行正常${NC}"
    fi
}

# 健康检查
health_check() {
    echo -e "${BLUE}[7/7] 健康检查...${NC}"
    
    # 等待服务启动
    sleep 2
    
    # 检查 HTTP 响应
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
    
    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓ HTTP 状态: 200 OK${NC}"
    else
        echo -e "${RED}✗ HTTP 状态: ${HTTP_CODE}${NC}"
        echo -e "${YELLOW}请检查 Nginx 错误日志: /var/log/nginx/error.log${NC}"
    fi
    
    # 检查 API 响应
    API_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/games || echo "000")
    if [ "$API_CODE" == "200" ]; then
        echo -e "${GREEN}✓ API 状态: 200 OK${NC}"
    else
        echo -e "${YELLOW}⚠ API 状态: ${API_CODE} (后端服务可能未启动)${NC}"
    fi
}

# 显示部署信息
show_info() {
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  部署成功！${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo -e "${BLUE}访问地址:${NC}"
    echo -e "  本地: http://localhost"
    echo -e "  网络: http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo -e "${BLUE}文件位置:${NC}"
    echo -e "  前端: ${DEPLOY_DIR}"
    echo -e "  Nginx: ${NGINX_SITES}/${PROJECT_NAME}.conf"
    echo -e "  日志: /var/log/nginx/"
    echo ""
    echo -e "${BLUE}常用命令:${NC}"
    echo -e "  查看日志: tail -f /var/log/nginx/event2table-access.log"
    echo -e "  重启 Nginx: sudo systemctl restart nginx"
    echo -e "  重载配置: sudo nginx -s reload"
    echo ""
    echo -e "${YELLOW}如需回滚:${NC}"
    echo -e "  备份目录: ${BACKUP_DIR}"
    echo ""
}

# 主流程
main() {
    check_root
    check_dependencies
    backup_current
    build_frontend
    deploy_files
    configure_nginx
    restart_services
    health_check
    show_info
}

# 执行
main
