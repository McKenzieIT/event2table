"""
模板变量替换引擎

负责HQL模板中的变量替换和验证
支持 ${variable} 格式的变量占位符
"""

import re
from typing import Dict, List, Set


class TemplateEngine:
    """
    HQL模板变量引擎

    功能:
    - 替换模板中的变量占位符
    - 提取模板中的变量名
    - 验证变量是否在可用列表中
    - 支持内置变量（如 ${ds} 等）
    """

    # 内置变量定义
    # 这些变量由计算引擎自动处理，不需要用户提供值
    BUILTIN_VARIABLES: Set[str] = {
        "ds",  # 分区日期，由计算引擎自动获取
        "bizdate",  # 业务日期（已废弃，保留兼容性）
        "table_name",  # 表名
        "event_name",  # 事件名
    }

    # 变量匹配正则表达式
    VARIABLE_PATTERN = re.compile(r"\$\{(\w+)\}")

    def __init__(self):
        """初始化模板引擎"""

    def render(self, template: str, variables: Dict[str, str] | None = None) -> str:
        """
        替换模板中的变量

        Args:
            template: HQL模板字符串
            variables: 变量字典 {变量名: 值}

        Returns:
            str: 替换后的HQL字符串

        Examples:
            >>> engine = TemplateEngine()
            >>> template = "SELECT * FROM table WHERE ds = '${ds}'"
            >>> result = engine.render(template, {"ds": "20260217"})
            >>> print(result)
            SELECT * FROM table WHERE ds = '20260217'

            >>> # 内置变量不会被替换（保留原样）
            >>> template = "SELECT * FROM ${table_name} WHERE ds = '${ds}'"
            >>> result = engine.render(template, {"table_name": "ods_table"})
            >>> print(result)
            SELECT * FROM ods_table WHERE ds = '${ds}'
        """
        if variables is None:
            variables = {}

        result = template

        # 查找所有变量占位符
        matches = self.VARIABLE_PATTERN.findall(template)

        for var_name in matches:
            # 如果是内置变量，保留原样不替换
            if var_name in self.BUILTIN_VARIABLES:
                continue

            # 如果用户提供了值，则替换
            if var_name in variables:
                placeholder = f"${{{var_name}}}"
                value = variables[var_name]
                result = result.replace(placeholder, str(value))

        return result

    def extract_variables(self, template: str) -> List[str]:
        """
        提取模板中的所有变量名

        Args:
            template: HQL模板字符串

        Returns:
            List[str]: 变量名列表

        Examples:
            >>> engine = TemplateEngine()
            >>> template = "SELECT * FROM ${table_name} WHERE ds = '${ds}' AND zone_id = ${zone_id}"
            >>> vars = engine.extract_variables(template)
            >>> print(vars)
            ['table_name', 'ds', 'zone_id']
        """
        matches = self.VARIABLE_PATTERN.findall(template)
        return list(matches)

    def validate_variables(
        self, template: str, available: Set[str] | None = None
    ) -> Dict[str, List[str]]:
        """
        验证模板中的变量

        Args:
            template: HQL模板字符串
            available: 可用的变量名集合（不包括内置变量）

        Returns:
            Dict[str, List[str]]: 验证结果
                - "builtin": 内置变量列表
                - "missing": 缺失的变量列表
                - "valid": 有效的变量列表

        Examples:
            >>> engine = TemplateEngine()
            >>> template = "SELECT * FROM ${table_name} WHERE ds = '${ds}' AND zone_id = ${zone_id}"
            >>> available = {"table_name", "zone_id"}
            >>> result = engine.validate_variables(template, available)
            >>> print(result)
            {
                'builtin': ['ds'],
                'missing': [],
                'valid': ['table_name', 'zone_id']
            }
        """
        if available is None:
            available = set()

        variables = self.extract_variables(template)

        result = {
            "builtin": [],
            "missing": [],
            "valid": [],
        }

        for var_name in variables:
            if var_name in self.BUILTIN_VARIABLES:
                result["builtin"].append(var_name)
            elif var_name in available:
                result["valid"].append(var_name)
            else:
                result["missing"].append(var_name)

        return result

    def get_builtin_variables(self) -> Set[str]:
        """
        获取所有内置变量名

        Returns:
            Set[str]: 内置变量名集合
        """
        return self.BUILTIN_VARIABLES.copy()

    def is_builtin_variable(self, var_name: str) -> bool:
        """
        检查变量是否为内置变量

        Args:
            var_name: 变量名

        Returns:
            bool: 是否为内置变量
        """
        return var_name in self.BUILTIN_VARIABLES


# 便捷函数
def render_template(template: str, variables: Dict[str, str] | None = None) -> str:
    """
    渲染模板（便捷函数）

    Args:
        template: HQL模板字符串
        variables: 变量字典

    Returns:
        str: 替换后的HQL字符串
    """
    engine = TemplateEngine()
    return engine.render(template, variables)


def extract_template_variables(template: str) -> List[str]:
    """
    提取模板变量（便捷函数）

    Args:
        template: HQL模板字符串

    Returns:
        List[str]: 变量名列表
    """
    engine = TemplateEngine()
    return engine.extract_variables(template)


# 导出
__all__ = [
    "TemplateEngine",
    "render_template",
    "extract_template_variables",
]
