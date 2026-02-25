#!/bin/bash
# 验证缓存架构优化模块

cd /Users/mckenzie/Documents/event2table/backend
source venv/bin/activate

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "        Event2Table 缓存架构优化 - 模块验证"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查文件存在
echo "📁 检查文件..."
FILES=(
    "core/cache/bloom_filter_enhanced.py"
    "core/cache/monitoring.py"
    "core/cache/capacity_monitor.py"
    "core/cache/consistency.py"
    "core/cache/degradation.py"
    "core/cache/intelligent_warmer.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(ls -lh "$file" | awk '{print $5}')
        echo "  ✅ $file ($SIZE)"
    else
        echo "  ❌ $file (不存在)"
    fi
done

echo ""
echo "🔍 验证模块导入..."

python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

modules = [
    ('core.cache.bloom_filter_enhanced', 'get_enhanced_bloom_filter'),
    ('core.cache.monitoring', 'CacheAlertManager'),
    ('core.cache.capacity_monitor', 'CacheCapacityMonitor'),
    ('core.cache.consistency', 'cache_rw_lock'),
    ('core.cache.degradation', 'cache_degradation_manager'),
    ('core.cache.intelligent_warmer', 'intelligent_cache_warmer')
]

success = 0
failed = 0

for module_name, attr_name in modules:
    try:
        module = __import__(module_name, fromlist=[attr_name])
        obj = getattr(module, attr_name)
        print(f"  ✅ {module_name.split('.')[-1]:30s}")
        success += 1
    except Exception as e:
        print(f"  ❌ {module_name.split('.')[-1]:30s} - ERROR: {str(e)[:50]}")
        failed += 1

print()
print(f"总结: {success}个成功, {failed}个失败")
PYEOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "验证完成!"
