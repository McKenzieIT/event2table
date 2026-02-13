#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest配置和共享fixtures

此文件包含所有测试共享的fixtures和配置。
使用独立的测试数据库以避免污染生产数据。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Debug output
print(f"[CONFTEST] sys.path[0]: {sys.path[0]}")
print(f"[CONFTEST] project_root: {project_root}")
print(f"[CONFTEST] backend in sys.modules: {'backend' in sys.modules}")

# Try to import backend and see what's in it
try:
    import backend
    print(f"[CONFTEST] backend module: {backend}")
    print(f"[CONFTEST] backend.__path__: {backend.__path__ if hasattr(backend, '__path__') else 'N/A'}")
    print(f"[CONFTEST] dir(backend): {dir(backend)}")
    # Try importing core explicitly
    import backend.core
    print(f"[CONFTEST] backend.core imported successfully!")
except Exception as e:
    print(f"[CONFTEST] Error importing backend: {e}")
    import traceback
    traceback.print_exc()

import pytest
from flask import Flask
from backend.core.database import get_db_connection, init_db, migrate_db
from backend.core.utils import execute_write
from backend.core.config import DB_PATH, TEST_DB_PATH


@pytest.fixture(scope="session")
def test_database():
    """
    共享的测试数据库初始化fixture

    确保测试数据库只被初始化一次，由app和db fixtures共享使用。
    这是session-scoped fixture，确保整个测试session使用同一个数据库。
    """
    # 设置测试环境
    os.environ["FLASK_ENV"] = "testing"

    # 确保测试数据库目录存在
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 删除旧测试数据库（如果存在）
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    # 使用 init_db() 初始化测试数据库（创建所有表）
    init_db(TEST_DB_PATH)

    # 运行数据库迁移（添加 game_gid 等字段）
    migrate_db(TEST_DB_PATH)

    yield TEST_DB_PATH

    # 可选：测试结束后删除测试数据库
    # if TEST_DB_PATH.exists():
    #     TEST_DB_PATH.unlink()


@pytest.fixture(scope="session")
def app(test_database):
    """创建Flask应用实例用于测试 - 依赖test_database fixture"""
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_SECRET_KEY"] = "test-secret-key"

    from backend.api import api_bp
    try:
        from backend.api.routes.hql_preview_v2 import hql_preview_v2_bp
    except ImportError:
        hql_preview_v2_bp = None
    try:
        from backend.services.games import games_bp
    except ImportError:
        games_bp = None
    # Note: categories routes are part of api_bp, not a separate blueprint
    try:
        from backend.services.events import events_bp, event_nodes_bp
    except ImportError:
        events_bp, event_nodes_bp = None, None
    try:
        from backend.services.parameters import common_params_bp, parameter_aliases_bp
    except ImportError:
        common_params_bp, parameter_aliases_bp = None, None
    try:
        from backend.services.canvas import canvas_bp
    except ImportError:
        canvas_bp = None
    try:
        from backend.services.bulk_operations import bulk_bp
    except ImportError:
        bulk_bp = None
    try:
        from backend.services.cache_monitor import cache_monitor_bp
    except ImportError:
        cache_monitor_bp = None

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    # 注册所有blueprints
    # Note: games_bp is registered AFTER api_bp, but has conflicting routes
    # For testing, we only use api_bp routes which have better implementation
    app.register_blueprint(api_bp)
    if hql_preview_v2_bp:
        app.register_blueprint(hql_preview_v2_bp)  # V2 HQL Preview API
    # app.register_blueprint(games_bp)  # Disabled: conflicts with api_bp /api/games routes
    # Note: categories routes are included in api_bp, no separate blueprint needed
    if events_bp:
        app.register_blueprint(events_bp)
    if event_nodes_bp:
        app.register_blueprint(event_nodes_bp)
    if common_params_bp:
        app.register_blueprint(common_params_bp)
    if parameter_aliases_bp:
        app.register_blueprint(parameter_aliases_bp)
    if canvas_bp:
        app.register_blueprint(canvas_bp)
    if bulk_bp:
        app.register_blueprint(bulk_bp)
    if cache_monitor_bp:
        app.register_blueprint(cache_monitor_bp)

    yield app

    # 清理
    app.context = None


