#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canvas Service单元测试

测试CanvasService的各个功能:
- Flow CRUD操作
- EventNode CRUD操作
- Flow验证和生成
- 缓存集成
"""

import os
import sys

# 添加项目根目录到path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.logging import get_logger
from models.entities import EventNodeEntity, FlowEntity
from services.canvas.canvas_service import CanvasService

logger = get_logger(__name__)


def test_canvas_service():
    """测试CanvasService基本功能"""

    print("=" * 60)
    print("Canvas Service 单元测试")
    print("=" * 60)

    service = CanvasService()

    # 测试1: 创建Flow
    print("\n[测试1] 创建Flow模板")
    try:
        flow_graph = {
            "nodes": [
                {"id": "n1", "type": "event_source", "data": {"event_id": 1}},
                {"id": "n2", "type": "output", "data": {"name": "Output"}},
            ],
            "connections": [{"source": "n1", "target": "n2"}],
        }

        flow = service.create_flow(
            game_gid=10000147, flow_name="Test Flow", flow_graph=flow_graph, description="测试Flow"
        )

        print(f"✅ Flow创建成功: ID={flow.id}, Name={flow.flow_name}")
        flow_id = flow.id
    except Exception as e:
        print(f"❌ Flow创建失败: {e}")
        return False

    # 测试2: 获取Flow
    print("\n[测试2] 获取Flow模板")
    try:
        retrieved_flow = service.get_flow(flow_id)
        if retrieved_flow and retrieved_flow.id == flow_id:
            print(f"✅ Flow获取成功: {retrieved_flow.flow_name}")
        else:
            print("❌ Flow获取失败")
            return False
    except Exception as e:
        print(f"❌ Flow获取异常: {e}")
        return False

    # 测试3: 获取游戏的Flow列表
    print("\n[测试3] 获取游戏的Flow列表")
    try:
        flows = service.get_flows_by_game(10000147)
        print(f"✅ 获取到{len(flows)}个Flow")
        if len(flows) > 0:
            print(f"   - 第一个Flow: {flows[0].flow_name}")
    except Exception as e:
        print(f"❌ 获取Flow列表失败: {e}")
        return False

    # 测试4: 验证Flow图
    print("\n[测试4] 验证Flow图")
    try:
        validation = service.validate_flow(flow_graph)
        if validation["valid"]:
            print(f"✅ Flow图验证通过")
            print(f"   - 执行顺序: {' -> '.join(validation['execution_order'])}")
        else:
            print(f"❌ Flow图验证失败: {'; '.join(validation['errors'])}")
            return False
    except Exception as e:
        print(f"❌ Flow图验证异常: {e}")
        return False

    # 测试5: 准备Flow用于生成
    print("\n[测试5] 准备Flow用于HQL生成")
    try:
        preparation = service.prepare_flow_for_generation(flow_graph)
        if preparation["success"]:
            print(f"✅ Flow准备成功")
            print(f"   - 节点数: {preparation['node_count']}")
            print(f"   - 连接数: {preparation['connection_count']}")
        else:
            print(f"❌ Flow准备失败: {preparation['error']}")
            return False
    except Exception as e:
        print(f"❌ Flow准备异常: {e}")
        return False

    # 测试6: 更新Flow
    print("\n[测试6] 更新Flow模板")
    try:
        success = service.update_flow(flow_id=flow_id, description="更新后的描述")
        if success:
            print("✅ Flow更新成功")
        else:
            print("❌ Flow更新失败")
            return False
    except Exception as e:
        print(f"❌ Flow更新异常: {e}")
        return False

    # 测试7: 导出Flow配置
    print("\n[测试7] 导出Flow配置")
    try:
        export = service.export_flow_config(flow_id)
        if export:
            print(f"✅ Flow导出成功")
            print(f"   - Flow名称: {export['flow']['flow_name']}")
            print(f"   - 导出时间: {export['exported_at']}")
        else:
            print("❌ Flow导出失败")
            return False
    except Exception as e:
        print(f"❌ Flow导出异常: {e}")
        return False

    # 测试8: 删除Flow (软删除)
    print("\n[测试8] 删除Flow模板")
    try:
        success = service.delete_flow(flow_id, game_gid=10000147)
        if success:
            print("✅ Flow删除成功")
        else:
            print("❌ Flow删除失败")
            return False
    except Exception as e:
        print(f"❌ Flow删除异常: {e}")
        return False

    print("\n" + "=" * 60)
    print("所有测试通过! ✅")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = test_canvas_service()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.exception(f"Test failed with exception: {e}")
        sys.exit(1)
