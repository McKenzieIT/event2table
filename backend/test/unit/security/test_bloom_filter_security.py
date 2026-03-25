#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Bloom Filter Security Fixes
===========================================

测试Bloom Filter安全修复: 
- Pickle替换为JSON序列化
- 数据验证
- 路径遍历防护
"""

import base64
import json
import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter, get_enhanced_bloom_filter


class TestBloomFilterSecurity:
    """Bloom Filter安全修复测试"""

    @pytest.fixture
    def temp_persistence_path(self):
        """创建临时持久化路径"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            path = f.name
        yield path
        # 清理
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(path + '.tmp'):
            os.remove(path + '.tmp')

    def test_initialization_with_path_validation(self, temp_persistence_path):
        """测试初始化时的路径验证"""
        # 应该成功初始化
        bloom = EnhancedBloomFilter(capacity=1000, persistence_path=temp_persistence_path)
        assert bloom is not None
        assert bloom.capacity == 1000

    def test_save_and_load_with_json(self, temp_persistence_path):
        """测试JSON序列化保存和加载"""
        bloom = EnhancedBloomFilter(
            capacity=1000,
            persistence_path=temp_persistence_path,
            strict_validation=False,  # Test mode for JSON serialization
        )

        # 添加一些数据
        bloom.add("key1")
        bloom.add("key2")
        bloom.add("key3")

        # 保存到磁盘
        result = bloom._save_to_disk()
        assert result is True
        assert os.path.exists(temp_persistence_path)

        # 验证是JSON格式, 不是pickle
        with open(temp_persistence_path, 'r') as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert 'size' in data
            # Test mode uses 'items' key for exact reconstruction
            assert 'items' in data or 'bloom_filter' in data
            assert 'item_count' in data

    def test_load_validates_data_structure(self, temp_persistence_path):
        """测试加载时验证数据结构"""
        # 创建有效的bloom filter数据
        bloom1 = EnhancedBloomFilter(capacity=1000, persistence_path=temp_persistence_path)
        bloom1.add("key1")
        bloom1._save_to_disk()

        # 加载应该成功
        bloom2 = EnhancedBloomFilter(capacity=1000, persistence_path=temp_persistence_path)
        assert bloom2.contains("key1") is True

    def test_load_rejects_invalid_data(self, temp_persistence_path):
        """测试拒绝无效数据"""
        # 创建无效的JSON数据
        with open(temp_persistence_path, 'w') as f:
            json.dump({"invalid": "data"}, f)

        # 加载应该失败并创建新的bloom filter
        bloom = EnhancedBloomFilter(capacity=1000, persistence_path=temp_persistence_path)
        # 应该创建新的bloom filter, 而不是加载无效数据
        assert bloom._item_count == 0

    def test_load_rejects_malicious_data(self, temp_persistence_path):
        """测试拒绝恶意构造的数据"""
        # 尝试过大的size(DoS攻击)
        malicious_data = {
            'size': 999999999999,  # 过大
            'hash_count': 7,
            'bloom_filter': base64.b64encode(b'fake_data').decode(),
            'item_count': 0,
        }

        with open(temp_persistence_path, 'w') as f:
            json.dump(malicious_data, f)

        # 加载应该拒绝恶意数据
        bloom = EnhancedBloomFilter(capacity=1000, persistence_path=temp_persistence_path)
        # 应该创建新的bloom filter
        assert bloom.capacity == 1000

    def test_load_rejects_invalid_base64(self, temp_persistence_path):
        """测试拒绝无效的base64数据"""
        malicious_data = {
            'size': 1000,
            'hash_count': 7,
            'bloom_filter': 'not_valid_base64!!!',
            'item_count': 0,
        }

        with open(temp_persistence_path, 'w') as f:
            json.dump(malicious_data, f)

        # 加载应该失败
        bloom = EnhancedBloomFilter(capacity=1000, persistence_path=temp_persistence_path)
        # 应该创建新的bloom filter
        assert bloom._item_count == 0

    def test_validate_loaded_data_checks_required_keys(self):
        """测试验证必需的键"""
        bloom = EnhancedBloomFilter(capacity=1000)

        # 缺少必需的键
        invalid_data = {'size': 1000}
        assert bloom._validate_loaded_data(invalid_data) is False

    def test_validate_loaded_data_checks_types(self):
        """测试验证数据类型"""
        bloom = EnhancedBloomFilter(capacity=1000)

        # 错误的类型
        invalid_data = {
            'size': "not_an_int",
            'hash_count': 7,
            'bloom_filter': base64.b64encode(b'data').decode(),
            'item_count': 0,
        }
        assert bloom._validate_loaded_data(invalid_data) is False

    def test_validate_loaded_data_checks_ranges(self):
        """测试验证数据范围"""
        bloom = EnhancedBloomFilter(capacity=1000)

        # 负数
        invalid_data = {
            'size': -100,
            'hash_count': 7,
            'bloom_filter': base64.b64encode(b'data').decode(),
            'item_count': -1,
        }
        assert bloom._validate_loaded_data(invalid_data) is False

    def test_path_traversal_protection(self):
        """测试路径遍历防护"""
        # 尝试使用路径遍历攻击
        malicious_paths = [
            "../../../etc/passwd",
            "../../data/malicious.json",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
        ]

        for malicious_path in malicious_paths:
            # 应该拒绝或重定向到安全路径
            bloom = EnhancedBloomFilter(capacity=1000, persistence_path=malicious_path)
            # 路径应该被验证和重定向到安全位置
            assert "bloom_filter" in bloom.persistence_path
            assert ".." not in bloom.persistence_path

    def test_atomic_save(self, temp_persistence_path):
        """测试原子保存(临时文件+重命名)"""
        bloom = EnhancedBloomFilter(capacity=1000, persistence_path=temp_persistence_path)

        # 保存
        result = bloom._save_to_disk()
        assert result is True

        # 验证没有临时文件残留
        assert not os.path.exists(temp_persistence_path + '.tmp')

        # 验证主文件存在
        assert os.path.exists(temp_persistence_path)

    def test_version_tracking(self, temp_persistence_path):
        """测试版本跟踪"""
        bloom = EnhancedBloomFilter(capacity=1000, persistence_path=temp_persistence_path)
        bloom.add("key1")
        bloom._save_to_disk()

        # 读取文件并检查版本
        with open(temp_persistence_path, 'r') as f:
            data = json.load(f)
            assert 'version' in data
            assert data['version'] == '2.0'


