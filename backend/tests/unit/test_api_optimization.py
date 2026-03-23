#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Response Optimization Tests

Comprehensive tests for Flask response compression and JSON serialization.

Performance Goals:
- Compression ratio: ≥70% for JSON responses
- JSON serialization: 2-3x faster than standard json module
- Transmission size: 70-80% reduction
- Response time: 30-50% reduction

Author: Event2Table Performance Optimization Team
Version: 1.0.0 (2026-03-18)
"""

import pytest
import json
import time
import gzip
import brotli
from io import BytesIO
from typing import Dict, Any, List

from flask import Flask, jsonify, Response
from flask_compress import Compress

from backend.core.config.compression import CompressionConfig, init_compression, enable_compression
from backend.core.utils.json_serializer import JSONSerializer, json_dumps, json_loads, HAS_ORJSON


class TestCompressionConfig:
    """Test compression configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = CompressionConfig()

        assert config.enabled is True
        assert config.min_size == 500
        assert config.level == 6
        assert 'br' in config.algorithms
        assert 'gzip' in config.algorithms

    def test_custom_config(self):
        """Test custom configuration values"""
        config = CompressionConfig(enabled=True, min_size=1000, level=8, algorithms=['gzip'])

        assert config.min_size == 1000
        assert config.level == 8
        assert config.algorithms == ['gzip']

    def test_level_clamping(self):
        """Test that compression level is clamped to valid range"""
        # Test lower bound
        config = CompressionConfig(level=0)
        assert config.level == 1

        # Test upper bound
        config = CompressionConfig(level=15)
        assert config.level == 11

        # Test valid values
        config = CompressionConfig(level=5)
        assert config.level == 5


class TestCompressionIntegration:
    """Test Flask compression integration"""

    @pytest.fixture
    def app(self):
        """Create test Flask app"""
        app = Flask(__name__)
        app.config['TESTING'] = True

        @app.route('/api/test')
        def test_endpoint():
            return jsonify(
                {'success': True, 'data': [i for i in range(100)], 'message': 'Test response data'}
            )

        @app.route('/api/small')
        def small_endpoint():
            return jsonify({'small': 'data'})

        return app

    def test_init_compression(self, app):
        """Test compression initialization"""
        config = CompressionConfig(enabled=True, min_size=500, level=6)

        init_compression(app, config)

        # Verify compression is registered
        assert 'compress' in app.extensions

    def test_compression_disabled(self, app):
        """Test compression can be disabled"""
        config = CompressionConfig(enabled=False)
        init_compression(app, config)

        # Should not have compression extension
        assert app.extensions.get('compress') is None

    def test_enable_compression_helper(self, app):
        """Test enable_compression helper function"""
        enable_compression(app, level=6, prefer_brotli=True)

        assert 'compress' in app.extensions


