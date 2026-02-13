#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Utils 单元测试

测试 backend.core.utils 中的工具函数
"""

import pytest
import sqlite3
import uuid
from backend.core.utils import (
    fetch_one_as_dict,
    fetch_all_as_dict,
    execute_write,
    json_success_response,
    json_error_response,
    validate_json_request,
    safe_int_convert,
)


class TestFetchFunctions:
    """测试数据库查询函数"""

    @pytest.mark.database
    def test_fetch_one_as_dict_success(self, db):
        """测试成功查询单条数据"""
        # 创建测试数据 - 使用唯一GID
        unique_gid = f"test_{uuid.uuid4().hex[:8]}"
        cursor = db.execute("""
            INSERT INTO games (gid, name, ods_db)
            VALUES (?, ?, ?)
        """, (unique_gid, "Fetch Test", "test_db"))
        db.commit()

        # 测试查询
        result = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (unique_gid,))

        assert result is not None
        assert result["gid"] == unique_gid
        assert result["name"] == "Fetch Test"

    @pytest.mark.database
    def test_fetch_one_as_dict_not_found(self, db):
        """测试查询不存在的数据"""
        result = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", ("NONEXISTENT",))
        assert result is None

    @pytest.mark.database
    def test_fetch_all_as_dict(self, db):
        """测试查询多条数据"""
        # 创建多条测试数据 - 使用唯一GID
        base_gid = uuid.uuid4().hex[:8]
        for i in range(3):
            db.execute("""
                INSERT INTO games (gid, name, ods_db)
                VALUES (?, ?, ?)
            """, (f"{base_gid}_{i}", f"Game {i}", "test_db"))
        db.commit()

        # 测试查询
        results = fetch_all_as_dict("SELECT * FROM games WHERE gid LIKE ?", (f"{base_gid}%",))

        assert len(results) == 3


class TestExecuteWrite:
    """测试数据库写操作函数"""

    @pytest.mark.database
    def test_execute_write_insert(self, db):
        """测试插入操作"""
        unique_gid = f"test_{uuid.uuid4().hex[:8]}"
        affected = execute_write("""
            INSERT INTO games (gid, name, ods_db)
            VALUES (?, ?, ?)
        """, (unique_gid, "Write Test", "test_db"))

        assert affected == 1

        # 验证数据已插入
        result = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (unique_gid,))
        assert result is not None
        assert result["name"] == "Write Test"

    @pytest.mark.database
    def test_execute_write_update(self, db, sample_game):
        """测试更新操作"""
        new_name = "Updated Name"
        affected = execute_write("""
            UPDATE games SET name = ? WHERE gid = ?
        """, (new_name, sample_game["gid"]))

        assert affected == 1

        # 验证数据已更新
        result = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (sample_game["gid"],))
        assert result["name"] == new_name


class TestJSONResponses:
    """测试JSON响应函数"""

    def test_json_success_response(self, app):
        """测试成功响应"""
        with app.app_context():
            response_obj, status = json_success_response(data={"test": "data"}, message="Success")

            assert status == 200
            # Get JSON data from response
            response_json = response_obj.get_json()
            assert "success" in response_json
            assert response_json["data"]["test"] == "data"
            assert response_json["message"] == "Success"
            assert "timestamp" in response_json

    def test_json_error_response(self, app):
        """测试错误响应"""
        with app.app_context():
            response_obj, status = json_error_response("Error message", status_code=400)

            assert status == 400
            # Get JSON data from response
            response_json = response_obj.get_json()
            assert "error" in response_json
            assert response_json["error"] == "Error message"
            assert "timestamp" in response_json

    def test_json_error_response_with_code(self, app):
        """测试带自定义错误码的错误响应"""
        with app.app_context():
            response_obj, status = json_error_response("Not found", status_code=404)

            assert status == 404


class TestValidationFunctions:
    """测试验证函数"""

    def test_validate_json_request_success(self):
        """测试JSON验证成功"""
        from flask import Flask
        app = Flask(__name__)

        with app.test_request_context(
            json={"key": "value"},
            content_type="application/json"
        ):
            is_valid, data, error = validate_json_request(["key"])
            assert is_valid is True
            assert data["key"] == "value"
            assert error is None

    def test_validate_json_request_missing_field(self):
        """测试JSON验证缺少字段"""
        from flask import Flask
        app = Flask(__name__)

        with app.test_request_context(
            json={"other": "value"},
            content_type="application/json"
        ):
            is_valid, data, error = validate_json_request(["key"])
            assert is_valid is False
            assert "Missing required fields" in error

    def test_safe_int_convert_valid(self):
        """测试整数转换成功"""
        assert safe_int_convert("123") == 123
        assert safe_int_convert("456") == 456

    def test_safe_int_convert_invalid(self):
        """测试整数转换失败"""
        # safe_int_convert returns 0 for invalid input (not None)
        assert safe_int_convert("abc") == 0
        assert safe_int_convert("") == 0
        assert safe_int_convert(None) == 0
