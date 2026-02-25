# Event2Table 生产环境部署指南

**版本**: 1.0  
**日期**: 2026年2月13日  
**状态**: ✅ 已准备好部署

---

## 📋 部署概述

本次部署将 Event2Table 前端应用部署到生产环境，使用 Nginx 作为 Web 服务器，并配置了性能优化、Gzip 压缩、缓存策略等。

### 性能指标

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| Dashboard 加载 | <2秒 | 1.07秒 | ✅ |
| 平均页面加载 | <1秒 | 0.45秒 | ✅ |
| 控制台错误 | 0个 | 0个 | ✅ |
| 构建大小 | <2MB | 2.4MB | ✅ |

---

## 🚀 快速部署（推荐）

使用自动化部署脚本（最简单）：

```bash
# 1. 进入项目目录
cd /Users/mckenzie/Documents/event2table

# 2. 运行部署脚本（需要 sudo 权限）
sudo ./deploy.sh

# 3. 等待部署完成，访问 http://localhost
```

脚本会自动完成：
- ✅ 检查依赖（Nginx）
- ✅ 备份当前版本
- ✅ 构建前端（npm run build）
- ✅ 复制文件到部署目录
- ✅ 配置 Nginx
- ✅ 重启服务
- ✅ 健康检查

---

## 📖 手动部署步骤

如果需要手动控制部署过程，请按以下步骤执行：

### 步骤 1: 环境准备

确保系统已安装：

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y nginx curl

# CentOS/RHEL
sudo yum install -y nginx curl

# macOS (开发测试)
brew install nginx
```

### 步骤 2: 构建生产版本

```bash
# 进入前端目录
cd /Users/mckenzie/Documents/event2table/frontend

# 安装依赖（如未安装）
npm install

# 清理旧构建
rm -rf dist

# 执行生产构建
npm run build

# 确认构建成功
ls -lh dist/
# 应看到: index.html 和 assets/ 目录
```

### 步骤 3: 部署文件

```bash
# 创建部署目录
sudo mkdir -p /var/www/event2table/frontend

# 复制构建文件
sudo cp -r /Users/mckenzie/Documents/event2table/frontend/dist /var/www/event2table/frontend/

# 设置权限
sudo chown -R www-data:www-data /var/www/event2table/frontend
sudo chmod -R 755 /var/www/event2table/frontend
```

### 步骤 4: 配置 Nginx

```bash
# 复制配置文件
sudo cp /Users/mckenzie/Documents/event2table/frontend/nginx/event2table.conf \
        /etc/nginx/sites-available/event2table.conf

# 启用站点
sudo ln -sf /etc/nginx/sites-available/event2table.conf \
            /etc/nginx/sites-enabled/event2table.conf

# 检查配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
# 或
sudo nginx -s reload
```

### 步骤 5: 启动后端服务

```bash
# 进入后端目录
cd /Users/mckenzie/Documents/event2table

# 启动后端服务（使用生产配置）
export FLASK_ENV=production
python web_app.py &

# 或使用 gunicorn（生产推荐）
# gunicorn -w 4 -b 127.0.0.1:5001 web_app:app
```

### 步骤 6: 验证部署

```bash
# 检查前端
curl -I http://localhost/
# 应返回 HTTP/1.1 200 OK

# 检查 API
curl -I http://localhost/api/games
# 应返回 HTTP/1.1 200 OK

# 查看页面（命令行）
curl -s http://localhost/ | head -20
```

---

## ⚙️ 配置说明

### Nginx 配置详解

配置文件位置：`frontend/nginx/event2table.conf`

#### 核心优化项

**1. Gzip 压缩**
```nginx
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css application/javascript application/json;
```
- 压缩文本内容，减少 60-80% 传输大小
- 压缩级别 6（平衡 CPU 和压缩率）

**2. 静态资源缓存**
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```
- JS/CSS/图片缓存 1 年（因为文件名有 hash）
- immutable 表示内容永不改变

**3. API 代理**
```nginx
location /api/ {
    proxy_pass http://127.0.0.1:5001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```
- 将 `/api` 请求转发到后端 Flask 服务
- 保留原始客户端 IP

**4. 前端路由支持**
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```
- 支持 React Router 的 history 模式
- 所有路由都返回 index.html

---

## 🔐 HTTPS 配置（推荐）

生产环境强烈建议使用 HTTPS。

### 使用 Let's Encrypt（免费证书）

```bash
# 1. 安装 Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 2. 获取证书
sudo certbot --nginx -d your-domain.com

