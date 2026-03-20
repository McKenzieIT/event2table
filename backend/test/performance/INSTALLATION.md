# Performance Test Suite - Installation and Setup

## 安装状态

Locust 正在后台安装中。安装完成后，您需要验证安装是否成功。

## 快速安装

```bash
# 激活虚拟环境
source backend/venv/bin/activate

# 安装 Locust 和依赖
pip install locust psutil

# 验证安装
locust --version
```

## 如果安装遇到问题

### 方法1: 使用国内镜像源

```bash
source backend/venv/bin/activate
pip install locust psutil -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方法2: 分步安装

```bash
source backend/venv/bin/activate

# 先升级 pip
pip install --upgrade pip

# 安装依赖
pip install psutil
pip install requests
pip install flask-cors
pip install configargparse
pip install msgpack
pip install pyzmq
pip install roundrobin
pip install Werkzeug

# 最后安装 Locust
pip install locust
```

### 方法3: 使用 conda（如果可用）

```bash
conda install -c conda-forge locust
```

## 验证安装

运行验证脚本：

```bash
bash backend/test/performance/verify_setup.sh
```

或手动验证：

```bash
source backend/venv/bin/activate

# 检查 Locust 版本
locust --version

# 检查 psutil
python3 -c "import psutil; print(psutil.__version__)"
```

## 预期输出

```
Locust version 2.34.0
```

## 测试文件位置

所有性能测试文件已创建在：

```
backend/test/performance/
├── test_cache_performance.py          # 主测试文件
├── run_performance_test.sh            # 完整测试套件
├── quick_test.sh                      # 快速单场景测试
├── verify_setup.sh                    # 安装验证脚本
├── README.md                          # 完整文档
├── PERFORMANCE_TEST_GUIDE.md          # 快速指南
└── INSTALLATION.md                    # 本文件
```

## 下一步

安装验证成功后，运行测试：

```bash
# 1. 确保后端服务器正在运行
python3 web_app.py

# 2. 运行完整测试套件
bash backend/test/performance/run_performance_test.sh

# 或运行快速测试
bash backend/test/performance/quick_test.sh normal
```

## 故障排除

### 问题: pip 安装卡住

**解决方案**: 终止卡住的进程，使用国内镜像源

```bash
# 查找并终止 pip 进程
ps aux | grep pip
kill <PID>

# 使用镜像源重新安装
pip install locust psutil -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题: 网络超时

**解决方案**: 增加超时时间

```bash
pip install locust psutil --timeout 300
```

### 问题: 权限错误

**解决方案**: 确保使用虚拟环境

```bash
# 不要使用 sudo
# 应该激活虚拟环境后再安装
source backend/venv/bin/activate
pip install locust psutil
```

### 问题: 依赖冲突

**解决方案**: 升级相关包

```bash
pip install --upgrade setuptools wheel
pip install locust psutil --force-reinstall
```

## 系统要求

- Python 3.9+
- 2GB+ 可用内存
- 稳定的网络连接（用于安装）
- 后端服务器在端口 5001 运行

## 支持的操作系统

- ✅ macOS (测试通过)
- ✅ Linux
- ✅ Windows (使用 WSL 或 Git Bash)

## 获取帮助

如果安装仍然失败：

1. 查看 pip 日志：`~/.pip/pip.log`
2. 检查网络连接
3. 尝试使用不同的镜像源
4. 参考项目文档：`docs/testing/`

---

**最后更新**: 2026-02-24
**版本**: 1.0.0
