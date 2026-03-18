#!/usr/bin/env python3
"""
Generate Comprehensive Performance Baseline Report
整合所有性能测试结果，生成综合基线报告
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"


class BaselineReportGenerator:
    """基线报告生成器"""

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)

        self.report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "branch": "opt/monitoring"
            },
            "lighthouse": {},
            "api_performance": {},
            "database_performance": {},
            "summary": {}
        }

    def run_lighthouse_baseline(self):
        """运行Lighthouse基线测试"""
        print("\n" + "="*60)
        print("Running Lighthouse Baseline Tests...")
        print("="*60)

        try:
            # 检查前端是否已构建
            dist_dir = PROJECT_ROOT / "frontend" / "dist"
            if not dist_dir.exists():
                print("Building frontend...")
                result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=PROJECT_ROOT / "frontend",
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"Build failed: {result.stderr}")
                    return False

            # 运行Lighthouse CI（注意：需要前端服务器运行）
            print("\nNote: Lighthouse CI requires the frontend server to be running.")
            print("Please run 'npm run dev' in a separate terminal first.")
            print("Then run: cd frontend && npm run lighthouse:baseline")

            self.report["lighthouse"] = {
                "status": "manual",
                "instructions": "Run 'npm run lighthouse:baseline' manually with server running",
                "config_file": "lighthouserc.json",
                "budget_file": "lighthouse-budget.json"
            }

            return True

        except Exception as e:
            print(f"Error running Lighthouse: {e}")
            self.report["lighthouse"] = {"error": str(e)}
            return False

    def run_api_performance_tests(self):
        """运行API性能测试"""
        print("\n" + "="*60)
        print("Running API Performance Tests...")
        print("="*60)

        try:
            # 检查后端服务器是否运行
            import requests
            response = requests.get("http://127.0.0.1:5001/api/games", timeout=2)
            print("Backend server is running")
        except Exception as e:
            print(f"Warning: Backend server may not be running: {e}")
            print("Please ensure the backend is running: python web_app.py")

        try:
            script_path = PROJECT_ROOT / "scripts" / "benchmarks" / "test_api_performance.py"
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )

            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)

            # 读取生成的结果文件
            api_baseline_file = self.output_dir / f"api-baseline-{datetime.now().strftime('%Y-%m-%d')}.json"
            if api_baseline_file.exists():
                with open(api_baseline_file, 'r') as f:
                    self.report["api_performance"] = json.load(f)
                return True
            else:
                print(f"Warning: API baseline file not found: {api_baseline_file}")
                return False

        except Exception as e:
            print(f"Error running API performance tests: {e}")
            self.report["api_performance"] = {"error": str(e)}
            return False

    def run_database_performance_tests(self):
        """运行数据库性能测试"""
        print("\n" + "="*60)
        print("Running Database Performance Tests...")
        print("="*60)

        try:
            script_path = PROJECT_ROOT / "scripts" / "benchmarks" / "test_db_queries.py"
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )

            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)

            # 读取生成的结果文件
            db_baseline_file = self.output_dir / f"db-baseline-{datetime.now().strftime('%Y-%m-%d')}.json"
            if db_baseline_file.exists():
                with open(db_baseline_file, 'r') as f:
                    self.report["database_performance"] = json.load(f)
                return True
            else:
                print(f"Warning: Database baseline file not found: {db_baseline_file}")
                return False

        except Exception as e:
            print(f"Error running database performance tests: {e}")
            self.report["database_performance"] = {"error": str(e)}
            return False

    def generate_summary(self):
        """生成综合摘要"""
        print("\n" + "="*60)
        print("Generating Summary...")
        print("="*60)

        summary = {
            "tests_completed": [],
            "tests_failed": [],
            "recommendations": []
        }

        # 检查Lighthouse
        if self.report.get("lighthouse", {}).get("status") == "manual":
            summary["tests_completed"].append("Lighthouse CI configured")
            summary["recommendations"].append(
                "Run Lighthouse tests manually with frontend server running"
            )
        elif "error" in self.report.get("lighthouse", {}):
            summary["tests_failed"].append("Lighthouse CI")

        # 检查API性能
        if "summary" in self.report.get("api_performance", {}):
            summary["tests_completed"].append("API Performance")
            api_summary = self.report["api_performance"]["summary"]
            if api_summary.get("success_rate", 0) < 100:
                summary["recommendations"].append(
                    f"Some API requests failed (success rate: {api_summary['success_rate']}%)"
                )
        elif "error" in self.report.get("api_performance", {}):
            summary["tests_failed"].append("API Performance")

        # 检查数据库性能
        if "summary" in self.report.get("database_performance", {}):
            summary["tests_completed"].append("Database Performance")
            db_summary = self.report["database_performance"]["summary"]
            slowest = db_summary.get("slowest_queries", [])
            if slowest and slowest[0].get("mean_duration_ms", 0) > 100:
                summary["recommendations"].append(
                    f"Slowest query ({slowest[0]['name']}) took {slowest[0]['mean_duration_ms']}ms"
                )
        elif "error" in self.report.get("database_performance", {}):
            summary["tests_failed"].append("Database Performance")

        self.report["summary"] = summary

    def export_report(self, filename: str = None):
        """导出报告"""
        if filename is None:
            filename = f"baseline-{datetime.now().strftime('%Y-%m-%d')}.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(self.report, f, indent=2)

        print(f"\n{'='*60}")
        print(f"Comprehensive baseline report saved to: {output_path}")
        print(f"{'='*60}")

        return output_path

    def print_summary(self):
        """打印摘要"""
        summary = self.report.get("summary", {})

        print(f"\n{'='*60}")
        print("BASELINE REPORT SUMMARY")
        print(f"{'='*60}")
        print(f"Generated: {self.report['metadata']['generated_at']}")
        print(f"Branch: {self.report['metadata']['branch']}")
        print(f"\nTests Completed: {len(summary.get('tests_completed', []))}")
        for test in summary.get('tests_completed', []):
            print(f"  ✓ {test}")

        if summary.get('tests_failed'):
            print(f"\nTests Failed: {len(summary.get('tests_failed', []))}")
            for test in summary.get('tests_failed', []):
                print(f"  ✗ {test}")

        if summary.get('recommendations'):
            print(f"\nRecommendations: {len(summary.get('recommendations', []))}")
            for rec in summary.get('recommendations', []):
                print(f"  • {rec}")

        print(f"{'='*60}\n")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("PERFORMANCE BASELINE REPORT GENERATOR")
    print("="*60)

    generator = BaselineReportGenerator()

    # 1. Lighthouse基线测试（需要手动运行）
    generator.run_lighthouse_baseline()

    # 2. API性能测试
    generator.run_api_performance_tests()

    # 3. 数据库性能测试
    generator.run_database_performance_tests()

    # 4. 生成摘要
    generator.generate_summary()

    # 5. 打印摘要
    generator.print_summary()

    # 6. 导出报告
    generator.export_report()

    print("Baseline report generation completed!")


if __name__ == "__main__":
    main()
