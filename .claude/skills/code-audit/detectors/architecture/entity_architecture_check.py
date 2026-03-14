"""
Entity Architecture Compliance Detector

Checks that code follows Event2Table Entity architecture patterns.

Based on Event2Table Entity architecture standards:
- Repository layer must return Entity objects, not Dict
- Service layer must use Entity.model_dump() for serialization
- API layer must use Entity for request validation
"""

import ast
from pathlib import Path
from typing import List, Set, Dict

from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class EntityArchitectureDetector(BaseDetector):
    """
    Detects Entity architecture compliance issues

    Rules:
    1. Repository methods must return Entity objects, not Dict
    2. Service methods must use Entity.model_dump() for serialization
    3. API routes must use Entity for request validation
    """

    # Entity base classes
    ENTITY_BASE_CLASSES = {'BaseModel', 'Entity', 'GameEntity', 'EventEntity', 'ParameterEntity'}

    # Repository method return patterns
    DICT_RETURN_PATTERNS = {
        'Dict[str, Any]',
        'dict',
        'Dict',
        'return {',  # Dictionary literal
    }

    def __init__(self):
        super().__init__()
        self.rule_id = "ENTITY_ARCH_001"

    def is_applicable(self, file_path: str) -> bool:
        """
        Check if detector applies to this file

        Analyze Python files in backend/models/repositories/ and backend/services/
        """
        path = Path(file_path)
        return (
            path.suffix == '.py' and
            'backend' in str(path) and
            ('repositories' in str(path) or 'services' in str(path) or 'api/routes' in str(path)) and
            'test' not in str(path).lower() and
            '__pycache__' not in str(path)
        )

    def detect(self, file_path: str) -> List[Issue]:
        """Detect Entity architecture compliance issues"""
        issues = []

        try:
            content = Path(file_path).read_text()
            tree = ast.parse(content)

            if 'repositories' in str(file_path):
                # Check Repository layer
                issues.extend(self._check_repository_layer(file_path, tree))

            elif 'services' in str(file_path):
                # Check Service layer
                issues.extend(self._check_service_layer(file_path, tree))

            elif 'api/routes' in str(file_path):
                # Check API layer
                issues.extend(self._check_api_layer(file_path, tree))

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _check_repository_layer(self, file_path: str, tree: ast.AST) -> List[Issue]:
        """Check Repository layer for Entity architecture compliance"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith('Repository'):
                # Check all methods in this repository
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        issues.extend(self._check_repository_method(file_path, node.name, item))

        return issues

    def _check_repository_method(
        self,
        file_path: str,
        class_name: str,
        method: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> List[Issue]:
        """Check if repository method returns Entity objects"""
        issues = []

        # Find return type annotation
        return_annotation = method.returns
        if return_annotation:
            return_type_str = self._get_type_string(return_annotation)

            # Check if return type is Dict (should be Entity)
            if any(pattern in return_type_str for pattern in self.DICT_RETURN_PATTERNS):
                # But make exception for special cases like _as_dict()
                if not method.name.startswith('_'):
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=method.lineno,
                        severity=Severity.HIGH,
                        category=IssueCategory.ARCHITECTURE,
                        message=f"Repository method {class_name}.{method.name}() returns Dict instead of Entity",
                        suggestion="Return Entity object instead of Dict. Use Entity(**data) to convert dict to Entity.",
                        code_snippet=self._extract_method_signature(method),
                        rule_id=self.rule_id,
                        metadata={'class': class_name, 'method': method.name, 'return_type': return_type_str}
                    ))

        return issues

    def _check_service_layer(self, file_path: str, tree: ast.AST) -> List[Issue]:
        """Check Service layer for Entity architecture compliance"""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith('Service'):
                # Check all methods in this service
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        issues.extend(self._check_service_method(file_path, node.name, item))

        return issues

    def _check_service_method(
        self,
        file_path: str,
        class_name: str,
        method: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> List[Issue]:
        """Check if service method properly handles Entity objects"""
        issues = []

        # Check if method has database queries (fetch_all_as_dict, fetch_one_as_dict)
        has_raw_db_query = self._has_database_query_call(method)

        # Check if method returns Entity objects
        returns_entity = self._method_returns_entity(method)

        if has_raw_db_query and not returns_entity:
            issues.append(Issue(
                file_path=file_path,
                line_number=method.lineno,
                severity=Severity.HIGH,
                category=IssueCategory.ARCHITECTURE,
                message=f"Service method {class_name}.{method.name}() uses raw DB queries but doesn't return Entity objects",
                suggestion="Convert query results to Entity objects: Entity(**data) or [Entity(**d) for d in results]",
                code_snippet=self._extract_method_signature(method),
                rule_id=self.rule_id,
                metadata={'class': class_name, 'method': method.name}
            ))

        # Check if method uses .model_dump() for serialization
        has_model_dump = self._has_model_dump_call(method)

        if has_model_dump:
            # This is good - no issue
            pass

        return issues

    def _check_api_layer(self, file_path: str, tree: ast.AST) -> List[Issue]:
        """Check API layer for Entity architecture compliance"""
        issues = []

        # Check if API routes use Entity for request validation
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith(('get_', 'post_', 'put_', 'delete_')):
                # Check if function uses Pydantic models for validation
                uses_entity_validation = self._uses_entity_validation(node)

                # Check if function parses JSON without Entity
                has_raw_json_parse = False
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr == 'get_json' and isinstance(child.func.value, ast.Name):
                                if child.func.value.id == 'request':
                                    has_raw_json_parse = True

                if has_raw_json_parse and not uses_entity_validation:
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=node.lineno,
                        severity=Severity.MEDIUM,
                        category=IssueCategory.ARCHITECTURE,
                        message=f"API route {node.name}() uses raw request.get_json() without Entity validation",
                        suggestion="Use Pydantic Entity for automatic validation: data = Entity(**request.get_json())",
                        code_snippet=self._extract_method_signature(node),
                        rule_id=self.rule_id,
                        metadata={'function': node.name}
                    ))

        return issues

    def _has_database_query_call(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method calls database query functions"""
        for node in ast.walk(method):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in {'fetch_all_as_dict', 'fetch_one_as_dict', 'execute_query'}:
                        return True
        return False

    def _method_returns_entity(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method return type indicates Entity return"""
        if not method.returns:
            return False

        return_type_str = self._get_type_string(method.returns)
        return 'Entity' in return_type_str or return_type_str.endswith('Entity')

    def _has_model_dump_call(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Check if method calls .model_dump() for serialization"""
        for node in ast.walk(method):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'model_dump':
                        return True
        return False

    def _uses_entity_validation(self, method: ast.FunctionDef) -> bool:
        """Check if method uses Pydantic Entity for validation"""
        for node in ast.walk(method):
            # Check for Entity(**data) pattern
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if 'Entity' in node.func.id or node.func.id.endswith('Entity'):
                        return True
        return False

    def _get_type_string(self, type_node: ast.AST) -> str:
        """Get string representation of type annotation"""
        if type_node is None:
            return ""

        if isinstance(type_node, ast.Name):
            return type_node.id
        elif isinstance(type_node, ast.Subscript):
            base = self._get_type_string(type_node.value)
            if hasattr(type_node, 'slice') and type_node.slice:
                slice_str = self._get_type_string(type_node.slice)
                return f"{base}[{slice_str}]"
            return base
        elif isinstance(type_node, ast.Constant):
            return str(type_node.value)
        else:
            return ""

    def _extract_method_signature(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract method signature as string"""
        args = []
        for arg in method.args.args:
            args.append(arg.arg)

        async_prefix = "async " if isinstance(method, ast.AsyncFunctionDef) else ""
        return f"def {method.name}({', '.join(args[:3])}...)"  # Show first 3 args

    def _extract_code_snippet(self, method: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract code snippet for issue report"""
        return self._extract_method_signature(method)
