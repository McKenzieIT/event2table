# 缓存系统安全修复清单

> **生成日期**: 2026-02-24
> **参考报告**: SECURITY_CODE_AUDIT_CACHE_SYSTEM.md

---

## 快速概览

| 优先级 | 问题数量 | 预计工作量 | 截止日期 |
|--------|----------|------------|----------|
| P0 - 关键 | 2 | 2天 | 本周 |
| P1 - 高危 | 4 | 5天 | 2周内 |
| P2 - 中危 | 4 | 3天 | 1个月内 |
| P3 - 低危 | 2 | 1天 | 有时间时 |

**总计**: 12个问题 | **预计总工作量**: 11个工作日

---

## P0 修复任务 (关键 - 本周完成)

### ✅ P0-1: 缓存键注入漏洞

**文件**: `backend/core/security/cache_key_validator.py` (新建)

**检查清单**:
- [ ] 创建`CacheKeyValidator`类
- [ ] 定义参数名白名单`ALLOWED_PARAM_NAMES`
- [ ] 定义缓存模式白名单`ALLOWED_PATTERNS`
- [ ] 实现`validate_pattern()`方法
- [ ] 实现`validate_params()`方法
- [ ] 实现`validate_and_build()`方法
- [ ] 修改`cache_system.py`的`CacheKeyBuilder.build()`
- [ ] 修改`cache_hierarchical.py`的`get()`方法
- [ ] 修改`invalidator.py`的`invalidate_key()`方法
- [ ] 添加单元测试(10个测试用例)
- [ ] 验证所有缓存操作都使用验证器

**预计时间**: 4小时

**验证命令**:
```bash
cd backend
python -m pytest tests/test_cache_key_validator.py -v
```

---

### ✅ P0-2: 敏感信息泄露到日志

**文件**: `backend/core/security/sensitive_data_filter.py` (新建)

**检查清单**:
- [ ] 创建`SensitiveDataFilter`类
- [ ] 定义敏感字段列表`SENSITIVE_FIELDS`
- [ ] 实现`sanitize_dict()`方法
- [ ] 实现`sanitize_log_message()`方法
- [ ] 创建`SafeLoggerAdapter`类
- [ ] 修改`invalidator.py`使用SafeLoggerAdapter
- [ ] 修改`decorators.py`使用SafeLoggerAdapter
- [ ] 修改`cache_hierarchical.py`使用SafeLoggerAdapter
- [ ] 配置生产环境日志级别为INFO
- [ ] 验证日志不包含敏感数据

**预计时间**: 3小时

**验证命令**:
```bash
# 检查日志文件是否包含敏感数据
grep -i "password\|token\|secret\|key" logs/app.log
# 应该没有结果（或只有REDACTED）
```

---

## P1 修复任务 (高危 - 2周内完成)

### ✅ P1-1: 布隆过滤器路径遍历漏洞

**文件**: `backend/core/security/path_validator.py` (新建)

**检查清单**:
- [ ] 创建`PathValidator`类
- [ ] 定义允许的基础目录`ALLOWED_BASE_DIRS`
- [ ] 实现`validate_persistence_path()`方法
- [ ] 实现`safe_open()`方法
- [ ] 修改`bloom_filter_enhanced.py`的`__init__()`
- [ ] 修改`bloom_filter_enhanced.py`的`_load_from_disk()`
- [ ] 添加路径验证测试

**预计时间**: 2小时

---

### ✅ P1-2: Pickle反序列化代码执行漏洞

**文件**: `backend/core/security/secure_bloom_filter_loader.py` (新建)

**检查清单**:
- [ ] 创建`SecureBloomFilterLoader`类
- [ ] 实现`save_with_signature()`方法
- [ ] 实现`load_with_signature()`方法
- [ ] 使用HMAC验证pickle文件
- [ ] 修改`bloom_filter_enhanced.py`使用安全加载器
- [ ] 或者: 将Pickle替换为JSON
- [ ] 添加反序列化安全测试

**预计时间**: 4小时

**重要**: 如果选择JSON方案，需要确保`ScalableBloomFilter`可以序列化

---

### ✅ P1-3: 并发竞态条件 - TOCTOU漏洞

**文件**: `backend/core/cache/decorators.py` (修改)

