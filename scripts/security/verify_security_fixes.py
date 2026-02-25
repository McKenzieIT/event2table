#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Fixes Verification Script
==================================

验证P1安全问题修复：
1. Pickle反序列化漏洞修复
2. 路径遍历防护
3. Redis连接泄露修复

执行方式:
    source backend/venv/bin/activate
    python scripts/security/verify_security_fixes.py

Author: Event2Table Development Team
Date: 2026-02-24
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityVerificationReport:
    """安全验证报告"""

    def __init__(self):
        self.passed_checks: List[str] = []
        self.failed_checks: List[Tuple[str, str]] = []
        self.warnings: List[str] = []

    def add_pass(self, check_name: str, details: str = ""):
        """添加通过的检查"""
        self.passed_checks.append((check_name, details))
        logger.info(f"✅ PASS: {check_name}")

    def add_fail(self, check_name: str, reason: str):
        """添加失败的检查"""
        self.failed_checks.append((check_name, reason))
        logger.error(f"❌ FAIL: {check_name} - {reason}")

    def add_warning(self, check_name: str, message: str):
        """添加警告"""
        self.warnings.append((check_name, message))
        logger.warning(f"⚠️  WARNING: {check_name} - {message}")

    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 80)
        print("SECURITY VERIFICATION SUMMARY")
        print("=" * 80)

        print(f"\n✅ Passed Checks: {len(self.passed_checks)}")
        for check, details in self.passed_checks:
            print(f"  - {check}")
            if details:
                print(f"    {details}")

        if self.failed_checks:
            print(f"\n❌ Failed Checks: {len(self.failed_checks)}")
            for check, reason in self.failed_checks:
                print(f"  - {check}: {reason}")

        if self.warnings:
            print(f"\n⚠️  Warnings: {len(self.warnings)}")
            for check, message in self.warnings:
                print(f"  - {check}: {message}")

        print("\n" + "=" * 80)

        if self.failed_checks:
            print("❌ SECURITY VERIFICATION FAILED")
            print(f"   {len(self.failed_checks)} critical issues must be fixed")
            return False
        else:
            print("✅ SECURITY VERIFICATION PASSED")
            print(f"   All {len(self.passed_checks)} security checks passed")
            return True


def verify_pickle_fix(report: SecurityVerificationReport):
    """验证Pickle漏洞修复"""
    logger.info("\n" + "=" * 80)
    logger.info("Verifying Pickle Deserialization Fix")
    logger.info("=" * 80)

    # 1. 检查bloom_filter_enhanced.py不再使用pickle
    check_name = "Bloom filter no longer uses pickle"
    try:
        bloom_file = project_root / "backend/core/cache/bloom_filter_enhanced.py"
        content = bloom_file.read_text()

        if "import pickle" in content:
            report.add_fail(check_name, "File still imports pickle")
        elif "pickle." in content:
            report.add_fail(check_name, "File still uses pickle functions")
        else:
            report.add_pass(check_name, "Pickle import removed from bloom_filter_enhanced.py")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check file: {e}")

    # 2. 检查使用JSON序列化
    check_name = "Bloom filter uses JSON serialization"
    try:
        bloom_file = project_root / "backend/core/cache/bloom_filter_enhanced.py"
        content = bloom_file.read_text()

        if "import json" in content and "json.dump" in content:
            report.add_pass(check_name, "JSON serialization implemented")
        else:
            report.add_fail(check_name, "JSON serialization not found")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check file: {e}")

    # 3. 检查数据验证
    check_name = "Bloom filter validates loaded data"
    try:
        bloom_file = project_root / "backend/core/cache/bloom_filter_enhanced.py"
        content = bloom_file.read_text()

        if "_validate_loaded_data" in content:
            report.add_pass(check_name, "Data validation function present")
        else:
            report.add_fail(check_name, "Data validation function missing")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check file: {e}")


