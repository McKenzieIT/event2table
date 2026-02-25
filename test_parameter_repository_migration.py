#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ParameterRepository迁移到Entity模式

验证:
1. 所有查询方法返回ParameterEntity而非字典
2. ParameterEntity的验证功能正常工作
3. CRUD操作正常工作
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_parameter_repository_entity():
    """测试ParameterRepository返回Entity"""
    from backend.models.repositories.parameters import ParameterRepository
    from backend.models.entities import ParameterEntity

    print("=" * 60)
    print("测试 ParameterRepository Entity 迁移")
    print("=" * 60)

    repo = ParameterRepository()

    # 测试1: find_by_id 返回 ParameterEntity
    print("\n[测试1] find_by_id 返回 ParameterEntity")
    param = repo.find_by_id(1)
    if param:
        print(f"✅ find_by_id(1) 返回: {type(param).__name__}")
        print(f"   - 参数ID: {param.id}")
        print(f"   - 参数名: {param.name}")
        print(f"   - 事件ID: {param.event_id}")
        print(f"   - 游戏GID: {param.game_gid}")
        print(f"   - 参数类型: {param.param_type}")
        assert isinstance(param, ParameterEntity), "应该返回ParameterEntity"
        assert hasattr(param, 'name'), "应该有name属性"
    else:
        print("⚠️  数据库中没有ID=1的参数，跳过此测试")

    # 测试2: get_active_by_event 返回 ParameterEntity列表
    print("\n[测试2] get_active_by_event 返回 ParameterEntity列表")
    params = repo.get_active_by_event(1)
    print(f"✅ get_active_by_event(1) 返回 {len(params)} 个参数")
    if params:
        first_param = params[0]
        print(f"   - 第一个参数类型: {type(first_param).__name__}")
        print(f"   - 第一个参数名: {first_param.name}")
        assert isinstance(first_param, ParameterEntity), "应该返回ParameterEntity"
        assert hasattr(first_param, 'name'), "应该有name属性"

    # 测试3: get_all_by_event 返回 ParameterEntity列表
    print("\n[测试3] get_all_by_event 返回 ParameterEntity列表")
    all_params = repo.get_all_by_event(1, include_inactive=True)
    print(f"✅ get_all_by_event(1, include_inactive=True) 返回 {len(all_params)} 个参数")
    if all_params:
        assert all(isinstance(p, ParameterEntity) for p in all_params), "所有参数应该是ParameterEntity"

    # 测试4: ParameterEntity验证功能
    print("\n[测试4] ParameterEntity验证功能")
    try:
        # 测试XSS防护
        test_param = ParameterEntity(
            event_id=1,
            game_gid=10000147,
            name="<script>alert('xss')</script>",
            param_type="base"
        )
        print(f"✅ XSS防护: {test_param.name}")
        assert "&lt;script&gt;" in test_param.name, "应该转义HTML字符"

        # 测试JSON路径验证
        test_param2 = ParameterEntity(
            event_id=1,
            game_gid=10000147,
            name="zone_id",
            param_type="param",
            json_path="$.zoneId"
        )
        print(f"✅ JSON路径验证: {test_param2.json_path}")

        # 测试无效JSON路径
        try:
            test_param3 = ParameterEntity(
                event_id=1,
                game_gid=10000147,
                name="invalid",
                param_type="param",
                json_path="invalid_path"
            )
            print("❌ 应该拒绝无效的JSON路径")
        except ValueError as e:
            print(f"✅ JSON路径验证正常工作: {e}")

    except Exception as e:
        print(f"❌ Entity验证失败: {e}")
        raise

    # 测试5: find_by_name_and_event 返回 ParameterEntity
    print("\n[测试5] find_by_name_and_event 返回 ParameterEntity")
    if params:
        param_by_name = repo.find_by_name_and_event(params[0].name, 1)
        if param_by_name:
            print(f"✅ find_by_name_and_event 返回: {type(param_by_name).__name__}")
            assert isinstance(param_by_name, ParameterEntity), "应该返回ParameterEntity"

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


def test_parameter_crud():
    """测试Parameter的CRUD操作"""
    from backend.models.repositories.parameters import ParameterRepository
    from backend.models.entities import ParameterEntity
    from backend.core.utils.converters import get_db_connection

    print("\n" + "=" * 60)
    print("测试 Parameter CRUD 操作")
    print("=" * 60)

    repo = ParameterRepository()

    # 测试创建参数
    print("\n[测试1] 创建参数")
    conn = get_db_connection()
    cursor = conn.cursor()

    # 先获取一个有效的事件ID
    cursor.execute("SELECT id FROM log_events LIMIT 1")
    result = cursor.fetchone()
    if not result:
        print("⚠️  数据库中没有事件，跳过CRUD测试")
        conn.close()
        return

    test_event_id = result[0]
    test_game_gid = 10000147

    # 创建测试参数（注意：不插入game_gid，它从关联的log_events获取）
    cursor.execute(
        """
        INSERT INTO event_params (event_id, param_name, param_name_cn, json_path, template_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (test_event_id, "test_param_entity", "测试参数", "$.testField", 1)
    )
    test_param_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"✅ 创建测试参数 ID: {test_param_id}")

    # 测试读取参数
    print("\n[测试2] 读取参数")
    param = repo.find_by_id(test_param_id)
    assert param is not None, "应该能找到刚创建的参数"
    assert isinstance(param, ParameterEntity), "应该返回ParameterEntity"
    assert param.name == "test_param_entity", "参数名应该匹配"
    print(f"✅ 读取参数成功: {param.name}")

    # 测试更新参数
    print("\n[测试3] 更新参数")
    # 注意：更新时使用数据库字段名 param_name
    updated_param = repo.update(test_param_id, {"param_name": "updated_test_param"})
    assert updated_param is not None, "更新后应该能返回参数"
    assert isinstance(updated_param, ParameterEntity), "应该返回ParameterEntity"
    assert updated_param.name == "updated_test_param", "参数名应该已更新"
    print(f"✅ 更新参数成功: {updated_param.name}")

    # 测试删除参数
    print("\n[测试4] 删除参数")
    deleted = repo.delete(test_param_id)
    assert deleted is True, "删除应该成功"

    # 验证删除
    param_after_delete = repo.find_by_id(test_param_id)
    assert param_after_delete is None, "删除后不应该能找到参数"
    print(f"✅ 删除参数成功")

    print("\n" + "=" * 60)
    print("✅ 所有CRUD测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    # 激活虚拟环境
    import subprocess
    venv_path = os.path.join(os.path.dirname(__file__), "backend", "venv")
    if os.path.exists(venv_path):
        print("使用虚拟环境: backend/venv")
    else:
        print("⚠️  虚拟环境不存在，请先创建虚拟环境")
        sys.exit(1)

    try:
        # 运行测试
        test_parameter_repository_entity()
        test_parameter_crud()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
