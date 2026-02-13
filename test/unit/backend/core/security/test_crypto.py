"""
SecureHasher 模块测试

测试安全哈希计算器的功能：
- 字符串哈希
- 对象哈希
- 文件哈希
- 算法支持
- 错误处理

TDD Phase: Red - 先写测试，看测试失败
"""

import pytest
import tempfile
import os
from pathlib import Path


class TestSecureHasher:
    """测试 SecureHasher 类"""

    def test_hash_string_sha256(self):
        """测试SHA-256字符串哈希"""
        from backend.core.crypto import SecureHasher

        result = SecureHasher.hash_string("hello")
        # SHA-256哈希应该是64位十六进制字符串
        assert len(result) == 64
        assert isinstance(result, str)
        # 验证是有效的十六进制
        assert all(c in '0123456789abcdef' for c in result)

    def test_hash_string_consistency(self):
        """测试相同输入产生相同哈希"""
        from backend.core.crypto import SecureHasher

        input_str = "test input"
        hash1 = SecureHasher.hash_string(input_str)
        hash2 = SecureHasher.hash_string(input_str)

        assert hash1 == hash2

    def test_hash_string_different_inputs(self):
        """测试不同输入产生不同哈希"""
        from backend.core.crypto import SecureHasher

        hash1 = SecureHasher.hash_string("input1")
        hash2 = SecureHasher.hash_string("input2")

        assert hash1 != hash2

    def test_hash_string_sha512(self):
        """测试SHA-512算法"""
        from backend.core.crypto import SecureHasher

        result = SecureHasher.hash_string("hello", algorithm='sha512')
        # SHA-512哈希应该是128位十六进制字符串
        assert len(result) == 128
        assert isinstance(result, str)

    def test_hash_string_unsupported_algorithm(self):
        """测试不支持的算法抛出ValueError"""
        from backend.core.crypto import SecureHasher

        with pytest.raises(ValueError, match="Unsupported algorithm"):
            SecureHasher.hash_string("hello", algorithm='md5')

    def test_hash_object_simple_dict(self):
        """测试简单字典对象哈希"""
        from backend.core.crypto import SecureHasher

        data = {'name': 'Alice', 'age': 30}
        result = SecureHasher.hash_object(data)

        assert len(result) == 64
        assert isinstance(result, str)

    def test_hash_object_dict_sort_keys(self):
        """测试字典键排序确保哈希一致性"""
        from backend.core.crypto import SecureHasher

        # 键顺序不同，但内容相同
        data1 = {'name': 'Alice', 'age': 30}
        data2 = {'age': 30, 'name': 'Alice'}

        hash1 = SecureHasher.hash_object(data1, sort_keys=True)
        hash2 = SecureHasher.hash_object(data2, sort_keys=True)

        assert hash1 == hash2

    def test_hash_object_list(self):
        """测试列表对象哈希"""
        from backend.core.crypto import SecureHasher

        data = [1, 2, 3, 'test']
        result = SecureHasher.hash_object(data)

        assert len(result) == 64
        assert isinstance(result, str)

    def test_hash_object_nested_structure(self):
        """测试嵌套结构哈希"""
        from backend.core.crypto import SecureHasher

        data = {
            'users': [
                {'name': 'Alice', 'age': 30},
                {'name': 'Bob', 'age': 25}
            ],
            'count': 2
        }
        result = SecureHasher.hash_object(data)

        assert len(result) == 64
        assert isinstance(result, str)

    def test_hash_object_consistency(self):
        """测试相同对象产生相同哈希"""
        from backend.core.crypto import SecureHasher

        data = {'key': 'value', 'number': 42}
        hash1 = SecureHasher.hash_object(data)
        hash2 = SecureHasher.hash_object(data)

        assert hash1 == hash2

    def test_hash_file_small_file(self):
        """测试小文件哈希"""
        from backend.core.crypto import SecureHasher

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content for hashing")
            temp_path = f.name

        try:
            result = SecureHasher.hash_file(temp_path)
            assert len(result) == 64
            assert isinstance(result, str)
        finally:
            os.unlink(temp_path)

    def test_hash_file_large_file(self):
        """测试大文件哈希（分块读取）"""
        from backend.core.crypto import SecureHasher

        # 创建较大的临时文件（1MB）
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b'x' * (1024 * 1024))
            temp_path = f.name

        try:
            result = SecureHasher.hash_file(temp_path, chunk_size=8192)
            assert len(result) == 64
            assert isinstance(result, str)
        finally:
            os.unlink(temp_path)

    def test_hash_file_consistency(self):
        """测试相同文件产生相同哈希"""
        from backend.core.crypto import SecureHasher

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("consistent content")
            temp_path = f.name

        try:
            hash1 = SecureHasher.hash_file(temp_path)
            hash2 = SecureHasher.hash_file(temp_path)
            assert hash1 == hash2
        finally:
            os.unlink(temp_path)

    def test_hash_file_not_found(self):
        """测试文件不存在抛出错误"""
        from backend.core.crypto import SecureHasher

        with pytest.raises(FileNotFoundError):
            SecureHasher.hash_file('/nonexistent/path/to/file.txt')


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_compute_hash_string(self):
        """测试compute_hash处理字符串"""
        from backend.core.crypto import compute_hash

        result = compute_hash("hello")
        assert len(result) == 64
        assert isinstance(result, str)

    def test_compute_hash_object(self):
        """测试compute_hash处理对象"""
        from backend.core.crypto import compute_hash

        result = compute_hash({'key': 'value'})
        assert len(result) == 64
        assert isinstance(result, str)

    def test_compute_cache_key(self):
        """测试compute_cache_key函数"""
        from backend.core.crypto import compute_cache_key

        data = {'event': 'login', 'fields': ['user_id', 'timestamp']}
        result = compute_cache_key(data)

        assert len(result) == 64
        assert isinstance(result, str)

    def test_compute_cache_key_consistency(self):
        """测试compute_cache_key一致性"""
        from backend.core.crypto import compute_cache_key

        data = {'event': 'login', 'fields': ['user_id', 'timestamp']}
        key1 = compute_cache_key(data)
        key2 = compute_cache_key(data)

        assert key1 == key2


class TestSecurityProperties:
    """测试安全属性"""

    def test_avoids_md5(self):
        """验证不使用MD5算法"""
        from backend.core.crypto import SecureHasher

        # 尝试使用md5应该失败
        with pytest.raises(ValueError):
            SecureHasher.hash_string("test", algorithm='md5')

    def test_default_algorithm_is_secure(self):
        """验证默认算法是安全的（sha256）"""
        from backend.core.crypto import SecureHasher

        assert SecureHasher.DEFAULT_ALGORITHM == 'sha256'

    def test_sha256_output_length(self):
        """验证SHA-256输出长度正确"""
        from backend.core.crypto import SecureHasher

        result = SecureHasher.hash_string("any input")
        # SHA-256总是产生64位十六进制字符串
        assert len(result) == 64

    def test_sha512_output_length(self):
        """验证SHA-512输出长度正确"""
        from backend.core.crypto import SecureHasher

        result = SecureHasher.hash_string("any input", algorithm='sha512')
        # SHA-512总是产生128位十六进制字符串
        assert len(result) == 128