def verify_path_traversal_fix(report: SecurityVerificationReport):
    """验证路径遍历防护"""
    logger.info("\n" + "=" * 80)
    logger.info("Verifying Path Traversal Protection")
    logger.info("=" * 80)

    # 1. 检查PathValidator模块存在
    check_name = "PathValidator module exists"
    try:
        path_validator_file = project_root / "backend/core/security/path_validator.py"
        if path_validator_file.exists():
            report.add_pass(check_name, "PathValidator module created")
        else:
            report.add_fail(check_name, "PathValidator module not found")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check: {e}")

    # 2. 检查bloom_filter使用PathValidator
    check_name = "Bloom filter uses PathValidator"
    try:
        bloom_file = project_root / "backend/core/cache/bloom_filter_enhanced.py"
        content = bloom_file.read_text()

        if "from backend.core.security.path_validator import PathValidator" in content:
            report.add_pass(check_name, "PathValidator imported in bloom_filter_enhanced.py")
        else:
            report.add_warning(check_name, "PathValidator not imported in bloom_filter_enhanced.py")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check file: {e}")

    # 3. 检查crypto.py使用PathValidator
    check_name = "Crypto module uses PathValidator"
    try:
        crypto_file = project_root / "backend/core/crypto.py"
        content = crypto_file.read_text()

        if "PathValidator" in content:
            report.add_pass(check_name, "PathValidator used in crypto.py")
        else:
            report.add_warning(check_name, "PathValidator not found in crypto.py")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check file: {e}")


def verify_redis_connection_fix(report: SecurityVerificationReport):
    """验证Redis连接泄露修复"""
    logger.info("\n" + "=" * 80)
    logger.info("Verifying Redis Connection Leak Fix")
    logger.info("=" * 80)

    # 1. 检查RedisConnectionManager模块存在
    check_name = "RedisConnectionManager module exists"
    try:
        conn_manager_file = project_root / "backend/core/cache/redis_connection_manager.py"
        if conn_manager_file.exists():
            report.add_pass(check_name, "RedisConnectionManager module created")
        else:
            report.add_fail(check_name, "RedisConnectionManager module not found")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check: {e}")

    # 2. 检查cache_system.py使用RedisConnectionManager
    check_name = "Cache system uses RedisConnectionManager"
    try:
        cache_file = project_root / "backend/core/cache/cache_system.py"
        content = cache_file.read_text()

        if "from backend.core.cache.redis_connection_manager import" in content:
            report.add_pass(check_name, "RedisConnectionManager imported in cache_system.py")
        else:
            report.add_warning(check_name, "RedisConnectionManager not imported in cache_system.py")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check file: {e}")

    # 3. 检查连接泄露监控功能
    check_name = "Connection leak monitoring implemented"
    try:
        conn_manager_file = project_root / "backend/core/cache/redis_connection_manager.py"
        content = conn_manager_file.read_text()

        if "check_connection_leaks" in content:
            report.add_pass(check_name, "Connection leak monitoring function present")
        else:
            report.add_fail(check_name, "Connection leak monitoring missing")

    except Exception as e:
        report.add_fail(check_name, f"Failed to check file: {e}")


def verify_unit_tests(report: SecurityVerificationReport):
    """验证单元测试存在"""
    logger.info("\n" + "=" * 80)
    logger.info("Verifying Unit Tests")
    logger.info("=" * 80)

    test_files = [
        ("PathValidator tests", "backend/test/unit/security/test_path_validator.py"),
        ("RedisConnectionManager tests", "backend/test/unit/security/test_redis_connection_manager.py"),
        ("Bloom Filter security tests", "backend/test/unit/security/test_bloom_filter_security.py"),
    ]

    for test_name, test_path in test_files:
        check_name = f"{test_name} exist"
        try:
            full_path = project_root / test_path
            if full_path.exists():
                report.add_pass(check_name, f"Test file: {test_path}")
            else:
                report.add_warning(check_name, f"Test file not found: {test_path}")

        except Exception as e:
            report.add_fail(check_name, f"Failed to check: {e}")


def run_security_verification():
    """运行完整的安全验证"""
    logger.info("=" * 80)
    logger.info("P1 SECURITY FIXES VERIFICATION")
    logger.info("=" * 80)

    report = SecurityVerificationReport()

    # 执行所有验证
    verify_pickle_fix(report)
    verify_path_traversal_fix(report)
    verify_redis_connection_fix(report)
    verify_unit_tests(report)

    # 打印摘要并返回结果
    success = report.print_summary()

    return success


if __name__ == "__main__":
    success = run_security_verification()
    sys.exit(0 if success else 1)