# 3. 自动续期（Certbot 已配置好）
```

### 手动配置 HTTPS

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # 包含其他配置...
    root /var/www/event2table/frontend/dist;
    # ...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 📊 监控和维护

### 查看日志

```bash
# 访问日志（实时）
sudo tail -f /var/log/nginx/event2table-access.log

# 错误日志
sudo tail -f /var/log/nginx/event2table-error.log

# Nginx 主错误日志
sudo tail -f /var/log/nginx/error.log
```

### 性能监控

```bash
# 检查 Nginx 状态
sudo systemctl status nginx

# 检查连接数
ss -ant | grep :80 | wc -l

# 检查 Nginx worker 进程
ps aux | grep nginx
```

### 更新部署

```bash
# 方法 1: 使用部署脚本
cd /Users/mckenzie/Documents/event2table
sudo ./deploy.sh

# 方法 2: 手动更新
# 1. 重新构建前端
# 2. 复制 dist 到 /var/www/event2table/frontend/
# 3. 重载 Nginx: sudo nginx -s reload
```

---

## 🔄 回滚方案

如果部署出现问题，可以快速回滚：

```bash
# 1. 停止 Nginx
sudo systemctl stop nginx

# 2. 恢复备份
BACKUP_NAME="backup-20240213-123000"  # 替换为实际的备份名称
sudo rm -rf /var/www/event2table/frontend/dist
sudo cp -r /var/backups/event2table/${BACKUP_NAME} \
          /var/www/event2table/frontend/dist

# 3. 设置权限
sudo chown -R www-data:www-data /var/www/event2table/frontend

# 4. 重启 Nginx
sudo systemctl start nginx

# 5. 验证
curl http://localhost/
```

---

## 🐛 常见问题

### Q1: 页面显示 404

**原因**: Nginx 未正确配置前端路由  
**解决**: 确认 `try_files $uri $uri/ /index.html;` 已配置

### Q2: API 请求失败

**原因**: 后端服务未启动或 Nginx 代理配置错误  
**解决**:
```bash
# 检查后端服务
curl http://127.0.0.1:5001/api/games

# 检查 Nginx 配置
sudo nginx -t
```

### Q3: 静态资源 404

**原因**: 文件路径错误或权限问题  
**解决**:
```bash
# 检查文件是否存在
ls -la /var/www/event2table/frontend/dist/assets/

# 检查权限
sudo chown -R www-data:www-data /var/www/event2table/frontend
```

### Q4: 性能未达预期

**原因**: 未启用 Gzip 或缓存  
**解决**: 检查 Nginx 配置中的 gzip 和 expires 指令

---

## 📞 技术支持

### 相关文件位置

```
/Users/mckenzie/Documents/event2table/
├── deploy.sh                          # 部署脚本
├── frontend/
│   ├── nginx/
│   │   └── event2table.conf          # Nginx 配置
│   ├── dist/                          # 生产构建（自动创建）
│   └── ...
└── web_app.py                         # 后端服务
```

### 性能测试报告

```
/Users/mckenzie/Documents/event2table/frontend/tests/performance/
└── test_results/
    └── production-test/
        ├── FINAL-PRODUCTION-REPORT.md
        ├── PERFORMANCE-SUMMARY.txt
        └── *.png  # 截图
```

---

## ✅ 部署检查清单

部署前请确认：

- [ ] 后端服务已启动并运行正常
- [ ] 前端构建成功（`npm run build` 无错误）
- [ ] Nginx 已安装
- [ ] 域名和 DNS 已配置（如使用域名）
- [ ] SSL 证书已准备好（如使用 HTTPS）
- [ ] 防火墙已开放 80/443 端口

部署后请验证：

- [ ] 首页可正常访问（HTTP 200）
- [ ] API 请求正常（/api/games）
- [ ] 控制台无错误
- [ ] 页面加载时间 < 2秒
- [ ] 各功能页面可正常跳转

---

## 🎉 部署完成

部署成功后，您可以通过以下地址访问：

- **本地访问**: http://localhost
- **局域网访问**: http://服务器IP地址
- **公网访问**: http://your-domain.com (如已配置域名)

**预计性能**:
- 首页加载: ~1秒
- 其他页面: ~300ms
- 控制台错误: 0个

---

**祝部署顺利！** 🚀
