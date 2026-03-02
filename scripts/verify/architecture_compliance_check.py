#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
架构合规性检查脚本

检查项目分层架构的合规性：
1. API层不应直接调用Repository层（应通过Service层）
2. Service层不应直接访问数据库（应通过Repository层）
3. Repository层不应包含业务逻辑
4. Entity层不应包含业务逻辑

使用方法：
    python scripts/verify/architecture_compliance_check.py
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ArchitectureChecker:
    """架构合规性检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_root = project_root / "backend"
        self.violations = []
        self.warnings = []
        self.compliant_files = []

        # 定义层次结构
        self.layers = {
            "api": "API层",
            "service": "Service层",
            "repository": "Repository层",
            "entity": "Entity层"
        }

        # 定义禁止的导入关系
        self.forbidden_imports = {
            # API层不应直接导入Repository层
            "api_to_repository": {
                "from_dir": "api/routes",
                "forbidden_import": "models/repositories",
                "reason": "API层应通过Service层访问数据，不应直接导入Repository"
            },
            # Service层不应直接导入数据库操作
            "service_to_database": {
                "from_dir": "services",
                "forbidden_import": "core/database/converters",
                "reason": "Service层应通过Repository层访问数据，不应直接使用数据库操作"
            },
            # Repository层不应导入Service层
            "repository_to_service": {
                "from_dir": "models/repositories",
                "forbidden_import": "services",
                "reason": "Repository层不应依赖Service层，违反依赖倒置原则"
            },
            # Entity层不应导入Service层或Repository层
            "entity_to_service": {
                "from_dir": "models",
                "forbidden_import": "services",
                "reason": "Entity层应是纯数据模型，不应依赖业务逻辑层"
            }
        }

    def check_import_violations(self) -> Dict[str, List[Dict]]:
        """检查导入违规"""
        print("🔍 检查导入违规...")

        results = {key: [] for key in self.forbidden_imports.keys()}

        # 遍历所有Python文件
        for py_file in self.backend_root.rglob("*.py"):
            # 跳过__pycache__和虚拟环境
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                rel_path = py_file.relative_to(self.backend_root)

                # 检查每种违规类型
                for violation_type, config in self.forbidden_imports.items():
                    from_dir = config["from_dir"]
                    forbidden = config["forbidden_import"]

                    # 只检查指定目录下的文件
                    if str(rel_path).startswith(from_dir):
                        # 检查是否包含禁止的导入
                        if forbidden in content:
                            # 提取导入行
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if forbidden in line and ("import" in line or "from" in line):
                                    results[violation_type].append({
                                        "file": str(py_file.relative_to(self.project_root)),
                                        "line": i,
                                        "content": line.strip(),
                                        "reason": config["reason"]
                                    })
            except Exception as e:
                print(f"⚠️  读取文件失败 {py_file}: {e}")

        return results

    def check_database_access_in_services(self) -> List[Dict]:
        """检查Service层中的直接数据库访问"""
        print("🔍 检查Service层直接数据库访问...")

        violations = []

        # Service层文件
        service_files = (self.backend_root / "services").rglob("*.py")

        for py_file in service_files:
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                # 检查直接数据库操作的迹象
                db_patterns = [
                    r'fetch_one_as_dict\(',
                    r'fetch_all_as_dict\(',
                    r'execute_update\(',
                    r'execute_insert\(',
                    r'execute_query\(',
                    r'sqlite3\.connect\(',
                    r'cursor\.execute\('
                ]

                for i, line in enumerate(lines, 1):
                    for pattern in db_patterns:
                        if re.search(pattern, line):
                            # 排除注释
                            if not line.strip().startswith('#'):
                                violations.append({
                                    "file": str(py_file.relative_to(self.project_root)),
                                    "line": i,
                                    "content": line.strip(),
                                    "pattern": pattern
                                })
            except Exception as e:
                print(f"⚠️  读取文件失败 {py_file}: {e}")

        return violations

    def check_business_logic_in_repositories(self) -> List[Dict]:
        """检查Repository层中的业务逻辑"""
        print("🔍 检查Repository层业务逻辑...")

        violations = []

        # Repository层文件
        repo_files = (self.backend_root / "models" / "repositories").rglob("*.py")

        for py_file in repo_files:
            if "__pycache__" in str(py_file) or "__init__.py" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                # 检查业务逻辑的迹象（除了CRUD之外的复杂逻辑）
                business_logic_patterns = [
                    r'if.*and.*:',  # 复杂条件判断
                    r'for.*in.*:',  # 循环处理（可能是业务逻辑）
                    r'class.*\(.*\).*:',  # 除了Repository之外的类定义
                    r'def.*\(.*\).*->.*:',  # 复杂方法（需要人工审查）
                ]

                # 简化检查：查找非CRUD方法
                for i, line in enumerate(lines, 1):
                    # 跳过注释和简单的CRUD方法
                    if line.strip().startswith('#'):
                        continue

                    # 检查是否有除CRUD外的复杂方法
                    if re.search(r'def (?!get_by|find_by|create|update|delete|save|list_all)\w+', line):
                        # 可能是业务逻辑方法
                        violations.append({
                            "file": str(py_file.relative_to(self.project_root)),
                            "line": i,
                            "content": line.strip(),
                            "type": "potential_business_logic"
                        })
            except Exception as e:
                print(f"⚠️  读取文件失败 {py_file}: {e}")

        return violations

    def check_error_handling_consistency(self) -> Dict[str, List[Dict]]:
        """检查错误处理一致性"""
        print("🔍 检查错误处理一致性...")

        results = {
            "missing_try_except": [],
            "raw_exception_exposure": [],
            "inconsistent_error_response": []
        }

        # API层文件
        api_files = (self.backend_root / "api" / "routes").rglob("*.py")

        for py_file in api_files:
            if "__pycache__" in str(py_file) or "__init__.py" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                # 检查每个路由函数
                for i, line in enumerate(lines, 1):
                    # 查找路由定义
                    if re.search(r'@.*\.route\(', line):
                        # 检查下一个函数是否有try-except
                        func_found = False
                        try_except_found = False
                        func_indent = 0

                        for j in range(i, min(i + 50, len(lines))):
                            func_line = lines[j]

                            # 找到函数定义
                            if re.search(r'def \w+\(', func_line):
                                func_found = True
                                func_indent = len(func_line) - len(func_line.lstrip())

                            # 如果找到函数，检查是否有try-except
                            if func_found:
                                if 'try:' in func_line:
                                    try_except_found = True
                                    break

                                # 如果遇到同级别或更低级别的其他定义，说明函数结束了
                                if j > i + 1:
                                    line_indent = len(func_line) - len(func_line.lstrip())
                                    if line_indent <= func_indent and func_line.strip():
                                        break

                        if func_found and not try_except_found:
                            results["missing_try_except"].append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": i,
                                "content": line.strip()
                            })

                    # 检查是否暴露原始异常信息
                    if re.search(r'(raise.*Exception|str\(e\)|repr\(e\))', line):
                        if not line.strip().startswith('#'):
                            results["raw_exception_exposure"].append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": i,
                                "content": line.strip()
                            })

            except Exception as e:
                print(f"⚠️  读取文件失败 {py_file}: {e}")

        return results

    def check_validation_consistency(self) -> Dict[str, List[Dict]]:
        """检查数据验证一致性"""
        print("🔍 检查数据验证一致性...")

        results = {
            "missing_entity_validation": [],
            "inconsistent_validation": []
        }

        # API层文件
        api_files = (self.backend_root / "api" / "routes").rglob("*.py")

        for py_file in api_files:
            if "__pycache__" in str(py_file) or "__init__.py" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                # 检查POST/PUT请求是否使用Entity验证
                for i, line in enumerate(lines, 1):
                    if re.search(r'@.*\.route.*methods.*=.*\[.*["\']POST|["\']PUT', line):
                        # 检查函数体内是否使用Entity
                        func_found = False
                        entity_validation = False
                        func_end = min(i + 50, len(lines))

                        for j in range(i, func_end):
                            func_line = lines[j]

                            if re.search(r'def \w+\(', func_line):
                                func_found = True

                            if func_found:
                                # 检查是否使用Entity
                                if re.search(r'(GameEntity|EventEntity|ParameterEntity)\(', func_line):
                                    entity_validation = True
                                    break

                                # 如果函数结束
                                if j > i + 5 and re.search(r'^\S', func_line) and not func_line.strip().startswith('#'):
                                    break

                        if func_found and not entity_validation:
                            results["missing_entity_validation"].append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": i,
                                "content": line.strip()
                            })

            except Exception as e:
                print(f"⚠️  读取文件失败 {py_file}: {e}")

        return results

    def generate_report(self) -> str:
        """生成架构合规性报告"""

        print("\n" + "="*80)
        print("🏗️  架构合规性检查报告")
        print("="*80 + "\n")

        report_lines = []

        # 1. 导入违规检查
        import_violations = self.check_import_violations()

        total_import_violations = sum(len(v) for v in import_violations.values())

        if total_import_violations > 0:
            report_lines.append("## ❌ 导入违规检查\n")

            for violation_type, violations in import_violations.items():
                if violations:
                    report_lines.append(f"\n### {violation_type.upper()}: {len(violations)}个违规\n")

                    for v in violations[:10]:  # 只显示前10个
                        report_lines.append(f"**文件**: {v['file']}")
                        report_lines.append(f"**行号**: {v['line']}")
                        report_lines.append(f"**内容**: `{v['content']}`")
                        report_lines.append(f"**原因**: {v['reason']}")
                        report_lines.append("")

                    if len(violations) > 10:
                        report_lines.append(f"\n*... 还有 {len(violations) - 10} 个违规*\n")
        else:
            report_lines.append("## ✅ 导入违规检查")
            report_lines.append("未发现导入违规\n")

        # 2. 数据库访问检查
        db_violations = self.check_database_access_in_services()

        if db_violations:
            report_lines.append("## ❌ Service层直接数据库访问\n")
            report_lines.append(f"发现 {len(db_violations)} 处直接数据库访问\n")

            for v in db_violations[:10]:
                report_lines.append(f"**文件**: {v['file']}")
                report_lines.append(f"**行号**: {v['line']}")
                report_lines.append(f"**内容**: `{v['content']}`")
                report_lines.append(f"**模式**: {v['pattern']}")
                report_lines.append("")

            if len(db_violations) > 10:
                report_lines.append(f"\n*... 还有 {len(db_violations) - 10} 个违规*\n")
        else:
            report_lines.append("## ✅ Service层数据库访问检查")
            report_lines.append("Service层正确使用Repository访问数据\n")

        # 3. 业务逻辑检查
        logic_violations = self.check_business_logic_in_repositories()

        if logic_violations:
            report_lines.append("## ⚠️  Repository层业务逻辑检查\n")
            report_lines.append(f"发现 {len(logic_violations)} 处可能的业务逻辑（需人工审查）\n")

            for v in logic_violations[:10]:
                report_lines.append(f"**文件**: {v['file']}")
                report_lines.append(f"**行号**: {v['line']}")
                report_lines.append(f"**内容**: `{v['content']}`")
                report_lines.append("")
        else:
            report_lines.append("## ✅ Repository层业务逻辑检查")
            report_lines.append("Repository层职责清晰，未发现业务逻辑\n")

        # 4. 错误处理检查
        error_results = self.check_error_handling_consistency()

        report_lines.append("## 错误处理一致性检查\n")

        if error_results["missing_try_except"]:
            report_lines.append(f"### ❌ 缺少try-except: {len(error_results['missing_try_except'])}处\n")
            for v in error_results["missing_try_except"][:5]:
                report_lines.append(f"- {v['file']}:{v['line']}")
            report_lines.append("")

        if error_results["raw_exception_exposure"]:
            report_lines.append(f"### ❌ 原始异常暴露: {len(error_results['raw_exception_exposure'])}处\n")
            for v in error_results["raw_exception_exposure"][:5]:
                report_lines.append(f"- {v['file']}:{v['line']}")
            report_lines.append("")

        if not error_results["missing_try_except"] and not error_results["raw_exception_exposure"]:
            report_lines.append("### ✅ 错误处理合规\n")

        # 5. 数据验证检查
        validation_results = self.check_validation_consistency()

        report_lines.append("## 数据验证一致性检查\n")

        if validation_results["missing_entity_validation"]:
            report_lines.append(f"### ❌ 缺少Entity验证: {len(validation_results['missing_entity_validation'])}处\n")
            for v in validation_results["missing_entity_validation"][:5]:
                report_lines.append(f"- {v['file']}:{v['line']}")
            report_lines.append("")
        else:
            report_lines.append("### ✅ 数据验证合规\n")

        # 6. 合规性统计
        report_lines.append("\n" + "="*80)
        report_lines.append("📊 合规性统计")
        report_lines.append("="*80 + "\n")

        total_files = len(list((self.backend_root / "api" / "routes").rglob("*.py"))) + \
                      len(list((self.backend_root / "services").rglob("*.py"))) + \
                      len(list((self.backend_root / "models" / "repositories").rglob("*.py")))

        violation_count = total_import_violations + len(db_violations) + \
                         len(error_results["missing_try_except"]) + \
                         len(error_results["raw_exception_exposure"]) + \
                         len(validation_results["missing_entity_validation"])

        compliance_rate = max(0, 100 - (violation_count / max(1, total_files) * 10))

        report_lines.append(f"- 总检查文件数: {total_files}")
        report_lines.append(f"- 发现违规数量: {violation_count}")
        report_lines.append(f"- **架构合规率: {compliance_rate:.1f}%**")

        # 7. 修复建议
        if violation_count > 0:
            report_lines.append("\n" + "="*80)
            report_lines.append("🔧 修复建议")
            report_lines.append("="*80 + "\n")

            if total_import_violations > 0:
                report_lines.append("### 导入违规修复")
                report_lines.append("1. API层应通过Service层访问数据")
                report_lines.append("2. Service层应通过Repository层访问数据库")
                report_lines.append("3. 移除跨层直接导入\n")

            if db_violations:
                report_lines.append("### 数据库访问修复")
                report_lines.append("1. 将直接数据库操作移到Repository层")
                report_lines.append("2. Service层只调用Repository方法")
                report_lines.append("3. 使用依赖注入模式\n")

            if error_results["missing_try_except"]:
                report_lines.append("### 错误处理修复")
                report_lines.append("1. 所有路由函数添加try-except")
                report_lines.append("2. 使用json_error_response统一返回错误")
                report_lines.append("3. 避免暴露原始异常信息\n")

            if validation_results["missing_entity_validation"]:
                report_lines.append("### 数据验证修复")
                report_lines.append("1. POST/PUT请求使用Pydantic Entity验证")
                report_lines.append("2. 在API层入口进行参数验证")
                report_lines.append("3. 使用Entity.field_validator进行业务规则验证\n")

        return "\n".join(report_lines)


def main():
    """主函数"""
    print("🏗️  架构合规性检查工具")
    print("="*80)

    project_root = Path("/Users/mckenzie/Documents/event2table")
    checker = ArchitectureChecker(project_root)

    # 生成报告
    report = checker.generate_report()

    # 保存报告
    output_file = project_root / "docs/reports/2026-03-02/architecture-compliance-report.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ 报告已生成: {output_file}")
    print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
