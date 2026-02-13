# DWD Generator

数据仓库（DWD）层HQL生成工具，用于自动化创建Hive视图。

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 18+
- SQLite 3

### 安装
```bash
# 后端
pip install -r requirements.txt
python scripts/setup/init_db.py

# 前端
cd frontend
npm install
npm run build
```

### 运行
```bash
# 启动后端
python web_app.py

# 访问应用
open http://127.0.0.1:5001
```

## 测试

### 测试框架
项目采用完整的测试体系，包括单元测试、集成测试、E2E测试和API契约测试。

### 运行测试
```bash
# API契约测试（验证前后端一致性）
npm run test:contract

# 后端单元测试
npm run test:backend:unit

# 前端单元测试
npm run test:frontend

# 完整测试套件
npm run test

# 开发完成验证
npm run verify
```

### Git自动化测试
- **Pre-commit**: 自动运行API契约测试 + 快速单元测试
- **Pre-push**: 运行完整测试套件

每次提交代码时，Git会自动运行相关测试，确保代码质量。

### 测试目录结构
```
test/
├── unit/              # 单元测试
│   ├── backend/
│   └── frontend/
├── integration/         # 集成测试
├── e2e/              # 端到端测试
├── contract/          # API契约测试
└── archive/           # 已归档的测试
```

详见 [测试指南](test/README.md)

## 文档
- [架构设计](docs/development/architecture.md)
- [快速开始](docs/development/getting-started.md)
- [API文档](docs/api/)
- [架构决策记录](docs/adr/)

## 开发
详见 [贡献指南](docs/development/contributing.md)

## 许可证
MIT License
