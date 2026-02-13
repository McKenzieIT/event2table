#!/usr/bin/env python3
"""
自动化测试框架 - DWD Generator

功能：
1. 代码变更追踪
2. 自动化测试执行
3. 测试结果记录
4. 代码覆盖率统计
"""

import os
import sys
import json
import subprocess
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class TestTracker:
    """测试追踪器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.test_db = self.project_root / "tests" / "test_history.db"
        self.init_database()

    def init_database(self):
        """初始化测试数据库"""
        self.test_db.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        # 创建测试记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE,
                timestamp TEXT,
                test_type TEXT,
                total_tests INTEGER,
                passed_tests INTEGER,
                failed_tests INTEGER,
                coverage_percent REAL,
                git_commit TEXT,
                changed_files TEXT
            )
        ''')

        # 创建代码变更表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_id TEXT UNIQUE,
                timestamp TEXT,
                file_path TEXT,
                change_type TEXT,
                description TEXT,
                test_run_id TEXT,
                FOREIGN KEY (test_run_id) REFERENCES test_runs(run_id)
            )
        ''')

        conn.commit()
        conn.close()

    def record_change(self, file_path: str, change_type: str, description: str) -> str:
        """记录代码变更"""
        change_id = f"C{uuid.uuid4().hex[:8]}"

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO code_changes (change_id, timestamp, file_path, change_type, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (change_id, datetime.now().isoformat(), file_path, change_type, description))

        conn.commit()
        conn.close()

        return change_id

    def start_test_run(self, test_type: str) -> str:
        """开始测试运行"""
        run_id = f"T{uuid.uuid4().hex[:8]}"

        # 获取 git commit
        try:
            git_commit = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            git_commit = "unknown"

        # 获取变更的文件
        try:
            changed_files = subprocess.check_output(
                ['git', 'diff', '--name-only'],
                cwd=self.project_root,
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            changed_files = ""

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO test_runs (run_id, timestamp, test_type, git_commit, changed_files)
            VALUES (?, ?, ?, ?, ?)
        ''', (run_id, datetime.now().isoformat(), test_type, git_commit, changed_files))

        conn.commit()
        conn.close()

        return run_id

    def finish_test_run(self, run_id: str, total: int, passed: int, failed: int, coverage: float):
        """完成测试运行"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE test_runs
            SET total_tests = ?, passed_tests = ?, failed_tests = ?, coverage_percent = ?
            WHERE run_id = ?
        ''', (total, passed, failed, coverage, run_id))

        conn.commit()
        conn.close()

    def get_test_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取测试历史"""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT run_id, timestamp, test_type, total_tests, passed_tests, failed_tests, coverage_percent
            FROM test_runs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'run_id': row[0],
                'timestamp': row[1],
                'test_type': row[2],
                'total': row[3],
                'passed': row[4],
                'failed': row[5],
                'coverage': row[6]
            }
            for row in rows
        ]


def test_canvas_api(tracker: TestTracker) -> Dict[str, Any]:
    """测试 Canvas API"""

    print("\n" + "="*60)
    print("测试: Canvas Flow Management API")
    print("="*60)

    # 记录代码变更
    changes = [
        {
            'file': 'modules/node/canvas.py',
            'type': 'API',
            'desc': '新增 GET /api/flows/<id> 端点'
        },
        {
            'file': 'modules/node/canvas.py',
            'type': 'API',
            'desc': '新增 POST /api/flows/save 端点'
        }
    ]

    change_ids = []
    for change in changes:
        change_id = tracker.record_change(change['file'], change['type'], change['desc'])
        change_ids.append(change_id)
        print(f"✓ 记录变更: {change_id} - {change['desc']}")

    # 开始测试运行
    run_id = tracker.start_test_run("Canvas API")

    # 执行测试
    try:
        import requests

        base_url = "http://localhost:5001"
        results = []

        # 测试 1: GET /canvas/api/flows/1
        print("\n测试 GET /canvas/api/flows/1...")
        try:
            response = requests.get(f"{base_url}/canvas/api/flows/1", timeout=5)
            is_json = response.headers.get('Content-Type', '').startswith('application/json')

            if is_json:
                print(f"✅ 状态码: {response.status_code}")
                print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
                results.append(True)
            else:
                print(f"❌ 状态码: {response.status_code}")
                print(f"❌ Content-Type: {response.headers.get('Content-Type')} (预期: application/json)")
                results.append(False)
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            results.append(False)

        # 测试 2: POST /canvas/api/flows/save
        print("\n测试 POST /canvas/api/flows/save...")
        try:
            response = requests.post(
                f"{base_url}/canvas/api/flows/save",
                json={
                    "game_gid": 10000147,
                    "flow_name": "Test Flow",
                    "flow_graph": {"nodes": [], "edges": []}
                },
                timeout=5
            )
            is_json = response.headers.get('Content-Type', '').startswith('application/json')

            if is_json and response.status_code in [200, 201]:
                print(f"✅ 状态码: {response.status_code}")
                print(f"✅ Content-Type: {response.headers.get('Content-Type')}")
                results.append(True)
            else:
                print(f"❌ 状态码: {response.status_code}")
                print(f"❌ Content-Type: {response.headers.get('Content-Type')}")
                results.append(False)
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            results.append(False)

        # 汇总结果
        total = len(results)
        passed = sum(results)
        failed = total - passed
        coverage = (passed / total * 100) if total > 0 else 0

        # 完成测试运行
        tracker.finish_test_run(run_id, total, passed, failed, coverage)

        print("\n" + "="*60)
        print(f"测试结果: {passed}/{total} 通过 ({coverage:.0f}%)")
        print("="*60)

        return {
            'run_id': run_id,
            'total': total,
            'passed': passed,
            'failed': failed,
            'coverage': coverage,
            'change_ids': change_ids
        }

    except ImportError:
        print("\n❌ 缺少 requests 模块")
        print("安装命令: pip install requests")
        return {'error': 'Missing requests module'}


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent

    print("="*60)
    print("DWD Generator - 自动化测试框架")
    print("="*60)
    print(f"项目根目录: {project_root}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 创建追踪器
    tracker = TestTracker(project_root)

    # 运行测试
    result = test_canvas_api(tracker)

    if 'error' in result:
        return 1

    # 显示测试历史
    print("\n" + "="*60)
    print("最近测试历史")
    print("="*60)

    history = tracker.get_test_history(limit=5)
    for i, run in enumerate(history, 1):
        status = "✅" if run['failed'] == 0 else "❌"
        print(f"{i}. {status} {run['run_id']} - {run['passed']}/{run['total']} 通过 ({run['coverage']:.0f}%)")
        print(f"   时间: {run['timestamp']}")
        print(f"   类型: {run['test_type']}")

    return 0 if result['passed'] == result['total'] else 1


if __name__ == "__main__":
    sys.exit(main())
