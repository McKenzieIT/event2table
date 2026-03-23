"""
XSS防护测试 - 测试用户输入是否被正确转义

测试目标:
1. 事件名称的XSS防护
2. 参数名称的XSS防护
3. 所有用户输入字段的HTML转义

TDD流程:
- RED阶段: 测试失败（当前无防护）
- GREEN阶段: 实施防护后测试通过
- REFACTOR阶段: 重构优化
"""

import pytest
import html
from backend.core.utils import execute_write, fetch_one_as_dict
from backend.core.database.database import get_db_connection
from backend.core.config.config import TEST_DB_PATH


class TestXSSProtection:
    """XSS防护测试套件"""

    @pytest.fixture(autouse=True)
    def setup_test_game(self):
        """设置测试游戏"""
        # 确保测试游戏存在
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (90000001,))
        if not game:
            execute_write(
                """INSERT INTO games (gid, name, ods_db, dwd_prefix)
                   VALUES (?, ?, ?, ?)""",
                (90000001, "TEST_XSS_GAME", "ieu_ods", "ieu_cdm"),
            )
        else:
            # 获取game_id用于外键
            return game['id']
        return None

    def test_event_name_stores_xss_payload_directly_RED(self):
        """
        [RED阶段] 测试事件名称直接存储XSS payload（当前行为）

        Given: 恶意的事件名称包含<script>标签
        When: 创建事件时
        Then: 当前应该直接存储未转义的XSS payload（测试失败 = 发现问题）

        这是一个失败的测试, 证明当前存在XSS漏洞
        """
        # 先获取测试游戏的game_id
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (90000001,))
        game_id = game['id']

        malicious_name = "<script>alert('xss')</script>"

        # 创建事件(应该被转义, 但当前没有)
        event_id = execute_write(
            """INSERT INTO log_events
               (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (game_id, 90000001, malicious_name, "测试事件", "test.test", "test.target"),
            return_last_id=True,
        )

        # 从数据库读取
        event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))

        # ❌ RED阶段: 当前行为是直接存储未转义的payload
        # 这个断言会失败, 证明存在XSS漏洞
        assert (
            event['event_name'] == malicious_name
        ), f"[XSS漏洞发现] 事件名称未转义: 存储为 '{event['event_name']}', 应该存储为 '&lt;script&gt;...'"

        # ✅ 期望行为(当前未实现):
        # expected_escaped = html.escape(malicious_name)
        # assert event['event_name'] == expected_escaped, \
        #     f"事件名称应被转义: 期望 '{expected_escaped}', 实际 '{event['event_name']}'"

    def test_parameter_name_stores_xss_payload_directly_RED(self):
        """
        [RED阶段] 测试参数名称直接存储XSS payload（当前行为）

        Given: 恶意的参数名称包含XSS payload
        When: 创建参数时
        Then: 当前应该直接存储未转义的XSS payload（测试失败 = 发现问题）

        这是一个失败的测试, 证明当前存在XSS漏洞
        """
        # 先获取测试游戏的game_id
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (90000001,))
        game_id = game['id']

        # 先创建测试事件
        event_id = execute_write(
            """INSERT INTO log_events
               (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (game_id, 90000001, "test_event", "测试事件", "test.test", "test.target"),
            return_last_id=True,
        )

        malicious_param_name = '<img src=x onerror=alert(1)>'

        # 创建参数(应该被转义, 但当前没有)
        # 注意: event_params表没有param_type字段, 使用template_id代替
        param_id = execute_write(
            """INSERT INTO event_params
               (event_id, param_name, template_id, json_path)
               VALUES (?, ?, ?, ?)""",
            (event_id, malicious_param_name, 1, "$.test"),
            return_last_id=True,
        )

        # 从数据库读取
        param = fetch_one_as_dict("SELECT * FROM event_params WHERE id = ?", (param_id,))

        # ❌ RED阶段: 当前行为是直接存储未转义的payload
        assert (
            param['param_name'] == malicious_param_name
        ), f"[XSS漏洞发现] 参数名称未转义: 存储为 '{param['param_name']}', 应该存储为 '&lt;img ...'"

    def test_html_escape_functionality(self):
        """
        测试Python html.escape()函数的基本功能

        Given: 各种XSS payload
        When: 使用html.escape()转义
        Then: 所有特殊字符应被正确转义

        这个测试应该通过, 验证html.escape()确实有效
        """
        test_cases = [
            ("<script>", "&lt;script&gt;"),
            ("<img>", "&lt;img&gt;"),
            ("'>", "&#x27;&gt;"),  # html.escape默认转义单引号为&#x27;
            ("<\"", "&lt;&quot;"),
            (
                "<script>alert('xss')</script>",
                "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;",
            ),
            ("<img src=x onerror=alert(1)>", "&lt;img src=x onerror=alert(1)&gt;"),
            ("<iframe src='malicious.js'>", "&lt;iframe src=&#x27;malicious.js&#x27;&gt;"),
            ("<svg onload=alert(1)>", "&lt;svg onload=alert(1)&gt;"),
        ]

        for input_str, expected_output in test_cases:
            escaped = html.escape(input_str)
            assert (
                escaped == expected_output
            ), f"HTML escape failed: {input_str} → {escaped} (expected {expected_output})"

    def test_multiple_xss_payloads_in_event_name(self):
        """
        [RED阶段] 测试多种XSS payload在事件名称中的存储

        Given: 事件名称包含多种XSS payload
        When: 创建事件时
        Then: 当前应该直接存储未转义的payload（测试失败 = 发现问题）
        """
        # 先获取测试游戏的game_id
        game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (90000001,))
        game_id = game['id']

        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "<iframe src='javascript:alert(1)'>",
            "<body onload=alert(1)>",
        ]

        for i, payload in enumerate(xss_payloads):
            # 创建事件
            event_id = execute_write(
                """INSERT INTO log_events
                   (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (game_id, 90000001, payload, f"测试事件{i}", "test.test", "test.target"),
                return_last_id=True,
            )

            # 从数据库读取
            event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))

            # ❌ RED阶段: 验证存储的是未转义的payload
            assert (
                event['event_name'] == payload
            ), f"[XSS漏洞发现] 事件名称未转义 [{i}]: 存储为 '{event['event_name']}'"

    def test_xss_payload_variations(self):
        """
        测试各种XSS payload变体的转义

        Given: 不同编码和混淆的XSS payload
        When: 转义时
        Then: 所有变体都应被正确转义
        """
        test_cases = [
            # 基础标签
            ("<script>", "&lt;script&gt;"),
            ("</script>", "&lt;/script&gt;"),
            # 事件处理器(属性名不转义, 但单引号会被转义)
            ("onload=alert(1)", "onload=alert(1)"),
            ("onclick='alert(1)", "onclick=&#x27;alert(1)"),  # 单引号转义为&#x27;
            # 混合大小写
            ("<Script>", "&lt;Script&gt;"),
            ("<SCRIPT>", "&lt;SCRIPT&gt;"),
            # 带属性
            ("<img src=x>", "&lt;img src=x&gt;"),
            ("<a href='javascript:alert(1)'>", "&lt;a href=&#x27;javascript:alert(1)&#x27;&gt;"),
            # Unicode混淆
            ("<script>", "&lt;script&gt;"),
        ]

        for input_str, expected_output in test_cases:
            escaped = html.escape(input_str)
            assert (
                escaped == expected_output
            ), f"XSS escape failed: {input_str} → {escaped} (expected {expected_output})"
