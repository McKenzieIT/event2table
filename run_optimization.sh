#!/bin/bash
# Event2Table 优化方案快速启动脚本

echo "========================================"
echo "Event2Table 优化方案实施"
echo "========================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

echo "✅ Python环境检查通过"
echo ""

# 检查依赖
echo "检查依赖..."
pip3 list | grep -E "Flask|redis|cachetools" > /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ 警告: 部分依赖未安装"
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

echo "✅ 依赖检查通过"
echo ""

# 运行缓存性能测试
echo "========================================"
echo "1. 运行缓存性能测试"
echo "========================================"
python3 tests/performance/test_cache_performance.py

echo ""
echo "========================================"
echo "2. 启动应用(带优化)"
echo "========================================"
echo "正在启动Flask应用..."
echo "访问地址: http://localhost:5001"
echo ""
echo "按Ctrl+C停止应用"
echo ""

# 启动应用
python3 web_app.py