**检查清单**:
- [ ] 实现`_get_lock_for_key()`函数
- [ ] 创建`_cache_locks`字典(使用SizedLockDict)
- [ ] 修改`cached_service`装饰器使用锁
- [ ] 实现Double-Checked Locking模式
- [ ] 添加并发测试(10个线程 x 100次操作)
- [ ] 验证没有重复的数据库查询

**预计时间**: 3小时

**验证命令**:
```bash
cd backend
python -m pytest tests/test_concurrent_cache.py -v
```

---

### ✅ P1-4: Redis连接信息泄露

**文件**: `backend/core/cache/cache_system.py` (修改)

**检查清单**:
- [ ] 创建`safe_redis_error_handler`装饰器
- [ ] 实现安全的错误处理逻辑
- [ ] 区分开发和生产环境的错误日志
- [ ] 修改所有Redis操作使用错误处理装饰器
- [ ] 验证生产环境不记录完整异常

**预计时间**: 2小时

---

## P2 修复任务 (中危 - 1个月内完成)

### ✅ P2-1: 容量监控数值不稳定

**文件**: `backend/core/cache/capacity_monitor.py` (修改)

**检查清单**:
- [ ] 修改`predict_exhaustion()`使用归一化时间
- [ ] 添加更好的数值稳定性检查
- [ ] 处理除零错误
- [ ] 添加边界条件测试

**预计时间**: 1.5小时

---

### ✅ P2-2: 监控系统告警泛滥

**文件**: `backend/core/cache/monitoring.py` (修改)

**检查清单**:
- [ ] 创建`AlertDeduplicator`类
- [ ] 实现5分钟冷却期
- [ ] 修改告警触发逻辑使用去重器
- [ ] 添加告警去重测试

**预计时间**: 1.5小时

---

### ✅ P2-3: 缓存统计信息竞态条件

**文件**: `backend/core/cache/cache_hierarchical.py` (修改)

**检查清单**:
- [ ] 创建`ThreadSafeStats`类
- [ ] 修改`stats`字典使用`ThreadSafeStats`
- [ ] 更新所有统计操作使用线程安全方法
- [ ] 添加统计并发测试

**预计时间**: 2小时

---

### ✅ P2-4: 缓存降级策略状态不一致

**文件**: `backend/core/cache/degradation.py` (修改)

**检查清单**:
- [ ] 实现进入/退出降级的阈值分离
- [ ] 添加最小降级持续时间(60秒)
- [ ] 防止状态频繁切换
- [ ] 添加状态机测试

**预计时间**: 2小时

---

## P3 修复任务 (低危 - 有时间时)

### ✅ P3-1: 内存泄漏风险

**检查清单**:
- [ ] 创建`SizedLockDict`类
- [ ] 实现LRU淘汰机制
- [ ] 替换`_cache_locks`使用`SizedLockDict`

**预计时间**: 1小时

---

### ✅ P3-2: 日志格式不一致

**检查清单**:
- [ ] 创建`SecurityAuditFormatter`类
- [ ] 实现结构化JSON日志格式
- [ ] 统一所有模块的日志格式

**预计时间**: 1小时

---

## 实施计划

### 第1周 (P0修复)

**目标**: 完成所有P0关键问题修复

**Day 1-2 (P0-1)**:
- 上午: 实现CacheKeyValidator
- 下午: 修改所有缓存键构建点
- 晚上: 编写单元测试

**Day 3 (P0-2)**:
- 上午: 实现SensitiveDataFilter
- 下午: 修改所有日志记录
- 晚上: 配置生产环境日志

**Day 4-5**:
- 全面测试P0修复
- 代码审查
- 部署到测试环境

### 第2周 (P1修复)

**目标**: 完成所有P1高危问题修复

**Day 1-2 (P1-1, P1-2)**:
- 布隆过滤器安全修复

**Day 3 (P1-3)**:
- 并发安全修复

**Day 4 (P1-4)**:
- Redis错误处理

**Day 5**:
- P1全面测试
- 代码审查

### 第3-4周 (P2修复)

**目标**: 完成所有P2中危问题修复

- 容量监控改进
- 告警去重
- 线程安全统计
- 降级策略改进

### 后续 (P3修复)