@pytest.fixture(scope="function")
def db(test_database):
    """
    提供测试数据库连接的fixture - 依赖test_database fixture

    注意：这个fixture提供的是数据库连接对象，不是数据库路径。
    test_database fixture负责初始化数据库。

    使用function scope确保每个测试获得独立的数据库连接，
    防止测试之间的状态污染和连接损坏传播。

    使用事务回滚模式：
    - 每个测试开始时开启新事务
    - 测试完成后回滚所有更改
    - 确保每个测试都在干净的数据库状态上运行
    """
    conn = get_db_connection(TEST_DB_PATH)  # 显式使用测试数据库路径

    # 开启事务，确保测试的更改可以被回滚
    conn.execute("BEGIN")

    yield conn

    # 回滚事务，撤销测试期间的所有更改
    conn.rollback()
    conn.close()


@pytest.fixture
def sample_game(db):
    """创建示例游戏数据 - 使用独特的GID"""
    import random
    import time

    # 使用大数字GID确保不与生产数据冲突 (90000000-99999999范围)
    unique_gid = 90000000 + int(str(int(time.time() * 1000))[-4:]) + random.randint(0, 999)

    cursor = db.execute(
        """
        INSERT INTO games (gid, name, ods_db)
        VALUES (?, ?, ?)
    """,
        (unique_gid, "Test Game", "test_ods"),
    )
    game_id = cursor.lastrowid
    db.commit()

    # 返回游戏数据
    game = db.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    return game


@pytest.fixture
def sample_event(db, sample_game):
    """创建示例事件数据"""
    cursor = db.execute(
        """
        INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (sample_game["id"], sample_game["gid"], "test_event", "测试事件", "ods_test", "dwd_test"),
    )
    event_id = cursor.lastrowid
    db.commit()

    event = db.execute("SELECT * FROM log_events WHERE id = ?", (event_id,)).fetchone()
    return event


@pytest.fixture
def hql_v2_test_data(db):
    """
    为HQL V2集成测试创建测试数据

    创建game_gid=10000147和event_id=55，满足test_hql_v2_integration.py的需求
    """
    # 确保测试游戏存在（使用固定的test gid以避免冲突）
    test_game_gid = 10000147
    game = db.execute('SELECT * FROM games WHERE gid = ?', (test_game_gid,)).fetchone()
    if not game:
        cursor = db.execute(
            """
            INSERT INTO games (gid, name, ods_db)
            VALUES (?, ?, ?)
        """,
            (test_game_gid, 'Test Game for HQL V2', 'ieu_ods'),
        )
        game_id = cursor.lastrowid
        db.commit()
        game = db.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()

    # 确保测试事件存在（使用固定的event_id=55）
    test_event_id = 55
    event = db.execute('SELECT * FROM log_events WHERE id = ?', (test_event_id,)).fetchone()
    if not event:
        game_db_id = game['id']
        cursor = db.execute(
            """
            INSERT INTO log_events (id, game_id, game_gid, event_name, event_name_cn, source_table, target_table)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (test_event_id, game_db_id, test_game_gid, 'test.role_online', '测试角色上线',
             'ieu_ods.ods_10000147_all_view', 'dwd.v_dwd_10000147_test_role_online_di'),
        )
        db.commit()
        event = db.execute("SELECT * FROM log_events WHERE id = ?", (test_event_id,)).fetchone()

    return {
        'game_gid': test_game_gid,
        'event_id': test_event_id,
        'game': game,
        'event': event
    }


class TestClient:
    """Flask测试客户端封装"""

    def __init__(self, app):
        self.app = app

    def get(self, url, **kwargs):
        return self.app.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self.app.post(url, **kwargs)

    def put(self, url, **kwargs):
        return self.app.put(url, **kwargs)

    def delete(self, url, **kwargs):
        return self.app.delete(url, **kwargs)


@pytest.fixture
def client(app):
    """提供Flask测试客户端"""
    return app.test_client()


# Pytest钩子
def pytest_configure(config):
    """Pytest配置钩子"""
    config.addinivalue_line("markers", "unit: 单元测试（测试单个函数/类）")
    config.addinivalue_line("markers", "integration: 集成测试（测试模块间交互）")
    config.addinivalue_line("markers", "slow: 慢速测试（运行时间>1秒）")
    config.addinivalue_line("markers", "database: 数据库相关测试")
    config.addinivalue_line("markers", "api: API端点测试")
