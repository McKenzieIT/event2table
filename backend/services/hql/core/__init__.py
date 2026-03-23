"""核心模块"""

from .template_engine import TemplateEngine, render_template, extract_template_variables

__all__ = [
    "TemplateEngine",
    "render_template",
    "extract_template_variables",
]