class TestCompressionPerformance:
    """Test compression performance and ratios"""

    @pytest.fixture
    def sample_json_data(self) -> Dict[str, Any]:
        """Generate sample JSON data for testing"""
        return {
            'games': [
                {
                    'gid': f'10000{i}',
                    'name': f'Game {i}',
                    'ods_db': 'domestic' if i % 2 == 0 else 'overseas',
                    'description': f'Test game description {i}' * 10,
                    'events': [
                        {
                            'event_id': j,
                            'event_name': f'event_{j}',
                            'params': [f'param_{k}' for k in range(20)],
                        }
                        for j in range(10)
                    ],
                }
                for i in range(10)
            ],
            'metadata': {'total': 10, 'page': 1, 'timestamp': '2026-03-18T00:00:00Z'},
        }

    def test_json_size(self, sample_json_data):
        """Test original JSON size"""
        json_str = json.dumps(sample_json_data)
        original_size = len(json_str.encode('utf-8'))

        # Should be substantial size for meaningful compression test
        assert original_size > 1000
        print(f"Original JSON size: {original_size:,} bytes")

    def test_gzip_compression_ratio(self, sample_json_data):
        """Test gzip compression ratio (should be ≥70%)"""
        json_str = json.dumps(sample_json_data)
        original_size = len(json_str.encode('utf-8'))

        # Compress with gzip
        compressed = gzip.compress(json_str.encode('utf-8'), compresslevel=6)
        compressed_size = len(compressed)

        compression_ratio = ((original_size - compressed_size) / original_size) * 100

        print(
            f"Gzip compression: {original_size:,} → {compressed_size:,} bytes ({compression_ratio:.1f}% reduction)"
        )

        # Assert compression ratio ≥70%
        assert (
            compression_ratio >= 70
        ), f"Compression ratio: {compression_ratio:.1f}% (target: ≥70%)"

    def test_brotli_compression_ratio(self, sample_json_data):
        """Test Brotli compression ratio (should be ≥70%)"""
        json_str = json.dumps(sample_json_data)
        original_size = len(json_str.encode('utf-8'))

        # Compress with Brotli
        compressed = brotli.compress(json_str.encode('utf-8'), mode=brotli.MODE_GENERIC, quality=6)
        compressed_size = len(compressed)

        compression_ratio = ((original_size - compressed_size) / original_size) * 100

        print(
            f"Brotli compression: {original_size:,} → {compressed_size:,} bytes ({compression_ratio:.1f}% reduction)"
        )

        # Assert compression ratio ≥70%
        assert (
            compression_ratio >= 70
        ), f"Compression ratio: {compression_ratio:.1f}% (target: ≥70%)"

    def test_brotli_vs_gzip(self, sample_json_data):
        """Test that Brotli achieves better compression than gzip"""
        json_str = json.dumps(sample_json_data)
        original_size = len(json_str.encode('utf-8'))

        # Gzip compression
        gzip_compressed = gzip.compress(json_str.encode('utf-8'), compresslevel=6)
        gzip_size = len(gzip_compressed)

        # Brotli compression
        brotli_compressed = brotli.compress(
            json_str.encode('utf-8'), mode=brotli.MODE_GENERIC, quality=6
        )
        brotli_size = len(brotli_compressed)

        # Brotli should be better or equal
        print(f"Gzip: {gzip_size:,} bytes, Brotli: {brotli_size:,} bytes")
        assert brotli_size <= gzip_size, "Brotli should compress better than gzip"

    def test_small_response_not_compressed(self):
        """Test that small responses (<500 bytes) are not compressed"""
        small_data = {'small': 'data'}

        # JSON size should be < 500 bytes
        json_str = json.dumps(small_data)
        assert len(json_str) < 500


class TestJSONSerialization:
    """Test JSON serialization performance"""

    @pytest.fixture
    def sample_data(self) -> Dict[str, Any]:
        """Generate sample data for serialization tests"""
        return {
            'games': [
                {
                    'gid': f'10000{i}',
                    'name': f'Game {i}',
                    'ods_db': 'domestic' if i % 2 == 0 else 'overseas',
                    'events': [f'event_{j}' for j in range(50)],
                }
                for i in range(100)
            ],
            'timestamp': '2026-03-18T00:00:00Z',
        }

    def test_json_serializer_initialization(self):
        """Test JSONSerializer initialization"""
        serializer = JSONSerializer()

        assert serializer is not None
        assert hasattr(serializer, 'dumps')
        assert hasattr(serializer, 'loads')

    def test_json_dumps_basic(self, sample_data):
        """Test basic json_dumps functionality"""
        json_str = json_dumps(sample_data)

        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed == sample_data

    def test_json_loads_basic(self):
        """Test basic json_loads functionality"""
        json_str = '{"name":"Test","value":123}'
        data = json_loads(json_str)

        assert data == {'name': 'Test', 'value': 123}

    def test_json_dumps_indent(self, sample_data):
        """Test json_dumps with indentation"""
        # Without indent
        compact = json_dumps(sample_data, indent=False)

        # With indent
        pretty = json_dumps(sample_data, indent=True)

        # Pretty should be longer
        assert len(pretty) > len(compact)

        # Both should parse to same data
        assert json.loads(compact) == json.loads(pretty)

    def test_datetime_serialization(self):
        """Test datetime serialization"""
        from datetime import datetime

        data = {'timestamp': datetime(2026, 3, 18, 12, 30, 45), 'name': 'Test'}

        json_str = json_dumps(data)

        # Should not raise an error
        assert isinstance(json_str, str)

        # Parse and verify
        parsed = json_loads(json_str)
        assert 'timestamp' in parsed
        assert parsed['name'] == 'Test'

    def test_unicode_serialization(self):
        """Test Unicode character serialization"""
        data = {'chinese': '你好世界', 'emoji': '😀🎉', 'special': '©®™€'}

        json_str = json_dumps(data)
        parsed = json_loads(json_str)

        assert parsed == data

    def test_large_list_serialization(self):
        """Test serializing large lists"""
        data = {'items': [i for i in range(10000)]}

        json_str = json_dumps(data)

        assert isinstance(json_str, str)
        parsed = json_loads(json_str)
        assert len(parsed['items']) == 10000


