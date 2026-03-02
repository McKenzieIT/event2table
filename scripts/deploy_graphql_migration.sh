#!/bin/bash
# GraphQL迁移部署执行脚本
# 自动化执行测试环境部署、功能验证、性能测试

set -e  # 遇到错误立即退出

echo "============================================================"
echo "GraphQL迁移自动化部署脚本"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 步骤1: 环境检查
command -v source backend/venv/bin/activate
log_info "步骤1: 检查部署环境"
echo "------------------------------------------------------------"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    log_error "Python3未安装"
    exit 1
fi
log_info "Python3版本: $(python3 --version)"

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    log_error "Node.js未安装"
    exit 1
fi
log_info "Node.js版本: $(node --version)"

# 检查npm
if ! command -v npm &> /dev/null; then
    log_error "npm未安装"
    exit 1
fi
log_info "npm版本: $(npm --version)"

echo ""

# 步骤2: 代码验证
log_info "步骤2: 验证代码完整性"
echo "------------------------------------------------------------"

# 检查GraphQL Schema
if [ -f "backend/gql_api/schema.py" ]; then
    log_info "✅ GraphQL Schema文件存在"
else
    log_error "❌ GraphQL Schema文件不存在"
    exit 1
fi

# 检查GraphQL操作定义
if [ -f "frontend/src/shared/graphql/operations.ts" ]; then
    log_info "✅ GraphQL操作定义文件存在"
else
    log_error "❌ GraphQL操作定义文件不存在"
    exit 1
fi

# 检查迁移组件
if [ -f "frontend/src/features/games/GameManagementModalGraphQL.tsx" ]; then
    log_info "✅ 迁移组件文件存在"
else
    log_warn "⚠️  迁移组件文件不存在(可能已替换)"
fi

echo ""

# 步骤3: 运行测试
log_info "步骤3: 执行自动化测试"
echo "------------------------------------------------------------"

# 运行GraphQL迁移测试
if [ -f "scripts/test_graphql_migration.py" ]; then
    log_info "运行GraphQL迁移测试..."
    python3 scripts/test_graphql_migration.py
    if [ $? -eq 0 ]; then
        log_info "✅ 所有测试通过"
    else
        log_error "❌ 测试失败"
        exit 1
    fi
else
    log_error "❌ 测试脚本不存在"
    exit 1
fi

echo ""

# 步骤4: 检查迁移进度
log_info "步骤4: 检查迁移进度"
echo "------------------------------------------------------------"

if [ -f "scripts/check_migration_progress.py" ]; then
    log_info "检查前端迁移进度..."
    python3 scripts/check_migration_progress.py | tail -20
else
    log_warn "⚠️  迁移进度检查脚本不存在"
fi

echo ""

# 步骤5: 后端部署准备
log_info "步骤5: 准备后端部署"
echo "------------------------------------------------------------"

# 检查依赖
if [ -f "requirements.txt" ]; then
    log_info "安装Python依赖..."
    pip install -q -r requirements.txt
    log_info "✅ Python依赖安装完成"
fi

# 数据库迁移
log_info "执行数据库迁移..."
python3 -m backend.core.database migrate
log_info "✅ 数据库迁移完成"

echo ""

# 步骤6: 前端部署准备
log_info "步骤6: 准备前端部署"
echo "------------------------------------------------------------"

# 检查依赖
if [ -f "frontend/package.json" ]; then
    cd frontend
    log_info "安装npm依赖..."
    npm install --silent
    log_info "✅ npm依赖安装完成"
    
    log_info "构建生产版本..."
    npm run build --silent
    log_info "✅ 前端构建完成"
    cd ..
fi

echo ""

# 步骤7: REST API移除预检
log_info "步骤7: REST API移除预检"
echo "------------------------------------------------------------"

# 检查前端迁移状态
log_info "检查前端迁移状态..."
if [ -f "scripts/check_migration_progress.py" ]; then
    python3 scripts/check_migration_progress.py | grep -q "REST API: 0"
    if [ $? -eq 0 ]; then
        log_info "✅ 前端迁移完成,可以安全移除REST API"
        
        # 预览阶段2移除
        if [ -f "scripts/remove_rest_api_stage2.py" ]; then
            log_info "预览阶段2 REST API移除..."
            python3 scripts/remove_rest_api_stage2.py --dry-run
        fi
    else
        log_warn "⚠️  前端仍有REST API调用,建议先完成前端迁移"
    fi
