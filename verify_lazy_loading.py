#!/usr/bin/env python3
"""快速验证lazy loading修复"""

import sys
import os
import time

# 设置测试环境
os.environ["TESTING"] = "true"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Lazy Loading修复验证")
print("=" * 60)

# 测试1: EventService初始化速度
print("\n1. 测试EventService初始化速度...")
start = time.time()
from backend.services.events.event_service import EventService
event_service = EventService()
elapsed = time.time() - start

print(f"   EventService初始化时间: {elapsed*1000:.2f}ms")
if elapsed < 0.1:
    print(f"   ✅ PASS: 初始化<100ms")
else:
    print(f"   ❌ FAIL: 初始化{elapsed*1000:.2f}ms >=100ms")

# 验证lazy loading
if event_service._bloom_filter is None:
    print(f"   ✅ PASS: Bloom Filter未初始化（lazy loading）")
else:
    print(f"   ❌ FAIL: Bloom Filter已初始化（非lazy loading）")

# 测试2: GameService初始化速度
print("\n2. 测试GameService初始化速度...")
start = time.time()
from backend.services.games.game_service import GameService
game_service = GameService()
elapsed = time.time() - start

print(f"   GameService初始化时间: {elapsed*1000:.2f}ms")
if elapsed < 0.1:
    print(f"   ✅ PASS: 初始化<100ms")
else:
    print(f"   ❌ FAIL: 初始化{elapsed*1000:.2f}ms >=100ms")

# 验证lazy loading
if game_service._bloom_filter is None:
    print(f"   ✅ PASS: Bloom Filter未初始化（lazy loading）")
else:
    print(f"   ❌ FAIL: Bloom Filter已初始化（非lazy loading）")

# 测试3: Bloom Filter延迟加载
print("\n3. 测试Bloom Filter延迟加载...")
start = time.time()
bf = event_service.bloom_filter
elapsed = time.time() - start

print(f"   Bloom Filter初始化时间: {elapsed*1000:.2f}ms")
if bf is not None:
    print(f"   ✅ PASS: Bloom Filter已初始化")
else:
    print(f"   ❌ FAIL: Bloom Filter未初始化")

# 验证缓存
bf2 = event_service.bloom_filter
if bf is bf2:
    print(f"   ✅ PASS: 返回缓存的实例")
else:
    print(f"   ❌ FAIL: 未返回缓存的实例")

print("\n" + "=" * 60)
print("验证完成")
print("=" * 60)