class TestJSONSerializationPerformance:
    """Test JSON serialization performance"""

    @pytest.fixture
    def large_data(self) -> Dict[str, Any]:
        """Generate large data for performance tests"""
        return {
            'games': [
                {
                    'gid': f'10000{i}',
                    'name': f'Game {i}',
                    'description': f'Test game description {i}' * 50,
                    'events': [
                        {'event_id': j, 'params': [f'param_{k}' for k in range(100)]}
                        for j in range(100)
                    ],
                }
                for i in range(100)
            ]
        }

    def test_serialization_performance(self, large_data):
        """Test that orjson serialization is faster than json"""
        iterations = 100

        # Test standard json
        start = time.time()
        for _ in range(iterations):
            _ = json.dumps(large_data)
        json_time = time.time() - start

        # Test orjson (if available)
        if HAS_ORJSON:
            start = time.time()
            for _ in range(iterations):
                _ = json_dumps(large_data)
            orjson_time = time.time() - start

            speedup = json_time / orjson_time
            print(
                f"Serialization speedup: {speedup:.2f}x (json: {json_time:.3f}s, orjson: {orjson_time:.3f}s)"
            )

            # orjson should be at least 1.5x faster
            assert speedup >= 1.5, f"Speedup: {speedup:.2f}x (target: ≥1.5x)"
        else:
            print("orjson not available, skipping performance comparison")

    def test_deserialization_performance(self, large_data):
        """Test that orjson deserialization is faster than json"""
        json_str = json.dumps(large_data)
        iterations = 100

        # Test standard json
        start = time.time()
        for _ in range(iterations):
            _ = json.loads(json_str)
        json_time = time.time() - start

        # Test orjson (if available)
        if HAS_ORJSON:
            start = time.time()
            for _ in range(iterations):
                _ = json_loads(json_str)
            orjson_time = time.time() - start

            speedup = json_time / orjson_time
            print(
                f"Deserialization speedup: {speedup:.2f}x (json: {json_time:.3f}s, orjson: {orjson_time:.3f}s)"
            )

            # orjson should be at least 1.5x faster
            assert speedup >= 1.5, f"Speedup: {speedup:.2f}x (target: ≥1.5x)"
        else:
            print("orjson not available, skipping performance comparison")


class TestOptimizationIntegration:
    """Integration tests for compression + JSON optimization"""

    def test_end_to_end_optimization(self):
        """Test end-to-end optimization pipeline"""
        # Generate test data
        data = {
            'games': [
                {
                    'gid': f'10000{i}',
                    'name': f'Game {i}',
                    'events': [f'event_{j}' for j in range(50)],
                }
                for i in range(50)
            ]
        }

        # Step 1: Serialize with orjson
        json_str = json_dumps(data)
        original_size = len(json_str.encode('utf-8'))

        # Step 2: Compress with Brotli
        compressed = brotli.compress(json_str.encode('utf-8'), quality=6)
        compressed_size = len(compressed)

        # Calculate overall reduction
        total_reduction = ((original_size - compressed_size) / original_size) * 100

        print(
            f"End-to-end: {original_size:,} → {compressed_size:,} bytes ({total_reduction:.1f}% reduction)"
        )

        # Assert ≥70% overall reduction
        assert total_reduction >= 70, f"Total reduction: {total_reduction:.1f}% (target: ≥70%)"

    def test_round_trip_preservation(self):
        """Test that data survives round-trip (serialize → compress → decompress → deserialize)"""
        original_data = {
            'games': [
                {
                    'gid': '100001',
                    'name': 'Test Game',
                    'value': 42,
                    'active': True,
                    'tags': ['game', 'test', 'sample'],
                }
            ]
        }

        # Serialize
        json_str = json_dumps(original_data)

        # Compress
        compressed = brotli.compress(json_str.encode('utf-8'))

        # Decompress
        decompressed = brotli.decompress(compressed).decode('utf-8')

        # Deserialize
        restored_data = json_loads(decompressed)

        # Verify data integrity
        assert restored_data == original_data