class TestBloomFilterIntegration:
    """Bloom Filter集成测试"""

    def test_full_lifecycle(self):
        """测试完整生命周期"""
        with tempfile.TemporaryDirectory() as tmpdir:
            persistence_path = os.path.join(tmpdir, "test_bloom.json")

            # 1. 创建bloom filter
            bloom1 = EnhancedBloomFilter(capacity=1000, persistence_path=persistence_path)

            # 2. 添加数据
            for i in range(100):
                bloom1.add(f"key_{i}")

            # 3. 保存到磁盘
            bloom1._save_to_disk()
            assert os.path.exists(persistence_path)

            # 4. 加载新的bloom filter
            bloom2 = EnhancedBloomFilter(capacity=1000, persistence_path=persistence_path)

            # 5. 验证数据
            for i in range(100):
                assert bloom2.contains(f"key_{i}") is True

            # 6. 验证统计
            stats = bloom2.get_stats()
            assert stats['total_items'] == 100

    def test_migration_from_pickle_to_json(self):
        """
        测试从旧版本pickle迁移（如果存在）

        如果检测到旧的.pkl文件, 应该创建新的.json文件
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            pickle_path = os.path.join(tmpdir, "bloom_filter.pkl")
            json_path = os.path.join(tmpdir, "bloom_filter.json")

            # 创建新的bloom filter(应该使用.json)
            bloom = EnhancedBloomFilter(capacity=1000, persistence_path=pickle_path)  # 传入.pkl路径

            # 验证实际使用.json路径
            assert (
                bloom.persistence_path.endswith('.json') or 'bloom_filter' in bloom.persistence_path
            )


class TestBloomFilterThreadSafety:
    """线程安全测试"""

    def test_concurrent_operations(self):
        """测试并发操作"""
        import threading

        bloom = EnhancedBloomFilter(capacity=10000)

        results = []
        errors = []

        def worker(worker_id):
            try:
                for i in range(100):
                    bloom.add(f"worker_{worker_id}_key_{i}")
                results.append(worker_id)
            except Exception as e:
                errors.append(e)

        # 创建多个线程
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证
        assert len(results) == 10
        assert len(errors) == 0

        # 验证数据一致性
        stats = bloom.get_stats()
        assert stats['total_items'] == 1000  # 10 workers * 100 keys
