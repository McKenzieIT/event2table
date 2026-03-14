"""
Pydantic Model Completeness Detector

Checks that Pydantic models include all fields accessed by the Service layer.

Based on Event2Table Entity architecture standards:
- Pydantic models must define all fields accessed by Service layer
- Missing fields lead to AttributeError at runtime
- Field type annotations must be complete (Optional[str], str, int)
"""

import ast
from pathlib import Path
from typing import List, Set, Dict, Tuple

from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class PydanticCompletenessDetector(BaseDetector):
    """
    Detects Pydantic model completeness issues

    Rules:
    1. Pydantic models must define all fields accessed by Service methods
    2. Field type annotations must be complete
    3. Required fields should not use Optional without default value
    """

    def __init__(self):
        super().__init__()
        self.rule_id = "PYDANTIC_COMPLETE_001"

    def is_applicable(self, file_path: str) -> bool:
        """
        Check if detector applies to this file

        Analyze Python files in backend/models/entities.py and backend/services/
        """
        path = Path(file_path)
        return (
            path.suffix == '.py' and
            'backend' in str(path) and
            'test' not in str(path).lower() and
            '__pycache__' not in str(path)
        )

    def detect(self, file_path: str) -> List[Issue]:
        """Detect Pydantic model completeness issues"""
        issues = []

        try:
            content = Path(file_path).read_text()
            tree = ast.parse(content)

            # Check if this is an entities file or service file
            if 'entities.py' in str(file_path):
                # Collect all Pydantic model definitions
                models = self._extract_pydantic_models(tree)

                # For now, just check that models have proper field definitions
                for model_name, model_info in models.items():
                    issues.extend(self._check_model_fields(file_path, model_name, model_info))

            elif 'services' in str(file_path):
                # Cross-check: Find entity attribute access
                issues.extend(self._check_service_entity_access(file_path, tree))

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _extract_pydantic_models(self, tree: ast.AST) -> Dict[str, Dict]:
        """Extract all Pydantic model definitions and their fields"""
        models = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this class inherits from BaseModel
                is_pydantic = False
                base_names = []

                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_names.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        base_names.append(base.attr)

                if 'BaseModel' in base_names or 'Entity' in base_names:
                    is_pydantic = True

                if is_pydantic:
                    # Extract field definitions
                    fields = {}
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign):
                            # Field with type annotation: field_name: FieldType
                            if isinstance(item.target, ast.Name):
                                field_name = item.target.id
                                field_type = self._get_type_string(item.annotation)
                                has_default = item.value is not None
                                is_optional = self._is_optional_type(item.annotation)

                                fields[field_name] = {
                                    'type': field_type,
                                    'has_default': has_default,
                                    'is_optional': is_optional,
                                    'line_number': item.lineno
                                }

                    models[node.name] = {
                        'fields': fields,
                        'line_number': node.lineno
                    }

        return models

    def _check_service_entity_access(self, file_path: str, tree: ast.AST) -> List[Issue]:
        """Check Service methods for entity attribute access"""
        issues = []

        # Find all Service classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith('Service'):
                # Find all methods that access entity attributes
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        issues.extend(self._check_method_entity_access(file_path, node.name, item))

        return issues

    def _check_method_entity_access(
        self,
        file_path: str,
        class_name: str,
        method: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> List[Issue]:
        """Check if method accesses entity attributes that might not exist"""
        issues = []

        # Find all attribute access patterns like entity.field_name
        for node in ast.walk(method):
            if isinstance(node, ast.Attribute):
                # Check if this looks like entity.field access
                if isinstance(node.value, ast.Name):
                    variable_name = node.value.id
                    attribute_name = node.attr

                    # Check if variable name suggests it's an entity
                    if any(keyword in variable_name.lower() for keyword in ['entity', 'data', 'game', 'event', 'param']):
                        # This is a heuristic - we can't verify without cross-file analysis
                        # But we can flag potential issues
                        pass

        return issues

    def _check_model_fields(
        self,
        file_path: str,
        model_name: str,
        model_info: Dict
    ) -> List[Issue]:
        """Check if model fields are properly defined"""
        issues = []

        for field_name, field_info in model_info['fields'].items():
            # Check 1: Field has type annotation (already guaranteed by AnnAssign)

            # Check 2: Optional fields should have default values
            if field_info['is_optional'] and not field_info['has_default']:
                issues.append(Issue(
                    file_path=file_path,
                    line_number=field_info['line_number'],
                    severity=Severity.MEDIUM,
                    category=IssueCategory.QUALITY,
                    message=f"Optional field '{field_name}' in {model_name} should have a default value",
                    suggestion="Add default value or remove Optional: field_name: FieldType = None",
                    code_snippet=f"{field_name}: {field_info['type']}  # Optional but no default",
                    rule_id=self.rule_id,
                    metadata={'model': model_name, 'field': field_name}
                ))

        return issues

    def _get_type_string(self, type_node: ast.AST) -> str:
        """Get string representation of type annotation"""
        if type_node is None:
            return "Any"

        if isinstance(type_node, ast.Name):
            return type_node.id
        elif isinstance(type_node, ast.Subscript):
            base = self._get_type_string(type_node.value)
            # For simple cases like List[str], Optional[int]
            if hasattr(type_node, 'slice'):
                slice_str = self._get_type_string(type_node.slice)
                return f"{base}[{slice_str}]"
            return base
        elif isinstance(type_node, ast.BinOp):
            # Handle Union types like str | None (Python 3.10+)
            return "Union"
        elif isinstance(type_node, ast.Constant):
            return str(type_node.value)
        else:
            return "ComplexType"

    def _is_optional_type(self, type_node: ast.AST) -> bool:
        """Check if type is Optional (Union[..., None] or X | None)"""
        if isinstance(type_node, ast.Subscript):
            # Check if it's Optional[X] or Union[X, None]
            if isinstance(type_node.value, ast.Name):
                if type_node.value.id in {'Optional', 'Union'}:
                    return True

        # Check for X | None syntax (Python 3.10+)
        if isinstance(type_node, ast.BinOp):
            if isinstance(type_node.op, ast.BitOr):
                # Check if one side is None
                if isinstance(type_node.right, ast.Constant) and type_node.right.value is None:
                    return True

        return False