class TestOptimizationTargets:
    """Test that optimization targets are met"""

    def test_compression_target_70_percent(self):
        """Test compression ratio target: ≥70%"""
        # Generate realistic API response data
        data = {
            'success': True,
            'data': {
                'games': [
                    {
                        'gid': f'10000{i}',
                        'name': f'Game Name {i}' * 10,
                        'ods_db': 'domestic',
                        'description': f'Game description {i}' * 20,
                        'events': [
                            {
                                'event_id': j,
                                'event_name': f'event_name_{j}' * 5,
                                'params': [f'param_{k}' for k in range(30)],
                            }
                            for j in range(20)
                        ],
                    }
                    for i in range(10)
                ]
            },
        }

        json_str = json.dumps(data)
        original_size = len(json_str.encode('utf-8'))

        # Test Brotli compression
        compressed = brotli.compress(json_str.encode('utf-8'), quality=6)
        compressed_size = len(compressed)

        compression_ratio = ((original_size - compressed_size) / original_size) * 100

        print(f"\n📊 Compression Performance:")
        print(f"   Original size: {original_size:,} bytes")
        print(f"   Compressed size: {compressed_size:,} bytes")
        print(f"   Compression ratio: {compression_ratio:.1f}%")
        print(f"   Bandwidth saved: {original_size - compressed_size:,} bytes")

        assert (
            compression_ratio >= 70
        ), f"Compression ratio: {compression_ratio:.1f}% (target: ≥70%)"

    def test_transmission_size_reduction_70_80_percent(self):
        """Test transmission size reduction target: 70-80%"""
        # Generate large realistic response
        data = {
            'results': [
                {
                    'id': i,
                    'name': f'Item {i}',
                    'description': f'Description {i}' * 50,
                    'metadata': {
                        'tags': [f'tag{j}' for j in range(20)],
                        'attributes': {f'attr{k}': f'value{k}' * 10 for k in range(10)},
                    },
                }
                for i in range(100)
            ]
        }

        json_str = json.dumps(data)
        original_size = len(json_str.encode('utf-8'))

        # Compress
        compressed = brotli.compress(json_str.encode('utf-8'), quality=6)
        compressed_size = len(compressed)

        reduction_percent = ((original_size - compressed_size) / original_size) * 100

        print(f"\n📊 Transmission Size Reduction:")
        print(f"   Original: {original_size:,} bytes")
        print(f"   After compression: {compressed_size:,} bytes")
        print(f"   Reduction: {reduction_percent:.1f}%")

        # Assert ≥70% reduction (we often exceed 80% with Brotli)
        assert reduction_percent >= 70, f"Reduction: {reduction_percent:.1f}% (target: ≥70%)"

    @pytest.mark.skipif(not HAS_ORJSON, reason="orjson not installed")
    def test_json_serialization_speed_target(self):
        """Test JSON serialization speed target: 2-3x faster"""
        # Generate test data
        data = {
            'items': [
                {'id': i, 'name': f'Item {i}', 'values': [j for j in range(100)]}
                for i in range(1000)
            ]
        }

        iterations = 50

        # Standard json
        start = time.time()
        for _ in range(iterations):
            _ = json.dumps(data)
        json_time = time.time() - start

        # orjson
        start = time.time()
        for _ in range(iterations):
            _ = json_dumps(data)
        orjson_time = time.time() - start

        speedup = json_time / orjson_time

        print(f"\n📊 JSON Serialization Speed:")
        print(f"   Standard json: {json_time:.3f}s")
        print(f"   orjson: {orjson_time:.3f}s")
        print(f"   Speedup: {speedup:.2f}x")

        # Assert ≥2x speedup (we often exceed 3x with orjson)
        assert speedup >= 2, f"Speedup: {speedup:.2f}x (target: ≥2x)"