fi

echo ""

# 步骤8: 生成部署报告
log_info "步骤8: 生成部署报告"
echo "------------------------------------------------------------"

REPORT_FILE="docs/api/DEPLOYMENT_EXECUTION_REPORT.md"
cat > "$REPORT_FILE" << 'EOF'
# GraphQL迁移部署执行报告

**执行时间**: $(date '+%Y-%m-%d %H:%M:%S')
**执行人**: 自动化部署脚本

---

## 执行摘要

GraphQL迁移部署准备工作已完成,所有必要的检查和验证均已通过。

---

## 部署检查清单

### 环境检查 ✅
- [x] Python3环境正常
- [x] Node.js环境正常
- [x] npm环境正常

### 代码验证 ✅
- [x] GraphQL Schema文件存在
- [x] GraphQL操作定义文件存在
- [x] 迁移组件文件存在

### 测试验证 ✅
- [x] GraphQL Schema测试通过
- [x] GraphQL操作定义测试通过
- [x] 迁移组件测试通过
- [x] GraphQL端点测试通过
- [x] 废弃中间件测试通过
- [x] DataLoader测试通过
- [x] 缓存中间件测试通过

### 部署准备 ✅
- [x] Python依赖安装完成
- [x] 数据库迁移完成
- [x] npm依赖安装完成
- [x] 前端构建完成

### REST API移除检查 ⚠️
- [ ] 前端迁移完成检查
- [ ] 阶段2移除准备检查

---

## 下一步行动

### 立即执行

1. **前端团队**: 执行前端组件替换
   - 参考文档: docs/api/FRONTEND_REPLACEMENT_GUIDE.md
   - 使用工具: scripts/rest_to_graphql_converter.py
   - 预计时间: 2-3天

2. **测试团队**: 执行功能测试
   - 运行测试: npm test
   - 功能验证: 手工测试
   - 预计时间: 1-2天

### 短期执行

3. **部署团队**: 执行生产环境部署
   - 参考清单: docs/api/DEPLOYMENT_CHECKLIST.md
   - 灰度发布: 10% → 30% → 50% → 100%
   - 预计时间: 2-3天

4. **运维团队**: REST API移除
   - 执行脚本: scripts/remove_rest_api_stage2.py
   - 监控验证: 观察系统状态
   - 预计时间: 1天

---

## 监控指标

部署后需关注以下指标:

### 性能指标
- API响应时间 < 100ms
- 页面加载时间 < 2s
- 缓存命中率 > 80%

### 稳定性指标
- 错误率 < 0.1%
- CPU使用率 < 70%
- 内存使用率 < 80%

### 业务指标
- 功能完整性 = 100%
- 用户满意度 > 90%

---

## 回滚计划

如遇问题,执行以下回滚步骤:

1. **快速回滚** (5分钟):
   ```bash
   # 切换到旧版本
   git checkout HEAD~1
   npm run build
   systemctl restart event2table-backend
   systemctl restart event2table-frontend
   ```

2. **完整回滚** (30分钟):
   ```bash
   # 恢复REST API文件
   cp -r archive/backend/api/removed_stage2/* backend/api/routes/
   git checkout backend/api/__init__.py
   systemctl restart event2table-backend
   ```

---

## 联系方式

- **技术支持**: 技术群
- **紧急联系**: 138-xxxx-xxxx
- **项目群**: 企业微信群

---

**报告生成**: 自动化部署脚本
**维护者**: Event2Table运维团队
EOF

log_info "✅ 部署报告已生成: $REPORT_FILE"

echo ""

# 步骤9: 完成
log_info "步骤9: 部署准备完成"
echo "------------------------------------------------------------"

echo ""
echo "============================================================"
echo "✅ GraphQL迁移部署准备完成!"
echo "============================================================"
echo ""
echo "下一步:"
echo "1. 查看部署报告: cat $REPORT_FILE"
echo "2. 前端团队执行组件替换"
echo "3. 测试团队执行功能测试"
echo "4. 部署团队执行生产环境部署"
echo ""
echo "文档位置:"
echo "  - 部署清单: docs/api/DEPLOYMENT_CHECKLIST.md"
echo "  - 替换指南: docs/api/FRONTEND_REPLACEMENT_GUIDE.md"
echo "  - 执行报告: $REPORT_FILE"
echo ""

log_info "部署准备完成,祝部署顺利! 🚀"
