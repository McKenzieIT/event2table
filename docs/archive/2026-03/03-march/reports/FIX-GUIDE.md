# Event2Table 前端加载问题修复指南

**问题日期**: 2026-03-03
**严重程度**: P0 - 阻塞性
**状态**: 待修复

---

## 🚨 问题摘要

所有 E2E 测试失败，因为前端应用卡在 "Loading Event2Table..." 状态，无法正常加载。

**错误**:
```
Error: The requested module '/node_modules/.vite/deps/@apollo_client.js?v=b0e01465'
does not provide an export named 'ApolloProvider'
```

---

## 🛠️ 修复步骤

### 方案 1: 清理 Vite 缓存（推荐，最快）

```bash
# 1. 停止前端开发服务器
# 按 Ctrl+C 停止当前运行的 npm run dev

# 2. 清理 Vite 缓存
cd /Users/mckenzie/Documents/event2table/frontend
rm -rf node_modules/.vite

# 3. 重启前端开发服务器
npm run dev
```

**验证步骤**:
1. 打开浏览器访问 http://localhost:5173
2. 页面应该正常显示（不再卡在 "Loading Event2Table..."）
3. 打开浏览器控制台（F12），确认没有错误

---

### 方案 2: 完全重新安装依赖（如果方案1无效）

```bash
# 1. 停止所有服务器
# 按 Ctrl+C 停止 npm run dev 和 python web_app.py

# 2. 进入前端目录
cd /Users/mckenzie/Documents/event2table/frontend

# 3. 删除 node_modules 和锁文件
rm -rf node_modules
rm -rf package-lock.json

# 4. 重新安装依赖
npm install

# 5. 重启前端开发服务器
npm run dev
```

**预期耗时**: 3-5 分钟（取决于网络速度）

---

### 方案 3: 检查并修复 Apollo Client（如果方案2无效）

```bash
# 1. 检查 Apollo Client 版本
cd /Users/mckenzie/Documents/event2table/frontend
npm list @apollo/client

# 2. 如果版本过低或有问题，重新安装
npm uninstall @apollo/client
npm install @apollo/client@latest

# 3. 重启前端开发服务器
npm run dev
```

---

## ✅ 修复验证

### 步骤 1: 手动验证

1. 打开浏览器访问 http://localhost:5173
2. 确认页面正常显示（Dashboard 应该可见）
3. 打开开发者工具（F12）→ Console 标签页
4. 确认没有红色错误信息

### 步骤 2: 自动化测试验证

```bash
# 运行快速冒烟测试
cd /Users/mckenzie/Documents/event2table/frontend
npm run test:e2e:quick

# 预期结果：所有6个测试应该通过
# ✘   2 [chromium] › homepage loads
# ✘   4 [chromium] › games page loads
# ... 等
```

### 步骤 3: 完整测试验证

```bash
# 运行完整冒烟测试
npm run test:e2e:smoke

# 预期结果：所有测试应该通过
```

---

## 🔍 根本原因分析

### 为什么会出现这个问题？

1. **Vite 依赖预构建缓存损坏**:
   - Vite 会预构建依赖到 `node_modules/.vite` 目录
   - 当依赖更新或配置变化时，缓存可能损坏
   - 导致模块导出不匹配

2. **Apollo Client 版本问题**:
   - `@apollo/client` 包可能有版本冲突
   - 不同版本的导出可能不一致

3. **Node.js 版本变化**:
   - 如果 Node.js 版本升级，可能需要重新构建依赖

---

## 📋 预防措施

### 定期清理 Vite 缓存

```bash
# 每周或每次大更新后清理
cd frontend
rm -rf node_modules/.vite
npm run dev
```

### 使用 .gitignore 排除缓存

确保 `.gitignore` 包含：
```
node_modules/.vite
dist
```

### 监控依赖更新

```bash
# 定期检查过时的依赖
npm outdated

# 谨慎更新依赖
npm update
```

---

## 🚨 如果问题仍然存在

### 收集诊断信息

```bash
# 1. 检查 Vite 版本
npm list vite

# 2. 检查 React 版本
npm list react

# 3. 检查 Apollo Client 版本
npm list @apollo/client

# 4. 检查 Node.js 版本
node --version
npm --version

# 5. 查看完整错误日志
# 在浏览器开发者工具中查看 Console 和 Network 标签页
```

### 寻求帮助

1. 保存浏览器控制台的完整错误日志
2. 保存 `npm list` 的输出
3. 保存 Vite 配置文件 (`vite.config.ts`)
4. 联系开发团队或查看 GitHub Issues

---

## 📊 影响评估

### 用户影响
- **当前**: 用户无法访问应用
- **修复后**: 应用恢复正常

### 开发影响
- **当前**: 所有 E2E 测试失败
- **修复后**: 测试可以正常运行

### 时间评估
- **方案 1**: 1-2 分钟
- **方案 2**: 3-5 分钟
- **方案 3**: 5-10 分钟

---

**修复优先级**: P0 - 立即修复
**预期修复时间**: 5 分钟内
**验证时间**: 10 分钟

---

**更新时间**: 2026-03-03 22:45:00 UTC