**目标**: 在有时间时完成P3低危问题修复

- 内存优化
- 日志格式统一

---

## 测试策略

### 单元测试

```bash
# 运行所有安全测试
cd backend
python -m pytest tests/test_cache_security/ -v

# 运行特定测试
python -m pytest tests/test_cache_security/test_cache_key_injection.py -v
```

### 集成测试

```bash
# 运行缓存集成测试
python -m pytest tests/test_cache_integration/ -v

# 并发测试
python -m pytest tests/test_cache_concurrent/ -v --threads=10
```

### 手动测试

```bash
# 1. 测试缓存键注入防护
cd backend
python3 -c "
from backend.core.security.cache_key_validator import CacheKeyValidator
try:
    CacheKeyValidator.validate_params({'game_gid': '1:*\r\nDEL *'})
    print('❌ 测试失败: 应该拒绝恶意输入')
except ValueError:
    print('✅ 测试通过: 恶意输入被拒绝')
"

# 2. 测试敏感数据过滤
python3 -c "
from backend.core.security.sensitive_data_filter import SensitiveDataFilter
filtered = SensitiveDataFilter.sanitize_dict({'password': 'secret123'})
print(f'过滤结果: {filtered}')
assert filtered['password'] == '***REDACTED***'
print('✅ 测试通过: 敏感数据被过滤')
"
```

### 渗透测试

```bash
# 使用Burp Suite或sqlmap测试
# 1. 启动应用
python web_app.py

# 2. 运行sqlmap
sqlmap --url="http://localhost:5001/api/games?game_gid=1" \
       --level=5 \
       --risk=3 \
       --batch
```

---

## 验收标准

### P0验收标准

- [ ] 所有单元测试通过(100%)
- [ ] 没有缓存键注入漏洞
- [ ] 日志不包含敏感数据
- [ ] 代码审查通过
- [ ] 部署到生产环境

### P1验收标准

- [ ] 所有单元测试通过(100%)
- [ ] 没有路径遍历漏洞
- [ ] 没有反序列化漏洞
- [ ] 没有竞态条件
- [ ] 代码审查通过

### P2验收标准

- [ ] 所有单元测试通过(90%+)
- [ ] 数值计算稳定
- [ ] 告警不泛滥
- [ ] 统计信息准确
- [ ] 降级状态稳定

---

## 风险评估

### 高风险项

1. **P0-1修复可能导致现有功能中断**
   - 缓解: 先在测试环境充分测试
   - 回滚: 保留旧代码分支

2. **P1-2替换Pickle可能导致兼容性问题**
   - 缓解: 使用HMAC验证而非完全替换
   - 回滚: 保留Pickle加载逻辑作为fallback

### 中风险项

1. **P1-3添加锁可能影响性能**
   - 缓解: 使用细粒度锁和双重检查
   - 监控: 观察缓存响应时间

2. **P2修复可能影响现有监控**
   - 缓解: 保留原有告警机制
   - 测试: 在测试环境验证告警逻辑

---

## 回滚计划

如果修复导致问题，按以下步骤回滚：

1. **识别问题模块**
   ```bash
   # 查看日志确定问题
   tail -f logs/app.log
   ```

2. **回滚到上一个稳定版本**
   ```bash
   git revert <commit-hash>
   ```

3. **验证回滚成功**
   ```bash
   python -m pytest tests/ -v
   ```

4. **报告问题**
   - 创建issue记录问题
   - 分析根本原因
   - 制定新的修复方案

---

## 参考资料

### 内部文档

- [CLAUDE.md](../../CLAUDE.md) - 项目开发规范
- [security-essentials.md](../../docs/lessons-learned/security-essentials.md) - 安全要点

### 外部资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
- [Python pickle documentation](https://docs.python.org/3/library/pickle.html#restricting-globals)

### 工具

- **Bandit**: `pip install bandit`
- **Safety**: `pip install safety`
- **Pytest**: `pip install pytest pytest-cov`

---

## 联系信息

**安全问题**: 请直接报告给安全团队

**紧急联系**: security@event2table.com

**非紧急**: 创建GitHub Issue

---

**清单版本**: 1.0
**最后更新**: 2026-02-24
**维护者**: Event2Table Security Team
