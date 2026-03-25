"""
输入验证测试 - P0-8

测试目标: 验证Pydantic Schema输入验证
当前状态: 已有基本验证（测试应该通过）

TDD Phase: RED → GREEN - 验证现有Schema的输入验证
"""

import pytest
from pydantic import ValidationError

from backend.models.schemas import EventCreate, EventParameterCreate


def test_parameter_create_requires_valid_name():
    """
    测试参数创建需要有效的参数名

    验证规则:
    - 不能为空
    - 不能包含空格
    - 长度限制: 1-100字符
    """
    from backend.models.schemas import EventParameterCreate

    # 测试1: 空参数名
    with pytest.raises(ValidationError) as exc_info:
        EventParameterCreate(param_name="", template_id=1)  # ❌ 空字符串
    assert "param_name不能为空" in str(exc_info.value)

    # 测试2: 包含空格
    with pytest.raises(ValidationError) as exc_info:
        EventParameterCreate(param_name="user name", template_id=1)  # ❌ 包含空格
    assert "param_name不能包含空格" in str(exc_info.value)

    # 测试3: 仅空格
    with pytest.raises(ValidationError) as exc_info:
        EventParameterCreate(param_name="   ", template_id=1)  # ❌ 仅空格
    # 应该被strip后变为空字符串
    assert "param_name不能为空" in str(exc_info.value)


def test_event_create_requires_valid_fields():
    """
    测试事件创建需要有效的字段
    """
    from backend.models.schemas import EventCreate, EventParameterCreate

    # 测试4: 无效的event_name(包含空格)
    with pytest.raises(ValidationError) as exc_info:
        EventCreate(
            game_gid=90000001,
            event_name="test event",  # ❌ 包含空格
            event_name_cn="测试事件",
            category_id=1,
            source_table="test.test",
            parameters=[],
        )
    assert "event_name不能包含空格" in str(exc_info.value)

    # 测试5: 空的event_name
    with pytest.raises(ValidationError) as exc_info:
        EventCreate(
            game_gid=90000001,
            event_name="",  # ❌ 空字符串
            event_name_cn="测试事件",
            category_id=1,
            source_table="test.test",
            parameters=[],
        )
    assert "event_name不能为空" in str(exc_info.value)

    # 测试6: 至少需要一个参数
    with pytest.raises(ValidationError) as exc_info:
        EventCreate(
            game_gid=90000001,
            event_name="test_event",
            event_name_cn="测试事件",
            category_id=1,
            source_table="test.test",
            parameters=[],  # ❌ 空参数列表
        )
    assert "至少需要一个参数" in str(exc_info.value)


def test_json_path_validation():
    """
    测试JSON路径格式验证
    """
    from backend.models.schemas import EventParameterCreate

    # 测试7: 无效的JSON路径(不以$.开头)
    with pytest.raises(ValidationError) as exc_info:
        EventParameterCreate(
            param_name="test_param", json_path="invalid", template_id=1  # ❌ 不以$.开头
        )
    assert "json_path必须以'$.'开头" in str(exc_info.value)

    # 测试8: 正确的JSON路径格式
    try:
        EventParameterCreate(param_name="test_param", json_path="$.zoneId", template_id=1)  # ✅ 正确格式
    except ValidationError:
        pytest.fail("正确的JSON路径格式应该通过验证")

    # 测试9: 空JSON路径(应该允许, 因为它是可选的)
    try:
        EventParameterCreate(param_name="test_param", json_path="", template_id=1)  # ✅ 空字符串是可选字段
    except ValidationError:
        pytest.fail("空JSON路径应该被允许（它是可选字段）")


def test_xss_prevention_in_parameter_name():
    """
    测试参数名的XSS防护
    """
    from backend.models.schemas import EventParameterCreate

    # 测试10: HTML标签应该被转义(在中文名中)
    param = EventParameterCreate(
        param_name="test_param",
        param_name_cn="<script>alert('xss')</script>",  # ❌ HTML标签
        template_id=1,
    )
    assert "&lt;script&gt;" in param.param_name_cn
    assert "<script>" not in param.param_name_cn


def test_xss_prevention_in_event_name():
    """
    测试事件名的XSS防护
    """
    from backend.models.schemas import EventCreate, EventParameterCreate

    # 测试11: HTML标签应该被转义(在中文名中)
    event = EventCreate(
        game_gid=90000001,
        event_name="test_event",
        event_name_cn="<img src=x onerror=alert('xss')>",  # ❌ HTML标签
        category_id=1,
        source_table="test.test",
        parameters=[EventParameterCreate(param_name="test_param", template_id=1)],
    )
    assert "&lt;img" in event.event_name_cn
    assert "<img" not in event.event_name_cn
